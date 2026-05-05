"""Migración one-shot: renombra archivos de cards legacy a formato con padding.

Antes de centralizar el formato del filename (`format_card_filename`),
algunas tools/scripts pudieron haber escrito archivos sin padding
(`1.jpg`, `42.png`). Este script los renombra a `0001.jpg`, `0042.png`
para que `find_card_image` los encuentre.

Convención: padding fijo a 4 dígitos. NO toca archivos que ya estén
correctamente padded ni archivos que no matcheen el patrón
`{n}.{jpg|jpeg|png}` con `n` siendo un entero positivo.

Uso CLI:
    python -m collections_app.admin.tools.rename_legacy_cards --collection-id 1
    python -m collections_app.admin.tools.rename_legacy_cards --collection-id 2 --dry-run
"""

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from collections_app.core.utils.paths import (
    format_card_filename,
    get_generated_cards_dir,
)

logger = logging.getLogger(__name__)

# Archivos legacy: dígitos sin padding + extensión de imagen.
_LEGACY_PATTERN = re.compile(r"^(\d{1,3})\.(jpg|jpeg|png)$", re.IGNORECASE)
# Archivos ya correctamente padded (4 dígitos).
_PADDED_PATTERN = re.compile(r"^\d{4,}\.(jpg|jpeg|png)$", re.IGNORECASE)


@dataclass
class RenameResult:
    """Resumen del run de migración."""

    renamed: int = 0
    skipped_already_padded: int = 0
    skipped_unrecognized: int = 0
    skipped_collision: int = 0
    errors: int = 0


def rename_legacy_cards(collection_dir: Path, *, dry_run: bool = False) -> RenameResult:
    """Renombra archivos legacy a formato con padding dentro de `collection_dir`.

    `dry_run=True` solo loguea las acciones sin tocar el filesystem.
    Si el destino padded ya existe, NO se sobreescribe — se loguea warning.
    """
    result = RenameResult()
    if not collection_dir.exists():
        logger.warning("Directorio no existe: %s", collection_dir)
        return result

    for path in sorted(collection_dir.iterdir()):
        if not path.is_file():
            continue

        if _PADDED_PATTERN.match(path.name):
            result.skipped_already_padded += 1
            continue

        match = _LEGACY_PATTERN.match(path.name)
        if not match:
            result.skipped_unrecognized += 1
            logger.debug("Saltando archivo no reconocido: %s", path.name)
            continue

        card_number = int(match.group(1))
        ext = match.group(2).lower()
        new_name = format_card_filename(card_number, ext)
        new_path = path.with_name(new_name)

        if new_path.exists():
            result.skipped_collision += 1
            logger.warning(
                "Colisión: ya existe %s, no se sobreescribe (legacy %s queda intacto)",
                new_path.name,
                path.name,
            )
            continue

        if dry_run:
            logger.info("[dry-run] %s → %s", path.name, new_name)
            result.renamed += 1
            continue

        try:
            path.rename(new_path)
            logger.info("%s → %s", path.name, new_name)
            result.renamed += 1
        except OSError as exc:
            logger.error("Error renombrando %s → %s: %s", path.name, new_name, exc)
            result.errors += 1

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Renombra archivos de cards legacy (sin padding) a " "formato con padding 4 dígitos."
        ),
    )
    parser.add_argument("--collection-id", type=int, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar qué se renombraría sin hacer cambios",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    collection_dir = get_generated_cards_dir() / str(args.collection_id)
    print(f"Directorio: {collection_dir}")
    print(f"Dry-run:    {args.dry_run}")
    print()

    result = rename_legacy_cards(collection_dir, dry_run=args.dry_run)

    print()
    print("=== Resumen ===")
    label = "Renombrarían" if args.dry_run else "Renombrados"
    print(f"{label}:                {result.renamed}")
    print(f"Ya con padding (skip):       {result.skipped_already_padded}")
    print(f"No reconocidos (skip):       {result.skipped_unrecognized}")
    print(f"Colisiones (skip):           {result.skipped_collision}")
    print(f"Errores:                     {result.errors}")
    return 0 if result.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
