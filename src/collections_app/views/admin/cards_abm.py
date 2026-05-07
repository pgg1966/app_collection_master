"""ABM de cards de una colección.

Vista modal accesible desde "Administración → Cards...". Trae su propio
combo de colecciones (independiente del sidebar de la `MainWindow`),
así el usuario puede editar cualquier colección sin tener que cambiarla
en la UI principal.

Operaciones:
- Listar todas las cards de la colección activa.
- Filtrar client-side por code_id (combo) y por número/nombre (texto).
- Agregar / Editar via `CardEditDialog`.
- Eliminar con confirmación; cascade SQL borra el inventory y las
  transactions huérfanas (las transactions sin CASCADE bloquean delete
  → mensaje de error claro).

Refresh strategy: la vista se refresca a sí misma tras cada CRUD; no
emite signals — el caller (MainWindow) refresca los detail views
activos al cerrar el dialog (alternativa simple del plan).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.card import Card
from collections_app.core.models.collection import Collection
from collections_app.services.exceptions import CardsError

_HEADERS = ["Código", "Número", "Nombre"]
_FILTER_ALL = "(todos)"


class CardEditDialog(QDialog):
    """Dialog modal para crear o editar una card.

    Si `card_to_edit` es None, modo "crear". Si no, modo "editar".
    El service distingue: create() lanza CardsError si UNIQUE rompe;
    upsert() reemplaza si la business key ya existía. Para edit que
    cambia code_id+card_number, usamos delete viejo + create nuevo
    (operación compuesta) — pero MVP solo permite editar `card_name`,
    así que `code_id` y `card_number` quedan read-only en modo edit.
    """

    def __init__(
        self: CardEditDialog,
        ctx: AppContext,
        collection: Collection,
        card_to_edit: Card | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._card_to_edit = card_to_edit
        self.setWindowTitle(self.tr("Editar card") if card_to_edit else self.tr("Agregar card"))
        self._build_ui()
        self._update_ok_enabled()

    def _build_ui(self: CardEditDialog) -> None:
        outer = QVBoxLayout(self)
        form = QFormLayout()

        self._code_id_edit = QLineEdit()
        self._code_id_edit.setMaxLength(10)
        if self._card_to_edit is not None:
            self._code_id_edit.setText(self._card_to_edit.code_id)
            self._code_id_edit.setReadOnly(True)
        form.addRow(self.tr("Código"), self._code_id_edit)

        self._card_number_spin = QSpinBox()
        self._card_number_spin.setRange(1, 999_999)
        if self._card_to_edit is not None:
            self._card_number_spin.setValue(self._card_to_edit.card_number)
            self._card_number_spin.setReadOnly(True)
            self._card_number_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        form.addRow(self.tr("Número"), self._card_number_spin)

        self._card_name_edit = QLineEdit()
        if self._card_to_edit is not None:
            self._card_name_edit.setText(self._card_to_edit.card_name)
        self._card_name_edit.textChanged.connect(self._update_ok_enabled)
        self._code_id_edit.textChanged.connect(self._update_ok_enabled)
        form.addRow(self.tr("Nombre"), self._card_name_edit)

        outer.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        outer.addWidget(self._buttons)

    def _update_ok_enabled(self: CardEditDialog) -> None:
        ok_button = self._buttons.button(QDialogButtonBox.StandardButton.Ok)
        valid = bool(self._code_id_edit.text().strip()) and bool(
            self._card_name_edit.text().strip()
        )
        ok_button.setEnabled(valid)

    def _on_accept(self: CardEditDialog) -> None:
        assert self._collection.collection_id is not None
        card = Card(
            card_id=self._card_to_edit.card_id if self._card_to_edit else None,
            collection_id=self._collection.collection_id,
            code_id=self._code_id_edit.text().strip(),
            card_number=self._card_number_spin.value(),
            card_name=self._card_name_edit.text().strip(),
        )
        try:
            if self._card_to_edit is None:
                self._ctx.cards.create(card)
            else:
                self._ctx.cards.upsert(card)
            self._ctx.conn.commit()
        except CardsError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            return
        self.accept()


class CardsAbmView(QDialog):
    """ABM modal de cards. Se abre desde 'Administración → Cards...'."""

    def __init__(
        self: CardsAbmView,
        ctx: AppContext,
        initial_collection: Collection | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self.setWindowTitle(self.tr("Administración de cards"))
        self.resize(900, 600)
        self._all_cards: list[Card] = []
        self._build_ui()
        self._populate_collections(initial_collection)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: CardsAbmView) -> None:
        outer = QVBoxLayout(self)

        # Top bar: combo colección + filtros
        top = QHBoxLayout()
        top.addWidget(QLabel(self.tr("Colección:")))
        self._collection_combo = QComboBox()
        self._collection_combo.currentIndexChanged.connect(self._on_collection_changed)
        top.addWidget(self._collection_combo, 1)
        outer.addLayout(top)

        filters = QHBoxLayout()
        filters.addWidget(QLabel(self.tr("Filtro código:")))
        self._code_filter_combo = QComboBox()
        self._code_filter_combo.currentTextChanged.connect(self._refresh_table)
        filters.addWidget(self._code_filter_combo)
        filters.addSpacing(20)
        filters.addWidget(QLabel(self.tr("Buscar:")))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(self.tr("número o nombre"))
        self._search_edit.textChanged.connect(self._refresh_table)
        filters.addWidget(self._search_edit, 1)
        outer.addLayout(filters)

        # Tabla
        self._table = QTableWidget(0, len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        outer.addWidget(self._table, 1)

        # Botones
        btns = QHBoxLayout()
        self._add_btn = QPushButton(self.tr("Agregar"))
        self._add_btn.clicked.connect(self._on_add)
        self._edit_btn = QPushButton(self.tr("Editar"))
        self._edit_btn.clicked.connect(self._on_edit)
        self._delete_btn = QPushButton(self.tr("Eliminar"))
        self._delete_btn.clicked.connect(self._on_delete)
        self._close_btn = QPushButton(self.tr("Cerrar"))
        self._close_btn.clicked.connect(self.accept)
        btns.addWidget(self._add_btn)
        btns.addWidget(self._edit_btn)
        btns.addWidget(self._delete_btn)
        btns.addStretch()
        btns.addWidget(self._close_btn)
        outer.addLayout(btns)

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------

    def _populate_collections(self: CardsAbmView, initial: Collection | None) -> None:
        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        collections = self._ctx.collections.list_all()
        for coll in collections:
            self._collection_combo.addItem(coll.collection_name, coll)
        self._collection_combo.blockSignals(False)
        if initial is not None:
            for i in range(self._collection_combo.count()):
                if self._collection_combo.itemData(i).collection_id == initial.collection_id:
                    self._collection_combo.setCurrentIndex(i)
                    break
        self._on_collection_changed(self._collection_combo.currentIndex())

    def _on_collection_changed(self: CardsAbmView, _idx: int) -> None:
        coll = self._current_collection()
        if coll is None or coll.collection_id is None:
            self._all_cards = []
            self._refresh_code_filter()
            self._refresh_table()
            return
        self._all_cards = self._ctx.cards.list_by_collection(coll.collection_id)
        self._refresh_code_filter()
        self._refresh_table()

    def _current_collection(self: CardsAbmView) -> Collection | None:
        data = self._collection_combo.currentData()
        return data if isinstance(data, Collection) else None

    def _refresh_code_filter(self: CardsAbmView) -> None:
        self._code_filter_combo.blockSignals(True)
        self._code_filter_combo.clear()
        self._code_filter_combo.addItem(_FILTER_ALL)
        for code_id in sorted({c.code_id for c in self._all_cards}):
            self._code_filter_combo.addItem(code_id)
        self._code_filter_combo.blockSignals(False)

    def _refresh_table(self: CardsAbmView) -> None:
        filtered = self._filtered_cards()
        # Suprimir repaints intermedios: con `setAlternatingRowColors(True)`
        # cada setItem fuerza re-evaluación de paleta tras cerrar un
        # modal y la inserción degenera en O(N²).
        self._table.setUpdatesEnabled(False)
        try:
            self._table.setRowCount(len(filtered))
            for row, card in enumerate(filtered):
                self._table.setItem(row, 0, QTableWidgetItem(card.code_id))
                num_item = QTableWidgetItem(str(card.card_number))
                num_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(row, 1, num_item)
                name_item = QTableWidgetItem(card.card_name)
                # Guardamos la card completa en el item para recuperarla en edit/delete.
                name_item.setData(Qt.ItemDataRole.UserRole, card)
                self._table.setItem(row, 2, name_item)
        finally:
            self._table.setUpdatesEnabled(True)

    def _filtered_cards(self: CardsAbmView) -> list[Card]:
        code_filter = self._code_filter_combo.currentText()
        search = self._search_edit.text().strip().lower()
        out: list[Card] = []
        for card in self._all_cards:
            if code_filter != _FILTER_ALL and card.code_id != code_filter:
                continue
            if search:
                hay_in_number = search in str(card.card_number)
                hay_in_name = search in card.card_name.lower()
                if not (hay_in_number or hay_in_name):
                    continue
            out.append(card)
        return out

    def _selected_card(self: CardsAbmView) -> Card | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 2)
        if item is None:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data if isinstance(data, Card) else None

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_add(self: CardsAbmView) -> None:
        coll = self._current_collection()
        if coll is None:
            return
        dialog = CardEditDialog(ctx=self._ctx, collection=coll, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._on_collection_changed(self._collection_combo.currentIndex())

    def _on_edit(self: CardsAbmView) -> None:
        card = self._selected_card()
        coll = self._current_collection()
        if card is None or coll is None:
            QMessageBox.information(
                self,
                self.tr("Editar card"),
                self.tr("Seleccioná una card primero."),
            )
            return
        dialog = CardEditDialog(ctx=self._ctx, collection=coll, card_to_edit=card, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._on_collection_changed(self._collection_combo.currentIndex())

    def _on_delete(self: CardsAbmView) -> None:
        card = self._selected_card()
        if card is None or card.card_id is None:
            QMessageBox.information(
                self,
                self.tr("Eliminar card"),
                self.tr("Seleccioná una card primero."),
            )
            return
        confirm = QMessageBox.question(
            self,
            self.tr("Eliminar card"),
            self.tr(
                "¿Eliminar la card {code}-{num} «{name}»?\n"
                "El inventario asociado se borrará también."
            ).format(code=card.code_id, num=card.card_number, name=card.card_name),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self._ctx.cards.delete_by_id(card.card_id)
            self._ctx.conn.commit()
        except Exception as exc:  # FK violation por transactions sin CASCADE
            self._ctx.conn.rollback()
            QMessageBox.critical(
                self,
                self.tr("Error al eliminar"),
                self.tr(
                    "No se pudo eliminar la card.\n\n"
                    "Si tiene transacciones registradas en el historial, "
                    "no se puede borrar (queda como referencia para la "
                    "trazabilidad).\n\nDetalle: {msg}"
                ).format(msg=exc),
            )
            return
        self._on_collection_changed(self._collection_combo.currentIndex())
