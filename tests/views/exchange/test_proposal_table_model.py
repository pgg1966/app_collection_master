"""Tests del ExchangeProposalTableModel — lógica de checkboxes y selection.

TDD obligatorio: el modelo es lógica testeable (no es smoke de un
QDialog). Cubre:

- Forma de la tabla (filas/columnas).
- Render del identificador con/sin código (collection.requires_code).
- Estado inicial: todas las filas tildadas por default.
- `flags()`: solo la columna 0 es checkable, ninguna editable.
- `setData(role=CheckStateRole)` togglea la fila y emite `selection_changed`.
- `selected_rows()` retorna sólo las tildadas.
- `total_selected_quantity()` suma `proposed_quantity` de las tildadas.

No es un test de Qt visual; usa señales y métodos del QAbstractTableModel
sin necesidad de mostrar el widget.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QModelIndex, Qt

from collections_app.core.models.aggregates.exchange_proposal import (
    ProposedExchange,
)
from collections_app.views.exchange.proposal_table_model import (
    ExchangeProposalTableModel,
)


def _make_rows() -> tuple[ProposedExchange, ...]:
    return (
        ProposedExchange("ARG", 1, "Messi", 1, 2),
        ProposedExchange("ARG", 4, "Lautaro", 1, 1),
        ProposedExchange("BRA", 7, "Neymar", 1, 3),
    )


# ---------------------------------------------------------------------
# Forma de la tabla
# ---------------------------------------------------------------------


def test_model_has_three_columns() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    assert model.columnCount() == 3


def test_model_row_count_matches_rows() -> None:
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    assert model.rowCount() == len(rows)


def test_model_headers() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    headers = [
        model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        for c in range(model.columnCount())
    ]
    # Col 0 es checkbox: el header puede ser "" o algo corto, no asumimos texto.
    assert headers[1] == "Identificador"
    assert headers[2] == "Nombre"


# ---------------------------------------------------------------------
# Render del identificador
# ---------------------------------------------------------------------


def test_identifier_with_code_shows_code_and_number() -> None:
    """Con `requires_code=True`: 'ARG-1', 'BRA-7'."""
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    val0 = model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole)
    val2 = model.data(model.index(2, 1), Qt.ItemDataRole.DisplayRole)
    assert val0 == "ARG-1"
    assert val2 == "BRA-7"


def test_identifier_without_code_shows_only_number() -> None:
    """Con `requires_code=False`: solo el número."""
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=False)
    val0 = model.data(model.index(0, 1), Qt.ItemDataRole.DisplayRole)
    val1 = model.data(model.index(1, 1), Qt.ItemDataRole.DisplayRole)
    assert val0 == "1"
    assert val1 == "4"


def test_card_name_in_third_column() -> None:
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    assert model.data(model.index(0, 2), Qt.ItemDataRole.DisplayRole) == "Messi"
    assert model.data(model.index(1, 2), Qt.ItemDataRole.DisplayRole) == "Lautaro"


# ---------------------------------------------------------------------
# Estado inicial: todas tildadas
# ---------------------------------------------------------------------


def test_all_rows_checked_by_default() -> None:
    """Default: todas las filas tildadas."""
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    for row in range(model.rowCount()):
        state = model.data(model.index(row, 0), Qt.ItemDataRole.CheckStateRole)
        assert state == Qt.CheckState.Checked


# ---------------------------------------------------------------------
# Flags: solo col 0 checkable, nada editable
# ---------------------------------------------------------------------


def test_only_first_column_is_checkable() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    flags_col0 = model.flags(model.index(0, 0))
    flags_col1 = model.flags(model.index(0, 1))
    flags_col2 = model.flags(model.index(0, 2))
    assert bool(flags_col0 & Qt.ItemFlag.ItemIsUserCheckable)
    assert not bool(flags_col1 & Qt.ItemFlag.ItemIsUserCheckable)
    assert not bool(flags_col2 & Qt.ItemFlag.ItemIsUserCheckable)


def test_no_column_is_editable() -> None:
    """Solo el checkbox es editable; ninguna columna acepta edición de texto."""
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    for col in range(model.columnCount()):
        f = model.flags(model.index(0, col))
        assert not bool(f & Qt.ItemFlag.ItemIsEditable)


# ---------------------------------------------------------------------
# setData: toggle + signal
# ---------------------------------------------------------------------


def test_uncheck_row_via_setdata_returns_true() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    ok = model.setData(
        model.index(0, 0), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole
    )
    assert ok is True
    state = model.data(model.index(0, 0), Qt.ItemDataRole.CheckStateRole)
    assert state == Qt.CheckState.Unchecked


def test_setdata_emits_selection_changed(qtbot) -> None:  # type: ignore[no-untyped-def]
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    with qtbot.waitSignal(model.selection_changed, timeout=500):
        model.setData(
            model.index(0, 0),
            Qt.CheckState.Unchecked.value,
            Qt.ItemDataRole.CheckStateRole,
        )


def test_setdata_on_non_checkable_role_returns_false() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    ok = model.setData(model.index(0, 1), "X", Qt.ItemDataRole.EditRole)
    assert ok is False


def test_setdata_invalid_index_returns_false() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    ok = model.setData(QModelIndex(), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole)
    assert ok is False


# ---------------------------------------------------------------------
# selected_rows() y total_selected_quantity()
# ---------------------------------------------------------------------


def test_selected_rows_returns_all_when_all_checked() -> None:
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    assert model.selected_rows() == list(rows)


def test_selected_rows_excludes_unchecked() -> None:
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    model.setData(model.index(1, 0), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole)
    selected = model.selected_rows()
    assert selected == [rows[0], rows[2]]


def test_total_selected_quantity_with_all_checked() -> None:
    """Suma de `proposed_quantity` de filas tildadas."""
    rows = _make_rows()  # qtys: 1+1+1 = 3
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    assert model.total_selected_quantity() == 3


def test_total_selected_quantity_after_uncheck() -> None:
    rows = _make_rows()
    model = ExchangeProposalTableModel(rows=rows, requires_code=True)
    # Destildar 0 y 2 → solo queda fila 1, qty=1.
    model.setData(model.index(0, 0), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole)
    model.setData(model.index(2, 0), Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole)
    assert model.total_selected_quantity() == 1


def test_empty_rows_yields_zero_quantity() -> None:
    model = ExchangeProposalTableModel(rows=(), requires_code=True)
    assert model.rowCount() == 0
    assert model.selected_rows() == []
    assert model.total_selected_quantity() == 0


# ---------------------------------------------------------------------
# Casos de invalidez
# ---------------------------------------------------------------------


def test_data_invalid_index_returns_none() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    assert model.data(QModelIndex(), Qt.ItemDataRole.DisplayRole) is None


def test_data_unsupported_role_returns_none() -> None:
    model = ExchangeProposalTableModel(rows=_make_rows(), requires_code=True)
    # Un role que el modelo no provee.
    assert model.data(model.index(0, 1), Qt.ItemDataRole.ToolTipRole) is None


# ---------------------------------------------------------------------
# Marcadores pytest
# ---------------------------------------------------------------------

pytestmark = pytest.mark.gui
