"""Tests del CardLoaderView."""

import pytest
from PySide6.QtCore import Qt

from collections_app.client.views.card_loader import DEFAULT_CODE, CardLoaderView
from collections_app.core.models import Card, CodeLine, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def loader_collection(memory_db, sample_code_header):
    """Collection (requires_code=True) con codes_lines + cards."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [
        (DEFAULT_CODE, "Sin prefijo"),
        ("ARG", "Argentina"),
        ("MR", "Master Rookies"),
    ]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Test WC",
            card_count=100,
            requires_code=True,
            code_field_name="País",
            code_header_id=hid,
        )
    )

    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(col.collection_id, DEFAULT_CODE, 24, "LIONEL MESSI"))
    cards_repo.upsert(Card(col.collection_id, DEFAULT_CODE, 25, "EMILIANO MARTINEZ"))
    cards_repo.upsert(Card(col.collection_id, "ARG", 1, "ARG STUFF"))
    cards_repo.upsert(Card(col.collection_id, "MR", 1, "PAZ"))
    memory_db.commit()
    return col


@pytest.fixture
def free_collection(memory_db, sample_code_header):
    """Collection con requires_code=False (todas las cards usan DEFAULT_CODE)."""
    hid = sample_code_header.code_header_id
    CodesLinesRepository(memory_db).upsert(CodeLine(hid, DEFAULT_CODE, "Sin prefijo"))
    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Free",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=hid,
        )
    )
    CardsRepository(memory_db).upsert(Card(col.collection_id, DEFAULT_CODE, 1, "First"))
    memory_db.commit()
    return col


@pytest.fixture
def loader(qtbot, memory_db, loader_collection):
    view = CardLoaderView(memory_db, loader_collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    return view


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_loader_default_focus_on_number(qtbot, loader):
    qtbot.wait(50)
    assert loader._number_input.hasFocus()


def test_checkbox_hidden_when_collection_does_not_require_code(qtbot, memory_db, free_collection):
    view = CardLoaderView(memory_db, free_collection)
    qtbot.addWidget(view)
    view.show()
    assert view._has_code_checkbox.isVisible() is False


def test_checkbox_toggles_code_field_visibility(qtbot, loader):
    assert loader._code_combo.isVisible() is False
    loader._has_code_checkbox.setChecked(True)
    assert loader._code_combo.isVisible() is True
    loader._has_code_checkbox.setChecked(False)
    assert loader._code_combo.isVisible() is False


def test_loader_focus_moves_to_code_when_checkbox_marked(qtbot, loader):
    loader._has_code_checkbox.setChecked(True)
    qtbot.wait(50)
    assert loader._code_combo.hasFocus()


def test_typing_number_validates_and_shows_card_info(qtbot, loader):
    loader._number_input.setText("24")
    assert loader._name_input.text() == "LIONEL MESSI"
    assert "Nueva" in loader._status_label.text()


def test_invalid_number_shows_invalid_status(qtbot, loader):
    loader._number_input.setText("9999")
    assert "no existe" in loader._status_label.text().lower()
    assert loader._name_input.text() == ""


def test_existing_card_shows_repetida_status_with_quantity(
    qtbot, memory_db, loader, loader_collection
):
    InventoryService(memory_db).add_card(loader_collection.collection_id, DEFAULT_CODE, 24, 2)
    loader._number_input.setText("24")
    assert "Repetida" in loader._status_label.text()
    assert "2" in loader._status_label.text()


def test_new_card_shows_nueva_status(qtbot, loader):
    loader._number_input.setText("24")
    assert "Nueva" in loader._status_label.text()


def test_enter_in_number_focuses_qty(qtbot, loader):
    loader._number_input.setText("24")
    qtbot.keyClick(loader._number_input, Qt.Key.Key_Return)
    assert loader._qty_input.hasFocus()


def test_enter_in_qty_saves_card_alta(qtbot, memory_db, loader, loader_collection):
    loader._number_input.setText("24")
    loader._qty_input.setText("1")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)

    item = InventoryRepository(memory_db).get(loader_collection.collection_id, DEFAULT_CODE, 24)
    assert item is not None
    assert item.quantity == 1


def test_save_alta_increments_inventory(qtbot, memory_db, loader, loader_collection):
    loader._number_input.setText("24")
    loader._qty_input.setText("3")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(loader_collection.collection_id, DEFAULT_CODE, 24)
    assert item is not None
    assert item.quantity == 3


def test_enter_in_qty_saves_card_baja(qtbot, memory_db, loader, loader_collection):
    InventoryService(memory_db).add_card(loader_collection.collection_id, DEFAULT_CODE, 24, 5)
    loader._baja_radio.setChecked(True)
    loader._number_input.setText("24")
    loader._qty_input.setText("2")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(loader_collection.collection_id, DEFAULT_CODE, 24)
    assert item is not None
    assert item.quantity == 3


def test_save_baja_decrements_inventory(qtbot, memory_db, loader, loader_collection):
    InventoryService(memory_db).add_card(loader_collection.collection_id, DEFAULT_CODE, 24, 2)
    loader._baja_radio.setChecked(True)
    loader._number_input.setText("24")
    loader._qty_input.setText("1")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(loader_collection.collection_id, DEFAULT_CODE, 24)
    assert item is not None
    assert item.quantity == 1


def test_save_baja_when_zero_shows_error(qtbot, memory_db, loader):
    loader._baja_radio.setChecked(True)
    loader._number_input.setText("24")
    loader._qty_input.setText("1")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    # No hay inventario → error
    assert (
        "inventario" in loader._status_label.text().lower()
        or "insuficiente" in loader._status_label.text().lower()
    )


def test_form_resets_after_save(qtbot, loader):
    loader._number_input.setText("24")
    loader._qty_input.setText("2")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert loader._number_input.text() == ""
    assert loader._qty_input.text() == "1"
    assert loader._country_input.text() == ""
    assert loader._name_input.text() == ""


def test_focus_returns_to_first_field_after_save(qtbot, loader):
    loader._number_input.setText("24")
    loader._qty_input.setText("1")
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert loader._number_input.hasFocus()


def test_save_with_code_prefix_uses_combo_value(qtbot, memory_db, loader, loader_collection):
    """Marcar checkbox + elegir 'MR' + número '1' → guarda PAZ."""
    loader._has_code_checkbox.setChecked(True)
    # Setear el combo a "MR — Master Rookies" (index del combo)
    idx = loader._code_combo.findData("MR")
    loader._code_combo.setCurrentIndex(idx)
    loader._number_input.setText("1")
    assert loader._name_input.text() == "PAZ"
    qtbot.keyClick(loader._number_input, Qt.Key.Key_Return)
    qtbot.keyClick(loader._qty_input, Qt.Key.Key_Return)

    item = InventoryRepository(memory_db).get(loader_collection.collection_id, "MR", 1)
    assert item is not None
    assert item.quantity == 1


def test_set_active_collection_refreshes_combo(qtbot, memory_db, loader, sample_code_header):
    """Cambiar de colección refresca el combo y la visibilidad del checkbox."""
    free = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="OtherFree",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()
    loader.set_active_collection(free)
    assert loader._has_code_checkbox.isVisible() is False
