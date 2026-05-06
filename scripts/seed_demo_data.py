"""Crea datos de demostración para validar el flow end-to-end de la UI.

Uso:
    python scripts/seed_demo_data.py                # default profile
    python scripts/seed_demo_data.py --profile demo # collections_demo.db

Seedea exactamente:
- 1 CodeHeader: "Países FIFA" (max_length=3)
- 5 CodeLine: ARG, BRA, FRA, ITA, ESP (con code_order 1..5)
- 1 Collection: "Mundial 2026 Demo" (requires_code=True)
- 12 Card distribuidas: ARG-1..3, BRA-1..3, FRA-1..2, ITA-1..2, ESP-1..2

NO seedea inventario. La idea es que el usuario haga las altas él mismo
desde la UI para probar el flow Mis cards / Cargar stock / Historial.

Idempotente: si la colección "Mundial 2026 Demo" ya existe en el profile
target, sale sin tocar nada con un mensaje informativo. Para regenerar
desde cero hay que borrar la DB del profile o usar otro `--profile`.
"""

from __future__ import annotations

import argparse
import sys

from collections_app.app_context import create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.utils.paths import get_db_path_for_profile

DEMO_COLLECTION_NAME = "Mundial 2026 Demo"
DEMO_HEADER_NAME = "Países FIFA"

DEMO_CODES = [
    ("ARG", "Argentina"),
    ("BRA", "Brasil"),
    ("FRA", "Francia"),
    ("ITA", "Italia"),
    ("ESP", "España"),
]

DEMO_CARDS: list[tuple[str, int, str]] = [
    ("ARG", 1, "Lionel Messi"),
    ("ARG", 2, "Emiliano Martínez"),
    ("ARG", 3, "Julián Álvarez"),
    ("BRA", 1, "Vinicius Jr."),
    ("BRA", 2, "Rodrygo"),
    ("BRA", 3, "Casemiro"),
    ("FRA", 1, "Kylian Mbappé"),
    ("FRA", 2, "Antoine Griezmann"),
    ("ITA", 1, "Gianluigi Donnarumma"),
    ("ITA", 2, "Federico Chiesa"),
    ("ESP", 1, "Pedri"),
    ("ESP", 2, "Lamine Yamal"),
]


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seedea datos de demostración en la DB del profile elegido."
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Profile target. Sin --profile usa la DB default.",
    )
    return parser.parse_args(argv)


def seed(profile: str | None) -> int:
    """Aplica el seed sobre el profile dado. Idempotente.

    Returns:
        0 si seedeó OK o si ya estaba seedeado (no error).
        2 si el profile es inválido.
    """
    try:
        db_path = get_db_path_for_profile(profile)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    profile_label = profile if profile is not None else "default"
    print(f"Seedeando profile {profile_label!r} en {db_path}")

    ctx = create_app_context(db_path)
    try:
        existing = ctx.collections.get_by_name(DEMO_COLLECTION_NAME)
        if existing is not None:
            print(f"Ya existe la colección demo {DEMO_COLLECTION_NAME!r} " f"en este profile.")
            print(
                "Para regenerarla desde cero, borrá la DB del profile " "o usá un profile distinto:"
            )
            print("  python scripts/seed_demo_data.py --profile demo")
            return 0

        # 1. Header
        header_existing = ctx.code_headers.get_by_name(DEMO_HEADER_NAME)
        if header_existing is None:
            header = ctx.code_headers.create(
                CodeHeader(
                    code_header_id=None,
                    code_header_name=DEMO_HEADER_NAME,
                    code_max_length=3,
                )
            )
        else:
            header = header_existing
        assert header.code_header_id is not None

        # 2. Code lines
        for order, (code_id, code_name) in enumerate(DEMO_CODES, start=1):
            ctx.code_lines.upsert(
                CodeLine(
                    code_line_id=None,
                    code_header_id=header.code_header_id,
                    code_id=code_id,
                    code_name=code_name,
                    code_order=order,
                )
            )

        # 3. Collection
        collection = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name=DEMO_COLLECTION_NAME,
                card_count=len(DEMO_CARDS),
                requires_code=True,
                code_field_name="País",
                code_header_id=header.code_header_id,
            )
        )
        assert collection.collection_id is not None

        # 4. Cards
        cards = [
            Card(
                card_id=None,
                collection_id=collection.collection_id,
                code_id=code_id,
                card_number=number,
                card_name=name,
            )
            for code_id, number, name in DEMO_CARDS
        ]
        ctx.cards.bulk_upsert(cards)

        ctx.conn.commit()
        print(
            f"OK: seedeada {DEMO_COLLECTION_NAME!r} con "
            f"{len(DEMO_CODES)} codes y {len(DEMO_CARDS)} cards."
        )
        return 0
    finally:
        ctx.close()


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    return seed(args.profile)


if __name__ == "__main__":
    sys.exit(main())
