"""Tab Álbum: genera 4 PDFs (álbum visual + listas faltantes/repetidas/owned)."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.db.connection import create_connection
from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.core.services import AlbumService, InventoryService, PdfGeneratorResult
from collections_app.core.utils.paths import get_crest_path
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class _PdfWorker(QThread):
    """Genera un PDF en thread separado.

    Abre su propia conexión a la DB (NO se pueden compartir `sqlite3.Connection`
    entre threads). El kind define cuál de los 4 generadores invoca.
    """

    finished_ok = Signal(object)  # PdfGeneratorResult
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        output_path: Path,
        kind: str,  # "album" | "missing" | "duplicates" | "owned"
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._output_path = output_path
        self._kind = kind

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                col = CollectionsRepository(conn).get_by_id(self._collection_id)
                if col is None:
                    raise ValueError(f"Colección {self._collection_id} no encontrada")
                service = AlbumService(conn)
                match self._kind:
                    case "album":
                        result = service.generate_album_pdf(col, self._output_path)
                    case "missing":
                        result = service.generate_missing_pdf(col, self._output_path)
                    case "duplicates":
                        result = service.generate_duplicates_pdf(col, self._output_path)
                    case "owned":
                        result = service.generate_owned_pdf(col, self._output_path)
                    case _:
                        raise ValueError(f"Tipo de PDF desconocido: {self._kind}")
            finally:
                conn.close()
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando PDF (%s)", self._kind)
            if self._output_path.exists():
                self._output_path.unlink(missing_ok=True)
            self.failed.emit(str(exc))


class AlbumView(QWidget):
    """Tab del cliente: genera PDFs del álbum y listas asociadas."""

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

        title = QLabel(self.tr("Exportar Álbum a PDF"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        layout.addWidget(self._build_export_section())
        layout.addWidget(self._build_info_section())
        layout.addStretch()

    def _build_export_section(self) -> QFrame:
        frame = self._section_frame()
        outer = QVBoxLayout(frame)
        outer.setSpacing(Spacing.MD)

        outer.addWidget(self._section_title(self.tr("📄 PDFs")))
        outer.addWidget(
            QLabel(
                self.tr(
                    "El layout del álbum visual (columnas/filas/orientación) "
                    "se configura en Admin → Colecciones."
                )
            )
        )

        # Botón 1: álbum visual
        outer.addLayout(
            self._make_button_row(
                self.tr("📄 Álbum visual completo"),
                self.tr("Todas las cards — con foto o placeholder."),
                kind="album",
            )
        )
        # Botón 2: faltantes
        outer.addLayout(
            self._make_button_row(
                self.tr("📋 PDF de faltantes"),
                self.tr("Lista de cards que te faltan."),
                kind="missing",
            )
        )
        # Botón 3: repetidas
        outer.addLayout(
            self._make_button_row(
                self.tr("📋 PDF de repetidas"),
                self.tr("Lista de cards que tenés más de una vez."),
                kind="duplicates",
            )
        )
        # Botón 4: owned
        outer.addLayout(
            self._make_button_row(
                self.tr("📋 PDF de lo que tengo"),
                self.tr("Lista completa de tu colección actual."),
                kind="owned",
            )
        )

        # Estado
        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._status_label.setTextInteractionFlags(self._status_label.textInteractionFlags())
        outer.addWidget(self._status_label)
        return frame

    def _make_button_row(self, label: str, subtitle: str, kind: str) -> QVBoxLayout:
        row = QVBoxLayout()
        row.setSpacing(Spacing.XS)
        button = QPushButton(label)
        button.clicked.connect(lambda: self._generate(kind))
        row.addWidget(button)
        row.addWidget(QLabel(subtitle))
        # Guardar referencia para deshabilitar/habilitar
        if not hasattr(self, "_buttons"):
            self._buttons: list[QPushButton] = []
        self._buttons.append(button)
        return row

    def _build_info_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.XS)
        layout.addWidget(self._section_title(self.tr("ℹ️ Info de imágenes")))
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
        """Muestra cuántos códigos de la colección ya tienen escudo (info)."""
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
        if total_codes == 0:
            self._image_count_label.setText(
                self.tr("La colección no tiene códigos definidos todavía.")
            )
            return
        with_crest = sum(1 for line in lines if get_crest_path(line.code_id).exists())
        pct = (with_crest / total_codes * 100) if total_codes > 0 else 0
        self._image_count_label.setText(
            self.tr("Escudos cargados: {n} / {t} ({pct:.1f}%)").format(
                n=with_crest, t=total_codes, pct=pct
            )
        )

    # ------------------------------------------------------------------
    # Generación
    # ------------------------------------------------------------------

    _PREFIX_BY_KIND: dict[str, str] = {
        "album": "Album",
        "missing": "Faltantes",
        "duplicates": "Repetidas",
        "owned": "Tengo",
    }

    def _default_filename(self, kind: str) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        slug = self.collection.collection_name.replace(" ", "_")
        return f"{self._PREFIX_BY_KIND[kind]}_{slug}_{date}.pdf"

    def _generate(self, kind: str) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar PDF"),
            self._default_filename(kind),
            self.tr("PDF (*.pdf)"),
        )
        if not path_str:
            return  # usuario canceló
        out = Path(path_str)
        self._set_buttons_enabled(False)
        self._status_label.setText(self.tr("Generando…"))

        assert self.collection.collection_id is not None
        worker = _PdfWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            output_path=out,
            kind=kind,
            parent=self,
        )
        self._worker = worker

        title = self._PREFIX_BY_KIND[kind]

        def on_ok(result: object) -> None:
            assert isinstance(result, PdfGeneratorResult)
            self._set_buttons_enabled(True)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._last_run_label.setText(self.tr("Última generación: {ts}").format(ts=ts))
            self._status_label.setText(
                self.tr("✓ PDF guardado en: {p}").format(p=str(result.output_path))
            )
            QMessageBox.information(
                self,
                title,
                self.tr(
                    "PDF generado.\n\nPáginas: {p}\nCon foto: {f}\n"
                    "Placeholder celeste: {c}\nFaltantes: {m}"
                ).format(
                    p=result.pages,
                    f=result.cards_with_image,
                    c=result.cards_celeste_placeholder,
                    m=result.cards_missing,
                ),
            )

        def on_failed(msg: str) -> None:
            self._set_buttons_enabled(True)
            self._status_label.setText("")
            QMessageBox.critical(self, title, msg)

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for b in self._buttons:
            b.setEnabled(enabled)


# ----------------------------------------------------------------------
# Helper backwards-compatible para tests / scripts
# ----------------------------------------------------------------------


def open_pdf_externally(path: Path) -> None:
    """Helper: abre un PDF con la app default del sistema."""
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
