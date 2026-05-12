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
from typing import TYPE_CHECKING

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.services.cards_service import CardsService
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.collections_service import CollectionsService
from collections_app.services.csv_import_service import CsvImportService
from collections_app.services.exceptions import OcrError
from collections_app.services.exchange_apply_service import ExchangeApplyService
from collections_app.services.exchange_export_service import ExchangeExportService
from collections_app.services.exchange_import_service import ExchangeImportService
from collections_app.services.inventory_import_service import InventoryImportService
from collections_app.services.inventory_service import InventoryService
from collections_app.services.inventory_snapshot_service import InventorySnapshotService
from collections_app.services.ocr_install_service import OcrInstallService
from collections_app.services.settings_service import SettingsService
from collections_app.services.transactions_service import TransactionsService

if TYPE_CHECKING:
    from collections_app.core.models.collection import Collection
    from collections_app.services.ocr_service import OcrService


@dataclass(slots=True)
class AppContext:
    """Container con la conexión y todos los services instanciados.

    `db_path` se conserva como string (no `Path`) porque puede ser
    el literal `:memory:` que NO es un path de filesystem. Es lo
    que se le pasa a `sqlite3.connect` cuando un worker de QThread
    necesita su propia conexión (CLAUDE.md sec 2.1 + fix post-5d:
    no compartir Connection cross-thread).
    """

    conn: sqlite3.Connection
    db_path: str
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
    ocr_install: OcrInstallService

    def close(self: AppContext) -> None:
        """Cierra la conexión SQLite. Idempotente."""
        # Conexión ya cerrada o inválida → nada que hacer.
        with contextlib.suppress(sqlite3.Error):
            self.conn.close()

    def create_worker_connection(self: AppContext) -> sqlite3.Connection:
        """Abre una `sqlite3.Connection` nueva apuntando a la misma DB.

        Los views NO pueden importar `core.db.connection` (CLAUDE.md sec
        2.1), así que el ctx — que sí puede — expone este helper. Lo usan
        los workers de QThread que necesitan su propia conexión, ya que
        SQLite no permite compartir Connection entre hilos.

        El caller es responsable de cerrar la conexión (`with` o try/finally).
        """
        return create_connection(self.db_path)

    def get_ocr_guide_path(self: AppContext, collection: Collection) -> Path | None:
        """Path absoluto de la imagen de guía OCR de `collection`.

        Devuelve `None` si la colección no tiene `ocr_guide_filename`
        configurado o si el archivo no existe en disco. El caller
        (OcrLoaderTab) usa esto para decidir si renderiza la imagen o
        no.
        """
        if not collection.ocr_guide_filename:
            return None
        # Import lazy: paths.py NO se quiere cargar al testear el
        # AppContext con `:memory:` (no hace falta).
        from collections_app.core.utils.paths import get_images_dir  # noqa: PLC0415

        path = get_images_dir() / collection.ocr_guide_filename
        return path if path.is_file() else None

    def get_ocr_model_path(self: AppContext, collection: Collection) -> Path | None:
        """Path absoluto del modelo OCR de `collection`.

        Devuelve `None` si la colección no tiene `ocr_model_filename`
        configurado o si el archivo no existe en disco. La vista usa
        este helper (vs. importar `get_models_dir()` directo, lo cual
        violaría la regla de capas) para distinguir:
        - `collection.ocr_model_filename` truthy AND retorno None →
          modelo configurado en DB pero NO en disco. Variante "necesita
          descarga" del Estado 2 del OcrLoaderTab.
        - `collection.ocr_model_filename` falsy → modelo no configurado.
          Variante "pedile al admin".
        """
        if not collection.ocr_model_filename:
            return None
        from collections_app.core.utils.paths import get_models_dir  # noqa: PLC0415

        path = get_models_dir() / collection.ocr_model_filename
        return path if path.is_file() else None

    def get_ocr_service(self: AppContext, collection: Collection) -> OcrService | None:
        """Factory de `OcrService` para una colección específica.

        Devuelve `None` si:
        - Las dependencias (torch / ultralytics) no están instaladas.
        - La colección no tiene modelo configurado.
        - El archivo del modelo no existe en `get_models_dir()`.
        - El modelo existe pero no se pudo cargar (versión incompatible,
          archivo corrupto, etc.) → captura `OcrError` y devuelve None
          para que la UI caiga al Estado 2 sin crashear.

        El `OcrService` no se cachea: cada llamada re-evalúa el estado y
        re-intenta cargar. La construcción es barata cuando todo está OK
        (importa YOLO + carga el modelo) y la UI llama esto una vez por
        colección al cambiar de tab.
        """
        if not OcrInstallService.is_installed():
            return None
        if not collection.ocr_model_filename:
            return None
        # Import lazy: solo si llegamos hasta acá.
        from collections_app.core.utils.paths import get_models_dir  # noqa: PLC0415
        from collections_app.services.ocr_service import OcrService  # noqa: PLC0415

        path = get_models_dir() / collection.ocr_model_filename
        if not path.is_file():
            return None
        try:
            return OcrService(path)
        except OcrError:
            return None


def create_app_context(db_path: Path | str) -> AppContext:
    """Construye un `AppContext` aplicando migraciones contra `db_path`.

    Acepta `:memory:` para tests. Para producción usar
    `core.utils.paths.get_default_db_path()`.
    """
    conn = create_connection(db_path)
    run_migrations(conn)
    return AppContext(
        conn=conn,
        db_path=str(db_path),
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
        ocr_install=OcrInstallService(),
    )
