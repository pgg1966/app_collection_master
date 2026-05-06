"""Tests del fix de deadlock al cerrar las ABM administrativas.

`MainWindow._open_*_abm` difieren el refresh post-cierre con
`QTimer.singleShot(0, ...)`. Si lo ejecutaran sincrónicamente,
repueblan tablas grandes mientras Qt todavía está procesando el
teardown del modal — y se traba el event loop.

Estos tests se separaron de `test_main_window.py` para mantener foco:
acá vive el contrato "el refresh es asíncrono, no inmediato".
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views import main_window as main_window_mod
from collections_app.views.main_window import MainWindow

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


def _seed_collection(ctx: AppContext, name: str, n_cards: int) -> int:
    h = ctx.code_headers.create(CodeHeader(code_header_id=None, code_header_name=f"H-{name}"))
    assert h.code_header_id is not None
    coll = ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=n_cards,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    for n in range(n_cards):
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id="A",
                card_number=n + 1,
                card_name=f"card-{n}",
            )
        )
    ctx.conn.commit()
    return coll.collection_id


@pytest.fixture
def small_ctx() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        _seed_collection(ctx, "Demo", n_cards=3)
        yield ctx
    finally:
        ctx.close()


@pytest.fixture
def large_ctx() -> Iterator[AppContext]:
    """Una colección con ~1000 cards. Smoke load — captura regresiones
    de orden de magnitud, no benchmarks finos."""
    ctx = create_app_context(":memory:")
    try:
        _seed_collection(ctx, "Big", n_cards=1000)
        yield ctx
    finally:
        ctx.close()


# ---------------------------------------------------------------------
# Test A: el refresh queda en cola del event loop, no se ejecuta inline.
# ---------------------------------------------------------------------


def test_open_cards_abm_defers_refresh_to_event_loop(
    qtbot,  # type: ignore[no-untyped-def]
    small_ctx: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_window_mod.CardsAbmView,
        "exec",
        lambda self: int(QDialog.DialogCode.Accepted),
    )
    win = MainWindow(ctx=small_ctx)
    qtbot.addWidget(win)
    refresh_spy = MagicMock()
    monkeypatch.setattr(win, "_refresh_active_detail", refresh_spy)

    win._open_cards_abm()
    assert refresh_spy.call_count == 0, "refresh debería estar diferido, no inmediato"
    qtbot.wait(50)
    assert refresh_spy.call_count == 1


def test_open_codes_abm_defers_refresh_to_event_loop(
    qtbot,  # type: ignore[no-untyped-def]
    small_ctx: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_window_mod.CodesMasterDetailView,
        "exec",
        lambda self: int(QDialog.DialogCode.Accepted),
    )
    win = MainWindow(ctx=small_ctx)
    qtbot.addWidget(win)
    refresh_spy = MagicMock()
    monkeypatch.setattr(win, "_refresh_active_detail", refresh_spy)

    win._open_codes_master_detail()
    assert refresh_spy.call_count == 0
    qtbot.wait(50)
    assert refresh_spy.call_count == 1


def test_open_collections_abm_defers_post_close_block_to_event_loop(
    qtbot,  # type: ignore[no-untyped-def]
    small_ctx: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """En collections el bloque diferido es más grande (selector +
    discard/refresh). Spy del helper agrupador `_after_collections_abm_close`."""
    monkeypatch.setattr(
        main_window_mod.CollectionsAbmView,
        "exec",
        lambda self: int(QDialog.DialogCode.Accepted),
    )
    win = MainWindow(ctx=small_ctx)
    qtbot.addWidget(win)
    after_spy = MagicMock()
    monkeypatch.setattr(win, "_after_collections_abm_close", after_spy)

    win._open_collections_abm()
    assert after_spy.call_count == 0
    qtbot.wait(50)
    assert after_spy.call_count == 1


# ---------------------------------------------------------------------
# Test B: smoke con dataset grande — el ciclo completa en tiempo
# razonable. No es benchmark; captura regresiones de orden de magnitud.
# ---------------------------------------------------------------------


_LARGE_DATASET_TIMEOUT_MS = 10000


def test_open_cards_abm_with_1000_cards_completes_under_threshold(
    qtbot,  # type: ignore[no-untyped-def]
    large_ctx: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        main_window_mod.CardsAbmView,
        "exec",
        lambda self: int(QDialog.DialogCode.Accepted),
    )
    win = MainWindow(ctx=large_ctx)
    qtbot.addWidget(win)

    completed: list[bool] = []
    original_refresh = win._refresh_active_detail

    def wrapped_refresh() -> None:
        original_refresh()
        completed.append(True)

    monkeypatch.setattr(win, "_refresh_active_detail", wrapped_refresh)

    t0 = time.perf_counter()
    win._open_cards_abm()
    qtbot.waitUntil(lambda: bool(completed), timeout=_LARGE_DATASET_TIMEOUT_MS)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    assert (
        elapsed_ms < _LARGE_DATASET_TIMEOUT_MS
    ), f"Took {elapsed_ms:.0f}ms with 1000 cards; threshold {_LARGE_DATASET_TIMEOUT_MS}ms"
