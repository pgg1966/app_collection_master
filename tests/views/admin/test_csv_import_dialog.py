"""Tests del CsvImportDialog (admin view)."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.views.admin.csv_import_dialog import (
    _ERRORS_DISPLAY_CAP,
    CsvImportDialog,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx() -> Iterator[AppContext]:
    c = create_app_context(":memory:")
    try:
        yield c
    finally:
        c.close()


def _write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def test_dialog_constructs_and_disables_import_when_inputs_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
) -> None:
    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    assert dialog._import_btn.isEnabled() is False


def test_dialog_enables_import_when_required_fields_filled(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
) -> None:
    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("My Coll")
    dialog._header_name.setText("My Header")
    assert dialog._import_btn.isEnabled() is True


def test_dialog_imports_codes_and_cards_and_emits_signal(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
    tmp_path: Path,
) -> None:
    """End-to-end: completar form, click Importar, signal emitido,
    DB con la collection y las cards."""
    codes_csv = tmp_path / "codes.csv"
    cards_csv = tmp_path / "cards.csv"
    _write_csv(
        codes_csv,
        ["code_id,code_name,code_order", "ARG,Argentina,1", "BRA,Brasil,2"],
    )
    _write_csv(
        cards_csv,
        ["code_id,card_number,card_name", "ARG,1,Messi", "BRA,1,Vinicius"],
    )

    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("WC2026")
    dialog._header_name.setText("WC")
    dialog._codes_path_edit.setText(str(codes_csv))
    dialog._cards_path_edit.setText(str(cards_csv))

    with qtbot.waitSignal(dialog.import_completed, timeout=2000) as blocker:
        dialog._on_import()

    reports = blocker.args[0]
    assert reports["codes"].rows_inserted == 2
    assert reports["cards"].rows_inserted == 2

    coll = ctx.collections.get_by_name("WC2026")
    assert coll is not None
    assert coll.collection_id is not None
    assert ctx.cards.count(coll.collection_id) == 2


def test_dialog_renders_errors_table_with_invalid_rows(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
    tmp_path: Path,
) -> None:
    """CSV con filas inválidas: la tabla de errores aparece y muestra Tipo+Fila+Mensaje."""
    cards_csv = tmp_path / "cards.csv"
    _write_csv(
        cards_csv,
        [
            "code_id,card_number,card_name",
            "ARG,1,Messi",  # ARG no existe → error
            "ARG,2,",  # name vacío + ARG no existe
        ],
    )
    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("Solo")
    dialog._header_name.setText("EmptyHeader")
    # Sin codes_csv: codes_lines vacío. Cards van a fallar el lookup de code_id.
    dialog._cards_path_edit.setText(str(cards_csv))
    dialog._on_import()

    # Tabla poblada con 2 filas (visibility no chequea para no requerir show()).
    assert dialog._errors_table.rowCount() == 2
    assert dialog._errors_table.isHidden() is False
    assert dialog._truncation_label.isHidden() is True


def test_dialog_truncates_errors_at_cap_with_warning(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
    tmp_path: Path,
) -> None:
    """Más de 200 errores: tabla muestra 200 + label de truncamiento."""
    n_rows = _ERRORS_DISPLAY_CAP + 50
    rows = ["code_id,card_number,card_name"] + [f"BAD,{i},name{i}" for i in range(n_rows)]
    cards_csv = tmp_path / "cards.csv"
    _write_csv(cards_csv, rows)

    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("Junk")
    dialog._header_name.setText("Junk")
    dialog._cards_path_edit.setText(str(cards_csv))
    dialog._on_import()

    assert dialog._errors_table.rowCount() == _ERRORS_DISPLAY_CAP
    assert dialog._truncation_label.isHidden() is False
    assert "Mostrando" in dialog._truncation_label.text()
    assert str(_ERRORS_DISPLAY_CAP) in dialog._truncation_label.text()


def test_dialog_warns_when_no_csv_selected(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin ningún CSV elegido, mostrar warning y NO importar."""
    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("Test")
    dialog._header_name.setText("Test")
    # Ambos paths quedan vacíos.

    warned = {"called": False}

    def fake_warning(*args: object, **kwargs: object) -> None:
        warned["called"] = True

    monkeypatch.setattr(
        "collections_app.views.admin.csv_import_dialog.QMessageBox.warning",
        fake_warning,
    )

    dialog._on_import()
    assert warned["called"] is True
    # No se pobló la tabla de errores.
    assert dialog._errors_table.rowCount() == 0


def test_dialog_creates_collection_in_db(
    qtbot,  # type: ignore[no-untyped-def]
    ctx: AppContext,
    tmp_path: Path,
) -> None:
    """El facade crea header + collection aunque solo se provea codes_csv."""
    codes_csv = tmp_path / "codes.csv"
    _write_csv(codes_csv, ["code_id,code_name,code_order", "ARG,Argentina,1"])

    dialog = CsvImportDialog(ctx=ctx)
    qtbot.addWidget(dialog)
    dialog._collection_name.setText("OnlyCodes")
    dialog._header_name.setText("OC")
    dialog._codes_path_edit.setText(str(codes_csv))
    dialog._on_import()

    assert ctx.code_headers.get_by_name("OC") is not None
    assert ctx.collections.get_by_name("OnlyCodes") is not None
