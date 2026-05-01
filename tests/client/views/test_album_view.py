"""Tests del AlbumView."""

import pytest

from collections_app.client.views.album_view import AlbumView
from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)


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
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=3))  # repetida x2
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=1))  # tengo
    memory_db.commit()
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, album_setup):
    v = AlbumView(memory_db, album_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def test_album_view_loads_without_error(qtbot, view):
    """La view se construye sin levantar excepciones."""
    assert view._unique_button is not None
    assert view._duplicates_button is not None


def test_image_count_shows_zero_when_no_crests(
    qtbot, memory_db, album_setup, tmp_path, monkeypatch
):
    """Sin escudos en disco, muestra mensaje de 'no hay escudos cargados'."""
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, album_setup)
    qtbot.addWidget(v)
    text = v._image_count_label.text().lower()
    assert "escudos" in text
    assert "no hay" in text


def test_image_count_shows_loaded_crests(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    """Si hay escudos en el dir crests para ARG, lo contabiliza (1 de 1)."""
    (tmp_path / "ARG.png").touch()
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, album_setup)
    qtbot.addWidget(v)
    text = v._image_count_label.text()
    # En album_setup hay solo el código ARG → 1 de 1
    assert "1 / 1" in text


def test_generate_unique_calls_generator(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    """Click en 'Generar álbum' llama al generador con la config configurada."""
    out = tmp_path / "out.pdf"
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QFileDialog.getSaveFileName",
        lambda *a, **kw: (str(out), "pdf"),
    )

    captured: list = []

    def fake_unique(self, output_path, on_progress=None):
        captured.append((self.config, output_path))
        output_path.write_bytes(b"%PDF-fake")
        return output_path

    monkeypatch.setattr(
        "collections_app.core.services.PdfAlbumGenerator.generate_unique_album",
        fake_unique,
    )
    # Evitar abrir el visor
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QDesktopServices.openUrl",
        lambda url: True,
    )
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QMessageBox.information",
        lambda *a, **kw: None,
    )

    view = AlbumView(memory_db, album_setup)
    qtbot.addWidget(view)
    view._cols_input.setValue(3)
    view._rows_input.setValue(2)
    view._generate_unique()
    qtbot.waitUntil(lambda: bool(captured), timeout=3000)
    config, path = captured[0]
    assert config.cols == 3
    assert config.rows == 2
    assert path == out


def test_generate_duplicates_calls_generator(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    out = tmp_path / "dups.pdf"
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QFileDialog.getSaveFileName",
        lambda *a, **kw: (str(out), "pdf"),
    )
    captured: list = []

    def fake_dup(self, output_path, on_progress=None):
        captured.append(output_path)
        output_path.write_bytes(b"%PDF-fake")
        return output_path

    monkeypatch.setattr(
        "collections_app.core.services.PdfAlbumGenerator.generate_duplicates_album",
        fake_dup,
    )
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QDesktopServices.openUrl",
        lambda url: True,
    )
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QMessageBox.information",
        lambda *a, **kw: None,
    )

    view = AlbumView(memory_db, album_setup)
    qtbot.addWidget(view)
    view._generate_duplicates()
    qtbot.waitUntil(lambda: bool(captured), timeout=3000)
    assert captured[0] == out


def test_no_duplicates_shows_info_message(qtbot, memory_db, sample_collection, monkeypatch):
    """Sin repetidas en el inventory, click muestra info y no abre FileDialog."""
    info_calls: list = []
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QMessageBox.information",
        lambda *a, **kw: info_calls.append(a),
    )
    file_dialog_called = []
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QFileDialog.getSaveFileName",
        lambda *a, **kw: file_dialog_called.append(True) or ("", ""),
    )
    view = AlbumView(memory_db, sample_collection)
    qtbot.addWidget(view)
    view._generate_duplicates()
    assert info_calls
    assert not file_dialog_called


def test_export_missing_calls_generator(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    out = tmp_path / "missing.txt"
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QFileDialog.getSaveFileName",
        lambda *a, **kw: (str(out), "txt"),
    )
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QDesktopServices.openUrl",
        lambda url: True,
    )
    view = AlbumView(memory_db, album_setup)
    qtbot.addWidget(view)
    view._export_missing()
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "FALTANTES" in content


def test_export_duplicates_calls_generator(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    out = tmp_path / "dups.txt"
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QFileDialog.getSaveFileName",
        lambda *a, **kw: (str(out), "txt"),
    )
    monkeypatch.setattr(
        "collections_app.client.views.album_view.QDesktopServices.openUrl",
        lambda url: True,
    )
    view = AlbumView(memory_db, album_setup)
    qtbot.addWidget(view)
    view._export_duplicates()
    assert out.exists()
    assert "REPETIDAS" in out.read_text(encoding="utf-8")


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
    view = AlbumView(memory_db, album_setup)
    qtbot.addWidget(view)
    initial = view._image_count_label.text()
    view.set_active_collection(other)
    new_text = view._image_count_label.text()
    # El texto cambia: la colección "Other" no tiene cards
    assert initial != new_text
