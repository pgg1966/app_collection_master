"""Modelos agregados — resultados de queries que combinan tablas.

A diferencia de los modelos de tabla en `core.models.*`, estos NO se
persisten directamente y NO tienen un repositorio dedicado: son
contenedores tipados para resultados de queries de stats / agregaciones.

Aún así viven dentro de la capa `models` (la regla de imports los trata
igual que cualquier otro dataclass) y son `@dataclass(slots=True)` para
que el contrato de retorno de los repos cumpla CLAUDE.md sec 2.3.
"""
