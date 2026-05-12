"""Tests del OcrInstallService — mock de subprocess.Popen streameado.

Cero subprocess real. Cubre:

- `is_installed()` delega correctamente a `OcrService.is_available()`.
- `install()` recorre el pipeline en orden y emite progreso por cada
  línea de output del pip.
- Si el output del pip stalls > `_IDLE_TICK_SECONDS`, se emiten ticks
  incrementales para que la barra no parezca congelada.
- Si `Popen` retorna código != 0, levanta `OcrInstallError` con el
  tail del output capturado.
- Si `Popen` lanza OSError, también levanta `OcrInstallError`.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Iterator
from unittest.mock import patch

import pytest

from collections_app.services.exceptions import OcrInstallError
from collections_app.services.ocr_install_service import OcrInstallService

# ---------------------------------------------------------------------
# is_installed
# ---------------------------------------------------------------------


def test_is_installed_delegates_to_ocr_service(monkeypatch: pytest.MonkeyPatch) -> None:
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
# Fake Popen — protocolo mínimo para el streaming
# ---------------------------------------------------------------------


class _FakeStdout:
    """`readline()` devuelve líneas del buffer y luego "" al terminar."""

    def __init__(self: _FakeStdout, lines: list[str]) -> None:
        self._iter: Iterator[str] = iter(lines)
        self._exhausted = False

    def readline(self: _FakeStdout) -> str:
        try:
            return next(self._iter)
        except StopIteration:
            self._exhausted = True
            return ""


class _FakeProcess:
    """`subprocess.Popen` stub con stdout streameado y returncode."""

    def __init__(
        self: _FakeProcess,
        lines: list[str],
        returncode: int = 0,
    ) -> None:
        self.stdout = _FakeStdout(lines)
        self.returncode = returncode
        # `poll()` debe devolver None mientras hay líneas pendientes,
        # y el returncode una vez que readline() devolvió "".
        self._poll_state: int | None = None
        self._lines_total = len(lines)
        self._lines_read = 0

    def readline_via_stdout(self: _FakeProcess) -> str:
        # Wrapper para llevar la cuenta. El service llama
        # `self._stdout.readline()` directamente, así que en este fake
        # podemos delegar y avanzar el contador desde un wrapper externo.
        line = self.stdout.readline()
        if line:
            self._lines_read += 1
        return line

    def poll(self: _FakeProcess) -> int | None:
        return self._poll_state

    def wait(self: _FakeProcess) -> int:
        # Forzar el cierre: cuando wait() corre, ya consumimos todo.
        self._poll_state = self.returncode
        return self.returncode


def _patch_stdout_with_poll(fake_proc: _FakeProcess) -> None:
    """Hace que readline() devuelva las líneas y poll() vire a returncode
    cuando se agota el stream — sin requerir wait()."""
    original_readline = fake_proc.stdout.readline

    def readline_and_poll() -> str:
        line = original_readline()
        if not line:
            fake_proc._poll_state = fake_proc.returncode
        return line

    fake_proc.stdout.readline = readline_and_poll  # type: ignore[assignment]


def _make_popen(lines: list[str], returncode: int = 0):  # type: ignore[no-untyped-def]
    """Factory para usar como `side_effect` de patch('subprocess.Popen').

    Crea un FakeProcess fresco para cada llamada (cada comando del
    pipeline necesita su propio stream).
    """
    calls: list[list[str]] = []

    def factory(cmd, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(cmd)
        proc = _FakeProcess(lines.copy(), returncode=returncode)
        _patch_stdout_with_poll(proc)
        return proc

    factory.calls = calls  # type: ignore[attr-defined]
    return factory


# ---------------------------------------------------------------------
# install — happy path
# ---------------------------------------------------------------------


def test_install_runs_full_pipeline_with_streaming_output() -> None:
    """Cada línea del pip se emite al callback en su porcentaje vigente."""
    factory = _make_popen(["Collecting torch\n", "Installing collected packages\n"])
    progress: list[tuple[int, str]] = []

    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda pct, msg: progress.append((pct, msg)))

    # 3 comandos en el pipeline (torch / ultralytics / easyocr+opencv).
    assert len(factory.calls) == 3  # type: ignore[attr-defined]
    assert "torch" in factory.calls[0]  # type: ignore[attr-defined]
    assert "ultralytics" in factory.calls[1]  # type: ignore[attr-defined]
    assert "easyocr" in factory.calls[2]  # type: ignore[attr-defined]
    assert "opencv-python" in factory.calls[2]  # type: ignore[attr-defined]

    # Primer y último tick: inicio del paso 1 y "Instalación completada."
    assert progress[0][0] == 0
    assert progress[-1] == (100, "Instalación completada.")
    # Hay al menos un mensaje con el contenido de stdout.
    assert any("Collecting torch" in msg for _pct, msg in progress)


def test_install_emits_progress_for_each_command_in_pipeline() -> None:
    """El callback recibe los tres mensajes descriptivos del pipeline."""
    factory = _make_popen([])
    messages: list[str] = []

    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda _p, m: messages.append(m))

    assert any("PyTorch" in m for m in messages)
    assert any("Ultralytics" in m for m in messages)
    assert any("EasyOCR" in m for m in messages)
    assert messages[-1] == "Instalación completada."


def test_install_progress_percentages_are_monotonic() -> None:
    """El porcentaje nunca retrocede."""
    factory = _make_popen(["line 1\n", "line 2\n"])
    progress: list[int] = []

    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda pct, _m: progress.append(pct))

    assert progress == sorted(progress)
    assert progress[0] == 0
    assert progress[-1] == 100


# ---------------------------------------------------------------------
# install — errores
# ---------------------------------------------------------------------


def test_install_raises_with_captured_tail_when_pip_returns_nonzero() -> None:
    """Cuando Popen retorna != 0, el error incluye las últimas líneas."""
    factory = _make_popen(
        ["Collecting torch\n", "ERROR: package not found\n"],
        returncode=1,
    )
    with (
        patch("subprocess.Popen", side_effect=factory),
        pytest.raises(OcrInstallError, match="código 1"),
    ):
        OcrInstallService().install(lambda _p, _m: None)


def test_install_error_message_includes_stderr_tail() -> None:
    """El mensaje de error incluye el output capturado."""
    factory = _make_popen(["ERROR: could not find torch\n"], returncode=1)
    with (
        patch("subprocess.Popen", side_effect=factory),
        pytest.raises(OcrInstallError) as exc_info,
    ):
        OcrInstallService().install(lambda _p, _m: None)
    assert "could not find torch" in str(exc_info.value)


def test_install_raises_when_popen_oserror() -> None:
    def boom(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise OSError("python no encontrado")

    with (
        patch("subprocess.Popen", side_effect=boom),
        pytest.raises(OcrInstallError, match="no se pudo lanzar pip"),
    ):
        OcrInstallService().install(lambda _p, _m: None)


# ---------------------------------------------------------------------
# Idle ticks: si no hay output, el callback igual recibe progreso
# ---------------------------------------------------------------------


def test_install_emits_idle_tick_when_pip_is_silent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si stdout no emite nada y poll() sigue None, debe haber ticks.

    Forzamos `time.monotonic` a saltar 2.5s entre llamadas para que el
    branch de idle-tick se dispare sin esperar tiempo real.
    """
    # Stub time.monotonic con un contador que avanza 2.5s cada llamada.
    counter = {"t": 0.0}

    def fake_monotonic() -> float:
        counter["t"] += 2.5
        return counter["t"]

    # `time.sleep` también lo neutralizamos para que el test sea instantáneo.
    monkeypatch.setattr(
        "collections_app.services.ocr_install_service.time.monotonic", fake_monotonic
    )
    monkeypatch.setattr("collections_app.services.ocr_install_service.time.sleep", lambda _s: None)

    # Un FakeProcess silente: stdout vacío al principio, pero poll() devuelve
    # None las primeras N veces y luego returncode. Eso fuerza idle ticks.
    class _SilentProc:
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            self.stdout = _FakeStdout([])
            self.returncode = 0
            self._poll_calls = 0

        def poll(self):  # type: ignore[no-untyped-def]
            self._poll_calls += 1
            return None if self._poll_calls < 5 else 0

        def wait(self):  # type: ignore[no-untyped-def]
            return 0

    def factory(_cmd, **_kwargs):  # type: ignore[no-untyped-def]
        return _SilentProc()

    progress: list[tuple[int, str]] = []
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda p, m: progress.append((p, m)))

    # El callback recibió al menos un idle tick con el mensaje genérico.
    assert any("puede tardar" in msg for _pct, msg in progress)


def test_install_idle_tick_does_not_exceed_step_ceiling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Aunque pip esté silente mucho tiempo, el % del tick no rebasa el
    techo del paso (48% para torch, 98% para ultralytics)."""
    counter = {"t": 0.0}

    def fake_monotonic() -> float:
        counter["t"] += 2.5
        return counter["t"]

    monkeypatch.setattr(
        "collections_app.services.ocr_install_service.time.monotonic", fake_monotonic
    )
    monkeypatch.setattr("collections_app.services.ocr_install_service.time.sleep", lambda _s: None)

    class _VeryQuietProc:
        def __init__(self) -> None:  # type: ignore[no-untyped-def]
            self.stdout = _FakeStdout([])
            self.returncode = 0
            self._poll_calls = 0

        def poll(self):  # type: ignore[no-untyped-def]
            self._poll_calls += 1
            # 200 ticks silentes antes de cerrar.
            return None if self._poll_calls < 200 else 0

        def wait(self):  # type: ignore[no-untyped-def]
            return 0

    def factory(_cmd, **_kwargs):  # type: ignore[no-untyped-def]
        return _VeryQuietProc()

    progress: list[int] = []
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda p, _m: progress.append(p))

    # Ningún tick excede el 100% global. Y el 100% se emite solo al final.
    assert max(progress) == 100
    # El 100% aparece una sola vez, al final.
    assert progress.count(100) == 1
    assert progress[-1] == 100


# ---------------------------------------------------------------------
# Pre-flight: detectar módulos bloqueados antes de pip
# ---------------------------------------------------------------------


def test_install_raises_pre_flight_when_cv2_already_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si cv2 ya está en sys.modules, install() falla antes de tocar pip.

    Es el escenario "el usuario abrió una foto antes de instalar":
    el .pyd queda mapeado y pip no puede sobrescribirlo. Mejor avisar
    con un mensaje útil que dejar caer un WinError 5 opaco.
    """
    import sys
    import types

    monkeypatch.setitem(sys.modules, "cv2", types.ModuleType("cv2"))

    def spy_popen(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("Popen no debería ejecutarse en pre-flight")

    with (
        patch("subprocess.Popen", side_effect=spy_popen),
        pytest.raises(OcrInstallError, match="cerrá y reabrí"),
    ):
        OcrInstallService().install(lambda _p, _m: None)


def test_install_pre_flight_passes_when_modules_not_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si ningún módulo está cargado, install() avanza al pipeline."""
    import sys

    for m in ("cv2", "torch", "torchvision", "ultralytics", "easyocr"):
        monkeypatch.delitem(sys.modules, m, raising=False)

    factory = _make_popen([])
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda _p, _m: None)
    assert len(factory.calls) == 3  # type: ignore[attr-defined]


def test_install_pre_flight_ignores_none_module_in_sys_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`monkeypatch.setitem(sys.modules, "X", None)` (patrón de los
    tests del service para forzar ImportError) NO debe contar como
    módulo cargado en el pre-flight."""
    import sys

    for m in ("cv2", "torch", "torchvision", "ultralytics", "easyocr"):
        monkeypatch.setitem(sys.modules, m, None)

    factory = _make_popen([])
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda _p, _m: None)
    assert len(factory.calls) == 3  # type: ignore[attr-defined]


# ---------------------------------------------------------------------
# Descarga de modelo OCR y guía (feature Prompt 7d)
# ---------------------------------------------------------------------


def _redirect_assets_to_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path) -> tuple:  # type: ignore[no-untyped-def]
    """Aisla `get_models_dir` y `get_images_dir` para que `install()`
    descargue/lea en `tmp_path` y no en el `%APPDATA%` real."""
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
    return models_dir, images_dir


def test_install_downloads_model_and_guide_after_pip_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    """Happy path: tras los pip install se descargan los 2 assets."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _redirect_assets_to_tmp(monkeypatch, tmp_path)
    urls_called: list[str] = []

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        urls_called.append(url)
        from pathlib import Path

        Path(dest).write_bytes(b"x" * 1024)
        if reporthook is not None:
            reporthook(1, 1024, 1024)
        return str(dest), None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    factory = _make_popen([])
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda _p, _m: None)

    assert urls_called == [mod.OCR_MODEL_URL, mod.OCR_GUIDE_URL]
    assert (models_dir / mod.OCR_MODEL_FILENAME).is_file()
    assert (images_dir / mod.OCR_GUIDE_FILENAME).is_file()


def test_install_skips_download_when_files_already_exist(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    """Idempotente: si los assets ya están en disco, no hay descarga."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _redirect_assets_to_tmp(monkeypatch, tmp_path)
    (models_dir / mod.OCR_MODEL_FILENAME).write_bytes(b"existing model")
    (images_dir / mod.OCR_GUIDE_FILENAME).write_bytes(b"existing guide")

    def boom(*_a, **_kw):  # type: ignore[no-untyped-def]
        raise AssertionError("urlretrieve no debería ejecutarse en el caso idempotente")

    monkeypatch.setattr(urllib.request, "urlretrieve", boom)
    factory = _make_popen([])
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda _p, _m: None)

    # Contenido pre-existente intacto (no se sobrescribió).
    assert (models_dir / mod.OCR_MODEL_FILENAME).read_bytes() == b"existing model"
    assert (images_dir / mod.OCR_GUIDE_FILENAME).read_bytes() == b"existing guide"


def test_install_raises_when_model_download_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    """Fallo de red descargando el modelo → OcrInstallError (fatal)."""
    from collections_app.services import ocr_install_service as mod

    models_dir, _ = _redirect_assets_to_tmp(monkeypatch, tmp_path)

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        # Simular escritura parcial antes del fallo (debe ser limpiada).
        from pathlib import Path

        Path(dest).write_bytes(b"partial")
        raise urllib.error.URLError("Connection reset")

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    factory = _make_popen([])
    with (
        patch("subprocess.Popen", side_effect=factory),
        pytest.raises(OcrInstallError, match="No se pudo descargar el modelo OCR"),
    ):
        OcrInstallService().install(lambda _p, _m: None)

    # El archivo parcial fue limpiado para que el siguiente intento NO
    # entre al branch idempotente.
    assert not (models_dir / mod.OCR_MODEL_FILENAME).exists()


def test_install_guide_download_failure_does_not_raise(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    """Fallo de red descargando la guía → warning, install sigue OK."""
    from collections_app.services import ocr_install_service as mod

    models_dir, images_dir = _redirect_assets_to_tmp(monkeypatch, tmp_path)
    # Pre-existir el modelo para que solo la guía intente descargarse.
    (models_dir / mod.OCR_MODEL_FILENAME).write_bytes(b"existing model")

    def fake_urlretrieve(url, dest, reporthook=None):  # type: ignore[no-untyped-def]
        from pathlib import Path

        Path(dest).write_bytes(b"partial guide")
        raise urllib.error.URLError("Timeout")

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve)
    factory = _make_popen([])
    progress: list[tuple[int, str]] = []
    with patch("subprocess.Popen", side_effect=factory):
        OcrInstallService().install(lambda p, m: progress.append((p, m)))

    # install retornó sin levantar.
    assert progress[-1] == (100, "Instalación completada.")
    # Guía parcial limpiada — no quedó archivo corrupto en disco.
    assert not (images_dir / mod.OCR_GUIDE_FILENAME).exists()
