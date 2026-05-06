"""ABM de colecciones.

Vista modal accesible desde "Administración → Colecciones...".

Operaciones:
- Listar colecciones.
- Agregar → delega al CsvImportDialog existente (no crea flow paralelo).
- Editar via `CollectionEditDialog` con la matriz del plan
  (siempre/cuidado/no editable).
- Eliminar con confirmación fuerte; cascade SQL borra cards e inventory.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.services.exceptions import CollectionsError
from collections_app.views.admin.csv_import_dialog import CsvImportDialog

_DELETE_CONFIRM_TEXT = (
    "Esto borrará la colección «{name}» y TODAS sus cards e inventario "
    "asociados. Esta acción no se puede deshacer."
)
_RISK_REQUIRES_CODE_TEXT = (
    "Cambiar 'requires_code' con cards cargadas puede dejar la UI inconsistente. " "¿Confirmás?"
)
_RISK_HEADER_TEXT = (
    "Cambiar el header con cards cargadas puede dejar las cards "
    "huérfanas (sus code_id ya no resolverán). ¿Confirmás?"
)


class CollectionEditDialog(QDialog):
    """Dialog modal para editar una colección existente.

    Matriz del plan:
    - Siempre editable: name, code_field_name, card_count, album_*.
    - Editable con confirmación si hay cards: requires_code, code_header_id.
    - No editable en MVP: is_premium, license_key_required (read-only label).
    """

    def __init__(
        self: CollectionEditDialog,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._original = collection
        self.setWindowTitle(self.tr("Editar colección"))
        self._has_cards = self._ctx.cards.count(collection.collection_id or 0) > 0
        self._build_ui()
        self._update_ok_enabled()

    def _build_ui(self: CollectionEditDialog) -> None:
        outer = QVBoxLayout(self)
        form = QFormLayout()

        self._name_edit = QLineEdit(self._original.collection_name)
        self._name_edit.textChanged.connect(self._update_ok_enabled)
        form.addRow(self.tr("Nombre"), self._name_edit)

        self._code_field_edit = QLineEdit(self._original.code_field_name or "")
        form.addRow(self.tr("Etiqueta de código (UI)"), self._code_field_edit)

        self._card_count_spin = QSpinBox()
        self._card_count_spin.setRange(0, 999_999)
        self._card_count_spin.setValue(self._original.card_count)
        form.addRow(self.tr("card_count declarado"), self._card_count_spin)

        self._requires_code = QCheckBox()
        self._requires_code.setChecked(self._original.requires_code)
        form.addRow(self.tr("Requires code"), self._requires_code)

        self._header_combo = QComboBox()
        for header in self._ctx.code_headers.list_all():
            self._header_combo.addItem(header.code_header_name, header)
            if header.code_header_id == self._original.code_header_id:
                self._header_combo.setCurrentIndex(self._header_combo.count() - 1)
        form.addRow(self.tr("CodeHeader"), self._header_combo)

        self._album_cols = QSpinBox()
        self._album_cols.setRange(1, 32)
        self._album_cols.setValue(self._original.album_columns)
        form.addRow(self.tr("Álbum: columnas"), self._album_cols)

        self._album_rows = QSpinBox()
        self._album_rows.setRange(1, 32)
        self._album_rows.setValue(self._original.album_rows)
        form.addRow(self.tr("Álbum: filas"), self._album_rows)

        self._album_orient_combo = QComboBox()
        self._album_orient_combo.addItems(["portrait", "landscape"])
        self._album_orient_combo.setCurrentText(self._original.album_orientation)
        form.addRow(self.tr("Álbum: orientación"), self._album_orient_combo)

        # Read-only en MVP.
        premium_label = QLabel(
            self.tr("Sí (con licencia)") if self._original.is_premium else self.tr("No")
        )
        premium_label.setEnabled(False)
        form.addRow(self.tr("Premium"), premium_label)

        outer.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        outer.addWidget(self._buttons)

    def _update_ok_enabled(self: CollectionEditDialog) -> None:
        ok_btn = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setEnabled(bool(self._name_edit.text().strip()))

    def _on_accept(self: CollectionEditDialog) -> None:
        new_requires_code = self._requires_code.isChecked()
        new_header_id = self._header_combo.currentData().code_header_id
        if self._has_cards and new_requires_code != self._original.requires_code:
            confirm = QMessageBox.question(
                self,
                self.tr("Cambio de configuración"),
                self.tr(_RISK_REQUIRES_CODE_TEXT),
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
        if self._has_cards and new_header_id != self._original.code_header_id:
            confirm = QMessageBox.question(
                self,
                self.tr("Cambio de CodeHeader"),
                self.tr(_RISK_HEADER_TEXT),
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        updated = Collection(
            collection_id=self._original.collection_id,
            collection_name=self._name_edit.text().strip(),
            card_count=self._card_count_spin.value(),
            requires_code=new_requires_code,
            code_field_name=self._code_field_edit.text().strip() or None,
            code_header_id=new_header_id,
            is_premium=self._original.is_premium,
            license_key_required=self._original.license_key_required,
            album_columns=self._album_cols.value(),
            album_rows=self._album_rows.value(),
            album_orientation=self._album_orient_combo.currentText(),
        )
        try:
            self._ctx.collections.update(updated)
            self._ctx.conn.commit()
        except CollectionsError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self.accept()


class CollectionsAbmView(QDialog):
    """ABM modal de colecciones."""

    def __init__(
        self: CollectionsAbmView,
        ctx: AppContext,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self.setWindowTitle(self.tr("Administración de colecciones"))
        self.resize(700, 500)
        self._build_ui()
        self._refresh()

    def _build_ui(self: CollectionsAbmView) -> None:
        outer = QVBoxLayout(self)
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        outer.addWidget(self._list, 1)

        btns = QHBoxLayout()
        self._add_btn = QPushButton(self.tr("Nueva colección..."))
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn = QPushButton(self.tr("Editar"))
        self._edit_btn.clicked.connect(self._on_edit)
        self._delete_btn = QPushButton(self.tr("Eliminar"))
        self._delete_btn.clicked.connect(self._on_delete)
        self._close_btn = QPushButton(self.tr("Cerrar"))
        self._close_btn.clicked.connect(self.accept)
        btns.addWidget(self._add_btn)
        btns.addWidget(self._edit_btn)
        btns.addWidget(self._delete_btn)
        btns.addStretch()
        btns.addWidget(self._close_btn)
        outer.addLayout(btns)

    def _refresh(self: CollectionsAbmView) -> None:
        self._list.clear()
        for coll in self._ctx.collections.list_all():
            item = QListWidgetItem(coll.collection_name)
            item.setData(Qt.ItemDataRole.UserRole, coll)
            self._list.addItem(item)

    def _selected(self: CollectionsAbmView) -> Collection | None:
        item = self._list.currentItem()
        if item is None:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data if isinstance(data, Collection) else None

    def _on_add(self: CollectionsAbmView) -> None:
        """Delega al CsvImportDialog existente (mismo flow que el menú Archivo)."""
        dialog = CsvImportDialog(ctx=self._ctx, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh()

    def _on_edit(self: CollectionsAbmView) -> None:
        coll = self._selected()
        if coll is None:
            QMessageBox.information(
                self,
                self.tr("Editar colección"),
                self.tr("Seleccioná una colección primero."),
            )
            return
        dialog = CollectionEditDialog(ctx=self._ctx, collection=coll, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh()

    def _on_delete(self: CollectionsAbmView) -> None:
        coll = self._selected()
        if coll is None or coll.collection_id is None:
            QMessageBox.information(
                self,
                self.tr("Eliminar colección"),
                self.tr("Seleccioná una colección primero."),
            )
            return
        confirm = QMessageBox.question(
            self,
            self.tr("Eliminar colección"),
            self.tr(_DELETE_CONFIRM_TEXT).format(name=coll.collection_name),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self._ctx.collections.delete(coll.collection_id)
            self._ctx.conn.commit()
        except Exception as exc:  # FK por transactions huérfanas
            self._ctx.conn.rollback()
            QMessageBox.critical(
                self,
                self.tr("Error al eliminar"),
                self.tr(
                    "No se pudo eliminar la colección.\n\n"
                    "Es posible que tenga transacciones registradas.\n\n"
                    "Detalle: {msg}"
                ).format(msg=exc),
            )
            return
        self._refresh()
