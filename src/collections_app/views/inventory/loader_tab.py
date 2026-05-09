"""Wrapper de la tab "Cargas" con sub-tabs Manual / Por foto (Sesión 5d).

Reemplaza el uso directo de `CardLoaderView` en `CollectionDetailView`.
Por dentro hay un `QTabWidget` con dos sub-tabs:

- "Manual" → `CardLoaderView` (vista preservada de v0.1, intacta).
- "Por foto" → `OcrLoaderTab` (Sesión 5d).

`card_changed` se re-emite desde ambos hijos: alta manual y aplicación
de OCR ambas terminan invalidando el inventario, así que el
`CollectionDetailView` puede mantener su patrón de refresh chain
conectando una sola signal.

`set_active_collection` propaga a los dos sub-tabs para que ambos
sigan apuntando a la collection activa.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.inventory.ocr_loader_tab import OcrLoaderTab

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection


class LoaderTab(QWidget):
    """Wrapper con dos sub-tabs (Manual + Por foto)."""

    card_changed = Signal()

    def __init__(
        self: LoaderTab,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self._inner_tabs = QTabWidget()
        self._manual = CardLoaderView(ctx=ctx, collection=collection)
        self._ocr = OcrLoaderTab(ctx=ctx, collection=collection)
        self._inner_tabs.addTab(self._manual, self.tr("Manual"))
        self._inner_tabs.addTab(self._ocr, self.tr("Por foto"))
        outer.addWidget(self._inner_tabs)
        # Re-emit: cualquier sub-tab que mute inventario empuja al exterior.
        self._manual.card_changed.connect(self.card_changed)
        self._ocr.card_changed.connect(self.card_changed)

    def set_active_collection(self: LoaderTab, collection: Collection) -> None:
        """Propaga la nueva collection a los dos sub-tabs."""
        self._manual.set_active_collection(collection)
        self._ocr.set_active_collection(collection)

    @property
    def manual(self: LoaderTab) -> CardLoaderView:
        return self._manual

    @property
    def ocr(self: LoaderTab) -> OcrLoaderTab:
        return self._ocr
