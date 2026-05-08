"""Tests de los helpers de sistema usados por el dialog de éxito (5b).

Cubre:
- `open_folder_with_file_selected`: arma el comando `explorer /select,`
  con path absoluto, captura `OSError` con fallback a abrir solo el
  directorio padre.
- `open_mailto`: construye el URL `mailto:?subject=...&body=...` con
  quoting correcto y pasa por `QDesktopServices.openUrl`. Cuerpo cap a
  500 chars (mitigación riesgo G1 del plan).

Ambos helpers son cross-platform en intent pero el target principal es
Windows; en Linux/Mac se degrada a abrir el directorio padre.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from collections_app.views.exchange._system_helpers import (
    _build_mailto_url,
    _truncate_body,
    open_folder_with_file_selected,
    open_mailto,
)

# ---------------------------------------------------------------------
# open_folder_with_file_selected
# ---------------------------------------------------------------------


@pytest.mark.skipif(sys.platform != "win32", reason="explorer.exe es Windows-only")
def test_open_folder_uses_explorer_with_select_flag(tmp_path: Path) -> None:
    """En Windows: `explorer /select,<absolute_path>`."""
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")
    with patch("subprocess.Popen") as mock_popen:
        open_folder_with_file_selected(f)
    # Debe haber sido llamado al menos una vez.
    assert mock_popen.called
    args, _ = mock_popen.call_args
    cmd = args[0]
    # Args: ['explorer', '/select,', '<absolute path>']
    assert cmd[0] == "explorer"
    assert cmd[1] == "/select,"
    assert Path(cmd[2]).is_absolute()
    assert Path(cmd[2]) == f.resolve()


@pytest.mark.skipif(sys.platform != "win32", reason="explorer.exe es Windows-only")
def test_open_folder_falls_back_when_explorer_oserrors(tmp_path: Path) -> None:
    """Si `Popen(explorer)` lanza OSError, fallback a abrir el directorio padre."""
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_popen(cmd, *args, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(cmd)
        if cmd[0] == "explorer" and "/select," in cmd:
            msg = "boom"
            raise OSError(msg)
        # Fallback OK.

        class _Dummy:
            pass

        return _Dummy()

    with patch("subprocess.Popen", side_effect=fake_popen):
        open_folder_with_file_selected(f)

    # Debe haber al menos 2 llamadas: la primera con /select,, la segunda fallback.
    assert len(calls) >= 2
    fallback = calls[-1]
    # El fallback abre el directorio padre.
    assert Path(fallback[-1]) == f.parent.resolve()


# ---------------------------------------------------------------------
# open_mailto
# ---------------------------------------------------------------------


def test_build_mailto_url_quotes_subject_and_body() -> None:
    url = _build_mailto_url(subject="Hola che!", body="Línea 1\nLínea 2")
    # Espacios → %20, salto de línea → %0A, signos especiales preservados.
    assert url.startswith("mailto:?")
    assert "subject=Hola%20che%21" in url
    assert "body=" in url
    assert "L%C3%ADnea%201" in url  # Línea (encoded)
    assert "%0A" in url


def test_build_mailto_url_with_empty_body() -> None:
    url = _build_mailto_url(subject="Asunto", body="")
    assert url.startswith("mailto:?")
    assert "body=" in url


def test_truncate_body_under_cap_returns_input() -> None:
    body = "x" * 100
    assert _truncate_body(body) == body


def test_truncate_body_over_cap_is_capped() -> None:
    body = "x" * 1000
    out = _truncate_body(body)
    # Default cap del módulo: 500 chars.
    assert len(out) <= 500


def test_open_mailto_calls_qdesktopservices_with_mailto_url() -> None:
    with patch(
        "collections_app.views.exchange._system_helpers.QDesktopServices.openUrl"
    ) as mock_open:
        open_mailto(subject="Hola", body="Cuerpo")
    assert mock_open.called
    qurl = mock_open.call_args.args[0]
    # QUrl tiene `toString()`.
    assert qurl.toString().startswith("mailto:?")


def test_open_mailto_truncates_long_body() -> None:
    long_body = "x" * 5000
    with patch(
        "collections_app.views.exchange._system_helpers.QDesktopServices.openUrl"
    ) as mock_open:
        open_mailto(subject="Hola", body=long_body)
    qurl = mock_open.call_args.args[0]
    url_str = qurl.toString()
    # El URL completo no debería ser tan largo como el body original (5000 chars
    # quoted serían ~5000+; con cap a 500 queda muy por debajo).
    assert len(url_str) < 1500
