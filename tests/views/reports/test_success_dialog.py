"""Tests del ReportSavedDialog — smoke + slot wiring."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from collections_app.views.reports._success_dialog import ReportSavedDialog

pytestmark = pytest.mark.gui


def test_dialog_constructs_with_two_buttons(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "rep.txt"
    f.write_text("dummy", encoding="utf-8")
    dlg = ReportSavedDialog(path=f)
    qtbot.addWidget(dlg)
    assert dlg._open_folder_btn is not None
    assert dlg._close_btn is not None


def test_open_folder_button_calls_helper(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "rep.txt"
    f.write_text("dummy", encoding="utf-8")
    dlg = ReportSavedDialog(path=f)
    qtbot.addWidget(dlg)
    with patch(
        "collections_app.views.reports._success_dialog.open_folder_with_file_selected"
    ) as mock_open:
        dlg._on_open_folder()
    assert mock_open.called
    assert mock_open.call_args.args[0] == f


def test_close_button_accepts_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
) -> None:
    f = tmp_path / "rep.txt"
    f.write_text("dummy", encoding="utf-8")
    dlg = ReportSavedDialog(path=f)
    qtbot.addWidget(dlg)
    dlg._close_btn.click()
    assert dlg.result() == dlg.DialogCode.Accepted
