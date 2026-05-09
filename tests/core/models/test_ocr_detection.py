"""Tests del módulo `ocr_detection` — parser de labels + dataclasses.

TDD obligatorio (lógica testeable). Cubre:

- `parse_label`: 7 casos especificados en el plan.
- `OcrDetection` y `OcrParseError`: equality y hash (frozen+slots).
"""

from __future__ import annotations

import pytest

from collections_app.core.models.ocr_detection import (
    OcrDetection,
    OcrParseError,
    parse_label,
)

# ---------------------------------------------------------------------
# parse_label — colección con código
# ---------------------------------------------------------------------


def test_parse_label_with_dash_returns_code_and_number() -> None:
    assert parse_label("ARG-04", requires_code=True) == ("ARG", 4)


def test_parse_label_no_dash_splits_letters_and_digits() -> None:
    """ARG04 → ARG + 4 (auto-split por la frontera letras/dígitos)."""
    assert parse_label("ARG04", requires_code=True) == ("ARG", 4)


def test_parse_label_lowercase_uppercased() -> None:
    """Códigos siempre normalizados a uppercase."""
    assert parse_label("arg-04", requires_code=True) == ("ARG", 4)


def test_parse_label_strips_whitespace() -> None:
    assert parse_label("  ARG-04  ", requires_code=True) == ("ARG", 4)


def test_parse_label_empty_returns_none() -> None:
    assert parse_label("", requires_code=True) is None


def test_parse_label_blank_returns_none() -> None:
    assert parse_label("   ", requires_code=True) is None


def test_parse_label_only_letters_returns_none() -> None:
    assert parse_label("XYZ-ABC", requires_code=True) is None


def test_parse_label_only_number_with_requires_code_returns_none() -> None:
    """Falta código en una colección que lo requiere → no parsea."""
    assert parse_label("04", requires_code=True) is None


def test_parse_label_negative_or_zero_number_returns_none() -> None:
    assert parse_label("ARG-0", requires_code=True) is None


# ---------------------------------------------------------------------
# parse_label — colección sin código
# ---------------------------------------------------------------------


def test_parse_label_only_number_without_code() -> None:
    assert parse_label("04", requires_code=False) == ("", 4)


def test_parse_label_with_code_kept_when_no_code_required() -> None:
    """Si la collection no requiere código pero el label trae uno,
    lo conservamos (decisión del plan)."""
    assert parse_label("ARG-04", requires_code=False) == ("ARG", 4)


def test_parse_label_empty_no_code_returns_none() -> None:
    assert parse_label("", requires_code=False) is None


def test_parse_label_non_numeric_no_code_returns_none() -> None:
    assert parse_label("abc", requires_code=False) is None


# ---------------------------------------------------------------------
# OcrDetection / OcrParseError dataclasses
# ---------------------------------------------------------------------


def test_ocr_detection_equality_by_value() -> None:
    a = OcrDetection(
        raw_label="ARG-04",
        code_id="ARG",
        card_number=4,
        confidence=0.94,
        card_name="Lautaro",
        card_id=42,
    )
    b = OcrDetection(
        raw_label="ARG-04",
        code_id="ARG",
        card_number=4,
        confidence=0.94,
        card_name="Lautaro",
        card_id=42,
    )
    assert a == b
    assert hash(a) == hash(b)


def test_ocr_detection_is_frozen() -> None:
    d = OcrDetection(
        raw_label="x",
        code_id="X",
        card_number=1,
        confidence=0.0,
        card_name="x",
        card_id=None,
    )
    with pytest.raises((AttributeError, TypeError)):
        d.confidence = 0.5  # type: ignore[misc]


def test_ocr_parse_error_equality() -> None:
    a = OcrParseError(raw_label="???", confidence=0.5, reason="formato no reconocido")
    b = OcrParseError(raw_label="???", confidence=0.5, reason="formato no reconocido")
    assert a == b
