"""Tests del CrestFinder (refactor a Google CSE).

Cubre la cascada cache → SPECIAL → Google CSE → placeholder, las
validaciones defensivas de `_download_and_process_crest`, y los helpers
de detección de formato (`_is_svg`, `_has_image_magic`).
"""

import io
import os
from unittest.mock import patch

import responses
from PIL import Image

from collections_app.admin.crests.crest_finder import (
    ENV_GOOGLE_API_KEY,
    ENV_GOOGLE_CSE_ID,
    GOOGLE_CSE_URL,
    MIN_VALID_FILE_BYTES,
    SETTING_GOOGLE_API_KEY,
    SETTING_GOOGLE_CSE_ID,
    SOURCE_CACHE,
    SOURCE_GOOGLE,
    SOURCE_PLACEHOLDER,
    SPECIAL_CODES,
    CrestFinder,
    _build_crest_queries,
    _load_google_credentials,
    is_valid_crest_file,
)
from collections_app.core.repositories.settings_repo import SettingsRepository


def _png_bytes(w: int = 200, h: int = 200) -> bytes:
    """PNG RGBA con ruido (alta entropía → siempre > MIN_VALID_FILE_BYTES)."""
    img = Image.frombytes("RGBA", (w, h), os.urandom(w * h * 4))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _set_google_keys(conn) -> None:
    """Persiste credenciales de Google CSE en `app_settings`."""
    repo = SettingsRepository(conn)
    repo.set(SETTING_GOOGLE_API_KEY, "test-api-key")
    repo.set(SETTING_GOOGLE_CSE_ID, "test-cse-id")
    conn.commit()


def _redirect_crest_paths(monkeypatch, tmp_path):
    """Hace que get_crests_dir y get_crest_path apunten a tmp_path."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )


# ----------------------------------------------------------------------
# Cache + SPECIAL_CODES + import manual + cosas que no tocan red
# ----------------------------------------------------------------------


def test_uses_cache_if_crest_exists(tmp_path, monkeypatch, memory_db):
    """Si el escudo ya está en disco y es válido, no toca la red."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    cached = tmp_path / "ARG.png"
    cached.write_bytes(_png_bytes())

    finder = CrestFinder()
    with responses.RequestsMock():  # explícito: no se debe llamar a nadie
        result = finder.find_crest("ARG", "ARGENTINA", memory_db)

    assert result.source == SOURCE_CACHE
    assert result.local_path == cached


def test_special_codes_go_to_placeholder(tmp_path, monkeypatch, memory_db):
    """code_id en SPECIAL_CODES → placeholder con iniciales, sin red."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    code_id = next(iter(SPECIAL_CODES))
    with responses.RequestsMock():  # ningún request debe ocurrir
        result = finder.find_crest(code_id, code_id, memory_db)

    assert result.source == SOURCE_PLACEHOLDER
    assert result.local_path.exists()


def test_pan_not_in_special_codes():
    """PAN es selección nacional, no set especial."""
    assert "PAN" not in SPECIAL_CODES


def test_placeholder_generated_with_code_initials(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "XXX.png"
    finder._generate_placeholder_crest("XXX", dest)
    assert dest.exists()
    img = Image.open(dest)
    assert img.mode == "RGBA"
    assert img.size == (200, 200)


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
    assert saved.size[0] <= 200 and saved.size[1] <= 200


def test_find_crest_success_returns_path(tmp_path, monkeypatch, memory_db):
    _redirect_crest_paths(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(_png_bytes())

    finder = CrestFinder()
    with responses.RequestsMock():
        result = finder.find_crest("ARG", "ARGENTINA", memory_db)

    assert result.local_path == tmp_path / "ARG.png"
    assert result.source == SOURCE_CACHE


# ----------------------------------------------------------------------
# Validación defensiva en _download_and_process_crest
# ----------------------------------------------------------------------


def test_download_converts_to_rgba_png(tmp_path, monkeypatch):
    """La imagen descargada se guarda como PNG RGBA."""
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
        rsps.add(
            responses.GET,
            img_url,
            body=html,
            status=200,
            content_type="text/html",
        )
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


def test_save_too_small_is_discarded(tmp_path, monkeypatch):
    """Si img.save produce un PNG < MIN_VALID_FILE_BYTES, se borra y retorna False."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "TIN.png"
    img_url = "https://example.com/tiny-but-valid.png"
    tiny = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
    buf = io.BytesIO()
    tiny.save(buf, format="PNG")
    body = buf.getvalue() + b"\x00" * 600

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            img_url,
            body=body,
            status=200,
            content_type="image/png",
        )
        ok = finder._download_and_process_crest(img_url, dest)

    assert ok is False
    assert not dest.exists()


def test_svg_detected_correctly():
    finder = CrestFinder()
    assert finder._is_svg(b'<?xml version="1.0"?><svg></svg>') is True
    assert finder._is_svg(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>') is True
    assert finder._is_svg(b'  \n  <?xml version="1.0"?><svg></svg>') is True
    assert finder._is_svg(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) is False
    assert finder._is_svg(b"\xff\xd8\xff\xe0" + b"\x00" * 100) is False
    assert finder._is_svg(b"GIF89a" + b"\x00" * 100) is False


def test_has_image_magic():
    finder = CrestFinder()
    assert finder._has_image_magic(b"\x89PNG\r\n\x1a\n") is True
    assert finder._has_image_magic(b"\xff\xd8\xff\xe0") is True
    assert finder._has_image_magic(b"GIF89a") is True
    assert finder._has_image_magic(b"RIFF\x00\x00\x00\x00WEBP") is True
    assert finder._has_image_magic(b"\x00\x00\x01\x00") is True
    assert finder._has_image_magic(b"<html>") is False
    assert finder._has_image_magic(b"<?xml") is False


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
# Google CSE: _build_crest_queries
# ----------------------------------------------------------------------


def test_build_crest_queries_returns_clipart_first():
    """El primer query debe usar imgType='clipart' y el code_name aparecer en todos."""
    queries = _build_crest_queries("Argentina")
    assert len(queries) >= 2
    assert queries[0][1] == "clipart"
    for query, _img_type in queries:
        assert "Argentina" in query


def test_build_crest_queries_titles_uppercase_input():
    """El input MAYÚSCULAS del CSV se convierte a Title-case en las queries."""
    queries = _build_crest_queries("ARGENTINA")
    assert all("Argentina" in q for q, _ in queries)
    assert not any("ARGENTINA" in q for q, _ in queries)


# ----------------------------------------------------------------------
# Google CSE: _search_google_crest
# ----------------------------------------------------------------------


def test_search_google_crest_returns_urls_when_configured(tmp_path, monkeypatch, memory_db):
    """Con keys configuradas y respuesta válida, retorna las URLs del primer match."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _set_google_keys(memory_db)

    finder = CrestFinder()
    cse_response = {
        "items": [
            {"link": "https://example.com/a.png"},
            {"link": "https://example.com/b.png"},
            {"link": "https://example.com/c.png"},
        ]
    }
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, GOOGLE_CSE_URL, json=cse_response, status=200)
        urls = finder._search_google_crest("ARGENTINA", memory_db)

    assert urls == [
        "https://example.com/a.png",
        "https://example.com/b.png",
        "https://example.com/c.png",
    ]


def test_search_google_crest_returns_empty_when_not_configured(tmp_path, monkeypatch, memory_db):
    """Sin api_key/cse_id en settings NI env vars, retorna [] sin hacer requests."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    # NO seteamos las keys en settings; tampoco deben existir como env vars
    monkeypatch.delenv(ENV_GOOGLE_API_KEY, raising=False)
    monkeypatch.delenv(ENV_GOOGLE_CSE_ID, raising=False)

    finder = CrestFinder()
    with responses.RequestsMock():  # ningún request debe ocurrir
        urls = finder._search_google_crest("ARGENTINA", memory_db)

    assert urls == []


# ----------------------------------------------------------------------
# Cascada settings → env vars en _load_google_credentials
# ----------------------------------------------------------------------


def test_load_credentials_uses_settings_when_present(monkeypatch, memory_db):
    """Si las claves están en `app_settings`, esas ganan sobre env vars."""
    _set_google_keys(memory_db)  # setea "from-settings"
    monkeypatch.setenv(ENV_GOOGLE_API_KEY, "from-env")
    monkeypatch.setenv(ENV_GOOGLE_CSE_ID, "from-env")

    api_key, cse_id = _load_google_credentials(memory_db)
    assert api_key == "test-api-key"
    assert cse_id == "test-cse-id"


def test_load_credentials_falls_back_to_env_vars(monkeypatch, memory_db):
    """Sin entradas en settings, lee de env vars."""
    # Sin _set_google_keys(): app_settings vacío
    monkeypatch.setenv(ENV_GOOGLE_API_KEY, "env-api-key")
    monkeypatch.setenv(ENV_GOOGLE_CSE_ID, "env-cse-id")

    api_key, cse_id = _load_google_credentials(memory_db)
    assert api_key == "env-api-key"
    assert cse_id == "env-cse-id"


def test_load_credentials_returns_none_when_neither_present(monkeypatch, memory_db):
    """Sin settings ni env vars, retorna (None, None)."""
    monkeypatch.delenv(ENV_GOOGLE_API_KEY, raising=False)
    monkeypatch.delenv(ENV_GOOGLE_CSE_ID, raising=False)

    api_key, cse_id = _load_google_credentials(memory_db)
    assert api_key is None
    assert cse_id is None


def test_load_credentials_logs_partial_config_warning(monkeypatch, memory_db, caplog):
    """Si solo está api_key (sin cse_id) en settings, debe logear WARNING."""
    SettingsRepository(memory_db).set(SETTING_GOOGLE_API_KEY, "only-api-key")
    memory_db.commit()
    monkeypatch.delenv(ENV_GOOGLE_API_KEY, raising=False)
    monkeypatch.delenv(ENV_GOOGLE_CSE_ID, raising=False)

    with caplog.at_level("WARNING", logger="collections_app.admin.crests.crest_finder"):
        api_key, cse_id = _load_google_credentials(memory_db)

    assert api_key is None  # incompleto → no usable
    assert cse_id is None
    # Debe haber un WARNING que mencione el campo presente y el faltante
    msgs = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any(
        SETTING_GOOGLE_API_KEY in m and SETTING_GOOGLE_CSE_ID in m for m in msgs
    ), f"Esperaba WARNING mencionando ambos campos, vi: {msgs}"


def test_load_credentials_logs_partial_config_warning_inverted(monkeypatch, memory_db, caplog):
    """Caso inverso: solo cse_id presente en settings."""
    SettingsRepository(memory_db).set(SETTING_GOOGLE_CSE_ID, "only-cse-id")
    memory_db.commit()
    monkeypatch.delenv(ENV_GOOGLE_API_KEY, raising=False)
    monkeypatch.delenv(ENV_GOOGLE_CSE_ID, raising=False)

    with caplog.at_level("WARNING", logger="collections_app.admin.crests.crest_finder"):
        _load_google_credentials(memory_db)

    msgs = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any(
        SETTING_GOOGLE_CSE_ID in m and SETTING_GOOGLE_API_KEY in m for m in msgs
    ), f"Esperaba WARNING mencionando ambos campos, vi: {msgs}"


def test_search_google_crest_uses_env_var_fallback(tmp_path, monkeypatch, memory_db):
    """`_search_google_crest` funciona end-to-end leyendo solo de env vars."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    monkeypatch.setenv(ENV_GOOGLE_API_KEY, "env-api-key")
    monkeypatch.setenv(ENV_GOOGLE_CSE_ID, "env-cse-id")

    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            GOOGLE_CSE_URL,
            json={"items": [{"link": "https://example.com/from-env.png"}]},
            status=200,
        )
        urls = finder._search_google_crest("ARGENTINA", memory_db)

    assert urls == ["https://example.com/from-env.png"]


def test_search_google_crest_returns_empty_on_quota_exhausted(tmp_path, monkeypatch, memory_db):
    """HTTP 429 (cuota) → retorna [] sin levantar y sin probar más queries."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _set_google_keys(memory_db)

    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, GOOGLE_CSE_URL, json={}, status=429)
        urls = finder._search_google_crest("ARGENTINA", memory_db)
        # Solo 1 call: detectado quota, no se siguen probando queries.
        # `rsps.calls` se resetea al salir del context, por eso el
        # assert va adentro.
        assert len(rsps.calls) == 1

    assert urls == []


def test_search_google_crest_tries_clipart_first(tmp_path, monkeypatch, memory_db):
    """Cuando el primer query (clipart) está vacío, se cae al siguiente."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _set_google_keys(memory_db)

    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        # Primer call: vacío
        rsps.add(responses.GET, GOOGLE_CSE_URL, json={"items": []}, status=200)
        # Segundo call: con resultados
        rsps.add(
            responses.GET,
            GOOGLE_CSE_URL,
            json={"items": [{"link": "https://example.com/x.png"}]},
            status=200,
        )
        urls = finder._search_google_crest("ARGENTINA", memory_db)
        # `rsps.calls` se vacía al salir del context — verificamos adentro
        first_url = rsps.calls[0].request.url
        assert "imgType=clipart" in first_url

    assert urls == ["https://example.com/x.png"]


# ----------------------------------------------------------------------
# Google CSE: integración via find_crest
# ----------------------------------------------------------------------


def test_find_crest_uses_google_cse(tmp_path, monkeypatch, memory_db):
    """find_crest delega en _search_google_crest y descarga la URL devuelta."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _set_google_keys(memory_db)
    img_url = "https://example.com/arg-crest.png"

    finder = CrestFinder()
    with (
        patch.object(finder, "_search_google_crest", return_value=[img_url]),
        responses.RequestsMock() as rsps,
    ):
        rsps.add(responses.GET, img_url, body=_png_bytes(), status=200)
        result = finder.find_crest("ARG", "ARGENTINA", memory_db)

    assert result.source == SOURCE_GOOGLE
    assert result.success is True
    assert result.local_path.exists()


def test_find_crest_falls_to_placeholder_when_google_returns_nothing(
    tmp_path, monkeypatch, memory_db
):
    """Si Google CSE no devuelve URLs, el resultado es placeholder."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    with patch.object(finder, "_search_google_crest", return_value=[]):
        result = finder.find_crest("ARG", "ARGENTINA", memory_db)

    assert result.source == SOURCE_PLACEHOLDER
    assert result.local_path.exists()
    assert result.local_path.stat().st_size > MIN_VALID_FILE_BYTES


def test_find_crest_falls_to_placeholder_when_all_downloads_fail(tmp_path, monkeypatch, memory_db):
    """Si Google devuelve URLs pero ninguna baja → placeholder."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    bad_urls = ["https://example.com/a.png", "https://example.com/b.png"]
    with (
        patch.object(finder, "_search_google_crest", return_value=bad_urls),
        patch.object(finder, "_download_and_process_crest", return_value=False),
    ):
        result = finder.find_crest("ARG", "ARGENTINA", memory_db)

    assert result.source == SOURCE_PLACEHOLDER


def test_find_crest_skips_google_for_special_codes(tmp_path, monkeypatch, memory_db):
    """Para SPECIAL_CODES, _search_google_crest NO se llama."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    with patch.object(finder, "_search_google_crest") as mock_search:
        result = finder.find_crest("GBL", "Global", memory_db)

    mock_search.assert_not_called()
    assert result.source == SOURCE_PLACEHOLDER


def test_corrupt_cache_is_deleted_and_retried(tmp_path, monkeypatch, memory_db):
    """Un PNG corrupto en cache se borra y se relanza la búsqueda."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _set_google_keys(memory_db)

    corrupt = tmp_path / "URU.png"
    corrupt.write_bytes(b"")  # 0 bytes — corrupto
    img_url = "https://example.com/uru.png"

    finder = CrestFinder()
    with (
        patch.object(finder, "_search_google_crest", return_value=[img_url]),
        responses.RequestsMock() as rsps,
    ):
        rsps.add(responses.GET, img_url, body=_png_bytes(), status=200)
        result = finder.find_crest("URU", "URUGUAY", memory_db)

    assert result.source == SOURCE_GOOGLE
    assert result.local_path.exists()
    assert result.local_path.stat().st_size > MIN_VALID_FILE_BYTES


# ----------------------------------------------------------------------
# find_all_crests
# ----------------------------------------------------------------------


def test_find_all_respects_rate_limiting(tmp_path, monkeypatch, memory_db):
    """find_all_crests espera RATE_LIMIT_DELAY entre requests reales."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    sleep_calls: list[float] = []

    def fake_sleep(s: float) -> None:
        sleep_calls.append(s)

    monkeypatch.setattr("collections_app.admin.crests.crest_finder.time.sleep", fake_sleep)

    finder = CrestFinder()
    # Sin keys configuradas → search Google retorna [] sin red
    finder.find_all_crests(
        [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("FRA", "FRANCE")],
        memory_db,
    )

    # No se duerme antes del primer call de red, sí entre 2do y 3ro
    assert len(sleep_calls) == 2
    assert all(s >= 1.0 for s in sleep_calls)


def test_find_all_does_not_sleep_for_cached_or_special(tmp_path, monkeypatch, memory_db):
    """No se aplica rate-limit para entradas ya cacheadas o SPECIAL."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    # ARG ya cacheado, GBL es SPECIAL
    (tmp_path / "ARG.png").write_bytes(_png_bytes())

    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    finder = CrestFinder()
    finder.find_all_crests([("ARG", "ARGENTINA"), ("GBL", "Global")], memory_db)

    assert sleep_calls == []
