"""Tests del CrestFinder."""

import io
import os
from pathlib import Path
from unittest.mock import patch

import responses
from PIL import Image

from collections_app.admin.crests.crest_finder import (
    COUNTRY_WIKIPEDIA_MAP,
    MIN_VALID_FILE_BYTES,
    SOURCE_CACHE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    SPECIAL_CODES,
    CrestFinder,
    is_valid_crest_file,
)


def _png_bytes(w: int = 200, h: int = 200) -> bytes:
    """PNG RGBA con ruido (alta entropía → siempre > MIN_VALID_FILE_BYTES).

    Se usa ruido en vez de color sólido para que el PNG resultante (y
    también el guardado tras `thumbnail`) supere holgadamente el umbral
    de validez de cache (`MIN_VALID_FILE_BYTES`).
    """
    img = Image.frombytes("RGBA", (w, h), os.urandom(w * h * 4))
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
    # Generamos un JPEG (RGB) con ruido para verificar la conversión a RGBA
    # y a la vez asegurar que el PNG guardado supera MIN_VALID_FILE_BYTES.
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


# ----------------------------------------------------------------------
# BUG 1 — Panamá no es set especial
# ----------------------------------------------------------------------


def test_pan_not_in_special_codes():
    """PAN es selección nacional: debe ir por la cascada de Wikipedia."""
    assert "PAN" not in SPECIAL_CODES
    assert "PANAMA" in COUNTRY_WIKIPEDIA_MAP
    assert COUNTRY_WIKIPEDIA_MAP["PANAMA"] == "Panama national football team"


# ----------------------------------------------------------------------
# BUG 2 — Validación defensiva de descargas
# ----------------------------------------------------------------------


def test_download_rejects_empty_response(tmp_path, monkeypatch):
    """Una respuesta de 0 bytes debe descartarse sin escribir el destino."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    finder = CrestFinder()
    dest = tmp_path / "EMP.png"
    img_url = "https://example.com/empty.png"

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"", status=200)
        ok = finder._download_and_process_crest(img_url, dest)

    assert ok is False
    assert not dest.exists()


def test_download_rejects_html_content(tmp_path, monkeypatch):
    """Si el server devuelve HTML, no se debe interpretar como imagen."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
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
    """Cualquier descarga < MIN_DOWNLOAD_BYTES se descarta."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    finder = CrestFinder()
    dest = tmp_path / "SML.png"
    img_url = "https://example.com/tiny.png"

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"x" * 200, status=200)
        ok = finder._download_and_process_crest(img_url, dest)

    assert ok is False
    assert not dest.exists()


def test_svg_detected_correctly():
    """`_is_svg` reconoce headers XML/SVG y rechaza binarios de imagen."""
    finder = CrestFinder()
    assert finder._is_svg(b'<?xml version="1.0"?><svg></svg>') is True
    assert finder._is_svg(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>') is True
    # Whitespace/BOM-style padding inicial: igual debe detectarse
    assert finder._is_svg(b'  \n  <?xml version="1.0"?><svg></svg>') is True
    # PNG / JPEG no son SVG
    assert finder._is_svg(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) is False
    assert finder._is_svg(b"\xff\xd8\xff\xe0" + b"\x00" * 100) is False
    assert finder._is_svg(b"GIF89a" + b"\x00" * 100) is False


def test_has_image_magic():
    """`_has_image_magic` reconoce los formatos binarios soportados."""
    finder = CrestFinder()
    assert finder._has_image_magic(b"\x89PNG\r\n\x1a\n") is True
    assert finder._has_image_magic(b"\xff\xd8\xff\xe0") is True  # JPEG
    assert finder._has_image_magic(b"GIF89a") is True
    assert finder._has_image_magic(b"RIFF\x00\x00\x00\x00WEBP") is True
    assert finder._has_image_magic(b"\x00\x00\x01\x00") is True  # ICO
    assert finder._has_image_magic(b"<html>") is False
    assert finder._has_image_magic(b"<?xml") is False


def test_is_valid_crest_file(tmp_path):
    """`is_valid_crest_file`: existe + supera MIN_VALID_FILE_BYTES."""
    missing = tmp_path / "missing.png"
    too_small = tmp_path / "small.png"
    too_small.write_bytes(b"x" * 100)
    big_enough = tmp_path / "ok.png"
    big_enough.write_bytes(b"x" * (MIN_VALID_FILE_BYTES + 1))

    assert is_valid_crest_file(missing) is False
    assert is_valid_crest_file(too_small) is False
    assert is_valid_crest_file(big_enough) is True


def test_corrupt_cache_is_deleted_and_retried(tmp_path, monkeypatch):
    """Si el cache contiene un PNG corrupto, se borra y la cascada continúa."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )

    # Pre-existe un archivo "corrupto" (vacío) que no supera el umbral
    corrupt = tmp_path / "URU.png"
    corrupt.write_bytes(b"")
    assert corrupt.exists()

    summary_url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/" "Uruguay_national_football_team"
    )
    img_url = "https://example.com/uruguay-crest.png"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            summary_url,
            json={"thumbnail": {"source": img_url}},
            status=200,
        )
        rsps.add(responses.GET, img_url, body=_png_bytes(), status=200)

        finder = CrestFinder()
        result = finder.find_crest("URU", "URUGUAY")

    # El cache corrupto se borró y se bajó el escudo real
    assert result.source == SOURCE_WIKIPEDIA
    assert result.local_path.exists()
    assert result.local_path.stat().st_size > MIN_VALID_FILE_BYTES


def test_placeholder_meets_min_valid_file_size(tmp_path, monkeypatch):
    """Los placeholders deben superar MIN_VALID_FILE_BYTES para que el cache los acepte."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    finder = CrestFinder()
    dest = tmp_path / "PLH.png"
    finder._generate_placeholder_crest("PLH", dest)
    assert dest.exists()
    assert dest.stat().st_size > MIN_VALID_FILE_BYTES
    assert is_valid_crest_file(dest) is True


def test_save_too_small_is_discarded(tmp_path, monkeypatch):
    """Si img.save produce un PNG < MIN_VALID_FILE_BYTES, se borra y retorna False."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    finder = CrestFinder()
    dest = tmp_path / "TIN.png"
    img_url = "https://example.com/tiny-but-valid.png"
    # Una imagen 4x4 sólida pasa los chequeos previos en bytes (PNG bien
    # formado), pero el archivo guardado queda muy por debajo de 1000 B.
    tiny = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
    buf = io.BytesIO()
    tiny.save(buf, format="PNG")
    # Padding para que la *descarga* supere MIN_DOWNLOAD_BYTES (500).
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
