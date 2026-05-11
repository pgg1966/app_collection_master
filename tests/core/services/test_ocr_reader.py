"""Tests del módulo `ocr_reader` — mock de EasyOCR y cv2.

Cero modelo real cargado, cero dependencia de easyocr/cv2 instalados:
los imports lazy se interceptan con `sys.modules` antes de invocar
`leer_badge`.

Cubre:

- `leer_badge` con crop None / size=0 → "".
- Caso happy path: EasyOCR devuelve un texto que matchea el formato
  XXX## → se devuelve sin cambios.
- Múltiples textos: se prueba también la concatenación.
- Texto que no matchea formato → devuelve el más largo.
- Imagen chica (h<60) → se escala x3 y se vuelve a OCR.
- Error en EasyOCR → devuelve `""`.
"""

from __future__ import annotations

import sys
import types
from typing import Any

import pytest

from collections_app.services import ocr_reader

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


class _FakeCrop:
    """Mínimo numpy.ndarray-like para que `leer_badge` no requiera numpy real."""

    def __init__(self, h: int, w: int) -> None:
        self.shape = (h, w, 3)
        self.size = h * w * 3


def _install_fake_easyocr(
    monkeypatch: pytest.MonkeyPatch,
    readtext_return: list[list[str]],
) -> None:
    """Patch `easyocr.Reader.readtext` para devolver listas configurables.

    `readtext_return` es una lista de listas: en cada llamada a
    `_ocr_imagen` devuelve la siguiente entrada (consumiendo una
    posición del queue). Esto permite simular el caso de variante
    original vs escalada que `leer_badge` hace internamente.
    """
    calls: list[list[str]] = list(readtext_return)

    class _FakeReader:
        def readtext(self, _img: Any, **_kwargs: Any) -> list[str]:
            if not calls:
                return []
            return calls.pop(0)

    fake_module = types.ModuleType("easyocr")
    fake_module.Reader = lambda *_a, **_k: _FakeReader()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "easyocr", fake_module)
    # Reset del singleton para que cada test instancie un reader nuevo.
    monkeypatch.setattr(ocr_reader, "_reader", None, raising=False)


def _install_fake_cv2(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch `cv2.resize` y constantes mínimas."""
    fake_module = types.ModuleType("cv2")
    fake_module.INTER_LANCZOS4 = 4  # type: ignore[attr-defined]

    def fake_resize(img, _size, **_kwargs):  # type: ignore[no-untyped-def]
        return img  # devuelve la misma imagen para tests deterministas

    fake_module.resize = fake_resize  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cv2", fake_module)


# ---------------------------------------------------------------------
# Casos edge
# ---------------------------------------------------------------------


def test_leer_badge_none_returns_empty() -> None:
    assert ocr_reader.leer_badge(None) == ""


def test_leer_badge_empty_crop_returns_empty() -> None:
    """Crop con size=0 (array vacío) → string vacío sin tocar EasyOCR."""

    class _EmptyCrop:
        size = 0
        shape = (0, 0, 3)

    assert ocr_reader.leer_badge(_EmptyCrop()) == ""


# ---------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------


def test_leer_badge_returns_match_formatted_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si EasyOCR devuelve un texto que matchea XXX##, ese se devuelve."""
    _install_fake_cv2(monkeypatch)
    _install_fake_easyocr(monkeypatch, [["IRO6"]])
    crop = _FakeCrop(h=100, w=100)
    assert ocr_reader.leer_badge(crop) == "IRO6"


def test_leer_badge_concatenates_when_multiple_texts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """EasyOCR a veces separa el código del número en dos detecciones.

    El reader agrega la concatenación como candidato extra, que sí
    matchea el formato y se devuelve.
    """
    _install_fake_cv2(monkeypatch)
    _install_fake_easyocr(monkeypatch, [["IRO", "6"]])
    crop = _FakeCrop(h=100, w=100)
    assert ocr_reader.leer_badge(crop) == "IRO6"


def test_leer_badge_returns_longest_when_no_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin candidatos que matcheen XXX##, devuelve el más largo (al
    validador, que aplica correcciones letra↔dígito).

    Input: ["FOO", "BAR"] (ninguno matchea XXX##). El reader agrega
    además la concatenación "FOOBAR" → ese es el más largo y se
    devuelve.
    """
    _install_fake_cv2(monkeypatch)
    _install_fake_easyocr(monkeypatch, [["FOO", "BAR"]])
    crop = _FakeCrop(h=100, w=100)
    assert ocr_reader.leer_badge(crop) == "FOOBAR"


# ---------------------------------------------------------------------
# Imagen chica → escala x3 + OCR de la versión grande
# ---------------------------------------------------------------------


def test_leer_badge_small_image_runs_ocr_twice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """h < 60 dispara la variante escalada → 2 llamadas a readtext."""
    calls: list[Any] = []

    class _CountingReader:
        def readtext(self, img: Any, **_kwargs: Any) -> list[str]:
            calls.append(img)
            return ["IRO6"]

    fake_easyocr = types.ModuleType("easyocr")
    fake_easyocr.Reader = lambda *_a, **_k: _CountingReader()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "easyocr", fake_easyocr)
    monkeypatch.setattr(ocr_reader, "_reader", None, raising=False)
    _install_fake_cv2(monkeypatch)

    crop = _FakeCrop(h=30, w=80)  # h < 60 → escala
    ocr_reader.leer_badge(crop)
    assert len(calls) == 2


def test_leer_badge_normal_size_runs_ocr_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """h >= 60 → solo una pasada por EasyOCR."""
    calls: list[Any] = []

    class _CountingReader:
        def readtext(self, img: Any, **_kwargs: Any) -> list[str]:
            calls.append(img)
            return ["IRO6"]

    fake_easyocr = types.ModuleType("easyocr")
    fake_easyocr.Reader = lambda *_a, **_k: _CountingReader()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "easyocr", fake_easyocr)
    monkeypatch.setattr(ocr_reader, "_reader", None, raising=False)
    _install_fake_cv2(monkeypatch)

    crop = _FakeCrop(h=80, w=120)
    ocr_reader.leer_badge(crop)
    assert len(calls) == 1


# ---------------------------------------------------------------------
# Errores de EasyOCR
# ---------------------------------------------------------------------


def test_leer_badge_swallows_easyocr_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si EasyOCR rompe (bug del modelo, GPU, etc.), devuelve "" sin crashear."""

    class _BrokenReader:
        def readtext(self, *_a: Any, **_k: Any) -> list[str]:
            raise RuntimeError("modelo corrupto")

    fake_easyocr = types.ModuleType("easyocr")
    fake_easyocr.Reader = lambda *_a, **_k: _BrokenReader()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "easyocr", fake_easyocr)
    monkeypatch.setattr(ocr_reader, "_reader", None, raising=False)
    _install_fake_cv2(monkeypatch)

    crop = _FakeCrop(h=100, w=100)
    assert ocr_reader.leer_badge(crop) == ""


# ---------------------------------------------------------------------
# Cleanup del singleton entre tests
# ---------------------------------------------------------------------


def test_reader_singleton_resets_per_test(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sanity: cada test que use _install_fake_easyocr resetea el singleton.

    Si el singleton persistiera entre tests, los tests serían
    inter-dependientes según orden — este test confirma el reset.
    """
    _install_fake_cv2(monkeypatch)
    _install_fake_easyocr(monkeypatch, [["X"]])
    assert ocr_reader._reader is None  # antes del primer uso
    crop = _FakeCrop(h=100, w=100)
    ocr_reader.leer_badge(crop)
    assert ocr_reader._reader is not None  # ya cargado
