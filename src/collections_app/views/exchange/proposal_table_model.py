"""Modelo de una grilla de la propuesta de intercambio (Prompt 5b).

Cada `ExchangeProposalDialog` muestra dos grillas (Necesito / Ofrezco)
y cada una usa una instancia de este modelo. El modelo es el único
componente con lógica testeable de los views nuevos: maneja el estado
de los checkboxes y expone helpers para el resumen al pie y el filtrado
de la propuesta antes de aplicarla.

Columnas (3 fijas, NO configurables):
    0. Checkbox (`Qt.CheckStateRole`, default `Checked`).
    1. Identificador: "{code_id}-{card_number}" si la colección usa
       códigos; sólo "{card_number}" si no.
    2. Nombre de la card.

No se muestra `proposed_quantity` ni `max_quantity` porque en el
matching actual `proposed_quantity` siempre vale 1 — agregar columnas
con "1" en cada fila es ruido visual. Si en el futuro la propuesta
incluye qty editables, este modelo crece con un delegate dedicado en
otra columna.

El único elemento editable de la fila es el checkbox. Las dos columnas
de display NO son editables (`flags()` las marca sin `ItemIsEditable`).

Signal `selection_changed` se emite cada vez que el usuario tilda o
destilda una fila, para que el dialog actualice el resumen al pie y
habilite/deshabilite el botón "Ejecutar".
"""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget

from collections_app.core.models.aggregates.exchange_proposal import (
    ProposedExchange,
)

_COL_CHECK = 0
_COL_IDENT = 1
_COL_NAME = 2
_COLUMN_COUNT = 3
_HEADERS = ("", "Identificador", "Nombre")


class ExchangeProposalTableModel(QAbstractTableModel):
    """Modelo de una de las dos grillas (Necesito / Ofrezco)."""

    selection_changed = Signal()

    def __init__(
        self: ExchangeProposalTableModel,
        rows: Sequence[ProposedExchange],
        *,
        requires_code: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._rows: list[ProposedExchange] = list(rows)
        self._requires_code = requires_code
        # Default: todas tildadas.
        self._checked: list[bool] = [True] * len(self._rows)

    # ------------------------------------------------------------------
    # API requerida por QAbstractTableModel
    # ------------------------------------------------------------------

    def rowCount(  # noqa: N802  (Qt API casing)
        self: ExchangeProposalTableModel,
        parent: QModelIndex | None = None,
    ) -> int:
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(  # noqa: N802
        self: ExchangeProposalTableModel,
        parent: QModelIndex | None = None,
    ) -> int:
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else _COLUMN_COUNT

    def data(
        self: ExchangeProposalTableModel,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if row < 0 or row >= len(self._rows):
            return None
        item = self._rows[row]

        if role == Qt.ItemDataRole.CheckStateRole and col == _COL_CHECK:
            return Qt.CheckState.Checked if self._checked[row] else Qt.CheckState.Unchecked

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_IDENT:
                if self._requires_code:
                    return f"{item.code_id}-{item.card_number}"
                return str(item.card_number)
            if col == _COL_NAME:
                return item.card_name

        return None

    def headerData(  # noqa: N802
        self: ExchangeProposalTableModel,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and 0 <= section < _COLUMN_COUNT
        ):
            return _HEADERS[section]
        return None

    def flags(self: ExchangeProposalTableModel, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        base = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == _COL_CHECK:
            return base | Qt.ItemFlag.ItemIsUserCheckable
        return base

    def setData(  # noqa: N802
        self: ExchangeProposalTableModel,
        index: QModelIndex,
        value: object,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid():
            return False
        if role != Qt.ItemDataRole.CheckStateRole or index.column() != _COL_CHECK:
            return False
        row = index.row()
        if row < 0 or row >= len(self._rows):
            return False
        # Qt manda `Qt.CheckState` o el `int` equivalente según binding.
        checked = value == Qt.CheckState.Checked or value == Qt.CheckState.Checked.value
        self._checked[row] = checked
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        self.selection_changed.emit()
        return True

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def selected_rows(self: ExchangeProposalTableModel) -> list[ProposedExchange]:
        """Filas con checkbox tildado, en el orden original."""
        return [r for r, ck in zip(self._rows, self._checked, strict=True) if ck]

    def total_selected_quantity(self: ExchangeProposalTableModel) -> int:
        """Suma de `proposed_quantity` de las filas tildadas."""
        return sum(
            r.proposed_quantity for r, ck in zip(self._rows, self._checked, strict=True) if ck
        )
