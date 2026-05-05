"""Service de bitácora de transacciones.

Wrapper sobre `TransactionsRepository`. Validaciones de negocio:
quantity > 0 (también enforced por CHECK en schema), card_id existente,
fecha `start <= end` en consultas por rango.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from collections_app.core.models.transaction import Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services.exceptions import TransactionsError


class TransactionsService:
    """Lógica de negocio sobre `transactions`."""

    def __init__(self: TransactionsService, conn: sqlite3.Connection) -> None:
        self._repo = TransactionsRepository(conn)
        self._cards = CardsRepository(conn)

    def log(self: TransactionsService, txn: Transaction) -> Transaction:
        """Registra una transacción. Valida qty > 0 y card existente."""
        if txn.quantity <= 0:
            raise TransactionsError(f"quantity debe ser > 0, recibido {txn.quantity}")
        if self._cards.get_by_id(txn.card_id) is None:
            raise TransactionsError(f"card_id={txn.card_id} no existe")
        return self._repo.log(txn)

    def list_by_card(
        self: TransactionsService, card_id: int, limit: int = 100
    ) -> list[Transaction]:
        return self._repo.list_by_card(card_id, limit)

    def list_by_collection(
        self: TransactionsService, collection_id: int, limit: int = 100
    ) -> list[Transaction]:
        return self._repo.list_by_collection(collection_id, limit)

    def list_recent(self: TransactionsService, limit: int = 20) -> list[Transaction]:
        return self._repo.list_recent(limit)

    def list_by_date_range(
        self: TransactionsService,
        start: datetime,
        end: datetime,
        collection_id: int | None = None,
    ) -> list[Transaction]:
        """Transacciones en `[start, end]`. Valida orden start <= end."""
        if start > end:
            raise TransactionsError(
                f"start ({start.isoformat()}) debe ser <= end ({end.isoformat()})"
            )
        return self._repo.list_by_date_range(start, end, collection_id)
