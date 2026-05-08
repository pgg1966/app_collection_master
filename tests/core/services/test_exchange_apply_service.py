"""Tests del ExchangeApplyService — atomicidad + overflow + reglas de negocio."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from collections_app.core.models.aggregates.exchange_proposal import (
    ExchangeProposal,
    ProposedExchange,
)
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.services.exchange_apply_service import ExchangeApplyService
from collections_app.services.exchange_errors import InsufficientInventory


@pytest.fixture
def setup() -> Iterator[tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]]]:
    """Setup mínimo: collection con ARG-1, BRA-7, FRA-10 e inventario inicial."""
    from collections_app.app_context import create_app_context

    ctx = create_app_context(":memory:")
    try:
        conn = ctx.conn
        headers = CodeHeadersRepository(conn)
        lines = CodeLinesRepository(conn)
        collections = CollectionsRepository(conn)
        cards = CardsRepository(conn)
        inv = InventoryRepository(conn)

        h = headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        for code in ("ARG", "BRA", "FRA"):
            lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=h.code_header_id,
                    code_id=code,
                    code_name=code,
                    code_order=1,
                )
            )
        coll = collections.create(
            Collection(
                collection_id=None,
                collection_name="Mundial",
                card_count=3,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        ids: dict[tuple[str, int], int] = {}
        for code, num, name in [("ARG", 1, "Messi"), ("BRA", 7, "Neymar"), ("FRA", 10, "Mbappé")]:
            c = cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=num,
                    card_name=name,
                )
            )
            assert c.card_id is not None
            ids[(code, num)] = c.card_id
        # Inventario inicial: ARG-1 qty=3, BRA-7 qty=0 (faltante), FRA-10 qty=2.
        inv.adjust_quantity(ids[("ARG", 1)], 3)
        inv.adjust_quantity(ids[("FRA", 10)], 2)
        conn.commit()
        yield conn, coll, ids
    finally:
        ctx.close()


# ---------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------


def test_apply_basic_exchange_updates_inventory(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Doy 1 ARG-1, recibo 1 BRA-7. Inventario refleja: ARG-1 qty=2, BRA-7 qty=1."""
    conn, coll, ids = setup
    proposal = ExchangeProposal(
        cards_to_give=(ProposedExchange("ARG", 1, "Messi", 1, 2),),
        cards_to_receive=(ProposedExchange("BRA", 7, "Neymar", 1, 5),),
    )
    assert coll.collection_id is not None
    result = ExchangeApplyService(conn).apply_proposal(
        proposal=proposal, collection_id=coll.collection_id
    )
    inv = InventoryRepository(conn)
    arg_qty = inv.get_by_card_id(ids[("ARG", 1)])
    bra_qty = inv.get_by_card_id(ids[("BRA", 7)])
    assert arg_qty is not None and arg_qty.quantity == 2
    assert bra_qty is not None and bra_qty.quantity == 1
    assert result.given_count == 1
    assert result.received_count == 1


def test_apply_logs_transactions_with_shared_event_id(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Todas las transactions del apply comparten el mismo `exchange_event_id`."""
    conn, coll, ids = setup
    proposal = ExchangeProposal(
        cards_to_give=(
            ProposedExchange("ARG", 1, "Messi", 1, 2),
            ProposedExchange("FRA", 10, "Mbappé", 1, 1),
        ),
        cards_to_receive=(ProposedExchange("BRA", 7, "Neymar", 2, 5),),
    )
    assert coll.collection_id is not None
    result = ExchangeApplyService(conn).apply_proposal(
        proposal=proposal, collection_id=coll.collection_id
    )
    rows = conn.execute(
        "SELECT operation, quantity, exchange_event_id FROM transactions"
    ).fetchall()
    assert len(rows) == 3
    event_ids = {r[2] for r in rows}
    assert event_ids == {result.exchange_event_id}


def test_apply_skips_zero_quantity_rows(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Filas con `proposed_quantity == 0` no generan transaction ni movimiento."""
    conn, coll, ids = setup
    proposal = ExchangeProposal(
        cards_to_give=(ProposedExchange("ARG", 1, "Messi", 0, 2),),
        cards_to_receive=(ProposedExchange("BRA", 7, "Neymar", 1, 5),),
    )
    assert coll.collection_id is not None
    ExchangeApplyService(conn).apply_proposal(proposal=proposal, collection_id=coll.collection_id)
    # ARG-1 sigue en 3 (no se aplicó la baja).
    inv = InventoryRepository(conn)
    arg_qty = inv.get_by_card_id(ids[("ARG", 1)])
    assert arg_qty is not None and arg_qty.quantity == 3
    rows = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert rows[0] == 1  # solo la alta


# ---------------------------------------------------------------------
# Pre-validación de stock
# ---------------------------------------------------------------------


def test_apply_raises_when_insufficient_inventory_no_db_changes(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Si pides dar 5 ARG-1 pero solo tenés 3: raise + DB intacta."""
    conn, coll, ids = setup
    proposal = ExchangeProposal(
        cards_to_give=(ProposedExchange("ARG", 1, "Messi", 5, 5),),
        cards_to_receive=(ProposedExchange("BRA", 7, "Neymar", 1, 5),),
    )
    assert coll.collection_id is not None
    with pytest.raises(InsufficientInventory, match="hay 3"):
        ExchangeApplyService(conn).apply_proposal(
            proposal=proposal, collection_id=coll.collection_id
        )
    inv = InventoryRepository(conn)
    arg = inv.get_by_card_id(ids[("ARG", 1)])
    bra = inv.get_by_card_id(ids[("BRA", 7)])
    assert arg is not None and arg.quantity == 3  # sin cambios
    assert bra is None or bra.quantity == 0  # nunca se aplicó la alta
    rows = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert rows[0] == 0


def test_apply_raises_when_card_not_in_collection(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Card de la propuesta que no existe localmente → InsufficientInventory."""
    conn, coll, _ = setup
    proposal = ExchangeProposal(
        cards_to_give=(),
        cards_to_receive=(ProposedExchange("ITA", 99, "Phantom", 1, 5),),
    )
    assert coll.collection_id is not None
    with pytest.raises(InsufficientInventory, match="no existe"):
        ExchangeApplyService(conn).apply_proposal(
            proposal=proposal, collection_id=coll.collection_id
        )


# ---------------------------------------------------------------------
# Overflow check de exchange_event_id (sec 5 del mini-prompt)
# ---------------------------------------------------------------------


def test_exchange_event_id_persists_without_truncation(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """El event_id (~16 dígitos) cabe en SQLite INTEGER (int64) sin truncamiento."""
    conn, coll, _ = setup
    proposal = ExchangeProposal(
        cards_to_give=(),
        cards_to_receive=(ProposedExchange("BRA", 7, "Neymar", 1, 5),),
    )
    assert coll.collection_id is not None
    result = ExchangeApplyService(conn).apply_proposal(
        proposal=proposal, collection_id=coll.collection_id
    )
    # Verificar que el event_id es del orden esperado (epoch_ms × 1000).
    assert result.exchange_event_id > 10**15
    # Leer de vuelta y confirmar que matchea exactamente.
    row = conn.execute(
        "SELECT exchange_event_id FROM transactions WHERE exchange_event_id = ?",
        (result.exchange_event_id,),
    ).fetchone()
    assert row is not None
    assert row[0] == result.exchange_event_id


# ---------------------------------------------------------------------
# Atomicidad
# ---------------------------------------------------------------------


def test_apply_is_atomic_on_unhandled_exception(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si una mutación falla a mitad, rollback total (DB intacta)."""
    conn, coll, ids = setup
    proposal = ExchangeProposal(
        cards_to_give=(ProposedExchange("ARG", 1, "Messi", 1, 2),),
        cards_to_receive=(
            ProposedExchange("BRA", 7, "Neymar", 1, 5),
            ProposedExchange("FRA", 10, "Mbappé", 1, 5),
        ),
    )
    svc = ExchangeApplyService(conn)
    # Hacer que el segundo `transactions.log` rompa.
    real_log = svc._transactions.log
    counter = {"n": 0}

    def flaky_log(*args: object, **kwargs: object) -> object:
        counter["n"] += 1
        if counter["n"] == 2:
            raise sqlite3.OperationalError("simulated mid-apply failure")
        return real_log(*args, **kwargs)

    monkeypatch.setattr(svc._transactions, "log", flaky_log)

    assert coll.collection_id is not None
    with pytest.raises(sqlite3.OperationalError):
        svc.apply_proposal(proposal=proposal, collection_id=coll.collection_id)

    # Rollback total: ARG-1 sigue en 3, no hay transactions.
    inv = InventoryRepository(conn)
    arg = inv.get_by_card_id(ids[("ARG", 1)])
    assert arg is not None and arg.quantity == 3
    rows = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert rows[0] == 0


def test_apply_with_empty_proposal_is_noop(
    setup: tuple[sqlite3.Connection, Collection, dict[tuple[str, int], int]],
) -> None:
    """Propuesta vacía no rompe ni genera transactions."""
    conn, coll, _ = setup
    proposal = ExchangeProposal(cards_to_give=(), cards_to_receive=())
    assert coll.collection_id is not None
    result = ExchangeApplyService(conn).apply_proposal(
        proposal=proposal, collection_id=coll.collection_id
    )
    assert result.given_count == 0
    assert result.received_count == 0
    rows = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert rows[0] == 0
