"""Clase base abstracta para todos los repositorios."""

import sqlite3
from abc import ABC


class BaseRepository(ABC):  # noqa: B024 — marker del patrón Repository, no agrega API abstracta
    """Repository base. Todas las repos reciben una conexión SQLite.

    Las repositories NO crean la conexión, la reciben (inversion of control).
    Esto permite usar la misma conexión para varias operaciones en una
    transacción coordinada por el caller.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
