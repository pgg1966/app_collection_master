"""Service de álbum: orquesta cards + inventario + nombres de código + imágenes.

Es la capa de **datos** entre la DB y los renderers de PDF. Mantiene
`pdf_generator.py` ignorante del schema/repositorios — solo recibe
`AlbumCard` ya armadas.

Uso típico desde la vista cliente:

    from collections_app.core.services import AlbumService

    service = AlbumService(conn)
    service.generate_album_pdf(collection, output_path)
"""

import logging
import sqlite3
from pathlib import Path

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services.pdf_generator import (
    AlbumCard,
    DuplicatesReportMode,
    PdfGeneratorResult,
    generate_album_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
)
from collections_app.core.utils.paths import find_card_image

logger = logging.getLogger(__name__)


class AlbumService:
    """Carga datos del álbum desde DB y delega la generación al renderer."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Carga de datos (data layer)
    # ------------------------------------------------------------------

    def build_album_cards(self, collection: Collection) -> list[AlbumCard]:
        """Cruza cards con inventario + nombres de código + orden + imágenes.

        Ordenado por `(code_order, code_id, card_number)`: las categorías
        respetan el `CodeLine.code_order` configurado en Admin (no alfabético
        por code_id). El secundario `code_id` desempata casos de igual
        code_order. Las cards sin entrada en inventario quedan con `quantity=0`.
        """
        assert collection.collection_id is not None
        cid: int = collection.collection_id

        cards = CardsRepository(self._conn).list_by_collection(cid)
        inv = {
            (i.code_id, i.card_number): i.quantity
            for i in InventoryRepository(self._conn).list_by_collection(cid)
        }
        # Una sola lectura de codes_lines: nombre + orden por code_id.
        code_meta = self._get_code_meta(collection)

        result: list[AlbumCard] = []
        for card in cards:
            name, order = code_meta.get(card.code_id, (card.code_id, 0))
            qty = inv.get((card.code_id, card.card_number), 0)
            result.append(
                AlbumCard(
                    card=card,
                    quantity=qty,
                    image_path=find_card_image(cid, card.card_number),
                    requires_code=collection.requires_code,
                    code_name=name,
                    code_order=order,
                )
            )
        result.sort(key=lambda ac: (ac.code_order, ac.card.code_id, ac.card.card_number))
        return result

    def get_code_names(self, collection: Collection) -> dict[str, str]:
        """Mapeo `code_id → code_name` desde `codes_lines`.

        Útil para renderear headers de categoría con el nombre humano
        ("ARGENTINA") en vez del id corto ("ARG").
        """
        return {code_id: name for code_id, (name, _) in self._get_code_meta(collection).items()}

    def _get_code_meta(self, collection: Collection) -> dict[str, tuple[str, int]]:
        """Mapeo `code_id → (code_name, code_order)`. Una sola query."""
        lines = CodesLinesRepository(self._conn).list_by_header(collection.code_header_id)
        return {line.code_id: (line.code_name, line.code_order) for line in lines}

    # ------------------------------------------------------------------
    # Wrappers de generación (render layer)
    # ------------------------------------------------------------------

    def generate_album_pdf(self, collection: Collection, output_path: Path) -> PdfGeneratorResult:
        """PDF álbum visual (todas las cards, foto o placeholder)."""
        cards = self.build_album_cards(collection)
        return generate_album_pdf(collection, cards, output_path)

    def generate_missing_pdf(self, collection: Collection, output_path: Path) -> PdfGeneratorResult:
        """PDF lista de cards faltantes (`quantity == 0`)."""
        cards = self.build_album_cards(collection)
        return generate_missing_pdf(collection, cards, output_path)

    def generate_duplicates_pdf(
        self,
        collection: Collection,
        output_path: Path,
        mode: DuplicatesReportMode = DuplicatesReportMode.FULL,
    ) -> PdfGeneratorResult:
        """PDF lista de cards repetidas (`quantity > 1`)."""
        cards = self.build_album_cards(collection)
        return generate_duplicates_pdf(collection, cards, output_path, mode=mode)

    def generate_owned_pdf(self, collection: Collection, output_path: Path) -> PdfGeneratorResult:
        """PDF lista de cards en posesión (`quantity >= 1`)."""
        cards = self.build_album_cards(collection)
        return generate_owned_pdf(collection, cards, output_path)
