"""Búsqueda y descarga de escudos por code_id desde Google Custom Search.

Cada `code_id` (ej. "ARG", "BRA") tiene UN escudo en
`get_crest_path(code_id)`. La cascada de descarga es:

1. Cache local válido — si ya existe un PNG > MIN_VALID_FILE_BYTES,
   no se redescarga (`is_valid_crest_file`).
2. Si el code_id está en `SPECIAL_CODES` (sets temáticos sin equipo
   nacional asociado, p.ej. Golden Ballers), se genera placeholder
   directamente — el usuario debe importar la imagen manualmente.
3. Google Custom Search API (`searchType=image`, `imgType=clipart`) con
   queries en orden de especificidad decreciente. Wikipedia/Commons
   resultaron poco confiables (devolvían fotos de partidos o nada);
   Google CSE filtrando por `clipart` apunta directo a logos/escudos.
4. Si todo falla, se genera un placeholder con las iniciales del
   code_id sobre un círculo gris.

Las API keys (`google_api_key`, `google_cse_id`) viven en `app_settings`.
Si no están configuradas, la cascada salta a placeholder con un log
explícito (no es un error).
"""

import io
import logging
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from collections_app.core.repositories.settings_repo import SettingsRepository
from collections_app.core.utils.paths import get_crest_path, get_crests_dir

logger = logging.getLogger(__name__)

GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
DOWNLOAD_TIMEOUT = 15  # segundos para descargas y para llamados a Google CSE
USER_AGENT = "CollectionsApp/1.0"
RATE_LIMIT_DELAY = 1.0  # segundos entre requests reales (no entre cache hits)
CREST_TARGET_SIZE = (200, 200)
SVG_RENDER_SIZE = 200
GOOGLE_RESULTS_PER_QUERY = 5

# Tamaño mínimo (en bytes) que debe tener una respuesta HTTP para ser
# considerada una imagen real. Las descargas válidas (PNG/JPEG/SVG) están
# bien por encima de este umbral.
MIN_DOWNLOAD_BYTES = 500

# Tamaño mínimo (en bytes) de un PNG ya guardado para ser considerado
# un escudo válido en cache (también aplica a placeholders).
MIN_VALID_FILE_BYTES = 1_000

# "Magic bytes" de los formatos de imagen aceptados. Se chequean cuando
# el Content-Type de la respuesta no es `image/*` (algunos CDNs sirven
# las imágenes con `application/octet-stream` o tras un redirect).
IMAGE_MAGIC_BYTES: tuple[bytes, ...] = (
    b"\x89PNG",
    b"\xff\xd8",  # JPEG
    b"GIF",
    b"RIFF",  # WebP empieza con RIFF....WEBP
    b"\x00\x00\x01\x00",  # ICO
)

# Sets especiales (no son selecciones nacionales): el escudo no se puede
# bajar automáticamente, requiere import manual.
SPECIAL_CODES = frozenset(
    {
        "GBL",
        "CON",
        "TKP",
        "DRK",
        "MMS",
        "GMC",
        "MRK",
        "EXC",
        "RTR",
        "FWC",
        "CCO",
    }
)

# Sources para `CrestResult.source`.
SOURCE_CACHE = "cache"
SOURCE_GOOGLE = "google"
SOURCE_MANUAL = "manual"
SOURCE_PLACEHOLDER = "placeholder"

# Settings keys donde viven las credenciales de Google CSE.
SETTING_GOOGLE_API_KEY = "google_api_key"
SETTING_GOOGLE_CSE_ID = "google_cse_id"


@dataclass(frozen=True)
class CrestResult:
    """Resultado de buscar/descargar el escudo de un code_id."""

    code_id: str
    code_name: str
    local_path: Path
    source: str  # "cache" | "google" | "manual" | "placeholder"
    success: bool
    error: str | None = None


def _build_crest_queries(code_name: str) -> list[tuple[str, str]]:
    """Genera queries Google CSE en orden de especificidad decreciente.

    Cada tupla es `(query, img_type)` donde `img_type` es el valor del
    parámetro `imgType` de Google CSE (`"clipart"` filtra por
    logos/íconos, `""` deja la búsqueda sin restringir el tipo).
    """
    name = code_name.title()  # "ARGENTINA" → "Argentina"
    return [
        (f"{name} national football team badge logo", "clipart"),
        (f"{name} football federation crest", "clipart"),
        (f"{name} soccer federation logo", "clipart"),
        (f"{name} national football team crest logo", ""),
    ]


class CrestFinder:
    """Busca y descarga escudos de selecciones nacionales via Google CSE."""

    def __init__(self) -> None:
        self.crests_dir = get_crests_dir()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def find_crest(
        self,
        code_id: str,
        code_name: str,
        conn: sqlite3.Connection,
    ) -> CrestResult:
        """Busca el escudo para un `code_id`.

        Cascada:
        1. Cache válido (`is_valid_crest_file`).
        2. Si está en `SPECIAL_CODES` → placeholder con iniciales.
        3. Google Custom Search (con keys leídas de `app_settings`).
        4. Placeholder con iniciales.

        `conn` se usa solo para leer las API keys de Google CSE desde
        `app_settings`. Devuelve un `CrestResult` con el path local y el
        `source`.
        """
        logger.info("Buscando crest para %s (%s)…", code_id, code_name)
        dest = get_crest_path(code_id)

        if is_valid_crest_file(dest):
            return CrestResult(code_id, code_name, dest, SOURCE_CACHE, True)
        if dest.exists():
            # Existe pero es inválido (intento previo fallido). Lo borramos
            # para que la cascada vuelva a intentar bajarlo limpiamente.
            dest.unlink(missing_ok=True)
            logger.debug("Borrado crest inválido en cache: %s", dest)

        if code_id in SPECIAL_CODES:
            self._generate_placeholder_crest(code_id, dest)
            return CrestResult(
                code_id,
                code_name,
                dest,
                SOURCE_PLACEHOLDER,
                True,
                error="Set especial — importar imagen manualmente",
            )

        urls = self._search_google_crest(code_name, conn)
        if not urls:
            logger.info("Crest %s: Google CSE no devolvió URLs — usando placeholder", code_id)
            self._generate_placeholder_crest(code_id, dest)
            return CrestResult(
                code_id,
                code_name,
                dest,
                SOURCE_PLACEHOLDER,
                True,
                error="Google CSE no devolvió resultados",
            )

        logger.info(
            "Crest %s: Google CSE devolvió %d URLs — intentando descarga",
            code_id,
            len(urls),
        )
        for url in urls:
            if self._download_and_process_crest(url, dest):
                logger.info("Crest %s encontrado via Google CSE", code_id)
                return CrestResult(code_id, code_name, dest, SOURCE_GOOGLE, True)

        logger.info("Crest %s: ninguna URL de Google CSE descargable — placeholder", code_id)
        self._generate_placeholder_crest(code_id, dest)
        return CrestResult(
            code_id,
            code_name,
            dest,
            SOURCE_PLACEHOLDER,
            True,
            error="Ninguna URL de Google CSE pudo descargarse",
        )

    def find_all_crests(
        self,
        codes: list[tuple[str, str]],
        conn: sqlite3.Connection,
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> list[CrestResult]:
        """Procesa una lista de `(code_id, code_name)`.

        Aplica un rate-limit de `RATE_LIMIT_DELAY` segundos entre los
        requests reales (no entre cards cacheadas o especiales).
        """
        results: list[CrestResult] = []
        total = len(codes)
        first_network_call = True
        for i, (code_id, code_name) in enumerate(codes, start=1):
            dest = get_crest_path(code_id)
            needs_network = not is_valid_crest_file(dest) and code_id not in SPECIAL_CODES
            if needs_network and not first_network_call:
                time.sleep(RATE_LIMIT_DELAY)
            result = self.find_crest(code_id, code_name, conn)
            if needs_network:
                first_network_call = False
            results.append(result)
            if on_progress is not None:
                on_progress(i, total, f"{code_id} {code_name}")
        return results

    def import_manual_crest(self, code_id: str, source_image: Path) -> CrestResult:
        """Importa una imagen local como escudo de un code_id.

        Convierte a RGBA, redimensiona a `CREST_TARGET_SIZE` y guarda
        como PNG en `get_crest_path(code_id)`.
        """
        dest = get_crest_path(code_id)
        try:
            with Image.open(source_image) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
        except (OSError, ValueError) as exc:
            return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, False, error=str(exc))
        return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, True)

    # ------------------------------------------------------------------
    # Google Custom Search
    # ------------------------------------------------------------------

    def _search_google_crest(self, code_name: str, conn: sqlite3.Connection) -> list[str]:
        """Busca escudos via Google CSE. Retorna lista de URLs en orden de relevancia.

        Las queries se prueban en orden de especificidad. La primera que
        devuelve resultados corta el bucle (no acumulamos URLs de queries
        sucesivas para no mezclar contextos). Si la API no está
        configurada o la cuota se agota, retorna `[]` sin levantar.
        """
        settings = SettingsRepository(conn)
        api_key = settings.get(SETTING_GOOGLE_API_KEY)
        cse_id = settings.get(SETTING_GOOGLE_CSE_ID)

        if not api_key or not cse_id:
            logger.info("Crest %s: Google CSE no configurado — placeholder", code_name)
            return []

        for query, img_type in _build_crest_queries(code_name):
            params: dict[str, str | int] = {
                "key": api_key,
                "cx": cse_id,
                "q": query,
                "searchType": "image",
                "num": GOOGLE_RESULTS_PER_QUERY,
                "safe": "active",
                "imgSize": "medium",
            }
            if img_type:
                params["imgType"] = img_type

            try:
                r = requests.get(
                    GOOGLE_CSE_URL,
                    params=params,
                    timeout=DOWNLOAD_TIMEOUT,
                )
                if r.status_code == 429:
                    logger.warning("Google CSE: cuota diaria agotada")
                    return []
                if r.status_code != 200:
                    logger.debug("Google CSE: HTTP %s para query %r", r.status_code, query)
                    continue
                items = r.json().get("items", []) or []
                urls = [
                    str(item["link"]) for item in items if isinstance(item, dict) and "link" in item
                ]
                if urls:
                    return urls
            except Exception as exc:  # noqa: BLE001
                logger.debug("Google CSE falló para %r: %s", query, exc)
                continue

        return []

    # ------------------------------------------------------------------
    # Descarga y procesamiento
    # ------------------------------------------------------------------

    def _download_and_process_crest(self, url: str, dest: Path) -> bool:
        """Descarga `url`, convierte a PNG RGBA `CREST_TARGET_SIZE` y guarda.

        Devuelve True si la descarga produjo un PNG válido en `dest`. La
        validación es defensiva en varios pasos:

        1. Status HTTP 200 y tamaño mínimo (`MIN_DOWNLOAD_BYTES`) — descarta
           respuestas vacías o páginas de error redirigidas.
        2. Detección de SVG (algunos resultados de Google CSE son SVG y
           Pillow no los abre): si hay SVG, intenta convertirlo con
           cairosvg; si no está instalado, falla limpiamente.
        3. Validación de Content-Type o "magic bytes" — si no es imagen
           reconocible, descarta antes de invocar a Pillow.
        4. Conversión a RGBA `CREST_TARGET_SIZE` con `thumbnail` (preserva
           aspect ratio).
        5. Re-validación post-save (`MIN_VALID_FILE_BYTES`) — si Pillow
           guardó algo trivialmente pequeño/corrupto, lo descarta.
        """
        try:
            r = requests.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                return False

            content = r.content
            if len(content) < MIN_DOWNLOAD_BYTES:
                logger.debug(
                    "Descarga muy pequeña (%d bytes) para %s — descartando",
                    len(content),
                    url,
                )
                return False

            content_type = r.headers.get("Content-Type", "").lower()

            if "svg" in content_type or self._is_svg(content):
                png_bytes = self._svg_to_png(content)
                if png_bytes is None:
                    logger.debug("SVG no convertible para %s", url)
                    return False
                content = png_bytes
            elif "image" not in content_type and not self._has_image_magic(content):
                logger.debug(
                    "Respuesta no parece imagen (CT=%r) para %s",
                    content_type,
                    url,
                )
                return False

            with Image.open(io.BytesIO(content)) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
        except Exception as exc:  # noqa: BLE001
            logger.debug("No se pudo descargar/procesar %s: %s", url, exc)
            dest.unlink(missing_ok=True)
            return False

        if not dest.exists() or dest.stat().st_size < MIN_VALID_FILE_BYTES:
            dest.unlink(missing_ok=True)
            logger.debug("PNG guardado demasiado pequeño o vacío para %s", url)
            return False

        return True

    # ------------------------------------------------------------------
    # Validación e introspección de bytes
    # ------------------------------------------------------------------

    @staticmethod
    def _is_svg(content: bytes) -> bool:
        """Detecta si `content` empieza con un encabezado XML/SVG."""
        snippet = content[:512].lstrip().lower()
        return snippet.startswith(b"<?xml") or snippet.startswith(b"<svg")

    @staticmethod
    def _has_image_magic(content: bytes) -> bool:
        """True si los primeros bytes coinciden con un formato de imagen conocido."""
        return any(content.startswith(magic) for magic in IMAGE_MAGIC_BYTES)

    @staticmethod
    def _svg_to_png(svg_bytes: bytes) -> bytes | None:
        """Rasteriza SVG a PNG usando cairosvg (dependencia opcional).

        Retorna `None` si cairosvg no está instalado o si la conversión
        falla. La degradación es elegante: el caller usa placeholder.
        """
        try:
            import cairosvg
        except ImportError:
            logger.debug("cairosvg no instalado — no se puede convertir SVG a PNG")
            return None
        try:
            png = cairosvg.svg2png(
                bytestring=svg_bytes,
                output_width=SVG_RENDER_SIZE,
                output_height=SVG_RENDER_SIZE,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("cairosvg falló: %s", exc)
            return None
        return bytes(png) if png else None

    # ------------------------------------------------------------------
    # Placeholder
    # ------------------------------------------------------------------

    def _generate_placeholder_crest(self, code_id: str, dest: Path) -> None:
        """Crea un placeholder: círculo gris relleno con las iniciales.

        Se usa cuando Google CSE falla o cuando el code_id está en
        `SPECIAL_CODES` (sets sin equipo nacional asociado). El círculo
        va relleno (no solo outline) para garantizar que el PNG resultante
        supere `MIN_VALID_FILE_BYTES` y el cache lo considere válido.
        """
        size = CREST_TARGET_SIZE
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(size) // 20
        draw.ellipse(
            (margin, margin, size[0] - margin, size[1] - margin),
            fill=(230, 230, 230, 255),
            outline=(150, 150, 150, 220),
            width=3,
        )
        draw.text(
            (size[0] // 2, size[1] // 2),
            code_id[:3],
            fill=(120, 120, 120, 230),
            anchor="mm",
        )
        img.save(dest, "PNG")


# ----------------------------------------------------------------------
# Helpers de módulo (API pública usada también desde la vista)
# ----------------------------------------------------------------------


def is_valid_crest_file(path: Path) -> bool:
    """Retorna True si `path` existe y supera el tamaño mínimo válido.

    Los crests reales descargados y los placeholders generados internamente
    siempre superan `MIN_VALID_FILE_BYTES`. Cualquier archivo más chico es
    probablemente un intento previo fallido (truncado, vacío, corrupto).
    La vista usa esta función para evitar mostrar/cachear escudos que estén
    en disco pero rotos.
    """
    return path.exists() and path.stat().st_size > MIN_VALID_FILE_BYTES
