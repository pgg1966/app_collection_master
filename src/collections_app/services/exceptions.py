"""Excepciones de dominio para la capa `services`.

Patrón obligatorio (CLAUDE.md sec 4: "excepciones de dominio por service"):

- `ServiceError` es la base común a toda la capa. Todo error de
  reglas de negocio que un service detecta debe heredar de esta clase.
- Cada service define **una** excepción específica que hereda de
  `ServiceError`. Naming: `<Dominio>Error`.
- Si un service necesita una segunda excepción más específica (ej.
  `AmbiguousCardError` dentro de inventario), esa subclase hereda de
  la `XError` del service, no de `ServiceError` directamente, para
  que el caller pueda hacer `except InventoryError` y atrapar todas
  las variantes de inventario.

Razón: el caller (vistas Qt, otros services) puede atrapar
`ServiceError` para un manejo genérico ("error de negocio") o atrapar
la específica para mensajes/UX dirigidos. Nada de `Exception` o
`RuntimeError` genéricos en la lógica — sec 4 lo prohíbe.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections_app.core.models.card import Card


class ServiceError(Exception):
    """Base común para todos los errores de la capa `services`."""


class InventoryError(ServiceError):
    """Violación de una regla de negocio del inventario.

    Ejemplos:
    - Una baja dejaría la `quantity` en negativo (vía `adjust_quantity`).
    - `add_card` con qty <= 0, o sobre una card inexistente.
    - `remove_card` sin inventario o con stock insuficiente.
    """


class AmbiguousCardError(InventoryError):
    """Un número de card resolvió a más de una card en la colección.

    Disparada por `InventoryService.add_card_by_number` /
    `remove_card_by_number` cuando `Collection.requires_code=False` y el
    número ingresado coexiste en >1 `code_id`. El caller (UI) debe
    pedirle al usuario que especifique el código y reintentar con la
    versión `_by_code`.

    Hereda de `InventoryError` para que un `except InventoryError`
    genérico también la atrape.
    """

    def __init__(self: AmbiguousCardError, matches: list[Card]) -> None:
        self.matches = matches
        super().__init__(f"{len(matches)} cards comparten el mismo número; especificar code_id")


class CollectionsError(ServiceError):
    """Violación de regla de negocio de `CollectionsService`."""


class CardsError(ServiceError):
    """Violación de regla de negocio de `CardsService`."""


class CodeHeadersError(ServiceError):
    """Violación de regla de negocio de `CodeHeadersService`."""


class CodeLinesError(ServiceError):
    """Violación de regla de negocio de `CodeLinesService`."""


class TransactionsError(ServiceError):
    """Violación de regla de negocio de `TransactionsService`."""


class SettingsError(ServiceError):
    """Violación de regla de negocio de `SettingsService`."""
