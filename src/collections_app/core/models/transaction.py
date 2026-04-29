"""Modelo Transaction: bitácora de altas/bajas de inventario."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OperationType(StrEnum):
    """Tipo de operación registrada en la bitácora."""

    ALTA = "alta"
    BAJA = "baja"


@dataclass(frozen=True)
class Transaction:
    """Registro inmutable de un movimiento sobre el inventario.

    Attributes:
        transaction_id: PK auto-incremental. None si aún no fue persistido.
        collection_id: FK a la Collection afectada.
        code_id: parte de la PK compuesta de Card.
        card_number: parte de la PK compuesta de Card.
        operation: alta o baja (ver OperationType).
        quantity: unidades movidas (siempre positivo; el signo lo da `operation`).
        transaction_date: timestamp del movimiento.
    """

    transaction_id: int | None
    collection_id: int
    code_id: str
    card_number: int
    operation: OperationType
    quantity: int
    transaction_date: datetime
