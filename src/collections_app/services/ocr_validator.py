"""Validador de códigos OCR contra el catálogo de la DB (Sesión 5d).

Toma el texto crudo que devolvió `ocr_reader.leer_badge` y lo convierte
en un código canónico `"XXX N"`, aplicando correcciones letra↔dígito
para los errores típicos de OCR (G→6, O→0, S→5, etc.).

A diferencia del `validator.py` standalone del usuario, los códigos
válidos y los números máximos **no están hardcoded**: se cargan desde
la DB de la colección activa vía `build_validator`. Eso permite reusar
la misma lógica para cualquier álbum (no solo Panini FIFA 2026).

Estructura:

- `LETRA_A_DIGITO` / `DIGITO_A_LETRA`: mapas de correcciones OCR
  típicas. Hardcoded — son característicos de cómo confunden las redes
  OCR sin importar el catálogo.
- `CollectionValidator`: dataclass que encapsula `valid_codes`,
  `max_number_by_code` y `default_max`. Tiene `validar_codigo`.
- `build_validator(collection_id, conn)`: factory que pide el catálogo
  al `CardsRepository` y construye el validador.

La lógica interna de `validar_codigo` se preservó íntegra del
`validator.py` original: scoring, `_corregir_a_numero`,
`_todas_las_posiciones`, `_numero_valido` y la estrategia final con
`DIGITO_A_LETRA`. Solo se cambió la fuente de los datos (DB en lugar
de constantes de módulo).
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass

from collections_app.core.repositories.cards_repo import CardsRepository

# Correcciones típicas: letras que el OCR puede confundir con dígitos.
# Hardcoded — son artefactos del modelo OCR, no del álbum.
LETRA_A_DIGITO: dict[str, str] = {
    "O": "0",
    "I": "1",
    "L": "1",
    "Z": "2",
    "B": "8",
    "S": "5",
    "G": "6",
    "T": "7",
}

# Inversa: dígitos que el OCR puede confundir con letras. Sólo se usa
# en la estrategia final (Ej: "1RO6" → "IRO" + "6").
DIGITO_A_LETRA: dict[str, str] = {
    "1": "I",
    "0": "O",
    "5": "S",
    "8": "B",
    "6": "G",
}

# Default si la colección no especifica un máximo para el código
# (típicamente un álbum donde las cards van de 1 a 20). Se puede
# sobreescribir por colección.
_DEFAULT_MAX = 20


@dataclass(frozen=True, slots=True)
class CollectionValidator:
    """Validador de códigos OCR para una colección específica.

    Attributes:
        valid_codes: frozenset de códigos válidos (uppercase). Se usa
            como universo de comparación para el matching.
        max_number_by_code: máximo `card_number` por código. Si un código
            no aparece acá, se usa `default_max`.
        default_max: límite superior cuando el código no está en
            `max_number_by_code`. Default 20 (caso típico del álbum
            Panini).
    """

    valid_codes: frozenset[str]
    max_number_by_code: dict[str, int]
    default_max: int = _DEFAULT_MAX

    def validar_codigo(self: CollectionValidator, texto_raw: str | None) -> str | None:
        """Convierte texto OCR en código canónico `"XXX N"` o `None`.

        Estrategia (preservada del validator.py original):

        1. Limpiar el texto: solo letras/dígitos, uppercase.
        2. Para cada código válido (más largo primero), buscar todas
           sus posiciones en el texto.
        3. Para cada posición, intentar leer los 2/1 chars siguientes
           como número, aplicando correcciones letra→dígito.
        4. Si el número es válido para ese código, agregarlo como
           candidato con un score (preferimos más dígitos puros y
           menos correcciones).
        5. Devolver el candidato con mejor score.
        6. Estrategia final: aplicar correcciones dígito→letra en los
           primeros 3 chars (último recurso para casos como "1RO6").

        Returns:
            `"CODE NUMBER"` si el matching funcionó, `None` si nada
            cuadró con el catálogo.
        """
        if not texto_raw:
            return None

        texto = re.sub(r"[^A-Z0-9]", "", texto_raw.upper())
        if not texto:
            return None

        candidatos: list[tuple[int, str, int]] = []

        # Para cada código válido (más largo primero), buscar matches.
        for codigo in sorted(self.valid_codes, key=len, reverse=True):
            for idx in _todas_las_posiciones(texto, codigo):
                resto = texto[idx + len(codigo) :]
                if not resto:
                    continue
                for largo_num in (2, 1):
                    if len(resto) < largo_num:
                        continue
                    num_str, correcciones = _corregir_a_numero(resto[:largo_num])
                    if num_str and num_str.isdigit():
                        num = int(num_str)
                        if self._numero_valido(codigo, num):
                            score = largo_num * 10 - correcciones
                            candidatos.append((score, codigo, num))

        if candidatos:
            candidatos.sort(reverse=True)
            _, codigo, num = candidatos[0]
            return f"{codigo} {num}"

        # Estrategia final: corregir dígitos del prefijo a letras.
        if len(texto) >= 4:
            prefijo = ""
            for ch in texto[:3]:
                if ch.isalpha():
                    prefijo += ch
                elif ch in DIGITO_A_LETRA:
                    prefijo += DIGITO_A_LETRA[ch]
                else:
                    break
            if len(prefijo) == 3 and prefijo in self.valid_codes:
                resto = texto[3:]
                for largo_num in (2, 1):
                    if len(resto) >= largo_num:
                        num_str, _ = _corregir_a_numero(resto[:largo_num])
                        if num_str and num_str.isdigit():
                            num = int(num_str)
                            if self._numero_valido(prefijo, num):
                                return f"{prefijo} {num}"
        return None

    def _numero_valido(self: CollectionValidator, codigo: str, num: int) -> bool:
        """¿`num` cae dentro del rango válido para `codigo`?"""
        if num < 1:
            return False
        max_num = self.max_number_by_code.get(codigo, self.default_max)
        return num <= max_num


def build_validator(collection_id: int, conn: sqlite3.Connection) -> CollectionValidator:
    """Construye un `CollectionValidator` leyendo el catálogo de la DB.

    Una sola query al repo (`get_code_catalog`) trae los códigos y los
    máximos. Si la colección está vacía, devuelve un validador con
    `valid_codes=frozenset()` que rechaza todo — útil como guarda
    defensiva si el caller se equivoca de collection_id.
    """
    cards_repo = CardsRepository(conn)
    catalog = cards_repo.get_code_catalog(collection_id)
    return CollectionValidator(
        valid_codes=frozenset(catalog.codes),
        max_number_by_code=catalog.max_number_by_code,
    )


# ----------------------------------------------------------------------
# Helpers (preservados íntegros del validator.py original)
# ----------------------------------------------------------------------


def _todas_las_posiciones(texto: str, sub: str) -> Iterator[int]:
    """Genera todas las posiciones donde aparece `sub` en `texto`."""
    start = 0
    while True:
        idx = texto.find(sub, start)
        if idx < 0:
            return
        yield idx
        start = idx + 1


def _corregir_a_numero(s: str) -> tuple[str, int]:
    """Convierte `s` a string de dígitos aplicando correcciones letra→dígito.

    Returns:
        `(string_de_digitos, num_correcciones_aplicadas)`. Si el char no
        es dígito ni una letra-confusión conocida, se corta el resultado
        en esa posición.
    """
    resultado = ""
    correcciones = 0
    for ch in s:
        if ch.isdigit():
            resultado += ch
        elif ch in LETRA_A_DIGITO:
            resultado += LETRA_A_DIGITO[ch]
            correcciones += 1
        else:
            break
    return resultado, correcciones
