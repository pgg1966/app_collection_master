"""Tests del AppContext."""

from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path

from collections_app.app_context import AppContext, create_app_context
from collections_app.services.cards_service import CardsService
from collections_app.services.code_headers_service import CodeHeadersService
from collections_app.services.code_lines_service import CodeLinesService
from collections_app.services.collections_service import CollectionsService
from collections_app.services.inventory_service import InventoryService
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
