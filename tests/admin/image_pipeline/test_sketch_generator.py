"""Tests del SketchGenerator."""

from pathlib import Path

import cv2
import numpy as np
import pytest

from collections_app.admin.image_pipeline.sketch_generator import (
    DEFAULT_TARGET_H,
    DEFAULT_TARGET_W,
    SketchGenerator,
)


def _save_synthetic_image(path: Path, w: int = 400, h: int = 500) -> None:
    """Imagen sintética: gradiente con un círculo (no es una cara real)."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        img[y, :, :] = (200 - y // 5, 200 - y // 5, 200 - y // 5)
    cv2.circle(img, (w // 2, h // 2), 80, (50, 50, 50), -1)
    cv2.imwrite(str(path), img)


@pytest.fixture
def generator() -> SketchGenerator:
    return SketchGenerator()


def test_sketch_returns_grayscale_array(tmp_path, generator):
    img_path = tmp_path / "input.jpg"
    _save_synthetic_image(img_path)
    sketch = generator.generate_sketch(img_path)
    assert sketch.ndim == 2  # grayscale (sin canales)


def test_sketch_preserves_card_dimensions(tmp_path, generator):
    img_path = tmp_path / "input.jpg"
    _save_synthetic_image(img_path, w=300, h=400)
    sketch = generator.generate_sketch(img_path)
    assert sketch.shape == (DEFAULT_TARGET_H, DEFAULT_TARGET_W)


def test_face_detection_fallback_when_no_face(tmp_path, generator):
    """Imagen sin cara → se procesa la imagen completa, no falla."""
    img_path = tmp_path / "noface.jpg"
    _save_synthetic_image(img_path)
    sketch = generator.generate_sketch(img_path)
    assert sketch.shape == (DEFAULT_TARGET_H, DEFAULT_TARGET_W)
    # No es una imagen uniforme (procesó algo)
    assert sketch.std() > 1


def test_output_is_uint8(tmp_path, generator):
    img_path = tmp_path / "input.jpg"
    _save_synthetic_image(img_path)
    sketch = generator.generate_sketch(img_path)
    assert sketch.dtype == np.uint8


def test_resize_for_card_correct_dimensions(generator):
    """El resize directo respeta target_w/target_h."""
    arr = np.full((100, 100), 200, dtype=np.uint8)
    out = generator._resize_for_card(arr, target_w=50, target_h=80)
    assert out.shape == (80, 50)


def test_handles_very_small_input(tmp_path, generator):
    """Una imagen 60x60 chica no debería romper, debe escalarse."""
    img_path = tmp_path / "tiny.jpg"
    arr = np.full((60, 60, 3), 100, dtype=np.uint8)
    cv2.imwrite(str(img_path), arr)
    sketch = generator.generate_sketch(img_path)
    assert sketch.shape == (DEFAULT_TARGET_H, DEFAULT_TARGET_W)


def test_missing_image_returns_uniform_canvas(tmp_path, generator):
    """Si el archivo no existe, retorna canvas uniforme sin crashear."""
    sketch = generator.generate_sketch(tmp_path / "nope.jpg")
    assert sketch.shape == (DEFAULT_TARGET_H, DEFAULT_TARGET_W)


def test_resize_handles_zero_dimensions(generator):
    """Edge case defensivo: arrays de tamaño cero."""
    arr = np.zeros((0, 0), dtype=np.uint8)
    out = generator._resize_for_card(arr)
    assert out.shape == (DEFAULT_TARGET_H, DEFAULT_TARGET_W)


# ----------------------------------------------------------------------
# Mejoras: limpieza de fondo + CLAHE + crop generoso
# ----------------------------------------------------------------------


def test_clean_background_returns_same_shape(generator):
    """`_clean_background` no cambia las dimensiones de la imagen."""
    img = np.full((400, 300, 3), 100, dtype=np.uint8)
    out = generator._clean_background(img)
    assert out.shape == img.shape
    assert out.dtype == np.uint8


def test_clean_background_blurs_outside_center(generator):
    """En las regiones de los bordes la varianza disminuye tras la limpieza."""
    img = np.full((400, 300, 3), 128, dtype=np.uint8)
    rng = np.random.default_rng(42)
    img[:50, :, :] = rng.integers(0, 256, size=(50, 300, 3), dtype=np.uint8)
    img[-50:, :, :] = rng.integers(0, 256, size=(50, 300, 3), dtype=np.uint8)

    out = generator._clean_background(img)
    border_in = img[:50, :, :].std()
    border_out = out[:50, :, :].std()
    assert border_out < border_in


def test_pipeline_calls_clean_background(generator, tmp_path):
    """`generate_sketch` invoca `_clean_background` en el flow."""
    from unittest.mock import patch

    img_path = tmp_path / "input.jpg"
    arr = np.full((500, 400, 3), 150, dtype=np.uint8)
    cv2.imwrite(str(img_path), arr)
    with patch.object(generator, "_clean_background", wraps=generator._clean_background) as cb:
        generator.generate_sketch(img_path)
    assert cb.call_count == 1


def test_crop_uses_generous_margins():
    """Los márgenes del crop son generosos (≥30% lados, ≥60% arriba, ≥40% abajo)."""
    from collections_app.admin.image_pipeline import sketch_generator as sg

    assert sg.SIDE_MARGIN_RATIO >= 0.30
    assert sg.TOP_MARGIN_RATIO >= 0.60
    assert sg.BOTTOM_MARGIN_RATIO >= 0.40


# ----------------------------------------------------------------------
# Sketch Nivel 4 (Line Art)
# ----------------------------------------------------------------------


def test_level4_output_has_mostly_white_background(tmp_path, generator):
    """El output de Nivel 4 tiene >60% de píxeles blancos (fondo limpio)."""
    img_path = tmp_path / "input.jpg"
    _save_synthetic_image(img_path, w=400, h=500)
    sketch = generator.generate_sketch(img_path)
    white_pct = float(np.mean(sketch == 255))
    assert white_pct > 0.60, f"Esperado >60% blanco, fue {white_pct:.2%}"


def test_level4_output_has_clean_black_lines(tmp_path, generator):
    """El threshold binario produce solo dos valores: 0 (negro) y 255 (blanco)."""
    img_path = tmp_path / "input.jpg"
    _save_synthetic_image(img_path, w=400, h=500)
    sketch = generator.generate_sketch(img_path)
    unique_values = set(np.unique(sketch).tolist())
    # Tras threshold binario y resize con INTER_AREA puede haber un par de
    # valores intermedios en los bordes del resize, pero la enorme mayoría
    # debe ser puro 0 o puro 255.
    pure_pixels = float(np.mean((sketch == 0) | (sketch == 255)))
    assert pure_pixels > 0.95, (
        f"Esperado >95% píxeles puros (0 o 255), fue {pure_pixels:.2%}; "
        f"valores únicos: {sorted(unique_values)[:10]}"
    )


def test_level4_parameters_are_configurable():
    """Los parámetros del Nivel 4 son constantes editables del módulo."""
    from collections_app.admin.image_pipeline import sketch_generator as sg

    # Kernel impar y razonablemente grande
    assert sg.SKETCH_BLUR_KERNEL >= 51
    assert sg.SKETCH_BLUR_KERNEL % 2 == 1
    # Threshold cerca de 255 para fondo limpio
    assert 180 <= sg.SKETCH_THRESHOLD <= 245
    # Engrosado configurable y no negativo
    assert sg.SKETCH_LINE_THICKNESS >= 0


def test_level4_apply_directly_on_blank_image(generator):
    """Una imagen blanca da un sketch totalmente blanco."""
    blank = np.full((200, 200, 3), 240, dtype=np.uint8)
    out = generator._apply_sketch_level4(blank)
    assert out.shape == (200, 200)
    # Imagen plana → sin líneas → todo blanco
    assert float(np.mean(out == 255)) > 0.95
