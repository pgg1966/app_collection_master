"""Tab Escudos: gestiona el escudo de cada code_id de una colección."""

import logging
import shutil
import sqlite3
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.crests import (
    SPECIAL_CODES,
    CrestFinder,
)
from collections_app.admin.crests.crest_finder import CrestResult
from collections_app.core.models import CodeLine, Collection
from collections_app.core.repositories import (
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.core.utils.paths import get_crest_path
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)

PREVIEW_SIZE = 150
ICON_SIZE = 32

STATUS_NONE = "Sin escudo"
STATUS_WIKIPEDIA = "Wikipedia"
STATUS_MANUAL = "Manual"
STATUS_PLACEHOLDER = "Placeholder"


class _CrestSearchWorker(QThread):
    """Ejecuta `CrestFinder.find_all_crests` en un thread separado."""

    progress = Signal(int, int, str)
    finished_ok = Signal(list)  # list[CrestResult]
    failed = Signal(str)

    def __init__(
        self,
        finder: CrestFinder,
        codes: list[tuple[str, str]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._finder = finder
        self._codes = codes

    def run(self) -> None:
        try:
            results = self._finder.find_all_crests(self._codes, on_progress=self._emit)
            self.finished_ok.emit(results)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en _CrestSearchWorker")
            self.failed.emit(str(exc))

    def _emit(self, current: int, total: int, label: str) -> None:
        self.progress.emit(current, total, label)


class CrestsView(QWidget):
    """Tab admin: ver / buscar / importar escudos por code_id."""

    COL_ICON = 0
    COL_CODE = 1
    COL_NAME = 2
    COL_STATUS = 3

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._finder = CrestFinder()
        self._worker: _CrestSearchWorker | None = None
        self._build_ui()
        self._populate_collections_combo()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Gestión de Escudos"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        # Combo de colecciones
        combo_row = QHBoxLayout()
        combo_row.addWidget(QLabel(self.tr("Colección") + ":"))
        self._collection_combo = QComboBox()
        self._collection_combo.setMinimumWidth(280)
        self._collection_combo.currentIndexChanged.connect(self._on_collection_changed)
        combo_row.addWidget(self._collection_combo)
        combo_row.addStretch()
        layout.addLayout(combo_row)

        # Tabla
        self._model = QStandardItemModel(0, 4, self)
        self._model.setHorizontalHeaderLabels(
            [self.tr(""), self.tr("Code"), self.tr("Nombre"), self.tr("Estado")]
        )
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(self.COL_ICON, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_CODE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeMode.ResizeToContents)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_selected)
        layout.addWidget(self._table, stretch=1)

        # Botonera
        buttons_row = QHBoxLayout()
        self._search_button = QPushButton(self.tr("🌐 Buscar automáticamente (países)"))
        self._search_button.clicked.connect(self._search_auto)
        self._import_button = QPushButton(self.tr("📂 Importar imagen para code seleccionado"))
        self._import_button.clicked.connect(self._import_manual)
        self._delete_button = QPushButton(self.tr("🗑️ Borrar escudo seleccionado"))
        self._delete_button.clicked.connect(self._delete_crest)
        buttons_row.addWidget(self._search_button)
        buttons_row.addWidget(self._import_button)
        buttons_row.addWidget(self._delete_button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)

        # Preview
        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel(self.tr("Preview") + ":"))
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(PREVIEW_SIZE, PREVIEW_SIZE)
        self._preview_label.setStyleSheet("border: 1px solid #888; background: #f0f0f0;")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_row.addWidget(self._preview_label)
        preview_row.addStretch()
        layout.addLayout(preview_row)

    def _populate_collections_combo(self) -> None:
        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        self._collection_combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in CollectionsRepository(self.conn).list_all():
            self._collection_combo.addItem(col.collection_name, userData=col.collection_id)
        self._collection_combo.blockSignals(False)
        self._on_collection_changed(self._collection_combo.currentIndex())

    # ------------------------------------------------------------------
    # Cambios de selección
    # ------------------------------------------------------------------

    def _on_collection_changed(self, idx: int) -> None:
        del idx
        cid = self._current_collection_id()
        if cid is None:
            self._model.removeRows(0, self._model.rowCount())
            self._set_buttons_enabled(False)
            self._preview_label.clear()
            return
        self._refresh_grid(cid)
        self._set_buttons_enabled(True)

    def _current_collection_id(self) -> int | None:
        data = self._collection_combo.currentData()
        return int(data) if data is not None else None

    def _current_collection(self) -> Collection | None:
        cid = self._current_collection_id()
        if cid is None:
            return None
        return CollectionsRepository(self.conn).get_by_id(cid)

    def _selected_code_line(self) -> CodeLine | None:
        idx = self._table.currentIndex()
        if not idx.isValid():
            return None
        row = idx.row()
        code_id = self._model.item(row, self.COL_CODE).text()
        code_name = self._model.item(row, self.COL_NAME).text()
        col = self._current_collection()
        header_id = col.code_header_id if col is not None else 0
        return CodeLine(code_header_id=header_id, code_id=code_id, code_name=code_name)

    def _on_row_selected(self) -> None:
        line = self._selected_code_line()
        if line is None:
            self._preview_label.clear()
            return
        path = get_crest_path(line.code_id)
        if path.exists():
            pix = QPixmap(str(path)).scaled(
                PREVIEW_SIZE,
                PREVIEW_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._preview_label.setPixmap(pix)
        else:
            self._preview_label.setText(self.tr("(sin escudo)"))

    # ------------------------------------------------------------------
    # Grid
    # ------------------------------------------------------------------

    def _refresh_grid(self, collection_id: int) -> None:
        col = CollectionsRepository(self.conn).get_by_id(collection_id)
        if col is None:
            self._model.removeRows(0, self._model.rowCount())
            return
        lines = CodesLinesRepository(self.conn).list_by_header(col.code_header_id)
        self._model.removeRows(0, self._model.rowCount())
        for line in lines:
            self._model.appendRow(self._build_row(line))

    def _build_row(self, line: CodeLine) -> list[QStandardItem]:
        path = get_crest_path(line.code_id)
        icon_item = QStandardItem()
        if path.exists():
            icon_item.setIcon(QIcon(str(path)))
        code_item = QStandardItem(line.code_id)
        name_item = QStandardItem(line.code_name)
        status_item = QStandardItem(self._compute_status(line.code_id, path))
        return [icon_item, code_item, name_item, status_item]

    @staticmethod
    def _compute_status(code_id: str, path: Path) -> str:
        if not path.exists():
            return STATUS_NONE if code_id not in SPECIAL_CODES else STATUS_PLACEHOLDER
        # Heurística simple: el placeholder generado tiene el code_id en
        # el nombre del archivo no, pero lo identificamos por ser el
        # único caso "auto" cuando code_id ∈ SPECIAL_CODES. Para el resto
        # asumimos Wikipedia o Manual y mostramos el más probable según
        # cuándo se modificó (no diferenciamos en este nivel — el usuario
        # ve por el preview si es real o placeholder).
        return STATUS_PLACEHOLDER if code_id in SPECIAL_CODES else STATUS_WIKIPEDIA

    def _set_buttons_enabled(self, enabled: bool) -> None:
        running = self._worker is not None and self._worker.isRunning()
        self._search_button.setEnabled(enabled and not running)
        self._import_button.setEnabled(enabled and not running)
        self._delete_button.setEnabled(enabled and not running)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _search_auto(self) -> None:
        cid = self._current_collection_id()
        if cid is None:
            return
        col = CollectionsRepository(self.conn).get_by_id(cid)
        if col is None:
            return
        # Procesamos sólo codes que NO están en SPECIAL_CODES y que NO
        # tienen escudo cacheado.
        all_lines = CodesLinesRepository(self.conn).list_by_header(col.code_header_id)
        candidates: list[tuple[str, str]] = [
            (line.code_id, line.code_name)
            for line in all_lines
            if line.code_id not in SPECIAL_CODES and not get_crest_path(line.code_id).exists()
        ]
        if not candidates:
            QMessageBox.information(
                self,
                self.tr("Buscar escudos"),
                self.tr("No hay códigos sin escudo para procesar."),
            )
            return

        progress = QProgressDialog(
            self.tr("Descargando escudos…"),
            self.tr("Cancelar"),
            0,
            len(candidates),
            self,
        )
        progress.setWindowTitle(self.tr("Buscar escudos"))
        progress.setMinimumDuration(0)

        self._worker = _CrestSearchWorker(self._finder, candidates, parent=self)
        worker = self._worker

        def on_progress(c: int, _t: int, label: str) -> None:
            progress.setValue(c)
            progress.setLabelText(label)

        def on_ok(results: list[CrestResult]) -> None:
            progress.close()
            wiki = sum(1 for r in results if r.source == "wikipedia")
            ph = sum(1 for r in results if r.source == "placeholder")
            QMessageBox.information(
                self,
                self.tr("Buscar escudos"),
                self.tr("Procesados: {n}. Wikipedia: {w}. Placeholder: {p}.").format(
                    n=len(results), w=wiki, p=ph
                ),
            )
            assert cid is not None
            self._refresh_grid(cid)
            self._on_row_selected()
            self._set_buttons_enabled(True)

        def on_failed(msg: str) -> None:
            progress.close()
            QMessageBox.critical(self, self.tr("Buscar escudos"), msg)
            self._set_buttons_enabled(True)

        def on_canceled() -> None:
            worker.requestInterruption()
            progress.close()
            self._set_buttons_enabled(True)

        worker.progress.connect(on_progress)
        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        progress.canceled.connect(on_canceled)
        worker.start()
        self._set_buttons_enabled(True)

    def _import_manual(self) -> None:
        line = self._selected_code_line()
        if line is None:
            QMessageBox.warning(
                self,
                self.tr("Importar escudo"),
                self.tr("Seleccioná una fila primero."),
            )
            return
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Elegir imagen para {code}").format(code=line.code_id),
            "",
            self.tr("Imágenes (*.png *.jpg *.jpeg *.svg *.webp);;Todos (*)"),
        )
        if not path_str:
            return
        result = self._finder.import_manual_crest(line.code_id, Path(path_str))
        if not result.success:
            QMessageBox.critical(
                self,
                self.tr("Importar escudo"),
                self.tr("No se pudo procesar la imagen: {err}").format(err=result.error or ""),
            )
            return
        # Marcar el row como manual y refrescar
        cid = self._current_collection_id()
        if cid is not None:
            self._refresh_grid(cid)
        self._set_status_for(line.code_id, STATUS_MANUAL)
        self._on_row_selected()

    def _delete_crest(self) -> None:
        line = self._selected_code_line()
        if line is None:
            return
        path = get_crest_path(line.code_id)
        if not path.exists():
            return
        confirmed = QMessageBox.question(
            self,
            self.tr("Borrar escudo"),
            self.tr("¿Borrar el escudo de {code}?").format(code=line.code_id),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        path.unlink(missing_ok=True)
        cid = self._current_collection_id()
        if cid is not None:
            self._refresh_grid(cid)
        self._on_row_selected()

    def _set_status_for(self, code_id: str, status: str) -> None:
        for row in range(self._model.rowCount()):
            if self._model.item(row, self.COL_CODE).text() == code_id:
                self._model.item(row, self.COL_STATUS).setText(status)
                # Refrescar icono
                path = get_crest_path(code_id)
                if path.exists():
                    self._model.item(row, self.COL_ICON).setIcon(QIcon(str(path)))
                return


# Helper exportado para uso externo (tests)
def copy_crest_file(src: Path, code_id: str) -> Path:
    """Copia `src` a `get_crest_path(code_id)` (para tests / scripts)."""
    dest = get_crest_path(code_id)
    shutil.copy(src, dest)
    return dest
