"""Tests del SettingsService."""

from collections_app.core.services import SettingsService


def test_get_active_collection_id_when_unset(memory_db):
    svc = SettingsService(memory_db)
    assert svc.get_active_collection_id() is None


def test_set_and_get_active_collection_id(memory_db):
    svc = SettingsService(memory_db)
    svc.set_active_collection(42)
    assert svc.get_active_collection_id() == 42


def test_clear_active_collection(memory_db):
    svc = SettingsService(memory_db)
    svc.set_active_collection(42)
    svc.clear_active_collection()
    assert svc.get_active_collection_id() is None


def test_get_active_collection_returns_none_when_unset(memory_db):
    svc = SettingsService(memory_db)
    assert svc.get_active_collection() is None


def test_get_active_collection_returns_full_object(memory_db, sample_collection):
    svc = SettingsService(memory_db)
    svc.set_active_collection(sample_collection.collection_id)
    found = svc.get_active_collection()
    assert found is not None
    assert found.collection_id == sample_collection.collection_id


def test_get_active_collection_handles_stale_id(memory_db):
    """Si el setting apunta a un id inexistente, retorna None sin romper."""
    svc = SettingsService(memory_db)
    svc.set_active_collection(9999)
    assert svc.get_active_collection() is None
