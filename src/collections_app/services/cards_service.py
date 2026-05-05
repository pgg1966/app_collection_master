"""Service del catálogo de cards.

Wrapper sobre `CardsRepository` con validaciones de negocio: nombre
no vacío, card_number positivo, FK a colección. Incluye también el
acceso al aggregate `CodeStats`.
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.card import Card
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import CardsError


class CardsService:
    """Lógica de negocio sobre `cards`."""

    def __init__(self: CardsService, conn: sqlite3.Connection) -> None:
        self._repo = CardsRepository(conn)
        self._collections = CollectionsRepository(conn)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def list_by_collection(self: CardsService, collection_id: int) -> list[Card]:
        return self._repo.list_by_collection(collection_id)

    def list_by_code(self: CardsService, collection_id: int, code_id: str) -> list[Card]:
        return self._repo.list_by_code(collection_id, code_id)

    def find_by_number(self: CardsService, collection_id: int, card_number: int) -> list[Card]:
        return self._repo.find_by_number(collection_id, card_number)

    def lookup(
        self: CardsService,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> Card | None:
        """Card por business key (collection, code, number), o None."""
        return self._repo.get(collection_id, code_id, card_number)

    def get_by_id(self: CardsService, card_id: int) -> Card | None:
        return self._repo.get_by_id(card_id)

    def count(self: CardsService, collection_id: int) -> int:
        return self._repo.count_by_collection(collection_id)

    def get_stats_by_code(self: CardsService, collection_id: int) -> list[CodeStats]:
        return self._repo.get_stats_by_code(collection_id)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create(self: CardsService, card: Card) -> Card:
        """Crea una card. Valida campos antes de delegar al repo."""
        self._validate(card)
        try:
            return self._repo.create(card)
        except sqlite3.IntegrityError as exc:
            raise CardsError(
                f"card ya existe en (collection_id={card.collection_id}, "
                f"code_id={card.code_id!r}, card_number={card.card_number})"
            ) from exc

    def upsert(self: CardsService, card: Card) -> Card:
        """Inserta o actualiza por business key."""
        self._validate(card)
        return self._repo.upsert(card)

    def bulk_upsert(self: CardsService, cards: list[Card]) -> int:
        """Inserta/actualiza muchas cards en un batch.

        Valida TODAS las cards antes de tocar la DB. Si alguna falla
        validación, lanza `CardsError` y la DB queda intacta.
        """
        for card in cards:
            self._validate(card)
        return self._repo.bulk_upsert(cards)

    def delete_by_id(self: CardsService, card_id: int) -> bool:
        return self._repo.delete_by_id(card_id)

    # ------------------------------------------------------------------
    # Validaciones internas
    # ------------------------------------------------------------------

    def _validate(self: CardsService, card: Card) -> None:
        if not card.card_name.strip():
            raise CardsError("card_name no puede ser vacio")
        if card.card_number <= 0:
            raise CardsError(f"card_number debe ser > 0, recibido {card.card_number}")
        if self._collections.get_by_id(card.collection_id) is None:
            raise CardsError(f"collection_id={card.collection_id} no existe")
