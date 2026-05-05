"""Tab Reportes: bitácora de altas/bajas con presets y export CSV."""

import csv
import logging
import sqlite3
from datetime import UTC, datetime, time, timedelta
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection, OperationType
from collections_app.core.services import ReportsService, TransactionWithCard
from collections_app.core.utils.datetime_helpers import (
    format_for_display,
    to_local,
)
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)

# Presets para el combo "Período"
PRESET_TODAY = "Hoy"
PRESET_LAST_7 = "Últimos 7 días"
PRESET_LAST_30 = "Últimos 30 días"
PRESET_THIS_MONTH = "Este mes"
PRESET_LAST_MONTH = "Mes anterior"
PRESET_CUSTOM = "Personalizado…"

OP_ALL = "Todas"


class ReportsView(QWidget):
    """Tab de reportes: filtros de período y operación + grilla + export CSV."""

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
        self.refresh()

    def refresh(self) -> None:
        start, end = self._compute_range()
        op = self._selected_operation()
        assert self.collection.collection_id is not None
        rows = ReportsService(self.conn).get_transactions_in_period(
            self.collection.collection_id, start, end, op
        )
        self._populate_grid(rows)
        self._update_summary(rows)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        layout.addLayout(self._build_filters_row())
        layout.addLayout(self._build_custom_row())

        self._grid_model = QStandardItemModel(0, 5, self)
        self._grid_model.setHorizontalHeaderLabels(
            [
                self.tr("Fecha"),
                self.tr("Op"),
                self.tr("Code"),
                self.tr("Nombre"),
                self.tr("Cant."),
            ]
        )
        self._grid_view = QTableView()
        self._grid_view.setModel(self._grid_model)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._grid_view, stretch=1)

        bottom = QHBoxLayout()
        self._summary_label = QLabel("")
        bottom.addWidget(self._summary_label)
        bottom.addStretch()
        self._export_button = QPushButton(self.tr("Exportar a CSV…"))
        self._export_button.clicked.connect(self._export_csv)
        bottom.addWidget(self._export_button)
        layout.addLayout(bottom)

    def _build_filters_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        row.addWidget(QLabel(self.tr("Período") + ":"))
        self._period_combo = QComboBox()
        self._period_combo.addItems(
            [
                PRESET_TODAY,
                PRESET_LAST_7,
                PRESET_LAST_30,
                PRESET_THIS_MONTH,
                PRESET_LAST_MONTH,
                PRESET_CUSTOM,
            ]
        )
        self._period_combo.setCurrentText(PRESET_LAST_7)
        self._period_combo.currentTextChanged.connect(self._on_period_changed)
        row.addWidget(self._period_combo)

        row.addWidget(QLabel(self.tr("Operación") + ":"))
        self._op_combo = QComboBox()
        self._op_combo.addItem(OP_ALL)
        self._op_combo.addItem(self.tr("Alta"), userData=OperationType.ALTA)
        self._op_combo.addItem(self.tr("Baja"), userData=OperationType.BAJA)
        self._op_combo.currentTextChanged.connect(lambda _: self.refresh())
        row.addWidget(self._op_combo)
        row.addStretch()
        return row

    def _build_custom_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._custom_from_label = QLabel(self.tr("Desde") + ":")
        self._custom_to_label = QLabel(self.tr("Hasta") + ":")
        self._date_from = QDateEdit(QDate.currentDate().addDays(-7))
        self._date_to = QDateEdit(QDate.currentDate())
        for d in (self._date_from, self._date_to):
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy-MM-dd")
            d.dateChanged.connect(lambda _: self.refresh())

        row.addWidget(self._custom_from_label)
        row.addWidget(self._date_from)
        row.addWidget(self._custom_to_label)
        row.addWidget(self._date_to)
        row.addStretch()
        # Visibilidad inicial según preset
        self._set_custom_visibility(False)
        return row

    def _set_custom_visibility(self, visible: bool) -> None:
        self._custom_from_label.setVisible(visible)
        self._custom_to_label.setVisible(visible)
        self._date_from.setVisible(visible)
        self._date_to.setVisible(visible)

    # ------------------------------------------------------------------
    # Período: cálculo y sincronización
    # ------------------------------------------------------------------

    def _on_period_changed(self, preset: str) -> None:
        if preset == PRESET_CUSTOM:
            self._set_custom_visibility(True)
        else:
            self._set_custom_visibility(False)
        self.refresh()

    def _compute_range(self) -> tuple[datetime, datetime]:
        """Calcula `(start, end)` en UTC para el preset/custom seleccionado.

        Los presets se calculan sobre la fecha LOCAL (lo que el usuario
        espera ver) y se convierten a UTC antes de retornar.
        """
        preset = self._period_combo.currentText()
        today_local = datetime.now().astimezone()
        local_tz = today_local.tzinfo
        today_date = today_local.date()

        if preset == PRESET_TODAY:
            start_local = datetime.combine(today_date, time.min, tzinfo=local_tz)
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_7:
            start_local = datetime.combine(
                today_date - timedelta(days=6), time.min, tzinfo=local_tz
            )
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_30:
            start_local = datetime.combine(
                today_date - timedelta(days=29), time.min, tzinfo=local_tz
            )
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_THIS_MONTH:
            first = today_date.replace(day=1)
            start_local = datetime.combine(first, time.min, tzinfo=local_tz)
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_MONTH:
            first_this = today_date.replace(day=1)
            last_prev = first_this - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            start_local = datetime.combine(first_prev, time.min, tzinfo=local_tz)
            end_local = datetime.combine(last_prev, time.max, tzinfo=local_tz)
        else:  # PRESET_CUSTOM
            d_from = self._date_from.date()
            d_to = self._date_to.date()
            start_local = datetime(d_from.year(), d_from.month(), d_from.day(), tzinfo=local_tz)
            end_local = datetime(
                d_to.year(),
                d_to.month(),
                d_to.day(),
                23,
                59,
                59,
                tzinfo=local_tz,
            )
        return (
            start_local.astimezone(UTC),
            end_local.astimezone(UTC),
        )

    def _selected_operation(self) -> OperationType | None:
        data = self._op_combo.currentData()
        if data is None:
            return None
        # PySide6 puede deserializar el StrEnum como str; aceptamos ambos.
        if isinstance(data, OperationType):
            return data
        if isinstance(data, str):
            try:
                return OperationType(data)
            except ValueError:
                return None
        return None

    # ------------------------------------------------------------------
    # Grilla y resumen
    # ------------------------------------------------------------------

    def _populate_grid(self, rows: list[TransactionWithCard]) -> None:
        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for r in rows:
            items = [
                QStandardItem(format_for_display(r.transaction_date)),
                QStandardItem(
                    self.tr("Alta") if r.operation == OperationType.ALTA else self.tr("Baja")
                ),
                QStandardItem(f"{r.code_id}-{r.card_number}"),
                QStandardItem(r.card_name),
                QStandardItem(str(r.quantity)),
            ]
            for item in items:
                item.setEditable(False)
            self._grid_model.appendRow(items)

    def _update_summary(self, rows: list[TransactionWithCard]) -> None:
        altas = sum(1 for r in rows if r.operation == OperationType.ALTA)
        bajas = sum(1 for r in rows if r.operation == OperationType.BAJA)
        self._summary_label.setText(
            self.tr("Resumen del período: {a} altas, {b} bajas").format(a=altas, b=bajas)
        )

    # ------------------------------------------------------------------
    # Export CSV
    # ------------------------------------------------------------------

    def _export_csv(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Exportar reporte"),
            "report.csv",
            self.tr("CSV files (*.csv)"),
        )
        if not path_str:
            return

        start, end = self._compute_range()
        op = self._selected_operation()
        assert self.collection.collection_id is not None
        rows = ReportsService(self.conn).get_transactions_in_period(
            self.collection.collection_id, start, end, op
        )

        try:
            self._write_csv(Path(path_str), rows, start, end)
        except OSError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            logger.exception("Error escribiendo CSV de reporte")
            return

        QMessageBox.information(
            self,
            self.tr("Exportar reporte"),
            self.tr("Exportadas {n} filas a {path}").format(n=len(rows), path=path_str),
        )

    def _write_csv(
        self,
        path: Path,
        rows: list[TransactionWithCard],
        start: datetime,
        end: datetime,
    ) -> None:
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            # Comentario inicial con metadata: nombre y rango (en hora local)
            writer.writerow(
                [
                    f"# {self.collection.collection_name}",
                    f"desde={format_for_display(start, with_seconds=True)}",
                    f"hasta={format_for_display(end, with_seconds=True)}",
                ]
            )
            writer.writerow(["fecha", "operacion", "codigo", "numero", "nombre", "cantidad"])
            for r in rows:
                writer.writerow(
                    [
                        to_local(r.transaction_date).isoformat(timespec="seconds"),
                        r.operation.value,
                        r.code_id,
                        r.card_number,
                        r.card_name,
                        r.quantity,
                    ]
                )
