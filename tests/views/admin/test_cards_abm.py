"""Tests del CardsAbmView."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.admin.cards_abm import CardEditDialog, CardsAbmView

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_data() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        for code, name, order in [("ARG", "Argentina", 1), ("BRA", "Brasil", 2)]:
            ctx.code_lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=h.code_header_id,
                    code_id=code,
                    code_name=name,
                    code_order=order,
                )
            )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="WC2026",
                card_count=4,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        for code, num, name in [
            ("ARG", 1, "Messi"),
            ("ARG", 2, "Di María"),
            ("BRA", 1, "Vinicius"),
            ("BRA", 2, "Rodrygo"),
        ]:
            ctx.cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=num,
                    card_name=name,
                )
            )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


def test_view_constructs_and_shows_all_cards(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    view = CardsAbmView(ctx=ctx_with_data)
    qtbot.addWidget(view)
    assert view._table.rowCount() == 4


def test_filter_by_code_narrows_table(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    view = CardsAbmView(ctx=ctx_with_data)
    qtbot.addWidget(view)
    # Combo populado: (todos), ARG, BRA → 3 entries
    assert view._code_filter_combo.count() == 3
    view._code_filter_combo.setCurrentText("ARG")
    assert view._table.rowCount() == 2
    for row in range(view._table.rowCount()):
        assert view._table.item(row, 0).text() == "ARG"


def test_search_filters_by_name_or_number(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    view = CardsAbmView(ctx=ctx_with_data)
    qtbot.addWidget(view)

    view._search_edit.setText("messi")
    assert view._table.rowCount() == 1
    assert view._table.item(0, 2).text() == "Messi"

    view._search_edit.setText("2")  # número 2
    assert view._table.rowCount() == 2  # Di María (ARG-2) y Rodrygo (BRA-2)


def test_card_edit_dialog_creates_card(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    coll = ctx_with_data.collections.list_all()[0]
    dialog = CardEditDialog(ctx=ctx_with_data, collection=coll)
    qtbot.addWidget(dialog)
    dialog._code_id_edit.setText("ARG")
    dialog._card_number_spin.setValue(99)
    dialog._card_name_edit.setText("Test")
    dialog._on_accept()
    fetched = ctx_with_data.cards.lookup(coll.collection_id or 0, "ARG", 99)
    assert fetched is not None
    assert fetched.card_name == "Test"


def test_card_edit_dialog_disables_ok_when_fields_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    coll = ctx_with_data.collections.list_all()[0]
    dialog = CardEditDialog(ctx=ctx_with_data, collection=coll)
    qtbot.addWidget(dialog)
    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dialog._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is False
    dialog._code_id_edit.setText("X")
    dialog._card_name_edit.setText("Y")
    assert ok_btn.isEnabled() is True


def test_card_edit_dialog_makes_business_key_readonly_in_edit_mode(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
) -> None:
    coll = ctx_with_data.collections.list_all()[0]
    cards = ctx_with_data.cards.list_by_collection(coll.collection_id or 0)
    dialog = CardEditDialog(ctx=ctx_with_data, collection=coll, card_to_edit=cards[0])
    qtbot.addWidget(dialog)
    assert dialog._code_id_edit.isReadOnly() is True


def test_delete_card_removes_from_db(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(
        "collections_app.views.admin.cards_abm.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )
    view = CardsAbmView(ctx=ctx_with_data)
    qtbot.addWidget(view)
    # Selecciono la primera fila
    view._table.selectRow(0)
    selected = view._selected_card()
    assert selected is not None
    card_id = selected.card_id

    view._on_delete()
    assert ctx_with_data.cards.get_by_id(card_id or 0) is None
    assert view._table.rowCount() == 3


def test_delete_with_transactions_shows_error(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Card con transactions no se puede borrar (FK sin CASCADE)."""
    from PySide6.QtWidgets import QMessageBox

    coll = ctx_with_data.collections.list_all()[0]
    # Generar transaction sobre la primera card.
    ctx_with_data.inventory.add_card(coll.collection_id or 0, "ARG", 1, 1)
    ctx_with_data.conn.commit()

    monkeypatch.setattr(
        "collections_app.views.admin.cards_abm.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )
    critical_called: list[bool] = []
    monkeypatch.setattr(
        "collections_app.views.admin.cards_abm.QMessageBox.critical",
        lambda *a, **k: critical_called.append(True) or 0,
    )

    view = CardsAbmView(ctx=ctx_with_data)
    qtbot.addWidget(view)
    # Buscar la fila de ARG-1 (la que tiene transaction).
    for row in range(view._table.rowCount()):
        if view._table.item(row, 0).text() == "ARG" and view._table.item(row, 1).text() == "1":
            view._table.selectRow(row)
            break
    view._on_delete()
    assert critical_called == [True]
    # La card sigue en la DB (rollback).
    assert ctx_with_data.cards.lookup(coll.collection_id or 0, "ARG", 1) is not None
