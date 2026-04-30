"""Composición final de la card: sketch + fondo + marco + número + nombre."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Geometría de la card
CARD_W = 280
CARD_H = 380
SKETCH_TOP = 10
LABEL_HEIGHT = 50
SEPARATOR_Y = CARD_H - LABEL_HEIGHT - 5

# Colores (RGB)
OWNED_BG = (173, 216, 230)
MISSING_BG = (245, 245, 245)
BORDER_COLOR = (80, 80, 80)
SEPARATOR_COLOR = (140, 140, 140)
NUMBER_BOX_BG = (60, 60, 60)
NUMBER_BOX_FG = (255, 255, 255)
LABEL_FG = (30, 30, 30)
BADGE_BG = (200, 60, 60)
BADGE_FG = (255, 255, 255)

# Truncado de nombre largo
MAX_NAME_CHARS = 20


class CardComposer:
    """Compone la imagen final de una card a partir del sketch B&W."""

    def __init__(self) -> None:
        # PIL fonts: usa el default que no requiere TTF instalado.
        self._font_label = ImageFont.load_default()
        self._font_number = ImageFont.load_default()
        self._font_badge = ImageFont.load_default()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def compose(
        self,
        sketch: np.ndarray,
        card_number: int,
        player_name: str,
        code_name: str,
        owned: bool,
    ) -> Image.Image:
        """Compone la card y retorna una PIL Image RGB."""
        del code_name  # reservado para variantes futuras (mostrar país en card)
        bg_color = OWNED_BG if owned else MISSING_BG
        card = Image.new("RGB", (CARD_W, CARD_H), bg_color)

        self._paste_sketch(card, sketch)
        self._draw_separator(card)
        self._draw_label(card, card_number, player_name)
        self._draw_border(card)
        return card

    def compose_with_duplicate_badge(
        self,
        sketch: np.ndarray,
        card_number: int,
        player_name: str,
        code_name: str,
        extra_copies: int,
    ) -> Image.Image:
        """Como `compose` pero con badge "x{n}" en esquina superior derecha."""
        card = self.compose(sketch, card_number, player_name, code_name, owned=True)
        if extra_copies > 0:
            self._draw_badge(card, extra_copies)
        return card

    def save(self, card_image: Image.Image, output_path: Path) -> None:
        """Guarda la card como PNG."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        card_image.save(output_path, "PNG", optimize=True)

    # ------------------------------------------------------------------
    # Helpers de dibujo
    # ------------------------------------------------------------------

    def _paste_sketch(self, card: Image.Image, sketch: np.ndarray) -> None:
        """Pega el sketch (grayscale numpy) centrado en la zona superior."""
        sketch_pil = Image.fromarray(sketch).convert("RGB")
        # Centrado horizontalmente; la zona inferior queda libre para el label
        x = (CARD_W - sketch_pil.width) // 2
        y = SKETCH_TOP
        card.paste(sketch_pil, (x, y))

    def _draw_separator(self, card: Image.Image) -> None:
        draw = ImageDraw.Draw(card)
        draw.line(
            [(10, SEPARATOR_Y), (CARD_W - 10, SEPARATOR_Y)],
            fill=SEPARATOR_COLOR,
            width=1,
        )

    def _draw_label(self, card: Image.Image, number: int, player_name: str) -> None:
        draw = ImageDraw.Draw(card)
        y_label = CARD_H - LABEL_HEIGHT + 8

        # Caja de número
        num_text = f"#{number}"
        num_x = 12
        num_w = 60
        num_h = LABEL_HEIGHT - 16
        draw.rectangle([num_x, y_label, num_x + num_w, y_label + num_h], fill=NUMBER_BOX_BG)
        # Centrar el texto en la caja
        bbox = draw.textbbox((0, 0), num_text, font=self._font_number)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (num_x + (num_w - tw) // 2, y_label + (num_h - th) // 2 - bbox[1]),
            num_text,
            fill=NUMBER_BOX_FG,
            font=self._font_number,
        )

        # Nombre truncado, en mayúsculas
        name_text = self._truncate_name(player_name)
        name_x = num_x + num_w + 10
        name_y = y_label + 4
        draw.text((name_x, name_y), name_text, fill=LABEL_FG, font=self._font_label)

    def _draw_border(self, card: Image.Image) -> None:
        draw = ImageDraw.Draw(card)
        draw.rectangle([0, 0, CARD_W - 1, CARD_H - 1], outline=BORDER_COLOR, width=2)

    def _draw_badge(self, card: Image.Image, extra_copies: int) -> None:
        """Círculo rojo en esquina superior derecha con 'x{n}' en blanco."""
        draw = ImageDraw.Draw(card)
        radius = 22
        cx = CARD_W - radius - 8
        cy = radius + 8
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=BADGE_BG)
        text = f"x{extra_copies}"
        bbox = draw.textbbox((0, 0), text, font=self._font_badge)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(
            (cx - tw // 2, cy - th // 2 - bbox[1]),
            text,
            fill=BADGE_FG,
            font=self._font_badge,
        )

    @staticmethod
    def _truncate_name(name: str) -> str:
        upper = name.upper()
        if len(upper) <= MAX_NAME_CHARS:
            return upper
        return upper[: MAX_NAME_CHARS - 1] + "…"
