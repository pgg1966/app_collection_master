"""Manejo de conexiones SQLite."""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


def create_connection(db_path: Path | str) -> sqlite3.Connection:
    """Crea una conexión SQLite con WAL y FKs activadas.

    Args:
        db_path: path al archivo de DB. Usar ":memory:" para tests.

    Returns:
        Conexión configurada.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if str(db_path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    logger.debug("Conexión creada a %s", db_path)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Context manager para transacciones con rollback automático."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Rollback de transacción por excepción")
        raise
