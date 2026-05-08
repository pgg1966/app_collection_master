"""Tab "Mis cards" — todo el catálogo de la colección con qty actual.

Filas con qty=0 se muestran en gris claro para que el usuario sepa
qué le falta. Sin filtros / búsqueda en MVP (queda en backlog).

Composición de datos sin agregar API al service: una sola query
a `inventory_service.list_owned(cid)` trae todas las cards con qty>0;
el resto se resuelve vía `dict.get(card_id, 0)` con default 0. Eso
cubre dos casos que el usuario ve idénticos (gris):

- Cards sin entry en `inventory` (nunca se les hizo alta).
- Cards con entry pero qty=0 (alta + baja al mismo total).

Implementación con `QTableView` + `QAbstractTableModel` (issue #002):
`QTableWidget` con `setItem` per cell post-cierre de modal exhibía
slowdown patológico (~7 minutos para 994 cards) por re-evaluación de
roles de paleta heredada en cada llamada. El refactor a Model/View
nativo de Qt evita ese path: las celdas se renderizan on-demand vía
`data()`, y un único `beginResetModel`/`endResetModel` reemplaza el
loop de N inserciones.
"""

from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QColor
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

_ZERO_QTY_COLOR = QColor("#A0A0A0")  # gris medio para filas sin stock
_HEADERS = ["Código", "Número", "Nombre", "Cantidad"]
_COL_CODE = 0
_COL_NUMBER = 1
_COL_NAME = 2
_COL_QTY = 3
_RIGHT_ALIGN = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


class InventoryTabModel(QAbstractTableModel):
    """Modelo de la tabla "Mis cards".

    Mantiene la lista de cards y un mapa qty_by_card_id en memoria.
    `set_data(...)` reemplaza ambos atómicamente con
    `beginResetModel/endResetModel` — el view se invalida y repinta
    una sola vez sin emitir signals por celda.
    """

    def __init__(self: InventoryTabModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cards: list[Card] = []
        self._qty_by_card_id: dict[int, int] = {}

    # ------------------------------------------------------------------
    # API requerida por QAbstractTableModel
    # ------------------------------------------------------------------

    def rowCount(  # noqa: N802  (Qt API casing)
        self: InventoryTabModel, parent: QModelIndex | None = None
    ) -> int:
        # Default `QModelIndex()` no se puede usar como argumento por
        # defecto (B008): construirlo cuando no llega explícito.
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else len(self._cards)

    def columnCount(  # noqa: N802
        self: InventoryTabModel, parent: QModelIndex | None = None
    ) -> int:
        parent = parent if parent is not None else QModelIndex()
        return 0 if parent.isValid() else len(_HEADERS)

    def data(
        self: InventoryTabModel,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if not index.isValid():
            return None
        row = index.row()
        if row < 0 or row >= len(self._cards):
            return None
        card = self._cards[row]
        col = index.column()
        qty = self._qty_by_card_id.get(card.card_id or 0, 0)

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_CODE:
                return card.code_id
            if col == _COL_NUMBER:
                return str(card.card_number)
            if col == _COL_NAME:
                return card.card_name
            if col == _COL_QTY:
                return str(qty)
            return None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (_COL_NUMBER, _COL_QTY):
                return _RIGHT_ALIGN
            return None

        if role == Qt.ItemDataRole.ForegroundRole:
            if qty == 0:
                return QBrush(_ZERO_QTY_COLOR)
            return None

        return None

    def headerData(  # noqa: N802
        self: InventoryTabModel,
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
        self: InventoryTabModel,
        cards: list[Card],
        qty_by_card_id: dict[int, int],
    ) -> None:
        """Reemplaza atómicamente las cards y el mapa de cantidades.

        `beginResetModel/endResetModel` invalida el view conectado sin
        emitir signals por celda — clave para evitar el bug del issue
        #002.
        """
        self.beginResetModel()
        self._cards = list(cards)
        self._qty_by_card_id = dict(qty_by_card_id)
        self.endResetModel()


class InventoryTab(QWidget):
    """Tab que lista todas las cards de la colección con su qty actual."""

    def __init__(
        self: InventoryTab,
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

    def _build_ui(self: InventoryTab) -> None:
        outer = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self._refresh_btn = QPushButton(self.tr("Refrescar"))
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)
        toolbar.addStretch()
        outer.addLayout(toolbar)

        self._model = InventoryTabModel(self)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(_COL_CODE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_NUMBER, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_QTY, QHeaderView.ResizeMode.ResizeToContents)
        outer.addWidget(self._table)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self: InventoryTab) -> None:
        """Vuelve a cargar cards + inventory desde la DB y repuebla la tabla."""
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id
        cards = self._ctx.cards.list_by_collection(cid)
        items = self._ctx.inventory.list_owned(cid)
        qty_by_card_id = {item.card_id: item.quantity for item in items}
        self._model.set_data(cards, qty_by_card_id)

    def set_active_collection(self: InventoryTab, collection: Collection) -> None:
        """Cambia la colección visible y refresca."""
        self._collection = collection
        self.refresh()
