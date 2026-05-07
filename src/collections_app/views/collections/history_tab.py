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
"""

from __future__ import annotations

from PySide6.QtCore import Qt
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
from collections_app.core.models.transaction import OperationType

_HISTORY_LIMIT = 200
_HEADERS = ["Fecha", "Operación", "Card", "Cantidad"]


def _format_card_label(code_id: str, card_number: int, card_name: str) -> str:
    """Render compacto de identidad de card para el historial.

    Forma: 'CODE-NUM · nombre'. Si la card fue borrada y la transacción
    quedó huérfana (caso edge: el schema NO tiene CASCADE de cards →
    transactions), devuelve un placeholder con el id crudo.
    """
    return f"{code_id}-{card_number} · {card_name}"


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

    def refresh(self: HistoryTab) -> None:
        """Lee las últimas N transacciones + cards y repuebla la tabla."""
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id
        cards = self._ctx.cards.list_by_collection(cid)
        cards_by_id = {card.card_id: card for card in cards if card.card_id is not None}
        txns = self._ctx.transactions.list_by_collection(cid, limit=_HISTORY_LIMIT)

        # Suprimir repaints durante el llenado: ver justificación en
        # InventoryTab — alternating-row colors + setItem repetidos.
        self._table.setUpdatesEnabled(False)
        try:
            self._table.setRowCount(len(txns))
            for row, txn in enumerate(txns):
                card = cards_by_id.get(txn.card_id)
                if card is None:
                    card_label = self.tr("(card #{cid} eliminada)").format(cid=txn.card_id)
                else:
                    card_label = _format_card_label(card.code_id, card.card_number, card.card_name)
                op_label = self._operation_label(txn.operation)
                date_label = txn.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                self._set_row(row, date_label, op_label, card_label, txn.quantity)
        finally:
            self._table.setUpdatesEnabled(True)

    def set_active_collection(self: HistoryTab, collection: Collection) -> None:
        self._collection = collection
        self.refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _operation_label(self: HistoryTab, op: OperationType) -> str:
        return self.tr("Alta") if op is OperationType.ALTA else self.tr("Baja")

    def _set_row(
        self: HistoryTab,
        row: int,
        date: str,
        operation: str,
        card_label: str,
        quantity: int,
    ) -> None:
        cells = [
            QTableWidgetItem(date),
            QTableWidgetItem(operation),
            QTableWidgetItem(card_label),
            QTableWidgetItem(str(quantity)),
        ]
        cells[3].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        for col, cell in enumerate(cells):
            self._table.setItem(row, col, cell)
