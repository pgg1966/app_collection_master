"""Tests del script seed_demo_data."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import scripts.seed_demo_data as seed_module
from collections_app.app_context import create_app_context


def _isolate_app_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_base = tmp_path / "FakeBase"
    if sys.platform == "win32":
        monkeypatch.setenv("APPDATA", str(fake_base))
    elif sys.platform == "darwin":
        monkeypatch.setenv("HOME", str(fake_base))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(fake_base))


def test_seed_creates_collection_codes_and_cards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    rc = seed_module.seed(profile="testseed")
    assert rc == 0

    from collections_app.core.utils.paths import get_db_path_for_profile

    ctx = create_app_context(get_db_path_for_profile("testseed"))
    try:
        coll = ctx.collections.get_by_name(seed_module.DEMO_COLLECTION_NAME)
        assert coll is not None
        assert coll.requires_code is True

        header = ctx.code_headers.get_by_name(seed_module.DEMO_HEADER_NAME)
        assert header is not None
        assert header.code_header_id is not None
        codes = ctx.code_lines.list_by_header(header.code_header_id)
        assert len(codes) == len(seed_module.DEMO_CODES)

        assert coll.collection_id is not None
        cards = ctx.cards.list_by_collection(coll.collection_id)
        assert len(cards) == len(seed_module.DEMO_CARDS)
    finally:
        ctx.close()


def test_seed_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Segunda ejecución sale sin tocar nada y avisa al usuario."""
    _isolate_app_data(tmp_path, monkeypatch)
    assert seed_module.seed(profile="testseed_idem") == 0
    capsys.readouterr()  # descartar output del primer run

    rc = seed_module.seed(profile="testseed_idem")
    assert rc == 0
    out = capsys.readouterr().out
    assert "Ya existe" in out
    assert seed_module.DEMO_COLLECTION_NAME in out


def test_seed_invalid_profile_returns_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _isolate_app_data(tmp_path, monkeypatch)
    rc = seed_module.seed(profile="bad/name")
    assert rc == 2
    err = capsys.readouterr().err
    assert "profile invalido" in err


def test_main_passes_profile_through(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """main(argv) parsea --profile y delega a seed()."""
    _isolate_app_data(tmp_path, monkeypatch)
    rc = seed_module.main(["--profile", "testseed_main"])
    assert rc == 0


def test_main_without_profile_uses_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin --profile, usa la DB default del data dir aislado."""
    _isolate_app_data(tmp_path, monkeypatch)
    rc = seed_module.main([])
    assert rc == 0
    from collections_app.core.utils.paths import get_default_db_path

    assert get_default_db_path().exists()
