"""Tests del AppContext."""

from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path

import pytest

from collections_app.app_context import AppContext, create_app_context
from collections_app.services.cards_service import CardsService
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.collections_service import CollectionsService
from collections_app.services.csv_import_service import CsvImportService
from collections_app.services.exchange_apply_service import ExchangeApplyService
from collections_app.services.exchange_export_service import ExchangeExportService
from collections_app.services.exchange_import_service import ExchangeImportService
from collections_app.services.inventory_service import InventoryService
from collections_app.services.inventory_snapshot_service import (
    InventorySnapshotService,
)
from collections_app.services.ocr_install_service import OcrInstallService
from collections_app.services.settings_service import SettingsService
from collections_app.services.transactions_service import TransactionsService


def test_create_app_context_in_memory_runs_migrations() -> None:
    ctx = create_app_context(":memory:")
    try:
        # Si las migraciones se aplicaron, schema_version >= 1.
        row = ctx.conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
        assert row["v"] >= 1
    finally:
        ctx.close()


def test_app_context_exposes_all_services() -> None:
    ctx = create_app_context(":memory:")
    try:
        assert isinstance(ctx.inventory, InventoryService)
        assert isinstance(ctx.collections, CollectionsService)
        assert isinstance(ctx.cards, CardsService)
        assert isinstance(ctx.code_headers, CodeHeadersService)
        assert isinstance(ctx.code_lines, CodeLinesService)
        assert isinstance(ctx.transactions, TransactionsService)
        assert isinstance(ctx.settings, SettingsService)
        assert isinstance(ctx.csv_import, CsvImportService)
        assert isinstance(ctx.inventory_snapshot, InventorySnapshotService)
        assert isinstance(ctx.exchange_export, ExchangeExportService)
        assert isinstance(ctx.exchange_import, ExchangeImportService)
        assert isinstance(ctx.exchange_apply, ExchangeApplyService)
        assert isinstance(ctx.ocr_install, OcrInstallService)
    finally:
        ctx.close()


def test_app_context_services_share_connection() -> None:
    """Los services deben usar la misma connection — clave para atomicidad."""
    ctx = create_app_context(":memory:")
    try:
        # Acceso al `_conn` del InventoryService (atributo privado, OK en test).
        assert ctx.inventory._conn is ctx.conn
    finally:
        ctx.close()


def test_app_context_close_is_idempotent() -> None:
    ctx = create_app_context(":memory:")
    ctx.close()
    ctx.close()  # no rompe


def test_app_context_persists_to_file(tmp_path: Path) -> None:
    """Persistencia: lo que escribe un context se ve cuando se reabre el archivo."""
    db_path = tmp_path / "test.db"
    ctx1 = create_app_context(db_path)
    try:
        ctx1.settings.set("test_key", "test_value")
        ctx1.conn.commit()
    finally:
        ctx1.close()

    ctx2 = create_app_context(db_path)
    try:
        fetched = ctx2.settings.get("test_key")
        assert fetched is not None
        assert fetched.value == "test_value"
    finally:
        ctx2.close()


def test_create_app_context_returns_dataclass_with_slots() -> None:
    """AppContext debe ser slots para coherencia con el resto del proyecto."""
    ctx = create_app_context(":memory:")
    try:
        assert isinstance(ctx, AppContext)
        assert hasattr(AppContext, "__slots__")
    finally:
        ctx.close()


def test_close_after_native_close_does_not_raise() -> None:
    """Si el caller cerro la conn manualmente, ctx.close() no debe romper."""
    ctx = create_app_context(":memory:")
    with contextlib.suppress(sqlite3.Error):
        ctx.conn.close()
    # close() debe ser tolerante.
    ctx.close()


# ---------------------------------------------------------------------
# get_ocr_service factory (Sesión 5d)
# ---------------------------------------------------------------------


def test_get_ocr_service_returns_none_when_deps_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin torch/ultralytics → factory devuelve None sin tocar el modelo."""
    from collections_app.core.models.code_header import CodeHeader
    from collections_app.core.models.collection import Collection

    monkeypatch.setattr(
        "collections_app.app_context.OcrInstallService.is_installed",
        staticmethod(lambda: False),
    )
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="X",
                card_count=0,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
                ocr_model_filename="ocr_99.pt",  # daría igual
            )
        )
        assert ctx.get_ocr_service(coll) is None
    finally:
        ctx.close()


def test_get_ocr_service_returns_none_when_no_model_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deps OK pero collection.ocr_model_filename = None → None."""
    from collections_app.core.models.code_header import CodeHeader
    from collections_app.core.models.collection import Collection

    monkeypatch.setattr(
        "collections_app.app_context.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="X",
                card_count=0,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.ocr_model_filename is None
        assert ctx.get_ocr_service(coll) is None
    finally:
        ctx.close()


def test_create_worker_connection_returns_separate_connection() -> None:
    """`create_worker_connection` debe devolver una conn NUEVA, no la del ctx.

    Es la que usan los workers de QThread para evitar el cross-thread
    error de SQLite. El ctx también guarda `db_path` para que la conn
    apunte a la misma DB.
    """
    ctx = create_app_context(":memory:")
    try:
        worker_conn = ctx.create_worker_connection()
        try:
            assert worker_conn is not ctx.conn
            # Apunta a la misma DB lógica (`:memory:` es un caso especial;
            # cada conn :memory: es una DB distinta — verificamos solo que
            # devolvió una conn usable).
            assert hasattr(worker_conn, "execute")
        finally:
            worker_conn.close()
    finally:
        ctx.close()


def test_ctx_db_path_preserved_after_creation(tmp_path: Path) -> None:
    """`ctx.db_path` queda en el ctx para que los workers lo usen."""
    db_path = tmp_path / "test.db"
    ctx = create_app_context(db_path)
    try:
        assert ctx.db_path == str(db_path)
    finally:
        ctx.close()


def test_get_ocr_service_returns_none_when_model_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Filename configurado pero el archivo no existe → None."""
    import sys

    from collections_app.core.models.code_header import CodeHeader
    from collections_app.core.models.collection import Collection

    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))

    monkeypatch.setattr(
        "collections_app.app_context.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="X",
                card_count=0,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
                ocr_model_filename="ocr_inexistente.pt",
            )
        )
        assert ctx.get_ocr_service(coll) is None
    finally:
        ctx.close()


# ---------------------------------------------------------------------
# get_ocr_guide_path (migración 003)
# ---------------------------------------------------------------------


def _isolate_app_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Apunta `<app_data>/` al tmp_path del test."""
    import sys

    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))


def _make_collection_with_guide(ctx: AppContext, guide_filename: str | None):  # type: ignore[no-untyped-def]
    from collections_app.core.models.code_header import CodeHeader
    from collections_app.core.models.collection import Collection

    h = ctx.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    assert h.code_header_id is not None
    return ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="X",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
            ocr_guide_filename=guide_filename,
        )
    )


def test_get_ocr_guide_path_returns_none_when_filename_not_configured() -> None:
    """`collection.ocr_guide_filename = None` → factory devuelve None."""
    ctx = create_app_context(":memory:")
    try:
        coll = _make_collection_with_guide(ctx, None)
        assert ctx.get_ocr_guide_path(coll) is None
    finally:
        ctx.close()


def test_get_ocr_guide_path_returns_none_when_file_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Filename configurado pero el archivo no existe en `images/` → None."""
    _isolate_app_data(tmp_path, monkeypatch)
    ctx = create_app_context(":memory:")
    try:
        coll = _make_collection_with_guide(ctx, "ocr_guide_nope.jpg")
        assert ctx.get_ocr_guide_path(coll) is None
    finally:
        ctx.close()


def test_get_ocr_guide_path_returns_path_when_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Filename configurado + archivo presente → Path absoluto."""
    from collections_app.core.utils.paths import get_images_dir

    _isolate_app_data(tmp_path, monkeypatch)
    images_dir = get_images_dir()
    real_image = images_dir / "ocr_guide_42.png"
    real_image.write_bytes(b"\x89PNG\r\n\x1a\n")  # PNG header dummy

    ctx = create_app_context(":memory:")
    try:
        coll = _make_collection_with_guide(ctx, "ocr_guide_42.png")
        result = ctx.get_ocr_guide_path(coll)
        assert result == real_image
        assert result.is_file()
    finally:
        ctx.close()
