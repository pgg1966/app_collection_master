"""Repositorio para `cards`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.aggregates.code_catalog import CodeCatalog
from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.card import Card
from collections_app.core.repositories.base import BaseRepository


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardsRepository(BaseRepository):
    """CRUD y queries específicas sobre `cards`."""

    def get_by_id(self: CardsRepository, card_id: int) -> Card | None:
        """Card por PK subrogada, o None."""
        row = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_card(row) if row else None

    def get(
        self: CardsRepository,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> Card | None:
        """Card por business key (collection, code, number), o None."""
        row = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card(row) if row else None

    def list_by_collection(self: CardsRepository, collection_id: int) -> list[Card]:
        """Cards de la colección ordenadas por code_order del header.

        Usa LEFT JOIN con `codes_lines` filtrado por el header de la
        colección. Para colecciones con `requires_code=False` (sin
        entradas en `codes_lines`) el JOIN devuelve `code_order=NULL`
        y `COALESCE(...,0)` colapsa todo al mismo bucket → ordena por
        `card_number` solamente.
        """
        rows = self.conn.execute(
            "SELECT c.card_id, c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? "
            "ORDER BY COALESCE(cl.code_order, 0), c.code_id, c.card_number",
            (collection_id, collection_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def list_by_code(self: CardsRepository, collection_id: int, code_id: str) -> list[Card]:
        """Cards filtradas por code_id, ordenadas por card_number."""
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND code_id = ? "
            "ORDER BY card_number",
            (collection_id, code_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def find_by_number(self: CardsRepository, collection_id: int, card_number: int) -> list[Card]:
        """Busca cards por número sin filtrar por code_id.

        Útil cuando `Collection.requires_code=False`: el usuario solo
        ingresa el número y la lógica de servicio resuelve ambigüedad
        si hay >1 match. Ordenado por code_id para determinismo.
        """
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND card_number = ? "
            "ORDER BY code_id",
            (collection_id, card_number),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_code_catalog(self: CardsRepository, collection_id: int) -> CodeCatalog:
        """Catálogo de códigos de la colección (para validador OCR).

        Sesión 5d / fix post-smoke: empaqueta los dos datos que el
        validador de OCR necesita — los códigos únicos en orden de
        álbum y el máximo `card_number` por código — en un solo
        agregado para respetar el contrato de retorno de repos
        (CLAUDE.md sec 2.3 prohíbe `list[str]` y `dict[str, int]`
        sueltos).

        Para colecciones con `requires_code=False`, los códigos pueden
        no estar en `codes_lines`; el LEFT JOIN deja `code_order=NULL`
        y `COALESCE(...,0)` los agrupa al mismo bucket. Una única
        query resuelve los dos datos.
        """
        rows = self.conn.execute(
            "SELECT c.code_id AS code_id, "
            "       MAX(c.card_number) AS max_num, "
            "       COALESCE(cl.code_order, 0) AS code_order "
            "FROM cards c "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections "
            "       WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? "
            "GROUP BY c.code_id, cl.code_order "
            "ORDER BY code_order, c.code_id",
            (collection_id, collection_id),
        ).fetchall()
        codes = tuple(row["code_id"] for row in rows)
        max_by_code = {row["code_id"]: int(row["max_num"]) for row in rows}
        return CodeCatalog(codes=codes, max_number_by_code=max_by_code)

    def count_by_collection(self: CardsRepository, collection_id: int) -> int:
        """Cuántas cards tiene la colección."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def create(self: CardsRepository, card: Card) -> Card:
        """Inserta y retorna la card con `card_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?)",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        return Card(
            card_id=cursor.lastrowid,
            collection_id=card.collection_id,
            code_id=card.code_id,
            card_number=card.card_number,
            card_name=card.card_name,
        )

    def upsert(self: CardsRepository, card: Card) -> Card:
        """Inserta o actualiza por business key. Retorna con id poblado."""
        self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        fetched = self.get(card.collection_id, card.code_id, card.card_number)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def bulk_upsert(self: CardsRepository, cards: list[Card]) -> int:
        """Inserta o actualiza muchas cards en un batch. Retorna cantidad procesada."""
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

    def delete_by_id(self: CardsRepository, card_id: int) -> bool:
        """Borra la card. Cascade borra inventory y card_images. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
        return cursor.rowcount > 0

    def get_stats_by_code(self: CardsRepository, collection_id: int) -> list[CodeStats]:
        """Stats agregadas por code_id de la colección.

        Para cada code_id presente en `cards`: total de cards, cuántas
        tiene el usuario (inventory.quantity > 0), porcentaje. code_name
        se resuelve desde `codes_lines` filtrando por el header de la
        colección; fallbackea al code_id si no hay match. Orden:
        codes_lines.code_order primero, code_id alfabético como
        tiebreak — coincide con el orden visible al usuario.

        Retorna lista de CodeStats (dataclass slots, sec 2.3).
        """
        rows = self.conn.execute(
            "SELECT c.code_id AS code_id, "
            "       COALESCE(cl.code_name, c.code_id) AS code_name, "
            "       COALESCE(cl.code_order, 0) AS code_order, "
            "       COUNT(*) AS total, "
            "       SUM(CASE WHEN i.quantity > 0 THEN 1 ELSE 0 END) AS owned "
            "FROM cards c "
            "LEFT JOIN inventory i ON i.card_id = c.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections "
            "       WHERE collection_id = ?"
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
