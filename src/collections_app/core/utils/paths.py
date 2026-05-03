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
