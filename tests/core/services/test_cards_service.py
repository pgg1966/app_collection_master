"""Tests de CardsService."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.cards_service import CardsService
from collections_app.services.exceptions import CardsError


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> CardsService:
    return CardsService(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
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


def _card(collection_id: int, **kw: object) -> Card:
    base: dict[str, object] = {
        "card_id": None,
        "collection_id": collection_id,
        "code_id": "X",
        "card_number": 1,
        "card_name": "Test",
    }
    base.update(kw)
    return Card(**base)  # type: ignore[arg-type]


def test_list_by_collection_empty(service: CardsService, collection_id: int) -> None:
    assert service.list_by_collection(collection_id) == []


def test_create_returns_card_with_id(service: CardsService, collection_id: int) -> None:
    saved = service.create(_card(collection_id))
    assert saved.card_id is not None


def test_create_with_empty_name_raises(service: CardsService, collection_id: int) -> None:
    with pytest.raises(CardsError, match="card_name"):
        service.create(_card(collection_id, card_name=""))


def test_create_with_card_number_zero_raises(service: CardsService, collection_id: int) -> None:
    with pytest.raises(CardsError, match="card_number"):
        service.create(_card(collection_id, card_number=0))


def test_create_with_negative_card_number_raises(service: CardsService, collection_id: int) -> None:
    with pytest.raises(CardsError, match="card_number"):
        service.create(_card(collection_id, card_number=-1))


def test_create_with_unknown_collection_raises(service: CardsService) -> None:
    with pytest.raises(CardsError, match="collection"):
        service.create(_card(999))


def test_create_duplicate_business_key_raises(service: CardsService, collection_id: int) -> None:
    service.create(_card(collection_id, code_id="X", card_number=1))
    with pytest.raises(CardsError, match="ya existe"):
        service.create(_card(collection_id, code_id="X", card_number=1))


def test_lookup_returns_card(service: CardsService, collection_id: int) -> None:
    service.create(_card(collection_id, code_id="A", card_number=10))
    fetched = service.lookup(collection_id, "A", 10)
    assert fetched is not None


def test_lookup_returns_none_for_missing(service: CardsService, collection_id: int) -> None:
    assert service.lookup(collection_id, "X", 999) is None


def test_get_by_id_returns_none_for_missing(service: CardsService) -> None:
    assert service.get_by_id(999) is None


def test_list_by_code_filters(service: CardsService, collection_id: int) -> None:
    service.create(_card(collection_id, code_id="A", card_number=1))
    service.create(_card(collection_id, code_id="B", card_number=1))
    items = service.list_by_code(collection_id, "A")
    assert len(items) == 1
    assert items[0].code_id == "A"


def test_find_by_number_returns_matches(service: CardsService, collection_id: int) -> None:
    service.create(_card(collection_id, code_id="A", card_number=10))
    service.create(_card(collection_id, code_id="B", card_number=10))
    matches = service.find_by_number(collection_id, 10)
    assert len(matches) == 2


def test_count_by_collection(service: CardsService, collection_id: int) -> None:
    assert service.count(collection_id) == 0
    service.create(_card(collection_id, card_number=1))
    assert service.count(collection_id) == 1


def test_upsert_inserts_and_updates(service: CardsService, collection_id: int) -> None:
    service.upsert(_card(collection_id, card_number=1, card_name="V1"))
    service.upsert(_card(collection_id, card_number=1, card_name="V2"))
    fetched = service.lookup(collection_id, "X", 1)
    assert fetched is not None
    assert fetched.card_name == "V2"


def test_bulk_upsert_returns_count(service: CardsService, collection_id: int) -> None:
    cards = [_card(collection_id, card_number=i) for i in range(1, 6)]
    assert service.bulk_upsert(cards) == 5


def test_bulk_upsert_empty_list(service: CardsService) -> None:
    assert service.bulk_upsert([]) == 0


def test_bulk_upsert_validates_each_card(service: CardsService, collection_id: int) -> None:
    """Una card invalida en el batch falla todo el batch antes de tocar la DB."""
    cards = [
        _card(collection_id, card_number=1, card_name="Good"),
        _card(collection_id, card_number=0, card_name="Bad"),
    ]
    with pytest.raises(CardsError, match="card_number"):
        service.bulk_upsert(cards)
    # Ninguna se persistió.
    assert service.count(collection_id) == 0


def test_delete_by_id_returns_true(service: CardsService, collection_id: int) -> None:
    saved = service.create(_card(collection_id, card_number=1))
    assert saved.card_id is not None
    assert service.delete_by_id(saved.card_id) is True


def test_delete_by_id_returns_false_when_missing(service: CardsService) -> None:
    assert service.delete_by_id(999) is False


def test_get_stats_by_code_returns_aggregates(service: CardsService, collection_id: int) -> None:
    service.create(_card(collection_id, code_id="ARG", card_number=1))
    stats = service.get_stats_by_code(collection_id)
    assert all(isinstance(s, CodeStats) for s in stats)
    assert len(stats) == 1
