"""Modelo CodeLine: un código individual dentro de un CodeHeader."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeLine:
    """Línea de código asociada a un header.

    PK subrogada `code_line_id`; UNIQUE sobre (code_header_id, code_id).

    Attributes:
        code_line_id: PK auto-incremental. None si aún no fue persistido.
        code_header_id: FK al CodeHeader contenedor.
        code_id: identificador del código (ej. "ARG", "MR"). Texto libre con
            longitud máxima validada por `CodeHeader.code_max_length`.
        code_name: descripción legible del código (ej. "Argentina", "Mirage").
        code_order: posición para ordenar manualmente dentro del header.
            Lower = primero. Default 0 (alfabético si no se configura).
    """

    code_line_id: int | None
    code_header_id: int
    code_id: str
    code_name: str
    code_order: int = 0
