"""Tests del sidebar de selección de colección."""

from __future__ import annotations

import pytest

from collections_app.app_context import AppContext
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.collections.collection_selector import (
    CollectionSelectorView,
)

pytestmark = pytest.mark.gui


def test_selector_lists_all_collections(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    assert view._list.count() == 1
    assert view._list.item(0).text() == "WC"


def test_selector_empty_when_no_collections(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    """DB vacía → selector vacío. is_empty() True."""
    from collections_app.app_context import create_app_context

    ctx = create_app_context(":memory:")
    try:
        view = CollectionSelectorView(collections_service=ctx.collections)
        qtbot.addWidget(view)
        assert view._list.count() == 0
        assert view.is_empty() is True
    finally:
        ctx.close()


def test_selector_emits_signal_on_double_click(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    item = view._list.item(0)
    with qtbot.waitSignal(view.collection_selected, timeout=1000) as blocker:
        view._list.itemDoubleClicked.emit(item)
    coll = blocker.args[0]
    assert isinstance(coll, Collection)
    assert coll.collection_name == "WC"


def test_selector_emits_via_open_button(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    """Click en 'Abrir' con una fila seleccionada emite el signal."""
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    with qtbot.waitSignal(view.collection_selected, timeout=1000):
        view._open_btn.click()


def test_selector_open_button_with_no_selection_does_nothing(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    """Sin fila seleccionada, 'Abrir' no debe emitir."""
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    view._list.clearSelection()
    view._list.setCurrentRow(-1)
    with qtbot.assertNotEmitted(view.collection_selected):
        view._open_btn.click()


def test_selector_select_first_emits_and_returns(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    with qtbot.waitSignal(view.collection_selected, timeout=1000):
        coll = view.select_first()
    assert coll is not None
    assert coll.collection_name == "WC"


def test_selector_select_first_returns_none_when_empty(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    from collections_app.app_context import create_app_context

    ctx = create_app_context(":memory:")
    try:
        view = CollectionSelectorView(collections_service=ctx.collections)
        qtbot.addWidget(view)
        assert view.select_first() is None
    finally:
        ctx.close()


def test_selector_emits_on_single_click_via_current_item_changed(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    """Click simple en una fila distinta dispara `currentItemChanged` →
    emit del signal. Bug heredado: sin esta conexión, el detail view
    no se refrescaba al cambiar de colección con un click."""
    # Seedear una segunda collection para tener >=2 filas en el sidebar.
    other_h = ctx_with_demo.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="Other")
    )
    assert other_h.code_header_id is not None
    ctx_with_demo.collections.create(
        Collection(
            collection_id=None,
            collection_name="Magic",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    ctx_with_demo.conn.commit()

    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    assert view._list.count() == 2
    name0 = view._list.item(0).text()
    name1 = view._list.item(1).text()
    assert name0 != name1

    # Establecer current inicial sin asertar el primer signal.
    view._list.setCurrentRow(0)

    # Cambiar a la fila 1 — debe emitir con la collection de esa fila.
    captured: list[Collection] = []
    view.collection_selected.connect(captured.append)
    view._list.setCurrentRow(1)
    assert len(captured) == 1
    assert captured[0].collection_name == name1

    # Volver a la fila 0 — debe emitir la 1ra.
    view._list.setCurrentRow(0)
    assert len(captured) == 2
    assert captured[1].collection_name == name0


def test_selector_select_first_emits_only_once(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    """`select_first()` emite exactamente 1 vez (vía currentItemChanged),
    sin la doble emisión del bug original."""
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    captured: list[Collection] = []
    view.collection_selected.connect(captured.append)
    view.select_first()
    assert len(captured) == 1
    assert captured[0].collection_name == "WC"


def test_selector_refresh_picks_up_new_collection(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
) -> None:
    view = CollectionSelectorView(collections_service=ctx_with_demo.collections)
    qtbot.addWidget(view)
    assert view._list.count() == 1

    other_h = ctx_with_demo.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="Other")
    )
    assert other_h.code_header_id is not None
    ctx_with_demo.collections.create(
        Collection(
            collection_id=None,
            collection_name="Magic",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    ctx_with_demo.conn.commit()

    view.refresh()
    assert view._list.count() == 2
