"""Tests del CollectionsAbmView."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.admin.collections_abm import (
    CollectionEditDialog,
    CollectionsAbmView,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_collections() -> Iterator[AppContext]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="H", code_max_length=3)
        )
        assert h.code_header_id is not None
        for name in ["Coll A", "Coll B"]:
            ctx.collections.create(
                Collection(
                    collection_id=None,
                    collection_name=name,
                    card_count=10,
                    requires_code=True,
                    code_field_name="País",
                    code_header_id=h.code_header_id,
                )
            )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


def test_view_constructs_and_lists_collections(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    assert view._list.count() == 2


# ---------------------------------------------------------------------
# Botón "Configurar modelo OCR" (Sesión 5d / G1+I)
# ---------------------------------------------------------------------


def test_ocr_config_button_hidden_without_admin_env(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin COLLECTIONS_ADMIN=1 el botón existe pero NO se muestra."""
    monkeypatch.delenv("COLLECTIONS_ADMIN", raising=False)
    coll = ctx_with_collections.collections.list_all()[0]
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert dlg._ocr_config_btn.isHidden() is True


def test_ocr_config_button_visible_with_admin_env(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Con COLLECTIONS_ADMIN=1 el botón se muestra (no escondido)."""
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    coll = ctx_with_collections.collections.list_all()[0]
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert dlg._ocr_config_btn.isHidden() is False


def test_ocr_status_label_shows_no_configurado_when_none(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    coll = ctx_with_collections.collections.list_all()[0]
    assert coll.ocr_model_filename is None
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert "No configurado" in dlg._ocr_status_label.text()


def test_configure_ocr_copies_file_and_updates_label(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Click "Configurar modelo..." → file picker → copia + renombra a ocr_<id>.pt."""
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    # Aislar models_dir vía APPDATA (igual que tests de paths.py).
    fake_base = tmp_path / "FakeBase"
    monkeypatch.setenv("APPDATA", str(fake_base))

    src_model = tmp_path / "modelo_descargado.pt"
    src_model.write_bytes(b"\x00" * 16)

    coll = ctx_with_collections.collections.list_all()[0]
    cid = coll.collection_id

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QFileDialog.getOpenFileName",
        lambda *_a, **_k: (str(src_model), "Modelos PyTorch (*.pt)"),
    )

    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    dlg._on_configure_ocr_model()

    expected_filename = f"ocr_{cid}.pt"
    assert dlg._pending_ocr_filename == expected_filename
    assert expected_filename in dlg._ocr_status_label.text()

    # El archivo se copió al models_dir canónico.
    from collections_app.core.utils.paths import get_models_dir

    assert (get_models_dir() / expected_filename).is_file()


def test_configure_ocr_persists_on_accept(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Tras configurar + accept, la collection en DB tiene el filename."""
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    fake_base = tmp_path / "FakeBase"
    monkeypatch.setenv("APPDATA", str(fake_base))

    src_model = tmp_path / "modelo.pt"
    src_model.write_bytes(b"\x00" * 16)

    coll = ctx_with_collections.collections.list_all()[0]
    cid = coll.collection_id

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QFileDialog.getOpenFileName",
        lambda *_a, **_k: (str(src_model), ""),
    )

    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    dlg._on_configure_ocr_model()
    dlg._on_accept()

    fetched = ctx_with_collections.collections.get_by_id(cid or 0)
    assert fetched is not None
    assert fetched.ocr_model_filename == f"ocr_{cid}.pt"


# ---------------------------------------------------------------------
# Botón "Configurar imagen OCR" (Migración 003)
# ---------------------------------------------------------------------


def test_guide_config_button_hidden_without_admin_env(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("COLLECTIONS_ADMIN", raising=False)
    coll = ctx_with_collections.collections.list_all()[0]
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert dlg._guide_config_btn.isHidden() is True


def test_guide_config_button_visible_with_admin_env(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    coll = ctx_with_collections.collections.list_all()[0]
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert dlg._guide_config_btn.isHidden() is False


def test_guide_status_label_shows_no_configurada_when_none(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    coll = ctx_with_collections.collections.list_all()[0]
    assert coll.ocr_guide_filename is None
    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    assert "No configurada" in dlg._guide_status_label.text()


def test_configure_guide_copies_file_and_updates_label(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Click "Configurar imagen..." → copia a images/ con nombre canónico."""
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    fake_base = tmp_path / "FakeBase"
    monkeypatch.setenv("APPDATA", str(fake_base))

    src = tmp_path / "guia_original.PNG"  # mayúsculas a propósito
    src.write_bytes(b"\x89PNG\r\n\x1a\n")

    coll = ctx_with_collections.collections.list_all()[0]
    cid = coll.collection_id

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QFileDialog.getOpenFileName",
        lambda *_a, **_k: (str(src), "Imágenes (*.png)"),
    )

    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    dlg._on_configure_ocr_guide()

    expected_filename = f"ocr_guide_{cid}.png"  # suffix.lower()
    assert dlg._pending_guide_filename == expected_filename
    assert expected_filename in dlg._guide_status_label.text()

    from collections_app.core.utils.paths import get_images_dir

    assert (get_images_dir() / expected_filename).is_file()


def test_configure_guide_persists_on_accept(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    monkeypatch.setenv("COLLECTIONS_ADMIN", "1")
    fake_base = tmp_path / "FakeBase"
    monkeypatch.setenv("APPDATA", str(fake_base))

    src = tmp_path / "guia.jpg"
    src.write_bytes(b"\xff\xd8\xff")

    coll = ctx_with_collections.collections.list_all()[0]
    cid = coll.collection_id

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QFileDialog.getOpenFileName",
        lambda *_a, **_k: (str(src), ""),
    )

    dlg = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dlg)
    dlg._on_configure_ocr_guide()
    dlg._on_accept()

    fetched = ctx_with_collections.collections.get_by_id(cid or 0)
    assert fetched is not None
    assert fetched.ocr_guide_filename == f"ocr_guide_{cid}.jpg"


def test_edit_dialog_updates_name(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    dialog._name_edit.setText("Renamed")
    dialog._on_accept()
    fetched = ctx_with_collections.collections.get_by_id(coll.collection_id or 0)
    assert fetched is not None
    assert fetched.collection_name == "Renamed"


def test_edit_dialog_disables_ok_when_name_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    from PySide6.QtWidgets import QDialogButtonBox

    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    ok = dialog._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok.isEnabled() is True
    dialog._name_edit.setText("")
    assert ok.isEnabled() is False


def test_edit_dialog_warns_on_requires_code_change_with_cards(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si hay cards y se cambia requires_code, pedir confirmación."""
    coll = ctx_with_collections.collections.list_all()[0]
    # Agregar una card.
    ctx_with_collections.cards.create(
        Card(
            card_id=None,
            collection_id=coll.collection_id or 0,
            code_id="X",
            card_number=1,
            card_name="Test",
        )
    )
    ctx_with_collections.conn.commit()

    asked: list[bool] = []

    def fake_question(*_a: object, **_k: object) -> int:
        asked.append(True)
        return QMessageBox.StandardButton.No

    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        fake_question,
    )

    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    dialog._requires_code.setChecked(not coll.requires_code)
    dialog._on_accept()

    assert asked == [True]
    # Como respondió No, no se actualizó.
    fetched = ctx_with_collections.collections.get_by_id(coll.collection_id or 0)
    assert fetched is not None
    assert fetched.requires_code == coll.requires_code


def test_premium_field_is_readonly_label(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
) -> None:
    """is_premium no debe ser editable en MVP."""
    coll = ctx_with_collections.collections.list_all()[0]
    dialog = CollectionEditDialog(ctx=ctx_with_collections, collection=coll)
    qtbot.addWidget(dialog)
    # No hay un widget editable para is_premium.
    assert not hasattr(dialog, "_premium_checkbox")


def test_delete_collection_with_confirmation_removes_from_db(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.Yes,
    )
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    selected = view._selected()
    assert selected is not None
    cid = selected.collection_id

    view._on_delete()
    assert ctx_with_collections.collections.get_by_id(cid or 0) is None
    assert view._list.count() == 1


def test_delete_collection_cancelled_keeps_data(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.No,
    )
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    view._on_delete()
    assert view._list.count() == 2  # nada borrado


def test_delete_emits_collections_changed_signal(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tras delete exitoso se emite `collections_changed` (Sesión 5.5 / C1)."""
    monkeypatch.setattr(
        "collections_app.views.admin.collections_abm.QMessageBox.question",
        lambda *_a, **_k: QMessageBox.StandardButton.Yes,
    )
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    received: list[bool] = []
    view.collections_changed.connect(lambda: received.append(True))
    view._on_delete()
    assert received == [True]


def test_edit_emits_collections_changed_signal(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_collections: AppContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Edit exitoso emite el signal."""
    view = CollectionsAbmView(ctx=ctx_with_collections)
    qtbot.addWidget(view)
    view._list.setCurrentRow(0)
    received: list[bool] = []
    view.collections_changed.connect(lambda: received.append(True))

    # Stub del CollectionEditDialog: aceptar inmediatamente.
    from collections_app.views.admin import collections_abm as mod

    class _StubDialog:
        def __init__(self, **_k):  # type: ignore[no-untyped-def]
            pass

        def exec(self):  # type: ignore[no-untyped-def]
            return mod.QDialog.DialogCode.Accepted

    monkeypatch.setattr(mod, "CollectionEditDialog", _StubDialog)
    view._on_edit()
    assert received == [True]
