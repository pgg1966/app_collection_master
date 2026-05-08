"""Tests del aggregate InventorySnapshot (frozen, hashable, equality por valor)."""

from __future__ import annotations

from collections_app.core.models.aggregates.inventory_snapshot import (
    DuplicateCard,
    InventorySnapshot,
    MissingCard,
)


def test_inventory_snapshot_equality_by_value() -> None:
    """Dos snapshots con mismo contenido son iguales."""
    a = InventorySnapshot(
        user_label="PGG",
        collection_name="Mundial 2026",
        collection_card_count=670,
        missing=(MissingCard("ARG", 1, "Messi", 1),),
        duplicates=(),
    )
    b = InventorySnapshot(
        user_label="PGG",
        collection_name="Mundial 2026",
        collection_card_count=670,
        missing=(MissingCard("ARG", 1, "Messi", 1),),
        duplicates=(),
    )
    assert a == b


def test_inventory_snapshot_is_hashable() -> None:
    """Frozen dataclass con tuplas es hashable."""
    snap = InventorySnapshot(
        user_label=None,
        collection_name="X",
        collection_card_count=10,
        missing=(),
        duplicates=(),
    )
    assert hash(snap) == hash(snap)


def test_missing_card_equality() -> None:
    a = MissingCard("ARG", 1, "Messi", 2)
    b = MissingCard("ARG", 1, "Messi", 2)
    c = MissingCard("ARG", 1, "Messi", 3)
    assert a == b
    assert a != c


def test_duplicate_card_equality() -> None:
    a = DuplicateCard("BRA", 7, "Neymar", 3)
    b = DuplicateCard("BRA", 7, "Neymar", 3)
    assert a == b
