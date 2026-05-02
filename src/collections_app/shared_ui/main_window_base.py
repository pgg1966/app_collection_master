"""Base común de QMainWindow para admin y client."""

import logging
import sqlite3
from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.services import SettingsService

logger = logging.getLogger(__name__)


class MainWindowBase(QMainWindow):
    """Ventana base con conexión a DB, migraciones, status bar y menús.

    Las subclases deben overridear `_build_menus()` para agregar acciones
    propias. La conexión queda accesible via `self.conn` y se cierra
    automáticamente en `closeEvent`.
    """

    def __init__(self, db_path: Path, app_name: str = "Collections") -> None:
        super().__init__()
        self._app_name = app_name
        self.setWindowTitle(app_name)

        self._db_path = db_path
        self._conn = create_connection(db_path)
        run_migrations(self._conn)
        self._conn.commit()

        self._build_menus()
        self.statusBar()
        self._update_status_bar()

    @property
    def conn(self) -> sqlite3.Connection:
        """Conexión SQLite compartida para toda la ventana."""
        return self._conn

    @property
    def db_path(self) -> Path:
        """Path al archivo de DB. Útil para abrir conexiones nuevas en threads."""
        return self._db_path

    def _build_menus(self) -> None:
        """Hook para que subclases agreguen menús específicos."""
        file_menu = self.menuBar().addMenu(self.tr("&Archivo"))
        exit_action = file_menu.addAction(self.tr("Salir"))
        exit_action.triggered.connect(self.close)

    def _update_status_bar(self) -> None:
        """Refresca el texto de la status bar (colección activa)."""
        active = SettingsService(self._conn).get_active_collection()
        if active is None:
            text = self.tr("Colección activa: ninguna")
        else:
            text = self.tr("Colección activa: {name}").format(name=active.collection_name)
        self.statusBar().showMessage(text)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        try:
            self._conn.close()
        except Exception:
            logger.exception("Error cerrando conexión SQLite")
        super().closeEvent(event)
