"""Tests de SettingsService."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.app_setting import AppSetting
from collections_app.services.exceptions import SettingsError
from collections_app.services.settings_service import SettingsService


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> SettingsService:
    return SettingsService(db_conn)


def test_get_returns_none_when_missing(service: SettingsService) -> None:
    assert service.get("missing") is None


def test_set_then_get_round_trips(service: SettingsService) -> None:
    service.set("theme", "dark")
    fetched = service.get("theme")
    assert fetched is not None
    assert fetched.value == "dark"


def test_set_overwrites_existing(service: SettingsService) -> None:
    service.set("theme", "dark")
    service.set("theme", "light")
    fetched = service.get("theme")
    assert fetched is not None
    assert fetched.value == "light"


def test_get_int_parses_value(service: SettingsService) -> None:
    service.set_int("retries", 5)
    assert service.get_int("retries") == 5


def test_get_int_returns_none_when_missing(service: SettingsService) -> None:
    assert service.get_int("missing") is None


def test_get_int_returns_none_when_value_not_int(service: SettingsService) -> None:
    service.set("retries", "abc")
    assert service.get_int("retries") is None


def test_set_int_persists_as_string(service: SettingsService) -> None:
    """SettingsService normaliza el value a string a nivel storage."""
    service.set_int("retries", 42)
    fetched = service.get("retries")
    assert fetched is not None
    assert fetched.value == "42"


def test_get_bool_truthy_values(service: SettingsService) -> None:
    service.set_bool("flag", True)
    assert service.get_bool("flag") is True


def test_get_bool_falsy_values(service: SettingsService) -> None:
    service.set_bool("flag", False)
    assert service.get_bool("flag") is False


def test_set_bool_persists_canonical_string(service: SettingsService) -> None:
    """set_bool normaliza a 'true' / 'false' en la DB para que get_bool sea estable."""
    service.set_bool("flag", True)
    fetched = service.get("flag")
    assert fetched is not None
    assert fetched.value == "true"


def test_get_bool_returns_none_when_missing(service: SettingsService) -> None:
    assert service.get_bool("missing") is None


def test_get_bool_returns_none_when_unknown_string(
    service: SettingsService,
) -> None:
    service.set("flag", "maybe")
    assert service.get_bool("flag") is None


def test_delete_returns_true_when_existed(service: SettingsService) -> None:
    service.set("k", "v")
    assert service.delete("k") is True
    assert service.get("k") is None


def test_delete_returns_false_when_missing(service: SettingsService) -> None:
    assert service.delete("never") is False


def test_list_all_returns_app_settings(service: SettingsService) -> None:
    service.set("a", "1")
    service.set("b", "2")
    items = service.list_all()
    assert len(items) == 2
    assert all(isinstance(s, AppSetting) for s in items)


def test_set_with_empty_key_raises(service: SettingsService) -> None:
    """Regla de negocio: la key no puede ser vacia."""
    with pytest.raises(SettingsError, match="key"):
        service.set("", "v")
