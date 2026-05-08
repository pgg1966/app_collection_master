"""TEMP perf diagnostic — REMOVE este archivo y todos sus imports en el
commit de cleanup tras identificar el bottleneck del cambio lento de
colección.

CLAUDE.md sec 3.8: módulo aislado para que la limpieza sea trivial.
Búsqueda recomendada para cleanup: `grep -rn "TEMP perf diagnostic"`.

Imprime a stderr (no usa logger) para evitar configuración global que
podría tener side effects en tests. Mismo patrón usado en el debugging
del issue #002.
"""

from __future__ import annotations

import sys
import time

_T0 = time.perf_counter()


def plog(label: str) -> None:
    """Imprime '[XXXX.Xms] label' a stderr con timing relativo al import."""
    elapsed_ms = (time.perf_counter() - _T0) * 1000
    print(f"[{elapsed_ms:9.1f}ms] {label}", file=sys.stderr, flush=True)
