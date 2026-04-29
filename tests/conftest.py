"""Fixtures compartidas de pytest."""

import sqlite3
from collections.abc import Iterator

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import Card, CodeHeader, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
)


@pytest.fixture
def memory_db() -> Iterator[sqlite3.Connection]:
    """DB SQLite en memoria con todas las migraciones aplicadas."""
    conn = create_connection(":memory:")
    run_migrations(conn)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sample_code_header(memory_db: sqlite3.Connection) -> CodeHeader:
    """Crea y persiste un CodeHeader 'FIFA Codes' con max_length 5."""
    repo = CodesHeadersRepository(memory_db)
    header = repo.create(
        CodeHeader(code_header_id=None, code_header_name="FIFA Codes", code_max_length=5)
    )
    memory_db.commit()
    return header


@pytest.fixture
def sample_collection(
    memory_db: sqlite3.Connection,
    sample_code_header: CodeHeader,
) -> Collection:
    """Crea y persiste una Collection 'FIFA WC 2026' con sample_code_header."""
    assert sample_code_header.code_header_id is not None
    repo = CollectionsRepository(memory_db)
    collection = repo.create(
        Collection(
            collection_id=None,
            collection_name="FIFA WC 2026",
            card_count=5,
            requires_code=True,
            code_field_name="País",
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()
    return collection


@pytest.fixture
def sample_cards(
    memory_db: sqlite3.Connection,
    sample_collection: Collection,
) -> list[Card]:
    """Crea y persiste 5 cards de prueba en sample_collection."""
    assert sample_collection.collection_id is not None
    cid = sample_collection.collection_id
    cards = [
        Card(collection_id=cid, code_id="ARG", card_number=1, card_name="Lionel Messi"),
        Card(collection_id=cid, code_id="ARG", card_number=2, card_name="Emiliano Martínez"),
        Card(collection_id=cid, code_id="BRA", card_number=1, card_name="Vinícius Jr."),
        Card(collection_id=cid, code_id="BRA", card_number=2, card_name="Neymar"),
        Card(collection_id=cid, code_id="FRA", card_number=1, card_name="Kylian Mbappé"),
    ]
    repo = CardsRepository(memory_db)
    repo.bulk_upsert(cards)
    memory_db.commit()
    return cards
