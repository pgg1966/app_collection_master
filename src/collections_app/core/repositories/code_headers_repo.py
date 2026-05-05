"""Repositorio para `codes_headers`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.repositories.base import BaseRepository


def _row_to_header(row: sqlite3.Row) -> CodeHeader:
    return CodeHeader(
        code_header_id=row["code_header_id"],
        code_header_name=row["code_header_name"],
        code_max_length=row["code_max_length"],
    )


class CodeHeadersRepository(BaseRepository):
    """CRUD sobre `codes_headers`."""

    def list_all(self: CodeHeadersRepository) -> list[CodeHeader]:
        """Retorna todos los headers ordenados por nombre."""
        rows = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers ORDER BY code_header_name"
        ).fetchall()
        return [_row_to_header(r) for r in rows]

    def get_by_id(self: CodeHeadersRepository, code_header_id: int) -> CodeHeader | None:
        """Retorna el header por id, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_id = ?",
            (code_header_id,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def get_by_name(self: CodeHeadersRepository, name: str) -> CodeHeader | None:
        """Retorna el header por nombre exacto (case-sensitive), o None."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_name = ?",
            (name,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def create(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader:
        """Inserta y retorna el header con `code_header_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
            (header.code_header_name, header.code_max_length),
        )
        return CodeHeader(
            code_header_id=cursor.lastrowid,
            code_header_name=header.code_header_name,
            code_max_length=header.code_max_length,
        )

    def update(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader:
        """Actualiza un header existente. Requiere `code_header_id` no None."""
        if header.code_header_id is None:
            raise ValueError("update requiere code_header_id no None")
        self.conn.execute(
            "UPDATE codes_headers "
            "SET code_header_name = ?, code_max_length = ? "
            "WHERE code_header_id = ?",
            (header.code_header_name, header.code_max_length, header.code_header_id),
        )
        return header

    def delete(self: CodeHeadersRepository, code_header_id: int) -> bool:
        """Borra un header. Cascade borra `codes_lines` asociadas."""
        cursor = self.conn.execute(
            "DELETE FROM codes_headers WHERE code_header_id = ?", (code_header_id,)
        )
        return cursor.rowcount > 0
