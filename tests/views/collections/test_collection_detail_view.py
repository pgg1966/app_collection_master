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
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.reports.reports_view import ReportsView
from collections_app.views.stats.stats_view import StatsView

pytestmark = pytest.mark.gui


def test_detail_view_constructs_with_five_tabs(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    assert view._tabs.count() == 5
    # Orden y tipos esperados.
    assert isinstance(view._tabs.widget(0), InventoryTab)
    assert isinstance(view._tabs.widget(1), CardLoaderView)
    assert isinstance(view._tabs.widget(2), HistoryTab)
    assert isinstance(view._tabs.widget(3), StatsView)
    assert isinstance(view._tabs.widget(4), ReportsView)


def test_detail_view_tab_titles_in_spanish(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    titles = [view._tabs.tabText(i) for i in range(view._tabs.count())]
    assert titles == [
        "Mis cards",
        "Cargar stock",
        "Historial",
        "Estadísticas",
        "Reportes",
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
    assert view.history_tab._table.rowCount() == 0

    # Mutación atómica via service (simula lo que el loader haría al save).
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 5)
    ctx_with_demo.conn.commit()

    # Disparar el signal manualmente — equivale a un save exitoso del loader.
    view.loader_tab.card_changed.emit()

    # Inventory tab debe mostrar 5 en ARG-1.
    arg1_qty = next(
        view.inventory_tab._table.item(row, 3).text()
        for row in range(view.inventory_tab._table.rowCount())
        if view.inventory_tab._table.item(row, 0).text() == "ARG"
        and view.inventory_tab._table.item(row, 1).text() == "1"
    )
    assert arg1_qty == "5"

    # History tab debe mostrar 1 transaction con label granular.
    assert view.history_tab._table.rowCount() == 1
    assert "ARG-1" in view.history_tab._table.item(0, 2).text()


def test_loader_tab_uses_ctx_inventory_service(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """La vista preservada recibe el service del context, no uno nuevo."""
    view = CollectionDetailView(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(view)
    # Acceso al atributo privado _service del CardLoaderView (test helper).
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
    found_qty = None
    for row in range(view.inventory_tab._table.rowCount()):
        if (
            view.inventory_tab._table.item(row, 0).text() == "ARG"
            and view.inventory_tab._table.item(row, 1).text() == "1"
        ):
            found_qty = view.inventory_tab._table.item(row, 3).text()
            break
    assert found_qty == "7"
    # Stats tab muestra 1 owned para ARG.
    arg_owned = next(
        view.stats_tab._table.item(row, 3).text()
        for row in range(view.stats_tab._table.rowCount())
        if view.stats_tab._table.item(row, 0).text() == "ARG"
    )
    assert arg_owned == "1"
