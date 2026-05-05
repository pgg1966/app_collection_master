"""Importador de codes_lines desde CSV."""

import csv
import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from collections_app.core.db.connection import transaction
from collections_app.core.models import CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)

logger = logging.getLogger(__name__)

# Mapeo posicional cuando el CSV no tiene header.
_DEFAULT_COLUMN_INDEXES = {"code_id": 0, "code_name": 1, "code_order": 2}


@dataclass
class CodesCsvImportResult:
    """Resumen del resultado de un import de códigos."""

    total_rows: int
    imported: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class CodesCsvImporter:
    """Importa codes_lines desde un CSV.

    Formato esperado (UTF-8, separador coma):

        code_id,code_name,code_order
        ARG,Argentina,1
        BRA,Brasil,2

    Si el CSV trae una columna adicional `code_max_length` (formato
    histórico), se ignora silenciosamente — esa configuración pertenece
    al header padre, no a cada línea.

    La primera fila puede ser header (detectado por `code_id` presente
    en cualquier columna) o directamente datos; en ese caso se asume
    el orden posicional `code_id, code_name, code_order` y cualquier
    columna extra se descarta.

    Validaciones por fila (filas inválidas se reportan en `errors` y se
    omiten, pero NO abortan el import):
      - `code_id` no vacío y de longitud ≤ `code_max_length` del header.
      - `code_name` no vacío.
      - `code_order` entero si está presente; default 0.

    El upsert final corre dentro de una transacción.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def import_file(
        self,
        csv_path: Path,
        code_header_id: int,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CodesCsvImportResult:
        """Lee y procesa el CSV.

        Args:
            csv_path: archivo a leer (UTF-8).
            code_header_id: id del header al que pertenecen los códigos.
            on_progress: callback `(current, total)` para barras de progreso.

        Returns:
            `CodesCsvImportResult` con totales y errores por fila.

        Raises:
            ValueError: si el header no existe.
            FileNotFoundError: si el archivo no se puede abrir.
        """
        header = CodesHeadersRepository(self.conn).get_by_id(code_header_id)
        if header is None:
            raise ValueError(f"code_header_id {code_header_id} no existe")

        max_len = header.code_max_length

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))

        if not rows:
            return CodesCsvImportResult(0, 0, 0)

        column_indexes, data_rows = self._detect_columns(rows)

        total = len(data_rows)
        lines_to_save: list[CodeLine] = []
        errors: list[str] = []
        skipped = 0

        for i, row in enumerate(data_rows, start=1):
            if on_progress:
                on_progress(i, total)
            ok, line_or_error = self._parse_row(row, code_header_id, max_len, i, column_indexes)
            if not ok:
                errors.append(line_or_error)  # type: ignore[arg-type]
                skipped += 1
                continue
            lines_to_save.append(line_or_error)  # type: ignore[arg-type]

        repo = CodesLinesRepository(self.conn)
        with transaction(self.conn):
            for line in lines_to_save:
                repo.upsert(line)

        logger.info(
            "Import codes CSV: total=%d imported=%d skipped=%d errors=%d",
            total,
            len(lines_to_save),
            skipped,
            len(errors),
        )
        return CodesCsvImportResult(
            total_rows=total,
            imported=len(lines_to_save),
            skipped=skipped,
            errors=errors,
        )

    def _detect_columns(self, rows: list[list[str]]) -> tuple[dict[str, int], list[list[str]]]:
        """Decide si la primera fila es header y construye el mapping.

        Retorna `(column_indexes, data_rows)`. Si la primera fila contiene
        `code_id` (case-insensitive), se interpreta como header y los
        índices se derivan de los nombres; columnas no reconocidas
        (incluyendo `code_max_length`) se ignoran silenciosamente. Si no
        hay header, se asume el mapping posicional por defecto.
        """
        first = [c.strip().lower() for c in rows[0]]
        if "code_id" in first:
            mapping: dict[str, int] = {}
            for i, name in enumerate(first):
                if name in {"code_id", "code_name", "code_order"}:
                    mapping[name] = i
                # cualquier otra columna (incluyendo "code_max_length") se ignora
            return mapping, rows[1:]
        return _DEFAULT_COLUMN_INDEXES, rows

    def _parse_row(
        self,
        row: list[str],
        code_header_id: int,
        max_len: int,
        row_index: int,
        column_indexes: dict[str, int],
    ) -> tuple[bool, CodeLine | str]:
        def cell(name: str) -> str:
            idx = column_indexes.get(name)
            if idx is None or idx >= len(row):
                return ""
            return row[idx].strip()

        code_id = cell("code_id")
        code_name = cell("code_name")
        order_str = cell("code_order")

        if not code_id:
            return False, f"fila {row_index}: code_id vacío"
        if len(code_id) > max_len:
            return False, f"fila {row_index}: code_id '{code_id}' excede max_length {max_len}"
        if not code_name:
            return False, f"fila {row_index}: code_name vacío"

        if order_str:
            try:
                code_order = int(order_str)
            except ValueError:
                return False, f"fila {row_index}: code_order '{order_str}' no es entero"
        else:
            code_order = 0

        return True, CodeLine(
            code_header_id=code_header_id,
            code_id=code_id,
            code_name=code_name,
            code_order=code_order,
        )
