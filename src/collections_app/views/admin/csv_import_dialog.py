"""Diálogo "Nueva colección desde CSV".

Reemplaza el placeholder del menú "Archivo → Nueva colección desde CSV..."
de la `MainWindow`. Cubre el flow completo: crea header + colección si no
existen y delega a `CsvImportService.import_collection_from_csvs(...)`.

UX:
- Inputs requeridos: nombre de colección y nombre de header. Sin ellos
  el botón Importar queda deshabilitado.
- Defaults sensatos para el resto: code_field_name="País",
  code_max_length=3, requires_code=True.
- Ambos archivos opcionales: si solo se provee uno, se importa eso.
- Después del import emite signal `import_completed(dict[str, CsvImportReport])`
  que el caller (MainWindow) usa para refrescar el sidebar.
- Errores: muestra hasta `_ERRORS_DISPLAY_CAP` (200). Si hay más,
  un mensaje al pie alerta sobre revisar el archivo de origen.

El service catastrófico se traduce a `QMessageBox.critical` y el dialog
no se cierra — el usuario puede ajustar inputs y reintentar.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exceptions import ServiceError

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.aggregates.csv_import_report import (
        CsvImportReport,
    )

_ERRORS_DISPLAY_CAP = 200
_ERROR_HEADERS = ["Tipo", "Fila", "Mensaje"]


class CsvImportDialog(QDialog):
    """Diálogo único para crear una colección a partir de CSVs."""

    import_completed = Signal(dict)

    def __init__(
        self: CsvImportDialog,
        ctx: AppContext,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self.setWindowTitle(self.tr("Nueva colección desde CSV"))
        self.resize(700, 500)
        self._build_ui()
        self._update_import_enabled()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: CsvImportDialog) -> None:
        outer = QVBoxLayout(self)

        form = QFormLayout()
        self._collection_name = QLineEdit()
        self._collection_name.textChanged.connect(self._update_import_enabled)
        form.addRow(self.tr("Nombre de la colección"), self._collection_name)

        self._header_name = QLineEdit()
        self._header_name.textChanged.connect(self._update_import_enabled)
        form.addRow(self.tr("Nombre del CodeHeader"), self._header_name)

        self._code_field_name = QLineEdit("País")
        form.addRow(self.tr("Etiqueta del campo de código (UI)"), self._code_field_name)

        self._code_max_length = QSpinBox()
        self._code_max_length.setRange(1, 32)
        self._code_max_length.setValue(3)
        form.addRow(self.tr("Longitud máxima de code_id"), self._code_max_length)

        self._requires_code = QCheckBox()
        self._requires_code.setChecked(True)
        form.addRow(self.tr("Requires code"), self._requires_code)

        self._codes_path_edit, codes_row = self._make_file_picker(self.tr("Archivo de codes (CSV)"))
        self._cards_path_edit, cards_row = self._make_file_picker(self.tr("Archivo de cards (CSV)"))
        form.addRow(self.tr("Archivo de codes (CSV)"), codes_row)
        form.addRow(self.tr("Archivo de cards (CSV)"), cards_row)

        outer.addLayout(form)

        # Botones
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

        self._errors_table = QTableWidget(0, len(_ERROR_HEADERS))
        self._errors_table.setHorizontalHeaderLabels(_ERROR_HEADERS)
        self._errors_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._errors_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self._errors_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._errors_table.setVisible(False)
        outer.addWidget(self._errors_table)

        self._truncation_label = QLabel("")
        self._truncation_label.setVisible(False)
        self._truncation_label.setStyleSheet("color: #854F0B;")
        outer.addWidget(self._truncation_label)

    def _make_file_picker(self: CsvImportDialog, label_text: str) -> tuple[QLineEdit, QHBoxLayout]:
        edit = QLineEdit()
        edit.setReadOnly(True)
        edit.setPlaceholderText(self.tr("(opcional)"))
        btn = QPushButton(self.tr("Examinar..."))

        def on_browse() -> None:
            path, _ = QFileDialog.getOpenFileName(
                self, label_text, "", self.tr("CSV files (*.csv)")
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
    # Estado del botón Importar
    # ------------------------------------------------------------------

    def _update_import_enabled(self: CsvImportDialog) -> None:
        coll_name_ok = bool(self._collection_name.text().strip())
        header_name_ok = bool(self._header_name.text().strip())
        self._import_btn.setEnabled(coll_name_ok and header_name_ok)

    # ------------------------------------------------------------------
    # Acción de import
    # ------------------------------------------------------------------

    def _on_import(self: CsvImportDialog) -> None:
        codes_path = self._codes_path_edit.text().strip()
        cards_path = self._cards_path_edit.text().strip()
        if not codes_path and not cards_path:
            QMessageBox.warning(
                self,
                self.tr("Sin archivos"),
                self.tr("Seleccioná al menos uno de los dos CSVs (codes o cards)."),
            )
            return

        try:
            reports = self._ctx.csv_import.import_collection_from_csvs(
                collection_name=self._collection_name.text().strip(),
                code_header_name=self._header_name.text().strip(),
                code_field_name=self._code_field_name.text().strip() or "País",
                code_max_length=self._code_max_length.value(),
                requires_code=self._requires_code.isChecked(),
                codes_csv_path=Path(codes_path) if codes_path else None,
                cards_csv_path=Path(cards_path) if cards_path else None,
            )
        except ServiceError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de importación"),
                str(exc),
            )
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de I/O"),
                self.tr("No se pudo abrir el archivo: {msg}").format(msg=exc),
            )
            return

        self._render_result(reports)
        self.import_completed.emit(reports)

    # ------------------------------------------------------------------
    # Render del resultado
    # ------------------------------------------------------------------

    def _render_result(self: CsvImportDialog, reports: dict[str, CsvImportReport]) -> None:
        lines: list[str] = []
        all_errors: list[tuple[str, int, str]] = []
        for kind, report in reports.items():
            lines.append(
                self.tr(
                    "{kind}: {inserted} importados, {skipped} omitidos " "(de {total} filas)"
                ).format(
                    kind=kind,
                    inserted=report.rows_inserted,
                    skipped=report.rows_skipped,
                    total=report.rows_total,
                )
            )
            for err in report.errors:
                all_errors.append((kind, err.row_index, err.message))

        self._result_label.setText("\n".join(lines))
        self._result_label.setVisible(True)
        self._populate_errors_table(all_errors)

    def _populate_errors_table(self: CsvImportDialog, errors: list[tuple[str, int, str]]) -> None:
        if not errors:
            self._errors_table.setVisible(False)
            self._truncation_label.setVisible(False)
            return

        truncated = len(errors) > _ERRORS_DISPLAY_CAP
        display = errors[:_ERRORS_DISPLAY_CAP]
        self._errors_table.setRowCount(len(display))
        for row, (kind, idx, msg) in enumerate(display):
            self._errors_table.setItem(row, 0, QTableWidgetItem(kind))
            self._errors_table.setItem(row, 1, QTableWidgetItem(str(idx) if idx >= 0 else "—"))
            self._errors_table.setItem(row, 2, QTableWidgetItem(msg))
        self._errors_table.setVisible(True)

        if truncated:
            self._truncation_label.setText(
                self.tr(
                    "Mostrando {cap} de {total} errores. Verificar el archivo "
                    "de origen — algo grave puede estar mal."
                ).format(cap=_ERRORS_DISPLAY_CAP, total=len(errors))
            )
            self._truncation_label.setVisible(True)
        else:
            self._truncation_label.setVisible(False)
