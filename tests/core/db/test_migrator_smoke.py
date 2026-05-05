"""Smoke tests del migrator y de la conexión.

Verifican el comportamiento básico del scaffold antes de que existan
migraciones reales (Prompt 1). Cuando la primera migración aterrice,
extender `legacy/v0_1/tests/core/db/test_migrator.py` como referencia.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import (
    _get_current_version,
    run_migrations,
)


def test_create_connection_enables_foreign_keys() -> None:
    """`PRAGMA foreign_keys` debe quedar en 1 al crear la conexión."""
    conn = create_connection(":memory:")
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_create_connection_uses_row_factory() -> None:
    """Las filas vienen como `sqlite3.Row` (acceso por nombre de columna)."""
    conn = create_connection(":memory:")
    row = conn.execute("SELECT 1 AS n").fetchone()
    assert isinstance(row, sqlite3.Row)
    assert row["n"] == 1


def test_get_current_version_returns_zero_when_table_absent() -> None:
    """En una DB virgen sin `schema_version`, la versión actual es 0."""
    conn = create_connection(":memory:")
    assert _get_current_version(conn) == 0


def test_run_migrations_with_empty_schema_dir_returns_zero(tmp_path) -> None:
    """`schema_dir` existente pero sin .sql: no crea schema_version, retorna 0."""
    conn = create_connection(":memory:")
    final = run_migrations(conn, schema_dir=tmp_path)
    assert final == 0
    # Verificar que no se creó la tabla schema_version (no había migración
    # 001 que la incluyera).
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert "schema_version" not in tables


def test_run_migrations_is_idempotent_with_empty_dir(tmp_path) -> None:
    """Correr migraciones dos veces sobre schema_dir vacío no rompe."""
    conn = create_connection(":memory:")
    first = run_migrations(conn, schema_dir=tmp_path)
    second = run_migrations(conn, schema_dir=tmp_path)
    assert first == second == 0


def test_run_migrations_raises_on_missing_schema_dir(tmp_path) -> None:
    """`schema_dir` inexistente debe lanzar FileNotFoundError descriptivo."""
    conn = create_connection(":memory:")
    missing = tmp_path / "no_existe"
    with pytest.raises(FileNotFoundError, match=str(missing.name)):
        run_migrations(conn, schema_dir=missing)


def test_run_migrations_applies_a_minimal_fake_migration(tmp_path) -> None:
    """End-to-end: una migración fake escrita en disco se aplica y bumpea schema_version.

    Sirve para validar que el pipeline (ordenamiento por número, lectura,
    `executescript`, verificación de schema_version) está bien armado,
    sin depender de las migraciones reales que va a aterrizar Prompt 1.
    """
    sql = (
        "CREATE TABLE schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ");\n"
        "INSERT INTO schema_version (version) VALUES (1);\n"
    )
    (tmp_path / "001_initial.sql").write_text(sql, encoding="utf-8")
    conn = create_connection(":memory:")
    final = run_migrations(conn, schema_dir=tmp_path)
    assert final == 1
    # Re-correr es idempotente.
    second = run_migrations(conn, schema_dir=tmp_path)
    assert second == 1


def test_run_migrations_fails_if_migration_does_not_bump_schema_version(
    tmp_path,
) -> None:
    """Una migración que no inserta en `schema_version` debe disparar RuntimeError."""
    bad_sql = (
        "CREATE TABLE schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ");\n"
        # Falta INSERT INTO schema_version → debe romper.
        "CREATE TABLE foo (id INTEGER PRIMARY KEY);\n"
    )
    (tmp_path / "001_no_bump.sql").write_text(bad_sql, encoding="utf-8")
    conn = create_connection(":memory:")
    with pytest.raises(RuntimeError, match="schema_version"):
        run_migrations(conn, schema_dir=tmp_path)
