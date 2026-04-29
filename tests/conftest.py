"""Fixtures compartidas de pytest."""

import sqlite3
from collections.abc import Iterator

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


@pytest.fixture
def memory_db() -> Iterator[sqlite3.Connection]:
    """DB SQLite en memoria con todas las migraciones aplicadas."""
    conn = create_connection(":memory:")
    run_migrations(conn)
    try:
        yield conn
    finally:
        conn.close()
