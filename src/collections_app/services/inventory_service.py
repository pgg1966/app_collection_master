"""Service de inventario — facade del loader y reglas de negocio.

Conviven dos responsabilidades en este service:

1. **Reglas de negocio puras de inventario**: `adjust_quantity` con la
   invariante `quantity >= 0` (CLAUDE.md sec 4: excepciones de dominio
   por service; el schema NO tiene `CHECK` porque la regla vive acá).

2. **Facade del flujo de carga rápida** que consume la vista preservada
   `CardLoaderView` (ver legacy/v0_1/preserved/README.md). La vista
   recibe **un solo service** y delega en él toda interacción con cards,
   inventory, codes_lines y transactions. Esto justifica que
   InventoryService instancie internamente los repos de cards,
   codes_lines y transactions: es composición de loader workflow, no
   acoplamiento accidental.

`add_card` y `remove_card` registran simultáneamente la mutación en
`inventory` y un `Transaction` en `transactions`. Ambos writes van en
una transacción SQL atómica (`with self._conn`): si una falla,
rollback total. `exchange_event_id=NULL` en este flujo (los movimientos
de intercambio van por otro path con `exchange_event_id` no nulo —
fuera de scope de Prompt 2).
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from collections_app.core.models.card import Card
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services.exceptions import (
    AmbiguousCardError,
    InventoryError,
)


def _utc_now_naive() -> datetime:
    """UTC actual sin tzinfo, para matchear el formato del default SQL `datetime('now')`."""
    return datetime.now(UTC).replace(tzinfo=None)


class InventoryService:
    """Reglas de negocio del inventario + facade del loader workflow."""

    def __init__(self: InventoryService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._inventory = InventoryRepository(conn)
        self._cards = CardsRepository(conn)
        self._code_lines = CodeLinesRepository(conn)
        self._transactions = TransactionsRepository(conn)

    # ------------------------------------------------------------------
    # Reglas puras de inventario
    # ------------------------------------------------------------------

    def adjust_quantity(self: InventoryService, card_id: int, delta: int) -> InventoryItem:
        """Suma `delta` a la quantity de `card_id` validando >= 0.

        Si la suma quedara negativa, lanza `InventoryError` y NO toca
        la DB. Si no había entry previa, current_qty se trata como 0.

        NOTE: read-then-write pattern. Safe in single-connection SQLite,
        but would need a transaction with row lock if migrated to
        multi-user backend (v1.0 cloud).
        """
        current = self._inventory.get_by_card_id(card_id)
        current_qty = current.quantity if current else 0
        new_qty = current_qty + delta
        if new_qty < 0:
            raise InventoryError(
                f"quantity quedaria negativo: card_id={card_id}, "
                f"current={current_qty}, delta={delta}"
            )
        return self._inventory.adjust_quantity(card_id, delta)

    # ------------------------------------------------------------------
    # Lookups que la vista necesita (facade)
    # ------------------------------------------------------------------

    def lookup_card(
        self: InventoryService,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> Card | None:
        """Card por business key, o None."""
        return self._cards.get(collection_id, code_id, card_number)

    def find_cards_by_number(
        self: InventoryService, collection_id: int, card_number: int
    ) -> list[Card]:
        """Cards de la colección con ese número (sin filtrar code_id)."""
        return self._cards.find_by_number(collection_id, card_number)

    def get_inventory_for_card(
        self: InventoryService,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> InventoryItem | None:
        """Inventory item por business key.

        En v0.2 inventory está normalizado por card_id, así que se
        resuelve la card primero y después se lee inventory.
        """
        card = self._cards.get(collection_id, code_id, card_number)
        if card is None or card.card_id is None:
            return None
        return self._inventory.get_by_card_id(card.card_id)

    def list_codes_for_collection(self: InventoryService, collection: Collection) -> list[CodeLine]:
        """Códigos válidos del header de la colección, ordenados por code_order."""
        return self._code_lines.list_by_header(collection.code_header_id)

    def lookup_code_name(self: InventoryService, code_header_id: int, code_id: str) -> str:
        """Nombre legible de un code_id, con fallback al code_id si no hay línea."""
        line = self._code_lines.get(code_header_id, code_id)
        return line.code_name if line else code_id

    # ------------------------------------------------------------------
    # Reads agregados sobre el inventario
    # ------------------------------------------------------------------

    def list_owned(self: InventoryService, collection_id: int) -> list[InventoryItem]:
        return self._inventory.list_owned(collection_id)

    def list_missing(self: InventoryService, collection_id: int) -> list[Card]:
        return self._inventory.list_missing(collection_id)

    def list_duplicates(self: InventoryService, collection_id: int) -> list[InventoryItem]:
        return self._inventory.list_duplicates(collection_id)

    def get_top_duplicates(
        self: InventoryService, collection_id: int, limit: int = 10
    ) -> list[InventoryItem]:
        return self._inventory.get_top_duplicates(collection_id, limit)

    # ------------------------------------------------------------------
    # Mutaciones del flujo de carga rápida (alta / baja)
    # ------------------------------------------------------------------

    def add_card(
        self: InventoryService,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int,
    ) -> InventoryItem:
        """Alta de stock: incrementa inventory y registra Transaction.

        Atómico: ambos writes (UPSERT inventory + INSERT transactions)
        van en la misma transacción SQL. Si una falla, rollback total.
        """
        if quantity <= 0:
            raise InventoryError(f"quantity debe ser > 0 (recibido: {quantity})")
        card = self._cards.get(collection_id, code_id, card_number)
        if card is None or card.card_id is None:
            raise InventoryError(f"card ({collection_id}, {code_id!r}, {card_number}) no existe")
        return self._apply_movement(card.card_id, OperationType.ALTA, quantity)

    def remove_card(
        self: InventoryService,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int,
    ) -> InventoryItem:
        """Baja de stock: decrementa inventory y registra Transaction.

        Falla con `InventoryError` si no hay inventory previo o si la
        quantity actual es menor que `quantity`. Atómico igual que add.
        """
        if quantity <= 0:
            raise InventoryError(f"quantity debe ser > 0 (recibido: {quantity})")
        card = self._cards.get(collection_id, code_id, card_number)
        if card is None or card.card_id is None:
            raise InventoryError(f"card ({collection_id}, {code_id!r}, {card_number}) no existe")
        existing = self._inventory.get_by_card_id(card.card_id)
        if existing is None:
            raise InventoryError(
                f"no hay inventario para card_id={card.card_id} ({code_id}-{card_number})"
            )
        if existing.quantity < quantity:
            raise InventoryError(
                f"stock insuficiente: hay {existing.quantity}, se piden {quantity}"
            )
        return self._apply_movement(card.card_id, OperationType.BAJA, quantity)

    def add_card_by_number(
        self: InventoryService,
        collection_id: int,
        card_number: int,
        quantity: int,
    ) -> InventoryItem:
        """Alta resolviendo el código vía búsqueda por número.

        Lanza `InventoryError` si no hay matches y `AmbiguousCardError`
        si hay >1, para que la UI muestre disambiguation.
        """
        card = self._resolve_unique_by_number(collection_id, card_number)
        return self.add_card(collection_id, card.code_id, card_number, quantity)

    def remove_card_by_number(
        self: InventoryService,
        collection_id: int,
        card_number: int,
        quantity: int,
    ) -> InventoryItem:
        """Baja resolviendo el código vía búsqueda por número."""
        card = self._resolve_unique_by_number(collection_id, card_number)
        return self.remove_card(collection_id, card.code_id, card_number, quantity)

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _resolve_unique_by_number(
        self: InventoryService, collection_id: int, card_number: int
    ) -> Card:
        """Busca cards por número. 0 → InventoryError; 1 → Card; >1 → AmbiguousCardError."""
        matches = self._cards.find_by_number(collection_id, card_number)
        if not matches:
            raise InventoryError(
                f"card numero {card_number} no existe en collection {collection_id}"
            )
        if len(matches) > 1:
            raise AmbiguousCardError(matches)
        return matches[0]

    def _apply_movement(
        self: InventoryService,
        card_id: int,
        operation: OperationType,
        quantity: int,
    ) -> InventoryItem:
        """Aplica el delta a inventory y registra la transaction, atómicamente.

        El context manager `with self._conn` commitea al salir limpio
        y hace rollback si se eleva una excepción dentro del bloque.
        """
        delta = quantity if operation is OperationType.ALTA else -quantity
        with self._conn:
            updated = self._inventory.adjust_quantity(card_id, delta)
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    card_id=card_id,
                    operation=operation,
                    quantity=quantity,
                    transaction_date=_utc_now_naive(),
                    exchange_event_id=None,
                )
            )
        return updated
