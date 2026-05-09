"""Tests del OcrInstallService — mock de subprocess.

Cero subprocess real. Cubre:

- `is_installed()` delega correctamente a `OcrService.is_available()`.
- `install()` llama al pipeline en orden, reporta progreso y termina
  con 100%.
- Si `pip install` retorna código != 0, levanta `OcrInstallError` con
  el stderr en el mensaje.
- Si `subprocess.run` lanza OSError, también levanta `OcrInstallError`.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from collections_app.services.exceptions import OcrInstallError
from collections_app.services.ocr_install_service import OcrInstallService

# ---------------------------------------------------------------------
# is_installed
# ---------------------------------------------------------------------


def test_is_installed_delegates_to_ocr_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """is_installed() devuelve lo que devuelve OcrService.is_available()."""
    monkeypatch.setattr(
        "collections_app.services.ocr_service.OcrService.is_available",
        staticmethod(lambda: True),
    )
    assert OcrInstallService.is_installed() is True

    monkeypatch.setattr(
        "collections_app.services.ocr_service.OcrService.is_available",
        staticmethod(lambda: False),
    )
    assert OcrInstallService.is_installed() is False


# ---------------------------------------------------------------------
# install
# ---------------------------------------------------------------------


class _FakeRun:
    """Simula `subprocess.run`. Retorna el code/stderr configurado."""

    def __init__(self, returncode: int = 0, stderr: str = "") -> None:
        self.returncode = returncode
        self.stderr = stderr
        self.calls: list[list[str]] = []

    def __call__(self, cmd, **_kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(cmd)
        return self  # subprocess.CompletedProcess-like


def test_install_runs_full_pipeline_and_reports_progress() -> None:
    fake = _FakeRun(returncode=0)
    progress: list[tuple[int, str]] = []

    with patch("subprocess.run", fake):
        OcrInstallService().install(lambda pct, msg: progress.append((pct, msg)))

    # 2 comandos en el pipeline + el tick final 100%.
    assert len(fake.calls) == 2
    assert "torch" in fake.calls[0]
    assert "ultralytics" in fake.calls[1]
    # Progreso: 0%, 50%, 100%.
    pcts = [pct for pct, _msg in progress]
    assert pcts == [0, 50, 100]
    assert progress[-1][1] == "Instalación completada."


def test_install_raises_when_pip_returns_nonzero() -> None:
    fake = _FakeRun(returncode=1, stderr="ERROR: could not find package torch")
    with (
        patch("subprocess.run", fake),
        pytest.raises(OcrInstallError, match="código 1"),
    ):
        OcrInstallService().install(lambda _p, _m: None)


def test_install_raises_when_subprocess_oserror() -> None:
    def boom(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise OSError("python no encontrado")

    with (
        patch("subprocess.run", boom),
        pytest.raises(OcrInstallError, match="no se pudo lanzar pip"),
    ):
        OcrInstallService().install(lambda _p, _m: None)


def test_install_progress_callback_includes_messages() -> None:
    """Cada comando del pipeline tiene su mensaje descriptivo."""
    fake = _FakeRun(returncode=0)
    messages: list[str] = []

    with patch("subprocess.run", fake):
        OcrInstallService().install(lambda _p, m: messages.append(m))

    assert any("PyTorch" in m for m in messages)
    assert any("Ultralytics" in m for m in messages)
    assert messages[-1] == "Instalación completada."


def test_install_truncates_long_stderr_in_error() -> None:
    """Stderr de >1500 chars se trunca para que el QMessageBox no se desborde."""
    long_err = "x" * 5000
    fake = _FakeRun(returncode=1, stderr=long_err)
    with (
        patch("subprocess.run", fake),
        pytest.raises(OcrInstallError) as exc_info,
    ):
        OcrInstallService().install(lambda _p, _m: None)
    assert len(str(exc_info.value)) < 2000
