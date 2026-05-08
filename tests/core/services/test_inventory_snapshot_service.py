"""Tests del InventorySnapshotService — composición del snapshot local.

Cubre la lógica que antes era el `_build_snapshot` privado del
`ExchangeExportService` y que ahora vive en su propio service para
ser reutilizable por la UI de matching post-import (5b) sin tener
que escribir un archivo intermedio.
"""

from __future__ import annotations

import sqlite3

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
from collections_app.services.exchange_errors import CollectionNotFound
from collections_app.services.inventory_snapshot_service import (
    InventorySnapshotService,
)


@pytest.fixture
def collection_with_inventory(
    db_conn: sqlite3.Connection,
) -> Collection:
    """Setup canónico: 5 cards, ARG-1 owned, ARG-2 con duplicate, ARG-3 missing,
    BRA-1 missing, BRA-2 owned."""
    headers = CodeHeadersRepository(db_conn)
    lines = CodeLinesRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    cards_repo = CardsRepository(db_conn)
    inv = InventoryRepository(db_conn)

    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3))
    assert h.code_header_id is not None
    for code in ("ARG", "BRA"):
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id=code,
                code_name=code,
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
    arg1 = cards_repo.get(coll.collection_id, "ARG", 1)
    arg2 = cards_repo.get(coll.collection_id, "ARG", 2)
    bra2 = cards_repo.get(coll.collection_id, "BRA", 2)
    assert arg1 and arg2 and bra2 and arg1.card_id and arg2.card_id and bra2.card_id
    inv.adjust_quantity(arg1.card_id, 1)
    inv.adjust_quantity(arg2.card_id, 3)
    inv.adjust_quantity(bra2.card_id, 1)
    db_conn.commit()
    return coll


def test_build_local_snapshot_returns_correct_collection_metadata(
    db_conn: sqlite3.Connection,
    collection_with_inventory: Collection,
) -> None:
    """`collection_name` y `collection_card_count` corresponden a la DB."""
    svc = InventorySnapshotService(db_conn)
    assert collection_with_inventory.collection_id is not None
    snap = svc.build_local_snapshot(
        collection_id=collection_with_inventory.collection_id,
        user_label="PGG",
    )
    assert snap.collection_name == "Mundial 2026"
    assert snap.collection_card_count == 5
    assert snap.user_label == "PGG"


def test_build_local_snapshot_lists_missing_cards(
    db_conn: sqlite3.Connection,
    collection_with_inventory: Collection,
) -> None:
    """ARG-3 y BRA-1 están como missing."""
    svc = InventorySnapshotService(db_conn)
    assert collection_with_inventory.collection_id is not None
    snap = svc.build_local_snapshot(
        collection_id=collection_with_inventory.collection_id,
        user_label=None,
    )
    keys = {(m.code_id, m.card_number) for m in snap.missing}
    assert keys == {("ARG", 3), ("BRA", 1)}
    # `needed_quantity` default = 1.
    assert all(m.needed_quantity == 1 for m in snap.missing)


def test_build_local_snapshot_duplicates_use_quantity_minus_one(
    db_conn: sqlite3.Connection,
    collection_with_inventory: Collection,
) -> None:
    """`available_quantity = inventory.quantity - 1`."""
    svc = InventorySnapshotService(db_conn)
    assert collection_with_inventory.collection_id is not None
    snap = svc.build_local_snapshot(
        collection_id=collection_with_inventory.collection_id,
        user_label=None,
    )
    # ARG-2 tenía qty=3 → available = 2.
    arg2 = next(d for d in snap.duplicates if d.card_number == 2 and d.code_id == "ARG")
    assert arg2.available_quantity == 2
    # ARG-1 tiene qty=1 → available = 0 → no aparece.
    assert all(not (d.code_id == "ARG" and d.card_number == 1) for d in snap.duplicates)


def test_build_local_snapshot_strips_user_label(
    db_conn: sqlite3.Connection,
    collection_with_inventory: Collection,
) -> None:
    """`user_label` con whitespace se hace strip; vacío post-strip → None."""
    svc = InventorySnapshotService(db_conn)
    assert collection_with_inventory.collection_id is not None
    snap = svc.build_local_snapshot(
        collection_id=collection_with_inventory.collection_id,
        user_label="  PGG  ",
    )
    assert snap.user_label == "PGG"
    snap2 = svc.build_local_snapshot(
        collection_id=collection_with_inventory.collection_id,
        user_label="   ",
    )
    assert snap2.user_label is None


def test_build_local_snapshot_unknown_collection_raises(
    db_conn: sqlite3.Connection,
) -> None:
    """`collection_id` inexistente → CollectionNotFound."""
    svc = InventorySnapshotService(db_conn)
    with pytest.raises(CollectionNotFound):
        svc.build_local_snapshot(collection_id=999, user_label=None)


def test_build_local_snapshot_empty_collection(
    db_conn: sqlite3.Connection,
) -> None:
    """Colección sin cards: snapshot con missing y duplicates vacíos."""
    headers = CodeHeadersRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="X", code_max_length=2))
    assert h.code_header_id is not None
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Vacía",
            card_count=0,
            requires_code=True,
            code_field_name="X",
            code_header_id=h.code_header_id,
        )
    )
    db_conn.commit()
    svc = InventorySnapshotService(db_conn)
    assert coll.collection_id is not None
    snap = svc.build_local_snapshot(collection_id=coll.collection_id, user_label=None)
    assert snap.missing == ()
    assert snap.duplicates == ()
    assert snap.collection_card_count == 0
