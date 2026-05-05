"""Tests del dataclass CodeLine."""

from __future__ import annotations

from collections_app.core.models.code_line import CodeLine


def test_code_line_default_order_is_zero() -> None:
    line = CodeLine(code_line_id=None, code_header_id=1, code_id="ARG", code_name="Argentina")
    assert line.code_order == 0


def test_code_line_id_can_be_none() -> None:
    line = CodeLine(code_line_id=None, code_header_id=1, code_id="ARG", code_name="Argentina")
    assert line.code_line_id is None


def test_code_line_with_explicit_order() -> None:
    line = CodeLine(
        code_line_id=5,
        code_header_id=1,
        code_id="MR",
        code_name="Mirage",
        code_order=10,
    )
    assert line.code_order == 10
