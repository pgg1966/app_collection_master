"""Widget compartido: `QLabel` que re-escala su pixmap al tamaño disponible.

El `QLabel` default no re-escala el pixmap al redimensionar el widget
(`setScaledContents=True` lo hace pero pierde aspect ratio). Esta subclase
guarda el pixmap original y re-escala en cada `resizeEvent` preservando
proporción.

Usado tanto por `OcrResultDialog` (foto anotada del modal post-procesamiento)
como por `OcrLoaderTab` (imagen de guía en Estado 3).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget


class ScaledImageLabel(QLabel):
    """QLabel que re-escala su pixmap original al tamaño actual."""

    def __init__(
        self: ScaledImageLabel,
        pixmap: QPixmap,
        parent: QWidget | None = None,
        *,
        minimum_width: int = 300,
        minimum_height: int = 200,
    ) -> None:
        super().__init__(parent)
        self._original = pixmap
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setMinimumWidth(minimum_width)
        self.setMinimumHeight(minimum_height)
        # Mostrar el pixmap antes del primer resize (si esperamos al
        # resizeEvent, el label queda vacío hasta que el widget se
        # muestra; en tests headless no se llega a mostrar nunca).
        if not pixmap.isNull():
            super().setPixmap(pixmap)

    def resizeEvent(self: ScaledImageLabel, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        if not self._original.isNull():
            scaled = self._original.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)

    def set_original_pixmap(self: ScaledImageLabel, pixmap: QPixmap) -> None:
        """Reemplaza el pixmap fuente y dispara un re-escalado."""
        self._original = pixmap
        if pixmap.isNull():
            self.clear()
            return
        # Si el widget ya tiene tamaño asignado, escalar; sino guardar
        # original y dejar que resizeEvent escale al primer layout pass.
        if self.width() > 0 and self.height() > 0:
            super().setPixmap(
                pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            super().setPixmap(pixmap)
