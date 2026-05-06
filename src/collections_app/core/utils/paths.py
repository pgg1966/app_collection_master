"""Resolución de paths del paquete y del directorio de datos del usuario.

- `get_schema_dir()`: assets read-only embebidos en el paquete (los SQLs
  de migración). Funciona en desarrollo y dentro del bundle de PyInstaller.
- `get_app_data_dir()`: directorio mutable del usuario, en la convención
  del SO.
- `get_db_path_for_profile(profile)`: archivo SQLite para un profile
  específico. `None` → `collections.db` (default sin profile);
  `"<name>"` → `collections_<name>.db`. v0.2 reemplaza el approach de
  v0.1 (subdirectorios por profile) con un único directorio que aloja
  archivos `collections_<profile>.db`.
- `get_generated_cards_dir_for_profile(profile)`: directorio para
  imágenes generadas por colección, segregado por profile vía
  subdirectorio. Sin consumidor todavía en v0.2 (Prompt 2/3 no tocan
  imágenes); existe acá para que el Prompt de imágenes futuro encuentre
  el helper listo.

Layout cross-platform:
- Windows : `%APPDATA%\\Collections\\`
- macOS   : `~/Library/Application Support/Collections/`
- Linux   : `$XDG_DATA_HOME/Collections/` (default `~/.local/share/Collections/`)

`get_app_data_dir()` crea el directorio si no existe.

**Validación de profiles:** sólo alfanumérico ASCII y guion bajo. Cualquier
otro carácter es rechazado por `_validate_profile()` con un `ValueError`
explícito — los callers (típicamente `main.py`) traducen eso a un exit
limpio con mensaje al usuario.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


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
    """Directorio donde la app persiste datos del usuario.

    Crea el directorio si no existe. Todos los profiles comparten este
    directorio raíz; cada profile usa su propio archivo
    `collections_<profile>.db` adentro.
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


def _validate_profile(profile: str) -> None:
    """Valida que el profile sea alfanumérico + guion bajo, no vacío.

    Caracteres no permitidos (espacios, separadores de path, símbolos)
    quedan fuera para evitar inyecciones en el filename y para que el
    nombre sea legible/copiable. Lanza ValueError con un mensaje
    pensado para mostrarle al usuario.
    """
    if not profile or not _PROFILE_NAME_RE.match(profile):
        raise ValueError(
            f"profile invalido {profile!r}: solo alfanumerico ASCII " f"y guion bajo, no vacio"
        )


def get_db_path_for_profile(profile: str | None) -> Path:
    """Path al archivo SQLite del profile.

    - `profile=None` → `<app_data>/collections.db` (default).
    - `profile="demo"` → `<app_data>/collections_demo.db`.

    Lanza `ValueError` si el profile contiene caracteres prohibidos.
    """
    if profile is None:
        return get_app_data_dir() / "collections.db"
    _validate_profile(profile)
    return get_app_data_dir() / f"collections_{profile}.db"


def get_default_db_path() -> Path:
    """Path al archivo SQLite default (sin profile).

    Equivalente a `get_db_path_for_profile(None)`. Mantiene retrocompat
    con callers existentes en bootstrap.
    """
    return get_db_path_for_profile(None)


def get_generated_cards_dir_for_profile(profile: str | None) -> Path:
    """Directorio para imágenes generadas, segregado por profile.

    - `profile=None` → `<app_data>/generated_cards/default/`.
    - `profile="demo"` → `<app_data>/generated_cards/demo/`.

    Crea el directorio si no existe. Sin consumidor en v0.2; existe
    para que el Prompt futuro de imágenes encuentre el helper listo.

    Lanza `ValueError` si el profile es inválido.
    """
    if profile is not None:
        _validate_profile(profile)
    subdir = profile if profile is not None else "default"
    target = get_app_data_dir() / "generated_cards" / subdir
    target.mkdir(parents=True, exist_ok=True)
    return target
