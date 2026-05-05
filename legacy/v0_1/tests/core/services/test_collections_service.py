"""Tests del CollectionsService."""

import pytest

from collections_app.core.models import Collection
from collections_app.core.services import CollectionsService


def test_create_collection_validates_header_exists(memory_db, sample_code_header):
    svc = CollectionsService(memory_db)
    created = svc.create_collection_with_validation(
        Collection(
            collection_id=None,
            collection_name="Test",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    assert created.collection_id is not None


def test_create_collection_rejects_missing_header(memory_db):
    svc = CollectionsService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.create_collection_with_validation(
            Collection(
                collection_id=None,
                collection_name="Test",
                card_count=10,
                requires_code=False,
                code_field_name=None,
                code_header_id=999,
            )
        )


def test_get_full_collection_info_returns_dict(memory_db, sample_collection, sample_cards):
    svc = CollectionsService(memory_db)
    info = svc.get_full_collection_info(sample_collection.collection_id)
    assert info is not None
    assert info["collection"].collection_id == sample_collection.collection_id
    assert info["code_header"] is not None
    assert info["num_cards"] == 5
    assert info["num_codes"] == 0  # no hay codes_lines en sample fixtures


def test_get_full_collection_info_missing(memory_db):
    svc = CollectionsService(memory_db)
    assert svc.get_full_collection_info(999) is None


def test_can_be_deleted_existing(memory_db, sample_collection):
    svc = CollectionsService(memory_db)
    can, reason = svc.can_be_deleted(sample_collection.collection_id)
    assert can is True
    assert reason == ""


def test_can_be_deleted_missing(memory_db):
    svc = CollectionsService(memory_db)
    can, reason = svc.can_be_deleted(999)
    assert can is False
    assert "no existe" in reason
