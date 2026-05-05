"""Tests de CodeLinesService."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.exceptions import CodeLinesError


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> CodeLinesService:
    return CodeLinesService(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def _line(header_id: int, code_id: str, **kw: object) -> CodeLine:
    base: dict[str, object] = {
        "code_line_id": None,
        "code_header_id": header_id,
        "code_id": code_id,
        "code_name": code_id.lower(),
        "code_order": 0,
    }
    base.update(kw)
    return CodeLine(**base)  # type: ignore[arg-type]


def test_list_by_header_empty(service: CodeLinesService, header_id: int) -> None:
    assert service.list_by_header(header_id) == []


def test_upsert_inserts(service: CodeLinesService, header_id: int) -> None:
    saved = service.upsert(_line(header_id, "ARG", code_name="Argentina"))
    assert saved.code_line_id is not None
    assert saved.code_id == "ARG"


def test_upsert_with_empty_code_id_raises(service: CodeLinesService, header_id: int) -> None:
    with pytest.raises(CodeLinesError, match="code_id"):
        service.upsert(_line(header_id, ""))


def test_upsert_with_empty_code_name_raises(service: CodeLinesService, header_id: int) -> None:
    with pytest.raises(CodeLinesError, match="code_name"):
        service.upsert(_line(header_id, "ARG", code_name=""))


def test_upsert_violates_max_length_raises(
    service: CodeLinesService, db_conn: sqlite3.Connection
) -> None:
    """code_id supera code_max_length del header."""
    h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="Tight", code_max_length=3)
    )
    assert h.code_header_id is not None
    with pytest.raises(CodeLinesError, match="max_length"):
        service.upsert(_line(h.code_header_id, "TOOLONG"))


def test_upsert_at_max_length_is_allowed(
    service: CodeLinesService, db_conn: sqlite3.Connection
) -> None:
    """Limite es <=, no <."""
    h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="T", code_max_length=3)
    )
    assert h.code_header_id is not None
    saved = service.upsert(_line(h.code_header_id, "ABC"))
    assert saved.code_id == "ABC"


def test_upsert_unknown_header_raises(service: CodeLinesService) -> None:
    """No existe header_id=999, validacion de FK precede al INSERT."""
    with pytest.raises(CodeLinesError, match="header"):
        service.upsert(_line(999, "X"))


def test_lookup_returns_line(service: CodeLinesService, header_id: int) -> None:
    service.upsert(_line(header_id, "MR", code_name="Mirage"))
    line = service.lookup(header_id, "MR")
    assert line is not None
    assert line.code_name == "Mirage"


def test_lookup_returns_none_for_missing(service: CodeLinesService, header_id: int) -> None:
    assert service.lookup(header_id, "ZZZ") is None


def test_lookup_name_returns_code_name(service: CodeLinesService, header_id: int) -> None:
    service.upsert(_line(header_id, "ARG", code_name="Argentina"))
    assert service.lookup_name(header_id, "ARG") == "Argentina"


def test_lookup_name_falls_back_to_code_id_when_missing(
    service: CodeLinesService, header_id: int
) -> None:
    """Vista preservada espera fallback al code_id si la linea no existe."""
    assert service.lookup_name(header_id, "GHOST") == "GHOST"


def test_delete_returns_true_when_existed(service: CodeLinesService, header_id: int) -> None:
    service.upsert(_line(header_id, "A"))
    assert service.delete(header_id, "A") is True


def test_delete_returns_false_when_missing(service: CodeLinesService, header_id: int) -> None:
    assert service.delete(header_id, "ghost") is False


def test_reorder_assigns_orders(service: CodeLinesService, header_id: int) -> None:
    for code in ("A", "B", "C"):
        service.upsert(_line(header_id, code))
    service.reorder(header_id, ["B", "A", "C"])
    items = service.list_by_header(header_id)
    assert [(i.code_id, i.code_order) for i in items] == [("B", 1), ("A", 2), ("C", 3)]
