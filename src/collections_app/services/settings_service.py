"""Service de settings clave/valor.

Wrapper sobre `AppSettingsRepository` que expone helpers tipados
(`get_int`, `set_bool`, etc.). El service normaliza los valores al
escribir (int → str, bool → 'true'/'false') para que la lectura sea
estable independientemente de quién haya seteado la entrada.
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.app_setting import AppSetting
from collections_app.core.repositories.app_settings_repo import AppSettingsRepository
from collections_app.services.exceptions import SettingsError


class SettingsService:
    """Configuración persistida — wrapper tipado sobre `app_settings`."""

    def __init__(self: SettingsService, conn: sqlite3.Connection) -> None:
        self._repo = AppSettingsRepository(conn)

    # ------------------------------------------------------------------
    # Acceso crudo
    # ------------------------------------------------------------------

    def get(self: SettingsService, key: str) -> AppSetting | None:
        """Setting por clave, o None."""
        return self._repo.get(key)

    def list_all(self: SettingsService) -> list[AppSetting]:
        """Todos los settings ordenados por clave."""
        return self._repo.list_all()

    def set(self: SettingsService, key: str, value: str | None) -> None:
        """Inserta o actualiza el setting. La key no puede ser vacia."""
        if not key:
            raise SettingsError("setting key no puede ser vacio")
        self._repo.set(AppSetting(key=key, value=value))

    def delete(self: SettingsService, key: str) -> bool:
        """Borra el setting. Retorna True si existía."""
        return self._repo.delete(key)

    # ------------------------------------------------------------------
    # Helpers tipados
    # ------------------------------------------------------------------

    def get_int(self: SettingsService, key: str) -> int | None:
        """Valor parseado como int, o None si no existe / no parsea."""
        s = self._repo.get(key)
        return s.as_int() if s else None

    def set_int(self: SettingsService, key: str, value: int) -> None:
        """Persiste un int como string en `app_settings.setting_value`."""
        self.set(key, str(value))

    def get_bool(self: SettingsService, key: str) -> bool | None:
        """Valor parseado como bool, o None si no existe / no reconocible."""
        s = self._repo.get(key)
        return s.as_bool() if s else None

    def set_bool(self: SettingsService, key: str, value: bool) -> None:
        """Persiste un bool con representación canónica 'true' / 'false'."""
        self.set(key, "true" if value else "false")
