"""Tests del PdfAlbumGenerator."""


import pytest

from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import (
    AlbumConfig,
    PdfAlbumGenerator,
)


@pytest.fixture
def album_setup(memory_db, sample_collection):
    """5 cards en 2 codes, con inventory parcial."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines_repo = CodesLinesRepository(memory_db)
    lines_repo.upsert(CodeLine(hid, "ARG", "ARGENTINA", code_order=1))
    lines_repo.upsert(CodeLine(hid, "BRA", "BRAZIL", code_order=2))

    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    cards_repo.upsert(Card(cid, "ARG", 2, "Emiliano Martinez"))
    cards_repo.upsert(Card(cid, "ARG", 3, "Nahuel Molina"))
    cards_repo.upsert(Card(cid, "BRA", 1, "Vinicius Jr"))
    cards_repo.upsert(Card(cid, "BRA", 2, "Neymar"))

    inv = InventoryRepository(memory_db)
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=3))  # repetida
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=1))  # tengo
    inv.upsert(InventoryItem(cid, "BRA", 1, quantity=2))  # repetida
    # ARG-3 y BRA-2 → falta
    memory_db.commit()
    return sample_collection


def test_generate_unique_album_creates_pdf_file(memory_db, album_setup, tmp_path):
    out = tmp_path / "album.pdf"
    gen = PdfAlbumGenerator(memory_db, album_setup)
    gen.generate_unique_album(out)
    assert out.exists()


def test_generate_unique_album_file_size_nonzero(memory_db, album_setup, tmp_path):
    out = tmp_path / "album.pdf"
    PdfAlbumGenerator(memory_db, album_setup).generate_unique_album(out)
    assert out.stat().st_size > 0
    # Es un PDF (firma %PDF-)
    assert out.read_bytes()[:5] == b"%PDF-"


def test_generate_duplicates_album_with_duplicates(memory_db, album_setup, tmp_path):
    out = tmp_path / "dups.pdf"
    PdfAlbumGenerator(memory_db, album_setup).generate_duplicates_album(out)
    assert out.exists()
    assert out.read_bytes()[:5] == b"%PDF-"


def test_generate_duplicates_album_no_duplicates_creates_single_page(
    memory_db, sample_collection, tmp_path
):
    """Si no hay repetidas, el PDF tiene mensaje de placeholder."""
    # No insertamos cards ni inventory → sin repetidas
    out = tmp_path / "empty_dups.pdf"
    PdfAlbumGenerator(memory_db, sample_collection).generate_duplicates_album(out)
    assert out.exists()
    assert out.read_bytes()[:5] == b"%PDF-"


def test_slot_data_ordered_by_code_order_then_card_number(memory_db, album_setup):
    gen = PdfAlbumGenerator(memory_db, album_setup)
    slots = gen._build_slot_data()
    # ARG (order=1) viene antes que BRA (order=2)
    keys = [(s.card.code_id, s.card.card_number) for s in slots]
    assert keys == [
        ("ARG", 1),
        ("ARG", 2),
        ("ARG", 3),
        ("BRA", 1),
        ("BRA", 2),
    ]


def test_slot_data_includes_generated_image_path_when_exists(
    memory_db, album_setup, tmp_path, monkeypatch
):
    """Si el PNG existe en disco, slot.generated_image_path apunta a él."""
    fake_png = tmp_path / "ARG-1.png"
    fake_png.write_bytes(b"\x89PNG\r\n\x1a\n")  # mínimo de magic bytes

    def fake_path(_cid, key):
        return tmp_path / f"{key}.png"

    monkeypatch.setattr(
        "collections_app.core.services.pdf_generator.get_generated_card_path",
        fake_path,
    )

    slots = PdfAlbumGenerator(memory_db, album_setup)._build_slot_data()
    by_key = {(s.card.code_id, s.card.card_number): s for s in slots}
    assert by_key[("ARG", 1)].generated_image_path == fake_png
    # Las que no tienen archivo: None
    assert by_key[("ARG", 2)].generated_image_path is None


def test_slot_data_image_path_none_when_no_image(memory_db, album_setup, tmp_path, monkeypatch):
    """Sin PNGs en disco, todas las paths son None."""
    monkeypatch.setattr(
        "collections_app.core.services.pdf_generator.get_generated_card_path",
        lambda _cid, key: tmp_path / f"missing-{key}.png",
    )
    slots = PdfAlbumGenerator(memory_db, album_setup)._build_slot_data()
    assert all(s.generated_image_path is None for s in slots)


def test_export_missing_list_creates_txt(memory_db, album_setup, tmp_path):
    out = tmp_path / "missing.txt"
    PdfAlbumGenerator(memory_db, album_setup).export_missing_list(out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "FALTANTES" in content
    # ARG-3 y BRA-2 son las faltantes
    assert "Nahuel Molina".upper() in content.upper()
    assert "Neymar".upper() in content.upper()


def test_export_missing_list_groups_by_code(memory_db, album_setup, tmp_path):
    out = tmp_path / "missing.txt"
    PdfAlbumGenerator(memory_db, album_setup).export_missing_list(out)
    content = out.read_text(encoding="utf-8")
    # Headers de grupos
    assert "ARGENTINA (ARG)" in content
    assert "BRAZIL (BRA)" in content


def test_export_duplicates_list_shows_extra_count(memory_db, album_setup, tmp_path):
    out = tmp_path / "dups.txt"
    PdfAlbumGenerator(memory_db, album_setup).export_duplicates_list(out)
    content = out.read_text(encoding="utf-8")
    assert "REPETIDAS" in content
    # ARG-1 con qty=3 → ×2 copias extra
    assert "×2" in content
    # BRA-1 con qty=2 → ×1
    assert "×1" in content


def test_album_config_show_owned_false_excludes_owned(memory_db, album_setup, tmp_path):
    """show_owned=False → solo cards faltantes en el filter."""
    config = AlbumConfig(show_owned=False, show_missing=True)
    gen = PdfAlbumGenerator(memory_db, album_setup, config=config)
    slots = gen._build_slot_data()
    filtered = gen._filter_by_config(slots)
    assert all(not s.is_owned for s in filtered)


def test_album_config_show_missing_false_excludes_missing(memory_db, album_setup):
    """show_missing=False → solo cards tenidas."""
    config = AlbumConfig(show_owned=True, show_missing=False)
    gen = PdfAlbumGenerator(memory_db, album_setup, config=config)
    slots = gen._build_slot_data()
    filtered = gen._filter_by_config(slots)
    assert all(s.is_owned for s in filtered)


def test_progress_callback_called(memory_db, album_setup, tmp_path):
    """on_progress se invoca durante la generación."""
    calls: list[tuple[int, int]] = []
    out = tmp_path / "album.pdf"
    PdfAlbumGenerator(memory_db, album_setup).generate_unique_album(
        out, on_progress=lambda c, t: calls.append((c, t))
    )
    assert len(calls) > 0
    assert calls[-1][0] == calls[-1][1]  # último progreso = total


def test_export_duplicates_list_when_none(memory_db, sample_collection, tmp_path):
    """Lista de repetidas sin duplicados: muestra mensaje."""
    out = tmp_path / "empty.txt"
    PdfAlbumGenerator(memory_db, sample_collection).export_duplicates_list(out)
    assert "No tenés repetidas" in out.read_text(encoding="utf-8")


def test_slot_data_quantity_property(memory_db, album_setup):
    gen = PdfAlbumGenerator(memory_db, album_setup)
    slots = gen._build_slot_data()
    by_key = {(s.card.code_id, s.card.card_number): s for s in slots}
    assert by_key[("ARG", 1)].quantity == 3
    assert by_key[("ARG", 1)].is_owned is True
    assert by_key[("ARG", 3)].quantity == 0
    assert by_key[("ARG", 3)].is_owned is False
