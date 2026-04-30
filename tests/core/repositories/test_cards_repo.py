"""Tests del CardsRepository."""

import sqlite3

import pytest

from collections_app.core.models import Card
from collections_app.core.repositories import CardsRepository


def test_upsert_insert(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    card = Card(sample_collection.collection_id, "ARG", 1, "Messi")
    repo.upsert(card)
    fetched = repo.get(sample_collection.collection_id, "ARG", 1)
    assert fetched == card


def test_upsert_update_existing(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 1, "Messi"))
    repo.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.card_name == "Lionel Messi"


def test_get_missing_returns_none(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ARG", 99) is None


def test_list_by_collection_with_data(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    cards = repo.list_by_collection(sample_collection.collection_id)
    assert len(cards) == 5


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_by_code(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    arg_cards = repo.list_by_code(sample_collection.collection_id, "ARG")
    assert len(arg_cards) == 2
    assert all(c.code_id == "ARG" for c in arg_cards)


def test_count_by_collection(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.count_by_collection(sample_collection.collection_id) == 5


def test_count_by_collection_empty(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.count_by_collection(sample_collection.collection_id) == 0


def test_delete_existing(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id, "ARG", 1) is True
    assert repo.get(sample_collection.collection_id, "ARG", 1) is None


def test_delete_nonexistent(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id, "XXX", 99) is False


def test_bulk_upsert_inserts(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    cards = [Card(cid, "X", n, f"Card-{n}") for n in range(1, 21)]
    inserted = repo.bulk_upsert(cards)
    assert inserted == 20
    assert repo.count_by_collection(cid) == 20


def test_bulk_upsert_empty_list(memory_db):
    repo = CardsRepository(memory_db)
    assert repo.bulk_upsert([]) == 0


def test_bulk_upsert_updates_existing(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 1, "Old"))
    repo.bulk_upsert([Card(cid, "ARG", 1, "New")])
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.card_name == "New"


def test_card_key_property():
    card = Card(1, "ARG", 24, "Lionel Messi")
    assert card.card_key == "ARG-24"


def test_invalid_collection_fk(memory_db):
    repo = CardsRepository(memory_db)
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(Card(999, "X", 1, "ghost"))


def test_cascade_delete_from_collection(memory_db, sample_cards, sample_collection):
    """Borrar la colección elimina sus cards en cascade."""
    from collections_app.core.repositories import CollectionsRepository

    cards_repo = CardsRepository(memory_db)
    CollectionsRepository(memory_db).delete(sample_collection.collection_id)
    assert cards_repo.list_by_collection(sample_collection.collection_id) == []


def test_find_by_number_returns_match(memory_db, sample_cards, sample_collection):
    """Si hay un solo card con ese número, lo retorna."""
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    # sample_cards tiene FRA-1 (número 1 en code "FRA"). ARG-1, BRA-1 también.
    matches = repo.find_by_number(cid, 1)
    assert len(matches) == 3  # ARG-1, BRA-1, FRA-1
    codes = {c.code_id for c in matches}
    assert codes == {"ARG", "BRA", "FRA"}


def test_find_by_number_returns_empty_when_not_exists(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.find_by_number(sample_collection.collection_id, 9999) == []


def test_find_by_number_returns_multiple_when_ambiguous(memory_db, sample_collection):
    """Cuando varias cards comparten número en distintos códigos, retorna todas."""
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 24, "Messi"))
    repo.upsert(Card(cid, "BRA", 24, "Vinicius"))
    matches = repo.find_by_number(cid, 24)
    assert len(matches) == 2
    assert {m.code_id for m in matches} == {"ARG", "BRA"}
