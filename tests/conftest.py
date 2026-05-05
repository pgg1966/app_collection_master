"""Fixtures compartidas para todos los tests.

Fixtures expuestas:

- `db_conn`: conexión SQLite `:memory:` con la migración 001 (y futuras)
  aplicadas. Scope `function` — DB fresca por test, sin leakage entre
  casos. Construida vía el migrator real (no setup paralelo en SQL): si
  una migración rompe, los tests de repos se enteran inmediatamente.

Tests de migrator y de schema NO usan esta fixture (tienen las suyas o
manejan la conexión inline) para no acoplarse al estado pre-migrado.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


@pytest.fixture
def db_conn() -> Iterator[sqlite3.Connection]:
    """Conexión `:memory:` con todas las migraciones aplicadas."""
    conn = create_connection(":memory:")
    run_migrations(conn)
    try:
        yield conn
    finally:
        conn.close()
