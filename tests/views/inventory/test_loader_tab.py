"""Smoke tests del CargasTab — wrapper con 3 frames (Prompt 6)."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGroupBox, QSplitter

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.admin.inventory_import_dialog import InventoryImportPanel
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.inventory.loader_tab import CargasTab
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


def test_cargas_tab_has_three_panels(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Manual + Importer + OCR, accesibles vía properties."""
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert isinstance(tab.manual, CardLoaderView)
    assert isinstance(tab.importer, InventoryImportPanel)
    assert isinstance(tab.ocr, OcrLoaderTab)


def test_cargas_tab_uses_two_splitters(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Splitter horizontal (Manual/Importer) anidado en uno vertical (top/OCR)."""
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    splitters = tab.findChildren(QSplitter)
    orientations = {s.orientation() for s in splitters}
    assert Qt.Orientation.Horizontal in orientations
    assert Qt.Orientation.Vertical in orientations


def test_cargas_tab_wraps_each_panel_in_groupbox(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Cada panel está envuelto en un QGroupBox con su título."""
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    titles = {g.title() for g in tab.findChildren(QGroupBox)}
    # Los títulos van pasados por `tr()`, pero sin traducción quedan igual.
    assert "Manual" in titles
    assert "Por archivo" in titles
    assert "Cargar desde fotos (OCR)" in titles


def test_card_changed_re_emits_from_manual_panel(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.card_changed.connect(lambda: received.append(True))
    tab.manual.card_changed.emit()
    assert received == [True]


def test_card_changed_re_emits_from_ocr_panel(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.card_changed.connect(lambda: received.append(True))
    tab.ocr.card_changed.emit()
    assert received == [True]


def test_card_changed_re_emits_from_importer_panel(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """`import_completed(dict)` del importer → `card_changed()` del tab."""
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    received: list[bool] = []
    tab.card_changed.connect(lambda: received.append(True))
    # `import_completed` lleva un dict — el adapter en CargasTab lo
    # descarta y emite card_changed() sin payload.
    tab.importer.import_completed.emit({})
    assert received == [True]


def test_set_active_collection_propagates_to_all_three(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    tab = CargasTab(ctx=ctx, collection=coll)
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
    # InventoryImportPanel guarda la collection internamente; al menos
    # verificar que el método se invocó sin error.
