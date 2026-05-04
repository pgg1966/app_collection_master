"""Tab Comparar Álbumes: genera/importa archivos .colexchange y compara.

Flujo del usuario:
1. "Generar archivo .colexchange" → guarda los faltantes/repetidas propios
   en un archivo y lo comparte con el otro usuario (mail, WhatsApp, etc.).
2. "Importar archivo del otro usuario" → carga el archivo del compañero,
   valida checksum, y dispara la comparación automáticamente.
3. Las dos grillas muestran el resultado: "Me hacen falta" / "Puedo ofrecer".
4. "Generar PDF" produce un PDF con ambas listas (con metadata embebida).
5. "Ejecutar intercambio" abre el `ExchangeView` (dialog modal) que
   bloquea las cartas en inventario hasta confirmar/cancelar.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.client.views.exchange_view import ExchangeView
from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Collection,
    ComparisonResult,
    ExchangeFile,
)
from collections_app.core.repositories import CodesLinesRepository
from collections_app.core.services import (
    EXCHANGE_EXTENSION,
    ExchangeService,
    PdfGeneratorResult,
)
from collections_app.core.services.pdf_generator import generate_comparison_pdf
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Workers (cada uno abre su propia conexión a la DB — NO compartir)
# ----------------------------------------------------------------------


class _GenerateFileWorker(QThread):
    """Genera el archivo .colexchange en thread separado."""

    finished_ok = Signal(object)  # ExchangeFile
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        output_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._output_path = output_path

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                ef = ExchangeService(conn).generate_exchange_file(
                    self._collection_id, self._output_path
                )
            finally:
                conn.close()
            self.finished_ok.emit(ef)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando archivo de comparación")
            self.failed.emit(str(exc))


class _ComparisonPdfWorker(QThread):
    """Genera el PDF de comparación en thread separado."""

    finished_ok = Signal(object)  # PdfGeneratorResult
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection: Collection,
        result: ComparisonResult,
        output_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection = collection
        self._result = result
        self._output_path = output_path

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                code_names = {
                    line.code_id: line.code_name
                    for line in CodesLinesRepository(conn).list_by_header(
                        self._collection.code_header_id
                    )
                }
                result = generate_comparison_pdf(
                    self._collection,
                    code_names,
                    self._result.i_need,
                    self._result.i_can_offer,
                    self._output_path,
                )
            finally:
                conn.close()
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando PDF de comparación")
            if self._output_path.exists():
                self._output_path.unlink(missing_ok=True)
            self.failed.emit(str(exc))


# ----------------------------------------------------------------------
# View principal
# ----------------------------------------------------------------------


class CompareView(QWidget):
    """Tab principal del módulo Comparar."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: Path,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._db_path = db_path
        self.collection = collection

        self._other_file: ExchangeFile | None = None
        self._comparison: ComparisonResult | None = None
        self._gen_worker: _GenerateFileWorker | None = None
        self._pdf_worker: _ComparisonPdfWorker | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        """Cambio de colección: limpiar estado para evitar comparar datos cruzados."""
        self.collection = collection
        self._other_file = None
        self._comparison = None
        self._other_status_label.setText(self.tr("Ninguno cargado"))
        self._i_need_list.clear()
        self._i_offer_list.clear()
        self._update_action_buttons()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        outer.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Comparar Álbumes"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        outer.addWidget(title)

        outer.addWidget(self._build_steps_section())
        outer.addWidget(self._build_results_section(), stretch=1)
        outer.addLayout(self._build_actions_row())

        self._update_action_buttons()

    def _build_steps_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.SM)

        # Paso 1
        step1 = QLabel(
            "<b>" + self.tr("Paso 1") + "</b>: " + self.tr("Generar mi archivo de comparación")
        )
        layout.addWidget(step1)
        row1 = QHBoxLayout()
        self._gen_button = QPushButton(self.tr("Generar archivo .colexchange"))
        self._gen_button.clicked.connect(self._on_generate_file)
        row1.addWidget(self._gen_button)
        self._gen_status_label = QLabel("")
        self._gen_status_label.setWordWrap(True)
        row1.addWidget(self._gen_status_label, stretch=1)
        layout.addLayout(row1)

        # Paso 2
        step2 = QLabel(
            "<b>" + self.tr("Paso 2") + "</b>: " + self.tr("Importar archivo del otro usuario")
        )
        layout.addWidget(step2)
        row2 = QHBoxLayout()
        self._import_button = QPushButton(self.tr("Importar archivo .colexchange"))
        self._import_button.clicked.connect(self._on_import_file)
        row2.addWidget(self._import_button)
        self._other_status_label = QLabel(self.tr("Ninguno cargado"))
        row2.addWidget(self._other_status_label, stretch=1)
        layout.addLayout(row2)

        return frame

    def _build_results_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        outer = QVBoxLayout(frame)
        outer.setSpacing(Spacing.SM)

        row = QHBoxLayout()
        # Columna izquierda: me hacen falta
        left = QVBoxLayout()
        self._i_need_title = QLabel("<b>" + self.tr("Me hacen falta") + "</b>")
        left.addWidget(self._i_need_title)
        self._i_need_list = QListWidget()
        left.addWidget(self._i_need_list)

        # Columna derecha: puedo ofrecer
        right = QVBoxLayout()
        self._i_offer_title = QLabel("<b>" + self.tr("Puedo ofrecer") + "</b>")
        right.addWidget(self._i_offer_title)
        self._i_offer_list = QListWidget()
        right.addWidget(self._i_offer_list)

        row.addLayout(left, stretch=1)
        row.addLayout(right, stretch=1)
        outer.addLayout(row)
        return frame

    def _build_actions_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self._pdf_button = QPushButton(self.tr("Generar PDF comparación"))
        self._pdf_button.clicked.connect(self._on_generate_pdf)
        self._exec_button = QPushButton(self.tr("Ejecutar intercambio"))
        self._exec_button.clicked.connect(self._on_execute_exchange)
        row.addWidget(self._pdf_button)
        row.addWidget(self._exec_button)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_generate_file(self) -> None:
        # Default: ~/Downloads (fallback a ~ si no existe — cuentas nuevas
        # de Windows o sistemas Linux mínimos pueden no tenerla).
        default_dir = Path.home() / "Downloads"
        if not default_dir.exists():
            default_dir = Path.home()

        date = datetime.now().strftime("%Y-%m-%d")
        # Sanitizar el nombre de la colección para que sea filename-safe:
        # mantener alfanuméricos, espacios, guiones y _; reemplazar el resto.
        safe_name = (
            "".join(
                ch if ch.isalnum() or ch in " _-" else "_" for ch in self.collection.collection_name
            )
            .strip()
            .replace(" ", "_")
        )
        default_name = f"MiAlbum_{safe_name}_{date}{EXCHANGE_EXTENSION}"
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar archivo de comparación"),
            str(default_dir / default_name),
            self.tr("CollectionsApp Exchange (*{ext})").format(ext=EXCHANGE_EXTENSION),
        )
        if not path_str:
            return
        out = Path(path_str)
        if out.suffix != EXCHANGE_EXTENSION:
            out = out.with_suffix(EXCHANGE_EXTENSION)

        self._gen_button.setEnabled(False)
        self._gen_status_label.setText(self.tr("Generando…"))
        self._gen_status_label.setStyleSheet("")

        assert self.collection.collection_id is not None
        worker = _GenerateFileWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            output_path=out,
            parent=self,
        )
        self._gen_worker = worker

        def on_ok(_ef: object) -> None:
            self._gen_button.setEnabled(True)
            self._gen_status_label.setText(self.tr("✓ Archivo generado en: {p}").format(p=str(out)))
            self._gen_status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")

        def on_failed(msg: str) -> None:
            self._gen_button.setEnabled(True)
            self._gen_status_label.setText(self.tr("Error: {m}").format(m=msg))
            self._gen_status_label.setStyleSheet(f"color: {StatusColor.ERROR};")

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _on_import_file(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar archivo de comparación"),
            "",
            self.tr("CollectionsApp Exchange (*{ext})").format(ext=EXCHANGE_EXTENSION),
        )
        if not path_str:
            return
        path = Path(path_str)

        try:
            other = ExchangeService(self.conn).load_exchange_file(path)
        except ValueError as exc:
            QMessageBox.warning(
                self,
                self.tr("Archivo inválido"),
                str(exc),
            )
            return

        if other.collection_id != self.collection.collection_id:
            QMessageBox.warning(
                self,
                self.tr("Colección distinta"),
                self.tr(
                    'El archivo es de la colección "{name}" (id={id}) — '
                    'no coincide con la activa ("{active}").'
                ).format(
                    name=other.collection_name,
                    id=other.collection_id,
                    active=self.collection.collection_name,
                ),
            )
            return

        self._other_file = other
        self._other_status_label.setText(
            self.tr("✓ {n} faltantes / {d} repetidas").format(
                n=len(other.missing), d=len(other.duplicates)
            )
        )
        self._other_status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")
        self._run_comparison()

    def _run_comparison(self) -> None:
        """Genera mi snapshot in-memory y compara con el otro archivo."""
        if self._other_file is None:
            return

        # Snapshot propio in-memory (sin escribir a disco). Usamos un
        # path temporal que borramos enseguida — la API actual escribe
        # siempre, pero el costo es despreciable.
        import tempfile

        assert self.collection.collection_id is not None
        with tempfile.NamedTemporaryFile(suffix=EXCHANGE_EXTENSION, delete=False) as tf:
            tmp_path = Path(tf.name)
        try:
            svc = ExchangeService(self.conn)
            my_file = svc.generate_exchange_file(self.collection.collection_id, tmp_path)
            self._comparison = svc.compare(my_file, self._other_file)
        finally:
            tmp_path.unlink(missing_ok=True)

        self._populate_results()
        self._update_action_buttons()

    def _populate_results(self) -> None:
        self._i_need_list.clear()
        self._i_offer_list.clear()
        if self._comparison is None:
            return

        self._i_need_title.setText(
            "<b>" + self.tr("Me hacen falta") + f" ({len(self._comparison.i_need)})</b>"
        )
        self._i_offer_title.setText(
            "<b>" + self.tr("Puedo ofrecer") + f" ({len(self._comparison.i_can_offer)})</b>"
        )

        for card in self._comparison.i_need:
            self._i_need_list.addItem(QListWidgetItem(self._format_card(card, with_qty=False)))
        for card in self._comparison.i_can_offer:
            self._i_offer_list.addItem(
                QListWidgetItem(self._format_card(card, with_qty=card.quantity > 1))
            )

    def _format_card(self, card: object, with_qty: bool) -> str:
        from collections_app.core.models import ExchangeCard

        assert isinstance(card, ExchangeCard)
        if self.collection.requires_code:
            label = f"{card.code_id}-{card.card_number}"
        else:
            label = str(card.card_number)
        text = f"{label:<10} {card.card_name}"
        if with_qty and card.quantity > 1:
            text += f"  ×{card.quantity}"
        return text

    def _update_action_buttons(self) -> None:
        has_result = self._comparison is not None
        self._pdf_button.setEnabled(has_result)
        # Ejecutar intercambio: solo si hay AL MENOS una carta para
        # intercambiar (en cualquiera de las dos direcciones).
        has_cards = has_result and (
            len(self._comparison.i_need) > 0  # type: ignore[union-attr]
            or len(self._comparison.i_can_offer) > 0  # type: ignore[union-attr]
        )
        self._exec_button.setEnabled(has_cards)

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------

    def _on_generate_pdf(self) -> None:
        if self._comparison is None:
            return
        date = datetime.now().strftime("%Y-%m-%d")
        slug = self.collection.collection_name.replace(" ", "_")
        default_name = f"Comparacion_{slug}_{date}.pdf"
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar PDF de comparación"),
            default_name,
            self.tr("PDF (*.pdf)"),
        )
        if not path_str:
            return
        out = Path(path_str)
        self._pdf_button.setEnabled(False)

        worker = _ComparisonPdfWorker(
            db_path=self._db_path,
            collection=self.collection,
            result=self._comparison,
            output_path=out,
            parent=self,
        )
        self._pdf_worker = worker

        def on_ok(result: object) -> None:
            self._pdf_button.setEnabled(True)
            assert isinstance(result, PdfGeneratorResult)
            _show_pdf_done_dialog(self, self.tr("PDF de comparación"), result.output_path)

        def on_failed(msg: str) -> None:
            self._pdf_button.setEnabled(True)
            QMessageBox.critical(self, self.tr("Error"), msg)

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    # ------------------------------------------------------------------
    # Ejecutar intercambio
    # ------------------------------------------------------------------

    def _on_execute_exchange(self) -> None:
        if self._comparison is None:
            return
        assert self.collection.collection_id is not None
        dlg = ExchangeView(
            conn=self.conn,
            db_path=self._db_path,
            collection=self.collection,
            comparison=self._comparison,
            parent=self,
        )
        if dlg.exec():
            # Intercambio confirmado: limpiar comparación y refrescar UI
            self._comparison = None
            self._other_file = None
            self._other_status_label.setText(self.tr("Ninguno cargado"))
            self._i_need_list.clear()
            self._i_offer_list.clear()
            self._update_action_buttons()


# ----------------------------------------------------------------------
# Helper compartido: dialog "PDF generado" + botón Visualizar
# ----------------------------------------------------------------------


def _show_pdf_done_dialog(parent: QWidget, title: str, pdf_path: Path) -> None:
    """QMessageBox con botones [OK] [Visualizar]. Abre el PDF si elige Visualizar."""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(parent.tr("PDF guardado en:\n{p}").format(p=str(pdf_path)))
    msg.addButton(parent.tr("OK"), QMessageBox.ButtonRole.AcceptRole)
    btn_view = msg.addButton(parent.tr("Visualizar"), QMessageBox.ButtonRole.ActionRole)
    msg.exec()
    if msg.clickedButton() is btn_view:
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path)))
