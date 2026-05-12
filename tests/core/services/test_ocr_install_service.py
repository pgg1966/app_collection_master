"""Tests del OcrInstallService — solo flow de descarga de assets.

Antes (Prompt 7c) este service manejaba `pip install` de torch/etc. hacia
el Python del sistema. Con torch incluido en el bundle (Prompt 7e) ese
flow desaparece; el unico path que queda es la descarga de modelo + guia
OCR desde GitHub Releases.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path

import pytest

from collections_app.services.exceptions import OcrInstallError
from collections_app.services.ocr_install_service import OcrInstallService


@pytest.fixture(autouse=True)
def _isolated_ocr_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    """Asegura que NINGUN test toque `%APPDATA%/Collections/` real ni la red.

    Patchea:
    - `get_models_dir` / `get_images_dir` → subdirs de `tmp_path`.
    - `urllib.request.urlretrieve` → escribe un archivo fake al `dest`.
      Tests que necesiten un urlretrieve distinto (idempotencia, fallo)
      lo overrideán via su propio monkeypatch.

    Returns (models_dir, images_dir) para tests que quieran asertarlos.
    """
    models_dir = tmp_path / "models"
    images_dir = tmp_path / "images"
    models_dir.mkdir(parents=True)
    images_dir.mkdir(parents=True)
    monkeypatch.setattr(
        "collections_app.services.ocr_install_service.get_models_dir",
        lambda: models_dir,
    )
    monkeypatch.setattr(
        "collections_app.services.ocr_install_service.get_images_dir",
        lambda: images_dir,
    )

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        Path(dest).write_bytes(b"fake bytes")
        if reporthook is not None:
            reporthook(1, 1024, 1024)
        return str(dest), None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    return models_dir, images_dir


# ---------------------------------------------------------------------
# download_ocr_assets — happy path / idempotencia / errores
# ---------------------------------------------------------------------


def test_download_ocr_assets_downloads_both_when_missing(
    _isolated_ocr_paths: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Happy path: descarga modelo + guía y termina con progress 100."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _isolated_ocr_paths
    urls_called: list[str] = []

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        urls_called.append(url)
        Path(dest).write_bytes(b"y")
        return str(dest), None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    progress: list[tuple[int, str]] = []
    OcrInstallService().download_ocr_assets(lambda p, m: progress.append((p, m)))

    assert urls_called == [mod.OCR_MODEL_URL, mod.OCR_GUIDE_URL]
    assert (models_dir / mod.OCR_MODEL_FILENAME).is_file()
    assert (images_dir / mod.OCR_GUIDE_FILENAME).is_file()
    assert progress[-1] == (100, "Descarga completada.")


def test_download_ocr_assets_skips_when_files_already_exist(
    _isolated_ocr_paths: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Idempotente: archivos pre-existentes no se sobrescriben."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _isolated_ocr_paths
    (models_dir / mod.OCR_MODEL_FILENAME).write_bytes(b"existing model")
    (images_dir / mod.OCR_GUIDE_FILENAME).write_bytes(b"existing guide")

    def boom(*_a, **_kw):  # type: ignore[no-untyped-def]
        raise AssertionError("urlretrieve no debería ejecutarse")

    monkeypatch.setattr(urllib.request, "urlretrieve", boom)
    OcrInstallService().download_ocr_assets(lambda _p, _m: None)

    assert (models_dir / mod.OCR_MODEL_FILENAME).read_bytes() == b"existing model"
    assert (images_dir / mod.OCR_GUIDE_FILENAME).read_bytes() == b"existing guide"


def test_download_ocr_assets_raises_when_model_fails(
    _isolated_ocr_paths: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fallo del modelo → OcrInstallError (fatal)."""
    models_dir, _ = _isolated_ocr_paths

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        Path(dest).write_bytes(b"partial")
        raise urllib.error.URLError("Connection reset")

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    with pytest.raises(OcrInstallError, match="No se pudo descargar el modelo OCR"):
        OcrInstallService().download_ocr_assets(lambda _p, _m: None)

    # El destino final NO existe (.part limpiado, sin rename).
    from collections_app.services import ocr_install_service as mod

    assert not (models_dir / mod.OCR_MODEL_FILENAME).exists()
    assert not (models_dir / (mod.OCR_MODEL_FILENAME + ".part")).exists()


def test_download_ocr_assets_does_not_corrupt_existing_on_failure(
    _isolated_ocr_paths: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si urlretrieve falla con 404, archivos pre-existentes no se tocan.

    Regresión del bug donde urlretrieve(url, dest, ...) escribía el body
    del 404 a dest antes de raisear, y el catch lo unlink-eaba después,
    perdiendo el archivo válido. Fix: descargar a `<dest>.part` y solo
    renombrar si la descarga completó.
    """
    models_dir, _ = _isolated_ocr_paths
    other_path = models_dir / "other_critical.dat"
    other_path.write_bytes(b"critical pre-existing data")

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        Path(dest).write_bytes(b"<html>404 not found</html>")
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)  # type: ignore[arg-type]

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    with pytest.raises(OcrInstallError, match="No se pudo descargar el modelo OCR"):
        OcrInstallService().download_ocr_assets(lambda _p, _m: None)

    assert other_path.read_bytes() == b"critical pre-existing data"


def test_download_ocr_assets_guide_failure_does_not_raise(
    _isolated_ocr_paths: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fallo de la guía (no-fatal) → warning, no raise."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _isolated_ocr_paths
    # Modelo pre-existente para que solo la guía intente descargarse.
    (models_dir / mod.OCR_MODEL_FILENAME).write_bytes(b"existing model")

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        Path(dest).write_bytes(b"partial guide")
        raise urllib.error.URLError("Timeout")

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    progress: list[tuple[int, str]] = []
    OcrInstallService().download_ocr_assets(lambda p, m: progress.append((p, m)))

    assert progress[-1] == (100, "Descarga completada.")
    assert not (images_dir / mod.OCR_GUIDE_FILENAME).exists()
