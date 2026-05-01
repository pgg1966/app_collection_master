"""Tests del CrestFinder."""

import io
from pathlib import Path
from unittest.mock import patch

import responses
from PIL import Image

from collections_app.admin.crests.crest_finder import (
    SOURCE_CACHE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    SPECIAL_CODES,
    CrestFinder,
)


def _png_bytes(w: int = 100, h: int = 100, color=(255, 0, 0, 255)) -> bytes:
    img = Image.new("RGBA", (w, h), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@responses.activate
def test_uses_cache_if_crest_exists(tmp_path, monkeypatch):
    """Si el escudo ya está en disco, no toca la red."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    cached = tmp_path / "ARG.png"
    cached.write_bytes(_png_bytes())

    finder = CrestFinder()
    result = finder.find_crest("ARG", "ARGENTINA")
    assert result.source == SOURCE_CACHE
    assert result.local_path == cached
    assert len(responses.calls) == 0


def test_special_codes_go_to_placeholder(tmp_path, monkeypatch):
    """code_id en SPECIAL_CODES → placeholder con iniciales, sin red."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    finder = CrestFinder()
    # Pickear un code que esté efectivamente en SPECIAL_CODES
    code_id = next(iter(SPECIAL_CODES))
    result = finder.find_crest(code_id, code_id)
    assert result.source == SOURCE_PLACEHOLDER
    assert result.local_path.exists()


def test_wikipedia_api_called_for_country(tmp_path, monkeypatch):
    """Para un país, se hace request a Wikipedia y se baja el thumbnail."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    summary_url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/" "Argentina_national_football_team"
    )
    img_url = "https://example.com/argentina-crest.png"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            summary_url,
            json={"thumbnail": {"source": img_url}},
            status=200,
        )
        rsps.add(responses.GET, img_url, body=_png_bytes(), status=200)

        finder = CrestFinder()
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_WIKIPEDIA
    assert result.local_path.exists()


def test_download_converts_to_rgba_png(tmp_path, monkeypatch):
    """La imagen descargada se guarda como PNG RGBA."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    finder = CrestFinder()
    img_url = "https://example.com/jpg-image.jpg"
    # Generamos un JPEG (RGB) para verificar la conversión a RGBA
    rgb = Image.new("RGB", (100, 100), (0, 255, 0))
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=buf.getvalue(), status=200)
        ok = finder._download_and_process_crest(img_url, tmp_path / "BRA.png")

    assert ok is True
    saved = Image.open(tmp_path / "BRA.png")
    assert saved.mode == "RGBA"
    assert saved.format == "PNG"


def test_placeholder_generated_with_code_initials(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    finder = CrestFinder()
    dest = tmp_path / "XXX.png"
    finder._generate_placeholder_crest("XXX", dest)
    assert dest.exists()
    img = Image.open(dest)
    assert img.mode == "RGBA"
    assert img.size == (200, 200)


def test_invalid_image_url_triggers_placeholder(tmp_path, monkeypatch):
    """Si Wikipedia retorna un thumbnail inválido, se genera placeholder."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    summary_url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/" "Brazil_national_football_team"
    )
    img_url = "https://example.com/bad.png"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            summary_url,
            json={"thumbnail": {"source": img_url}},
            status=200,
        )
        rsps.add(responses.GET, img_url, body=b"not an image", status=200)

        finder = CrestFinder()
        result = finder.find_crest("BRA", "BRAZIL")

    assert result.source == SOURCE_PLACEHOLDER
    # El placeholder igual queda guardado
    assert result.local_path.exists()


def test_find_all_respects_rate_limiting(tmp_path, monkeypatch):
    """`find_all_crests` espera RATE_LIMIT_DELAY entre requests reales."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    sleep_calls: list[float] = []

    def fake_sleep(s: float) -> None:
        sleep_calls.append(s)

    monkeypatch.setattr("collections_app.admin.crests.crest_finder.time.sleep", fake_sleep)

    finder = CrestFinder()
    # Hacemos que find_crest siempre devuelva placeholder (sin red real)
    with patch.object(
        finder,
        "_get_wikipedia_crest_url",
        return_value=None,
    ):
        finder.find_all_crests([("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("FRA", "FRANCIA")])

    # Sleep no se llama antes del primer call de red, sí entre 2do y 3ro
    assert len(sleep_calls) == 2
    assert all(s >= 1.0 for s in sleep_calls)


def test_result_source_set_correctly_for_special_code(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    finder = CrestFinder()
    result = finder.find_crest("GBL", "Golden Ballers")
    assert result.code_id == "GBL"
    assert result.code_name == "Golden Ballers"
    assert result.source == SOURCE_PLACEHOLDER
    assert result.success is True


def test_import_manual_crest(tmp_path, monkeypatch):
    """import_manual_crest copia y normaliza una imagen local."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    src = tmp_path / "src.jpg"
    rgb = Image.new("RGB", (300, 300), (0, 0, 255))
    rgb.save(src, format="JPEG")

    finder = CrestFinder()
    result = finder.import_manual_crest("GBL", src)
    assert result.success is True
    saved = Image.open(result.local_path)
    assert saved.mode == "RGBA"
    assert saved.size[0] <= 200 and saved.size[1] <= 200


def test_country_not_in_map_falls_to_placeholder(tmp_path, monkeypatch):
    """Si el code_name no está en el mapa, no se busca y va a placeholder."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    finder = CrestFinder()
    result = finder.find_crest("XYZ", "PAIS_INVENTADO")
    assert result.source == SOURCE_PLACEHOLDER


def test_find_crest_success_returns_path(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    finder = CrestFinder()
    # Pre-cachear ARG
    (tmp_path / "ARG.png").write_bytes(_png_bytes())
    result = finder.find_crest("ARG", "ARGENTINA")
    assert result.local_path == tmp_path / "ARG.png"
    assert result.local_path.exists()
