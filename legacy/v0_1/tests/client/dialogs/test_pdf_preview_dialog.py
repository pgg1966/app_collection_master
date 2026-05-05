"""Tests del PdfPreviewDialog: cancel borra temp, save copia y opcionalmente abre."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox

from collections_app.client.dialogs.pdf_preview_dialog import PdfPreviewDialog

# Bytes mínimos válidos de un PDF (header + EOF). Suficiente para que
# QPdfDocument lo reconozca como PDF al abrirlo (puede mostrar página
# vacía o fallar silenciosamente — el dialog cae al fallback).
_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\n"
    b"0000000000 65535 f\n"
    b"0000000009 00000 n\n"
    b"0000000052 00000 n\n"
    b"0000000101 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n160\n%%EOF\n"
)


@pytest.fixture
def temp_pdf(tmp_path) -> Path:
    """Crea un archivo .pdf mínimo válido en tmp_path."""
    p = tmp_path / "preview_input.pdf"
    p.write_bytes(_MINIMAL_PDF)
    return p


def test_cancel_deletes_temp_file(qtbot, temp_pdf):
    """Click Cancelar borra el archivo temp y devuelve None."""
    assert temp_pdf.exists()
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_cancel()
    qtbot.wait(50)
    assert not temp_pdf.exists()
    assert dialog.saved_path() is None


def test_save_copies_to_destination(qtbot, temp_pdf, tmp_path, monkeypatch):
    """Click Guardar copia al destino, borra el temp y setea saved_path."""
    dest = tmp_path / "saved_output.pdf"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *a, **kw: (str(dest), "PDF (*.pdf)")),
    )
    # Mockear QMessageBox.exec para que no bloquee con el "Abrir/OK".
    # En PySide6 QMessageBox.exec retorna el StandardButton presionado.
    monkeypatch.setattr(QMessageBox, "exec", lambda self: None)
    # clickedButton() devuelve None tras nuestro mock → no se intenta abrir.

    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_save()
    qtbot.wait(50)

    assert dest.exists()
    assert dest.read_bytes() == _MINIMAL_PDF
    assert not temp_pdf.exists()
    assert dialog.saved_path() == dest


def test_save_canceled_keeps_temp(qtbot, temp_pdf, monkeypatch):
    """Si el usuario cancela el QFileDialog: NO borra el temp ni cierra dialog."""
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *a, **kw: ("", "")),  # path vacío = cancelado
    )
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_save()
    qtbot.wait(50)
    # El temp sigue ahí, saved_path sigue None
    assert temp_pdf.exists()
    assert dialog.saved_path() is None


def test_close_event_cleans_temp(qtbot, temp_pdf):
    """Cerrar el dialog con la X (o reject) también borra el temp."""
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog.close()
    qtbot.wait(50)
    assert not temp_pdf.exists()
