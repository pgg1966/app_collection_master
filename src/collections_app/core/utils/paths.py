"""Resolución de paths del paquete.

En v0.2.0 sólo se expone `get_schema_dir()`, que apunta al directorio
con los SQLs de migración. Los paths de datos del usuario (DB, logs,
imágenes generadas) se reintroducirán cuando los necesite la app
(Prompt 2/3+), evitando arrastrar código de v0.1 que aún no tiene
consumidor en v0.2.
"""

from __future__ import annotations

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
