"""Tests de los algoritmos puros de format de reports — sin Qt."""

from __future__ import annotations

from collections_app.core.models.card import Card
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.views.reports._formatters import (
    URL_SAFE_LIMIT,
    format_duplicates_report,
    format_missing_report,
    text_fits_in_url,
)


def _line(code_id: str, name: str, order: int) -> CodeLine:
    return CodeLine(
        code_line_id=None,
        code_header_id=1,
        code_id=code_id,
        code_name=name,
        code_order=order,
    )


def _card(card_id: int, code_id: str, number: int) -> Card:
    return Card(
        card_id=card_id,
        collection_id=1,
        code_id=code_id,
        card_number=number,
        card_name=f"{code_id}-{number}",
    )


def _inv(card_id: int, qty: int) -> InventoryItem:
    return InventoryItem(inventory_id=None, card_id=card_id, quantity=qty)


# ---------------------------------------------------------------------
# format_missing_report
# ---------------------------------------------------------------------


def test_missing_empty_collection_returns_empty_string() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    assert format_missing_report([], codes) == ""


def test_missing_no_codes_returns_empty_string() -> None:
    cards = [_card(1, "ARG", 1)]
    assert format_missing_report(cards, []) == ""


def test_missing_one_code_one_card() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    missing = [_card(1, "ARG", 4)]
    assert format_missing_report(missing, codes) == "ARGENTINA: 4"


def test_missing_one_code_multiple_cards_separated_by_dash() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    missing = [_card(1, "ARG", 4), _card(2, "ARG", 7), _card(3, "ARG", 12)]
    assert format_missing_report(missing, codes) == "ARGENTINA: 4 - 7 - 12"


def test_missing_codes_sorted_by_code_order() -> None:
    """code_order=1 antes que code_order=2."""
    codes = [
        _line("BRA", "BRASIL", 2),
        _line("ARG", "ARGENTINA", 1),
    ]
    # codes_in_order ya viene del caller con el orden que quiere.
    codes_sorted = sorted(codes, key=lambda c: c.code_order)
    missing = [_card(1, "ARG", 1), _card(2, "BRA", 3)]
    result = format_missing_report(missing, codes_sorted)
    lines = result.split("\n")
    assert lines[0].startswith("ARGENTINA:")
    assert lines[1].startswith("BRASIL:")


def test_missing_omits_codes_without_missing_cards() -> None:
    codes = [
        _line("ARG", "ARGENTINA", 1),
        _line("BRA", "BRASIL", 2),
        _line("FRA", "FRANCIA", 3),
    ]
    missing = [_card(1, "ARG", 1), _card(2, "FRA", 5)]
    result = format_missing_report(missing, codes)
    assert "BRASIL" not in result
    assert "ARGENTINA: 1" in result
    assert "FRANCIA: 5" in result


def test_missing_numbers_sorted_within_code() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    missing = [_card(1, "ARG", 18), _card(2, "ARG", 4), _card(3, "ARG", 12)]
    assert format_missing_report(missing, codes) == "ARGENTINA: 4 - 12 - 18"


def test_missing_real_mundial_example_from_prompt() -> None:
    codes = [
        _line("PNN", "PANINI", 1),
        _line("ARG", "ARGENTINA", 2),
        _line("BRA", "BRASIL", 3),
        _line("FRA", "FRANCIA", 4),
    ]
    missing = [
        _card(1, "PNN", 1),
        _card(2, "PNN", 2),
        _card(3, "ARG", 4),
        _card(4, "ARG", 7),
        _card(5, "ARG", 12),
        _card(6, "ARG", 18),
        _card(7, "ARG", 23),
        _card(8, "BRA", 2),
        _card(9, "BRA", 5),
        _card(10, "BRA", 9),
        _card(11, "FRA", 1),
        _card(12, "FRA", 3),
        _card(13, "FRA", 6),
        _card(14, "FRA", 11),
        _card(15, "FRA", 15),
        _card(16, "FRA", 19),
    ]
    expected = (
        "PANINI: 1 - 2\n"
        "ARGENTINA: 4 - 7 - 12 - 18 - 23\n"
        "BRASIL: 2 - 5 - 9\n"
        "FRANCIA: 1 - 3 - 6 - 11 - 15 - 19"
    )
    assert format_missing_report(missing, codes) == expected


# ---------------------------------------------------------------------
# format_duplicates_report
# ---------------------------------------------------------------------


def test_duplicates_empty_returns_empty_string() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    assert format_duplicates_report([], {}, codes) == ""


def test_duplicates_quantity_one_skipped() -> None:
    """quantity=1 NO es duplicado, no aparece."""
    codes = [_line("ARG", "ARGENTINA", 1)]
    cards_by_id = {1: _card(1, "ARG", 5)}
    duplicates = [_inv(1, 1)]
    assert format_duplicates_report(duplicates, cards_by_id, codes) == ""


def test_duplicates_quantity_two_shows_x1() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    cards_by_id = {1: _card(1, "ARG", 8)}
    duplicates = [_inv(1, 2)]
    assert format_duplicates_report(duplicates, cards_by_id, codes) == ("ARGENTINA: 8 (x1)")


def test_duplicates_quantity_five_shows_x4() -> None:
    codes = [_line("ARG", "ARGENTINA", 1)]
    cards_by_id = {1: _card(1, "ARG", 8)}
    duplicates = [_inv(1, 5)]
    assert format_duplicates_report(duplicates, cards_by_id, codes) == ("ARGENTINA: 8 (x4)")


def test_duplicates_real_example_from_prompt() -> None:
    codes = [
        _line("ARG", "ARGENTINA", 1),
        _line("BRA", "BRASIL", 2),
    ]
    cards_by_id = {
        1: _card(1, "ARG", 8),
        2: _card(2, "ARG", 14),
        3: _card(3, "BRA", 1),
        4: _card(4, "BRA", 7),
        5: _card(5, "BRA", 19),
    }
    duplicates = [
        _inv(1, 3),  # ARG 8 (x2)
        _inv(2, 4),  # ARG 14 (x3)
        _inv(3, 3),  # BRA 1 (x2)
        _inv(4, 5),  # BRA 7 (x4)
        _inv(5, 3),  # BRA 19 (x2)
    ]
    expected = "ARGENTINA: 8 (x2) - 14 (x3)\n" "BRASIL: 1 (x2) - 7 (x4) - 19 (x2)"
    assert format_duplicates_report(duplicates, cards_by_id, codes) == expected


def test_duplicates_orphan_card_id_skipped() -> None:
    """Si el card_id no está en cards_by_id (caso edge), se omite sin crash."""
    codes = [_line("ARG", "ARGENTINA", 1)]
    cards_by_id: dict[int, Card] = {}  # vacío
    duplicates = [_inv(999, 3)]  # card_id 999 no resuelve
    assert format_duplicates_report(duplicates, cards_by_id, codes) == ""


# ---------------------------------------------------------------------
# text_fits_in_url
# ---------------------------------------------------------------------


def test_text_fits_in_url_short_returns_true() -> None:
    assert text_fits_in_url("hola") is True


def test_text_fits_in_url_at_limit_returns_true() -> None:
    assert text_fits_in_url("a" * URL_SAFE_LIMIT) is True


def test_text_fits_in_url_above_limit_returns_false() -> None:
    assert text_fits_in_url("a" * (URL_SAFE_LIMIT + 1)) is False


def test_text_fits_in_url_custom_limit() -> None:
    assert text_fits_in_url("hola mundo", limit=5) is False
    assert text_fits_in_url("hola", limit=5) is True
