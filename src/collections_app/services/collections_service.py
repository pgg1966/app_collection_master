"""Service de colecciones.

Wrapper sobre `CollectionsRepository` con validaciones de negocio:
nombre no vacío y único, card_count no negativo, album_columns y
album_rows positivos, album_orientation en el set válido, FK válida
contra `codes_headers`.
"""

from __future__ import annotations

import sqlite3

from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import CollectionsError

VALID_ORIENTATIONS = frozenset({"portrait", "landscape"})


class CollectionsService:
    """Lógica de negocio sobre `collections`."""

    def __init__(self: CollectionsService, conn: sqlite3.Connection) -> None:
        self._repo = CollectionsRepository(conn)
        self._headers = CodeHeadersRepository(conn)

    def list_all(self: CollectionsService) -> list[Collection]:
        return self._repo.list_all()

    def get_by_id(self: CollectionsService, collection_id: int) -> Collection | None:
        return self._repo.get_by_id(collection_id)

    def get_by_name(self: CollectionsService, name: str) -> Collection | None:
        return self._repo.get_by_name(name)

    def create(self: CollectionsService, collection: Collection) -> Collection:
        """Crea una colección. Valida campos antes de delegar al repo."""
        self._validate(collection)
        try:
            return self._repo.create(collection)
        except sqlite3.IntegrityError as exc:
            raise CollectionsError(
                f"collection_name ya existe: {collection.collection_name!r}"
            ) from exc

    def update(self: CollectionsService, collection: Collection) -> Collection:
        """Actualiza una colección existente. Requiere id."""
        if collection.collection_id is None:
            raise CollectionsError("update requiere collection_id no None")
        self._validate(collection)
        try:
            return self._repo.update(collection)
        except sqlite3.IntegrityError as exc:
            raise CollectionsError(
                f"collection_name ya existe: {collection.collection_name!r}"
            ) from exc

    def delete(self: CollectionsService, collection_id: int) -> bool:
        """Borra la colección. Cascade borra cards e inventory."""
        return self._repo.delete(collection_id)

    # ------------------------------------------------------------------
    # Validaciones internas
    # ------------------------------------------------------------------

    def _validate(self: CollectionsService, collection: Collection) -> None:
        if not collection.collection_name.strip():
            raise CollectionsError("collection_name no puede ser vacio")
        if collection.card_count < 0:
            raise CollectionsError(f"card_count debe ser >= 0, recibido {collection.card_count}")
        if collection.album_columns <= 0 or collection.album_rows <= 0:
            raise CollectionsError(
                f"album_columns y album_rows deben ser > 0 "
                f"(recibido {collection.album_columns}x{collection.album_rows})"
            )
        if collection.album_orientation not in VALID_ORIENTATIONS:
            raise CollectionsError(
                f"album_orientation invalido: {collection.album_orientation!r} "
                f"(esperado uno de {sorted(VALID_ORIENTATIONS)})"
            )
        if self._headers.get_by_id(collection.code_header_id) is None:
            raise CollectionsError(f"code_header_id={collection.code_header_id} no existe")
