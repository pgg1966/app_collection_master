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
        locked=row["locked"],
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
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_by_collection(self, collection_id: int) -> list[InventoryItem]:
        """Lista todo el inventario de una colección."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory WHERE collection_id = ? "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_owned(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 0."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 0 "
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
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY quantity DESC, code_id, card_number "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_duplicates(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 1."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_locked(self, collection_id: int) -> list[InventoryItem]:
        """Items con locked > 0 (reservados para un intercambio en curso)."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND locked > 0 "
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
        """Crea o actualiza el inventory item.

        IMPORTANTE: este upsert NO toca la columna `locked` para no
        pisar reservas de intercambio en curso. Para mover el locked,
        usar `lock` / `unlock` / `unlock_all`.
        """
        self.conn.execute(
            "INSERT INTO inventory "
            "(collection_id, code_id, card_number, quantity, image_path, locked) "
            "VALUES (?, ?, ?, ?, ?, COALESCE("
            "  (SELECT locked FROM inventory "
            "    WHERE collection_id=? AND code_id=? AND card_number=?), 0)) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "quantity = excluded.quantity, image_path = excluded.image_path",
            (
                item.collection_id,
                item.code_id,
                item.card_number,
                item.quantity,
                item.image_path,
                item.collection_id,
                item.code_id,
                item.card_number,
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
            locked=existing.locked if existing else 0,
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

    # ------------------------------------------------------------------
    # Bloqueo para intercambios
    # ------------------------------------------------------------------

    def lock(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        amount: int = 1,
    ) -> InventoryItem:
        """Incrementa `locked` en `amount`. NO modifica `quantity`.

        Si el item no existe, se crea con quantity=0 y locked=amount —
        caso usado al agregar manualmente una carta a "Entrego" en el
        ExchangeView (la carta saldrá del inventario al ejecutar).
        """
        if amount <= 0:
            raise ValueError(f"amount debe ser > 0 (recibido: {amount})")
        existing = self.get(collection_id, code_id, card_number)
        if existing is None:
            self.conn.execute(
                "INSERT INTO inventory "
                "(collection_id, code_id, card_number, quantity, image_path, locked) "
                "VALUES (?, ?, ?, 0, NULL, ?)",
                (collection_id, code_id, card_number, amount),
            )
        else:
            self.conn.execute(
                "UPDATE inventory SET locked = locked + ? "
                "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
                (amount, collection_id, code_id, card_number),
            )
        result = self.get(collection_id, code_id, card_number)
        assert result is not None
        return result

    def unlock(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        amount: int = 1,
    ) -> InventoryItem:
        """Decrementa `locked` en `amount`. Mínimo 0 (clamp)."""
        if amount <= 0:
            raise ValueError(f"amount debe ser > 0 (recibido: {amount})")
        self.conn.execute(
            "UPDATE inventory SET locked = MAX(0, locked - ?) "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (amount, collection_id, code_id, card_number),
        )
        result = self.get(collection_id, code_id, card_number)
        if result is None:
            # No había nada, retornamos un item sintético con todo en 0
            # para mantener la firma consistente.
            return InventoryItem(
                collection_id=collection_id,
                code_id=code_id,
                card_number=card_number,
            )
        return result

    def unlock_all(self, collection_id: int) -> int:
        """Resetea locked=0 para toda la colección. Retorna filas afectadas."""
        cursor = self.conn.execute(
            "UPDATE inventory SET locked = 0 " "WHERE collection_id = ? AND locked > 0",
            (collection_id,),
        )
        return cursor.rowcount
