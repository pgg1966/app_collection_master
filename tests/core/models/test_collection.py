"""Tests del dataclass Collection."""

from __future__ import annotations

from collections_app.core.models.collection import Collection


def _minimal(**overrides: object) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": "Test",
        "card_count": 100,
        "requires_code": False,
        "code_field_name": None,
        "code_header_id": 1,
    }
    base.update(overrides)
    return Collection(**base)  # type: ignore[arg-type]


def test_collection_minimal_uses_album_defaults() -> None:
    c = _minimal()
    assert c.album_columns == 3
    assert c.album_rows == 4
    assert c.album_orientation == "portrait"


def test_collection_default_is_premium_is_false() -> None:
    c = _minimal()
    assert c.is_premium is False
    assert c.license_key_required is None


def test_collection_with_premium_and_license() -> None:
    c = _minimal(is_premium=True, license_key_required="hash123")
    assert c.is_premium is True
    assert c.license_key_required == "hash123"


def test_collection_with_landscape_album() -> None:
    c = _minimal(album_orientation="landscape", album_columns=2, album_rows=3)
    assert c.album_orientation == "landscape"
    assert c.album_columns == 2
    assert c.album_rows == 3
