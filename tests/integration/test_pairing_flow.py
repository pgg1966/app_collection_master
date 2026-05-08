"""Integration test end-to-end del pairing `.colexchange` (Prompt 5a).

Simula dos usuarios A y B con DBs `:memory:` independientes, donde:

- Cada uno tiene la misma collection sembrada con el mismo catálogo.
- Cada uno tiene un inventario distinto (faltantes y duplicados
  complementarios).
- Usuario A exporta su `.colexchange` a un `tmp_path`.
- Usuario B importa el archivo, calcula matching, y aplica la
  propuesta a su DB.
- Verificamos que las quantities finales en B son correctas y que
  todas las transactions del intercambio comparten el mismo
  `exchange_event_id`.

Cubre el contrato cross-service: signing → export → import → matching
→ apply funcionan juntos como esperado.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from collections_app.app_context import AppContext, create_app_context
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
from collections_app.services.exchange_export_service import ExchangeExportService
from collections_app.services.exchange_import_service import ExchangeImportService
from collections_app.services.matching_service import MatchingService


def _seed_collection(
    conn: sqlite3.Connection,
    *,
    cards: list[tuple[str, int, str]],
) -> tuple[Collection, dict[tuple[str, int], int]]:
    """Crea collection 'Mundial' con las cards listadas."""
    headers = CodeHeadersRepository(conn)
    lines = CodeLinesRepository(conn)
    collections = CollectionsRepository(conn)
    cards_repo = CardsRepository(conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3))
    assert h.code_header_id is not None
    seen_codes: set[str] = set()
    for code, _, _ in cards:
        if code in seen_codes:
            continue
        seen_codes.add(code)
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
            card_count=len(cards),
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    ids: dict[tuple[str, int], int] = {}
    for code, num, name in cards:
        c = cards_repo.create(
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
    conn.commit()
    return coll, ids


@pytest.fixture
def two_users_setup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[AppContext, AppContext, Path]]:
    """Dos AppContext independientes (A y B) + redirección de Downloads a tmp_path."""
    ctx_a = create_app_context(":memory:")
    ctx_b = create_app_context(":memory:")
    # Redirigir get_downloads_dir al tmp_path (export va a escribir ahí).
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    try:
        yield ctx_a, ctx_b, tmp_path
    finally:
        ctx_a.close()
        ctx_b.close()


def test_full_pairing_flow_end_to_end(
    two_users_setup: tuple[AppContext, AppContext, Path],
) -> None:
    """Flow completo: A exporta → B importa → matching → apply.

    Estado inicial:
    - Catálogo: ARG-1 (Messi), BRA-7 (Neymar), FRA-10 (Mbappé).
    - A tiene: ARG-1 qty=3 (2 duplicados), BRA-7 qty=0 (faltante),
      FRA-10 qty=1 (owned, sin duplicados).
    - B tiene: ARG-1 qty=0 (faltante), BRA-7 qty=4 (3 duplicados),
      FRA-10 qty=2 (1 duplicado).

    Esperado tras el matching desde la perspectiva de B:
    - B necesita ARG-1 (qty 1), A tiene 2 duplicados → B recibe ARG-1.
    - A necesita BRA-7 (qty 1), B tiene 3 duplicados → B entrega BRA-7.
    - FRA-10: ambos tienen owned, B tiene 1 duplicado pero A no lo
      necesita (A tiene FRA-10) → no matchea.

    Tras apply en B:
    - ARG-1 qty=1 (recibida).
    - BRA-7 qty=3 (entregada 1).
    - FRA-10 qty=2 (sin cambios).
    """
    ctx_a, ctx_b, tmp_path = two_users_setup

    # Catálogo idéntico en ambas DBs.
    catalog: list[tuple[str, int, str]] = [
        ("ARG", 1, "Messi"),
        ("BRA", 7, "Neymar"),
        ("FRA", 10, "Mbappé"),
    ]
    coll_a, ids_a = _seed_collection(ctx_a.conn, cards=catalog)
    coll_b, ids_b = _seed_collection(ctx_b.conn, cards=catalog)

    # Inventario inicial.
    inv_a = InventoryRepository(ctx_a.conn)
    inv_b = InventoryRepository(ctx_b.conn)
    inv_a.adjust_quantity(ids_a[("ARG", 1)], 3)
    inv_a.adjust_quantity(ids_a[("FRA", 10)], 1)
    inv_b.adjust_quantity(ids_b[("BRA", 7)], 4)
    inv_b.adjust_quantity(ids_b[("FRA", 10)], 2)
    ctx_a.conn.commit()
    ctx_b.conn.commit()

    # ----- Usuario A: exportar -----
    assert coll_a.collection_id is not None
    file_path = ExchangeExportService(ctx_a.conn).export_to_file(
        collection_id=coll_a.collection_id, user_label="A"
    )
    assert file_path.exists()
    assert file_path.parent == tmp_path

    # ----- Usuario B: importar -----
    import_result = ExchangeImportService(ctx_b.conn).read_from_file(file_path)
    assert import_result.warnings == ()  # mismo catálogo en ambas DBs
    assert import_result.snapshot.user_label == "A"
    assert import_result.local_collection_id == coll_b.collection_id

    # ----- Usuario B: snapshot propio + matching -----
    file_path_b = ExchangeExportService(ctx_b.conn).export_to_file(
        collection_id=coll_b.collection_id, user_label="B"
    )
    snapshot_b = ExchangeImportService(ctx_b.conn).read_from_file(file_path_b).snapshot

    proposal = MatchingService.calculate_proposal(
        my_inventory=snapshot_b,
        their_inventory=import_result.snapshot,
    )

    # B recibe ARG-1.
    assert len(proposal.cards_to_receive) == 1
    receive = proposal.cards_to_receive[0]
    assert (receive.code_id, receive.card_number) == ("ARG", 1)
    assert receive.proposed_quantity == 1  # min(needed=1, available=2)

    # B entrega BRA-7.
    assert len(proposal.cards_to_give) == 1
    give = proposal.cards_to_give[0]
    assert (give.code_id, give.card_number) == ("BRA", 7)
    assert give.proposed_quantity == 1  # min(needed=1, available=3)

    # ----- Usuario B: apply -----
    assert coll_b.collection_id is not None
    result = ExchangeApplyService(ctx_b.conn).apply_proposal(
        proposal=proposal, collection_id=coll_b.collection_id
    )

    # Quantities finales en B.
    arg_b = inv_b.get_by_card_id(ids_b[("ARG", 1)])
    bra_b = inv_b.get_by_card_id(ids_b[("BRA", 7)])
    fra_b = inv_b.get_by_card_id(ids_b[("FRA", 10)])
    assert arg_b is not None and arg_b.quantity == 1
    assert bra_b is not None and bra_b.quantity == 3
    assert fra_b is not None and fra_b.quantity == 2  # sin cambios

    # Reconstrucción del evento via exchange_event_id.
    rows = ctx_b.conn.execute(
        "SELECT operation, quantity FROM transactions WHERE exchange_event_id = ? "
        "ORDER BY transaction_id",
        (result.exchange_event_id,),
    ).fetchall()
    assert len(rows) == 2
    ops = {r[0] for r in rows}
    assert ops == {"alta", "baja"}
