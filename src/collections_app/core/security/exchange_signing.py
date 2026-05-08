"""Firma HMAC-SHA256 para archivos `.colexchange`.

Provee `compute_signature` y `verify_signature`. La clave es una
constante de 32 bytes hardcoded en este módulo, generada una sola
vez para v0.2.x y mantenida estable por toda la línea (ver
`docs/exchange_design.md`, sección "Implementación de la clave").

Nivel de protección 2 (decisión arquitectónica):
- Detecta archivos no generados por la app (firma no coincide).
- Detecta ediciones manuales y archivos corruptos.
- NO protege contra alguien que decompila la app y extrae la clave.
- Ese trade-off es proporcional al riesgo de una app de coleccionistas
  entre amigos. Si en el futuro se justifica Nivel 3 (servidor), se
  migra entonces.

Aislamiento por capas (CLAUDE.md sec 2.1, regla `core/security`):
este módulo solo importa stdlib (`hmac`, `hashlib`, `json`). No toca
repos, services, views ni Qt. La clave NO se loggea, NO aparece en
mensajes de error ni en variables de entorno.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

# Generada con `secrets.token_bytes(32)` y pegada como literal hex.
# Ver `docs/exchange_design.md` (Nivel 2 protection by design).
EXCHANGE_HMAC_KEY: bytes = bytes.fromhex(  # noqa: S105 — see docs/exchange_design.md
    "6143677adaa5f25a0c8d7108eae45d13e15469b613a7b4a9c24ad396182fb739"
)


def _canonical_json(payload: dict[str, Any]) -> bytes:
    """Serialización determinista del payload para HMAC.

    `sort_keys=True` ordena las claves alfabéticamente (mismo dict
    siempre da el mismo string). `separators=(",", ":")` elimina
    espacios entre tokens (más compacto y determinista).
    `ensure_ascii=False` preserva caracteres unicode tal cual (los
    nombres de cards pueden tener acentos).
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_signature(payload: dict[str, Any]) -> str:
    """Calcula HMAC-SHA256 sobre `payload` (sin el campo `signature`).

    El caller es responsable de pasar el dict SIN la clave `signature`
    — este módulo no extrae ni inserta. Devuelve el hex digest (64
    caracteres lowercase).
    """
    canonical = _canonical_json(payload)
    digest = hmac.new(EXCHANGE_HMAC_KEY, canonical, hashlib.sha256)
    return digest.hexdigest()


def verify_signature(payload: dict[str, Any], signature: str) -> bool:
    """Verifica que `signature` matchea el HMAC de `payload`.

    Usa `hmac.compare_digest` (comparación constant-time, resistente
    a timing attacks). El `payload` debe pasarse SIN el campo
    `signature` — el caller lo extrae antes de llamar.
    """
    expected = compute_signature(payload)
    return hmac.compare_digest(expected, signature)
