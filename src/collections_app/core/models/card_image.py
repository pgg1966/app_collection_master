"""Modelo CardImage: tracking de imágenes generadas por card."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CardImage:
    """Registro de la imagen generada para una card.

    PK subrogada `card_image_id`; UNIQUE sobre `card_id` (1:1 con cards).
    Si una card todavía no tiene imagen procesada, no aparece — usar
    `CardImagesRepository.get_pending(collection_id)` para listar las
    cards sin imagen.

    Esta tabla es la **única fuente** del path de imagen (sec 6 prohíbe
    duplicar el dato en `inventory`).

    Attributes:
        card_image_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card asociada (UNIQUE).
        found_photo: True si la imagen final usa una foto real,
            False si quedó como placeholder.
        image_source: fuente ("wikipedia", "duckduckgo", "google",
            "placeholder", "cache") o None si no se sabe.
        image_path: path al PNG generado, o None si no se grabó.
        generated_at: ISO datetime UTC de la generación, o None.
    """

    card_image_id: int | None
    card_id: int
    found_photo: bool
    image_source: str | None = None
    image_path: str | None = None
    generated_at: str | None = None
