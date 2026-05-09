"""Tab "Reportes" — listas de faltantes y repetidas con panel de exportación.

Estructura:

    ┌─ REPORTE FALTANTES ──────────────────────────┐
    │ texto plano generado por _formatters         │
    └──────────────────────────────────────────────┘
    [Copiar] [Guardar .txt] [Imprimir] [Mail] [WhatsApp]

    ┌─ REPORTE REPETIDAS ──────────────────────────┐
    │ texto plano generado por _formatters         │
    └──────────────────────────────────────────────┘
    [Copiar] [Guardar .txt] [Imprimir] [Mail] [WhatsApp]

Las dos secciones tienen el mismo set de 5 botones, encapsulados en
`_ReportSectionWidget`. Los algoritmos de formato son funciones puras
en `_formatters.py` (testeables sin Qt).

Botones:
- Copiar texto: `QApplication.clipboard().setText(...)` + tooltip
  "Copiado" 2s.
- Guardar como .txt: `QFileDialog.getSaveFileName(...)` + write UTF-8.
- Imprimir: `QPrinter` + `QPrintDialog` + `QTextDocument` monospace.
- Enviar por mail: `mailto:` directo si el texto entra; si no, archivo
  temporal + `mailto:` con body corto + dialog informativo.
- WhatsApp: `wa.me/?text=...` si el texto entra; si no, copy al
  clipboard + abrir web.whatsapp.com + dialog informativo.

Sin integraciones SMTP / WhatsApp Business / Telegram. Solo lo que
`mailto:` y `wa.me` cubren del lado del SO.
"""

from __future__ import annotations

import tempfile
import urllib.parse
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFont, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.core.utils.paths import get_downloads_dir
from collections_app.views.reports._formatters import (
    URL_SAFE_LIMIT,
    format_duplicates_report,
    format_missing_report,
    text_fits_in_url,
)
from collections_app.views.reports._success_dialog import ReportSavedDialog

_DATE_SLUG_FORMAT = "%Y-%m-%d"


def _slugify_for_filename(name: str) -> str:
    """Reemplaza caracteres no ASCII-alfanuméricos por guion bajo.

    Restringimos a ASCII (no a `str.isalnum()`, que acepta acentos)
    para que los filenames sean estables al sincronizar entre OS y
    portar entre versiones de la app.
    """
    safe: list[str] = []
    for ch in name:
        if ch.isascii() and (ch.isalnum() or ch in ("-", "_")):
            safe.append(ch)
        else:
            safe.append("_")
    return "".join(safe).strip("_") or "reporte"


class _ReportSectionWidget(QWidget):
    """Una sección del panel de reports: título, texto, 5 botones de export."""

    def __init__(
        self: _ReportSectionWidget,
        title: str,
        kind: str,  # "faltantes" / "repetidas" — usado en filename / subject
        collection_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._kind = kind
        self._collection_name = collection_name
        self._build_ui(title)
        self.set_text("")

    def _build_ui(self: _ReportSectionWidget, title: str) -> None:
        outer = QVBoxLayout(self)

        group = QGroupBox(title)
        inner = QVBoxLayout(group)
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        # Monospace para que las listas alineen.
        font = QFont("Consolas, monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._text_edit.setFont(font)
        inner.addWidget(self._text_edit, 1)
        outer.addWidget(group, 1)

        btns = QHBoxLayout()
        self._copy_btn = QPushButton(self.tr("Copiar texto"))
        self._copy_btn.clicked.connect(self._on_copy)
        self._save_btn = QPushButton(self.tr("Guardar como .txt"))
        self._save_btn.clicked.connect(self._on_save)
        self._print_btn = QPushButton(self.tr("Imprimir"))
        self._print_btn.clicked.connect(self._on_print)
        self._mail_btn = QPushButton(self.tr("Enviar por mail"))
        self._mail_btn.clicked.connect(self._on_mail)
        self._whatsapp_btn = QPushButton(self.tr("Compartir por WhatsApp"))
        self._whatsapp_btn.clicked.connect(self._on_whatsapp)
        for b in (
            self._copy_btn,
            self._save_btn,
            self._print_btn,
            self._mail_btn,
            self._whatsapp_btn,
        ):
            btns.addWidget(b)
        btns.addStretch()
        outer.addLayout(btns)

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def set_text(self: _ReportSectionWidget, text: str) -> None:
        """Setea el texto del reporte. Si está vacío, deshabilita los botones."""
        self._text_edit.setPlainText(text)
        has_text = bool(text.strip())
        for b in (
            self._copy_btn,
            self._save_btn,
            self._print_btn,
            self._mail_btn,
            self._whatsapp_btn,
        ):
            b.setEnabled(has_text)

    def text(self: _ReportSectionWidget) -> str:
        return self._text_edit.toPlainText()

    def update_collection_name(self: _ReportSectionWidget, collection_name: str) -> None:
        self._collection_name = collection_name

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _default_filename(self: _ReportSectionWidget) -> str:
        slug = _slugify_for_filename(self._collection_name)
        date = datetime.now().strftime(_DATE_SLUG_FORMAT)
        return f"{self._kind}_{slug}_{date}.txt"

    def _subject(self: _ReportSectionWidget) -> str:
        kind_label = "Faltantes" if self._kind == "faltantes" else "Repetidas"
        return f"Mi colección — {kind_label}"

    def _on_copy(self: _ReportSectionWidget) -> None:
        QApplication.clipboard().setText(self.text())
        # Feedback visual breve en el botón.
        QToolTip.showText(
            self._copy_btn.mapToGlobal(self._copy_btn.rect().bottomLeft()),
            self.tr("Copiado"),
            self._copy_btn,
            self._copy_btn.rect(),
            2000,
        )

    def _on_save(self: _ReportSectionWidget) -> None:
        """Guarda el reporte en la carpeta Descargas y muestra dialog de éxito.

        Reemplaza el `QFileDialog` previo por guardado automático con
        nombre canónico (`_default_filename`). El usuario puede abrir
        la carpeta desde el dialog post-guardado.
        """
        dest_dir = get_downloads_dir()
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error al guardar"),
                self.tr("No se pudo crear la carpeta de destino: {msg}").format(msg=exc),
            )
            return
        dest_path = dest_dir / self._default_filename()
        try:
            dest_path.write_text(self.text(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error al guardar"),
                self.tr("No se pudo escribir el archivo: {msg}").format(msg=exc),
            )
            return
        ReportSavedDialog(path=dest_path, parent=self).exec()

    def _on_print(self: _ReportSectionWidget) -> None:
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QPrintDialog.DialogCode.Accepted:
            return
        document = QTextDocument()
        document.setDefaultFont(self._text_edit.font())
        document.setPlainText(self.text())
        document.print_(printer)

    def _on_mail(self: _ReportSectionWidget) -> None:
        text = self.text()
        subject = self._subject()
        if text_fits_in_url(text):
            params = urllib.parse.urlencode(
                {"subject": subject, "body": text}, quote_via=urllib.parse.quote
            )
            QDesktopServices.openUrl(QUrl(f"mailto:?{params}"))
            return
        # Fallback: archivo temporal + mailto con body corto + dialog.
        tmp_path = Path(tempfile.gettempdir()) / self._default_filename()
        tmp_path.write_text(text, encoding="utf-8")
        body_short = self.tr(
            "Adjunto la lista en archivo separado (revisá tu carpeta "
            "de descargas o temp).\n\nArchivo: {path}"
        ).format(path=tmp_path)
        params = urllib.parse.urlencode(
            {"subject": subject, "body": body_short},
            quote_via=urllib.parse.quote,
        )
        QDesktopServices.openUrl(QUrl(f"mailto:?{params}"))
        QMessageBox.information(
            self,
            self.tr("Reporte largo"),
            self.tr(
                "El reporte es muy largo para enviarse directo. "
                "Guardamos el archivo en {path}. Adjuntalo manualmente al mail."
            ).format(path=tmp_path),
        )

    def _on_whatsapp(self: _ReportSectionWidget) -> None:
        text = self.text()
        if text_fits_in_url(text):
            encoded = urllib.parse.quote(text)
            QDesktopServices.openUrl(QUrl(f"https://wa.me/?text={encoded}"))
            return
        # Fallback: clipboard + abrir WhatsApp Web + dialog.
        QApplication.clipboard().setText(text)
        QDesktopServices.openUrl(QUrl("https://web.whatsapp.com"))
        QMessageBox.information(
            self,
            self.tr("Reporte largo"),
            self.tr(
                "El texto es demasiado largo para enviarse por WhatsApp directo. "
                "Te lo copiamos al portapapeles para que lo pegues manualmente."
            ),
        )


class ReportsView(QWidget):
    """Tab embebido en CollectionDetailView con dos secciones de export."""

    def __init__(
        self: ReportsView,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._build_ui()
        self.refresh()

    def _build_ui(self: ReportsView) -> None:
        outer = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel(self.tr("Listas para mandar por mail / WhatsApp.")))
        toolbar.addStretch()
        self._refresh_btn = QPushButton(self.tr("Refrescar"))
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)
        outer.addLayout(toolbar)

        self._missing_section = _ReportSectionWidget(
            title=self.tr("REPORTE FALTANTES"),
            kind="faltantes",
            collection_name=self._collection.collection_name,
        )
        self._duplicates_section = _ReportSectionWidget(
            title=self.tr("REPORTE REPETIDAS"),
            kind="repetidas",
            collection_name=self._collection.collection_name,
        )
        outer.addWidget(self._missing_section, 1)
        outer.addWidget(self._duplicates_section, 1)

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def refresh(self: ReportsView) -> None:
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id

        codes = self._ctx.code_lines.list_by_header(self._collection.code_header_id)

        missing_cards = self._ctx.inventory.list_missing(cid)
        missing_text = format_missing_report(missing_cards, codes)
        self._missing_section.set_text(missing_text)

        duplicates = self._ctx.inventory.list_duplicates(cid)
        cards = self._ctx.cards.list_by_collection(cid)
        cards_by_id = {card.card_id: card for card in cards if card.card_id is not None}
        duplicates_text = format_duplicates_report(duplicates, cards_by_id, codes)
        self._duplicates_section.set_text(duplicates_text)

    def set_active_collection(self: ReportsView, collection: Collection) -> None:
        self._collection = collection
        self._missing_section.update_collection_name(collection.collection_name)
        self._duplicates_section.update_collection_name(collection.collection_name)
        self.refresh()


__all__ = [
    "URL_SAFE_LIMIT",
    "ReportsView",
    "_ReportSectionWidget",
    "_slugify_for_filename",
]
