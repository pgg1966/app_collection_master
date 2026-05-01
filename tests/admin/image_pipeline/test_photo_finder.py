"""Tests del PhotoFinder con mocks de internet."""

from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import responses
from PIL import Image

from collections_app.admin.image_pipeline.photo_finder import (
    SOURCE_CACHE,
    SOURCE_DUCKDUCKGO,
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


def test_all_urls_without_face_falls_back_to_wikipedia(tmp_path):
    """Si ninguna URL de DDG tiene cara, va a Wikipedia."""
    finder = PhotoFinder(tmp_path)
    no_face_url = "https://example.com/noface.jpg"
    wiki_url = "https://upload.wikimedia.org/portrait.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, no_face_url, body=_fake_image_bytes(200, 200), status=200)
        rsps.add(responses.GET, wiki_url, body=_fake_image_bytes(200, 200), status=200)
        with (
            patch.object(finder, "_search_duckduckgo", return_value=[no_face_url]),
            patch.object(finder, "_search_wikipedia", return_value=wiki_url),
            patch.object(finder, "_image_has_face", return_value=False),
        ):
            result = finder.find_photo("Player", "Country", "ABC-2")
    assert result.source == SOURCE_WIKIPEDIA


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
            patch.object(finder, "_image_has_face", return_value=True),
        ):
            result = finder.find_photo("Lionel Messi", "Argentina", "ARG-24")
    assert result.source == SOURCE_DUCKDUCKGO
    assert len(queries_called) >= 2
