"""Helpers de sistema usados por el dialog de éxito post-export (5b).

Dos funciones:

- `open_folder_with_file_selected(path)`: abre el explorador de archivos
  del SO con el archivo seleccionado. En Windows usa `explorer /select,`,
  en Linux/Mac fallback a abrir el directorio padre con `xdg-open`/`open`.

- `open_mailto(subject, body)`: abre el cliente de mail predeterminado
  con asunto y cuerpo pre-llenados. Cuerpo se trunca a 500 chars
  (mitigación G1: límite ~2000 chars en algunos clientes para URL
  `mailto:`).

Ambas funciones son tolerantes a errores: si el SO no responde, se
silencia el error con un fallback graceful (no romper la UI).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices

# Cap del cuerpo del `mailto:` para evitar URLs gigantes.
_MAILTO_BODY_CAP = 500


def _truncate_body(body: str) -> str:
    """Cap a `_MAILTO_BODY_CAP` chars para evitar URLs gigantes."""
    if len(body) <= _MAILTO_BODY_CAP:
        return body
    return body[: _MAILTO_BODY_CAP - 1] + "…"


def _build_mailto_url(*, subject: str, body: str) -> str:
    """Construye el URL `mailto:?subject=...&body=...` con quoting RFC 3986."""
    body = _truncate_body(body)
    qsubject = quote(subject, safe="")
    qbody = quote(body, safe="")
    return f"mailto:?subject={qsubject}&body={qbody}"


def open_mailto(*, subject: str, body: str) -> None:
    """Abre el cliente de mail predeterminado con asunto + cuerpo.

    El body se trunca a 500 chars (mitigación G1 del plan, riesgo de
    URLs gigantes que rompen en algunos clientes).
    """
    url = _build_mailto_url(subject=subject, body=body)
    QDesktopServices.openUrl(QUrl(url))


def open_folder_with_file_selected(path: Path) -> None:
    """Abre el explorador del SO con el archivo `path` seleccionado.

    - Windows: `explorer /select,<path>` (path absoluto).
    - Linux/Mac: fallback a abrir el directorio padre con
      `xdg-open`/`open`.

    Tolerante a errores: si el SO no responde, intenta el fallback de
    abrir el directorio padre. Si tampoco anda, retorna sin romper.
    """
    abs_path = path.resolve()
    parent = abs_path.parent

    if sys.platform == "win32":
        try:
            subprocess.Popen(  # noqa: S603 — comando estándar de Windows; args fijos
                ["explorer", "/select,", str(abs_path)],  # noqa: S607 — explorer en PATH del SO
            )
            return
        except OSError:
            # Fallback: abrir solo el directorio padre.
            try:
                subprocess.Popen(  # noqa: S603
                    ["explorer", str(parent)],  # noqa: S607
                )
            except OSError:
                return
        return

    # Linux / Mac: no tenemos `/select,` equivalente portable; abrir el padre.
    opener = (
        "open" if sys.platform == "darwin" else "xdg-open" if shutil.which("xdg-open") else None
    )
    if opener is None:
        return
    try:
        subprocess.Popen([opener, str(parent)])  # noqa: S603 — opener resuelto arriba
    except OSError:
        return
