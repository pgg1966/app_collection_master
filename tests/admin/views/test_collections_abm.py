"""Tests del CollectionsAbmView."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLineEdit

from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.core.repositories import CollectionsRepository


def test_collections_abm_loads(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # Sin colecciones todavía → grilla vacía
    assert view.abm._grid_model.rowCount() == 0


def test_collections_abm_save_creates_record(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Setear inputs mínimos válidos
    view.abm._inputs["collection_name"].setText("Test Collection")
    view.abm._inputs["card_count"].setValue(50)
    # Combo header: index 0 está poblado
    view.abm._inputs["code_header_id"].setCurrentIndex(0)

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)

    cols = CollectionsRepository(memory_db).list_all()
    assert len(cols) == 1
    assert cols[0].collection_name == "Test Collection"


def test_collections_abm_validate_requires_code_field_name(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    name_input = view.abm._inputs["collection_name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("Premium Collection")
    view.abm._inputs["card_count"].setValue(10)
    view.abm._inputs["code_header_id"].setCurrentIndex(0)
    requires_code = view.abm._inputs["requires_code"]
    assert isinstance(requires_code, QCheckBox)
    requires_code.setChecked(True)
    # code_field_name vacío → debería fallar validación

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    assert "etiqueta" in view.abm._status_label.text().lower()
    assert CollectionsRepository(memory_db).list_all() == []


def test_collections_abm_validate_premium_requires_license(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    view.abm._inputs["collection_name"].setText("Premium")
    view.abm._inputs["card_count"].setValue(10)
    view.abm._inputs["code_header_id"].setCurrentIndex(0)
    is_premium = view.abm._inputs["is_premium"]
    assert isinstance(is_premium, QCheckBox)
    is_premium.setChecked(True)
    # license_key_required vacío

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    assert "licencia" in view.abm._status_label.text().lower()
    assert CollectionsRepository(memory_db).list_all() == []
