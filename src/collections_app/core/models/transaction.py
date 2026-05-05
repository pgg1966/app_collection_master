"""Modelo Transaction: bitácora de altas/bajas de inventario."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OperationType(StrEnum):
    """Tipo de operación registrada en la bitácora."""

    ALTA = "alta"
    BAJA = "baja"


@dataclass(slots=True)
class Transaction:
    """Registro inmutable de un movimiento sobre el inventario.

    FK granular a `card_id` (sec 2.5: bitácoras apuntan a la entidad
    atómica afectada, no a su contenedor). `exchange_event_id` agrupa
    transacciones que pertenecen a un mismo intercambio (mismo valor
    en todas las altas y bajas del evento); NULL para movimientos
    aislados que no son parte de un intercambio.

    Attributes:
        transaction_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card afectada.
        operation: alta o baja (ver OperationType).
        quantity: unidades movidas (siempre positivo, CHECK > 0).
        transaction_date: timestamp del movimiento.
        exchange_event_id: agrupador de transacciones de un intercambio,
            o None.
    """

    transaction_id: int | None
    card_id: int
    operation: OperationType
    quantity: int
    transaction_date: datetime
    exchange_event_id: int | None = None
