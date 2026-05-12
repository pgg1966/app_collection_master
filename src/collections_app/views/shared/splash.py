"""Splash screen con barra de progreso para el arranque (Prompt 7).

Diseño minimalista: un `QSplashScreen` con un `QProgressBar` superpuesto.
Sin imagen de fondo externa, sin texto por paso, sin fade-out.

Uso en `main.py`:

    splash = AppSplashScreen()
    splash.show()
    QApplication.processEvents()

    splash.set_progress(20)   # despues de _ensure_default_db
    splash.set_progress(60)   # despues de crear AppContext
    splash.set_progress(90)   # despues de crear MainWindow
    splash.set_progress(100)
    window.showMaximized()
    splash.finish(window)

`set_progress` bombea el event loop con `processEvents()` para que
el pixmap se repinte; si no, la barra se queda en 0 hasta que el
event loop vuelva a girar (post `app.exec()`).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QProgressBar, QSplashScreen


class AppSplashScreen(QSplashScreen):
    """Splash con titulo + 'Cargando...' + barra de progreso."""

    WIDTH = 400
    HEIGHT = 220

    def __init__(self: AppSplashScreen) -> None:
        pixmap = self._make_pixmap()
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint)
        self._bar = QProgressBar(self)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(True)
        self._bar.setFormat("%p%")
        self._bar.setGeometry(20, 160, self.WIDTH - 40, 28)
        self._bar.setStyleSheet(
            "QProgressBar { border: 1px solid #404040; border-radius: 4px;"
            " background: #F0F0F0; text-align: center; font-weight: bold; }"
            " QProgressBar::chunk { background: #4A90D9; border-radius: 3px; }"
        )

    def set_progress(self: AppSplashScreen, value: int) -> None:
        """Actualiza la barra (clamp 0-100) y bombea el event loop."""
        self._bar.setValue(max(0, min(100, value)))
        QApplication.processEvents()

    @staticmethod
    def _make_pixmap() -> QPixmap:
        px = QPixmap(AppSplashScreen.WIDTH, AppSplashScreen.HEIGHT)
        px.fill(QColor("#F5F5F5"))
        painter = QPainter(px)
        try:
            font = QFont()
            font.setPointSize(22)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#202020"))
            painter.drawText(
                px.rect().adjusted(0, 40, 0, 0),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                "Collections App",
            )
            font.setPointSize(11)
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QColor("#606060"))
            painter.drawText(
                px.rect().adjusted(0, 90, 0, 0),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                "Cargando...",
            )
        finally:
            painter.end()
        return px
