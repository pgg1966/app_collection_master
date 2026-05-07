"""Tests del InventoryImportService — generación de modelos + import."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from openpyxl import load_workbook

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import ServiceError
from collections_app.services.inventory_import_service import (
    InventoryImportService,
)


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> InventoryImportService:
    return InventoryImportService(db_conn)


@pytest.fixture
def collection_with_codes(db_conn: sqlite3.Connection) -> Collection:
    """Colección Mundial-style: header WC con 3 codes (ARG, BRA, FRA)."""
    headers_repo = CodeHeadersRepository(db_conn)
    lines_repo = CodeLinesRepository(db_conn)
    collections_repo = CollectionsRepository(db_conn)

    header = headers_repo.create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    assert header.code_header_id is not None
    for i, (code, name) in enumerate([("ARG", "Argentina"), ("BRA", "Brasil"), ("FRA", "Francia")]):
        lines_repo.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=header.code_header_id,
                code_id=code,
                code_name=name,
                code_order=i + 1,
            )
        )
    coll = collections_repo.create(
        Collection(
            collection_id=None,
            collection_name="Mundial",
            card_count=15,
            requires_code=True,
            code_field_name="País",
            code_header_id=header.code_header_id,
        )
    )
    db_conn.commit()
    return coll


@pytest.fixture
def collection_without_codes(db_conn: sqlite3.Connection) -> Collection:
    """Colección sin requires_code (solo número + cantidad)."""
    headers_repo = CodeHeadersRepository(db_conn)
    collections_repo = CollectionsRepository(db_conn)
    header = headers_repo.create(
        CodeHeader(code_header_id=None, code_header_name="Empty", code_max_length=3)
    )
    assert header.code_header_id is not None
    coll = collections_repo.create(
        Collection(
            collection_id=None,
            collection_name="Simple",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=header.code_header_id,
        )
    )
    db_conn.commit()
    return coll


# ---------------------------------------------------------------------
# generate_template
# ---------------------------------------------------------------------


def test_generate_template_with_codes_creates_two_sheets(
    tmp_path: Path,
    service: InventoryImportService,
    collection_with_codes: Collection,
) -> None:
    """requires_code=True → 2 pestañas, headers correctos, codes pre-llenados."""
    assert collection_with_codes.collection_id is not None
    dest = tmp_path / "modelo.xlsx"
    result = service.generate_template(
        collection_id=collection_with_codes.collection_id, dest_path=dest
    )
    assert result == dest
    assert dest.exists()

    wb = load_workbook(dest)
    assert wb.sheetnames == ["Inventario", "Códigos"]

    inv = wb["Inventario"]
    assert [c.value for c in inv[1]] == ["código", "número", "cantidad"]
    # Solo headers, sin filas de datos.
    assert inv.max_row == 1

    codes = wb["Códigos"]
    assert [c.value for c in codes[1]] == ["code_id", "code_name"]
    # 3 codes (ARG, BRA, FRA) + header.
    assert codes.max_row == 4
    code_ids = {codes.cell(row=r, column=1).value for r in range(2, 5)}
    assert code_ids == {"ARG", "BRA", "FRA"}


def test_generate_template_without_codes_creates_one_sheet(
    tmp_path: Path,
    service: InventoryImportService,
    collection_without_codes: Collection,
) -> None:
    """requires_code=False → solo pestaña Inventario, sin columna código."""
    assert collection_without_codes.collection_id is not None
    dest = tmp_path / "modelo_simple.xlsx"
    service.generate_template(collection_id=collection_without_codes.collection_id, dest_path=dest)

    wb = load_workbook(dest)
    assert wb.sheetnames == ["Inventario"]
    inv = wb["Inventario"]
    assert [c.value for c in inv[1]] == ["número", "cantidad"]
    assert inv.max_row == 1


def test_generate_template_unknown_collection_raises(
    tmp_path: Path,
    service: InventoryImportService,
) -> None:
    """Collection inexistente → ServiceError (no genera archivo)."""
    dest = tmp_path / "huerfano.xlsx"
    with pytest.raises(ServiceError, match="no existe"):
        service.generate_template(collection_id=999, dest_path=dest)
    assert not dest.exists()
