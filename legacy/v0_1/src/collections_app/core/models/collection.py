"""Modelo Collection: una colección configurada de cards."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Collection:
    """Representa una colección a juntar (catálogo de cards).

    Attributes:
        collection_id: PK auto-incremental. None si aún no fue persistido.
        collection_name: nombre único de la colección.
        card_count: cantidad total esperada de cards.
        requires_code: si True, las cards de la colección se subdividen por code_id.
        code_field_name: etiqueta visible del campo de código en la UI (ej. "Set").
        code_header_id: FK al CodeHeader que define el universo de códigos.
        is_premium: si True, requiere licencia para usar.
        license_key_required: hash de la key requerida (None si free).
        album_columns: cards por fila en el PDF álbum (default 3).
        album_rows: filas por página en el PDF álbum (default 4).
        album_orientation: 'portrait' o 'landscape' — algunas colecciones
            tienen cards horizontales y necesitan landscape (default portrait).
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
