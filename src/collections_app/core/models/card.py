"""Modelo Card: una entrada del catálogo de una colección."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Card:
    """Card del catálogo.

    PK subrogada `card_id`; UNIQUE sobre (collection_id, code_id, card_number).

    Attributes:
        card_id: PK auto-incremental. None pre-persistencia.
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG"). Si la colección no
            requiere código, suele usarse uno vacío o un placeholder.
        card_number: número correlativo dentro del code_id.
        card_name: nombre legible (ej. "Lionel Messi").
    """

    card_id: int | None
    collection_id: int
    code_id: str
    card_number: int
    card_name: str

    @property
    def card_key(self: Card) -> str:
        """Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1')."""
        return f"{self.code_id}-{self.card_number}"
