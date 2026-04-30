"""Tests del CardLoaderView.

Reescritos tras rediseño en el cual:
- Se removió el checkbox "Tiene código de prefijo".
- Se removió el DEFAULT_CODE = "NON" hardcodeado.
- requires_code=False → solo Número/Cantidad, búsqueda por find_by_number.
- requires_code=True → Código siempre obligatorio.
- Ambigüedad (>1 match en find_by_number) muestra combo limitado.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox

from collections_app.client.views.card_loader import CardLoaderView
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
def collection_no_code(memory_db, sample_code_header):
    """Collection con requires_code=False y cards de ejemplo.

    Los códigos del header son `ARG`, `BRA`, `MR`. Hay un número repetido
    (24) en ARG y BRA para tests de ambigüedad.
    """
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("MR", "MASTER ROOKIES")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Adrenalyne",
            card_count=100,
            requires_code=False,  # ← clave del nuevo diseño
            code_field_name=None,
            code_header_id=hid,
        )
    )
    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(col.collection_id, "ARG", 24, "LIONEL MESSI"))
    cards_repo.upsert(Card(col.collection_id, "BRA", 24, "VINICIUS"))  # ambiguo con ARG-24
    cards_repo.upsert(Card(col.collection_id, "ARG", 1, "GOLDEN BALLERS"))
    cards_repo.upsert(Card(col.collection_id, "MR", 5, "PAZ"))
    memory_db.commit()
    return col


@pytest.fixture
def collection_with_code(memory_db, sample_code_header):
    """Collection con requires_code=True (modo Stickers Panini)."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("S1", "Set 1"), ("S2", "Set 2")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Stickers",
            card_count=20,
            requires_code=True,
            code_field_name="Set",
            code_header_id=hid,
        )
    )
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S1", 1, "Sticker A"))
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S2", 1, "Sticker B"))
    memory_db.commit()
    return col


# ----------------------------------------------------------------------
# Tests de visibilidad y foco
# ----------------------------------------------------------------------


def test_no_checkbox_visible(qtbot, memory_db, collection_no_code):
    """El checkbox de prefijo ya no existe en ningún caso."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    checkboxes = view.findChildren(QCheckBox)
    assert checkboxes == []


def test_no_code_field_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_combo.isVisible() is False
    assert view._code_label.isVisible() is False


def test_code_field_always_visible_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_combo.isVisible() is True
    assert view._code_label.isVisible() is True


def test_focus_on_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._number_input.hasFocus()


def test_focus_on_code_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._code_combo.hasFocus()


# ----------------------------------------------------------------------
# Validación con find_by_number (requires_code=False)
# ----------------------------------------------------------------------


def test_find_by_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    """Con número único MR-5, autocompleta país/nombre y muestra Nueva."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    assert view._name_input.text() == "PAZ"
    assert "MASTER ROOKIES" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


def test_unknown_number_shows_clear_message(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("9999")
    assert "9999" in view._status_label.text()
    assert "no existe" in view._status_label.text().lower()
    assert view._name_input.text() == ""


def test_ambiguous_number_shows_code_selector(qtbot, memory_db, collection_no_code):
    """Número 24 está en ARG y BRA → debe mostrar combo y pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    assert view._has_ambiguity is True
    assert view._code_combo.isVisible() is True
    # El combo solo debe contener los códigos ambiguos (ARG y BRA, no MR)
    values = {view._code_combo.itemData(i) for i in range(view._code_combo.count())}
    assert values == {"ARG", "BRA"}
    assert (
        "especificá" in view._status_label.text().lower()
        or "especifica" in view._status_label.text().lower()
    )


def test_choosing_code_after_ambiguity_validates_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Elegir ARG en el combo
    idx = view._code_combo.findData("ARG")
    view._code_combo.setCurrentIndex(idx)
    assert view._name_input.text() == "LIONEL MESSI"
    assert "ARGENTINA" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


# ----------------------------------------------------------------------
# Save: dispatch correcto entre by_number y con código
# ----------------------------------------------------------------------


def test_save_uses_add_card_by_number_when_unambiguous(qtbot, memory_db, collection_no_code):
    """Caso Adrenalyn: número único → save sin pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_save_uses_add_card_when_user_specified_code(qtbot, memory_db, collection_no_code):
    """Tras desambiguar, el save usa el código elegido."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Ambigüedad: el combo aparece. Elegir BRA.
    idx = view._code_combo.findData("BRA")
    view._code_combo.setCurrentIndex(idx)
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item_arg = InventoryRepository(memory_db).get(collection_no_code.collection_id, "ARG", 24)
    item_bra = InventoryRepository(memory_db).get(collection_no_code.collection_id, "BRA", 24)
    assert item_arg is None or item_arg.quantity == 0
    assert item_bra is not None
    assert item_bra.quantity == 1


def test_save_alta_increments_inventory_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    view._qty_input.setText("3")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 3


def test_save_baja_decrements_inventory_correctly(qtbot, memory_db, collection_no_code):
    InventoryService(memory_db).add_card_by_number(collection_no_code.collection_id, 5, 3)
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._baja_radio.setChecked(True)
    view._number_input.setText("5")
    view._qty_input.setText("2")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_form_resets_after_save_keeping_focus(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._number_input.text() == ""
    assert view._qty_input.text() == "1"
    assert view._country_input.text() == ""
    assert view._number_input.hasFocus()


# ----------------------------------------------------------------------
# Regresión: bug original (NON-24 hardcodeado)
# ----------------------------------------------------------------------


def test_typing_number_24_finds_messi_in_adrenalyn_like_setup(qtbot, memory_db, collection_no_code):
    """Reproduce el bug: con requires_code=False, tipear '24' debe encontrar
    la card sin importar el código (vía find_by_number, no NON-24)."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # No debe decir "NON-24 no existe"; o muestra info (si fuera unívoco)
    # o pide desambiguar (este caso, es ambiguo).
    msg = view._status_label.text().lower()
    assert "non-24" not in msg
    assert "no existe" not in msg or "especificá" in msg
