"""Tests del CardsCsvImporter."""

from pathlib import Path

import pytest

from collections_app.admin.tools.csv_importer import CardsCsvImporter
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.fixture
def collection_with_codes(memory_db, sample_collection):
    """Carga ARG/BRA/FRA en codes_lines del header de la collection."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in ("ARG", "BRA", "FRA"):
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()
    return sample_collection


def test_import_valid_csv(memory_db, collection_with_codes):
    importer = CardsCsvImporter(memory_db)
    result = importer.import_file(
        FIXTURES / "sample_cards.csv",
        collection_with_codes.collection_id,
    )
    assert result.total_rows == 10
    assert result.imported == 10
    assert result.skipped == 0
    assert result.errors == []
    cards = CardsRepository(memory_db).list_by_collection(collection_with_codes.collection_id)
    assert len(cards) == 10


def test_import_skips_invalid_code_id(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "bad_codes.csv"
    csv.write_text(
        "code_id,card_number,card_name\n" "ARG,1,Messi\n" "ZZZ,1,Desconocido\n" "BRA,1,Vinicius\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 3
    assert result.imported == 2
    assert result.skipped == 1
    assert any("ZZZ" in e for e in result.errors)


def test_import_handles_missing_header_row(memory_db, collection_with_codes, tmp_path):
    """Si la primera fila no es header, se trata como dato."""
    csv = tmp_path / "no_header.csv"
    csv.write_text(
        "ARG,1,Messi\nBRA,2,Neymar\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 2
    assert result.imported == 2


def test_import_handles_unicode_names_with_accents(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "unicode.csv"
    csv.write_text(
        "code_id,card_number,card_name\n" "ARG,1,Ángel Di María\n" "FRA,2,Kylian Mbappé\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 2
    cards = CardsRepository(memory_db).list_by_collection(collection_with_codes.collection_id)
    names = {c.card_name for c in cards}
    assert "Ángel Di María" in names
    assert "Kylian Mbappé" in names


def test_import_with_progress_callback(memory_db, collection_with_codes):
    progress_calls: list[tuple[int, int]] = []
    CardsCsvImporter(memory_db).import_file(
        FIXTURES / "sample_cards.csv",
        collection_with_codes.collection_id,
        on_progress=lambda c, t: progress_calls.append((c, t)),
    )
    assert len(progress_calls) == 10
    assert progress_calls[-1] == (10, 10)


def test_import_skips_invalid_card_number(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "bad_num.csv"
    csv.write_text(
        "ARG,abc,X\nARG,-1,Y\nARG,5,Z\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    assert result.skipped == 2


def test_import_skips_empty_name(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "empty_name.csv"
    csv.write_text(
        "ARG,1,\nARG,2,Messi\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    assert result.skipped == 1


def test_import_rejects_unknown_collection(memory_db):
    importer = CardsCsvImporter(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        importer.import_file(FIXTURES / "sample_cards.csv", 999)


def test_import_empty_csv(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("", encoding="utf-8")
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 0
    assert result.imported == 0


def test_import_overwrites_existing_card(memory_db, collection_with_codes, tmp_path):
    """bulk_upsert debe sobrescribir el card_name si la card ya existía."""
    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(collection_with_codes.collection_id, "ARG", 1, "Old Name"))
    memory_db.commit()
    csv = tmp_path / "update.csv"
    csv.write_text("ARG,1,New Name\n", encoding="utf-8")
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    fresh = cards_repo.get(collection_with_codes.collection_id, "ARG", 1)
    assert fresh is not None
    assert fresh.card_name == "New Name"
