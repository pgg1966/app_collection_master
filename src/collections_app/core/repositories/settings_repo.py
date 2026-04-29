"""Repository simple key/value para la tabla app_settings."""

from collections_app.core.repositories.base import BaseRepository


class SettingsRepository(BaseRepository):
    """Acceso clave/valor a `app_settings`."""

    def get(self, key: str) -> str | None:
        """Retorna el valor de `key`, o None si no existe."""
        row = self.conn.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        value: str | None = row["setting_value"]
        return value

    def set(self, key: str, value: str) -> None:
        """Inserta o actualiza el valor de `key`."""
        self.conn.execute(
            "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
            (key, value),
        )

    def delete(self, key: str) -> bool:
        """Borra la entrada. Retorna True si se borró efectivamente."""
        cursor = self.conn.execute(
            "DELETE FROM app_settings WHERE setting_key = ?",
            (key,),
        )
        return cursor.rowcount > 0

    def get_int(self, key: str) -> int | None:
        """Retorna el valor parseado como int, o None si no existe o no es int válido."""
        raw = self.get(key)
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError:
            return None
