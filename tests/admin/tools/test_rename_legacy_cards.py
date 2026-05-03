"""Tests del script de migración rename_legacy_cards."""

import logging

from collections_app.admin.tools import rename_legacy_cards
from collections_app.admin.tools.rename_legacy_cards import (
    main,
)
from collections_app.admin.tools.rename_legacy_cards import (
    rename_legacy_cards as do_rename,
)


def test_renames_legacy_files_to_padded(tmp_path):
    """`1.jpg` y `42.png` se renombran a `0001.jpg` y `0042.png`."""
    (tmp_path / "1.jpg").write_bytes(b"a")
    (tmp_path / "42.png").write_bytes(b"b")

    result = do_rename(tmp_path)

    assert result.renamed == 2
    assert result.errors == 0
    assert (tmp_path / "0001.jpg").exists()
    assert (tmp_path / "0042.png").exists()
    assert not (tmp_path / "1.jpg").exists()
    assert not (tmp_path / "42.png").exists()


def test_skips_already_padded_files(tmp_path):
    """Archivos ya con padding no se tocan."""
    (tmp_path / "0001.jpg").write_bytes(b"x")
    (tmp_path / "0042.png").write_bytes(b"y")

    result = do_rename(tmp_path)

    assert result.renamed == 0
    assert result.skipped_already_padded == 2
    assert (tmp_path / "0001.jpg").read_bytes() == b"x"
    assert (tmp_path / "0042.png").read_bytes() == b"y"


def test_dry_run_does_not_modify_files(tmp_path):
    """Con dry_run no se toca el filesystem, pero se cuenta lo que se haría."""
    (tmp_path / "1.jpg").write_bytes(b"x")

    result = do_rename(tmp_path, dry_run=True)

    assert result.renamed == 1  # contado pero no aplicado
    assert (tmp_path / "1.jpg").exists()
    assert not (tmp_path / "0001.jpg").exists()


def test_does_not_overwrite_existing_padded(tmp_path, caplog):
    """Si ya existe `0001.jpg`, no se sobreescribe con `1.jpg` legacy."""
    (tmp_path / "1.jpg").write_bytes(b"legacy")
    (tmp_path / "0001.jpg").write_bytes(b"original")

    with caplog.at_level(logging.WARNING, logger="collections_app.admin.tools.rename_legacy_cards"):
        result = do_rename(tmp_path)

    assert result.skipped_collision == 1
    assert result.renamed == 0
    assert (tmp_path / "0001.jpg").read_bytes() == b"original"  # intacto
    assert (tmp_path / "1.jpg").read_bytes() == b"legacy"  # también intacto
    msgs = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("Colisión" in m or "0001.jpg" in m for m in msgs)


def test_skips_unrecognized_files(tmp_path):
    """Archivos que no matcheen el patrón legacy (ej. README) se ignoran."""
    (tmp_path / "README.txt").write_bytes(b"x")
    (tmp_path / "thumb.gif").write_bytes(b"y")
    (tmp_path / "1.jpg").write_bytes(b"z")

    result = do_rename(tmp_path)

    assert result.renamed == 1
    assert result.skipped_unrecognized == 2
    assert (tmp_path / "README.txt").exists()
    assert (tmp_path / "thumb.gif").exists()
    assert (tmp_path / "0001.jpg").exists()


def test_handles_missing_directory(tmp_path):
    """Si el directorio no existe, retorna result vacío sin levantar."""
    result = do_rename(tmp_path / "no-existe")
    assert result.renamed == 0
    assert result.errors == 0


def test_extension_normalized_to_lowercase(tmp_path):
    """Extensiones en mayúscula (`1.JPG`) se normalizan a minúscula."""
    (tmp_path / "5.JPG").write_bytes(b"x")
    do_rename(tmp_path)
    assert (tmp_path / "0005.jpg").exists()
    assert not (tmp_path / "5.JPG").exists()


# ----------------------------------------------------------------------
# CLI main()
# ----------------------------------------------------------------------


def test_main_returns_zero_when_no_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(rename_legacy_cards, "get_generated_cards_dir", lambda: tmp_path)
    (tmp_path / "1").mkdir()
    (tmp_path / "1" / "1.jpg").write_bytes(b"x")

    rc = main(["--collection-id", "1"])

    assert rc == 0
    assert (tmp_path / "1" / "0001.jpg").exists()


def test_main_dry_run_does_not_write(tmp_path, monkeypatch):
    monkeypatch.setattr(rename_legacy_cards, "get_generated_cards_dir", lambda: tmp_path)
    (tmp_path / "1").mkdir()
    (tmp_path / "1" / "42.jpg").write_bytes(b"x")

    rc = main(["--collection-id", "1", "--dry-run"])

    assert rc == 0
    assert (tmp_path / "1" / "42.jpg").exists()
    assert not (tmp_path / "1" / "0042.jpg").exists()
