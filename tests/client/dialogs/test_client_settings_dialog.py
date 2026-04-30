"""Tests del ClientSettingsDialog."""

import pytest

from collections_app.client.dialogs.client_settings_dialog import ClientSettingsDialog
from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import (
    LicenseService,
    LocalHashLicenseValidator,
    SettingsService,
)

VALID_KEY = "secret-123"


def _make_free(memory_db, sample_code_header, name="Free") -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()
    return col


def _make_premium(memory_db, sample_code_header, name="Premium") -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name=name,
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


@pytest.fixture
def free_col(memory_db, sample_code_header):
    return _make_free(memory_db, sample_code_header)


@pytest.fixture
def premium_col(memory_db, sample_code_header):
    return _make_premium(memory_db, sample_code_header)


def test_dialog_lists_all_collections(qtbot, memory_db, free_col, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # placeholder + 2 colecciones
    assert dlg._combo.count() == 3


def test_free_collection_enables_ok_directly(qtbot, memory_db, free_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    idx = dlg._combo.findData(free_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert dlg._license_container.isVisible() is False


def test_premium_collection_shows_license_field(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is False
    assert dlg._license_container.isVisible() is True


def test_validate_correct_key_unlocks_premium(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    dlg._license_input.setText(VALID_KEY)
    dlg._on_validate_license()

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert LicenseService(memory_db).is_unlocked(premium_col.collection_id) is True


def test_validate_wrong_key_keeps_locked(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    dlg._license_input.setText("wrong")
    dlg._on_validate_license()

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is False
    assert "inválida" in dlg._license_status.text().lower()
    assert LicenseService(memory_db).is_unlocked(premium_col.collection_id) is False


def test_accept_persists_active_collection(qtbot, memory_db, free_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    idx = dlg._combo.findData(free_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg._on_accept()
    assert dlg.selected_collection_id == free_col.collection_id
    assert SettingsService(memory_db).get_active_collection_id() == free_col.collection_id


def test_already_unlocked_premium_does_not_show_license_section(qtbot, memory_db, premium_col):
    """Si la premium fue desbloqueada antes, el dialog no pide la clave de nuevo."""
    LicenseService(memory_db).unlock(premium_col.collection_id, VALID_KEY)

    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert dlg._license_container.isVisible() is False
