"""Tests del AlbumView (cliente)."""

from pathlib import Path

import pytest

from collections_app.client.views import album_view as view_mod
from collections_app.client.views.album_view import AlbumView
from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)

# `db_path` dummy: el worker real nunca arranca (lo stubeamos), por lo
# tanto el path no se usa para abrir conexiones.
_DUMMY_DB_PATH = Path(":memory:")


@pytest.fixture
def album_setup(memory_db, sample_collection):
    """Cards y inventory parcial: ARG-1 repetida, ARG-2 tengo, ARG-3 falta."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "ARGENTINA"))

    cards = CardsRepository(memory_db)
    cards.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    cards.upsert(Card(cid, "ARG", 2, "Emi Martinez"))
    cards.upsert(Card(cid, "ARG", 3, "Nahuel Molina"))

    inv = InventoryRepository(memory_db)
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=3))
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=1))
    memory_db.commit()
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, album_setup):
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    v.show()
    return v


# ----------------------------------------------------------------------
# Construcción
# ----------------------------------------------------------------------


def test_album_view_loads_without_error(qtbot, view):
    """Construye los 5 botones (album / missing / duplicates_full /
    duplicates_summary / owned)."""
    assert len(view._buttons) == 5


def test_image_count_shows_zero_when_no_crests(
    qtbot, memory_db, album_setup, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    text = v._image_count_label.text()
    # 0 escudos cargados / 1 total
    assert "0 / 1" in text


def test_image_count_shows_loaded_crests(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    (tmp_path / "ARG.png").touch()
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    assert "1 / 1" in v._image_count_label.text()


# ----------------------------------------------------------------------
# Botones de generación: dispatch al worker con el kind correcto
# ----------------------------------------------------------------------


def _stub_worker(captured: dict):
    """Crea una clase _StubWorker que captura los args al construirse."""

    class _StubWorker:
        finished_ok = type("S", (), {"connect": lambda *a, **k: None})()
        failed = type("S", (), {"connect": lambda *a, **k: None})()

        def __init__(self, db_path, collection_id, output_path, kind, parent=None):
            captured["db_path"] = db_path
            captured["collection_id"] = collection_id
            captured["output_path"] = output_path
            captured["kind"] = kind

        def start(self):
            pass

    return _StubWorker


@pytest.mark.parametrize(
    ("button_idx", "expected_kind", "expected_prefix"),
    [
        (0, "album", "Album"),
        (1, "missing", "Faltantes"),
        (2, "duplicates_full", "Repetidas_Completo"),
        (3, "duplicates_summary", "Repetidas_Resumido"),
        (4, "owned", "Tengo"),
    ],
)
def test_each_button_dispatches_correct_kind_to_worker(
    qtbot, view, monkeypatch, button_idx, expected_kind, expected_prefix
):
    """Cada uno de los 5 botones lanza el worker con el `kind` correcto.

    Bajo el flujo nuevo, el botón NO abre QFileDialog — genera a un
    archivo temporal y luego abre el preview. Solo verificamos que el
    worker arranca con los args correctos.
    """
    captured: dict = {}
    monkeypatch.setattr(view_mod, "_PdfWorker", _stub_worker(captured))

    view._buttons[button_idx].click()

    assert captured["kind"] == expected_kind
    assert captured["collection_id"] == view.collection.collection_id
    # output_path es un archivo temporal (.pdf) — verificamos forma.
    out = captured["output_path"]
    assert isinstance(out, Path)
    assert out.suffix == ".pdf"
    # El nombre sugerido (que pasaría al preview) tiene el prefijo correcto.
    suggested = view._suggested_filename(expected_kind)
    assert suggested.startswith(expected_prefix + "_")


def test_buttons_disabled_during_generation(qtbot, view, monkeypatch):
    """Mientras el worker corre, los botones quedan deshabilitados."""
    captured: dict = {}
    monkeypatch.setattr(view_mod, "_PdfWorker", _stub_worker(captured))
    view._buttons[0].click()
    # Después del click, todos los botones quedan deshabilitados hasta on_ok.
    assert all(not b.isEnabled() for b in view._buttons)


# ----------------------------------------------------------------------
# set_active_collection
# ----------------------------------------------------------------------


def test_set_active_collection_refreshes_image_count(
    qtbot, memory_db, album_setup, sample_code_header, tmp_path, monkeypatch
):
    """Cambiar la colección activa refresca el contador de escudos."""
    from collections_app.core.models import Collection
    from collections_app.core.repositories import CollectionsRepository

    other = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Other",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()

    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    view = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(view)
    initial = view._image_count_label.text()
    view.set_active_collection(other)
    assert view._image_count_label.text() != initial
