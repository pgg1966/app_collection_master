"""Tests de InventoryService — validación de invariante quantity >= 0.

El service envuelve `InventoryRepository.adjust_quantity` chequeando que
`current + delta >= 0` antes de tocar la DB. Si la suma quedaría
negativa, lanza `InventoryError` y no muta nada.
"""

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
from collections_app.services.exceptions import InventoryError, ServiceError
from collections_app.services.inventory_service import InventoryService


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


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> InventoryService:
    return InventoryService(db_conn)


# ---------------------------------------------------------------------
# Casos válidos: el delta deja quantity >= 0
# ---------------------------------------------------------------------


def test_positive_delta_from_zero_creates_entry(service: InventoryService, card_id: int) -> None:
    item = service.adjust_quantity(card_id, 3)
    assert item.quantity == 3
    assert item.card_id == card_id


def test_positive_delta_from_existing_increments(
    service: InventoryService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=card_id, quantity=5)
    )
    item = service.adjust_quantity(card_id, 2)
    assert item.quantity == 7


def test_delta_landing_exactly_at_zero_is_allowed(
    service: InventoryService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    """qty=0 es válido; el invariante es >= 0, no > 0."""
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=card_id, quantity=3)
    )
    item = service.adjust_quantity(card_id, -3)
    assert item.quantity == 0


def test_zero_delta_without_entry_creates_zero_quantity(
    service: InventoryService, card_id: int
) -> None:
    item = service.adjust_quantity(card_id, 0)
    assert item.quantity == 0


# ---------------------------------------------------------------------
# Casos inválidos: el delta dejaría quantity < 0
# ---------------------------------------------------------------------


def test_delta_to_negative_raises_inventory_error_and_keeps_db_unchanged(
    service: InventoryService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    """Test #4 robusto: estado inicial=5, delta=-10, raise, qty sigue 5."""
    repo = InventoryRepository(db_conn)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=5))

    with pytest.raises(InventoryError):
        service.adjust_quantity(card_id, -10)

    # Verificación explícita post-raise: la DB no cambió.
    after = repo.get_by_card_id(card_id)
    assert after is not None
    assert after.quantity == 5


def test_negative_delta_without_entry_raises_inventory_error(
    service: InventoryService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    """Sin entry previa, current_qty=0; cualquier delta<0 viola la invariante."""
    repo = InventoryRepository(db_conn)

    with pytest.raises(InventoryError):
        service.adjust_quantity(card_id, -1)

    # No se creó entry: get_by_card_id sigue None.
    assert repo.get_by_card_id(card_id) is None


# ---------------------------------------------------------------------
# Forma del error
# ---------------------------------------------------------------------


def test_inventory_error_message_includes_context(
    service: InventoryService, card_id: int, db_conn: sqlite3.Connection
) -> None:
    """El mensaje debe incluir card_id, current_qty y delta para debug."""
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=card_id, quantity=2)
    )
    with pytest.raises(InventoryError) as exc_info:
        service.adjust_quantity(card_id, -5)

    msg = str(exc_info.value)
    assert str(card_id) in msg
    assert "2" in msg  # current_qty
    assert "-5" in msg  # delta


def test_inventory_error_subclasses_service_error(service: InventoryService, card_id: int) -> None:
    """Permite catch genérico de ServiceError en callers."""
    with pytest.raises(ServiceError):
        service.adjust_quantity(card_id, -1)
