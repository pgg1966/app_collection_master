"""Diálogo "Generar archivo de intercambio" (Prompt 5b).

Modal chico con un input de label opcional y un botón "Generar". El
label se pasa tal cual al `ExchangeExportService`, que lo strip-ea
y omite del filename si queda vacío.

Tras un export exitoso `accept()` y deja el `Path` resultante en
`self.result_path`. Errores de servicio (`CollectionNotFound`) van a
`QMessageBox.critical` y el dialog no se cierra para que el usuario
pueda reintentar — aunque en la práctica este flow no debería disparar
errores: la collection viene seleccionada del tab.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exceptions import ServiceError

if TYPE_CHECKING:
    from collections_app.app_context import AppContext


class ExchangeExportDialog(QDialog):
    """Diálogo modal: pedir label opcional y exportar `.colexchange`."""

    def __init__(
        self: ExchangeExportDialog,
        ctx: AppContext,
        collection_id: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection_id = collection_id
        self.result_path: Path | None = None
        self.setWindowTitle(self.tr("Generar archivo de intercambio"))
        self._build_ui()

    def _build_ui(self: ExchangeExportDialog) -> None:
        outer = QVBoxLayout(self)

        info = QLabel(
            self.tr(
                "Vamos a generar tu archivo de intercambio con tus faltantes "
                "y duplicados de esta colección. Si querés, podés agregar una "
                "etiqueta corta para que el otro coleccionista sepa de quién es."
            )
        )
        info.setWordWrap(True)
        outer.addWidget(info)

        form = QFormLayout()
        self._label_edit = QLineEdit()
        self._label_edit.setPlaceholderText(self.tr("Etiqueta opcional, ej: PGG"))
        form.addRow(self.tr("Etiqueta"), self._label_edit)
        outer.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        self._cancel_btn = QPushButton(self.tr("Cancelar"))
        self._cancel_btn.clicked.connect(self.reject)
        self._generate_btn = QPushButton(self.tr("Generar"))
        self._generate_btn.setDefault(True)
        self._generate_btn.clicked.connect(self._on_generate)
        btns.addWidget(self._cancel_btn)
        btns.addWidget(self._generate_btn)
        outer.addLayout(btns)

    def _on_generate(self: ExchangeExportDialog) -> None:
        label = self._label_edit.text().strip() or None
        try:
            path = self._ctx.exchange_export.export_to_file(
                collection_id=self._collection_id,
                user_label=label,
            )
        except ServiceError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error al generar el archivo"),
                str(exc),
            )
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de I/O"),
                self.tr("No se pudo escribir el archivo: {msg}").format(msg=exc),
            )
            return
        self.result_path = path
        self.accept()
