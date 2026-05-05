"""Tests del dataclass CardImage."""

from __future__ import annotations

from collections_app.core.models.card_image import CardImage


def test_card_image_minimal() -> None:
    img = CardImage(card_image_id=None, card_id=1, found_photo=False)
    assert img.image_source is None
    assert img.image_path is None
    assert img.generated_at is None


def test_card_image_with_all_fields() -> None:
    img = CardImage(
        card_image_id=10,
        card_id=1,
        found_photo=True,
        image_source="wikipedia",
        image_path="/tmp/x.png",
        generated_at="2026-05-05T10:00:00Z",
    )
    assert img.found_photo is True
    assert img.image_source == "wikipedia"
    assert img.image_path == "/tmp/x.png"
    assert img.generated_at == "2026-05-05T10:00:00Z"
