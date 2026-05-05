"""Tests del CrestFinder (Wikimedia Commons backend).

Cubre la cascada cache → SPECIAL → override → Commons search → not_found,
las heurísticas de filtrado y las validaciones defensivas de descarga.
"""

import io
import os
from unittest.mock import patch

import responses
from PIL import Image

from collections_app.admin.crests.crest_finder import (
    COMMONS_API_URL,
    COMMONS_FILE_OVERRIDES,
    COMMONS_USER_AGENT,
    MIN_VALID_FILE_BYTES,
    SOURCE_CACHE,
    SOURCE_COMMONS,
    SOURCE_COMMONS_OVERRIDE,
    SOURCE_NOT_FOUND,
    SOURCE_PLACEHOLDER,
    SPECIAL_CODES,
    CrestFinder,
    is_valid_crest_file,
)


def _png_bytes(w: int = 200, h: int = 200) -> bytes:
    """PNG RGBA con ruido (alta entropía → siempre > MIN_VALID_FILE_BYTES)."""
    img = Image.frombytes("RGBA", (w, h), os.urandom(w * h * 4))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _redirect_crest_paths(monkeypatch, tmp_path):
    """Hace que get_crests_dir y get_crest_path apunten a tmp_path."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )


def _no_query_delay(monkeypatch):
    """Evita el sleep entre queries en tests."""
    monkeypatch.setattr("collections_app.admin.crests.crest_finder.time.sleep", lambda _s: None)


# ----------------------------------------------------------------------
# Cache, SPECIAL_CODES, import manual, helpers básicos
# ----------------------------------------------------------------------


def test_uses_cache_if_crest_exists(tmp_path, monkeypatch):
    """Si el escudo ya está en disco y es válido, no toca la red."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    cached = tmp_path / "ARG.png"
    cached.write_bytes(_png_bytes())

    finder = CrestFinder()
    with responses.RequestsMock():  # explícito: no se debe llamar a nadie
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_CACHE
    assert result.local_path == cached


def test_special_codes_make_placeholder(tmp_path, monkeypatch):
    """code_id en SPECIAL_CODES → placeholder con iniciales, sin red."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    code_id = next(iter(SPECIAL_CODES))
    with responses.RequestsMock():
        result = finder.find_crest(code_id, code_id)

    assert result.source == SOURCE_PLACEHOLDER
    assert result.local_path.exists()


def test_pan_not_in_special_codes():
    assert "PAN" not in SPECIAL_CODES


def test_placeholder_meets_min_valid_file_size(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "PLH.png"
    finder._generate_placeholder_crest("PLH", dest)
    assert dest.stat().st_size > MIN_VALID_FILE_BYTES
    assert is_valid_crest_file(dest) is True


def test_import_manual_crest(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    src = tmp_path / "src.jpg"
    rgb = Image.new("RGB", (300, 300), (0, 0, 255))
    rgb.save(src, format="JPEG")

    finder = CrestFinder()
    result = finder.import_manual_crest("GBL", src)
    assert result.success is True
    saved = Image.open(result.local_path)
    assert saved.mode == "RGBA"


def test_is_valid_crest_file(tmp_path):
    missing = tmp_path / "missing.png"
    too_small = tmp_path / "small.png"
    too_small.write_bytes(b"x" * 100)
    big_enough = tmp_path / "ok.png"
    big_enough.write_bytes(b"x" * (MIN_VALID_FILE_BYTES + 1))

    assert is_valid_crest_file(missing) is False
    assert is_valid_crest_file(too_small) is False
    assert is_valid_crest_file(big_enough) is True


# ----------------------------------------------------------------------
# Validación defensiva en _download_and_process_crest
# ----------------------------------------------------------------------


def test_download_converts_to_rgba_png(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    img_url = "https://example.com/jpg-image.jpg"
    rgb = Image.frombytes("RGB", (200, 200), os.urandom(200 * 200 * 3))
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=buf.getvalue(), status=200)
        ok = finder._download_and_process_crest(img_url, tmp_path / "BRA.png")

    assert ok is True
    saved = Image.open(tmp_path / "BRA.png")
    assert saved.mode == "RGBA"
    assert saved.format == "PNG"


def test_download_rejects_empty_response(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "EMP.png"
    img_url = "https://example.com/empty.png"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"", status=200)
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_download_rejects_html_content(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "HTM.png"
    img_url = "https://example.com/redirected.html"
    html = b"<html><body>" + (b"x" * 1000) + b"</body></html>"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=html, status=200, content_type="text/html")
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_download_rejects_too_small_response(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "SML.png"
    img_url = "https://example.com/tiny.png"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"x" * 200, status=200)
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_svg_detected_correctly():
    finder = CrestFinder()
    assert finder._is_svg(b'<?xml version="1.0"?><svg></svg>') is True
    assert finder._is_svg(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>') is True
    assert finder._is_svg(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) is False
    assert finder._is_svg(b"\xff\xd8\xff\xe0" + b"\x00" * 100) is False


def test_has_image_magic():
    finder = CrestFinder()
    assert finder._has_image_magic(b"\x89PNG\r\n\x1a\n") is True
    assert finder._has_image_magic(b"\xff\xd8\xff\xe0") is True
    assert finder._has_image_magic(b"GIF89a") is True
    assert finder._has_image_magic(b"RIFF\x00\x00\x00\x00WEBP") is True
    assert finder._has_image_magic(b"<html>") is False


# ----------------------------------------------------------------------
# Wikimedia Commons: _search_commons_files
# ----------------------------------------------------------------------


def _commons_search_response(titles: list[str]) -> dict:
    return {"query": {"search": [{"title": t} for t in titles]}}


def test_search_commons_files_returns_titles_on_success():
    titles_returned = [
        "File:Argentina FA logo.svg",
        "File:Brazil federation crest.svg",
        "File:France national football team logo.svg",
    ]
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_search_response(titles_returned),
            status=200,
        )
        titles = finder._search_commons_files("Argentina national football team", limit=5)
        # rsps.calls se vacía al salir del context — verificamos adentro
        assert len(rsps.calls) == 1
        assert rsps.calls[0].request.headers["User-Agent"] == COMMONS_USER_AGENT
        assert "commons.wikimedia.org/w/api.php" in rsps.calls[0].request.url

    assert titles == titles_returned


def test_search_commons_files_returns_empty_on_http_error():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, COMMONS_API_URL, json={}, status=500)
        titles = finder._search_commons_files("Argentina")
    assert titles == []


def test_search_commons_files_filters_out_non_crest_results():
    """La búsqueda devuelve fotos pero el filtro las descarta."""
    raw_titles = [
        "File:Argentina vs Brazil 2022 match.jpg",  # match → descarta
        "File:Argentina FA logo.svg",  # logo → pasa
        "File:Messi celebration.jpg",  # celebration → descarta
    ]
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_search_response(raw_titles),
            status=200,
        )
        titles = finder._search_commons_files("Argentina")
    assert titles == ["File:Argentina FA logo.svg"]


# ----------------------------------------------------------------------
# Wikimedia Commons: _get_commons_thumb_url
# ----------------------------------------------------------------------


def _commons_imageinfo_response(info: dict) -> dict:
    return {"query": {"pages": {"1": {"imageinfo": [info]}}}}


def test_get_commons_thumb_url_prefers_thumburl_over_url():
    """Cuando hay thumburl (PNG), se prefiere sobre url (puede ser SVG)."""
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_imageinfo_response(
                {
                    "thumburl": "https://upload.wikimedia.org/foo-300px.png",
                    "url": "https://upload.wikimedia.org/foo.svg",
                    "mime": "image/svg+xml",
                }
            ),
            status=200,
        )
        url = finder._get_commons_thumb_url("File:Foo.svg")
    assert url == "https://upload.wikimedia.org/foo-300px.png"


def test_get_commons_thumb_url_returns_url_when_not_svg():
    """Sin thumburl, si el original NO es SVG, lo devuelve directo."""
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_imageinfo_response(
                {"url": "https://example.com/foo.png", "mime": "image/png"}
            ),
            status=200,
        )
        url = finder._get_commons_thumb_url("File:Foo.png")
    assert url == "https://example.com/foo.png"


def test_get_commons_thumb_url_returns_none_when_no_imageinfo():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json={"query": {"pages": {"1": {}}}},
            status=200,
        )
        url = finder._get_commons_thumb_url("File:NoExist.svg")
    assert url is None


def test_get_commons_thumb_url_returns_none_on_http_error():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, COMMONS_API_URL, json={}, status=503)
        url = finder._get_commons_thumb_url("File:Foo.svg")
    assert url is None


# ----------------------------------------------------------------------
# Heurística _is_likely_crest_file
# ----------------------------------------------------------------------


def test_is_likely_crest_file_accepts_logo_or_crest():
    f = CrestFinder()
    assert f._is_likely_crest_file("File:Argentina FA logo.svg") is True
    assert f._is_likely_crest_file("File:Brazil_national_football_team_crest.svg") is True
    assert f._is_likely_crest_file("File:Federation logo.png") is True
    assert f._is_likely_crest_file("File:Football association badge.svg") is True


def test_is_likely_crest_file_rejects_match_or_player_photo():
    f = CrestFinder()
    assert f._is_likely_crest_file("File:Argentina vs Brazil 2022 match.jpg") is False
    assert f._is_likely_crest_file("File:Messi celebration logo.jpg") is False
    assert f._is_likely_crest_file("File:Stadium logo.jpg") is False
    assert f._is_likely_crest_file("File:Players training crest.jpg") is False
    assert f._is_likely_crest_file("File:Random photo.jpg") is False  # ni crest


# ----------------------------------------------------------------------
# Cascada de find_crest
# ----------------------------------------------------------------------


def test_find_crest_uses_override_when_present(tmp_path, monkeypatch):
    """Si hay override en COMMONS_FILE_OVERRIDES, se usa sin buscar."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)
    monkeypatch.setitem(COMMONS_FILE_OVERRIDES, "TESTLAND", "File:Testland.svg")

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_get_commons_thumb_url", return_value="https://example.com/x.png"
        ) as mock_url,
        patch.object(finder, "_download_and_process_crest", return_value=True) as mock_dl,
        patch.object(finder, "_search_commons_files") as mock_search,
    ):
        result = finder.find_crest("TST", "TESTLAND")

    mock_url.assert_called_once_with("File:Testland.svg")
    mock_dl.assert_called_once()
    mock_search.assert_not_called()  # NO se buscó porque hubo override
    assert result.source == SOURCE_COMMONS_OVERRIDE
    assert result.success is True


def test_find_crest_falls_back_to_search_when_no_override(tmp_path, monkeypatch):
    """Sin override, se itera sobre la cascada de queries."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_search_commons_files", return_value=["File:Argentina FA logo.svg"]
        ) as mock_search,
        patch.object(finder, "_get_commons_thumb_url", return_value="https://example.com/arg.png"),
        patch.object(finder, "_download_and_process_crest", return_value=True),
    ):
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_COMMONS
    assert result.success is True
    mock_search.assert_called()  # se buscó


def test_find_crest_returns_not_found_when_all_queries_fail(tmp_path, monkeypatch):
    """Cuando todas las queries fallan, NO se escribe archivo (permite reintento)."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with patch.object(finder, "_search_commons_files", return_value=[]):
        result = finder.find_crest("XYZ", "FAKELAND")

    assert result.source == SOURCE_NOT_FOUND
    assert result.success is False
    assert (
        not result.local_path.exists()
    ), "find_crest no debe escribir archivo cuando no hay resultado"


def test_find_crest_returns_not_found_when_all_downloads_fail(tmp_path, monkeypatch):
    """Si Commons devuelve titles pero ninguna descarga sale → NOT_FOUND."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_search_commons_files", return_value=["File:Foo.svg", "File:Bar.svg"]
        ),
        patch.object(finder, "_get_commons_thumb_url", return_value="https://example.com/x.png"),
        patch.object(finder, "_download_and_process_crest", return_value=False),
    ):
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_NOT_FOUND
    assert not result.local_path.exists()


def test_not_found_crest_is_retried_next_time(tmp_path, monkeypatch):
    """Después de NOT_FOUND, la siguiente llamada vuelve a buscar (no devuelve cache)."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    call_count = {"n": 0}

    def fake_search(_q: str, limit: int = 5) -> list[str]:
        del limit
        call_count["n"] += 1
        return []

    with patch.object(finder, "_search_commons_files", side_effect=fake_search):
        first = finder.find_crest("ARG", "ARGENTINA")
        before = call_count["n"]
        second = finder.find_crest("ARG", "ARGENTINA")

    assert first.source == SOURCE_NOT_FOUND
    assert second.source == SOURCE_NOT_FOUND
    # La SEGUNDA llamada efectivamente reintentó búsqueda — no devolvió cache
    assert call_count["n"] > before


def test_find_crest_special_codes_make_placeholder(tmp_path, monkeypatch):
    """SPECIAL_CODES SÍ siguen escribiendo placeholder en disco (recordatorio)."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    result = finder.find_crest("GBL", "Golden Ballers")

    assert result.source == SOURCE_PLACEHOLDER
    assert result.success is True
    assert result.local_path.exists()
    assert result.local_path.stat().st_size > MIN_VALID_FILE_BYTES


def test_find_crest_skips_search_for_special_codes(tmp_path, monkeypatch):
    """Para SPECIAL_CODES, _search_commons_files NO se llama."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    with patch.object(finder, "_search_commons_files") as mock_search:
        finder.find_crest("GBL", "Golden Ballers")

    mock_search.assert_not_called()


def test_user_agent_is_descriptive():
    """El User-Agent debe identificar la app, no ser el genérico de requests."""
    assert "CollectionsApp" in COMMONS_USER_AGENT
    assert "python-requests" not in COMMONS_USER_AGENT.lower()


# ----------------------------------------------------------------------
# cleanup_failed_placeholders
# ----------------------------------------------------------------------


def test_cleanup_failed_placeholders_deletes_non_special(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    arg = tmp_path / "ARG.png"
    gbl = tmp_path / "GBL.png"
    arg.write_bytes(b"placeholder-arg")
    gbl.write_bytes(b"placeholder-gbl")

    finder = CrestFinder()
    deleted = finder.cleanup_failed_placeholders([("ARG", "Argentina"), ("GBL", "Golden Ballers")])

    assert deleted == 1
    assert not arg.exists(), "Placeholder de ARG (no special) debió borrarse"
    assert gbl.exists(), "Placeholder de GBL (special) NO debe borrarse"


def test_cleanup_failed_placeholders_returns_zero_when_no_files(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    deleted = finder.cleanup_failed_placeholders([("ARG", "Argentina"), ("BRA", "Brazil")])
    assert deleted == 0


# ----------------------------------------------------------------------
# find_all_crests
# ----------------------------------------------------------------------


def test_find_all_respects_rate_limiting(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    finder = CrestFinder()
    # Sin red real: _search_commons_files retorna [] sin tocar HTTP.
    with patch.object(finder, "_search_commons_files", return_value=[]):
        finder.find_all_crests([("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("FRA", "FRANCE")])

    # Hubo dos sleeps a 1.0s (rate limit entre find_crest reales). También hubo
    # sleeps a 0.5s entre queries del find_crest (QUERY_DELAY). Verificamos
    # solo los del rate-limit.
    rate_sleeps = [s for s in sleep_calls if s >= 1.0]
    assert len(rate_sleeps) == 2


def test_find_all_does_not_sleep_for_cached_or_special(tmp_path, monkeypatch):
    """No se aplica rate-limit para entradas cacheadas o SPECIAL."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(_png_bytes())

    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    finder = CrestFinder()
    finder.find_all_crests([("ARG", "ARGENTINA"), ("GBL", "Global")])

    # Ningún rate-limit (1.0s) — solo cache hit y SPECIAL. Tampoco hubo
    # query loops para meter delays de 0.5s.
    assert sleep_calls == []
