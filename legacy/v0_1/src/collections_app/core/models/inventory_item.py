"""Modelo InventoryItem: cantidad poseída por el usuario de una Card específica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryItem:
    """Stock del usuario para una Card.

    Attributes:
        collection_id: FK a la Collection.
        code_id: parte de la PK compuesta de Card.
        card_number: parte de la PK compuesta de Card.
        quantity: cantidad poseída total. 0 = no tiene; >1 = duplicados.
        image_path: path al archivo de imagen subido por el usuario.
        locked: cantidad reservada para un intercambio en curso. Las
            cartas bloqueadas siguen contando para `quantity` pero NO
            están disponibles para una nueva baja/intercambio. Se
            resetea a 0 al cancelar o ejecutar el intercambio.
    """

    collection_id: int
    code_id: str
    card_number: int
    quantity: int = 0
    image_path: str | None = None
    locked: int = 0

    @property
    def is_owned(self) -> bool:
        """True si el usuario tiene al menos una copia."""
        return self.quantity > 0

    @property
    def has_duplicates(self) -> bool:
        """True si el usuario tiene más de una copia (sin descontar locked)."""
        return self.quantity > 1

    @property
    def available_quantity(self) -> int:
        """Cantidad disponible para nuevas operaciones = quantity - locked."""
        return max(0, self.quantity - self.locked)

    @property
    def has_available_duplicates(self) -> bool:
        """True si tiene >1 copias DESCONTANDO las bloqueadas."""
        return self.available_quantity > 1
