"""Tests del ExchangeExportDialog — smoke + flow básico."""

from __future__ import annotations

from pathlib import Path

import pytest

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.exchange.export_dialog import ExchangeExportDialog

pytestmark = pytest.mark.gui


def test_dialog_constructs_with_label_input(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Construcción básica: hay un input de label y un botón Generar."""
    assert demo_collection.collection_id is not None
    dlg = ExchangeExportDialog(ctx=ctx_with_demo, collection_id=demo_collection.collection_id)
    qtbot.addWidget(dlg)
    assert dlg._label_edit is not None
    assert dlg._generate_btn is not None
    assert dlg._cancel_btn is not None


def test_dialog_with_empty_label_calls_service_with_none(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Label vacío → service llamado con `user_label=None`."""
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    captured: dict[str, object] = {}
    real_export = ctx_with_demo.exchange_export.export_to_file

    def spy(**kwargs):  # type: ignore[no-untyped-def]
        captured.update(kwargs)
        return real_export(**kwargs)

    monkeypatch.setattr(ctx_with_demo.exchange_export, "export_to_file", spy)

    assert demo_collection.collection_id is not None
    dlg = ExchangeExportDialog(ctx=ctx_with_demo, collection_id=demo_collection.collection_id)
    qtbot.addWidget(dlg)
    dlg._label_edit.setText("   ")  # whitespace puro → None tras strip
    dlg._on_generate()
    assert captured["user_label"] is None
    assert dlg.result_path is not None
    assert dlg.result_path.is_file()


def test_dialog_with_label_calls_service_with_value(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    assert demo_collection.collection_id is not None
    dlg = ExchangeExportDialog(ctx=ctx_with_demo, collection_id=demo_collection.collection_id)
    qtbot.addWidget(dlg)
    dlg._label_edit.setText("PGG")
    dlg._on_generate()
    assert dlg.result_path is not None
    # El label canónico aparece en el filename.
    assert "PGG" in dlg.result_path.name


def test_dialog_unknown_collection_does_not_crash(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
) -> None:
    """Service error → QMessageBox, dialog NO se cierra, result_path queda None."""
    monkeypatch.setattr(
        "collections_app.services.exchange_export_service.get_downloads_dir",
        lambda: tmp_path,
    )
    # Stub QMessageBox.critical para que no bloquee.
    monkeypatch.setattr(
        "collections_app.views.exchange.export_dialog.QMessageBox.critical",
        lambda *args, **kwargs: None,
    )
    dlg = ExchangeExportDialog(ctx=ctx_with_demo, collection_id=999_999)
    qtbot.addWidget(dlg)
    dlg._on_generate()
    assert dlg.result_path is None
