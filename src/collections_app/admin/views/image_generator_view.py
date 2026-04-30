"""Tab Generar Imágenes: ejecuta el ImagePipeline en un QThread y muestra log en vivo."""

import logging
import sqlite3
from datetime import datetime

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.image_pipeline.pipeline import (
    ImagePipeline,
    PipelineResult,
)
from collections_app.core.repositories import (
    CardsRepository,
    CollectionsRepository,
)
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)

LOG_MAX_LINES = 500


class PipelineWorker(QThread):
    """Ejecuta el ImagePipeline en un thread separado para no bloquear la UI."""

    progress = Signal(int, int, str)  # current, total, label
    log_entry = Signal(str, str, str)  # card_key, source, status
    result_ready = Signal(object)  # PipelineResult

    def __init__(
        self,
        pipeline: ImagePipeline,
        force: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._pipeline = pipeline
        self._force = force

    def run(self) -> None:
        try:
            result = self._pipeline.run_batch(
                on_progress=self._emit_progress,
                on_log=self._emit_log,
                force=self._force,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en PipelineWorker")
            result = PipelineResult(errors=[str(exc)])
        self.result_ready.emit(result)

    def _emit_progress(self, current: int, total: int, label: str) -> None:
        self.progress.emit(current, total, label)

    def _emit_log(self, card_key: str, source: str, status: str) -> None:
        self.log_entry.emit(card_key, source, status)

    def stop(self) -> None:
        """Pide al pipeline detenerse al finalizar la card actual."""
        self._pipeline.stop()


class ImageGeneratorView(QWidget):
    """Tab admin para generar imágenes de cards en batch."""

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._worker: PipelineWorker | None = None
        self._build_ui()
        self._populate_collections_combo()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Generador de Imágenes de Cards"))
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

        # Estado de generación
        self._state_label = QLabel("")
        layout.addWidget(self._state_label)
        self._overall_bar = QProgressBar()
        self._overall_bar.setRange(0, 100)
        layout.addWidget(self._overall_bar)

        # Progreso del batch actual
        self._batch_label = QLabel(self.tr("Procesando: —"))
        layout.addWidget(self._batch_label)
        self._batch_bar = QProgressBar()
        self._batch_bar.setRange(0, 100)
        layout.addWidget(self._batch_bar)

        # Botonera
        buttons_row = QHBoxLayout()
        self._start_button = QPushButton(self.tr("▶ Generar pendientes"))
        self._start_button.clicked.connect(self._start_pending)
        self._regen_button = QPushButton(self.tr("↺ Regenerar todas"))
        self._regen_button.clicked.connect(self._regenerate_all)
        self._stop_button = QPushButton(self.tr("⏹ Detener"))
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self._stop_worker)
        buttons_row.addWidget(self._start_button)
        buttons_row.addWidget(self._regen_button)
        buttons_row.addWidget(self._stop_button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)

        # Log
        layout.addWidget(QLabel(self.tr("Log") + ":"))
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setStyleSheet("font-family: Consolas, monospace; font-size: 10pt;")
        layout.addWidget(self._log_view, stretch=1)

    def _populate_collections_combo(self) -> None:
        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        self._collection_combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in CollectionsRepository(self.conn).list_all():
            self._collection_combo.addItem(col.collection_name, userData=col.collection_id)
        self._collection_combo.blockSignals(False)
        self._on_collection_changed(self._collection_combo.currentIndex())

    # ------------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------------

    def _on_collection_changed(self, idx: int) -> None:
        del idx
        cid = self._current_collection_id()
        if cid is None:
            self._state_label.setText(self.tr("(elegí una colección)"))
            self._overall_bar.setValue(0)
            self._set_buttons_enabled(False)
            return
        total = CardsRepository(self.conn).count_by_collection(cid)
        existing = ImagePipeline(self.conn, cid).get_existing_count()
        pct = (existing / total * 100) if total > 0 else 0.0
        self._state_label.setText(
            self.tr("Imágenes generadas: {e} / {t} ({p:.1f}%)").format(e=existing, t=total, p=pct)
        )
        self._overall_bar.setValue(int(pct))
        self._set_buttons_enabled(True)

    def _current_collection_id(self) -> int | None:
        data = self._collection_combo.currentData()
        return int(data) if data is not None else None

    def _set_buttons_enabled(self, enabled: bool) -> None:
        running = self._worker is not None and self._worker.isRunning()
        self._start_button.setEnabled(enabled and not running)
        self._regen_button.setEnabled(enabled and not running)
        self._stop_button.setEnabled(running)

    # ------------------------------------------------------------------
    # Worker control
    # ------------------------------------------------------------------

    def _start_pending(self) -> None:
        self._launch_worker(force=False)

    def _regenerate_all(self) -> None:
        confirmed = QMessageBox.question(
            self,
            self.tr("Regenerar todas"),
            self.tr("¿Regenerar todas las imágenes? Esto puede tardar varios minutos."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        self._launch_worker(force=True)

    def _launch_worker(self, force: bool) -> None:
        cid = self._current_collection_id()
        if cid is None:
            return
        pipeline = ImagePipeline(self.conn, cid)
        self._worker = PipelineWorker(pipeline, force=force, parent=self)
        self._worker.progress.connect(self._on_progress)
        self._worker.log_entry.connect(self._on_log_entry)
        self._worker.result_ready.connect(self._on_finished)
        self._worker.start()
        self._set_buttons_enabled(True)
        self._append_log(self.tr("Inicio de generación (force=") + str(force) + ")", "info")

    def _stop_worker(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._append_log(self.tr("Solicitud de detención…"), "warn")

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_progress(self, current: int, total: int, label: str) -> None:
        self._batch_label.setText(self.tr("Procesando: {label}").format(label=label))
        self._batch_bar.setRange(0, total or 1)
        self._batch_bar.setValue(current)

    def _on_log_entry(self, card_key: str, source: str, status: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        if status == "ok":
            level = "warn" if source == "placeholder" else "ok"
            line = f"[{ts}] {card_key} → {source} ✓"
        else:
            level = "error"
            line = f"[{ts}] {card_key} → {source} ✗ ({status})"
        self._append_log(line, level)

    def _on_finished(self, result: PipelineResult) -> None:
        self._append_log(
            self.tr(
                "Fin: {ok} ok, {fail} errores · DDG={d} Wiki={w} Cache={c} Placeholder={p}"
            ).format(
                ok=result.succeeded,
                fail=result.failed,
                d=result.from_duckduckgo,
                w=result.from_wikipedia,
                c=result.from_cache,
                p=result.from_placeholder,
            ),
            "info",
        )
        self._worker = None
        self._on_collection_changed(self._collection_combo.currentIndex())

    # ------------------------------------------------------------------
    # Log helpers
    # ------------------------------------------------------------------

    def _append_log(self, message: str, level: str) -> None:
        color = self._color_for_level(level)
        cursor = self._log_view.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(message + "\n", fmt)
        self._trim_log()
        self._log_view.ensureCursorVisible()

    def _trim_log(self) -> None:
        doc = self._log_view.document()
        block_count = doc.blockCount()
        if block_count <= LOG_MAX_LINES:
            return
        cursor = self._log_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        for _ in range(block_count - LOG_MAX_LINES):
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()  # newline

    @staticmethod
    def _color_for_level(level: str) -> str:
        return {
            "ok": StatusColor.SUCCESS,
            "warn": StatusColor.WARNING,
            "error": StatusColor.ERROR,
            "info": StatusColor.INFO,
        }.get(level, "#000000")
