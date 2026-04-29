"""Tests del migrator."""

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


def test_migrator_applies_initial_schema():
    """Verifica que la migración 001 deja el schema en versión 1."""
    conn = create_connection(":memory:")
    final_version = run_migrations(conn)
    assert final_version == 1


def test_migrator_creates_all_expected_tables(memory_db: sqlite3.Connection):
    """Verifica que se crearon todas las tablas esperadas."""
    rows = memory_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = {row["name"] for row in rows}

    expected = {
        "schema_version",
        "app_settings",
        "codes_headers",
        "codes_lines",
        "collections",
        "cards",
        "inventory",
        "transactions",
    }
    # SQLite agrega sqlite_sequence automáticamente con AUTOINCREMENT
    assert expected.issubset(table_names)


def test_migrator_is_idempotent(memory_db: sqlite3.Connection):
    """Correr migraciones dos veces no debe fallar ni duplicar nada."""
    initial_version = run_migrations(memory_db)
    second_version = run_migrations(memory_db)
    assert initial_version == second_version


def test_foreign_keys_are_enabled(memory_db: sqlite3.Connection):
    """Verifica que el PRAGMA foreign_keys está activo."""
    result = memory_db.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_cannot_create_collection_with_invalid_code_header(memory_db: sqlite3.Connection):
    """FK debe impedir crear colección con code_header_id inexistente."""
    with pytest.raises(sqlite3.IntegrityError):
        memory_db.execute(
            "INSERT INTO collections (collection_name, card_count, code_header_id) "
            "VALUES ('Test', 100, 999)"
        )
        memory_db.commit()
