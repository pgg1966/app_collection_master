"""Vista master-detail: headers de códigos y sus líneas."""

import sqlite3

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import CodeHeader, CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType


class CodesMasterDetailView(QWidget):
    """Master (codes_headers) arriba, detail (codes_lines) abajo.

    Cuando el usuario selecciona un header, el detail se habilita y
    muestra sus líneas. Crear/editar líneas usa siempre el header
    actualmente seleccionado vía `extra_kwargs`.
    """

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._current_header: CodeHeader | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # MASTER
        self.headers_abm = self._build_headers_abm()
        layout.addWidget(self.headers_abm, stretch=1)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        self.detail_label = QLabel(self.tr("Seleccione un header para ver sus códigos"))
        self.detail_label.setStyleSheet("font-weight: 500; padding: 8px;")
        layout.addWidget(self.detail_label)

        # DETAIL
        self.lines_abm, self._lines_config = self._build_lines_abm()
        self.lines_abm.setEnabled(False)
        layout.addWidget(self.lines_abm, stretch=1)

        # Conexiones master ↔ detail
        self.headers_abm.grid_selection_changed.connect(self._on_header_selected)
        self.headers_abm.record_saved.connect(self._on_header_saved)
        self.headers_abm.record_deleted.connect(self._on_header_deleted)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build_headers_abm(self) -> AbmWidget:
        config = AbmConfig(
            title=self.tr("Headers de Códigos"),
            module_code="COD001",
            fields=[
                FieldDef(
                    "code_header_id",
                    "ID",
                    FieldType.READONLY,
                    is_id=True,
                    is_required=False,
                    grid_width=50,
                ),
                FieldDef(
                    "code_header_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=250,
                ),
                FieldDef(
                    "code_max_length",
                    "Max longitud código",
                    FieldType.INT,
                    grid_width=150,
                ),
            ],
            filter_field="code_header_name",
            on_load_all=lambda: CodesHeadersRepository(self.conn).list_all(),
            on_save=self._save_header,
            on_delete=self._delete_header,
            model_class=CodeHeader,
        )
        return AbmWidget(config)

    def _build_lines_abm(self) -> tuple[AbmWidget, AbmConfig]:
        config = AbmConfig(
            title=self.tr("Códigos del header"),
            module_code="COD002",
            fields=[
                FieldDef(
                    "code_id",
                    "Código",
                    FieldType.TEXT,
                    is_id=True,
                    max_length=10,
                    grid_width=80,
                ),
                FieldDef(
                    "code_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=250,
                ),
                FieldDef(
                    "code_order",
                    "Orden",
                    FieldType.INT,
                    is_required=False,
                    grid_width=80,
                ),
            ],
            filter_field="code_id",
            on_load_all=lambda: [],  # se reasigna al seleccionar un header
            on_save=self._save_line,
            on_delete=self._delete_line,
            on_validate=self._validate_line,
            model_class=CodeLine,
        )
        widget = AbmWidget(config)
        return widget, config

    # ------------------------------------------------------------------
    # Callbacks de master
    # ------------------------------------------------------------------

    def _save_header(self, header: CodeHeader) -> CodeHeader:
        repo = CodesHeadersRepository(self.conn)
        saved = repo.create(header) if header.code_header_id is None else repo.update(header)
        self.conn.commit()
        return saved

    def _delete_header(self, header: CodeHeader) -> bool:
        assert header.code_header_id is not None
        ok = CodesHeadersRepository(self.conn).delete(header.code_header_id)
        self.conn.commit()
        return ok

    def _on_header_selected(self, header: CodeHeader) -> None:
        self._current_header = header
        self.detail_label.setText(
            self.tr("Códigos del header: {name}").format(name=header.code_header_name)
        )
        self.lines_abm.setEnabled(True)
        self._refresh_lines_for_current_header()

    def _on_header_saved(self, header: CodeHeader) -> None:
        # Si el header guardado es el actual, refresca su nombre en el label
        if self._current_header and (self._current_header.code_header_id == header.code_header_id):
            self._current_header = header
            self.detail_label.setText(
                self.tr("Códigos del header: {name}").format(name=header.code_header_name)
            )

    def _on_header_deleted(self, header: CodeHeader) -> None:
        if self._current_header and self._current_header.code_header_id == header.code_header_id:
            self._current_header = None
            self.detail_label.setText(self.tr("Seleccione un header para ver sus códigos"))
            self.lines_abm.setEnabled(False)
            self._lines_config.on_load_all = lambda: []
            self._lines_config.extra_kwargs = {}
            self.lines_abm.refresh()
            self.lines_abm.clear_form()

    # ------------------------------------------------------------------
    # Detail / lines
    # ------------------------------------------------------------------

    def _refresh_lines_for_current_header(self) -> None:
        if self._current_header is None or self._current_header.code_header_id is None:
            return
        hid: int = self._current_header.code_header_id
        self._lines_config.on_load_all = lambda: CodesLinesRepository(self.conn).list_by_header(hid)
        self._lines_config.extra_kwargs = {"code_header_id": hid}
        self.lines_abm.refresh()
        self.lines_abm.clear_form()

    def _save_line(self, line: CodeLine) -> CodeLine:
        repo = CodesLinesRepository(self.conn)
        saved = repo.upsert(line)
        self.conn.commit()
        return saved

    def _delete_line(self, line: CodeLine) -> bool:
        ok = CodesLinesRepository(self.conn).delete(line.code_header_id, line.code_id)
        self.conn.commit()
        return ok

    def _validate_line(self, line: CodeLine) -> tuple[bool, str]:
        if self._current_header is None:
            return False, self.tr("No hay header seleccionado.")
        if len(line.code_id) > self._current_header.code_max_length:
            return False, self.tr("El código '{code}' excede la longitud máxima ({max}).").format(
                code=line.code_id, max=self._current_header.code_max_length
            )
        return True, ""
