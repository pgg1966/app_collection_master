"""Tests del CodesMasterDetailView."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.admin.codes_master_detail import (
    CodeHeaderEditDialog,
    CodeLineEditDialog,
    CodesMasterDetailView,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_codes() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        h1 = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        h2 = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="Magic", code_max_length=4)
        )
        assert h1.code_header_id is not None
        assert h2.code_header_id is not None
        for code, name, order in [
            ("ARG", "Argentina", 1),
            ("BRA", "Brasil", 2),
            ("FRA", "Francia", 3),
        ]:
            ctx.code_lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=h1.code_header_id,
                    code_id=code,
                    code_name=name,
                    code_order=order,
                )
            )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


def test_view_constructs_with_master_populated(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    assert view._master_list.count() == 2


def test_selecting_header_populates_detail(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    # Header WC tiene 3 codes, Magic tiene 0. Por defecto seleccionado el primero.
    selected = view._selected_header()
    assert selected is not None
    if selected.code_header_name == "WC":
        assert view._detail_table.rowCount() == 3
    else:
        assert view._detail_table.rowCount() == 0
        # Cambiar a WC.
        for row in range(view._master_list.count()):
            data = view._master_list.item(row).data(0x0100)  # ItemDataRole.UserRole
            if data.code_header_name == "WC":
                view._master_list.setCurrentRow(row)
                break
        assert view._detail_table.rowCount() == 3


def test_create_new_header_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    dialog = CodeHeaderEditDialog(ctx=ctx_with_codes)
    qtbot.addWidget(dialog)
    dialog._name_edit.setText("NewHeader")
    dialog._max_len_spin.setValue(2)
    dialog._on_accept()
    fetched = ctx_with_codes.code_headers.get_by_name("NewHeader")
    assert fetched is not None
    assert fetched.code_max_length == 2


def test_create_codeline_dialog_persists_with_max_length(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    h = ctx_with_codes.code_headers.get_by_name("WC")
    assert h is not None
    dialog = CodeLineEditDialog(ctx=ctx_with_codes, header=h)
    qtbot.addWidget(dialog)
    dialog._code_id_edit.setText("ITA")
    dialog._code_name_edit.setText("Italia")
    dialog._on_accept()
    line = ctx_with_codes.code_lines.lookup(h.code_header_id or 0, "ITA")
    assert line is not None
    assert line.code_name == "Italia"


def test_codeline_dialog_makes_code_id_readonly_in_edit(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    h = ctx_with_codes.code_headers.get_by_name("WC")
    assert h is not None
    line = ctx_with_codes.code_lines.list_by_header(h.code_header_id or 0)[0]
    dialog = CodeLineEditDialog(ctx=ctx_with_codes, header=h, line_to_edit=line)
    qtbot.addWidget(dialog)
    assert dialog._code_id_edit.isReadOnly() is True


def test_move_selected_swaps_order(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    # Seleccionar header WC.
    for row in range(view._master_list.count()):
        item = view._master_list.item(row)
        if item.data(0x0100).code_header_name == "WC":
            view._master_list.setCurrentRow(row)
            break
    # Detail debería tener: ARG (orden 1), BRA (2), FRA (3).
    view._detail_table.selectRow(0)  # ARG
    view._move_selected(+1)  # ARG baja → BRA primero
    h = ctx_with_codes.code_headers.get_by_name("WC")
    assert h is not None
    lines = ctx_with_codes.code_lines.list_by_header(h.code_header_id or 0)
    assert [line.code_id for line in lines] == ["BRA", "ARG", "FRA"]


def test_move_selected_at_top_does_nothing(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
) -> None:
    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    for row in range(view._master_list.count()):
        if view._master_list.item(row).data(0x0100).code_header_name == "WC":
            view._master_list.setCurrentRow(row)
            break
    view._detail_table.selectRow(0)
    view._move_selected(-1)  # ya está en el top
    h = ctx_with_codes.code_headers.get_by_name("WC")
    lines = ctx_with_codes.code_lines.list_by_header(h.code_header_id or 0)
    # Orden no cambió.
    assert [line.code_id for line in lines] == ["ARG", "BRA", "FRA"]


def test_delete_header_blocks_when_collection_uses_it(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Header con colección asociada → mensaje de error y NO se borra."""
    h = ctx_with_codes.code_headers.get_by_name("WC")
    assert h is not None
    ctx_with_codes.collections.create(
        Collection(
            collection_id=None,
            collection_name="UsesWC",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id or 0,
        )
    )
    ctx_with_codes.conn.commit()

    critical_messages: list[str] = []

    def fake_critical(_parent: object, _title: str, text: str) -> int:
        critical_messages.append(text)
        return 0

    monkeypatch.setattr(
        "collections_app.views.admin.codes_master_detail.QMessageBox.critical",
        fake_critical,
    )

    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    for row in range(view._master_list.count()):
        if view._master_list.item(row).data(0x0100).code_header_name == "WC":
            view._master_list.setCurrentRow(row)
            break
    view._on_delete_header()
    assert len(critical_messages) == 1
    assert "UsesWC" in critical_messages[0]
    # El header sigue existiendo.
    assert ctx_with_codes.code_headers.get_by_name("WC") is not None


def test_delete_codeline_with_confirmation(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_codes: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.views.admin.codes_master_detail.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.Yes,
    )
    view = CodesMasterDetailView(ctx=ctx_with_codes)
    qtbot.addWidget(view)
    for row in range(view._master_list.count()):
        if view._master_list.item(row).data(0x0100).code_header_name == "WC":
            view._master_list.setCurrentRow(row)
            break
    # Eliminar la primera fila (ARG).
    view._detail_table.selectRow(0)
    view._on_delete_line()
    h = ctx_with_codes.code_headers.get_by_name("WC")
    lines = ctx_with_codes.code_lines.list_by_header(h.code_header_id or 0)
    assert [line.code_id for line in lines] == ["BRA", "FRA"]
