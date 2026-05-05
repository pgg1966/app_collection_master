"""Tests del dataclass Card."""

from __future__ import annotations

from collections_app.core.models.card import Card


def test_card_key_combines_code_and_number() -> None:
    card = Card(card_id=1, collection_id=1, code_id="ARG", card_number=24, card_name="Messi")
    assert card.card_key == "ARG-24"


def test_card_key_with_short_code() -> None:
    card = Card(card_id=2, collection_id=1, code_id="MR", card_number=1, card_name="X")
    assert card.card_key == "MR-1"


def test_card_id_can_be_none_pre_persistence() -> None:
    card = Card(card_id=None, collection_id=1, code_id="X", card_number=1, card_name="X")
    assert card.card_id is None
