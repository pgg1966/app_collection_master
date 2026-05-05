"""Tests del dataclass CodeHeader."""

from __future__ import annotations

from collections_app.core.models.code_header import CodeHeader


def test_code_header_default_max_length_is_5() -> None:
    h = CodeHeader(code_header_id=None, code_header_name="Foo")
    assert h.code_max_length == 5


def test_code_header_with_explicit_max_length() -> None:
    h = CodeHeader(code_header_id=1, code_header_name="Foo", code_max_length=10)
    assert h.code_max_length == 10


def test_code_header_id_can_be_none_for_unsaved() -> None:
    h = CodeHeader(code_header_id=None, code_header_name="Unsaved")
    assert h.code_header_id is None
