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

**Streaming de progreso (fix post-smoke 5d):** el callback se llama
en cada línea de output del pip + un "tick incremental" cuando no
hay output por más de `_IDLE_TICK_SECONDS` segundos. Si pip queda
descargando torch (~800 MB) sin emitir nada, el tick avanza el
porcentaje 1% a la vez hasta el techo del paso (~48% para torch,
~98% para ultralytics) para que la UI nunca parezca colgada.
"""

from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Callable

from collections_app.services.exceptions import OcrInstallError

ProgressCallback = Callable[[int, str], None]


# Cada paso del pipeline define el rango de porcentaje que ocupa.
# El "ceiling" deja un 2% de headroom para que el último tick no
# alcance el techo del próximo paso antes de que el comando termine.
_INSTALL_PIPELINE: list[tuple[list[str], str, int, int]] = [
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
        0,  # start_pct
        48,  # ceiling_pct (deja 2% antes del 50% del siguiente paso)
    ),
    (
        [sys.executable, "-m", "pip", "install", "ultralytics"],
        "Instalando Ultralytics YOLO...",
        50,
        98,
    ),
]

_IDLE_TICK_SECONDS = 2.0  # cada cuánto avanzar 1% si pip no emite output


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
        """Corre el pipeline de instalación con progreso streameado.

        Para cada comando: lanza `Popen` con stdout mergeado, lee
        línea por línea y llama al `progress_callback` con cada
        renglón de output. Si pip queda silente por más de
        `_IDLE_TICK_SECONDS`, emite un tick con un mensaje genérico
        para que la barra no parezca congelada.

        Al terminar el pipeline llama una vez más con
        `(100, "Instalación completada.")`.

        Raises:
            OcrInstallError: si algún comando retorna código != 0 o si
                `Popen` lanza OSError.
        """
        for cmd, message, start_pct, ceiling_pct in _INSTALL_PIPELINE:
            progress_callback(start_pct, message)
            self._run_streamed(
                cmd=cmd,
                start_pct=start_pct,
                ceiling_pct=ceiling_pct,
                progress_callback=progress_callback,
            )
        progress_callback(100, "Instalación completada.")

    def _run_streamed(
        self: OcrInstallService,
        *,
        cmd: list[str],
        start_pct: int,
        ceiling_pct: int,
        progress_callback: ProgressCallback,
    ) -> None:
        """Lanza `cmd` y reportea progreso línea a línea.

        Cuando el output stalls > `_IDLE_TICK_SECONDS`, avanza el
        porcentaje 1% (sin pasarse de `ceiling_pct`) y emite un
        mensaje genérico.
        """
        try:
            process = subprocess.Popen(  # noqa: S603 — cmd construido a mano arriba
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise OcrInstallError(
                f"no se pudo lanzar pip: {exc}. Verificá que Python esté "
                "disponible en el sistema."
            ) from exc

        current_pct = start_pct
        last_emit = time.monotonic()
        captured_tail: list[str] = []

        try:
            assert process.stdout is not None
            for line in self._iter_lines_with_idle_ticks(
                process=process,
                progress_callback=progress_callback,
                start_pct=start_pct,
                ceiling_pct=ceiling_pct,
                last_emit_ref=[last_emit],
                current_pct_ref=[current_pct],
            ):
                # Mantener un buffer chico del output para incluir en
                # OcrInstallError si el comando falla. Captamos las
                # últimas 50 líneas — suficiente para diagnosticar
                # errores típicos sin sobrecargar el dialog.
                captured_tail.append(line)
                if len(captured_tail) > 50:
                    captured_tail.pop(0)
        finally:
            process.wait()

        if process.returncode != 0:
            tail = "\n".join(captured_tail).strip()
            tail = tail[-1500:] if len(tail) > 1500 else tail
            raise OcrInstallError(f"el comando falló (código {process.returncode}):\n{tail}")

    def _iter_lines_with_idle_ticks(
        self: OcrInstallService,
        *,
        process: subprocess.Popen,  # type: ignore[type-arg]
        progress_callback: ProgressCallback,
        start_pct: int,
        ceiling_pct: int,
        last_emit_ref: list[float],
        current_pct_ref: list[int],
    ) -> list[str]:
        """Generator-like: lee líneas y emite idle ticks intercalados.

        Devuelve la lista de líneas leídas para que el caller pueda
        capturar un tail para errores. La razón por la que NO usa un
        generator real es para que el `wait()` del finally del caller
        siempre se ejecute incluso si el callback rompe.
        """
        assert process.stdout is not None
        lines: list[str] = []
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                # Pip silencioso → idle tick si pasó suficiente tiempo.
                now = time.monotonic()
                if now - last_emit_ref[0] >= _IDLE_TICK_SECONDS:
                    if current_pct_ref[0] < ceiling_pct:
                        current_pct_ref[0] += 1
                    progress_callback(
                        current_pct_ref[0],
                        "Instalando... (esto puede tardar varios minutos)",
                    )
                    last_emit_ref[0] = now
                # Sleep cortito para no spin-loopear sobre stdout.
                time.sleep(0.1)
                continue
            stripped = line.strip()
            if stripped:
                progress_callback(current_pct_ref[0], stripped)
                last_emit_ref[0] = time.monotonic()
            lines.append(line)
        return lines
