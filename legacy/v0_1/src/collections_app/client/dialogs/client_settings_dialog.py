"""Diálogo de configuración del cliente: elección de colección + licencia."""

import logging
import sqlite3

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.__version__ import __app_name__, __version__
from collections_app.core.repositories import CollectionsRepository, SettingsRepository
from collections_app.core.services import LicenseService, SettingsService
from collections_app.core.services.update_service import (
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)
from collections_app.core.utils.datetime_helpers import (
    format_for_display,
    parse_db_datetime,
    utc_now,
)
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)

SETTING_LAST_UPDATE_CHECK = "last_update_check"
SETTING_SERVER_URL = "server_url"
SETTING_SERVER_API_KEY = "server_api_key"


class _ManualUpdateCheckWorker(QThread):
    """Worker para el botón "Buscar actualizaciones" del diálogo.

    Idéntico en espíritu al worker de main.py pero emite SIEMPRE un
    resultado (con `is_newer=False` cuando estamos al día) o `None`
    cuando no hay conexión — la UI necesita los tres estados (nueva /
    al día / sin red) para pintar el QLabel correctamente.
    """

    finished_check = Signal(object)  # UpdateInfo | None

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
            self.finished_check.emit(service.check_for_updates())
        except Exception:
            logger.exception("ManualUpdateCheckWorker: fallo inesperado")
            self.finished_check.emit(None)


class ClientSettingsDialog(QDialog):
    """Permite al usuario elegir la colección activa.

    Si la colección elegida es premium y aún no fue desbloqueada, muestra
    un campo de licencia con botón "Validar". El botón Aceptar queda
    deshabilitado hasta que la licencia se valide (o si la colección es free).

    Layout:
        Colección: [combo ▼]
        ── solo si premium y no unlocked ──
        Esta colección requiere licencia.
        Clave: [____] [Validar]
        ── separator ──
        Acerca de
          CollectionsApp v1.0.0
          [Buscar actualizaciones]
          (estado del último chequeo)
        [Cancelar] [Aceptar]
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._settings = SettingsService(conn)
        self._licenses = LicenseService(conn)
        self._collections_repo = CollectionsRepository(conn)
        self._settings_repo = SettingsRepository(conn)
        self._selected_id: int | None = None
        self._update_worker: _ManualUpdateCheckWorker | None = None
        self._last_update_info: UpdateInfo | None = None

        self.setWindowTitle(self.tr("Configuración"))
        self._build_ui()
        self._load_collections()
        self._update_license_section()
        self._refresh_last_check_label()

    @property
    def selected_collection_id(self) -> int | None:
        """ID de la colección elegida al aceptar, o None si canceló."""
        return self._selected_id

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)

        form = QFormLayout()
        self._combo = QComboBox()
        self._combo.setMinimumWidth(280)
        self._combo.currentIndexChanged.connect(self._update_license_section)
        form.addRow(self.tr("Colección") + ":", self._combo)
        root.addLayout(form)

        # Sección de licencia (visible solo cuando hace falta)
        self._license_container = QWidget()
        license_layout = QVBoxLayout(self._license_container)
        license_layout.setContentsMargins(0, 0, 0, 0)
        license_layout.setSpacing(Spacing.SM)

        self._license_msg = QLabel(self.tr("Esta colección requiere licencia."))
        license_layout.addWidget(self._license_msg)

        license_row = QHBoxLayout()
        license_row.setContentsMargins(0, 0, 0, 0)
        license_row.addWidget(QLabel(self.tr("Clave") + ":"))
        self._license_input = QLineEdit()
        self._license_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._license_input.returnPressed.connect(self._on_validate_license)
        license_row.addWidget(self._license_input, stretch=1)
        self._validate_button = QPushButton(self.tr("Validar"))
        self._validate_button.clicked.connect(self._on_validate_license)
        license_row.addWidget(self._validate_button)
        license_layout.addLayout(license_row)

        self._license_status = QLabel("")
        license_layout.addWidget(self._license_status)
        root.addWidget(self._license_container)

        # Sección "Acerca de"
        root.addWidget(self._build_about_section())

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        root.addWidget(self._buttons)

    def _build_about_section(self) -> QWidget:
        """Construye el bloque "Acerca de" con versión y chequeo manual."""
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        title = QLabel("<b>" + self.tr("Acerca de") + "</b>")
        layout.addWidget(title)

        version_label = QLabel(f"{__app_name__} v{__version__}")
        layout.addWidget(version_label)

        # Botón + (eventual) "Descargar" en una fila.
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        self._check_button = QPushButton(self.tr("Buscar actualizaciones"))
        self._check_button.clicked.connect(self._on_check_for_updates)
        button_row.addWidget(self._check_button)

        self._download_button = QPushButton(self.tr("Descargar"))
        self._download_button.setVisible(False)
        self._download_button.clicked.connect(self._on_download_clicked)
        button_row.addWidget(self._download_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        # Estado del último chequeo (vacío hasta que se haga uno).
        self._update_status = QLabel("")
        self._update_status.setWordWrap(True)
        layout.addWidget(self._update_status)

        # Timestamp del último chequeo (siempre visible si hay valor).
        self._last_check_label = QLabel("")
        self._last_check_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(self._last_check_label)

        return container

    def _load_collections(self) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in self._collections_repo.list_all():
            self._combo.addItem(col.collection_name, userData=col.collection_id)

        active_id = self._settings.get_active_collection_id()
        if active_id is not None:
            idx = self._combo.findData(active_id)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Estado y validación de licencia
    # ------------------------------------------------------------------

    def _update_license_section(self) -> None:
        """Decide si mostrar el campo de licencia y habilitar 'Aceptar'."""
        collection_id = self._combo.currentData()
        if collection_id is None:
            self._license_container.setVisible(False)
            self._set_ok_enabled(False)
            return

        # Si ya está unlocked (free o premium-unlocked) → ocultar y habilitar Aceptar
        if self._licenses.is_unlocked(int(collection_id)):
            self._license_container.setVisible(False)
            self._set_ok_enabled(True)
            return

        # Necesita licencia y no está unlocked
        self._license_container.setVisible(True)
        self._license_input.clear()
        self._license_status.setText("")
        self._license_status.setStyleSheet("")
        self._set_ok_enabled(False)

    def _on_validate_license(self) -> None:
        collection_id = self._combo.currentData()
        if collection_id is None:
            return
        key = self._license_input.text().strip()
        if not key:
            self._show_license_status(self.tr("Ingresá una clave."), StatusColor.WARNING)
            return

        if self._licenses.unlock(int(collection_id), key):
            self._show_license_status(self.tr("Clave válida."), StatusColor.SUCCESS)
            self._license_container.setVisible(False)
            self._set_ok_enabled(True)
        else:
            self._show_license_status(self.tr("Clave inválida."), StatusColor.ERROR)
            self._set_ok_enabled(False)

    def _show_license_status(self, text: str, color: str) -> None:
        self._license_status.setText(text)
        self._license_status.setStyleSheet(f"color: {color};")

    def _set_ok_enabled(self, enabled: bool) -> None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    # ------------------------------------------------------------------
    # Update checker (botón "Buscar actualizaciones")
    # ------------------------------------------------------------------

    def _on_check_for_updates(self) -> None:
        """Lanza el chequeo manual en background — UI no se bloquea."""
        # Si ya hay un check corriendo, no relanzamos.
        if self._update_worker is not None and self._update_worker.isRunning():
            return
        self._check_button.setEnabled(False)
        self._download_button.setVisible(False)
        self._update_status.setText(self.tr("Verificando…"))
        self._update_status.setStyleSheet("")
        self._last_update_info = None

        # Si el usuario configuró servidor propio (futuro), usarlo.
        server_url = self._settings_repo.get(SETTING_SERVER_URL)
        source: UpdateSource | None = None
        if server_url:
            api_key = self._settings_repo.get(SETTING_SERVER_API_KEY) or ""
            source = ServerUpdateSource(server_url, api_key)

        self._update_worker = _ManualUpdateCheckWorker(source=source, parent=self)
        self._update_worker.finished_check.connect(self._on_update_check_finished)
        self._update_worker.start()

    def _on_update_check_finished(self, info: object) -> None:
        self._check_button.setEnabled(True)
        if info is None:
            # No hay conexión / fuente caída.
            self._update_status.setText(self.tr("No se pudo verificar (sin conexión)"))
            self._update_status.setStyleSheet(f"color: {StatusColor.WARNING};")
            return
        if not isinstance(info, UpdateInfo):
            return

        # Persistir timestamp del chequeo.
        self._settings_repo.set(SETTING_LAST_UPDATE_CHECK, utc_now().isoformat())
        self._conn.commit()
        self._refresh_last_check_label()

        if info.is_newer:
            self._last_update_info = info
            self._update_status.setText(
                self.tr("Hay una versión nueva: v{v}").format(v=info.latest_version)
            )
            self._update_status.setStyleSheet(f"color: {StatusColor.SUCCESS};")
            self._download_button.setVisible(True)
        else:
            self._update_status.setText(
                self.tr("Estás en la última versión (v{v})").format(v=info.current_version)
            )
            self._update_status.setStyleSheet(f"color: {StatusColor.SUCCESS};")

    def _on_download_clicked(self) -> None:
        if self._last_update_info is None:
            return
        QDesktopServices.openUrl(QUrl(self._last_update_info.download_url))

    def _refresh_last_check_label(self) -> None:
        """Pinta el timestamp del último chequeo (en hora local) si existe."""
        raw = self._settings_repo.get(SETTING_LAST_UPDATE_CHECK)
        if not raw:
            self._last_check_label.setText("")
            return
        try:
            dt = parse_db_datetime(raw)
        except ValueError:
            self._last_check_label.setText("")
            return
        self._last_check_label.setText(
            self.tr("Última verificación: {ts}").format(ts=format_for_display(dt))
        )

    # ------------------------------------------------------------------
    # Aceptar
    # ------------------------------------------------------------------

    def _on_accept(self) -> None:
        collection_id = self._combo.currentData()
        if collection_id is None:
            return
        cid = int(collection_id)
        if not self._licenses.is_unlocked(cid):
            return  # Defensa: no debería pasar (Aceptar disabled), pero por las dudas
        self._settings.set_active_collection(cid)
        self._conn.commit()
        self._selected_id = cid
        self.accept()
