"""Modelo Card: una entrada del catálogo de una colección."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    """Card del catálogo (PK compuesta collection+code+number).

    Attributes:
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG"). Si la colección no
            requiere código, suele usarse uno vacío o un placeholder.
        card_number: número correlativo dentro del code_id.
        card_name: nombre legible (ej. "Lionel Messi").
    """

    collection_id: int
    code_id: str
    card_number: int
    card_name: str

    @property
    def card_key(self) -> str:
        """Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1')."""
        return f"{self.code_id}-{self.card_number}"
