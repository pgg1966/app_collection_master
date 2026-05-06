"""Tests de la MainWindow — orquestación de selector + detail + empty state."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.collections.collection_detail_view import (
    CollectionDetailView,
)
from collections_app.views.main_window import MainWindow

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def empty_ctx() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        yield ctx
    finally:
        ctx.close()


@pytest.fixture
def seeded_ctx() -> Iterator[AppContext]:
    """Context con 2 colecciones distintas para probar el switch."""
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(CodeHeader(code_header_id=None, code_header_name="World"))
        assert h.code_header_id is not None
        coll_a = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Alpha",
                card_count=1,
                requires_code=False,
                code_field_name=None,
                code_header_id=h.code_header_id,
            )
        )
        coll_b = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Beta",
                card_count=1,
                requires_code=False,
                code_field_name=None,
                code_header_id=h.code_header_id,
            )
        )
        assert coll_a.collection_id is not None
        assert coll_b.collection_id is not None
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll_a.collection_id,
                code_id="X",
                card_number=1,
                card_name="A1",
            )
        )
        ctx.cards.create(
            Card(
                card_id=None,
                collection_id=coll_b.collection_id,
                code_id="X",
                card_number=1,
                card_name="B1",
            )
        )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


# ---------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------


def test_main_window_shows_empty_state_when_no_collections(
    qtbot,  # type: ignore[no-untyped-def]
    empty_ctx: AppContext,
) -> None:
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    assert win.is_showing_empty_state() is True
    assert win.active_detail is None


def test_main_window_title_default_no_profile(
    qtbot,  # type: ignore[no-untyped-def]
    empty_ctx: AppContext,
) -> None:
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    assert win.windowTitle() == "Collections"


def test_main_window_title_with_profile_suffix(
    qtbot,  # type: ignore[no-untyped-def]
    empty_ctx: AppContext,
) -> None:
    win = MainWindow(ctx=empty_ctx, title_suffix=" — [demo]")
    qtbot.addWidget(win)
    assert win.windowTitle() == "Collections — [demo]"


# ---------------------------------------------------------------------
# Carga inicial con colecciones
# ---------------------------------------------------------------------


def test_main_window_auto_selects_first_collection(
    qtbot,  # type: ignore[no-untyped-def]
    seeded_ctx: AppContext,
) -> None:
    """Con >=1 colección, MainWindow ya muestra el detail de la primera."""
    win = MainWindow(ctx=seeded_ctx)
    qtbot.addWidget(win)
    assert win.is_showing_empty_state() is False
    detail = win.active_detail
    assert detail is not None
    assert isinstance(detail, CollectionDetailView)
    assert detail.collection.collection_name == "Alpha"


def test_main_window_switching_collection_destroys_previous_detail(
    qtbot,  # type: ignore[no-untyped-def]
    seeded_ctx: AppContext,
) -> None:
    """Al cambiar de colección, el detail anterior se elimina del stack."""
    win = MainWindow(ctx=seeded_ctx)
    qtbot.addWidget(win)
    first = win.active_detail
    assert first is not None

    # Buscar el item Beta en el selector y emitir.
    listw = win.selector._list
    beta_row = next(i for i in range(listw.count()) if listw.item(i).text() == "Beta")
    item = listw.item(beta_row)
    win.selector._list.itemActivated.emit(item)

    second = win.active_detail
    assert second is not None
    assert second is not first  # objeto distinto: se recreó.
    assert second.collection.collection_name == "Beta"


def test_main_window_csv_menu_opens_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    """La acción 'Nueva colección desde CSV...' abre `CsvImportDialog`.

    Se mockea `CsvImportDialog.exec` para no bloquear en un dialog modal."""
    exec_calls: list[object] = []

    def fake_exec(self: object) -> int:
        exec_calls.append(self)
        return 0

    monkeypatch.setattr(
        "collections_app.views.admin.csv_import_dialog.CsvImportDialog.exec",
        fake_exec,
    )

    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    win._open_csv_import_dialog()
    assert len(exec_calls) == 1


def test_main_window_refreshes_sidebar_on_import_completed(
    qtbot,  # type: ignore[no-untyped-def]
    empty_ctx: AppContext,
    tmp_path: object,  # noqa: ARG001
) -> None:
    """Tras `import_completed`, el sidebar refresca y selecciona la primera
    colección si la DB estaba vacía (saliendo del empty state)."""
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    assert win.is_showing_empty_state() is True
    assert win.selector.is_empty() is True

    # Simulamos un import exitoso creando la collection vía service y
    # disparando manualmente el slot que la MainWindow conecta al signal.
    from collections_app.core.models.code_header import CodeHeader
    from collections_app.core.models.collection import Collection

    h = empty_ctx.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="H", code_max_length=3)
    )
    assert h.code_header_id is not None
    empty_ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="Imported",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    empty_ctx.conn.commit()

    win._on_import_completed({})
    assert win.selector.is_empty() is False
    assert win.is_showing_empty_state() is False
    assert win.active_detail is not None
