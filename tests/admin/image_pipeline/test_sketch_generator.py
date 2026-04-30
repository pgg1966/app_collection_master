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
