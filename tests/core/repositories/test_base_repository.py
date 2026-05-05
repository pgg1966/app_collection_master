"""Smoke tests del BaseRepository y de la fixture `db_conn`.

Verifica que:
- `BaseRepository` guarda la conexión recibida en `self.conn`.
- `db_conn` aplica las migraciones (schema_version >= 1, FKs ON).
"""

from __future__ import annotations

import sqlite3

from collections_app.core.repositories.base import BaseRepository


def test_base_repository_stores_connection() -> None:
    conn = sqlite3.connect(":memory:")
    repo = BaseRepository(conn)
    assert repo.conn is conn


def test_db_conn_fixture_has_migrations_applied(
    db_conn: sqlite3.Connection,
) -> None:
    """La fixture aplica al menos la migración 001."""
    row = db_conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    assert row["v"] >= 1


def test_db_conn_fixture_has_foreign_keys_enabled(
    db_conn: sqlite3.Connection,
) -> None:
    result = db_conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_db_conn_fixture_provides_fresh_db_per_test_step1(
    db_conn: sqlite3.Connection,
) -> None:
    """Primer test: inserta y verifica que aparece."""
    db_conn.execute(
        "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)", ("k", "v")
    )
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM app_settings").fetchone()
    assert rows["c"] == 1


def test_db_conn_fixture_provides_fresh_db_per_test_step2(
    db_conn: sqlite3.Connection,
) -> None:
    """Segundo test: la inserción del test anterior NO debe persistir."""
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM app_settings").fetchone()
    assert rows["c"] == 0
