"""Diálogo de configuración del cliente: elección de colección + licencia."""

import sqlite3

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import LicenseService, SettingsService
from collections_app.shared_ui.theme import Spacing, StatusColor


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
        self._selected_id: int | None = None

        self.setWindowTitle(self.tr("Configuración"))
        self._build_ui()
        self._load_collections()
        self._update_license_section()

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

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        root.addWidget(self._buttons)

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
