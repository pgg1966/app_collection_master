"""Tests del scraper de Panini.

Mockean requests con `responses` para no tocar la red. Cubren:
- Parseo de HTML de Blogger (`_extract_card_images`).
- Filtros de relevancia (`_is_relevant_page`).
- Validación defensiva en `_download_card` (size + magic bytes).
- Loop de `run()` (rate-limit, dedupe, max_pages, missing_numbers).
- CLI `main()` (creación de output dir).
"""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
import responses
from bs4 import BeautifulSoup

from collections_app.admin.tools import panini_scraper
from collections_app.admin.tools.panini_scraper import (
    COLLECTIONS,
    DELAY_AFTER_429,
    JPEG_MAGIC,
    CardImage,
    PaniniScraper,
    ScrapeResult,
    main,
)

ADRENALYN = COLLECTIONS["adrenalyn"]


# ----------------------------------------------------------------------
# Fixtures HTML
# ----------------------------------------------------------------------


def _post_body(inner_html: str, title: str = "Adrenalyn XL FIFA World Cup 2026 (09)") -> str:
    """Envuelve `inner_html` en una página estilo Blogger."""
    return f"""
    <html><head><title>{title}</title></head><body>
      <div class="post-body">
        {inner_html}
      </div>
      <a class="blog-pager-older-link" href="/2026/02/older.html">Older Post</a>
      <a class="blog-pager-newer-link" href="/2026/02/newer.html">Newer Post</a>
    </body></html>
    """


def _make_scraper(tmp_path: Path) -> PaniniScraper:
    return PaniniScraper(config=ADRENALYN, output_dir=tmp_path, force=False)


def _valid_jpeg(size_kb: int = 10) -> bytes:
    return JPEG_MAGIC + b"\x00" * (size_kb * 1024)


# ----------------------------------------------------------------------
# _extract_card_images
# ----------------------------------------------------------------------


def test_extract_card_images_parses_blogger_html(tmp_path):
    inner = "".join(
        f'<a href="https://blogger.googleusercontent.com/img/abc/s620/'
        f'AXL%20World%20Cup%202026%20-{n:03d}.jpg">link</a>'
        for n in (1, 2, 3, 10, 42)
    )
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    scraper = _make_scraper(tmp_path)

    cards = scraper._extract_card_images(soup, "https://example.com/post.html")

    numbers = sorted(c.card_number for c in cards)
    assert numbers == [1, 2, 3, 10, 42]
    assert all(c.source_page == "https://example.com/post.html" for c in cards)


def test_extract_card_images_upgrades_to_s1600(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-010.jpg">x</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert len(cards) == 1
    assert "/s1600/" in cards[0].url
    assert "/s620/" not in cards[0].url
    assert cards[0].original_url.endswith("/s620/AXL-010.jpg")


def test_extract_card_images_dedupes_by_number(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-007.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/zzz/s403/AXL-007.jpg">y</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert len(cards) == 1
    assert cards[0].card_number == 7
    # Quedó la primera aparición
    assert "/img/abc/" in cards[0].original_url


def test_extract_card_images_ignores_non_blogger_urls(tmp_path):
    inner = """
    <a href="https://example.com/AXL-001.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-002.jpg">ok</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [2]


def test_extract_card_images_ignores_unrelated_filenames(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/random-photo.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-005.jpg">ok</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [5]


def test_extract_card_images_url_decodes_filename(tmp_path):
    """Blogger sirve URLs URL-encoded; el regex aplica sobre el unquote."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL%20World%20Cup%20-099.jpg">x</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [99]


def test_extract_card_images_only_searches_post_body(tmp_path):
    """No tocar el sidebar 'Popular Posts' que también tiene <img>."""
    html = """
    <html><head><title>Adrenalyn XL FIFA World Cup 2026</title></head><body>
      <div class="popular-posts">
        <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-666.jpg">sidebar</a>
      </div>
      <div class="post-body">
        <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-001.jpg">x</a>
      </div>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [1]


# ----------------------------------------------------------------------
# _is_relevant_page
# ----------------------------------------------------------------------


def test_is_relevant_page_accepts_card_pages(tmp_path):
    soup = BeautifulSoup(
        "<html><head><title>Adrenalyn XL FIFA World Cup 2026 (09) - 010-045</title></head></html>",
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is True


def _title_html(title: str) -> str:
    return f"<html><head><title>{title}</title></head></html>"


def test_is_relevant_page_rejects_limited_edition(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 - Limited Edition"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_checklist(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 (07) - Checklist"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_official_guide(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 - Official Guide"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_non_collection_post(tmp_path):
    soup = BeautifulSoup(
        "<html><head><title>Cards from Euro 2024</title></head></html>",
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_empty_title(tmp_path):
    soup = BeautifulSoup("<html></html>", "html.parser")
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


# ----------------------------------------------------------------------
# _download_card
# ----------------------------------------------------------------------


def _card(n: int = 42, url: str = "https://example.com/img.jpg") -> CardImage:
    return CardImage(card_number=n, url=url, original_url=url, source_page="src")


def test_download_card_skips_existing_unless_force(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    existing = tmp_path / "0042.jpg"
    existing.write_bytes(b"old")

    scraper = _make_scraper(tmp_path)
    with responses.RequestsMock():  # ningún request debe ocurrir
        outcome = scraper._download_card(_card(42))
    assert outcome == "skipped"
    assert existing.read_bytes() == b"old"

    # Con force=True, sí se baja y reescribe.
    forced = PaniniScraper(config=ADRENALYN, output_dir=tmp_path, force=True)
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, "https://example.com/img.jpg", body=_valid_jpeg(20), status=200)
        outcome = forced._download_card(_card(42))
    assert outcome == "downloaded"
    assert existing.read_bytes().startswith(JPEG_MAGIC)


def test_download_card_validates_content_size(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/tiny.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=b"\xff\xd8\xff" + b"x" * 100, status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(1, url))
    assert outcome == "failed"
    assert not (tmp_path / "0001.jpg").exists()


def test_download_card_validates_magic_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/fake.jpg"
    body = b"<html>" + b"x" * 6000 + b"</html>"  # > MIN_VALID_IMAGE_BYTES, magic incorrecto
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=body, status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(1, url))
    assert outcome == "failed"
    assert not (tmp_path / "0001.jpg").exists()


def test_download_card_writes_valid_jpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/ok.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=_valid_jpeg(15), status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(7, url))
    assert outcome == "downloaded"
    saved = tmp_path / "0007.jpg"
    assert saved.exists()
    assert saved.read_bytes().startswith(JPEG_MAGIC)


def test_download_card_handles_http_error(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/missing.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=404)
        outcome = _make_scraper(tmp_path)._download_card(_card(13, url))
    assert outcome == "failed"


# ----------------------------------------------------------------------
# _fetch_html / 429
# ----------------------------------------------------------------------


def test_fetch_html_handles_http_429_with_backoff(tmp_path, monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda s: sleeps.append(s))

    url = "https://example.com/post"
    scraper = _make_scraper(tmp_path)
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=429)
        rsps.add(responses.GET, url, body="<html><title>OK</title></html>", status=200)
        html = scraper._fetch_html(url)

    assert html is not None
    assert "<title>OK</title>" in html
    assert DELAY_AFTER_429 in sleeps  # se respetó el backoff


def test_fetch_html_returns_none_on_persistent_429(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/post"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=429)
        rsps.add(responses.GET, url, status=429)
        html = _make_scraper(tmp_path)._fetch_html(url)
    assert html is None


def test_fetch_html_returns_none_on_non_200(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/missing"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=404)
        assert _make_scraper(tmp_path)._fetch_html(url) is None


# ----------------------------------------------------------------------
# _find_next_pages
# ----------------------------------------------------------------------


def test_find_next_pages_returns_older_and_newer_links(tmp_path):
    soup = BeautifulSoup(_post_body("", "Adrenalyn XL FIFA World Cup 2026"), "html.parser")
    pages = _make_scraper(tmp_path)._find_next_pages(soup, "https://x.com/cur")
    # Older + Newer (urljoineados) están en la lista
    assert any(p.endswith("/2026/02/older.html") for p in pages)
    assert any(p.endswith("/2026/02/newer.html") for p in pages)


def test_find_next_pages_excludes_already_visited(tmp_path):
    soup = BeautifulSoup(_post_body(""), "html.parser")
    scraper = _make_scraper(tmp_path)
    older = "https://cartophilic-info-exch.blogspot.com/2026/02/older.html"
    scraper._visited_pages.add(older)
    pages = scraper._find_next_pages(soup, "https://cartophilic-info-exch.blogspot.com/cur")
    assert older not in pages


# ----------------------------------------------------------------------
# run()
# ----------------------------------------------------------------------


def test_run_respects_max_pages(tmp_path, monkeypatch):
    """Cada página linkea a una página nueva; el loop se corta en max_pages."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    page_idx = {"n": 0}

    def fake_fetch(_url: str) -> str:
        page_idx["n"] += 1
        next_n = page_idx["n"] + 1
        # Cada página linkea a la próxima
        return _post_body(
            f"""
            <a href="https://blogger.googleusercontent.com/img/x/s620/AXL-{page_idx['n']:03d}.jpg">x</a>
            """,
        ).replace(
            "/2026/02/older.html",
            f"https://cartophilic-info-exch.blogspot.com/2026/02/page-{next_n}.html",
        )

    scraper = PaniniScraper(config=ADRENALYN, output_dir=tmp_path, max_pages=5)
    with (
        patch.object(scraper, "_fetch_html", side_effect=fake_fetch),
        patch.object(scraper, "_download_card", return_value="downloaded"),
    ):
        result = scraper.run()

    assert result.pages_visited == 5


def test_run_dedupes_visited_pages(tmp_path, monkeypatch):
    """A linkea B y B linkea A: cada URL se procesa una sola vez."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    base = "https://cartophilic-info-exch.blogspot.com"
    seed = f"{base}/A.html"
    fetched: list[str] = []

    def fake_fetch(url: str) -> str:
        fetched.append(url)
        if url.endswith("A.html"):
            return (
                _post_body("")
                .replace("/2026/02/older.html", f"{base}/B.html")
                .replace("/2026/02/newer.html", f"{base}/B.html")
            )
        return (
            _post_body("")
            .replace("/2026/02/older.html", f"{base}/A.html")
            .replace("/2026/02/newer.html", f"{base}/A.html")
        )

    scraper = PaniniScraper(
        config=replace(ADRENALYN, seed_url=seed),
        output_dir=tmp_path,
        max_pages=20,
    )
    with patch.object(scraper, "_fetch_html", side_effect=fake_fetch):
        result = scraper.run()

    assert result.pages_visited == 2  # A y B, no más
    assert fetched == [f"{base}/A.html", f"{base}/B.html"]


def test_run_reports_missing_numbers(tmp_path, monkeypatch):
    """Si solo se descargan algunas cards, missing_numbers lista el resto."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    inner = "".join(
        f'<a href="https://blogger.googleusercontent.com/img/x/s620/AXL-{n:03d}.jpg">x</a>'
        for n in (1, 2, 5)
    )
    config_small = replace(ADRENALYN, expected_total=10)
    scraper = PaniniScraper(config=config_small, output_dir=tmp_path, max_pages=1)

    with (
        patch.object(scraper, "_fetch_html", return_value=_post_body(inner)),
        patch.object(scraper, "_download_card", return_value="downloaded"),
    ):
        result = scraper.run()

    assert result.downloaded == 3
    assert result.missing_numbers == [3, 4, 6, 7, 8, 9, 10]


def test_run_skips_pages_marked_as_irrelevant(tmp_path, monkeypatch):
    """Una página que no matchea title_keyword no se procesa para cards."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    irrelevant_html = "<html><head><title>Some other album</title></head><body></body></html>"
    scraper = _make_scraper(tmp_path)
    with (
        patch.object(scraper, "_fetch_html", return_value=irrelevant_html),
        patch.object(scraper, "_download_card") as mock_dl,
    ):
        scraper.run()
    mock_dl.assert_not_called()


# ----------------------------------------------------------------------
# CLI main()
# ----------------------------------------------------------------------


def test_main_creates_output_dir(tmp_path, monkeypatch):
    """El CLI crea la carpeta {generated_cards}/{collection_id}/ antes de correr."""
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )

    captured: dict = {}

    class _StubScraper:
        def __init__(self, **kwargs):
            captured["output_dir"] = kwargs["output_dir"]

        def run(self):
            return ScrapeResult()

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)

    rc = main(["--collection", "adrenalyn"])

    assert rc == 0
    expected = tmp_path / str(ADRENALYN.collection_id)
    assert expected.exists()
    assert captured["output_dir"] == expected


def test_main_returns_nonzero_when_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )

    class _StubScraper:
        def __init__(self, **_kwargs):
            pass

        def run(self):
            return ScrapeResult(downloaded=1, failed=2)

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)

    rc = main(["--collection", "adrenalyn"])
    assert rc == 1


def test_main_collection_id_override_uses_custom_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )
    captured: dict = {}

    class _StubScraper:
        def __init__(self, **kwargs):
            captured["output_dir"] = kwargs["output_dir"]

        def run(self):
            return ScrapeResult()

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)
    main(["--collection", "adrenalyn", "--collection-id", "99"])
    assert captured["output_dir"] == tmp_path / "99"


# ----------------------------------------------------------------------
# Sanity
# ----------------------------------------------------------------------


@pytest.mark.parametrize("name", ["adrenalyn", "stickers"])
def test_collections_config_complete(name):
    """COLLECTIONS tiene los dos sets esperados con campos válidos."""
    cfg = COLLECTIONS[name]
    assert cfg.name == name
    assert cfg.collection_id > 0
    assert cfg.seed_url.startswith("https://cartophilic-info-exch.blogspot.com")
    assert cfg.title_keyword
    assert cfg.expected_total > 0
    assert cfg.filename_pattern.pattern  # regex no vacía
