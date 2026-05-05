"""Repositorio para `codes_lines`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.base import BaseRepository


def _row_to_line(row: sqlite3.Row) -> CodeLine:
    return CodeLine(
        code_line_id=row["code_line_id"],
        code_header_id=row["code_header_id"],
        code_id=row["code_id"],
        code_name=row["code_name"],
        code_order=row["code_order"],
    )


class CodeLinesRepository(BaseRepository):
    """CRUD sobre `codes_lines` con soporte de reordenamiento manual."""

    def list_by_header(self: CodeLinesRepository, code_header_id: int) -> list[CodeLine]:
        """Líneas del header ordenadas por (code_order, code_id)."""
        rows = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_header_id = ? "
            "ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [_row_to_line(r) for r in rows]

    def get(self: CodeLinesRepository, code_header_id: int, code_id: str) -> CodeLine | None:
        """Línea por business key (header_id, code_id), o None si no existe."""
        row = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        ).fetchone()
        return _row_to_line(row) if row else None

    def get_by_id(self: CodeLinesRepository, code_line_id: int) -> CodeLine | None:
        """Línea por PK subrogada, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_line_id = ?",
            (code_line_id,),
        ).fetchone()
        return _row_to_line(row) if row else None

    def upsert(self: CodeLinesRepository, line: CodeLine) -> CodeLine:
        """Inserta o actualiza la línea según (code_header_id, code_id) UNIQUE.

        Retorna el modelo con `code_line_id` poblado (incluso para updates,
        donde se relee la fila).
        """
        self.conn.execute(
            "INSERT INTO codes_lines "
            "(code_header_id, code_id, code_name, code_order) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(code_header_id, code_id) DO UPDATE SET "
            "code_name = excluded.code_name, code_order = excluded.code_order",
            (line.code_header_id, line.code_id, line.code_name, line.code_order),
        )
        # Releer para devolver el id (sea recién creado o preexistente).
        fetched = self.get(line.code_header_id, line.code_id)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def delete(self: CodeLinesRepository, code_header_id: int, code_id: str) -> bool:
        """Borra una línea por business key. Retorna True si existía."""
        cursor = self.conn.execute(
            "DELETE FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        )
        return cursor.rowcount > 0

    def reorder(
        self: CodeLinesRepository,
        code_header_id: int,
        ordered_code_ids: list[str],
    ) -> None:
        """Reasigna `code_order` según el índice (1-based) en la lista.

        Líneas no incluidas en `ordered_code_ids` mantienen su order previo.
        Útil cuando el usuario reordena visualmente solo un subconjunto.
        """
        for index, code_id in enumerate(ordered_code_ids, start=1):
            self.conn.execute(
                "UPDATE codes_lines SET code_order = ? " "WHERE code_header_id = ? AND code_id = ?",
                (index, code_header_id, code_id),
            )
