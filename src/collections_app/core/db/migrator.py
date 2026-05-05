"""Sistema simple de migraciones de schema.

Las migraciones viven en `core/db/schema/`, numeradas `NNN_*.sql`.
Cada migración debe insertar su propio `INSERT INTO schema_version`
con la versión correspondiente; el migrator verifica que efectivamente
quedó registrada antes de continuar.

Reglas (CLAUDE.md sec 2.7):
- Migraciones inmutables: una vez aplicadas en cualquier entorno, no se editan.
- Idempotentes: correrlas dos veces no debe fallar.
- En transacción: cada `.sql` se aplica con `executescript`, lo cual
  envuelve todo el archivo en una transacción implícita de SQLite.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

from collections_app.core.utils.paths import get_schema_dir

logger = logging.getLogger(__name__)

MIGRATION_FILENAME_PATTERN = re.compile(r"^(\d{3})_.*\.sql$")


def _list_migration_files(schema_dir: Path) -> list[tuple[int, Path]]:
    """Lista las migraciones disponibles, ordenadas por versión."""
    migrations: list[tuple[int, Path]] = []
    for path in schema_dir.glob("*.sql"):
        match = MIGRATION_FILENAME_PATTERN.match(path.name)
        if match:
            migrations.append((int(match.group(1)), path))
    return sorted(migrations, key=lambda x: x[0])


def _get_current_version(conn: sqlite3.Connection) -> int:
    """Retorna la versión actual del schema, o 0 si la tabla no existe."""
    try:
        row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
        version: int = row["v"] if row and row["v"] is not None else 0
        return version
    except sqlite3.OperationalError:
        return 0


def run_migrations(conn: sqlite3.Connection, schema_dir: Path | None = None) -> int:
    """Aplica todas las migraciones pendientes.

    Args:
        conn: conexión SQLite.
        schema_dir: directorio con los SQLs. Si None, usa get_schema_dir().

    Returns:
        Versión final del schema. 0 si no hay migraciones disponibles
        y la DB nunca tuvo schema_version creada.
    """
    if schema_dir is None:
        schema_dir = get_schema_dir()

    if not schema_dir.exists():
        raise FileNotFoundError(f"No existe schema_dir: {schema_dir}")

    current = _get_current_version(conn)
    available = _list_migration_files(schema_dir)

    if not available:
        logger.warning("No hay archivos de migración en %s", schema_dir)
        return current

    pending = [(v, p) for v, p in available if v > current]

    if not pending:
        logger.info("Schema actualizado en versión %d", current)
        return current

    logger.info(
        "Aplicando %d migraciones (de v%d a v%d)",
        len(pending),
        current,
        pending[-1][0],
    )

    for version, path in pending:
        logger.info("Aplicando migración %03d: %s", version, path.name)
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        new_version = _get_current_version(conn)
        if new_version < version:
            msg = (
                f"Migración {path.name} no actualizó schema_version. "
                f"Asegurate de incluir el INSERT correspondiente "
                f"(schema_version version={version})."
            )
            raise RuntimeError(msg)

    final = _get_current_version(conn)
    logger.info("Migraciones completadas. Schema en v%d", final)
    return final
