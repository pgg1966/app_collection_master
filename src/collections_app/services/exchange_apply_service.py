"""Aplica una `ExchangeProposal` como grupo atómico de transactions (Prompt 5).

Cada apply genera UN `exchange_event_id` compartido por todas las
transactions del intercambio. Eso permite reconstruir el evento desde
el historial:
    SELECT * FROM transactions WHERE exchange_event_id = ?
    ORDER BY transaction_date

El formato del prompt original sugería `epoch_ms × 10000 + 4 random
digits`. Reusamos `services/_event_id.py` que usa `× 1000 + 3 random
digits`. Ambos formatos garantizan unicidad práctica (la probabilidad
de colisión es despreciable a escalas humanas) y caben en SQLite
INTEGER (int64). No bumpeamos el helper para no introducir cambio
de comportamiento en otros consumers (importer de inventario, etc.).

Pre-validación: antes de empezar la transacción SQL, se verifica que
TODOS los `give` tienen stock suficiente. Si falta stock en alguno,
se lanza `InsufficientInventory` ANTES de tocar la DB. Esto evita
rollbacks parciales por validaciones de negocio (las violaciones de
schema sí dispararían rollback, pero esas no deberían ocurrir en
estado consistente).

Atomicidad SQL: el `with self._conn:` envuelve todas las mutaciones.
Si una falla a mitad (FK violation, etc.), rollback total — DB queda
intacta.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from collections_app.core.models.aggregates.exchange_proposal import (
    ExchangeEventResult,
    ExchangeProposal,
    ProposedExchange,
)
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository
from collections_app.services._event_id import generate_event_id
from collections_app.services.exchange_errors import InsufficientInventory


def _utc_now_naive() -> datetime:
    """UTC actual sin tzinfo, formato consistente con el default SQL."""
    return datetime.now(UTC).replace(tzinfo=None)


class ExchangeApplyService:
    """Aplica una `ExchangeProposal` al inventario del usuario."""

    def __init__(self: ExchangeApplyService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._inventory = InventoryRepository(conn)
        self._cards = CardsRepository(conn)
        self._transactions = TransactionsRepository(conn)

    def apply_proposal(
        self: ExchangeApplyService,
        *,
        proposal: ExchangeProposal,
        collection_id: int,
    ) -> ExchangeEventResult:
        """Aplica `proposal` para `collection_id` atómicamente.

        Reglas:
        - Filas con `proposed_quantity == 0` se ignoran (no generan
          transaction ni movimiento de inventory).
        - Pre-validación: todos los `give` deben tener stock >= qty.
          Si falla, raise `InsufficientInventory` ANTES de la
          transacción SQL — DB intacta.
        - Genera UN `exchange_event_id` para todas las transactions
          del evento.
        - Para cada `give`: BAJA + `adjust_quantity(-qty)`.
        - Para cada `receive`: ALTA + `adjust_quantity(+qty)`.
        - Todo dentro de `with self._conn:` (atómico).

        Returns:
            `ExchangeEventResult` con `exchange_event_id` y conteos.

        Raises:
            InsufficientInventory: pre-validación falla.
        """
        # Filtrar filas con qty>0 (las cero las ignoramos; ver doc).
        gives = [g for g in proposal.cards_to_give if g.proposed_quantity > 0]
        receives = [r for r in proposal.cards_to_receive if r.proposed_quantity > 0]

        # Resolver card_id por (code_id, card_number) para cada fila.
        give_resolutions = self._resolve_cards(collection_id, gives)
        receive_resolutions = self._resolve_cards(collection_id, receives)

        # Pre-validación de stock para los gives.
        self._check_sufficient_inventory(give_resolutions)

        event_id = generate_event_id()
        now = _utc_now_naive()
        with self._conn:
            for card_id, qty in give_resolutions:
                self._inventory.adjust_quantity(card_id, -qty)
                self._transactions.log(
                    Transaction(
                        transaction_id=None,
                        card_id=card_id,
                        operation=OperationType.BAJA,
                        quantity=qty,
                        transaction_date=now,
                        exchange_event_id=event_id,
                    )
                )
            for card_id, qty in receive_resolutions:
                self._inventory.adjust_quantity(card_id, qty)
                self._transactions.log(
                    Transaction(
                        transaction_id=None,
                        card_id=card_id,
                        operation=OperationType.ALTA,
                        quantity=qty,
                        transaction_date=now,
                        exchange_event_id=event_id,
                    )
                )

        return ExchangeEventResult(
            exchange_event_id=event_id,
            received_count=len(receive_resolutions),
            given_count=len(give_resolutions),
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _resolve_cards(
        self: ExchangeApplyService,
        collection_id: int,
        rows: list[ProposedExchange],
    ) -> list[tuple[int, int]]:
        """Resuelve cada fila a `(card_id, quantity)`.

        Si una card de la propuesta no existe en la DB local, raise
        `InsufficientInventory` con un mensaje claro — no debería
        ocurrir si el caller usó el `MatchingService` sobre snapshots
        importados (que filtran cards desconocidas en warnings), pero
        es defensivo.
        """
        out: list[tuple[int, int]] = []
        for row in rows:
            card = self._cards.get(collection_id, row.code_id, row.card_number)
            if card is None or card.card_id is None:
                raise InsufficientInventory(
                    f"La card {row.code_id}-{row.card_number} ({row.card_name}) "
                    f"no existe en esta colección."
                )
            out.append((card.card_id, row.proposed_quantity))
        return out

    def _check_sufficient_inventory(
        self: ExchangeApplyService,
        give_resolutions: list[tuple[int, int]],
    ) -> None:
        """Verifica que `inventory.quantity >= qty` para cada give.

        Lanza `InsufficientInventory` si alguno falla. Ejecuta ANTES
        de empezar la transacción SQL para que la DB quede intacta
        en el caso de error.
        """
        for card_id, qty in give_resolutions:
            current = self._inventory.get_by_card_id(card_id)
            current_qty = current.quantity if current is not None else 0
            if current_qty < qty:
                raise InsufficientInventory(
                    f"Stock insuficiente para card_id={card_id}: hay {current_qty}, "
                    f"se piden {qty}."
                )
