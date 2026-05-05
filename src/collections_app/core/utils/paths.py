"""Resolución de paths del paquete y del directorio de datos del usuario.

- `get_schema_dir()`: assets read-only embebidos en el paquete (los SQLs
  de migración). Funciona en desarrollo y dentro del bundle de PyInstaller.
- `get_app_data_dir()` / `get_default_db_path()`: paths mutables del
  usuario, en el directorio convencional del SO.

Layout cross-platform:
- Windows : `%APPDATA%\\Collections\\`
- macOS   : `~/Library/Application Support/Collections/`
- Linux   : `$XDG_DATA_HOME/Collections/` (default `~/.local/share/Collections/`)

`get_app_data_dir()` crea el directorio si no existe.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _get_bundle_dir() -> Path:
    """Directorio raíz de los assets read-only embebidos en el paquete.

    En desarrollo / instalación pip apunta a la carpeta `collections_app`.
    En el bundle de PyInstaller (frozen) usa `sys._MEIPASS`.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "collections_app"
    # paths.py vive en collections_app/core/utils/, subir 3 niveles.
    return Path(__file__).resolve().parent.parent.parent


def get_schema_dir() -> Path:
    """Path al directorio con los SQLs de migración (`core/db/schema/`)."""
    return _get_bundle_dir() / "core" / "db" / "schema"


def get_app_data_dir() -> Path:
    """Directorio donde la app persiste datos del usuario (DB, etc.).

    Crea el directorio si no existe. v0.2 no tiene perfiles de usuario,
    así que es el path "default" — equivalente a `%APPDATA%\\Collections\\`
    en Windows.
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


def get_default_db_path() -> Path:
    """Path al archivo SQLite de la app, dentro del data dir del usuario."""
    return get_app_data_dir() / "collections.db"
