"""Tests de los helpers de paths."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from collections_app.core.utils.paths import (
    get_app_data_dir,
    get_default_db_path,
    get_schema_dir,
)


def test_schema_dir_exists() -> None:
    """El schema_dir embebido debe existir y contener al menos la mig 001."""
    schema = get_schema_dir()
    assert schema.is_dir()
    sqls = sorted(schema.glob("*.sql"))
    assert any("001" in p.name for p in sqls)


def test_get_app_data_dir_creates_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """get_app_data_dir debe crear el directorio si no existe."""
    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))

    target = get_app_data_dir()
    assert target.is_dir()
    assert target.name == "Collections"


def test_get_default_db_path_inside_app_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))

    db_path = get_default_db_path()
    assert db_path.name == "collections.db"
    assert db_path.parent == get_app_data_dir()
