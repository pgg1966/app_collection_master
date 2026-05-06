"""Tests del CollectionsAbmView."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.admin.collections_abm import (
    CollectionEditDialog,
    CollectionsAbmView,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_collections() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="H", code_max_length=3)
        )
        assert h.code_header_id is not None
        for name in ["Coll A", "Coll B"]:
            ctx.collections.create(
                Collection(
                    collection_id=None,
                    collection_name=name,
                    card_count=10,
                    requires_code=True,
                    code_field_name="País",
                    code_header_id=h.code_header_id,
                )
            )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


def test_view_constructs_and_lists_collections(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    assert view._list.count() == 2


def test_edit_dialog_updates_name(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    dialog._name_edit.setText("Renamed")
    dialog._on_accept()
    fetched = ctx_with_collections.collections.get_by_id(coll.collection_id or 0)
    assert fetched is not None
    assert fetched.collection_name == "Renamed"


def test_edit_dialog_disables_ok_when_name_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    from PySide6.QtWidgets import QDialogButtonBox

    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    ok = dialog._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok.isEnabled() is True
    dialog._name_edit.setText("")
    assert ok.isEnabled() is False


def test_edit_dialog_warns_on_requires_code_change_with_cards(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si hay cards y se cambia requires_code, pedir confirmación."""
    coll = ctx_with_collections.collections.list_all()[0]
    # Agregar una card.
    ctx_with_collections.cards.create(
        Card(
            card_id=None,
            collection_id=coll.collection_id or 0,
            code_id="X",
            card_number=1,
            card_name="Test",
        )
    )
    ctx_with_collections.conn.commit()

    asked: list[bool] = []

    def fake_question(*_a: object, **_k: object) -> int:
        asked.append(True)
        return QMessageBox.StandardButton.No

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        fake_question,
    )

    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    dialog._requires_code.setChecked(not coll.requires_code)
    dialog._on_accept()

    assert asked == [True]
    # Como respondió No, no se actualizó.
    fetched = ctx_with_collections.collections.get_by_id(coll.collection_id or 0)
    assert fetched is not None
    assert fetched.requires_code == coll.requires_code


def test_premium_field_is_readonly_label(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    """is_premium no debe ser editable en MVP."""
    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    # No hay un widget editable para is_premium.
    assert not hasattr(dialog, "_premium_checkbox")


def test_delete_collection_with_confirmation_removes_from_db(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.Yes,
    )
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    selected = view._selected()
    assert selected is not None
    cid = selected.collection_id

    view._on_delete()
    assert ctx_with_collections.collections.get_by_id(cid or 0) is None
    assert view._list.count() == 1


def test_delete_collection_cancelled_keeps_data(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.No,
    )
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    view._on_delete()
    assert view._list.count() == 2  # nada borrado
