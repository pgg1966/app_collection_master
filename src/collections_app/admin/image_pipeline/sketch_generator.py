"""Conversión de fotos a sketch B&W usando OpenCV.

Pipeline (Nivel 3):
  cargar → detectar cara → recortar con margen → edge-preserve + pencil
  dodge & burn + bordes Canny reforzados → suavizar artefactos.

La detección usa Haar Cascade frontalface por simplicidad y porque viene
empacado con `opencv-python`. Si no detecta cara, se usa la imagen
completa.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Tamaño objetivo para el slot de la card. Definido acá para evitar circular
# imports con CardComposer.
DEFAULT_TARGET_W = 260
DEFAULT_TARGET_H = 310

# Márgenes adicionales sobre la cara detectada (porcentaje del bounding box)
TOP_MARGIN_RATIO = 0.40  # +40% arriba (cabello)
SIDE_MARGIN_RATIO = 0.20  # +20% a cada lado
BOTTOM_MARGIN_RATIO = 0.10  # +10% abajo (mentón)


class SketchGenerator:
    """Convierte fotos a sketch artístico B&W usando OpenCV (Nivel 3)."""

    def __init__(self) -> None:
        # cv2.data está disponible en runtime pero no expuesto al type checker
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore[attr-defined]
        self._face_cascade = cv2.CascadeClassifier(cascade_path)
        if self._face_cascade.empty():
            logger.warning("Haar cascade vacío en %s", cascade_path)

    def generate_sketch(self, image_path: Path) -> np.ndarray:
        """Pipeline end-to-end: carga → detecta cara → recorta → sketch.

        Returns:
            Imagen numpy 2D en grayscale (uint8). Si la imagen no se puede
            cargar, retorna un array gris uniforme del tamaño objetivo.
        """
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning("No se pudo cargar imagen: %s", image_path)
            return np.full((DEFAULT_TARGET_H, DEFAULT_TARGET_W), 220, dtype=np.uint8)

        cropped = self._detect_and_crop_face(img)
        sketch = self._apply_sketch_level3(cropped)
        return self._resize_for_card(sketch)

    # ------------------------------------------------------------------
    # Face detection y crop
    # ------------------------------------------------------------------

    def _detect_and_crop_face(self, img: np.ndarray) -> np.ndarray:
        """Detecta la cara más grande y recorta con márgenes generosos.

        Si no detecta cara, retorna la imagen tal cual (el resize final la
        ajusta al slot de la card).
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        if len(faces) == 0:
            return img

        # Elegir la cara con mayor área (suele ser la del foreground)
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        h_img, w_img = img.shape[:2]
        x0 = max(0, int(x - SIDE_MARGIN_RATIO * w))
        x1 = min(w_img, int(x + w + SIDE_MARGIN_RATIO * w))
        y0 = max(0, int(y - TOP_MARGIN_RATIO * h))
        y1 = min(h_img, int(y + h + BOTTOM_MARGIN_RATIO * h))
        return img[y0:y1, x0:x1]

    # ------------------------------------------------------------------
    # Sketch nivel 3
    # ------------------------------------------------------------------

    def _apply_sketch_level3(self, img: np.ndarray) -> np.ndarray:
        """Edge-preserving + pencil dodge & burn + bordes Canny reforzados."""
        # 1. Edge-preserving filter sobre la imagen color (suaviza zonas planas
        #    sin perder bordes).
        smoothed_color = cv2.edgePreservingFilter(img, sigma_s=60, sigma_r=0.4)
        gray = cv2.cvtColor(smoothed_color, cv2.COLOR_BGR2GRAY)

        # 2. Pencil dodge & burn
        inv = cv2.bitwise_not(gray)
        blur = cv2.GaussianBlur(inv, (21, 21), 0)
        # divide produce el efecto típico de pencil sketch
        sketch = cv2.divide(gray, cv2.bitwise_not(blur), scale=256.0)

        # 3. Detección de bordes y refuerzo
        edges = cv2.Canny(gray, 30, 100)
        edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)

        # 4. Oscurecer donde hay borde (sin underflow)
        darkened = sketch.astype(np.int16)
        darkened[edges > 0] -= 60
        sketch = np.clip(darkened, 0, 255).astype(np.uint8)

        # 5. Suavizar artefactos
        return cv2.GaussianBlur(sketch, (3, 3), 0)

    # ------------------------------------------------------------------
    # Resize final
    # ------------------------------------------------------------------

    def _resize_for_card(
        self,
        sketch: np.ndarray,
        target_w: int = DEFAULT_TARGET_W,
        target_h: int = DEFAULT_TARGET_H,
    ) -> np.ndarray:
        """Escala manteniendo aspect ratio y rellena con blanco (fondo card)."""
        h, w = sketch.shape[:2]
        if h == 0 or w == 0:
            return np.full((target_h, target_w), 245, dtype=np.uint8)

        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = cv2.resize(sketch, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = np.full((target_h, target_w), 245, dtype=np.uint8)
        x0 = (target_w - new_w) // 2
        y0 = (target_h - new_h) // 2
        canvas[y0 : y0 + new_h, x0 : x0 + new_w] = resized
        return canvas
