"""Entry point de la aplicación client (uso final)."""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QWidget

from collections_app.client.dialogs.client_settings_dialog import ClientSettingsDialog
from collections_app.client.views.album_view import AlbumView
from collections_app.client.views.card_loader import CardLoaderView
from collections_app.client.views.inventory_view import InventoryView
from collections_app.client.views.reports_view import ReportsView
from collections_app.client.views.stats_view import StatsView
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path
from collections_app.shared_ui import MainWindowBase, apply_app_style

logger = logging.getLogger(__name__)


class ClientMainWindow(MainWindowBase):
    """Ventana principal del cliente.

    Al iniciar pide elegir una colección (o valida la licencia si la
    colección activa es premium). Solo expone "Cambiar colección" en el
    menú — el cliente no debe acceder a los ABMs de configuración.
    """

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name="Collections")
        self.setMinimumSize(900, 700)
        self._card_loader: CardLoaderView | None = None
        # Diferimos la inicialización para que la ventana se muestre primero
        # y el SettingsDialog tenga un parent visible.
        QTimer.singleShot(0, self._initialize_active_collection)

    # ------------------------------------------------------------------
    # Menús
    # ------------------------------------------------------------------

    def _build_menus(self) -> None:
        super()._build_menus()
        config_menu = self.menuBar().addMenu(self.tr("&Configuración"))
        action = config_menu.addAction(self.tr("Cambiar colección..."))
        action.triggered.connect(self._open_settings)

    # ------------------------------------------------------------------
    # Inicialización del estado
    # ------------------------------------------------------------------

    def _initialize_active_collection(self) -> None:
        """Si no hay colección activa o no está unlocked, pedirla."""
        from collections_app.core.services import LicenseService, SettingsService

        settings = SettingsService(self.conn)
        licenses = LicenseService(self.conn)
        active = settings.get_active_collection()

        needs_dialog = active is None
        if active is not None and active.collection_id is not None:
            needs_dialog = not licenses.is_unlocked(active.collection_id)

        if needs_dialog:
            self._open_settings()
        else:
            self._build_central_widget()

    def _open_settings(self) -> None:
        dlg = ClientSettingsDialog(self.conn, parent=self)
        if dlg.exec():
            self._build_central_widget()
            self._update_status_bar()
        else:
            # Usuario canceló: si todavía no hay colección activa, mostramos
            # placeholder para que la ventana no quede vacía.
            if self.centralWidget() is None:
                self._build_placeholder()

    # ------------------------------------------------------------------
    # Construcción del central widget
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        from collections_app.core.services import SettingsService

        active = SettingsService(self.conn).get_active_collection()
        if active is None:
            self._build_placeholder()
            return

        tabs = QTabWidget()
        self._card_loader = CardLoaderView(self.conn, active)
        self._inventory_view = InventoryView(self.conn, active)
        self._album_view = AlbumView(self.conn, active)
        self._stats_view = StatsView(self.conn, active)
        self._reports_view = ReportsView(self.conn, active)

        tabs.addTab(self._card_loader, self.tr("Cargar Cards"))
        tabs.addTab(self._inventory_view, self.tr("Inventario"))
        tabs.addTab(self._album_view, self.tr("Álbum"))
        tabs.addTab(self._stats_view, self.tr("Estadísticas"))
        tabs.addTab(self._reports_view, self.tr("Reportes"))
        self.setCentralWidget(tabs)

        # Auto-refresh de vistas afectadas tras una alta/baja en CardLoader.
        # Reports y Álbum quedan fuera: el usuario los dispara explícitamente.
        self._card_loader.card_changed.connect(self._inventory_view.refresh)
        self._card_loader.card_changed.connect(self._stats_view.refresh)

    def _build_placeholder(self) -> None:
        placeholder = QLabel(
            self.tr("Seleccione una colección desde Configuración → Cambiar colección…")
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)

    def _placeholder_widget(self) -> QWidget:
        label = QLabel(self.tr("Próximamente"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label


def main() -> int:
    """Entry point. Inicializa logging, abre la ventana principal."""
    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info("Client app — bootstrap OK (db=%s)", db_path)

    app = QApplication(sys.argv)
    apply_app_style(app)
    window = ClientMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
