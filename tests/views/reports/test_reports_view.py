"""Tests pytest-qt del ReportsView + _ReportSectionWidget."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.views.reports.reports_view import (
    ReportsView,
    _ReportSectionWidget,
    _slugify_for_filename,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_and_collection() -> Iterator[tuple[AppContext, Collection]]:
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        for code, name, order in [
            ("ARG", "ARGENTINA", 1),
            ("BRA", "BRASIL", 2),
        ]:
            ctx.code_lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=h.code_header_id,
                    code_id=code,
                    code_name=name,
                    code_order=order,
                )
            )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Mi Colección 2026",
                card_count=4,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        for code, num in [("ARG", 1), ("ARG", 2), ("BRA", 1), ("BRA", 2)]:
            ctx.cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=num,
                    card_name=f"{code}-{num}",
                )
            )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


# ---------------------------------------------------------------------
# Helper de filename
# ---------------------------------------------------------------------


def test_slugify_replaces_spaces_and_specials() -> None:
    assert _slugify_for_filename("Mi Colección 2026") == "Mi_Colecci_n_2026"
    assert _slugify_for_filename("FIFA/WC*2026") == "FIFA_WC_2026"


def test_slugify_preserves_alnum_dash_underscore() -> None:
    assert _slugify_for_filename("collection_v1-2") == "collection_v1-2"


# ---------------------------------------------------------------------
# ReportsView
# ---------------------------------------------------------------------


def test_view_constructs_with_empty_reports_when_no_inventory(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Sin inventory cargado: faltantes lista todo (las 4 cards)."""
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    missing = view._missing_section.text()
    assert "ARGENTINA: 1 - 2" in missing
    assert "BRASIL: 1 - 2" in missing
    # Repetidas vacío (sin inventory > 1).
    assert view._duplicates_section.text() == ""


def test_view_reports_reflect_inventory(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Faltantes excluye las que tengo, repetidas incluye las > 1."""
    ctx, coll = ctx_and_collection
    cid = coll.collection_id or 0
    ctx.inventory.add_card(cid, "ARG", 1, 1)  # 1 copia → no falta, no repe
    ctx.inventory.add_card(cid, "ARG", 2, 3)  # 3 copias → repe x2
    ctx.inventory.add_card(cid, "BRA", 1, 5)  # 5 copias → repe x4
    ctx.conn.commit()

    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    missing = view._missing_section.text()
    assert "ARGENTINA" not in missing  # ambas tengo
    assert "BRASIL: 2" in missing  # solo BRA-2 falta

    duplicates = view._duplicates_section.text()
    assert "ARGENTINA: 2 (x2)" in duplicates
    assert "BRASIL: 1 (x4)" in duplicates


def test_section_buttons_disabled_when_text_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Sin texto, los 5 botones están disabled."""
    ctx, coll = ctx_and_collection
    section = _ReportSectionWidget(
        title="X", kind="faltantes", collection_name=coll.collection_name
    )
    qtbot.addWidget(section)
    section.set_text("")
    assert section._copy_btn.isEnabled() is False
    assert section._save_btn.isEnabled() is False
    assert section._print_btn.isEnabled() is False
    assert section._mail_btn.isEnabled() is False
    assert section._whatsapp_btn.isEnabled() is False
    section.set_text("ARGENTINA: 1")
    assert section._copy_btn.isEnabled() is True


# ---------------------------------------------------------------------
# Botón Copiar
# ---------------------------------------------------------------------


def test_copy_button_writes_to_clipboard(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    section = view._missing_section
    section._on_copy()
    clipboard_text = QApplication.clipboard().text()
    assert clipboard_text == section.text()


# ---------------------------------------------------------------------
# Botón Guardar
# ---------------------------------------------------------------------


def test_save_button_pre_fills_dialog_with_downloads_and_canonical_name(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """5.5 / B1 revisión: el dialog abre con Descargas + nombre canónico."""
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    fake_downloads = tmp_path / "Downloads"
    fake_downloads.mkdir()
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.get_downloads_dir",
        lambda: fake_downloads,
    )

    # Capturamos el `dir` con el que se abre el QFileDialog y devolvemos
    # un path concreto para que el flow se complete.
    captured: dict[str, str] = {}
    target = tmp_path / "elegido_por_el_usuario.txt"

    def fake_dialog(_self, _title, suggested, _filter):  # type: ignore[no-untyped-def]
        captured["suggested"] = suggested
        return (str(target), "Archivos de texto (*.txt)")

    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QFileDialog.getSaveFileName",
        fake_dialog,
    )
    view._missing_section._on_save()

    # El "suggested" del dialog incluye Descargas + filename canónico.
    assert str(fake_downloads) in captured["suggested"]
    assert "faltantes_" in captured["suggested"]
    assert captured["suggested"].endswith(".txt")
    # El archivo se escribe donde el user eligió.
    assert target.exists()
    assert "ARGENTINA" in target.read_text(encoding="utf-8")


def test_save_button_cancel_does_nothing(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si el user cancela el dialog (path vacío), no se escribe nada."""
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    fake_downloads = tmp_path / "Downloads"
    fake_downloads.mkdir()
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.get_downloads_dir",
        lambda: fake_downloads,
    )
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QFileDialog.getSaveFileName",
        lambda *_a, **_k: ("", ""),
    )
    view._missing_section._on_save()
    # Nada quedó en Descargas.
    assert list(fake_downloads.glob("*")) == []


# ---------------------------------------------------------------------
# Botones Mail / WhatsApp (mockean QDesktopServices.openUrl)
# ---------------------------------------------------------------------


def test_mail_button_short_text_opens_mailto(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    opened: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()) or True,
    )
    view._missing_section._on_mail()
    assert len(opened) == 1
    assert opened[0].startswith("mailto:")
    assert "subject=" in opened[0]


def test_mail_button_long_text_falls_back_to_temp_file(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Texto > 1500 chars → archivo temp + dialog informativo."""
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    # Forzar texto largo.
    view._missing_section.set_text("X" * 2000)

    info_calls: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QMessageBox.information",
        lambda _p, _t, msg: info_calls.append(msg) or 0,
    )
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QDesktopServices.openUrl",
        lambda _url: True,
    )
    view._missing_section._on_mail()
    assert len(info_calls) == 1
    assert "Adjuntalo manualmente" in info_calls[0]


def test_whatsapp_button_short_text_opens_wame(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    opened: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()) or True,
    )
    view._missing_section._on_whatsapp()
    assert len(opened) == 1
    assert opened[0].startswith("https://wa.me/?text=")


def test_whatsapp_button_long_text_falls_back_to_clipboard(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    view._missing_section.set_text("X" * 2000)

    info_calls: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QMessageBox.information",
        lambda _p, _t, msg: info_calls.append(msg) or 0,
    )
    opened: list[str] = []
    monkeypatch.setattr(
        "collections_app.views.reports.reports_view.QDesktopServices.openUrl",
        lambda url: opened.append(url.toString()) or True,
    )

    view._missing_section._on_whatsapp()
    # Clipboard debe tener el texto.
    assert QApplication.clipboard().text() == "X" * 2000
    # Se abrió WhatsApp Web (no wa.me/?text=).
    assert any("web.whatsapp.com" in u for u in opened)
    # Dialog informativo apareció.
    assert len(info_calls) == 1
    assert "demasiado largo" in info_calls[0]


# ---------------------------------------------------------------------
# Print (mocked)
# ---------------------------------------------------------------------


def test_print_button_opens_print_dialog_and_renders(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mockear QPrintDialog para no abrir UI; verifica que document.print_ se
    invoca cuando el dialog acepta."""
    from PySide6.QtPrintSupport import QPrintDialog

    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    # Forzar el dialog a "Accepted".
    monkeypatch.setattr(QPrintDialog, "exec", lambda self: QPrintDialog.DialogCode.Accepted)
    # Capturar llamadas a QTextDocument.print_.
    print_calls: list[bool] = []

    from PySide6.QtGui import QTextDocument

    real_print = QTextDocument.print_

    def fake_print(self: QTextDocument, printer: object) -> None:
        print_calls.append(True)

    monkeypatch.setattr(QTextDocument, "print_", fake_print)
    try:
        view._missing_section._on_print()
    finally:
        monkeypatch.setattr(QTextDocument, "print_", real_print)
    assert print_calls == [True]


def test_print_button_cancel_does_not_print(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtPrintSupport import QPrintDialog

    ctx, coll = ctx_and_collection
    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)

    monkeypatch.setattr(QPrintDialog, "exec", lambda self: QPrintDialog.DialogCode.Rejected)
    print_calls: list[bool] = []
    from PySide6.QtGui import QTextDocument

    monkeypatch.setattr(QTextDocument, "print_", lambda self, p: print_calls.append(True))
    view._missing_section._on_print()
    assert print_calls == []


# ---------------------------------------------------------------------
# set_active_collection
# ---------------------------------------------------------------------


def test_set_active_collection_swaps_data(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    ctx, coll = ctx_and_collection
    other = ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="Otra",
            card_count=0,
            requires_code=False,
            code_field_name=None,
            code_header_id=coll.code_header_id,
        )
    )
    ctx.conn.commit()

    view = ReportsView(ctx=ctx, collection=coll)
    qtbot.addWidget(view)
    assert "ARGENTINA" in view._missing_section.text()

    view.set_active_collection(other)
    # Sin cards en "Otra", missing está vacío.
    assert view._missing_section.text() == ""
