"""Conversión de fotos a sketch B&W usando OpenCV.

Pipeline:
  cargar → detectar cara → recortar con margen amplio → limpiar fondo
  (blur fuera de la cara) → preprocesar (upscale + CLAHE + bilateral)
  → sketch tipo lápiz (edge-preserving + dodge blend + Canny suave)
  → ajuste adaptativo de brillo → resize.

Salida: sketch en escala de grises con líneas suaves y mucha área
clara, pensado para imprimir bien sobre el slot de la card.

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

# Umbral mínimo de tamaño bajo el cual hacemos upscale por interpolación
# cúbica antes de aplicar el sketch (las imágenes chicas pierden detalle).
MIN_PREPROCESS_DIM = 300


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
        """Pipeline end-to-end."""
        img = cv2.imread(str(image_path))
        if img is None:
            logger.warning("No se pudo cargar imagen: %s", image_path)
            return np.full((DEFAULT_TARGET_H, DEFAULT_TARGET_W), 255, dtype=np.uint8)

        cropped = self._detect_and_crop_face(img)
        cleaned = self._clean_background(cropped)
        sketch = self._apply_sketch_level3(cleaned)
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
    # Preprocesamiento previo al sketch
    # ------------------------------------------------------------------

    def _preprocess_photo(self, img: np.ndarray) -> np.ndarray:
        """Upscale + CLAHE + bilateral, para mejorar el resultado del sketch.

        - Si la imagen es chica (< MIN_PREPROCESS_DIM), se upscalea con
          interpolación cúbica para que el sketch tenga más detalle.
        - CLAHE en el canal L de LAB sube el contraste local sin
          saturar.
        - Bilateral filter reduce ruido preservando bordes.
        """
        h, w = img.shape[:2]
        if h < MIN_PREPROCESS_DIM or w < MIN_PREPROCESS_DIM:
            scale = max(MIN_PREPROCESS_DIM / max(h, 1), MIN_PREPROCESS_DIM / max(w, 1))
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_chan = clahe.apply(l_chan)
        img = cv2.cvtColor(cv2.merge([l_chan, a_chan, b_chan]), cv2.COLOR_LAB2BGR)

        return cv2.bilateralFilter(img, 9, 75, 75)

    # ------------------------------------------------------------------
    # Sketch tipo lápiz con bordes Canny suaves y brillo adaptativo
    # ------------------------------------------------------------------

    def _apply_sketch_level3(self, img: np.ndarray) -> np.ndarray:
        """Sketch tipo lápiz: trazos suaves sobre fondo claro.

        1. Preprocesar (upscale + CLAHE + bilateral).
        2. `edgePreservingFilter` de OpenCV para suavizar manteniendo bordes.
        3. Dodge blend (`gray / inv_blur`) para el sketch base.
        4. Canny suave (umbrales bajos) para reforzar bordes sin
           sobrecargar.
        5. GaussianBlur final para que las líneas no queden duras.
        6. Si el resultado quedó oscuro (mean < 180), aclarar con
           `convertScaleAbs` (alpha=1.2, beta=20).
        """
        img = self._preprocess_photo(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge-preserving sobre la imagen color, después gris
        smooth = cv2.edgePreservingFilter(img, flags=1, sigma_s=45, sigma_r=0.35)
        smooth_gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)

        # Dodge blend (sketch base estilo lápiz)
        inv = cv2.bitwise_not(smooth_gray)
        blur = cv2.GaussianBlur(inv, (17, 17), 0)
        sketch = cv2.divide(smooth_gray, cv2.bitwise_not(blur), scale=256.0)

        # Bordes suaves con Canny (umbrales bajos = más bordes pero finos)
        edges = cv2.Canny(gray, 20, 80)
        edges = cv2.dilate(edges, np.ones((1, 1), np.uint8))

        # Aplicar bordes: oscurece sólo donde Canny detectó borde
        signed = sketch.copy().astype(np.int16)
        signed[edges > 0] = np.clip(signed[edges > 0] - 40, 0, 255)
        result: np.ndarray = signed.astype(np.uint8)

        # Suavizado final para suavizar líneas (kernel chico)
        result = cv2.GaussianBlur(result, (5, 5), 0)

        # Brillo adaptativo: si el sketch quedó oscuro, levantarlo
        if float(result.mean()) < 180:
            result = cv2.convertScaleAbs(result, alpha=1.2, beta=20)

        return np.clip(result, 0, 255).astype(np.uint8)

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
