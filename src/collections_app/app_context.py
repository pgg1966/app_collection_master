"""Container de servicios y conexión SQLite para el bootstrap de la app.

`AppContext` se construye una vez en `main.py` (o en un fixture de test)
y se le pasa a las vistas explícitamente — no es un singleton ni un
service locator. La inversión de dependencias queda clara: la vista
recibe el service que necesita, no el contenedor entero.

Uso típico:

    ctx = create_app_context(get_default_db_path())
    view = CardLoaderView(ctx=ctx, collection=...)

Tests pueden construir un context contra `:memory:`:

    ctx = create_app_context(":memory:")
"""

from __future__ import annotations

import contextlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.services.cards_service import CardsService
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.collections_service import CollectionsService
from collections_app.services.csv_import_service import CsvImportService
from collections_app.services.exchange_apply_service import ExchangeApplyService
from collections_app.services.exchange_export_service import ExchangeExportService
from collections_app.services.exchange_import_service import ExchangeImportService
from collections_app.services.inventory_import_service import InventoryImportService
from collections_app.services.inventory_service import InventoryService
from collections_app.services.inventory_snapshot_service import InventorySnapshotService
from collections_app.services.settings_service import SettingsService
from collections_app.services.transactions_service import TransactionsService


@dataclass(slots=True)
class AppContext:
    """Container con la conexión y todos los services instanciados."""

    conn: sqlite3.Connection
    inventory: InventoryService
    collections: CollectionsService
    cards: CardsService
    code_headers: CodeHeadersService
    code_lines: CodeLinesService
    transactions: TransactionsService
    settings: SettingsService
    csv_import: CsvImportService
    inventory_import: InventoryImportService
    inventory_snapshot: InventorySnapshotService
    exchange_export: ExchangeExportService
    exchange_import: ExchangeImportService
    exchange_apply: ExchangeApplyService

    def close(self: AppContext) -> None:
        """Cierra la conexión SQLite. Idempotente."""
        # Conexión ya cerrada o inválida → nada que hacer.
        with contextlib.suppress(sqlite3.Error):
            self.conn.close()


def create_app_context(db_path: Path | str) -> AppContext:
    """Construye un `AppContext` aplicando migraciones contra `db_path`.

    Acepta `:memory:` para tests. Para producción usar
    `core.utils.paths.get_default_db_path()`.
    """
    conn = create_connection(db_path)
    run_migrations(conn)
    return AppContext(
        conn=conn,
        inventory=InventoryService(conn),
        collections=CollectionsService(conn),
        cards=CardsService(conn),
        code_headers=CodeHeadersService(conn),
        code_lines=CodeLinesService(conn),
        transactions=TransactionsService(conn),
        settings=SettingsService(conn),
        csv_import=CsvImportService(conn),
        inventory_import=InventoryImportService(conn),
        inventory_snapshot=InventorySnapshotService(conn),
        exchange_export=ExchangeExportService(conn),
        exchange_import=ExchangeImportService(conn),
        exchange_apply=ExchangeApplyService(conn),
    )
