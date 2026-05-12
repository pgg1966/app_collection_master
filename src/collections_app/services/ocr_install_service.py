"""Service de descarga de assets OCR.

Antes (Prompt 7c) este service tambien manejaba `pip install` de las
deps pesadas (torch/ultralytics/easyocr/cv2) hacia el Python del
sistema. Con torch ya incluido en el bundle PyInstaller (Prompt 7e),
el unico flow que queda es **descargar los assets** (modelo .pt e
imagen de guia) desde GitHub Releases hacia `<APPDATA>/Collections/`.

Las URLs y filenames son constantes module-level. La descarga es
idempotente: si los archivos ya existen, se saltan sin tocar la red.

Nota de deuda tecnica (post-Mundial): renombrar a `OcrAssetService`
para reflejar que ya no instala nada. No se hace en esta sesion para
evitar la cascada cosmetica en `app_context.ocr_install` + callsites.
"""

from __future__ import annotations

import contextlib
import logging
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path

from collections_app.core.utils.paths import get_images_dir, get_models_dir
from collections_app.services.exceptions import OcrInstallError

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[int, str], None]


# URLs y filenames de los assets OCR distribuidos via GitHub Releases.
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


class OcrInstallService:
    """Descarga assets OCR (modelo + guia) bajo demanda."""

    def download_ocr_assets(self: OcrInstallService, progress_callback: ProgressCallback) -> None:
        """Descarga modelo y guia OCR desde GitHub Releases.

        Idempotente: si los archivos ya existen en disco, se saltan.
        El modelo es fatal (sin .pt el OCR no funciona); la guia es
        no-fatal (solo es ayuda visual en la tab).

        Raises:
            OcrInstallError: si falla la descarga del modelo.
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
        """Descarga modelo (fatal) + guia (no-fatal) en los rangos dados.

        Los rangos de progreso vienen como tuplas (start, end) para que
        este metodo pueda emitirse con porcentajes custom. NO emite el
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
        # Rename atómico solo si la descarga completó.
        temp.replace(dest)
