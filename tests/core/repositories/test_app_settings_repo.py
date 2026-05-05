"""Tests CRUD de AppSettingsRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.app_setting import AppSetting
from collections_app.core.repositories.app_settings_repo import AppSettingsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> AppSettingsRepository:
    return AppSettingsRepository(db_conn)


def test_get_returns_none_for_missing_key(repo: AppSettingsRepository) -> None:
    assert repo.get("missing") is None


def test_set_then_get_round_trips(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="theme", value="dark"))
    fetched = repo.get("theme")
    assert fetched is not None
    assert fetched.key == "theme"
    assert fetched.value == "dark"


def test_set_overwrites_existing_value(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="theme", value="dark"))
    repo.set(AppSetting(key="theme", value="light"))
    fetched = repo.get("theme")
    assert fetched is not None
    assert fetched.value == "light"


def test_set_can_store_none_value(repo: AppSettingsRepository) -> None:
    """value es nullable en el schema."""
    repo.set(AppSetting(key="optional", value=None))
    fetched = repo.get("optional")
    assert fetched is not None
    assert fetched.value is None


def test_delete_returns_true_when_existed(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="k", value="v"))
    assert repo.delete("k") is True
    assert repo.get("k") is None


def test_delete_returns_false_when_missing(repo: AppSettingsRepository) -> None:
    assert repo.delete("never_existed") is False


def test_list_all_empty(repo: AppSettingsRepository) -> None:
    assert repo.list_all() == []


def test_list_all_returns_all_entries_sorted_by_key(
    repo: AppSettingsRepository,
) -> None:
    repo.set(AppSetting(key="zebra", value="z"))
    repo.set(AppSetting(key="alpha", value="a"))
    repo.set(AppSetting(key="mike", value="m"))
    items = repo.list_all()
    assert [s.key for s in items] == ["alpha", "mike", "zebra"]
    assert all(isinstance(s, AppSetting) for s in items)
