"""Repositorio para `transactions`."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.base import BaseRepository


def _row_to_txn(row: sqlite3.Row) -> Transaction:
    return Transaction(
        transaction_id=row["transaction_id"],
        card_id=row["card_id"],
        operation=OperationType(row["operation"]),
        quantity=row["quantity"],
        transaction_date=datetime.fromisoformat(row["transaction_date"]),
        exchange_event_id=row["exchange_event_id"],
    )


class TransactionsRepository(BaseRepository):
    """Bitácora de operaciones (alta/baja) sobre el inventario.

    FK granular a `card_id` (sec 2.5). Cada `log()` persiste el ISO del
    `transaction_date`; el repo lo parsea de vuelta en lecturas.
    `exchange_event_id` agrupa transacciones de un mismo intercambio.
    """

    def log(self: TransactionsRepository, txn: Transaction) -> Transaction:
        """Inserta una transacción y la retorna con `transaction_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO transactions "
            "(card_id, operation, quantity, transaction_date, exchange_event_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                txn.card_id,
                txn.operation.value,
                txn.quantity,
                txn.transaction_date.isoformat(sep=" "),
                txn.exchange_event_id,
            ),
        )
        return Transaction(
            transaction_id=cursor.lastrowid,
            card_id=txn.card_id,
            operation=txn.operation,
            quantity=txn.quantity,
            transaction_date=txn.transaction_date,
            exchange_event_id=txn.exchange_event_id,
        )

    def list_by_card(
        self: TransactionsRepository, card_id: int, limit: int = 100
    ) -> list[Transaction]:
        """Transacciones de una card, las más recientes primero."""
        rows = self.conn.execute(
            "SELECT transaction_id, card_id, operation, quantity, "
            "       transaction_date, exchange_event_id "
            "FROM transactions WHERE card_id = ? "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (card_id, limit),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_by_collection(
        self: TransactionsRepository,
        collection_id: int,
        limit: int = 100,
    ) -> list[Transaction]:
        """Transacciones de cards de la colección, recientes primero."""
        rows = self.conn.execute(
            "SELECT t.transaction_id, t.card_id, t.operation, t.quantity, "
            "       t.transaction_date, t.exchange_event_id "
            "FROM transactions t "
            "INNER JOIN cards c ON c.card_id = t.card_id "
            "WHERE c.collection_id = ? "
            "ORDER BY t.transaction_date DESC, t.transaction_id DESC "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_recent(self: TransactionsRepository, limit: int = 20) -> list[Transaction]:
        """Las N transacciones más recientes globalmente."""
        rows = self.conn.execute(
            "SELECT transaction_id, card_id, operation, quantity, "
            "       transaction_date, exchange_event_id "
            "FROM transactions "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (limit,),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_by_date_range(
        self: TransactionsRepository,
        start: datetime,
        end: datetime,
        collection_id: int | None = None,
    ) -> list[Transaction]:
        """Transacciones en `[start, end]` (inclusivo).

        Si `collection_id` se provee, JOIN con cards y filtra por colección.
        """
        start_str = start.isoformat(sep=" ")
        end_str = end.isoformat(sep=" ")
        if collection_id is None:
            rows = self.conn.execute(
                "SELECT transaction_id, card_id, operation, quantity, "
                "       transaction_date, exchange_event_id "
                "FROM transactions "
                "WHERE transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (start_str, end_str),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT t.transaction_id, t.card_id, t.operation, t.quantity, "
                "       t.transaction_date, t.exchange_event_id "
                "FROM transactions t "
                "INNER JOIN cards c ON c.card_id = t.card_id "
                "WHERE t.transaction_date BETWEEN ? AND ? "
                "  AND c.collection_id = ? "
                "ORDER BY t.transaction_date DESC, t.transaction_id DESC",
                (start_str, end_str, collection_id),
            ).fetchall()
        return [_row_to_txn(r) for r in rows]
