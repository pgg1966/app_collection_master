"""Limpia registros huérfanos de colecciones borradas.

Si en algún momento se ejecutó `DELETE FROM collections` sin tener el
PRAGMA `foreign_keys=ON` activado (típicamente desde el shell sqlite3
o un script externo), las cards/inventory/transactions de esa
colección quedaron huérfanas. Este script las elimina.

Las conexiones que abre `create_connection()` en este proyecto siempre
prenden el pragma, así que el problema no se reproduce desde la app.

Uso:
    python -m collections_app.core.db.scripts.cleanup_orphans
"""

import logging

from collections_app.core.db.connection import create_connection, transaction
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path

logger = logging.getLogger(__name__)


def cleanup_orphans(db_path: str | None = None) -> dict[str, int]:
    """Elimina cards/inventory/transactions huérfanas.

    Args:
        db_path: path a la DB. Si None, usa la default del usuario.

    Returns:
        Dict con la cuenta de filas eliminadas por tabla.
    """
    path = db_path or str(get_database_path())
    conn = create_connection(path)
    deleted: dict[str, int] = {}
    try:
        with transaction(conn):
            for table, fk_cols in (
                # `cards` cuelga directo de `collections`
                ("cards", "collection_id"),
                # `inventory` cuelga de `cards`; basta con orphans en collection_id
                ("inventory", "collection_id"),
                # `transactions` no tiene CASCADE — se acumulan huérfanos
                ("transactions", "collection_id"),
                # `card_images` (migración 003) cascadea desde cards, pero
                # si el bug ocurrió antes de migrar, podría tener huérfanos
                ("card_images", "collection_id"),
            ):
                cur = conn.execute(
                    f"DELETE FROM {table} "  # noqa: S608 — table whitelist arriba
                    f"WHERE {fk_cols} NOT IN (SELECT collection_id FROM collections)"
                )
                deleted[table] = cur.rowcount
                logger.info("%s: %d filas huérfanas eliminadas", table, cur.rowcount)
    finally:
        conn.close()
    return deleted


def main() -> int:
    setup_logging(level=logging.INFO)
    deleted = cleanup_orphans()
    print("=== Limpieza de huérfanos ===")
    for table, n in deleted.items():
        print(f"  {table}: {n} filas")
    print("Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
