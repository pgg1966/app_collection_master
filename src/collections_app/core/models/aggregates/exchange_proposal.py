"""Resultado del matching de pairing (Prompt 5).

`ExchangeProposal` es el output del `MatchingService` y la entrada
del `ExchangeApplyService`. Contiene dos listas:

- `cards_to_receive` (Match A): cards que el otro me puede dar.
- `cards_to_give` (Match B): cards que yo le puedo dar.

`ProposedExchange` describe una fila de la propuesta con
`proposed_quantity` (default greedy = `min(needed, available)`) y
`max_quantity` (límite superior — la UI solo permite ajustar a la
baja).

`ExchangeEventResult` es el resumen tras aplicar la propuesta —
incluye el `exchange_event_id` para reconstruir el evento desde el
historial.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ProposedExchange:
    """Una fila de la propuesta: card + cantidad propuesta + máximo."""

    code_id: str
    card_number: int
    card_name: str
    proposed_quantity: int
    max_quantity: int


@dataclass(slots=True, frozen=True)
class ExchangeProposal:
    """Resultado del matching entre dos snapshots.

    `cards_to_receive` y `cards_to_give` son tuplas (no listas) para
    mantener el dataclass frozen + hashable + equality por valor.
    """

    cards_to_receive: tuple[ProposedExchange, ...]
    cards_to_give: tuple[ProposedExchange, ...]


@dataclass(slots=True, frozen=True)
class ExchangeEventResult:
    """Resumen del intercambio aplicado.

    `exchange_event_id` agrupa todas las transactions del evento —
    permite reconstruir el intercambio en el historial vía
    `transactions WHERE exchange_event_id = ?`.
    """

    exchange_event_id: int
    received_count: int
    given_count: int
