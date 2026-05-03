"""Scraper de cards Panini desde cartophilic-info-exch.blogspot.com.

Tool standalone (no toca la DB) que crawlea posts del blog y descarga
las imágenes de cards en alta resolución a
`%APPDATA%/Collections/generated_cards/<collection_id>/`.

Soporta dos colecciones (FIFA WC 2026):
- "adrenalyn": Adrenalyn XL trading cards (~630 cards).
- "stickers" : Sticker album (~980 stickers).

Uso CLI:
    python -m collections_app.admin.tools.panini_scraper --collection adrenalyn
    python -m collections_app.admin.tools.panini_scraper --collection stickers
    python -m collections_app.admin.tools.panini_scraper \\
        --collection adrenalyn --max-pages 3        # smoke test rápido
"""

import argparse
import logging
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup, Tag

from collections_app.core.utils.paths import (
    format_card_filename,
    get_generated_cards_dir,
)

logger = logging.getLogger(__name__)

BLOG_BASE_URL = "https://cartophilic-info-exch.blogspot.com"
USER_AGENT = "CollectionsApp/1.0 (personal album tool)"
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_REQUESTS = 1.0  # segundos entre GETs
DELAY_AFTER_429 = 30.0  # backoff si nos rate-limitean
MIN_VALID_IMAGE_BYTES = 5_000  # bytes mínimos para considerar una imagen válida
PNG_MAGIC = b"\x89PNG"
JPEG_MAGIC = b"\xff\xd8\xff"

ADRENALYN_SEED_URL = (
    "https://cartophilic-info-exch.blogspot.com/2026/02/"
    "panini-adrenalyn-xl-fifa-world-cup-2026_0501236099.html"
)
STICKERS_SEED_URL = (
    "https://cartophilic-info-exch.blogspot.com/2026/04/"
    "panini-fifa-world-cup-2026-23-brazil.html"
)

# Términos que descalifican una página aunque su título matchee la keyword:
# son sets paralelos / accesorios / variantes que no nos interesan.
_BLACKLIST_TITLE_TERMS = (
    "limited edition",
    "special box",
    "upgrade",
    "xxl",
    "hologram",
    "multipack",
    "starter pack",
    "official guide",
    "checklist",
    "cosmic",
    "parallel",
)


@dataclass(frozen=True)
class CollectionConfig:
    """Parámetros que cambian por colección (Adrenalyn vs Stickers)."""

    name: str
    collection_id: int
    seed_url: str
    title_keyword: str
    filename_pattern: re.Pattern[str]
    expected_total: int


COLLECTIONS: dict[str, CollectionConfig] = {
    "adrenalyn": CollectionConfig(
        name="adrenalyn",
        collection_id=1,
        seed_url=ADRENALYN_SEED_URL,
        title_keyword="Adrenalyn XL FIFA World Cup 2026",
        # ej: "AXL World Cup 2026 -042.jpg"
        filename_pattern=re.compile(r"AXL.*?-(\d+)\.jpe?g$", re.IGNORECASE),
        expected_total=630,
    ),
    "stickers": CollectionConfig(
        name="stickers",
        collection_id=2,
        seed_url=STICKERS_SEED_URL,
        title_keyword="FIFA World Cup 2026",
        # ej: "FIFA World Cup 2026 - Brazil-001.jpg" / "...-001a.jpg"
        # TODO: refinar tras probar empíricamente con la URL semilla.
        filename_pattern=re.compile(
            r"FIFA World Cup 2026[^/]*?-(\d{1,3})[a-z]*\.jpe?g$",
            re.IGNORECASE,
        ),
        expected_total=980,
    ),
}


@dataclass(frozen=True)
class CardImage:
    """Una imagen de card descubierta en una página del blog."""

    card_number: int
    url: str  # URL en alta resolución (s1600)
    original_url: str  # URL como vino del HTML
    source_page: str  # URL del post donde se encontró


@dataclass
class ScrapeResult:
    """Resumen del run del scraper."""

    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    pages_visited: int = 0
    missing_numbers: list[int] = field(default_factory=list)


class PaniniScraper:
    """Crawler que recorre posts del blog y descarga las cards de una colección."""

    def __init__(
        self,
        config: CollectionConfig,
        output_dir: Path,
        force: bool = False,
        on_log: Callable[[str], None] | None = None,
        max_pages: int = 100,
    ) -> None:
        self._config = config
        self._output_dir = output_dir
        self._force = force
        self._log = on_log or (lambda _m: None)
        self._max_pages = max_pages
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT
        self._visited_pages: set[str] = set()
        self._downloaded_numbers: set[int] = set()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def run(self) -> ScrapeResult:
        """Crawl iterativo: arranca en `seed_url`, sigue Older/Newer Post.

        Termina cuando se queda sin URLs nuevas o llega a `max_pages`.
        """
        result = ScrapeResult()
        queue: list[str] = [self._config.seed_url]

        while queue and result.pages_visited < self._max_pages:
            url = queue.pop(0)
            if url in self._visited_pages:
                continue
            self._visited_pages.add(url)
            result.pages_visited += 1

            self._info("Visitando página %d: %s", result.pages_visited, url)
            html = self._fetch_html(url)
            if html is None:
                continue

            soup = BeautifulSoup(html, "html.parser")
            if not self._is_relevant_page(soup, url):
                self._info("Página descartada (no relevante): %s", url)
                queue.extend(self._find_next_pages(soup, url))
                continue

            title = self._page_title(soup) or "(sin título)"
            self._info("Página relevante: %s", title)

            cards = self._extract_card_images(soup, url)
            self._info("Encontradas %d cards en esta página", len(cards))

            for card in cards:
                outcome = self._download_card(card)
                if outcome == "downloaded":
                    result.downloaded += 1
                    self._downloaded_numbers.add(card.card_number)
                elif outcome == "skipped":
                    result.skipped += 1
                    self._downloaded_numbers.add(card.card_number)
                else:
                    result.failed += 1

            queue.extend(self._find_next_pages(soup, url))

        expected = set(range(1, self._config.expected_total + 1))
        result.missing_numbers = sorted(expected - self._downloaded_numbers)
        return result

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> str | None:
        """GET con retry en 429. Devuelve el HTML o None si no se pudo."""
        for attempt in (1, 2):
            try:
                r = self._session.get(url, timeout=REQUEST_TIMEOUT)
            except requests.RequestException as exc:
                logger.warning("[scraper] excepción al pedir %s: %s", url, exc)
                return None

            if r.status_code == 429:
                if attempt == 1:
                    self._info("HTTP 429 — esperando %.0fs y reintentando", DELAY_AFTER_429)
                    time.sleep(DELAY_AFTER_429)
                    continue
                self._info("HTTP 429 persistente para %s — abortando", url)
                return None

            if r.status_code != 200:
                self._info("HTTP %s para %s", r.status_code, url)
                return None

            time.sleep(DELAY_BETWEEN_REQUESTS)
            return str(r.text)

        return None

    # ------------------------------------------------------------------
    # Parseo de páginas
    # ------------------------------------------------------------------

    @staticmethod
    def _page_title(soup: BeautifulSoup) -> str | None:
        node = soup.find("title")
        return node.get_text(strip=True) if node else None

    def _is_relevant_page(self, soup: BeautifulSoup, _url: str) -> bool:
        """True si el `<title>` contiene la keyword y NO matchea blacklist."""
        title = (self._page_title(soup) or "").strip()
        if not title:
            return False
        if self._config.title_keyword.lower() not in title.lower():
            return False
        lower = title.lower()
        return not any(term in lower for term in _BLACKLIST_TITLE_TERMS)

    def _extract_card_images(self, soup: BeautifulSoup, source_url: str) -> list[CardImage]:
        """Extrae cards del post.

        Estrategia:
        - Solo busca dentro del `div.post-body` cuando existe (evita el
          sidebar "Popular Posts" del blog que tiene thumbnails que
          también matchean por accidente).
        - Itera `<a href="…blogger.googleusercontent.com…">` cuya URL,
          tras URL-decode, matchee `filename_pattern`.
        - Upgrade de resolución reemplazando `/sNNN/` por `/s1600/`.
        - Deduplica por `card_number` (la primera aparición gana).
        """
        scope: BeautifulSoup | Tag = soup
        post_body = soup.find("div", class_="post-body")
        if isinstance(post_body, Tag):
            scope = post_body

        seen: set[int] = set()
        cards: list[CardImage] = []
        for link in scope.find_all("a", href=True):
            if not isinstance(link, Tag):
                continue
            href = link.get("href", "")
            if not isinstance(href, str):
                continue
            if "blogger.googleusercontent.com" not in href:
                continue
            decoded = unquote(href)
            match = self._config.filename_pattern.search(decoded)
            if not match:
                continue
            try:
                number = int(match.group(1))
            except (ValueError, IndexError):
                continue
            if number in seen:
                continue
            seen.add(number)
            cards.append(
                CardImage(
                    card_number=number,
                    url=re.sub(r"/s\d+/", "/s1600/", href),
                    original_url=href,
                    source_page=source_url,
                )
            )
        return cards

    def _find_next_pages(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Links a otras páginas relevantes: Older/Newer Post + Blog Archive."""
        candidates: list[str] = []

        for css_class in ("blog-pager-older-link", "blog-pager-newer-link"):
            for node in soup.find_all("a", class_=css_class, href=True):
                if isinstance(node, Tag):
                    href = node.get("href")
                    if isinstance(href, str):
                        candidates.append(href)

        # Sidebar "Blog Archive": links cuyo title o texto matchee la keyword.
        keyword_lower = self._config.title_keyword.lower()
        for node in soup.find_all("a", href=True):
            if not isinstance(node, Tag):
                continue
            href = node.get("href")
            if not isinstance(href, str) or not href:
                continue
            label = str(node.get("title") or node.get_text(strip=True) or "").lower()
            if keyword_lower in label:
                candidates.append(href)

        # Normalizar a URL absoluta y dedupe contra ya-visitadas.
        absolute: list[str] = []
        seen_local: set[str] = set()
        for href in candidates:
            full = urljoin(current_url or BLOG_BASE_URL, href)
            if full in self._visited_pages or full in seen_local:
                continue
            seen_local.add(full)
            absolute.append(full)
        return absolute

    # ------------------------------------------------------------------
    # Descarga
    # ------------------------------------------------------------------

    def _download_card(self, card: CardImage) -> str:
        """Descarga `card`. Retorna `'downloaded'` | `'skipped'` | `'failed'`."""
        dest = self._output_dir / format_card_filename(card.card_number, "jpg")

        if dest.exists() and not self._force:
            self._info("Card %04d → ya existe, skip", card.card_number)
            return "skipped"

        try:
            r = self._session.get(card.url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            self._info("Card %04d → falló: %s", card.card_number, exc)
            return "failed"

        if r.status_code != 200:
            self._info("Card %04d → falló: HTTP %s", card.card_number, r.status_code)
            return "failed"

        content = r.content
        if len(content) < MIN_VALID_IMAGE_BYTES:
            self._info(
                "Card %04d → falló: %d bytes (esperaba > %d)",
                card.card_number,
                len(content),
                MIN_VALID_IMAGE_BYTES,
            )
            return "failed"

        if not (content.startswith(JPEG_MAGIC) or content.startswith(PNG_MAGIC)):
            self._info("Card %04d → falló: contenido no parece JPEG/PNG", card.card_number)
            return "failed"

        dest.write_bytes(content)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        self._info("Card %04d → descargada (%d KB)", card.card_number, len(content) // 1024)
        return "downloaded"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _info(self, fmt: str, *args: object) -> None:
        """Loguea via `logging` y propaga al callback `on_log`."""
        message = fmt % args if args else fmt
        logger.info("[scraper] %s", message)
        self._log(f"[scraper] {message}")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Descarga cards de Panini desde cartophilic-info-exch.blogspot.com"),
    )
    parser.add_argument("--collection", required=True, choices=list(COLLECTIONS))
    parser.add_argument(
        "--collection-id",
        type=int,
        default=None,
        help="Override del collection_id (carpeta de salida)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-descargar aunque el archivo destino ya exista",
    )
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument(
        "--seed-url",
        default=None,
        help="Override de la URL semilla (útil para arrancar desde otro post)",
    )
    args = parser.parse_args(argv)

    config = COLLECTIONS[args.collection]
    if args.collection_id is not None:
        config = replace(config, collection_id=args.collection_id)
    if args.seed_url:
        config = replace(config, seed_url=args.seed_url)

    output_dir = get_generated_cards_dir() / str(config.collection_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output: {output_dir}")
    print(f"Seed:   {config.seed_url}")
    print(f"Force:  {args.force}")
    print()

    scraper = PaniniScraper(
        config=config,
        output_dir=output_dir,
        force=args.force,
        max_pages=args.max_pages,
        on_log=print,
    )
    result = scraper.run()

    print()
    print("=== Resumen ===")
    print(f"Páginas visitadas:  {result.pages_visited}")
    print(f"Cards descargadas:  {result.downloaded}")
    print(f"Cards omitidas:     {result.skipped}")
    print(f"Fallos:             {result.failed}")
    if result.missing_numbers:
        preview = result.missing_numbers[:20]
        tail = "..." if len(result.missing_numbers) > 20 else ""
        print(f"Cards faltantes ({len(result.missing_numbers)}): {preview}{tail}")
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
