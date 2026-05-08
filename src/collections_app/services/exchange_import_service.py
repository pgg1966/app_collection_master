"""Lee y valida archivos `.colexchange` (Prompt 5).

Devuelve un `(InventorySnapshot, list[str])`:
- Snapshot agnóstico (input para el `MatchingService`).
- Lista de warnings: cards del archivo que no existen en la DB local.
  No detiene el import (el archivo puede ser válido aunque algunas
  cards no estén en el catálogo del importador, ej. álbum distinto
  o errores tipográficos del exporter). La UI futura (5b) muestra
  los warnings al usuario.

Validaciones aplicadas (en orden):
1. JSON parsea.
2. Campos obligatorios presentes.
3. `format == "collections_app_exchange"`.
4. `format_version` soportado por esta app (== 1 en v0.2).
5. Firma HMAC verifica con `hmac.compare_digest`.
6. La colección existe localmente (`collection.name`).
7. (Por fila) la card existe en la DB local — si no, va a warnings.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from collections_app.core.models.aggregates.inventory_snapshot import (
    DuplicateCard,
    InventorySnapshot,
    MissingCard,
)
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.security.exchange_signing import verify_signature
from collections_app.services.collections_service import CollectionsService
from collections_app.services.exchange_errors import (
    CollectionNotFound,
    InvalidExchangeFile,
    UnsupportedFormatVersion,
)

_FORMAT = "collections_app_exchange"
_SUPPORTED_VERSION = 1
_WARNING_CAP = 50


@dataclass(slots=True, frozen=True)
class ImportResult:
    """Resultado del import: snapshot + warnings + collection local matcheada.

    `local_collection_id` es el `Collection.collection_id` de la DB
    del importador — necesario para que el `ApplyService` resuelva
    los `card_id` de cada card de la propuesta.
    """

    snapshot: InventorySnapshot
    warnings: tuple[str, ...]
    local_collection_id: int


class ExchangeImportService:
    """Lee, valida y parsea archivos `.colexchange`."""

    def __init__(self: ExchangeImportService, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._collections = CollectionsService(conn)
        self._cards = CardsRepository(conn)

    def read_from_file(self: ExchangeImportService, path: Path) -> ImportResult:
        """Lee `path`, valida y devuelve un `ImportResult`.

        Raises:
            InvalidExchangeFile: JSON malformado, firma inválida,
                campos faltantes, formato incorrecto.
            UnsupportedFormatVersion: archivo de versión > 1.
            CollectionNotFound: la `collection.name` del archivo no
                existe en la DB local.
        """
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise InvalidExchangeFile(f"No se pudo leer el archivo: {exc}") from exc

        try:
            payload: dict[str, Any] = json.loads(text)
        except json.JSONDecodeError as exc:
            raise InvalidExchangeFile("Archivo inválido: JSON malformado.") from exc

        if not isinstance(payload, dict):
            raise InvalidExchangeFile("Archivo inválido: estructura inesperada.")

        self._validate_format(payload)
        self._verify_signature(payload)
        local_collection = self._resolve_local_collection(payload)
        snapshot, warnings = self._build_snapshot(payload, local_collection)
        assert local_collection.collection_id is not None
        return ImportResult(
            snapshot=snapshot,
            warnings=warnings,
            local_collection_id=local_collection.collection_id,
        )

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def _validate_format(self: ExchangeImportService, payload: dict[str, Any]) -> None:
        fmt = payload.get("format")
        if fmt != _FORMAT:
            raise InvalidExchangeFile("Archivo inválido o no generado por esta aplicación.")
        version = payload.get("format_version")
        if not isinstance(version, int) or version < 1:
            raise InvalidExchangeFile(
                "Archivo inválido: campo `format_version` ausente o incorrecto."
            )
        if version > _SUPPORTED_VERSION:
            raise UnsupportedFormatVersion(
                f"Archivo de versión {version} — esta app soporta hasta "
                f"versión {_SUPPORTED_VERSION}. Actualizá la app para abrirlo."
            )

    def _verify_signature(self: ExchangeImportService, payload: dict[str, Any]) -> None:
        signature = payload.get("signature")
        if not isinstance(signature, str) or not signature:
            raise InvalidExchangeFile("Archivo inválido: falta la firma.")
        # Copia sin signature para verificar.
        payload_for_sig = {k: v for k, v in payload.items() if k != "signature"}
        if not verify_signature(payload_for_sig, signature):
            raise InvalidExchangeFile("Archivo inválido o no generado por esta aplicación.")

    def _resolve_local_collection(
        self: ExchangeImportService, payload: dict[str, Any]
    ) -> Collection:
        collection_block = payload.get("collection")
        if not isinstance(collection_block, dict):
            raise InvalidExchangeFile("Archivo inválido: falta el bloque `collection`.")
        name = collection_block.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InvalidExchangeFile("Archivo inválido: la colección no tiene nombre.")
        local = self._collections.get_by_name(name)
        if local is None:
            raise CollectionNotFound(f"La colección «{name}» no está instalada en esta app.")
        return local

    # ------------------------------------------------------------------
    # Construcción del snapshot
    # ------------------------------------------------------------------

    def _build_snapshot(
        self: ExchangeImportService,
        payload: dict[str, Any],
        local_collection: Collection,
    ) -> tuple[InventorySnapshot, tuple[str, ...]]:
        assert local_collection.collection_id is not None
        # Set de cards locales para validar existencia.
        local_keys: set[tuple[str, int]] = {
            (c.code_id, c.card_number)
            for c in self._cards.list_by_collection(local_collection.collection_id)
        }

        warnings: list[str] = []
        missing_list: list[MissingCard] = []
        duplicates_list: list[DuplicateCard] = []

        for raw in payload.get("missing", []):
            entry = self._parse_missing_entry(raw)
            if entry is None:
                continue
            if (entry.code_id, entry.card_number) not in local_keys:
                if len(warnings) < _WARNING_CAP:
                    warnings.append(
                        f"Faltante {entry.code_id}-{entry.card_number} "
                        f"({entry.card_name}): no existe en tu colección."
                    )
                continue
            missing_list.append(entry)

        for raw in payload.get("duplicates", []):
            entry = self._parse_duplicate_entry(raw)
            if entry is None:
                continue
            if (entry.code_id, entry.card_number) not in local_keys:
                if len(warnings) < _WARNING_CAP:
                    warnings.append(
                        f"Duplicado {entry.code_id}-{entry.card_number} "
                        f"({entry.card_name}): no existe en tu colección."
                    )
                continue
            duplicates_list.append(entry)

        collection_block = payload.get("collection", {})
        snapshot = InventorySnapshot(
            user_label=payload.get("user_label"),
            collection_name=collection_block.get("name", ""),
            collection_card_count=int(collection_block.get("card_count", 0)),
            missing=tuple(missing_list),
            duplicates=tuple(duplicates_list),
        )
        return snapshot, tuple(warnings)

    def _parse_missing_entry(self: ExchangeImportService, raw: object) -> MissingCard | None:
        if not isinstance(raw, dict):
            return None
        try:
            return MissingCard(
                code_id=str(raw["code_id"]),
                card_number=int(raw["card_number"]),
                card_name=str(raw["card_name"]),
                needed_quantity=int(raw.get("needed_quantity", 1)),
            )
        except (KeyError, TypeError, ValueError):
            return None

    def _parse_duplicate_entry(self: ExchangeImportService, raw: object) -> DuplicateCard | None:
        if not isinstance(raw, dict):
            return None
        try:
            return DuplicateCard(
                code_id=str(raw["code_id"]),
                card_number=int(raw["card_number"]),
                card_name=str(raw["card_name"]),
                available_quantity=int(raw.get("available_quantity", 0)),
            )
        except (KeyError, TypeError, ValueError):
            return None
