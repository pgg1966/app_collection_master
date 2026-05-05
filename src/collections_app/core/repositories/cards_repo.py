"""Repositorio para `cards`."""

from __future__ import annotations

import sqlite3

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
        """Cards de la colección ordenadas por (code_id, card_number)."""
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? "
            "ORDER BY code_id, card_number",
            (collection_id,),
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
