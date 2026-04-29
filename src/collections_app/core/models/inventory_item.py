"""Modelo InventoryItem: cantidad poseída por el usuario de una Card específica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryItem:
    """Stock del usuario para una Card.

    Attributes:
        collection_id: FK a la Collection.
        code_id: parte de la PK compuesta de Card.
        card_number: parte de la PK compuesta de Card.
        quantity: cantidad poseída. 0 = no tiene; >1 = duplicados.
        image_path: path al archivo de imagen subido por el usuario.
    """

    collection_id: int
    code_id: str
    card_number: int
    quantity: int = 0
    image_path: str | None = None

    @property
    def is_owned(self) -> bool:
        """True si el usuario tiene al menos una copia."""
        return self.quantity > 0

    @property
    def has_duplicates(self) -> bool:
        """True si el usuario tiene más de una copia."""
        return self.quantity > 1
