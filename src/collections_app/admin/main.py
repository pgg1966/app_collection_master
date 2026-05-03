"""Entry point de la aplicación admin (configuración)."""

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTabWidget

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.admin.views.crests_view import CrestsView
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path
from collections_app.shared_ui import (
    MainWindowBase,
    SettingsDialog,
    apply_app_style,
)

logger = logging.getLogger(__name__)


class AdminMainWindow(MainWindowBase):
    """Ventana principal del admin con tabs Colecciones / Códigos / Cards / Escudos."""

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name="Collections — Admin")
        self.setMinimumSize(1200, 800)

        self._collections_view = CollectionsAbmView(self.conn)
        self._codes_view = CodesMasterDetailView(self.conn)
        self._cards_view = CardsAbmView(self.conn)
        self._crests_view = CrestsView(self.conn)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._collections_view, self.tr("Colecciones"))
        self._tabs.addTab(self._codes_view, self.tr("Códigos"))
        self._tabs.addTab(self._cards_view, self.tr("Cards"))
        self._tabs.addTab(self._crests_view, self.tr("Escudos"))
        self.setCentralWidget(self._tabs)

        # Cuando se crea/edita o borra una colección, refrescar el combo
        # de Cards para que vea las novedades sin reiniciar la app.
        self._collections_view.abm.record_saved.connect(self._cards_view.refresh_collections_combo)
        self._collections_view.abm.record_deleted.connect(
            self._cards_view.refresh_collections_combo
        )

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
