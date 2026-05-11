"""Lector OCR de un badge ya recortado (Sesión 5d / fix pipeline).

Toma un crop NumPy (BGR, salida típica de cv2.imread) de un badge y
devuelve el texto crudo que el validador convertirá a un código
canónico. Usa EasyOCR, que maneja mucho mejor que Tesseract el caso
"texto blanco sobre fondo oscuro" — los badges de Panini.

**Imports lazy obligatorios (CLAUDE.md sec 2.1 + regla 5d):** ni
`easyocr` ni `cv2` aparecen en nivel de módulo. Se importan adentro de
`_get_reader()` y `_get_cv2()`. El test de arquitectura
`test_no_top_level_torch_imports` también los cubre.

El reader vive como singleton de módulo: la primera carga descarga el
modelo de EasyOCR (~100 MB) y construye la red — caro. Las llamadas
sucesivas reusan el reader cargado.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Whitelist de caracteres aceptables. Restringe la salida del OCR para
# que no aparezcan signos de puntuación o caracteres no-ASCII que el
# validador tendría que filtrar.
_ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Singletons de módulo (lazy).
_reader: object | None = None  # easyocr.Reader, tipado como object por sec 2.1.


def _get_reader() -> object:
    """Devuelve el `easyocr.Reader` singleton, cargándolo en el primer uso.

    El import vive adentro para que `import ocr_reader` no arrastre
    torch + easyocr al árbol de imports — eso rompería el arranque de
    la app cuando las dependencias aún no se instalaron.
    """
    global _reader
    if _reader is None:
        import easyocr  # noqa: PLC0415

        logger.info("Cargando modelo EasyOCR (primera vez puede tardar)...")
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        logger.info("EasyOCR cargado")
    return _reader


def leer_badge(crop: object) -> str:
    """Lee el texto de un crop de badge (array NumPy BGR).

    Args:
        crop: imagen recortada del badge, típicamente el output de
            `img[y1:y2, x1:x2]` después de la detección YOLO. Anotado
            como `object` para que el módulo no requiera importar
            NumPy a nivel de módulo (las views no pueden, y este
            service se importa lazy desde un view).

    Returns:
        String con el texto detectado limpio (sólo letras y dígitos,
        uppercase). Ejemplos: `"IRO6"`, `"TUR20"`, `"KORG"` (este último
        es un error típico de OCR que el validador corrige a `"KOR 6"`).

        Devuelve `""` si el crop es None / vacío / si EasyOCR falla.
    """
    if crop is None or getattr(crop, "size", 0) == 0:
        return ""

    import cv2  # noqa: PLC0415

    reader = _get_reader()
    candidatos: list[str] = []

    # Variante 1: imagen original.
    candidatos.extend(_ocr_imagen(reader, crop))

    # Variante 2: imagen escalada x3 si es chica (a veces ayuda).
    h, w = crop.shape[:2]
    if h < 60:
        big = cv2.resize(crop, (w * 3, h * 3), interpolation=cv2.INTER_LANCZOS4)
        candidatos.extend(_ocr_imagen(reader, big))

    if not candidatos:
        return ""

    # Preferir candidatos que matcheen exactamente el formato XXX## o XX#.
    # Si hay uno, devolverlo directo — sin ambigüedad.
    for c in candidatos:
        if re.match(r"^[A-Z]{2,3}\d{1,2}$", c):
            return c

    # Si ninguno matchea, devolver el más largo: le da más info al
    # validador para que aplique sus correcciones (letra↔dígito).
    return max(candidatos, key=len)


def _ocr_imagen(reader: object, img: object) -> list[str]:
    """Ejecuta EasyOCR sobre `img` y devuelve textos limpios.

    Si EasyOCR separa "IRO" y "6" en dos detecciones, agrega también
    la versión concatenada para que el validador pueda intentar
    interpretarla como una sola unidad.
    """
    try:
        resultados = reader.readtext(  # type: ignore[attr-defined]
            img,
            detail=0,
            allowlist=_ALLOWLIST,
            paragraph=False,
        )
    except Exception as exc:  # noqa: BLE001 — bug del modelo / GPU / etc.
        logger.warning("Error en EasyOCR: %s", exc)
        return []

    textos: list[str] = []
    for r in resultados:
        limpio = re.sub(r"[^A-Z0-9]", "", str(r).upper())
        if limpio:
            textos.append(limpio)

    if len(textos) > 1:
        textos.append("".join(textos))
    return textos
