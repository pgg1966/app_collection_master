"""Repository para la tabla transactions."""

import sqlite3
from datetime import datetime

from collections_app.core.models import OperationType, Transaction
from collections_app.core.repositories.base import BaseRepository
from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    parse_db_datetime,
)


def _row_to_transaction(row: sqlite3.Row) -> Transaction:
    return Transaction(
        transaction_id=row["transaction_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        operation=OperationType(row["operation"]),
        quantity=row["quantity"],
        transaction_date=parse_db_datetime(row["transaction_date"]),
    )


_SELECT_COLS = (
    "transaction_id, collection_id, code_id, card_number, " "operation, quantity, transaction_date"
)


class TransactionsRepository(BaseRepository):
    """Bitácora de operaciones (alta/baja) sobre el inventario."""

    def log(self, txn: Transaction) -> Transaction:
        """Inserta una transacción.

        El `transaction_id` y `transaction_date` del input son ignorados — se
        asignan en la DB.

        Returns:
            La transacción persistida con id y fecha reales.
        """
        cursor = self.conn.execute(
            "INSERT INTO transactions "
            "(collection_id, code_id, card_number, operation, quantity) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                txn.collection_id,
                txn.code_id,
                txn.card_number,
                txn.operation.value,
                txn.quantity,
            ),
        )
        new_id = cursor.lastrowid
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions WHERE transaction_id = ?",  # noqa: S608
            (new_id,),
        ).fetchone()
        return _row_to_transaction(row)

    def list_by_collection(self, collection_id: int, limit: int = 100) -> list[Transaction]:
        """Transacciones de una colección, las más recientes primero."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
            "WHERE collection_id = ? "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_transaction(r) for r in rows]

    def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        collection_id: int | None = None,
    ) -> list[Transaction]:
        """Transacciones en un rango [start, end] inclusivo, opcionalmente filtradas.

        `start` y `end` se convierten a UTC antes de comparar contra los
        timestamps de la DB (también UTC).
        """
        start_str = format_for_db(start)
        end_str = format_for_db(end)
        if collection_id is None:
            rows = self.conn.execute(
                f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
                "WHERE transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (start_str, end_str),
            ).fetchall()
        else:
            rows = self.conn.execute(
                f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
                "WHERE collection_id = ? AND transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (collection_id, start_str, end_str),
            ).fetchall()
        return [_row_to_transaction(r) for r in rows]

    def list_recent(self, limit: int = 20) -> list[Transaction]:
        """Las N transacciones más recientes globalmente."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (limit,),
        ).fetchall()
        return [_row_to_transaction(r) for r in rows]
