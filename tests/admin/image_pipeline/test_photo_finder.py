"""Tests del PhotoFinder con mocks de internet."""

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
    SOURCE_CACHE,
    SOURCE_DUCKDUCKGO,
    SOURCE_GOOGLE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoFinder,
)


def _write_fake_jpg(path: Path, w: int = 200, h: int = 200) -> bytes:
    """Crea un JPEG válido en `path` y retorna los bytes."""
    arr = np.full((h, w, 3), 200, dtype=np.uint8)
    cv2.imwrite(str(path), arr)
    return path.read_bytes()


def _fake_image_bytes(w: int = 200, h: int = 200) -> bytes:
    """JPEG válido en memoria sin tocar disco."""
    arr = np.full((h, w, 3), 180, dtype=np.uint8)
    img = Image.fromarray(arr)
    import io

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_uses_cache_if_exists(tmp_path):
    """Si el archivo ya existe en caché, retorna sin tocar la red."""
    finder = PhotoFinder(tmp_path)
    cached = tmp_path / "ARG-24.jpg"
    _write_fake_jpg(cached)

    with patch.object(finder, "_search_duckduckgo") as ddg_mock:
        result = finder.find_photo("Lionel Messi", "Argentina", "ARG-24")
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
            patch.object(finder, "_search_duckduckgo", return_value=[fake_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG-24")
    assert result.source == SOURCE_DUCKDUCKGO
    assert result.success is True
    assert result.local_path.exists()


def test_wikipedia_fallback_when_ddg_fails(tmp_path):
    finder = PhotoFinder(tmp_path)
    wiki_url = "https://upload.wikimedia.org/foo.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[]),
            patch.object(finder, "_search_wikipedia", return_value=wiki_url),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG-24")
    assert result.source == SOURCE_WIKIPEDIA
    assert result.local_path.exists()


def test_placeholder_when_all_fail(tmp_path):
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("Unknown Player", "Atlantis", "XYZ-1")
    assert result.source == SOURCE_PLACEHOLDER
    assert result.success is True
    assert result.local_path.exists()


def test_download_validates_minimum_image_size(tmp_path):
    """Una imagen muy chica (50x50) se rechaza y dispara el siguiente fallback."""
    finder = PhotoFinder(tmp_path)
    tiny_url = "https://example.com/tiny.jpg"
    big_url = "https://example.com/big.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, tiny_url, body=_fake_image_bytes(50, 50), status=200)
        rsps.add(responses.GET, big_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[tiny_url, big_url]),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Player", "Country", "ABC-1")
    assert result.source == SOURCE_DUCKDUCKGO
    # La elegida fue la grande, no la chica
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
            result = finder.find_photo("Player", "Country", "ABC-2")
    assert result.source == SOURCE_PLACEHOLDER


def test_cache_key_uses_card_key(tmp_path):
    """El nombre del archivo cacheado coincide con el `card_key`."""
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("X", "Y", "MR-7")
    assert result.local_path.name == "MR-7.jpg"


def test_second_call_uses_cache(tmp_path):
    """Tras la primera descarga (placeholder), la segunda llamada usa caché."""
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        first = finder.find_photo("X", "Y", "ZZZ-1")
        assert first.source == SOURCE_PLACEHOLDER
    # Ahora con DDG/Wiki "disponibles", igual usa el caché
    with patch.object(finder, "_search_duckduckgo") as ddg_mock:
        second = finder.find_photo("X", "Y", "ZZZ-1")
    assert second.source == SOURCE_CACHE
    ddg_mock.assert_not_called()


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
            result = finder.find_photo("P", "C", "AAA-1")
    assert result.source == SOURCE_PLACEHOLDER


def test_placeholder_generation_creates_valid_image(tmp_path):
    """El placeholder generado es una imagen válida cargable por OpenCV."""
    finder = PhotoFinder(tmp_path)
    with (
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "_search_wikipedia", return_value=None),
    ):
        result = finder.find_photo("X", "Y", "PLC-1")
    img = cv2.imread(str(result.local_path))
    assert img is not None
    assert img.shape[0] > 0 and img.shape[1] > 0


# ----------------------------------------------------------------------
# Mejoras: queries múltiples y validación por face detection
# ----------------------------------------------------------------------


def test_build_queries_includes_lastname_and_spanish(tmp_path):
    """Las queries incluyen variantes con apellido solo y español."""
    finder = PhotoFinder(tmp_path)
    queries = finder._build_queries("Lionel Messi", "Argentina")
    joined = " | ".join(queries)
    # Apellido solo
    assert any(q.startswith("Messi ") or " Messi" in q for q in queries)
    # Variante en español
    assert "futbolista" in joined
    # Site hints
    assert "site:transfermarkt.com" in joined


def test_build_queries_with_single_word_name(tmp_path):
    finder = PhotoFinder(tmp_path)
    queries = finder._build_queries("Pele", "Brazil")
    # No debería romper con un solo nombre
    assert all(isinstance(q, str) and q for q in queries)


def test_image_without_face_triggers_next_url(tmp_path):
    """Si la primera URL devuelve imagen sin cara, prueba la siguiente."""
    finder = PhotoFinder(tmp_path)
    no_face_url = "https://example.com/noface.jpg"
    with_face_url = "https://example.com/face.jpg"

    call_count = {"n": 0}

    def fake_has_face(_path):
        call_count["n"] += 1
        # Primera vez False (rechazar), segunda True (aceptar)
        return call_count["n"] >= 2

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, no_face_url, body=_fake_image_bytes(200, 200), status=200)
        rsps.add(responses.GET, with_face_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(
                finder,
                "_search_duckduckgo",
                return_value=[no_face_url, with_face_url],
            ),
            patch.object(finder, "_image_has_face", side_effect=fake_has_face),
        ):
            result = finder.find_photo("Player", "Country", "ABC-1")
    assert result.source == SOURCE_DUCKDUCKGO
    # Probó al menos 2 imágenes (la primera rechazada por face)
    assert call_count["n"] >= 2


def test_wikipedia_used_first_when_available(tmp_path):
    """Wiki es la fuente prioritaria: si retorna URL, no se intenta DDG."""
    finder = PhotoFinder(tmp_path)
    wiki_url = "https://upload.wikimedia.org/portrait.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(200, 200), status=200)
        ddg_mock = patch.object(finder, "_search_duckduckgo")
        with (
            ddg_mock as ddg,
            patch.object(finder, "_search_wikipedia", return_value=wiki_url),
        ):
            result = finder.find_photo("Player", "Country", "ABC-2")
    assert result.source == SOURCE_WIKIPEDIA
    ddg.assert_not_called()


def test_image_has_face_rejects_blank_image(tmp_path):
    """Una imagen plana (sin caras reales) retorna False en _image_has_face."""
    finder = PhotoFinder(tmp_path)
    blank = tmp_path / "blank.jpg"
    arr = np.full((300, 300, 3), 200, dtype=np.uint8)
    cv2.imwrite(str(blank), arr)
    assert finder._image_has_face(blank) is False


def test_image_has_face_returns_false_when_path_invalid(tmp_path):
    finder = PhotoFinder(tmp_path)
    assert finder._image_has_face(tmp_path / "missing.jpg") is False


def test_finder_tries_multiple_queries(tmp_path):
    """Si la primera query no devuelve URLs, prueba la siguiente."""
    finder = PhotoFinder(tmp_path)
    fake_url = "https://example.com/found.jpg"

    queries_called: list[str] = []

    def fake_ddg(query: str) -> list[str]:
        queries_called.append(query)
        # Primera query vacía, segunda devuelve URL
        return [fake_url] if len(queries_called) >= 2 else []

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, fake_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", side_effect=fake_ddg),
            patch.object(finder, "_search_wikipedia", return_value=None),
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG-24")
    assert result.source == SOURCE_DUCKDUCKGO
    assert len(queries_called) >= 2


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
            result = finder.find_photo("Player", "Country", "ABC-1")
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
            result = finder.find_photo("Player", "Country", "ABC-2")
    assert result.source == SOURCE_GOOGLE
    assert finder.google_calls_used == 1


def test_google_skipped_when_quota_exhausted(tmp_path):
    """Si google_calls_used >= google_quota, Google no se intenta."""
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
        result = finder.find_photo("Player", "Country", "ABC-3")
    assert result.source == SOURCE_PLACEHOLDER
    google_mock.assert_not_called()
    assert finder.google_calls_used == 0


def test_google_skipped_when_env_not_configured(tmp_path):
    """Sin env vars, Google no se intenta y la cascada termina en placeholder."""
    finder = PhotoFinder(tmp_path)
    # Asegurar que las env vars NO están seteadas
    env = {k: v for k, v in os.environ.items() if k not in (GOOGLE_API_KEY_ENV, GOOGLE_CSE_ID_ENV)}
    with (
        patch.dict(os.environ, env, clear=True),
        patch.object(finder, "_search_wikipedia", return_value=None),
        patch.object(finder, "_search_duckduckgo", return_value=[]),
        patch.object(finder, "search_google_only") as google_mock,
    ):
        result = finder.find_photo("Player", "Country", "ABC-4")
    assert result.source == SOURCE_PLACEHOLDER
    google_mock.assert_not_called()
    assert finder.google_calls_used == 0


def test_google_counter_increments_each_call(tmp_path):
    """Cada vez que find_photo decide consultar Google, el counter sube."""
    finder = PhotoFinder(tmp_path, google_quota=10)
    google_url = "https://google.example/img.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, google_url, body=_fake_image_bytes(200, 200), status=200)
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
            finder.find_photo("Player", "Country", "ABC-A")
            finder.find_photo("Player", "Country", "ABC-B")
    assert finder.google_calls_used == 2


def test_is_google_enabled_combines_env_and_quota(tmp_path):
    """`_is_google_enabled` requiere quota disponible Y env vars seteadas."""
    finder = PhotoFinder(tmp_path, google_quota=2)
    # Sin env: deshabilitado aunque haya cuota
    env_no_google = {
        k: v for k, v in os.environ.items() if k not in (GOOGLE_API_KEY_ENV, GOOGLE_CSE_ID_ENV)
    }
    with patch.dict(os.environ, env_no_google, clear=True):
        assert finder._is_google_enabled() is False

    # Con env y cuota: habilitado
    with patch.dict(
        os.environ,
        {GOOGLE_API_KEY_ENV: "k", GOOGLE_CSE_ID_ENV: "c"},
    ):
        assert finder._is_google_enabled() is True
        # Si la cuota se agota, deshabilitado
        finder.google_calls_used = 2
        assert finder._is_google_enabled() is False
