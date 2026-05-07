"""Aggregates de reporte para imports de inventario (Prompt 4c).

Resultado tipado que devuelve `InventoryImportService.import_inventory`.
Sigue el patrón de `csv_import_report.py` pero con dos listas separadas:

- `errors`: filas inválidas (código inexistente, número/cantidad mal
  formados, card que no existe en el catálogo). No se aplican.
- `warnings`: filas con cantidad = 0. Válidas semánticamente pero no
  se aplican (decisión: si el usuario quiere "borrar" stock de una
  card, no incluya la fila — qty=0 se trata como dato accidental).

Invariante: `rows_total == rows_applied + rows_skipped`, donde
`rows_skipped == len(errors) + len(warnings)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class InventoryImportError:
    """Una fila inválida detectada durante el import.

    Attributes:
        row_index: número de fila 1-based, excluyendo el header.
            -1 indica un error que no mapea a una fila concreta
            (ej. error catastrófico de header, no usado en errors[]
            sino raised como ServiceError).
        message: descripción del problema.
    """

    row_index: int
    message: str


@dataclass(slots=True)
class InventoryImportWarning:
    """Una fila con cantidad = 0 — válida pero no aplicada.

    Attributes:
        row_index: número de fila 1-based, excluyendo el header.
        code_id: código de la card (cadena vacía si la collection
            tiene `requires_code=False`).
        card_number: número de la card.
        message: descripción del aviso (ej. "cantidad = 0; fila ignorada").
    """

    row_index: int
    code_id: str
    card_number: int
    message: str


@dataclass(slots=True)
class InventoryImportReport:
    """Resumen de un import de inventario.

    Attributes:
        rows_total: filas leídas del archivo (excluyendo header).
        rows_applied: filas con cambio efectivo aplicado a inventory.
            Incluye filas con delta=0 en modo replace (no generan
            transaction pero cuentan como procesadas exitosamente).
        rows_skipped: filas no aplicadas == len(errors) + len(warnings).
        errors: lista de errores con `(row_index, message)`.
        warnings: lista de avisos con `(row_index, code_id, card_number,
            message)`.
    """

    rows_total: int
    rows_applied: int
    rows_skipped: int
    errors: list[InventoryImportError] = field(default_factory=list)
    warnings: list[InventoryImportWarning] = field(default_factory=list)
