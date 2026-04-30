"""Repository para la tabla inventory."""

import sqlite3

from collections_app.core.models import Card, InventoryItem
from collections_app.core.repositories.base import BaseRepository


def _row_to_item(row: sqlite3.Row) -> InventoryItem:
    return InventoryItem(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        quantity=row["quantity"],
        image_path=row["image_path"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class InventoryRepository(BaseRepository):
    """CRUD y queries específicas sobre `inventory`."""

    def get(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> InventoryItem | None:
        """Retorna el inventario por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path "
            "FROM inventory "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_by_collection(self, collection_id: int) -> list[InventoryItem]:
        """Lista todo el inventario de una colección."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path "
            "FROM inventory WHERE collection_id = ? "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_owned(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 0."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path "
            "FROM inventory WHERE collection_id = ? AND quantity > 0 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_top_duplicates(
        self,
        collection_id: int,
        limit: int = 10,
    ) -> list[InventoryItem]:
        """Las cards con mayor cantidad (quantity > 1), ordenadas desc."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path "
            "FROM inventory WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY quantity DESC, code_id, card_number "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_duplicates(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 1."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path "
            "FROM inventory WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_missing(self, collection_id: int) -> list[Card]:
        """Cards que el usuario aún no tiene (sin inventory o quantity=0)."""
        rows = self.conn.execute(
            "SELECT c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN inventory i "
            "  ON c.collection_id = i.collection_id "
            " AND c.code_id = i.code_id "
            " AND c.card_number = i.card_number "
            "WHERE c.collection_id = ? "
            "  AND (i.quantity IS NULL OR i.quantity = 0) "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def upsert(self, item: InventoryItem) -> InventoryItem:
        """Crea o actualiza el inventory item."""
        self.conn.execute(
            "INSERT INTO inventory "
            "(collection_id, code_id, card_number, quantity, image_path) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "quantity = excluded.quantity, image_path = excluded.image_path",
            (
                item.collection_id,
                item.code_id,
                item.card_number,
                item.quantity,
                item.image_path,
            ),
        )
        return item

    def adjust_quantity(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        delta: int,
    ) -> InventoryItem:
        """Suma `delta` a la quantity (delta puede ser negativo).

        Si el item no existe, se crea con `quantity = max(0, delta)`.

        Raises:
            ValueError: si el resultado quedaría en negativo.
        """
        existing = self.get(collection_id, code_id, card_number)
        current_qty = existing.quantity if existing else 0
        new_qty = current_qty + delta

        if new_qty < 0:
            raise ValueError(
                f"Cantidad resultante negativa para ({collection_id}, {code_id}, "
                f"{card_number}): actual={current_qty}, delta={delta}"
            )

        item = InventoryItem(
            collection_id=collection_id,
            code_id=code_id,
            card_number=card_number,
            quantity=new_qty,
            image_path=existing.image_path if existing else None,
        )
        return self.upsert(item)

    def set_image(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        image_path: str,
    ) -> None:
        """Setea el image_path del inventory item, creándolo con quantity=0 si no existe."""
        existing = self.get(collection_id, code_id, card_number)
        quantity = existing.quantity if existing else 0
        self.upsert(
            InventoryItem(
                collection_id=collection_id,
                code_id=code_id,
                card_number=card_number,
                quantity=quantity,
                image_path=image_path,
            )
        )
