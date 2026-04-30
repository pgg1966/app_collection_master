"""Tests del InventoryService."""

import pytest

from collections_app.core.models import OperationType
from collections_app.core.repositories import (
    InventoryRepository,
    TransactionsRepository,
)
from collections_app.core.services import InventoryService


def test_add_card_creates_inventory_and_logs(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    item = svc.add_card(cid, "ARG", 1, quantity=2)
    assert item.quantity == 2

    txns = TransactionsRepository(memory_db).list_by_collection(cid)
    assert len(txns) == 1
    assert txns[0].operation == OperationType.ALTA
    assert txns[0].quantity == 2


def test_add_card_increments_existing(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    item = svc.add_card(cid, "ARG", 1, quantity=3)
    assert item.quantity == 4


def test_add_card_rejects_zero_or_negative(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="quantity"):
        svc.add_card(cid, "ARG", 1, quantity=0)
    with pytest.raises(ValueError, match="quantity"):
        svc.add_card(cid, "ARG", 1, quantity=-1)


def test_add_card_rejects_unknown_card(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="no existe"):
        svc.add_card(cid, "ZZZ", 999, quantity=1)


def test_remove_card_decrements_and_logs(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=5)
    item = svc.remove_card(cid, "ARG", 1, quantity=2)
    assert item.quantity == 3

    txns = TransactionsRepository(memory_db).list_by_collection(cid)
    operations = [t.operation for t in txns]
    assert OperationType.BAJA in operations


def test_remove_card_rejects_zero_or_negative(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    with pytest.raises(ValueError, match="quantity"):
        svc.remove_card(cid, "ARG", 1, quantity=0)
    with pytest.raises(ValueError, match="quantity"):
        svc.remove_card(cid, "ARG", 1, quantity=-1)


def test_remove_card_rejects_when_no_inventory(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="No hay inventario"):
        svc.remove_card(cid, "ARG", 1, quantity=1)


def test_remove_card_rejects_when_insufficient(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    with pytest.raises(ValueError, match="insuficiente"):
        svc.remove_card(cid, "ARG", 1, quantity=5)


def test_remove_card_rollback_does_not_log_on_error(memory_db, sample_cards, sample_collection):
    """Si la baja falla validación, no se debe loguear ninguna transacción."""
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError):
        svc.remove_card(cid, "ARG", 1, quantity=1)
    assert TransactionsRepository(memory_db).list_by_collection(cid) == []


def test_get_stats_empty_collection(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    stats = svc.get_stats(sample_collection.collection_id)
    assert stats["total_cards"] == 0
    assert stats["owned"] == 0
    assert stats["missing"] == 0
    assert stats["percentage"] == 0.0
    assert stats["total_physical"] == 0
    assert stats["cards_with_duplicates"] == 0
    assert stats["total_duplicate_copies"] == 0


def test_get_stats_with_data(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=3)  # con duplicados (2 extras)
    svc.add_card(cid, "ARG", 2, quantity=1)
    svc.add_card(cid, "BRA", 1, quantity=2)  # 1 extra

    stats = svc.get_stats(cid)
    assert stats["total_cards"] == 5
    assert stats["owned"] == 3
    assert stats["missing"] == 2
    assert stats["percentage"] == pytest.approx(60.0)
    assert stats["total_physical"] == 6
    assert stats["cards_with_duplicates"] == 2
    assert stats["total_duplicate_copies"] == 3


def test_add_card_by_number_unique_match(memory_db, sample_cards, sample_collection):
    """Cuando find_by_number retorna 1, alta_by_number agrega normalmente."""
    from collections_app.core.models import Card
    from collections_app.core.repositories import CardsRepository

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    # Insertar una card con número único
    CardsRepository(memory_db).upsert(Card(cid, "FRA", 99, "Único"))
    memory_db.commit()
    item = svc.add_card_by_number(cid, 99, quantity=3)
    assert item.quantity == 3
    assert item.code_id == "FRA"
    assert item.card_number == 99


def test_add_card_by_number_zero_matches_raises_value_error(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.add_card_by_number(sample_collection.collection_id, 9999)


def test_add_card_by_number_ambiguous_raises(memory_db, sample_cards, sample_collection):
    """Si hay >1 card con ese número (en distintos códigos), AmbiguousCardError."""
    from collections_app.core.services import AmbiguousCardError

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    # En sample_cards, número 1 aparece en ARG, BRA, FRA → ambiguo
    with pytest.raises(AmbiguousCardError) as exc_info:
        svc.add_card_by_number(cid, 1)
    assert len(exc_info.value.matches) == 3


def test_remove_card_by_number_unique_match(memory_db, sample_cards, sample_collection):
    from collections_app.core.models import Card
    from collections_app.core.repositories import CardsRepository

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    CardsRepository(memory_db).upsert(Card(cid, "FRA", 99, "Único"))
    memory_db.commit()
    svc.add_card_by_number(cid, 99, quantity=5)
    item = svc.remove_card_by_number(cid, 99, quantity=2)
    assert item.quantity == 3


def test_remove_card_by_number_zero_matches_raises(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.remove_card_by_number(sample_collection.collection_id, 9999)


def test_remove_card_by_number_ambiguous_raises(memory_db, sample_cards, sample_collection):
    from collections_app.core.services import AmbiguousCardError

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(AmbiguousCardError):
        svc.remove_card_by_number(cid, 1)


def test_add_card_inside_transaction_does_not_partial_commit(
    memory_db, sample_cards, sample_collection
):
    """Verifica que la operación es atómica (alta + log juntos)."""
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    inv_count = len(InventoryRepository(memory_db).list_owned(cid))
    txn_count = len(TransactionsRepository(memory_db).list_by_collection(cid))
    assert inv_count == txn_count == 1
