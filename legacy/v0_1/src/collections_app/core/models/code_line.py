"""Modelo CodeLine: un código individual dentro de un CodeHeader."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeLine:
    """Línea de código asociada a un header (PK compuesta header+code).

    Attributes:
        code_header_id: FK al CodeHeader contenedor.
        code_id: identificador del código (ej. "ARG", "MR"). Texto libre con
            longitud máxima validada por `CodeHeader.code_max_length`.
        code_name: descripción legible del código (ej. "Argentina", "Mirage").
        code_order: posición para ordenar manualmente dentro del header.
            Lower = primero. Default 0 (alfabético si no se configura).
    """

    code_header_id: int
    code_id: str
    code_name: str
    code_order: int = 0
