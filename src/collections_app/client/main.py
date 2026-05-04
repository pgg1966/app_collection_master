"""Entry point de la aplicación client (uso final)."""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from collections_app.__version__ import __app_name__, __version__
from collections_app.client.dialogs.client_settings_dialog import ClientSettingsDialog
from collections_app.client.views.album_view import AlbumView
from collections_app.client.views.card_loader import CardLoaderView
from collections_app.client.views.inventory_view import InventoryView
from collections_app.client.views.reports_view import ReportsView
from collections_app.client.views.stats_view import StatsView
from collections_app.core.repositories import SettingsRepository
from collections_app.core.services.update_service import (
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path
from collections_app.shared_ui import MainWindowBase, apply_app_style

logger = logging.getLogger(__name__)

# Settings keys usadas para persistir el estado del update checker.
SETTING_SKIPPED_VERSION = "skipped_version"
SETTING_SERVER_URL = "server_url"
SETTING_SERVER_API_KEY = "server_api_key"

# Delay antes de chequear updates al arrancar. Damos margen para que la
# UI quede 100% interactiva antes de tirar un request HTTP en background.
UPDATE_CHECK_DELAY_MS = 3_000


class _UpdateCheckWorker(QThread):
    """Chequea updates en un thread separado para no bloquear la UI.

    No accede a la DB ni a otros recursos compartidos: solo invoca la
    `UpdateSource` (red). El resultado se entrega via signal — el slot
    receptor corre en el thread de la UI, así que es seguro tocar widgets.
    """

    update_found = Signal(object)  # UpdateInfo
    no_update = Signal()

    def __init__(
        self,
        source: UpdateSource | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source

    def run(self) -> None:
        try:
            service = UpdateService(self._source) if self._source else UpdateService()
            info = service.check_for_updates()
            if info and info.is_newer:
                self.update_found.emit(info)
            else:
                self.no_update.emit()
        except Exception:
            logger.exception("UpdateCheckWorker: fallo inesperado")
            self.no_update.emit()


class ClientMainWindow(MainWindowBase):
    """Ventana principal del cliente.

    Al iniciar pide elegir una colección (o valida la licencia si la
    colección activa es premium). Solo expone "Cambiar colección" en el
    menú — el cliente no debe acceder a los ABMs de configuración.
    """

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name=__app_name__)
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(900, 700)
        self._card_loader: CardLoaderView | None = None
        self._update_worker: _UpdateCheckWorker | None = None
        # Diferimos la inicialización para que la ventana se muestre primero
        # y el SettingsDialog tenga un parent visible.
        QTimer.singleShot(0, self._initialize_active_collection)
        # Update check con delay: la UI debe estar viva antes de pegarle
        # a la red. Si el usuario cierra antes, el worker queda colgando
        # pero `parent=self` lo limpia al destruirse la ventana.
        QTimer.singleShot(UPDATE_CHECK_DELAY_MS, self._start_update_check)

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
        self._album_view = AlbumView(self.conn, self.db_path, active)
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

    # ------------------------------------------------------------------
    # Update checker
    # ------------------------------------------------------------------

    def _start_update_check(self) -> None:
        """Lanza el worker de chequeo. Si el usuario configuró servidor
        propio, usa `ServerUpdateSource`; si no, default a GitHub."""
        repo = SettingsRepository(self.conn)
        server_url = repo.get(SETTING_SERVER_URL)
        source: UpdateSource | None = None
        if server_url:
            api_key = repo.get(SETTING_SERVER_API_KEY) or ""
            source = ServerUpdateSource(server_url, api_key)

        skipped = repo.get(SETTING_SKIPPED_VERSION)

        self._update_worker = _UpdateCheckWorker(source=source, parent=self)
        self._update_worker.update_found.connect(lambda info: self._on_update_found(info, skipped))
        self._update_worker.start()

    def _on_update_found(self, info: object, skipped: str | None) -> None:
        # `info` viene como `object` por la firma del Signal — re-tipear acá.
        if not isinstance(info, UpdateInfo):
            return
        if skipped and skipped == info.latest_version:
            logger.debug("Versión %s ignorada por el usuario", info.latest_version)
            return
        self._show_update_banner(info)

    def _show_update_banner(self, info: UpdateInfo) -> None:
        """Banner azul no intrusivo arriba del central widget."""
        banner = QFrame(self)
        banner.setObjectName("updateBanner")
        banner.setStyleSheet(
            "#updateBanner { background-color: #2E86AB; border-radius: 4px; }"
            "#updateBanner QLabel { color: white; font-weight: bold; }"
            "#updateBanner QPushButton { color: white; border: 1px solid white;"
            "  border-radius: 3px; padding: 2px 8px; background: transparent; }"
            "#updateBanner QPushButton:hover { background-color: #1a6a8a; }"
        )

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(8, 4, 8, 4)

        label = QLabel(
            self.tr("Nueva versión disponible: v{latest} (instalada: v{current})").format(
                latest=info.latest_version, current=info.current_version
            )
        )
        layout.addWidget(label, stretch=1)

        btn_download = QPushButton(self.tr("Descargar"))
        btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_download.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(info.download_url)))
        layout.addWidget(btn_download)

        btn_notes = QPushButton(self.tr("Ver cambios"))
        btn_notes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_notes.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(info.release_url)))
        layout.addWidget(btn_notes)

        btn_skip = QPushButton(self.tr("Ignorar esta versión"))
        btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_skip.clicked.connect(lambda: self._skip_version(info.latest_version, banner))
        layout.addWidget(btn_skip)

        btn_close = QPushButton("X")
        btn_close.setFixedWidth(28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(banner.deleteLater)
        layout.addWidget(btn_close)

        # Insertar arriba del layout del widget central. Si no hay layout
        # (placeholder QLabel), no podemos insertar un banner — silencioso.
        central = self.centralWidget()
        if central is not None:
            central_layout = central.layout()
            if central_layout is not None:
                # `insertWidget` solo está en QBoxLayout; QTabWidget viene
                # con uno por default. Defensa: solo insertamos si está disponible.
                insert_widget = getattr(central_layout, "insertWidget", None)
                if insert_widget is not None:
                    insert_widget(0, banner)
                    return
        # Fallback: si no se pudo insertar arriba del central widget,
        # mostrar el banner como popup flotante junto a la ventana.
        banner.setParent(None)
        banner.setWindowFlags(Qt.WindowType.Tool)
        banner.show()

    def _skip_version(self, version: str, banner: QWidget) -> None:
        """Persiste la versión ignorada y cierra el banner."""
        SettingsRepository(self.conn).set(SETTING_SKIPPED_VERSION, version)
        self.conn.commit()
        banner.deleteLater()


def main() -> int:
    """Entry point. Inicializa logging, abre la ventana principal."""
    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info("Client app v%s — bootstrap OK (db=%s)", __version__, db_path)

    app = QApplication(sys.argv)
    apply_app_style(app)
    window = ClientMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
