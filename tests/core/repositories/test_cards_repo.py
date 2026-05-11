"""Tests CRUD + queries específicas de CardsRepository (sin stats — paso 8)."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
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
def collection_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    collections = CollectionsRepository(db_conn)
    c = collections.create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make(collection_id: int, **overrides: object) -> Card:
    base = {
        "card_id": None,
        "collection_id": collection_id,
        "code_id": "X",
        "card_number": 1,
        "card_name": "Test",
    }
    base.update(overrides)
    return Card(**base)  # type: ignore[arg-type]


def test_list_by_collection_empty(repo: CardsRepository, collection_id: int) -> None:
    assert repo.list_by_collection(collection_id) == []


def test_create_returns_card_with_id(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    assert saved.card_number == 1


def test_create_violates_unique_business_key(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="X", card_number=1))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(collection_id, code_id="X", card_number=1))


def test_get_by_id_returns_card(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_name="Hello"))
    assert saved.card_id is not None
    fetched = repo.get_by_id(saved.card_id)
    assert fetched is not None
    assert fetched.card_name == "Hello"


def test_get_by_id_returns_none_for_missing(repo: CardsRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_business_key_returns_card(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="ARG", card_number=24, card_name="Messi"))
    fetched = repo.get(collection_id, "ARG", 24)
    assert fetched is not None
    assert fetched.card_name == "Messi"


def test_get_by_business_key_returns_none_for_missing(
    repo: CardsRepository, collection_id: int
) -> None:
    assert repo.get(collection_id, "X", 999) is None


def test_list_by_collection_orders_by_code_then_number(
    repo: CardsRepository, collection_id: int
) -> None:
    repo.create(_make(collection_id, code_id="B", card_number=2, card_name="b2"))
    repo.create(_make(collection_id, code_id="A", card_number=1, card_name="a1"))
    repo.create(_make(collection_id, code_id="A", card_number=2, card_name="a2"))
    items = repo.list_by_collection(collection_id)
    assert [(c.code_id, c.card_number) for c in items] == [
        ("A", 1),
        ("A", 2),
        ("B", 2),
    ]


def test_list_by_collection_only_returns_that_collections_cards(
    repo: CardsRepository, collection_id: int, db_conn: sqlite3.Connection
) -> None:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="OtherH"))
    assert h.code_header_id is not None
    other = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OtherC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert other.collection_id is not None
    repo.create(_make(collection_id, code_id="X", card_number=1))
    repo.create(_make(other.collection_id, code_id="X", card_number=1))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].collection_id == collection_id


def test_list_by_code_filters_correctly(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="A", card_number=1))
    repo.create(_make(collection_id, code_id="A", card_number=2))
    repo.create(_make(collection_id, code_id="B", card_number=1))
    items = repo.list_by_code(collection_id, "A")
    assert [c.card_number for c in items] == [1, 2]


def test_find_by_number_zero_matches(repo: CardsRepository, collection_id: int) -> None:
    assert repo.find_by_number(collection_id, 999) == []


def test_find_by_number_one_match(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="A", card_number=42, card_name="x"))
    items = repo.find_by_number(collection_id, 42)
    assert len(items) == 1
    assert items[0].code_id == "A"


def test_find_by_number_multiple_matches(repo: CardsRepository, collection_id: int) -> None:
    """Mismo número en distintos códigos: retorna todos ordenados por code_id."""
    repo.create(_make(collection_id, code_id="B", card_number=10))
    repo.create(_make(collection_id, code_id="A", card_number=10))
    repo.create(_make(collection_id, code_id="C", card_number=10))
    items = repo.find_by_number(collection_id, 10)
    assert [c.code_id for c in items] == ["A", "B", "C"]


def test_count_by_collection(repo: CardsRepository, collection_id: int) -> None:
    assert repo.count_by_collection(collection_id) == 0
    repo.create(_make(collection_id, card_number=1))
    repo.create(_make(collection_id, code_id="Y", card_number=2))
    assert repo.count_by_collection(collection_id) == 2


def test_upsert_inserts_when_new(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.upsert(_make(collection_id, card_number=5, card_name="V1"))
    assert saved.card_id is not None
    fetched = repo.get(collection_id, "X", 5)
    assert fetched is not None
    assert fetched.card_name == "V1"


def test_upsert_updates_on_conflict(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, card_number=5, card_name="Old"))
    repo.upsert(_make(collection_id, card_number=5, card_name="New"))
    fetched = repo.get(collection_id, "X", 5)
    assert fetched is not None
    assert fetched.card_name == "New"


def test_bulk_upsert_returns_count(repo: CardsRepository, collection_id: int) -> None:
    cards = [_make(collection_id, card_number=i) for i in range(1, 6)]
    count = repo.bulk_upsert(cards)
    assert count == 5
    assert repo.count_by_collection(collection_id) == 5


def test_bulk_upsert_empty_list_returns_zero(repo: CardsRepository) -> None:
    assert repo.bulk_upsert([]) == 0


def test_bulk_upsert_updates_existing(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, card_number=1, card_name="Old1"))
    repo.create(_make(collection_id, card_number=2, card_name="Old2"))
    new = [
        _make(collection_id, card_number=1, card_name="New1"),
        _make(collection_id, card_number=2, card_name="New2"),
        _make(collection_id, card_number=3, card_name="New3"),
    ]
    repo.bulk_upsert(new)
    assert repo.count_by_collection(collection_id) == 3
    one = repo.get(collection_id, "X", 1)
    assert one is not None
    assert one.card_name == "New1"


def test_delete_by_id_returns_true_when_existed(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    assert repo.delete_by_id(saved.card_id) is True
    assert repo.get_by_id(saved.card_id) is None


def test_delete_by_id_returns_false_when_missing(repo: CardsRepository) -> None:
    assert repo.delete_by_id(999) is False


def test_delete_by_id_cascades_to_inventory(
    repo: CardsRepository, collection_id: int, db_conn: sqlite3.Connection
) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    db_conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (saved.card_id, 3))
    repo.delete_by_id(saved.card_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM inventory WHERE card_id = ?", (saved.card_id,)
    ).fetchone()
    assert remaining["c"] == 0


# ---------------------------------------------------------------------
# get_code_catalog (Sesión 5d / fix OCR)
# ---------------------------------------------------------------------


def test_get_code_catalog_empty_collection(repo: CardsRepository, collection_id: int) -> None:
    """Collection sin cards → catálogo vacío."""
    catalog = repo.get_code_catalog(collection_id)
    assert catalog.codes == ()
    assert catalog.max_number_by_code == {}


def test_get_code_catalog_returns_unique_codes(repo: CardsRepository, collection_id: int) -> None:
    """Múltiples cards con el mismo `code_id` aparecen una sola vez en `codes`."""
    repo.create(_make(collection_id, code_id="ARG", card_number=1))
    repo.create(_make(collection_id, code_id="ARG", card_number=2))
    repo.create(_make(collection_id, code_id="BRA", card_number=1))
    catalog = repo.get_code_catalog(collection_id)
    assert set(catalog.codes) == {"ARG", "BRA"}


def test_get_code_catalog_orders_codes_by_code_order(
    db_conn: sqlite3.Connection,
) -> None:
    """Si la colección tiene `codes_lines` con `code_order`, respeta ese orden."""
    headers = CodeHeadersRepository(db_conn)
    lines = CodeLinesRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    repo = CardsRepository(db_conn)

    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC"))
    assert h.code_header_id is not None
    for code, order in [("ZIM", 1), ("ARG", 2), ("ALG", 3)]:
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id=code,
                code_name=code,
                code_order=order,
            )
        )
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Mundial",
            card_count=3,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    for code in ("ALG", "ARG", "ZIM"):  # alfabético al insertar
        repo.create(_make(coll.collection_id, code_id=code, card_number=1))
    catalog = repo.get_code_catalog(coll.collection_id)
    assert catalog.codes == ("ZIM", "ARG", "ALG")


def test_get_code_catalog_returns_max_number_per_code(
    repo: CardsRepository, collection_id: int
) -> None:
    """`max(card_number)` por code_id, una entrada por código."""
    for code, num in [("ARG", 1), ("ARG", 18), ("ARG", 5), ("BRA", 20), ("KOR", 6)]:
        repo.create(_make(collection_id, code_id=code, card_number=num))
    catalog = repo.get_code_catalog(collection_id)
    assert catalog.max_number_by_code == {"ARG": 18, "BRA": 20, "KOR": 6}


def test_get_code_catalog_isolated_per_collection(
    repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    """El catálogo de una colección no se contamina con cards de otra."""
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="OtherH"))
    assert h.code_header_id is not None
    other = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OtherC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert other.collection_id is not None
    repo.create(_make(collection_id, code_id="X", card_number=5))
    repo.create(_make(other.collection_id, code_id="X", card_number=99))
    assert repo.get_code_catalog(collection_id).max_number_by_code == {"X": 5}
    assert repo.get_code_catalog(other.collection_id).max_number_by_code == {"X": 99}
