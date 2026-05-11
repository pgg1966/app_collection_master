"""Smoke test de la migración 003 — agrega `ocr_guide_filename` a collections.

Aplica todas las migraciones disponibles sobre `:memory:` y verifica:

- `schema_version` queda en 3, con historial [1, 2, 3].
- `collections` tiene la nueva columna `ocr_guide_filename TEXT NULL`.
- Las filas existentes pre-migración tienen `ocr_guide_filename = NULL`.
- La columna del 002 (`ocr_model_filename`) sigue intacta.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


@pytest.fixture
def conn() -> sqlite3.Connection:
    c = create_connection(":memory:")
    run_migrations(c)
    return c


def _columns(conn: sqlite3.Connection, table: str) -> dict[str, sqlite3.Row]:
    return {row["name"]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def test_schema_version_is_three(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    assert row["v"] == 3


def test_schema_version_keeps_history(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT version FROM schema_version ORDER BY version").fetchall()
    versions = [r["version"] for r in rows]
    assert versions == [1, 2, 3]


def test_collections_has_ocr_guide_filename_column(conn: sqlite3.Connection) -> None:
    cols = _columns(conn, "collections")
    assert "ocr_guide_filename" in cols
    col = cols["ocr_guide_filename"]
    assert col["type"].upper() == "TEXT"
    assert col["notnull"] == 0


def test_collections_keeps_ocr_model_filename_column(conn: sqlite3.Connection) -> None:
    """La columna del 002 sigue presente — no se rompió."""
    cols = _columns(conn, "collections")
    assert "ocr_model_filename" in cols


def test_existing_rows_get_null_in_new_column(conn: sqlite3.Connection) -> None:
    """Insertar una collection sin tocar `ocr_guide_filename` deja NULL."""
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("WC", 3),
    )
    header_id = conn.execute("SELECT code_header_id FROM codes_headers").fetchone()[0]
    conn.execute(
        "INSERT INTO collections "
        "(collection_name, card_count, requires_code, code_field_name, code_header_id) "
        "VALUES (?, ?, ?, ?, ?)",
        ("WC2026", 100, 1, "Pais", header_id),
    )
    row = conn.execute(
        "SELECT ocr_guide_filename FROM collections WHERE collection_name = ?", ("WC2026",)
    ).fetchone()
    assert row["ocr_guide_filename"] is None
