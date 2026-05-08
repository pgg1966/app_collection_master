"""Excepciones de dominio del subsistema de pairing (Prompt 5).

Todas heredan de `ExchangeError` (que a su vez hereda de
`ServiceError`). El caller (vistas Qt en 5b, otros services) puede:

- Atrapar `ServiceError` para manejo genérico.
- Atrapar `ExchangeError` para errores de pairing en general.
- Atrapar la subclase específica para mensajes/UX dirigidos.

Mensajes orientados al usuario final (no al desarrollador).
"""

from __future__ import annotations

from collections_app.services.exceptions import ServiceError


class ExchangeError(ServiceError):
    """Base de todos los errores del subsistema de pairing."""


class InvalidExchangeFile(ExchangeError):  # noqa: N818 — nombre del prompt
    """Archivo `.colexchange` con estructura inválida o firma rota.

    Disparada cuando:
    - El JSON no parsea.
    - Falta algún campo obligatorio (`format`, `format_version`,
      `signature`, etc.).
    - `format` no es `"collections_app_exchange"`.
    - `format_version` está ausente o es < 1.
    - La firma HMAC no coincide con el contenido.
    """


class CollectionNotFound(ExchangeError):  # noqa: N818 — nombre del prompt
    """La colección referenciada en el archivo no existe localmente.

    Disparada al importar un `.colexchange` cuya `collection.name`
    no matchea ninguna colección instalada en la DB del usuario que
    importa.
    """


class UnsupportedFormatVersion(ExchangeError):  # noqa: N818 — nombre del prompt
    """El archivo usa una versión de formato que esta app no soporta.

    Típicamente: archivo generado por una versión más nueva de la app
    (`format_version > 1`). El usuario debería actualizar la app.
    """


class InsufficientInventory(ExchangeError):  # noqa: N818 — nombre del prompt
    """Algún `give` de la propuesta excede el stock disponible.

    Disparada en `ExchangeApplyService.apply_proposal` durante la
    pre-validación. El apply NO empieza la transacción si esta falla
    — el estado de la DB queda intacto.
    """
