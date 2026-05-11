"""Smoke test de la migración 002 — agrega `ocr_model_filename` a collections.

Aplica todas las migraciones disponibles sobre `:memory:` y verifica:

- `schema_version` queda en 2.
- `collections` tiene la nueva columna `ocr_model_filename TEXT NULL`.
- Las filas existentes pre-migración tienen `ocr_model_filename = NULL`
  (default de SQLite cuando se agrega columna sin DEFAULT).
- El resto del schema sigue intacto (no se rompió ninguna tabla del 001).
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


@pytest.fixture
def conn() -> sqlite3.Connection:
    """Conexión `:memory:` con TODAS las migraciones aplicadas."""
    c = create_connection(":memory:")
    run_migrations(c)
    return c


def _columns(conn: sqlite3.Connection, table: str) -> dict[str, sqlite3.Row]:
    return {row["name"]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_schema_version_includes_two(conn: sqlite3.Connection) -> None:
    """El historial incluye la 002. Las migraciones siguientes (003+)
    pueden estar aplicadas — solo verificamos que 002 sigue ahí."""
    versions = {r["version"] for r in conn.execute("SELECT version FROM schema_version").fetchall()}
    assert 2 in versions


def test_collections_has_ocr_model_filename_column(conn: sqlite3.Connection) -> None:
    cols = _columns(conn, "collections")
    assert "ocr_model_filename" in cols
    col = cols["ocr_model_filename"]
    # `TEXT` con NOT NULL = 0 (= nullable).
    assert col["type"].upper() == "TEXT"
    assert col["notnull"] == 0


def test_existing_rows_get_null_in_new_column(conn: sqlite3.Connection) -> None:
    """Insertar una collection sin tocar `ocr_model_filename` deja NULL."""
    # Crear el header mínimo + collection sin pasar la columna nueva.
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("WC", 3),
    )
    header_id = conn.execute("SELECT last_insert_rowid() AS r").fetchone()["r"]
    conn.execute(
        "INSERT INTO collections "
        "(collection_name, card_count, requires_code, code_field_name, "
        "code_header_id, is_premium, license_key_required, "
        "album_columns, album_rows, album_orientation) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("X", 0, 1, "País", header_id, 0, None, 3, 4, "portrait"),
    )
    row = conn.execute(
        "SELECT ocr_model_filename FROM collections WHERE collection_name = 'X'"
    ).fetchone()
    assert row["ocr_model_filename"] is None


def test_other_tables_intact_after_002(conn: sqlite3.Connection) -> None:
    """Tablas del 001 siguen existiendo con sus PKs subrogadas."""
    expected = {
        "schema_version",
        "app_settings",
        "codes_headers",
        "codes_lines",
        "collections",
        "cards",
        "inventory",
        "card_images",
        "transactions",
    }
    actual = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert expected.issubset(actual)
