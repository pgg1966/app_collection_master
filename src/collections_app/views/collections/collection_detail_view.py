"""Vista de detalle de una colección — orquesta los 5 tabs.

- "Mis cards"     → InventoryTab
- "Cargar stock"  → CardLoaderView (vista preservada de v0.1, embebida)
- "Historial"     → HistoryTab
- "Estadísticas"  → StatsView (Prompt 4b)
- "Reportes"      → ReportsView (Prompt 4b)

El cableado clave es el signal `CardLoaderView.card_changed`: cada vez
que el usuario cierra un alta/baja, los otros 4 tabs se refrescan
automáticamente para reflejar la mutación.

`refresh_all_tabs()` permite a la `MainWindow` forzar un refresh de
todos los tabs cuando una ABM modal modificó datos.
"""

from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.history_tab import HistoryTab
from collections_app.views.collections.inventory_tab import InventoryTab
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.reports.reports_view import ReportsView
from collections_app.views.stats.stats_view import StatsView


class CollectionDetailView(QWidget):
    """Contenedor con los cinco tabs de la colección activa."""

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
        self._stats_tab = StatsView(ctx=self._ctx, collection=self._collection)
        self._reports_tab = ReportsView(ctx=self._ctx, collection=self._collection)

        self._tabs.addTab(self._inventory_tab, self.tr("Mis cards"))
        self._tabs.addTab(self._loader_tab, self.tr("Cargar stock"))
        self._tabs.addTab(self._history_tab, self.tr("Historial"))
        self._tabs.addTab(self._stats_tab, self.tr("Estadísticas"))
        self._tabs.addTab(self._reports_tab, self.tr("Reportes"))

        outer.addWidget(self._tabs)

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _wire_refresh_chain(self: CollectionDetailView) -> None:
        """`card_changed` del loader → refresh de los 4 tabs no-loader."""
        self._loader_tab.card_changed.connect(self._inventory_tab.refresh)
        self._loader_tab.card_changed.connect(self._history_tab.refresh)
        self._loader_tab.card_changed.connect(self._stats_tab.refresh)
        self._loader_tab.card_changed.connect(self._reports_tab.refresh)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh_all_tabs(self: CollectionDetailView) -> None:
        """Fuerza refresh de los tabs que leen DB.

        Lo usa `MainWindow` después de cerrar una ABM modal para que
        cambios externos (edits en cards, codes, etc.) se reflejen sin
        que el usuario tenga que tocar nada (alternativa simple del
        plan, sin signals granulares).
        """
        self._inventory_tab.refresh()
        self._history_tab.refresh()
        self._stats_tab.refresh()
        self._reports_tab.refresh()
        # `loader_tab` no tiene `refresh` (es un form de input); lo que
        # rebuildea su completer cuando cambia la collection es
        # `set_active_collection`, no aplica acá.

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

    @property
    def stats_tab(self: CollectionDetailView) -> StatsView:
        return self._stats_tab

    @property
    def reports_tab(self: CollectionDetailView) -> ReportsView:
        return self._reports_tab
