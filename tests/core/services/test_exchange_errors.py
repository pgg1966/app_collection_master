"""Sanity tests de la jerarquía de excepciones del subsistema de pairing."""

from __future__ import annotations

from collections_app.services.exceptions import ServiceError
from collections_app.services.exchange_errors import (
    CollectionNotFound,
    ExchangeError,
    InsufficientInventory,
    InvalidExchangeFile,
    UnsupportedFormatVersion,
)


def test_exchange_error_inherits_from_service_error() -> None:
    assert issubclass(ExchangeError, ServiceError)


def test_subclasses_inherit_from_exchange_error() -> None:
    for cls in (
        InvalidExchangeFile,
        CollectionNotFound,
        UnsupportedFormatVersion,
        InsufficientInventory,
    ):
        assert issubclass(cls, ExchangeError)
        assert issubclass(cls, ServiceError)


def test_can_raise_and_catch_at_each_level() -> None:
    """Confirma que el caller puede atrapar a cualquier nivel."""
    try:
        raise InvalidExchangeFile("archivo corrupto")
    except ServiceError as exc:
        assert isinstance(exc, ExchangeError)
        assert isinstance(exc, InvalidExchangeFile)
        assert str(exc) == "archivo corrupto"
