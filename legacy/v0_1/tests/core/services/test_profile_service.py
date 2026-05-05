"""Tests del ProfileService: detección de perfiles + import_structure."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import (
    Card,
    CodeHeader,
    Collection,
    InventoryItem,
    OperationType,
    Transaction,
)
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
    InventoryRepository,
    TransactionsRepository,
)
from collections_app.core.services.profile_service import (
    _STRUCTURE_TABLES,
    ProfileService,
)
from collections_app.core.utils import paths
from collections_app.core.utils.datetime_helpers import utc_now

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _new_db(path: Path) -> sqlite3.Connection:
    """Crea una DB SQLite migrada al schema actual en `path`."""
    conn = create_connection(path)
    run_migrations(conn)
    conn.commit()
    return conn


def _populate_source(conn: sqlite3.Connection) -> tuple[int, int]:
    """Inserta 2 colecciones, 1 header con 2 lines, 5 cards.

    Devuelve (cantidad_colecciones, cantidad_cards) para asserts.
    """
    hdr = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name="FIFA", code_max_length=5)
    )
    hid = hdr.code_header_id

    from collections_app.core.models import CodeLine
    from collections_app.core.repositories import CodesLinesRepository

    lines_repo = CodesLinesRepository(conn)
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brazil"))

    col_repo = CollectionsRepository(conn)
    col1 = col_repo.create(
        Collection(
            collection_id=None,
            collection_name="WC 2026",
            card_count=3,
            requires_code=True,
            code_field_name="País",
            code_header_id=hid,
        )
    )
    col2 = col_repo.create(
        Collection(
            collection_id=None,
            collection_name="Stickers",
            card_count=2,
            requires_code=True,
            code_field_name="Set",
            code_header_id=hid,
        )
    )

    cards_repo = CardsRepository(conn)
    cards_repo.bulk_upsert(
        [
            Card(col1.collection_id, "ARG", 1, "Messi"),
            Card(col1.collection_id, "ARG", 2, "Martínez"),
            Card(col1.collection_id, "BRA", 1, "Vinícius"),
            Card(col2.collection_id, "ARG", 1, "Sticker A"),
            Card(col2.collection_id, "BRA", 1, "Sticker B"),
        ]
    )
    conn.commit()
    return 2, 5


# ----------------------------------------------------------------------
# import_structure
# ----------------------------------------------------------------------


def test_import_structure_copies_collections(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    n_cols, _ = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    count = ProfileService.import_structure(src_path, tgt)
    assert count == n_cols
    assert len(CollectionsRepository(tgt).list_all()) == n_cols
    tgt.close()


def test_import_structure_copies_cards(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _, n_cards = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # Sumar cards de todas las colecciones del target
    cards_repo = CardsRepository(tgt)
    total = sum(
        len(cards_repo.list_by_collection(c.collection_id))
        for c in CollectionsRepository(tgt).list_all()
    )
    assert total == n_cards
    tgt.close()


def test_import_structure_skips_inventory(tmp_path):
    """Inventario en source con qty>0 NO se copia al target."""
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _populate_source(src)
    # Cargar 1 unidad en cada colección (card_number=1 existe en ambas).
    for col in CollectionsRepository(src).list_all():
        InventoryRepository(src).upsert(InventoryItem(col.collection_id, "ARG", 1, quantity=5))
    src.commit()
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # En target NO debe haber items con quantity > 0 en NINGUNA colección
    for col in CollectionsRepository(tgt).list_all():
        owned = InventoryRepository(tgt).list_owned(col.collection_id)
        assert owned == []
    tgt.close()


def test_import_structure_skips_transactions(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _populate_source(src)
    cid = CollectionsRepository(src).list_all()[0].collection_id
    tx_repo = TransactionsRepository(src)
    for _ in range(3):
        tx_repo.log(
            Transaction(
                transaction_id=None,
                collection_id=cid,
                code_id="ARG",
                card_number=1,
                operation=OperationType.ALTA,
                quantity=1,
                transaction_date=utc_now(),
            )
        )
    src.commit()
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # En target NO debe haber transactions
    row = tgt.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert row[0] == 0
    tgt.close()


def test_import_structure_is_idempotent(tmp_path):
    """Correr import dos veces no duplica nada (INSERT OR IGNORE)."""
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    n_cols, n_cards = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    first = ProfileService.import_structure(src_path, tgt)
    second = ProfileService.import_structure(src_path, tgt)
    assert first == n_cols
    assert second == n_cols  # mismo count, no duplicó
    cards_repo = CardsRepository(tgt)
    total = sum(
        len(cards_repo.list_by_collection(c.collection_id))
        for c in CollectionsRepository(tgt).list_all()
    )
    assert total == n_cards
    tgt.close()


def test_structure_tables_constant_excludes_user_data():
    """Sanity: la lista de tablas a copiar NO incluye inventory ni transactions."""
    assert "inventory" not in _STRUCTURE_TABLES
    assert "transactions" not in _STRUCTURE_TABLES


# ----------------------------------------------------------------------
# get_all_profiles
# ----------------------------------------------------------------------


@pytest.fixture
def isolated_app_data(monkeypatch, tmp_path):
    """Apunta APPDATA a tmp_path y restaura el perfil al final."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr(paths.sys, "platform", "win32")
    yield tmp_path / "Collections"
    paths.set_active_profile("default")


def test_get_all_profiles_finds_default(isolated_app_data):
    base = isolated_app_data
    base.mkdir(parents=True, exist_ok=True)
    # Crear DB en la raíz (perfil default)
    conn = _new_db(base / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "default" in names


def test_get_all_profiles_finds_subdirectories(isolated_app_data):
    base = isolated_app_data
    (base / "personal").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "personal" / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "personal" in names


def test_get_all_profiles_ignores_dirs_without_db(isolated_app_data):
    base = isolated_app_data
    (base / "empty_dir").mkdir(parents=True, exist_ok=True)
    # Sin collections.db dentro

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "empty_dir" not in names


def test_profile_info_reads_collection_count(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)  # 2 colecciones
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.collection_count == 2


def test_profile_info_detects_inventory(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)
    cid = CollectionsRepository(conn).list_all()[0].collection_id
    InventoryRepository(conn).upsert(InventoryItem(cid, "ARG", 1, quantity=5))
    conn.commit()
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.has_inventory is True


def test_profile_info_no_inventory(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.has_inventory is False


def test_default_profile_display_name_is_principal(isolated_app_data):
    base = isolated_app_data
    base.mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    default = next(p for p in profiles if p.name == "default")
    assert default.display_name == "Principal"
