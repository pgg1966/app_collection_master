"""Exporta un `.colexchange` con la info de pairing del usuario (Prompt 5).

Genera un archivo JSON firmado con HMAC-SHA256 que contiene los
faltantes y duplicados de una colección. El archivo se guarda en la
carpeta Descargas del usuario con nombre canónico
`{collection_slug}_{label_slug}_{YYYY-MM-DD}.colexchange`.

Decisiones (sec del prompt 5a):
- El destino NO se pasa por parámetro: se resuelve internamente vía
  `get_downloads_dir()`. La UI futura (5b) sabe dónde quedó por el
  `Path` retornado.
- Filename sanitiza solo los caracteres reservados de Windows
  (`<>:"/\\|?*`) y espacios → `_`. Acentos y otros chars unicode se
  preservan (Windows los acepta).
- Si `user_label` es `None` o vacío post-strip, se omite del nombre
  (no queda `__` doble).

Refactor 5b: la composición del `InventorySnapshot` se delegó a
`InventorySnapshotService` para que la UI de matching post-import
pueda reutilizarla sin escribir un archivo intermedio.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from collections_app import __version__ as _app_version
from collections_app.core.security.exchange_signing import compute_signature
from collections_app.core.utils.paths import get_downloads_dir
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exchange_errors import CollectionNotFound
from collections_app.services.inventory_snapshot_service import (
    InventorySnapshotService,
)

# Caracteres reservados en Windows + espacio. Se reemplazan por `_`.
_FILENAME_FORBIDDEN = '<>:"/\\|?* '
_FORMAT = "collections_app_exchange"
_FORMAT_VERSION = 1


def _sanitize_for_filename(value: str) -> str:
    """Reemplaza chars reservados de Windows + espacios por `_`.

    Acentos y otros unicode quedan como están (Windows los acepta).
    Strip final colapsa runs de `_`.
    """
    out_chars: list[str] = []
    for ch in value:
        out_chars.append("_" if ch in _FILENAME_FORBIDDEN else ch)
    raw = "".join(out_chars)
    # Colapsar runs de `_` y trim de bordes.
    while "__" in raw:
        raw = raw.replace("__", "_")
    return raw.strip("_")


def _build_filename(collection_name: str, user_label: str | None) -> str:
    """Construye `{coll}_{label}_{YYYY-MM-DD}.colexchange`.

    Si `user_label` es None o vacío post-strip, omite ese segmento.
    """
    coll_slug = _sanitize_for_filename(collection_name) or "coleccion"
    date_slug = datetime.now().strftime("%Y-%m-%d")
    parts = [coll_slug]
    if user_label is not None:
        cleaned_label = _sanitize_for_filename(user_label.strip())
        if cleaned_label:
            parts.append(cleaned_label)
    parts.append(date_slug)
    return "_".join(parts) + ".colexchange"


class ExchangeExportService:
    """Genera archivos `.colexchange` para compartir."""

    def __init__(self: ExchangeExportService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._collections = CollectionsService(conn)
        self._snapshots = InventorySnapshotService(conn)

    def export_to_file(
        self: ExchangeExportService,
        *,
        collection_id: int,
        user_label: str | None,
    ) -> Path:
        """Exporta el snapshot de pairing de `collection_id` a un archivo.

        Returns:
            `Path` del archivo creado, en la carpeta Descargas del
            usuario (o tempfile.gettempdir() si Descargas no existe).

        Raises:
            CollectionNotFound: si `collection_id` no existe.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            raise CollectionNotFound(f"La colección con id {collection_id} no existe en esta DB.")

        snapshot = self._snapshots.build_local_snapshot(
            collection_id=collection_id, user_label=user_label
        )

        # Payload (sin signature todavía).
        payload: dict = {
            "format": _FORMAT,
            "format_version": _FORMAT_VERSION,
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "exported_by_app_version": _app_version,
            "collection": {
                "name": snapshot.collection_name,
                "card_count": collection.card_count,
            },
            "user_label": snapshot.user_label,
            "missing": [
                {
                    "code_id": m.code_id,
                    "card_number": m.card_number,
                    "card_name": m.card_name,
                    "needed_quantity": m.needed_quantity,
                }
                for m in snapshot.missing
            ],
            "duplicates": [
                {
                    "code_id": d.code_id,
                    "card_number": d.card_number,
                    "card_name": d.card_name,
                    "available_quantity": d.available_quantity,
                }
                for d in snapshot.duplicates
            ],
        }
        payload["signature"] = compute_signature(payload)

        dest_dir = get_downloads_dir()
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = _build_filename(snapshot.collection_name, user_label)
        dest_path = dest_dir / filename
        dest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return dest_path
