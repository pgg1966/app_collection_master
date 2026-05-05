"""Tests del aggregate CodeStats."""

from __future__ import annotations

from collections_app.core.models.aggregates.code_stats import CodeStats


def test_code_stats_holds_fields() -> None:
    s = CodeStats(code_id="ARG", code_name="Argentina", total=10, owned=4, percentage=40.0)
    assert s.code_id == "ARG"
    assert s.code_name == "Argentina"
    assert s.total == 10
    assert s.owned == 4
    assert s.percentage == 40.0
