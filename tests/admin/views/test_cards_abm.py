"""Tests del CardsAbmView."""

from PySide6.QtCore import Qt

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.core.models import CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)


def _seed(memory_db, sample_collection):
    """Inserta codes_lines necesarios para el header de la collection."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in ("ARG", "BRA"):
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()


def test_cards_view_initial_state(qtbot, memory_db):
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # Sin colecciones → no hay ABM montado, importar deshabilitado
    assert view._import_button.isEnabled() is False
    assert view._cards_widget is None


def test_cards_view_lists_collections_in_combo(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # combo: 1 placeholder + 1 colección
    assert view._collection_combo.count() == 2


def test_cards_view_rebuilds_abm_on_collection_change(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)  # procesa eventos pendientes antes del teardown
    assert view._cards_widget is not None
    assert view._import_button.isEnabled() is True


def test_cards_view_save_card(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)
    assert view._cards_widget is not None

    view._cards_widget._inputs["code_id"].setCurrentIndex(0)
    view._cards_widget._inputs["card_number"].setValue(7)
    view._cards_widget._inputs["card_name"].setText("Test Card")
    qtbot.mouseClick(view._cards_widget._save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    cards = CardsRepository(memory_db).list_by_collection(sample_collection.collection_id)
    assert len(cards) == 1
    assert cards[0].card_name == "Test Card"
    assert cards[0].collection_id == sample_collection.collection_id


def test_cards_combo_choices_use_codes_of_header(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)
    code_combo = view._cards_widget._inputs["code_id"]
    values = [code_combo.itemData(i) for i in range(code_combo.count())]
    assert set(values) == {"ARG", "BRA"}
