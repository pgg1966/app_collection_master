"""Pantalla de carga rápida de cards: alta/baja con navegación por Enter.

Comportamiento según `Collection.requires_code`:

- `requires_code=True`: el campo Código siempre está visible y es
  obligatorio. Foco inicial en Código. Búsqueda exacta `(code, number)`.
- `requires_code=False`: solo se muestran Número y Cantidad. Foco inicial
  en Número. La búsqueda se hace con `CardsRepository.find_by_number`:
    * 0 matches → status "Número X no existe en esta colección".
    * 1 match → autocompleta país/nombre, status Nueva/Repetida.
    * >1 matches → muestra el combo de Código limitado a esos códigos
      ambiguos; status pide al usuario que especifique. Cuando el usuario
      elige uno, se valida exacto.
"""

import logging
import sqlite3

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QCompleter,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Card, Collection, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import AmbiguousCardError, InventoryService
from collections_app.shared_ui.theme import READONLY_BG, Spacing, StatusColor
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

logger = logging.getLogger(__name__)


class CardLoaderView(QWidget):
    """Pantalla principal del cliente: alta/baja rápida de cards."""

    # Emitida después de cada save exitoso. Las otras vistas (Inventario,
    # Estadísticas) la conectan para auto-refrescarse.
    card_changed = Signal()

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._navigator = EnterNavigator(self)
        # Estado: cuando hay >1 match en find_by_number, se ofrece al
        # usuario elegir el código entre los ambiguos. Con `requires_code=True`,
        # esto es siempre False; el combo se llena con todos los codes_lines.
        self._has_ambiguity = False
        # Cache del último match unívoco (cuando requires_code=False y find_by_number
        # devolvió exactamente 1) para que `_save_card` use add_card_by_number sin
        # tener que volver a buscar.
        self._unambiguous_card: Card | None = None

        self._build_ui()
        self._wire_navigator()
        focus_target = self._first_active_input()
        focus_target.setFocus()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        """Cambia la colección activa, reconfigurando la UI según `requires_code`."""
        self.collection = collection
        self._has_ambiguity = False
        self._unambiguous_card = None
        if collection.requires_code:
            self._populate_combo_with_all_codes()
            self._set_combo_visible(True)
        else:
            self._code_combo.clear()
            self._set_combo_visible(False)
        self._reset_form()

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)

        container = QWidget()
        container.setMaximumWidth(500)
        outer.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)

        grid = QGridLayout(container)
        grid.setHorizontalSpacing(Spacing.MD)
        grid.setVerticalSpacing(Spacing.SM)

        row = 0
        grid.addWidget(QLabel(self.tr("Operación") + ":"), row, 0)
        grid.addLayout(self._build_operation_row(), row, 1)
        row += 1

        # Combo de código: visibilidad según contexto. Con requires_code=True
        # siempre visible. Con requires_code=False inicia oculto y solo aparece
        # si find_by_number devuelve >1 (ambigüedad).
        self._code_label = QLabel((self.collection.code_field_name or self.tr("Código")) + ":")
        self._code_combo = QComboBox()
        self._code_combo.setEditable(True)
        self._code_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._code_combo.setCompleter(completer)
        self._code_combo.editTextChanged.connect(lambda _: self._on_code_changed())
        grid.addWidget(self._code_label, row, 0)
        grid.addWidget(self._code_combo, row, 1)
        row += 1

        if self.collection.requires_code:
            self._populate_combo_with_all_codes()
            self._set_combo_visible(True)
        else:
            self._set_combo_visible(False)

        grid.addWidget(QLabel(self.tr("Número") + ":"), row, 0)
        grid.addLayout(self._build_number_qty_row(), row, 1)
        row += 1

        country_label_text = self.collection.code_field_name or self.tr("País / Set")
        grid.addWidget(QLabel(country_label_text + ":"), row, 0)
        self._country_input = QLineEdit()
        self._country_input.setReadOnly(True)
        self._country_input.setStyleSheet(f"background-color: {READONLY_BG};")
        grid.addWidget(self._country_input, row, 1)
        row += 1

        grid.addWidget(QLabel(self.tr("Nombre") + ":"), row, 0)
        self._name_input = QLineEdit()
        self._name_input.setReadOnly(True)
        self._name_input.setStyleSheet(f"background-color: {READONLY_BG};")
        grid.addWidget(self._name_input, row, 1)
        row += 1

        self._status_label = QLabel("")
        self._status_label.setVisible(False)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()

    def _build_operation_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._alta_radio = QRadioButton(self.tr("&Alta"))
        self._baja_radio = QRadioButton(self.tr("&Baja"))
        self._alta_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self._alta_radio)
        group.addButton(self._baja_radio)
        row.addWidget(self._alta_radio)
        row.addWidget(self._baja_radio)
        row.addStretch()
        return row

    def _build_number_qty_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._number_input = QLineEdit()
        self._number_input.setValidator(QIntValidator(0, 99_999, self))
        self._number_input.setFixedWidth(100)
        self._number_input.textChanged.connect(lambda _: self._validate_card())
        row.addWidget(self._number_input)

        row.addWidget(QLabel(self.tr("Cantidad") + ":"))
        self._qty_input = QLineEdit("1")
        self._qty_input.setValidator(QIntValidator(1, 999, self))
        self._qty_input.setFixedWidth(70)
        self._qty_input.installEventFilter(self)
        row.addWidget(self._qty_input)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Combo: poblar / mostrar / leer
    # ------------------------------------------------------------------

    def _populate_combo_with_all_codes(self) -> None:
        """Llena el combo con TODOS los codes_lines del header de la colección."""
        repo = CodesLinesRepository(self.conn)
        lines = repo.list_by_header(self.collection.code_header_id)
        self._set_combo_items([(line.code_id, line.code_name) for line in lines])

    def _populate_combo_with_ambiguous(self, matches: list[Card]) -> None:
        """Llena el combo con SOLO los códigos que matchearon en find_by_number."""
        items = [(card.code_id, self._lookup_code_name(card.code_id)) for card in matches]
        self._set_combo_items(items)
        # Forzar al usuario a elegir
        self._code_combo.setCurrentIndex(-1)

    def _set_combo_items(self, items: list[tuple[str, str]]) -> None:
        self._code_combo.blockSignals(True)
        self._code_combo.clear()
        for code_id, code_name in items:
            self._code_combo.addItem(f"{code_id} — {code_name}", userData=code_id)
        self._code_combo.blockSignals(False)

    def _set_combo_visible(self, visible: bool) -> None:
        self._code_label.setVisible(visible)
        self._code_combo.setVisible(visible)

    def _get_selected_code(self) -> str:
        """Lee el código actual del combo (datos > texto)."""
        data = self._code_combo.currentData()
        if isinstance(data, str) and data:
            return data
        # El usuario tipeó algo no listado; intentar parsear "ARG — Argentina"
        text = self._code_combo.currentText().strip()
        if " — " in text:
            text = text.split(" — ", 1)[0].strip()
        return text.upper()

    # ------------------------------------------------------------------
    # Navegación y eventos
    # ------------------------------------------------------------------

    def _wire_navigator(self) -> None:
        self._navigator.uninstall()
        chain: list[QWidget] = []
        if self.collection.requires_code:
            chain = [self._code_combo, self._number_input, self._qty_input]
        elif self._has_ambiguity:
            # El número ya fue tipeado; saltarlo y ir directo a qty tras código.
            chain = [self._code_combo, self._qty_input]
        else:
            chain = [self._number_input, self._qty_input]
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_card
        self._navigator.install()

    def _first_active_input(self) -> QWidget:
        if self.collection.requires_code:
            return self._code_combo
        return self._number_input

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._qty_input and event.type() == QEvent.Type.FocusIn:
            self._qty_input.selectAll()
        return super().eventFilter(watched, event)

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def _on_code_changed(self) -> None:
        """Cuando el usuario cambia el combo (modo requires_code o ambigüedad)."""
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _validate_card(self) -> None:
        """Llamado al editar número o código."""
        number_text = self._number_input.text().strip()
        if not number_text:
            self._clear_info()
            return

        try:
            number = int(number_text)
        except ValueError:
            self._set_status(self.tr("Inválido"), StatusColor.WARNING)
            return

        if self.collection.requires_code:
            self._validate_with_code(number)
            return

        self._validate_by_number(number)

    def _validate_with_code(self, number: int) -> None:
        """Modo requires_code=True: búsqueda exacta `(code, number)`."""
        code = self._get_selected_code()
        if not code:
            return  # esperando que el usuario elija un código
        cards_repo = CardsRepository(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        card = cards_repo.get(cid, code, number)
        if card is None:
            self._country_input.setText("")
            self._name_input.setText("")
            self._set_status(
                self.tr("{code}-{n} no existe").format(code=code, n=number),
                StatusColor.WARNING,
            )
            return
        self._show_card_info(card)

    def _validate_by_number(self, number: int) -> None:
        """Modo requires_code=False: búsqueda por número con manejo de ambigüedad."""
        cards_repo = CardsRepository(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id

        if self._has_ambiguity:
            # El usuario ya está eligiendo un código del combo limitado:
            # validar exacto contra el código elegido.
            code = self._get_selected_code()
            if not code:
                return
            card = cards_repo.get(cid, code, number)
            if card is None:
                self._country_input.setText("")
                self._name_input.setText("")
                self._set_status(
                    self.tr("{code}-{n} no existe").format(code=code, n=number),
                    StatusColor.WARNING,
                )
                return
            self._show_card_info(card)
            return

        matches = cards_repo.find_by_number(cid, number)
        if not matches:
            self._clear_info()
            self._set_status(
                self.tr("Número {n} no existe en esta colección").format(n=number),
                StatusColor.WARNING,
            )
            return

        if len(matches) == 1:
            self._unambiguous_card = matches[0]
            self._show_card_info(matches[0])
            return

        # Ambigüedad: ofrecer combo limitado a los códigos matched
        self._unambiguous_card = None
        self._has_ambiguity = True
        self._populate_combo_with_ambiguous(matches)
        self._set_combo_visible(True)
        self._wire_navigator()
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_status(
            self.tr("Hay {n} cards con número {num}, especificá el código").format(
                n=len(matches), num=number
            ),
            StatusColor.WARNING,
        )
        self._code_combo.setFocus()

    def _show_card_info(self, card: Card) -> None:
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        self._country_input.setText(self._lookup_code_name(card.code_id))
        self._name_input.setText(card.card_name)
        item = InventoryRepository(self.conn).get(cid, card.code_id, card.card_number)
        if item is None or item.quantity == 0:
            self._set_status(self.tr("Nueva"), StatusColor.SUCCESS)
        else:
            self._set_status(
                self.tr("Repetida · tenés {n}").format(n=item.quantity),
                StatusColor.REPEATED,
            )

    def _clear_info(self) -> None:
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_status("", "")
        if not self.collection.requires_code and self._has_ambiguity:
            self._set_combo_visible(False)
            self._has_ambiguity = False
            self._wire_navigator()
        self._unambiguous_card = None

    def _lookup_code_name(self, code_id: str) -> str:
        line = CodesLinesRepository(self.conn).get(self.collection.code_header_id, code_id)
        return line.code_name if line else code_id

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save_card(self) -> None:
        number_text = self._number_input.text().strip()
        qty_text = self._qty_input.text().strip() or "1"
        if not number_text:
            self._set_status(self.tr("Falta número"), StatusColor.WARNING)
            return
        try:
            number = int(number_text)
            qty = int(qty_text)
        except ValueError:
            self._set_status(self.tr("Cantidad o número inválido"), StatusColor.WARNING)
            return
        if qty <= 0:
            self._set_status(self.tr("Cantidad debe ser positiva"), StatusColor.WARNING)
            return

        is_alta = self._alta_radio.isChecked()
        service = InventoryService(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id

        # Cuándo el usuario debió especificar un código:
        # - requires_code=True (siempre)
        # - hubo ambigüedad y el usuario eligió uno
        user_specified_code = self.collection.requires_code or self._has_ambiguity

        try:
            updated = self._dispatch_save(service, cid, number, qty, is_alta, user_specified_code)
        except AmbiguousCardError as exc:
            # Defensa: no debería pasar (la UI ya filtra), pero por las dudas.
            logger.warning("Ambigüedad inesperada al guardar: %d matches", len(exc.matches))
            self._set_status(
                self.tr("Hay {n} cards con ese número, especificá el código").format(
                    n=len(exc.matches)
                ),
                StatusColor.WARNING,
            )
            return
        except ValueError as exc:
            self._set_status(str(exc), StatusColor.ERROR)
            return

        op_label = self.tr("alta") if is_alta else self.tr("baja")
        self._set_status(
            self.tr("OK · {op} · ahora tenés {n}").format(op=op_label, n=updated.quantity),
            StatusColor.SUCCESS,
        )
        self._reset_form()
        self.card_changed.emit()

    def _dispatch_save(
        self,
        service: InventoryService,
        cid: int,
        number: int,
        qty: int,
        is_alta: bool,
        user_specified_code: bool,
    ) -> InventoryItem:
        if user_specified_code:
            code = self._get_selected_code()
            if not code:
                raise ValueError(self.tr("Falta código"))
            if is_alta:
                return service.add_card(cid, code, number, qty)
            return service.remove_card(cid, code, number, qty)
        if is_alta:
            return service.add_card_by_number(cid, number, qty)
        return service.remove_card_by_number(cid, number, qty)

    def _reset_form(self) -> None:
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        if not self.collection.requires_code:
            # Salir del modo ambigüedad
            self._has_ambiguity = False
            self._set_combo_visible(False)
            self._code_combo.clear()
        self._wire_navigator()
        self._unambiguous_card = None
        self._first_active_input().setFocus()

    def _set_status(self, message: str, color: str) -> None:
        if not message:
            self._status_label.setVisible(False)
            self._status_label.setText("")
            self._status_label.setStyleSheet("")
            return
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"border: 1px solid {color}; border-radius: 4px;"
            f" padding: 4px 8px; color: {color}; font-size: 11pt;"
        )
        self._status_label.setVisible(True)
