"""Búsqueda y descarga de fotos de jugadores con fallback en cascada.

Estrategia:
1. Caché local (`data/photo_cache/{card_key}.jpg`) — si existe, se usa.
2. DuckDuckGo image search — varias queries variadas (full name, apellido,
   español, con `site:` hints). Cada URL descargada se valida por tamaño
   mínimo Y por contener una cara detectable; si no, se prueba la siguiente.
3. Wikipedia API (`page/summary`).
4. Placeholder local generado con PIL.

La validación por cara usa el mismo Haar Cascade que `SketchGenerator`,
para que las imágenes que pasan el filtro acá también funcionen bien
en la etapa de sketch.
"""

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import requests
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

USER_AGENT = "CollectionsApp/1.0"
MIN_IMAGE_DIM = 100
MAX_URLS_PER_QUERY = 3
HTTP_TIMEOUT = 15  # antes 10, ahora más generoso para fotos grandes
WIKI_TIMEOUT = 8

SOURCE_CACHE = "cache"
SOURCE_DUCKDUCKGO = "duckduckgo"
SOURCE_WIKIPEDIA = "wikipedia"
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


class PhotoFinder:
    """Busca fotos con fallback en cascada y validación por face detection."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cascade_path = (
            cv2.data.haarcascades  # type: ignore[attr-defined]
            + "haarcascade_frontalface_default.xml"
        )
        self._face_cascade = cv2.CascadeClassifier(cascade_path)

    def find_photo(
        self,
        player_name: str,
        country_name: str,
        card_key: str,
    ) -> PhotoResult:
        """Busca y devuelve la mejor foto disponible para esa card."""
        dest = self.cache_dir / f"{card_key}.jpg"
        if dest.exists():
            return PhotoResult(
                player_name=player_name,
                source_url=str(dest),
                local_path=dest,
                source=SOURCE_CACHE,
                success=True,
            )

        # 1) DuckDuckGo: varias queries hasta encontrar una imagen válida con cara.
        for query in self._build_queries(player_name, country_name):
            urls = self._search_duckduckgo(query)
            for url in urls[:MAX_URLS_PER_QUERY]:
                if self._download_image(url, dest) and self._image_has_face(dest):
                    return PhotoResult(player_name, url, dest, SOURCE_DUCKDUCKGO, True)
                # Si descargó pero no pasó la validación, limpiar el archivo
                # parcial para que la próxima URL no tenga side-effects.
                dest.unlink(missing_ok=True)

        # 2) Wikipedia: aceptamos aunque el cascade no detecte cara (los
        # thumbs son chicos y a veces el detector falla por ángulo).
        wiki_url = self._search_wikipedia(player_name)
        if wiki_url and self._download_image(wiki_url, dest):
            return PhotoResult(player_name, wiki_url, dest, SOURCE_WIKIPEDIA, True)

        # 3) Placeholder local
        placeholder_path = self._use_placeholder(card_key)
        return PhotoResult(
            player_name=player_name,
            source_url=str(placeholder_path),
            local_path=placeholder_path,
            source=SOURCE_PLACEHOLDER,
            success=True,
            error="Photo not found online",
        )

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
        try:
            from duckduckgo_search import DDGS  # noqa: PLC0415

            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=5, type_image="photo"))
            return [r["image"] for r in results if r.get("image")]
        except Exception as exc:  # noqa: BLE001
            logger.debug("DuckDuckGo search failed for %r: %s", query, exc)
            return []

    def _search_wikipedia(self, player_name: str) -> str | None:
        try:
            name_encoded = player_name.title().replace(" ", "_")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name_encoded}"
            r = requests.get(url, timeout=WIKI_TIMEOUT, headers={"User-Agent": USER_AGENT})
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
                headers={"User-Agent": USER_AGENT},
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

    # ------------------------------------------------------------------
    # Placeholder
    # ------------------------------------------------------------------

    def _use_placeholder(self, card_key: str) -> Path:
        dest = self.cache_dir / f"{card_key}.jpg"
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
