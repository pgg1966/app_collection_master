"""Modelos para el sistema de comparación e intercambio de álbumes.

Estos modelos NO se persisten en la DB — son DTOs in-memory + payload del
archivo `.colexchange`. La DB solo se entera del intercambio cuando se
ejecuta (vía `InventoryService.add_card` / `remove_card`) y cuando se
bloquea (vía `InventoryRepository.lock` / `unlock_all`).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExchangeCard:
    """Una carta dentro de un archivo de intercambio.

    `quantity` es 0 cuando la carta está en `missing` (faltante del
    usuario) o ≥1 cuando está en `duplicates` (cantidad disponible
    para regalar = quantity - 1, pero acá guardamos la cantidad total
    visible en el archivo para que el otro usuario sepa el rango).
    """

    code_id: str
    card_number: int
    card_name: str
    quantity: int = 0


@dataclass
class ExchangeFile:
    """Contenido del archivo `.colexchange` generado por un usuario.

    `checksum` es un SHA256 truncado calculado sobre los campos estables
    (NO incluye `generated_at` para que el checksum sea reproducible).
    Se usa para detectar archivos manipulados manualmente.
    """

    app: str  # "CollectionsApp"
    version: str  # "1.0"
    collection_id: int
    collection_name: str
    generated_at: str  # UTC ISO
    missing: list[ExchangeCard] = field(default_factory=list)
    duplicates: list[ExchangeCard] = field(default_factory=list)
    checksum: str = ""


@dataclass
class ComparisonResult:
    """Resultado de comparar dos `ExchangeFile`.

    Calculado siempre desde la perspectiva del usuario "yo" (`my_file`):
    - `i_need`: mis faltantes que el otro tiene como repetidas.
    - `i_can_offer`: mis repetidas que al otro le faltan.
    """

    i_need: list[ExchangeCard] = field(default_factory=list)
    i_can_offer: list[ExchangeCard] = field(default_factory=list)


@dataclass
class ExchangeSession:
    """Estado in-memory de un intercambio en proceso de ejecución.

    Lo construye el ExchangeView a partir del ComparisonResult + las
    decisiones del usuario (qué chequear/desmarcar, qué cartas extra
    agregar manualmente). `locked_items` registra qué cartas fueron
    bloqueadas en inventario para poder revertirlas si se cancela.
    """

    to_give: list[ExchangeCard] = field(default_factory=list)
    to_receive: list[ExchangeCard] = field(default_factory=list)
    locked_items: list[ExchangeCard] = field(default_factory=list)
