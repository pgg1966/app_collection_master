"""Repository para la tabla card_images."""

import sqlite3

from collections_app.core.models import Card, CardImage
from collections_app.core.repositories.base import BaseRepository


def _row_to_card_image(row: sqlite3.Row) -> CardImage:
    return CardImage(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        found_photo=bool(row["found_photo"]),
        image_source=row["image_source"],
        image_path=row["image_path"],
        generated_at=row["generated_at"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardImagesRepository(BaseRepository):
    """Tracking de imágenes generadas por card.

    Cada card tiene como mucho una fila acá. Si no aparece, todavía no
    se procesó (la pipeline la consideraría "pending"). Si aparece con
    `found_photo=False`, salió placeholder y se puede reintentar.
    """

    def upsert(self, image: CardImage) -> None:
        """Inserta o actualiza el tracking de una card."""
        self.conn.execute(
            """
            INSERT INTO card_images (
                collection_id, code_id, card_number,
                found_photo, image_source, image_path, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET
                found_photo = excluded.found_photo,
                image_source = excluded.image_source,
                image_path = excluded.image_path,
                generated_at = excluded.generated_at
            """,
            (
                image.collection_id,
                image.code_id,
                image.card_number,
                int(image.found_photo),
                image.image_source,
                image.image_path,
                image.generated_at,
            ),
        )

    def get(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> CardImage | None:
        """Retorna la entry por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ? AND code_id = ? AND card_number = ?
            """,
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card_image(row) if row else None

    def list_by_collection(self, collection_id: int) -> list[CardImage]:
        """Todas las imágenes registradas de una colección."""
        rows = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ?
            ORDER BY code_id, card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card_image(r) for r in rows]

    def get_pending(self, collection_id: int) -> list[Card]:
        """Cards que todavía no tienen imagen generada (no aparecen en card_images)."""
        rows = self.conn.execute(
            """
            SELECT c.collection_id, c.code_id, c.card_number, c.card_name
            FROM cards c
            LEFT JOIN card_images i
                ON c.collection_id = i.collection_id
                AND c.code_id = i.code_id
                AND c.card_number = i.card_number
            WHERE c.collection_id = ? AND i.collection_id IS NULL
            ORDER BY c.code_id, c.card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_placeholders(self, collection_id: int) -> list[CardImage]:
        """Cards generadas pero con `found_photo=False` (placeholder)."""
        rows = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ? AND found_photo = 0
            ORDER BY code_id, card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card_image(r) for r in rows]

    def get_found_count(self, collection_id: int) -> int:
        """Cuántas cards tienen `found_photo=True`."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM card_images " "WHERE collection_id = ? AND found_photo = 1",
            (collection_id,),
        ).fetchone()
        return int(row["n"]) if row else 0

    def get_total_generated(self, collection_id: int) -> int:
        """Cuántas cards tienen alguna imagen (real o placeholder)."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM card_images WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        return int(row["n"]) if row else 0

    def delete(self, collection_id: int, code_id: str, card_number: int) -> None:
        """Borra el tracking de una card (forzando que vuelva a "pending")."""
        self.conn.execute(
            "DELETE FROM card_images "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        )
