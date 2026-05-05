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


# ----------------------------------------------------------------------
# _get_bundle_dir / get_schema_dir — detección de PyInstaller frozen
# ----------------------------------------------------------------------


def test_bundle_dir_returns_package_root_in_dev():
    """En desarrollo (sys.frozen ausente) apunta al paquete instalado."""
    bundle = paths._get_bundle_dir()
    # Debe ser la raíz de `collections_app/` — `core/utils/paths.py`
    # vive 2 niveles abajo, así que la subida nos lleva ahí.
    assert bundle.name == "collections_app"
    assert (bundle / "core" / "utils" / "paths.py").exists()


def test_get_schema_dir_returns_existing_directory_in_dev():
    """En dev, el schema_dir existe y tiene los .sql de migración."""
    schema = paths.get_schema_dir()
    assert schema.exists()
    sql_files = sorted(p.name for p in schema.glob("*.sql"))
    assert sql_files  # al menos uno
    assert all(name.endswith(".sql") for name in sql_files)


def test_bundle_dir_uses_meipass_when_frozen(monkeypatch, tmp_path):
    """Simulando sys.frozen + sys._MEIPASS, _get_bundle_dir() apunta ahí."""
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    bundle = paths._get_bundle_dir()
    assert bundle == tmp_path / "collections_app"


def test_get_schema_dir_uses_meipass_when_frozen(monkeypatch, tmp_path):
    """En modo frozen, get_schema_dir resuelve a _MEIPASS/.../schema."""
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    expected = tmp_path / "collections_app" / "core" / "db" / "schema"
    assert paths.get_schema_dir() == expected


def test_app_data_dir_does_not_depend_on_meipass(monkeypatch, tmp_path):
    """Datos del usuario (DB, escudos, cards) viven en %APPDATA%, NO en _MEIPASS.

    Si get_app_data_dir o las funciones que delegan en él dependieran de
    _MEIPASS, los datos se perderían cada vez que el bootloader recreara
    la carpeta temp. Este test garantiza esa separación.
    """
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    app_dir = paths.get_app_data_dir()
    # No debe estar dentro de _MEIPASS
    assert tmp_path not in app_dir.parents
    assert app_dir != tmp_path


# ----------------------------------------------------------------------
# Perfiles de datos: set_active_profile / get_active_profile
# ----------------------------------------------------------------------


import pytest  # noqa: E402


@pytest.fixture(autouse=False)
def reset_profile_after_test():
    """Restaura el perfil a 'default' después del test (estado global)."""
    yield
    paths.set_active_profile("default")


def test_set_active_profile_sanitizes_input(reset_profile_after_test):
    """Caracteres no [a-zA-Z0-9-] se reemplazan por _."""
    paths.set_active_profile("Mi Perfil!")
    assert paths.get_active_profile() == "Mi_Perfil"
    paths.set_active_profile("with.dots/and:colons")
    assert paths.get_active_profile() == "with_dots_and_colons"


def test_set_active_profile_empty_falls_back_to_default(reset_profile_after_test):
    paths.set_active_profile("")
    assert paths.get_active_profile() == "default"
    paths.set_active_profile("   ")
    assert paths.get_active_profile() == "default"
    # También si quedan solo separadores tras sanitizar.
    paths.set_active_profile("!!!")
    assert paths.get_active_profile() == "default"


def test_set_active_profile_keeps_valid_chars(reset_profile_after_test):
    paths.set_active_profile("test-profile-2")
    assert paths.get_active_profile() == "test-profile-2"


def test_default_profile_uses_base_dir(monkeypatch, tmp_path, reset_profile_after_test):
    """default → APPDATA/Collections (sin subdirectorio extra)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("default")
    app_dir = paths.get_app_data_dir()
    assert app_dir == tmp_path / "Collections"


def test_named_profile_uses_subdirectory(monkeypatch, tmp_path, reset_profile_after_test):
    """test → APPDATA/Collections/test."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("test")
    app_dir = paths.get_app_data_dir()
    assert app_dir == tmp_path / "Collections" / "test"


def test_get_database_path_includes_profile(monkeypatch, tmp_path, reset_profile_after_test):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("personal")
    db = paths.get_database_path()
    assert db == tmp_path / "Collections" / "personal" / "collections.db"


def test_profile_isolates_generated_cards_dir(monkeypatch, tmp_path, reset_profile_after_test):
    """Las imágenes derivan de get_app_data_dir → también heredan el perfil."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("test")
    cards_dir = paths.get_generated_cards_dir()
    assert cards_dir == tmp_path / "Collections" / "test" / "generated_cards"
