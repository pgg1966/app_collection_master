"""Búsqueda y descarga de escudos por code_id desde Wikimedia Commons.

Cada `code_id` (ej. "ARG", "BRA") tiene UN escudo en
`get_crest_path(code_id)`. La cascada de descarga es:

1. Cache local válido — si ya existe un PNG > MIN_VALID_FILE_BYTES,
   no se redescarga (`is_valid_crest_file`).
2. Si el code_id está en `SPECIAL_CODES` (sets temáticos sin equipo
   nacional asociado, p.ej. Golden Ballers), se genera placeholder
   directamente — el usuario debe importar la imagen manualmente.
3. Override manual (`COMMONS_FILE_OVERRIDES`) — si el code_name está
   en el dict, se usa ese `File:` exacto en vez de buscar.
4. Búsqueda en Wikimedia Commons API con cascada de queries (logo,
   crest, badge, federación) y filtros heurísticos para descartar
   fotos de partidos / jugadores.
5. Si todo falla, retorna `SOURCE_NOT_FOUND` SIN escribir archivo —
   permite reintento automático en la próxima ejecución.

¿Por qué Commons y no Google CSE? Google Custom Search JSON API fue
cerrada a clientes nuevos en 2025: proyectos de GCP creados después
de esa fecha reciben HTTP 403 PERMISSION_DENIED aunque la API esté
"habilitada" en consola, sin workaround. Commons es gratis, sin API
key, sin cuota práctica, y además es la fuente original de los SVG
de escudos (Google los servía referenciando a Commons).
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

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
# La API de Wikimedia REQUIERE un User-Agent descriptivo (políticas de uso);
# sin él pueden devolver 403 silenciosamente.
COMMONS_USER_AGENT = "CollectionsApp/1.0 (admin tool for FIFA WC 2026 album)"
COMMONS_THUMB_SIZE = 300  # px — ancho del thumbnail rasterizado
COMMONS_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 15
RATE_LIMIT_DELAY = 1.0  # segundos entre find_crest cuando hay red
QUERY_DELAY = 0.5  # segundos entre queries dentro del mismo find_crest
COMMONS_SEARCH_LIMIT = 5  # resultados por query
CREST_TARGET_SIZE = (200, 200)
SVG_RENDER_SIZE = 200

# Tamaño mínimo (en bytes) que debe tener una respuesta HTTP para ser
# considerada una imagen real. Las descargas válidas (PNG/JPEG/SVG)
# están bien por encima de este umbral.
MIN_DOWNLOAD_BYTES = 500

# Tamaño mínimo (en bytes) de un PNG ya guardado para ser considerado
# un escudo válido en cache (también aplica a placeholders).
MIN_VALID_FILE_BYTES = 1_000

# "Magic bytes" de los formatos de imagen aceptados. Se chequean cuando
# el Content-Type de la respuesta no es `image/*`.
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
SOURCE_COMMONS = "commons"
SOURCE_COMMONS_OVERRIDE = "commons_override"
SOURCE_MANUAL = "manual"
SOURCE_PLACEHOLDER = "placeholder"
# `not_found`: la búsqueda no devolvió URLs descargables. NO se escribe
# archivo en disco para que la próxima ejecución reintente automáticamente.
SOURCE_NOT_FOUND = "not_found"


# Override manual: code_name (UPPER) → File: title exacto en Commons.
# Usar SOLO si la búsqueda automática falla repetidamente para ese país.
# Empieza vacío y se puebla iterativamente cuando se detecten faltantes.
COMMONS_FILE_OVERRIDES: dict[str, str] = {}


# Heurísticas para filtrar resultados de búsqueda — los títulos de archivo
# que matchean BLACKLIST_TERMS son fotos/escenas que no queremos. Los que
# matchean WHITELIST_TERMS son escudos/logos.
BLACKLIST_TERMS: tuple[str, ...] = (
    "match",
    "vs",
    "player",
    "stadium",
    "fans",
    "celebration",
    "kit",
    "jersey",
    "shirt",
    "uniform",
    "manager",
    "coach",
    "training",
    "fixtures",
)
WHITELIST_TERMS: tuple[str, ...] = (
    "logo",
    "crest",
    "badge",
    "emblem",
    "shield",
    "coat of arms",
    "federation",
    "association",
    "fa ",
    " fa",
)


@dataclass(frozen=True)
class CrestResult:
    """Resultado de buscar/descargar el escudo de un code_id."""

    code_id: str
    code_name: str
    local_path: Path
    source: str  # "cache" | "commons" | "commons_override" | "manual" | "placeholder" | "not_found"
    success: bool
    error: str | None = None


class CrestFinder:
    """Busca y descarga escudos de selecciones nacionales via Wikimedia Commons."""

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
        3. Override manual (`COMMONS_FILE_OVERRIDES`) si existe.
        4. Búsqueda en Commons con cascada de queries.
        5. `SOURCE_NOT_FOUND` — NO escribe nada en disco para permitir
           reintento automático en la próxima ejecución.
        """
        logger.info("Buscando crest para %s (%s)…", code_id, code_name)
        dest = get_crest_path(code_id)

        if is_valid_crest_file(dest):
            return CrestResult(code_id, code_name, dest, SOURCE_CACHE, True)
        if dest.exists():
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

        # Override manual: si está mapeado, no buscamos — vamos directo al File:
        override = COMMONS_FILE_OVERRIDES.get(code_name.upper())
        if override:
            url = self._get_commons_thumb_url(override)
            if url and self._download_and_process_crest(url, dest):
                logger.info("Crest %s: override Commons %r", code_id, override)
                return CrestResult(code_id, code_name, dest, SOURCE_COMMONS_OVERRIDE, True)

        # Búsqueda con cascada de queries (de más a menos específica).
        for query in self._build_commons_queries(code_name):
            titles = self._search_commons_files(query, limit=COMMONS_SEARCH_LIMIT)
            for title in titles:
                url = self._get_commons_thumb_url(title)
                if url and self._download_and_process_crest(url, dest):
                    logger.info(
                        "Crest %s: encontrado vía Commons (query=%r, file=%r)",
                        code_id,
                        query,
                        title,
                    )
                    return CrestResult(code_id, code_name, dest, SOURCE_COMMONS, True)
            # Pequeño delay entre queries para no abusar de la API
            time.sleep(QUERY_DELAY)

        logger.info("Crest %s: sin resultado — se reintentará la próxima vez", code_id)
        return CrestResult(
            code_id,
            code_name,
            dest,
            SOURCE_NOT_FOUND,
            False,
            error="No se encontró escudo en Wikimedia Commons",
        )

    def find_all_crests(
        self,
        codes: list[tuple[str, str]],
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> list[CrestResult]:
        """Procesa una lista de `(code_id, code_name)`.

        Aplica `RATE_LIMIT_DELAY` segundos entre find_crest reales (no entre
        cards cacheadas o especiales).
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
        """Importa una imagen local como escudo de un code_id."""
        dest = get_crest_path(code_id)
        try:
            with Image.open(source_image) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
        except (OSError, ValueError) as exc:
            return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, False, error=str(exc))
        return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, True)

    def cleanup_failed_placeholders(self, codes: list[tuple[str, str]]) -> int:
        """Borra placeholders previos de códigos NO especiales.

        Los placeholders heredados (ej. cuando find_crest aún escribía
        `SOURCE_PLACEHOLDER` en disco para errores) siguen siendo "cache
        válido" y bloquean reintentos. Llamar antes de `find_all_crests`
        cuando el usuario pide buscar de nuevo, para que esos países se
        reintenten en vez de devolverse del cache. SPECIAL_CODES NO se
        tocan (su placeholder es intencional).

        Retorna cuántos archivos borró.
        """
        deleted = 0
        for code_id, _ in codes:
            if code_id in SPECIAL_CODES:
                continue
            path = get_crest_path(code_id)
            if path.exists():
                path.unlink(missing_ok=True)
                deleted += 1
                logger.debug("Borrado placeholder previo: %s", code_id)
        return deleted

    # ------------------------------------------------------------------
    # Wikimedia Commons
    # ------------------------------------------------------------------

    def _build_commons_queries(self, code_name: str) -> list[str]:
        """Genera queries para Commons en orden de especificidad decreciente.

        Las primeras queries hintean SVG (escudos vectoriales son los
        archivos más limpios en Commons), las últimas dejan abierto el tipo.
        """
        name = code_name.title()
        return [
            f"{name} national football team crest svg",
            f"{name} national football team logo svg",
            f"{name} football federation logo svg",
            f"{name} football association crest svg",
            f"{name} national football team crest",
            f"{name} football federation logo",
        ]

    def _search_commons_files(self, query: str, limit: int = 5) -> list[str]:
        """Busca archivos en Commons en namespace File:. Retorna títulos filtrados.

        El filtro `_is_likely_crest_file` descarta resultados que parecen
        fotos de partidos / jugadores / estadios.
        """
        params: dict[str, str | int] = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,  # namespace File:
            "srlimit": limit,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                headers={"User-Agent": COMMONS_USER_AGENT},
                timeout=COMMONS_TIMEOUT,
            )
            if r.status_code != 200:
                logger.warning(
                    "[commons] search HTTP %s para %r — body=%s",
                    r.status_code,
                    query,
                    r.text[:300],
                )
                return []
            data = r.json()
            results = data.get("query", {}).get("search", []) or []
            raw_titles = [
                str(item["title"]) for item in results if isinstance(item, dict) and "title" in item
            ]
            titles = [t for t in raw_titles if self._is_likely_crest_file(t)]
            logger.info(
                "[commons] search %r → %d raw → %d filtrados",
                query,
                len(raw_titles),
                len(titles),
            )
            return titles
        except Exception as exc:  # noqa: BLE001
            logger.warning("[commons] search excepción: %s", exc)
            return []

    def _get_commons_thumb_url(self, file_title: str) -> str | None:
        """Para un `File:Foo.svg`, retorna la URL del thumbnail PNG rasterizado.

        Pide `iiurlwidth=COMMONS_THUMB_SIZE` para forzar a Commons a generar
        un PNG (incluso si el original es SVG). Esto evita depender de
        cairosvg para la mayoría de los escudos. Retorna `None` si no se
        puede resolver.
        """
        params: dict[str, str | int] = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": COMMONS_THUMB_SIZE,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                headers={"User-Agent": COMMONS_USER_AGENT},
                timeout=COMMONS_TIMEOUT,
            )
            if r.status_code != 200:
                return None
            data = r.json()
            pages = data.get("query", {}).get("pages", {}) or {}
            for page in pages.values():
                if not isinstance(page, dict):
                    continue
                infos = page.get("imageinfo") or []
                if not infos or not isinstance(infos[0], dict):
                    continue
                info = infos[0]
                # 1. thumburl: PNG rasterizado al ancho pedido — preferido.
                thumb_url = info.get("thumburl")
                if thumb_url:
                    return str(thumb_url)
                # 2. url: original. Si NO es SVG, lo usamos directo.
                orig_url = info.get("url")
                mime = (info.get("mime") or "").lower()
                if orig_url and "svg" not in mime:
                    return str(orig_url)
                # 3. SVG sin thumb — `_download_and_process_crest` intentará
                #    convertirlo con cairosvg (degrada a None si no está).
                return str(orig_url) if orig_url else None
            return None
        except Exception as exc:  # noqa: BLE001
            logger.debug("[commons] imageinfo falló para %r: %s", file_title, exc)
            return None

    @staticmethod
    def _is_likely_crest_file(file_title: str) -> bool:
        """Heurística de filtrado: el título debe parecer un escudo, no una foto."""
        lower = file_title.lower()
        if any(term in lower for term in BLACKLIST_TERMS):
            return False
        return any(term in lower for term in WHITELIST_TERMS)

    # ------------------------------------------------------------------
    # Descarga y procesamiento
    # ------------------------------------------------------------------

    def _download_and_process_crest(self, url: str, dest: Path) -> bool:
        """Descarga `url`, convierte a PNG RGBA `CREST_TARGET_SIZE` y guarda.

        Devuelve True si la descarga produjo un PNG válido en `dest`. La
        validación es defensiva: status, tamaño mínimo, detección de SVG
        (con conversión vía cairosvg si está), magic bytes, conversión a
        RGBA y re-validación post-save.
        """
        try:
            r = requests.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                headers={"User-Agent": COMMONS_USER_AGENT},
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
        """Rasteriza SVG a PNG usando cairosvg (dependencia opcional)."""
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
        """Crea un placeholder: círculo gris relleno con las iniciales."""
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
    """
    return path.exists() and path.stat().st_size > MIN_VALID_FILE_BYTES
