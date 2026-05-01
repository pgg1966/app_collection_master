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
    GOOGLE_DAILY_LIMIT,
    ImagePipeline,
    PipelineResult,
)
from collections_app.core.repositories import (
    CardsRepository,
    CollectionsRepository,
)
from collections_app.core.utils.paths import get_database_path
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
        regenerate_placeholders_only: bool = False,
        regenerate_sketches_only: bool = False,
        google_fill_only: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._pipeline = pipeline
        self._force = force
        self._regenerate_placeholders_only = regenerate_placeholders_only
        self._regenerate_sketches_only = regenerate_sketches_only
        self._google_fill_only = google_fill_only

    def run(self) -> None:
        try:
            if self._regenerate_placeholders_only:
                result = self._pipeline.regenerate_placeholders(
                    on_progress=self._emit_progress,
                    on_log=self._emit_log,
                )
            elif self._regenerate_sketches_only:
                result = self._pipeline.run_resketch(
                    on_progress=self._emit_progress,
                    on_log=self._emit_log,
                )
            elif self._google_fill_only:
                result = self._pipeline.run_google_fill(
                    on_progress=self._emit_progress,
                    on_log=self._emit_log,
                )
            else:
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
        self._last_mode: str = "batch"  # batch | placeholders | sketches | google_fill
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

        # Contador de placeholders + cuota Google
        self._placeholder_label = QLabel("")
        self._placeholder_label.setStyleSheet("color: #555; font-style: italic;")
        layout.addWidget(self._placeholder_label)

        # Progreso del batch actual
        self._batch_label = QLabel(self.tr("Procesando: —"))
        layout.addWidget(self._batch_label)
        self._batch_bar = QProgressBar()
        self._batch_bar.setRange(0, 100)
        layout.addWidget(self._batch_bar)

        # Botonera principal
        buttons_row = QHBoxLayout()
        self._start_button = QPushButton(self.tr("▶ Generar pendientes"))
        self._start_button.clicked.connect(self._start_pending)
        self._regen_placeholders_button = QPushButton(
            self.tr("🔄 Regenerar placeholders (con mejoras)")
        )
        self._regen_placeholders_button.clicked.connect(self._regenerate_placeholders)
        self._regen_button = QPushButton(self.tr("↺ Regenerar todas"))
        self._regen_button.clicked.connect(self._regenerate_all)
        self._stop_button = QPushButton(self.tr("⏹ Detener"))
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self._stop_worker)
        buttons_row.addWidget(self._start_button)
        buttons_row.addWidget(self._regen_placeholders_button)
        buttons_row.addWidget(self._regen_button)
        buttons_row.addWidget(self._stop_button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)

        # Botonera secundaria: re-sketch sin internet + Google fill
        secondary_row = QHBoxLayout()
        self._resketch_button = QPushButton(
            self.tr("🎨 Regenerar sketches (mismo algoritmo, mejor calidad)")
        )
        self._resketch_button.clicked.connect(self._regenerate_sketches)
        self._google_fill_button = QPushButton(
            self.tr("🔍 Rellenar placeholders (cascada + Google max {n})").format(
                n=GOOGLE_DAILY_LIMIT
            )
        )
        self._google_fill_button.clicked.connect(self._google_fill)
        secondary_row.addWidget(self._resketch_button)
        secondary_row.addWidget(self._google_fill_button)
        secondary_row.addStretch()
        layout.addLayout(secondary_row)

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
            self._placeholder_label.setText("")
            self._overall_bar.setValue(0)
            self._set_buttons_enabled(False)
            return
        total = CardsRepository(self.conn).count_by_collection(cid)
        pipeline = ImagePipeline(get_database_path(), cid)
        found = pipeline.get_found_count()
        total_generated = pipeline.get_total_generated()
        placeholders = total_generated - found
        pending = max(0, total - total_generated)
        pct = (total_generated / total * 100) if total > 0 else 0.0
        self._state_label.setText(
            self.tr(
                "Fotos reales: {f} · Placeholders: {ph} · Pendientes: {p} · Total: {t} ({pct:.1f}%)"
            ).format(f=found, ph=placeholders, p=pending, t=total, pct=pct)
        )
        self._placeholder_label.setText(
            self.tr("Cards con placeholder: {ph} · Se procesarán hoy: hasta {n}").format(
                ph=placeholders, n=GOOGLE_DAILY_LIMIT
            )
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
        self._regen_placeholders_button.setEnabled(enabled and not running)
        self._resketch_button.setEnabled(enabled and not running)
        self._google_fill_button.setEnabled(enabled and not running)
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

    def _regenerate_placeholders(self) -> None:
        cid = self._current_collection_id()
        if cid is None:
            return
        pipeline = ImagePipeline(get_database_path(), cid)
        n = len(pipeline.get_placeholder_card_keys())
        if n == 0:
            QMessageBox.information(
                self,
                self.tr("Regenerar placeholders"),
                self.tr("No hay cards generadas como placeholder en esta colección."),
            )
            return
        confirmed = QMessageBox.question(
            self,
            self.tr("Regenerar placeholders"),
            self.tr(
                "Se reintentará la búsqueda online de {n} cards que cayeron a "
                "placeholder. Esto puede tardar varios minutos."
            ).format(n=n),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        self._launch_worker(force=False, regenerate_placeholders_only=True)

    def _regenerate_sketches(self) -> None:
        """Re-aplica el algoritmo actual de sketch a las fotos cacheadas."""
        cid = self._current_collection_id()
        if cid is None:
            return
        confirmed = QMessageBox.question(
            self,
            self.tr("Regenerar sketches"),
            self.tr(
                "Se regenerarán los sketches de todas las cards con foto cacheada "
                "usando el algoritmo actual (sin internet). ¿Continuar?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        self._launch_worker(force=False, regenerate_sketches_only=True)

    def _google_fill(self) -> None:
        """Rellena placeholders con cascada Wiki → DDG → Google (max 100/día)."""
        cid = self._current_collection_id()
        if cid is None:
            return
        pipeline = ImagePipeline(get_database_path(), cid)
        n = len(pipeline.get_placeholder_card_keys())
        if n == 0:
            QMessageBox.information(
                self,
                self.tr("Rellenar placeholders"),
                self.tr("No hay cards en placeholder para rellenar."),
            )
            return
        confirmed = QMessageBox.question(
            self,
            self.tr("Rellenar placeholders"),
            self.tr(
                "Se intentará rellenar {n} placeholders con la cascada completa "
                "(Wikipedia → DuckDuckGo → Google). Google se usará solo cuando los "
                "primeros fallen, hasta un máximo de {q} queries hoy."
            ).format(n=n, q=GOOGLE_DAILY_LIMIT),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        self._launch_worker(force=False, google_fill_only=True)

    def _launch_worker(
        self,
        force: bool,
        regenerate_placeholders_only: bool = False,
        regenerate_sketches_only: bool = False,
        google_fill_only: bool = False,
    ) -> None:
        cid = self._current_collection_id()
        if cid is None:
            return
        # ImagePipeline recibe db_path (no conn) porque corre en QThread:
        # SQLite no permite usar una conexión cross-thread.
        pipeline = ImagePipeline(get_database_path(), cid)
        self._worker = PipelineWorker(
            pipeline,
            force=force,
            regenerate_placeholders_only=regenerate_placeholders_only,
            regenerate_sketches_only=regenerate_sketches_only,
            google_fill_only=google_fill_only,
            parent=self,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.log_entry.connect(self._on_log_entry)
        self._worker.result_ready.connect(self._on_finished)
        self._worker.start()
        self._set_buttons_enabled(True)
        if regenerate_placeholders_only:
            self._last_mode = "placeholders"
            self._append_log(self.tr("Inicio de regeneración de placeholders"), "info")
        elif regenerate_sketches_only:
            self._last_mode = "sketches"
            self._append_log(self.tr("Inicio de regeneración de sketches (sin internet)"), "info")
        elif google_fill_only:
            self._last_mode = "google_fill"
            self._append_log(
                self.tr("Inicio de rellenado con cascada completa (Google max {n} hoy)").format(
                    n=GOOGLE_DAILY_LIMIT
                ),
                "info",
            )
        else:
            self._last_mode = "batch"
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
        if self._last_mode == "google_fill":
            replaced = result.from_wikipedia + result.from_duckduckgo + result.from_google
            self._append_log(
                self.tr(
                    "Reemplazadas: {r} (de las cuales: {w} wikipedia, {d} duckduckgo, "
                    "{g} google)"
                ).format(
                    r=replaced,
                    w=result.from_wikipedia,
                    d=result.from_duckduckgo,
                    g=result.from_google,
                ),
                "info",
            )
            self._append_log(
                self.tr("Siguen como placeholder: {n}").format(n=result.from_placeholder),
                "warn" if result.from_placeholder else "info",
            )
            self._append_log(
                self.tr("Cuota Google usada: {used}/{quota}").format(
                    used=result.google_calls_used, quota=GOOGLE_DAILY_LIMIT
                ),
                "info",
            )
            if result.google_quota_exhausted:
                self._append_log(
                    self.tr(
                        "⚠ Cuota diaria de Google alcanzada — reintentar mañana "
                        "para rellenar los restantes"
                    ),
                    "warn",
                )
        else:
            self._append_log(
                self.tr(
                    "Fin: {ok} ok, {fail} errores · Wiki={w} DDG={d} Google={g} "
                    "Cache={c} Placeholder={p}"
                ).format(
                    ok=result.succeeded,
                    fail=result.failed,
                    w=result.from_wikipedia,
                    d=result.from_duckduckgo,
                    g=result.from_google,
                    c=result.from_cache,
                    p=result.from_placeholder,
                ),
                "info",
            )
            if result.google_calls_used:
                self._append_log(
                    self.tr("Google: {used} queries usadas en esta sesión").format(
                        used=result.google_calls_used
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
