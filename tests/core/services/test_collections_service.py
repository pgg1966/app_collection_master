"""Tests de CollectionsService."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exceptions import CollectionsError


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> CollectionsService:
    return CollectionsService(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def _coll(header_id: int, **overrides: object) -> Collection:
    base: dict[str, object] = {
        "collection_id": None,
        "collection_name": "Test",
        "card_count": 100,
        "requires_code": False,
        "code_field_name": None,
        "code_header_id": header_id,
    }
    base.update(overrides)
    return Collection(**base)  # type: ignore[arg-type]


def test_list_all_empty(service: CollectionsService) -> None:
    assert service.list_all() == []


def test_create_returns_collection_with_id(service: CollectionsService, header_id: int) -> None:
    saved = service.create(_coll(header_id, collection_name="FIFA"))
    assert saved.collection_id is not None


def test_create_with_empty_name_raises(service: CollectionsService, header_id: int) -> None:
    with pytest.raises(CollectionsError, match="name"):
        service.create(_coll(header_id, collection_name=""))


def test_create_duplicate_name_raises(service: CollectionsService, header_id: int) -> None:
    service.create(_coll(header_id, collection_name="Dup"))
    with pytest.raises(CollectionsError, match="ya existe"):
        service.create(_coll(header_id, collection_name="Dup"))


def test_create_unknown_header_raises(service: CollectionsService) -> None:
    with pytest.raises(CollectionsError, match="header"):
        service.create(_coll(999))


def test_create_negative_card_count_raises(service: CollectionsService, header_id: int) -> None:
    with pytest.raises(CollectionsError, match="card_count"):
        service.create(_coll(header_id, card_count=-1))


def test_create_invalid_album_orientation_raises(
    service: CollectionsService, header_id: int
) -> None:
    with pytest.raises(CollectionsError, match="orientation"):
        service.create(_coll(header_id, album_orientation="diagonal"))


def test_create_invalid_album_dims_raises(service: CollectionsService, header_id: int) -> None:
    with pytest.raises(CollectionsError, match="album"):
        service.create(_coll(header_id, album_columns=0))
    with pytest.raises(CollectionsError, match="album"):
        service.create(_coll(header_id, album_rows=0))


def test_get_by_id_returns_none_for_missing(service: CollectionsService) -> None:
    assert service.get_by_id(999) is None


def test_get_by_name_returns_none_for_missing(
    service: CollectionsService,
) -> None:
    assert service.get_by_name("ghost") is None


def test_get_by_name_returns_collection(service: CollectionsService, header_id: int) -> None:
    service.create(_coll(header_id, collection_name="Magic"))
    fetched = service.get_by_name("Magic")
    assert fetched is not None
    assert fetched.collection_name == "Magic"


def test_update_changes_card_count(service: CollectionsService, header_id: int) -> None:
    saved = service.create(_coll(header_id, card_count=100))
    updated = service.update(
        Collection(
            collection_id=saved.collection_id,
            collection_name=saved.collection_name,
            card_count=200,
            requires_code=saved.requires_code,
            code_field_name=saved.code_field_name,
            code_header_id=saved.code_header_id,
            is_premium=saved.is_premium,
            license_key_required=saved.license_key_required,
            album_columns=saved.album_columns,
            album_rows=saved.album_rows,
            album_orientation=saved.album_orientation,
        )
    )
    assert updated.card_count == 200


def test_update_without_id_raises(service: CollectionsService, header_id: int) -> None:
    with pytest.raises(CollectionsError, match="id"):
        service.update(_coll(header_id))


def test_delete_returns_true_when_existed(service: CollectionsService, header_id: int) -> None:
    saved = service.create(_coll(header_id))
    assert saved.collection_id is not None
    assert service.delete(saved.collection_id) is True


def test_delete_returns_false_when_missing(service: CollectionsService) -> None:
    assert service.delete(999) is False
