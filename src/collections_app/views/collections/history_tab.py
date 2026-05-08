"""Tab "Historial" — bitácora de altas/bajas con trazabilidad granular.

La prueba arquitectónica del rewrite: cada `Transaction` tiene FK
directo a `card_id` (no solo a `collection_id` como en v0.1), así que
podemos mostrar **a qué card específica** corresponde cada movimiento.
La columna "Card" renderiza `CODE-NUM · nombre` para que el usuario
identifique sin ambigüedad.

Composición de datos: el service expone solo el id de la card en cada
transacción. Para no hacer N queries al render, se carga una sola vez
el listado de cards de la colección y se arma un `dict[card_id, Card]`
local; la columna se compone por lookup en ese dict. Pre-Mundial es
suficiente; si los volúmenes crecen, se pasa a un JOIN dedicado en el
repo (queda en backlog post-Mundial).

Implementación con `QTableView` + `QAbstractTableModel` por consistencia
con InventoryTab (commit `fdb2c2c`, fix del issue #002). HistoryTab no
disparaba el bug en la práctica (datasets chicos por el cap de 200
transacciones) pero se alinea al patrón Model/View nativo de Qt para
preparar el camino del resto de la UI.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.card import Card
from collections_app.core.models.collection import Collection
from collections_app.core.models.transaction import OperationType, Transaction

_HISTORY_LIMIT = 200
_HEADERS = ["Fecha", "Operación", "Card", "Cantidad"]
_COL_DATE = 0
_COL_OP = 1
_COL_CARD = 2
_COL_QTY = 3
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_RIGHT_ALIGN = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


def _format_card_label(code_id: str, card_number: int, card_name: str) -> str:
    """Render compacto de identidad de card para el historial.

    Forma: 'CODE-NUM · nombre'. Si la card fue borrada y la transacción
    quedó huérfana (caso edge: el schema NO tiene CASCADE de cards →
    transactions), el modelo devuelve un placeholder con el id crudo.
    """
    return f"{code_id}-{card_number} · {card_name}"


class HistoryTabModel(QAbstractTableModel):
    """Modelo de la tabla "Historial".

    Mantiene la lista de transacciones y un mapa cards_by_id para
    componer la columna `Card`. `set_data(...)` reemplaza ambos
    atómicamente con `beginResetModel/endResetModel`.
    """

    def __init__(self: HistoryTabModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._txns: list[Transaction] = []
        self._cards_by_id: dict[int, Card] = {}

    # ------------------------------------------------------------------
    # API requerida por QAbstractTableModel
    # ------------------------------------------------------------------

    def rowCount(  # noqa: N802  (Qt API casing)
        self: HistoryTabModel, parent: QModelIndex | None = None
    ) -> int:
        # Default `QModelIndex()` no se puede usar como argumento por
        # defecto (B008): construirlo cuando no llega explícito.
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else len(self._txns)

    def columnCount(  # noqa: N802
        self: HistoryTabModel, parent: QModelIndex | None = None
    ) -> int:
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else len(_HEADERS)

    def data(
        self: HistoryTabModel,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._txns):
            return None
        txn = self._txns[row]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_DATE:
                return txn.transaction_date.strftime(_DATE_FORMAT)
            if col == _COL_OP:
                return self.tr("Alta") if txn.operation is OperationType.ALTA else self.tr("Baja")
            if col == _COL_CARD:
                card = self._cards_by_id.get(txn.card_id)
                if card is None:
                    return self.tr("(card #{cid} eliminada)").format(cid=txn.card_id)
                return _format_card_label(card.code_id, card.card_number, card.card_name)
            if col == _COL_QTY:
                return str(txn.quantity)
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col == _COL_QTY:
                return _RIGHT_ALIGN
            return None

        return None

    def headerData(  # noqa: N802
        self: HistoryTabModel,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and 0 <= section < len(_HEADERS)
        ):
            return _HEADERS[section]
        return None

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_data(
        self: HistoryTabModel,
        txns: list[Transaction],
        cards_by_id: dict[int, Card],
    ) -> None:
        """Reemplaza atómicamente las transacciones y el mapa de cards.

        `beginResetModel/endResetModel` invalida el view conectado sin
        emitir signals por celda — alineado al patrón de InventoryTab
        (issue #002).
        """
        self.beginResetModel()
        self._txns = list(txns)
        self._cards_by_id = dict(cards_by_id)
        self.endResetModel()


class HistoryTab(QWidget):
    """Tab que lista las últimas N transacciones de la colección."""

    def __init__(
        self: HistoryTab,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: HistoryTab) -> None:
        outer = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self._refresh_btn = QPushButton(self.tr("Refrescar"))
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)
        toolbar.addStretch()
        outer.addLayout(toolbar)

        self._model = HistoryTabModel(self)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(_COL_DATE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_OP, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_CARD, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_QTY, QHeaderView.ResizeMode.ResizeToContents)
        outer.addWidget(self._table)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self: HistoryTab) -> None:
        """Lee las últimas N transacciones + cards y repuebla la tabla."""
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id
        cards = self._ctx.cards.list_by_collection(cid)
        cards_by_id = {c.card_id: c for c in cards if c.card_id is not None}
        txns = self._ctx.transactions.list_by_collection(cid, limit=_HISTORY_LIMIT)
        self._model.set_data(txns, cards_by_id)

    def set_active_collection(self: HistoryTab, collection: Collection) -> None:
        self._collection = collection
        self.refresh()
