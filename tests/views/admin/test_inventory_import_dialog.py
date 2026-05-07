"""Smoke tests del InventoryImportDialog (wrapper modal del panel).

Tras Prompt 5b, la lógica detallada del importer vive en
`InventoryImportPanel`. El dialog es un thin wrapper que solo embebe
el panel y re-emite el signal `import_completed`. Acá testeamos solo
ese contrato — los tests detallados están en `test_inventory_import_panel.py`.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.aggregates.inventory_import_report import (
    InventoryImportReport,
)
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.admin.inventory_import_dialog import (
    InventoryImportDialog,
    InventoryImportPanel,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_collection() -> Iterator[tuple[AppContext, Collection]]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Demo",
                card_count=0,
                requires_code=False,
                code_field_name=None,
                code_header_id=h.code_header_id,
            )
        )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


def test_dialog_embeds_panel(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    """El wrapper modal contiene una instancia de InventoryImportPanel."""
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)
    assert isinstance(dialog._panel, InventoryImportPanel)


def test_dialog_reemits_panel_import_completed_signal(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collection: tuple[AppContext, Collection],
) -> None:
    """Cuando el panel emite import_completed, el dialog lo re-emite."""
    ctx, coll = ctx_with_collection
    dialog = InventoryImportDialog(ctx=ctx, collection=coll)
    qtbot.addWidget(dialog)

    captured: list[InventoryImportReport] = []
    dialog.import_completed.connect(lambda r: captured.append(r))

    fake_report = InventoryImportReport(rows_total=0, rows_applied=0, rows_skipped=0)
    dialog._panel.import_completed.emit(fake_report)
    assert captured == [fake_report]
