"""Snapshot agnóstico de un inventario para pairing (Prompt 5).

`InventorySnapshot` y sus dataclasses asociados son la entrada/salida
del `MatchingService`. Son **agnósticos del medio**: vienen de un
archivo `.colexchange` en v0.2, podrían venir de una API REST en
v1.0, sin que la lógica de matching cambie.

Aislamiento por capas (CLAUDE.md sec 2.1, regla `models`): solo
stdlib (dataclasses, slots, frozen). No tocan repos, services, views,
sqlite3 ni Qt.

Frozen + tuples (no list) garantizan equality por valor + hashable,
útil para tests deterministas.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MissingCard:
    """Una card que el usuario aún no tiene (faltante del álbum)."""

    code_id: str
    card_number: int
    card_name: str
    needed_quantity: int


@dataclass(slots=True, frozen=True)
class DuplicateCard:
    """Una card que el usuario tiene de más (disponible para intercambio)."""

    code_id: str
    card_number: int
    card_name: str
    available_quantity: int


@dataclass(slots=True, frozen=True)
class InventorySnapshot:
    """Foto del inventario de un usuario para una colección.

    `user_label` es opcional; los demás campos son obligatorios.
    `missing` y `duplicates` son tuplas (no listas) para mantener el
    dataclass frozen + hashable + equality por valor.
    """

    user_label: str | None
    collection_name: str
    collection_card_count: int
    missing: tuple[MissingCard, ...]
    duplicates: tuple[DuplicateCard, ...]
