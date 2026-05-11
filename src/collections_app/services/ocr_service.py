"""Service de reconocimiento óptico de cards (Sesión 5d / fix pipeline).

El pipeline completo, ejecutado por `run_inference`:

1. `cv2.imread` carga la foto.
2. YOLO detecta bounding boxes de badges (`self._model(img, conf=0.4)`).
3. Para cada bbox: recortar con 4px de padding.
4. `ocr_reader.leer_badge(crop)` lee texto crudo con EasyOCR.
5. `ocr_validator.build_validator(...)` arma un validador desde la
   DB de la colección activa; su `validar_codigo` corrige errores
   típicos (G→6, O→0) y valida contra el catálogo.
6. Para cada código válido, buscar la card en el catálogo y armar el
   `OcrDetection` con `card_id` y `card_name` resueltos.

**Imports lazy obligatorios:** ningún import de `torch`, `ultralytics`,
`easyocr` o `cv2` aparece a nivel de módulo. Los 4 viven dentro de los
métodos que los necesitan. El test
`tests/architecture/test_no_top_level_torch_imports.py` lo enforcea.

**SQLite cross-thread:** `run_inference` recibe `db_path` y abre su
propia `sqlite3.Connection` adentro (el caller — un QThread —
no puede usar la conn del hilo principal sin que SQLite proteste).
La conn se cierra en `finally`.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from collections_app.core.db.connection import create_connection
from collections_app.core.models.ocr_detection import (
    OcrDetection,
    OcrParseError,
)
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import OcrModelError

if TYPE_CHECKING:
    from collections_app.core.models.card import Card


# Confianza mínima que YOLO debe reportar para considerar una detección.
# Igual que el detector standalone del usuario.
_YOLO_CONF_THRESHOLD = 0.4
# Padding (pixeles) alrededor del bbox antes del crop. Mejora la lectura
# de EasyOCR — el bbox de YOLO suele recortar muy ajustado al texto.
_CROP_PADDING = 4


class OcrService:
    """Pipeline YOLO + EasyOCR + validador dinámico."""

    @staticmethod
    def is_available() -> bool:
        """¿Están instaladas las 4 dependencias del pipeline OCR?

        Pipeline: YOLO (torch + ultralytics) → crop (cv2) → EasyOCR
        (easyocr, que internamente usa torch). Si falta cualquiera de
        las 4 piezas el flow no funciona, así que devolvemos `False`.

        Se llama desde la UI ANTES de instanciar el service para decidir
        el estado de la tab. Hace los imports adentro para que un módulo
        que importe `OcrService` no arrastre torch al cargar.
        """
        try:
            import cv2  # noqa: F401, PLC0415
            import easyocr  # noqa: F401, PLC0415
            import torch  # noqa: F401, PLC0415
            import ultralytics  # noqa: F401, PLC0415
        except ImportError:
            return False
        return True

    def __init__(self: OcrService, model_path: Path) -> None:
        if not model_path.is_file():
            raise OcrModelError(
                f"el modelo OCR no existe en {model_path}. "
                "Pedile al administrador que lo configure."
            )
        try:
            from ultralytics import YOLO  # noqa: PLC0415
        except ImportError as exc:
            raise OcrModelError(
                "las dependencias de OCR (torch, ultralytics) no están "
                "instaladas. Instalalas desde la tab de OCR."
            ) from exc
        try:
            self._model = YOLO(str(model_path))
        except Exception as exc:  # noqa: BLE001 — versión incompatible, etc.
            raise OcrModelError(f"no se pudo cargar el modelo {model_path.name}: {exc}") from exc
        self._model_path = model_path

    def run_inference(
        self: OcrService,
        image_path: Path,
        *,
        db_path: str,
        collection_id: int,
    ) -> tuple[list[OcrDetection], list[OcrParseError]]:
        """Corre el pipeline completo sobre `image_path`.

        Pasos:
        1. cv2.imread carga la imagen.
        2. YOLO devuelve bounding boxes con su confianza.
        3. Para cada bbox: crop con padding → EasyOCR lee texto crudo.
        4. El validador (construido desde la DB en `build_validator`)
           lo convierte en código canónico `"XXX N"` o `None`.
        5. Cada `"XXX N"` se resuelve contra el catálogo local de
           cards. Si la card existe, `card_id` y `card_name` se
           rellenan; si no, queda con `card_id=None` y `card_name=""`
           (la UI muestra warning).
        6. Lecturas que el validador rechaza se reportan como
           `OcrParseError` para que el user las vea como detección no
           reconocida.

        Args:
            image_path: foto a procesar.
            db_path: ruta a la DB de la app. El service abre su propia
                conn (SQLite no permite conn cross-thread).
            collection_id: collection contra la que validar/resolver.

        Returns:
            `(detections, parse_errors)`.
        """
        import cv2  # noqa: PLC0415

        from collections_app.services.ocr_reader import leer_badge  # noqa: PLC0415
        from collections_app.services.ocr_validator import build_validator  # noqa: PLC0415

        img = cv2.imread(str(image_path))
        if img is None:
            raise OcrModelError(f"no se pudo leer la imagen: {image_path}")

        # `create_connection` configura `row_factory=sqlite3.Row` y los
        # PRAGMA del proyecto. Igual queda en este hilo del worker, no
        # se comparte con el hilo principal.
        conn = create_connection(db_path)
        try:
            collection = CollectionsRepository(conn).get_by_id(collection_id)
            if collection is None:
                raise OcrModelError(f"collection_id={collection_id} no existe en esta DB")

            validator = build_validator(collection_id, conn)

            cards_repo = CardsRepository(conn)
            cards_index: dict[tuple[str, int], Card] = {
                (c.code_id, c.card_number): c
                for c in cards_repo.list_by_collection(collection_id)
                if c.card_id is not None
            }

            yolo_results = self._model(img, conf=_YOLO_CONF_THRESHOLD, verbose=False)

            detections: list[OcrDetection] = []
            errors: list[OcrParseError] = []
            h_img, w_img = img.shape[:2]

            for result in yolo_results:
                boxes = getattr(result, "boxes", None)
                if boxes is None:
                    continue
                for box in boxes:
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = xyxy
                    # Padding clamped a la imagen.
                    x1 = max(0, x1 - _CROP_PADDING)
                    y1 = max(0, y1 - _CROP_PADDING)
                    x2 = min(w_img, x2 + _CROP_PADDING)
                    y2 = min(h_img, y2 + _CROP_PADDING)
                    crop = img[y1:y2, x1:x2]

                    texto_raw = leer_badge(crop)
                    codigo = validator.validar_codigo(texto_raw)

                    if codigo is None:
                        errors.append(
                            OcrParseError(
                                raw_label=texto_raw or "",
                                confidence=confidence,
                                reason="no matchea ningún código válido",
                            )
                        )
                        continue

                    # `validar_codigo` siempre devuelve "CODE NUMBER" cuando no
                    # es None. Defensivo: si el formato cambia, no crashear.
                    parts = codigo.split(" ", 1)
                    if len(parts) != 2 or not parts[1].isdigit():
                        errors.append(
                            OcrParseError(
                                raw_label=texto_raw or "",
                                confidence=confidence,
                                reason=f"formato inesperado del validador: {codigo!r}",
                            )
                        )
                        continue
                    code_id = parts[0]
                    card_number = int(parts[1])

                    card = cards_index.get((code_id, card_number))
                    detections.append(
                        OcrDetection(
                            raw_label=codigo,
                            code_id=code_id,
                            card_number=card_number,
                            confidence=confidence,
                            card_name=card.card_name if card else "",
                            card_id=card.card_id if card else None,
                        )
                    )

            return detections, errors
        finally:
            conn.close()
