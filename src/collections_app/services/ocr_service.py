"""Service de reconocimiento óptico de cards (Sesión 5d).

Carga un modelo YOLO entrenado para una colección, corre inferencia
sobre fotos, parsea cada label y resuelve cada detección contra el
catálogo de cards de la colección.

**Imports lazy (regla crítica del prompt 5d):** ningún import de
`torch` o `ultralytics` aparece a nivel de módulo. Solo dentro de los
métodos que efectivamente los necesitan, marcados con `noqa: PLC0415`.
Esto permite que la app arranque sin esas dependencias y muestre el
Estado 1 (instalación) en la tab de OCR.

`is_available()` es un staticmethod que se puede llamar sin instanciar
el service: el caller la usa para decidir el estado de la UI antes de
intentar construir un `OcrService`.

`run_inference` retorna una tupla `(detections, parse_errors)` para
que la UI pueda mostrar tanto las cards reconocidas como los labels
que no pudieron parsearse, sin que estos últimos rompan el flow.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING

from collections_app.core.models.ocr_detection import (
    OcrDetection,
    OcrParseError,
    parse_label,
)
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import OcrModelError

if TYPE_CHECKING:
    from collections_app.core.models.card import Card


class OcrService:
    """Inferencia YOLO + resolución contra el catálogo local."""

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
        except Exception as exc:  # noqa: BLE001 — versión incompatible, archivo corrupto, etc.
            raise OcrModelError(f"no se pudo cargar el modelo {model_path.name}: {exc}") from exc
        self._model_path = model_path

    def run_inference(
        self: OcrService,
        image_path: Path,
        *,
        conn: sqlite3.Connection,
        collection_id: int,
    ) -> tuple[list[OcrDetection], list[OcrParseError]]:
        """Corre YOLO sobre `image_path` y resuelve cada label.

        Args:
            image_path: foto a procesar.
            conn: conexión SQLite usada para resolver `card_id` /
                `card_name` contra el catálogo local.
            collection_id: collection sobre la que resolver. Determina
                también el flag `requires_code` que rige el parser.

        Returns:
            Tupla `(detections, parse_errors)`:

            - `detections`: cada label parseable se devuelve como
              `OcrDetection`, con `card_id` y `card_name` resueltos
              contra la DB (o `None` / `""` si no matcheó nada local).
            - `parse_errors`: cada label no parseable se devuelve como
              `OcrParseError` con el `reason` correspondiente.
        """
        collections_repo = CollectionsRepository(conn)
        collection = collections_repo.get_by_id(collection_id)
        if collection is None:
            raise OcrModelError(f"collection_id={collection_id} no existe en esta DB")

        cards_repo = CardsRepository(conn)
        cards_index: dict[tuple[str, int], Card] = {
            (c.code_id, c.card_number): c
            for c in cards_repo.list_by_collection(collection_id)
            if c.card_id is not None
        }

        detections: list[OcrDetection] = []
        errors: list[OcrParseError] = []

        for raw_label, confidence in self._raw_inference(image_path):
            parsed = parse_label(raw_label, requires_code=collection.requires_code)
            if parsed is None:
                errors.append(
                    OcrParseError(
                        raw_label=raw_label,
                        confidence=confidence,
                        reason=(
                            "formato no reconocido"
                            if not collection.requires_code or "-" in raw_label
                            else "falta código"
                        ),
                    )
                )
                continue
            code_id, card_number = parsed
            # Resolución contra el catálogo. Si no matchea (ej. card del
            # álbum equivocado), se incluye igual con card_id=None y
            # card_name="" para que la UI pueda mostrarlo como warning.
            card = cards_index.get((code_id, card_number))
            detections.append(
                OcrDetection(
                    raw_label=raw_label,
                    code_id=code_id,
                    card_number=card_number,
                    confidence=confidence,
                    card_name=card.card_name if card else "",
                    card_id=card.card_id if card else None,
                )
            )

        return detections, errors

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _raw_inference(self: OcrService, image_path: Path) -> list[tuple[str, float]]:
        """Corre YOLO y devuelve `[(label, confidence), ...]`.

        Aislado en su propio método para que los tests puedan
        mockearlo sin cargar torch.
        """
        results = self._model(str(image_path))
        out: list[tuple[str, float]] = []
        for result in results:
            boxes = getattr(result, "boxes", None)
            names = getattr(result, "names", None)
            if boxes is None or names is None:
                continue
            for cls_tensor, conf_tensor in zip(boxes.cls, boxes.conf, strict=True):
                cls_idx = int(cls_tensor.item())
                conf = float(conf_tensor.item())
                label = str(names.get(cls_idx, "") if isinstance(names, dict) else names[cls_idx])
                out.append((label, conf))
        return out
