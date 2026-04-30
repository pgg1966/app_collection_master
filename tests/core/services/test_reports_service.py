"""Tests del ReportsService."""

from datetime import UTC, timedelta

from collections_app.core.models import OperationType
from collections_app.core.services import (
    InventoryService,
    ReportsService,
)
from collections_app.core.utils.datetime_helpers import utc_now


def _add_some_cards(memory_db, collection_id: int) -> None:
    svc = InventoryService(memory_db)
    svc.add_card(collection_id, "ARG", 1, 1)
    svc.add_card(collection_id, "ARG", 2, 1)
    svc.add_card(collection_id, "BRA", 1, 2)
    svc.remove_card(collection_id, "BRA", 1, 1)


def test_get_transactions_in_period_returns_card_info(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    # 4 movimientos: 3 altas + 1 baja
    assert len(rows) == 4
    # Cada uno trae el card_name del JOIN
    by_card = {(r.code_id, r.card_number): r for r in rows}
    assert by_card[("ARG", 1)].card_name == "Lionel Messi"
    assert by_card[("BRA", 1)].card_name == "Vinícius Jr."


def test_get_transactions_in_period_filters_by_date(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    # Un rango futuro no debería tener nada
    future = utc_now() + timedelta(hours=1)
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id, future, future + timedelta(hours=1)
    )
    assert rows == []


def test_get_transactions_in_period_filters_by_operation(
    memory_db, sample_cards, sample_collection
):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    altas = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
        operation=OperationType.ALTA,
    )
    bajas = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
        operation=OperationType.BAJA,
    )
    assert len(altas) == 3
    assert len(bajas) == 1
    assert all(t.operation == OperationType.ALTA for t in altas)
    assert all(t.operation == OperationType.BAJA for t in bajas)


def test_empty_period_returns_empty_list(memory_db, sample_collection):
    svc = ReportsService(memory_db)
    now = utc_now()
    assert (
        svc.get_transactions_in_period(
            sample_collection.collection_id,
            now - timedelta(minutes=1),
            now + timedelta(minutes=1),
        )
        == []
    )


def test_transactions_have_utc_tzinfo(memory_db, sample_cards, sample_collection):
    """Las fechas devueltas son siempre UTC."""

    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    assert rows
    for r in rows:
        assert r.transaction_date.tzinfo is UTC


def test_transactions_ordered_by_date_desc(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    # Los más recientes (la baja final) primero
    assert rows[0].operation == OperationType.BAJA


def test_only_collection_transactions(memory_db, sample_cards, sample_collection):
    """Verifica que el filtro por collection_id funciona."""
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    other = svc.get_transactions_in_period(
        9999, now - timedelta(minutes=1), now + timedelta(minutes=1)
    )
    assert other == []


def test_card_name_empty_when_card_deleted(memory_db, sample_cards, sample_collection):
    """Si la card fue borrada del catálogo, el reporte sigue funcionando."""
    from collections_app.core.repositories import CardsRepository

    _add_some_cards(memory_db, sample_collection.collection_id)
    # Borrar la card del catálogo (las transactions sobreviven)
    CardsRepository(memory_db).delete(sample_collection.collection_id, "ARG", 1)
    memory_db.commit()

    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    arg_1 = next((r for r in rows if r.code_id == "ARG" and r.card_number == 1), None)
    assert arg_1 is not None
    assert arg_1.card_name == ""
