"""Tests del StatsView."""

import pytest

from collections_app.client.views.stats_view import StatsView
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def stats_setup(memory_db, sample_collection):
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines.upsert(CodeLine(hid, "BRA", "Brasil"))

    cards = CardsRepository(memory_db)
    # Catálogo: 4 ARG, 4 BRA
    for n in (1, 2, 3, 4):
        cards.upsert(Card(cid, "ARG", n, f"Player ARG-{n}"))
        cards.upsert(Card(cid, "BRA", n, f"Player BRA-{n}"))

    inv = InventoryService(memory_db)
    inv.add_card(cid, "ARG", 1, 3)  # repetida x3
    inv.add_card(cid, "ARG", 2, 1)  # tengo
    inv.add_card(cid, "BRA", 1, 2)  # repetida x2
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, stats_setup):
    v = StatsView(memory_db, stats_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def test_overall_progress_calculated_correctly(qtbot, view):
    """3 owned / 8 total = 37.5%."""
    text = view._overall_label.text()
    assert "3/8" in text
    assert "37.5" in text


def test_overall_bar_value_matches(qtbot, view):
    assert view._overall_bar.maximum() == 8
    assert view._overall_bar.value() == 3


def test_progress_by_code_shown(qtbot, view):
    """Debe haber un row por cada code (ARG y BRA)."""
    # Cada row es un widget hijo del container
    assert view._per_code_layout.count() == 2


def test_top_duplicates_displayed(qtbot, view):
    """Las dos cards repetidas (ARG-1 x3, BRA-1 x2) aparecen."""
    # 2 widgets en el layout (no el placeholder de "sin repetidas")
    count = view._top_dup_layout.count()
    assert count == 2


def test_top_duplicates_placeholder_when_none(qtbot, memory_db, sample_collection):
    """Sin duplicados, muestra placeholder."""
    v = StatsView(memory_db, sample_collection)
    qtbot.addWidget(v)
    v.show()
    # 1 widget (label "sin repetidas todavía")
    assert v._top_dup_layout.count() == 1


def test_summary_shows_correct_numbers(qtbot, view):
    text = view._summary_label.text()
    # Total físico = 3 + 1 + 2 = 6
    assert "6" in text
    # Cards únicas = 3
    assert "3" in text
    # Copias extra = (3-1) + (2-1) = 3
    assert "3" in text


def test_refresh_updates_numbers(qtbot, memory_db, view, stats_setup):
    """Cambiar el inventario externamente y refrescar refleja los nuevos valores."""
    InventoryService(memory_db).add_card(stats_setup.collection_id, "BRA", 2, 1)
    view.refresh()
    # Ahora 4 owned / 8 total = 50%
    assert "4/8" in view._overall_label.text()
    assert "50.0" in view._overall_label.text()
