"""Tests de CardsRepository.get_stats_by_code (aggregate query)."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def fixture_setup(
    db_conn: sqlite3.Connection,
) -> tuple[int, int]:
    """Crea header con codes_lines + colección. Retorna (collection_id, header_id)."""
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    lines = CodeLinesRepository(db_conn)
    lines.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="ARG",
            code_name="Argentina",
            code_order=2,
        )
    )
    lines.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="BRA",
            code_name="Brasil",
            code_order=1,
        )
    )
    collections = CollectionsRepository(db_conn)
    c = collections.create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id, h.code_header_id


def _create_card(
    db_conn: sqlite3.Connection,
    collection_id: int,
    code_id: str,
    card_number: int,
    quantity: int = 0,
) -> int:
    """Crea card y opcionalmente inventory; retorna card_id."""
    cur = db_conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) " "VALUES (?, ?, ?, ?)",
        (collection_id, code_id, card_number, f"{code_id}-{card_number}"),
    )
    card_id = cur.lastrowid
    assert card_id is not None
    if quantity > 0:
        db_conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?)",
            (card_id, quantity),
        )
    return card_id


def test_get_stats_by_code_empty_collection(
    repo: CardsRepository, fixture_setup: tuple[int, int]
) -> None:
    collection_id, _ = fixture_setup
    assert repo.get_stats_by_code(collection_id) == []


def test_get_stats_by_code_returns_dataclasses(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    items = repo.get_stats_by_code(collection_id)
    assert all(isinstance(s, CodeStats) for s in items)


def test_get_stats_groups_by_code_id_with_counts(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """Para ARG: 3 cards total, 2 owned (qty>0). Para BRA: 2 total, 0 owned."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    _create_card(db_conn, collection_id, "ARG", 2, quantity=3)
    _create_card(db_conn, collection_id, "ARG", 3, quantity=0)
    _create_card(db_conn, collection_id, "BRA", 1)
    _create_card(db_conn, collection_id, "BRA", 2)
    items = repo.get_stats_by_code(collection_id)
    by_code = {s.code_id: s for s in items}
    assert by_code["ARG"].total == 3
    assert by_code["ARG"].owned == 2
    assert by_code["BRA"].total == 2
    assert by_code["BRA"].owned == 0


def test_get_stats_percentage_calculation(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    _create_card(db_conn, collection_id, "ARG", 2, quantity=2)
    _create_card(db_conn, collection_id, "ARG", 3, quantity=0)
    _create_card(db_conn, collection_id, "ARG", 4, quantity=0)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.total == 4
    assert arg.owned == 2
    assert arg.percentage == 50.0


def test_get_stats_resolves_code_name_from_codes_lines(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """code_name debe venir de codes_lines, no del code_id."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.code_name == "Argentina"


def test_get_stats_falls_back_to_code_id_when_no_codes_lines_match(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """Card con un code_id que no está en codes_lines: code_name = code_id."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ZZZ", 1)
    items = repo.get_stats_by_code(collection_id)
    zzz = next(s for s in items if s.code_id == "ZZZ")
    assert zzz.code_name == "ZZZ"


def test_get_stats_orders_by_code_order_then_code_id(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """BRA tiene code_order=1, ARG=2 → BRA primero."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1)
    _create_card(db_conn, collection_id, "BRA", 1)
    items = repo.get_stats_by_code(collection_id)
    assert [s.code_id for s in items] == ["BRA", "ARG"]


def test_get_stats_only_counts_target_collection(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, header_id = fixture_setup
    other = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="Other",
            card_count=10,
            requires_code=True,
            code_field_name="País",
            code_header_id=header_id,
        )
    )
    assert other.collection_id is not None
    _create_card(db_conn, collection_id, "ARG", 1)
    _create_card(db_conn, other.collection_id, "ARG", 1)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.total == 1


def test_get_stats_handles_zero_total_percentage(
    repo: CardsRepository, fixture_setup: tuple[int, int]
) -> None:
    """Sin cards, get_stats retorna lista vacía (no hay división por cero)."""
    collection_id, _ = fixture_setup
    items = repo.get_stats_by_code(collection_id)
    assert items == []
