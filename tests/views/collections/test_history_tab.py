"""Tests de HistoryTab — la prueba de trazabilidad granular del v0.2."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.history_tab import (
    HistoryTab,
    _format_card_label,
)

pytestmark = pytest.mark.gui


def _cell_text(tab: HistoryTab, row: int, col: int) -> str:
    """Texto que el modelo expone vía DisplayRole."""
    value = tab._model.data(tab._model.index(row, col), Qt.ItemDataRole.DisplayRole)
    return "" if value is None else str(value)


def test_format_card_label_combines_fields() -> None:
    """Helper puro: 'ARG-1 · Messi'."""
    assert _format_card_label("ARG", 1, "Messi") == "ARG-1 · Messi"


def test_history_tab_empty_when_no_transactions(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._model.rowCount() == 0


def test_history_tab_lists_transaction_after_alta(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Tras un alta, la tabla muestra una fila con operación 'Alta'."""
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 3)
    ctx_with_demo.conn.commit()

    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._model.rowCount() == 1
    assert _cell_text(tab, 0, 1) == "Alta"
    assert _cell_text(tab, 0, 3) == "3"


def test_history_tab_renders_card_label_with_code_and_name(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """**Prueba de trazabilidad granular** — la columna Card muestra
    `CODE-NUM · nombre`, no solo el id de colección como en v0.1."""
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "BRA", 2, 1)  # Rodrygo
    ctx_with_demo.conn.commit()

    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert _cell_text(tab, 0, 2) == "BRA-2 · Rodrygo"


def test_history_tab_orders_recent_first(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Tres altas seguidas: la última registrada va en la fila 0."""
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 1)
    ctx_with_demo.inventory.add_card(cid, "ARG", 2, 1)
    ctx_with_demo.inventory.add_card(cid, "BRA", 1, 1)
    ctx_with_demo.conn.commit()

    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    # La columna 2 es Card. La más reciente debería ser BRA-1.
    assert tab._model.rowCount() == 3
    assert "BRA-1" in _cell_text(tab, 0, 2)


def test_history_tab_baja_renders_label_baja(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 5)
    ctx_with_demo.inventory.remove_card(cid, "ARG", 1, 2)
    ctx_with_demo.conn.commit()

    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    # La operación más reciente es la baja.
    assert _cell_text(tab, 0, 1) == "Baja"
    assert _cell_text(tab, 0, 3) == "2"


def test_history_tab_set_active_collection_swaps(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    cid = demo_collection.collection_id or 0
    ctx_with_demo.inventory.add_card(cid, "ARG", 1, 1)
    ctx_with_demo.conn.commit()

    other = ctx_with_demo.collections.create(
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

    tab = HistoryTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._model.rowCount() == 1
    tab.set_active_collection(other)
    assert tab._model.rowCount() == 0
