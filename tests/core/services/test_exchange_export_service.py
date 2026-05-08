"""Tests del ExchangeExportService — generación + firma + filename."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.security.exchange_signing import verify_signature
from collections_app.services.exchange_errors import CollectionNotFound
from collections_app.services.exchange_export_service import (
    ExchangeExportService,
    _build_filename,
    _sanitize_for_filename,
)


@pytest.fixture
def collection_with_inventory(
    db_conn: sqlite3.Connection,
) -> tuple[Collection, CardsRepository]:
    """Collection 'Mundial 2026' con 5 cards: 2 owned, 1 con duplicate, 2 missing."""
    headers = CodeHeadersRepository(db_conn)
    lines = CodeLinesRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    cards_repo = CardsRepository(db_conn)
    inv = InventoryRepository(db_conn)

    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3))
    assert h.code_header_id is not None
    for code, name in [("ARG", "Argentina"), ("BRA", "Brasil")]:
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id=code,
                code_name=name,
                code_order=1,
            )
        )
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Mundial 2026",
            card_count=5,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    # Cards: ARG-1 (owned, qty=1), ARG-2 (owned, qty=3 → 2 duplicates),
    # ARG-3 (missing), BRA-1 (missing), BRA-2 (owned, qty=1).
    for code, num, name in [
        ("ARG", 1, "Messi"),
        ("ARG", 2, "Di María"),
        ("ARG", 3, "Lautaro"),
        ("BRA", 1, "Neymar"),
        ("BRA", 2, "Vinícius"),
    ]:
        cards_repo.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id=code,
                card_number=num,
                card_name=name,
            )
        )
    db_conn.commit()
    # Setup inventory.
    arg1 = cards_repo.get(coll.collection_id, "ARG", 1)
    arg2 = cards_repo.get(coll.collection_id, "ARG", 2)
    bra2 = cards_repo.get(coll.collection_id, "BRA", 2)
    assert arg1 and arg2 and bra2 and arg1.card_id and arg2.card_id and bra2.card_id
    inv.adjust_quantity(arg1.card_id, 1)
    inv.adjust_quantity(arg2.card_id, 3)
    inv.adjust_quantity(bra2.card_id, 1)
    db_conn.commit()
    return coll, cards_repo


# ---------------------------------------------------------------------
# Filename / sanitización
# ---------------------------------------------------------------------


def test_sanitize_replaces_windows_reserved_chars() -> None:
    assert _sanitize_for_filename('a<b>c:d"e/f\\g|h?i*j k') == "a_b_c_d_e_f_g_h_i_j_k"


def test_sanitize_preserves_accents() -> None:
    assert _sanitize_for_filename("Mundial 2026 — Edición Argentina") == (
        "Mundial_2026_—_Edición_Argentina"
    )


def test_build_filename_with_label() -> None:
    name = _build_filename("Mundial 2026", "PGG")
    assert name.startswith("Mundial_2026_PGG_")
    assert name.endswith(".colexchange")


def test_build_filename_without_label() -> None:
    name = _build_filename("Mundial 2026", None)
    parts = name[: -len(".colexchange")].split("_")
    # 'Mundial', '2026', 'YYYY-MM-DD' = 3 segmentos.
    assert len(parts) == 3
    assert parts[0] == "Mundial"
    assert parts[1] == "2026"


def test_build_filename_empty_label_omitted() -> None:
    """Label vacío post-strip se omite (no deja `__` doble)."""
    name = _build_filename("Mundial 2026", "   ")
    parts = name[: -len(".colexchange")].split("_")
    assert len(parts) == 3  # mismo que None


# ---------------------------------------------------------------------
# Exportación end-to-end
# ---------------------------------------------------------------------


def test_export_writes_file_in_downloads_dir(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_inventory: tuple[Collection, CardsRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """El archivo se escribe en la carpeta Descargas resuelta."""
    coll, _ = collection_with_inventory
    fake_downloads = tmp_path / "Downloads"
    fake_downloads.mkdir()
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: fake_downloads,
    )

    svc = ExchangeExportService(db_conn)
    assert coll.collection_id is not None
    out = svc.export_to_file(collection_id=coll.collection_id, user_label="PGG")
    assert out.parent == fake_downloads
    assert out.name.startswith("Mundial_2026_PGG_")
    assert out.name.endswith(".colexchange")
    assert out.is_file()


def test_export_payload_has_correct_structure(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_inventory: tuple[Collection, CardsRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """JSON exportado tiene la estructura del documento de diseño."""
    coll, _ = collection_with_inventory
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    svc = ExchangeExportService(db_conn)
    assert coll.collection_id is not None
    out = svc.export_to_file(collection_id=coll.collection_id, user_label="PGG")
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["format"] == "collections_app_exchange"
    assert payload["format_version"] == 1
    assert "exported_at" in payload
    assert "exported_by_app_version" in payload
    assert payload["collection"]["name"] == "Mundial 2026"
    assert payload["user_label"] == "PGG"
    assert isinstance(payload["missing"], list)
    assert isinstance(payload["duplicates"], list)
    assert "signature" in payload


def test_export_signature_verifies(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_inventory: tuple[Collection, CardsRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La firma del archivo verifica con `verify_signature`."""
    coll, _ = collection_with_inventory
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    svc = ExchangeExportService(db_conn)
    assert coll.collection_id is not None
    out = svc.export_to_file(collection_id=coll.collection_id, user_label="PGG")
    payload = json.loads(out.read_text(encoding="utf-8"))
    sig = payload.pop("signature")
    assert verify_signature(payload, sig) is True


def test_export_missing_cards_match_db_state(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_inventory: tuple[Collection, CardsRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Las cards listadas como `missing` son exactamente las que faltan."""
    coll, _ = collection_with_inventory
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    svc = ExchangeExportService(db_conn)
    assert coll.collection_id is not None
    out = svc.export_to_file(collection_id=coll.collection_id, user_label=None)
    payload = json.loads(out.read_text(encoding="utf-8"))
    missing_keys = {(m["code_id"], m["card_number"]) for m in payload["missing"]}
    # ARG-3 y BRA-1 fueron sembrados como missing.
    assert missing_keys == {("ARG", 3), ("BRA", 1)}


def test_export_duplicates_use_quantity_minus_one(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_inventory: tuple[Collection, CardsRepository],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`available_quantity = inventory.quantity - 1` (el primero es del álbum)."""
    coll, _ = collection_with_inventory
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    svc = ExchangeExportService(db_conn)
    assert coll.collection_id is not None
    out = svc.export_to_file(collection_id=coll.collection_id, user_label=None)
    payload = json.loads(out.read_text(encoding="utf-8"))
    # ARG-2 tenía qty=3 → available = 2.
    arg2_dup = next(d for d in payload["duplicates"] if d["card_number"] == 2)
    assert arg2_dup["available_quantity"] == 2


def test_export_unknown_collection_raises(
    db_conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    svc = ExchangeExportService(db_conn)
    with pytest.raises(CollectionNotFound):
        svc.export_to_file(collection_id=999, user_label=None)
