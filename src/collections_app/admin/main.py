"""Entry point de la aplicación admin (configuración)."""

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTabWidget

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.admin.views.crests_view import CrestsView
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import (
    get_active_profile,
    get_database_path,
    set_active_profile,
)
from collections_app.shared_ui import (
    MainWindowBase,
    SettingsDialog,
    apply_app_style,
)

logger = logging.getLogger(__name__)

_APP_NAME = "Collections — Admin"


class AdminMainWindow(MainWindowBase):
    """Ventana principal del admin con tabs Colecciones / Códigos / Cards / Escudos."""

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name=_APP_NAME)
        title = _APP_NAME
        if get_active_profile() != "default":
            title += f"  [{get_active_profile()}]"
        self.setWindowTitle(title)
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
    # Parsear --profile antes de cualquier inicialización que toque
    # paths/DB. Ver collections_app.core.utils.paths.set_active_profile.
    parser = argparse.ArgumentParser(add_help=False, description=_APP_NAME)
    parser.add_argument(
        "--profile",
        default="default",
        help="Perfil de datos (alfanumérico). Default: 'default'.",
    )
    args, remaining = parser.parse_known_args()
    set_active_profile(args.profile)

    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info("Admin app — bootstrap OK (profile=%s, db=%s)", get_active_profile(), db_path)

    app = QApplication([sys.argv[0], *remaining])
    apply_app_style(app)
    window = AdminMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
