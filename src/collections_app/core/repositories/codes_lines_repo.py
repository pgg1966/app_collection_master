"""Repository para la tabla codes_lines."""

import sqlite3

from collections_app.core.models import CodeLine
from collections_app.core.repositories.base import BaseRepository


def _row_to_line(row: sqlite3.Row) -> CodeLine:
    return CodeLine(
        code_header_id=row["code_header_id"],
        code_id=row["code_id"],
        code_name=row["code_name"],
        code_order=row["code_order"],
    )


class CodesLinesRepository(BaseRepository):
    """CRUD sobre `codes_lines` con validación de longitud contra el header."""

    def list_by_header(self, code_header_id: int) -> list[CodeLine]:
        """Retorna las líneas de un header ordenadas por (code_order, code_id)."""
        rows = self.conn.execute(
            "SELECT code_header_id, code_id, code_name, code_order FROM codes_lines "
            "WHERE code_header_id = ? ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [_row_to_line(r) for r in rows]

    def get(self, code_header_id: int, code_id: str) -> CodeLine | None:
        """Retorna la línea por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_id, code_name, code_order FROM codes_lines "
            "WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        ).fetchone()
        return _row_to_line(row) if row else None

    def upsert(self, line: CodeLine) -> CodeLine:
        """Inserta o actualiza la línea según exista.

        Valida que `len(code_id)` no exceda `code_max_length` del header
        contenedor.

        Raises:
            ValueError: si el code_id excede el max_length del header, o si el
                header no existe.
        """
        max_len_row = self.conn.execute(
            "SELECT code_max_length FROM codes_headers WHERE code_header_id = ?",
            (line.code_header_id,),
        ).fetchone()
        if max_len_row is None:
            raise ValueError(f"code_header_id {line.code_header_id} no existe")
        if len(line.code_id) > max_len_row["code_max_length"]:
            raise ValueError(
                f"code_id '{line.code_id}' excede max_length {max_len_row['code_max_length']}"
            )

        self.conn.execute(
            "INSERT INTO codes_lines (code_header_id, code_id, code_name, code_order) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(code_header_id, code_id) DO UPDATE SET "
            "code_name = excluded.code_name, code_order = excluded.code_order",
            (line.code_header_id, line.code_id, line.code_name, line.code_order),
        )
        return line

    def delete(self, code_header_id: int, code_id: str) -> bool:
        """Borra una línea. Retorna True si se borró efectivamente."""
        cursor = self.conn.execute(
            "DELETE FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        )
        return cursor.rowcount > 0

    def list_codes_only(self, code_header_id: int) -> list[str]:
        """Solo los IDs de los códigos de un header (útil para autocomplete)."""
        rows = self.conn.execute(
            "SELECT code_id FROM codes_lines WHERE code_header_id = ? "
            "ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [r["code_id"] for r in rows]

    def reorder(self, code_header_id: int, ordered_code_ids: list[str]) -> None:
        """Reasigna code_order según el índice (1-based) en la lista.

        Útil para drag&drop: pasás los code_id en el orden deseado y este
        método actualiza `code_order` con 1, 2, 3, ... respectivamente.
        Los códigos no incluidos en la lista quedan con su `code_order` actual.
        """
        for i, cid in enumerate(ordered_code_ids, start=1):
            self.conn.execute(
                "UPDATE codes_lines SET code_order = ? " "WHERE code_header_id = ? AND code_id = ?",
                (i, code_header_id, cid),
            )
