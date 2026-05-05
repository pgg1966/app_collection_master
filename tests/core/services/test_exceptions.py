"""Tests del módulo `services/exceptions.py` — jerarquía de errores."""

from __future__ import annotations

import pytest

from collections_app.core.models.card import Card
from collections_app.services.exceptions import (
    AmbiguousCardError,
    CardsError,
    CodeHeadersError,
    CodeLinesError,
    CollectionsError,
    InventoryError,
    ServiceError,
    SettingsError,
    TransactionsError,
)


@pytest.mark.parametrize(
    "exc_cls",
    [
        InventoryError,
        CollectionsError,
        CardsError,
        CodeHeadersError,
        CodeLinesError,
        TransactionsError,
        SettingsError,
    ],
)
def test_each_service_error_subclasses_service_error(
    exc_cls: type[ServiceError],
) -> None:
    """Patrón sec 4: toda XError hereda de ServiceError."""
    assert issubclass(exc_cls, ServiceError)


def test_ambiguous_card_error_subclasses_inventory_error() -> None:
    """AmbiguousCardError hereda de InventoryError, no de ServiceError directo.

    Permite que `except InventoryError` también la atrape.
    """
    assert issubclass(AmbiguousCardError, InventoryError)
    assert issubclass(AmbiguousCardError, ServiceError)


def test_ambiguous_card_error_holds_matches() -> None:
    cards = [
        Card(card_id=1, collection_id=1, code_id="A", card_number=10, card_name="A-10"),
        Card(card_id=2, collection_id=1, code_id="B", card_number=10, card_name="B-10"),
    ]
    err = AmbiguousCardError(cards)
    assert err.matches == cards
    assert "2" in str(err)  # mensaje incluye la cantidad


def test_service_error_can_catch_any_specific_subclass() -> None:
    """Caller genérico: `except ServiceError` atrapa todas las variantes."""
    with pytest.raises(ServiceError):
        raise CardsError("test")
    with pytest.raises(ServiceError):
        raise SettingsError("test")
    with pytest.raises(ServiceError):
        raise AmbiguousCardError([])
