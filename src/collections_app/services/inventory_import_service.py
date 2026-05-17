"""Service de importación de inventario desde Excel/CSV (Prompt 4c).

Tres niveles de uso:

- `generate_template(collection_id, dest_path)`: genera un .xlsx vacío
  para que el usuario complete sus cantidades en Excel. Si la
  colección tiene `requires_code=True`, el .xlsx incluye una pestaña
  "Códigos" con los códigos válidos como referencia visual.
- `import_inventory(file_path, collection_id, mode)`: lee el archivo
  (xlsx o csv), valida y aplica al inventario. Modo "replace" pisa
  cantidades; modo "add" suma a las existentes.

Reglas comunes:

- **Formatos:** `.xlsx` (openpyxl) y `.csv` (csv stdlib, encoding
  `utf-8-sig` que acepta UTF-8 plain y UTF-8-BOM transparentemente —
  Excel en Windows guarda CSVs con BOM por default).
- **Atomicidad:** todo el archivo se aplica dentro de un único
  `with self._conn:`. Si una mutación falla a mitad, rollback total.
- **Validación strict por fila:** filas inválidas se acumulan en
  `errors[]`; filas con qty=0 se acumulan en `warnings[]`. Las válidas
  con qty>0 siguen procesándose.
- **Header strict:** el primer renglón debe matchear los headers
  esperados (case-insensitive, trimmed). Si no, el service raise
  `ServiceError` catastrófico — nada se importa.
- **Logging:** cada cambio efectivo en inventory genera una
  `Transaction` con `exchange_event_id` compartido entre todas las
  filas del mismo import (reusa el campo histórico de intercambio
  para agrupar — refactor de naming queda para post-Mundial cuando
  se construya la herramienta admin separada).

Cap en errors y warnings: 200 max, después truncado (mismo patrón
del Prompt 4a).
"""

from __future__ import annotations

import csv
import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from openpyxl import Workbook, load_workbook

from collections_app.core.models.aggregates.inventory_import_report import (
    InventoryImportError,
    InventoryImportReport,
    InventoryImportWarning,
)
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services._event_id import generate_event_id
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

_TEMPLATE_SHEET_INVENTORY = "Inventario"
_TEMPLATE_SHEET_CODES = "Códigos"
_TEMPLATE_HEADERS_WITH_CODE = ["código", "número", "cantidad"]
_TEMPLATE_HEADERS_WITHOUT_CODE = ["número", "cantidad"]
_CODES_SHEET_HEADERS = ["code_id", "code_name"]

# Cap de errores y warnings en el reporte (mismo patrón que Prompt 4a).
_REPORT_CAP = 200

ImportMode = Literal["replace", "add"]


def _utc_now_naive() -> datetime:
    """UTC actual sin tzinfo, matchea el formato del default SQL."""
    return datetime.now(UTC).replace(tzinfo=None)


@dataclass(slots=True)
class _PendingChange:
    """Cambio validado, listo para aplicar dentro del bloque atómico."""

    row_index: int
    card_id: int
    new_qty: int  # cantidad target leída del archivo (>0; qty=0 ya filtrado)


class InventoryImportService:
    """Importer de inventario desde Excel/CSV.

    Compone repos directos (válido en services/) en lugar de delegar
    a InventoryService porque necesita escribir transactions con
    `exchange_event_id` no nulo (agrupador del import) — la API
    pública de InventoryService asume `exchange_event_id=None` para
    el flujo de carga rápida.
    """

    def __init__(self: InventoryImportService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._inventory = InventoryRepository(conn)
        self._cards = CardsRepository(conn)
        self._code_lines = CodeLinesRepository(conn)
        self._transactions = TransactionsRepository(conn)
        self._collections = CollectionsService(conn)

    # ------------------------------------------------------------------
    # Generación del modelo descargable
    # ------------------------------------------------------------------

    def generate_template(
        self: InventoryImportService,
        *,
        collection_id: int,
        dest_path: Path,
    ) -> Path:
        """Genera un .xlsx modelo en `dest_path` para `collection_id`.

        Estructura:

        - Pestaña "Inventario": solo los headers, sin filas. El usuario
          rellena ahí.
        - Pestaña "Códigos" (solo si la colección tiene
          `requires_code=True`): listado de códigos válidos como
          referencia visual. El importer la ignora al leer.

        Si la colección no existe lanza `ServiceError`. Idempotente
        respecto al filesystem: sobrescribe `dest_path` si existía.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            raise ServiceError(f"collection_id={collection_id} no existe")

        wb = Workbook()
        # Pestaña por defecto creada vacía — la renombramos a "Inventario".
        inv_sheet = wb.active
        assert inv_sheet is not None
        inv_sheet.title = _TEMPLATE_SHEET_INVENTORY

        if collection.requires_code:
            inv_sheet.append(_TEMPLATE_HEADERS_WITH_CODE)
            codes_sheet = wb.create_sheet(_TEMPLATE_SHEET_CODES)
            codes_sheet.append(_CODES_SHEET_HEADERS)
            for line in self._code_lines.list_by_header(collection.code_header_id):
                codes_sheet.append([line.code_id, line.code_name])
        else:
            inv_sheet.append(_TEMPLATE_HEADERS_WITHOUT_CODE)

        wb.save(str(dest_path))
        logger.info("generate_template: collection_id=%d dest=%s", collection_id, dest_path)
        return dest_path

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_inventory(
        self: InventoryImportService,
        *,
        file_path: Path,
        collection_id: int,
        mode: ImportMode,
    ) -> InventoryImportReport:
        """Lee `file_path` (xlsx o csv) y aplica el inventario a `collection_id`.

        El encoding de CSV es `utf-8-sig`, que acepta tanto UTF-8 plain
        como UTF-8 con BOM (Excel en Windows guarda CSVs con BOM por
        default; sin esto la validación de header fallaría por un
        carácter invisible al inicio).

        Modos:
        - "replace": la cantidad del archivo pisa la actual.
        - "add": la cantidad del archivo se suma a la actual.

        En ambos modos qty=0 se trata como warning y NO se aplica
        (decisión: si el usuario quiere "borrar" stock, no incluya la
        fila). En modo replace, si la cantidad del archivo coincide con
        la actual el delta es 0 → no se genera transaction pero la fila
        cuenta como aplicada (procesada exitosamente).

        Atomicidad: todo el archivo se aplica dentro de un único
        `with self._conn:`. Si una mutación falla, rollback total.

        Logging: cada cambio efectivo (delta != 0) genera una
        Transaction con `exchange_event_id` compartido por todas las
        filas del mismo import — útil para trazar/revertir el evento
        completo desde el historial.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            raise ServiceError(f"collection_id={collection_id} no existe")

        rows = self._read_rows(file_path)
        if not rows:
            return InventoryImportReport(rows_total=0, rows_applied=0, rows_skipped=0)

        column_indexes, data_rows = self._validate_header(
            rows, requires_code=collection.requires_code
        )

        valid_codes: set[str] = set()
        if collection.requires_code:
            valid_codes = {
                line.code_id for line in self._code_lines.list_by_header(collection.code_header_id)
            }

        # Mapa (code_id, card_number) -> card_id para lookup eficiente cuando
        # `requires_code=True`. Cuando es False usamos `cards_by_number` para
        # resolver por número solo (las cards no necesariamente tienen
        # `code_id=""` en la DB; el caller de admin puede haber usado un
        # placeholder distinto).
        cards = self._cards.list_by_collection(collection_id)
        cards_index: dict[tuple[str, int], int] = {
            (c.code_id, c.card_number): c.card_id for c in cards if c.card_id is not None
        }
        cards_by_number: dict[int, list[int]] = {}
        for c in cards:
            if c.card_id is not None:
                cards_by_number.setdefault(c.card_number, []).append(c.card_id)

        errors: list[InventoryImportError] = []
        warnings_: list[InventoryImportWarning] = []
        pending: list[_PendingChange] = []

        for i, row in enumerate(data_rows, start=1):
            self._classify_row(
                row=row,
                row_index=i,
                column_indexes=column_indexes,
                requires_code=collection.requires_code,
                valid_codes=valid_codes,
                cards_index=cards_index,
                cards_by_number=cards_by_number,
                errors=errors,
                warnings_=warnings_,
                pending=pending,
            )

        # Aplicación atómica. Si cualquier write rompe (FK, sintaxis SQL
        # inesperada, etc.) el bloque hace rollback total.
        rows_applied = 0
        event_id = generate_event_id()
        with self._conn:
            for change in pending:
                applied = self._apply_change(change=change, mode=mode, event_id=event_id)
                if applied:
                    rows_applied += 1

        report = InventoryImportReport(
            rows_total=len(data_rows),
            rows_applied=rows_applied,
            rows_skipped=len(errors) + len(warnings_),
            errors=errors[:_REPORT_CAP],
            warnings=warnings_[:_REPORT_CAP],
        )
        logger.info(
            "import_inventory: file=%s collection_id=%d mode=%s "
            "total=%d applied=%d errors=%d warnings=%d event_id=%d",
            file_path.name,
            collection_id,
            mode,
            report.rows_total,
            report.rows_applied,
            len(errors),
            len(warnings_),
            event_id,
        )
        return report

    # ------------------------------------------------------------------
    # Import por diferencia (lista de faltantes)
    # ------------------------------------------------------------------

    def import_missing(
        self: InventoryImportService,
        *,
        file_path: Path,
        collection_id: int,
    ) -> InventoryImportReport:
        """Aplica un Excel/CSV de FALTANTES como diferencia al inventario.

        Semántica: `inventario_final = todas_las_cards − cards_del_archivo`.
        Para cada card de la colección NO presente en el archivo, queda
        con qty=1. Para cada card presente en el archivo, queda con
        qty=0. La columna `cantidad` del archivo se ignora (no hay
        info de duplicadas — aceptado por diseño).

        Reusa `_read_rows`, `_validate_header` y `_resolve_card_id_from_row`
        para no duplicar lógica de parseo. Filas con código/número
        inválido se acumulan en `errors` y se ignoran.

        Casos borde:
        - Archivo vacío (solo header) → `missing_card_ids=∅` → TODAS
          las cards quedan en qty=1.
        - Archivo cubre toda la colección → todas las cards en qty=0.
        - Cards de la colección con qty>1 previa que NO están en el
          archivo: quedan en qty=1 (replace strict — pierden info de
          duplicadas, aceptado por spec).

        Atomicidad: todos los cambios en un único `with self._conn:`.
        Logging: una `Transaction` por cada cambio efectivo (delta != 0)
        con `exchange_event_id` compartido por todo el import.

        Mapeo del `InventoryImportReport` devuelto:
        - `rows_total`: filas del Excel (faltantes según el archivo).
        - `rows_applied`: cards de la colección que quedaron qty=1.
        - `rows_skipped`: filas del Excel inválidas (errors).
        - `errors`: detalle por fila inválida del archivo.
        - `warnings`: vacío en este flow.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            raise ServiceError(f"collection_id={collection_id} no existe")

        rows = self._read_rows(file_path)
        if not rows:
            data_rows: list[list[str]] = []
            column_indexes: dict[str, int] = {}
        else:
            column_indexes, data_rows = self._validate_header(
                rows, requires_code=collection.requires_code
            )

        valid_codes: set[str] = set()
        if collection.requires_code:
            valid_codes = {
                line.code_id for line in self._code_lines.list_by_header(collection.code_header_id)
            }

        cards = self._cards.list_by_collection(collection_id)
        cards_index: dict[tuple[str, int], int] = {
            (c.code_id, c.card_number): c.card_id for c in cards if c.card_id is not None
        }
        cards_by_number: dict[int, list[int]] = {}
        for c in cards:
            if c.card_id is not None:
                cards_by_number.setdefault(c.card_number, []).append(c.card_id)

        errors: list[InventoryImportError] = []
        missing_card_ids: set[int] = set()

        for i, row in enumerate(data_rows, start=1):
            resolved = self._resolve_card_id_from_row(
                row=row,
                row_index=i,
                column_indexes=column_indexes,
                requires_code=collection.requires_code,
                valid_codes=valid_codes,
                cards_index=cards_index,
                cards_by_number=cards_by_number,
                errors=errors,
            )
            if resolved is None:
                continue
            card_id, _code_id, _number = resolved
            missing_card_ids.add(card_id)

        all_card_ids: set[int] = {c.card_id for c in cards if c.card_id is not None}
        owned_card_ids = all_card_ids - missing_card_ids

        # Aplicación atómica: por cada card de la colección, ajustar la
        # qty al target (1 si "tenida", 0 si "faltante"). Las que ya
        # están en su target generan delta=0 y no producen Transaction.
        rows_applied = 0
        event_id = generate_event_id()
        with self._conn:
            for card_id in owned_card_ids:
                if self._set_qty(card_id=card_id, target_qty=1, event_id=event_id):
                    pass  # cambio efectivo registrado
                rows_applied += 1
            for card_id in missing_card_ids:
                self._set_qty(card_id=card_id, target_qty=0, event_id=event_id)

        report = InventoryImportReport(
            rows_total=len(data_rows),
            rows_applied=rows_applied,
            rows_skipped=len(errors),
            errors=errors[:_REPORT_CAP],
            warnings=[],
        )
        logger.info(
            "import_missing: file=%s collection_id=%d total=%d "
            "owned=%d missing=%d errors=%d event_id=%d",
            file_path.name,
            collection_id,
            report.rows_total,
            len(owned_card_ids),
            len(missing_card_ids),
            len(errors),
            event_id,
        )
        return report

    def _set_qty(
        self: InventoryImportService,
        *,
        card_id: int,
        target_qty: int,
        event_id: int,
    ) -> bool:
        """Ajusta el inventory de `card_id` a `target_qty` exacto.

        Devuelve True si hubo cambio efectivo (delta != 0) y se logueó
        una Transaction; False si la qty ya coincidía con el target.
        """
        current = self._inventory.get_by_card_id(card_id)
        current_qty = current.quantity if current is not None else 0
        delta = target_qty - current_qty
        if delta == 0:
            return False
        self._inventory.adjust_quantity(card_id, delta)
        op = OperationType.ALTA if delta > 0 else OperationType.BAJA
        self._transactions.log(
            Transaction(
                transaction_id=None,
                card_id=card_id,
                operation=op,
                quantity=abs(delta),
                transaction_date=_utc_now_naive(),
                exchange_event_id=event_id,
            )
        )
        return True

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _read_rows(self: InventoryImportService, file_path: Path) -> list[list[str]]:
        """Lee el archivo (xlsx o csv) en memoria como lista de filas de strings."""
        suffix = file_path.suffix.lower()
        if suffix == ".xlsx":
            wb = load_workbook(str(file_path), read_only=True, data_only=True)
            try:
                # Primera pestaña por posición (la pestaña "Códigos" si
                # existe se ignora).
                sheet = wb.worksheets[0]
                rows: list[list[str]] = []
                for raw in sheet.iter_rows(values_only=True):
                    rows.append(["" if v is None else str(v).strip() for v in raw])
            finally:
                wb.close()
            # Filas vacías al final del sheet ("", "", ...) — descartarlas.
            while rows and not any(c for c in rows[-1]):
                rows.pop()
            return rows
        if suffix == ".csv":
            with file_path.open("r", encoding="utf-8-sig", newline="") as fh:
                return [[c.strip() for c in row] for row in csv.reader(fh)]
        raise ServiceError(f"formato no soportado: {suffix!r}. Use .xlsx o .csv.")

    def _validate_header(
        self: InventoryImportService,
        rows: list[list[str]],
        *,
        requires_code: bool,
    ) -> tuple[dict[str, int], list[list[str]]]:
        """Verifica que la primera fila matchee los headers esperados.

        Si no, raise ServiceError catastrófico — nada se importa.
        Devuelve `(column_indexes, data_rows)` con la primera fila ya
        consumida.
        """
        expected = _TEMPLATE_HEADERS_WITH_CODE if requires_code else _TEMPLATE_HEADERS_WITHOUT_CODE
        first = [c.strip().lower() for c in rows[0]]
        if first[: len(expected)] != expected:
            raise ServiceError(
                "El archivo no tiene los headers esperados "
                f"({', '.join(expected)}). Volvé a descargar el modelo."
            )
        column_indexes = {name: i for i, name in enumerate(expected)}
        return column_indexes, rows[1:]

    def _classify_row(
        self: InventoryImportService,
        *,
        row: list[str],
        row_index: int,
        column_indexes: dict[str, int],
        requires_code: bool,
        valid_codes: set[str],
        cards_index: dict[tuple[str, int], int],
        cards_by_number: dict[int, list[int]],
        errors: list[InventoryImportError],
        warnings_: list[InventoryImportWarning],
        pending: list[_PendingChange],
    ) -> None:
        """Valida una fila y la clasifica en errors / warnings / pending."""
        resolved = self._resolve_card_id_from_row(
            row=row,
            row_index=row_index,
            column_indexes=column_indexes,
            requires_code=requires_code,
            valid_codes=valid_codes,
            cards_index=cards_index,
            cards_by_number=cards_by_number,
            errors=errors,
        )
        if resolved is None:
            return
        card_id, code_id, number = resolved

        qty_str = self._cell(row, column_indexes, "cantidad")
        try:
            qty = int(qty_str)
        except ValueError:
            errors.append(InventoryImportError(row_index, f"cantidad {qty_str!r} no es entero"))
            return
        if qty < 0:
            errors.append(InventoryImportError(row_index, f"cantidad {qty} no puede ser negativa"))
            return

        if qty == 0:
            warnings_.append(
                InventoryImportWarning(
                    row_index=row_index,
                    code_id=code_id,
                    card_number=number,
                    message="cantidad = 0; fila ignorada",
                )
            )
            return

        pending.append(_PendingChange(row_index, card_id, qty))

    def _resolve_card_id_from_row(
        self: InventoryImportService,
        *,
        row: list[str],
        row_index: int,
        column_indexes: dict[str, int],
        requires_code: bool,
        valid_codes: set[str],
        cards_index: dict[tuple[str, int], int],
        cards_by_number: dict[int, list[int]],
        errors: list[InventoryImportError],
    ) -> tuple[int, str, int] | None:
        """Resuelve `(card_id, code_id, card_number)` desde una fila.

        Encapsula la lectura y validación de las columnas `código` y
        `número` y el lookup en el catálogo de cards. Si la fila es
        inválida, agrega el error a `errors` y devuelve `None`. La
        columna `cantidad` NO se toca acá — la maneja el caller según
        contexto (import normal usa qty del archivo; import_missing la
        ignora).
        """
        code_id = ""
        if requires_code:
            code_id = self._cell(row, column_indexes, "código")
            if not code_id:
                errors.append(InventoryImportError(row_index, "código vacío"))
                return None
            if code_id not in valid_codes:
                errors.append(
                    InventoryImportError(row_index, f"código {code_id!r} no existe en el header")
                )
                return None

        num_str = self._cell(row, column_indexes, "número")
        try:
            number = int(num_str)
        except ValueError:
            errors.append(InventoryImportError(row_index, f"número {num_str!r} no es entero"))
            return None
        if number <= 0:
            errors.append(InventoryImportError(row_index, f"número {number} debe ser > 0"))
            return None

        if requires_code:
            card_id = cards_index.get((code_id, number))
            if card_id is None:
                errors.append(
                    InventoryImportError(
                        row_index,
                        f"card ({code_id!r}, {number}) no existe en el catálogo",
                    )
                )
                return None
        else:
            matches = cards_by_number.get(number, [])
            if not matches:
                errors.append(
                    InventoryImportError(
                        row_index,
                        f"card con número {number} no existe en el catálogo",
                    )
                )
                return None
            if len(matches) > 1:
                errors.append(
                    InventoryImportError(
                        row_index,
                        (
                            f"el número {number} existe más de una vez en esta "
                            f"colección. Revisá los datos."
                        ),
                    )
                )
                return None
            card_id = matches[0]

        return card_id, code_id, number

    def _cell(
        self: InventoryImportService,
        row: list[str],
        column_indexes: dict[str, int],
        name: str,
    ) -> str:
        idx = column_indexes.get(name)
        if idx is None or idx >= len(row):
            return ""
        return row[idx].strip()

    def _apply_change(
        self: InventoryImportService,
        *,
        change: _PendingChange,
        mode: ImportMode,
        event_id: int,
    ) -> bool:
        """Aplica un cambio validado al inventory + log de transaction.

        Devuelve True si el cambio se aplicó exitosamente. En modo
        replace con delta=0, devuelve True (la fila se procesó OK) sin
        generar transaction.
        """
        current = self._inventory.get_by_card_id(change.card_id)
        current_qty = current.quantity if current is not None else 0

        if mode == "replace":
            delta = change.new_qty - current_qty
        elif mode == "add":
            delta = change.new_qty
        else:
            raise ServiceError(f"mode {mode!r} no soportado")

        if delta == 0:
            return True
        if delta > 0:
            self._inventory.adjust_quantity(change.card_id, delta)
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    card_id=change.card_id,
                    operation=OperationType.ALTA,
                    quantity=delta,
                    transaction_date=_utc_now_naive(),
                    exchange_event_id=event_id,
                )
            )
        else:
            self._inventory.adjust_quantity(change.card_id, delta)
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    card_id=change.card_id,
                    operation=OperationType.BAJA,
                    quantity=-delta,
                    transaction_date=_utc_now_naive(),
                    exchange_event_id=event_id,
                )
            )
        return True
