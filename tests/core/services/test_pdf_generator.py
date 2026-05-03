"""Tests de los generadores de PDF (álbum + listas + metadata de intercambio)."""

import json
import os
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter

from collections_app.core.models import Card, Collection
from collections_app.core.services.pdf_generator import (
    EXCHANGE_APP_NAME,
    AlbumCard,
    _build_exchange_metadata,
    _chunks,
    format_label,
    generate_album_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
    validate_exchange_pdf_metadata,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _collection(
    name: str = "WC2026",
    cid: int = 1,
    requires_code: bool = True,
    cols: int = 3,
    rows: int = 4,
    orientation: str = "portrait",
) -> Collection:
    return Collection(
        collection_id=cid,
        collection_name=name,
        card_count=100,
        requires_code=requires_code,
        code_field_name="País" if requires_code else None,
        code_header_id=1,
        album_columns=cols,
        album_rows=rows,
        album_orientation=orientation,
    )


def _card(code: str, n: int, name: str = "Player") -> Card:
    return Card(collection_id=1, code_id=code, card_number=n, card_name=name)


def _ac(
    code: str,
    n: int,
    qty: int = 0,
    image_path: Path | None = None,
    requires_code: bool = True,
    code_name: str | None = None,
    name: str = "Player",
) -> AlbumCard:
    return AlbumCard(
        card=_card(code, n, name),
        quantity=qty,
        image_path=image_path,
        requires_code=requires_code,
        code_name=code_name or code,
    )


def _make_jpeg(path: Path, w: int = 100, h: int = 100) -> Path:
    """Genera un JPEG simple para usar como image_path en tests."""
    img = Image.frombytes("RGB", (w, h), os.urandom(w * h * 3))
    img.save(path, format="JPEG")
    return path


# ----------------------------------------------------------------------
# Helpers básicos: format_label / _chunks
# ----------------------------------------------------------------------


def test_format_label_requires_code():
    assert format_label(5, "ARG", requires_code=True) == "ARG-5"


def test_format_label_no_code():
    assert format_label(42, "ANY", requires_code=False) == "42"


def test_chunks_basic():
    assert _chunks([], 3) == []
    items = [_ac("X", n) for n in range(1, 6)]
    chunks = _chunks(items, 2)
    assert [len(c) for c in chunks] == [2, 2, 1]


# ----------------------------------------------------------------------
# Álbum visual
# ----------------------------------------------------------------------


def test_album_pdf_creates_nonempty_file(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=2, image_path=_make_jpeg(tmp_path / "img1.jpg")),  # CASO A
        _ac("ARG", 2, qty=1, code_name="ARGENTINA"),  # CASO B
        _ac("ARG", 3, qty=0, code_name="ARGENTINA"),  # CASO C
    ]
    out = tmp_path / "album.pdf"
    result = generate_album_pdf(col, cards, out)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages == 1


def test_album_pdf_new_category_new_page(tmp_path):
    """12 cards de ARG (llenan 1 página) + 1 de BRA = 2 páginas."""
    col = _collection(cols=3, rows=4)  # 12 cards/página
    cards_arg = [_ac("ARG", n, qty=1) for n in range(1, 13)]
    cards_bra = [_ac("BRA", 1, qty=1)]
    out = tmp_path / "album.pdf"
    result = generate_album_pdf(col, cards_arg + cards_bra, out)
    assert result.pages == 2


def test_album_pdf_12_same_category_one_page(tmp_path):
    col = _collection(cols=3, rows=4)
    cards = [_ac("ARG", n, qty=1) for n in range(1, 13)]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.pages == 1


def test_album_pdf_13_same_category_two_pages(tmp_path):
    col = _collection(cols=3, rows=4)
    cards = [_ac("ARG", n, qty=1) for n in range(1, 14)]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.pages == 2


def test_album_pdf_stats_count_each_case(tmp_path):
    col = _collection()
    img1 = _make_jpeg(tmp_path / "img1.jpg")
    img2 = _make_jpeg(tmp_path / "img2.jpg")
    cards = [
        _ac("ARG", 1, qty=1, image_path=img1),  # A
        _ac("ARG", 2, qty=2, image_path=img2),  # A
        _ac("ARG", 3, qty=1),  # B
        _ac("ARG", 4, qty=0),  # C
        _ac("ARG", 5, qty=0),  # C
    ]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.cards_with_image == 2
    assert result.cards_celeste_placeholder == 1
    assert result.cards_missing == 2


def test_album_pdf_no_photo_when_quantity_zero(tmp_path):
    """Aunque la foto exista en disco, si quantity=0 NO se muestra (CASO C).

    El álbum representa la colección del usuario, no el catálogo.
    """
    col = _collection()
    img = _make_jpeg(tmp_path / "exists.jpg")
    cards = [
        _ac("ARG", 1, qty=0, image_path=img),  # foto en disco PERO no la tengo
    ]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    # Debe contar como missing (CASO C), NO como with_image (CASO A).
    assert result.cards_with_image == 0
    assert result.cards_missing == 1


def test_album_pdf_landscape_uses_landscape_pagesize(tmp_path):
    """Si la colección es landscape, el PDF también lo es (ancho > alto)."""
    col = _collection(orientation="landscape")
    cards = [_ac("ARG", 1, qty=1)]
    out = tmp_path / "album.pdf"
    generate_album_pdf(col, cards, out)
    reader = PdfReader(str(out))
    page = reader.pages[0]
    assert float(page.mediabox.width) > float(page.mediabox.height)


def test_album_pdf_portrait_uses_portrait_pagesize(tmp_path):
    col = _collection(orientation="portrait")
    cards = [_ac("ARG", 1, qty=1)]
    out = tmp_path / "album.pdf"
    generate_album_pdf(col, cards, out)
    reader = PdfReader(str(out))
    page = reader.pages[0]
    assert float(page.mediabox.height) > float(page.mediabox.width)


def test_album_pdf_empty_input_creates_one_page(tmp_path):
    col = _collection()
    result = generate_album_pdf(col, [], tmp_path / "album.pdf")
    assert result.pages == 1


# ----------------------------------------------------------------------
# Faltantes
# ----------------------------------------------------------------------


def test_missing_pdf_creates_file(tmp_path):
    col = _collection()
    cards = [_ac("ARG", n, qty=0) for n in range(1, 6)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)
    assert out.exists()
    assert out.stat().st_size > 1000


def test_missing_pdf_only_includes_quantity_zero(tmp_path):
    """Solo las cards con qty==0 entran en faltantes."""
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=0),
        _ac("BRA", 1, qty=2),
        _ac("BRA", 2, qty=0),
    ]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)
    # Inspeccionamos la metadata embebida para verificar conteo
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    # 3 faltantes: ARG-1, ARG-3, BRA-2
    assert len(meta["cards"]) == 3
    assert all(card["quantity"] == 0 for card in meta["cards"])


# ----------------------------------------------------------------------
# Repetidas
# ----------------------------------------------------------------------


def test_duplicates_pdf_only_includes_quantity_gt_1(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=2),
        _ac("ARG", 4, qty=3),
        _ac("ARG", 5, qty=1),
    ]
    out = tmp_path / "duplicates.pdf"
    generate_duplicates_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert len(meta["cards"]) == 2
    assert {c["card_number"] for c in meta["cards"]} == {3, 4}


# ----------------------------------------------------------------------
# Owned
# ----------------------------------------------------------------------


def test_owned_pdf_only_includes_quantity_gte_1(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=5),
    ]
    out = tmp_path / "owned.pdf"
    generate_owned_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert {c["card_number"] for c in meta["cards"]} == {2, 3}


# ----------------------------------------------------------------------
# Metadata de intercambio
# ----------------------------------------------------------------------


def test_exchange_metadata_roundtrip(tmp_path):
    """Generar PDF de faltantes → validate retorna metadata coherente."""
    col = _collection(name="WC2026", cid=42)
    cards = [_ac("ARG", 1, qty=0), _ac("BRA", 5, qty=0)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)

    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["app"] == EXCHANGE_APP_NAME
    assert meta["subtype"] == "missing"
    assert meta["collection_id"] == 42
    assert meta["collection_name"] == "WC2026"
    assert "checksum" in meta
    assert len(meta["checksum"]) == 16
    assert "generated_at" in meta


def test_exchange_metadata_tampered_checksum_fails(tmp_path):
    """Si modificamos los Keywords del PDF, validate retorna None."""
    col = _collection()
    cards = [_ac("ARG", 1, qty=0)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)

    # Reescribir el PDF con Keywords manipulados
    reader = PdfReader(str(out))
    writer = PdfWriter(clone_from=reader)
    bad_data = json.loads(reader.metadata["/Keywords"])
    bad_data["cards"].append({"code_id": "FAKE", "card_number": 999, "quantity": 0})
    writer.add_metadata({"/Keywords": json.dumps(bad_data)})
    tampered = tmp_path / "tampered.pdf"
    with open(tampered, "wb") as fp:
        writer.write(fp)

    assert validate_exchange_pdf_metadata(tampered) is None


def test_exchange_metadata_unrelated_pdf_returns_none(tmp_path):
    """Un PDF cualquiera (sin metadata de CollectionsApp) → None."""
    plain = tmp_path / "plain.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(plain, "wb") as fp:
        writer.write(fp)
    assert validate_exchange_pdf_metadata(plain) is None


def test_build_exchange_metadata_includes_required_keys():
    raw = _build_exchange_metadata(
        subtype="missing",
        collection_id=1,
        collection_name="X",
        cards=[{"code_id": "ARG", "card_number": 5, "quantity": 0}],
    )
    data = json.loads(raw)
    assert data["app"] == EXCHANGE_APP_NAME
    assert data["subtype"] == "missing"
    assert data["cards"][0]["card_number"] == 5
    assert "checksum" in data
    # Generated_at no participa en el checksum: dos invocaciones tienen el
    # mismo checksum incluso en distinto microsegundo.
    raw2 = _build_exchange_metadata(
        subtype="missing",
        collection_id=1,
        collection_name="X",
        cards=[{"code_id": "ARG", "card_number": 5, "quantity": 0}],
    )
    assert json.loads(raw2)["checksum"] == data["checksum"]
