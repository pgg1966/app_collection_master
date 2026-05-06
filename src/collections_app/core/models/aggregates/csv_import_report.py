"""Aggregates de reporte para imports de CSV.

Resultado tipado que devuelven los métodos de `CsvImportService`.
Sigue la convención de los demás aggregates (`CodeStats`):
`@dataclass(slots=True)`, sin lógica de I/O, sin SQL.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CsvImportError:
    """Una fila inválida detectada durante el import.

    Attributes:
        row_index: número de fila 1-based, excluyendo el header del CSV.
        message: descripción del problema (ej. "code_id 'XYZ' no existe
            en el header").
    """

    row_index: int
    message: str


@dataclass(slots=True)
class CsvImportReport:
    """Resumen de un import de CSV.

    Las filas inválidas se acumulan en `errors` sin abortar el import;
    las válidas se cuentan en `rows_inserted`. Si el CSV es ilegible o
    el target (Collection / CodeHeader) no existe, el service lanza una
    excepción de dominio antes de construir el reporte.

    Attributes:
        rows_total: filas leídas del CSV (excluyendo header).
        rows_inserted: cantidad de filas válidas que llegaron a la DB.
        rows_skipped: filas inválidas (= len(errors)).
        errors: lista de errores con `(row_index, message)`.
    """

    rows_total: int
    rows_inserted: int
    rows_skipped: int
    errors: list[CsvImportError] = field(default_factory=list)
