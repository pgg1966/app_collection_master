"""Tests del PhotoFinder con mocks de internet."""

import io
import os
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import responses
from PIL import Image

from collections_app.admin.image_pipeline.photo_finder import (
    GOOGLE_API_KEY_ENV,
    GOOGLE_CSE_ID_ENV,
    PLACEHOLDER_FILENAME,
    SOURCE_CACHE,
    SOURCE_DUCKDUCKGO,
    SOURCE_GOOGLE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoFinder,
)


def _noisy_array(w: int = 200, h: int = 200, seed: int = 42) -> np.ndarray:
    """Array RGB con suficiente varianza para pasar `_is_good_photo`.

    `_is_good_photo` rechaza imágenes con std < 20 (uniformes) o con
    mean fuera de [30, 225]. El ruido random le mete std ~70 y mean ~127.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)


def _write_fake_jpg(path: Path, w: int = 200, h: int = 200) -> bytes:
    """Crea un JPEG válido (con varianza) en `path` y retorna los bytes."""
    cv2.imwrite(str(path), _noisy_array(w, h))
    return path.read_bytes()


def _fake_image_bytes(w: int = 200, h: int = 200, seed: int = 42) -> bytes:
    """JPEG válido (con varianza) en memoria sin tocar disco."""
    arr = _noisy_array(w, h, seed=seed)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_uses_cache_if_exists(tmp_path):
    """Si el archivo ya existe en el cache del jugador, retorna sin tocar la red."""
    finder = PhotoFinder(tmp_path)
    cached = finder.cached_photo_path("Lionel Messi", "ARG")
    _write_fake_jpg(cached)

    with patch.object(finder, "_search_duckduckgo") as ddg_mock:
        result = finder.find_photo("Lionel Messi", "Argentina", "ARG")
    assert result.source == SOURCE_CACHE
    assert result.local_path == cached
    ddg_mock.assert_not_called()


def test_duckduckgo_primary_source(tmp_path):
    """Si DDG devuelve URLs, la descarga es OK y la imagen tiene cara, usa esa fuente."""
    finder = PhotoFinder(tmp_path)
    fake_url = "https://example.com/messi.jpg"
    img_bytes = _fake_image_bytes()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, fake_url, body=img_bytes, status=200)
        with (
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_search_duckduckgo", return_value=[fake_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG")
    assert result.source == SOURCE_DUCKDUCKGO
    assert result.success is True
    assert result.local_path.exists()


def test_wikipedia_used_when_returns_url(tmp_path):
    finder = PhotoFinder(tmp_path)
    wiki_url = "https://upload.wikimedia.org/foo.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[]),
            patch.object(finder, "_search_wikipedia", return_value=wiki_url),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG")
    assert result.source == SOURCE_WIKIPEDIA
    assert result.local_path.exists()


def test_placeholder_when_all_fail(tmp_path):
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("Unknown Player", "Atlantis", "XYZ")
    assert result.source == SOURCE_PLACEHOLDER
    assert result.success is True
    assert result.local_path.exists()
    assert result.local_path.name == PLACEHOLDER_FILENAME


def test_download_validates_minimum_image_size(tmp_path):
    """Una imagen muy chica (50x50) se rechaza y dispara el siguiente fallback."""
    finder = PhotoFinder(tmp_path)
    tiny_url = "https://example.com/tiny.jpg"
    big_url = "https://example.com/big.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, tiny_url, body=_fake_image_bytes(50, 50), status=200)
        rsps.add(responses.GET, big_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_search_duckduckgo", return_value=[tiny_url, big_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_DUCKDUCKGO
    img = cv2.imread(str(result.local_path))
    assert img.shape[0] >= 100


def test_invalid_image_triggers_fallback(tmp_path):
    """URL devuelve bytes que no son una imagen → debe descartarla."""
    finder = PhotoFinder(tmp_path)
    bad_url = "https://example.com/notimage.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, bad_url, body=b"not an image", status=200)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[bad_url]),
            patch.object(finder, "_search_wikipedia", return_value=None),
        ):
            result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_PLACEHOLDER


def test_cache_key_uses_player_and_country(tmp_path):
    """El nombre del cache se compone de country_code + name slug."""
    assert PhotoFinder._player_cache_key("Lionel Messi", "ARG") == "ARG_LIONEL_MESSI"
    assert PhotoFinder._player_cache_key("Pelé", "BRA") == "BRA_PEL"
    assert PhotoFinder._player_cache_key("José María", "URU") == "URU_JOS_MAR_A"

    finder = PhotoFinder(tmp_path)
    path = finder.cached_photo_path("Lionel Messi", "ARG")
    assert path.name == "ARG_LIONEL_MESSI.jpg"


def test_second_call_uses_cache(tmp_path):
    """Tras una descarga exitosa, la segunda llamada al mismo jugador usa caché."""
    finder = PhotoFinder(tmp_path)
    wiki_url = "https://upload.wikimedia.org/photo.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(), status=200)
        with (patch.object(finder, "_search_wikipedia", return_value=wiki_url),):
            first = finder.find_photo("X Player", "Y Country", "ZZZ")
            assert first.source == SOURCE_WIKIPEDIA

    # Segunda llamada al mismo jugador → cache hit, no toca network
    with patch.object(finder, "_search_wikipedia") as wiki_mock:
        second = finder.find_photo("X Player", "Y Country", "ZZZ")
    assert second.source == SOURCE_CACHE
    wiki_mock.assert_not_called()


def test_placeholder_not_cached_per_player(tmp_path):
    """Cuando todo falla, el placeholder NO se guarda como cache del jugador.

    Esto permite que la próxima corrida intente la búsqueda real otra vez.
    """
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("Unknown Player", "Country", "ZZZ")

    assert result.source == SOURCE_PLACEHOLDER
    # El cache_path del jugador NO existe
    assert not finder.cached_photo_path("Unknown Player", "ZZZ").exists()
    # En cambio el placeholder compartido sí
    assert (tmp_path / PLACEHOLDER_FILENAME).exists()


def test_http_404_triggers_fallback(tmp_path):
    """Una URL que retorna 404 dispara el siguiente fallback."""
    finder = PhotoFinder(tmp_path)
    bad_url = "https://example.com/missing.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, bad_url, status=404)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[bad_url]),
            patch.object(finder, "_search_wikipedia", return_value=None),
        ):
            result = finder.find_photo("P", "C", "AAA")
    assert result.source == SOURCE_PLACEHOLDER


def test_placeholder_generation_creates_valid_image(tmp_path):
    """El placeholder generado es una imagen válida cargable por OpenCV."""
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("X", "Y", "PLC")
    img = cv2.imread(str(result.local_path))
    assert img is not None
    assert img.shape[0] > 0 and img.shape[1] > 0


# ----------------------------------------------------------------------
# Queries y face detection
# ----------------------------------------------------------------------


def test_build_queries_includes_lastname_and_spanish(tmp_path):
    finder = PhotoFinder(tmp_path)
    queries = finder._build_queries("Lionel Messi", "Argentina")
    joined = " | ".join(queries)
    assert any(q.startswith("Messi ") or " Messi" in q for q in queries)
    assert "futbolista" in joined
    assert "site:transfermarkt.com" in joined


def test_build_queries_with_single_word_name(tmp_path):
    finder = PhotoFinder(tmp_path)
    queries = finder._build_queries("Pele", "Brazil")
    assert all(isinstance(q, str) and q for q in queries)


def test_image_without_face_triggers_next_url(tmp_path):
    """Si la primera URL devuelve imagen sin cara, prueba la siguiente."""
    finder = PhotoFinder(tmp_path)
    no_face_url = "https://example.com/noface.jpg"
    with_face_url = "https://example.com/face.jpg"

    call_count = {"n": 0}

    def fake_has_face(_path):
        call_count["n"] += 1
        return call_count["n"] >= 2

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, no_face_url, body=_fake_image_bytes(200, 200), status=200)
        rsps.add(responses.GET, with_face_url, body=_fake_image_bytes(200, 200, seed=7), status=200)
        with (
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(
                finder,
                "_search_duckduckgo",
                return_value=[no_face_url, with_face_url],
            ),
            patch.object(finder, "_image_has_face", side_effect=fake_has_face),
        ):
            result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_DUCKDUCKGO
    assert call_count["n"] >= 2


def test_finder_tries_multiple_queries(tmp_path):
    """Si la primera query no devuelve URLs, prueba la siguiente."""
    finder = PhotoFinder(tmp_path)
    fake_url = "https://example.com/found.jpg"

    queries_called: list[str] = []

    def fake_ddg(query: str) -> list[str]:
        queries_called.append(query)
        return [fake_url] if len(queries_called) >= 2 else []

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, fake_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", side_effect=fake_ddg),
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG")
    assert result.source == SOURCE_DUCKDUCKGO
    assert len(queries_called) >= 2


def test_image_has_face_rejects_blank_image(tmp_path):
    finder = PhotoFinder(tmp_path)
    blank = tmp_path / "blank.jpg"
    arr = np.full((300, 300, 3), 200, dtype=np.uint8)
    cv2.imwrite(str(blank), arr)
    assert finder._image_has_face(blank) is False


def test_image_has_face_returns_false_when_path_invalid(tmp_path):
    finder = PhotoFinder(tmp_path)
    assert finder._image_has_face(tmp_path / "missing.jpg") is False


# ----------------------------------------------------------------------
# `_is_good_photo` (Issue 2a)
# ----------------------------------------------------------------------


def test_is_good_photo_accepts_normal_image(tmp_path):
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "good.jpg"
    cv2.imwrite(str(p), _noisy_array(200, 200))
    assert finder._is_good_photo(p) is True


def test_is_good_photo_rejects_too_wide(tmp_path):
    """Aspect ratio > 1.8 → descartar (foto grupal)."""
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "wide.jpg"
    cv2.imwrite(str(p), _noisy_array(400, 200))  # 2.0 aspect
    assert finder._is_good_photo(p) is False


def test_is_good_photo_rejects_blank_image(tmp_path):
    """Una imagen totalmente uniforme (std bajo) se descarta."""
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "blank.jpg"
    cv2.imwrite(str(p), np.full((200, 200, 3), 128, dtype=np.uint8))
    assert finder._is_good_photo(p) is False


def test_is_good_photo_rejects_almost_black(tmp_path):
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "dark.jpg"
    rng = np.random.default_rng(1)
    arr = rng.integers(0, 30, size=(200, 200, 3), dtype=np.uint8)
    cv2.imwrite(str(p), arr)
    assert finder._is_good_photo(p) is False


def test_is_good_photo_rejects_almost_white(tmp_path):
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "white.jpg"
    rng = np.random.default_rng(1)
    arr = rng.integers(230, 256, size=(200, 200, 3), dtype=np.uint8)
    cv2.imwrite(str(p), arr)
    assert finder._is_good_photo(p) is False


def test_is_good_photo_rejects_too_small(tmp_path):
    finder = PhotoFinder(tmp_path)
    p = tmp_path / "tiny.jpg"
    cv2.imwrite(str(p), _noisy_array(50, 50))
    assert finder._is_good_photo(p) is False


def test_is_good_photo_returns_false_when_path_invalid(tmp_path):
    finder = PhotoFinder(tmp_path)
    assert finder._is_good_photo(tmp_path / "missing.jpg") is False


# ----------------------------------------------------------------------
# Cascada Wiki → DDG → Google + cuota Google
# ----------------------------------------------------------------------


def test_cascade_order_wikipedia_before_duckduckgo(tmp_path):
    """Wiki se intenta antes que DDG: si wiki retorna URL, no se llama DDG."""
    finder = PhotoFinder(tmp_path)
    wiki_url = "https://upload.wikimedia.org/portrait.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_wikipedia", return_value=wiki_url),
            patch.object(finder, "_search_duckduckgo") as ddg,
        ):
            result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_WIKIPEDIA
    ddg.assert_not_called()


def test_cascade_order_google_after_duckduckgo(tmp_path):
    """Google se intenta solo si Wiki Y DDG fallaron."""
    finder = PhotoFinder(tmp_path)
    google_url = "https://google.example/img.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, google_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.dict(
                os.environ,
                {GOOGLE_API_KEY_ENV: "fake_key", GOOGLE_CSE_ID_ENV: "fake_cse"},
            ),
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_search_duckduckgo", return_value=[]),
            patch.object(finder, "search_google_only", return_value=[google_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_GOOGLE
    assert finder.google_calls_used == 1


def test_google_skipped_when_quota_exhausted(tmp_path):
    finder = PhotoFinder(tmp_path, google_quota=0)
    with (
        patch.dict(
            os.environ,
            {GOOGLE_API_KEY_ENV: "fake_key", GOOGLE_CSE_ID_ENV: "fake_cse"},
        ),
        patch.object(finder, "_search_wikipedia", return_value=None),
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "search_google_only") as google_mock,
    ):
        result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_PLACEHOLDER
    google_mock.assert_not_called()
    assert finder.google_calls_used == 0


def test_google_skipped_when_env_not_configured(tmp_path):
    finder = PhotoFinder(tmp_path)
    env = {k: v for k, v in os.environ.items() if k not in (GOOGLE_API_KEY_ENV, GOOGLE_CSE_ID_ENV)}
    with (
        patch.dict(os.environ, env, clear=True),
        patch.object(finder, "_search_wikipedia", return_value=None),
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "search_google_only") as google_mock,
    ):
        result = finder.find_photo("Player", "Country", "PLY")
    assert result.source == SOURCE_PLACEHOLDER
    google_mock.assert_not_called()
    assert finder.google_calls_used == 0


def test_google_counter_increments_each_call(tmp_path):
    finder = PhotoFinder(tmp_path, google_quota=10)
    google_url = "https://google.example/img.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, google_url, body=_fake_image_bytes(200, 200), status=200)
        rsps.add(responses.GET, google_url, body=_fake_image_bytes(200, 200, seed=7), status=200)
        with (
            patch.dict(
                os.environ,
                {GOOGLE_API_KEY_ENV: "fake_key", GOOGLE_CSE_ID_ENV: "fake_cse"},
            ),
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_search_duckduckgo", return_value=[]),
            patch.object(finder, "search_google_only", return_value=[google_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            finder.find_photo("Player A", "Country", "PYA")
            finder.find_photo("Player B", "Country", "PYB")
    assert finder.google_calls_used == 2


def test_is_google_enabled_combines_env_and_quota(tmp_path):
    finder = PhotoFinder(tmp_path, google_quota=2)
    env_no_google = {
        k: v for k, v in os.environ.items() if k not in (GOOGLE_API_KEY_ENV, GOOGLE_CSE_ID_ENV)
    }
    with patch.dict(os.environ, env_no_google, clear=True):
        assert finder._is_google_enabled() is False

    with patch.dict(os.environ, {GOOGLE_API_KEY_ENV: "k", GOOGLE_CSE_ID_ENV: "c"}):
        assert finder._is_google_enabled() is True
        finder.google_calls_used = 2
        assert finder._is_google_enabled() is False
