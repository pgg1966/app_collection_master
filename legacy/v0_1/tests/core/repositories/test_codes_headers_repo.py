"""Tests del CodesHeadersRepository."""

import sqlite3

import pytest

from collections_app.core.models import CodeHeader
from collections_app.core.repositories import CodesHeadersRepository


def test_create_returns_header_with_id(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    assert created.code_header_id is not None
    assert created.code_header_name == "FIFA"
    assert created.code_max_length == 4


def test_get_by_id_returns_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    found = repo.get_by_id(created.code_header_id)
    assert found == created


def test_get_by_id_returns_none_when_missing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "FIFA", 4))
    found = repo.get_by_name("FIFA")
    assert found is not None
    assert found.code_header_name == "FIFA"


def test_get_by_name_returns_none_when_missing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.get_by_name("NOPE") is None


def test_list_all_empty(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.list_all() == []


def test_list_all_with_data_sorted_by_name(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "Zeta", 5))
    repo.create(CodeHeader(None, "Alpha", 3))
    repo.create(CodeHeader(None, "Mid", 4))
    names = [h.code_header_name for h in repo.list_all()]
    assert names == ["Alpha", "Mid", "Zeta"]


def test_update_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    updated = repo.update(CodeHeader(created.code_header_id, "FIFA Codes", 6))
    assert updated.code_header_name == "FIFA Codes"
    fresh = repo.get_by_id(created.code_header_id)
    assert fresh is not None
    assert fresh.code_max_length == 6


def test_update_without_id_raises(memory_db):
    repo = CodesHeadersRepository(memory_db)
    with pytest.raises(ValueError, match="code_header_id"):
        repo.update(CodeHeader(None, "FIFA", 5))


def test_delete_existing_returns_true(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    assert repo.delete(created.code_header_id) is True
    assert repo.get_by_id(created.code_header_id) is None


def test_delete_nonexistent_returns_false(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.delete(999) is False


def test_unique_name_constraint(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "FIFA", 4))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(CodeHeader(None, "FIFA", 5))
