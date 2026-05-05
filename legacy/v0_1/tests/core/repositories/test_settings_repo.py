"""Tests del SettingsRepository."""

from collections_app.core.repositories import SettingsRepository


def test_get_missing_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.get("nope") is None


def test_set_and_get(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    assert repo.get("foo") == "bar"


def test_set_overwrites_existing(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    repo.set("foo", "baz")
    assert repo.get("foo") == "baz"


def test_delete_existing(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    assert repo.delete("foo") is True
    assert repo.get("foo") is None


def test_delete_missing_returns_false(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.delete("nope") is False


def test_get_int_returns_parsed(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("count", "42")
    assert repo.get_int("count") == 42


def test_get_int_missing_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.get_int("nope") is None


def test_get_int_invalid_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "not-a-number")
    assert repo.get_int("foo") is None
