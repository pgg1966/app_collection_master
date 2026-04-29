"""Tests del CodesLinesRepository."""

import pytest

from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository


def test_upsert_insert(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    line = CodeLine(sample_code_header.code_header_id, "ARG", "Argentina")
    saved = repo.upsert(line)
    assert saved == line
    fetched = repo.get(sample_code_header.code_header_id, "ARG")
    assert fetched == line


def test_upsert_update_existing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "ARG", "ARG (Argentina)"))
    fetched = repo.get(hid, "ARG")
    assert fetched is not None
    assert fetched.code_name == "ARG (Argentina)"


def test_upsert_validates_max_length(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    too_long = "X" * 10  # max_length es 5
    with pytest.raises(ValueError, match="excede max_length"):
        repo.upsert(CodeLine(hid, too_long, "Demasiado largo"))


def test_upsert_rejects_unknown_header(memory_db):
    repo = CodesLinesRepository(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        repo.upsert(CodeLine(999, "ARG", "Argentina"))


def test_get_returns_none_when_missing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.get(sample_code_header.code_header_id, "NOPE") is None


def test_list_by_header_empty(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.list_by_header(sample_code_header.code_header_id) == []


def test_list_by_header_sorted(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "FRA", "Francia"))
    codes = [line.code_id for line in repo.list_by_header(hid)]
    assert codes == ["ARG", "BRA", "FRA"]


def test_list_codes_only(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    assert repo.list_codes_only(hid) == ["ARG", "BRA"]


def test_delete_existing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    assert repo.delete(hid, "ARG") is True
    assert repo.get(hid, "ARG") is None


def test_delete_nonexistent_returns_false(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.delete(sample_code_header.code_header_id, "NOPE") is False


def test_cascade_delete_from_header(memory_db, sample_code_header):
    """Si borro el header, las lines se borran por cascade."""
    from collections_app.core.repositories import CodesHeadersRepository

    lines_repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brasil"))

    CodesHeadersRepository(memory_db).delete(hid)
    assert lines_repo.list_by_header(hid) == []
