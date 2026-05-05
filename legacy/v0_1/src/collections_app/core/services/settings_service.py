"""Servicio para configuración de la app (colección activa, etc.)."""

import sqlite3

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository, SettingsRepository

SETTING_KEY_ACTIVE_COLLECTION = "active_collection_id"


class SettingsService:
    """Operaciones de alto nivel sobre `app_settings`."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._settings = SettingsRepository(conn)
        self._collections = CollectionsRepository(conn)

    def get_active_collection_id(self) -> int | None:
        """Retorna el id de la colección activa, o None si no hay una configurada."""
        return self._settings.get_int(SETTING_KEY_ACTIVE_COLLECTION)

    def set_active_collection(self, collection_id: int) -> None:
        """Persiste el id de la colección activa."""
        self._settings.set(SETTING_KEY_ACTIVE_COLLECTION, str(collection_id))

    def clear_active_collection(self) -> None:
        """Elimina la configuración de colección activa."""
        self._settings.delete(SETTING_KEY_ACTIVE_COLLECTION)

    def get_active_collection(self) -> Collection | None:
        """Retorna la Collection activa o None si no hay configurada o no existe.

        Si el setting apunta a una colección que ya no existe, retorna None
        (no levanta error). Esto permite recuperarse de DBs reseteadas.
        """
        active_id = self.get_active_collection_id()
        if active_id is None:
            return None
        return self._collections.get_by_id(active_id)
