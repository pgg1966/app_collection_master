"""Test de arquitectura sec 2.3 — contratos de retorno de los repos.

Métodos públicos de cualquier subclase de `BaseRepository` retornan
**únicamente** uno de:

- Un dataclass de `core/models/` (incluyendo `core/models/aggregates/`).
- `<Model> | None`.
- `list[<Model>]`.
- `bool` (existencia / éxito de delete).
- `int` (counts agregados).
- `None` (literal — solo para métodos que no retornan).

Prohibido: `tuple[...]`, `dict[...]`, `Any`, `sqlite3.Row`, `str`,
`list[str]`, etc. — todos detectados parseando la anotación con `ast`.
"""

from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src" / "collections_app"
MODELS_DIR = SRC_ROOT / "core" / "models"
REPOS_DIR = SRC_ROOT / "core" / "repositories"

# Tipos primitivos permitidos como retorno crudo.
ALLOWED_PRIMITIVES = frozenset({"bool", "int"})


def _model_class_names() -> frozenset[str]:
    """Set de nombres de clase (dataclasses) en core/models/ y aggregates/."""
    names: set[str] = set()
    for py_path in MODELS_DIR.rglob("*.py"):
        if py_path.name == "__init__.py":
            continue
        tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                names.add(node.name)
    return frozenset(names)


_MODEL_NAMES = _model_class_names()


def _is_none_literal(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _is_allowed_atom(node: ast.expr) -> bool:
    """`bool`, `int`, `None`, o un nombre de modelo registrado."""
    if _is_none_literal(node):
        return True
    if isinstance(node, ast.Name):
        return node.id in ALLOWED_PRIMITIVES or node.id in _MODEL_NAMES
    return False


def _is_model_or_optional_model(node: ast.expr) -> bool:
    """`<Model>` o `<Model> | None` (en cualquier orden)."""
    if isinstance(node, ast.Name) and node.id in _MODEL_NAMES:
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = node.left, node.right
        # Model | None
        if isinstance(left, ast.Name) and left.id in _MODEL_NAMES and _is_none_literal(right):
            return True
        # None | Model
        if _is_none_literal(left) and isinstance(right, ast.Name) and right.id in _MODEL_NAMES:
            return True
    return False


def _is_list_of_model(node: ast.expr) -> bool:
    """`list[<Model>]`."""
    if not (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)):
        return False
    if node.value.id != "list":
        return False
    inner = node.slice
    return isinstance(inner, ast.Name) and inner.id in _MODEL_NAMES


def _is_allowed_return(node: ast.expr) -> bool:
    """Combinación de las formas permitidas."""
    return _is_allowed_atom(node) or _is_model_or_optional_model(node) or _is_list_of_model(node)


def _annotation_str(node: ast.expr) -> str:
    """Render legible de la anotación para mensajes de error."""
    try:
        return ast.unparse(node)
    except AttributeError:  # pragma: no cover — Python < 3.9
        return "<unparseable>"


def _is_subclass_of_base_repository(class_node: ast.ClassDef) -> bool:
    """`class X(BaseRepository)` directo."""
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id == "BaseRepository":
            return True
    return False


def _public_methods(class_node: ast.ClassDef) -> list[ast.FunctionDef]:
    return [
        node
        for node in class_node.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]


def _collect_violations() -> list[str]:
    """Walk de core/repositories/*.py y verificación de cada método público."""
    violations: list[str] = []
    for py_path in sorted(REPOS_DIR.glob("*.py")):
        if py_path.name in {"__init__.py", "base.py"}:
            continue
        tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=str(py_path))
        rel = py_path.relative_to(PROJECT_ROOT).as_posix()
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not _is_subclass_of_base_repository(node):
                continue
            for method in _public_methods(node):
                if method.returns is None:
                    violations.append(
                        f"{rel}:{method.lineno} - {node.name}.{method.name} "
                        f"sin anotación de retorno"
                    )
                    continue
                if not _is_allowed_return(method.returns):
                    violations.append(
                        f"{rel}:{method.lineno} - {node.name}.{method.name} "
                        f"retorna '{_annotation_str(method.returns)}' "
                        f"(no está en el set permitido: bool, int, None, "
                        f"<Model>, <Model> | None, list[<Model>])"
                    )
    return violations


def test_repo_methods_return_only_allowed_types() -> None:
    violations = _collect_violations()
    assert not violations, "Repos con retornos prohibidos:\n" + "\n".join(violations)


def test_at_least_one_repo_was_inspected() -> None:
    """Sanity: si la estructura cambia y _collect_violations no encuentra
    ningún archivo, el test arriba pasaría vacuamente. Este harness lo evita.
    """
    repo_files = [p for p in REPOS_DIR.glob("*.py") if p.name not in {"__init__.py", "base.py"}]
    assert len(repo_files) >= 1, "No se encontró ningún repo para inspeccionar"
