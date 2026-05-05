"""Tests del dataclass InventoryItem."""

from __future__ import annotations

from collections_app.core.models.inventory_item import InventoryItem


def test_is_owned_true_when_quantity_positive() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=1).is_owned is True
    assert InventoryItem(inventory_id=1, card_id=1, quantity=99).is_owned is True


def test_is_owned_false_when_quantity_zero() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=0).is_owned is False


def test_has_duplicates_true_when_quantity_above_one() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=2).has_duplicates is True


def test_has_duplicates_false_when_quantity_one_or_less() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=1).has_duplicates is False
    assert InventoryItem(inventory_id=1, card_id=1, quantity=0).has_duplicates is False


def test_inventory_id_can_be_none_pre_persistence() -> None:
    item = InventoryItem(inventory_id=None, card_id=1, quantity=0)
    assert item.inventory_id is None
