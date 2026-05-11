"""Tests CRUD de CollectionsRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CollectionsRepository:
    return CollectionsRepository(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def _make(header_id: int, **overrides: object) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": "Test",
        "card_count": 100,
        "requires_code": False,
        "code_field_name": None,
        "code_header_id": header_id,
    }
    base.update(overrides)
    return Collection(**base)  # type: ignore[arg-type]


def test_list_all_empty(repo: CollectionsRepository) -> None:
    assert repo.list_all() == []


def test_create_returns_collection_with_id(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id, collection_name="FIFA"))
    assert saved.collection_id is not None
    assert saved.collection_name == "FIFA"


def test_create_violates_unique_name(repo: CollectionsRepository, header_id: int) -> None:
    repo.create(_make(header_id, collection_name="Dup"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(header_id, collection_name="Dup"))


def test_create_persists_album_defaults(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id))
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.album_columns == 3
    assert fetched.album_rows == 4
    assert fetched.album_orientation == "portrait"


def test_create_persists_album_overrides(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="Land",
            album_columns=2,
            album_rows=3,
            album_orientation="landscape",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.album_columns == 2
    assert fetched.album_rows == 3
    assert fetched.album_orientation == "landscape"


def test_create_persists_premium_and_license(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="Pro",
            is_premium=True,
            license_key_required="hash",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.is_premium is True
    assert fetched.license_key_required == "hash"


def test_create_default_ocr_model_filename_is_none(
    repo: CollectionsRepository, header_id: int
) -> None:
    """Sin pasar `ocr_model_filename` queda None (sin OCR configurado)."""
    saved = repo.create(_make(header_id, collection_name="NoOCR"))
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_model_filename is None


def test_create_persists_ocr_model_filename(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id, collection_name="WithOCR", ocr_model_filename="ocr_42.pt"))
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_model_filename == "ocr_42.pt"


def test_update_persists_ocr_model_filename(repo: CollectionsRepository, header_id: int) -> None:
    """Setear el modelo después de crear debe persistir tras `update`."""
    saved = repo.create(_make(header_id, collection_name="LateOCR"))
    saved.ocr_model_filename = "ocr_99.pt"
    repo.update(saved)
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_model_filename == "ocr_99.pt"


def test_create_default_ocr_guide_filename_is_none(
    repo: CollectionsRepository, header_id: int
) -> None:
    """Sin pasar `ocr_guide_filename` queda None (sin imagen de guía)."""
    saved = repo.create(_make(header_id, collection_name="NoGuide"))
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_guide_filename is None


def test_create_persists_ocr_guide_filename(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(
        _make(header_id, collection_name="WithGuide", ocr_guide_filename="ocr_guide_42.jpg")
    )
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_guide_filename == "ocr_guide_42.jpg"


def test_update_persists_ocr_guide_filename(repo: CollectionsRepository, header_id: int) -> None:
    """Setear la imagen después de crear debe persistir tras `update`."""
    saved = repo.create(_make(header_id, collection_name="LateGuide"))
    saved.ocr_guide_filename = "ocr_guide_99.png"
    repo.update(saved)
    fetched = repo.get_by_id(saved.collection_id or 0)
    assert fetched is not None
    assert fetched.ocr_guide_filename == "ocr_guide_99.png"


def test_create_persists_requires_code_and_field_name(
    repo: CollectionsRepository, header_id: int
) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="WithCode",
            requires_code=True,
            code_field_name="Set",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.requires_code is True
    assert fetched.code_field_name == "Set"


def test_create_violates_album_orientation_check(
    repo: CollectionsRepository, header_id: int
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(header_id, album_orientation="diagonal"))


def test_get_by_id_returns_none_for_missing(repo: CollectionsRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_collection(repo: CollectionsRepository, header_id: int) -> None:
    repo.create(_make(header_id, collection_name="Magic"))
    fetched = repo.get_by_name("Magic")
    assert fetched is not None
    assert fetched.collection_name == "Magic"


def test_get_by_name_returns_none_for_missing(
    repo: CollectionsRepository,
) -> None:
    assert repo.get_by_name("ghost") is None


def test_update_changes_card_count(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id, card_count=100))
    updated = repo.update(
        Collection(
            collection_id=saved.collection_id,
            collection_name=saved.collection_name,
            card_count=200,
            requires_code=saved.requires_code,
            code_field_name=saved.code_field_name,
            code_header_id=saved.code_header_id,
        )
    )
    assert updated.card_count == 200
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.card_count == 200


def test_update_requires_id(repo: CollectionsRepository, header_id: int) -> None:
    with pytest.raises(ValueError, match="collection_id"):
        repo.update(_make(header_id))


def test_delete_returns_true_when_existed(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id))
    assert saved.collection_id is not None
    assert repo.delete(saved.collection_id) is True
    assert repo.get_by_id(saved.collection_id) is None


def test_delete_returns_false_when_missing(repo: CollectionsRepository) -> None:
    assert repo.delete(999) is False


def test_delete_cascades_to_cards(
    repo: CollectionsRepository, header_id: int, db_conn: sqlite3.Connection
) -> None:
    saved = repo.create(_make(header_id))
    assert saved.collection_id is not None
    db_conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) " "VALUES (?, ?, ?, ?)",
        (saved.collection_id, "X", 1, "Test"),
    )
    repo.delete(saved.collection_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
        (saved.collection_id,),
    ).fetchone()
    assert remaining["c"] == 0


def test_list_all_returns_collections_sorted_by_name(
    repo: CollectionsRepository, header_id: int
) -> None:
    repo.create(_make(header_id, collection_name="Zebra"))
    repo.create(_make(header_id, collection_name="Alpha"))
    repo.create(_make(header_id, collection_name="Mike"))
    items = repo.list_all()
    assert [c.collection_name for c in items] == ["Alpha", "Mike", "Zebra"]
    assert all(isinstance(c, Collection) for c in items)
