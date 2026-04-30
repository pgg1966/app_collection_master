"""Repository para la tabla cards."""

import sqlite3
from typing import TypedDict

from collections_app.core.models import Card
from collections_app.core.repositories.base import BaseRepository


class CodeStats(TypedDict):
    """Stats agregadas por código (ver `CardsRepository.get_stats_by_code`)."""

    code_id: str
    code_name: str
    total: int
    owned: int
    percentage: float


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

    def find_by_number(self, collection_id: int, card_number: int) -> list[Card]:
        """Busca cards en la colección por número, sin filtrar por code_id.

        Útil cuando `Collection.requires_code=False` y el usuario solo
        ingresa el número. Retorna lista para soportar el caso edge de
        múltiples cards con el mismo número en distintos códigos.
        """
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND card_number = ? "
            "ORDER BY code_id",
            (collection_id, card_number),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def list_by_code(self, collection_id: int, code_id: str) -> list[Card]:
        """Retorna las cards de una colección filtradas por code_id."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND code_id = ? "
            "ORDER BY card_number",
            (collection_id, code_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_stats_by_code(self, collection_id: int) -> list[CodeStats]:
        """Stats agregadas por code_id de la colección.

        Para cada código del catálogo: total de cards, cuántas tiene el
        usuario (quantity > 0), porcentaje. Ordenado por `code_order` del
        header (luego alfabético) para que coincida con el orden visible.

        Returns:
            list[dict] con keys: code_id, code_name, total, owned, percentage.
        """
        rows = self.conn.execute(
            "SELECT c.code_id AS code_id, "
            "       COALESCE(cl.code_name, c.code_id) AS code_name, "
            "       COALESCE(cl.code_order, 0) AS code_order, "
            "       COUNT(*) AS total, "
            "       SUM(CASE WHEN i.quantity > 0 THEN 1 ELSE 0 END) AS owned "
            "FROM cards c "
            "LEFT JOIN inventory i "
            "  ON c.collection_id = i.collection_id "
            " AND c.code_id = i.code_id "
            " AND c.card_number = i.card_number "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? "
            "GROUP BY c.code_id "
            "ORDER BY code_order, c.code_id",
            (collection_id, collection_id),
        ).fetchall()
        result: list[CodeStats] = []
        for row in rows:
            total = int(row["total"])
            owned = int(row["owned"] or 0)
            percentage = (owned / total * 100) if total > 0 else 0.0
            result.append(
                CodeStats(
                    code_id=str(row["code_id"]),
                    code_name=str(row["code_name"]),
                    total=total,
                    owned=owned,
                    percentage=percentage,
                )
            )
        return result

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
