"""Tab "Por foto" — carga de inventario por reconocimiento óptico.

Dos estados, vivientes en un `QStackedWidget`:

1. **No-model**: deps OCR OK (torch+cv2+etc. están en el bundle) pero
   el modelo `.pt` no se puede usar. Dos sub-variantes:
   - Modelo configurado en DB pero archivo no en disco → botón
     "Descargar modelo" que baja `.pt` + guía desde GitHub Releases.
   - Modelo no configurado en DB → mensaje "pedile al admin".
2. **Ready**: modelo presente. Botón "Agregar fotos" que abre un file
   picker, lista de fotos pendientes y un progress bar. Tras cada
   inferencia se abre `OcrResultDialog` (foto anotada + tabla); los
   3 botones del flow viven en el diálogo.

Re-evaluación: en `__init__`, después de descargar el modelo, y cuando
cambia la collection vía `set_active_collection`.

Inferencia: cada foto se procesa en un `QThread` para no bloquear la
UI. El service se obtiene del `AppContext` vía
`ctx.get_ocr_service(collection)` (factory, devuelve `None` si no
está disponible).

Apply: las cards tildadas en el diálogo se aplican vía
`inventory_service.add_card` por cada detección. Tras aplicar la
última foto se emite `card_changed` para que el resto de los tabs se
refresque.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exceptions import (
    InventoryError,
    OcrError,
    OcrInstallError,
)
from collections_app.services.ocr_install_service import OcrInstallService
from collections_app.views.inventory._scaled_image_label import ScaledImageLabel
from collections_app.views.inventory.ocr_result_dialog import OcrResultDialog

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection
    from collections_app.core.models.ocr_detection import OcrDetection, OcrParseError
    from collections_app.services.ocr_service import OcrService


_PAGE_NO_MODEL = 0
_PAGE_READY = 1


# ======================================================================
# Workers de QThread
# ======================================================================


class _DownloadOnlyWorker(QThread):
    """Wrapper de `OcrInstallService.download_ocr_assets` en QThread.

    Para el flow "Descargar modelo" del Estado No-Model variante B: el
    modelo está configurado en DB pero falta en disco. Este worker baja
    modelo + guía desde GitHub Releases sin bloquear la UI.
    """

    progress = Signal(int, str)
    finished = Signal()
    failed = Signal(str)

    def __init__(
        self: _DownloadOnlyWorker,
        parent: QObject | None,
        service: OcrInstallService,
    ) -> None:
        super().__init__(parent)
        self._service = service

    def run(self: _DownloadOnlyWorker) -> None:
        try:
            self._service.download_ocr_assets(lambda pct, msg: self.progress.emit(pct, msg))
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
    """Tab con los dos estados del flow OCR."""

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
        self._inference_thread: QThread | None = None
        self._inference_worker: _InferenceWorker | None = None
        # Worker de descarga del modelo (botón "Descargar modelo" del
        # Estado No-Model variante B).
        self._download_worker: _DownloadOnlyWorker | None = None
        # Estado del flow de carga (Estado Ready).
        self._pending_paths: list[Path] = []
        self._current_index: int = 0
        self._loaded_count: int = 0
        self._build_ui()
        self._evaluate_state()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: OcrLoaderTab) -> None:
        outer = QVBoxLayout(self)
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_no_model_page())
        self._stack.addWidget(self._build_ready_page())
        outer.addWidget(self._stack)

    def _build_no_model_page(self: OcrLoaderTab) -> QWidget:
        """Estado No-Model: el OCR no está listo para correr.

        Dos sub-variantes (ver `_show_no_model_state`):
        - **Variante B** (modelo en DB pero no en disco): muestra el
          botón "Descargar modelo" + barra de progreso. Click dispara
          `_DownloadOnlyWorker` que baja `ocr_1.pt` + `ocr_guide_1.jpg`
          de GitHub Releases.
        - **Variante A** (modelo no configurado): muestra mensaje
          "pedile al admin". El botón queda oculto.

        Las visibilidades concretas se setean en `_show_no_model_state`
        según la variante. Acá solo construimos los widgets, ocultos.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._no_model_label = QLabel("")
        self._no_model_label.setWordWrap(True)
        layout.addWidget(self._no_model_label)

        self._download_model_btn = QPushButton(self.tr("Descargar modelo"))
        self._download_model_btn.clicked.connect(self._on_download_model_clicked)
        self._download_model_btn.setVisible(False)
        layout.addWidget(self._download_model_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self._download_progress = QProgressBar()
        self._download_progress.setRange(0, 100)
        self._download_progress.setVisible(False)
        layout.addWidget(self._download_progress)

        self._download_status = QLabel("")
        self._download_status.setVisible(False)
        layout.addWidget(self._download_status)

        layout.addStretch()
        return page

    def _build_ready_page(self: OcrLoaderTab) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        # Imagen de guía OCR — visible solo si la colección tiene una
        # configurada. Se inicializa con un placeholder vacío y se
        # actualiza en `_refresh_guide_image()` (también llamado desde
        # set_active_collection cuando cambia la colección).
        self._guide_image = ScaledImageLabel(
            QPixmap(), parent=page, minimum_width=200, minimum_height=120
        )
        self._guide_image.setMaximumHeight(250)
        self._guide_image.setVisible(False)
        layout.addWidget(self._guide_image)

        intro = QLabel(
            self.tr(
                "Sacá fotos como se indica en el modelo.\n"
                "Podés agregar varias fotos a la vez.\n"
                "Las cartas no reconocidas se pueden cargar manualmente."
            )
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        top_row = QHBoxLayout()
        self._add_photos_btn = QPushButton(self.tr("Agregar fotos"))
        self._add_photos_btn.clicked.connect(self._on_add_photos_clicked)
        top_row.addWidget(self._add_photos_btn)
        top_row.addStretch()
        layout.addLayout(top_row)

        self._photos_list = QListWidget()
        self._photos_list.setMaximumHeight(80)
        layout.addWidget(self._photos_list)

        # Estado del procesamiento (oculto cuando no hay flow activo).
        self._status_label = QLabel("")
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._summary_label = QLabel("")
        self._summary_label.setVisible(False)
        layout.addWidget(self._summary_label)

        layout.addStretch(1)
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
        """Decide qué página mostrar.

        Con torch incluido en el bundle (Prompt 7e), las deps OCR
        siempre están disponibles — ya no hace falta un Estado 1 de
        instalación. Solo queda chequear si el modelo `.pt` puede
        cargarse: si sí → Estado Ready; si no → Estado No-Model con la
        variante A o B según corresponda.
        """
        ocr = self._get_ocr_service()
        if ocr is None:
            self._show_no_model_state()
            return
        self._refresh_guide_image()
        self._stack.setCurrentIndex(_PAGE_READY)

    def _show_no_model_state(self: OcrLoaderTab) -> None:
        """Configura el contenido del Estado No-Model según la sub-variante."""
        has_model_in_db = bool(self._collection.ocr_model_filename)
        model_on_disk_getter = getattr(self._ctx, "get_ocr_model_path", None)
        model_path = (
            model_on_disk_getter(self._collection) if model_on_disk_getter is not None else None
        )
        needs_download = has_model_in_db and model_path is None

        if needs_download:
            self._no_model_label.setText(
                self.tr(
                    "El modelo OCR está configurado pero no está descargado "
                    "todavía.\n\nClick en «Descargar modelo» para bajarlo."
                )
            )
            self._download_model_btn.setVisible(True)
            self._download_model_btn.setEnabled(True)
            self._download_model_btn.setText(self.tr("Descargar modelo"))
        else:
            self._no_model_label.setText(
                self.tr(
                    "La colección «{name}» no tiene un modelo OCR "
                    "configurado todavía.\n\n"
                    "Pedile al administrador que lo configure desde "
                    "Administración → Colecciones."
                ).format(name=self._collection.collection_name)
            )
            self._download_model_btn.setVisible(False)
        # Reset de progreso por si quedaron visibles de un intento previo.
        self._download_progress.setVisible(False)
        self._download_progress.setValue(0)
        self._download_status.setVisible(False)
        self._stack.setCurrentIndex(_PAGE_NO_MODEL)

    def _refresh_guide_image(self: OcrLoaderTab) -> None:
        """Actualiza la imagen de guía OCR si la colección tiene una.

        Si `ctx.get_ocr_guide_path(collection)` devuelve `None` (sin
        filename configurado o archivo no existe en disco), oculta el
        widget. Si devuelve un path válido, carga el QPixmap y lo
        muestra.
        """
        getter = getattr(self._ctx, "get_ocr_guide_path", None)
        guide_path = getter(self._collection) if getter is not None else None
        if guide_path is None:
            self._guide_image.setVisible(False)
            return
        pix = QPixmap(str(guide_path))
        if pix.isNull():
            self._guide_image.setVisible(False)
            return
        self._guide_image.set_original_pixmap(pix)
        self._guide_image.setVisible(True)

    def _get_ocr_service(self: OcrLoaderTab) -> OcrService | None:
        """Acceso a la factory del ctx con manejo defensivo."""
        getter = getattr(self._ctx, "get_ocr_service", None)
        if getter is None:
            return None
        try:
            return getter(self._collection)
        except OcrError:
            return None

    # ------------------------------------------------------------------
    # Estado No-Model — Solo descarga del modelo
    # ------------------------------------------------------------------

    def _on_download_model_clicked(self: OcrLoaderTab) -> None:
        """Lanza la descarga standalone del modelo + guía OCR."""
        self._download_model_btn.setEnabled(False)
        self._download_model_btn.setText(self.tr("Descargando..."))
        self._download_progress.setValue(0)
        self._download_progress.setVisible(True)
        self._download_status.setText(self.tr("Iniciando descarga..."))
        self._download_status.setVisible(True)

        worker = _DownloadOnlyWorker(self, OcrInstallService())
        worker.progress.connect(self._on_download_progress)
        worker.finished.connect(self._on_download_finished)
        worker.failed.connect(self._on_download_failed)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        self._download_worker = worker
        worker.start()

    def _on_download_progress(self: OcrLoaderTab, pct: int, message: str) -> None:
        self._download_progress.setValue(pct)
        self._download_status.setText(message)

    def _on_download_finished(self: OcrLoaderTab) -> None:
        """Descarga OK: re-evalua estado (debe transicionar a Estado Ready)."""
        self._download_progress.setValue(100)
        self._download_status.setText(self.tr("Descarga completada."))
        self._evaluate_state()

    def _on_download_failed(self: OcrLoaderTab, message: str) -> None:
        QMessageBox.critical(
            self,
            self.tr("Error en la descarga"),
            message,
        )
        self._download_progress.setVisible(False)
        self._download_status.setVisible(False)
        self._download_model_btn.setEnabled(True)
        self._download_model_btn.setText(self.tr("Reintentar descarga"))

    # ------------------------------------------------------------------
    # Estado Ready — Flow foto a foto
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
        self._summary_label.setVisible(False)
        self._progress_bar.setRange(0, len(self._pending_paths))
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
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

        self._status_label.setText(
            self.tr("Procesando foto {n} de {total}: {name}").format(
                n=self._current_index + 1,
                total=len(self._pending_paths),
                name=path.name,
            )
        )
        self._status_label.setVisible(True)
        self._progress_bar.setValue(self._current_index)

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
        """Abre el diálogo de verificación y despacha según la salida."""
        path = self._pending_paths[self._current_index]
        dialog = OcrResultDialog(
            image_path=path,
            detections=detections,
            errors=parse_errors,
            photo_index=self._current_index,
            total_photos=len(self._pending_paths),
            ctx=self._ctx,
            collection=self._collection,
            parent=self,
        )
        dialog.exec()
        if dialog.cancel_all:
            self._show_final_summary()
            return
        if not dialog.skip:
            self._apply_detections(dialog.selected_detections())
        self._current_index += 1
        self._progress_bar.setValue(self._current_index)
        self._process_next_photo()

    def _on_inference_failed(self: OcrLoaderTab, message: str) -> None:
        QMessageBox.critical(self, self.tr("Error en inferencia"), message)
        # Saltar la foto fallida y seguir.
        self._current_index += 1
        self._progress_bar.setValue(self._current_index)
        self._process_next_photo()

    def _apply_detections(self: OcrLoaderTab, detections: list[OcrDetection]) -> None:
        """Aplica las detecciones marcadas en el diálogo al inventario."""
        applied = 0
        for d in detections:
            if d.card_id is None:
                # Card no está en el catálogo local: no podemos imputar
                # inventario aunque el user la haya dejado tildada.
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

    def _show_final_summary(self: OcrLoaderTab) -> None:
        processed = self._current_index
        self._status_label.setVisible(False)
        self._progress_bar.setVisible(False)
        self._summary_label.setText(
            self.tr("Cargaste {n} cards de {p} fotos procesadas.").format(
                n=self._loaded_count, p=processed
            )
        )
        self._summary_label.setVisible(True)
        QMessageBox.information(
            self,
            self.tr("Carga terminada"),
            self._summary_label.text(),
        )
        self._reset_loading_state(keep_summary=True)

    def _reset_loading_state(self: OcrLoaderTab, *, keep_summary: bool = False) -> None:
        self._pending_paths.clear()
        self._photos_list.clear()
        self._current_index = 0
        self._loaded_count = 0
        self._status_label.setVisible(False)
        self._progress_bar.setVisible(False)
        if not keep_summary:
            self._summary_label.setVisible(False)
        self._add_photos_btn.setEnabled(True)
