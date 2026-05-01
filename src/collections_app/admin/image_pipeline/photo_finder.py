"""Búsqueda y descarga de fotos de jugadores con fallback en cascada.

Estrategia (`find_photo`):
1. Caché compartido por jugador (`{country_code}_{name_slug}.jpg`).
   Indexado por jugador, no por card_key, así una foto descargada para
   "ARG_LIONEL_MESSI" sirve para Adrenalyn y Stickers Mundial sin
   redescargarla.
2. Wikipedia API (`page/summary`) — fuente más estable, sin rate limit.
3. DuckDuckGo image search — varias queries variadas (full name,
   apellido, español, con `site:` hints). UA rotation + rate limiting
   suave entre queries. Cada URL descargada se valida por tamaño mínimo,
   por aspect ratio (rechaza fotos grupales muy anchas), y por contener
   una cara detectable; si no, se prueba la siguiente.
4. Google Custom Search — último recurso (cuota 100/día). Solo se
   intenta si el contador `google_calls_used` no superó `google_quota`
   y si las env vars `GOOGLE_API_KEY`/`GOOGLE_CSE_ID` están configuradas.
5. Placeholder compartido — NO se guarda en el cache de jugadores
   (para que un próximo run pueda reintentar la búsqueda real).

El contador `google_calls_used` es por instancia y empieza en 0. El
caller (típicamente `ImagePipeline.run_google_fill`) lo resetea entre
runs y ajusta `google_quota` según necesite.
"""

import logging
import os
import random
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import requests
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

# Pool de User-Agents para rotación (rate-limit más suave; evita ser
# clasificado como bot demasiado rápido).
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "CollectionsApp/1.0",
]

MIN_IMAGE_DIM = 100
MAX_URLS_PER_QUERY = 3
HTTP_TIMEOUT = 15
WIKI_TIMEOUT = 8
GOOGLE_TIMEOUT = 8
DDG_QUERY_DELAY_SEC = 0.2  # rate-limit suave entre queries

# Filtros de calidad para `_is_good_photo`
MAX_ASPECT_RATIO = 1.8  # imágenes más anchas que altas → probables fotos grupales
MIN_MEAN_GRAY = 30  # más oscuro = imagen casi negra
MAX_MEAN_GRAY = 225  # más claro = imagen casi blanca
MIN_GRAY_STD = 20  # std bajo = imagen casi uniforme (sin contenido real)

PLACEHOLDER_FILENAME = "_placeholder.jpg"

# Cuota diaria default: 100 (límite de la free tier de Google Custom Search).
DEFAULT_GOOGLE_QUOTA = 100

# Env vars donde leer las credenciales de Google Custom Search.
GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"
GOOGLE_CSE_ID_ENV = "GOOGLE_CSE_ID"

SOURCE_CACHE = "cache"
SOURCE_DUCKDUCKGO = "duckduckgo"
SOURCE_WIKIPEDIA = "wikipedia"
SOURCE_GOOGLE = "google"
SOURCE_PLACEHOLDER = "placeholder"

# Sitios con buenas fotos de futbolistas; incluidos como `site:` hint en una query.
PREFERRED_SITES = [
    "transfermarkt.com",
    "wikipedia.org",
    "soccerway.com",
    "goal.com",
    "sofascore.com",
]


@dataclass(frozen=True)
class PhotoResult:
    """Resultado de la búsqueda de foto para una card."""

    player_name: str
    source_url: str
    local_path: Path
    source: str
    success: bool
    error: str | None = None


def _random_ua() -> str:
    """Retorna un User-Agent aleatorio del pool."""
    return random.choice(USER_AGENTS)  # noqa: S311 — no es uso criptográfico


class PhotoFinder:
    """Busca fotos con fallback en cascada y validación por face detection."""

    def __init__(
        self,
        cache_dir: Path,
        google_quota: int = DEFAULT_GOOGLE_QUOTA,
    ) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cascade_path = (
            cv2.data.haarcascades  # type: ignore[attr-defined]
            + "haarcascade_frontalface_default.xml"
        )
        self._face_cascade = cv2.CascadeClassifier(cascade_path)
        # Contador de llamadas a Google CSE por instancia. Se incrementa
        # cada vez que find_photo decide consultar Google. El caller
        # puede resetearlo entre runs (`finder.google_calls_used = 0`).
        self.google_quota = google_quota
        self.google_calls_used = 0

    def find_photo(
        self,
        player_name: str,
        country_name: str,
        country_code: str,
    ) -> PhotoResult:
        """Busca y devuelve la mejor foto disponible para ese jugador.

        Cascada: cache_jugador → Wikipedia → DuckDuckGo → Google CSE →
        placeholder. La foto se cachea bajo `{country_code}_{name_slug}.jpg`,
        compartida entre colecciones (un mismo jugador en dos álbumes
        distintos reusa la foto).
        """
        dest = self.cached_photo_path(player_name, country_code)
        if dest.exists():
            return PhotoResult(
                player_name=player_name,
                source_url=str(dest),
                local_path=dest,
                source=SOURCE_CACHE,
                success=True,
            )

        # 1) Wikipedia: estable y sin rate limiting. Aceptamos aunque el
        # cascade no detecte cara (los thumbs son chicos y a veces el
        # detector falla por ángulo); igual filtramos por aspect/contraste.
        wiki_url = self._search_wikipedia(player_name)
        if wiki_url and self._download_image(wiki_url, dest) and self._is_good_photo(dest):
            return PhotoResult(player_name, wiki_url, dest, SOURCE_WIKIPEDIA, True)
        dest.unlink(missing_ok=True)

        # 2) DuckDuckGo: varias queries hasta encontrar una imagen válida con cara.
        for query in self._build_queries(player_name, country_name):
            urls = self._search_duckduckgo(query)
            for url in urls[:MAX_URLS_PER_QUERY]:
                if (
                    self._download_image(url, dest)
                    and self._is_good_photo(dest)
                    and self._image_has_face(dest)
                ):
                    return PhotoResult(player_name, url, dest, SOURCE_DUCKDUCKGO, True)
                # Si descargó pero no pasó la validación, limpiar el archivo
                # parcial para que la próxima URL no tenga side-effects.
                dest.unlink(missing_ok=True)

        # 3) Google CSE como último recurso (cuota diaria de 100).
        if self._is_google_enabled():
            self.google_calls_used += 1
            for url in self.search_google_only(player_name, country_name)[:MAX_URLS_PER_QUERY]:
                if (
                    self._download_image(url, dest)
                    and self._is_good_photo(dest)
                    and self._image_has_face(dest)
                ):
                    return PhotoResult(player_name, url, dest, SOURCE_GOOGLE, True)
                dest.unlink(missing_ok=True)

        # 4) Placeholder compartido — NO lo guardamos como cache_jugador
        # para que la próxima corrida pueda reintentar la búsqueda real.
        placeholder_path = self._use_placeholder()
        return PhotoResult(
            player_name=player_name,
            source_url=str(placeholder_path),
            local_path=placeholder_path,
            source=SOURCE_PLACEHOLDER,
            success=True,
            error="Photo not found online",
        )

    # ------------------------------------------------------------------
    # Cache key por jugador
    # ------------------------------------------------------------------

    @staticmethod
    def _player_cache_key(player_name: str, country_code: str) -> str:
        """Genera una clave de cache normalizada para el jugador.

        Ejemplo: ("Lionel Messi", "ARG") → "ARG_LIONEL_MESSI".
        Toma sólo letras A-Z y dígitos; cualquier otro char se reemplaza
        por `_`. Múltiples `_` consecutivos se colapsan.
        """
        slug = re.sub(r"[^A-Z0-9]", "_", player_name.upper())
        slug = re.sub(r"_+", "_", slug).strip("_")
        return f"{country_code.upper()}_{slug}"

    def cached_photo_path(self, player_name: str, country_code: str) -> Path:
        """Path al .jpg cacheado para ese jugador (puede no existir aún).

        Útil para callers que necesitan saber si la foto ya está localmente
        sin disparar una búsqueda online (ej. resketch).
        """
        return self.cache_dir / f"{self._player_cache_key(player_name, country_code)}.jpg"

    def _is_google_enabled(self) -> bool:
        """¿Tiene sentido intentar Google?

        True si las env vars están configuradas Y el contador de llamadas
        no superó la cuota. Si Google no está configurado, la cascada
        salta directo a placeholder (sin gastar una llamada falsa).
        """
        if self.google_calls_used >= self.google_quota:
            return False
        return bool(os.environ.get(GOOGLE_API_KEY_ENV)) and bool(os.environ.get(GOOGLE_CSE_ID_ENV))

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def _build_queries(self, player_name: str, country_name: str) -> list[str]:
        """Construye múltiples queries para maximizar el match.

        Las primeras son las más específicas. Las últimas son rescatistas
        (apellido solo, español, sites preferidos).
        """
        name = player_name.title().strip()
        country = country_name.title().strip()
        parts = name.split()
        last_name = parts[-1] if len(parts) > 1 else name

        queries = [
            f"{name} {country} footballer face",
            f"{name} footballer portrait",
            f"{last_name} {country} football player",
            f"{last_name} footballer",
            f"{name} futbolista",  # español
            f"{last_name} soccer player portrait",
        ]
        sites = " OR ".join(f"site:{s}" for s in PREFERRED_SITES)
        queries.append(f"{name} {country} footballer ({sites})")
        return queries

    # ------------------------------------------------------------------
    # Backends de búsqueda
    # ------------------------------------------------------------------

    def _search_duckduckgo(self, query: str) -> list[str]:
        # Rate-limit suave entre queries para no caer en bot detection.
        time.sleep(DDG_QUERY_DELAY_SEC)
        try:
            from duckduckgo_search import DDGS  # noqa: PLC0415

            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=5, type_image="photo"))
            return [r["image"] for r in results if r.get("image")]
        except Exception as exc:  # noqa: BLE001
            logger.debug("DuckDuckGo search failed for %r: %s", query, exc)
            return []

    def _search_google(self, query: str) -> list[str]:
        """Google Custom Search Image API.

        Requiere `GOOGLE_API_KEY` y `GOOGLE_CSE_ID` en env. Si no están
        configuradas, retorna [] silenciosamente (no es un error: el
        usuario puede preferir no usar Google).

        El caller es responsable de respetar la cuota diaria — esta
        función solo realiza una llamada por invocación.
        """
        api_key = os.environ.get(GOOGLE_API_KEY_ENV)
        cse_id = os.environ.get(GOOGLE_CSE_ID_ENV)
        if not api_key or not cse_id:
            return []
        try:
            r = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": api_key,
                    "cx": cse_id,
                    "q": query,
                    "searchType": "image",
                    "num": "5",
                    "safe": "active",
                },
                timeout=GOOGLE_TIMEOUT,
                headers={"User-Agent": _random_ua()},
            )
            if r.status_code != 200:
                logger.debug("Google CSE returned %s for %r", r.status_code, query)
                return []
            data = r.json()
            items = data.get("items", []) or []
            return [it["link"] for it in items if it.get("link")]
        except Exception as exc:  # noqa: BLE001
            logger.debug("Google CSE failed for %r: %s", query, exc)
            return []

    def search_google_only(self, player_name: str, country_name: str) -> list[str]:
        """Realiza UNA query a Google y devuelve las URLs candidatas.

        Pensado para ser invocado desde `ImagePipeline.run_google_fill`,
        que controla el límite diario de 99 llamadas. Esta función NO
        sabe nada del contador — solo hace una llamada.
        """
        queries = self._build_queries(player_name, country_name)
        # Usamos solo la primera query (la más específica) para minimizar
        # consumo de la cuota diaria de Google.
        if not queries:
            return []
        return self._search_google(queries[0])

    def _search_wikipedia(self, player_name: str) -> str | None:
        try:
            name_encoded = player_name.title().replace(" ", "_")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name_encoded}"
            r = requests.get(url, timeout=WIKI_TIMEOUT, headers={"User-Agent": _random_ua()})
            if r.status_code == 200:
                data = r.json()
                thumb = data.get("thumbnail", {})
                if isinstance(thumb, dict):
                    src = thumb.get("source")
                    return str(src) if src else None
        except Exception as exc:  # noqa: BLE001
            logger.debug("Wikipedia lookup failed for %s: %s", player_name, exc)
        return None

    # ------------------------------------------------------------------
    # Descarga y validación
    # ------------------------------------------------------------------

    def _download_image(self, url: str, dest: Path) -> bool:
        """Descarga `url` a `dest` y valida tamaño mínimo (≥100x100)."""
        try:
            r = requests.get(
                url,
                timeout=HTTP_TIMEOUT,
                headers={"User-Agent": _random_ua()},
                stream=True,
            )
            if r.status_code != 200:
                return False
            with dest.open("wb") as fh:
                for chunk in r.iter_content(8192):
                    fh.write(chunk)
            img = cv2.imread(str(dest))
            if img is not None and img.shape[0] >= MIN_IMAGE_DIM and img.shape[1] >= MIN_IMAGE_DIM:
                return True
            dest.unlink(missing_ok=True)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Download failed for %s: %s", url, exc)
            dest.unlink(missing_ok=True)
        return False

    def _image_has_face(self, img_path: Path) -> bool:
        """Verifica que la imagen contenga al menos una cara detectable."""
        img = cv2.imread(str(img_path))
        if img is None:
            return False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
        )
        return len(faces) > 0

    def _is_good_photo(self, img_path: Path) -> bool:
        """Filtros de calidad rápidos sobre la foto descargada.

        Rechaza:
        - imágenes muy chicas (< MIN_IMAGE_DIM)
        - fotos demasiado anchas (aspect > 1.8): suelen ser grupos / equipos
        - imágenes casi negras o casi blancas (mean fuera de [30, 225])
        - imágenes casi uniformes (std < 20): probablemente fondo solo

        Retorna True si la imagen pasa todos los filtros.
        """
        img = cv2.imread(str(img_path))
        if img is None:
            return False
        h, w = img.shape[:2]
        if h < MIN_IMAGE_DIM or w < MIN_IMAGE_DIM:
            return False
        if (w / h) > MAX_ASPECT_RATIO:
            return False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mean_val = float(gray.mean())
        if mean_val < MIN_MEAN_GRAY or mean_val > MAX_MEAN_GRAY:
            return False
        std_val = float(gray.std())
        return std_val >= MIN_GRAY_STD

    # ------------------------------------------------------------------
    # Placeholder
    # ------------------------------------------------------------------

    def _use_placeholder(self) -> Path:
        """Retorna el path a un placeholder compartido entre todas las cards.

        Se genera una vez por instancia del cache_dir y se reusa. El
        archivo se llama `_placeholder.jpg` para no chocar con cache
        keys reales (esos empiezan con código de país).
        """
        dest = self.cache_dir / PLACEHOLDER_FILENAME
        if dest.exists():
            return dest
        official = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "data"
            / "assets"
            / "placeholder_card.png"
        )
        if official.exists():
            shutil.copy(official, dest)
        else:
            self._generate_placeholder(dest)
        return dest

    def _generate_placeholder(self, dest: Path) -> None:
        img = Image.new("L", (280, 320), 240)
        draw = ImageDraw.Draw(img)
        draw.polygon([(140, 60), (80, 200), (200, 200)], fill=180, outline=100)
        draw.rectangle([110, 200, 170, 230], fill=180, outline=100)
        draw.rectangle([90, 225, 190, 240], fill=180, outline=100)
        for y in range(80, 200, 15):
            draw.line([(100, y), (180, y)], fill=160, width=1)
        draw.text((140, 270), "?", fill=100, anchor="mm")
        img.save(dest, "JPEG", quality=85)
