"""Resolver paths estándar de la aplicación."""

import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    r"""Retorna el directorio donde guardar datos de la app.

    Windows: %APPDATA%\Collections
    macOS:   ~/Library/Application Support/Collections
    Linux:   ~/.local/share/Collections
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base / "Collections"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path(filename: str = "collections.db") -> Path:
    """Path al archivo de base de datos del usuario."""
    return get_app_data_dir() / filename


def get_logs_dir() -> Path:
    """Path al directorio de logs."""
    logs = get_app_data_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def get_schema_dir() -> Path:
    """Path al directorio con los SQLs de migración (dentro del paquete)."""
    return Path(__file__).resolve().parent.parent / "db" / "schema"
