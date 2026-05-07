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

import logging
import sqlite3
from pathlib import Path

from openpyxl import Workbook

from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exceptions import ServiceError

logger = logging.getLogger(__name__)

_TEMPLATE_SHEET_INVENTORY = "Inventario"
_TEMPLATE_SHEET_CODES = "Códigos"
_TEMPLATE_HEADERS_WITH_CODE = ["código", "número", "cantidad"]
_TEMPLATE_HEADERS_WITHOUT_CODE = ["número", "cantidad"]
_CODES_SHEET_HEADERS = ["code_id", "code_name"]


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
