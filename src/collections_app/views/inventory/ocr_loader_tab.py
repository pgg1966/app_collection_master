"""Tab "Por foto" — carga de inventario por reconocimiento óptico (Sesión 5d).

Tres estados, vivientes en un `QStackedWidget`:

1. Sin dependencias (torch/ultralytics) instaladas → mensaje + botón
   para instalarlas. La instalación corre en `QThread` y emite
   progreso. Al terminar se re-evalúa el estado.
2. Dependencias OK pero la colección no tiene modelo configurado →
   mensaje "pedile al admin que configure el modelo".
3. Listo → botón "Agregar fotos" que abre un file picker, lista de
   fotos pendientes, panel de resultados foto-a-foto con tabla de
   detecciones y los tres botones del flow (cargar / saltar / cancelar).

Re-evaluación: en `__init__`, después de instalar exitosamente, y
cuando cambia la collection vía `set_active_collection`.

Inferencia: cada foto se procesa en un `QThread` para no bloquear la
UI. El service se obtiene del `AppContext` vía
`ctx.get_ocr_service(collection)` (factory, devuelve `None` si no
está disponible).

Apply: las cards tildadas (≥70% pre-seleccionadas, el user puede
ajustar) se aplican vía `inventory_service.add_card` por cada
detección. Tras aplicar la última foto se emite `card_changed` para
que el resto de los tabs se refresque.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exceptions import (
    InventoryError,
    OcrError,
    OcrInstallError,
)
from collections_app.services.ocr_install_service import OcrInstallService

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection
    from collections_app.core.models.ocr_detection import OcrDetection, OcrParseError
    from collections_app.services.ocr_service import OcrService


_CONFIDENCE_THRESHOLD = 0.70

# Sentinels que indican que pip falló por archivos bloqueados. El
# patrón aparece tal cual en Windows (CPython traduce automáticamente
# el `errno` a "WinError 5"; el español a "Acceso denegado").
_ACCESS_DENIED_HINTS: tuple[str, ...] = ("WinError 5", "Acceso denegado")


def _format_install_error(raw_message: str) -> str:
    """Si el error de pip es de archivos bloqueados, dar instrucciones.

    Devuelve el mensaje crudo en cualquier otro caso. Función pura
    para que el test la cubra sin necesidad de Qt.
    """
    if any(hint in raw_message for hint in _ACCESS_DENIED_HINTS):
        return (
            "Acceso denegado.\n\n"
            "Intentá:\n"
            "1. Cerrar la app\n"
            "2. Abrir PowerShell como administrador\n"
            "3. Correr: .venv\\Scripts\\pip install easyocr opencv-python\n"
            "4. Reabrir la app\n\n"
            "Detalle técnico:\n"
            f"{raw_message}"
        )
    return raw_message


_PAGE_INSTALL = 0
_PAGE_NO_MODEL = 1
_PAGE_READY = 2

_RESULT_HEADERS = ["", "Código", "Nombre", "Confianza"]
_COL_CHECK = 0
_COL_CODE = 1
_COL_NAME = 2
_COL_CONF = 3


# ======================================================================
# Workers de QThread
# ======================================================================


class _InstallWorker(QObject):
    """Wrapper de `OcrInstallService.install` para correr en un QThread."""

    progress = Signal(int, str)  # (pct, message)
    finished = Signal()  # emitido tras éxito; NO recibe nada
    failed = Signal(str)  # emitido tras error; mensaje para el user

    def __init__(self: _InstallWorker, service: OcrInstallService) -> None:
        super().__init__()
        self._service = service

    def run(self: _InstallWorker) -> None:
        try:
            self._service.install(lambda pct, msg: self.progress.emit(pct, msg))
        except OcrInstallError as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit()


class _InferenceWorker(QObject):
    """Wrapper de `OcrService.run_inference` para correr en un QThread.

    SQLite no permite compartir `Connection` entre hilos. La firma de
    `run_inference` post-fix recibe `db_path` (no `Connection`) y abre
    su propia conexión internamente — el worker solo le pasa el path.
    """

    finished = Signal(list, list)  # (detections, parse_errors)
    failed = Signal(str)

    def __init__(
        self: _InferenceWorker,
        ocr_service: OcrService,
        image_path: Path,
        db_path: str,
        collection_id: int,
    ) -> None:
        super().__init__()
        self._ocr = ocr_service
        self._image = image_path
        self._db_path = db_path
        self._cid = collection_id

    def run(self: _InferenceWorker) -> None:
        try:
            detections, errors = self._ocr.run_inference(
                self._image,
                db_path=self._db_path,
                collection_id=self._cid,
            )
        except OcrError as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(list(detections), list(errors))


# ======================================================================
# OcrLoaderTab
# ======================================================================


class OcrLoaderTab(QWidget):
    """Tab con los tres estados del flow OCR."""

    card_changed = Signal()

    def __init__(
        self: OcrLoaderTab,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        # Workers + threads viven mientras la tab existe.
        self._install_thread: QThread | None = None
        self._install_worker: _InstallWorker | None = None
        self._inference_thread: QThread | None = None
        self._inference_worker: _InferenceWorker | None = None
        # Estado del flow de carga (Estado 3).
        self._pending_paths: list[Path] = []
        self._current_index: int = 0
        self._current_detections: list[OcrDetection] = []
        self._loaded_count: int = 0
        self._build_ui()
        self._evaluate_state()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: OcrLoaderTab) -> None:
        outer = QVBoxLayout(self)
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_install_page())
        self._stack.addWidget(self._build_no_model_page())
        self._stack.addWidget(self._build_ready_page())
        outer.addWidget(self._stack)

    def _build_install_page(self: OcrLoaderTab) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(
            QLabel(
                self.tr(
                    "Para usar la carga por foto necesitás instalar:\n\n"
                    "• PyTorch (procesamiento de imágenes con IA)  ~800 MB\n"
                    "• Ultralytics YOLO (detección de objetos)        ~50 MB\n\n"
                    "La instalación puede tardar varios minutos."
                )
            )
        )
        self._install_progress = QProgressBar()
        self._install_progress.setRange(0, 100)
        self._install_progress.setVisible(False)
        layout.addWidget(self._install_progress)
        self._install_status_label = QLabel("")
        self._install_status_label.setVisible(False)
        layout.addWidget(self._install_status_label)
        self._install_btn = QPushButton(self.tr("Instalar dependencias"))
        self._install_btn.clicked.connect(self._on_install_clicked)
        layout.addWidget(self._install_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        return page

    def _build_no_model_page(self: OcrLoaderTab) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(QLabel(self.tr("✓ Dependencias instaladas")))
        self._no_model_label = QLabel("")
        self._no_model_label.setWordWrap(True)
        layout.addWidget(self._no_model_label)
        layout.addStretch()
        return page

    def _build_ready_page(self: OcrLoaderTab) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel(
            self.tr(
                "Sacá fotos a los reversos de las figuritas y agregalas. "
                "Te vamos a mostrar las detecciones de cada foto para que "
                "confirmes antes de cargar."
            )
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Botón "Agregar fotos" + lista de fotos pendientes
        top_row = QHBoxLayout()
        self._add_photos_btn = QPushButton(self.tr("Agregar fotos"))
        self._add_photos_btn.clicked.connect(self._on_add_photos_clicked)
        top_row.addWidget(self._add_photos_btn)
        top_row.addStretch()
        layout.addLayout(top_row)

        self._photos_list = QListWidget()
        self._photos_list.setMaximumHeight(80)
        layout.addWidget(self._photos_list)

        # Panel de resultados (oculto al inicio)
        self._results_label = QLabel("")
        self._results_label.setVisible(False)
        layout.addWidget(self._results_label)
        self._results_table = QTableWidget(0, len(_RESULT_HEADERS))
        self._results_table.setHorizontalHeaderLabels(_RESULT_HEADERS)
        self._results_table.setVisible(False)
        header = self._results_table.horizontalHeader()
        header.setSectionResizeMode(_COL_CHECK, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_CODE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_CONF, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._results_table, 1)

        self._summary_label = QLabel("")
        self._summary_label.setVisible(False)
        layout.addWidget(self._summary_label)

        # Botones del flow foto-a-foto
        btn_row = QHBoxLayout()
        self._load_photo_btn = QPushButton(self.tr("Cargar esta foto"))
        self._load_photo_btn.clicked.connect(self._on_load_photo_clicked)
        self._load_photo_btn.setVisible(False)
        self._skip_photo_btn = QPushButton(self.tr("Saltar foto"))
        self._skip_photo_btn.clicked.connect(self._on_skip_photo_clicked)
        self._skip_photo_btn.setVisible(False)
        self._cancel_all_btn = QPushButton(self.tr("Cancelar todo"))
        self._cancel_all_btn.clicked.connect(self._on_cancel_all_clicked)
        self._cancel_all_btn.setVisible(False)
        btn_row.addWidget(self._load_photo_btn)
        btn_row.addWidget(self._skip_photo_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._cancel_all_btn)
        layout.addLayout(btn_row)
        return page

    # ------------------------------------------------------------------
    # API pública (consistencia con otros tabs)
    # ------------------------------------------------------------------

    def set_active_collection(self: OcrLoaderTab, collection: Collection) -> None:
        """Cambia la colección activa y re-evalúa el estado.

        Si había un flow de carga en curso, se cancela: la collection
        cambió y las detecciones del modelo viejo no aplican.
        """
        self._collection = collection
        self._reset_loading_state()
        self._evaluate_state()

    # ------------------------------------------------------------------
    # Evaluación del estado
    # ------------------------------------------------------------------

    def _evaluate_state(self: OcrLoaderTab) -> None:
        """Decide qué página mostrar y prepara los textos dinámicos."""
        if not OcrInstallService.is_installed():
            self._stack.setCurrentIndex(_PAGE_INSTALL)
            return
        ocr = self._get_ocr_service()
        if ocr is None:
            self._no_model_label.setText(
                self.tr(
                    "La colección «{name}» no tiene un modelo OCR "
                    "configurado todavía.\n\n"
                    "Pedile al administrador que lo configure desde "
                    "Administración → Colecciones."
                ).format(name=self._collection.collection_name)
            )
            self._stack.setCurrentIndex(_PAGE_NO_MODEL)
            return
        self._stack.setCurrentIndex(_PAGE_READY)

    def _get_ocr_service(self: OcrLoaderTab) -> OcrService | None:
        """Acceso a la factory del ctx con manejo defensivo.

        Si el ctx no tiene la factory todavía (sesión 5d aún no
        terminada), devolvemos None — la tab se queda en Estado 2.
        """
        getter = getattr(self._ctx, "get_ocr_service", None)
        if getter is None:
            return None
        try:
            return getter(self._collection)
        except OcrError:
            return None

    # ------------------------------------------------------------------
    # Estado 1 — Instalación
    # ------------------------------------------------------------------

    def _on_install_clicked(self: OcrLoaderTab) -> None:
        self._install_btn.setVisible(False)
        self._install_progress.setValue(0)
        self._install_progress.setVisible(True)
        self._install_status_label.setText(self.tr("Iniciando..."))
        self._install_status_label.setVisible(True)

        worker = _InstallWorker(OcrInstallService())
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_install_progress)
        worker.finished.connect(self._on_install_finished)
        worker.failed.connect(self._on_install_failed)
        # Cleanup
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._install_worker = worker
        self._install_thread = thread
        thread.start()

    def _on_install_progress(self: OcrLoaderTab, pct: int, message: str) -> None:
        self._install_progress.setValue(pct)
        self._install_status_label.setText(message)

    def _on_install_finished(self: OcrLoaderTab) -> None:
        self._install_progress.setValue(100)
        self._install_status_label.setText(self.tr("Instalación completada."))
        self._evaluate_state()

    def _on_install_failed(self: OcrLoaderTab, message: str) -> None:
        QMessageBox.critical(
            self,
            self.tr("Error en la instalación"),
            _format_install_error(message),
        )
        self._install_progress.setVisible(False)
        self._install_status_label.setVisible(False)
        self._install_btn.setText(self.tr("Reintentar"))
        self._install_btn.setVisible(True)

    # ------------------------------------------------------------------
    # Estado 3 — Flow foto a foto
    # ------------------------------------------------------------------

    def _on_add_photos_clicked(self: OcrLoaderTab) -> None:
        paths_str, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("Agregar fotos"),
            "",
            self.tr("Imágenes (*.jpg *.jpeg *.png);;Todos los archivos (*)"),
        )
        if not paths_str:
            return
        new_paths = [Path(p) for p in paths_str]
        self._pending_paths.extend(new_paths)
        for p in new_paths:
            QListWidgetItem(p.name, self._photos_list)
        self._add_photos_btn.setEnabled(False)
        self._cancel_all_btn.setVisible(True)
        self._loaded_count = 0
        self._current_index = 0
        self._process_next_photo()

    def _process_next_photo(self: OcrLoaderTab) -> None:
        """Lanza la inferencia para `_pending_paths[_current_index]`."""
        if self._current_index >= len(self._pending_paths):
            self._show_final_summary()
            return
        path = self._pending_paths[self._current_index]
        ocr = self._get_ocr_service()
        if ocr is None:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("El modelo OCR ya no está disponible."),
            )
            self._reset_loading_state()
            self._evaluate_state()
            return

        self._results_label.setText(
            self.tr("Procesando foto {n} de {total}: {name}").format(
                n=self._current_index + 1,
                total=len(self._pending_paths),
                name=path.name,
            )
        )
        self._results_label.setVisible(True)
        self._results_table.setRowCount(0)
        self._results_table.setVisible(False)
        self._summary_label.setVisible(False)
        self._load_photo_btn.setVisible(False)
        self._skip_photo_btn.setVisible(False)

        assert self._collection.collection_id is not None
        worker = _InferenceWorker(
            ocr_service=ocr,
            image_path=path,
            db_path=self._ctx.db_path,
            collection_id=self._collection.collection_id,
        )
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_inference_finished)
        worker.failed.connect(self._on_inference_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._inference_worker = worker
        self._inference_thread = thread
        thread.start()

    def _on_inference_finished(
        self: OcrLoaderTab,
        detections: list[OcrDetection],
        parse_errors: list[OcrParseError],
    ) -> None:
        self._current_detections = detections
        self._populate_results_table(detections)
        # Resumen (detectadas válidas vs labels no parseables / no en catálogo).
        unrecognized = len(parse_errors) + sum(1 for d in detections if d.card_id is None)
        self._summary_label.setText(
            self.tr("Detectadas: {ok} | No reconocidas: ~{bad}").format(
                ok=sum(1 for d in detections if d.card_id is not None),
                bad=unrecognized,
            )
        )
        self._summary_label.setVisible(True)
        self._load_photo_btn.setVisible(True)
        self._skip_photo_btn.setVisible(True)

    def _on_inference_failed(self: OcrLoaderTab, message: str) -> None:
        QMessageBox.critical(self, self.tr("Error en inferencia"), message)
        self._on_skip_photo_clicked()

    def _populate_results_table(self: OcrLoaderTab, detections: list[OcrDetection]) -> None:
        self._results_table.setRowCount(len(detections))
        for row, d in enumerate(detections):
            check = QTableWidgetItem("")
            check.setFlags(check.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            # Pre-marcado si confidence ≥ threshold AND card existe en DB.
            initial = (
                Qt.CheckState.Checked
                if d.confidence >= _CONFIDENCE_THRESHOLD and d.card_id is not None
                else Qt.CheckState.Unchecked
            )
            check.setCheckState(initial)
            self._results_table.setItem(row, _COL_CHECK, check)

            code_text = f"{d.code_id}-{d.card_number}" if d.code_id else str(d.card_number)
            self._results_table.setItem(row, _COL_CODE, QTableWidgetItem(code_text))
            self._results_table.setItem(
                row,
                _COL_NAME,
                QTableWidgetItem(d.card_name or self.tr("(no encontrada)")),
            )
            self._results_table.setItem(
                row,
                _COL_CONF,
                QTableWidgetItem(f"{int(d.confidence * 100)}%"),
            )
        self._results_table.setVisible(True)

    def _on_load_photo_clicked(self: OcrLoaderTab) -> None:
        """Aplica las detecciones tildadas al inventario."""
        applied = 0
        for row, d in enumerate(self._current_detections):
            check = self._results_table.item(row, _COL_CHECK)
            if check is None or check.checkState() != Qt.CheckState.Checked:
                continue
            if d.card_id is None:
                continue
            try:
                assert self._collection.collection_id is not None
                self._ctx.inventory.add_card(
                    self._collection.collection_id,
                    d.code_id,
                    d.card_number,
                    1,
                )
                applied += 1
            except InventoryError as exc:
                QMessageBox.warning(
                    self,
                    self.tr("No se pudo cargar una card"),
                    self.tr("{label}: {msg}").format(label=d.raw_label, msg=exc),
                )
        if applied:
            self._ctx.conn.commit()
            self._loaded_count += applied
            self.card_changed.emit()
        self._current_index += 1
        self._process_next_photo()

    def _on_skip_photo_clicked(self: OcrLoaderTab) -> None:
        self._current_index += 1
        self._process_next_photo()

    def _on_cancel_all_clicked(self: OcrLoaderTab) -> None:
        confirm = QMessageBox.question(
            self,
            self.tr("Cancelar carga"),
            self.tr("¿Cancelar la carga? Las fotos ya cargadas se mantienen."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._show_final_summary()

    def _show_final_summary(self: OcrLoaderTab) -> None:
        processed = self._current_index
        QMessageBox.information(
            self,
            self.tr("Carga terminada"),
            self.tr("Cargaste {n} cards de {p} fotos procesadas.").format(
                n=self._loaded_count, p=processed
            ),
        )
        self._reset_loading_state()

    def _reset_loading_state(self: OcrLoaderTab) -> None:
        self._pending_paths.clear()
        self._photos_list.clear()
        self._current_index = 0
        self._current_detections = []
        self._loaded_count = 0
        self._results_label.setVisible(False)
        self._results_table.setRowCount(0)
        self._results_table.setVisible(False)
        self._summary_label.setVisible(False)
        self._load_photo_btn.setVisible(False)
        self._skip_photo_btn.setVisible(False)
        self._cancel_all_btn.setVisible(False)
        self._add_photos_btn.setEnabled(True)
