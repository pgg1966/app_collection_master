"""Tab "Estadísticas" — avance por code para la colección activa.

Una sola tabla con `Code · Code Name · Total · Owned · % Avance` +
footer con totales globales. Datos vienen del aggregate `CodeStats`
ya calculado por `cards.get_stats_by_code(cid)` (Prompt 1).

Sin gráficos, sin charts, sin pie. Solo tabla — explicitado en el
prompt y stop conditions.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views._perf_log import plog  # TEMP perf diagnostic

_HEADERS = ["Código", "Nombre", "Total", "Mías", "% Avance"]


def _percentage(owned: int, total: int) -> float:
    """% de avance, con guard de división por cero. Cap a 100% si owned > total."""
    if total <= 0:
        return 0.0
    pct = (owned / total) * 100
    return min(pct, 100.0)


class StatsView(QWidget):
    """Tab de stats de avance por code."""

    def __init__(
        self: StatsView,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._build_ui()
        self.refresh()
        plog("StatsView.__init__: DONE")  # TEMP perf diagnostic

    def _build_ui(self: StatsView) -> None:
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
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        outer.addWidget(self._table, 1)

        self._footer_label = QLabel("")
        self._footer_label.setObjectName("statsFooter")
        font = self._footer_label.font()
        font.setBold(True)
        self._footer_label.setFont(font)
        outer.addWidget(self._footer_label)

    def refresh(self: StatsView) -> None:
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id
        stats = self._ctx.cards.get_stats_by_code(cid)
        total_cards = 0
        total_owned = 0
        # Suprimir repaints durante el llenado: ver justificación en InventoryTab.
        self._table.setUpdatesEnabled(False)
        try:
            self._table.setRowCount(len(stats))
            for row, s in enumerate(stats):
                self._table.setItem(row, 0, QTableWidgetItem(s.code_id))
                self._table.setItem(row, 1, QTableWidgetItem(s.code_name))
                total_item = QTableWidgetItem(str(s.total))
                total_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(row, 2, total_item)
                owned_item = QTableWidgetItem(str(s.owned))
                owned_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(row, 3, owned_item)
                pct_item = QTableWidgetItem(f"{_percentage(s.owned, s.total):.0f}%")
                pct_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(row, 4, pct_item)
                total_cards += s.total
                total_owned += s.owned
        finally:
            self._table.setUpdatesEnabled(True)
        self._footer_label.setText(
            self.tr("Total: {total} cards · Mías: {owned} · {pct:.0f}%").format(
                total=total_cards,
                owned=total_owned,
                pct=_percentage(total_owned, total_cards),
            )
        )

    def set_active_collection(self: StatsView, collection: Collection) -> None:
        self._collection = collection
        self.refresh()
