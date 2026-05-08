"""Genera `docs/project_structure.md` con la estructura completa del proyecto.

Características:

- **Respeta `.gitignore`**: usa `git ls-files --cached --others --exclude-standard`
  para listar exactamente los archivos que git considera versionables. Si git
  no está disponible, fallback a una lista hardcoded de directorios/extensiones.
- **Cubre todos los archivos texto del repo**, no solo `.py`. Markdown, SQL,
  TOML, YAML, JSON, scripts shell/batch, etc. se incluyen completos. Binarios
  (imágenes, .db, .pdf, .xlsx) se listan con nota.
- **Por cada archivo `.py`**: outline de clases/funciones públicas con
  signaturas + docstring de primer renglón **antes** del código completo.
- Mantiene la sección de **schema SQL + dataclasses + repositories** como
  hand-off compacto para alimentar a un LLM.

Uso:
    python scripts/generate_context.py

Sin argumentos. Output: `docs/project_structure.md` (sobreescribe).
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
SCHEMA_DIR = SRC_DIR / "collections_app" / "core" / "db" / "schema"
MODELS_DIR = SRC_DIR / "collections_app" / "core" / "models"
REPOS_DIR = SRC_DIR / "collections_app" / "core" / "repositories"
DOCS_DIR = ROOT / "docs"
OUTPUT_PATH = DOCS_DIR / "project_structure.md"

# Extensiones tratadas como texto (contenido se incluye completo).
TEXT_SUFFIXES = frozenset(
    {
        ".py",
        ".md",
        ".rst",
        ".txt",
        ".toml",
        ".cfg",
        ".ini",
        ".yml",
        ".yaml",
        ".json",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
        ".env.example",
        ".editorconfig",
        ".gitignore",
        ".gitattributes",
    }
)
# Archivos sin extensión que tratamos como texto (Makefile, LICENSE, etc.).
TEXT_NAMES = frozenset({"Makefile", "Dockerfile", "LICENSE", "README", ".gitignore"})

# Mapping de extensión → lenguaje del code fence en markdown.
LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".md": "markdown",
    ".rst": "rst",
    ".toml": "toml",
    ".cfg": "ini",
    ".ini": "ini",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".sql": "sql",
    ".sh": "bash",
    ".bat": "batch",
    ".ps1": "powershell",
    ".gitignore": "gitignore",
    ".gitattributes": "gitattributes",
    ".editorconfig": "ini",
}

# Fallback si `git` no está disponible.
FALLBACK_IGNORE_DIRS = frozenset(
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
    }
)
FALLBACK_IGNORE_SUFFIXES = frozenset({".pyc", ".pyo", ".db", ".db-journal", ".log"})


# ---------------------------------------------------------------------
# File listing (gitignore-aware)
# ---------------------------------------------------------------------


def list_repo_files() -> list[Path]:
    """Lista los archivos del repo respetando `.gitignore`.

    Usa `git ls-files --cached --others --exclude-standard`:
    - `--cached`: archivos versionados (ya en el index).
    - `--others`: archivos untracked.
    - `--exclude-standard`: excluye los matchados por `.gitignore`,
      `.git/info/exclude` y `core.excludesFile`.

    Si git no está disponible o no es un repo, fallback a un walk
    manual con la lista hardcoded de `FALLBACK_IGNORE_*`.
    """
    # Argumentos hardcoded; no hay input del usuario. `git` se busca en
    # PATH — aceptable para una herramienta de proyecto local.
    cmd = ["git", "ls-files", "--cached", "--others", "--exclude-standard"]  # noqa: S607
    try:
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return _fallback_walk()

    paths: list[Path] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        path = ROOT / line
        if path.is_file():
            paths.append(path)
    paths.sort()
    return paths


def _fallback_walk() -> list[Path]:
    """Walk manual si git no responde."""
    paths: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in FALLBACK_IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix in FALLBACK_IGNORE_SUFFIXES:
            continue
        paths.append(path)
    return paths


def relative(path: Path) -> str:
    """Path relativo al ROOT con `/` como separador (links MD válidos)."""
    return path.resolve().relative_to(ROOT).as_posix()


def is_text_file(path: Path) -> bool:
    """True si el archivo se trata como texto (contenido va al output)."""
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def language_for(path: Path) -> str:
    return LANGUAGE_BY_SUFFIX.get(path.suffix, "")


# ---------------------------------------------------------------------
# AST extractor (outline para .py)
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
    fields: list[str]
    methods: list[FunctionSummary]


@dataclass
class ModuleSummary:
    path: Path
    docstring_first_line: str | None
    classes: list[ClassSummary]
    functions: list[FunctionSummary]
    error: str | None = None


def first_line(text: str | None) -> str | None:
    if text is None:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    return stripped.splitlines()[0].strip()


def format_arg(arg: ast.arg) -> str:
    out = arg.arg
    if arg.annotation is not None:
        out += f": {ast.unparse(arg.annotation)}"
    return out


def format_signature(func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args_node = func.args
    parts: list[str] = []
    pos_args = list(args_node.posonlyargs) + list(args_node.args)
    defaults = list(args_node.defaults)
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
    return any("dataclass" in ast.unparse(dec) for dec in node.decorator_list)


def extract_dataclass_fields(node: ast.ClassDef) -> list[str]:
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
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
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
# SQL parsing (sin cambios respecto del script original)
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
    tables: dict[str, TableSchema] = {}
    indexes_by_table: dict[str, list[str]] = {}
    for path in sql_files:
        sql = path.read_text(encoding="utf-8")
        sql_no_comments = re.sub(r"--[^\n]*", "", sql)
        for match in CREATE_TABLE_RE.finditer(sql_no_comments):
            name = match.group(1)
            body = match.group(2)
            if name in tables:
                continue
            cols: list[str] = []
            fks: list[str] = []
            pk: str | None = None
            for piece in split_top_level_commas(body):
                upper = piece.upper().strip()
                if upper.startswith("PRIMARY KEY"):
                    pk = piece
                elif upper.startswith("FOREIGN KEY"):
                    fks.append(piece)
                else:
                    cols.append(piece)
            tables[name] = TableSchema(
                name=name, columns=cols, primary_key=pk, foreign_keys=fks, indexes=[]
            )
        for match in ALTER_ADD_COLUMN_RE.finditer(sql_no_comments):
            tbl_name = match.group(1)
            col_def = " ".join(match.group(2).split())
            if tbl_name in tables and col_def not in tables[tbl_name].columns:
                tables[tbl_name].columns.append(col_def)
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


def build_tree_from_files(files: list[Path]) -> list[str]:
    """Construye el árbol de directorios a partir de la lista de archivos."""
    # Agrupar por carpeta padre (relativa al ROOT).
    tree: dict[str, list[Path]] = {}
    for f in files:
        rel = relative(f)
        parts = rel.split("/")
        # Indexar bajo cada prefijo de directorio.
        for i in range(len(parts)):
            parent = "/".join(parts[:i]) if i > 0 else ""
            tree.setdefault(parent, [])
        # Asignar el archivo a su carpeta inmediata.
        parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
        tree.setdefault(parent, []).append(f)

    lines: list[str] = []
    seen_dirs: set[str] = set()

    def emit(parent: str, depth: int) -> None:
        # Carpetas hijas inmediatas + archivos hijos inmediatos en la misma vista.
        children_dirs: set[str] = set()
        children_files: list[Path] = []
        for f in files:
            rel = relative(f)
            parts = rel.split("/")
            file_parent = "/".join(parts[:-1]) if len(parts) > 1 else ""
            if file_parent == parent:
                children_files.append(f)
            elif file_parent.startswith(parent + "/" if parent else ""):
                # Inmediato: la siguiente componente.
                tail = file_parent[len(parent) + 1 :] if parent else file_parent
                next_dir = tail.split("/")[0]
                if next_dir:
                    children_dirs.add(next_dir)
        for d in sorted(children_dirs):
            full = f"{parent}/{d}" if parent else d
            if full in seen_dirs:
                continue
            seen_dirs.add(full)
            indent = "  " * depth
            lines.append(f"{indent}- **{d}/**")
            emit(full, depth + 1)
        for f in sorted(children_files, key=lambda p: p.name.lower()):
            indent = "  " * depth
            lines.append(f"{indent}- [{f.name}]({relative(f)})")

    emit("", 0)
    return lines


# ---------------------------------------------------------------------
# Per-file rendering
# ---------------------------------------------------------------------


def render_python_outline(summary: ModuleSummary) -> list[str]:
    """Outline de un .py: docstring + clases con sus métodos públicos + funciones top-level."""
    out: list[str] = []
    if summary.error:
        out.append(f"> _Error parseando AST_: `{summary.error}`")
        out.append("")
        return out
    if summary.docstring_first_line:
        out.append(f"> {summary.docstring_first_line}")
        out.append("")
    if summary.classes or summary.functions:
        out.append("**Estructura:**")
        out.append("")
        for cls in summary.classes:
            bases = f"({', '.join(cls.bases)})" if cls.bases else ""
            tag = " [@dataclass]" if cls.is_dataclass else ""
            line = f"- `class {cls.name}{bases}`{tag}"
            if cls.docstring_first_line:
                line += f" — {cls.docstring_first_line}"
            out.append(line)
            if cls.is_dataclass and cls.fields:
                for f in cls.fields:
                    out.append(f"    - `{f}`")
            for m in cls.methods:
                method_line = f"    - `{m.name}{m.signature}`"
                if m.docstring_first_line:
                    method_line += f" — {m.docstring_first_line}"
                out.append(method_line)
        for fn in summary.functions:
            line = f"- `def {fn.name}{fn.signature}`"
            if fn.docstring_first_line:
                line += f" — {fn.docstring_first_line}"
            out.append(line)
        out.append("")
    return out


def render_file_section(path: Path) -> list[str]:
    rel = relative(path)
    out: list[str] = [f"### [{rel}]({rel})", ""]

    if not is_text_file(path):
        out.append(f"_(binario: {path.suffix or '<sin extensión>'} — contenido omitido)_")
        out.append("")
        return out

    # Outline solo para .py
    if path.suffix == ".py":
        summary = summarize_module(path)
        out.extend(render_python_outline(summary))

    # Contenido completo
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        out.append(f"> **Error leyendo archivo**: {exc}")
        out.append("")
        return out
    if not source.strip():
        out.append("_(archivo vacío)_")
        out.append("")
        return out
    lang = language_for(path)
    fence_open = f"```{lang}" if lang else "```"
    safe_source = source.replace("```", "ʼʼʼ")
    out.append(fence_open)
    out.append(safe_source.rstrip())
    out.append("```")
    out.append("")
    return out


# ---------------------------------------------------------------------
# Section renderers (same spirit as before)
# ---------------------------------------------------------------------


def render_function(fn: FunctionSummary, indent: str = "") -> str:
    line = f"{indent}- `{fn.name}{fn.signature}`"
    if fn.docstring_first_line:
        line += f" — {fn.docstring_first_line}"
    return line


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
                    out.append(render_function(m))
            out.append("")
    if not found_dataclasses:
        out.append("_(sin dataclasses encontrados.)_")
        out.append("")

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
                out.append(render_function(m))
            out.append("")

    return out


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def main() -> int:
    print(f"ROOT: {ROOT}")

    files = list_repo_files()
    print(f"Archivos detectados (gitignore-aware): {len(files)}")

    # Partición por categoría para la sección 3 (contexto).
    py_files = [p for p in files if p.suffix == ".py"]
    model_files = [p for p in py_files if MODELS_DIR in p.parents]
    repo_files = [p for p in py_files if REPOS_DIR in p.parents]
    sql_files = sorted(p for p in files if p.suffix == ".sql" and SCHEMA_DIR in p.parents)

    model_modules = [summarize_module(p) for p in model_files]
    repo_modules = [summarize_module(p) for p in repo_files]
    tables = parse_sql_schema(sql_files)
    print(f"Tablas detectadas: {sorted(tables)}")

    # Build sections.
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
        "Contenido en orden: **(1)** árbol del proyecto, **(2)** estructura + "
        "contenido de cada archivo (filtrado vía `.gitignore`), **(3)** contexto "
        "(schema SQL, modelos, repositorios)."
    )
    sections.append("")

    sections.append("# 1. Estructura del proyecto")
    sections.append("")
    sections.extend(build_tree_from_files(files))
    sections.append("")

    sections.append("# 2. Archivos del proyecto")
    sections.append("")
    sections.append(
        "Por cada archivo: estructura (clases/funciones públicas en `.py`) + "
        "contenido completo. Binarios se listan con nota."
    )
    sections.append("")
    for path in files:
        sections.extend(render_file_section(path))

    sections.extend(render_context_section(tables, model_modules, repo_modules))

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"OK: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
