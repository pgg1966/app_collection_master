"""Tab Álbum: genera PDFs imprimibles y exporta listas TXT."""

import logging
import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection
from collections_app.core.repositories import CodesLinesRepository
from collections_app.core.services import (
    AlbumConfig,
    InventoryService,
    PdfAlbumGenerator,
)
from collections_app.core.utils.paths import get_crest_path
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class _PdfWorker(QThread):
    """Ejecuta `task(output_path, on_progress)` en un thread separado.

    `task` puede ser `generate_unique_album`, `generate_duplicates_album`, o
    cualquier callable con esa misma firma.
    """

    progress = Signal(int, int)
    finished_ok = Signal(object)  # Path
    failed = Signal(str)

    def __init__(
        self,
        task: Callable[[Path, Callable[[int, int], None] | None], Path],
        output_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._task = task
        self._output_path = output_path

    def run(self) -> None:
        try:
            result = self._task(self._output_path, self._emit_progress)
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en _PdfWorker")
            # Si quedó un PDF parcial, borrarlo
            if self._output_path.exists():
                self._output_path.unlink(missing_ok=True)
            self.failed.emit(str(exc))

    def _emit_progress(self, current: int, total: int) -> None:
        self.progress.emit(current, total)


class AlbumView(QWidget):
    """Tab del cliente: genera álbum PDF y listas TXT."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._worker: _PdfWorker | None = None
        self._build_ui()
        self._refresh_image_count()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self._refresh_image_count()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Generador de Álbum PDF"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        layout.addWidget(self._build_unique_section())
        layout.addWidget(self._build_duplicates_section())
        layout.addWidget(self._build_lists_section())
        layout.addWidget(self._build_info_section())
        layout.addStretch()

    def _build_unique_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.SM)
        layout.addWidget(self._section_title("📗 Álbum Principal (Únicas)"))
        layout.addWidget(
            QLabel(
                self.tr(
                    "Todas las cards organizadas por categoría. "
                    "Las que tenés en color, las que faltan en gris."
                )
            )
        )

        opts = QHBoxLayout()
        opts.addWidget(QLabel(self.tr("Incluir:")))
        self._include_owned = QCheckBox(self.tr("Tengo"))
        self._include_owned.setChecked(True)
        self._include_missing = QCheckBox(self.tr("Faltan"))
        self._include_missing.setChecked(True)
        opts.addWidget(self._include_owned)
        opts.addWidget(self._include_missing)
        opts.addSpacing(20)
        opts.addWidget(QLabel(self.tr("Layout:")))
        self._cols_input = QSpinBox()
        self._cols_input.setRange(1, 8)
        self._cols_input.setValue(4)
        opts.addWidget(self._cols_input)
        opts.addWidget(QLabel("×"))
        self._rows_input = QSpinBox()
        self._rows_input.setRange(1, 8)
        self._rows_input.setValue(3)
        opts.addWidget(self._rows_input)
        opts.addStretch()
        layout.addLayout(opts)

        self._unique_button = QPushButton(self.tr("📄 Generar álbum de únicas"))
        self._unique_button.clicked.connect(self._generate_unique)
        layout.addWidget(self._unique_button)
        return frame

    def _build_duplicates_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.SM)
        layout.addWidget(self._section_title("📕 Álbum de Repetidas"))
        layout.addWidget(QLabel(self.tr("Solo las que tenés de más, con badge de cantidad.")))
        self._duplicates_button = QPushButton(self.tr("📄 Generar álbum de repetidas"))
        self._duplicates_button.clicked.connect(self._generate_duplicates)
        layout.addWidget(self._duplicates_button)
        return frame

    def _build_lists_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.SM)
        layout.addWidget(self._section_title("📝 Exportar Listas"))
        row = QHBoxLayout()
        self._missing_list_button = QPushButton(self.tr("📋 Lista de faltantes"))
        self._missing_list_button.clicked.connect(self._export_missing)
        self._duplicates_list_button = QPushButton(self.tr("📋 Lista de repetidas"))
        self._duplicates_list_button.clicked.connect(self._export_duplicates)
        row.addWidget(self._missing_list_button)
        row.addWidget(self._duplicates_list_button)
        row.addStretch()
        layout.addLayout(row)
        return frame

    def _build_info_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.XS)
        layout.addWidget(self._section_title("ℹ️ Info de imágenes"))
        self._image_count_label = QLabel("")
        layout.addWidget(self._image_count_label)
        self._last_run_label = QLabel(self.tr("Última generación: —"))
        layout.addWidget(self._last_run_label)
        return frame

    def _section_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(1)
        return frame

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        return label

    # ------------------------------------------------------------------
    # Info: cuántas imágenes hay generadas
    # ------------------------------------------------------------------

    def _refresh_image_count(self) -> None:
        """Muestra cuántos códigos de la colección ya tienen escudo."""
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        total_cards = InventoryService(self.conn).get_stats(cid)["total_cards"]
        if total_cards == 0:
            self._image_count_label.setText(
                self.tr("La colección no tiene cards en el catálogo todavía.")
            )
            return
        lines = CodesLinesRepository(self.conn).list_by_header(self.collection.code_header_id)
        total_codes = len(lines)
        with_crest = sum(1 for line in lines if get_crest_path(line.code_id).exists())
        if total_codes == 0:
            self._image_count_label.setText(
                self.tr("La colección no tiene códigos definidos todavía.")
            )
            return
        if with_crest == 0:
            self._image_count_label.setText(
                self.tr(
                    "No hay escudos cargados. Configurá los escudos desde el "
                    "Admin (tab Escudos)."
                )
            )
            return
        pct = (with_crest / total_codes * 100) if total_codes > 0 else 0
        self._image_count_label.setText(
            self.tr("Escudos cargados: {n} / {t} ({pct:.1f}%)").format(
                n=with_crest, t=total_codes, pct=pct
            )
            + "\n"
            + self.tr("Los códigos sin escudo se renderizan solo con número y nombre.")
        )

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _default_filename(self, prefix: str, ext: str) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        slug = self.collection.collection_name.replace(" ", "_")
        return f"{prefix}_{slug}_{date}.{ext}"

    def _ask_save_path(self, default_name: str, file_filter: str) -> Path | None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar como"),
            default_name,
            file_filter,
        )
        return Path(path_str) if path_str else None

    def _make_generator(self) -> PdfAlbumGenerator:
        config = AlbumConfig(
            cols=self._cols_input.value(),
            rows=self._rows_input.value(),
            show_owned=self._include_owned.isChecked(),
            show_missing=self._include_missing.isChecked(),
        )
        return PdfAlbumGenerator(self.conn, self.collection, config=config)

    def _generate_unique(self) -> None:
        out = self._ask_save_path(
            self._default_filename("album_unicas", "pdf"),
            self.tr("PDF (*.pdf)"),
        )
        if out is None:
            return
        gen = self._make_generator()
        self._run_pdf_worker(gen.generate_unique_album, out, "Álbum de únicas")

    def _generate_duplicates(self) -> None:
        # Pre-check: si no hay repetidas, mostrar info y no abrir FileDialog
        assert self.collection.collection_id is not None
        stats = InventoryService(self.conn).get_stats(self.collection.collection_id)
        if int(stats["cards_with_duplicates"]) == 0:
            QMessageBox.information(
                self,
                self.tr("Álbum de repetidas"),
                self.tr("No tenés repetidas en esta colección todavía."),
            )
            return
        out = self._ask_save_path(
            self._default_filename("album_repetidas", "pdf"),
            self.tr("PDF (*.pdf)"),
        )
        if out is None:
            return
        gen = PdfAlbumGenerator(self.conn, self.collection)
        self._run_pdf_worker(gen.generate_duplicates_album, out, "Álbum de repetidas")

    def _export_missing(self) -> None:
        out = self._ask_save_path(
            self._default_filename("faltantes", "txt"),
            self.tr("Texto (*.txt)"),
        )
        if out is None:
            return
        try:
            PdfAlbumGenerator(self.conn, self.collection).export_missing_list(out)
        except OSError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self._mark_done()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(out)))

    def _export_duplicates(self) -> None:
        out = self._ask_save_path(
            self._default_filename("repetidas", "txt"),
            self.tr("Texto (*.txt)"),
        )
        if out is None:
            return
        try:
            PdfAlbumGenerator(self.conn, self.collection).export_duplicates_list(out)
        except OSError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self._mark_done()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(out)))

    # ------------------------------------------------------------------
    # Worker handling
    # ------------------------------------------------------------------

    def _run_pdf_worker(
        self,
        task: Callable[[Path, Callable[[int, int], None] | None], Path],
        output_path: Path,
        title: str,
    ) -> None:
        progress = QProgressDialog(
            self.tr("Generando {t}…").format(t=title),
            self.tr("Cancelar"),
            0,
            100,
            self,
        )
        progress.setWindowTitle(title)
        progress.setMinimumDuration(0)

        self._worker = _PdfWorker(task, output_path, parent=self)
        worker = self._worker

        def on_progress(c: int, t: int) -> None:
            progress.setMaximum(max(1, t))
            progress.setValue(c)

        def on_ok(path: object) -> None:
            progress.close()
            self._mark_done()
            QMessageBox.information(
                self,
                title,
                self.tr("Generado: {path}").format(path=path),
            )
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

        def on_failed(msg: str) -> None:
            progress.close()
            QMessageBox.critical(self, title, msg)

        def on_canceled() -> None:
            worker.requestInterruption()
            output_path.unlink(missing_ok=True)
            progress.close()

        worker.progress.connect(on_progress)
        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        progress.canceled.connect(on_canceled)
        worker.start()

    def _mark_done(self) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._last_run_label.setText(self.tr("Última generación: {ts}").format(ts=ts))
