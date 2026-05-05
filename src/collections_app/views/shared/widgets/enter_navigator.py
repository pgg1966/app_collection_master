"""Navegación con Enter entre widgets de un formulario."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget


class EnterNavigator(QObject):
    """Hace que `Enter` avance al siguiente widget de una cadena ordenada.

    En el último widget de la cadena, dispara `on_last_enter` (si está
    seteado). Funciona con cualquier QWidget; usa un `eventFilter` que
    detecta `QEvent.KeyPress` con `Key_Return` o `Key_Enter`.

    Uso típico:
        nav = EnterNavigator(self)
        nav.set_chain([self.code_input, self.number_input, self.qty_input])
        nav.on_last_enter = self._save_card
        nav.install()
    """

    def __init__(self: EnterNavigator, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._chain: list[QWidget] = []
        self.on_last_enter: Callable[[], None] | None = None
        self._installed = False

    def set_chain(self: EnterNavigator, widgets: list[QWidget]) -> None:
        """Define el orden de navegación. No instala los filters todavía."""
        self._chain = list(widgets)

    def install(self: EnterNavigator) -> None:
        """Instala el event filter en cada widget de la cadena."""
        if self._installed:
            return
        for widget in self._chain:
            widget.installEventFilter(self)
        self._installed = True

    def uninstall(self: EnterNavigator) -> None:
        """Desinstala los event filters (útil para tests o cleanup)."""
        if not self._installed:
            return
        for widget in self._chain:
            widget.removeEventFilter(self)
        self._installed = False

    def eventFilter(  # noqa: N802
        self: EnterNavigator, watched: QObject, event: QEvent
    ) -> bool:
        """Intercepta KeyPress de Enter/Return en la cadena."""
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)

        key_event = event
        if not isinstance(key_event, QKeyEvent):
            return super().eventFilter(watched, event)
        if key_event.key() not in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return super().eventFilter(watched, event)

        try:
            idx = self._chain.index(watched)  # type: ignore[arg-type]
        except ValueError:
            return super().eventFilter(watched, event)

        if idx == len(self._chain) - 1:
            if self.on_last_enter is not None:
                self.on_last_enter()
            return True

        self._chain[idx + 1].setFocus()
        return True
