"""Modelo CardImage: tracking de imágenes generadas por card."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CardImage:
    """Registro de la imagen generada para una card.

    Una card tiene exactamente una entrada en `card_images` (PK compuesta
    igual que `cards`). Si todavía no se procesó, no aparece — usar el
    repo `get_pending(collection_id)` para listar las cards sin imagen.

    Attributes:
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG").
        card_number: número correlativo dentro del code_id.
        found_photo: True si la imagen final usa una foto real,
            False si quedó como placeholder.
        image_source: fuente de la imagen ("wikipedia", "duckduckgo",
            "google", "placeholder", "cache") o None si no se sabe.
        image_path: path al PNG generado, o None si no se grabó.
        generated_at: ISO datetime UTC de la generación, o None.
    """

    collection_id: int
    code_id: str
    card_number: int
    found_photo: bool
    image_source: str | None = None
    image_path: str | None = None
    generated_at: str | None = None
