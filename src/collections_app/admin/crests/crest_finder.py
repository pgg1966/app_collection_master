"""Búsqueda y descarga de escudos por code_id desde Wikipedia.

Cada `code_id` (ej. "ARG", "BRA") tiene UN escudo en
`get_crest_path(code_id)`. La cascada de descarga es:

1. Cache local — si el archivo ya existe, no se redescarga.
2. Si el code_id está en `SPECIAL_CODES` (sets temáticos sin equipo
   nacional asociado, p.ej. Golden Ballers), se genera placeholder
   directamente — el usuario debe importar la imagen manualmente.
3. Wikipedia API: la página del seleccionado nacional contiene el
   thumbnail con el escudo o el escudo de la asociación. Bajamos esa
   imagen, la convertimos a RGBA 200×200 y la guardamos.
4. Si Wikipedia falla, generamos un placeholder con las iniciales del
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

WIKIPEDIA_TIMEOUT = 10
DOWNLOAD_TIMEOUT = 10
USER_AGENT = "CollectionsApp/1.0"
RATE_LIMIT_DELAY = 1.0  # segundos entre requests a Wikipedia
CREST_TARGET_SIZE = (200, 200)

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
        "PAN",
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
    "CABO VERDE": "Cape Verde national football team",
    "CANADA": "Canada national soccer team",
    "COLOMBIA": "Colombia national football team",
    "CROACIA": "Croatia national football team",
    "CROATIA": "Croatia national football team",
    "CURAZAO": "Curaçao national football team",
    "ECUADOR": "Ecuador national football team",
    "EGIPTO": "Egypt national football team",
    "EGYPT": "Egypt national football team",
    "ESCOCIA": "Scotland national football team",
    "ESPAÑA": "Spain national football team",
    "SPAIN": "Spain national football team",
    "ESTADOS UNIDOS": "United States men's national soccer team",
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
    "NUEVA ZELANDA": "New Zealand national football team",
    "PAISES BAJOS": "Netherlands national football team",
    "NETHERLANDS": "Netherlands national football team",
    "PANAMA": "Panama national football team",
    "PARAGUAY": "Paraguay national football team",
    "PORTUGAL": "Portugal national football team",
    "QATAR": "Qatar national football team",
    "RD CONGO": "DR Congo national football team",
    "REP. CHECA": "Czech Republic national football team",
    "REP. COREA": "South Korea national football team",
    "ARABIA SAUDITA": "Saudi Arabia national football team",
    "SENEGAL": "Senegal national football team",
    "SUDAFRICA": "South Africa national football team",
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

        Cascada: cache → (special: placeholder) → Wikipedia → placeholder.
        Devuelve un `CrestResult` con el path local y el source.
        """
        dest = get_crest_path(code_id)
        if dest.exists():
            return CrestResult(code_id, code_name, dest, SOURCE_CACHE, True)

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

        # Fallback: placeholder con iniciales
        self._generate_placeholder_crest(code_id, dest)
        return CrestResult(
            code_id,
            code_name,
            dest,
            SOURCE_PLACEHOLDER,
            True,
            error="No se encontró escudo en Wikipedia",
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
            needs_network = not dest.exists() and code_id not in SPECIAL_CODES
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
        """Resuelve `code_name` a una URL de imagen via Wikipedia API.

        1. Mapea `code_name` (ej. "ARGENTINA") al título de la página en
           Wikipedia inglesa (ej. "Argentina national football team").
        2. Usa el endpoint REST `page/summary/{title}` que devuelve un
           thumbnail con el escudo del seleccionado nacional.
        3. Si el thumbnail no existe, retorna None.
        """
        title = COUNTRY_WIKIPEDIA_MAP.get(code_name.upper())
        if not title:
            return None
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
        try:
            r = requests.get(
                url,
                timeout=WIKIPEDIA_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                logger.debug("Wikipedia returned %s for %r", r.status_code, title)
                return None
            data = r.json()
            thumb = data.get("originalimage") or data.get("thumbnail") or {}
            if not isinstance(thumb, dict):
                return None
            src = thumb.get("source")
            return str(src) if src else None
        except Exception as exc:  # noqa: BLE001
            logger.debug("Wikipedia lookup failed for %r: %s", title, exc)
            return None

    # ------------------------------------------------------------------
    # Descarga y procesamiento
    # ------------------------------------------------------------------

    def _download_and_process_crest(self, url: str, dest: Path) -> bool:
        """Descarga `url`, convierte a PNG RGBA `CREST_TARGET_SIZE` y guarda.

        Retorna True si todo salió bien. La conversión a RGBA preserva
        transparencia y el `thumbnail` mantiene aspect ratio.
        """
        try:
            r = requests.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            if r.status_code != 200:
                return False
            with Image.open(io.BytesIO(r.content)) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
            return True
        except Exception as exc:  # noqa: BLE001
            logger.debug("No se pudo descargar/procesar %s: %s", url, exc)
            return False

    # ------------------------------------------------------------------
    # Placeholder
    # ------------------------------------------------------------------

    def _generate_placeholder_crest(self, code_id: str, dest: Path) -> None:
        """Crea un placeholder simple: círculo gris con las iniciales.

        Se usa cuando Wikipedia falla o cuando el code_id está en
        `SPECIAL_CODES` (sets sin equipo nacional asociado).
        """
        size = CREST_TARGET_SIZE
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(size) // 20
        draw.ellipse(
            (margin, margin, size[0] - margin, size[1] - margin),
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
