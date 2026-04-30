"""Tests del InventoryView."""

import pytest

from collections_app.client.views.inventory_view import (
    FILTER_ALL,
    STATUS_MISSING,
    STATUS_OWNED,
    STATUS_REPEATED,
    InventoryView,
)
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def inventory_setup(memory_db, sample_collection):
    """Catálogo con 5 cards (3 ARG + 2 BRA) e inventario parcial."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines.upsert(CodeLine(hid, "BRA", "Brasil"))

    cards = CardsRepository(memory_db)
    cards.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    cards.upsert(Card(cid, "ARG", 2, "Emiliano Martinez"))
    cards.upsert(Card(cid, "ARG", 3, "Nahuel Molina"))
    cards.upsert(Card(cid, "BRA", 1, "Vinicius"))
    cards.upsert(Card(cid, "BRA", 2, "Neymar"))

    inv = InventoryService(memory_db)
    inv.add_card(cid, "ARG", 1, 2)  # repetida
    inv.add_card(cid, "ARG", 2, 1)  # tengo
    inv.add_card(cid, "BRA", 1, 1)  # tengo
    # ARG-3 y BRA-2 no se cargaron → faltan
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, inventory_setup):
    v = InventoryView(memory_db, inventory_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def _row_count_visible(view: InventoryView) -> int:
    return view._proxy.rowCount()


def test_inventory_loads_all_cards(qtbot, view):
    """Por default muestra las 5 cards."""
    assert _row_count_visible(view) == 5


def test_filter_by_owned_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_OWNED)
    # Sólo las que tienen quantity == 1: ARG-2 y BRA-1
    assert _row_count_visible(view) == 2


def test_filter_by_missing_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_MISSING)
    # ARG-3 y BRA-2
    assert _row_count_visible(view) == 2


def test_filter_by_duplicates_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_REPEATED)
    # ARG-1 (qty=2)
    assert _row_count_visible(view) == 1


def test_filter_by_code(qtbot, view):
    view._code_filter.setCurrentText("ARG")
    assert _row_count_visible(view) == 3


def test_search_by_name(qtbot, view):
    view._search_input.setText("Messi")
    assert _row_count_visible(view) == 1


def test_filters_combine_with_and(qtbot, view):
    """Filtros se combinan: estado=Tengo + código=ARG → solo ARG-2."""
    view._state_filter.setCurrentText(STATUS_OWNED)
    view._code_filter.setCurrentText("ARG")
    assert _row_count_visible(view) == 1


def test_status_bar_shows_correct_counts(qtbot, view):
    """Total 5, tengo 3 (ARG-1 repetida + ARG-2 + BRA-1), faltan 2, repetidas 1."""
    text = view._status_label.text()
    assert "Total: 5" in text
    assert "Tengo: 3" in text  # owned + repeated
    assert "Faltan: 2" in text
    assert "Repetidas: 1" in text


def test_refresh_after_card_changed_signal(qtbot, memory_db, view, inventory_setup):
    """refresh() recalcula filas al cambiar el inventario externamente."""
    InventoryService(memory_db).add_card(inventory_setup.collection_id, "ARG", 3, 1)
    view.refresh()
    text = view._status_label.text()
    assert "Tengo: 4" in text
    assert "Faltan: 1" in text


def test_color_coding_by_status(qtbot, view):
    """Las celdas tienen color de fondo según el estado."""
    from collections_app.client.views.inventory_view import (
        COLOR_MISSING,
        COLOR_OWNED,
        COLOR_REPEATED,
    )

    # Buscar una fila por estado y comparar el background
    found_states = set()
    for row in range(view._grid_model.rowCount()):
        state = view._grid_model.item(row, view.COL_STATE).text()
        bg = view._grid_model.item(row, view.COL_STATE).background().color()
        found_states.add(state)
        if state == STATUS_OWNED:
            assert bg == COLOR_OWNED
        elif state == STATUS_REPEATED:
            assert bg == COLOR_REPEATED
        elif state == STATUS_MISSING:
            assert bg == COLOR_MISSING
    # Cubrimos los 3 estados
    assert found_states == {STATUS_OWNED, STATUS_REPEATED, STATUS_MISSING}


def test_initial_filter_is_all(qtbot, view):
    assert view._state_filter.currentText() == FILTER_ALL
    assert view._code_filter.currentText() == FILTER_ALL


def test_clearing_search_restores_all(qtbot, view):
    view._search_input.setText("Messi")
    assert _row_count_visible(view) == 1
    view._search_input.setText("")
    assert _row_count_visible(view) == 5
