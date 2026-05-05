"""Servicio para descubrir perfiles e importar la estructura entre ellos.

Un perfil tiene su propio `collections.db`. `get_all_profiles()` escanea
la carpeta base buscando esos archivos. `import_structure()` copia las
tablas de catálogo (colecciones, codes, cards) desde un perfil fuente
hacia el target — NO copia inventory ni transactions, así el usuario
empieza con stock cero pero sin tener que recrear el catálogo.

Usado por `ProfileSetupDialog` cuando el cliente arranca con un perfil
sin colecciones.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from collections_app.core.utils.paths import get_base_app_dir

logger = logging.getLogger(__name__)

# Tablas a copiar (en orden que respeta FKs de `001_initial.sql`):
# headers → lines, collections → cards.
_STRUCTURE_TABLES = (
    "codes_headers",
    "codes_lines",
    "collections",
    "cards",
)


@dataclass(frozen=True)
class ProfileInfo:
    """Snapshot de un perfil detectado en el filesystem.

    `display_name` es lo que se muestra en la UI (ej. "Principal" para
    "default"). `collection_count` y `has_inventory` se leen de la DB
    para que el usuario sepa de qué perfil está importando.
    """

    name: str
    db_path: Path
    display_name: str
    collection_count: int
    has_inventory: bool


class ProfileService:
    """Operaciones sobre perfiles. Sin estado — todos los métodos son estáticos."""

    @staticmethod
    def get_all_profiles() -> list[ProfileInfo]:
        """Detecta todos los perfiles con `collections.db` en disco.

        Incluye el perfil "default" (raíz `Collections/`) y cualquier
        subdirectorio que contenga un `collections.db`. Subdirectorios
        sin DB se ignoran (carpetas dejadas a medias o de otras apps).
        """
        base = get_base_app_dir()
        profiles: list[ProfileInfo] = []

        # Perfil default (raíz)
        default_db = base / "collections.db"
        if default_db.exists():
            profiles.append(ProfileService._read_profile_info("default", default_db, "Principal"))

        # Perfiles en subdirectorios
        if base.exists():
            for subdir in sorted(base.iterdir()):
                if not subdir.is_dir():
                    continue
                db = subdir / "collections.db"
                if not db.exists():
                    continue
                profiles.append(
                    ProfileService._read_profile_info(subdir.name, db, subdir.name.capitalize())
                )

        return profiles

    @staticmethod
    def _read_profile_info(name: str, db_path: Path, display_name: str) -> ProfileInfo:
        """Lee count de colecciones y existencia de inventario via read-only.

        Modo `?mode=ro` evita crear archivos `-wal`/`-shm` en la
        carpeta del otro perfil al solo leerlo.
        """
        collection_count = 0
        has_inventory = False
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            try:
                row = conn.execute("SELECT COUNT(*) FROM collections").fetchone()
                collection_count = int(row[0]) if row else 0
                try:
                    row = conn.execute(
                        "SELECT COUNT(*) FROM inventory WHERE quantity > 0"
                    ).fetchone()
                    has_inventory = bool(row and row[0] > 0)
                except sqlite3.OperationalError:
                    # DB vieja sin tabla inventory todavía.
                    has_inventory = False
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001 — diagnóstico, no rompe al usuario
            logger.debug("No se pudo leer perfil %s en %s: %s", name, db_path, exc)
        return ProfileInfo(
            name=name,
            db_path=db_path,
            display_name=display_name,
            collection_count=collection_count,
            has_inventory=has_inventory,
        )

    @staticmethod
    def import_structure(
        source_db_path: Path,
        target_conn: sqlite3.Connection,
    ) -> int:
        """Copia codes_headers/lines + collections + cards de fuente a target.

        - Idempotente: usa `INSERT OR IGNORE`, las filas existentes no se duplican.
        - NO toca `inventory` ni `transactions` — el usuario nuevo empieza
          con stock cero.
        - Asume que `target_conn` ya tiene el schema aplicado (las
          migraciones corrieron al inicializar la conexión).
        - Source se abre read-only con URI mode para no crear `-wal`/`-shm`.

        Retorna la cantidad TOTAL de colecciones en target después de la
        importación (útil para mostrar "N colecciones disponibles").
        """
        src = sqlite3.connect(f"file:{source_db_path}?mode=ro", uri=True)
        try:
            for table in _STRUCTURE_TABLES:
                # PRAGMA table_info sería más robusto que SELECT LIMIT 0
                # pero ambos funcionan; usamos description del cursor.
                cursor = src.execute(f"SELECT * FROM {table}")  # noqa: S608
                rows = cursor.fetchall()
                if not rows:
                    continue
                cols = [d[0] for d in cursor.description]
                placeholders = ", ".join("?" * len(cols))
                cols_str = ", ".join(cols)
                target_conn.executemany(
                    f"INSERT OR IGNORE INTO {table} ({cols_str}) "  # noqa: S608
                    f"VALUES ({placeholders})",
                    rows,
                )
            target_conn.commit()

            row = target_conn.execute("SELECT COUNT(*) FROM collections").fetchone()
            return int(row[0]) if row else 0
        finally:
            src.close()
