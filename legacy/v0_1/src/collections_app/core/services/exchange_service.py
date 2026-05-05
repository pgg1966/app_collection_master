"""Servicio de comparación e intercambio entre álbumes de dos usuarios.

Flujo end-to-end:

1. Usuario A: `generate_exchange_file()` → escribe `MiAlbum.colexchange`
   con sus faltantes y repetidas. Lo comparte con el usuario B.
2. Usuario B: `load_exchange_file()` → lee + valida el JSON + checksum.
3. `compare(my_file, other_file)` → `ComparisonResult` con cartas
   intercambiables.
4. `lock_cards()` antes de ejecutar (mientras el dialog está abierto).
5. `execute_exchange()` → bajas + altas + unlock dentro de una
   transacción. Rollback si algo falla.
6. Si el usuario cancela: `unlock_all_cards()`.

El checksum del archivo es deliberadamente truncado a 16 chars
(SHA256). No es criptográficamente fuerte — el objetivo es detectar
ediciones casuales, no impedir manipulación maliciosa.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from collections_app.core.db.connection import transaction
from collections_app.core.models import (
    ComparisonResult,
    ExchangeCard,
    ExchangeFile,
    ExchangeSession,
)
from collections_app.core.repositories import (
    CardsRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.services.inventory_service import InventoryService
from collections_app.core.utils.datetime_helpers import utc_now

EXCHANGE_APP_ID = "CollectionsApp"
EXCHANGE_FORMAT_VERSION = "1.0"
EXCHANGE_EXTENSION = ".colexchange"
_CHECKSUM_LEN = 16


class ExchangeService:
    """Genera/lee archivos `.colexchange` y orquesta el intercambio."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Generación de archivo
    # ------------------------------------------------------------------

    def generate_exchange_file(
        self,
        collection_id: int,
        output_path: Path,
    ) -> ExchangeFile:
        """Genera el archivo `.colexchange` con faltantes y repetidas.

        Las repetidas se calculan sobre `available_quantity` (descuenta
        las cartas bloqueadas por un intercambio en curso) — no tendría
        sentido ofrecer al otro usuario una carta que ya prometiste.
        """
        col = CollectionsRepository(self._conn).get_by_id(collection_id)
        if col is None:
            raise ValueError(f"Colección {collection_id} no encontrada")

        cards = {
            (c.code_id, c.card_number): c
            for c in CardsRepository(self._conn).list_by_collection(collection_id)
        }
        inventory = InventoryRepository(self._conn).list_by_collection(collection_id)
        owned = {(i.code_id, i.card_number): i for i in inventory if i.quantity > 0}

        missing: list[ExchangeCard] = []
        duplicates: list[ExchangeCard] = []

        for (code_id, number), card in sorted(cards.items()):
            inv = owned.get((code_id, number))
            if inv is None or inv.available_quantity == 0:
                missing.append(
                    ExchangeCard(
                        code_id=code_id,
                        card_number=number,
                        card_name=card.card_name,
                        quantity=0,
                    )
                )
            elif inv.available_quantity > 1:
                # Lo que el usuario realmente puede ofrecer = disponible - 1
                # (siempre conservamos UNA copia para que el álbum del
                # usuario no quede incompleto después del intercambio).
                oferable = inv.available_quantity - 1
                duplicates.append(
                    ExchangeCard(
                        code_id=code_id,
                        card_number=number,
                        card_name=card.card_name,
                        quantity=oferable,
                    )
                )

        ef = ExchangeFile(
            app=EXCHANGE_APP_ID,
            version=EXCHANGE_FORMAT_VERSION,
            collection_id=collection_id,
            collection_name=col.collection_name,
            generated_at=utc_now().isoformat(),
            missing=missing,
            duplicates=duplicates,
        )
        ef.checksum = self._compute_checksum(ef)
        self._write_file(ef, output_path)
        return ef

    # ------------------------------------------------------------------
    # Importación
    # ------------------------------------------------------------------

    def load_exchange_file(self, path: Path) -> ExchangeFile:
        """Carga + valida un `.colexchange`.

        Raises:
            ValueError: archivo inválido (JSON corrupto), no generado por
                CollectionsApp, o con checksum que no matchea (modificado
                manualmente).
        """
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Archivo inválido: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("Archivo inválido: estructura JSON inesperada")
        if data.get("app") != EXCHANGE_APP_ID:
            raise ValueError("El archivo no fue generado por CollectionsApp")

        stored_checksum = str(data.pop("checksum", ""))
        ef = self._dict_to_exchange_file(data)
        # Re-calculamos sin el checksum guardado y comparamos.
        computed = self._compute_checksum(ef)
        if computed != stored_checksum:
            raise ValueError("El archivo fue modificado externamente (checksum inválido)")
        ef.checksum = stored_checksum
        return ef

    # ------------------------------------------------------------------
    # Comparación
    # ------------------------------------------------------------------

    def compare(
        self,
        my_file: ExchangeFile,
        other_file: ExchangeFile,
    ) -> ComparisonResult:
        """Compara dos `ExchangeFile` y devuelve qué intercambiar."""
        if my_file.collection_id != other_file.collection_id:
            raise ValueError("Los archivos son de colecciones distintas y no se pueden comparar")

        other_duplicates = {(c.code_id, c.card_number) for c in other_file.duplicates}
        other_missing = {(c.code_id, c.card_number) for c in other_file.missing}

        i_need = [c for c in my_file.missing if (c.code_id, c.card_number) in other_duplicates]
        i_can_offer = [c for c in my_file.duplicates if (c.code_id, c.card_number) in other_missing]
        return ComparisonResult(i_need=i_need, i_can_offer=i_can_offer)

    # ------------------------------------------------------------------
    # Bloqueo
    # ------------------------------------------------------------------

    def lock_cards(
        self,
        collection_id: int,
        cards: list[ExchangeCard],
    ) -> None:
        """Bloquea las cartas en inventario (1 por carta). Commit incluido."""
        repo = InventoryRepository(self._conn)
        for card in cards:
            repo.lock(collection_id, card.code_id, card.card_number)
        self._conn.commit()

    def unlock_all_cards(self, collection_id: int) -> None:
        """Resetea locked=0 para toda la colección. Commit incluido."""
        InventoryRepository(self._conn).unlock_all(collection_id)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Ejecución del intercambio
    # ------------------------------------------------------------------

    def execute_exchange(
        self,
        collection_id: int,
        session: ExchangeSession,
    ) -> None:
        """Ejecuta el intercambio dentro de una transacción.

        Pasos:
          1. Baja de cada carta en `to_give` (1 unidad).
          2. Alta de cada carta en `to_receive` (1 unidad).
          3. unlock_all del inventario.

        Si CUALQUIER paso falla, se hace rollback y se propaga la
        excepción. NO commit parcial.
        """
        svc = InventoryService(self._conn)
        with transaction(self._conn):
            for card in session.to_give:
                svc._inventory.adjust_quantity(  # noqa: SLF001
                    collection_id, card.code_id, card.card_number, -1
                )
                self._log_transaction(svc, collection_id, card, alta=False)
            for card in session.to_receive:
                # add_card valida que la carta exista en el catálogo;
                # si la carta a recibir es nueva (no está en cards),
                # primero la creamos para que el FK no rompa.
                self._ensure_card_in_catalog(collection_id, card)
                svc._inventory.adjust_quantity(  # noqa: SLF001
                    collection_id, card.code_id, card.card_number, 1
                )
                self._log_transaction(svc, collection_id, card, alta=True)
            InventoryRepository(self._conn).unlock_all(collection_id)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _ensure_card_in_catalog(self, collection_id: int, card: ExchangeCard) -> None:
        """Asegura que la carta exista en `cards` antes de la alta.

        Caso de uso: el otro usuario me ofrece una carta que mi catálogo
        ya tiene (por convención los catálogos son simétricos), pero
        protegemos contra ediciones manuales del archivo.
        """
        from collections_app.core.models import Card

        repo = CardsRepository(self._conn)
        if repo.get(collection_id, card.code_id, card.card_number) is None:
            repo.upsert(
                Card(
                    collection_id=collection_id,
                    code_id=card.code_id,
                    card_number=card.card_number,
                    card_name=card.card_name,
                )
            )

    def _log_transaction(
        self,
        svc: InventoryService,
        collection_id: int,
        card: ExchangeCard,
        alta: bool,
    ) -> None:
        """Registra la transacción en `transactions` (sin tocar inventory)."""
        from collections_app.core.models import OperationType, Transaction

        op = OperationType.ALTA if alta else OperationType.BAJA
        svc._transactions.log(  # noqa: SLF001
            Transaction(
                transaction_id=None,
                collection_id=collection_id,
                code_id=card.code_id,
                card_number=card.card_number,
                operation=op,
                quantity=1,
                transaction_date=utc_now(),
            )
        )

    def _compute_checksum(self, ef: ExchangeFile) -> str:
        """SHA256 truncado sobre los campos estables del archivo.

        NO incluye `generated_at` (para que el checksum sea reproducible
        dado el mismo input) ni `checksum` (obvio).
        """
        payload = {
            "app": ef.app,
            "version": ef.version,
            "collection_id": ef.collection_id,
            "collection_name": ef.collection_name,
            "missing": [self._card_to_dict(c) for c in ef.missing],
            "duplicates": [self._card_to_dict(c) for c in ef.duplicates],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:_CHECKSUM_LEN]

    @staticmethod
    def _card_to_dict(c: ExchangeCard) -> dict[str, Any]:
        return {
            "code_id": c.code_id,
            "card_number": c.card_number,
            "card_name": c.card_name,
            "quantity": c.quantity,
        }

    def _write_file(self, ef: ExchangeFile, path: Path) -> None:
        data = {
            "app": ef.app,
            "version": ef.version,
            "collection_id": ef.collection_id,
            "collection_name": ef.collection_name,
            "generated_at": ef.generated_at,
            "missing": [self._card_to_dict(c) for c in ef.missing],
            "duplicates": [self._card_to_dict(c) for c in ef.duplicates],
            "checksum": ef.checksum,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _dict_to_exchange_file(self, data: dict[str, Any]) -> ExchangeFile:
        def parse_cards(lst: list[dict[str, Any]]) -> list[ExchangeCard]:
            return [
                ExchangeCard(
                    code_id=str(c["code_id"]),
                    card_number=int(c["card_number"]),
                    card_name=str(c["card_name"]),
                    quantity=int(c.get("quantity", 0)),
                )
                for c in lst
            ]

        return ExchangeFile(
            app=str(data.get("app", "")),
            version=str(data.get("version", "")),
            collection_id=int(data["collection_id"]),
            collection_name=str(data.get("collection_name", "")),
            generated_at=str(data.get("generated_at", "")),
            missing=parse_cards(data.get("missing", []) or []),
            duplicates=parse_cards(data.get("duplicates", []) or []),
        )
