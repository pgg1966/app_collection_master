"""Tests del CodesMasterDetailView."""

from PySide6.QtCore import Qt

from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.core.models import CodeHeader, CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)


def test_master_loads_headers(qtbot, memory_db):
    headers_repo = CodesHeadersRepository(memory_db)
    headers_repo.create(CodeHeader(None, "FIFA", 5))
    headers_repo.create(CodeHeader(None, "Pokemon", 4))
    memory_db.commit()

    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()
    assert view.headers_abm._grid_model.rowCount() == 2


def test_detail_disabled_until_header_selected(qtbot, memory_db, sample_code_header):
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()
    assert view.lines_abm.isEnabled() is False


def test_detail_loads_lines_of_selected_header(qtbot, memory_db, sample_code_header):
    lines_repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    memory_db.commit()

    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Simular selección en master
    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    assert view.lines_abm.isEnabled() is True
    assert view.lines_abm._grid_model.rowCount() == 2


def test_create_line_uses_current_header_id(qtbot, memory_db, sample_code_header):
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Seleccionar el header sample
    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    view.lines_abm._inputs["code_id"].setText("ARG")
    view.lines_abm._inputs["code_name"].setText("Argentina")
    view.lines_abm._inputs["code_order"].setValue(1)
    qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)

    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    assert len(lines) == 1
    assert lines[0].code_id == "ARG"
    assert lines[0].code_header_id == sample_code_header.code_header_id


def test_validate_line_rejects_too_long_code(qtbot, memory_db, sample_code_header):
    """sample_code_header tiene max_length=5; un código de 6 chars debe fallar."""
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    view.lines_abm._inputs["code_id"].setText("ABCDEF")  # 6 chars
    view.lines_abm._inputs["code_name"].setText("Demasiado")
    qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)
    assert "longitud" in view.lines_abm._status_label.text().lower()
    assert CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id) == []
