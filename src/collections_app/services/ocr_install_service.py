"""Service de instalación on-demand de torch/ultralytics (Sesión 5d).

Permite a la UI lanzar `pip install` desde un `QThread` con un
callback de progreso, sin tener que conocer los detalles del
subprocess.

**Riesgo conocido (R1 del plan):** en un bundle de PyInstaller,
`sys.executable` apunta al Python embebido del bundle, no al Python
del sistema. El `pip install` se aplica entonces dentro del directorio
del bundle. Esto es lo deseado para la app standalone, pero requiere
verificación durante el Prompt 7 (empaquetado). Si el bundle no
expone el módulo `pip`, este service falla con `OcrInstallError` y la
UI muestra el botón "Reintentar" + el `stderr` del comando.

El callback de progreso recibe `(porcentaje: int, mensaje: str)`. La
implementación no parsea el output del pip (formato cambiante entre
versiones); usa un esquema simple basado en cuántos comandos
del pipeline llevamos completados, para que la barra avance al menos
de manera discreta.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable

from collections_app.services.exceptions import OcrInstallError

ProgressCallback = Callable[[int, str], None]


_INSTALL_PIPELINE: list[tuple[list[str], str]] = [
    (
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "torch",
            "torchvision",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ],
        "Instalando PyTorch (CPU)... esto puede tardar varios minutos.",
    ),
    (
        [sys.executable, "-m", "pip", "install", "ultralytics"],
        "Instalando Ultralytics YOLO...",
    ),
]


class OcrInstallService:
    """Wrapper sobre `pip install` para los packages de OCR."""

    @staticmethod
    def is_installed() -> bool:
        """Alias de `OcrService.is_available()` — re-export para que
        la UI lo importe sin pasar por `OcrService`."""
        # Import dentro del método para evitar arrastrar OcrService
        # (y sus imports) al construir este service.
        from collections_app.services.ocr_service import OcrService  # noqa: PLC0415

        return OcrService.is_available()

    def install(self: OcrInstallService, progress_callback: ProgressCallback) -> None:
        """Corre el pipeline de instalación con progreso reportado.

        El callback recibe `(porcentaje, mensaje)` antes de cada
        comando. Después de que el pipeline termina, llama una vez más
        con `(100, "Instalación completada.")`.

        Args:
            progress_callback: invocado en este mismo hilo. La UI debe
                envolver la llamada a `install()` en un `QThread` y
                conectar el callback a un signal cross-thread para
                actualizar la barra sin bloquear el event loop.

        Raises:
            OcrInstallError: si algún `pip install` retorna código != 0.
                El mensaje incluye `stderr` truncado para mostrar al user.
        """
        total = len(_INSTALL_PIPELINE)
        for index, (cmd, message) in enumerate(_INSTALL_PIPELINE):
            pct = int(index * 100 / total)
            progress_callback(pct, message)
            try:
                result = subprocess.run(  # noqa: S603 — comando construido a mano arriba
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except OSError as exc:
                raise OcrInstallError(
                    f"no se pudo lanzar pip: {exc}. Verificá que Python esté "
                    "disponible en el sistema."
                ) from exc
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                tail = stderr[-1500:] if len(stderr) > 1500 else stderr
                raise OcrInstallError(f"el comando falló (código {result.returncode}):\n{tail}")
        progress_callback(100, "Instalación completada.")
