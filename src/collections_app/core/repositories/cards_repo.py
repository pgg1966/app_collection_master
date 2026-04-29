"""Repository para la tabla cards."""

import sqlite3

from collections_app.core.models import Card
from collections_app.core.repositories.base import BaseRepository


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardsRepository(BaseRepository):
    """CRUD sobre `cards`."""

    def list_by_collection(self, collection_id: int) -> list[Card]:
        """Retorna todas las cards de una colección ordenadas por (code_id, card_number)."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get(self, collection_id: int, code_id: str, card_number: int) -> Card | None:
        """Retorna la card por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card(row) if row else None

    def upsert(self, card: Card) -> Card:
        """Inserta o actualiza la card según exista."""
        self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        return card

    def delete(self, collection_id: int, code_id: str, card_number: int) -> bool:
        """Borra la card. Cascade borra el inventory item asociado."""
        cursor = self.conn.execute(
            "DELETE FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        )
        return cursor.rowcount > 0

    def count_by_collection(self, collection_id: int) -> int:
        """Cuenta cuántas cards tiene una colección."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def list_by_code(self, collection_id: int, code_id: str) -> list[Card]:
        """Retorna las cards de una colección filtradas por code_id."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND code_id = ? "
            "ORDER BY card_number",
            (collection_id, code_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def bulk_upsert(self, cards: list[Card]) -> int:
        """Inserta o actualiza muchas cards en un batch.

        Usa `executemany` para performance. NO commitea.

        Returns:
            Cantidad de cards procesadas.
        """
        if not cards:
            return 0
        params = [(c.collection_id, c.code_id, c.card_number, c.card_name) for c in cards]
        self.conn.executemany(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            params,
        )
        return len(params)
