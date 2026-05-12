"""Genera dos artefactos de contexto del proyecto.

Outputs:

- `docs/project_structure_NN.md` (N partes, default 3): árbol del repo +
  contenido completo de cada archivo texto. Particionado por tamaño para
  que cada archivo sea pegable a una conversación de LLM.
- `docs/data_dictionary.md` (un archivo): hand-off compacto con el
  schema SQL + dataclasses + repositorios. **Sin redundancia** con
  `project_structure_NN.md` — esos ya contienen los `.py`/`.sql` completos;
  este es el resumen.

Características:

- **Respeta `.gitignore`**: usa `git ls-files --cached --others --exclude-standard`
  para listar exactamente los archivos que git considera versionables. Si git
  no está disponible, fallback a una lista hardcoded de directorios/extensiones.
- **Cubre todos los archivos texto del repo**, no solo `.py`. Markdown, SQL,
  TOML, YAML, JSON, scripts shell/batch, etc. se incluyen completos. Binarios
  (imágenes, .db, .pdf, .xlsx) se listan con nota.
- **Por cada archivo `.py`**: outline de clases/funciones públicas con
  signaturas + docstring de primer renglón **antes** del código completo.
- **Partición**: si una parte supera `--max-mb` (default 1.0 MB), N aumenta
  automáticamente hasta que el archivo más grande quede dentro del límite.

Uso:
    python scripts/generate_context.py                    # 3 partes
    python scripts/generate_context.py --parts 5         # forzar 5 partes
    python scripts/generate_context.py --max-mb 0.7      # techo 700 KB/parte

`docs/project_structure.md` antiguo (monolítico) y huérfanos `_NN.md`
de runs previos se borran.
"""

from __future__ import annotations

import argparse
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
# Output path stem para las partes: docs/project_structure_NN.md.
OUTPUT_STEM = "project_structure"
LEGACY_OUTPUT = DOCS_DIR / "project_structure.md"
DATA_DICT_OUTPUT = DOCS_DIR / "data_dictionary.md"

DEFAULT_PARTS = 3
DEFAULT_MAX_MB = 1.0
# Tope duro para evitar splits absurdos si auto-grow se descontrola.
MAX_PARTS_CEILING = 30

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
    out: list[str] = ["# Schema, modelos y repositorios", ""]

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
# Partition helpers
# ---------------------------------------------------------------------


def _block_bytes(block: list[str]) -> int:
    """Tamaño aproximado en bytes de un bloque de líneas (incluye \\n)."""
    return sum(len(line) + 1 for line in block)


def split_into_parts(
    file_blocks: list[tuple[Path, list[str]]],
    num_parts: int,
) -> list[list[tuple[Path, list[str]]]]:
    """Reparte `file_blocks` en `num_parts` listas balanceadas por tamaño.

    Greedy con target = total / num_parts. Cuando agregar el siguiente
    bloque hace que la parte actual supere el target — y todavía quedan
    partes por usar — saltamos a la siguiente. Esto mantiene el orden
    original de los archivos (importante para la legibilidad del output)
    y evita partir un archivo entre dos partes.
    """
    if num_parts <= 1:
        return [list(file_blocks)]
    sizes = [_block_bytes(lines) for _, lines in file_blocks]
    total = sum(sizes)
    target = total / num_parts if num_parts else total

    parts: list[list[tuple[Path, list[str]]]] = [[] for _ in range(num_parts)]
    current = 0
    current_size = 0
    for entry, size in zip(file_blocks, sizes, strict=True):
        # Saltar a la siguiente parte solo si la actual ya tiene algo
        # (evita partes vacías cuando el primer archivo supera el target).
        if current_size + size > target and current < num_parts - 1 and parts[current]:
            current += 1
            current_size = 0
        parts[current].append(entry)
        current_size += size
    return parts


def split_with_auto_grow(
    file_blocks: list[tuple[Path, list[str]]],
    base_parts: int,
    max_bytes: int,
    overhead_per_part: int,
) -> list[list[tuple[Path, list[str]]]]:
    """Reparte en `base_parts` y aumenta N si alguna parte excede `max_bytes`.

    `overhead_per_part` es el costo fijo del header/navegación que se va a
    prepender a cada parte; se suma al tamaño de los blocks para que el
    cómputo del techo sea fiel al output final.
    """
    n = max(1, base_parts)
    while True:
        parts = split_into_parts(file_blocks, n)
        max_size = max(
            (overhead_per_part + sum(_block_bytes(lines) for _, lines in part)) for part in parts
        )
        if max_size <= max_bytes:
            return parts
        if n >= len(file_blocks) or n >= MAX_PARTS_CEILING:
            print(
                f"WARN: alcanzado el tope de partes ({n}); la mayor sigue "
                f"en {max_size/1024:.0f} KB > {max_bytes/1024:.0f} KB target."
            )
            return parts
        n += 1


def _navigation_block(part_idx: int, num_parts: int) -> list[str]:
    """Líneas de navegación entre partes: 'Parte 2 de 3' + links."""
    out: list[str] = [f"> **Parte {part_idx + 1} de {num_parts}**"]
    links = []
    for i in range(num_parts):
        name = f"{OUTPUT_STEM}_{i + 1:02d}.md"
        if i == part_idx:
            links.append(f"**{i + 1}**")
        else:
            links.append(f"[{i + 1}]({name})")
    out.append(">")
    out.append("> Navegación: " + " · ".join(links))
    out.append("")
    return out


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument(
        "--parts",
        type=int,
        default=DEFAULT_PARTS,
        help=f"Cantidad mínima de partes a generar (default {DEFAULT_PARTS}).",
    )
    parser.add_argument(
        "--max-mb",
        type=float,
        default=DEFAULT_MAX_MB,
        help=(
            f"Techo de tamaño por parte en MB (default {DEFAULT_MAX_MB}). "
            "Si alguna parte excede este límite, se aumenta N "
            "automáticamente hasta cumplirlo (o hasta el tope duro)."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    print(f"ROOT: {ROOT}")
    print(f"Args: parts>={args.parts}, max_mb={args.max_mb}")

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

    # Bloques de la §1 (árbol) y §3 (contexto compacto) — van enteros en la
    # primera y última parte respectivamente.
    tree_block: list[str] = ["# 1. Estructura del proyecto", ""]
    tree_block.extend(build_tree_from_files(files))
    tree_block.append("")

    # Bloques de §2 (uno por archivo). Pre-rendereados para que la
    # partición sea por tamaño real del output, no por estimación.
    file_blocks: list[tuple[Path, list[str]]] = [(p, render_file_section(p)) for p in files]

    # Tamaño aproximado del header/navegación por parte (para que el
    # auto-grow estime correctamente el techo del archivo final).
    overhead_estimate = 600

    parts = split_with_auto_grow(
        file_blocks,
        base_parts=args.parts,
        max_bytes=int(args.max_mb * 1024 * 1024),
        overhead_per_part=overhead_estimate,
    )
    num_parts = len(parts)
    print(f"Generando {num_parts} parte(s).")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Borrar el archivo monolítico anterior si quedó del flow viejo. Y los
    # _NN.md huérfanos que pueda haber dejado un run previo con más partes.
    if LEGACY_OUTPUT.exists():
        LEGACY_OUTPUT.unlink()
        print(f"  borrado legacy {LEGACY_OUTPUT.name}")
    for stale in sorted(DOCS_DIR.glob(f"{OUTPUT_STEM}_*.md")):
        m = re.match(rf"^{re.escape(OUTPUT_STEM)}_(\d+)\.md$", stale.name)
        if m and int(m.group(1)) > num_parts:
            stale.unlink()
            print(f"  borrado stale {stale.name}")

    for idx, part_blocks in enumerate(parts):
        out: list[str] = []
        out.append(f"# Contexto del Proyecto Collections — Parte {idx + 1} de {num_parts}")
        out.append("")
        out.append(
            "> Generado automáticamente por "
            "[`scripts/generate_context.py`](../scripts/generate_context.py). "
            "**No editar a mano** — se sobreescribe."
        )
        out.append("")
        out.extend(_navigation_block(idx, num_parts))

        if idx == 0:
            out.append(
                "Contenido en orden: **(1)** árbol del proyecto, **(2)** estructura + "
                "contenido de cada archivo (filtrado vía `.gitignore`, repartido "
                "entre las partes). Para el hand-off compacto de schema SQL + "
                "dataclasses + repositorios, ver `data_dictionary.md` (artefacto "
                "aparte)."
            )
            out.append("")
            out.extend(tree_block)

        out.append(f"# 2. Archivos del proyecto — parte {idx + 1}/{num_parts}")
        out.append("")
        out.append(
            "Por cada archivo: estructura (clases/funciones públicas en `.py`) + "
            "contenido completo. Binarios se listan con nota."
        )
        out.append("")
        for _path, lines in part_blocks:
            out.extend(lines)

        path = DOCS_DIR / f"{OUTPUT_STEM}_{idx + 1:02d}.md"
        path.write_text("\n".join(out), encoding="utf-8")
        size_kb = path.stat().st_size / 1024
        print(f"  OK: {path.name} ({size_kb:.0f} KB, {len(part_blocks)} archivos)")

    # data_dictionary.md: hand-off compacto del schema + modelos + repos.
    # Vive en un archivo separado para no inflar `project_structure_NN.md`
    # con contenido que ya está disponible (los .sql y .py completos ya
    # aparecen en §2 de las partes).
    dd_lines: list[str] = []
    dd_lines.append("# Data Dictionary — Collections")
    dd_lines.append("")
    dd_lines.append(
        "> Generado automáticamente por "
        "[`scripts/generate_context.py`](../scripts/generate_context.py). "
        "**No editar a mano** — se sobreescribe."
    )
    dd_lines.append("")
    dd_lines.append(
        "Hand-off compacto del contexto persistente: schema SQL, dataclasses "
        "de `core/models/` y API pública de `core/repositories/`. Pensado para "
        "alimentar a una conversación nueva de LLM sin necesidad de subir el "
        "`project_structure_NN.md` completo."
    )
    dd_lines.append("")
    dd_lines.extend(render_context_section(tables, model_modules, repo_modules))
    DATA_DICT_OUTPUT.write_text("\n".join(dd_lines), encoding="utf-8")
    dd_kb = DATA_DICT_OUTPUT.stat().st_size / 1024
    print(f"  OK: {DATA_DICT_OUTPUT.name} ({dd_kb:.0f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
