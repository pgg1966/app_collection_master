"""Service de inventario.

Reglas de negocio sobre `inventory` que no caben en el repo:

- `adjust_quantity` jamás puede dejar `quantity` en negativo. La columna
  no tiene `CHECK (quantity >= 0)` en el schema porque la regla vive
  en este service (CLAUDE.md sec 4: excepciones de dominio por service).
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.services.exceptions import InventoryError


class InventoryService:
    """Reglas de negocio del inventario."""

    def __init__(self: InventoryService, conn: sqlite3.Connection) -> None:
        self._inventory = InventoryRepository(conn)

    def adjust_quantity(self: InventoryService, card_id: int, delta: int) -> InventoryItem:
        """Suma `delta` a la quantity de `card_id` validando >= 0.

        Si la suma quedara negativa, lanza `InventoryError` y NO toca
        la DB. Si no había entry previa, current_qty se trata como 0.

        NOTE: read-then-write pattern. Safe in single-connection SQLite,
        but would need a transaction with row lock if migrated to
        multi-user backend (v1.0 cloud).
        """
        current = self._inventory.get_by_card_id(card_id)
        current_qty = current.quantity if current else 0
        new_qty = current_qty + delta
        if new_qty < 0:
            raise InventoryError(
                f"quantity quedaria negativo: card_id={card_id}, "
                f"current={current_qty}, delta={delta}"
            )
        return self._inventory.adjust_quantity(card_id, delta)
