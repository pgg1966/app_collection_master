"""Diálogo "Importar inventario desde archivo" (Prompt 4c).

Reemplaza el placeholder del menú "Archivo → Importar inventario..."
de la `MainWindow`. Pre-requisito: hay una colección activa en
`MainWindow` (la verificación vive ahí, no acá — el dialog la recibe
por constructor).

UX:
- File picker para .xlsx o .csv.
- Toggle modo replace / add (default replace).
- Botón "Descargar modelo" para generar el .xlsx vacío con headers
  + pestaña "Códigos" como referencia visual.
- Botón "Importar" deshabilitado hasta que haya archivo seleccionado.
- Tras importar: tabla con errores y warnings. El dialog NO se
  autocierra — el usuario revisa el reporte y cierra manualmente.
- Signal `import_completed(InventoryImportReport)` que el caller
  (MainWindow) usa para refrescar el detail view activo. El refresh
  corre mientras el dialog sigue abierto, lo que evita disparar el
  path post-modal del issue #002.

Cap de errores y warnings mostrados: 200 (mismo `_DISPLAY_CAP` que
el patrón Prompt 4a). Si hay más, un mensaje en pie alerta sobre
revisar el archivo de origen.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exceptions import ServiceError

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.aggregates.inventory_import_report import (
        InventoryImportReport,
    )
    from collections_app.core.models.collection import Collection

_DISPLAY_CAP = 200
_RESULT_HEADERS = ["Tipo", "Fila", "Card", "Mensaje"]
_DATE_SLUG_FORMAT = "%Y-%m-%d"


def _slugify_for_filename(name: str) -> str:
    """ASCII-alphanumeric + guion bajo, fallback "inventario"."""
    safe: list[str] = []
    for ch in name:
        if ch.isascii() and (ch.isalnum() or ch in ("-", "_")):
            safe.append(ch)
        else:
            safe.append("_")
    return "".join(safe).strip("_") or "inventario"


class InventoryImportDialog(QDialog):
    """Diálogo único para importar inventario desde Excel/CSV."""

    import_completed = Signal(object)  # InventoryImportReport

    def __init__(
        self: InventoryImportDialog,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self.setWindowTitle(self.tr("Importar inventario desde archivo"))
        self.resize(700, 600)
        self._build_ui()
        self._update_import_enabled()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: InventoryImportDialog) -> None:
        outer = QVBoxLayout(self)

        form = QFormLayout()

        coll_label = QLabel(self._collection.collection_name)
        coll_label.setEnabled(False)
        form.addRow(self.tr("Colección"), coll_label)

        self._file_edit, file_row = self._make_file_picker()
        form.addRow(self.tr("Archivo"), file_row)

        # Modo
        self._mode_replace = QRadioButton(self.tr("Reemplazar inventario actual"))
        self._mode_replace.setChecked(True)
        self._mode_add = QRadioButton(self.tr("Sumar al inventario actual"))
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self._mode_replace)
        self._mode_group.addButton(self._mode_add)
        mode_row = QVBoxLayout()
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.addWidget(self._mode_replace)
        mode_row.addWidget(self._mode_add)
        form.addRow(self.tr("Modo de aplicación"), mode_row)

        outer.addLayout(form)

        # Botón descargar modelo (alineado a izquierda, separado).
        template_row = QHBoxLayout()
        template_row.addWidget(QLabel(self.tr("¿No tenés un archivo?")))
        self._template_btn = QPushButton(self.tr("Descargar modelo"))
        self._template_btn.clicked.connect(self._on_download_template)
        template_row.addWidget(self._template_btn)
        template_row.addStretch()
        outer.addLayout(template_row)

        # Botones principales (cancelar / importar).
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._cancel_btn = QPushButton(self.tr("Cancelar"))
        self._cancel_btn.clicked.connect(self.reject)
        self._import_btn = QPushButton(self.tr("Importar"))
        self._import_btn.setDefault(True)
        self._import_btn.clicked.connect(self._on_import)
        btn_row.addWidget(self._cancel_btn)
        btn_row.addWidget(self._import_btn)
        outer.addLayout(btn_row)

        # Resultado
        self._result_label = QLabel("")
        self._result_label.setVisible(False)
        outer.addWidget(self._result_label)

        self._result_table = QTableWidget(0, len(_RESULT_HEADERS))
        self._result_table.setHorizontalHeaderLabels(_RESULT_HEADERS)
        self._result_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._result_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self._result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._result_table.setVisible(False)
        outer.addWidget(self._result_table, 1)

        self._truncation_label = QLabel("")
        self._truncation_label.setVisible(False)
        self._truncation_label.setStyleSheet("color: #854F0B;")
        outer.addWidget(self._truncation_label)

    def _make_file_picker(
        self: InventoryImportDialog,
    ) -> tuple[QLineEdit, QHBoxLayout]:
        edit = QLineEdit()
        edit.setReadOnly(True)
        edit.textChanged.connect(self._update_import_enabled)
        btn = QPushButton(self.tr("Examinar..."))

        def on_browse() -> None:
            path, _ = QFileDialog.getOpenFileName(
                self,
                self.tr("Seleccionar archivo de inventario"),
                "",
                self.tr("Excel/CSV (*.xlsx *.csv)"),
            )
            if path:
                edit.setText(path)

        btn.clicked.connect(on_browse)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(edit, 1)
        row.addWidget(btn)
        return edit, row

    # ------------------------------------------------------------------
    # Estado / acciones
    # ------------------------------------------------------------------

    def _update_import_enabled(self: InventoryImportDialog) -> None:
        self._import_btn.setEnabled(bool(self._file_edit.text().strip()))

    def _selected_mode(self: InventoryImportDialog) -> Literal["replace", "add"]:
        return "replace" if self._mode_replace.isChecked() else "add"

    def _default_template_filename(self: InventoryImportDialog) -> str:
        slug = _slugify_for_filename(self._collection.collection_name)
        date = datetime.now().strftime(_DATE_SLUG_FORMAT)
        return f"inventario_{slug}_{date}.xlsx"

    def _on_download_template(self: InventoryImportDialog) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar modelo"),
            self._default_template_filename(),
            self.tr("Excel (*.xlsx)"),
        )
        if not path_str:
            return
        path = Path(path_str)
        try:
            assert self._collection.collection_id is not None
            self._ctx.inventory_import.generate_template(
                collection_id=self._collection.collection_id, dest_path=path
            )
        except ServiceError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de I/O"),
                self.tr("No se pudo escribir el archivo: {msg}").format(msg=exc),
            )
            return
        QMessageBox.information(
            self,
            self.tr("Modelo descargado"),
            self.tr("Modelo guardado en:\n{path}").format(path=path),
        )

    def _on_import(self: InventoryImportDialog) -> None:
        file_path = Path(self._file_edit.text().strip())
        assert self._collection.collection_id is not None
        try:
            report = self._ctx.inventory_import.import_inventory(
                file_path=file_path,
                collection_id=self._collection.collection_id,
                mode=self._selected_mode(),
            )
        except ServiceError as exc:
            QMessageBox.critical(self, self.tr("Error de importación"), str(exc))
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de I/O"),
                self.tr("No se pudo abrir el archivo: {msg}").format(msg=exc),
            )
            return

        self._render_result(report)
        self.import_completed.emit(report)

    # ------------------------------------------------------------------
    # Render del resultado
    # ------------------------------------------------------------------

    def _render_result(self: InventoryImportDialog, report: InventoryImportReport) -> None:
        self._result_label.setText(
            self.tr(
                "Filas leídas: {total} · Aplicadas: {applied} · "
                "Errores: {errors} · Avisos: {warnings}"
            ).format(
                total=report.rows_total,
                applied=report.rows_applied,
                errors=len(report.errors),
                warnings=len(report.warnings),
            )
        )
        self._result_label.setVisible(True)

        rows: list[tuple[str, int, str, str]] = []
        for err in report.errors:
            rows.append((self.tr("Error"), err.row_index, "—", err.message))
        for w in report.warnings:
            card_label = f"{w.code_id}-{w.card_number}" if w.code_id else str(w.card_number)
            rows.append((self.tr("Aviso"), w.row_index, card_label, w.message))

        if not rows:
            self._result_table.setVisible(False)
            self._truncation_label.setVisible(False)
            return

        truncated = len(rows) > _DISPLAY_CAP
        display = rows[:_DISPLAY_CAP]
        self._result_table.setRowCount(len(display))
        for row, (kind, idx, card, msg) in enumerate(display):
            self._result_table.setItem(row, 0, QTableWidgetItem(kind))
            self._result_table.setItem(row, 1, QTableWidgetItem(str(idx)))
            self._result_table.setItem(row, 2, QTableWidgetItem(card))
            self._result_table.setItem(row, 3, QTableWidgetItem(msg))
        self._result_table.setVisible(True)

        if truncated:
            self._truncation_label.setText(
                self.tr(
                    "Mostrando {cap} de {total} filas con problemas. "
                    "Verificar el archivo de origen."
                ).format(cap=_DISPLAY_CAP, total=len(rows))
            )
            self._truncation_label.setVisible(True)
        else:
            self._truncation_label.setVisible(False)
