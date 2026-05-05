"""Dialog modal con preview de un PDF generado en archivo temporal.

Flujo del usuario:
  1. Click en un botón de "Generar PDF" en cualquier vista.
  2. La vista invoca el worker que genera el PDF en `%TEMP%`.
  3. Cuando el worker termina, instancia este dialog con el path temp.
  4. El usuario ve el PDF y decide:
     - "Guardar..." → QFileDialog → copia a destino → opción de abrir.
     - "Cancelar"   → borra el temp, no se guarda nada.

Si PySide6 fue compilado sin QtPdf/QtPdfWidgets (versiones viejas),
el dialog cae a un mensaje informativo: el usuario igual puede guardar
y abrir con su visor habitual.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class PdfPreviewDialog(QDialog):
    """Preview de un PDF antes de guardarlo a una ubicación final.

    `temp_pdf_path` es un archivo en `%TEMP%` que el dialog se hace
    cargo de borrar (en cancel o tras copiar al destino). Si el usuario
    cierra el dialog con la X también se limpia.
    """

    def __init__(
        self,
        temp_pdf_path: Path,
        suggested_filename: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Vista previa del PDF"))
        self.setMinimumSize(720, 820)
        self.setModal(True)

        self._temp_path = temp_pdf_path
        self._suggested_filename = suggested_filename
        self._saved_path: Path | None = None
        self._cleanup_done = False

        self._build_ui()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def saved_path(self) -> Path | None:
        """Path donde se guardó el PDF, o `None` si el usuario canceló."""
        return self._saved_path

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # Área de preview — QPdfView si está disponible, fallback si no.
        layout.addWidget(self._build_preview_area(), stretch=1)

        # Botones inferiores
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton(self.tr("Cancelar"))
        btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton(self.tr("Guardar…"))
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _build_preview_area(self) -> QWidget:
        """Intenta crear un QPdfView; cae a QLabel informativo si no está.

        Carga el PDF a memoria via `QBuffer` en vez de pasarle el path
        a `QPdfDocument`. Razón: en Windows, `QPdfDocument.load(path)`
        mantiene un mmap sobre el archivo que sobrevive a `close()` y
        bloquea el `unlink(temp)` posterior. Cargando bytes en memoria
        no se toca el filesystem después de la lectura inicial.
        """
        try:
            from PySide6.QtCore import QBuffer, QByteArray
            from PySide6.QtPdf import QPdfDocument
            from PySide6.QtPdfWidgets import QPdfView
        except ImportError:
            return self._build_fallback_label()

        try:
            data = self._temp_path.read_bytes()
        except OSError as exc:
            logger.warning("No se pudo leer temp %s: %s", self._temp_path, exc)
            return self._build_fallback_label()

        try:
            self._pdf_buffer = QBuffer(self)
            self._pdf_buffer.setData(QByteArray(data))
            self._pdf_buffer.open(QBuffer.OpenModeFlag.ReadOnly)
            self._pdf_doc = QPdfDocument(self)
            self._pdf_doc.load(self._pdf_buffer)
            self._pdf_view = QPdfView(self)
            self._pdf_view.setDocument(self._pdf_doc)
            self._pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            return self._pdf_view
        except Exception:  # noqa: BLE001
            logger.exception("Fallo al construir QPdfView para %s", self._temp_path)
            return self._build_fallback_label()

    def _build_fallback_label(self) -> QLabel:
        label = QLabel(
            self.tr(
                "Vista previa no disponible en esta versión.\n"
                "Guardá el PDF y abrilo con tu visor habitual."
            )
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-size: 11pt;")
        label.setWordWrap(True)
        return label

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        default_dir = Path.home() / "Documents"
        if not default_dir.exists():
            default_dir = Path.home()
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar PDF"),
            str(default_dir / self._suggested_filename),
            self.tr("PDF (*.pdf)"),
        )
        if not path_str:
            # Usuario canceló el dialog de guardar — volver al preview,
            # NO cerrar el dialog ni borrar el temp.
            return

        dest = Path(path_str)
        try:
            shutil.copy2(self._temp_path, dest)
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error al guardar"),
                self.tr("No se pudo guardar el PDF:\n{e}").format(e=exc),
            )
            return

        self._saved_path = dest
        self._delete_temp()
        # Cerrar el visor antes de mostrar el QMessageBox: en Windows
        # QPdfDocument bloquea el archivo origen y queremos que queden
        # libres ambos archivos por si el usuario abre el destino.
        self._release_pdf_view()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(self.tr("PDF guardado"))
        msg.setText(self.tr("PDF guardado en:\n{p}").format(p=str(dest)))
        msg.addButton(self.tr("OK"), QMessageBox.ButtonRole.AcceptRole)
        btn_open = msg.addButton(self.tr("Abrir"), QMessageBox.ButtonRole.ActionRole)
        msg.exec()

        if msg.clickedButton() is btn_open:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)))

        self.accept()

    def _on_cancel(self) -> None:
        self._release_pdf_view()
        self._delete_temp()
        self.reject()

    # closeEvent llama _release_pdf_view antes de _delete_temp también
    # (ver más abajo). Mantenemos las dos rutas (Cancelar / X) coherentes.

    def _release_pdf_view(self) -> None:
        """Cierra QPdfDocument y libera el archivo (Windows lock).

        En Windows, QPdfDocument mantiene un mmap sobre el archivo que
        sobrevive a `close()`. Para liberar el handle hay que destruir
        el QObject — usamos `deleteLater()` + processEvents para que
        Qt drene la cola de destrucción. Sin esto, `unlink(temp)` falla
        silenciosamente.
        """
        view = getattr(self, "_pdf_view", None)
        if view is not None:
            try:
                view.setDocument(None)
            except Exception:  # noqa: BLE001
                logger.debug("QPdfView.setDocument(None) falló (no crítico)")
        doc = getattr(self, "_pdf_doc", None)
        if doc is not None:
            try:
                doc.close()
                doc.deleteLater()
            except Exception:  # noqa: BLE001
                logger.debug("QPdfDocument cleanup falló (no crítico)")
            # Borramos el atributo del instance para que mypy no se queje
            # del re-asignamiento a None sobre un slot tipado.
            try:
                delattr(self, "_pdf_doc")
            except AttributeError:
                pass
        # Drenar la cola de deleteLater + IO pendiente.
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            app.processEvents()

    def _delete_temp(self) -> None:
        if self._cleanup_done:
            return
        try:
            self._temp_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.debug("No se pudo borrar temp %s: %s", self._temp_path, exc)
        self._cleanup_done = True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        """Si el usuario cierra con la X o Escape, también limpiar."""
        if self._saved_path is None:
            self._release_pdf_view()
            self._delete_temp()
        super().closeEvent(event)
