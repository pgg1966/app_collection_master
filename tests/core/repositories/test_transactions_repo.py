"""Tests del TransactionsRepository."""

from datetime import datetime, timedelta

from collections_app.core.models import OperationType, Transaction
from collections_app.core.repositories import TransactionsRepository


def _txn(cid: int, op: OperationType = OperationType.ALTA, qty: int = 1) -> Transaction:
    return Transaction(
        transaction_id=None,
        collection_id=cid,
        code_id="ARG",
        card_number=1,
        operation=op,
        quantity=qty,
        transaction_date=datetime.now(),
    )


def test_log_returns_with_id_and_date(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    saved = repo.log(_txn(sample_collection.collection_id))
    assert saved.transaction_id is not None
    assert isinstance(saved.transaction_date, datetime)
    assert saved.operation == OperationType.ALTA


def test_log_preserves_operation_type(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    saved = repo.log(_txn(sample_collection.collection_id, OperationType.BAJA))
    assert saved.operation == OperationType.BAJA


def test_list_by_collection_descending(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(3):
        repo.log(_txn(cid))
    txns = repo.list_by_collection(cid)
    assert len(txns) == 3
    ids = [t.transaction_id for t in txns]
    assert ids == sorted(ids, reverse=True)


def test_list_by_collection_respects_limit(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(5):
        repo.log(_txn(cid))
    txns = repo.list_by_collection(cid, limit=2)
    assert len(txns) == 2


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_recent(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(3):
        repo.log(_txn(cid))
    recent = repo.list_recent(limit=2)
    assert len(recent) == 2


def test_list_recent_default_limit(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(25):
        repo.log(_txn(cid))
    recent = repo.list_recent()
    assert len(recent) == 20  # default limit


def test_list_by_date_range(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    # Rango amplio para tolerar TZ: SQLite usa UTC, datetime.now() es local.
    now = datetime.now()
    txns = repo.list_by_date_range(now - timedelta(days=1), now + timedelta(days=1))
    assert len(txns) == 1


def test_list_by_date_range_excludes_outside(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    future_start = datetime.now() + timedelta(days=2)
    future_end = datetime.now() + timedelta(days=3)
    assert repo.list_by_date_range(future_start, future_end) == []


def test_list_by_date_range_filtered_by_collection(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    now = datetime.now()
    same_collection = repo.list_by_date_range(
        now - timedelta(days=1), now + timedelta(days=1), collection_id=cid
    )
    other_collection = repo.list_by_date_range(
        now - timedelta(days=1), now + timedelta(days=1), collection_id=999
    )
    assert len(same_collection) == 1
    assert other_collection == []
