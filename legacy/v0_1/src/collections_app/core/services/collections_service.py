"""Servicio que orquesta operaciones que cruzan collections + codes_headers + cards."""

import sqlite3
from typing import Any

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CodesLinesRepository,
    CollectionsRepository,
)


class CollectionsService:
    """Operaciones de alto nivel sobre `collections`."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._collections = CollectionsRepository(conn)
        self._headers = CodesHeadersRepository(conn)
        self._lines = CodesLinesRepository(conn)
        self._cards = CardsRepository(conn)

    def create_collection_with_validation(self, collection: Collection) -> Collection:
        """Crea una colección validando que el code_header_id exista.

        Raises:
            ValueError: si el `code_header_id` no apunta a un header existente.
        """
        if self._headers.get_by_id(collection.code_header_id) is None:
            raise ValueError(f"code_header_id {collection.code_header_id} no existe")
        return self._collections.create(collection)

    def get_full_collection_info(self, collection_id: int) -> dict[str, Any] | None:
        """Retorna info enriquecida de una colección.

        Returns:
            Dict con `collection`, `code_header`, `num_cards`, `num_codes`,
            o None si la colección no existe.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return None

        header = self._headers.get_by_id(collection.code_header_id)
        num_cards = self._cards.count_by_collection(collection_id)
        num_codes = len(self._lines.list_codes_only(collection.code_header_id))

        return {
            "collection": collection,
            "code_header": header,
            "num_cards": num_cards,
            "num_codes": num_codes,
        }

    def can_be_deleted(self, collection_id: int) -> tuple[bool, str]:
        """Indica si una colección puede borrarse.

        Por ahora siempre permite (el cascade borra cards e inventory).
        Más adelante podemos prohibir si está activa, etc.

        Returns:
            (puede_borrarse, razón_si_no).
        """
        if self._collections.get_by_id(collection_id) is None:
            return False, f"La colección {collection_id} no existe"
        return True, ""
