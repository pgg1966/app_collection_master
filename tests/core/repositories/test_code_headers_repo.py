"""Tests CRUD de CodeHeadersRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CodeHeadersRepository:
    return CodeHeadersRepository(db_conn)


def test_list_all_empty(repo: CodeHeadersRepository) -> None:
    assert repo.list_all() == []


def test_create_returns_header_with_id_populated(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="FIFA"))
    assert created.code_header_id is not None
    assert created.code_header_name == "FIFA"


def test_create_assigns_unique_incremental_ids(repo: CodeHeadersRepository) -> None:
    a = repo.create(CodeHeader(code_header_id=None, code_header_name="A"))
    b = repo.create(CodeHeader(code_header_id=None, code_header_name="B"))
    assert a.code_header_id != b.code_header_id


def test_create_violates_unique_name(repo: CodeHeadersRepository) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Dup"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(CodeHeader(code_header_id=None, code_header_name="Dup"))


def test_get_by_id_returns_header(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="X", code_max_length=8))
    assert created.code_header_id is not None
    fetched = repo.get_by_id(created.code_header_id)
    assert fetched is not None
    assert fetched.code_header_name == "X"
    assert fetched.code_max_length == 8


def test_get_by_id_returns_none_for_missing(repo: CodeHeadersRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_header(repo: CodeHeadersRepository) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Magic"))
    fetched = repo.get_by_name("Magic")
    assert fetched is not None
    assert fetched.code_header_name == "Magic"


def test_get_by_name_is_case_sensitive(repo: CodeHeadersRepository) -> None:
    """get_by_name no normaliza case (matchea exacto)."""
    repo.create(CodeHeader(code_header_id=None, code_header_name="Magic"))
    assert repo.get_by_name("MAGIC") is None
    assert repo.get_by_name("magic") is None


def test_get_by_name_returns_none_for_missing(repo: CodeHeadersRepository) -> None:
    assert repo.get_by_name("ghost") is None


def test_update_changes_name_and_max_length(repo: CodeHeadersRepository) -> None:
    created = repo.create(
        CodeHeader(code_header_id=None, code_header_name="Old", code_max_length=3)
    )
    updated = repo.update(
        CodeHeader(
            code_header_id=created.code_header_id,
            code_header_name="New",
            code_max_length=7,
        )
    )
    assert updated.code_header_name == "New"
    assert updated.code_max_length == 7
    fetched = repo.get_by_id(created.code_header_id) if created.code_header_id else None
    assert fetched is not None
    assert fetched.code_header_name == "New"


def test_update_requires_id(repo: CodeHeadersRepository) -> None:
    with pytest.raises(ValueError, match="code_header_id"):
        repo.update(CodeHeader(code_header_id=None, code_header_name="X"))


def test_delete_returns_true_when_existed(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="X"))
    assert created.code_header_id is not None
    assert repo.delete(created.code_header_id) is True
    assert repo.get_by_id(created.code_header_id) is None


def test_delete_returns_false_when_missing(repo: CodeHeadersRepository) -> None:
    assert repo.delete(999) is False


def test_delete_cascades_to_codes_lines(
    repo: CodeHeadersRepository, db_conn: sqlite3.Connection
) -> None:
    """Borrar header debe borrar sus codes_lines (FK ON DELETE CASCADE)."""
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="Casc"))
    assert created.code_header_id is not None
    db_conn.execute(
        "INSERT INTO codes_lines (code_header_id, code_id, code_name) VALUES (?, ?, ?)",
        (created.code_header_id, "ARG", "Argentina"),
    )
    repo.delete(created.code_header_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM codes_lines WHERE code_header_id = ?",
        (created.code_header_id,),
    ).fetchone()
    assert remaining["c"] == 0


def test_list_all_returns_headers_sorted_by_name(
    repo: CodeHeadersRepository,
) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Zebra"))
    repo.create(CodeHeader(code_header_id=None, code_header_name="Alpha"))
    repo.create(CodeHeader(code_header_id=None, code_header_name="Mike"))
    items = repo.list_all()
    assert [h.code_header_name for h in items] == ["Alpha", "Mike", "Zebra"]
    assert all(isinstance(h, CodeHeader) for h in items)
