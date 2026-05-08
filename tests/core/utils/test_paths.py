"""Tests de los helpers de paths."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from collections_app.core.utils.paths import (
    get_app_data_dir,
    get_db_path_for_profile,
    get_default_db_path,
    get_generated_cards_dir_for_profile,
    get_schema_dir,
)


def _isolate_app_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Apunta el `Collections/` data dir a un tmp_path para evitar tocar
    el directorio real del usuario en el test runner."""
    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))


def test_schema_dir_exists() -> None:
    """El schema_dir embebido debe existir y contener al menos la mig 001."""
    schema = get_schema_dir()
    assert schema.is_dir()
    sqls = sorted(schema.glob("*.sql"))
    assert any("001" in p.name for p in sqls)


def test_get_app_data_dir_creates_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """get_app_data_dir debe crear el directorio si no existe."""
    _isolate_app_data(tmp_path, monkeypatch)
    target = get_app_data_dir()
    assert target.is_dir()
    assert target.name == "Collections"


def test_get_default_db_path_inside_app_data_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    db_path = get_default_db_path()
    assert db_path.name == "collections.db"
    assert db_path.parent == get_app_data_dir()


# ---------------------------------------------------------------------
# get_db_path_for_profile
# ---------------------------------------------------------------------


def test_get_db_path_for_profile_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """profile=None coincide con get_default_db_path()."""
    _isolate_app_data(tmp_path, monkeypatch)
    assert get_db_path_for_profile(None) == get_default_db_path()


def test_get_db_path_for_profile_named(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """profile='demo' → collections_demo.db en el data dir."""
    _isolate_app_data(tmp_path, monkeypatch)
    db_path = get_db_path_for_profile("demo")
    assert db_path.name == "collections_demo.db"
    assert db_path.parent == get_app_data_dir()


def test_get_db_path_for_profile_accepts_underscores_and_digits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    db_path = get_db_path_for_profile("my_profile_2")
    assert db_path.name == "collections_my_profile_2.db"


@pytest.mark.parametrize(
    "bad",
    [
        "",  # vacío
        "foo bar",  # espacio
        "foo/bar",  # separador de path
        "foo\\bar",  # backslash en Windows-style
        "foo;rm",  # punto y coma
        "foo.bar",  # punto
        "foo-bar",  # guión común — no se acepta intencionalmente
        "fóo",  # acento
    ],
    ids=[
        "empty",
        "space",
        "forward_slash",
        "backslash",
        "semicolon",
        "dot",
        "dash",
        "non_ascii",
    ],
)
def test_get_db_path_for_profile_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValueError, match="profile invalido"):
        get_db_path_for_profile(bad)


# ---------------------------------------------------------------------
# get_generated_cards_dir_for_profile
# ---------------------------------------------------------------------


def test_get_generated_cards_dir_default_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    target = get_generated_cards_dir_for_profile(None)
    assert target.is_dir()
    assert target.name == "default"
    assert target.parent.name == "generated_cards"
    assert target.parent.parent == get_app_data_dir()


def test_get_generated_cards_dir_named_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    target = get_generated_cards_dir_for_profile("demo")
    assert target.is_dir()
    assert target.name == "demo"
    assert target.parent.name == "generated_cards"


def test_get_generated_cards_dir_creates_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Idempotente: crear, borrar, volver a llamar — debe re-crear."""
    _isolate_app_data(tmp_path, monkeypatch)
    target = get_generated_cards_dir_for_profile("test")
    assert target.is_dir()
    target.rmdir()
    assert not target.exists()
    target_again = get_generated_cards_dir_for_profile("test")
    assert target_again.is_dir()


def test_get_generated_cards_dir_rejects_invalid_profile() -> None:
    with pytest.raises(ValueError, match="profile invalido"):
        get_generated_cards_dir_for_profile("bad/name")


# ---------------------------------------------------------------------
# get_downloads_dir
# ---------------------------------------------------------------------


def test_get_downloads_dir_returns_downloads_when_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si `~/Downloads` existe, lo retorna."""
    from collections_app.core.utils.paths import get_downloads_dir

    fake_home = tmp_path / "home"
    (fake_home / "Downloads").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    assert get_downloads_dir() == fake_home / "Downloads"


def test_get_downloads_dir_falls_back_to_tempdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Si `~/Downloads` no existe, fallback a tempfile.gettempdir()."""
    import tempfile as _tempfile

    from collections_app.core.utils.paths import get_downloads_dir

    fake_home = tmp_path / "home_minimal"
    fake_home.mkdir()  # sin Downloads adentro
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    result = get_downloads_dir()
    assert result == Path(_tempfile.gettempdir())
