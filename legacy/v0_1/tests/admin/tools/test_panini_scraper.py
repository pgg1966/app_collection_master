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
    _compress_ranges,
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


# ----------------------------------------------------------------------
# Stickers — regex y blacklist (PASO 1)
# ----------------------------------------------------------------------


STICKERS = COLLECTIONS["stickers"]


def test_collections_stickers_config_is_id_3():
    """La colección stickers debe usar collection_id=3 y el seed correcto."""
    assert STICKERS.collection_id == 3
    assert STICKERS.expected_total == 980
    assert STICKERS.seed_url.startswith("https://cartophilic-info-exch.blogspot.com")
    # Seed actualizado al post de Checklist (mexusacan)
    assert "mexusacan" in STICKERS.seed_url


def test_stickers_pattern_matches_basic_filename():
    """El regex matchea filenames de stickers individuales."""
    pat = STICKERS.filename_pattern
    cases = {
        "2026 Panini - FIFA World Cup 2026 -001aa.jpg": 1,
        "2026 Panini - FIFA World Cup 2026 -042b.jpg": 42,
        "2026 Panini - FIFA World Cup 2026 -301a.jpg": 301,
        "2026 Panini - FIFA World Cup 2026 -980abc.jpg": 980,
    }
    for filename, expected in cases.items():
        m = pat.search(filename)
        assert m is not None, f"Esperaba match para {filename!r}"
        assert int(m.group(1)) == expected


def test_stickers_pattern_rejects_country_filenames():
    """El regex NO matchea filenames con código de país en lugar de número."""
    pat = STICKERS.filename_pattern
    rejected = (
        "2026 Panini - FIFA World Cup 2026 -USA1bbb.jpg",
        "2026 Panini - FIFA World Cup 2026 - Brazil2cc.jpg",
        "2026 Panini - FIFA World Cup - Brazil2cc.jpg",  # falta "2026"
    )
    for filename in rejected:
        assert pat.search(filename) is None, f"NO debería matchear {filename!r}"


def test_stickers_pattern_rejects_variants():
    """El regex NO matchea variantes patrocinadas / Play-Offs / Free Digital."""
    pat = STICKERS.filename_pattern
    rejected = (
        # Hay tokens entre "2026" y "-001a" (Coca-Cola, Play-Offs, etc.)
        "2026 Panini - FIFA World Cup 2026 - Coca-Cola -001a.jpg",
        "2026 Panini - FIFA World Cup 2026 - Play-Offs - 001a.jpg",
        "2026 Panini - FIFA World Cup 2026 - Free Digital Pack -001aa.jpg",
        "2026 Panini - FIFA World Cup 2026 - McDoanlds - Mexico2.jpg",
    )
    for filename in rejected:
        assert pat.search(filename) is None, f"NO debería matchear {filename!r}"


def _stickers_scraper(tmp_path: Path) -> PaniniScraper:
    return PaniniScraper(config=STICKERS, output_dir=tmp_path)


def _stickers_post(inner_html: str, title: str = "FIFA World Cup 2026 (07)") -> str:
    return f"""
    <html><head><title>{title}</title></head><body>
      <div class="post-body">{inner_html}</div>
      <a class="blog-pager-older-link" href="/2026/03/older.html">Older</a>
      <a class="blog-pager-newer-link" href="/2026/03/newer.html">Newer</a>
    </body></html>
    """


def test_blacklist_filters_country_grupal_sheets(tmp_path):
    """URL con ' - germany - ' es hoja grupal — descartar aunque tenga regex válido."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 - Germany - Album1a.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 -005aa.jpg">ok</a>
    """  # noqa: E501
    soup = BeautifulSoup(_stickers_post(inner), "html.parser")
    cards = _stickers_scraper(tmp_path)._extract_card_images(soup, "src")
    numbers = [c.card_number for c in cards]
    assert numbers == [5]  # solo el individual válido


def test_blacklist_filters_coca_cola(tmp_path):
    """URL con 'coca-cola' se descarta vía FILENAME_BLACKLIST_TOKENS."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini FIFA WC 2026 Coca-Cola -001a.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 -042a.jpg">ok</a>
    """  # noqa: E501
    soup = BeautifulSoup(_stickers_post(inner), "html.parser")
    cards = _stickers_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [42]


def test_seed_page_not_relevant_but_provides_links(tmp_path, monkeypatch):
    """Página seed (Checklist) no se scrapea para cards pero sí para links."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    title = "Panini FIFA World Cup 2026 - Checklist"
    inner = (
        '<a href="https://blogger.googleusercontent.com/img/x/s620/'
        "2026 Panini - FIFA World Cup 2026 -010aa.jpg"
        '">x</a>'
    )
    html = _stickers_post(inner, title=title)
    scraper = _stickers_scraper(tmp_path)
    soup = BeautifulSoup(html, "html.parser")

    # 1) La página NO se considera relevante (matchea blacklist 'checklist')
    assert scraper._is_relevant_page(soup, "u") is False

    # 2) Pero `_find_next_pages` SÍ devuelve links (Older/Newer Post)
    links = scraper._find_next_pages(soup, "https://cartophilic-info-exch.blogspot.com/cur")
    assert any(link.endswith("/2026/03/older.html") for link in links)
    assert any(link.endswith("/2026/03/newer.html") for link in links)

    # 3) El loop de run() también: visitamos la seed y NO bajamos cards
    #    (las descarta por título), pero el link aporta páginas a la queue.
    with (
        patch.object(scraper, "_fetch_html", return_value=html),
        patch.object(scraper, "_download_card") as mock_dl,
    ):
        # Restringimos a 1 página para acotar el test (la primera es la seed)
        scraper._max_pages = 1
        result = scraper.run()
    mock_dl.assert_not_called()
    assert result.pages_visited == 1


def test_run_skips_already_downloaded_numbers(tmp_path, monkeypatch):
    """Misma card en 3 páginas: solo la primera baja, las demás 'skipped'."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    page_idx = {"n": 0}
    base = "https://cartophilic-info-exch.blogspot.com"

    def fake_fetch(_url: str) -> str:
        page_idx["n"] += 1
        # Cada página linkea a la siguiente y contiene la misma card 042
        next_n = page_idx["n"] + 1
        inner = (
            '<a href="https://blogger.googleusercontent.com/img/x/s620/'
            "2026 Panini - FIFA World Cup 2026 -042aa.jpg"
            '">x</a>'
        )
        return (
            _stickers_post(inner)
            .replace("/2026/03/older.html", f"{base}/p{next_n}.html")
            .replace("/2026/03/newer.html", f"{base}/p{next_n}.html")
        )

    scraper = PaniniScraper(config=STICKERS, output_dir=tmp_path, max_pages=3)
    download_calls: list[int] = []

    def fake_download(card: CardImage) -> str:
        download_calls.append(card.card_number)
        # La primera retorna 'downloaded'; las siguientes el dedupe del run
        # (en _download_card real) las marca skipped sin entrar acá.
        # Pero como acá mockeamos _download_card completamente, contamos
        # cuántas veces lo llama el loop principal.
        return "downloaded"

    with (
        patch.object(scraper, "_fetch_html", side_effect=fake_fetch),
        patch.object(scraper, "_download_card", side_effect=fake_download),
    ):
        result = scraper.run()

    # _download_card se invoca para cada aparición de la card en cada página.
    # El dedupe real vive DENTRO de _download_card (chequea
    # _downloaded_numbers); ese path se ejercita en su propio test abajo.
    assert len(download_calls) == 3
    # Pero result.downloaded sigue siendo 3 sólo porque mockeamos el outcome.
    assert result.downloaded == 3


def test_download_card_skips_when_already_in_downloaded_numbers(tmp_path, monkeypatch):
    """`_download_card` detecta dedupe vía `_downloaded_numbers` antes del HTTP."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    scraper = _stickers_scraper(tmp_path)
    scraper._downloaded_numbers.add(42)

    card = CardImage(
        card_number=42,
        url="https://example.com/should-not-be-called.jpg",
        original_url="...",
        source_page="src",
    )
    with responses.RequestsMock():  # cero requests permitidos
        outcome = scraper._download_card(card)
    assert outcome == "skipped"


# ----------------------------------------------------------------------
# _compress_ranges
# ----------------------------------------------------------------------


def test_compress_ranges_basic():
    assert _compress_ranges([]) == ""
    assert _compress_ranges([1]) == "001"
    assert _compress_ranges([1, 2, 3]) == "001-003"
    assert _compress_ranges([1, 2, 3, 5, 7, 8, 9]) == "001-003, 005, 007-009"
    assert _compress_ranges([42, 100, 101, 102, 200]) == "042, 100-102, 200"


def test_compress_ranges_padding_at_three_digits():
    """El formato siempre usa 3 dígitos, incluso para números pequeños."""
    assert _compress_ranges([7]) == "007"
    assert _compress_ranges([7, 8, 9]) == "007-009"
