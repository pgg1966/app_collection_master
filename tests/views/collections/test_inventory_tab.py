"""Tests de InventoryTab — listado del catálogo con qty actual."""

from __future__ import annotations

import pytest
from PySide6.QtGui import QColor

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.inventory_tab import (
    _ZERO_QTY_COLOR,
    InventoryTab,
)

pytestmark = pytest.mark.gui


def test_inventory_tab_shows_all_cards_in_catalog(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """4 cards seedeadas → 4 filas en la tabla."""
    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._table.rowCount() == 4


def test_inventory_tab_renders_zero_qty_for_unstocked_cards(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Sin altas, cada fila debe mostrar 0 en la columna Cantidad."""
    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    qty_column = 3
    for row in range(tab._table.rowCount()):
        item = tab._table.item(row, qty_column)
        assert item is not None
        assert item.text() == "0"


def test_inventory_tab_paints_zero_qty_rows_grey(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """qty=0 → texto en gris (foreground = _ZERO_QTY_COLOR)."""
    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    item = tab._table.item(0, 0)
    assert item is not None
    assert item.foreground().color() == QColor(_ZERO_QTY_COLOR)


def test_inventory_tab_reflects_quantities_after_alta(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Tras un alta vía service, refresh() debe mostrar la qty nueva."""
    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 3)
    ctx_with_demo.conn.commit()
    tab.refresh()

    # Buscamos la fila ARG-1 y verificamos qty=3 + sin tinte gris.
    found = False
    for row in range(tab._table.rowCount()):
        if tab._table.item(row, 0).text() == "ARG" and tab._table.item(row, 1).text() == "1":
            assert tab._table.item(row, 3).text() == "3"
            assert tab._table.item(row, 0).foreground().color() != QColor(_ZERO_QTY_COLOR)
            found = True
            break
    assert found, "no se encontró la fila ARG-1 después del refresh"


def test_inventory_tab_set_active_collection_swaps_data(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Cambiar de collection vía set_active_collection refresca con la nueva."""
    # Crear segunda colección sin cards.
    other_coll = ctx_with_demo.collections.create(
        Collection(
            collection_id=None,
            collection_name="Empty",
            card_count=0,
            requires_code=False,
            code_field_name=None,
            code_header_id=demo_collection.code_header_id,
        )
    )
    ctx_with_demo.conn.commit()

    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._table.rowCount() == 4

    tab.set_active_collection(other_coll)
    assert tab._table.rowCount() == 0


def test_inventory_tab_refresh_button_works(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Click en Refrescar dispara refresh()."""
    tab = InventoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 5)
    ctx_with_demo.conn.commit()
    qtbot.mouseClick(
        tab._refresh_btn, qt_button := __import__("PySide6").QtCore.Qt.MouseButton.LeftButton
    )  # type: ignore[arg-type]
    _ = qt_button  # silencia ruff/unused
    # Tras el click, la fila ARG-1 debe mostrar 5.
    arg1_qty = next(
        tab._table.item(row, 3).text()
        for row in range(tab._table.rowCount())
        if tab._table.item(row, 0).text() == "ARG" and tab._table.item(row, 1).text() == "1"
    )
    assert arg1_qty == "5"
