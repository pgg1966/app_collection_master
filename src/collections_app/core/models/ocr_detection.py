"""Modelos para el reconocimiento óptico de cards (Sesión 5d).

`OcrDetection` representa una card detectada exitosamente: el label
crudo de YOLO ya parseado a `(code_id, card_number)`, la confianza,
y el matching contra el catálogo de la collection.

`OcrParseError` representa una detección cuyo label no pudo parsearse
(formato inesperado, número inválido). Se reporta al usuario pero no
crashea el flow.

`parse_label` es la función pura que transforma un label crudo de YOLO
("ARG-04", "ARG04", "04") en `(code_id, card_number)`. Devuelve `None`
si el label es inválido para esa colección — el caller decide si
acumular el resultado en un `OcrParseError` con un `reason` específico.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Captura code_id (letras) opcional, separador opcional, y número.
# - "ARG-04"  → groups ("ARG", "04")
# - "ARG04"   → groups ("ARG", "04")
# - "04"      → groups (None, "04")
_LABEL_RE = re.compile(r"^([A-Za-z]+)?[-_ ]?(\d+)$")


def parse_label(raw: str, *, requires_code: bool) -> tuple[str, int] | None:
    """Parsea un label crudo de YOLO a `(code_id, card_number)`.

    Reglas:

    - Trim de whitespace, code_id se uppercased.
    - Formato aceptado: `[CODE][-_ ]?NUMBER` con `CODE` letras,
      `NUMBER` dígitos > 0.
    - Si `requires_code=True` y el label no trae código: `None`.
    - Si `requires_code=False`: acepta tanto solo número como código
      + número (si viene se conserva).
    - `card_number = 0` o negativo se rechaza.

    Returns:
        Tupla `(code_id, card_number)` o `None` si el label no encaja.
    """
    text = raw.strip().upper()
    if not text:
        return None
    match = _LABEL_RE.match(text)
    if match is None:
        return None
    code, number_str = match.group(1), match.group(2)
    try:
        number = int(number_str)
    except ValueError:  # defensivo, regex ya garantiza dígitos
        return None
    if number <= 0:
        return None
    if requires_code and not code:
        return None
    return (code or "", number)


@dataclass(frozen=True, slots=True)
class OcrDetection:
    """Card detectada por YOLO y resuelta contra la DB local.

    Attributes:
        raw_label: el string que devolvió YOLO (ej. "ARG-04").
        code_id: parseado del raw_label, "" si la colección no usa códigos.
        card_number: parseado del raw_label.
        confidence: entre 0 y 1, lo que reportó el modelo.
        card_name: nombre humano de la card resuelto contra el catálogo.
            "" si el card_id no se encontró.
        card_id: PK de la card en la DB local, o `None` si la combinación
            (code_id, card_number) no existe en el catálogo de la
            colección activa.
        bbox: coordenadas del bounding box detectado por YOLO, ya
            ajustadas con el padding del crop. Formato `(x1, y1, x2, y2)`
            en píxeles sobre la imagen original. Sirve para anotar la
            foto en el dialog post-procesamiento.
    """

    raw_label: str
    code_id: str
    card_number: int
    confidence: float
    card_name: str
    card_id: int | None
    bbox: tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class OcrParseError:
    """Detección cuyo label no pudo parsearse al formato esperado.

    No es una excepción: se acumula en una lista paralela a las
    `OcrDetection` y se le muestra al usuario como aviso. El flow
    continúa con las detecciones válidas.
    """

    raw_label: str
    confidence: float
    reason: str
