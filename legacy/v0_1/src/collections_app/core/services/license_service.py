"""Servicio de licencias para colecciones premium.

Diseño en dos niveles:
- Nivel 1 (actual): honor system local. Cada `Collection` premium guarda
  un SHA256 de la clave válida en `license_key_required`. El usuario
  ingresa una clave, se hashea y se compara. Suficiente como gate
  inicial para empezar a vender.
- Nivel 2 (futuro): validación online. Migración: solo cambiar la
  implementación de `LicenseValidator` sin tocar la UI ni el `LicenseService`.

Las claves desbloqueadas se persisten por colección en `app_settings`,
con la clave `license_unlocked:{collection_id}` y como valor el hash
que validó. Si el admin cambia el `license_key_required` de la
colección, el unlock anterior queda invalidado automáticamente.
"""

import hashlib
import sqlite3
from abc import ABC, abstractmethod

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CollectionsRepository,
    SettingsRepository,
)

SETTING_KEY_LICENSE_PREFIX = "license_unlocked:"


class LicenseValidator(ABC):
    """Interfaz abstracta para validar licencias.

    Una implementación concreta puede ser local (hash) u online (HTTP).
    """

    @abstractmethod
    def validate(self, collection_id: int, license_key: str) -> bool:
        """Retorna True si la clave es válida para la colección."""

    @abstractmethod
    def is_required(self, collection: Collection) -> bool:
        """Retorna True si la colección requiere licencia para usarse."""


class LocalHashLicenseValidator(LicenseValidator):
    """Valida la clave comparando su SHA256 con `collection.license_key_required`.

    NO es seguro contra usuarios técnicos (la clave válida no se transmite
    en cleartext, pero el `license_key_required` es legible en la DB
    distribuida). Sirve como gate inicial. Migración a Nivel 2 (online)
    cambia solo esta clase.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def validate(self, collection_id: int, license_key: str) -> bool:
        col = CollectionsRepository(self.conn).get_by_id(collection_id)
        if col is None:
            return False
        if not self.is_required(col):
            return True
        if not col.license_key_required:
            return False
        return self.hash_key(license_key) == col.license_key_required

    def is_required(self, collection: Collection) -> bool:
        return bool(collection.is_premium and collection.license_key_required)

    @staticmethod
    def hash_key(key: str) -> str:
        """SHA256 hex digest. Útil para que admin genere los hashes."""
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


class LicenseService:
    """Wrapper de alto nivel: usa un validador y persiste unlocks en settings."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        validator: LicenseValidator | None = None,
    ) -> None:
        self.conn = conn
        self._validator = validator or LocalHashLicenseValidator(conn)
        self._collections = CollectionsRepository(conn)
        self._settings = SettingsRepository(conn)

    def is_unlocked(self, collection_id: int) -> bool:
        """True si la colección no requiere licencia o ya fue desbloqueada."""
        col = self._collections.get_by_id(collection_id)
        if col is None:
            return False
        if not self._validator.is_required(col):
            return True
        stored = self._settings.get(SETTING_KEY_LICENSE_PREFIX + str(collection_id))
        if stored is None:
            return False
        # Si el admin cambió el license_key_required, el unlock previo
        # queda inválido automáticamente.
        return stored == col.license_key_required

    def unlock(self, collection_id: int, license_key: str) -> bool:
        """Valida la clave y persiste el unlock si pasa.

        Returns:
            True si la clave es válida (y se persistió, si aplica).
        """
        if not self._validator.validate(collection_id, license_key):
            return False
        col = self._collections.get_by_id(collection_id)
        if col is not None and self._validator.is_required(col):
            assert col.license_key_required is not None
            self._settings.set(
                SETTING_KEY_LICENSE_PREFIX + str(collection_id),
                col.license_key_required,
            )
            self.conn.commit()
        return True

    def lock(self, collection_id: int) -> None:
        """Quita el unlock persistido (no afecta colecciones free)."""
        deleted = self._settings.delete(SETTING_KEY_LICENSE_PREFIX + str(collection_id))
        if deleted:
            self.conn.commit()
