"""Utilidades para manejo de timestamps.

Política del proyecto:
- La DB siempre guarda UTC (SQLite `datetime('now')` retorna UTC).
- Los `datetime` que circulan en código tienen `tzinfo=UTC`.
- La conversión a hora local sucede SOLO al mostrar al usuario.
"""

from datetime import UTC, datetime

DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def utc_now() -> datetime:
    """Retorna el datetime actual en UTC con tzinfo."""
    return datetime.now(UTC)


def to_local(dt: datetime) -> datetime:
    """Convierte un datetime UTC a hora local del sistema.

    Si `dt` es naive (sin tzinfo), se asume que ya está en UTC.
    Solo debe usarse para display; nunca persistir el resultado.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone()


def parse_db_datetime(s: str) -> datetime:
    """Parsea un timestamp de SQLite (`YYYY-MM-DD HH:MM:SS`) como UTC.

    Acepta también el formato ISO con `T` y microsegundos por flexibilidad.
    """
    try:
        dt = datetime.strptime(s, DB_DATE_FORMAT)
    except ValueError:
        # Fallback: ISO format
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def format_for_db(dt: datetime) -> str:
    """Formatea un datetime para insertarlo como string en SQLite (UTC).

    Si el datetime es naive se asume UTC; si tiene tzinfo, se convierte a
    UTC antes de formatear.
    """
    if dt.tzinfo is None:
        return dt.strftime(DB_DATE_FORMAT)
    return dt.astimezone(UTC).strftime(DB_DATE_FORMAT)


def format_for_display(dt: datetime, with_seconds: bool = False) -> str:
    """Formatea un datetime para mostrar al usuario, en hora local."""
    local = to_local(dt)
    fmt = "%Y-%m-%d %H:%M:%S" if with_seconds else "%Y-%m-%d %H:%M"
    return local.strftime(fmt)
