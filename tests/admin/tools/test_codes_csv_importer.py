"""Tests del CodesCsvImporter."""

from pathlib import Path

import pytest

from collections_app.admin.tools.codes_csv_importer import CodesCsvImporter
from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_import_valid_csv(memory_db, sample_code_header):
    """Importa el sample completo respetando code_max_length=5."""
    result = CodesCsvImporter(memory_db).import_file(
        FIXTURES / "sample_codes.csv",
        sample_code_header.code_header_id,
    )
    assert result.total_rows == 4
    assert result.imported == 4
    assert result.skipped == 0
    assert result.errors == []
    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    assert len(lines) == 4
    codes = {line.code_id for line in lines}
    assert codes == {"ARG", "BRA", "FRA", "ESP"}


def test_import_skips_codes_exceeding_max_length(memory_db, sample_code_header, tmp_path):
    """sample_code_header tiene max_length=5; 'ABCDEFG' (7 chars) debe omitirse."""
    csv = tmp_path / "long.csv"
    csv.write_text(
        "code_id,code_name,code_order\n"
        "ARG,Argentina,1\n"
        "ABCDEFG,Demasiado,2\n"
        "BRA,Brasil,3\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.total_rows == 3
    assert result.imported == 2
    assert result.skipped == 1
    assert any("ABCDEFG" in e for e in result.errors)
    assert any("max_length" in e for e in result.errors)


def test_import_overwrites_existing(memory_db, sample_code_header, tmp_path):
    """Códigos existentes se actualizan vía upsert."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Old Name", code_order=99))
    memory_db.commit()

    csv = tmp_path / "update.csv"
    csv.write_text("ARG,Argentina,1\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, hid)

    assert result.imported == 1
    fresh = repo.get(hid, "ARG")
    assert fresh is not None
    assert fresh.code_name == "Argentina"
    assert fresh.code_order == 1


def test_import_handles_unicode(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "unicode.csv"
    csv.write_text(
        "code_id,code_name,code_order\n" "ARG,Árgentîna,1\n" "ESP,España,2\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 2
    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    names = {line.code_name for line in lines}
    assert "Árgentîna" in names
    assert "España" in names


def test_import_with_progress(memory_db, sample_code_header):
    progress_calls: list[tuple[int, int]] = []
    CodesCsvImporter(memory_db).import_file(
        FIXTURES / "sample_codes.csv",
        sample_code_header.code_header_id,
        on_progress=lambda c, t: progress_calls.append((c, t)),
    )
    assert len(progress_calls) == 4
    assert progress_calls[-1] == (4, 4)


def test_import_rejects_unknown_header(memory_db):
    with pytest.raises(ValueError, match="no existe"):
        CodesCsvImporter(memory_db).import_file(FIXTURES / "sample_codes.csv", 999)


def test_import_handles_missing_header_row(memory_db, sample_code_header, tmp_path):
    """Si la primera fila no es header, se trata como dato."""
    csv = tmp_path / "no_header.csv"
    csv.write_text("ARG,Argentina,1\nBRA,Brasil,2\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.total_rows == 2
    assert result.imported == 2


def test_import_skips_empty_code_id(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "empty_id.csv"
    csv.write_text(",Empty,1\nARG,Argentina,2\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 1
    assert result.skipped == 1


def test_import_uses_default_order_when_missing(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "no_order.csv"
    csv.write_text("ARG,Argentina\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 1
    line = CodesLinesRepository(memory_db).get(sample_code_header.code_header_id, "ARG")
    assert line is not None
    assert line.code_order == 0
