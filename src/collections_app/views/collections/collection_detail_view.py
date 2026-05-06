"""Vista de detalle de una colección — orquesta los 3 tabs.

- "Mis cards"   → InventoryTab
- "Cargar stock"→ CardLoaderView (vista preservada de v0.1, embebida)
- "Historial"  → HistoryTab

El cableado clave es el signal `CardLoaderView.card_changed`: cada vez
que el usuario cierra un alta/baja, los otros dos tabs se refrescan
automáticamente para reflejar la mutación. Eso prueba el flujo
end-to-end (alta → inventario actualizado → transaction visible).
"""

from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.history_tab import HistoryTab
from collections_app.views.collections.inventory_tab import InventoryTab
from collections_app.views.inventory.card_loader import CardLoaderView


class CollectionDetailView(QWidget):
    """Contenedor con los tres tabs de la colección activa."""

    def __init__(
        self: CollectionDetailView,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._build_ui()
        self._wire_refresh_chain()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: CollectionDetailView) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._inventory_tab = InventoryTab(ctx=self._ctx, collection=self._collection)
        self._loader_tab = CardLoaderView(service=self._ctx.inventory, collection=self._collection)
        self._history_tab = HistoryTab(ctx=self._ctx, collection=self._collection)

        self._tabs.addTab(self._inventory_tab, self.tr("Mis cards"))
        self._tabs.addTab(self._loader_tab, self.tr("Cargar stock"))
        self._tabs.addTab(self._history_tab, self.tr("Historial"))

        outer.addWidget(self._tabs)

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _wire_refresh_chain(self: CollectionDetailView) -> None:
        """`card_changed` del loader → refresh de inventory + history."""
        self._loader_tab.card_changed.connect(self._inventory_tab.refresh)
        self._loader_tab.card_changed.connect(self._history_tab.refresh)

    # ------------------------------------------------------------------
    # Accessors útiles para los tests / la MainWindow
    # ------------------------------------------------------------------

    @property
    def collection(self: CollectionDetailView) -> Collection:
        return self._collection

    @property
    def inventory_tab(self: CollectionDetailView) -> InventoryTab:
        return self._inventory_tab

    @property
    def history_tab(self: CollectionDetailView) -> HistoryTab:
        return self._history_tab

    @property
    def loader_tab(self: CollectionDetailView) -> CardLoaderView:
        return self._loader_tab
