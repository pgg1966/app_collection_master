"""Modelo CodeHeader: universo de códigos (ej. "Países FIFA", "Sets de Magic")."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeHeader:
    """Representa un universo de códigos.

    Attributes:
        code_header_id: PK auto-incremental. None si aún no fue persistido.
        code_header_name: nombre único del header.
        code_max_length: longitud máxima permitida para los `code_id` hijos.
    """

    code_header_id: int | None
    code_header_name: str
    code_max_length: int = 5
