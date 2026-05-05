"""Tests del InventoryRepository."""

import pytest

from collections_app.core.models import Card, InventoryItem
from collections_app.core.repositories import InventoryRepository


def _item(cid: int, code: str = "ARG", num: int = 1, qty: int = 1, image=None) -> InventoryItem:
    return InventoryItem(cid, code, num, qty, image)


def test_upsert_creates_item(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    item = _item(sample_collection.collection_id, qty=3)
    repo.upsert(item)
    fetched = repo.get(sample_collection.collection_id, "ARG", 1)
    assert fetched == item


def test_upsert_updates_existing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1))
    repo.upsert(_item(cid, qty=5, image="/tmp/messi.png"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.quantity == 5
    assert fetched.image_path == "/tmp/messi.png"


def test_get_missing(memory_db, sample_collection):
    repo = InventoryRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ZZZ", 999) is None


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = InventoryRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_owned_filters_zero(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=0))
    repo.upsert(_item(cid, "ARG", 2, qty=2))
    repo.upsert(_item(cid, "BRA", 1, qty=1))
    owned = repo.list_owned(cid)
    assert len(owned) == 2
    assert all(i.quantity > 0 for i in owned)


def test_list_duplicates(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=1))
    repo.upsert(_item(cid, "ARG", 2, qty=3))
    repo.upsert(_item(cid, "BRA", 1, qty=2))
    dups = repo.list_duplicates(cid)
    assert len(dups) == 2
    assert {(i.code_id, i.card_number) for i in dups} == {("ARG", 2), ("BRA", 1)}


def test_list_missing_returns_cards_without_inventory(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=2))
    # Las otras 4 cards no tienen inventario
    missing = repo.list_missing(cid)
    assert len(missing) == 4
    assert all(isinstance(c, Card) for c in missing)
    assert ("ARG", 1) not in {(c.code_id, c.card_number) for c in missing}


def test_list_missing_treats_zero_qty_as_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=0))
    repo.upsert(_item(cid, "ARG", 2, qty=1))
    missing = repo.list_missing(cid)
    keys = {(c.code_id, c.card_number) for c in missing}
    assert ("ARG", 1) in keys  # qty=0 cuenta como missing
    assert ("ARG", 2) not in keys


def test_adjust_quantity_creates_when_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    item = repo.adjust_quantity(cid, "ARG", 1, 3)
    assert item.quantity == 3


def test_adjust_quantity_increments(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=2))
    item = repo.adjust_quantity(cid, "ARG", 1, 3)
    assert item.quantity == 5


def test_adjust_quantity_decrements(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=5))
    item = repo.adjust_quantity(cid, "ARG", 1, -3)
    assert item.quantity == 2


def test_adjust_quantity_negative_raises(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1))
    with pytest.raises(ValueError, match="negativa"):
        repo.adjust_quantity(cid, "ARG", 1, -5)


def test_adjust_quantity_preserves_image(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1, image="/img/messi.png"))
    item = repo.adjust_quantity(cid, "ARG", 1, 1)
    assert item.image_path == "/img/messi.png"


def test_set_image_creates_record_if_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.set_image(cid, "ARG", 1, "/img/messi.png")
    item = repo.get(cid, "ARG", 1)
    assert item is not None
    assert item.quantity == 0
    assert item.image_path == "/img/messi.png"


def test_set_image_preserves_quantity(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=4))
    repo.set_image(cid, "ARG", 1, "/img/messi.png")
    item = repo.get(cid, "ARG", 1)
    assert item is not None
    assert item.quantity == 4


def test_inventory_item_is_owned_property():
    assert InventoryItem(1, "X", 1, quantity=0).is_owned is False
    assert InventoryItem(1, "X", 1, quantity=2).is_owned is True


def test_inventory_item_has_duplicates_property():
    assert InventoryItem(1, "X", 1, quantity=1).has_duplicates is False
    assert InventoryItem(1, "X", 1, quantity=2).has_duplicates is True


def test_get_top_duplicates(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=5))
    repo.upsert(_item(cid, "ARG", 2, qty=3))
    repo.upsert(_item(cid, "BRA", 1, qty=2))
    repo.upsert(_item(cid, "BRA", 2, qty=1))  # no es duplicada
    top = repo.get_top_duplicates(cid)
    assert [(t.code_id, t.card_number, t.quantity) for t in top] == [
        ("ARG", 1, 5),
        ("ARG", 2, 3),
        ("BRA", 1, 2),
    ]


def test_get_top_duplicates_respects_limit(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=5))
    repo.upsert(_item(cid, "ARG", 2, qty=4))
    repo.upsert(_item(cid, "BRA", 1, qty=3))
    top = repo.get_top_duplicates(cid, limit=2)
    assert len(top) == 2
