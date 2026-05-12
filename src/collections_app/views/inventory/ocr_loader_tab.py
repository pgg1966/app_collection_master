"""Tab "Por foto" — carga de inventario por reconocimiento óptico (Sesión 5d).

Tres estados, vivientes en un `QStackedWidget`:

1. Sin dependencias (torch/ultralytics) instaladas → mensaje + botón
   para instalarlas. La instalación corre en `QThread` y emite
   progreso. Al terminar se re-evalúa el estado.
2. Dependencias OK pero la colección no tiene modelo configurado →
   mensaje "pedile al admin que configure el modelo".
3. Listo → botón "Agregar fotos" que abre un file picker, lista de
   fotos pendientes y un progress bar. Después de cada inferencia se
   abre `OcrResultDialog` (foto anotada + tabla); los 3 botones del
   flow viven en el diálogo.

Re-evaluación: en `__init__`, después de instalar exitosamente, y
cuando cambia la collection vía `set_active_collection`.

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

import sys
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


# ======================================================================
# Workers de QThread
# ======================================================================


class _InstallWorker(QObject):
    """Wrapper de `OcrInstallService.install` para correr en un QThread."""

    progress = Signal(int, str)  # (pct, message)
    finished = Signal(str)  # emitido tras éxito; payload = python_exe usado
    failed = Signal(str)  # emitido tras error; mensaje para el user

    def __init__(self: _InstallWorker, service: OcrInstallService) -> None:
        super().__init__()
        self._service = service

    def run(self: _InstallWorker) -> None:
        try:
            python_exe = self._service.install(lambda pct, msg: self.progress.emit(pct, msg))
        except OcrInstallError as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(python_exe)


class _CheckInstallWorker(QThread):
    """Verifica `OcrInstallService.is_installed()` en un hilo aparte.

    En el bundle PyInstaller, `is_installed()` lanza un subprocess al
    Python del sistema y puede tardar varios segundos (importlib.util
    find_spec sobre torch en un Python "frio" con AV scanning). Correr
    eso en el main thread congela la UI durante todo ese tiempo, asi
    que lo movemos a un QThread.

    Hereda directo de QThread (no QObject + moveToThread) porque el
    payload es pequeno (un bool) y no necesitamos cleanup elaborado.
    """

    result = Signal(bool)

    def __init__(
        self: _CheckInstallWorker,
        parent: QObject | None,
        python_exe_hint: str | None,
    ) -> None:
        super().__init__(parent)
        self._hint = python_exe_hint

    def run(self: _CheckInstallWorker) -> None:
        self.result.emit(OcrInstallService.is_installed(python_exe=self._hint))


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
        # Check async (bundle PyInstaller): worker temporal, vive solo
        # durante el subprocess. Se autodestruye con deleteLater.
        self._check_worker: _CheckInstallWorker | None = None
        # Estado del flow de carga (Estado 3).
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

        En el **bundle PyInstaller** la check delega a un subprocess al
        Python del sistema (puede tardar varios segundos por carga de
        DLLs nativas si torch/cv2 estan instalados). Para no congelar
        la UI, el check se hace en un `_CheckInstallWorker` y la
        continuación vive en `_on_install_check_done`. Durante esos
        segundos la tab queda en el _PAGE_INSTALL: si la check da True
        transiciona, si da False se queda — mismo estado terminal que
        antes.

        En **desarrollo** (no frozen) el check es un import directo:
        rapido y sincronico, sin worker.
        """
        if not getattr(sys, "frozen", False):
            self._on_install_check_done(OcrInstallService.is_installed())
            return

        # Bundle: check async. Mientras tanto, _PAGE_INSTALL.
        self._stack.setCurrentIndex(_PAGE_INSTALL)
        hint = self._read_python_exe_hint()
        worker = _CheckInstallWorker(self, python_exe_hint=hint)
        worker.result.connect(self._on_install_check_done)
        worker.finished.connect(worker.deleteLater)
        self._check_worker = worker
        worker.start()

    def _on_install_check_done(self: OcrLoaderTab, installed: bool) -> None:
        """Continuacion de `_evaluate_state` tras el check (sync o async)."""
        if not installed:
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
        self._refresh_guide_image()
        self._stack.setCurrentIndex(_PAGE_READY)

    def _read_python_exe_hint(self: OcrLoaderTab) -> str | None:
        """Lee el `python_exe` que uso `install()` exitoso, si existe."""
        setting = self._ctx.settings.get("ocr_python_exe")
        return setting.value if setting else None

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

    def _on_install_finished(self: OcrLoaderTab, python_exe: str) -> None:
        """Slot del signal `finished` del `_InstallWorker`.

        Persiste el `python_exe` que se uso en `install()` (asi
        `is_installed()` futuros consultan el mismo Python sin depender
        del PATH del shell) y re-evalua el estado para que la tab
        transicione al Estado 2 (sin modelo) o Estado 3 (listo).
        """
        self._install_progress.setValue(100)
        self._install_status_label.setText(self.tr("Instalación completada."))
        self._ctx.settings.set("ocr_python_exe", python_exe)
        self._ctx.conn.commit()
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
