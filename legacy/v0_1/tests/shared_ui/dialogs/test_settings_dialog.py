"""Tests del SettingsDialog."""

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import SettingsService
from collections_app.shared_ui.dialogs.settings_dialog import SettingsDialog


def _create_collections(memory_db, code_header_id: int) -> list[Collection]:
    repo = CollectionsRepository(memory_db)
    a = repo.create(Collection(None, "Alpha", 10, False, None, code_header_id))
    b = repo.create(Collection(None, "Beta", 20, False, None, code_header_id))
    memory_db.commit()
    return [a, b]


def test_dialog_lists_all_collections(qtbot, memory_db, sample_code_header):
    _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # Combo: 1 placeholder ("(ninguna)") + 2 colecciones
    assert dlg._combo.count() == 3
    labels = [dlg._combo.itemText(i) for i in range(dlg._combo.count())]
    assert "Alpha" in labels
    assert "Beta" in labels


def test_dialog_preselects_current_active(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    SettingsService(memory_db).set_active_collection(cols[1].collection_id)
    memory_db.commit()

    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    assert dlg._combo.currentData() == cols[1].collection_id


def test_accept_saves_setting(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)

    idx = dlg._combo.findData(cols[0].collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg._on_accept()

    assert dlg.selected_collection_id == cols[0].collection_id
    assert SettingsService(memory_db).get_active_collection_id() == cols[0].collection_id


def test_cancel_does_not_save_setting(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)

    idx = dlg._combo.findData(cols[0].collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg.reject()

    assert dlg.selected_collection_id is None
    assert SettingsService(memory_db).get_active_collection_id() is None


def test_dialog_with_no_collections(qtbot, memory_db):
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # Solo el placeholder "(ninguna)"
    assert dlg._combo.count() == 1
    assert dlg._combo.currentData() is None


def test_accepting_none_clears_active(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    SettingsService(memory_db).set_active_collection(cols[0].collection_id)
    memory_db.commit()

    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg._combo.setCurrentIndex(0)  # "(ninguna)"
    dlg._on_accept()

    assert SettingsService(memory_db).get_active_collection_id() is None
