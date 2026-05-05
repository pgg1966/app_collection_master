"""Importador de cards desde CSV."""

import csv
import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from collections_app.core.db.connection import transaction
from collections_app.core.models import Card
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class CsvImportResult:
    """Resumen del resultado de un import."""

    total_rows: int
    imported: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class CardsCsvImporter:
    """Importa cards desde un CSV.

    Formato esperado (UTF-8, separador coma):

        code_id,card_number,card_name
        NON,24,LIONEL MESSI
        MR,1,PAZ

    La primera fila puede o no ser header. Si el primer valor es
    `code_id` (case-insensitive), se asume header y se descarta.

    Validaciones por fila:
      - 3 columnas mínimas.
      - `code_id` debe existir en `codes_lines` del header de la collection.
      - `card_number` debe ser entero positivo.
      - `card_name` no vacío.

    Las filas inválidas se acumulan en `errors` y se omiten — no abortan
    el import. El bulk_upsert final corre dentro de una transacción.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def import_file(
        self,
        csv_path: Path,
        collection_id: int,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CsvImportResult:
        """Lee y procesa el CSV.

        Args:
            csv_path: archivo a leer (UTF-8).
            collection_id: id de la colección a la que pertenecen las cards.
            on_progress: callback `(current, total)` para barras de progreso.

        Returns:
            `CsvImportResult` con totales y errores por fila.

        Raises:
            ValueError: si la collection no existe.
            FileNotFoundError: si el archivo no se puede abrir.
        """
        collection = CollectionsRepository(self.conn).get_by_id(collection_id)
        if collection is None:
            raise ValueError(f"Collection {collection_id} no existe")

        valid_codes = set(
            CodesLinesRepository(self.conn).list_codes_only(collection.code_header_id)
        )

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))

        if not rows:
            return CsvImportResult(0, 0, 0)

        # Detectar header
        first = [c.strip().lower() for c in rows[0]]
        data_rows = rows[1:] if first and first[0] == "code_id" else rows

        total = len(data_rows)
        cards_to_save: list[Card] = []
        errors: list[str] = []
        skipped = 0

        for i, row in enumerate(data_rows, start=1):
            if on_progress:
                on_progress(i, total)
            valid, card_or_error = self._parse_row(row, collection_id, valid_codes, i)
            if not valid:
                errors.append(card_or_error)  # type: ignore[arg-type]
                skipped += 1
                continue
            cards_to_save.append(card_or_error)  # type: ignore[arg-type]

        with transaction(self.conn):
            CardsRepository(self.conn).bulk_upsert(cards_to_save)

        logger.info(
            "Import CSV: total=%d imported=%d skipped=%d errors=%d",
            total,
            len(cards_to_save),
            skipped,
            len(errors),
        )
        return CsvImportResult(
            total_rows=total,
            imported=len(cards_to_save),
            skipped=skipped,
            errors=errors,
        )

    def _parse_row(
        self,
        row: list[str],
        collection_id: int,
        valid_codes: set[str],
        row_index: int,
    ) -> tuple[bool, Card | str]:
        if len(row) < 3:
            return False, f"fila {row_index}: columnas insuficientes"

        code_id = row[0].strip()
        num_str = row[1].strip()
        name = row[2].strip()

        if code_id not in valid_codes:
            return False, f"fila {row_index}: code_id '{code_id}' no existe en el header"

        try:
            num = int(num_str)
        except ValueError:
            return False, f"fila {row_index}: card_number '{num_str}' no es entero"
        if num <= 0:
            return False, f"fila {row_index}: card_number {num} debe ser > 0"

        if not name:
            return False, f"fila {row_index}: card_name vacío"

        return True, Card(
            collection_id=collection_id,
            code_id=code_id,
            card_number=num,
            card_name=name,
        )
