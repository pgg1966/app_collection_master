"""Tests del dataclass Transaction y OperationType."""

from __future__ import annotations

from datetime import datetime

from collections_app.core.models.transaction import OperationType, Transaction


def test_operation_type_values() -> None:
    assert OperationType.ALTA.value == "alta"
    assert OperationType.BAJA.value == "baja"


def test_operation_type_str_enum_compat() -> None:
    """OperationType es StrEnum: comparable a strings sin .value."""
    assert OperationType.ALTA == "alta"
    assert OperationType.BAJA == "baja"


def test_transaction_minimal_fields() -> None:
    txn = Transaction(
        transaction_id=None,
        card_id=1,
        operation=OperationType.ALTA,
        quantity=2,
        transaction_date=datetime(2026, 5, 5, 12, 0, 0),
    )
    assert txn.exchange_event_id is None  # default


def test_transaction_with_exchange_event_id() -> None:
    txn = Transaction(
        transaction_id=None,
        card_id=1,
        operation=OperationType.BAJA,
        quantity=1,
        transaction_date=datetime(2026, 5, 5),
        exchange_event_id=42,
    )
    assert txn.exchange_event_id == 42
