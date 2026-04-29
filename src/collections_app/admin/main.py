"""Entry point de la aplicación admin (configuración)."""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path
from collections_app.shared_ui import (
    MainWindowBase,
    SettingsDialog,
    apply_app_style,
)

logger = logging.getLogger(__name__)


class AdminMainWindow(MainWindowBase):
    """Ventana principal del admin."""

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name="Collections — Admin")
        self.setMinimumSize(1024, 768)

    def _build_menus(self) -> None:
        super()._build_menus()
        config_menu = self.menuBar().addMenu(self.tr("&Configuración"))
        action = config_menu.addAction(self.tr("Settings..."))
        action.triggered.connect(self._open_settings)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.conn, parent=self)
        if dlg.exec():
            self._update_status_bar()


def main() -> int:
    """Entry point. Inicializa logging, abre la ventana principal."""
    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info("Admin app — bootstrap OK (db=%s)", db_path)

    app = QApplication(sys.argv)
    apply_app_style(app)
    window = AdminMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
