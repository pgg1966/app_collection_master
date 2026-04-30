"""Tests del CardComposer."""

import numpy as np
import pytest
from PIL import Image

from collections_app.admin.image_pipeline.card_composer import (
    BADGE_BG,
    BORDER_COLOR,
    CARD_H,
    CARD_W,
    MISSING_BG,
    OWNED_BG,
    CardComposer,
)


def _fake_sketch(w: int = 260, h: int = 310) -> np.ndarray:
    return np.full((h, w), 200, dtype=np.uint8)


@pytest.fixture
def composer() -> CardComposer:
    return CardComposer()


def test_compose_owned_has_blue_background(composer):
    card = composer.compose(_fake_sketch(), 24, "LIONEL MESSI", "ARGENTINA", owned=True)
    # Pixel cerca del centro arriba (zona del fondo, antes del sketch)
    assert card.getpixel((140, 5)) == OWNED_BG


def test_compose_missing_has_gray_background(composer):
    card = composer.compose(_fake_sketch(), 24, "LIONEL MESSI", "ARGENTINA", owned=False)
    assert card.getpixel((140, 5)) == MISSING_BG


def test_compose_truncates_long_name(composer):
    """Nombres largos no deben romper el composer (se truncan internamente)."""
    long_name = "A" * 50
    # No tiene que crashear
    card = composer.compose(_fake_sketch(), 1, long_name, "X", owned=True)
    assert card.size == (CARD_W, CARD_H)


def test_compose_badge_shows_extra_count(composer):
    """El badge dibuja un círculo rojo en la esquina superior derecha."""
    card = composer.compose_with_duplicate_badge(_fake_sketch(), 24, "MESSI", "ARG", extra_copies=3)
    # Pixel dentro del círculo (esquina sup-der, ~30 px del borde)
    badge_pixel = card.getpixel((CARD_W - 30, 30))
    assert badge_pixel == BADGE_BG


def test_no_badge_when_extra_zero(composer):
    """Sin extra copies, no se dibuja badge (mantiene fondo)."""
    card = composer.compose_with_duplicate_badge(_fake_sketch(), 1, "X", "X", extra_copies=0)
    badge_pixel = card.getpixel((CARD_W - 30, 30))
    # No es rojo
    assert badge_pixel != BADGE_BG


def test_output_is_pil_image_correct_size(composer):
    card = composer.compose(_fake_sketch(), 1, "X", "Y", owned=True)
    assert isinstance(card, Image.Image)
    assert card.size == (CARD_W, CARD_H)


def test_save_creates_png_file(composer, tmp_path):
    out = tmp_path / "card.png"
    card = composer.compose(_fake_sketch(), 1, "X", "Y", owned=True)
    composer.save(card, out)
    assert out.exists()
    # Es un PNG válido
    reopened = Image.open(out)
    assert reopened.format == "PNG"
    assert reopened.size == (CARD_W, CARD_H)


def test_border_drawn_on_edge(composer):
    """El marco gris está en los bordes."""
    card = composer.compose(_fake_sketch(), 1, "X", "Y", owned=True)
    # pixel (0, 0) debería ser BORDER_COLOR
    assert card.getpixel((0, 0)) == BORDER_COLOR


def test_save_creates_parent_dir(composer, tmp_path):
    """save() crea el directorio padre si no existe."""
    out = tmp_path / "nested" / "dir" / "card.png"
    card = composer.compose(_fake_sketch(), 1, "X", "Y", owned=True)
    composer.save(card, out)
    assert out.exists()
