"""Smoke tests del LoaderTab — wrapper con sub-tabs Manual + Por foto."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.inventory.loader_tab import LoaderTab
from collections_app.views.inventory.ocr_loader_tab import OcrLoaderTab

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_and_collection() -> Iterator[tuple[AppContext, Collection]]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Mundial",
                card_count=10,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


def test_loader_tab_has_two_sub_tabs(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    tab = LoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._inner_tabs.count() == 2
    titles = [tab._inner_tabs.tabText(i) for i in range(tab._inner_tabs.count())]
    assert titles == ["Manual", "Por foto"]
    assert isinstance(tab.manual, CardLoaderView)
    assert isinstance(tab.ocr, OcrLoaderTab)


def test_card_changed_re_emits_from_manual_sub_tab(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """El signal del sub-tab Manual sale por el wrapper."""
    ctx, coll = ctx_and_collection
    tab = LoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.card_changed.connect(lambda: received.append(True))
    tab.manual.card_changed.emit()
    assert received == [True]


def test_card_changed_re_emits_from_ocr_sub_tab(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """El signal del sub-tab OCR sale por el wrapper."""
    ctx, coll = ctx_and_collection
    tab = LoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.card_changed.connect(lambda: received.append(True))
    tab.ocr.card_changed.emit()
    assert received == [True]


def test_set_active_collection_propagates_to_both_sub_tabs(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    tab = LoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    other = Collection(
        collection_id=99,
        collection_name="Otra",
        card_count=0,
        requires_code=True,
        code_field_name="X",
        code_header_id=coll.code_header_id,
    )
    tab.set_active_collection(other)
    assert tab.manual.collection is other
    assert tab.ocr._collection is other
