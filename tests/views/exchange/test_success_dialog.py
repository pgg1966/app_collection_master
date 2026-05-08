"""Tests del ExchangeSuccessDialog — smoke + slots conectados."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from collections_app.views.exchange.success_dialog import ExchangeSuccessDialog

pytestmark = pytest.mark.gui


def test_dialog_constructs_with_three_buttons(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")
    dlg = ExchangeSuccessDialog(path=f, collection_name="Mundial 2026")
    qtbot.addWidget(dlg)
    assert dlg._open_folder_btn is not None
    assert dlg._send_mail_btn is not None
    assert dlg._close_btn is not None


def test_open_folder_button_calls_helper(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")
    dlg = ExchangeSuccessDialog(path=f, collection_name="Mundial 2026")
    qtbot.addWidget(dlg)
    with patch(
        "collections_app.views.exchange.success_dialog.open_folder_with_file_selected"
    ) as mock_open:
        dlg._on_open_folder()
    assert mock_open.called
    assert mock_open.call_args.args[0] == f


def test_send_mail_button_calls_helper(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")
    dlg = ExchangeSuccessDialog(path=f, collection_name="Mundial 2026")
    qtbot.addWidget(dlg)
    with patch("collections_app.views.exchange.success_dialog.open_mailto") as mock_mail:
        dlg._on_send_mail()
    assert mock_mail.called
    kwargs = mock_mail.call_args.kwargs
    assert "subject" in kwargs
    assert "body" in kwargs
    assert "Mundial 2026" in kwargs["subject"]


def test_close_button_accepts_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "x.colexchange"
    f.write_text("dummy", encoding="utf-8")
    dlg = ExchangeSuccessDialog(path=f, collection_name="Mundial 2026")
    qtbot.addWidget(dlg)
    dlg._close_btn.click()
    assert dlg.result() == dlg.DialogCode.Accepted
