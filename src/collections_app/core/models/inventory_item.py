"""Modelo InventoryItem: cantidad poseída por el usuario de una Card específica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InventoryItem:
    """Stock del usuario para una Card.

    Tabla normalizada via FK a card_id (UNIQUE — 1:1 con cards). El path
    de imagen vive solo en `card_images`, no acá (CLAUDE.md sec 6).

    Attributes:
        inventory_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card asociada (UNIQUE).
        quantity: cantidad poseída total. 0 = no tiene; >1 = duplicados.
    """

    inventory_id: int | None
    card_id: int
    quantity: int = 0

    @property
    def is_owned(self: InventoryItem) -> bool:
        """True si el usuario tiene al menos una copia."""
        return self.quantity > 0

    @property
    def has_duplicates(self: InventoryItem) -> bool:
        """True si el usuario tiene más de una copia."""
        return self.quantity > 1
