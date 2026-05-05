"""Diálogo de configuración: selección de la colección activa."""

import sqlite3

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import SettingsService
from collections_app.shared_ui.theme import Spacing


class SettingsDialog(QDialog):
    """Permite al usuario elegir la colección activa.

    Al aceptar persiste el setting con `SettingsService.set_active_collection`
    y commitea. Cancelar no toca el estado.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._settings = SettingsService(conn)
        self._collections_repo = CollectionsRepository(conn)
        self._selected_id: int | None = None

        self.setWindowTitle(self.tr("Configuración"))
        self._build_ui()
        self._load_collections()

    @property
    def selected_collection_id(self) -> int | None:
        """ID de la colección seleccionada al aceptar, o None si canceló."""
        return self._selected_id

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)

        form = QFormLayout()
        self._combo = QComboBox()
        self._combo.setMinimumWidth(280)
        form.addRow(self.tr("Colección activa") + ":", self._combo)
        root.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        root.addWidget(self._buttons)

    def _load_collections(self) -> None:
        self._combo.clear()
        self._combo.addItem(self.tr("(ninguna)"), userData=None)
        for col in self._collections_repo.list_all():
            self._combo.addItem(col.collection_name, userData=col.collection_id)

        active_id = self._settings.get_active_collection_id()
        if active_id is not None:
            idx = self._combo.findData(active_id)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)

    def _on_accept(self) -> None:
        chosen = self._combo.currentData()
        if chosen is None:
            self._settings.clear_active_collection()
        else:
            self._settings.set_active_collection(int(chosen))
        self._conn.commit()
        self._selected_id = chosen
        self.accept()
