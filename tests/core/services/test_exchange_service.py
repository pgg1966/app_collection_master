"""Tests del ExchangeService: archivos .colexchange, comparación e intercambio."""

import json

import pytest

from collections_app.core.models import (
    ExchangeCard,
    ExchangeFile,
    ExchangeSession,
    InventoryItem,
)
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services.exchange_service import (
    EXCHANGE_APP_ID,
    ExchangeService,
)

# ----------------------------------------------------------------------
# Fixtures locales
# ----------------------------------------------------------------------


@pytest.fixture
def populated_db(memory_db, sample_collection, sample_cards):
    """memory_db con sample_collection + sample_cards + inventario inicial.

    Inventario (collection FIFA WC 2026, requires_code=True):
      ARG-1 Messi:        quantity=1
      ARG-2 Martínez:     quantity=2  (repetida)
      BRA-1 Vinícius:     quantity=0  (faltante)
      BRA-2 Neymar:       quantity=3  (repetida)
      FRA-1 Mbappé:       quantity=0  (faltante)
    """
    cid = sample_collection.collection_id
    inv = InventoryRepository(memory_db)
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=1))
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=2))
    inv.upsert(InventoryItem(cid, "BRA", 2, quantity=3))
    memory_db.commit()
    return memory_db, sample_collection


# ----------------------------------------------------------------------
# Generación + carga + checksum
# ----------------------------------------------------------------------


def test_generate_creates_colexchange_file(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"

    ef = ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    assert out.exists()
    assert ef.app == EXCHANGE_APP_ID
    assert ef.collection_id == col.collection_id
    # Faltantes: BRA-1 y FRA-1. Repetidas: ARG-2, BRA-2.
    assert {(c.code_id, c.card_number) for c in ef.missing} == {("BRA", 1), ("FRA", 1)}
    assert {(c.code_id, c.card_number) for c in ef.duplicates} == {("ARG", 2), ("BRA", 2)}


def test_generated_file_has_valid_checksum(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    # load_exchange_file verifica el checksum y NO lanza si es válido.
    ef = ExchangeService(conn).load_exchange_file(out)
    assert ef.collection_id == col.collection_id
    assert ef.checksum != ""


def test_load_rejects_tampered_file(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    # Modificamos el archivo agregando una "carta extra" sin tocar el checksum.
    data = json.loads(out.read_text(encoding="utf-8"))
    data["duplicates"].append(
        {"code_id": "FAKE", "card_number": 999, "card_name": "Hacked", "quantity": 5}
    )
    out.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="checksum"):
        ExchangeService(conn).load_exchange_file(out)


def test_load_rejects_non_colexchange_app(memory_db, tmp_path):
    out = tmp_path / "fake.colexchange"
    out.write_text(
        json.dumps(
            {
                "app": "OtherApp",
                "version": "1.0",
                "collection_id": 1,
                "collection_name": "x",
                "missing": [],
                "duplicates": [],
                "checksum": "deadbeef",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="CollectionsApp"):
        ExchangeService(memory_db).load_exchange_file(out)


def test_load_rejects_invalid_json(memory_db, tmp_path):
    out = tmp_path / "bad.colexchange"
    out.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Archivo inválido"):
        ExchangeService(memory_db).load_exchange_file(out)


# ----------------------------------------------------------------------
# Comparación
# ----------------------------------------------------------------------


def _make_file(collection_id: int, *, missing=None, duplicates=None) -> ExchangeFile:
    return ExchangeFile(
        app=EXCHANGE_APP_ID,
        version="1.0",
        collection_id=collection_id,
        collection_name="X",
        generated_at="2026-01-01T00:00:00+00:00",
        missing=missing or [],
        duplicates=duplicates or [],
    )


def test_compare_i_need_correct(memory_db):
    # Yo necesito ARG-24. El otro lo tiene repetido.
    me = _make_file(1, missing=[ExchangeCard("ARG", 24, "Messi")])
    other = _make_file(
        1,
        duplicates=[ExchangeCard("ARG", 24, "Messi", 2), ExchangeCard("BRA", 7, "Vini", 3)],
    )
    result = ExchangeService(memory_db).compare(me, other)
    assert [(c.code_id, c.card_number) for c in result.i_need] == [("ARG", 24)]
    assert result.i_can_offer == []


def test_compare_i_can_offer_correct(memory_db):
    me = _make_file(1, duplicates=[ExchangeCard("NON", 42, "Álvarez", 2)])
    other = _make_file(1, missing=[ExchangeCard("NON", 42, "Álvarez"), ExchangeCard("BRA", 5, "X")])
    result = ExchangeService(memory_db).compare(me, other)
    assert [(c.code_id, c.card_number) for c in result.i_can_offer] == [("NON", 42)]
    assert result.i_need == []


def test_compare_no_overlap_returns_empty(memory_db):
    me = _make_file(
        1, missing=[ExchangeCard("ARG", 1, "x")], duplicates=[ExchangeCard("BRA", 1, "y", 2)]
    )
    other = _make_file(
        1, missing=[ExchangeCard("FRA", 1, "z")], duplicates=[ExchangeCard("ESP", 1, "w", 2)]
    )
    result = ExchangeService(memory_db).compare(me, other)
    assert result.i_need == []
    assert result.i_can_offer == []


def test_compare_different_collections_raises(memory_db):
    me = _make_file(1)
    other = _make_file(2)
    with pytest.raises(ValueError, match="colecciones distintas"):
        ExchangeService(memory_db).compare(me, other)


# ----------------------------------------------------------------------
# Lock / Unlock
# ----------------------------------------------------------------------


def test_lock_increments_locked_column(populated_db):
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    # ARG-2 quantity=2, locked=0
    item = repo.get(cid, "ARG", 2)
    assert item.quantity == 2 and item.locked == 0

    ExchangeService(conn).lock_cards(cid, [ExchangeCard("ARG", 2, "Martínez", 2)])

    item = repo.get(cid, "ARG", 2)
    assert item.locked == 1
    assert item.available_quantity == 1


def test_lock_creates_item_when_missing(populated_db):
    """Bloquear una carta sin inventario crea el item con qty=0, locked=1."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    assert repo.get(cid, "FRA", 1) is None  # no existía

    ExchangeService(conn).lock_cards(cid, [ExchangeCard("FRA", 1, "Mbappé")])

    item = repo.get(cid, "FRA", 1)
    assert item is not None
    assert item.quantity == 0
    assert item.locked == 1


def test_unlock_all_resets_locked(populated_db):
    conn, col = populated_db
    cid = col.collection_id
    svc = ExchangeService(conn)
    svc.lock_cards(
        cid,
        [
            ExchangeCard("ARG", 2, "Martínez"),
            ExchangeCard("BRA", 2, "Neymar"),
        ],
    )
    svc.unlock_all_cards(cid)

    repo = InventoryRepository(conn)
    assert repo.get(cid, "ARG", 2).locked == 0
    assert repo.get(cid, "BRA", 2).locked == 0
    assert repo.list_locked(cid) == []


# ----------------------------------------------------------------------
# Generación: las cartas bloqueadas no aparecen en duplicates
# ----------------------------------------------------------------------


def test_duplicates_excludes_locked_items(populated_db, tmp_path):
    """ARG-2 quantity=2, locked=1 → available=1 → NO aparece en duplicates."""
    conn, col = populated_db
    cid = col.collection_id

    InventoryRepository(conn).lock(cid, "ARG", 2)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    codes = {(c.code_id, c.card_number) for c in ef.duplicates}
    assert ("ARG", 2) not in codes
    # BRA-2 sigue disponible
    assert ("BRA", 2) in codes


def test_missing_includes_card_with_only_locked_unit(populated_db, tmp_path):
    """Si una carta tiene qty=1 y locked=1, available=0 → faltante."""
    conn, col = populated_db
    cid = col.collection_id
    # ARG-1 tiene qty=1. La bloqueamos.
    InventoryRepository(conn).lock(cid, "ARG", 1)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    missing_codes = {(c.code_id, c.card_number) for c in ef.missing}
    assert ("ARG", 1) in missing_codes


# ----------------------------------------------------------------------
# Ejecución del intercambio
# ----------------------------------------------------------------------


def test_execute_exchange_gives_and_receives(populated_db):
    """to_give resta del inventario, to_receive suma, locked queda en 0."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    assert repo.get(cid, "ARG", 2).quantity == 2  # entrego 1
    assert repo.get(cid, "BRA", 1) is None  # recibo 1

    session = ExchangeSession(
        to_give=[ExchangeCard("ARG", 2, "Martínez")],
        to_receive=[ExchangeCard("BRA", 1, "Vinícius")],
    )
    # Pre-lock como hace el dialog
    ExchangeService(conn).lock_cards(cid, session.to_give)

    ExchangeService(conn).execute_exchange(cid, session)

    arg2 = repo.get(cid, "ARG", 2)
    bra1 = repo.get(cid, "BRA", 1)
    assert arg2.quantity == 1
    assert arg2.locked == 0
    assert bra1.quantity == 1
    assert bra1.locked == 0


def test_execute_exchange_rollback_on_error(populated_db):
    """Si una baja falla, todas las operaciones revierten."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    arg2_before = repo.get(cid, "ARG", 2).quantity
    bra2_before = repo.get(cid, "BRA", 2).quantity

    # Pedimos bajar 1 de FRA-1 que no tenemos → debe fallar y revertir todo
    session = ExchangeSession(
        to_give=[
            ExchangeCard("ARG", 2, "Martínez"),
            ExchangeCard("FRA", 1, "Mbappé"),  # no la tengo → ValueError
        ],
        to_receive=[ExchangeCard("BRA", 1, "Vinícius")],
    )
    with pytest.raises(ValueError):
        ExchangeService(conn).execute_exchange(cid, session)

    # Estado inalterado: rollback exitoso
    assert repo.get(cid, "ARG", 2).quantity == arg2_before
    assert repo.get(cid, "BRA", 2).quantity == bra2_before
    assert repo.get(cid, "BRA", 1) is None  # no se creó


def test_execute_exchange_creates_card_in_catalog_if_missing(populated_db):
    """Si la carta a recibir no está en cards (raro), se crea silenciosamente."""
    conn, col = populated_db
    cid = col.collection_id

    cards_repo = CardsRepository(conn)
    # ZZZ-99 no existe
    assert cards_repo.get(cid, "ZZZ", 99) is None

    session = ExchangeSession(
        to_give=[],
        to_receive=[ExchangeCard("ZZZ", 99, "Foreign Card")],
    )
    ExchangeService(conn).execute_exchange(cid, session)

    # Carta creada en catálogo + inventario con quantity=1
    assert cards_repo.get(cid, "ZZZ", 99) is not None
    assert InventoryRepository(conn).get(cid, "ZZZ", 99).quantity == 1
