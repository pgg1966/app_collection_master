"""Tests de TransactionsService."""

from __future__ import annotations

import sqlite3
from datetime import datetime

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import TransactionsError
from collections_app.services.transactions_service import TransactionsService


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> TransactionsService:
    return TransactionsService(db_conn)


@pytest.fixture
def card_id(db_conn: sqlite3.Connection) -> int:
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
    saved = CardsRepository(db_conn).create(
        Card(
            card_id=None,
            collection_id=c.collection_id,
            code_id="X",
            card_number=1,
            card_name="X-1",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def _txn(
    card_id: int,
    op: OperationType = OperationType.ALTA,
    qty: int = 1,
    when: datetime | None = None,
    exchange_event_id: int | None = None,
) -> Transaction:
    return Transaction(
        transaction_id=None,
        card_id=card_id,
        operation=op,
        quantity=qty,
        transaction_date=when or datetime(2026, 5, 5, 12, 0, 0),
        exchange_event_id=exchange_event_id,
    )


def test_log_returns_transaction_with_id(service: TransactionsService, card_id: int) -> None:
    saved = service.log(_txn(card_id))
    assert saved.transaction_id is not None


def test_log_zero_quantity_raises(service: TransactionsService, card_id: int) -> None:
    with pytest.raises(TransactionsError, match="quantity"):
        service.log(_txn(card_id, qty=0))


def test_log_negative_quantity_raises(service: TransactionsService, card_id: int) -> None:
    with pytest.raises(TransactionsError, match="quantity"):
        service.log(_txn(card_id, qty=-1))


def test_log_unknown_card_raises(service: TransactionsService) -> None:
    with pytest.raises(TransactionsError, match="card"):
        service.log(_txn(999))


def test_log_persists_exchange_event_id(service: TransactionsService, card_id: int) -> None:
    saved = service.log(_txn(card_id, exchange_event_id=42))
    assert saved.exchange_event_id == 42


def test_list_by_card_descending(service: TransactionsService, card_id: int) -> None:
    service.log(_txn(card_id, when=datetime(2026, 5, 1)))
    service.log(_txn(card_id, when=datetime(2026, 5, 5)))
    service.log(_txn(card_id, when=datetime(2026, 5, 3)))
    items = service.list_by_card(card_id)
    dates = [t.transaction_date for t in items]
    assert dates == sorted(dates, reverse=True)


def test_list_by_collection_filter(
    service: TransactionsService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    cid = db_conn.execute(
        "SELECT collection_id FROM cards WHERE card_id = ?", (card_id,)
    ).fetchone()["collection_id"]
    service.log(_txn(card_id))
    items = service.list_by_collection(cid)
    assert len(items) == 1


def test_list_recent(service: TransactionsService, card_id: int) -> None:
    for i in range(3):
        service.log(_txn(card_id, when=datetime(2026, 5, i + 1)))
    items = service.list_recent(limit=5)
    assert len(items) == 3


def test_list_by_date_range_inclusive(service: TransactionsService, card_id: int) -> None:
    service.log(_txn(card_id, when=datetime(2026, 5, 1)))
    service.log(_txn(card_id, when=datetime(2026, 5, 5)))
    service.log(_txn(card_id, when=datetime(2026, 5, 10)))
    items = service.list_by_date_range(start=datetime(2026, 5, 5), end=datetime(2026, 5, 10))
    assert len(items) == 2


def test_list_by_date_range_invalid_order_raises(
    service: TransactionsService,
) -> None:
    with pytest.raises(TransactionsError, match="start"):
        service.list_by_date_range(start=datetime(2026, 5, 10), end=datetime(2026, 5, 1))
