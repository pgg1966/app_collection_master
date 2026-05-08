"""Tests exhaustivos del MatchingService (función pura)."""

from __future__ import annotations

from collections_app.core.models.aggregates.inventory_snapshot import (
    DuplicateCard,
    InventorySnapshot,
    MissingCard,
)
from collections_app.services.matching_service import MatchingService


def _snap(
    *,
    user_label: str | None = None,
    missing: tuple[MissingCard, ...] = (),
    duplicates: tuple[DuplicateCard, ...] = (),
) -> InventorySnapshot:
    return InventorySnapshot(
        user_label=user_label,
        collection_name="Mundial 2026",
        collection_card_count=670,
        missing=missing,
        duplicates=duplicates,
    )


# ---------------------------------------------------------------------
# Casos base
# ---------------------------------------------------------------------


def test_no_matches_returns_empty_proposal() -> None:
    """Sin coincidencias en ningún lado → propuesta vacía."""
    me = _snap(missing=(MissingCard("ARG", 1, "Messi", 1),))
    them = _snap(duplicates=(DuplicateCard("BRA", 7, "Neymar", 2),))
    proposal = MatchingService.calculate_proposal(me, them)
    assert proposal.cards_to_receive == ()
    assert proposal.cards_to_give == ()


def test_only_match_a_when_only_they_can_supply_my_missing() -> None:
    """Solo Match A: yo necesito ARG-1, él lo tiene de más."""
    me = _snap(missing=(MissingCard("ARG", 1, "Messi", 2),))
    them = _snap(duplicates=(DuplicateCard("ARG", 1, "Messi", 5),))
    proposal = MatchingService.calculate_proposal(me, them)
    assert len(proposal.cards_to_receive) == 1
    assert proposal.cards_to_give == ()
    receive = proposal.cards_to_receive[0]
    assert receive.code_id == "ARG"
    assert receive.card_number == 1
    assert receive.proposed_quantity == 2  # min(needed=2, available=5)
    assert receive.max_quantity == 5


def test_only_match_b_when_only_i_can_supply_their_missing() -> None:
    """Solo Match B: él necesita ARG-1, yo lo tengo de más."""
    me = _snap(duplicates=(DuplicateCard("ARG", 1, "Messi", 3),))
    them = _snap(missing=(MissingCard("ARG", 1, "Messi", 1),))
    proposal = MatchingService.calculate_proposal(me, them)
    assert proposal.cards_to_receive == ()
    assert len(proposal.cards_to_give) == 1
    give = proposal.cards_to_give[0]
    assert give.proposed_quantity == 1  # min(needed=1, available=3)
    assert give.max_quantity == 3


def test_both_matches_present() -> None:
    """Match A y Match B simultáneos."""
    me = _snap(
        missing=(MissingCard("ARG", 1, "Messi", 2),),
        duplicates=(DuplicateCard("BRA", 7, "Neymar", 4),),
    )
    them = _snap(
        missing=(MissingCard("BRA", 7, "Neymar", 1),),
        duplicates=(DuplicateCard("ARG", 1, "Messi", 3),),
    )
    proposal = MatchingService.calculate_proposal(me, them)
    assert len(proposal.cards_to_receive) == 1
    assert len(proposal.cards_to_give) == 1
    assert proposal.cards_to_receive[0].proposed_quantity == 2
    assert proposal.cards_to_give[0].proposed_quantity == 1


# ---------------------------------------------------------------------
# Reglas de cantidad
# ---------------------------------------------------------------------


def test_proposed_quantity_is_min_when_supply_exceeds_need() -> None:
    me = _snap(missing=(MissingCard("ARG", 1, "M", 1),))
    them = _snap(duplicates=(DuplicateCard("ARG", 1, "M", 10),))
    p = MatchingService.calculate_proposal(me, them)
    assert p.cards_to_receive[0].proposed_quantity == 1
    assert p.cards_to_receive[0].max_quantity == 10


def test_proposed_quantity_is_min_when_need_exceeds_supply() -> None:
    me = _snap(missing=(MissingCard("ARG", 1, "M", 10),))
    them = _snap(duplicates=(DuplicateCard("ARG", 1, "M", 2),))
    p = MatchingService.calculate_proposal(me, them)
    assert p.cards_to_receive[0].proposed_quantity == 2
    assert p.cards_to_receive[0].max_quantity == 2


def test_exact_quantities_match() -> None:
    me = _snap(missing=(MissingCard("ARG", 1, "M", 3),))
    them = _snap(duplicates=(DuplicateCard("ARG", 1, "M", 3),))
    p = MatchingService.calculate_proposal(me, them)
    assert p.cards_to_receive[0].proposed_quantity == 3
    assert p.cards_to_receive[0].max_quantity == 3


# ---------------------------------------------------------------------
# Identidad por (code_id, card_number)
# ---------------------------------------------------------------------


def test_same_number_different_code_does_not_match() -> None:
    """ARG-1 y BRA-1 son cards distintas aunque compartan el número."""
    me = _snap(missing=(MissingCard("ARG", 1, "Messi", 1),))
    them = _snap(duplicates=(DuplicateCard("BRA", 1, "Casemiro", 5),))
    p = MatchingService.calculate_proposal(me, them)
    assert p.cards_to_receive == ()


def test_same_code_different_number_does_not_match() -> None:
    me = _snap(missing=(MissingCard("ARG", 1, "Messi", 1),))
    them = _snap(duplicates=(DuplicateCard("ARG", 2, "Di María", 5),))
    p = MatchingService.calculate_proposal(me, them)
    assert p.cards_to_receive == ()


# ---------------------------------------------------------------------
# Pureza
# ---------------------------------------------------------------------


def test_function_is_pure_no_mutation_of_inputs() -> None:
    """La función no muta los snapshots de entrada."""
    me_missing = (MissingCard("ARG", 1, "M", 1),)
    me_dup = (DuplicateCard("BRA", 7, "N", 2),)
    me = _snap(missing=me_missing, duplicates=me_dup)
    them_missing = (MissingCard("BRA", 7, "N", 1),)
    them_dup = (DuplicateCard("ARG", 1, "M", 1),)
    them = _snap(missing=them_missing, duplicates=them_dup)

    MatchingService.calculate_proposal(me, them)
    MatchingService.calculate_proposal(me, them)  # idempotente

    # Los snapshots no cambiaron.
    assert me.missing is me_missing
    assert me.duplicates is me_dup
    assert them.missing is them_missing
    assert them.duplicates is them_dup


def test_calculate_proposal_is_deterministic() -> None:
    """Misma entrada → misma salida en llamadas sucesivas."""
    me = _snap(missing=(MissingCard("ARG", 1, "M", 1), MissingCard("BRA", 2, "B", 2)))
    them = _snap(duplicates=(DuplicateCard("ARG", 1, "M", 5), DuplicateCard("BRA", 2, "B", 5)))
    a = MatchingService.calculate_proposal(me, them)
    b = MatchingService.calculate_proposal(me, them)
    assert a == b
