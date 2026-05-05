"""Service de universos de códigos.

Wrapper sobre `CodeHeadersRepository` con validaciones de negocio:
nombre no vacío, unicidad por nombre, id requerido en update. Traduce
las excepciones de bajo nivel del repo (`sqlite3.IntegrityError`,
`ValueError`) a `CodeHeadersError` con mensajes de dominio.
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.services.exceptions import CodeHeadersError


class CodeHeadersService:
    """Lógica de negocio sobre `codes_headers`."""

    def __init__(self: CodeHeadersService, conn: sqlite3.Connection) -> None:
        self._repo = CodeHeadersRepository(conn)

    def list_all(self: CodeHeadersService) -> list[CodeHeader]:
        return self._repo.list_all()

    def get_by_id(self: CodeHeadersService, code_header_id: int) -> CodeHeader | None:
        return self._repo.get_by_id(code_header_id)

    def get_by_name(self: CodeHeadersService, name: str) -> CodeHeader | None:
        return self._repo.get_by_name(name)

    def create(self: CodeHeadersService, header: CodeHeader) -> CodeHeader:
        """Crea un header. Valida nombre no vacio y unicidad."""
        if not header.code_header_name.strip():
            raise CodeHeadersError("code_header_name no puede ser vacio")
        try:
            return self._repo.create(header)
        except sqlite3.IntegrityError as exc:
            raise CodeHeadersError(
                f"code_header_name ya existe: {header.code_header_name!r}"
            ) from exc

    def update(self: CodeHeadersService, header: CodeHeader) -> CodeHeader:
        """Actualiza un header existente. Requiere id."""
        if header.code_header_id is None:
            raise CodeHeadersError("update requiere code_header_id no None")
        if not header.code_header_name.strip():
            raise CodeHeadersError("code_header_name no puede ser vacio")
        try:
            return self._repo.update(header)
        except sqlite3.IntegrityError as exc:
            raise CodeHeadersError(
                f"code_header_name ya existe: {header.code_header_name!r}"
            ) from exc

    def delete(self: CodeHeadersService, code_header_id: int) -> bool:
        """Borra un header. Cascade borra sus codes_lines."""
        return self._repo.delete(code_header_id)
