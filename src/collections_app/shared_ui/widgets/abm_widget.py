"""Widget genérico de ABM (alta/baja/modificación) parametrizable.

El widget se construye a partir de una `AbmConfig` que define los campos del
formulario, callbacks de persistencia y el `model_class` a instanciar. La idea
es escribir un ABM nuevo configurando, no copiando código.

Layout (de arriba a abajo):
    Header oscuro:   Módulo: {title} ({module_code})
    Filtro:          Buscar: [____________]
    Body horizontal: [Listado QTableView] | [Formulario QFormLayout]
    Botonera:        [Guardar] [Nuevo] [Eliminar]
    Status:          mensaje no-bloqueante (warn/error)
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from PySide6.QtCore import (
    QItemSelection,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.shared_ui.theme import (
    HEADER_BG,
    HEADER_FG,
    READONLY_BG,
    Spacing,
    StatusColor,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator


class FieldType(StrEnum):
    """Tipos de campo soportados por el ABM."""

    TEXT = "text"
    INT = "int"
    BOOL = "bool"
    COMBO = "combo"
    READONLY = "readonly"


# Tipo para choices de COMBO: lista estática o callable que la genera al vuelo.
ComboChoices = list[tuple[str, Any]] | Callable[[], list[tuple[str, Any]]]


@dataclass(frozen=True)
class FieldDef:
    """Definición de un campo del ABM.

    Attributes:
        name: nombre del atributo en el modelo.
        label: texto del label visible.
        field_type: tipo del input (ver `FieldType`).
        is_id: si True, forma parte de la PK.
        is_required: si True, no puede estar vacío al guardar.
        max_length: longitud máxima del input TEXT.
        combo_choices: opciones del combo. Puede ser una lista estática
            `[(label_visible, value), ...]` o un callable que la retorna.
            Pasá un callable cuando los choices dependen de datos que
            pueden cambiar después de instanciar el widget; entonces
            `refresh_combo_choices()` (o las acciones que llaman a
            `clear_form` / `_populate_form`) re-evalúan el callable.
        placeholder: placeholder del input TEXT.
        show_in_grid: si False, el campo no aparece en la grilla.
        grid_width: ancho fijo de la columna en la grilla (px), opcional.
    """

    name: str
    label: str
    field_type: FieldType
    is_id: bool = False
    is_required: bool = True
    max_length: int | None = None
    combo_choices: ComboChoices | None = None
    placeholder: str = ""
    show_in_grid: bool = True
    grid_width: int | None = None


@dataclass
class AbmConfig:
    """Configuración completa de un ABM.

    Los callbacks son responsabilidad del caller. Los repositories no
    commitean: si `on_save` u `on_delete` involucra DB, debe commitear.
    """

    title: str
    module_code: str
    fields: list[FieldDef]
    on_load_all: Callable[[], list[Any]]
    on_save: Callable[[Any], Any]
    on_delete: Callable[[Any], bool]
    model_class: type
    list_label: str = "Listado"
    edit_label: str = "Edición"
    filter_label: str = "Buscar"
    filter_field: str | None = None
    on_validate: Callable[[Any], tuple[bool, str]] | None = None
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


class AbmWidget(QWidget):
    """Widget genérico que implementa el patrón ABM (filtro + grilla + form)."""

    record_saved = Signal(object)
    record_deleted = Signal(object)
    grid_selection_changed = Signal(object)

    def __init__(self, config: AbmConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self._current_record: Any | None = None
        self._inputs: dict[str, QWidget] = {}
        self._grid_columns: list[FieldDef] = [f for f in config.fields if f.show_in_grid]
        self._id_fields: list[FieldDef] = [f for f in config.fields if f.is_id]
        self._navigator = EnterNavigator(self)

        self._build_ui()
        self._wire_navigator()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Recarga la grilla desde `on_load_all`."""
        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for rec in self.config.on_load_all():
            self._append_record_to_grid(rec)

    def select_record(self, record: Any) -> None:
        """Selecciona una fila específica y carga el form."""
        for row in range(self._grid_model.rowCount()):
            stored = self._grid_model.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if self._records_equal(stored, record):
                source_index = self._grid_model.index(row, 0)
                proxy_index = self._proxy_model.mapFromSource(source_index)
                self._grid_view.selectRow(proxy_index.row())
                self._current_record = stored
                self._populate_form(stored)
                return

    def clear_form(self) -> None:
        """Limpia el formulario para crear un registro nuevo.

        Antes de limpiar, re-evalúa los `combo_choices` que sean callables
        para reflejar cambios en otros tabs sin reconstruir el widget.
        """
        self.refresh_combo_choices()
        self._current_record = None
        self._grid_view.clearSelection()
        for fdef in self.config.fields:
            self._set_input_value(fdef, None)
        self._update_pk_editability()
        self._set_status("", "")
        first_editable = self._first_editable_input()
        if first_editable is not None:
            first_editable.setFocus()

    def refresh_combo_choices(self) -> None:
        """Re-popula los QComboBox del form llamando los callables.

        Preserva el valor seleccionado actual si todavía existe en los
        nuevos choices; si no, queda en el primer item (o vacío si no hay).
        Los `combo_choices` que son listas estáticas también se repueblan,
        pero no cambian — esto es seguro y mantiene la lógica simple.
        """
        for fdef in self.config.fields:
            if fdef.field_type != FieldType.COMBO:
                continue
            widget = self._inputs.get(fdef.name)
            if not isinstance(widget, QComboBox):
                continue
            previous = widget.currentData()
            new_choices = self._resolve_combo_choices(fdef)
            widget.blockSignals(True)
            widget.clear()
            for label, value in new_choices:
                widget.addItem(label, userData=value)
            if previous is not None:
                idx = widget.findData(previous)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            widget.blockSignals(False)

    def _resolve_combo_choices(self, fdef: FieldDef) -> list[tuple[str, Any]]:
        choices = fdef.combo_choices
        if choices is None:
            return []
        if callable(choices):
            return list(choices())
        return list(choices)

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_filter_row())
        root.addWidget(self._build_body(), stretch=1)
        root.addWidget(self._build_status_bar())

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet(
            f"background-color: {HEADER_BG}; color: {HEADER_FG};"
            f" padding: {Spacing.SM}px {Spacing.MD}px;"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        title = QLabel(
            self.tr("Módulo: {title} ({code})").format(
                title=self.config.title,
                code=self.config.module_code,
            )
        )
        title.setStyleSheet(f"color: {HEADER_FG}; font-weight: bold;")
        layout.addWidget(title)
        layout.addStretch()
        return header

    def _build_filter_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.addStretch()
        layout.addWidget(QLabel(self.tr(self.config.filter_label) + ":"))
        self._filter_input = QLineEdit()
        self._filter_input.setMinimumWidth(220)
        self._filter_input.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_input)
        return row

    def _build_body(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_grid_panel())
        splitter.addWidget(self._build_form_panel())
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        return splitter

    def _build_grid_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(Spacing.MD, Spacing.XS, Spacing.SM, Spacing.SM)

        layout.addWidget(QLabel(self.tr(self.config.list_label)))

        self._grid_model = QStandardItemModel(0, len(self._grid_columns), self)
        self._grid_model.setHorizontalHeaderLabels([self.tr(c.label) for c in self._grid_columns])

        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._grid_model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._configure_filter_column()

        self._grid_view = QTableView()
        self._grid_view.setModel(self._proxy_model)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setStretchLastSection(True)
        self._grid_view.clicked.connect(self._on_row_clicked)
        self._grid_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        for i, col in enumerate(self._grid_columns):
            if col.grid_width:
                self._grid_view.horizontalHeader().resizeSection(i, col.grid_width)
            else:
                self._grid_view.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Interactive
                )
        layout.addWidget(self._grid_view)
        return panel

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.MD, Spacing.SM)

        layout.addWidget(QLabel(self.tr(self.config.edit_label)))

        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        for fdef in self.config.fields:
            widget = self._build_input(fdef)
            self._inputs[fdef.name] = widget
            form.addRow(self.tr(fdef.label) + ":", widget)
        layout.addWidget(form_container)

        layout.addLayout(self._build_buttons())
        layout.addStretch()
        return panel

    def _build_input(self, fdef: FieldDef) -> QWidget:
        match fdef.field_type:
            case FieldType.TEXT | FieldType.READONLY:
                line = QLineEdit()
                if fdef.placeholder:
                    line.setPlaceholderText(fdef.placeholder)
                if fdef.max_length:
                    line.setMaxLength(fdef.max_length)
                if fdef.field_type == FieldType.READONLY:
                    line.setReadOnly(True)
                    line.setStyleSheet(f"background-color: {READONLY_BG};")
                return line
            case FieldType.INT:
                spin = QSpinBox()
                spin.setRange(0, 999_999)
                return spin
            case FieldType.BOOL:
                return QCheckBox()
            case FieldType.COMBO:
                combo = QComboBox()
                for label, value in self._resolve_combo_choices(fdef):
                    combo.addItem(label, userData=value)
                return combo

    def _build_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self._save_button = QPushButton(self.tr("Guardar"))
        self._new_button = QPushButton(self.tr("Nuevo"))
        self._delete_button = QPushButton(self.tr("Eliminar"))
        self._save_button.clicked.connect(self._on_save_clicked)
        self._new_button.clicked.connect(self.clear_form)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        layout.addWidget(self._save_button)
        layout.addWidget(self._new_button)
        layout.addWidget(self._delete_button)
        layout.addStretch()
        return layout

    def _build_status_bar(self) -> QWidget:
        self._status_label = QLabel("")
        self._status_label.setContentsMargins(Spacing.MD, Spacing.XS, Spacing.MD, Spacing.XS)
        return self._status_label

    # ------------------------------------------------------------------
    # Eventos / callbacks
    # ------------------------------------------------------------------

    def _on_row_clicked(self, proxy_index: QModelIndex) -> None:
        source_index = self._proxy_model.mapToSource(proxy_index)
        record = self._grid_model.item(source_index.row(), 0).data(Qt.ItemDataRole.UserRole)
        self._current_record = record
        self._populate_form(record)
        self._set_status("", "")

    def _on_selection_changed(
        self,
        selected: QItemSelection,
        deselected: QItemSelection,
    ) -> None:
        del deselected  # parámetro requerido por la signature de Qt
        indexes = selected.indexes()
        if not indexes:
            return
        proxy_idx = indexes[0]
        if not proxy_idx.isValid():
            return
        source_idx = self._proxy_model.mapToSource(proxy_idx)
        record = self._grid_model.item(source_idx.row(), 0).data(Qt.ItemDataRole.UserRole)
        if record is not None:
            self.grid_selection_changed.emit(record)

    def _on_save_clicked(self) -> None:
        record, error = self._build_model_from_form()
        if record is None:
            self._set_status(error, StatusColor.WARNING)
            return

        if self.config.on_validate is not None:
            ok, reason = self.config.on_validate(record)
            if not ok:
                self._set_status(reason, StatusColor.WARNING)
                return

        try:
            saved = self.config.on_save(record)
        except Exception as exc:  # noqa: BLE001 — mostramos cualquier error al usuario
            self._set_status(str(exc), StatusColor.ERROR)
            return

        self.refresh()
        self.select_record(saved)
        self.record_saved.emit(saved)
        self._set_status("", "")

    def _on_delete_clicked(self) -> None:
        if self._current_record is None:
            self._set_status(
                self.tr("No hay registro seleccionado."),
                StatusColor.WARNING,
            )
            return

        record = self._current_record
        name = self._record_label(record)
        confirmed = QMessageBox.question(
            self,
            self.tr("Eliminar"),
            self.tr("¿Eliminar registro {name}?").format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return

        try:
            ok = self.config.on_delete(record)
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), StatusColor.ERROR)
            return

        if not ok:
            self._set_status(self.tr("No se pudo eliminar."), StatusColor.WARNING)
            return

        self.record_deleted.emit(record)
        self.clear_form()
        self.refresh()

    def _apply_filter(self, text: str) -> None:
        self._proxy_model.setFilterFixedString(text)

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _configure_filter_column(self) -> None:
        if self.config.filter_field is None:
            self._proxy_model.setFilterKeyColumn(-1)
            return
        for i, col in enumerate(self._grid_columns):
            if col.name == self.config.filter_field:
                self._proxy_model.setFilterKeyColumn(i)
                return
        self._proxy_model.setFilterKeyColumn(-1)

    def _wire_navigator(self) -> None:
        chain: list[QWidget] = []
        for fdef in self.config.fields:
            widget = self._inputs[fdef.name]
            if fdef.field_type == FieldType.READONLY:
                continue
            chain.append(widget)
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_button.setFocus
        self._navigator.install()

    def _append_record_to_grid(self, record: Any) -> None:
        items: list[QStandardItem] = []
        for i, col in enumerate(self._grid_columns):
            value = getattr(record, col.name)
            item = QStandardItem(self._format_for_grid(col, value))
            item.setEditable(False)
            if i == 0:
                item.setData(record, Qt.ItemDataRole.UserRole)
            items.append(item)
        self._grid_model.appendRow(items)

    def _format_for_grid(self, fdef: FieldDef, value: Any) -> str:
        if value is None:
            return ""
        if fdef.field_type == FieldType.BOOL:
            return self.tr("Sí") if value else self.tr("No")
        if fdef.field_type == FieldType.COMBO:
            for label, val in self._resolve_combo_choices(fdef):
                if val == value:
                    return label
        return str(value)

    def _populate_form(self, record: Any) -> None:
        # Asegurar que los combos tengan los choices actuales antes de
        # intentar seleccionar un valor (puede haberse agregado un item
        # nuevo en otro tab desde la última vez).
        self.refresh_combo_choices()
        for fdef in self.config.fields:
            value = getattr(record, fdef.name, None)
            self._set_input_value(fdef, value)
        self._update_pk_editability()

    def _set_input_value(self, fdef: FieldDef, value: Any) -> None:
        widget = self._inputs[fdef.name]
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            assert isinstance(widget, QLineEdit)
            widget.setText("" if value is None else str(value))
        elif fdef.field_type == FieldType.INT:
            assert isinstance(widget, QSpinBox)
            widget.setValue(int(value) if value is not None else 0)
        elif fdef.field_type == FieldType.BOOL:
            assert isinstance(widget, QCheckBox)
            widget.setChecked(bool(value))
        elif fdef.field_type == FieldType.COMBO:
            assert isinstance(widget, QComboBox)
            idx = widget.findData(value)
            widget.setCurrentIndex(idx if idx >= 0 else 0)

    def _read_input(self, fdef: FieldDef, widget: QWidget) -> Any:
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            assert isinstance(widget, QLineEdit)
            return widget.text().strip() or None
        if fdef.field_type == FieldType.INT:
            assert isinstance(widget, QSpinBox)
            return widget.value()
        if fdef.field_type == FieldType.BOOL:
            assert isinstance(widget, QCheckBox)
            return widget.isChecked()
        if fdef.field_type == FieldType.COMBO:
            assert isinstance(widget, QComboBox)
            return widget.currentData()
        return None

    def _build_model_from_form(self) -> tuple[Any | None, str]:
        kwargs: dict[str, Any] = dict(self.config.extra_kwargs)
        for fdef in self.config.fields:
            widget = self._inputs[fdef.name]
            if fdef.field_type == FieldType.READONLY:
                if self._current_record is not None:
                    kwargs[fdef.name] = getattr(self._current_record, fdef.name)
                else:
                    kwargs[fdef.name] = None
                continue
            value = self._read_input(fdef, widget)
            if fdef.is_required and self._is_empty(fdef, value):
                return None, self.tr("El campo '{label}' es obligatorio").format(label=fdef.label)
            kwargs[fdef.name] = value

        try:
            return self.config.model_class(**kwargs), ""
        except (TypeError, ValueError) as exc:
            return None, str(exc)

    def _is_empty(self, fdef: FieldDef, value: Any) -> bool:
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            return value is None or value == ""
        if fdef.field_type == FieldType.COMBO:
            return value is None
        return False

    def _update_pk_editability(self) -> None:
        """Hace readonly TODOS los campos `is_id` cuando se edita un existente.

        Soporta PK simple y compuesta. Cada tipo se maneja con la API
        adecuada: QLineEdit/QSpinBox vía setReadOnly, QComboBox/QCheckBox
        vía setEnabled (no tienen modo readonly nativo).
        """
        editing = self._current_record is not None
        for fdef in self.config.fields:
            if not fdef.is_id or fdef.field_type == FieldType.READONLY:
                continue
            widget = self._inputs[fdef.name]
            if isinstance(widget, (QLineEdit, QSpinBox)):
                widget.setReadOnly(editing)
                widget.setStyleSheet(f"background-color: {READONLY_BG};" if editing else "")
            elif isinstance(widget, (QComboBox, QCheckBox)):
                widget.setEnabled(not editing)

    def _first_editable_input(self) -> QWidget | None:
        for fdef in self.config.fields:
            if fdef.field_type == FieldType.READONLY:
                continue
            widget = self._inputs[fdef.name]
            if isinstance(widget, QLineEdit) and widget.isReadOnly():
                continue
            if isinstance(widget, QSpinBox) and widget.isReadOnly():
                continue
            if isinstance(widget, (QComboBox, QCheckBox)) and not widget.isEnabled():
                continue
            return widget
        return None

    def _records_equal(self, a: Any, b: Any) -> bool:
        if a is None or b is None:
            return False
        if self._id_fields:
            return all(getattr(a, f.name) == getattr(b, f.name) for f in self._id_fields)
        return bool(a == b)

    def _record_label(self, record: Any) -> str:
        # Buscar el primer campo show_in_grid no-id para mostrar
        for fdef in self.config.fields:
            if fdef.show_in_grid and not fdef.is_id:
                value = getattr(record, fdef.name, None)
                if value is not None:
                    return str(value)
        if self._id_fields:
            return ", ".join(str(getattr(record, f.name)) for f in self._id_fields)
        return str(record)

    def _set_status(self, message: str, color: str) -> None:
        self._status_label.setText(message)
        if color:
            self._status_label.setStyleSheet(f"color: {color};")
        else:
            self._status_label.setStyleSheet("")
