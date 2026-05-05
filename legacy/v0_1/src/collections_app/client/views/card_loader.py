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
from collections.abc import Callable

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QStringListModel,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QIntValidator, QKeyEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCompleter,
    QFrame,
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
from collections_app.shared_ui.theme import (
    INPUT_BG_ALTA,
    INPUT_BG_BAJA,
    READONLY_BG,
    Spacing,
    StatusColor,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

logger = logging.getLogger(__name__)


class _EmptyFieldFilter(QObject):
    """Bloquea Tab/Backtab/Enter cuando el QLineEdit watched está vacío.

    Pensado para el campo de Código (cuando requires_code=True) y el de
    Número: el usuario no debería poder saltar al siguiente campo ni
    disparar el save sin haber tipeado nada. El filter:

    - Si la tecla es Tab, Backtab, Return o Enter Y el texto stripeado
      está vacío: llama `on_empty(field_name)` y CONSUME el evento
      (return True) — el foco no avanza, el handler suele mostrar
      un flash de borde rojo en el campo.
    - Si el texto NO está vacío: deja pasar el evento (return False)
      para que el resto de la cadena (EnterNavigator, returnPressed)
      lo maneje normalmente.
    """

    def __init__(
        self,
        field_name: str,
        get_text: Callable[[], str],
        on_empty: Callable[[str], None],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._field_name = field_name
        self._get_text = get_text
        self._on_empty = on_empty

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)
        if not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        if event.key() not in (
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backtab,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            return super().eventFilter(watched, event)
        if self._get_text().strip():
            # Hay texto → dejar pasar al navigator / returnPressed.
            return super().eventFilter(watched, event)
        # Campo vacío: feedback visual + consumir el evento (no avanzar).
        self._on_empty(self._field_name)
        return True


class _CodeOnlyCompleter(QCompleter):
    """QCompleter que muestra `"CODE - Name"` pero inserta solo `"CODE"`.

    Override de `pathFromIndex`: Qt llama este método para obtener el texto
    a insertar en el QLineEdit cuando el usuario activa una opción del
    popup (Enter, click). Por default retorna el item completo del modelo
    (`"FWC - OFFICIAL_TROPHY"`); este override devuelve solo la parte
    previa al `" - "`.

    Sin este override, activar un ítem del popup deja
    `"FWC - OFFICIAL_TROPHY"` en el campo. El handler `_on_code_selected`
    intenta limpiarlo después con `setText("FWC")`, pero el orden de los
    signals + el manejo de focus del completer hace que ese clean-up se
    pierda. Resolverlo en `pathFromIndex` evita el race entero.
    """

    def pathFromIndex(  # noqa: N802 — Qt naming
        self, index: QModelIndex | QPersistentModelIndex
    ) -> str:
        full: str = super().pathFromIndex(index)
        return full.split(" - ", 1)[0].strip()


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
        # esto es siempre False; el completer se llena con todos los codes_lines.
        self._has_ambiguity = False
        # Cache del último match unívoco (cuando requires_code=False y find_by_number
        # devolvió exactamente 1) para que `_save_card` use add_card_by_number sin
        # tener que volver a buscar.
        self._unambiguous_card: Card | None = None
        # Set de code_ids válidos en el contexto actual (uppercase). Se
        # repuebla en cada llamada a `_populate_completer_*`. Sirve para
        # validación rápida sin recorrer el modelo del completer.
        self._valid_code_ids: set[str] = set()
        # Code seleccionado y validado por el usuario. None mientras el
        # texto del LineEdit no sea un código conocido. Reemplaza el
        # `_get_selected_code` viejo basado en QComboBox.currentData.
        self._selected_code_id: str | None = None
        # Flag post-carga: cuando el usuario confirma una card, el foco
        # vuelve al SET con texto seleccionado y este flag queda True.
        # Si presiona Enter sin modificar el texto, el _on_code_return_pressed
        # salta directo al número manteniendo el código actual.
        # Cualquier edición del usuario (textEdited) lo desactiva.
        self._set_confirmed: bool = False

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
            self._populate_completer_with_all_codes()
            self._set_code_visible(True)
        else:
            self._clear_completer()
            self._set_code_visible(False)
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
        grid.addWidget(self._build_operation_row(), row, 1)
        row += 1

        # Campo de código: QLineEdit con QCompleter (autocompletado por
        # contains, case-insensitive). Las opciones del completer son
        # strings tipo "ARG - Argentina" para que el usuario pueda buscar
        # tanto por code_id como por nombre. Visibilidad según contexto:
        # con requires_code=True siempre visible; con requires_code=False
        # inicia oculto y solo aparece si find_by_number devuelve >1
        # (ambigüedad).
        self._code_label = QLabel((self.collection.code_field_name or self.tr("Código")) + ":")
        self._code_edit = QLineEdit()
        self._code_edit.setPlaceholderText(self.tr("Código (ej: ARG)"))
        self._code_edit.setMaxLength(10)
        # Subclass propio: Qt inserta solo el code_id ("FWC"), no el item
        # completo ("FWC - OFFICIAL_TROPHY"). Ver _CodeOnlyCompleter.
        self._completer = _CodeOnlyCompleter([], self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        # `QCompleter.activated` tiene dos sobrecargas (str y QModelIndex);
        # el wrapper filtra por tipo para que mypy strict acepte la conexión
        # sin la sintaxis `signal[str]` (no soportada en stubs de PySide6).
        self._completer.activated.connect(self._on_completer_activated)
        self._code_edit.setCompleter(self._completer)
        # textChanged: cualquier cambio (incluyendo setText programático).
        # Sirve para mantener `_selected_code_id` sincronizado.
        self._code_edit.textChanged.connect(self._on_code_text_changed)
        # textEdited: SOLO input del usuario (no setText). Sirve para
        # invalidar `_set_confirmed` (que se setea en post-carga vía
        # selectAll, sin que cuente como edición) y para refrescar el
        # highlight del primer ítem del popup tras cada tecla.
        self._code_edit.textEdited.connect(self._on_code_text_edited)
        self._code_edit.returnPressed.connect(self._on_code_return_pressed)
        # eventFilter para que Down/Up abran el popup del completer cuando
        # está cerrado — por default QLineEdit ignora esas teclas y el
        # popup solo navega cuando ya está visible.
        self._code_edit.installEventFilter(self)
        grid.addWidget(self._code_label, row, 0)
        grid.addWidget(self._code_edit, row, 1)
        row += 1

        if self.collection.requires_code:
            self._populate_completer_with_all_codes()
            self._set_code_visible(True)
        else:
            self._set_code_visible(False)

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

        # Tinte inicial del frame de operación según el modo activo (Alta).
        self._apply_input_mode_styling()

    def _build_operation_row(self) -> QFrame:
        """Frame contenedor de los radios Alta/Baja, coloreable por modo.

        Pintamos el QFrame (no los QLineEdit) — setStyleSheet sobre
        QLineEdits dispara polish-cycles que rompen los tests de foco
        en pytest-qt. El frame no es focusable, su repolish no afecta
        a nadie y el color sigue siendo bien visible (rodea Alta/Baja).
        """
        self._operation_frame = QFrame()
        self._operation_frame.setObjectName("operationFrame")
        layout = QHBoxLayout(self._operation_frame)
        layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS)
        self._alta_radio = QRadioButton(self.tr("&Alta"))
        self._baja_radio = QRadioButton(self.tr("&Baja"))
        self._alta_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self._alta_radio)
        group.addButton(self._baja_radio)
        # Conectamos ambos radios. `toggled` se dispara dos veces al
        # cambiar (False para el que se desmarca, True para el que se
        # marca). El handler usa un guard para actuar SOLO en True.
        self._alta_radio.toggled.connect(self._on_operation_changed)
        self._baja_radio.toggled.connect(self._on_operation_changed)
        layout.addWidget(self._alta_radio)
        layout.addWidget(self._baja_radio)
        layout.addStretch()
        return self._operation_frame

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
    # Code field: poblar completer / mostrar / leer / validar
    # ------------------------------------------------------------------

    def _populate_completer_with_all_codes(self) -> None:
        """Llena el completer con TODOS los codes_lines del header."""
        repo = CodesLinesRepository(self.conn)
        lines = repo.list_by_header(self.collection.code_header_id)
        self._set_completer_items([(line.code_id, line.code_name) for line in lines])

    def _populate_completer_with_ambiguous(self, matches: list[Card]) -> None:
        """Llena el completer con SOLO los códigos que matchearon en find_by_number."""
        items = [(card.code_id, self._lookup_code_name(card.code_id)) for card in matches]
        self._set_completer_items(items)

    def _set_completer_items(self, items: list[tuple[str, str]]) -> None:
        """Setea las opciones del completer + el set de validación."""
        self._valid_code_ids = {code_id.upper() for code_id, _ in items}
        completion_strings = [f"{code_id} - {name}" for code_id, name in items]
        model = QStringListModel(completion_strings, self)
        self._completer.setModel(model)
        self._code_edit.blockSignals(True)
        self._code_edit.clear()
        self._code_edit.blockSignals(False)
        self._selected_code_id = None

    def _clear_completer(self) -> None:
        """Vacía el completer y la selección (al cambiar a requires_code=False)."""
        self._valid_code_ids = set()
        self._completer.setModel(QStringListModel([], self))
        self._code_edit.blockSignals(True)
        self._code_edit.clear()
        self._code_edit.blockSignals(False)
        self._selected_code_id = None

    def _set_code_visible(self, visible: bool) -> None:
        self._code_label.setVisible(visible)
        self._code_edit.setVisible(visible)

    def _get_selected_code(self) -> str:
        """Lee el código seleccionado y validado (uppercase, "" si no hay)."""
        return self._selected_code_id or ""

    # ------------------------------------------------------------------
    # Code field: handlers de texto y selección
    # ------------------------------------------------------------------

    def _on_code_text_changed(self, _text: str) -> None:
        """Invalida la selección si el texto deja de matchear un código válido."""
        upper = self._code_edit.text().strip().upper()
        if upper not in self._valid_code_ids:
            self._selected_code_id = None
        else:
            # Match exacto: marcamos como seleccionado pero NO movemos el foco
            # (el usuario puede seguir escribiendo o presionar Enter después).
            self._selected_code_id = upper
        # Si estamos en modo `requires_code` o ambigüedad, recalcular el preview.
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _on_code_text_edited(self, _text: str) -> None:
        """Solo input del usuario: invalida `_set_confirmed` y refresca highlight.

        `textEdited` (a diferencia de `textChanged`) NO se dispara con
        `setText()` programático, así que el `selectAll()` de
        `_after_successful_load` no rompe el flag.
        """
        self._set_confirmed = False
        # El completer recién filtra el modelo después de que terminemos
        # con este slot — el QTimer.singleShot(0) garantiza que el
        # highlight se aplique sobre la lista ya filtrada.
        QTimer.singleShot(0, self._highlight_first_completion)

    def _highlight_first_completion(self) -> None:
        """Resalta el primer ítem del popup del completer si hay matches.

        Bloquear signals del completer durante `popup.setCurrentIndex` es
        crítico: sin eso, Qt interpreta el cambio de currentIndex como una
        "selección" y auto-inserta el `pathFromIndex` del ítem en el
        QLineEdit. Resultado visible: el usuario tipea "f", el popup
        resalta "FWC", y el campo termina con "FWC" (no "f"). Bloqueando
        el completer evitamos que ese slot interno corra.
        """
        if self._completer.completionCount() <= 0:
            return
        self._completer.setCurrentRow(0)
        popup = self._completer.popup()
        if popup is None:
            return
        self._completer.blockSignals(True)
        try:
            popup.setCurrentIndex(self._completer.currentIndex())
        finally:
            self._completer.blockSignals(False)

    def _on_completer_activated(self, value: object) -> None:
        """Slot del completer.activated que descarta el overload QModelIndex."""
        if isinstance(value, str):
            self._on_code_selected(value)

    def _on_code_selected(self, text: str) -> None:
        """El usuario eligió una opción del popup ("ARG - Argentina")."""
        code_id = text.split(" - ", 1)[0].strip().upper()
        if code_id not in self._valid_code_ids:
            return
        self._selected_code_id = code_id
        # Mostrar solo el code_id (sin el nombre) en el campo.
        self._code_edit.blockSignals(True)
        self._code_edit.setText(code_id)
        self._code_edit.blockSignals(False)
        # Mover foco al número y seleccionar lo que haya para overwrite rápido.
        self._number_input.setFocus()
        self._number_input.selectAll()
        # Refrescar preview ahora que el código quedó fijo.
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _on_code_return_pressed(self) -> None:
        """Enter en el campo de código: resolver según matches.

        - Si `_set_confirmed` y el texto coincide con `_selected_code_id`
          (post-carga sin edición): salta directo a número manteniendo
          el código actual.
        - 1 match exacto / único parcial → seleccionar y pasar foco a número.
        - >1 matches parciales → abrir popup del completer.
        - 0 matches → flash visual de borde rojo (1s).
        """
        text = self._code_edit.text().strip().upper()
        if not text:
            return
        # Atajo post-carga: el SET viene "confirmado" del último save y
        # el texto no se modificó → ir directo al número.
        if self._set_confirmed and text == (self._selected_code_id or ""):
            self._set_confirmed = False
            self._number_input.setFocus()
            self._number_input.selectAll()
            return
        # A partir de acá es un Enter normal de validación.
        self._set_confirmed = False
        if text in self._valid_code_ids:
            self._on_code_selected(text)
            return
        matches = sorted(c for c in self._valid_code_ids if text in c)
        if len(matches) == 1:
            self._on_code_selected(matches[0])
        elif len(matches) > 1:
            self._completer.setCompletionPrefix(text)
            self._completer.complete()
        else:
            self._flash_invalid_code()

    def _flash_invalid_code(self) -> None:
        """Borde rojo temporal en el campo de código (1s)."""
        self._show_field_error("code")

    def _show_field_error(self, field: str) -> None:
        """Aplica borde rojo al campo indicado y revierte tras 1s.

        Al revertir, reaplica el tinte del modo Alta/Baja para no perder
        el color de fondo. Usamos la sobrecarga `singleShot(msec, context,
        slot)` con `self` como context: si el widget se destruye antes
        de que el timer dispare (típico en tests cortos), Qt cancela el
        callback y no intenta tocar el C++ object liberado.
        """
        self._apply_field_styles(error_field=field)
        QTimer.singleShot(1000, self, lambda: self._apply_field_styles(error_field=None))

    # ------------------------------------------------------------------
    # Tinte Alta/Baja: frame de operación + campos editables
    # ------------------------------------------------------------------

    def _mode_bg_color(self) -> str:
        """Color pastel correspondiente al modo activo (alta/baja)."""
        return INPUT_BG_ALTA if self._alta_radio.isChecked() else INPUT_BG_BAJA

    def _on_operation_changed(self, checked: bool) -> None:
        """Slot del toggled de los radios Alta/Baja.

        Hace dos cosas: actualiza colores y mueve el foco al primer
        campo de entrada. El guard `if not checked` evita ejecutar dos
        veces (toggled emite False para el radio que se desmarca y True
        para el que se marca — solo nos interesa la transición a True).
        """
        if not checked:
            return
        self._apply_input_mode_styling()
        # Foco al primer campo activo + selectAll para que la próxima
        # tecla reemplace lo que haya (UX de carga rápida).
        target = self._first_active_input()
        target.setFocus()
        if isinstance(target, QLineEdit):
            target.selectAll()

    def _apply_input_mode_styling(self) -> None:
        """Pinta el frame de operación + los campos editables.

        El frame es recordatorio constante (rodea Alta/Baja). Los campos
        coloreados dan feedback visual donde el usuario está tipeando.
        Llamado al construir y al togglear el radio.
        """
        bg = self._mode_bg_color()
        self._operation_frame.setStyleSheet(
            f"#operationFrame {{ background-color: {bg}; border-radius: 4px; }}"
        )
        self._apply_field_styles(error_field=None)

    def _apply_field_styles(self, error_field: str | None = None) -> None:
        """Aplica el tinte del modo a los QLineEdits editables.

        `error_field` ∈ {"code", "number", "qty", None}: si está seteado,
        ese campo recibe borde rojo (el resto mantiene el tinte normal).
        Al expirar el flash de error se llama de nuevo con None para
        restaurar el color de fondo del modo activo.
        """
        bg = self._mode_bg_color()
        normal_style = f"QLineEdit {{ background-color: {bg}; }}"
        error_style = f"QLineEdit {{ background-color: {bg}; border: 1px solid red; }}"
        fields: dict[str, QLineEdit | None] = {
            "code": self._code_edit,
            "number": self._number_input,
            "qty": self._qty_input,
        }
        for name, widget in fields.items():
            if widget is None:
                continue
            widget.setStyleSheet(error_style if name == error_field else normal_style)

    # ------------------------------------------------------------------
    # Navegación y eventos
    # ------------------------------------------------------------------

    def _wire_navigator(self) -> None:
        self._navigator.uninstall()
        chain: list[QWidget] = []
        if self.collection.requires_code:
            chain = [self._code_edit, self._number_input, self._qty_input]
        elif self._has_ambiguity:
            # El número ya fue tipeado; saltarlo y ir directo a qty tras código.
            chain = [self._code_edit, self._qty_input]
        else:
            chain = [self._number_input, self._qty_input]
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_card
        self._navigator.install()
        # Empty-field guards: instalar DESPUÉS del navigator para que en la
        # cadena LIFO de eventFilters se ejecuten ANTES (consume Tab/Enter
        # cuando el campo está vacío y bloquea el avance al siguiente).
        self._install_empty_field_filters()

    def _install_empty_field_filters(self) -> None:
        """Bloquea Tab/Backtab/Enter en code_edit y number_input cuando vacíos."""
        # Removemos cualquier filtro previo para evitar duplicados al
        # reinstalarse el navigator. Mantenemos refs vivas en self para
        # evitar que el GC los libere mientras Qt los tiene apuntados.
        for attr in ("_code_empty_filter", "_number_empty_filter"):
            old = getattr(self, attr, None)
            if old is not None:
                # `removeEventFilter` es seguro aunque no esté instalado.
                target = self._code_edit if attr == "_code_empty_filter" else self._number_input
                target.removeEventFilter(old)
        self._code_empty_filter = _EmptyFieldFilter(
            "code", self._code_edit.text, self._show_field_error, self
        )
        self._number_empty_filter = _EmptyFieldFilter(
            "number", self._number_input.text, self._show_field_error, self
        )
        self._code_edit.installEventFilter(self._code_empty_filter)
        self._number_input.installEventFilter(self._number_empty_filter)

    def _first_active_input(self) -> QWidget:
        if self.collection.requires_code:
            return self._code_edit
        return self._number_input

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        # `_qty_input` se construye después de `_code_edit` y este filter
        # puede dispararse durante setup. Guard con getattr.
        qty_input = getattr(self, "_qty_input", None)
        if qty_input is not None and watched is qty_input and event.type() == QEvent.Type.FocusIn:
            qty_input.selectAll()
        # Up/Down sobre el code_edit: abrir popup del completer si no está
        # visible. Una vez abierto, el popup procesa las flechas nativamente.
        if (
            watched is self._code_edit
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up)
        ):
            popup = self._completer.popup()
            if popup is None or not popup.isVisible():
                # Prefijo vacío → muestra TODAS las opciones; con texto, filtra.
                self._completer.setCompletionPrefix(self._code_edit.text())
                self._completer.complete()
                return True
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

        # Ambigüedad: ofrecer el campo de código limitado a los matched
        self._unambiguous_card = None
        self._has_ambiguity = True
        self._populate_completer_with_ambiguous(matches)
        self._set_code_visible(True)
        self._wire_navigator()
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_status(
            self.tr("Hay {n} cards con número {num}, especificá el código").format(
                n=len(matches), num=number
            ),
            StatusColor.WARNING,
        )
        self._code_edit.setFocus()

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
            self._set_code_visible(False)
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

        if user_specified_code and not self._selected_code_id:
            # No hay código válido seleccionado: bloquear save y avisar
            # visualmente (mismo flash rojo que en _on_code_return_pressed).
            self._code_edit.setFocus()
            self._flash_invalid_code()
            self._set_status(self.tr("Falta código"), StatusColor.WARNING)
            return

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
        self._after_successful_load()
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

    def _after_successful_load(self) -> None:
        """Post-carga: limpia número/qty/preview y posiciona foco según contexto.

        Diferencia clave con `_reset_form`:
        - **`requires_code=True`**: NO limpia el SET — lo deja con el texto
          actual seleccionado (`selectAll`) y `_set_confirmed=True`. Esto
          permite que un Enter inmediato en el SET (sin tipear nada) salte
          al número manteniendo el código (flujo común: cargar varias
          cards del mismo set seguidas).
        - **`requires_code=False`**: igual que `_reset_form` — sale de
          modo ambigüedad y vuelve foco al primer input activo.
        """
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        self._unambiguous_card = None

        if self.collection.requires_code:
            # Mantener el SET actual seleccionado para edición rápida.
            # Si el usuario presiona Enter sin tipear, `_on_code_return_pressed`
            # detecta `_set_confirmed=True` y salta a número.
            self._code_edit.setFocus()
            self._code_edit.selectAll()
            self._set_confirmed = True
            return

        # Sin código: salir de ambigüedad si correspondía y foco al número.
        if self._has_ambiguity:
            self._has_ambiguity = False
            self._set_code_visible(False)
            self._clear_completer()
            self._wire_navigator()
        self._first_active_input().setFocus()

    def _reset_form(self) -> None:
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_confirmed = False
        if self.collection.requires_code:
            # Limpiar el campo de código para la próxima alta/baja, manteniendo
            # las opciones del completer (siguen siendo todos los codes_lines).
            self._code_edit.blockSignals(True)
            self._code_edit.clear()
            self._code_edit.blockSignals(False)
            self._selected_code_id = None
        else:
            # Salir del modo ambigüedad
            self._has_ambiguity = False
            self._set_code_visible(False)
            self._clear_completer()
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
