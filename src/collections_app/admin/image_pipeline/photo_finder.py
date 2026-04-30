"""Búsqueda y descarga de fotos de jugadores con fallback en cascada.

Estrategia: DuckDuckGo image search → Wikipedia API → placeholder local.

Las fotos se cachean en `data/photo_cache/{card_key}.jpg` (path absoluto
configurable). Antes de bajar nada se verifica el caché.
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
MAX_DDG_ATTEMPTS = 3
HTTP_TIMEOUT = 10
WIKI_TIMEOUT = 8

SOURCE_CACHE = "cache"
SOURCE_DUCKDUCKGO = "duckduckgo"
SOURCE_WIKIPEDIA = "wikipedia"
SOURCE_PLACEHOLDER = "placeholder"


@dataclass(frozen=True)
class PhotoResult:
    """Resultado de la búsqueda de foto para una card."""

    player_name: str
    source_url: str
    local_path: Path
    source: str  # SOURCE_* constants
    success: bool
    error: str | None = None


class PhotoFinder:
    """Busca fotos de jugadores con fallback en cascada.

    Las llamadas a DDG y Wikipedia se hacen lazy (solo si no hay caché)
    y son tolerantes a fallos: cualquier excepción se traga y dispara
    el siguiente fallback.
    """

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def find_photo(
        self,
        player_name: str,
        country_name: str,
        card_key: str,
    ) -> PhotoResult:
        """Busca y devuelve un PhotoResult, descargando si hace falta.

        El `card_key` (ej. "ARG-24") se usa como nombre de archivo en el
        caché. Si ya existe, no se vuelve a descargar.
        """
        dest = self.cache_dir / f"{card_key}.jpg"
        if dest.exists():
            return PhotoResult(
                player_name=player_name,
                source_url=str(dest),
                local_path=dest,
                source=SOURCE_CACHE,
                success=True,
            )

        # 1) DuckDuckGo
        query = f"{player_name} {country_name} footballer face portrait"
        for url in self._search_duckduckgo(query)[:MAX_DDG_ATTEMPTS]:
            if self._download_image(url, dest):
                return PhotoResult(player_name, url, dest, SOURCE_DUCKDUCKGO, True)

        # 2) Wikipedia
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
    # Backends de búsqueda (extension points para tests)
    # ------------------------------------------------------------------

    def _search_duckduckgo(self, query: str) -> list[str]:
        """Retorna lista de URLs de imágenes encontradas (puede estar vacía)."""
        try:
            from duckduckgo_search import DDGS  # noqa: PLC0415

            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=5, type_image="photo"))
            return [r["image"] for r in results if r.get("image")]
        except Exception as exc:  # noqa: BLE001
            logger.debug("DuckDuckGo search failed: %s", exc)
            return []

    def _search_wikipedia(self, player_name: str) -> str | None:
        """Retorna URL de la imagen de Wikipedia o None."""
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

    def _download_image(self, url: str, dest: Path) -> bool:
        """Descarga una imagen a `dest`. Valida que sea decodificable y >= 50px."""
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

    def _use_placeholder(self, card_key: str) -> Path:
        """Copia (o genera) el placeholder oficial al caché para `card_key`."""
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
        """Genera un placeholder B&W mínimo (copa simplificada + signo de pregunta)."""
        img = Image.new("L", (280, 320), 240)
        draw = ImageDraw.Draw(img)
        # Copa simplificada
        draw.polygon([(140, 60), (80, 200), (200, 200)], fill=180, outline=100)
        draw.rectangle([110, 200, 170, 230], fill=180, outline=100)
        draw.rectangle([90, 225, 190, 240], fill=180, outline=100)
        for y in range(80, 200, 15):
            draw.line([(100, y), (180, y)], fill=160, width=1)
        draw.text((140, 270), "?", fill=100, anchor="mm")
        img.save(dest, "JPEG", quality=85)
