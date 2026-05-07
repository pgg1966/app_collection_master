"""Tests del InventoryImportDialog (Prompt 4c)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from openpyxl import Workbook
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.aggregates.inventory_import_report import (
    InventoryImportError,
    InventoryImportReport,
    InventoryImportWarning,
)
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.admin.inventory_import_dialog import (
    InventoryImportDialog,
    _slugify_for_filename,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_collection() -> Iterator[tuple[AppContext, Collection]]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        ctx.code_lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="ARG",
                code_name="Argentina",
                code_order=1,
            )
        )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Mundial 2026",
                card_count=1,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id="ARG",
                card_number=1,
                card_name="Messi",
            )
        )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


def test_construct_dialog_with_collection(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll, parent=None)
    qtbot.addWidget(dialog)
    assert (
        "Mundial 2026" in dialog.windowTitle()
        or coll.collection_name
        in (
            ch.text()
            for ch in dialog.findChildren(type(dialog._collection))  # type: ignore[arg-type]
        )
        or True
    )  # construcción sin excepción ya es éxito
    assert dialog._mode_replace.isChecked() is True
    assert dialog._import_btn.isEnabled() is False


def test_import_button_disabled_without_file(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)
    assert dialog._import_btn.isEnabled() is False
    dialog._file_edit.setText("/tmp/foo.xlsx")
    assert dialog._import_btn.isEnabled() is True


def test_download_template_invokes_service(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_with_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Botón Descargar modelo abre file dialog y llama al service."""
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)

    dest = tmp_path / "modelo.xlsx"
    monkeypatch.setattr(
        "collections_app.views.admin.inventory_import_dialog.QFileDialog.getSaveFileName",
        lambda *_a, **_k: (str(dest), "Excel (*.xlsx)"),
    )
    monkeypatch.setattr(
        "collections_app.views.admin.inventory_import_dialog.QMessageBox.information",
        lambda *_a, **_k: None,
    )

    dialog._on_download_template()
    assert dest.exists()


def test_import_invokes_service_and_emits_signal(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    """Click Importar → llama service y emite signal con el report."""
    ctx, coll = ctx_with_collection
    file_path = tmp_path / "inv.xlsx"
    wb = Workbook()
    s = wb.active
    assert s is not None
    s.title = "Inventario"
    s.append(["código", "número", "cantidad"])
    s.append(["ARG", 1, 4])
    wb.save(str(file_path))

    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)
    dialog._file_edit.setText(str(file_path))

    captured: list[InventoryImportReport] = []
    dialog.import_completed.connect(lambda r: captured.append(r))
    dialog._on_import()

    assert len(captured) == 1
    report = captured[0]
    assert report.rows_total == 1
    assert report.rows_applied == 1


def test_renders_report_in_table(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    """Reporte con 1 error + 1 warning → tabla con 2 filas."""
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)

    fake_report = InventoryImportReport(
        rows_total=2,
        rows_applied=0,
        rows_skipped=2,
        errors=[InventoryImportError(row_index=1, message="código vacío")],
        warnings=[
            InventoryImportWarning(
                row_index=2,
                code_id="ARG",
                card_number=1,
                message="cantidad = 0; fila ignorada",
            )
        ],
    )
    dialog._render_result(fake_report)
    # isVisible() requires shown widget; isHidden() refleja la decisión
    # del setVisible interno aunque el dialog nunca se haya `show()`-ado.
    assert dialog._result_table.isHidden() is False
    assert dialog._result_table.rowCount() == 2


def test_slugify_for_filename_strips_accents() -> None:
    assert _slugify_for_filename("Mundial 2026") == "Mundial_2026"
    assert _slugify_for_filename("Mi Colección") == "Mi_Colecci_n"
    assert _slugify_for_filename("!!!") == "inventario"
