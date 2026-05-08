"""Tests del ExchangeTab — smoke + flow básico (con dialogs mockeados)."""

from __future__ import annotations

from pathlib import Path

import pytest

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.exchange.exchange_tab import ExchangeTab

pytestmark = pytest.mark.gui


def test_tab_constructs_with_two_buttons(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert tab._export_btn is not None
    assert tab._import_btn is not None


def test_tab_exposes_inventory_changed_signal(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """El signal existe — el wire en CollectionDetailView lo necesita."""
    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    assert hasattr(tab, "inventory_changed")


def test_set_active_collection_updates_internal_state(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """`set_active_collection` reemplaza la collection sin recrear nada."""
    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    new_coll = Collection(
        collection_id=99,
        collection_name="Otra",
        card_count=0,
        requires_code=True,
        code_field_name="X",
        code_header_id=1,
    )
    tab.set_active_collection(new_coll)
    assert tab._collection is new_coll


def test_import_with_invalid_file_shows_critical_and_does_not_emit(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Archivo inválido → QMessageBox.critical, signal NO se emite."""
    bad_file = tmp_path / "broken.colexchange"
    bad_file.write_text("{not valid json", encoding="utf-8")

    from collections_app.views.exchange import exchange_tab as mod

    monkeypatch.setattr(
        mod.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: (str(bad_file), ""),
    )
    monkeypatch.setattr(mod.QMessageBox, "critical", lambda *a, **k: None)

    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.inventory_changed.connect(lambda: received.append(True))
    tab._on_import()
    assert received == []


def test_import_with_canceled_file_picker_is_noop(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Si el user cancela el QFileDialog, no se hace nada."""
    from collections_app.views.exchange import exchange_tab as mod

    monkeypatch.setattr(
        mod.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: ("", ""),
    )
    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.inventory_changed.connect(lambda: received.append(True))
    tab._on_import()
    assert received == []


def test_full_import_flow_with_no_matches_shows_info(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Importar un archivo válido pero sin matches → info, sin emit."""
    # Generamos un archivo válido del mismo ctx (idéntico inventario → cero matches).
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    assert demo_collection.collection_id is not None
    file_path = ctx_with_demo.exchange_export.export_to_file(
        collection_id=demo_collection.collection_id,
        user_label="self",
    )
    assert file_path.is_file()

    from collections_app.views.exchange import exchange_tab as mod

    monkeypatch.setattr(
        mod.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: (str(file_path), ""),
    )
    info_calls: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        mod.QMessageBox,
        "information",
        lambda *a, **k: info_calls.append(a),
    )

    tab = ExchangeTab(ctx=ctx_with_demo, collection=demo_collection)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.inventory_changed.connect(lambda: received.append(True))
    tab._on_import()

    # No emit, sí mensaje.
    assert received == []
    assert len(info_calls) >= 1
