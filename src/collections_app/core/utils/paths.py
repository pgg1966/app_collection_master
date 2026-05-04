"""Resolver paths estándar de la aplicación.

Soporta múltiples PERFILES de datos en la misma máquina. Cada perfil
tiene su propia DB, escudos, imágenes y logs — útil para separar
"personal" / "test" / "trabajo" sin tener que copiar archivos.

El perfil se setea UNA VEZ al arranque vía `set_active_profile()`
(típicamente desde el `main()` parseando `--profile`). El default
("default") usa la carpeta base sin subdirectorio para mantener
compatibilidad retro con instalaciones existentes.
"""

import os
import sys
from pathlib import Path

# Perfil activo. Se setea desde main() al parsear --profile.
# "default" → no agrega subdirectorio (compat con instalaciones viejas).
_active_profile: str = "default"


def set_active_profile(profile: str) -> None:
    """Setea el perfil activo. Llamar al inicio del main() de la app.

    Sanitiza: solo alfanumérico y guiones; el resto se reemplaza por `_`.
    Si queda vacío tras strip, vuelve a "default".

    Cualquier llamada a `get_app_data_dir()` posterior reflejará el cambio.
    """
    global _active_profile
    safe = "".join(c if c.isalnum() or c == "-" else "_" for c in profile.strip()).strip("_")
    _active_profile = safe or "default"


def get_active_profile() -> str:
    """Retorna el perfil activo (default si no se llamó set_active_profile)."""
    return _active_profile


def _get_bundle_dir() -> Path:
    """Directorio base de los assets EMBEBIDOS en el paquete.

    Resolución según el entorno:
    - **Desarrollo / instalación pip**: la raíz del paquete `collections_app`
      (sube dos niveles desde `core/utils/paths.py`).
    - **PyInstaller onefile**: `sys._MEIPASS` (carpeta temporal donde el
      bootloader extrae los datos al arrancar el .exe).

    Solo afecta a recursos READ-ONLY que viajan con la app — los archivos
    SQL de migración, por ejemplo. Los datos del usuario (DB, escudos,
    cards descargadas) NO van por acá; siempre viven en
    `get_app_data_dir()`.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # En el bundle de PyInstaller los datas se montan en
        # sys._MEIPASS/<dest_path>. El spec mapea schema/ a
        # "collections_app/core/db/schema", así que la raíz del bundle
        # es _MEIPASS y el paquete sigue desde "collections_app/".
        return Path(sys._MEIPASS) / "collections_app"
    # `paths.py` vive en collections_app/core/utils/, así que hay que
    # subir tres niveles para llegar a la raíz del paquete.
    return Path(__file__).resolve().parent.parent.parent


def get_app_data_dir() -> Path:
    r"""Retorna el directorio donde guardar datos del PERFIL ACTIVO.

    Layout:
      default:  %APPDATA%\Collections\
      personal: %APPDATA%\Collections\personal\
      test:     %APPDATA%\Collections\test\

    Windows: %APPDATA%\Collections[\<perfil>]
    macOS:   ~/Library/Application Support/Collections[/<perfil>]
    Linux:   ~/.local/share/Collections[/<perfil>]

    Las funciones derivadas (`get_database_path`, `get_crests_dir`,
    `get_generated_cards_dir`, `get_logs_dir`) heredan el perfil
    automáticamente.
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base / "Collections"
    if _active_profile != "default":
        app_dir = app_dir / _active_profile
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
    """Path al directorio con los SQLs de migración (dentro del paquete).

    Funciona tanto en desarrollo (paquete instalado) como en el .exe
    de PyInstaller (asset embebido en `_MEIPASS`).
    """
    return _get_bundle_dir() / "core" / "db" / "schema"


def get_crests_dir() -> Path:
    """Directorio donde el admin guarda los escudos por code_id.

    Un solo escudo por código (ej. `ARG.png`, `BRA.png`), compartido
    entre TODAS las colecciones que usen ese mismo header de códigos.
    """
    d = get_app_data_dir() / "crests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_crest_path(code_id: str) -> Path:
    """Path al escudo de un code_id específico (puede no existir aún)."""
    return get_crests_dir() / f"{code_id}.png"


def get_generated_cards_dir() -> Path:
    """Directorio raíz para imágenes de cards descargadas/generadas.

    Cada colección ocupa una subcarpeta (`<id>/`); el scraper de Panini
    y otras herramientas escriben acá. Los archivos se nombran por
    `card_number` zero-padded a 4 dígitos (ej. `0042.jpg`).
    """
    d = get_app_data_dir() / "generated_cards"
    d.mkdir(parents=True, exist_ok=True)
    return d


def format_card_filename(card_number: int, extension: str = "jpg") -> str:
    """Retorna el nombre de archivo de una card con padding de 4 dígitos.

    El padding fijo evita que `1.jpg` y `001.jpg` convivan en la misma
    carpeta y se vea desordenado en el explorador. La DB sigue guardando
    el `card_number` como INTEGER — el padding solo aplica al filename.

    Ejemplo:
        format_card_filename(1)         -> "0001.jpg"
        format_card_filename(42, "png") -> "0042.png"
        format_card_filename(42, ".png") -> "0042.png"   # acepta con o sin punto
    """
    return f"{card_number:04d}.{extension.lstrip('.')}"


def get_card_image_path(
    collection_id: int,
    card_number: int,
    extension: str = "jpg",
) -> Path:
    """Retorna el path completo esperado de la imagen de una card.

    Útil para escribir o consultar un path determinístico. Si necesitás
    encontrar la imagen probando varias extensiones, usá `find_card_image`.

    Ejemplo:
        %APPDATA%/Collections/generated_cards/1/0042.jpg
    """
    return (
        get_generated_cards_dir()
        / str(collection_id)
        / format_card_filename(card_number, extension)
    )


def find_card_image(collection_id: int, card_number: int) -> Path | None:
    """Busca la imagen de una card probando extensiones comunes.

    Retorna el primer path que existe entre `.jpg`, `.jpeg`, `.png`.
    Retorna `None` si ninguno existe (la imagen aún no se descargó o
    se generó).
    """
    base_dir = get_generated_cards_dir() / str(collection_id)
    stem = f"{card_number:04d}"
    for ext in ("jpg", "jpeg", "png"):
        candidate = base_dir / f"{stem}.{ext}"
        if candidate.exists():
            return candidate
    return None
