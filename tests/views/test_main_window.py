"""Tests de la MainWindow — orquestación de selector + detail + empty state."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.collections.collection_detail_view import (
    CollectionDetailView,
)
from collections_app.views.main_window import MainWindow


def _admin_actions(win: MainWindow) -> tuple[QAction, QAction, QAction]:
    """Devuelve (cards, collections, codes) buscando en el menú
    "Administración" por título de acción (sin mnemonic `&`)."""
    admin_menu = next(
        m
        for m in win.menuBar().findChildren(QMenu)
        if m.title().replace("&", "") == "Administración"
    )
    by_label = {a.text().replace("&", "").rstrip("."): a for a in admin_menu.actions()}
    return by_label["Cards"], by_label["Colecciones"], by_label["Códigos"]


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


def test_main_window_inventory_import_without_active_collection_shows_warning(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    """Sin colección activa, 'Importar inventario...' muestra warning y
    NO abre el dialog (no hay collection target)."""
    info_msgs: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.main_window.QMessageBox.information",
        lambda _p, _t, msg: info_msgs.append(msg) or 0,
    )
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    assert win.active_detail is None
    win._open_inventory_import_dialog()
    assert len(info_msgs) == 1
    assert "Seleccioná" in info_msgs[0]


def test_main_window_admin_cards_menu_opens_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    exec_calls: list[object] = []
    monkeypatch.setattr(
        "collections_app.views.admin.cards_abm.CardsAbmView.exec",
        lambda self: exec_calls.append(self) or 0,
    )
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    win._open_cards_abm()
    assert len(exec_calls) == 1


def test_main_window_admin_collections_menu_opens_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    exec_calls: list[object] = []
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.CollectionsAbmView.exec",
        lambda self: exec_calls.append(self) or 0,
    )
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    win._open_collections_abm()
    assert len(exec_calls) == 1


def test_main_window_admin_codes_menu_opens_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    exec_calls: list[object] = []
    monkeypatch.setattr(
        "collections_app.views.admin.codes_master_detail.CodesMasterDetailView.exec",
        lambda self: exec_calls.append(self) or 0,
    )
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    win._open_codes_master_detail()
    assert len(exec_calls) == 1


def test_main_window_collections_abm_discards_active_detail_if_collection_deleted(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    """Si la ABM borra la collection activa, el detail se descarta."""
    h = empty_ctx.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="H", code_max_length=3)
    )
    assert h.code_header_id is not None
    empty_ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="ToDelete",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    empty_ctx.conn.commit()

    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    assert win.active_detail is not None
    active_id = win.active_detail.collection.collection_id
    assert active_id is not None

    def fake_exec(self: object) -> int:
        empty_ctx.collections.delete(active_id)
        empty_ctx.conn.commit()
        return 0

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.CollectionsAbmView.exec",
        fake_exec,
    )
    win._open_collections_abm()
    # El bloque post-cierre (refresh selector + discard) se difiere con
    # QTimer.singleShot(0, ...) para evitar deadlock con el teardown del
    # modal — esperamos al próximo tick del event loop antes de aserciones.
    qtbot.waitUntil(lambda: win.active_detail is None, timeout=500)
    assert win.selector.is_empty() is True


# ---------------------------------------------------------------------
# Modo admin condicional vía COLLECTIONS_ADMIN
# ---------------------------------------------------------------------


def test_admin_menu_disabled_without_env_var(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    """Sin COLLECTIONS_ADMIN seteado, las 3 acciones admin quedan disabled."""
    monkeypatch.delenv("COLLECTIONS_ADMIN", raising=False)
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    for action in _admin_actions(win):
        assert action.isEnabled() is False
        assert "COLLECTIONS_ADMIN" in action.toolTip()


def test_admin_menu_enabled_with_env_var(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    empty_ctx: AppContext,
) -> None:
    """Con COLLECTIONS_ADMIN=1, las 3 acciones admin quedan enabled."""
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    win = MainWindow(ctx=empty_ctx)
    qtbot.addWidget(win)
    for action in _admin_actions(win):
        assert action.isEnabled() is True
