"""Tests del ReportsView."""

import csv
from datetime import UTC, datetime

import pytest
from PySide6.QtCore import QDate

from collections_app.client.views.reports_view import (
    PRESET_CUSTOM,
    PRESET_LAST_7,
    PRESET_TODAY,
    ReportsView,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def reports_setup(memory_db, sample_cards, sample_collection):
    inv = InventoryService(memory_db)
    inv.add_card(sample_collection.collection_id, "ARG", 1, 1)
    inv.add_card(sample_collection.collection_id, "ARG", 2, 1)
    inv.add_card(sample_collection.collection_id, "BRA", 1, 2)
    inv.remove_card(sample_collection.collection_id, "BRA", 1, 1)
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, reports_setup):
    v = ReportsView(memory_db, reports_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def test_default_period_is_last_7_days(qtbot, view):
    assert view._period_combo.currentText() == PRESET_LAST_7


def test_period_preset_changes_dates(qtbot, view):
    """Cambiar a 'Hoy' cambia el rango computado."""
    view._period_combo.setCurrentText(PRESET_TODAY)
    start, end = view._compute_range()
    # Ambos en UTC con tzinfo
    assert start.tzinfo == UTC
    assert end.tzinfo == UTC
    # El rango cubre menos de 25 horas
    assert (end - start).total_seconds() < 25 * 3600


def test_custom_period_enables_date_editors(qtbot, view):
    assert view._date_from.isVisible() is False
    view._period_combo.setCurrentText(PRESET_CUSTOM)
    assert view._date_from.isVisible() is True
    assert view._date_to.isVisible() is True


def test_filter_by_operation(qtbot, view):
    """Filtrando solo Altas, las 3 altas aparecen y las bajas no."""
    view._op_combo.setCurrentIndex(1)  # Alta
    view.refresh()
    assert view._grid_model.rowCount() == 3
    for row in range(3):
        assert "Alta" in view._grid_model.item(row, 1).text()


def test_filter_baja_only(qtbot, view):
    view._op_combo.setCurrentIndex(2)  # Baja
    view.refresh()
    assert view._grid_model.rowCount() == 1


def test_default_loads_recent_transactions(qtbot, view):
    """Con el preset default, la grilla muestra las 4 transactions hechas hoy."""
    assert view._grid_model.rowCount() == 4


def test_summary_shows_altas_y_bajas_counts(qtbot, view):
    text = view._summary_label.text()
    assert "3 altas" in text
    assert "1 bajas" in text


def test_export_csv_creates_valid_file(qtbot, view, tmp_path, monkeypatch):
    """El export crea un archivo con header de metadata + columnas + filas."""
    csv_path = tmp_path / "out.csv"

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **kw: (str(csv_path), "csv"))
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **kw: QMessageBox.StandardButton.Ok)

    view._export_csv()

    assert csv_path.exists()
    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    # Fila 0: metadata, fila 1: header columnas, resto: datos.
    assert rows[0][0].startswith("#")
    assert rows[1] == ["fecha", "operacion", "codigo", "numero", "nombre", "cantidad"]
    assert len(rows) == 2 + 4  # 4 transactions


def test_csv_dates_in_local_time(qtbot, view, tmp_path, monkeypatch):
    """Las fechas en el CSV están en hora local con offset (ISO format)."""
    csv_path = tmp_path / "out.csv"
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **kw: (str(csv_path), "csv"))
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **kw: QMessageBox.StandardButton.Ok)

    view._export_csv()

    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    first_data_row = rows[2]  # fecha, op, ...
    fecha = first_data_row[0]
    # ISO format con offset: "YYYY-MM-DDTHH:MM:SS±HH:MM" o sin offset
    # La fecha re-parseada debe coincidir aproximadamente con "ahora"
    parsed = datetime.fromisoformat(fecha)
    assert parsed.tzinfo is not None
    delta = abs((parsed.astimezone(UTC) - datetime.now(UTC)).total_seconds())
    assert delta < 60  # menos de 1 minuto de diferencia


def test_custom_date_range_filters_correctly(qtbot, memory_db, view):
    """Con un rango futuro, no aparece nada."""
    view._period_combo.setCurrentText(PRESET_CUSTOM)
    future = QDate.currentDate().addDays(30)
    view._date_from.setDate(future)
    view._date_to.setDate(future.addDays(1))
    view.refresh()
    assert view._grid_model.rowCount() == 0
