"""Tests del migrator."""

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


def test_migrator_applies_all_migrations():
    """Verifica que el migrator aplica todas las migraciones disponibles."""
    conn = create_connection(":memory:")
    final_version = run_migrations(conn)
    assert final_version >= 3  # 001 + 002 + 003


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
        "card_images",
    }
    # SQLite agrega sqlite_sequence automáticamente con AUTOINCREMENT
    assert expected.issubset(table_names)


def test_migration_003_creates_card_images_table(memory_db: sqlite3.Connection):
    """La migración 003 crea card_images con FK CASCADE desde cards."""
    cols = memory_db.execute("PRAGMA table_info(card_images)").fetchall()
    col_names = {row["name"] for row in cols}
    expected_cols = {
        "collection_id",
        "code_id",
        "card_number",
        "found_photo",
        "image_source",
        "image_path",
        "generated_at",
    }
    assert expected_cols.issubset(col_names)

    # FK con ON DELETE CASCADE hacia cards
    fks = memory_db.execute("PRAGMA foreign_key_list(card_images)").fetchall()
    assert any(fk["table"] == "cards" and fk["on_delete"] == "CASCADE" for fk in fks)

    # Index para queries por found_photo
    indexes = memory_db.execute("PRAGMA index_list(card_images)").fetchall()
    assert any(idx["name"] == "idx_card_images_found" for idx in indexes)


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


def test_migration_002_adds_code_order_column(memory_db: sqlite3.Connection):
    """Migración 002 debe agregar la columna code_order a codes_lines."""
    cols = {row["name"] for row in memory_db.execute("PRAGMA table_info(codes_lines)").fetchall()}
    assert "code_order" in cols


def test_migration_002_assigns_alphabetical_order_to_existing():
    """Aplicada en una DB con datos preexistentes, asigna orden alfabético."""
    conn = create_connection(":memory:")
    # Aplicar solo migración 001 simulando estado pre-002
    schema_001 = (
        "CREATE TABLE schema_version (version INTEGER PRIMARY KEY, "
        "applied_at TEXT NOT NULL DEFAULT (datetime('now')));"
        "CREATE TABLE codes_headers ("
        "  code_header_id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  code_header_name TEXT NOT NULL UNIQUE,"
        "  code_max_length INTEGER NOT NULL DEFAULT 5);"
        "CREATE TABLE codes_lines ("
        "  code_header_id INTEGER NOT NULL,"
        "  code_id TEXT NOT NULL,"
        "  code_name TEXT NOT NULL,"
        "  PRIMARY KEY (code_header_id, code_id),"
        "  FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id));"
        "INSERT INTO schema_version (version) VALUES (1);"
        "INSERT INTO codes_headers (code_header_name) VALUES ('FIFA');"
        "INSERT INTO codes_lines (code_header_id, code_id, code_name) VALUES "
        "  (1, 'BRA', 'Brasil'), (1, 'ARG', 'Argentina'), (1, 'CHI', 'Chile');"
    )
    conn.executescript(schema_001)
    conn.commit()
    # Aplicar todas las migraciones (debería aplicar 002)
    run_migrations(conn)

    rows = conn.execute("SELECT code_id, code_order FROM codes_lines ORDER BY code_id").fetchall()
    orders = {r["code_id"]: r["code_order"] for r in rows}
    assert orders == {"ARG": 1, "BRA": 2, "CHI": 3}
