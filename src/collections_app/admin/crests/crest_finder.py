"""Búsqueda y descarga de escudos por code_id desde Wikipedia.

Cada `code_id` (ej. "ARG", "BRA") tiene UN escudo en
`get_crest_path(code_id)`. La cascada de descarga es:

1. Cache local válido — si ya existe un PNG > MIN_VALID_FILE_BYTES,
   no se redescarga (`is_valid_crest_file`).
2. Si el code_id está en `SPECIAL_CODES` (sets temáticos sin equipo
   nacional asociado, p.ej. Golden Ballers), se genera placeholder
   directamente — el usuario debe importar la imagen manualmente.
3. Wikipedia Action API (`prop=pageimages`): devuelve la URL del
   escudo principal de la página, incluso cuando es un SVG (a
   diferencia del endpoint REST `page/summary` que solo expone fotos
   fotográficas). Se pide `pithumbsize=300` para obtener un PNG
   rasterizado y evitar pasar por cairosvg.
4. Wikimedia Commons: si Wikipedia no tiene imagen, se busca el escudo
   por nombre de federación (ej. "Argentina football federation") en
   Commons y se baja `thumburl` (PNG rasterizado).
5. Si todo falla, se genera un placeholder con las iniciales del
   code_id sobre un círculo gris.

El nombre del país en `code_name` viene del CSV (ya en MAYÚSCULAS sin
acentos). Lo mapeamos al título de la Wikipedia inglesa porque es la
fuente más estable y completa de escudos.
"""

import io
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from collections_app.core.utils.paths import get_crest_path, get_crests_dir

logger = logging.getLogger(__name__)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
WIKIPEDIA_TIMEOUT = 15  # Action API puede ser más lenta que summary
DOWNLOAD_TIMEOUT = 15  # algunos PNGs grandes necesitan más margen
USER_AGENT = "CollectionsApp/1.0"
RATE_LIMIT_DELAY = 1.0  # segundos entre requests a Wikipedia
CREST_TARGET_SIZE = (200, 200)
SVG_RENDER_SIZE = 200
WIKIPEDIA_THUMB_SIZE = 300  # px — tamaño del thumbnail rasterizado pedido a la API

# Tamaño mínimo (en bytes) que debe tener una respuesta HTTP para ser
# considerada una imagen real. Las descargas válidas (PNG/JPEG/SVG de
# Wikipedia) están bien por encima de este umbral.
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
# bajar de Wikipedia automáticamente, requiere import manual.
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
SOURCE_WIKIPEDIA = "wikipedia"
SOURCE_MANUAL = "manual"
SOURCE_PLACEHOLDER = "placeholder"


# Mapeo de nombres en MAYÚSCULAS sin acentos (los que produce el cleanup
# de CSV) → título de la página en Wikipedia inglesa.
#
# Notas sobre títulos:
# - Algunos países usan "men's national" en el título oficial (Canada, USA,
#   New Zealand) porque el título corto sin "men's" es una página de
#   desambiguación que no contiene la imagen del escudo.
# - Mantenemos las dos variantes (español + inglés) cuando el CSV puede
#   venir en cualquiera de los dos idiomas.
COUNTRY_WIKIPEDIA_MAP: dict[str, str] = {
    "ARGELIA": "Algeria national football team",
    "ALGERIA": "Algeria national football team",
    "ARGENTINA": "Argentina national football team",
    "AUSTRALIA": "Australia national football team",
    "AUSTRIA": "Austria national football team",
    "BELGICA": "Belgium national football team",
    "BELGIUM": "Belgium national football team",
    "BOSNIA": "Bosnia and Herzegovina national football team",
    "BRASIL": "Brazil national football team",
    "BRAZIL": "Brazil national football team",
    "C. DE MARFIL": "Ivory Coast national football team",
    "IVORY COAST": "Ivory Coast national football team",
    "CABO VERDE": "Cape Verde national football team",
    "CAPE VERDE": "Cape Verde national football team",
    "CANADA": "Canada men's national soccer team",
    "COLOMBIA": "Colombia national football team",
    "CROACIA": "Croatia national football team",
    "CROATIA": "Croatia national football team",
    "CURAZAO": "Curaçao national football team",
    "CURACAO": "Curaçao national football team",
    "ECUADOR": "Ecuador national football team",
    "EGIPTO": "Egypt national football team",
    "EGYPT": "Egypt national football team",
    "ESCOCIA": "Scotland national football team",
    "SCOTLAND": "Scotland national football team",
    "ESPAÑA": "Spain national football team",
    "SPAIN": "Spain national football team",
    "ESTADOS UNIDOS": "United States men's national soccer team",
    "UNITED STATES": "United States men's national soccer team",
    "FRANCIA": "France national football team",
    "FRANCE": "France national football team",
    "GERMANY": "Germany national football team",
    "ALEMANIA": "Germany national football team",
    "GHANA": "Ghana national football team",
    "HAITI": "Haiti national football team",
    "INGLATERRA": "England national football team",
    "ENGLAND": "England national football team",
    "IRAN": "Iran national football team",
    "IRAQ": "Iraq national football team",
    "JAPON": "Japan national football team",
    "JAPAN": "Japan national football team",
    "JORDANIA": "Jordan national football team",
    "JORDAN": "Jordan national football team",
    "MARRUECOS": "Morocco national football team",
    "MOROCCO": "Morocco national football team",
    "MEXICO": "Mexico national football team",
    "NORUEGA": "Norway national football team",
    "NORWAY": "Norway national football team",
    "NUEVA ZELANDA": "New Zealand men's national football team",
    "NEW ZEALAND": "New Zealand men's national football team",
    "PAISES BAJOS": "Netherlands national football team",
    "NETHERLANDS": "Netherlands national football team",
    "PANAMA": "Panama national football team",
    "PARAGUAY": "Paraguay national football team",
    "PORTUGAL": "Portugal national football team",
    "QATAR": "Qatar national football team",
    "RD CONGO": "DR Congo national football team",
    "REP. CHECA": "Czech Republic national football team",
    "REP. COREA": "South Korea national football team",
    "KOREA REPUBLIC": "South Korea national football team",
    "ARABIA SAUDITA": "Saudi Arabia national football team",
    "SAUDI ARABIA": "Saudi Arabia national football team",
    "SENEGAL": "Senegal national football team",
    "SUDAFRICA": "South Africa national football team",
    "SOUTH AFRICA": "South Africa national football team",
    "SUECIA": "Sweden national football team",
    "SUIZA": "Switzerland national football team",
    "SWITZERLAND": "Switzerland national football team",
    "TUNEZ": "Tunisia national football team",
    "TUNISIA": "Tunisia national football team",
    "TURQUIA": "Turkey national football team",
    "URUGUAY": "Uruguay national football team",
    "UZBEKISTAN": "Uzbekistan national football team",
}


@dataclass(frozen=True)
class CrestResult:
    """Resultado de buscar/descargar el escudo de un code_id."""

    code_id: str
    code_name: str
    local_path: Path
    source: str  # "cache" | "wikipedia" | "manual" | "placeholder"
    success: bool
    error: str | None = None


class CrestFinder:
    """Busca y descarga escudos de países desde Wikipedia."""

    def __init__(self) -> None:
        self.crests_dir = get_crests_dir()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def find_crest(self, code_id: str, code_name: str) -> CrestResult:
        """Busca el escudo para un `code_id`.

        Cascada:
        1. Cache válido (`is_valid_crest_file`).
        2. Si está en `SPECIAL_CODES` → placeholder con iniciales.
        3. Wikipedia Action API (`prop=pageimages`).
        4. Fallback: Wikimedia Commons (búsqueda por federación nacional).
        5. Placeholder con iniciales.

        Devuelve un `CrestResult` con el path local y el `source`.
        """
        dest = get_crest_path(code_id)
        if is_valid_crest_file(dest):
            return CrestResult(code_id, code_name, dest, SOURCE_CACHE, True)
        if dest.exists():
            # Existe pero es inválido (intento previo fallido). Lo borramos
            # para que la cascada vuelva a intentar bajarlo limpiamente.
            dest.unlink()
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

        wiki_url = self._get_wikipedia_crest_url(code_name)
        if wiki_url and self._download_and_process_crest(wiki_url, dest):
            return CrestResult(code_id, code_name, dest, SOURCE_WIKIPEDIA, True)

        # Wikipedia falló (página sin imagen, SVG sin cairosvg, etc.):
        # intentar Commons como segundo origen antes de dar por perdido.
        commons_url = self._get_wikimedia_commons_url(code_name)
        if commons_url and self._download_and_process_crest(commons_url, dest):
            return CrestResult(code_id, code_name, dest, SOURCE_WIKIPEDIA, True)

        # Fallback final: placeholder con iniciales
        self._generate_placeholder_crest(code_id, dest)
        return CrestResult(
            code_id,
            code_name,
            dest,
            SOURCE_PLACEHOLDER,
            True,
            error="No se encontró escudo en Wikipedia ni en Commons",
        )

    def find_all_crests(
        self,
        codes: list[tuple[str, str]],
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> list[CrestResult]:
        """Procesa una lista de `(code_id, code_name)`.

        Aplica un rate-limit de `RATE_LIMIT_DELAY` segundos entre los
        requests a Wikipedia (no entre cards cacheadas o especiales).
        """
        results: list[CrestResult] = []
        total = len(codes)
        first_network_call = True
        for i, (code_id, code_name) in enumerate(codes, start=1):
            dest = get_crest_path(code_id)
            needs_network = not is_valid_crest_file(dest) and code_id not in SPECIAL_CODES
            if needs_network and not first_network_call:
                time.sleep(RATE_LIMIT_DELAY)
            result = self.find_crest(code_id, code_name)
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
    # Wikipedia
    # ------------------------------------------------------------------

    def _get_wikipedia_crest_url(self, code_name: str) -> str | None:
        """Resuelve `code_name` a una URL de imagen via Wikipedia Action API.

        Usa `prop=pageimages` (Action API) en vez del endpoint REST
        `page/summary`: este último solo devuelve la "lead image" cuando es
        una FOTO, así que para selecciones de fútbol —cuya imagen principal
        suele ser un escudo SVG— retorna respuestas sin imagen y pesa apenas
        500-700 bytes. La Action API con `piprop=original|thumbnail` sí
        expone el escudo y, además, sirve un thumbnail rasterizado en PNG
        (vía `pithumbsize`) que evita pasar por cairosvg en el caller.
        """
        title = COUNTRY_WIKIPEDIA_MAP.get(code_name.upper())
        if not title:
            logger.debug("No hay mapeo Wikipedia para %r", code_name)
            return None

        params: dict[str, str | int] = {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "piprop": "original|thumbnail",
            "pithumbsize": WIKIPEDIA_THUMB_SIZE,
            "format": "json",
            "redirects": 1,
        }
        try:
            r = requests.get(
                WIKIPEDIA_API_URL,
                params=params,
                timeout=WIKIPEDIA_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                logger.debug("Wikipedia Action API returned %s for %r", r.status_code, title)
                return None
            data = r.json()
            pages = data.get("query", {}).get("pages", {}) or {}
            for page in pages.values():
                if not isinstance(page, dict):
                    continue
                thumb = page.get("thumbnail") or {}
                thumb_url = thumb.get("source") if isinstance(thumb, dict) else None
                original = page.get("original") or {}
                orig_url = original.get("source") if isinstance(original, dict) else None
                # Preferir thumbnail (PNG rasterizado a WIKIPEDIA_THUMB_SIZE)
                # sobre original (puede ser SVG y forzaría cairosvg).
                url = thumb_url or orig_url
                if url:
                    return str(url)
            logger.debug("Wikipedia no devolvió imagen para %r", title)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.debug("Wikipedia Action API falló para %r: %s", title, exc)
            return None

    def _get_wikimedia_commons_url(self, code_name: str) -> str | None:
        """Fallback: busca el escudo en Wikimedia Commons.

        Cuando la búsqueda en Wikipedia falla (página sin pageimage o
        descarga rota), intenta encontrar un archivo en Commons buscando
        por "{country} football federation" en el namespace File:. Toma el
        primer resultado y resuelve su URL de descarga (`thumburl` cuando
        está disponible para evitar SVG, sino `url`).
        """
        title = COUNTRY_WIKIPEDIA_MAP.get(code_name.upper())
        if not title:
            return None
        # "Argentina national football team" → "Argentina"
        country_word = title.split()[0]
        search_query = f"{country_word} football federation"
        params: dict[str, str | int] = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "srnamespace": 6,  # namespace File:
            "srlimit": 3,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                timeout=WIKIPEDIA_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            results = data.get("query", {}).get("search", []) or []
            if not results:
                logger.debug("Commons search vacío para %r", search_query)
                return None
            file_title = results[0].get("title")
            if not file_title:
                return None
            return self._get_commons_file_url(str(file_title))
        except Exception as exc:  # noqa: BLE001
            logger.debug("Commons search falló para %r: %s", search_query, exc)
            return None

    def _get_commons_file_url(self, file_title: str) -> str | None:
        """Obtiene la URL de descarga de un `File:` de Commons.

        Pide `iiprop=url|thumburl` con `iiurlwidth=WIKIPEDIA_THUMB_SIZE` —
        el `thumburl` viene como PNG rasterizado incluso si el original es
        SVG, lo que evita la dependencia a cairosvg.
        """
        params: dict[str, str | int] = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|thumburl",
            "iiurlwidth": WIKIPEDIA_THUMB_SIZE,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                timeout=WIKIPEDIA_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            pages = data.get("query", {}).get("pages", {}) or {}
            for page in pages.values():
                if not isinstance(page, dict):
                    continue
                infos = page.get("imageinfo") or []
                if infos and isinstance(infos[0], dict):
                    url = infos[0].get("thumburl") or infos[0].get("url")
                    if url:
                        return str(url)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Commons file URL falló para %r: %s", file_title, exc)
        return None

    # ------------------------------------------------------------------
    # Descarga y procesamiento
    # ------------------------------------------------------------------

    def _download_and_process_crest(self, url: str, dest: Path) -> bool:
        """Descarga `url`, convierte a PNG RGBA `CREST_TARGET_SIZE` y guarda.

        Devuelve True si la descarga produjo un PNG válido en `dest`. La
        validación es defensiva en varios pasos:

        1. Status HTTP 200 y tamaño mínimo (`MIN_DOWNLOAD_BYTES`) — descarta
           respuestas vacías o páginas de error redirigidas.
        2. Detección de SVG (Wikipedia sirve algunos escudos como SVG y
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

        Se usa cuando Wikipedia falla o cuando el code_id está en
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

    Los crests reales descargados de Wikipedia y los placeholders generados
    internamente siempre superan `MIN_VALID_FILE_BYTES`. Cualquier archivo
    más chico es probablemente un intento previo fallido (truncado, vacío,
    corrupto). La vista usa esta función para evitar mostrar/cachear
    escudos que estén en disco pero rotos.
    """
    return path.exists() and path.stat().st_size > MIN_VALID_FILE_BYTES
