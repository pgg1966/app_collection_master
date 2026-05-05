"""Tests de integración de la vista preservada CardLoaderView.

Marca `gui` (configurada en pyproject) — pueden requerir display.
Cada test construye un AppContext contra `:memory:` con una colección
seedeada y prueba un flujo end-to-end (vista → service → repos → DB).

NO testean cada slot individualmente: la vista es código preservado de
v0.1 y su lógica interna no se modifica. Estos tests son la red de
seguridad de "no rompí nada en la integración".
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.inventory.card_loader import CardLoaderView

pytestmark = pytest.mark.gui


@pytest.fixture
def app_ctx() -> Iterator[AppContext]:
    """Context con header + collection (requires_code=True) + 2 cards."""
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(CodeHeader(code_header_id=None, code_header_name="World"))
        assert h.code_header_id is not None
        ctx.code_lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="ARG",
                code_name="Argentina",
            )
        )
        ctx.code_lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="BRA",
                code_name="Brasil",
            )
        )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="WC",
                card_count=10,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id="ARG",
                card_number=10,
                card_name="Messi",
            )
        )
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id="BRA",
                card_number=10,
                card_name="Neymar",
            )
        )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


@pytest.fixture
def collection(app_ctx: AppContext) -> Collection:
    items = app_ctx.collections.list_all()
    assert len(items) == 1
    return items[0]


def test_card_loader_view_constructs(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """La vista se construye sin lanzar excepciones con el service nuevo."""
    view = CardLoaderView(service=app_ctx.inventory, collection=collection)
    qtbot.addWidget(view)
    assert view.collection.collection_name == "WC"


def test_set_active_collection_changes_state(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """`set_active_collection` reconfigura sin crashear."""
    view = CardLoaderView(service=app_ctx.inventory, collection=collection)
    qtbot.addWidget(view)

    other_header = app_ctx.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="Other")
    )
    assert other_header.code_header_id is not None
    other = app_ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="WithoutCode",
            card_count=5,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_header.code_header_id,
        )
    )
    view.set_active_collection(other)
    assert view.collection.collection_name == "WithoutCode"


def test_save_card_emits_card_changed_signal(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """End-to-end: completar el form y guardar dispara card_changed
    y persiste el inventario via la cadena vista → service → DB."""
    view = CardLoaderView(service=app_ctx.inventory, collection=collection)
    qtbot.addWidget(view)
    # Setear el código manualmente (saltamos el flow del completer para
    # mantener el test enfocado en la integración con el service).
    view._selected_code_id = "ARG"
    view._code_edit.setText("ARG")
    view._number_input.setText("10")
    view._qty_input.setText("3")

    with qtbot.waitSignal(view.card_changed, timeout=1000):
        view._save_card()

    # Verificación de persistencia: inventory para ARG-10 = 3.
    item = app_ctx.inventory.get_inventory_for_card(collection.collection_id or 0, "ARG", 10)
    assert item is not None
    assert item.quantity == 3


def test_save_unknown_card_does_not_emit_signal(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Card que no existe debe mostrar error sin emitir card_changed."""
    view = CardLoaderView(service=app_ctx.inventory, collection=collection)
    qtbot.addWidget(view)
    view._selected_code_id = "ARG"
    view._code_edit.setText("ARG")
    view._number_input.setText("999")  # no existe
    view._qty_input.setText("1")

    with qtbot.assertNotEmitted(view.card_changed):
        view._save_card()


def test_remove_card_below_zero_shows_error(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Una baja sin stock debe mostrar error de domain (InventoryError)."""
    # Estado inicial: stock = 1.
    app_ctx.inventory.add_card(collection.collection_id or 0, "ARG", 10, 1)
    app_ctx.conn.commit()

    view = CardLoaderView(service=app_ctx.inventory, collection=collection)
    qtbot.addWidget(view)
    view._baja_radio.setChecked(True)
    view._selected_code_id = "ARG"
    view._code_edit.setText("ARG")
    view._number_input.setText("10")
    view._qty_input.setText("5")  # >stock

    with qtbot.assertNotEmitted(view.card_changed):
        view._save_card()

    # Stock no se movió.
    item = app_ctx.inventory.get_inventory_for_card(collection.collection_id or 0, "ARG", 10)
    assert item is not None
    assert item.quantity == 1


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    """Garantiza un QApplication único por proceso."""
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]
