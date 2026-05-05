"""Aggregate CodeStats: stats por código dentro de una colección."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeStats:
    """Stats agregadas por code_id (resultado de `CardsRepository.get_stats_by_code`).

    Attributes:
        code_id: identificador del código (ej. "ARG").
        code_name: descripción legible del código (ej. "Argentina").
            Si no hay entrada en codes_lines, fallbackea al code_id.
        total: cantidad de cards del catálogo con ese code_id.
        owned: cantidad de cards con `inventory.quantity > 0`.
        percentage: owned/total * 100. 0.0 si total es 0.
    """

    code_id: str
    code_name: str
    total: int
    owned: int
    percentage: float
