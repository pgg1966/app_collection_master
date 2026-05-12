"""Service de instalación on-demand de torch/ultralytics (Sesión 5d).

Permite a la UI lanzar `pip install` desde un `QThread` con un
callback de progreso, sin tener que conocer los detalles del
subprocess.

**Bundle PyInstaller (Prompt 7):** dentro del bundle, `sys.executable`
apunta al `.exe` y NO acepta `-m pip` — PyInstaller no embebe un
intérprete Python utilizable. Por eso `_resolve_python_exe()` detecta
el modo frozen y busca Python en el `PATH` del sistema con
`shutil.which`. Si no se encuentra, lanza `OcrInstallError` con un
mensaje que apunta a python.org. En desarrollo (no frozen) se usa
`sys.executable` directo.

**Streaming de progreso (fix post-smoke 5d):** el callback se llama
en cada línea de output del pip + un "tick incremental" cuando no
hay output por más de `_IDLE_TICK_SECONDS` segundos. Si pip queda
descargando torch (~800 MB) sin emitir nada, el tick avanza el
porcentaje 1% a la vez hasta el techo del paso (~48% para torch,
~98% para ultralytics) para que la UI nunca parezca colgada.
"""

from __future__ import annotations

import contextlib
import logging
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

from collections_app.core.utils.paths import get_images_dir, get_models_dir
from collections_app.services.exceptions import OcrInstallError

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, str], None]


# URLs y filenames de los assets OCR distribuidos junto al .exe via
# GitHub Releases. Se descargan dentro de `install()` despues de los
# pip install, asi el usuario tiene un solo flow para preparar el OCR.
OCR_MODEL_URL = "https://github.com/pgg1966/app_collection_master/releases/download/v0.2.0/ocr_1.pt"
OCR_GUIDE_URL = (
    "https://github.com/pgg1966/app_collection_master" "/releases/download/v0.2.0/ocr_guide_1.jpg"
)
# Nombre canonico de la coleccion semilla que usa el modelo (informativo,
# no se valida en runtime — la semilla ya tiene los filenames seteados
# en `collections.ocr_model_filename` / `ocr_guide_filename`).
OCR_MODEL_COLLECTION_NAME = "Panini FIFA WC 2026 - Stickers"
OCR_MODEL_FILENAME = "ocr_1.pt"
OCR_GUIDE_FILENAME = "ocr_guide_1.jpg"


def _resolve_python_exe() -> str:
    """Devuelve el ejecutable de Python a usar para correr `pip install`.

    En desarrollo (no frozen): `sys.executable` apunta al intérprete
    real, se usa directo.

    En bundle PyInstaller (`sys.frozen` is True): `sys.executable` es
    el `.exe` del bundle, que NO soporta `-m pip`. Buscamos Python en
    el PATH del sistema con `shutil.which`. Si no aparece, lanzamos
    `OcrInstallError` con el link a python.org — el usuario necesita
    instalar Python para poder usar el OCR.
    """
    if getattr(sys, "frozen", False):
        found = shutil.which("python") or shutil.which("python3")
        if found is None:
            raise OcrInstallError(
                "Para usar el reconocimiento por foto necesitas tener "
                "Python 3.11+ instalado en el sistema. Descargalo desde "
                "https://www.python.org/downloads/ (marcando 'Add Python "
                "to PATH' durante la instalacion) y reabri la app."
            )
        return found
    return sys.executable


# Cada paso del pipeline define el rango de porcentaje que ocupa.
# El "ceiling" deja un 2% de headroom para que el último tick no
# alcance el techo del próximo paso antes de que el comando termine.
#
# Pipeline post fix-5d: PyTorch (necesario para YOLO y EasyOCR) →
# Ultralytics (modelo YOLO de detección de badges) → EasyOCR + OpenCV
# (segunda etapa de lectura de texto sobre cada crop). Cada paso ocupa
# ~30% del progreso total.
def _build_pipeline(python_exe: str) -> list[tuple[list[str], str, int, int]]:
    """Construye el pipeline de comandos `pip install` con el Python dado.

    Es función (no constante a nivel módulo) para que el ejecutable se
    resuelva en cada `install()` — necesario porque en el bundle el
    Python del sistema podría aparecer/desaparecer entre runs.
    """
    # Rangos comprimidos para dejar headroom (65-100) para las descargas
    # del modelo OCR y la imagen de guia que vienen despues del pip install.
    return [
        (
            [
                python_exe,
                "-m",
                "pip",
                "install",
                "torch",
                "torchvision",
                "--index-url",
                "https://download.pytorch.org/whl/cpu",
            ],
            "Instalando PyTorch (CPU)... esto puede tardar varios minutos.",
            0,
            28,
        ),
        (
            [python_exe, "-m", "pip", "install", "ultralytics"],
            "Instalando Ultralytics YOLO...",
            30,
            48,
        ),
        (
            [python_exe, "-m", "pip", "install", "easyocr", "opencv-python"],
            "Instalando EasyOCR + OpenCV...",
            50,
            63,
        ),
    ]


_IDLE_TICK_SECONDS = 2.0  # cada cuánto avanzar 1% si pip no emite output

# CREATE_NO_WINDOW (0x08000000) suprime la ventana de consola que
# Windows abre automaticamente al lanzar un subprocess GUI-less desde
# un .exe windowed. Solo aplica en Windows; en otros SO el flag se
# pasa como 0 (no-op).
_NO_WINDOW_FLAG = 0x08000000 if sys.platform == "win32" else 0

# Si alguno de estos módulos ya está cargado, pip no va a poder
# sobrescribir su `.pyd` y va a fallar con WinError 5 / Acceso denegado.
# El chequeo va antes de pip para dar al usuario un mensaje útil en
# lugar del traceback opaco.
_LOCKABLE_MODULES: tuple[str, ...] = (
    "cv2",
    "torch",
    "torchvision",
    "ultralytics",
    "easyocr",
)


class OcrInstallService:
    """Wrapper sobre `pip install` para los packages de OCR."""

    @staticmethod
    def is_installed(python_exe: str | None = None) -> bool:
        """Indica si torch/ultralytics/easyocr/cv2 estan disponibles.

        En **desarrollo** (no frozen) delega a `OcrService.is_available()`
        que hace un import directo: el venv del dev tiene torch en su
        sys.path, asi que ese check es correcto. El parametro
        `python_exe` se ignora en este modo.

        En **bundle PyInstaller** los imports del proceso apuntan al
        sys.path del bundle, que no incluye torch. El usuario los instala
        bajo demanda en el Python del sistema. Para chequear si esa
        instalacion existe lanzamos un subprocess al Python correcto:

        - Si el caller provee `python_exe` (tipicamente leido del
          AppSetting `ocr_python_exe` que persistio el `install()`
          exitoso), usar ese. Mismo Python que se uso para instalar
          → garantiza que el check encuentra las deps.
        - Si no, fallback a `shutil.which("python")`. Heredamos el PATH
          del shell que lanzo el .exe, asi que en doble-click desde
          Explorer resuelve al Python global del sistema.

        El subprocess usa `importlib.util.find_spec` para chequear que
        los modulos son importables sin cargarlos. Es ~30x mas rapido
        que `import torch` (que dispara la carga de DLLs nativas de
        torch / opencv, 5-15s cold). Timeout 30s defensivo para el
        peor caso (Python frio del sistema con AV scanning).
        """
        if not getattr(sys, "frozen", False):
            # Import dentro del método para evitar arrastrar OcrService
            # (y sus imports) al construir este service.
            from collections_app.services.ocr_service import OcrService  # noqa: PLC0415

            return OcrService.is_available()

        if python_exe is None:
            python_exe = shutil.which("python") or shutil.which("python3")
        if python_exe is None:
            return False
        try:
            result = subprocess.run(  # noqa: S603 — argv literal
                [
                    python_exe,
                    "-c",
                    (
                        "import importlib.util as u, sys; "
                        "sys.exit(0 if all("
                        "u.find_spec(m) for m in "
                        "('torch','ultralytics','easyocr','cv2')"
                        ") else 1)"
                    ),
                ],
                capture_output=True,
                timeout=30,
                creationflags=_NO_WINDOW_FLAG,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            return False
        return result.returncode == 0

    def install(self: OcrInstallService, progress_callback: ProgressCallback) -> str:
        """Corre el pipeline de instalación con progreso streameado.

        Para cada comando: lanza `Popen` con stdout mergeado, lee
        línea por línea y llama al `progress_callback` con cada
        renglón de output. Si pip queda silente por más de
        `_IDLE_TICK_SECONDS`, emite un tick con un mensaje genérico
        para que la barra no parezca congelada.

        Al terminar el pipeline llama una vez más con
        `(100, "Instalación completada.")`.

        Returns:
            El path al `python_exe` que se usó para correr `pip install`.
            El caller (slot en main thread) lo persiste en
            `AppSetting("ocr_python_exe")` para que `is_installed()`
            futuros consulten el mismo Python.

        Raises:
            OcrInstallError: si algún módulo del pipeline ya está
                cargado en el proceso actual (pip no podría
                sobrescribir su `.pyd`), o si algún comando retorna
                código != 0, o si `Popen` lanza OSError.
        """
        # Pre-flight: si cv2 / torch / etc. ya están en sys.modules, pip
        # va a fallar con WinError 5 al intentar reemplazar los archivos.
        # `is not None` para que el patrón de tests
        # `monkeypatch.setitem(sys.modules, "X", None)` no se considere
        # como módulo cargado.
        loaded = [m for m in _LOCKABLE_MODULES if sys.modules.get(m) is not None]
        if loaded:
            raise OcrInstallError(
                "Para instalar las dependencias de OCR, cerrá y reabrí "
                "la app y hacé click en 'Instalar dependencias' antes "
                "de abrir ninguna foto. El módulo de imágenes (cv2) "
                "está cargado y no se puede actualizar con la app en "
                "ejecución."
            )

        python_exe = _resolve_python_exe()
        for cmd, message, start_pct, ceiling_pct in _build_pipeline(python_exe):
            progress_callback(start_pct, message)
            self._run_streamed(
                cmd=cmd,
                start_pct=start_pct,
                ceiling_pct=ceiling_pct,
                progress_callback=progress_callback,
            )

        # Pasos 4+5: descarga de modelo + guia con rangos comprimidos
        # (los pip install ocuparon 0-63).
        self._download_assets(
            progress_callback,
            model_range=(65, 85),
            guide_range=(87, 95),
        )

        progress_callback(100, "Instalación completada.")
        return python_exe

    def download_ocr_assets(self: OcrInstallService, progress_callback: ProgressCallback) -> None:
        """Descarga solo modelo y guia OCR, sin tocar pip.

        Para el flow "Descargar modelo" del OcrLoaderTab cuando las
        deps de Python YA estan instaladas pero los archivos no existen
        en disco (ej. reinstalacion en PC nueva con el mismo Python que
        ya tenia torch). Idempotente: archivos pre-existentes se
        skippean igual que en `install()`.

        Mismas reglas de error que el bloque de descargas de `install()`:
        modelo es fatal, guia es no-fatal (warning + sigue).
        """
        self._download_assets(
            progress_callback,
            model_range=(0, 80),
            guide_range=(82, 97),
        )
        progress_callback(100, "Descarga completada.")

    def _download_assets(
        self: OcrInstallService,
        progress_callback: ProgressCallback,
        *,
        model_range: tuple[int, int],
        guide_range: tuple[int, int],
    ) -> None:
        """Pasos compartidos de descarga (modelo fatal + guia no-fatal).

        Los rangos de progreso vienen como tuplas (start, end) para que
        este metodo pueda emitirse tanto al final de `install()` (rangos
        comprimidos por encima del bloque pip) como en standalone via
        `download_ocr_assets()` (rangos completos 0-97). NO emite el
        progress final (100, "..."); el caller decide el mensaje.
        """
        model_dest = get_models_dir() / OCR_MODEL_FILENAME
        if model_dest.exists():
            progress_callback(model_range[1], "Modelo OCR ya descargado.")
        else:
            self._download_file(
                url=OCR_MODEL_URL,
                dest=model_dest,
                progress_callback=progress_callback,
                start_pct=model_range[0],
                end_pct=model_range[1],
                error_msg=(
                    "No se pudo descargar el modelo OCR. "
                    "Verificá tu conexión a internet y reintentá."
                ),
            )

        guide_dest = get_images_dir() / OCR_GUIDE_FILENAME
        if guide_dest.exists():
            progress_callback(guide_range[1], "Guía OCR ya descargada.")
        else:
            try:
                self._download_file(
                    url=OCR_GUIDE_URL,
                    dest=guide_dest,
                    progress_callback=progress_callback,
                    start_pct=guide_range[0],
                    end_pct=guide_range[1],
                    error_msg=None,
                )
            except (urllib.error.URLError, OSError) as exc:
                logger.warning("No se pudo descargar la guía OCR: %s", exc)
                progress_callback(guide_range[1], "Guía OCR no disponible (no es crítico).")

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
                creationflags=_NO_WINDOW_FLAG,
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

    def _download_file(
        self: OcrInstallService,
        *,
        url: str,
        dest: Path,
        progress_callback: ProgressCallback,
        start_pct: int,
        end_pct: int,
        error_msg: str | None,
    ) -> None:
        """Descarga `url` a `dest` con progreso entre `start_pct`/`end_pct`.

        Usa un archivo temporal `dest.<.part>` y solo renombra a `dest`
        si la descarga termino OK — para NO sobrescribir un archivo
        valido pre-existente en caso de fallo. `urllib.request.urlretrieve`
        escribe al destino antes de poder fallar (ej. al hacer 404
        recibe body de error y lo guarda igual), asi que el patron
        ingenuo `if exc: dest.unlink()` corrompe un archivo legitimo.

        Si `error_msg` se provee, las excepciones de red/IO se traducen
        a `OcrInstallError` con ese mensaje + detalle tecnico. Si es
        None, las excepciones se propagan tal cual al caller (que decide
        si las trata como warning).
        """
        progress_callback(start_pct, f"Descargando {dest.name}...")
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_name(dest.name + ".part")

        def reporthook(block_num: int, block_size: int, total_size: int) -> None:
            if total_size <= 0:
                return
            downloaded = min(block_num * block_size, total_size)
            fraction = downloaded / total_size
            pct = min(end_pct, start_pct + int(fraction * (end_pct - start_pct)))
            progress_callback(pct, f"Descargando {dest.name}... ({downloaded // 1024} KB)")

        try:
            urllib.request.urlretrieve(url, temp, reporthook=reporthook)  # noqa: S310 — URL hardcoded
        except (urllib.error.URLError, OSError) as exc:
            with contextlib.suppress(OSError):
                temp.unlink(missing_ok=True)
            if error_msg is not None:
                raise OcrInstallError(f"{error_msg}\n\nDetalle: {exc}") from exc
            raise
        # Rename atómico solo si la descarga completo.
        temp.replace(dest)

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
