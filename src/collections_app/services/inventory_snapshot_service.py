"""Construye `InventorySnapshot` a partir del inventario local (Prompt 5b).

Antes esta lógica vivía como método privado `_build_snapshot` en el
`ExchangeExportService`. La UI de pairing (5b) necesita el snapshot
local del usuario para alimentar el `MatchingService` después de
importar un archivo del otro coleccionista, sin tener que escribir
y leer un archivo intermedio (workaround feo del integration test).

Reglas de negocio (sec del prompt 5):
- `available_quantity = inventory.quantity - 1` para cada duplicado:
  la primera unidad es la que va al álbum del usuario, las demás son
  las que puede ofrecer en intercambio.
- `needed_quantity = 1` por default para los faltantes (semántica
  album: querés al menos 1 de cada). Si en el futuro se trackea
  cantidad necesaria distinta, va por acá.
- `user_label` se hace strip; vacío post-strip → None.
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.aggregates.inventory_snapshot import (
    DuplicateCard,
    InventorySnapshot,
    MissingCard,
)
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exchange_errors import CollectionNotFound
from collections_app.services.inventory_service import InventoryService


class InventorySnapshotService:
    """Compone `InventorySnapshot` desde la DB local del usuario."""

    def __init__(self: InventorySnapshotService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._collections = CollectionsService(conn)
        self._inventory = InventoryService(conn)
        self._cards = CardsRepository(conn)

    def build_local_snapshot(
        self: InventorySnapshotService,
        *,
        collection_id: int,
        user_label: str | None,
    ) -> InventorySnapshot:
        """Compone el snapshot del usuario local para `collection_id`.

        Returns:
            `InventorySnapshot` con `missing`, `duplicates`, metadata
            de la colección y label normalizado.

        Raises:
            CollectionNotFound: si `collection_id` no existe.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            raise CollectionNotFound(f"La colección con id {collection_id} no existe en esta DB.")

        cards_by_id = {
            c.card_id: c
            for c in self._cards.list_by_collection(collection_id)
            if c.card_id is not None
        }

        missing_cards = self._inventory.list_missing(collection_id)
        missing = tuple(
            MissingCard(
                code_id=c.code_id,
                card_number=c.card_number,
                card_name=c.card_name,
                needed_quantity=1,
            )
            for c in missing_cards
        )

        dup_items = self._inventory.list_duplicates(collection_id)
        duplicates_list: list[DuplicateCard] = []
        for item in dup_items:
            card = cards_by_id.get(item.card_id)
            if card is None:
                # Inventory huérfano (no debería pasar por FK, defensivo).
                continue
            available = item.quantity - 1
            if available <= 0:
                continue
            duplicates_list.append(
                DuplicateCard(
                    code_id=card.code_id,
                    card_number=card.card_number,
                    card_name=card.card_name,
                    available_quantity=available,
                )
            )

        normalized_label = user_label.strip() if user_label and user_label.strip() else None
        return InventorySnapshot(
            user_label=normalized_label,
            collection_name=collection.collection_name,
            collection_card_count=len(cards_by_id),
            missing=missing,
            duplicates=tuple(duplicates_list),
        )
