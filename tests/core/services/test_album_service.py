"""Tests del AlbumService (data layer entre DB y renderers)."""

from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import AlbumService


def _seed(memory_db, sample_collection, codes_lines, cards, inventory=None):
    """Helper: popula codes_lines, cards e (opcional) inventory.

    `codes_lines` es lista de `(code_id, code_name)` o `(code_id, code_name, order)`.
    """
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    cl_repo = CodesLinesRepository(memory_db)
    for entry in codes_lines:
        if len(entry) == 2:
            code_id, code_name = entry
            order = 0
        else:
            code_id, code_name, order = entry
        cl_repo.upsert(CodeLine(hid, code_id, code_name, code_order=order))
    c_repo = CardsRepository(memory_db)
    for code_id, n, name in cards:
        c_repo.upsert(Card(cid, code_id, n, name))
    if inventory:
        i_repo = InventoryRepository(memory_db)
        for code_id, n, qty in inventory:
            i_repo.upsert(InventoryItem(cid, code_id, n, quantity=qty))
    memory_db.commit()


# ----------------------------------------------------------------------
# build_album_cards
# ----------------------------------------------------------------------


def test_build_album_cards_all_present(memory_db, sample_collection):
    """3 cards en DB, 3 en inventario → 3 AlbumCards con qty>0."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "A"), ("ARG", 2, "B"), ("ARG", 3, "C")],
        [("ARG", 1, 1), ("ARG", 2, 2), ("ARG", 3, 1)],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert len(cards) == 3
    assert all(ac.quantity > 0 for ac in cards)


def test_build_album_cards_missing_have_quantity_zero(memory_db, sample_collection):
    """3 cards, solo 1 en inventario → las otras 2 tienen quantity=0."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "A"), ("ARG", 2, "B"), ("ARG", 3, "C")],
        [("ARG", 2, 1)],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_n = {ac.card.card_number: ac.quantity for ac in cards}
    assert by_n == {1: 0, 2: 1, 3: 0}


def test_build_album_cards_sorted_by_code_order_then_number(memory_db, sample_collection):
    """Categorías ordenadas por `code_order` (no alfabético por code_id)."""
    # ZIM (Zimbabwe) tiene code_order=1, ALG (Argelia) tiene order=2,
    # ARG order=3. Si fuera alfabético, ALG iría primero. Con el sort
    # nuevo, ZIM va primero porque tiene order menor.
    _seed(
        memory_db,
        sample_collection,
        [
            ("ZIM", "ZIMBABWE", 1),
            ("ALG", "ALGERIA", 2),
            ("ARG", "ARGENTINA", 3),
        ],
        [
            ("ARG", 1, "Messi"),
            ("ALG", 2, "Mahrez"),
            ("ZIM", 3, "Player"),
            ("ALG", 1, "Brahimi"),
        ],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    keys = [(ac.card.code_id, ac.card.card_number) for ac in cards]
    # ZIM (order=1) → ALG (order=2) → ARG (order=3); dentro de cada
    # categoría, por card_number ascendente.
    assert keys == [
        ("ZIM", 3),
        ("ALG", 1),
        ("ALG", 2),
        ("ARG", 1),
    ]


def test_build_album_cards_falls_back_to_alpha_when_orders_tied(memory_db, sample_collection):
    """Si dos categorías tienen el mismo code_order (default 0), desempata code_id alfa."""
    _seed(
        memory_db,
        sample_collection,
        [("BRA", "BRAZIL"), ("ARG", "ARGENTINA")],  # ambos order=0 implícito
        [("BRA", 1, "Vini"), ("ARG", 1, "Messi")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    keys = [ac.card.code_id for ac in cards]
    assert keys == ["ARG", "BRA"]


def test_build_album_cards_populates_code_order(memory_db, sample_collection):
    """AlbumCard.code_order viene poblado desde codes_lines."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA", 5), ("BRA", "BRAZIL", 7)],
        [("ARG", 1, "Messi"), ("BRA", 1, "Vini")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_code = {ac.card.code_id: ac.code_order for ac in cards}
    assert by_code == {"ARG": 5, "BRA": 7}


def test_build_album_cards_unknown_code_has_order_zero(memory_db, sample_collection):
    """Card con code_id no registrado en codes_lines → code_order=0 (default)."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA", 5)],
        [("XYZ", 1, "Player")],  # XYZ no está en codes_lines
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].code_order == 0


def test_build_album_cards_resolves_code_name(memory_db, sample_collection):
    """El AlbumCard incluye `code_name` del codes_lines, no el id corto."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")],
        [("ARG", 1, "Messi"), ("BRA", 1, "Vini")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_code = {ac.card.code_id: ac.code_name for ac in cards}
    assert by_code == {"ARG": "ARGENTINA", "BRA": "BRAZIL"}


def test_build_album_cards_unknown_code_falls_back_to_id(memory_db, sample_collection):
    """Card con code_id no presente en codes_lines → code_name = code_id."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("XYZ", 1, "Player")],  # code_id no está en codes_lines
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert len(cards) == 1
    assert cards[0].code_name == "XYZ"


def test_build_album_cards_image_path_none_when_not_downloaded(
    memory_db, sample_collection, monkeypatch
):
    """Sin foto descargada → image_path es None."""
    monkeypatch.setattr(
        "collections_app.core.services.album_service.find_card_image",
        lambda _cid, _n: None,
    )
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].image_path is None


def test_build_album_cards_image_path_resolved_when_present(
    memory_db, sample_collection, tmp_path, monkeypatch
):
    """Cuando find_card_image retorna un path existente, AlbumCard lo lleva."""
    fake = tmp_path / "0001.jpg"
    fake.write_bytes(b"x")
    monkeypatch.setattr(
        "collections_app.core.services.album_service.find_card_image",
        lambda _cid, _n: fake,
    )
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].image_path == fake


def test_build_album_cards_propagates_requires_code(memory_db, sample_collection):
    """`requires_code` del Collection se replica en cada AlbumCard."""
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert all(ac.requires_code is sample_collection.requires_code for ac in cards)


# ----------------------------------------------------------------------
# get_code_names
# ----------------------------------------------------------------------


def test_get_code_names_returns_mapping(memory_db, sample_collection):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")],
        [],
    )
    names = AlbumService(memory_db).get_code_names(sample_collection)
    assert names == {"ARG": "ARGENTINA", "BRA": "BRAZIL"}


def test_get_code_names_empty_when_no_lines(memory_db, sample_collection):
    assert AlbumService(memory_db).get_code_names(sample_collection) == {}


# ----------------------------------------------------------------------
# Wrappers de generación: smoke (delegan al renderer)
# ----------------------------------------------------------------------


def test_generate_album_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi"), ("ARG", 2, "Otamendi")],
        [("ARG", 1, 1)],
    )
    out = tmp_path / "album.pdf"
    result = AlbumService(memory_db).generate_album_pdf(sample_collection, out)
    assert out.exists()
    assert result.pages >= 1


def test_generate_missing_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi"), ("ARG", 2, "Otamendi")],
        # ninguna en inventario → ambas son faltantes
    )
    out = tmp_path / "missing.pdf"
    AlbumService(memory_db).generate_missing_pdf(sample_collection, out)
    assert out.exists()


def test_generate_duplicates_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi")],
        [("ARG", 1, 3)],
    )
    out = tmp_path / "dups.pdf"
    AlbumService(memory_db).generate_duplicates_pdf(sample_collection, out)
    assert out.exists()


def test_generate_owned_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi")],
        [("ARG", 1, 1)],
    )
    out = tmp_path / "owned.pdf"
    AlbumService(memory_db).generate_owned_pdf(sample_collection, out)
    assert out.exists()
