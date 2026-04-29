"""Tests del CollectionsRepository."""

import sqlite3

import pytest

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository


def _build(header_id: int, name: str = "Test", **kwargs) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": name,
        "card_count": 100,
        "requires_code": True,
        "code_field_name": "Set",
        "code_header_id": header_id,
        "is_premium": False,
        "license_key_required": None,
    }
    base.update(kwargs)
    return Collection(**base)


def test_create_returns_with_id(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    created = repo.create(_build(sample_code_header.code_header_id))
    assert created.collection_id is not None


def test_create_persists_premium_and_license(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    created = repo.create(
        _build(
            sample_code_header.code_header_id,
            name="Premium",
            is_premium=True,
            license_key_required="hash-abc",
        )
    )
    found = repo.get_by_id(created.collection_id)
    assert found is not None
    assert found.is_premium is True
    assert found.license_key_required == "hash-abc"


def test_get_by_id_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    found = repo.get_by_id(sample_collection.collection_id)
    assert found == sample_collection


def test_get_by_id_missing(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.get_by_id(999) is None


def test_get_by_name_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    found = repo.get_by_name("FIFA WC 2026")
    assert found is not None
    assert found.collection_id == sample_collection.collection_id


def test_get_by_name_missing(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.get_by_name("NOPE") is None


def test_list_all_empty(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.list_all() == []


def test_list_all_sorted_by_name(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.create(_build(hid, name="Zeta"))
    repo.create(_build(hid, name="Alpha"))
    names = [c.collection_name for c in repo.list_all()]
    assert names == ["Alpha", "Zeta"]


def test_update_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    updated = Collection(
        collection_id=sample_collection.collection_id,
        collection_name="FIFA WC 2026 (revised)",
        card_count=400,
        requires_code=False,
        code_field_name=None,
        code_header_id=sample_collection.code_header_id,
        is_premium=True,
        license_key_required="hash-xyz",
    )
    repo.update(updated)
    fresh = repo.get_by_id(sample_collection.collection_id)
    assert fresh == updated


def test_update_without_id_raises(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    with pytest.raises(ValueError, match="collection_id"):
        repo.update(_build(sample_code_header.code_header_id))


def test_delete_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id) is True
    assert repo.get_by_id(sample_collection.collection_id) is None


def test_delete_nonexistent(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.delete(999) is False


def test_unique_name(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.create(_build(hid, name="X"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_build(hid, name="X"))


def test_invalid_code_header_fk(memory_db):
    repo = CollectionsRepository(memory_db)
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_build(header_id=999))
