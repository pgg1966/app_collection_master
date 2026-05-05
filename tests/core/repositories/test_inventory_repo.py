"""Tests CRUD + queries específicas de InventoryRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> InventoryRepository:
    return InventoryRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make_card(cards_repo: CardsRepository, collection_id: int, n: int) -> int:
    saved = cards_repo.create(
        Card(
            card_id=None,
            collection_id=collection_id,
            code_id="X",
            card_number=n,
            card_name=f"X-{n}",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def test_get_by_card_id_returns_none_when_no_inventory(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.get_by_card_id(card_id) is None


def test_upsert_inserts_new(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=3))
    assert saved.inventory_id is not None
    assert saved.quantity == 3


def test_upsert_updates_existing_by_card_id(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=3))
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=7))
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.quantity == 7


def test_upsert_violates_fk_when_card_not_exists(
    repo: InventoryRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(InventoryItem(inventory_id=None, card_id=999, quantity=1))


def test_adjust_quantity_creates_entry_when_missing(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    item = repo.adjust_quantity(card_id, 3)
    assert item.quantity == 3
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.quantity == 3


def test_adjust_quantity_increments(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=5))
    item = repo.adjust_quantity(card_id, 3)
    assert item.quantity == 8


def test_adjust_quantity_decrements(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=5))
    item = repo.adjust_quantity(card_id, -2)
    assert item.quantity == 3


def test_list_by_collection_filters_correctly(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    """Solo retorna inventory cuyas cards pertenecen a esa colección."""
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=5))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_owned_excludes_zero_quantity(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=0))
    items = repo.list_owned(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_duplicates_only_above_one(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=1))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=c, quantity=5))
    items = repo.list_duplicates(collection_id)
    card_ids = {i.card_id for i in items}
    assert card_ids == {b, c}


def test_get_top_duplicates_sorted_desc_with_limit(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    for n, qty in enumerate([2, 5, 3, 7, 4], start=1):
        card_id = _make_card(cards_repo, collection_id, n)
        repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=qty))
    top = repo.get_top_duplicates(collection_id, limit=3)
    assert [i.quantity for i in top] == [7, 5, 4]


def test_list_missing_includes_cards_with_zero_quantity(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=0))
    items = repo.list_missing(collection_id)
    card_ids = {c.card_id for c in items}
    assert b in card_ids
    assert a not in card_ids


def test_list_missing_includes_cards_without_inventory_entry(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=3))
    items = repo.list_missing(collection_id)
    card_ids = {c.card_id for c in items}
    assert b in card_ids
    assert a not in card_ids


def test_list_missing_returns_card_dataclasses(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    items = repo.list_missing(collection_id)
    assert all(isinstance(c, Card) for c in items)
