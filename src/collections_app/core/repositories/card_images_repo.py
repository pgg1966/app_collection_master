"""Repositorio para `card_images`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.card import Card
from collections_app.core.models.card_image import CardImage
from collections_app.core.repositories.base import BaseRepository


def _row_to_image(row: sqlite3.Row) -> CardImage:
    return CardImage(
        card_image_id=row["card_image_id"],
        card_id=row["card_id"],
        found_photo=bool(row["found_photo"]),
        image_source=row["image_source"],
        image_path=row["image_path"],
        generated_at=row["generated_at"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardImagesRepository(BaseRepository):
    """CRUD y queries de tracking sobre `card_images`."""

    def get_by_card_id(self: CardImagesRepository, card_id: int) -> CardImage | None:
        """Imagen registrada para una card. None si nunca se procesó."""
        row = self.conn.execute(
            "SELECT card_image_id, card_id, found_photo, image_source, "
            "image_path, generated_at "
            "FROM card_images WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_image(row) if row else None

    def list_by_collection(self: CardImagesRepository, collection_id: int) -> list[CardImage]:
        """Imágenes registradas de cards de la colección."""
        rows = self.conn.execute(
            "SELECT ci.card_image_id, ci.card_id, ci.found_photo, "
            "       ci.image_source, ci.image_path, ci.generated_at "
            "FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def upsert(self: CardImagesRepository, image: CardImage) -> CardImage:
        """Inserta o actualiza por card_id UNIQUE."""
        self.conn.execute(
            "INSERT INTO card_images "
            "(card_id, found_photo, image_source, image_path, generated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET "
            "found_photo = excluded.found_photo, "
            "image_source = excluded.image_source, "
            "image_path = excluded.image_path, "
            "generated_at = excluded.generated_at",
            (
                image.card_id,
                int(image.found_photo),
                image.image_source,
                image.image_path,
                image.generated_at,
            ),
        )
        fetched = self.get_by_card_id(image.card_id)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def delete_by_card_id(self: CardImagesRepository, card_id: int) -> bool:
        """Borra el tracking de una card. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM card_images WHERE card_id = ?", (card_id,))
        return cursor.rowcount > 0

    def get_pending(self: CardImagesRepository, collection_id: int) -> list[Card]:
        """Cards sin entry en card_images (todavía no procesadas)."""
        rows = self.conn.execute(
            "SELECT c.card_id, c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN card_images ci ON ci.card_id = c.card_id "
            "WHERE c.collection_id = ? AND ci.card_id IS NULL "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_placeholders(self: CardImagesRepository, collection_id: int) -> list[CardImage]:
        """Imágenes generadas pero con `found_photo=False`."""
        rows = self.conn.execute(
            "SELECT ci.card_image_id, ci.card_id, ci.found_photo, "
            "       ci.image_source, ci.image_path, ci.generated_at "
            "FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? AND ci.found_photo = 0 "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def count_with_photo(self: CardImagesRepository, collection_id: int) -> int:
        """Cantidad de cards con `found_photo=True`."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? AND ci.found_photo = 1",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def count_total_generated(self: CardImagesRepository, collection_id: int) -> int:
        """Cantidad de cards con cualquier imagen (real o placeholder)."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count
