"""Service de líneas de código.

Wrapper sobre `CodeLinesRepository` con validaciones de negocio:
code_id no vacío, code_name no vacío, longitud máxima del code_id
respetando `CodeHeader.code_max_length` del header padre.

Expone `lookup_name(header_id, code_id) -> str` con fallback al
code_id cuando la línea no existe — patrón usado por la vista
preservada (`_lookup_code_name` original).
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.services.exceptions import CodeLinesError


class CodeLinesService:
    """Lógica de negocio sobre `codes_lines`."""

    def __init__(self: CodeLinesService, conn: sqlite3.Connection) -> None:
        self._repo = CodeLinesRepository(conn)
        self._headers = CodeHeadersRepository(conn)

    def list_by_header(self: CodeLinesService, code_header_id: int) -> list[CodeLine]:
        return self._repo.list_by_header(code_header_id)

    def lookup(self: CodeLinesService, code_header_id: int, code_id: str) -> CodeLine | None:
        """Línea por business key, o None."""
        return self._repo.get(code_header_id, code_id)

    def lookup_name(self: CodeLinesService, code_header_id: int, code_id: str) -> str:
        """Nombre legible de un código, con fallback al code_id si no existe.

        Comportamiento preservado del `_lookup_code_name` de la vista
        legacy: si no hay línea registrada, mostrar el code_id crudo
        en lugar de un string vacío.
        """
        line = self._repo.get(code_header_id, code_id)
        return line.code_name if line else code_id

    def upsert(self: CodeLinesService, line: CodeLine) -> CodeLine:
        """Inserta o actualiza la línea validando el contrato del header."""
        if not line.code_id.strip():
            raise CodeLinesError("code_id no puede ser vacio")
        if not line.code_name.strip():
            raise CodeLinesError("code_name no puede ser vacio")
        header = self._headers.get_by_id(line.code_header_id)
        if header is None:
            raise CodeLinesError(f"code_header_id={line.code_header_id} no existe")
        if len(line.code_id) > header.code_max_length:
            raise CodeLinesError(
                f"code_id={line.code_id!r} supera max_length={header.code_max_length} "
                f"del header {header.code_header_name!r}"
            )
        return self._repo.upsert(line)

    def delete(self: CodeLinesService, code_header_id: int, code_id: str) -> bool:
        """Borra una línea. Retorna True si existía."""
        return self._repo.delete(code_header_id, code_id)

    def reorder(
        self: CodeLinesService,
        code_header_id: int,
        ordered_code_ids: list[str],
    ) -> None:
        """Reasigna code_order según el índice 1-based de cada code_id."""
        self._repo.reorder(code_header_id, ordered_code_ids)
