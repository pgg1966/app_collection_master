"""Tests del workflow de loader de InventoryService.

Cubre los métodos agregados en Prompt 2 (lookups + add_card / remove_card
con logging atómico). Los tests de `adjust_quantity` viven en
`test_inventory_service.py` y siguen siendo la red de seguridad de la
invariante quantity >= 0.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.models.transaction import OperationType
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services.exceptions import (
    AmbiguousCardError,
    InventoryError,
)
from collections_app.services.inventory_service import InventoryService


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> InventoryService:
    return InventoryService(db_conn)


@pytest.fixture
def setup(db_conn: sqlite3.Connection) -> dict[str, int]:
    """Seedea header + colección + 3 cards. Retorna ids útiles."""
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    CodeLinesRepository(db_conn).upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="ARG",
            code_name="Argentina",
        )
    )
    CodeLinesRepository(db_conn).upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="BRA",
            code_name="Brasil",
        )
    )
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="World",
            card_count=10,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    cards_repo = CardsRepository(db_conn)
    arg1 = cards_repo.create(
        Card(
            card_id=None,
            collection_id=c.collection_id,
            code_id="ARG",
            card_number=1,
            card_name="Messi",
        )
    )
    arg2 = cards_repo.create(
        Card(
            card_id=None,
            collection_id=c.collection_id,
            code_id="ARG",
            card_number=2,
            card_name="Di María",
        )
    )
    bra1 = cards_repo.create(
        Card(
            card_id=None,
            collection_id=c.collection_id,
            code_id="BRA",
            card_number=1,
            card_name="Vinicius",
        )
    )
    assert arg1.card_id and arg2.card_id and bra1.card_id
    return {
        "header_id": h.code_header_id,
        "collection_id": c.collection_id,
        "arg1_card_id": arg1.card_id,
        "arg2_card_id": arg2.card_id,
        "bra1_card_id": bra1.card_id,
    }


# ---------------------------------------------------------------------
# Lookups facade
# ---------------------------------------------------------------------


def test_lookup_card_returns_card(service: InventoryService, setup: dict[str, int]) -> None:
    card = service.lookup_card(setup["collection_id"], "ARG", 1)
    assert card is not None
    assert card.card_name == "Messi"


def test_lookup_card_returns_none_for_missing(
    service: InventoryService, setup: dict[str, int]
) -> None:
    assert service.lookup_card(setup["collection_id"], "ZZZ", 1) is None


def test_find_cards_by_number(service: InventoryService, setup: dict[str, int]) -> None:
    matches = service.find_cards_by_number(setup["collection_id"], 1)
    # ARG-1 y BRA-1
    assert len(matches) == 2


def test_get_inventory_for_card_returns_none_without_inventory(
    service: InventoryService, setup: dict[str, int]
) -> None:
    assert service.get_inventory_for_card(setup["collection_id"], "ARG", 1) is None


def test_get_inventory_for_card_returns_none_for_missing_card(
    service: InventoryService, setup: dict[str, int]
) -> None:
    assert service.get_inventory_for_card(setup["collection_id"], "ZZZ", 99) is None


def test_get_inventory_for_card_returns_item(
    service: InventoryService, setup: dict[str, int]
) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 3)
    item = service.get_inventory_for_card(setup["collection_id"], "ARG", 1)
    assert item is not None
    assert item.quantity == 3


def test_list_codes_for_collection(
    service: InventoryService,
    setup: dict[str, int],
    db_conn: sqlite3.Connection,
) -> None:
    coll = CollectionsRepository(db_conn).get_by_id(setup["collection_id"])
    assert coll is not None
    codes = service.list_codes_for_collection(coll)
    assert {c.code_id for c in codes} == {"ARG", "BRA"}


def test_lookup_code_name_returns_name(service: InventoryService, setup: dict[str, int]) -> None:
    assert service.lookup_code_name(setup["header_id"], "ARG") == "Argentina"


def test_lookup_code_name_falls_back_to_code_id(
    service: InventoryService, setup: dict[str, int]
) -> None:
    """Comportamiento preservado del helper de la vista legacy."""
    assert service.lookup_code_name(setup["header_id"], "GHOST") == "GHOST"


# ---------------------------------------------------------------------
# Reads agregados de inventario
# ---------------------------------------------------------------------


def test_list_owned_excludes_zero_quantity(
    service: InventoryService,
    setup: dict[str, int],
    db_conn: sqlite3.Connection,
) -> None:
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=setup["arg1_card_id"], quantity=2)
    )
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=setup["arg2_card_id"], quantity=0)
    )
    owned = service.list_owned(setup["collection_id"])
    assert len(owned) == 1
    assert owned[0].card_id == setup["arg1_card_id"]


def test_list_missing_includes_cards_without_inventory(
    service: InventoryService, setup: dict[str, int]
) -> None:
    missing = service.list_missing(setup["collection_id"])
    assert len(missing) == 3  # ninguna tiene inventory


def test_list_duplicates_above_one(service: InventoryService, setup: dict[str, int]) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 5)
    service.add_card(setup["collection_id"], "ARG", 2, 1)
    dups = service.list_duplicates(setup["collection_id"])
    assert len(dups) == 1
    assert dups[0].card_id == setup["arg1_card_id"]


def test_get_top_duplicates(service: InventoryService, setup: dict[str, int]) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 5)
    service.add_card(setup["collection_id"], "BRA", 1, 3)
    top = service.get_top_duplicates(setup["collection_id"], limit=10)
    quantities = [t.quantity for t in top]
    assert quantities == sorted(quantities, reverse=True)


# ---------------------------------------------------------------------
# add_card / remove_card — validaciones + atomicidad
# ---------------------------------------------------------------------


def test_add_card_with_qty_zero_raises(service: InventoryService, setup: dict[str, int]) -> None:
    with pytest.raises(InventoryError, match="quantity"):
        service.add_card(setup["collection_id"], "ARG", 1, 0)


def test_add_card_with_negative_qty_raises(
    service: InventoryService, setup: dict[str, int]
) -> None:
    with pytest.raises(InventoryError, match="quantity"):
        service.add_card(setup["collection_id"], "ARG", 1, -1)


def test_add_card_for_unknown_card_raises(service: InventoryService, setup: dict[str, int]) -> None:
    with pytest.raises(InventoryError, match="no existe"):
        service.add_card(setup["collection_id"], "ZZZ", 99, 1)


def test_add_card_increments_inventory(service: InventoryService, setup: dict[str, int]) -> None:
    item = service.add_card(setup["collection_id"], "ARG", 1, 3)
    assert item.quantity == 3
    item2 = service.add_card(setup["collection_id"], "ARG", 1, 2)
    assert item2.quantity == 5


def test_add_card_logs_transaction(
    service: InventoryService,
    setup: dict[str, int],
    db_conn: sqlite3.Connection,
) -> None:
    """add_card escribe una row en transactions con operation='alta'."""
    service.add_card(setup["collection_id"], "ARG", 1, 3)
    txns = TransactionsRepository(db_conn).list_by_card(setup["arg1_card_id"])
    assert len(txns) == 1
    assert txns[0].operation is OperationType.ALTA
    assert txns[0].quantity == 3
    assert txns[0].exchange_event_id is None


def test_remove_card_with_no_inventory_raises(
    service: InventoryService, setup: dict[str, int]
) -> None:
    with pytest.raises(InventoryError, match="no hay inventario"):
        service.remove_card(setup["collection_id"], "ARG", 1, 1)


def test_remove_card_insufficient_stock_raises(
    service: InventoryService, setup: dict[str, int]
) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 2)
    with pytest.raises(InventoryError, match="insuficiente"):
        service.remove_card(setup["collection_id"], "ARG", 1, 5)


def test_remove_card_decrements_inventory(service: InventoryService, setup: dict[str, int]) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 5)
    item = service.remove_card(setup["collection_id"], "ARG", 1, 2)
    assert item.quantity == 3


def test_remove_card_logs_transaction(
    service: InventoryService,
    setup: dict[str, int],
    db_conn: sqlite3.Connection,
) -> None:
    service.add_card(setup["collection_id"], "ARG", 1, 5)
    service.remove_card(setup["collection_id"], "ARG", 1, 2)
    txns = TransactionsRepository(db_conn).list_by_card(setup["arg1_card_id"])
    # Una alta y una baja
    assert {t.operation for t in txns} == {OperationType.ALTA, OperationType.BAJA}


# ---------------------------------------------------------------------
# Atomicidad: si la inserción de la transaction falla, inventory rollbackea
# ---------------------------------------------------------------------


def test_add_card_rolls_back_inventory_when_transaction_log_fails(
    service: InventoryService,
    setup: dict[str, int],
    monkeypatch: pytest.MonkeyPatch,
    db_conn: sqlite3.Connection,
) -> None:
    """Si el log del transaction falla, el inventory cambio debe deshacerse.

    Forzar la falla dentro del bloque `with self._conn` monkeypatcheando
    el repo de transactions del service. Verifica que inventory NO refleja
    el adjust intentado.
    """

    def boom(_txn: object) -> None:
        raise RuntimeError("simulated transactions write failure")

    # Inventario inicial via repo (no service) para tener un baseline conocido.
    # Commit explicito: el seed debe quedar persistido antes de que la
    # transaccion atomica del service haga rollback. Sin esto, el rollback
    # del with conn:` alcanza tambien al upsert previo (todos comparten
    # la transaccion implicita del modulo sqlite3 de Python).
    InventoryRepository(db_conn).upsert(
        InventoryItem(inventory_id=None, card_id=setup["arg1_card_id"], quantity=4)
    )
    db_conn.commit()
    monkeypatch.setattr(service._transactions, "log", boom)

    with pytest.raises(RuntimeError, match="simulated"):
        service.add_card(setup["collection_id"], "ARG", 1, 7)

    # Inventory debe seguir en 4, no en 11.
    item = InventoryRepository(db_conn).get_by_card_id(setup["arg1_card_id"])
    assert item is not None
    assert item.quantity == 4

    # Y no quedaron transactions persistidas tampoco.
    txns = TransactionsRepository(db_conn).list_by_card(setup["arg1_card_id"])
    assert txns == []


# ---------------------------------------------------------------------
# *_by_number: resolución única / 0 matches / ambigüedad
# ---------------------------------------------------------------------


def test_add_card_by_number_resolves_unique(
    service: InventoryService,
    db_conn: sqlite3.Connection,
) -> None:
    """Colección sin requires_code, número único."""
    h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="H2")
    )
    assert h.code_header_id is not None
    coll = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="Solo",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    CardsRepository(db_conn).create(
        Card(
            card_id=None,
            collection_id=coll.collection_id,
            code_id="X",
            card_number=42,
            card_name="Solo-42",
        )
    )
    item = service.add_card_by_number(coll.collection_id, 42, 2)
    assert item.quantity == 2


def test_add_card_by_number_no_match_raises_inventory_error(
    service: InventoryService, setup: dict[str, int]
) -> None:
    with pytest.raises(InventoryError, match="numero"):
        service.add_card_by_number(setup["collection_id"], 999, 1)


def test_add_card_by_number_multiple_matches_raises_ambiguous(
    service: InventoryService, setup: dict[str, int]
) -> None:
    """Numero 1 está en ARG y BRA — no se puede resolver."""
    with pytest.raises(AmbiguousCardError) as exc_info:
        service.add_card_by_number(setup["collection_id"], 1, 1)
    assert len(exc_info.value.matches) == 2


def test_remove_card_by_number_no_match_raises(
    service: InventoryService, setup: dict[str, int]
) -> None:
    with pytest.raises(InventoryError, match="numero"):
        service.remove_card_by_number(setup["collection_id"], 999, 1)


def test_remove_card_by_number_ambiguous_raises(
    service: InventoryService, setup: dict[str, int]
) -> None:
    with pytest.raises(AmbiguousCardError):
        service.remove_card_by_number(setup["collection_id"], 1, 1)
