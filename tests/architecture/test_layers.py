"""Tests no-skippables de dirección de imports entre capas (CLAUDE.md sec 2.1).

Recorre todos los archivos .py bajo `src/collections_app/`, parsea con
`ast`, y verifica que cada import respeta la dirección permitida según
la capa del archivo origen.

Mapeo path → capa:

    views/                              -> "views"
    services/                           -> "services"
    core/repositories/                  -> "repositories"
    core/models/                        -> "models"
    core/{db,utils}/                    -> capa libre (no se chequea)

Reglas (prefijos de módulo prohibidos por capa, matcheados con startswith):

    views        -> collections_app.core.repositories,
                    collections_app.core.db,
                    sqlite3
    services     -> PySide6, PyQt5, PyQt6,
                    collections_app.views
    repositories -> PySide6, PyQt5, PyQt6,
                    collections_app.services,
                    collections_app.views
    models       -> sqlite3, PySide6, PyQt5, PyQt6,
                    collections_app.services,
                    collections_app.core.repositories,
                    collections_app.core.db,
                    collections_app.views

TODOs (extender en Prompt 1, ya hay scaffolding mental):

- **Sec 2.2** — paridad tabla SQL ↔ dataclass ↔ repo. Requiere migraciones
  reales y models/repos implementados; agregar a este módulo cuando
  exista la primera tabla.
- **Sec 2.3** — contratos de retorno de los repos (sólo Model | list[Model]
  | None | bool | int). Requiere repos implementados; usar `ast` para
  inspeccionar las anotaciones de retorno de cada método público.

Estos TODOs no pueden implementarse en Prompt 0 sin agregar tablas/modelos/
repos artificiales.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src" / "collections_app"

# Path relativo a src/collections_app/ -> nombre de capa.
LAYER_PATHS: dict[str, str] = {
    "views": "views",
    "services": "services",
    "core/repositories": "repositories",
    "core/models": "models",
}

# Prefijos prohibidos por capa. Match con `module == p` o `module.startswith(p + ".")`.
FORBIDDEN_BY_LAYER: dict[str, frozenset[str]] = {
    "views": frozenset(
        {
            "collections_app.core.repositories",
            "collections_app.core.db",
            "sqlite3",
        }
    ),
    "services": frozenset(
        {
            "PySide6",
            "PyQt5",
            "PyQt6",
            "collections_app.views",
        }
    ),
    "repositories": frozenset(
        {
            "PySide6",
            "PyQt5",
            "PyQt6",
            "collections_app.services",
            "collections_app.views",
        }
    ),
    "models": frozenset(
        {
            "sqlite3",
            "PySide6",
            "PyQt5",
            "PyQt6",
            "collections_app.services",
            "collections_app.core.repositories",
            "collections_app.core.db",
            "collections_app.views",
        }
    ),
}

EXPECTED_LAYERS = frozenset({"views", "services", "repositories", "models"})


def _layer_of(path: Path) -> str | None:
    """Capa del archivo según su ruta relativa a `src/collections_app/`.

    Retorna None si el archivo está fuera de las capas controladas
    (ej. core/db, core/utils, raíz del paquete).
    """
    try:
        rel = path.relative_to(SRC_ROOT)
    except ValueError:
        return None
    rel_posix = rel.as_posix()
    for prefix, layer in LAYER_PATHS.items():
        if rel_posix == prefix or rel_posix.startswith(prefix + "/"):
            return layer
    return None


def _imports_of(tree: ast.Module) -> list[tuple[str, int]]:
    """Lista de `(módulo_importado, lineno)` del archivo.

    - `import a.b.c`         -> ('a.b.c', lineno)
    - `from a.b import c`    -> ('a.b', lineno) — el módulo, no el símbolo
    - `from . import x`      -> ignorado (relativo, mismo paquete)
    """
    out: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module is not None:
                out.append((node.module, node.lineno))
    return out


def _matched_forbidden(module: str, forbidden: frozenset[str]) -> str | None:
    """Si `module` matchea algún prefijo de `forbidden`, retorna ese prefijo."""
    for prefix in forbidden:
        if module == prefix or module.startswith(prefix + "."):
            return prefix
    return None


def _layer_files() -> list[tuple[Path, str]]:
    """Recolecta `(archivo, capa)` para todos los .py bajo `src/collections_app/`."""
    files: list[tuple[Path, str]] = []
    if not SRC_ROOT.exists():
        return files
    for py_path in sorted(SRC_ROOT.rglob("*.py")):
        layer = _layer_of(py_path)
        if layer is None:
            continue
        files.append((py_path, layer))
    return files


def _test_id(item: tuple[Path, str]) -> str:
    py_path, layer = item
    rel = py_path.relative_to(PROJECT_ROOT).as_posix()
    return f"{layer}:{rel}"


_LAYER_FILES = _layer_files()


@pytest.mark.parametrize(
    "py_path,layer",
    _LAYER_FILES,
    ids=[_test_id(item) for item in _LAYER_FILES],
)
def test_imports_respect_layer_direction(py_path: Path, layer: str) -> None:
    """Cada archivo solo importa de capas permitidas (CLAUDE.md sec 2.1)."""
    forbidden = FORBIDDEN_BY_LAYER[layer]
    source = py_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_path))

    violations: list[str] = []
    for module, lineno in _imports_of(tree):
        prefix = _matched_forbidden(module, forbidden)
        if prefix is not None:
            rel = py_path.relative_to(PROJECT_ROOT).as_posix()
            violations.append(
                f"  {rel}:{lineno} - capa={layer!r} importa {module!r} "
                f"(prefijo prohibido: {prefix!r})"
            )

    assert not violations, (
        "Imports cross-layer detectados:\n" + "\n".join(violations)
    )


def test_all_expected_layers_have_files() -> None:
    """Sanity del harness: las 4 capas existen y al menos tienen `__init__.py`.

    Sin esto, una regresión en `_layer_of` o en la estructura del paquete
    haría que `parametrize` se quede vacío y el test pase silenciosamente.
    """
    layers_seen = {layer for _, layer in _LAYER_FILES}
    missing = EXPECTED_LAYERS - layers_seen
    assert not missing, (
        f"Capas sin archivos detectadas: {missing}. "
        f"Esto rompe el harness de tests de capas."
    )
