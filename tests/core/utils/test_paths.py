"""Tests de los helpers de paths del módulo `core.utils.paths`."""

from collections_app.core.utils import paths


def _redirect_generated_cards_dir(monkeypatch, tmp_path):
    """Hace que get_generated_cards_dir apunte a tmp_path."""
    monkeypatch.setattr(paths, "get_generated_cards_dir", lambda: tmp_path)


# ----------------------------------------------------------------------
# format_card_filename
# ----------------------------------------------------------------------


def test_format_card_filename_default_extension():
    assert paths.format_card_filename(1) == "0001.jpg"
    assert paths.format_card_filename(42) == "0042.jpg"
    assert paths.format_card_filename(630) == "0630.jpg"


def test_format_card_filename_custom_extension():
    assert paths.format_card_filename(1, "png") == "0001.png"
    # Acepta extensión con o sin punto
    assert paths.format_card_filename(1, ".png") == "0001.png"
    assert paths.format_card_filename(1, "jpeg") == "0001.jpeg"


def test_format_card_filename_zero_padding_at_boundaries():
    assert paths.format_card_filename(9999) == "9999.jpg"
    # Si supera 4 dígitos, igual lo formatea sin truncar
    assert paths.format_card_filename(10000) == "10000.jpg"


# ----------------------------------------------------------------------
# get_card_image_path
# ----------------------------------------------------------------------


def test_get_card_image_path_constructs_full_path(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.get_card_image_path(1, 42) == tmp_path / "1" / "0042.jpg"


def test_get_card_image_path_respects_custom_extension(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.get_card_image_path(2, 5, "png") == tmp_path / "2" / "0005.png"


# ----------------------------------------------------------------------
# find_card_image
# ----------------------------------------------------------------------


def test_find_card_image_returns_existing_jpg(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    target = tmp_path / "1" / "0042.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == target


def test_find_card_image_prefers_jpg_over_png(tmp_path, monkeypatch):
    """Si conviven .jpg y .png, gana .jpg (orden de búsqueda)."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    folder = tmp_path / "1"
    folder.mkdir()
    jpg = folder / "0042.jpg"
    png = folder / "0042.png"
    jpg.write_bytes(b"x")
    png.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == jpg


def test_find_card_image_returns_none_when_missing(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.find_card_image(1, 42) is None


def test_find_card_image_falls_back_to_png(tmp_path, monkeypatch):
    """Sin .jpg pero con .png → devuelve el .png."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    png = tmp_path / "1" / "0042.png"
    png.parent.mkdir(parents=True)
    png.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == png


def test_find_card_image_falls_back_to_jpeg(tmp_path, monkeypatch):
    """Sin .jpg ni .png pero con .jpeg → devuelve el .jpeg."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    jpeg = tmp_path / "1" / "0042.jpeg"
    jpeg.parent.mkdir(parents=True)
    jpeg.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == jpeg


def test_find_card_image_does_not_match_legacy_unpadded(tmp_path, monkeypatch):
    """Un archivo legacy sin padding (`42.jpg`) NO se debe encontrar.

    Forzar a `find_card_image` a buscar SOLO con padding garantiza que el
    consumidor llame a `rename_legacy_cards` antes que confiar en magia.
    """
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    legacy = tmp_path / "1" / "42.jpg"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b"x")
    assert paths.find_card_image(1, 42) is None
