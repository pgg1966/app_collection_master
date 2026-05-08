"""Diálogo de éxito post-export (Prompt 5b).

Modal chico con tres acciones disponibles para el archivo recién
generado: abrir la carpeta donde quedó, mandárselo por mail al otro
coleccionista, o cerrar.

Las dos primeras delegan a `_system_helpers`. El cuerpo del mail es
una línea fija para mantener el `mailto:` URL bien por debajo del
límite de algunos clientes.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.views.exchange._system_helpers import (
    open_folder_with_file_selected,
    open_mailto,
)


class ExchangeSuccessDialog(QDialog):
    """Diálogo modal con acciones para el archivo recién exportado."""

    def __init__(
        self: ExchangeSuccessDialog,
        path: Path,
        collection_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._path = path
        self._collection_name = collection_name
        self.setWindowTitle(self.tr("Archivo generado"))
        self._build_ui()

    def _build_ui(self: ExchangeSuccessDialog) -> None:
        outer = QVBoxLayout(self)

        msg = QLabel(self.tr("El archivo se generó correctamente."))
        outer.addWidget(msg)

        path_label = QLabel(str(self._path))
        path_label.setTextInteractionFlags(
            path_label.textInteractionFlags()
            | path_label.textInteractionFlags().__class__.TextSelectableByMouse
        )
        path_label.setWordWrap(True)
        outer.addWidget(path_label)

        btns = QHBoxLayout()
        self._open_folder_btn = QPushButton(self.tr("Abrir carpeta"))
        self._open_folder_btn.clicked.connect(self._on_open_folder)
        self._send_mail_btn = QPushButton(self.tr("Enviar por mail"))
        self._send_mail_btn.clicked.connect(self._on_send_mail)
        self._close_btn = QPushButton(self.tr("Cerrar"))
        self._close_btn.setDefault(True)
        self._close_btn.clicked.connect(self.accept)
        btns.addWidget(self._open_folder_btn)
        btns.addWidget(self._send_mail_btn)
        btns.addStretch()
        btns.addWidget(self._close_btn)
        outer.addLayout(btns)

    def _on_open_folder(self: ExchangeSuccessDialog) -> None:
        open_folder_with_file_selected(self._path)

    def _on_send_mail(self: ExchangeSuccessDialog) -> None:
        subject = self.tr("Mi inventario para intercambio — {coll}").format(
            coll=self._collection_name
        )
        body = self.tr(
            "Te mando mi archivo de intercambio adjunto. Abrilo desde la app "
            "para calcular qué podemos intercambiar."
        )
        open_mailto(subject=subject, body=body)
