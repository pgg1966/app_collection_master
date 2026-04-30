"""Tests del LicenseService y LocalHashLicenseValidator."""

import pytest

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import (
    LicenseService,
    LicenseValidator,
    LocalHashLicenseValidator,
)

VALID_KEY = "secret-123"


@pytest.fixture
def free_collection(memory_db, sample_code_header) -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Free",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=False,
            license_key_required=None,
        )
    )
    memory_db.commit()
    return col


@pytest.fixture
def premium_collection(memory_db, sample_code_header) -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Premium",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=True,
            license_key_required=LocalHashLicenseValidator.hash_key(VALID_KEY),
        )
    )
    memory_db.commit()
    return col


def test_free_collection_is_always_unlocked(memory_db, free_collection):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(free_collection.collection_id) is True


def test_premium_collection_locked_by_default(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_unlock_with_correct_key_persists(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.unlock(premium_collection.collection_id, VALID_KEY) is True
    assert svc.is_unlocked(premium_collection.collection_id) is True
    # Persiste tras reinstanciar el service
    svc2 = LicenseService(memory_db)
    assert svc2.is_unlocked(premium_collection.collection_id) is True


def test_unlock_with_wrong_key_fails(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.unlock(premium_collection.collection_id, "wrong") is False
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_already_unlocked_returns_true(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    # Llamar unlock de nuevo con la misma key debe seguir true
    assert svc.unlock(premium_collection.collection_id, VALID_KEY) is True
    assert svc.is_unlocked(premium_collection.collection_id) is True


def test_lock_removes_persisted_key(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    svc.lock(premium_collection.collection_id)
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_hash_key_is_deterministic():
    a = LocalHashLicenseValidator.hash_key("foo")
    b = LocalHashLicenseValidator.hash_key("foo")
    assert a == b
    assert a != LocalHashLicenseValidator.hash_key("bar")


def test_validator_swappable(memory_db, premium_collection):
    """Se puede inyectar un validador alternativo (futuro: HTTP)."""

    class AcceptAllValidator(LicenseValidator):
        def validate(self, collection_id: int, license_key: str) -> bool:
            return True

        def is_required(self, collection: Collection) -> bool:
            return False

    svc = LicenseService(memory_db, validator=AcceptAllValidator())
    assert svc.is_unlocked(premium_collection.collection_id) is True
    assert svc.unlock(premium_collection.collection_id, "anything") is True


def test_unknown_collection_returns_false(memory_db):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(9999) is False


def test_admin_changes_required_key_invalidates_unlock(memory_db, premium_collection):
    """Si el admin cambia el license_key_required, el unlock previo se invalida."""
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    assert svc.is_unlocked(premium_collection.collection_id) is True

    # Admin cambia la key
    repo = CollectionsRepository(memory_db)
    new_required = LocalHashLicenseValidator.hash_key("new-secret")
    updated = Collection(
        collection_id=premium_collection.collection_id,
        collection_name=premium_collection.collection_name,
        card_count=premium_collection.card_count,
        requires_code=premium_collection.requires_code,
        code_field_name=premium_collection.code_field_name,
        code_header_id=premium_collection.code_header_id,
        is_premium=True,
        license_key_required=new_required,
    )
    repo.update(updated)
    memory_db.commit()

    # El unlock previo ya no vale
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_is_required_only_when_premium_with_key(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    # Premium pero sin license_key_required → NO requerida (datos inconsistentes;
    # tratamos como free para no lockear al usuario por error de admin).
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Inconsistent",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=True,
            license_key_required=None,
        )
    )
    memory_db.commit()
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(col.collection_id) is True
