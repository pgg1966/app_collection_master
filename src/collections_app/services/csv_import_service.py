"""Service de importación de CSVs.

Importer del Prompt 4. Tres niveles de uso:

- `import_codes(csv_path, code_header_name)`: importa filas a las
  `codes_lines` del header dado.
- `import_cards(csv_path, collection_name)`: importa filas a las `cards`
  de la colección dada.
- `import_collection_from_csvs(...)`: facade que crea header y
  colección si no existen y delega a las dos primeras según qué CSVs
  se provean.

Reglas comunes:

- **Encoding fijo UTF-8.** Otros encodings se agregan como flag cuando
  aparezcan en archivos reales.
- **Idempotencia:** las filas se persisten vía `*Service.upsert` (o
  `bulk_upsert` para cards). Re-ejecutar es seguro.
- **Atomicidad por archivo:** `with self._conn:` envuelve los writes
  de cada `import_codes` / `import_cards`. Una excepción no de
  validación dispara rollback total del archivo.
- **Validación strict por fila:** filas inválidas se acumulan en
  `errors[]`; las válidas siguen procesándose. Las domain errors
  (`CodeLinesError`, `CardsError`) se traducen a `CsvImportError`.
- **Detección de header:** primera fila con `code_id` (case-insensitive)
  en alguna columna se trata como header y se descarta del conteo de
  filas de datos. Si no, asume orden posicional default.

El service usa los **services existentes**, nunca los repos directos.
Eso preserva las validaciones de negocio (max_length de code_id,
collection FK, etc.) que viven en la capa de servicios.
"""

from __future__ import annotations

import csv
import logging
import sqlite3
from pathlib import Path

from collections_app.core.models.aggregates.csv_import_report import (
    CsvImportError,
    CsvImportReport,
)
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.services.cards_service import CardsService
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exceptions import (
    CardsError,
    CodeHeadersError,
    CodeLinesError,
    CollectionsError,
)

logger = logging.getLogger(__name__)

# Mapeo posicional cuando el CSV no trae header.
_CODES_DEFAULT_INDEXES: dict[str, int] = {
    "code_id": 0,
    "code_name": 1,
    "code_order": 2,
}
_CARDS_DEFAULT_INDEXES: dict[str, int] = {
    "code_id": 0,
    "card_number": 1,
    "card_name": 2,
}


class CsvImportService:
    """Importer de CSVs de codes y cards."""

    def __init__(self: CsvImportService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._code_headers = CodeHeadersService(conn)
        self._code_lines = CodeLinesService(conn)
        self._collections = CollectionsService(conn)
        self._cards = CardsService(conn)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def import_codes(
        self: CsvImportService,
        csv_path: Path,
        code_header_name: str,
    ) -> CsvImportReport:
        """Importa filas de codes_lines al header dado.

        Lanza `CodeHeadersError` si el header no existe (catastrófico:
        nada se importa).
        """
        header = self._code_headers.get_by_name(code_header_name)
        if header is None:
            raise CodeHeadersError(f"code_header {code_header_name!r} no existe; crear primero")
        assert header.code_header_id is not None

        rows = self._read_csv_rows(csv_path)
        column_indexes, data_rows = self._detect_columns(rows, _CODES_DEFAULT_INDEXES)

        valid_lines: list[CodeLine] = []
        errors: list[CsvImportError] = []
        for i, row in enumerate(data_rows, start=1):
            parsed = self._parse_code_row(row, header, column_indexes, i, errors)
            if parsed is not None:
                valid_lines.append(parsed)

        with self._conn:
            for line in valid_lines:
                # Defensa: si el service rechaza la línea (mismatch entre
                # validaciones), la convertimos en error de import pero
                # usamos un row_index sentinel (-1) para indicar "no se
                # puede mapear a una fila específica del CSV".
                try:
                    self._code_lines.upsert(line)
                except CodeLinesError as exc:
                    errors.append(CsvImportError(row_index=-1, message=str(exc)))

        rows_skipped = len(errors)
        rows_inserted = len(data_rows) - rows_skipped
        logger.info(
            "import_codes: total=%d inserted=%d skipped=%d",
            len(data_rows),
            rows_inserted,
            rows_skipped,
        )
        return CsvImportReport(
            rows_total=len(data_rows),
            rows_inserted=rows_inserted,
            rows_skipped=rows_skipped,
            errors=errors,
        )

    def import_cards(
        self: CsvImportService,
        csv_path: Path,
        collection_name: str,
    ) -> CsvImportReport:
        """Importa filas de cards a la colección dada.

        Lanza `CollectionsError` si la colección no existe (catastrófico).
        Validación FK: cada `code_id` debe estar en `codes_lines` del
        header de la colección, sino la fila falla con error.
        """
        collection = self._collections.get_by_name(collection_name)
        if collection is None:
            raise CollectionsError(f"collection {collection_name!r} no existe; crear primero")
        assert collection.collection_id is not None
        valid_codes = {
            line.code_id for line in self._code_lines.list_by_header(collection.code_header_id)
        }

        rows = self._read_csv_rows(csv_path)
        column_indexes, data_rows = self._detect_columns(rows, _CARDS_DEFAULT_INDEXES)

        valid_cards: list[Card] = []
        errors: list[CsvImportError] = []
        for i, row in enumerate(data_rows, start=1):
            parsed = self._parse_card_row(
                row,
                collection.collection_id,
                valid_codes,
                column_indexes,
                i,
                errors,
            )
            if parsed is not None:
                valid_cards.append(parsed)

        with self._conn:
            if valid_cards:
                self._cards.bulk_upsert(valid_cards)

        logger.info(
            "import_cards: total=%d inserted=%d skipped=%d",
            len(data_rows),
            len(valid_cards),
            len(errors),
        )
        return CsvImportReport(
            rows_total=len(data_rows),
            rows_inserted=len(valid_cards),
            rows_skipped=len(errors),
            errors=errors,
        )

    def import_collection_from_csvs(
        self: CsvImportService,
        *,
        collection_name: str,
        code_header_name: str,
        code_field_name: str,
        code_max_length: int,
        requires_code: bool,
        codes_csv_path: Path | None,
        cards_csv_path: Path | None,
    ) -> dict[str, CsvImportReport]:
        """Facade: asegura header + collection y delega a las importers.

        Crea el header (si no existe) y la collection (si no existe).
        Si solo se provee `codes_csv_path` o solo `cards_csv_path`, el
        dict resultante incluye solo la clave correspondiente.

        Las creaciones de header / collection NO se envuelven en la
        misma transacción que las importaciones; cada paso es atómico
        individualmente. Si la importación de cards falla, header,
        collection y codes ya quedan persistidos — re-ejecutar es
        seguro por idempotencia.
        """
        header = self._code_headers.get_by_name(code_header_name)
        if header is None:
            header = self._code_headers.create(
                CodeHeader(
                    code_header_id=None,
                    code_header_name=code_header_name,
                    code_max_length=code_max_length,
                )
            )
        assert header.code_header_id is not None

        collection = self._collections.get_by_name(collection_name)
        if collection is None:
            collection = self._collections.create(
                Collection(
                    collection_id=None,
                    collection_name=collection_name,
                    card_count=0,
                    requires_code=requires_code,
                    code_field_name=code_field_name,
                    code_header_id=header.code_header_id,
                )
            )
        # commit explícito por si el caller espera ver el header/collection
        # después aún si falla la importación.
        self._conn.commit()

        reports: dict[str, CsvImportReport] = {}
        if codes_csv_path is not None:
            reports["codes"] = self.import_codes(codes_csv_path, code_header_name=code_header_name)
        if cards_csv_path is not None:
            reports["cards"] = self.import_cards(cards_csv_path, collection_name=collection_name)
        return reports

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _read_csv_rows(self: CsvImportService, csv_path: Path) -> list[list[str]]:
        """Lee el CSV completo (UTF-8, separador coma) en memoria."""
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.reader(fh))

    def _detect_columns(
        self: CsvImportService,
        rows: list[list[str]],
        default_indexes: dict[str, int],
    ) -> tuple[dict[str, int], list[list[str]]]:
        """Detecta header. Si la primera fila contiene `code_id`, la
        descarta y construye `column_indexes` por nombre. Sino usa el
        mapping posicional default.
        """
        if not rows:
            return default_indexes, []
        first_lower = [c.strip().lower() for c in rows[0]]
        if "code_id" in first_lower:
            mapping: dict[str, int] = {}
            for i, name in enumerate(first_lower):
                if name in default_indexes:
                    mapping[name] = i
                # cualquier otra columna se ignora silenciosamente
            return mapping, rows[1:]
        return default_indexes, rows

    def _cell(
        self: CsvImportService,
        row: list[str],
        column_indexes: dict[str, int],
        name: str,
    ) -> str:
        idx = column_indexes.get(name)
        if idx is None or idx >= len(row):
            return ""
        return row[idx].strip()

    def _parse_code_row(
        self: CsvImportService,
        row: list[str],
        header: CodeHeader,
        column_indexes: dict[str, int],
        row_index: int,
        errors: list[CsvImportError],
    ) -> CodeLine | None:
        code_id = self._cell(row, column_indexes, "code_id")
        code_name = self._cell(row, column_indexes, "code_name")
        order_str = self._cell(row, column_indexes, "code_order")

        if not code_id:
            errors.append(CsvImportError(row_index=row_index, message="code_id vacío"))
            return None
        if len(code_id) > header.code_max_length:
            errors.append(
                CsvImportError(
                    row_index=row_index,
                    message=(f"code_id {code_id!r} excede max_length=" f"{header.code_max_length}"),
                )
            )
            return None
        if not code_name:
            errors.append(CsvImportError(row_index=row_index, message="code_name vacío"))
            return None
        code_order = 0
        if order_str:
            try:
                code_order = int(order_str)
            except ValueError:
                errors.append(
                    CsvImportError(
                        row_index=row_index,
                        message=f"code_order {order_str!r} no es entero",
                    )
                )
                return None
        assert header.code_header_id is not None
        return CodeLine(
            code_line_id=None,
            code_header_id=header.code_header_id,
            code_id=code_id,
            code_name=code_name,
            code_order=code_order,
        )

    def _parse_card_row(
        self: CsvImportService,
        row: list[str],
        collection_id: int,
        valid_codes: set[str],
        column_indexes: dict[str, int],
        row_index: int,
        errors: list[CsvImportError],
    ) -> Card | None:
        code_id = self._cell(row, column_indexes, "code_id")
        num_str = self._cell(row, column_indexes, "card_number")
        name = self._cell(row, column_indexes, "card_name")

        if not code_id:
            errors.append(CsvImportError(row_index=row_index, message="code_id vacío"))
            return None
        if code_id not in valid_codes:
            errors.append(
                CsvImportError(
                    row_index=row_index,
                    message=f"code_id {code_id!r} no existe en el header",
                )
            )
            return None
        try:
            number = int(num_str)
        except ValueError:
            errors.append(
                CsvImportError(
                    row_index=row_index,
                    message=f"card_number {num_str!r} no es entero",
                )
            )
            return None
        if number <= 0:
            errors.append(
                CsvImportError(
                    row_index=row_index,
                    message=f"card_number {number} debe ser > 0",
                )
            )
            return None
        if not name:
            errors.append(CsvImportError(row_index=row_index, message="card_name vacío"))
            return None
        try:
            # Validación a nivel service: sirve como segunda red, aunque
            # los chequeos básicos ya quedaron arriba.
            card = Card(
                card_id=None,
                collection_id=collection_id,
                code_id=code_id,
                card_number=number,
                card_name=name,
            )
            self._cards._validate(card)  # type: ignore[attr-defined]
        except CardsError as exc:
            errors.append(CsvImportError(row_index=row_index, message=str(exc)))
            return None
        return card
