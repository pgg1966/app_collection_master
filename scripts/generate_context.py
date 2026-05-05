"""Genera documentación de contexto del proyecto para retomarla en una conversación nueva.

Produce UN ÚNICO archivo en `docs/project_structure.md` con tres
secciones, en este orden:

1. **Estructura**: árbol completo del proyecto (links a cada archivo).
2. **Código fuente**: contenido COMPLETO de cada archivo `.py` (con el
   path como encabezado y el código dentro de un bloque ```python).
3. **Contexto**: schema SQL parseado de las migraciones, modelos
   (dataclasses) y métodos públicos de cada Repository. Pensado como
   resumen compacto para alimentar a un LLM.

Uso:
    python scripts/generate_context.py

Sin argumentos (toma todo del root del proyecto). El script no requiere
dependencias externas: solo `ast` + regex de la stdlib.
"""

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
TESTS_DIR = ROOT / "tests"
SCRIPTS_DIR = ROOT / "scripts"
SCHEMA_DIR = SRC_DIR / "collections_app" / "core" / "db" / "schema"
MODELS_DIR = SRC_DIR / "collections_app" / "core" / "models"
REPOS_DIR = SRC_DIR / "collections_app" / "core" / "repositories"
DOCS_DIR = ROOT / "docs"

# Directorios y patrones a ignorar al armar el árbol.
IGNORE_DIRS = frozenset(
    {
        "__pycache__",
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".git",
        "node_modules",
        "build",
        "dist",
        "htmlcov",
        "data",
        ".idea",
        ".vscode",
        "collections.egg-info",
    }
)
IGNORE_FILE_SUFFIXES = frozenset({".pyc", ".pyo", ".db", ".db-journal", ".log"})
IGNORE_FILES = frozenset({".DS_Store"})

# Solo incluimos estos roots en el árbol y el detalle.
INCLUDE_ROOTS = (SRC_DIR, TESTS_DIR, SCRIPTS_DIR, DOCS_DIR)


# ---------------------------------------------------------------------
# Modelos internos del extractor
# ---------------------------------------------------------------------


@dataclass
class FunctionSummary:
    name: str
    signature: str
    docstring_first_line: str | None


@dataclass
class ClassSummary:
    name: str
    bases: list[str]
    is_dataclass: bool
    docstring_first_line: str | None
    fields: list[str]  # solo para dataclasses
    methods: list[FunctionSummary]


@dataclass
class ModuleSummary:
    path: Path
    docstring_first_line: str | None
    classes: list[ClassSummary]
    functions: list[FunctionSummary]
    error: str | None = None


# ---------------------------------------------------------------------
# Walking
# ---------------------------------------------------------------------


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix in IGNORE_FILE_SUFFIXES:
        return True
    return path.name in IGNORE_FILES


def walk_relevant_files(root: Path) -> list[Path]:
    """Lista todos los archivos no-ignorados bajo `root`, ordenados."""
    files: list[Path] = []
    if not root.exists():
        return files
    for path in sorted(root.rglob("*")):
        if path.is_file() and not is_ignored(path):
            files.append(path)
    return files


def relative(path: Path) -> str:
    """Devuelve el path relativo al ROOT con / como separador."""
    return path.resolve().relative_to(ROOT).as_posix()


def first_line(text: str | None) -> str | None:
    if text is None:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    return stripped.splitlines()[0].strip()


# ---------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------


def format_arg(arg: ast.arg) -> str:
    out = arg.arg
    if arg.annotation is not None:
        out += f": {ast.unparse(arg.annotation)}"
    return out


def format_signature(func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Reconstruye la signatura como texto: `(arg1: T, arg2=default) -> R`."""
    args_node = func.args
    parts: list[str] = []

    # posicionales (incluye self/cls)
    pos_args = list(args_node.posonlyargs) + list(args_node.args)
    defaults = list(args_node.defaults)
    # padding de defaults
    pad = [None] * (len(pos_args) - len(defaults)) + defaults
    for arg, default in zip(pos_args, pad, strict=False):
        s = format_arg(arg)
        if default is not None:
            s += f" = {ast.unparse(default)}"
        parts.append(s)

    if args_node.vararg is not None:
        parts.append(f"*{format_arg(args_node.vararg)}")
    elif args_node.kwonlyargs:
        parts.append("*")

    for arg, default in zip(args_node.kwonlyargs, args_node.kw_defaults, strict=True):
        s = format_arg(arg)
        if default is not None:
            s += f" = {ast.unparse(default)}"
        parts.append(s)

    if args_node.kwarg is not None:
        parts.append(f"**{format_arg(args_node.kwarg)}")

    sig = f"({', '.join(parts)})"
    if func.returns is not None:
        sig += f" -> {ast.unparse(func.returns)}"
    return sig


def has_dataclass_decorator(node: ast.ClassDef) -> bool:
    for dec in node.decorator_list:
        text = ast.unparse(dec)
        if "dataclass" in text:
            return True
    return False


def extract_dataclass_fields(node: ast.ClassDef) -> list[str]:
    """Retorna los nombres de campo (con tipo) de una @dataclass."""
    fields: list[str] = []
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            type_str = ast.unparse(item.annotation)
            fields.append(f"{item.target.id}: {type_str}")
    return fields


def is_public(name: str) -> bool:
    return not name.startswith("_") or name == "__init__"


def summarize_module(path: Path) -> ModuleSummary:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        return ModuleSummary(path, None, [], [], error=str(exc))

    classes: list[ClassSummary] = []
    functions: list[FunctionSummary] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            is_dc = has_dataclass_decorator(node)
            fields = extract_dataclass_fields(node) if is_dc else []
            methods: list[FunctionSummary] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef) and is_public(
                    item.name
                ):
                    methods.append(
                        FunctionSummary(
                            name=item.name,
                            signature=format_signature(item),
                            docstring_first_line=first_line(ast.get_docstring(item)),
                        )
                    )
            classes.append(
                ClassSummary(
                    name=node.name,
                    bases=[ast.unparse(b) for b in node.bases],
                    is_dataclass=is_dc,
                    docstring_first_line=first_line(ast.get_docstring(node)),
                    fields=fields,
                    methods=methods,
                )
            )
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and not node.name.startswith(
            "_"
        ):
            functions.append(
                FunctionSummary(
                    name=node.name,
                    signature=format_signature(node),
                    docstring_first_line=first_line(ast.get_docstring(node)),
                )
            )

    return ModuleSummary(
        path=path,
        docstring_first_line=first_line(ast.get_docstring(tree)),
        classes=classes,
        functions=functions,
    )


# ---------------------------------------------------------------------
# SQL parsing
# ---------------------------------------------------------------------


@dataclass
class TableSchema:
    name: str
    columns: list[str]
    primary_key: str | None
    foreign_keys: list[str]
    indexes: list[str]


CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)
CREATE_INDEX_RE = re.compile(
    r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(\w+)",
    re.IGNORECASE,
)
ALTER_ADD_COLUMN_RE = re.compile(
    r"ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(.+?);",
    re.IGNORECASE | re.DOTALL,
)


def split_top_level_commas(body: str) -> list[str]:
    """Divide `col1, col2, FOREIGN KEY (a) REFERENCES x(b), …` por comas top-level.

    Ignora las comas que están adentro de paréntesis (FOREIGN KEY tiene paréntesis).
    """
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def parse_sql_schema(sql_files: list[Path]) -> dict[str, TableSchema]:
    """Combina múltiples migraciones y retorna `{tabla: TableSchema}`."""
    tables: dict[str, TableSchema] = {}
    indexes_by_table: dict[str, list[str]] = {}

    for path in sql_files:
        sql = path.read_text(encoding="utf-8")
        # Quitar comentarios `-- …` para no confundir el regex.
        sql_no_comments = re.sub(r"--[^\n]*", "", sql)

        # Tablas
        for match in CREATE_TABLE_RE.finditer(sql_no_comments):
            name = match.group(1)
            body = match.group(2)
            if name in tables:
                continue  # primera definición gana; las migraciones futuras alteran columnas
            cols: list[str] = []
            fks: list[str] = []
            pk: str | None = None
            for piece in split_top_level_commas(body):
                upper = piece.upper().strip()
                if upper.startswith("PRIMARY KEY"):
                    pk = piece
                elif upper.startswith("FOREIGN KEY"):
                    fks.append(piece)
                elif upper.startswith("CHECK") or upper.startswith("UNIQUE"):
                    # restricciones extra: las pegamos como nota de columna virtual
                    cols.append(piece)
                else:
                    cols.append(piece)
            tables[name] = TableSchema(
                name=name, columns=cols, primary_key=pk, foreign_keys=fks, indexes=[]
            )

        # ALTER TABLE … ADD COLUMN
        for match in ALTER_ADD_COLUMN_RE.finditer(sql_no_comments):
            tbl_name = match.group(1)
            col_def = " ".join(match.group(2).split())  # normalizar whitespace
            if tbl_name in tables and col_def not in tables[tbl_name].columns:
                tables[tbl_name].columns.append(col_def)

        # Índices
        for match in CREATE_INDEX_RE.finditer(sql_no_comments):
            idx_name = match.group(1)
            tbl_name = match.group(2)
            indexes_by_table.setdefault(tbl_name, []).append(idx_name)

    for tbl_name, idx_list in indexes_by_table.items():
        if tbl_name in tables:
            tables[tbl_name].indexes = idx_list

    return tables


# ---------------------------------------------------------------------
# Tree rendering
# ---------------------------------------------------------------------


def build_tree_lines(roots: list[Path]) -> list[str]:
    """Genera el árbol como lista de líneas Markdown.

    Cada archivo `.py` es un link relativo a su path. Los directorios
    se muestran como bullets sin link.
    """
    lines: list[str] = []

    def walk(node: Path, depth: int) -> None:
        rel = relative(node)
        indent = "  " * depth
        if node.is_dir():
            lines.append(f"{indent}- **{node.name}/**")
            children = sorted(
                [p for p in node.iterdir() if not is_ignored(p)],
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
            for child in children:
                walk(child, depth + 1)
        else:
            lines.append(f"{indent}- [{node.name}]({rel})")

    for root in roots:
        if root.exists():
            walk(root, 0)

    # Archivos sueltos en la raíz (pyproject.toml, .gitignore, README, etc.)
    root_files = sorted(
        [
            p
            for p in ROOT.iterdir()
            if p.is_file() and not is_ignored(p) and p.suffix not in {".py", ".md"}
        ],
        key=lambda p: p.name.lower(),
    )
    if root_files:
        lines.append("")
        lines.append("**Archivos sueltos en raíz:**")
        for p in root_files:
            lines.append(f"- [{p.name}]({relative(p)})")

    return lines


# ---------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------


def render_function(fn: FunctionSummary, indent: str = "  ") -> str:
    line = f"{indent}- `{fn.name}{fn.signature}`"
    if fn.docstring_first_line:
        line += f" — {fn.docstring_first_line}"
    return line


def render_class(cls: ClassSummary) -> list[str]:
    out: list[str] = []
    bases = f"({', '.join(cls.bases)})" if cls.bases else ""
    tag = " [@dataclass]" if cls.is_dataclass else ""
    line = f"- **`class {cls.name}{bases}`**{tag}"
    if cls.docstring_first_line:
        line += f" — {cls.docstring_first_line}"
    out.append(line)
    if cls.is_dataclass and cls.fields:
        out.append("  - Campos:")
        for f in cls.fields:
            out.append(f"    - `{f}`")
    if cls.methods:
        out.append("  - Métodos:")
        for m in cls.methods:
            out.append(render_function(m, indent="    "))
    return out


def render_module_full_source(path: Path) -> list[str]:
    """Devuelve el path como header + el contenido completo del archivo en un code block."""
    rel = relative(path)
    out: list[str] = [f"### [{rel}]({rel})", ""]
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        out.append(f"> **Error leyendo archivo**: {exc}")
        return out
    if not source.strip():
        out.append("_(archivo vacío)_")
        return out
    out.append("```python")
    # Reemplazar fences ``` que pudieran estar dentro del código (raro pero posible)
    # para no romper el bloque markdown.
    safe_source = source.replace("```", "ʼʼʼ")
    out.append(safe_source.rstrip())
    out.append("```")
    return out


def render_tree_section() -> list[str]:
    out: list[str] = ["# 1. Estructura del proyecto", ""]
    out.extend(build_tree_lines(list(INCLUDE_ROOTS)))
    out.append("")
    return out


def render_source_section(py_files: list[Path]) -> list[str]:
    out: list[str] = ["# 2. Código fuente por archivo `.py`", ""]
    out.append(
        "El path de cada sección es un link al archivo real. El bloque de "
        "código contiene el contenido completo del módulo."
    )
    out.append("")
    for path in py_files:
        out.extend(render_module_full_source(path))
        out.append("")
    return out


def render_context_section(
    tables: dict[str, TableSchema],
    model_modules: list[ModuleSummary],
    repo_modules: list[ModuleSummary],
) -> list[str]:
    out: list[str] = ["# 3. Contexto (schema, modelos, repositorios)", ""]
    out.append(
        "Resumen compacto del schema SQL, los dataclasses de `core/models/` "
        "y la API pública de los Repository. Pensado como hand-off para "
        "una conversación nueva."
    )
    out.append("")

    # Schema SQL
    out.append("## Schema SQL")
    out.append("")
    if not tables:
        out.append("_(no se encontró ninguna tabla en `db/schema/`.)_")
        out.append("")
    else:
        for name in sorted(tables):
            tbl = tables[name]
            out.append(f"### Tabla `{name}`")
            out.append("")
            for col in tbl.columns:
                out.append(f"- `{col}`")
            if tbl.primary_key:
                out.append(f"- _{tbl.primary_key}_")
            if tbl.foreign_keys:
                out.append("")
                out.append("**Foreign keys:**")
                for fk in tbl.foreign_keys:
                    out.append(f"- `{fk}`")
            if tbl.indexes:
                out.append("")
                out.append("**Índices:** " + ", ".join(f"`{i}`" for i in tbl.indexes))
            out.append("")

    # Modelos
    out.append("## Modelos (dataclasses en `core/models/`)")
    out.append("")
    found_dataclasses = False
    for mod in model_modules:
        for cls in mod.classes:
            if not cls.is_dataclass:
                continue
            found_dataclasses = True
            rel = relative(mod.path)
            out.append(f"### `{cls.name}` — [{rel}]({rel})")
            out.append("")
            if cls.docstring_first_line:
                out.append(f"> {cls.docstring_first_line}")
                out.append("")
            for f in cls.fields:
                out.append(f"- `{f}`")
            if cls.methods:
                out.append("")
                out.append("**Métodos:**")
                for m in cls.methods:
                    out.append(render_function(m, indent=""))
            out.append("")
    if not found_dataclasses:
        out.append("_(sin dataclasses encontrados.)_")
        out.append("")

    # Repositorios
    out.append("## Repositorios (`core/repositories/`)")
    out.append("")
    out.append(
        "Una clase por tabla. Las repos NO crean conexión, la reciben "
        "(`__init__(conn)`). Los queries devuelven instancias de `core/models/`."
    )
    out.append("")
    for mod in repo_modules:
        for cls in mod.classes:
            if not cls.name.endswith("Repository"):
                continue
            rel = relative(mod.path)
            out.append(f"### `{cls.name}` — [{rel}]({rel})")
            out.append("")
            if cls.docstring_first_line:
                out.append(f"> {cls.docstring_first_line}")
                out.append("")
            out.append("**API pública:**")
            for m in cls.methods:
                out.append(render_function(m, indent=""))
            out.append("")

    return out


def write_project_context(
    py_files: list[Path],
    tables: dict[str, TableSchema],
    model_modules: list[ModuleSummary],
    repo_modules: list[ModuleSummary],
) -> Path:
    """Escribe `docs/project_structure.md` con estructura + código + contexto."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DIR / "project_structure.md"

    sections: list[str] = []
    sections.append("# Contexto del Proyecto Collections")
    sections.append("")
    sections.append(
        "> Generado automáticamente por "
        "[`scripts/generate_context.py`](../scripts/generate_context.py). "
        "**No editar a mano** — se sobreescribe."
    )
    sections.append("")
    sections.append(
        "Contenido en orden: **(1)** árbol del proyecto, **(2)** código "
        "completo de cada `.py`, **(3)** contexto (schema SQL, modelos, "
        "repositorios)."
    )
    sections.append("")

    sections.extend(render_tree_section())
    sections.extend(render_source_section(py_files))
    sections.extend(render_context_section(tables, model_modules, repo_modules))

    out_path.write_text("\n".join(sections), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> int:
    print(f"ROOT: {ROOT}")
    py_files: list[Path] = []
    for root in INCLUDE_ROOTS:
        for path in walk_relevant_files(root):
            if path.suffix == ".py":
                py_files.append(path)
    print(f"Encontrados {len(py_files)} archivos .py")

    # Para el data_dictionary necesitamos parsear los .py de models/repos.
    model_files = [p for p in py_files if MODELS_DIR in p.parents]
    repo_files = [p for p in py_files if REPOS_DIR in p.parents]
    model_modules = [summarize_module(p) for p in model_files]
    repo_modules = [summarize_module(p) for p in repo_files]

    sql_files = sorted(SCHEMA_DIR.glob("*.sql"))
    print(f"Migraciones SQL: {[p.name for p in sql_files]}")
    tables = parse_sql_schema(sql_files)
    print(f"Tablas detectadas: {sorted(tables)}")

    out_path = write_project_context(py_files, tables, model_modules, repo_modules)
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
