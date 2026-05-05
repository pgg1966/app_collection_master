"""Tab Inventario: lista todas las cards del catálogo con su estado."""

import sqlite3

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.shared_ui.theme import Spacing

# Colores sutiles para las filas según estado
COLOR_OWNED = QColor("#FFFFFF")  # blanco normal
COLOR_REPEATED = QColor("#FFF8DC")  # crema claro
COLOR_MISSING = QColor("#F5F5F5")  # gris muy claro

STATUS_OWNED = "Tengo"
STATUS_REPEATED = "Repetida"
STATUS_MISSING = "Falta"

FILTER_ALL = "Todas"


class _StateFilterProxy(QSortFilterProxyModel):
    """Filtra por la combinación de estado, código y substring del nombre."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state_filter: str = FILTER_ALL
        self._code_filter: str = FILTER_ALL
        self._name_substring: str = ""
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_state_filter(self, state: str) -> None:
        self._state_filter = state
        self.invalidate()

    def set_code_filter(self, code: str) -> None:
        self._code_filter = code
        self.invalidate()

    def set_name_substring(self, text: str) -> None:
        self._name_substring = text.strip().lower()
        self.invalidate()

    def filterAcceptsRow(  # noqa: N802
        self,
        source_row: int,
        source_parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        del source_parent  # Modelo plano, ignoramos el parent
        model = self.sourceModel()
        code = model.index(source_row, InventoryView.COL_CODE).data() or ""
        name = (model.index(source_row, InventoryView.COL_NAME).data() or "").lower()
        state = model.index(source_row, InventoryView.COL_STATE).data() or ""

        if self._state_filter != FILTER_ALL and state != self._state_filter:
            return False
        if self._code_filter != FILTER_ALL and code != self._code_filter:
            return False
        return not (self._name_substring and self._name_substring not in name)


class InventoryView(QWidget):
    """Tab que lista todas las cards con su estado de inventario."""

    COL_CODE = 0
    COL_NUMBER = 1
    COL_NAME = 2
    COL_QUANTITY = 3
    COL_STATE = 4

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self._populate_code_filter()
        self.refresh()

    def refresh(self) -> None:
        self._populate_grid()
        self._update_status_bar()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # Crear modelos antes que los filtros que los referencian.
        self._grid_model = QStandardItemModel(0, 5, self)
        self._grid_model.setHorizontalHeaderLabels(
            [
                self.tr("Código"),
                self.tr("Número"),
                self.tr("Nombre"),
                self.tr("Cantidad"),
                self.tr("Estado"),
            ]
        )
        self._proxy = _StateFilterProxy(self)
        self._proxy.setSourceModel(self._grid_model)

        layout.addLayout(self._build_filter_row())

        self._grid_view = QTableView()
        self._grid_view.setModel(self._proxy)
        self._grid_view.setSortingEnabled(True)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setStretchLastSection(False)
        self._grid_view.horizontalHeader().setSectionResizeMode(
            self.COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        self._grid_view.sortByColumn(self.COL_CODE, Qt.SortOrder.AscendingOrder)
        layout.addWidget(self._grid_view, stretch=1)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def _build_filter_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        row.addWidget(QLabel(self.tr("Estado") + ":"))
        self._state_filter = QComboBox()
        self._state_filter.addItems([FILTER_ALL, STATUS_OWNED, STATUS_REPEATED, STATUS_MISSING])
        self._state_filter.currentTextChanged.connect(self._proxy.set_state_filter)
        row.addWidget(self._state_filter)

        row.addWidget(QLabel(self.tr("Código") + ":"))
        self._code_filter = QComboBox()
        self._populate_code_filter()
        self._code_filter.currentTextChanged.connect(self._proxy.set_code_filter)
        row.addWidget(self._code_filter)

        row.addWidget(QLabel(self.tr("Buscar") + ":"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self.tr("nombre…"))
        self._search_input.textChanged.connect(self._proxy.set_name_substring)
        row.addWidget(self._search_input, stretch=1)
        return row

    # ------------------------------------------------------------------
    # Población de combos / grilla
    # ------------------------------------------------------------------

    def _populate_code_filter(self) -> None:
        repo = CodesLinesRepository(self.conn)
        self._code_filter.blockSignals(True)
        self._code_filter.clear()
        self._code_filter.addItem(FILTER_ALL)
        for line in repo.list_by_header(self.collection.code_header_id):
            self._code_filter.addItem(line.code_id)
        self._code_filter.blockSignals(False)

    def _populate_grid(self) -> None:
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        cards = CardsRepository(self.conn).list_by_collection(cid)
        inv = InventoryRepository(self.conn)
        inv_by_key = {(i.code_id, i.card_number): i for i in inv.list_by_collection(cid)}

        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for card in cards:
            item = inv_by_key.get((card.code_id, card.card_number))
            qty = item.quantity if item else 0
            if qty == 0:
                state = STATUS_MISSING
                color = COLOR_MISSING
            elif qty == 1:
                state = STATUS_OWNED
                color = COLOR_OWNED
            else:
                state = STATUS_REPEATED
                color = COLOR_REPEATED

            row = [
                self._make_item(card.code_id, color),
                self._make_item(str(card.card_number), color, numeric=card.card_number),
                self._make_item(card.card_name, color),
                self._make_item(str(qty), color, numeric=qty),
                self._make_item(state, color),
            ]
            self._grid_model.appendRow(row)

    def _make_item(
        self,
        text: str,
        color: QColor,
        numeric: int | None = None,
    ) -> QStandardItem:
        item = QStandardItem(text)
        item.setEditable(False)
        item.setBackground(QBrush(color))
        if numeric is not None:
            # Para que el sort numérico funcione (no alfabético sobre strings)
            item.setData(numeric, Qt.ItemDataRole.UserRole + 1)
        return item

    # ------------------------------------------------------------------
    # Status bar inferior
    # ------------------------------------------------------------------

    def _update_status_bar(self) -> None:
        total = self._grid_model.rowCount()
        owned = 0
        repeated = 0
        for row in range(total):
            state = self._grid_model.item(row, self.COL_STATE).text()
            if state == STATUS_OWNED:
                owned += 1
            elif state == STATUS_REPEATED:
                repeated += 1
        owned_total = owned + repeated  # cards distintas con qty>0
        missing = total - owned_total
        pct = (owned_total / total * 100) if total > 0 else 0.0
        self._status_label.setText(
            self.tr(
                "Total: {total} cards | Tengo: {owned} ({pct:.1f}%) | "
                "Faltan: {missing} | Repetidas: {repeated}"
            ).format(
                total=total,
                owned=owned_total,
                pct=pct,
                missing=missing,
                repeated=repeated,
            )
        )
