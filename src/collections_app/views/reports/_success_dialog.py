"""Diálogo chico de éxito tras guardar un reporte (Sesión 5.5 / B1).

Aislado en `views/reports/` por la regla 3.5 de CLAUDE.md (subdirs no
se cruzan). Comparte el helper `open_folder_with_file_selected` con
los views de exchange — usar el helper directamente, no copiar.

Sin botón "Enviar por mail": el reporte ya tiene su propio botón
de mail en el panel principal y mezclarlos confunde el flujo.
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
)


class ReportSavedDialog(QDialog):
    """Modal post-guardado de reporte: muestra el path + abrir carpeta."""

    def __init__(
        self: ReportSavedDialog,
        path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._path = path
        self.setWindowTitle(self.tr("Reporte guardado"))
        self._build_ui()

    def _build_ui(self: ReportSavedDialog) -> None:
        outer = QVBoxLayout(self)

        msg = QLabel(self.tr("El reporte se guardó correctamente."))
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
        self._close_btn = QPushButton(self.tr("Cerrar"))
        self._close_btn.setDefault(True)
        self._close_btn.clicked.connect(self.accept)
        btns.addWidget(self._open_folder_btn)
        btns.addStretch()
        btns.addWidget(self._close_btn)
        outer.addLayout(btns)

    def _on_open_folder(self: ReportSavedDialog) -> None:
        open_folder_with_file_selected(self._path)
