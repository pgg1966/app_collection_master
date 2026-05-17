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
from PySide6.QtCore import QMimeData, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.inventory.card_loader import CardLoaderView, _CodeLineEdit

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
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    assert view.collection.collection_name == "WC"


def test_set_active_collection_changes_state(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """`set_active_collection` reconfigura sin crashear."""
    view = CardLoaderView(ctx=app_ctx, collection=collection)
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
    view = CardLoaderView(ctx=app_ctx, collection=collection)
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
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view._selected_code_id = "ARG"
    view._code_edit.setText("ARG")
    view._number_input.setText("999")  # no existe
    view._qty_input.setText("1")

    with qtbot.assertNotEmitted(view.card_changed):
        view._save_card()


def test_remove_card_below_zero_shows_error(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Una baja sin stock debe mostrar error de domain (InventoryError).

    La confirmación de baja (5.5/E4) se mockea con Yes para que el flow
    llegue al `_dispatch_save` y ahí pegue contra el límite de stock.
    """
    # Estado inicial: stock = 1.
    app_ctx.inventory.add_card(collection.collection_id or 0, "ARG", 10, 1)
    app_ctx.conn.commit()

    monkeypatch.setattr(
        "collections_app.views.inventory.card_loader.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )

    view = CardLoaderView(ctx=app_ctx, collection=collection)
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


def test_baja_confirmation_cancel_does_not_emit_signal(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """5.5/E4: si el user cancela el confirm de baja, no se aplica."""
    app_ctx.inventory.add_card(collection.collection_id or 0, "ARG", 10, 5)
    app_ctx.conn.commit()

    monkeypatch.setattr(
        "collections_app.views.inventory.card_loader.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.No,
    )

    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view._baja_radio.setChecked(True)
    view._selected_code_id = "ARG"
    view._code_edit.setText("ARG")
    view._number_input.setText("10")
    view._qty_input.setText("1")

    with qtbot.assertNotEmitted(view.card_changed):
        view._save_card()

    # Stock intacto.
    item = app_ctx.inventory.get_inventory_for_card(collection.collection_id or 0, "ARG", 10)
    assert item is not None
    assert item.quantity == 5


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    """Garantiza un QApplication único por proceso."""
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


def test_card_loader_no_longer_embeds_inventory_import_panel(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
) -> None:
    """Prompt 6: el panel se movió a `CargasTab` como frame independiente.

    `CardLoaderView` ya no tiene `_import_panel` — el split horizontal
    interno se eliminó y el form vive solo en el frame "Manual" del
    `CargasTab`.
    """
    coll = app_ctx.collections.list_all()[0]
    view = CardLoaderView(ctx=app_ctx, collection=coll)
    qtbot.addWidget(view)
    assert not hasattr(view, "_import_panel")


# ----------------------------------------------------------------------
# Restricciones de input en el campo de Código (aisladas al widget)
# ----------------------------------------------------------------------
#
# Estos tests instancian `_CodeLineEdit` directo, no la `CardLoaderView`,
# para evitar interferencia con la lógica de auto-tab del view
# (que avanza foco al campo número cuando hay un match único de code_id).


def test_code_field_rejects_digits_and_specials(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    """Tipear "a1b2c3!" deja "ABC": dígitos y especiales descartados silenciosamente."""
    edit = _CodeLineEdit()
    qtbot.addWidget(edit)
    edit.setFocus()
    QTest.keyClicks(edit, "a1b2c3!")
    assert edit.text() == "ABC"


def test_code_field_auto_uppercases_typing(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    """Tipear minúsculas muestra el display en mayúsculas."""
    edit = _CodeLineEdit()
    qtbot.addWidget(edit)
    edit.setFocus()
    QTest.keyClicks(edit, "arg")
    assert edit.text() == "ARG"


def test_code_field_paste_filters_and_uppercases(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    """Pegar "arg123" → queda "ARG"; insertFromMimeData filtra dígitos y upper-casea."""
    edit = _CodeLineEdit()
    qtbot.addWidget(edit)
    mime = QMimeData()
    mime.setText("arg123")
    edit.insertFromMimeData(mime)
    assert edit.text() == "ARG"


def test_code_field_paste_only_digits_is_noop(
    qtbot,  # type: ignore[no-untyped-def]
) -> None:
    """Pegar texto sin letras no inserta nada (no rompe el campo)."""
    edit = _CodeLineEdit()
    qtbot.addWidget(edit)
    mime = QMimeData()
    mime.setText("123!@#")
    edit.insertFromMimeData(mime)
    assert edit.text() == ""


# ----------------------------------------------------------------------
# Navegación con Tab / Shift+Tab y bloqueo de avance con campo vacío
# ----------------------------------------------------------------------


def test_empty_code_tab_does_not_advance(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Tab con código vacío no debe mover foco al número."""
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    QTest.keyClick(view._code_edit, Qt.Key.Key_Tab)
    assert not view._number_input.hasFocus()


def test_empty_code_enter_does_not_advance(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Enter con código vacío no debe mover foco al número."""
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    QTest.keyClick(view._code_edit, Qt.Key.Key_Return)
    assert not view._number_input.hasFocus()


def test_empty_code_does_not_flash_red(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Spec: Enter/Tab con código vacío no muestra ningún feedback de error.

    El stylesheet del campo no debe contener `border: 1px solid red`
    después de presionar Tab o Enter con el campo vacío.
    """
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    QTest.keyClick(view._code_edit, Qt.Key.Key_Tab)
    QTest.keyClick(view._code_edit, Qt.Key.Key_Return)
    assert "red" not in view._code_edit.styleSheet()


def test_tab_advances_like_enter_when_code_present(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Con código presente, Tab debe mover foco al número (igual que Enter).

    Usamos `setText` programático para evitar que el auto-tab del view
    (gatillado en `textEdited` cuando hay 1 match único por code_id)
    interfiera con la verificación del Tab manual.
    """
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setText("ARG")
    view._code_edit.setFocus()
    QTest.keyClick(view._code_edit, Qt.Key.Key_Tab)
    assert view._number_input.hasFocus()


def test_shift_tab_retrocedes_from_number_to_code(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Shift+Tab desde el campo número debe volver al de código."""
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._number_input.setFocus()
    QTest.keyClick(view._number_input, Qt.Key.Key_Backtab)
    assert view._code_edit.hasFocus()


def test_shift_tab_from_empty_number_still_retrocedes(
    qtbot,  # type: ignore[no-untyped-def]
    app_ctx: AppContext,
    collection: Collection,
) -> None:
    """Backtab debe permitirse aun con campo vacío (corrección de typos)."""
    view = CardLoaderView(ctx=app_ctx, collection=collection)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._number_input.setFocus()
    assert view._number_input.text() == ""
    QTest.keyClick(view._number_input, Qt.Key.Key_Backtab)
    assert view._code_edit.hasFocus()
