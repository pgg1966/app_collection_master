"""Conversión de fotos a sketch B&W usando OpenCV.

Pipeline (Nivel 4 — Line Art):
  cargar → detectar cara → recortar con margen amplio → limpiar fondo
  (blur fuera de la cara) → bilateral filter + dodge blend con kernel
  grande + threshold → erode (=engrosar líneas) → resize.

Resultado: líneas negras limpias sobre fondo blanco puro, estilo retrato
a lápiz fino. El threshold final fuerza el fondo a 255 (blanco) y borra
los grises medios que generaban ruido en el Nivel 3.

La detección usa Haar Cascade frontalface (viene con `opencv-python`).
Si no detecta cara, se procesa la imagen completa.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Tamaño objetivo para el slot de la card
DEFAULT_TARGET_W = 260
DEFAULT_TARGET_H = 310

# Márgenes generosos sobre la cara detectada para que el sketch parezca
# una "figurita" (incluye cabello, hombros, cuello).
TOP_MARGIN_RATIO = 0.60  # +60% arriba
SIDE_MARGIN_RATIO = 0.30  # +30% a cada lado
BOTTOM_MARGIN_RATIO = 0.40  # +40% abajo

# Parámetros del Nivel 4 (Line Art)
SKETCH_BLUR_KERNEL = 111  # impar; más grande = líneas más suaves
SKETCH_THRESHOLD = 215  # mayor = fondo más blanco, menos grises
SKETCH_LINE_THICKNESS = 1  # 0 = no engrosar; 1 = engrosar 1 iteración


class SketchGenerator:
    """Convierte fotos a sketch artístico B&W con limpieza de fondo."""

    def __init__(self) -> None:
        cascade_path = (
            cv2.data.haarcascades  # type: ignore[attr-defined]
            + "haarcascade_frontalface_default.xml"
        )
        self._face_cascade = cv2.CascadeClassifier(cascade_path)
        if self._face_cascade.empty():
            logger.warning("Haar cascade vacío en %s", cascade_path)

    def generate_sketch(self, image_path: Path) -> np.ndarray:
        """Pipeline end-to-end (Nivel 4 Line Art)."""
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning("No se pudo cargar imagen: %s", image_path)
            return np.full((DEFAULT_TARGET_H, DEFAULT_TARGET_W), 255, dtype=np.uint8)

        cropped = self._detect_and_crop_face(img)
        cleaned = self._clean_background(cropped)
        sketch = self._apply_sketch_level4(cleaned)
        return self._resize_for_card(sketch)

    # ------------------------------------------------------------------
    # Face detection y crop
    # ------------------------------------------------------------------

    def _detect_and_crop_face(self, img: np.ndarray) -> np.ndarray:
        """Detecta la cara más grande y recorta con márgenes generosos."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        if len(faces) == 0:
            return img

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        h_img, w_img = img.shape[:2]
        x0 = max(0, int(x - SIDE_MARGIN_RATIO * w))
        x1 = min(w_img, int(x + w + SIDE_MARGIN_RATIO * w))
        y0 = max(0, int(y - TOP_MARGIN_RATIO * h))
        y1 = min(h_img, int(y + h + BOTTOM_MARGIN_RATIO * h))
        return img[y0:y1, x0:x1]

    # ------------------------------------------------------------------
    # Background cleanup
    # ------------------------------------------------------------------

    def _clean_background(self, img: np.ndarray) -> np.ndarray:
        """Suaviza el fondo para que no genere ruido en el sketch.

        Si detecta cara: blur fuerte fuera de una elipse alrededor de la
        cara, blend suave en los bordes.
        Si no detecta cara: blur en los bordes asumiendo que el sujeto
        está al centro.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50)
        )
        h_img, w_img = img.shape[:2]

        if len(faces) == 0:
            mask = np.zeros((h_img, w_img), dtype=np.uint8)
            cv2.ellipse(
                mask,
                (w_img // 2, h_img // 2),
                (max(1, w_img // 3), max(1, h_img // 2)),
                0,
                0,
                360,
                255,
                -1,
            )
        else:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            margin_x = int(w * 0.4)
            margin_y_top = int(h * 0.7)
            margin_y_bot = int(h * 0.5)
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y_top)
            x2 = min(w_img, x + w + margin_x)
            y2 = min(h_img, y + h + margin_y_bot)
            mask = np.zeros((h_img, w_img), dtype=np.uint8)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            axes = (max(1, (x2 - x1) // 2), max(1, (y2 - y1) // 2))
            cv2.ellipse(mask, (cx, cy), axes, 0, 0, 360, 255, -1)

        # Difumina los bordes de la máscara para un blend suave
        mask_blurred = cv2.GaussianBlur(mask, (61, 61), 0)
        mask_3ch = cv2.merge([mask_blurred, mask_blurred, mask_blurred]).astype(np.float32) / 255.0

        blurred = cv2.GaussianBlur(img, (51, 51), 0)
        out: np.ndarray = (img * mask_3ch + blurred * (1 - mask_3ch)).astype(np.uint8)
        return out

    # ------------------------------------------------------------------
    # Sketch nivel 4 (Line Art)
    # ------------------------------------------------------------------

    def _apply_sketch_level4(self, img: np.ndarray) -> np.ndarray:
        """Line Art: líneas negras limpias sobre fondo blanco puro.

        Pipeline:
        1. Bilateral filter para suavizar preservando bordes.
        2. Dodge blend con GaussianBlur de kernel grande (más natural).
        3. Threshold binario para forzar fondo blanco puro.
        4. Erode opcional para engrosar las líneas (en imagen invertida
           sería dilate; sobre la imagen blanca, erode achica los blancos
           y por ende engrosa las líneas negras).
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Suavizar preservando bordes
        smoothed = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # Dodge blend con blur grande
        inv = cv2.bitwise_not(smoothed)
        kernel = SKETCH_BLUR_KERNEL
        if kernel % 2 == 0:  # OpenCV exige kernel impar
            kernel += 1
        blur = cv2.GaussianBlur(inv, (kernel, kernel), 0)
        sketch = cv2.divide(smoothed, cv2.bitwise_not(blur), scale=256.0)

        # Threshold para forzar fondo blanco puro (limpia los grises medios)
        _, clean = cv2.threshold(sketch, SKETCH_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Engrosar las líneas negras (erode sobre fondo blanco)
        if SKETCH_LINE_THICKNESS > 0:
            line_kernel = np.ones((2, 2), np.uint8)
            clean = cv2.erode(clean, line_kernel, iterations=SKETCH_LINE_THICKNESS)

        return clean

    # ------------------------------------------------------------------
    # Resize final
    # ------------------------------------------------------------------

    def _resize_for_card(
        self,
        sketch: np.ndarray,
        target_w: int = DEFAULT_TARGET_W,
        target_h: int = DEFAULT_TARGET_H,
    ) -> np.ndarray:
        """Escala manteniendo aspect ratio y rellena con blanco puro."""
        h, w = sketch.shape[:2]
        if h == 0 or w == 0:
            return np.full((target_h, target_w), 255, dtype=np.uint8)

        scale = min(target_w / w, target_h / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = cv2.resize(sketch, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = np.full((target_h, target_w), 255, dtype=np.uint8)
        x0 = (target_w - new_w) // 2
        y0 = (target_h - new_h) // 2
        canvas[y0 : y0 + new_h, x0 : x0 + new_w] = resized
        return canvas
