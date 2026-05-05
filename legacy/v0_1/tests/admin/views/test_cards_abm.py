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


def test_collections_combo_reflects_new_collection(qtbot, memory_db, sample_collection):
    """Una colección creada después de instanciar el view aparece en el combo
    al llamar refresh_collections_combo (sin reiniciar)."""
    from collections_app.core.models import Collection
    from collections_app.core.repositories import CollectionsRepository

    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    initial_count = view._collection_combo.count()

    CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Nueva Colección",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_collection.code_header_id,
        )
    )
    memory_db.commit()

    view.refresh_collections_combo()
    assert view._collection_combo.count() == initial_count + 1
    labels = [view._collection_combo.itemText(i) for i in range(view._collection_combo.count())]
    assert "Nueva Colección" in labels


def test_collections_combo_handles_deleted_active_collection(qtbot, memory_db, sample_collection):
    """Si la colección activa se borra, el combo vuelve a (ninguna) y el
    AbmWidget queda deshabilitado."""
    from collections_app.core.repositories import CollectionsRepository

    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Selecciona la colección sample
    view._on_collection_changed(1)
    qtbot.wait(50)
    assert view._cards_widget is not None
    assert view._import_button.isEnabled() is True

    # Borra esa colección desde fuera y refresca
    CollectionsRepository(memory_db).delete(sample_collection.collection_id)
    memory_db.commit()
    view.refresh_collections_combo()
    qtbot.wait(50)

    assert view._collection_combo.currentData() is None
    assert view._cards_widget is None
    assert view._import_button.isEnabled() is False
    assert view._current_collection is None


def test_collections_combo_preserves_selection_on_refresh(qtbot, memory_db, sample_collection):
    """Si la colección activa sigue existiendo, refresh la mantiene."""
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)

    view.refresh_collections_combo()
    qtbot.wait(50)
    assert view._collection_combo.currentData() == sample_collection.collection_id
    assert view._current_collection is not None
    assert view._current_collection.collection_id == sample_collection.collection_id
