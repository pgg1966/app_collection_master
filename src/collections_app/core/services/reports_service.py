"""Servicio de reportes: transacciones con info de la card asociada.

Las queries se hacen con un único JOIN entre `transactions` y `cards`
para evitar N+1 al armar la grilla del reporte.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from collections_app.core.models import OperationType
from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    parse_db_datetime,
)


@dataclass(frozen=True)
class TransactionWithCard:
    """Transacción enriquecida con el nombre de la card afectada."""

    transaction_date: datetime
    operation: OperationType
    code_id: str
    card_number: int
    card_name: str
    quantity: int


class ReportsService:
    """Queries optimizadas para el tab de reportes."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_transactions_in_period(
        self,
        collection_id: int,
        start: datetime,
        end: datetime,
        operation: OperationType | None = None,
    ) -> list[TransactionWithCard]:
        """Retorna transacciones del rango con el nombre de la card.

        `start` y `end` se convierten a UTC antes de filtrar. Si la card
        del registro fue borrada del catálogo, `card_name` será una cadena
        vacía (LEFT JOIN preserva la transacción aunque no exista la card).
        """
        start_str = format_for_db(start)
        end_str = format_for_db(end)
        params: list[object] = [collection_id, start_str, end_str]
        sql = (
            "SELECT t.transaction_date AS transaction_date, "
            "       t.operation AS operation, "
            "       t.code_id AS code_id, "
            "       t.card_number AS card_number, "
            "       COALESCE(c.card_name, '') AS card_name, "
            "       t.quantity AS quantity "
            "FROM transactions t "
            "LEFT JOIN cards c "
            "  ON c.collection_id = t.collection_id "
            " AND c.code_id = t.code_id "
            " AND c.card_number = t.card_number "
            "WHERE t.collection_id = ? "
            "  AND t.transaction_date BETWEEN ? AND ? "
        )
        if operation is not None:
            sql += "  AND t.operation = ? "
            params.append(operation.value)
        sql += "ORDER BY t.transaction_date DESC, t.transaction_id DESC"

        rows = self.conn.execute(sql, params).fetchall()
        return [
            TransactionWithCard(
                transaction_date=parse_db_datetime(r["transaction_date"]),
                operation=OperationType(r["operation"]),
                code_id=r["code_id"],
                card_number=r["card_number"],
                card_name=r["card_name"],
                quantity=r["quantity"],
            )
            for r in rows
        ]
