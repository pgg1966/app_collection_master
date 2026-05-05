"""Repository base.

Todas las repos reciben una `sqlite3.Connection` por `__init__` y la
guardan en `self.conn`. La conexión la construye el caller (típicamente
un service o el bootstrap de la app); las repos nunca abren ni cierran.
"""

from __future__ import annotations

import sqlite3


class BaseRepository:
    """Repositorio base — almacena la conexión SQLite recibida."""

    def __init__(self: BaseRepository, conn: sqlite3.Connection) -> None:
        self.conn = conn
