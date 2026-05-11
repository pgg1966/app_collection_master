"""Catálogo de códigos de una colección (Sesión 5d / fix OCR).

`CodeCatalog` empaqueta los dos datos que el validador de OCR necesita
en una sola estructura: los códigos válidos (en orden de álbum) y el
número máximo de card por código. Vive como dataclass agregado para
respetar la sec 2.3 de CLAUDE.md (los repos retornan modelos, no
`list[str]` ni `dict[str, int]` sueltos).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CodeCatalog:
    """Snapshot del catálogo de códigos de una colección.

    Attributes:
        codes: códigos únicos en orden por `code_order` (orden del álbum).
        max_number_by_code: `{code_id: max(card_number)}` para validar
            si un número leído cae dentro del rango esperado.
    """

    codes: tuple[str, ...]
    max_number_by_code: dict[str, int]
