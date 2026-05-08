"""Lógica pura de matching entre dos `InventorySnapshot` (Prompt 5).

`MatchingService.calculate_proposal` es una **función pura**:
- Sin estado interno.
- Sin I/O (no toca DB, archivos, red, env vars).
- Sin imports a Qt, repos, services con efectos.
- Determinista: misma entrada → misma salida.

Implicación arquitectónica: la misma función va a usarse en v0.2
leyendo de archivos `.colexchange`, en v0.3 móvil, y en v1.0 cloud
recibiendo snapshots desde una API REST. Solo cambia **de dónde
vienen los snapshots**, no la lógica de matching.

Algoritmo (ver `docs/exchange_design.md`):

- **Match A** (cards que él te puede dar): `my_missing ∩ their_duplicates`.
  `proposed_quantity = min(needed, available)`, `max_quantity = available`.
- **Match B** (cards que vos le podés dar): `their_missing ∩ my_duplicates`.
  `proposed_quantity = min(needed, available)`, `max_quantity = available`.

El usuario en la UI puede ajustar `proposed_quantity` solo a la baja
(no por encima de `max_quantity`) — eso lo enforce la UI/ApplyService,
no esta función.
"""

from __future__ import annotations

from collections_app.core.models.aggregates.exchange_proposal import (
    ExchangeProposal,
    ProposedExchange,
)
from collections_app.core.models.aggregates.inventory_snapshot import (
    DuplicateCard,
    InventorySnapshot,
    MissingCard,
)


def _key(card: MissingCard | DuplicateCard) -> tuple[str, int]:
    """Identidad de una card: (code_id, card_number)."""
    return (card.code_id, card.card_number)


class MatchingService:
    """Calculadora pura de propuestas de intercambio."""

    @staticmethod
    def calculate_proposal(
        my_inventory: InventorySnapshot,
        their_inventory: InventorySnapshot,
    ) -> ExchangeProposal:
        """Calcula la propuesta de intercambio entre dos inventarios.

        Args:
            my_inventory: snapshot del usuario que importa el archivo.
            their_inventory: snapshot del archivo recibido.

        Returns:
            `ExchangeProposal` con `cards_to_receive` (Match A) y
            `cards_to_give` (Match B). Ambas listas vacías si no hay
            coincidencias.
        """
        receive = _match(
            my_needs=my_inventory.missing,
            their_supply=their_inventory.duplicates,
        )
        give = _match(
            my_needs=their_inventory.missing,
            their_supply=my_inventory.duplicates,
        )
        return ExchangeProposal(
            cards_to_receive=tuple(receive),
            cards_to_give=tuple(give),
        )


def _match(
    *,
    my_needs: tuple[MissingCard, ...],
    their_supply: tuple[DuplicateCard, ...],
) -> list[ProposedExchange]:
    """Intersección por (code_id, card_number) entre faltantes y duplicados.

    Para cada faltante que coincide con un duplicado del otro,
    `proposed_quantity = min(needed, available)`. `max_quantity` es
    `available` (la UI permite bajar, no subir).
    """
    supply_by_key: dict[tuple[str, int], DuplicateCard] = {_key(d): d for d in their_supply}
    out: list[ProposedExchange] = []
    for need in my_needs:
        supply = supply_by_key.get(_key(need))
        if supply is None:
            continue
        proposed = min(need.needed_quantity, supply.available_quantity)
        out.append(
            ProposedExchange(
                code_id=need.code_id,
                card_number=need.card_number,
                card_name=need.card_name,
                proposed_quantity=proposed,
                max_quantity=supply.available_quantity,
            )
        )
    return out
