"""Repositorio para `app_settings`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.app_setting import AppSetting
from collections_app.core.repositories.base import BaseRepository


def _row_to_setting(row: sqlite3.Row) -> AppSetting:
    return AppSetting(key=row["setting_key"], value=row["setting_value"])


class AppSettingsRepository(BaseRepository):
    """CRUD sobre `app_settings`."""

    def get(self: AppSettingsRepository, key: str) -> AppSetting | None:
        """Retorna el setting por clave, o None si no existe."""
        row = self.conn.execute(
            "SELECT setting_key, setting_value FROM app_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        return _row_to_setting(row) if row else None

    def set(self: AppSettingsRepository, setting: AppSetting) -> None:
        """Inserta o actualiza el setting."""
        self.conn.execute(
            "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
            (setting.key, setting.value),
        )

    def delete(self: AppSettingsRepository, key: str) -> bool:
        """Borra el setting. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM app_settings WHERE setting_key = ?", (key,))
        return cursor.rowcount > 0

    def list_all(self: AppSettingsRepository) -> list[AppSetting]:
        """Lista todos los settings ordenados por clave."""
        rows = self.conn.execute(
            "SELECT setting_key, setting_value FROM app_settings ORDER BY setting_key"
        ).fetchall()
        return [_row_to_setting(r) for r in rows]
