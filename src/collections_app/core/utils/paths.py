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


def get_photo_cache_dir() -> Path:
    """Directorio compartido donde el admin cachea fotos descargadas de internet.

    Las fotos crudas viven acá (no por colección): si el mismo jugador aparece
    en dos colecciones, se reusa la foto si la card_key coincide.
    """
    d = get_app_data_dir() / "photo_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_generated_cards_dir(collection_id: int) -> Path:
    """Directorio donde el admin guarda los sketches generados por colección.

    Cada colección tiene su propio subdirectorio bajo
    `{app_data}/generated_cards/{collection_id}/`.
    """
    d = get_app_data_dir() / "generated_cards" / str(collection_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_generated_card_path(collection_id: int, card_key: str) -> Path:
    """Path al sketch generado para una card específica (puede no existir aún)."""
    return get_generated_cards_dir(collection_id) / f"{card_key}.png"
