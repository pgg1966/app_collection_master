"""Tests CRUD + queries de TransactionsRepository."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> TransactionsRepository:
    return TransactionsRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


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


def _make_txn(
    card_id: int,
    operation: OperationType = OperationType.ALTA,
    quantity: int = 1,
    when: datetime | None = None,
    exchange_event_id: int | None = None,
) -> Transaction:
    return Transaction(
        transaction_id=None,
        card_id=card_id,
        operation=operation,
        quantity=quantity,
        transaction_date=when or datetime(2026, 5, 5, 12, 0, 0),
        exchange_event_id=exchange_event_id,
    )


def test_log_returns_txn_with_id_populated(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.log(_make_txn(card_id))
    assert saved.transaction_id is not None
    assert saved.card_id == card_id


def test_log_violates_quantity_check_when_zero(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    with pytest.raises(sqlite3.IntegrityError):
        repo.log(_make_txn(card_id, quantity=0))


def test_log_violates_fk_when_card_not_exists(
    repo: TransactionsRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.log(_make_txn(999))


def test_log_persists_exchange_event_id(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.log(_make_txn(card_id, exchange_event_id=77))
    assert saved.exchange_event_id == 77
    assert saved.transaction_id is not None
    fetched = repo.list_by_card(card_id)
    assert fetched[0].exchange_event_id == 77


def test_list_by_card_returns_transactions_desc(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, quantity=1, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(card_id, quantity=2, when=datetime(2026, 5, 3)))
    repo.log(_make_txn(card_id, quantity=3, when=datetime(2026, 5, 2)))
    items = repo.list_by_card(card_id)
    assert [t.quantity for t in items] == [2, 3, 1]


def test_list_by_card_respects_limit(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    for i in range(5):
        repo.log(_make_txn(card_id, when=datetime(2026, 5, i + 1)))
    items = repo.list_by_card(card_id, limit=3)
    assert len(items) == 3


def test_list_by_collection_joins_cards(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
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
    repo.log(_make_txn(a))
    repo.log(_make_txn(b))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_recent_globally_returns_most_recent_first(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.log(_make_txn(a, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(b, when=datetime(2026, 5, 5)))
    repo.log(_make_txn(a, when=datetime(2026, 5, 3)))
    items = repo.list_recent(limit=10)
    dates = [t.transaction_date for t in items]
    assert dates == sorted(dates, reverse=True)


def test_list_by_date_range_inclusive(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 5)))
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 10)))
    items = repo.list_by_date_range(start=datetime(2026, 5, 5), end=datetime(2026, 5, 10))
    assert len(items) == 2


def test_list_by_date_range_filters_by_collection_when_provided(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
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
    when = datetime(2026, 5, 5)
    repo.log(_make_txn(a, when=when))
    repo.log(_make_txn(b, when=when))
    items = repo.list_by_date_range(
        start=datetime(2026, 5, 1),
        end=datetime(2026, 5, 31),
        collection_id=collection_id,
    )
    assert len(items) == 1
    assert items[0].card_id == a


def test_log_round_trips_operation_type(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, operation=OperationType.ALTA))
    repo.log(_make_txn(card_id, operation=OperationType.BAJA))
    items = repo.list_by_card(card_id)
    ops = {t.operation for t in items}
    assert OperationType.ALTA in ops
    assert OperationType.BAJA in ops
    assert all(isinstance(t.operation, OperationType) for t in items)


def test_log_round_trips_datetime(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    when = datetime(2026, 5, 5, 14, 30, 0)
    repo.log(_make_txn(card_id, when=when))
    items = repo.list_by_card(card_id)
    assert items[0].transaction_date == when


def test_card_delete_does_not_break_transactions(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    """transactions.card_id no tiene ON DELETE CASCADE: borrar la card
    levanta IntegrityError porque la transaccion sigue referenciandola.
    Esa es la decision: las bitacoras no se borran al borrar cards.
    """
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id))
    with pytest.raises(sqlite3.IntegrityError):
        cards_repo.delete_by_id(card_id)


def test_list_by_collection_respects_limit(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    base = datetime(2026, 5, 1)
    for i in range(5):
        repo.log(_make_txn(card_id, when=base + timedelta(days=i)))
    items = repo.list_by_collection(collection_id, limit=2)
    assert len(items) == 2
