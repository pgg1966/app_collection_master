"""Capa de repositorios — acceso a la DB.

Cada tabla del schema (excepto `schema_version`) tiene su propia
`*Repository` que recibe una `sqlite3.Connection` y expone CRUD/queries
retornando dataclasses de `core.models`. Nunca tuplas, dicts ni
`sqlite3.Row` (CLAUDE.md sec 2.3).
"""

from collections_app.core.repositories.base import BaseRepository

__all__ = ["BaseRepository"]
