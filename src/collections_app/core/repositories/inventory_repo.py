"""Repositorio para `inventory`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.card import Card
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.repositories.base import BaseRepository


def _row_to_item(row: sqlite3.Row) -> InventoryItem:
    return InventoryItem(
        inventory_id=row["inventory_id"],
        card_id=row["card_id"],
        quantity=row["quantity"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class InventoryRepository(BaseRepository):
    """CRUD y queries específicas sobre `inventory`.

    `inventory` es 1:1 con `cards` via card_id UNIQUE. Las queries que
    necesitan filtrar por colección hacen JOIN con `cards`.
    """

    def get_by_card_id(self: InventoryRepository, card_id: int) -> InventoryItem | None:
        """Inventory item de una card. None si nunca se grabó."""
        row = self.conn.execute(
            "SELECT inventory_id, card_id, quantity " "FROM inventory WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_by_collection(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory de todas las cards de la colección (incluye qty=0).

        Ordena por `codes_lines.code_order` (LEFT JOIN, COALESCE para
        colecciones sin código). Sesión 5.5 / D1.
        """
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? "
            "ORDER BY COALESCE(cl.code_order, 0), c.code_id, c.card_number",
            (collection_id, collection_id),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_owned(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory items con quantity > 0 de la colección.

        Ordena por `codes_lines.code_order` (Sesión 5.5 / D1).
        """
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? AND i.quantity > 0 "
            "ORDER BY COALESCE(cl.code_order, 0), c.code_id, c.card_number",
            (collection_id, collection_id),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_duplicates(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory items con quantity > 1 de la colección.

        Ordena por `codes_lines.code_order` (Sesión 5.5 / D1).
        """
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? AND i.quantity > 1 "
            "ORDER BY COALESCE(cl.code_order, 0), c.code_id, c.card_number",
            (collection_id, collection_id),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_top_duplicates(
        self: InventoryRepository, collection_id: int, limit: int = 10
    ) -> list[InventoryItem]:
        """Las cards con mayor cantidad (quantity > 1), descendente.

        Sesión 5.5 / D1: dejamos `quantity DESC` como criterio principal
        (es el sentido de "top"); como tiebreak agregamos `code_order`
        en lugar del alfabético.
        """
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? AND i.quantity > 1 "
            "ORDER BY i.quantity DESC, COALESCE(cl.code_order, 0), c.code_id, c.card_number "
            "LIMIT ?",
            (collection_id, collection_id, limit),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_missing(self: InventoryRepository, collection_id: int) -> list[Card]:
        """Cards que el usuario aún no tiene (sin inventory o quantity=0).

        Ordena por `codes_lines.code_order` (Sesión 5.5 / D1).
        """
        rows = self.conn.execute(
            "SELECT c.card_id, c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN inventory i ON i.card_id = c.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? AND COALESCE(i.quantity, 0) = 0 "
            "ORDER BY COALESCE(cl.code_order, 0), c.code_id, c.card_number",
            (collection_id, collection_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def upsert(self: InventoryRepository, item: InventoryItem) -> InventoryItem:
        """Inserta o actualiza el inventory item por card_id UNIQUE."""
        self.conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET quantity = excluded.quantity",
            (item.card_id, item.quantity),
        )
        fetched = self.get_by_card_id(item.card_id)
        assert fetched is not None  # acabamos de upsertarlo
        return fetched

    def adjust_quantity(self: InventoryRepository, card_id: int, delta: int) -> InventoryItem:
        """Suma `delta` a la quantity (puede ser negativo).

        Crea la entrada con quantity=0 si no existía antes de aplicar el
        delta. La operación se hace en SQL para evitar race conditions.
        """
        self.conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET quantity = quantity + excluded.quantity",
            (card_id, delta),
        )
        fetched = self.get_by_card_id(card_id)
        assert fetched is not None  # acabamos de insertar/actualizar
        return fetched
