"""Tests de CodeHeadersService."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.exceptions import CodeHeadersError


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> CodeHeadersService:
    return CodeHeadersService(db_conn)


def test_list_all_empty(service: CodeHeadersService) -> None:
    assert service.list_all() == []


def test_create_returns_header_with_id(service: CodeHeadersService) -> None:
    saved = service.create(CodeHeader(code_header_id=None, code_header_name="FIFA"))
    assert saved.code_header_id is not None
    assert saved.code_header_name == "FIFA"


def test_create_with_empty_name_raises(service: CodeHeadersService) -> None:
    with pytest.raises(CodeHeadersError, match="name"):
        service.create(CodeHeader(code_header_id=None, code_header_name=""))


def test_create_with_duplicate_name_raises(service: CodeHeadersService) -> None:
    service.create(CodeHeader(code_header_id=None, code_header_name="Dup"))
    with pytest.raises(CodeHeadersError, match="ya existe"):
        service.create(CodeHeader(code_header_id=None, code_header_name="Dup"))


def test_get_by_id_returns_none_for_missing(service: CodeHeadersService) -> None:
    assert service.get_by_id(999) is None


def test_get_by_name_returns_none_for_missing(
    service: CodeHeadersService,
) -> None:
    assert service.get_by_name("ghost") is None


def test_get_by_name_returns_header(service: CodeHeadersService) -> None:
    service.create(CodeHeader(code_header_id=None, code_header_name="Magic"))
    fetched = service.get_by_name("Magic")
    assert fetched is not None
    assert fetched.code_header_name == "Magic"


def test_update_changes_name(service: CodeHeadersService) -> None:
    saved = service.create(CodeHeader(code_header_id=None, code_header_name="Old"))
    updated = service.update(
        CodeHeader(
            code_header_id=saved.code_header_id,
            code_header_name="New",
            code_max_length=saved.code_max_length,
        )
    )
    assert updated.code_header_name == "New"


def test_update_without_id_raises(service: CodeHeadersService) -> None:
    with pytest.raises(CodeHeadersError, match="id"):
        service.update(CodeHeader(code_header_id=None, code_header_name="X"))


def test_delete_returns_true_when_existed(service: CodeHeadersService) -> None:
    saved = service.create(CodeHeader(code_header_id=None, code_header_name="X"))
    assert saved.code_header_id is not None
    assert service.delete(saved.code_header_id) is True


def test_delete_returns_false_when_missing(service: CodeHeadersService) -> None:
    assert service.delete(999) is False


def test_list_all_sorted_by_name(service: CodeHeadersService) -> None:
    service.create(CodeHeader(code_header_id=None, code_header_name="Zeta"))
    service.create(CodeHeader(code_header_id=None, code_header_name="Alpha"))
    items = service.list_all()
    assert [h.code_header_name for h in items] == ["Alpha", "Zeta"]
