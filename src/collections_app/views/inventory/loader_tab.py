"""Tab "Cargas" — tres frames de carga de inventario (Prompt 6).

Layout:

    ┌──────────────────────────────────────────────────────┐
    │ ┌────────────────┐  ┌──────────────────────────────┐ │
    │ │     Manual     │  │       Por archivo            │ │
    │ │  (CardLoader)  │  │   (InventoryImportPanel)     │ │
    │ └────────────────┘  └──────────────────────────────┘ │
    │ ┌──────────────────────────────────────────────────┐ │
    │ │       Cargar desde fotos (OCR)                   │ │
    │ │              (OcrLoaderTab)                      │ │
    │ └──────────────────────────────────────────────────┘ │
    └──────────────────────────────────────────────────────┘

`QSplitter` horizontal entre Manual y Por archivo; `QSplitter`
vertical entre la fila superior y el panel OCR. Splitters arrastrables
para que el usuario ajuste la proporción.

Reemplaza el `LoaderTab` con sub-tabs (Sesión 5d): tres formas de
cargar inventario son hermanas, no modos exclusivos, así que tenerlas
visibles a la vez es más útil que esconderlas en tabs.

`card_changed` se re-emite desde los tres panels (alta manual, import
exitoso, apply de OCR). El `CollectionDetailView` sigue conectando
una sola signal — mismo patrón que tenía con `LoaderTab`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from collections_app.views.admin.inventory_import_dialog import InventoryImportPanel
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.inventory.ocr_loader_tab import OcrLoaderTab

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection


# Minimums para que los splitters no colapsen cuando la ventana es
# chica (~600px alto). Por debajo de estos valores cada frame queda
# inservible.
_MIN_TOP_HEIGHT = 220
_MIN_OCR_HEIGHT = 180


class CargasTab(QWidget):
    """Tab con tres frames de carga (Manual / Por archivo / OCR)."""

    card_changed = Signal()

    def __init__(
        self: CargasTab,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._manual = CardLoaderView(ctx=ctx, collection=collection)
        self._import = InventoryImportPanel(ctx=ctx, collection=collection)
        self._ocr = OcrLoaderTab(ctx=ctx, collection=collection)
        self._build_ui()
        self._wire_signals()

    def _build_ui(self: CargasTab) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        top_split = QSplitter(Qt.Orientation.Horizontal)
        top_split.addWidget(self._wrap_with_title("Manual", self._manual))
        top_split.addWidget(self._wrap_with_title("Por archivo", self._import))
        top_split.setStretchFactor(0, 1)
        top_split.setStretchFactor(1, 1)
        top_split.setSizes([1, 1])
        top_split.setMinimumHeight(_MIN_TOP_HEIGHT)

        main_split = QSplitter(Qt.Orientation.Vertical)
        main_split.addWidget(top_split)
        main_split.addWidget(self._wrap_with_title("Cargar desde fotos (OCR)", self._ocr))
        main_split.setStretchFactor(0, 1)
        main_split.setStretchFactor(1, 1)
        main_split.setSizes([1, 1])
        # Forzar mínimos en los hijos del splitter vertical evitando
        # que el OCR colapse cuando el splitter horizontal se infla.
        main_split.setCollapsible(0, False)
        main_split.setCollapsible(1, False)
        self._ocr.setMinimumHeight(_MIN_OCR_HEIGHT)

        outer.addWidget(main_split)
        self._top_split = top_split
        self._main_split = main_split

    def _wrap_with_title(self: CargasTab, title: str, widget: QWidget) -> QGroupBox:
        """Envuelve `widget` en un QGroupBox con el título dado.

        El estilo del QGroupBox viene del stylesheet global (borde +
        título en negrita) — no se setea inline para mantener una sola
        fuente de verdad.
        """
        box = QGroupBox(self.tr(title))
        layout = QVBoxLayout(box)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(widget)
        return box

    def _wire_signals(self: CargasTab) -> None:
        """Re-emite `card_changed` desde los tres panels."""
        self._manual.card_changed.connect(self.card_changed)
        # `InventoryImportPanel` emite `import_completed(dict)`; lo
        # traducimos a un `card_changed()` sin payload.
        self._import.import_completed.connect(lambda _r: self.card_changed.emit())
        self._ocr.card_changed.connect(self.card_changed)

    # ------------------------------------------------------------------
    # API pública (consistencia con los otros tabs del detail view)
    # ------------------------------------------------------------------

    def set_active_collection(self: CargasTab, collection: Collection) -> None:
        """Propaga la nueva collection a los tres panels."""
        self._manual.set_active_collection(collection)
        self._import.set_active_collection(collection)
        self._ocr.set_active_collection(collection)

    # ------------------------------------------------------------------
    # Accessors útiles para tests / debugging
    # ------------------------------------------------------------------

    @property
    def manual(self: CargasTab) -> CardLoaderView:
        return self._manual

    @property
    def importer(self: CargasTab) -> InventoryImportPanel:
        return self._import

    @property
    def ocr(self: CargasTab) -> OcrLoaderTab:
        return self._ocr
