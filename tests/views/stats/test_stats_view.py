"""Tests del StatsView + helper _percentage."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.stats.stats_view import StatsView, _percentage

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


# ---------------------------------------------------------------------
# Helper puro (sin Qt)
# ---------------------------------------------------------------------


def test_percentage_zero_total_returns_zero() -> None:
    """División por cero protegida."""
    assert _percentage(0, 0) == 0.0
    assert _percentage(5, 0) == 0.0


def test_percentage_normal_case() -> None:
    assert _percentage(1, 4) == 25.0
    assert _percentage(3, 4) == 75.0


def test_percentage_capped_at_100_when_owned_exceeds_total() -> None:
    """owned > total (caso edge — no debería pasar) → cap 100."""
    assert _percentage(10, 5) == 100.0


def test_percentage_full_collection() -> None:
    assert _percentage(20, 20) == 100.0


# ---------------------------------------------------------------------
# Vista
# ---------------------------------------------------------------------


@pytest.fixture
def ctx_with_data() -> Iterator[tuple[AppContext, Collection]]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        for code, name, order in [
            ("ARG", "Argentina", 1),
            ("BRA", "Brasil", 2),
        ]:
            ctx.code_lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=h.code_header_id,
                    code_id=code,
                    code_name=name,
                    code_order=order,
                )
            )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="WC2026",
                card_count=4,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        for code, num in [("ARG", 1), ("ARG", 2), ("BRA", 1), ("BRA", 2)]:
            ctx.cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=num,
                    card_name=f"{code}-{num}",
                )
            )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


def test_stats_view_constructs_with_table_populated(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_data
    view = StatsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    # 2 codes seedeados.
    assert view._table.rowCount() == 2


def test_stats_view_shows_zero_owned_initially(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_data
    view = StatsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    for row in range(view._table.rowCount()):
        assert view._table.item(row, 3).text() == "0"
        assert view._table.item(row, 4).text() == "0%"


def test_stats_view_reflects_quantities_after_alta(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_data
    cid = coll.collection_id or 0
    ctx.inventory.add_card(cid, "ARG", 1, 1)
    ctx.inventory.add_card(cid, "BRA", 1, 1)
    ctx.inventory.add_card(cid, "BRA", 2, 1)
    ctx.conn.commit()

    view = StatsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    # ARG: 1/2 = 50%, BRA: 2/2 = 100%
    by_code = {}
    for row in range(view._table.rowCount()):
        code = view._table.item(row, 0).text()
        owned = int(view._table.item(row, 3).text())
        pct = view._table.item(row, 4).text()
        by_code[code] = (owned, pct)
    assert by_code["ARG"] == (1, "50%")
    assert by_code["BRA"] == (2, "100%")


def test_stats_view_footer_shows_global_totals(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_data
    cid = coll.collection_id or 0
    ctx.inventory.add_card(cid, "ARG", 1, 1)
    ctx.conn.commit()

    view = StatsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    footer = view._footer_label.text()
    # 4 cards totales, 1 owned → 25% global
    assert "4" in footer
    assert "1" in footer
    assert "25%" in footer


def test_stats_view_set_active_collection_swaps(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_data: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_with_data
    other = ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="Other",
            card_count=0,
            requires_code=False,
            code_field_name=None,
            code_header_id=coll.code_header_id,
        )
    )
    ctx.conn.commit()
    view = StatsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    assert view._table.rowCount() == 2
    view.set_active_collection(other)
    assert view._table.rowCount() == 0
