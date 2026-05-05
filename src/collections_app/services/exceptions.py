"""Excepciones de dominio para la capa `services`.

Patrón obligatorio (CLAUDE.md sec 4: "excepciones de dominio por service"):

- `ServiceError` es la base común a toda la capa. Todo error de
  reglas de negocio que un service detecta debe heredar de esta clase.
- Cada service define **una** excepción específica que hereda de
  `ServiceError`. Naming: `<Dominio>Error`.

Ejemplos esperados a futuro:

    class InventoryError(ServiceError): ...      # implementado
    class CollectionsError(ServiceError): ...    # Prompt 2
    class CardsError(ServiceError): ...          # Prompt 2
    class LicenseError(ServiceError): ...        # Prompt 2 / 3

Razón: el caller (vistas Qt, otros services) puede atrapar
`ServiceError` para un manejo genérico ("error de negocio") o atrapar
la específica para mensajes/UX dirigidos. Nada de `Exception` o
`RuntimeError` genéricos en la lógica — sec 4 lo prohíbe.
"""

from __future__ import annotations


class ServiceError(Exception):
    """Base común para todos los errores de la capa `services`."""


class InventoryError(ServiceError):
    """Violación de una regla de negocio del inventario.

    Ejemplos:
    - Una baja dejaría la `quantity` en negativo.
    """
