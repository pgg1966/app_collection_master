"""Tests CRUD de CodeLinesRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CodeLinesRepository:
    return CodeLinesRepository(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    """Crea un header y retorna su id (las lines lo necesitan como FK)."""
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def test_list_by_header_empty(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.list_by_header(header_id) == []


def test_upsert_inserts_new_line(repo: CodeLinesRepository, header_id: int) -> None:
    line = CodeLine(
        code_line_id=None, code_header_id=header_id, code_id="ARG", code_name="Argentina"
    )
    saved = repo.upsert(line)
    assert saved.code_line_id is not None
    assert saved.code_id == "ARG"


def test_upsert_updates_existing_by_business_key(repo: CodeLinesRepository, header_id: int) -> None:
    """Upsert sobre (code_header_id, code_id) reemplaza nombre y orden."""
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="ARG",
            code_name="Old",
            code_order=1,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="ARG",
            code_name="New",
            code_order=5,
        )
    )
    line = repo.get(header_id, "ARG")
    assert line is not None
    assert line.code_name == "New"
    assert line.code_order == 5


def test_get_returns_line(repo: CodeLinesRepository, header_id: int) -> None:
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="MR",
            code_name="Mirage",
        )
    )
    fetched = repo.get(header_id, "MR")
    assert fetched is not None
    assert fetched.code_name == "Mirage"


def test_get_returns_none_for_missing(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.get(header_id, "ZZZ") is None


def test_get_by_id_returns_line(repo: CodeLinesRepository, header_id: int) -> None:
    saved = repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="X",
            code_name="X-name",
        )
    )
    assert saved.code_line_id is not None
    fetched = repo.get_by_id(saved.code_line_id)
    assert fetched is not None
    assert fetched.code_id == "X"


def test_get_by_id_returns_none_for_missing(repo: CodeLinesRepository) -> None:
    assert repo.get_by_id(999) is None


def test_delete_returns_true_when_existed(repo: CodeLinesRepository, header_id: int) -> None:
    repo.upsert(CodeLine(code_line_id=None, code_header_id=header_id, code_id="A", code_name="A"))
    assert repo.delete(header_id, "A") is True
    assert repo.get(header_id, "A") is None


def test_delete_returns_false_when_missing(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.delete(header_id, "ghost") is False


def test_list_by_header_orders_by_code_order_then_code_id(
    repo: CodeLinesRepository, header_id: int
) -> None:
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="C",
            code_name="C",
            code_order=2,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="A",
            code_name="A",
            code_order=2,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="B",
            code_name="B",
            code_order=1,
        )
    )
    items = repo.list_by_header(header_id)
    # order=1 first, then order=2 ordered alphabetically by code_id.
    assert [i.code_id for i in items] == ["B", "A", "C"]


def test_list_by_header_only_returns_that_headers_lines(
    repo: CodeLinesRepository,
    header_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    headers = CodeHeadersRepository(db_conn)
    other = headers.create(CodeHeader(code_header_id=None, code_header_name="Other"))
    assert other.code_header_id is not None
    repo.upsert(CodeLine(code_line_id=None, code_header_id=header_id, code_id="A", code_name="A"))
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=other.code_header_id,
            code_id="B",
            code_name="B",
        )
    )
    items = repo.list_by_header(header_id)
    assert len(items) == 1
    assert items[0].code_id == "A"


def test_reorder_assigns_orders_starting_at_one(repo: CodeLinesRepository, header_id: int) -> None:
    """reorder asigna code_order = índice 1-based según la lista provista."""
    for code_id in ("A", "B", "C"):
        repo.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=header_id,
                code_id=code_id,
                code_name=code_id,
            )
        )
    repo.reorder(header_id, ["B", "A", "C"])
    items = repo.list_by_header(header_id)
    assert [(i.code_id, i.code_order) for i in items] == [
        ("B", 1),
        ("A", 2),
        ("C", 3),
    ]


def test_reorder_ignores_codes_not_in_list(repo: CodeLinesRepository, header_id: int) -> None:
    """Códigos no incluidos en la lista mantienen su order anterior."""
    for code_id, order in (("A", 5), ("B", 6), ("C", 7)):
        repo.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=header_id,
                code_id=code_id,
                code_name=code_id,
                code_order=order,
            )
        )
    repo.reorder(header_id, ["A", "C"])  # B no se toca
    b = repo.get(header_id, "B")
    assert b is not None
    assert b.code_order == 6
