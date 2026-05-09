"""Tests de CollectionDetailView — cableado de tabs y refresh chain."""

from __future__ import annotations

import pytest

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.collection_detail_view import (
    CollectionDetailView,
)
from collections_app.views.collections.history_tab import HistoryTab
from collections_app.views.collections.inventory_tab import InventoryTab
from collections_app.views.exchange.exchange_tab import ExchangeTab
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.reports.reports_view import ReportsView
from collections_app.views.stats.stats_view import StatsView

pytestmark = pytest.mark.gui


def test_detail_view_constructs_with_six_tabs(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Orden de tabs (Sesión 5.5 / F1): Cargas, Reportes, Intercambio,
    Estadísticas, Mis cards, Historial."""
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    assert view._tabs.count() == 6
    assert isinstance(view._tabs.widget(0), CardLoaderView)
    assert isinstance(view._tabs.widget(1), ReportsView)
    assert isinstance(view._tabs.widget(2), ExchangeTab)
    assert isinstance(view._tabs.widget(3), StatsView)
    assert isinstance(view._tabs.widget(4), InventoryTab)
    assert isinstance(view._tabs.widget(5), HistoryTab)


def test_detail_view_tab_titles_in_spanish(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    titles = [view._tabs.tabText(i) for i in range(view._tabs.count())]
    assert titles == [
        "Cargas",
        "Reportes",
        "Intercambio",
        "Estadísticas",
        "Mis cards",
        "Historial",
    ]


def test_card_changed_signal_refreshes_inventory_and_history(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """El signal `card_changed` del loader dispara refresh en los otros 2 tabs."""
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)

    # Estado inicial: 0 transacciones, 0 qty para todas.
    assert view.history_tab._model.rowCount() == 0

    # Mutación atómica via service (simula lo que el loader haría al save).
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 5)
    ctx_with_demo.conn.commit()

    # Disparar el signal manualmente — equivale a un save exitoso del loader.
    view.loader_tab.card_changed.emit()

    # Inventory tab debe mostrar 5 en ARG-1.
    inv_model = view.inventory_tab._model
    arg1_qty = next(
        inv_model.data(inv_model.index(row, 3))
        for row in range(inv_model.rowCount())
        if inv_model.data(inv_model.index(row, 0)) == "ARG"
        and inv_model.data(inv_model.index(row, 1)) == "1"
    )
    assert arg1_qty == "5"

    # History tab debe mostrar 1 transaction con label granular.
    hist_model = view.history_tab._model
    assert hist_model.rowCount() == 1
    assert "ARG-1" in hist_model.data(hist_model.index(0, 2))


def test_loader_tab_uses_ctx_inventory_service(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """La vista preservada recibe el service del context, no uno nuevo."""
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    # Acceso al atributo privado _service del CardLoaderView (test helper).
    assert view.loader_tab._ctx is ctx_with_demo
    assert view.loader_tab._service is ctx_with_demo.inventory


def test_collection_property_exposes_active(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    assert view.collection is demo_collection


def test_refresh_all_tabs_updates_inventory_after_external_change(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Tras una mutación externa (ABM modal), refresh_all_tabs propaga
    el cambio a los 4 tabs lectores."""
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)

    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 7)
    ctx_with_demo.conn.commit()

    view.refresh_all_tabs()

    # Inventory tab debe reflejar qty=7 en ARG-1.
    inv_model = view.inventory_tab._model
    found_qty = None
    for row in range(inv_model.rowCount()):
        if (
            inv_model.data(inv_model.index(row, 0)) == "ARG"
            and inv_model.data(inv_model.index(row, 1)) == "1"
        ):
            found_qty = inv_model.data(inv_model.index(row, 3))
            break
    assert found_qty == "7"
    # Stats tab muestra 1 owned para ARG.
    arg_owned = next(
        view.stats_tab._table.item(row, 3).text()
        for row in range(view.stats_tab._table.rowCount())
        if view.stats_tab._table.item(row, 0).text() == "ARG"
    )
    assert arg_owned == "1"
