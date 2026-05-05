"""Test de arquitectura sec 2.2 — paridad tabla SQL ↔ dataclass ↔ repo.

Para cada `CREATE TABLE` en las migraciones (excepto `schema_version`),
verifica que existe:
- Un dataclass en `core/models/<x>.py` con clase `<X>`.
- Un repositorio en `core/repositories/<x>_repo.py` con clase `<X>Repository`.

Algunos mapeos son irregulares (ej. `inventory` → `InventoryItem`), por
lo que se mantienen en `EXPECTED_MAPPING` explícito. Si una tabla nueva
se introduce, este test falla hasta que se completa el trío.

Tests SOLO sobre la migración 001. Cuando aterricen migraciones nuevas
que agreguen tablas, extender `EXPECTED_MAPPING`.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = PROJECT_ROOT / "src" / "collections_app" / "core" / "db" / "schema"
MODELS_DIR = PROJECT_ROOT / "src" / "collections_app" / "core" / "models"
REPOS_DIR = PROJECT_ROOT / "src" / "collections_app" / "core" / "repositories"

# Tabla -> (módulo modelo, clase modelo, módulo repo, clase repo).
# Mantenido a mano porque hay irregularidades (inventory -> InventoryItem,
# codes_headers -> CodeHeader, etc.) que un guesser automático no captura.
EXPECTED_MAPPING: dict[str, tuple[str, str, str, str]] = {
    "app_settings": (
        "app_setting",
        "AppSetting",
        "app_settings_repo",
        "AppSettingsRepository",
    ),
    "codes_headers": (
        "code_header",
        "CodeHeader",
        "code_headers_repo",
        "CodeHeadersRepository",
    ),
    "codes_lines": (
        "code_line",
        "CodeLine",
        "code_lines_repo",
        "CodeLinesRepository",
    ),
    "collections": (
        "collection",
        "Collection",
        "collections_repo",
        "CollectionsRepository",
    ),
    "cards": ("card", "Card", "cards_repo", "CardsRepository"),
    "inventory": (
        "inventory_item",
        "InventoryItem",
        "inventory_repo",
        "InventoryRepository",
    ),
    "card_images": (
        "card_image",
        "CardImage",
        "card_images_repo",
        "CardImagesRepository",
    ),
    "transactions": (
        "transaction",
        "Transaction",
        "transactions_repo",
        "TransactionsRepository",
    ),
}

# Tablas presentes en el schema que NO requieren modelo + repo.
EXEMPT_TABLES = {"schema_version"}

CREATE_TABLE_RE = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE)


def _tables_in_schema() -> set[str]:
    """Set de nombres de tabla declarados con CREATE TABLE en las migraciones."""
    tables: set[str] = set()
    for sql_path in sorted(SCHEMA_DIR.glob("*.sql")):
        sql = sql_path.read_text(encoding="utf-8")
        tables.update(CREATE_TABLE_RE.findall(sql))
    return tables


def _file_defines_class(path: Path, class_name: str) -> bool:
    """True si `path` existe y declara `class <class_name>` top-level."""
    if not path.is_file():
        return False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(isinstance(node, ast.ClassDef) and node.name == class_name for node in tree.body)


def test_every_table_has_model_and_repo() -> None:
    """Sec 2.2: paridad estricta tabla ↔ modelo ↔ repo."""
    actual_tables = _tables_in_schema() - EXEMPT_TABLES
    declared = set(EXPECTED_MAPPING.keys())

    missing_in_mapping = actual_tables - declared
    assert not missing_in_mapping, (
        f"Tablas en schema sin entry en EXPECTED_MAPPING: {missing_in_mapping}. "
        "Agregar el trío modelo+repo+entry para cada una."
    )

    extra_in_mapping = declared - actual_tables
    assert (
        not extra_in_mapping
    ), f"EXPECTED_MAPPING declara tablas que no existen: {extra_in_mapping}."


@pytest.mark.parametrize(
    "table",
    sorted(EXPECTED_MAPPING.keys()),
    ids=sorted(EXPECTED_MAPPING.keys()),
)
def test_table_has_model_file_and_class(table: str) -> None:
    """Existe core/models/<x>.py con `class <X>`."""
    model_module, model_class, _, _ = EXPECTED_MAPPING[table]
    # Modelo puede vivir en core/models/<module>.py o
    # core/models/aggregates/<module>.py — chequear ambos.
    candidates = [
        MODELS_DIR / f"{model_module}.py",
        MODELS_DIR / "aggregates" / f"{model_module}.py",
    ]
    found = any(_file_defines_class(p, model_class) for p in candidates)
    assert found, (
        f"Tabla '{table}' espera dataclass '{model_class}' en uno de "
        f"{[str(p.relative_to(PROJECT_ROOT)) for p in candidates]}, no encontrado."
    )


@pytest.mark.parametrize(
    "table",
    sorted(EXPECTED_MAPPING.keys()),
    ids=sorted(EXPECTED_MAPPING.keys()),
)
def test_table_has_repo_file_and_class(table: str) -> None:
    """Existe core/repositories/<x>_repo.py con `class <X>Repository`."""
    _, _, repo_module, repo_class = EXPECTED_MAPPING[table]
    repo_path = REPOS_DIR / f"{repo_module}.py"
    assert _file_defines_class(repo_path, repo_class), (
        f"Tabla '{table}' espera repo '{repo_class}' en "
        f"core/repositories/{repo_module}.py, no encontrado."
    )
