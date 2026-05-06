"""Tests de los aggregates CsvImportReport / CsvImportError."""

from __future__ import annotations

from collections_app.core.models.aggregates.csv_import_report import (
    CsvImportError,
    CsvImportReport,
)


def test_csv_import_error_holds_fields() -> None:
    err = CsvImportError(row_index=42, message="code_id vacío")
    assert err.row_index == 42
    assert err.message == "code_id vacío"


def test_csv_import_report_default_errors_empty() -> None:
    report = CsvImportReport(rows_total=10, rows_inserted=10, rows_skipped=0)
    assert report.errors == []


def test_csv_import_report_with_errors() -> None:
    errs = [
        CsvImportError(row_index=3, message="card_number invalido"),
        CsvImportError(row_index=7, message="code_id no existe"),
    ]
    report = CsvImportReport(rows_total=10, rows_inserted=8, rows_skipped=2, errors=errs)
    assert report.rows_total == 10
    assert report.rows_inserted == 8
    assert len(report.errors) == 2


def test_csv_import_report_factory_default_isolates_instances() -> None:
    """Default factory list — cada instancia tiene su propia lista, no compartida."""
    r1 = CsvImportReport(rows_total=0, rows_inserted=0, rows_skipped=0)
    r2 = CsvImportReport(rows_total=0, rows_inserted=0, rows_skipped=0)
    r1.errors.append(CsvImportError(row_index=1, message="x"))
    assert r2.errors == []
