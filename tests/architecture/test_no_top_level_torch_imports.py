"""Architecture test — dependencias OCR SOLO en imports lazy (Sesión 5d).

Las dependencias pesadas del OCR (`torch`, `torchvision`, `ultralytics`,
`easyocr`, `cv2`) NO van en el `.exe` base; se instalan bajo demanda
desde la app. Si algún archivo de `src/` las importa a nivel de módulo,
la app crashea al arrancar con `ModuleNotFoundError` cuando el usuario
todavía no instaló nada.

Este test recorre todos los `.py` de `src/collections_app/` y verifica
que ninguna línea que comience con `import <pkg>` o `from <pkg>`
(para los packages prohibidos) aparezca en el nivel de módulo (sin
indentación).

Imports lazy dentro de funciones/métodos están permitidos (van con
indentación → no matchean este check).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Tupla de prefijos prohibidos a nivel de módulo. Cualquier línea que
# arranque con `import X` o `from X.foo` para alguno de estos packages
# rompe el test.
_FORBIDDEN_PKGS = ("torch", "torchvision", "ultralytics", "easyocr", "cv2")
_FORBIDDEN_TOP_LEVEL = re.compile(
    r"^(?:import|from)\s+(?:" + "|".join(_FORBIDDEN_PKGS) + r")\b",
    re.MULTILINE,
)


def _src_files() -> list[Path]:
    here = Path(__file__).resolve()
    src_root = here.parent.parent.parent / "src" / "collections_app"
    return sorted(src_root.rglob("*.py"))


@pytest.mark.parametrize("path", _src_files(), ids=lambda p: p.name)
def test_no_top_level_torch_or_ultralytics_imports(path: Path) -> None:
    """Cada `.py` de src/ no debe importar torch/ultralytics sin indentar."""
    text = path.read_text(encoding="utf-8")
    matches = _FORBIDDEN_TOP_LEVEL.findall(text)
    assert not matches, (
        f"{path.relative_to(path.parents[3])} tiene un import top-level "
        f"prohibido: {matches}. Mover dentro de un método con noqa: PLC0415."
    )
