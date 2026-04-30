"""Tests de datetime_helpers."""

from datetime import UTC, datetime, timedelta, timezone

from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    format_for_display,
    parse_db_datetime,
    to_local,
    utc_now,
)


def test_utc_now_has_utc_tzinfo():
    now = utc_now()
    assert now.tzinfo is UTC


def test_utc_now_is_close_to_real_now():
    now = utc_now()
    real = datetime.now(UTC)
    assert abs((real - now).total_seconds()) < 1


def test_to_local_converts_utc_to_local():
    utc_dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    local = to_local(utc_dt)
    # El resultado tiene tzinfo (no UTC necesariamente)
    assert local.tzinfo is not None
    # Debe representar el mismo instante
    assert local.timestamp() == utc_dt.timestamp()


def test_to_local_assumes_utc_for_naive():
    naive = datetime(2026, 4, 30, 18, 0)
    local = to_local(naive)
    # Mismo instante que naive interpretado como UTC
    expected_utc = naive.replace(tzinfo=UTC)
    assert local.timestamp() == expected_utc.timestamp()


def test_parse_db_datetime_returns_utc():
    dt = parse_db_datetime("2026-04-30 18:00:00")
    assert dt.tzinfo is UTC
    assert dt.year == 2026 and dt.hour == 18


def test_parse_db_datetime_accepts_iso():
    """Fallback para timestamps ISO (microsegundos)."""
    dt = parse_db_datetime("2026-04-30T18:00:00.123456")
    assert dt.tzinfo is UTC


def test_format_for_db_with_utc_datetime():
    dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    assert format_for_db(dt) == "2026-04-30 18:00:00"


def test_format_for_db_converts_local_to_utc():
    """Un datetime con tzinfo no-UTC se convierte antes de formatear."""
    # Forzar tzinfo +03:00 → 21:00 local equivale a 18:00 UTC
    tz_3 = timezone(timedelta(hours=3))
    dt = datetime(2026, 4, 30, 21, 0, tzinfo=tz_3)
    assert format_for_db(dt) == "2026-04-30 18:00:00"


def test_format_for_db_naive_is_treated_as_utc():
    naive = datetime(2026, 4, 30, 18, 0)
    assert format_for_db(naive) == "2026-04-30 18:00:00"


def test_format_for_display_uses_local_time():
    """Lo que sale es la hora del sistema; verificamos que el instante coincide."""
    utc_dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    out = format_for_display(utc_dt)
    # Re-parsear lo formateado y comparar instantes
    local_dt = datetime.strptime(out, "%Y-%m-%d %H:%M").astimezone()
    # Diferencia menor a un minuto (formato sin segundos)
    assert abs(local_dt.timestamp() - utc_dt.timestamp()) < 60


def test_format_for_display_with_seconds():
    utc_dt = datetime(2026, 4, 30, 18, 5, 17, tzinfo=UTC)
    out = format_for_display(utc_dt, with_seconds=True)
    assert len(out) == len("2026-04-30 18:05:17")
