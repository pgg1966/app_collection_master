"""Tab "Mis cards" — todo el catálogo de la colección con qty actual.

Filas con qty=0 se muestran en gris claro para que el usuario sepa
qué le falta. Sin filtros / búsqueda en MVP (queda en backlog).

Composición de datos sin agregar API al service: una sola query
a `inventory_service.list_owned(cid)` trae todas las cards con qty>0;
el resto se resuelve vía `dict.get(card_id, 0)` con default 0. Eso
cubre dos casos que el usuario ve idénticos (gris):

- Cards sin entry en `inventory` (nunca se les hizo alta).
- Cards con entry pero qty=0 (alta + baja al mismo total).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection

_ZERO_QTY_COLOR = QColor("#A0A0A0")  # gris medio para filas sin stock
_HEADERS = ["Código", "Número", "Nombre", "Cantidad"]


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

        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
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

        self._table.setRowCount(len(cards))
        for row, card in enumerate(cards):
            qty = qty_by_card_id.get(card.card_id or 0, 0)
            self._set_row(row, card.code_id, card.card_number, card.card_name, qty)

    def set_active_collection(self: InventoryTab, collection: Collection) -> None:
        """Cambia la colección visible y refresca."""
        self._collection = collection
        self.refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_row(
        self: InventoryTab,
        row: int,
        code_id: str,
        card_number: int,
        card_name: str,
        qty: int,
    ) -> None:
        cells = [
            QTableWidgetItem(code_id),
            QTableWidgetItem(str(card_number)),
            QTableWidgetItem(card_name),
            QTableWidgetItem(str(qty)),
        ]
        # qty alineada a la derecha; las primeras dos columnas también para
        # que código y número queden compactos.
        cells[1].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cells[3].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if qty == 0:
            grey = QBrush(_ZERO_QTY_COLOR)
            for cell in cells:
                cell.setForeground(grey)
        for col, cell in enumerate(cells):
            self._table.setItem(row, col, cell)
