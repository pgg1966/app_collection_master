"""Modelo Collection: catálogo de cards configurable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Collection:
    """Representa una colección a juntar (catálogo de cards).

    Attributes:
        collection_id: PK auto-incremental. None si aún no fue persistido.
        collection_name: nombre único de la colección.
        card_count: cantidad total esperada de cards.
        requires_code: si True, las cards se subdividen por code_id.
        code_field_name: label visible del campo de código en la UI
            (ej. "Set", "País"). Metadata de presentación; nunca se usa
            como referencia dinámica a otra columna (CLAUDE.md sec 6).
        code_header_id: FK al CodeHeader que define el universo de códigos.
        is_premium: si True, requiere licencia para usar.
        license_key_required: hash de la key requerida (None si free).
        album_columns: cards por fila en el PDF álbum (default 3).
        album_rows: filas por página en el PDF álbum (default 4).
        album_orientation: 'portrait' o 'landscape' — algunas colecciones
            tienen cards horizontales y necesitan landscape.
        ocr_model_filename: nombre del archivo del modelo YOLO entrenado
            para detectar las cards de esta colección (Sesión 5d). None
            si no hay modelo configurado. El path completo se reconstruye
            con `get_models_dir() / ocr_model_filename`.
        ocr_guide_filename: imagen de instrucciones (jpg/png/...) que el
            OcrLoaderTab muestra antes de cargar fotos (ej. cómo orientar
            el celular). None si no hay guía configurada. El path
            completo se reconstruye con
            `get_images_dir() / ocr_guide_filename`.
    """

    collection_id: int | None
    collection_name: str
    card_count: int
    requires_code: bool
    code_field_name: str | None
    code_header_id: int
    is_premium: bool = False
    license_key_required: str | None = None
    album_columns: int = 3
    album_rows: int = 4
    album_orientation: str = "portrait"
    ocr_model_filename: str | None = None
    ocr_guide_filename: str | None = None
