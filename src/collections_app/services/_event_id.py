"""Helper for generating unique event_ids that group related transactions.

Used by inventory imports (Prompt 4c) and pairing exchanges (Prompt 5).

The event_id is stored in `transactions.exchange_event_id` (INTEGER,
nullable). Schema doesn't require uniqueness, but for diagnostic /
reporting purposes we want collisions to be very unlikely even when
multiple imports run in the same millisecond.

Format: `epoch_ms × 1000 + random_suffix(0..999)` → ~16-17 digit int,
fits in int64 (max ~9.2 × 10^18). At >10^15, far above human-scale
volumes, so collision probability is negligible.
"""

from __future__ import annotations

import random
import time


def generate_event_id() -> int:
    """Genera un event_id único para agrupar transacciones relacionadas.

    Returns:
        Entero de ~16-17 dígitos: epoch_ms × 1000 + random suffix.
        Cabe en int64 sin problemas.
    """
    # No es uso criptográfico — solo agrupador de transacciones para
    # reporting; `random.randint` alcanza y evita el peso de `secrets`.
    return int(time.time() * 1000) * 1000 + random.randint(0, 999)  # noqa: S311
