"""Tests del bootstrap main() — parsing de argparse + manejo de profile.

No levantamos `QApplication.exec()`. Para los tests que necesitan una
app corriendo, mockeamos `_run` para que retorne 0 sin entrar al event
loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from collections_app import main as main_module


@pytest.fixture(autouse=True)
def _qapp() -> QApplication | None:
    """QApplication único por proceso para que QMainWindow no explote."""
    return QApplication.instance() or QApplication([])


def _isolate_app_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))


def test_main_with_invalid_profile_returns_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Profile inválido → exit 2 + mensaje en stderr (no crash)."""
    _isolate_app_data(tmp_path, monkeypatch)
    rc = main_module.main(["--profile", "bad/name"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "profile invalido" in err


def test_title_suffix_default_is_empty() -> None:
    assert main_module._title_suffix_for(None) == ""


def test_title_suffix_with_profile() -> None:
    assert main_module._title_suffix_for("demo") == " — [demo]"


def test_main_runs_with_default_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Profile default + DB efímera + _run mockeado → exit 0."""
    _isolate_app_data(tmp_path, monkeypatch)

    captured: dict[str, object] = {}

    def fake_run(ctx, app, profile):  # type: ignore[no-untyped-def]
        captured["profile"] = profile
        captured["ctx"] = ctx
        return 0

    monkeypatch.setattr(main_module, "_run", fake_run)
    rc = main_module.main([])
    assert rc == 0
    assert captured["profile"] is None


def test_main_runs_with_named_profile(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _isolate_app_data(tmp_path, monkeypatch)

    captured: dict[str, object] = {}

    def fake_run(ctx, app, profile):  # type: ignore[no-untyped-def]
        captured["profile"] = profile
        return 0

    monkeypatch.setattr(main_module, "_run", fake_run)
    rc = main_module.main(["--profile", "test_profile"])
    assert rc == 0
    assert captured["profile"] == "test_profile"


def test_main_closes_context_even_when_run_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si _run levanta, el ctx.close() del finally igual debe correr.

    Verificamos vía el counter `close_count` patcheado a nivel clase
    (AppContext usa slots, no se pueden reassignar métodos por instancia).
    """
    _isolate_app_data(tmp_path, monkeypatch)

    close_calls = {"n": 0}
    real_close = main_module.AppContext.close

    def counting_close(self) -> None:  # type: ignore[no-untyped-def]
        close_calls["n"] += 1
        real_close(self)

    monkeypatch.setattr(main_module.AppContext, "close", counting_close)

    def fake_run(ctx, app, profile):  # type: ignore[no-untyped-def]
        raise RuntimeError("simulated UI failure")

    monkeypatch.setattr(main_module, "_run", fake_run)

    with pytest.raises(RuntimeError, match="simulated"):
        main_module.main([])
    assert close_calls["n"] == 1
