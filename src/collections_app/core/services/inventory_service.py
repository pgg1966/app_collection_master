"""Servicio que coordina inventory + transactions de forma consistente."""

import sqlite3
from datetime import datetime

from collections_app.core.db.connection import transaction
from collections_app.core.models import (
    InventoryItem,
    OperationType,
    Transaction,
)
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
    TransactionsRepository,
)


class InventoryService:
    """Orquesta inventory + transactions para alta/baja consistente."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._cards = CardsRepository(conn)
        self._inventory = InventoryRepository(conn)
        self._transactions = TransactionsRepository(conn)

    def add_card(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Suma al inventario y registra transacción 'alta'.

        Validaciones:
        - quantity > 0
        - La (collection_id, code_id, card_number) debe existir en cards.

        Toda la operación corre dentro de una transacción SQLite.
        """
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")

        if self._cards.get(collection_id, code_id, card_number) is None:
            raise ValueError(f"Card ({collection_id}, {code_id}, {card_number}) no existe en cards")

        with transaction(self.conn):
            updated = self._inventory.adjust_quantity(collection_id, code_id, card_number, quantity)
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    collection_id=collection_id,
                    code_id=code_id,
                    card_number=card_number,
                    operation=OperationType.ALTA,
                    quantity=quantity,
                    transaction_date=datetime.now(),
                )
            )
        return updated

    def remove_card(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Resta del inventario y registra transacción 'baja'.

        Validaciones:
        - quantity > 0
        - El item debe existir y tener `quantity` >= cantidad pedida.

        Toda la operación corre dentro de una transacción SQLite.
        """
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")

        existing = self._inventory.get(collection_id, code_id, card_number)
        if existing is None:
            raise ValueError(f"No hay inventario para ({collection_id}, {code_id}, {card_number})")
        if existing.quantity < quantity:
            raise ValueError(f"Cantidad insuficiente: hay {existing.quantity}, se piden {quantity}")

        with transaction(self.conn):
            updated = self._inventory.adjust_quantity(
                collection_id, code_id, card_number, -quantity
            )
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    collection_id=collection_id,
                    code_id=code_id,
                    card_number=card_number,
                    operation=OperationType.BAJA,
                    quantity=quantity,
                    transaction_date=datetime.now(),
                )
            )
        return updated

    def get_stats(self, collection_id: int) -> dict[str, int | float]:
        """Estadísticas agregadas para una colección.

        Returns:
            Dict con:
            - total_cards: cantidad de cards en el catálogo.
            - owned: cards distintas con quantity > 0.
            - missing: cards sin stock (no en inventory o quantity = 0).
            - percentage: owned / total_cards * 100 (0.0 si total_cards = 0).
            - total_physical: suma de todas las quantities (todas las copias).
            - cards_with_duplicates: cards distintas con quantity > 1.
            - total_duplicate_copies: suma de (quantity - 1) sobre las que tienen duplicados.
        """
        total_cards = self._cards.count_by_collection(collection_id)
        owned_items = self._inventory.list_owned(collection_id)
        owned = len(owned_items)
        missing = max(0, total_cards - owned)
        percentage = (owned / total_cards * 100) if total_cards > 0 else 0.0
        total_physical = sum(i.quantity for i in owned_items)
        dup_items = [i for i in owned_items if i.quantity > 1]
        cards_with_duplicates = len(dup_items)
        total_duplicate_copies = sum(i.quantity - 1 for i in dup_items)

        return {
            "total_cards": total_cards,
            "owned": owned,
            "missing": missing,
            "percentage": percentage,
            "total_physical": total_physical,
            "cards_with_duplicates": cards_with_duplicates,
            "total_duplicate_copies": total_duplicate_copies,
        }
