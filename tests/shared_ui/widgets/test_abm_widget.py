"""Tests del AbmWidget genérico."""

from dataclasses import dataclass

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QMessageBox

from collections_app.shared_ui.widgets.abm_widget import (
    AbmConfig,
    AbmWidget,
    FieldDef,
    FieldType,
)

# ----------------------------------------------------------------------
# Modelos y store de prueba
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class FakeItem:
    """Modelo de prueba con PK auto-id."""

    item_id: int | None
    name: str
    quantity: int = 0


@dataclass(frozen=True)
class FakeCode:
    """Modelo de prueba con PK significativa de texto."""

    code_id: str
    code_name: str


class FakeStore:
    """Store en memoria para simular un repository."""

    def __init__(self) -> None:
        self.items: list[FakeItem] = []
        self._next_id = 1

    def list_all(self) -> list[FakeItem]:
        return list(self.items)

    def save(self, item: FakeItem) -> FakeItem:
        if item.item_id is None:
            saved = FakeItem(item_id=self._next_id, name=item.name, quantity=item.quantity)
            self._next_id += 1
            self.items.append(saved)
            return saved
        self.items = [it if it.item_id != item.item_id else item for it in self.items]
        return item

    def delete(self, item: FakeItem) -> bool:
        before = len(self.items)
        self.items = [it for it in self.items if it.item_id != item.item_id]
        return len(self.items) < before


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


def _build_item_config(store: FakeStore) -> AbmConfig:
    return AbmConfig(
        title="Items",
        module_code="ITM001",
        fields=[
            FieldDef(
                name="item_id",
                label="ID",
                field_type=FieldType.READONLY,
                is_id=True,
                is_required=False,
            ),
            FieldDef(name="name", label="Nombre", field_type=FieldType.TEXT),
            FieldDef(
                name="quantity",
                label="Cantidad",
                field_type=FieldType.INT,
                is_required=False,
            ),
        ],
        on_load_all=store.list_all,
        on_save=store.save,
        on_delete=store.delete,
        model_class=FakeItem,
        filter_field="name",
    )


def _build_code_config(store: list[FakeCode]) -> AbmConfig:
    return AbmConfig(
        title="Códigos",
        module_code="COD001",
        fields=[
            FieldDef(
                name="code_id",
                label="Código",
                field_type=FieldType.TEXT,
                is_id=True,
                max_length=3,
            ),
            FieldDef(name="code_name", label="Nombre", field_type=FieldType.TEXT),
        ],
        on_load_all=lambda: list(store),
        on_save=lambda c: store.append(c) or c,
        on_delete=lambda c: bool(store.remove(c)) or True,  # noqa: SIM222
        model_class=FakeCode,
    )


@pytest.fixture
def store() -> FakeStore:
    return FakeStore()


@pytest.fixture
def widget(qtbot, store):
    config = _build_item_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()
    qtbot.waitExposed(w)
    return w


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_abm_loads_records_into_grid(qtbot, store):
    store.save(FakeItem(None, "alpha", 1))
    store.save(FakeItem(None, "beta", 2))
    config = _build_item_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    assert w._grid_model.rowCount() == 2


def test_clicking_row_populates_form(qtbot, store, widget):
    store.save(FakeItem(None, "first", 5))
    widget.refresh()

    proxy_index = widget._proxy_model.index(0, 0)
    widget._grid_view.clicked.emit(proxy_index)

    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    assert name_input.text() == "first"


def test_save_new_record_appears_in_grid(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("nuevo")

    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1
    assert store.items[0].name == "nuevo"
    assert widget._grid_model.rowCount() == 1


def test_save_existing_record_updates_grid(qtbot, store, widget):
    saved = store.save(FakeItem(None, "old", 0))
    widget.refresh()

    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("updated")
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1
    assert store.items[0].name == "updated"
    assert store.items[0].item_id == saved.item_id


def test_filter_filters_grid_in_realtime(qtbot, store, widget):
    for n in ("apple", "banana", "apricot"):
        store.save(FakeItem(None, n, 0))
    widget.refresh()
    assert widget._proxy_model.rowCount() == 3

    widget._filter_input.setText("ap")
    assert widget._proxy_model.rowCount() == 2


def test_pk_field_is_readonly_when_editing_significant_id(qtbot):
    codes: list[FakeCode] = []
    config = _build_code_config(codes)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    codes.append(FakeCode("ARG", "Argentina"))
    w.refresh()
    w._grid_view.clicked.emit(w._proxy_model.index(0, 0))

    code_input = w._inputs["code_id"]
    assert isinstance(code_input, QLineEdit)
    assert code_input.isReadOnly() is True


def test_pk_field_is_editable_when_creating_significant_id(qtbot):
    codes: list[FakeCode] = []
    config = _build_code_config(codes)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    code_input = w._inputs["code_id"]
    assert isinstance(code_input, QLineEdit)
    assert code_input.isReadOnly() is False


def test_validation_failure_shows_status_message(qtbot, store):
    config = _build_item_config(store)
    config.on_validate = lambda _: (False, "razón inválida")
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    name_input = w._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("xx")
    qtbot.mouseClick(w._save_button, Qt.MouseButton.LeftButton)

    assert "razón inválida" in w._status_label.text()
    assert store.items == []  # no se guardó


def test_required_field_empty_blocks_save(qtbot, store, widget):
    # name está vacío y es required
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)
    assert "obligatorio" in widget._status_label.text().lower()
    assert store.items == []


def test_delete_with_confirmation_yes(qtbot, store, widget, monkeypatch):
    saved = store.save(FakeItem(None, "to_delete", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes)
    qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)

    assert saved not in store.items
    assert widget._grid_model.rowCount() == 0


def test_delete_with_confirmation_no(qtbot, store, widget, monkeypatch):
    store.save(FakeItem(None, "stay", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.No)
    qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1


def test_enter_in_last_field_focuses_save_button(qtbot, store, widget):
    name_input = widget._inputs["name"]
    quantity_input = widget._inputs["quantity"]

    name_input.setFocus()
    qtbot.keyClick(name_input, Qt.Key.Key_Return)
    assert quantity_input.hasFocus()

    qtbot.keyClick(quantity_input, Qt.Key.Key_Return)
    assert widget._save_button.hasFocus()


def test_record_saved_signal_emitted(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("emit-test")

    with qtbot.waitSignal(widget.record_saved, timeout=1000) as blocker:
        qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)
    saved = blocker.args[0]
    assert saved.name == "emit-test"
    assert saved.item_id is not None


def test_record_deleted_signal_emitted(qtbot, store, widget, monkeypatch):
    store.save(FakeItem(None, "del-emit", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes)
    with qtbot.waitSignal(widget.record_deleted, timeout=1000) as blocker:
        qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)
    deleted = blocker.args[0]
    assert deleted.name == "del-emit"


def test_clear_form_resets_inputs(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("dirty")
    widget.clear_form()
    assert name_input.text() == ""
    assert widget._current_record is None


def test_new_button_clears_form(qtbot, store, widget):
    store.save(FakeItem(None, "first", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))
    assert widget._current_record is not None
    qtbot.mouseClick(widget._new_button, Qt.MouseButton.LeftButton)
    assert widget._current_record is None
