"""Vista master/detail para CodeHeaders + CodeLines.

Vista modal accesible desde "Administración → Códigos...".

Layout:

    ┌────────────────────────┬─────────────────────────────────┐
    │ Headers                │ Codes del header seleccionado   │
    │ [Nuevo] [Edit] [Del]   │ [Add] [Edit] [Del] [↑] [↓]      │
    └────────────────────────┴─────────────────────────────────┘

Master (izq): `QListWidget` de headers.
Detail (der): `QTableWidget` con codes_lines del header seleccionado.

Reorder: botones ↑/↓ que reasignan `code_order` via
`code_lines_service.reorder(...)`.

Eliminar header bloquea con error si hay colecciones asociadas
(listándolas).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.services.exceptions import CodeHeadersError, CodeLinesError

_LINE_HEADERS = ["Código", "Nombre", "Orden"]


class CodeHeaderEditDialog(QDialog):
    """Crear o editar un CodeHeader."""

    def __init__(
        self: CodeHeaderEditDialog,
        ctx: AppContext,
        header_to_edit: CodeHeader | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._header_to_edit = header_to_edit
        self.setWindowTitle(self.tr("Editar header") if header_to_edit else self.tr("Nuevo header"))
        self._build_ui()
        self._update_ok_enabled()

    def _build_ui(self: CodeHeaderEditDialog) -> None:
        outer = QVBoxLayout(self)
        form = QFormLayout()
        self._name_edit = QLineEdit()
        if self._header_to_edit is not None:
            self._name_edit.setText(self._header_to_edit.code_header_name)
        self._name_edit.textChanged.connect(self._update_ok_enabled)
        form.addRow(self.tr("Nombre"), self._name_edit)

        self._max_len_spin = QSpinBox()
        self._max_len_spin.setRange(1, 32)
        self._max_len_spin.setValue(
            self._header_to_edit.code_max_length if self._header_to_edit else 5
        )
        form.addRow(self.tr("Longitud máxima de code_id"), self._max_len_spin)

        outer.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        outer.addWidget(self._buttons)

    def _update_ok_enabled(self: CodeHeaderEditDialog) -> None:
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setEnabled(bool(self._name_edit.text().strip()))

    def _on_accept(self: CodeHeaderEditDialog) -> None:
        try:
            if self._header_to_edit is None:
                self._ctx.code_headers.create(
                    CodeHeader(
                        code_header_id=None,
                        code_header_name=self._name_edit.text().strip(),
                        code_max_length=self._max_len_spin.value(),
                    )
                )
            else:
                self._ctx.code_headers.update(
                    CodeHeader(
                        code_header_id=self._header_to_edit.code_header_id,
                        code_header_name=self._name_edit.text().strip(),
                        code_max_length=self._max_len_spin.value(),
                    )
                )
            self._ctx.conn.commit()
        except CodeHeadersError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self.accept()


class CodeLineEditDialog(QDialog):
    """Crear o editar una CodeLine."""

    def __init__(
        self: CodeLineEditDialog,
        ctx: AppContext,
        header: CodeHeader,
        line_to_edit: CodeLine | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._header = header
        self._line_to_edit = line_to_edit
        self.setWindowTitle(self.tr("Editar code") if line_to_edit else self.tr("Nuevo code"))
        self._build_ui()
        self._update_ok_enabled()

    def _build_ui(self: CodeLineEditDialog) -> None:
        outer = QVBoxLayout(self)
        form = QFormLayout()

        self._code_id_edit = QLineEdit()
        self._code_id_edit.setMaxLength(self._header.code_max_length)
        if self._line_to_edit is not None:
            self._code_id_edit.setText(self._line_to_edit.code_id)
            self._code_id_edit.setReadOnly(True)
        self._code_id_edit.textChanged.connect(self._update_ok_enabled)
        form.addRow(self.tr("code_id"), self._code_id_edit)

        self._code_name_edit = QLineEdit()
        if self._line_to_edit is not None:
            self._code_name_edit.setText(self._line_to_edit.code_name)
        self._code_name_edit.textChanged.connect(self._update_ok_enabled)
        form.addRow(self.tr("Nombre"), self._code_name_edit)

        self._order_spin = QSpinBox()
        self._order_spin.setRange(0, 999_999)
        self._order_spin.setValue(self._line_to_edit.code_order if self._line_to_edit else 0)
        form.addRow(self.tr("Orden"), self._order_spin)

        outer.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        outer.addWidget(self._buttons)

    def _update_ok_enabled(self: CodeLineEditDialog) -> None:
        ok = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok.setEnabled(
            bool(self._code_id_edit.text().strip()) and bool(self._code_name_edit.text().strip())
        )

    def _on_accept(self: CodeLineEditDialog) -> None:
        assert self._header.code_header_id is not None
        line = CodeLine(
            code_line_id=self._line_to_edit.code_line_id if self._line_to_edit else None,
            code_header_id=self._header.code_header_id,
            code_id=self._code_id_edit.text().strip(),
            code_name=self._code_name_edit.text().strip(),
            code_order=self._order_spin.value(),
        )
        try:
            self._ctx.code_lines.upsert(line)
            self._ctx.conn.commit()
        except CodeLinesError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self.accept()


class CodesMasterDetailView(QDialog):
    """Vista modal master/detail de CodeHeaders y CodeLines."""

    def __init__(
        self: CodesMasterDetailView,
        ctx: AppContext,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self.setWindowTitle(self.tr("Administración de códigos"))
        self.resize(900, 600)
        self._build_ui()
        self._refresh_master()

    def _build_ui(self: CodesMasterDetailView) -> None:
        outer = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Master: izquierda
        master_widget = QWidget()
        master_layout = QVBoxLayout(master_widget)
        master_layout.addWidget(self._wrap_label(self.tr("Headers")))
        self._master_list = QListWidget()
        self._master_list.itemSelectionChanged.connect(self._on_master_changed)
        master_layout.addWidget(self._master_list, 1)

        master_btns = QHBoxLayout()
        self._new_header_btn = QPushButton(self.tr("Nuevo"))
        self._new_header_btn.clicked.connect(self._on_new_header)
        self._edit_header_btn = QPushButton(self.tr("Editar"))
        self._edit_header_btn.clicked.connect(self._on_edit_header)
        self._delete_header_btn = QPushButton(self.tr("Eliminar"))
        self._delete_header_btn.clicked.connect(self._on_delete_header)
        master_btns.addWidget(self._new_header_btn)
        master_btns.addWidget(self._edit_header_btn)
        master_btns.addWidget(self._delete_header_btn)
        master_layout.addLayout(master_btns)

        splitter.addWidget(master_widget)

        # Detail: derecha
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.addWidget(self._wrap_label(self.tr("Códigos del header")))
        self._detail_table = QTableWidget(0, len(_LINE_HEADERS))
        self._detail_table.setHorizontalHeaderLabels(_LINE_HEADERS)
        self._detail_table.verticalHeader().setVisible(False)
        self._detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._detail_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._detail_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        header = self._detail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        detail_layout.addWidget(self._detail_table, 1)

        detail_btns = QHBoxLayout()
        self._add_line_btn = QPushButton(self.tr("Agregar"))
        self._add_line_btn.clicked.connect(self._on_add_line)
        self._edit_line_btn = QPushButton(self.tr("Editar"))
        self._edit_line_btn.clicked.connect(self._on_edit_line)
        self._delete_line_btn = QPushButton(self.tr("Eliminar"))
        self._delete_line_btn.clicked.connect(self._on_delete_line)
        self._up_btn = QPushButton(self.tr("↑ Subir"))
        self._up_btn.clicked.connect(lambda: self._move_selected(-1))
        self._down_btn = QPushButton(self.tr("↓ Bajar"))
        self._down_btn.clicked.connect(lambda: self._move_selected(+1))
        detail_btns.addWidget(self._add_line_btn)
        detail_btns.addWidget(self._edit_line_btn)
        detail_btns.addWidget(self._delete_line_btn)
        detail_btns.addStretch()
        detail_btns.addWidget(self._up_btn)
        detail_btns.addWidget(self._down_btn)
        detail_layout.addLayout(detail_btns)

        splitter.addWidget(detail_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 620])
        outer.addWidget(splitter, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()
        close_btn = QPushButton(self.tr("Cerrar"))
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)
        outer.addLayout(bottom)

    def _wrap_label(self: CodesMasterDetailView, text: str) -> QWidget:
        from PySide6.QtWidgets import QLabel

        lbl = QLabel(text)
        font = lbl.font()
        font.setBold(True)
        lbl.setFont(font)
        return lbl

    # ------------------------------------------------------------------
    # Master
    # ------------------------------------------------------------------

    def _refresh_master(self: CodesMasterDetailView) -> None:
        previous = self._selected_header()
        self._master_list.clear()
        for header in self._ctx.code_headers.list_all():
            item = QListWidgetItem(header.code_header_name)
            item.setData(Qt.ItemDataRole.UserRole, header)
            self._master_list.addItem(item)
        # Restablecer selección o seleccionar la primera.
        if previous is not None:
            for row in range(self._master_list.count()):
                data = self._master_list.item(row).data(Qt.ItemDataRole.UserRole)
                if data.code_header_id == previous.code_header_id:
                    self._master_list.setCurrentRow(row)
                    return
        if self._master_list.count() > 0:
            self._master_list.setCurrentRow(0)
        else:
            self._refresh_detail()

    def _selected_header(self: CodesMasterDetailView) -> CodeHeader | None:
        item = self._master_list.currentItem()
        if item is None:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data if isinstance(data, CodeHeader) else None

    def _on_master_changed(self: CodesMasterDetailView) -> None:
        self._refresh_detail()

    def _on_new_header(self: CodesMasterDetailView) -> None:
        dialog = CodeHeaderEditDialog(ctx=self._ctx, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_master()

    def _on_edit_header(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        if header is None:
            QMessageBox.information(
                self,
                self.tr("Editar header"),
                self.tr("Seleccioná un header primero."),
            )
            return
        dialog = CodeHeaderEditDialog(ctx=self._ctx, header_to_edit=header, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_master()

    def _on_delete_header(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        if header is None or header.code_header_id is None:
            return
        # Buscar collections que usen este header.
        users = [
            c for c in self._ctx.collections.list_all() if c.code_header_id == header.code_header_id
        ]
        if users:
            names = "\n".join(f"  - «{c.collection_name}»" for c in users)
            QMessageBox.critical(
                self,
                self.tr("No se puede borrar"),
                self.tr(
                    "No se puede borrar: las siguientes colecciones usan "
                    "este header. Eliminalas primero:\n\n{names}"
                ).format(names=names),
            )
            return
        confirm = QMessageBox.question(
            self,
            self.tr("Eliminar header"),
            self.tr("Eliminar el header «{name}» y todos sus codes asociados?").format(
                name=header.code_header_name
            ),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._ctx.code_headers.delete(header.code_header_id)
        self._ctx.conn.commit()
        self._refresh_master()

    # ------------------------------------------------------------------
    # Detail
    # ------------------------------------------------------------------

    def _refresh_detail(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        self._detail_table.setRowCount(0)
        if header is None or header.code_header_id is None:
            return
        for row, line in enumerate(self._ctx.code_lines.list_by_header(header.code_header_id)):
            self._detail_table.insertRow(row)
            self._detail_table.setItem(row, 0, QTableWidgetItem(line.code_id))
            name_item = QTableWidgetItem(line.code_name)
            name_item.setData(Qt.ItemDataRole.UserRole, line)
            self._detail_table.setItem(row, 1, name_item)
            order_item = QTableWidgetItem(str(line.code_order))
            order_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._detail_table.setItem(row, 2, order_item)

    def _selected_line(self: CodesMasterDetailView) -> CodeLine | None:
        row = self._detail_table.currentRow()
        if row < 0:
            return None
        item = self._detail_table.item(row, 1)
        if item is None:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data if isinstance(data, CodeLine) else None

    def _on_add_line(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        if header is None:
            return
        dialog = CodeLineEditDialog(ctx=self._ctx, header=header, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_detail()

    def _on_edit_line(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        line = self._selected_line()
        if header is None or line is None:
            QMessageBox.information(
                self,
                self.tr("Editar code"),
                self.tr("Seleccioná un code primero."),
            )
            return
        dialog = CodeLineEditDialog(ctx=self._ctx, header=header, line_to_edit=line, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_detail()

    def _on_delete_line(self: CodesMasterDetailView) -> None:
        header = self._selected_header()
        line = self._selected_line()
        if header is None or line is None or header.code_header_id is None:
            return
        confirm = QMessageBox.question(
            self,
            self.tr("Eliminar code"),
            self.tr("Eliminar el code «{code}» («{name}»)?").format(
                code=line.code_id, name=line.code_name
            ),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self._ctx.code_lines.delete(header.code_header_id, line.code_id)
            self._ctx.conn.commit()
        except Exception as exc:
            self._ctx.conn.rollback()
            QMessageBox.critical(
                self,
                self.tr("Error al eliminar"),
                self.tr("No se pudo eliminar el code.\nDetalle: {msg}").format(msg=exc),
            )
            return
        self._refresh_detail()

    def _move_selected(self: CodesMasterDetailView, direction: int) -> None:
        """direction = -1 (subir) o +1 (bajar). Reasigna code_order."""
        header = self._selected_header()
        if header is None or header.code_header_id is None:
            return
        row = self._detail_table.currentRow()
        if row < 0:
            return
        target = row + direction
        if target < 0 or target >= self._detail_table.rowCount():
            return
        # Construir la lista de code_ids reordenada.
        code_ids: list[str] = []
        for r in range(self._detail_table.rowCount()):
            item = self._detail_table.item(r, 0)
            if item is not None:
                code_ids.append(item.text())
        code_ids[row], code_ids[target] = code_ids[target], code_ids[row]
        self._ctx.code_lines.reorder(header.code_header_id, code_ids)
        self._ctx.conn.commit()
        self._refresh_detail()
        self._detail_table.setCurrentCell(target, 0)
