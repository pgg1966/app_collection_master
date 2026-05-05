"""Tests del dataclass AppSetting (helpers de casteo).

El repo retorna `AppSetting | None` (CLAUDE.md sec 2.3 prohíbe que un
repo devuelva `str | None` o `int | None` crudo). Toda lógica de
casteo vive en el dataclass para que el caller pueda decidir si
quiere el string crudo o un tipo derivado.
"""

from __future__ import annotations

from collections_app.core.models.app_setting import AppSetting


def test_as_int_parses_valid_integer() -> None:
    s = AppSetting(key="max_retries", value="42")
    assert s.as_int() == 42


def test_as_int_returns_none_when_value_is_none() -> None:
    s = AppSetting(key="optional", value=None)
    assert s.as_int() is None


def test_as_int_returns_none_for_non_integer_string() -> None:
    s = AppSetting(key="bad", value="not-a-number")
    assert s.as_int() is None


def test_as_int_handles_negative_integers() -> None:
    s = AppSetting(key="offset", value="-5")
    assert s.as_int() == -5


def test_as_bool_true_for_truthy_strings() -> None:
    for value in ("1", "true", "True", "TRUE", "yes", "YES", "on"):
        assert AppSetting(key="k", value=value).as_bool() is True, value


def test_as_bool_false_for_falsy_strings() -> None:
    for value in ("0", "false", "False", "FALSE", "no", "NO", "off"):
        assert AppSetting(key="k", value=value).as_bool() is False, value


def test_as_bool_returns_none_when_value_is_none() -> None:
    s = AppSetting(key="k", value=None)
    assert s.as_bool() is None


def test_as_bool_returns_none_for_unknown_string() -> None:
    s = AppSetting(key="k", value="maybe")
    assert s.as_bool() is None


def test_as_bool_strips_whitespace() -> None:
    assert AppSetting(key="k", value="  true  ").as_bool() is True
