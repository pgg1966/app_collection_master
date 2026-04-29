"""Repository para la tabla collections."""

import sqlite3

from collections_app.core.models import Collection
from collections_app.core.repositories.base import BaseRepository


def _row_to_collection(row: sqlite3.Row) -> Collection:
    return Collection(
        collection_id=row["collection_id"],
        collection_name=row["collection_name"],
        card_count=row["card_count"],
        requires_code=bool(row["requires_code"]),
        code_field_name=row["code_field_name"],
        code_header_id=row["code_header_id"],
        is_premium=bool(row["is_premium"]),
        license_key_required=row["license_key_required"],
    )


_SELECT_COLS = (
    "collection_id, collection_name, card_count, requires_code, "
    "code_field_name, code_header_id, is_premium, license_key_required"
)


class CollectionsRepository(BaseRepository):
    """CRUD sobre `collections`."""

    def list_all(self) -> list[Collection]:
        """Retorna todas las colecciones ordenadas por nombre."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections ORDER BY collection_name"  # noqa: S608
        ).fetchall()
        return [_row_to_collection(r) for r in rows]

    def get_by_id(self, collection_id: int) -> Collection | None:
        """Retorna la colección por id, o None si no existe."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections WHERE collection_id = ?",  # noqa: S608
            (collection_id,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def get_by_name(self, name: str) -> Collection | None:
        """Retorna la colección por nombre exacto, o None si no existe."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections WHERE collection_name = ?",  # noqa: S608
            (name,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def create(self, collection: Collection) -> Collection:
        """Inserta y retorna la colección con `collection_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, requires_code, code_field_name, "
            " code_header_id, is_premium, license_key_required) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                collection.collection_name,
                collection.card_count,
                int(collection.requires_code),
                collection.code_field_name,
                collection.code_header_id,
                int(collection.is_premium),
                collection.license_key_required,
            ),
        )
        return Collection(
            collection_id=cursor.lastrowid,
            collection_name=collection.collection_name,
            card_count=collection.card_count,
            requires_code=collection.requires_code,
            code_field_name=collection.code_field_name,
            code_header_id=collection.code_header_id,
            is_premium=collection.is_premium,
            license_key_required=collection.license_key_required,
        )

    def update(self, collection: Collection) -> Collection:
        """Actualiza una colección existente. Requiere `collection_id` no None."""
        if collection.collection_id is None:
            raise ValueError("update requiere collection_id no None")
        self.conn.execute(
            "UPDATE collections SET "
            "collection_name = ?, card_count = ?, requires_code = ?, "
            "code_field_name = ?, code_header_id = ?, is_premium = ?, "
            "license_key_required = ? "
            "WHERE collection_id = ?",
            (
                collection.collection_name,
                collection.card_count,
                int(collection.requires_code),
                collection.code_field_name,
                collection.code_header_id,
                int(collection.is_premium),
                collection.license_key_required,
                collection.collection_id,
            ),
        )
        return collection

    def delete(self, collection_id: int) -> bool:
        """Borra la colección. Cascade borra cards e inventory."""
        cursor = self.conn.execute(
            "DELETE FROM collections WHERE collection_id = ?",
            (collection_id,),
        )
        return cursor.rowcount > 0
