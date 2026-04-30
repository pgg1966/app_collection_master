"""Pantalla de carga rápida de cards: alta/baja con navegación por Enter."""

import logging
import sqlite3

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
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

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService
from collections_app.shared_ui.theme import READONLY_BG, Spacing, StatusColor
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

logger = logging.getLogger(__name__)

# Code "implícito" cuando la colección no usa prefijo o el checkbox está apagado.
DEFAULT_CODE = "NON"


class CardLoaderView(QWidget):
    """Pantalla principal del cliente: alta/baja rápida de cards.

    Layout vertical centrado, ancho máximo 500px.

    Si `collection.requires_code` es True, hay un checkbox "Tiene código de
    prefijo" que muestra un combo editable con autocompletado. Si está
    apagado (o la colección no requiere código), todas las cards usan
    `DEFAULT_CODE`.

    El flujo: tipear número → ver info de la card y status (Nueva/Repetida/
    Inválido) → Enter avanza a Cantidad → Enter en Cantidad guarda. Sin
    botón Guardar.
    """

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

        self._build_ui()
        self._wire_navigator()
        # Foco inicial en el campo activo apropiado
        focus_target = self._first_active_input()
        if focus_target is not None:
            focus_target.setFocus()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        """Cambia la colección activa, refrescando los choices del combo."""
        self.collection = collection
        self._refresh_code_combo()
        # Actualizar visibilidad del checkbox según requires_code
        self._has_code_checkbox.setVisible(collection.requires_code)
        if not collection.requires_code:
            self._has_code_checkbox.setChecked(False)
        self._update_code_field_visibility()

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
        # Operación (radio Alta/Baja)
        grid.addWidget(QLabel(self.tr("Operación") + ":"), row, 0)
        grid.addLayout(self._build_operation_row(), row, 1)
        row += 1

        # Checkbox "Tiene código de prefijo"
        cb_label = self.collection.code_field_name or self.tr("Tiene código de prefijo")
        self._has_code_checkbox = QCheckBox(self.tr("Tiene {name}").format(name=cb_label))
        self._has_code_checkbox.toggled.connect(self._on_checkbox_toggled)
        self._has_code_checkbox.setVisible(self.collection.requires_code)
        grid.addWidget(self._has_code_checkbox, row, 0, 1, 2)
        row += 1

        # Combo de código (oculto inicialmente)
        self._code_label = QLabel((self.collection.code_field_name or self.tr("Código")) + ":")
        self._code_combo = QComboBox()
        self._code_combo.setEditable(True)
        self._code_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = QCompleter()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._code_combo.setCompleter(completer)
        self._refresh_code_combo()
        # editTextChanged se dispara al tipear o al cambiar la selección.
        self._code_combo.editTextChanged.connect(lambda _: self._validate_card())
        grid.addWidget(self._code_label, row, 0)
        grid.addWidget(self._code_combo, row, 1)
        self._code_label.setVisible(False)
        self._code_combo.setVisible(False)
        row += 1

        # Número + Cantidad en la misma fila
        grid.addWidget(QLabel(self.tr("Número") + ":"), row, 0)
        grid.addLayout(self._build_number_qty_row(), row, 1)
        row += 1

        # Readonly: país y nombre
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

        # Status sutil debajo del container
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
    # Helpers de UI
    # ------------------------------------------------------------------

    def _refresh_code_combo(self) -> None:
        """Repuebla el combo de códigos desde codes_lines de la colección."""
        repo = CodesLinesRepository(self.conn)
        lines = repo.list_by_header(self.collection.code_header_id)
        # Filtrar el código DEFAULT_CODE (no se muestra al usuario)
        items = [(line.code_id, line.code_name) for line in lines if line.code_id != DEFAULT_CODE]

        self._code_combo.blockSignals(True)
        self._code_combo.clear()
        for code_id, code_name in items:
            label = f"{code_id} — {code_name}"
            self._code_combo.addItem(label, userData=code_id)
        self._code_combo.setEditText("")
        self._code_combo.blockSignals(False)

    def _on_checkbox_toggled(self, checked: bool) -> None:
        self._update_code_field_visibility()
        self._wire_navigator()
        target = self._code_combo if checked else self._number_input
        target.setFocus()

    def _update_code_field_visibility(self) -> None:
        visible = self.collection.requires_code and self._has_code_checkbox.isChecked()
        self._code_label.setVisible(visible)
        self._code_combo.setVisible(visible)

    def _wire_navigator(self) -> None:
        self._navigator.uninstall()
        chain: list[QWidget] = []
        if self.collection.requires_code and self._has_code_checkbox.isChecked():
            chain.append(self._code_combo)
        chain.append(self._number_input)
        chain.append(self._qty_input)
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_card
        self._navigator.install()

    def _first_active_input(self) -> QWidget:
        if self.collection.requires_code and self._has_code_checkbox.isChecked():
            return self._code_combo
        return self._number_input

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        # FocusIn en el qty_input → seleccionar todo para sobrescribir fácil
        if watched is self._qty_input and event.type() == QEvent.Type.FocusIn:
            self._qty_input.selectAll()
        return super().eventFilter(watched, event)

    # ------------------------------------------------------------------
    # Lógica: validar y guardar
    # ------------------------------------------------------------------

    def _get_current_code(self) -> str:
        if not (self.collection.requires_code and self._has_code_checkbox.isChecked()):
            return DEFAULT_CODE
        text = self._code_combo.currentText().strip()
        # El texto puede ser "ARG — Argentina" o solo "ARG" o lo que tipeó el user
        if " — " in text:
            text = text.split(" — ", 1)[0].strip()
        return text.upper()

    def _validate_card(self) -> None:
        """Llamado on KeyRelease en código o número."""
        number_text = self._number_input.text().strip()
        if not number_text:
            self._set_status("", "")
            self._country_input.setText("")
            self._name_input.setText("")
            return

        try:
            number = int(number_text)
        except ValueError:
            self._set_status(self.tr("Inválido"), StatusColor.WARNING)
            return

        code = self._get_current_code()
        if not code:
            self._set_status(self.tr("Falta código"), StatusColor.WARNING)
            return

        cards_repo = CardsRepository(self.conn)
        assert self.collection.collection_id is not None
        card = cards_repo.get(self.collection.collection_id, code, number)
        if card is None:
            self._country_input.setText("")
            self._name_input.setText("")
            self._set_status(
                self.tr("{code}-{n} no existe").format(code=code, n=number),
                StatusColor.WARNING,
            )
            return

        self._country_input.setText(self._lookup_code_name(code))
        self._name_input.setText(card.card_name)

        inv_repo = InventoryRepository(self.conn)
        item = inv_repo.get(self.collection.collection_id, code, number)
        if item is None or item.quantity == 0:
            self._set_status(self.tr("Nueva"), StatusColor.SUCCESS)
        else:
            self._set_status(
                self.tr("Repetida · tenés {n}").format(n=item.quantity),
                StatusColor.REPEATED,
            )

    def _lookup_code_name(self, code_id: str) -> str:
        line = CodesLinesRepository(self.conn).get(self.collection.code_header_id, code_id)
        return line.code_name if line else code_id

    def _save_card(self) -> None:
        """Llamado al hacer Enter en Cantidad."""
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

        code = self._get_current_code()
        is_alta = self._alta_radio.isChecked()
        service = InventoryService(self.conn)
        assert self.collection.collection_id is not None
        try:
            if is_alta:
                updated = service.add_card(self.collection.collection_id, code, number, qty)
            else:
                updated = service.remove_card(self.collection.collection_id, code, number, qty)
        except ValueError as exc:
            self._set_status(str(exc), StatusColor.ERROR)
            return

        op_label = self.tr("alta") if is_alta else self.tr("baja")
        self._set_status(
            self.tr("OK · {op} · ahora tenés {n}").format(op=op_label, n=updated.quantity),
            StatusColor.SUCCESS,
        )
        self._reset_form()

    def _reset_form(self) -> None:
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        # No tocar el código: si el usuario está cargando varias del mismo set,
        # mantenerlo le ahorra retipearlo. Si el checkbox está apagado, ni
        # siquiera hay combo visible.
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
