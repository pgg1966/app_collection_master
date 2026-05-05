# Contexto del Proyecto Collections

> Generado automáticamente por [`scripts/generate_context.py`](../scripts/generate_context.py). **No editar a mano** — se sobreescribe.

Contenido en orden: **(1)** árbol del proyecto, **(2)** código completo de cada `.py`, **(3)** contexto (schema SQL, modelos, repositorios).

# 1. Estructura del proyecto

- **src/**
  - **collections_app/**
    - **core/**
      - **db/**
        - **schema/**
          - [.gitkeep](src/collections_app/core/db/schema/.gitkeep)
        - [__init__.py](src/collections_app/core/db/__init__.py)
        - [connection.py](src/collections_app/core/db/connection.py)
        - [migrator.py](src/collections_app/core/db/migrator.py)
      - **models/**
        - [__init__.py](src/collections_app/core/models/__init__.py)
      - **repositories/**
        - [__init__.py](src/collections_app/core/repositories/__init__.py)
      - **utils/**
        - [__init__.py](src/collections_app/core/utils/__init__.py)
        - [paths.py](src/collections_app/core/utils/paths.py)
      - [__init__.py](src/collections_app/core/__init__.py)
    - **services/**
      - [__init__.py](src/collections_app/services/__init__.py)
    - **views/**
      - [__init__.py](src/collections_app/views/__init__.py)
    - [__init__.py](src/collections_app/__init__.py)
- **scripts/**
  - [clean_csv.py](scripts/clean_csv.py)
  - [generate_context.py](scripts/generate_context.py)
- **docs/**
  - **reference/**
    - **prompts refactorization/**
      - [00_bootstrap_repo_v02.md](docs/reference/prompts refactorization/00_bootstrap_repo_v02.md)
      - [01_schema_modelos_repos.md](docs/reference/prompts refactorization/01_schema_modelos_repos.md)
      - [02_services_y_vista_preservada.md](docs/reference/prompts refactorization/02_services_y_vista_preservada.md)
      - [03_ui_minima_e2e.md](docs/reference/prompts refactorization/03_ui_minima_e2e.md)
      - [04_csvs_y_paridad.md](docs/reference/prompts refactorization/04_csvs_y_paridad.md)
      - [CLAUDE.md](docs/reference/prompts refactorization/CLAUDE.md)
      - [README.md](docs/reference/prompts refactorization/README.md)
    - [cards_adrenalyne.csv](docs/reference/cards_adrenalyne.csv)
    - [cards_FIFA_WC_2026_sticker_final.csv](docs/reference/cards_FIFA_WC_2026_sticker_final.csv)
    - [Clave api custom search.txt](docs/reference/Clave api custom search.txt)
    - [codes_adrenalyne.csv](docs/reference/codes_adrenalyne.csv)
    - [codes_FIFA_WC_2026_sticker_final.csv](docs/reference/codes_FIFA_WC_2026_sticker_final.csv)
    - [Deuda tecnica collections.docx](docs/reference/Deuda tecnica collections.docx)
    - [httpsgithub.compgg1966app_collectio.txt](docs/reference/httpsgithub.compgg1966app_collectio.txt)
    - [~$uda tecnica collections.docx](docs/reference/~$uda tecnica collections.docx)

**Archivos sueltos en raíz:**
- [.coverage](.coverage)
- [.gitignore](.gitignore)
- [Album_Adrenalyne_XL_FIFA_WC_2026_2026-05-03.pdf](Album_Adrenalyne_XL_FIFA_WC_2026_2026-05-03.pdf)
- [diagnostico.txt](diagnostico.txt)
- [MiAlbum_Adrenalyne_XL_FIFA_WC_2026_2026-05-04 1.colexchange](MiAlbum_Adrenalyne_XL_FIFA_WC_2026_2026-05-04 1.colexchange)
- [MiAlbum_Adrenalyne_XL_FIFA_WC_2026_2026-05-04.colexchange](MiAlbum_Adrenalyne_XL_FIFA_WC_2026_2026-05-04.colexchange)
- [pyproject.toml](pyproject.toml)

# 2. Código fuente por archivo `.py`

El path de cada sección es un link al archivo real. El bloque de código contiene el contenido completo del módulo.

### [src/collections_app/__init__.py](src/collections_app/__init__.py)

```python
"""collections_app — gestión de colecciones de cards/cromos (v0.2.0)."""

__version__ = "0.2.0"
```

### [src/collections_app/core/__init__.py](src/collections_app/core/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/db/__init__.py](src/collections_app/core/db/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/db/connection.py](src/collections_app/core/db/connection.py)

```python
"""Manejo de conexiones SQLite."""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


def create_connection(db_path: Path | str) -> sqlite3.Connection:
    """Crea una conexión SQLite con WAL y FKs activadas.

    Args:
        db_path: path al archivo de DB. Usar ":memory:" para tests.

    Returns:
        Conexión configurada.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if str(db_path) != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL")
    logger.debug("Conexión creada a %s", db_path)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Context manager para transacciones con rollback automático."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        logger.exception("Rollback de transacción por excepción")
        raise
```

### [src/collections_app/core/db/migrator.py](src/collections_app/core/db/migrator.py)

```python
"""Sistema simple de migraciones de schema.

Las migraciones viven en `core/db/schema/`, numeradas `NNN_*.sql`.
Cada migración debe insertar su propio `INSERT INTO schema_version`
con la versión correspondiente; el migrator verifica que efectivamente
quedó registrada antes de continuar.

Reglas (CLAUDE.md sec 2.7):
- Migraciones inmutables: una vez aplicadas en cualquier entorno, no se editan.
- Idempotentes: correrlas dos veces no debe fallar.
- En transacción: cada `.sql` se aplica con `executescript`, lo cual
  envuelve todo el archivo en una transacción implícita de SQLite.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

from collections_app.core.utils.paths import get_schema_dir

logger = logging.getLogger(__name__)

MIGRATION_FILENAME_PATTERN = re.compile(r"^(\d{3})_.*\.sql$")


def _list_migration_files(schema_dir: Path) -> list[tuple[int, Path]]:
    """Lista las migraciones disponibles, ordenadas por versión."""
    migrations: list[tuple[int, Path]] = []
    for path in schema_dir.glob("*.sql"):
        match = MIGRATION_FILENAME_PATTERN.match(path.name)
        if match:
            migrations.append((int(match.group(1)), path))
    return sorted(migrations, key=lambda x: x[0])


def _get_current_version(conn: sqlite3.Connection) -> int:
    """Retorna la versión actual del schema, o 0 si la tabla no existe."""
    try:
        row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
        version: int = row["v"] if row and row["v"] is not None else 0
        return version
    except sqlite3.OperationalError:
        return 0


def run_migrations(conn: sqlite3.Connection, schema_dir: Path | None = None) -> int:
    """Aplica todas las migraciones pendientes.

    Args:
        conn: conexión SQLite.
        schema_dir: directorio con los SQLs. Si None, usa get_schema_dir().

    Returns:
        Versión final del schema. 0 si no hay migraciones disponibles
        y la DB nunca tuvo schema_version creada.
    """
    if schema_dir is None:
        schema_dir = get_schema_dir()

    if not schema_dir.exists():
        raise FileNotFoundError(f"No existe schema_dir: {schema_dir}")

    current = _get_current_version(conn)
    available = _list_migration_files(schema_dir)

    if not available:
        logger.warning("No hay archivos de migración en %s", schema_dir)
        return current

    pending = [(v, p) for v, p in available if v > current]

    if not pending:
        logger.info("Schema actualizado en versión %d", current)
        return current

    logger.info(
        "Aplicando %d migraciones (de v%d a v%d)",
        len(pending),
        current,
        pending[-1][0],
    )

    for version, path in pending:
        logger.info("Aplicando migración %03d: %s", version, path.name)
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        new_version = _get_current_version(conn)
        if new_version < version:
            msg = (
                f"Migración {path.name} no actualizó schema_version. "
                f"Asegurate de incluir el INSERT correspondiente "
                f"(schema_version version={version})."
            )
            raise RuntimeError(msg)

    final = _get_current_version(conn)
    logger.info("Migraciones completadas. Schema en v%d", final)
    return final
```

### [src/collections_app/core/models/__init__.py](src/collections_app/core/models/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/repositories/__init__.py](src/collections_app/core/repositories/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/utils/__init__.py](src/collections_app/core/utils/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/utils/paths.py](src/collections_app/core/utils/paths.py)

```python
"""Resolución de paths del paquete.

En v0.2.0 sólo se expone `get_schema_dir()`, que apunta al directorio
con los SQLs de migración. Los paths de datos del usuario (DB, logs,
imágenes generadas) se reintroducirán cuando los necesite la app
(Prompt 2/3+), evitando arrastrar código de v0.1 que aún no tiene
consumidor en v0.2.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _get_bundle_dir() -> Path:
    """Directorio raíz de los assets read-only embebidos en el paquete.

    En desarrollo / instalación pip apunta a la carpeta `collections_app`.
    En el bundle de PyInstaller (frozen) usa `sys._MEIPASS`.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "collections_app"
    # paths.py vive en collections_app/core/utils/, subir 3 niveles.
    return Path(__file__).resolve().parent.parent.parent


def get_schema_dir() -> Path:
    """Path al directorio con los SQLs de migración (`core/db/schema/`)."""
    return _get_bundle_dir() / "core" / "db" / "schema"
```

### [src/collections_app/services/__init__.py](src/collections_app/services/__init__.py)

_(archivo vacío)_

### [src/collections_app/views/__init__.py](src/collections_app/views/__init__.py)

_(archivo vacío)_

### [scripts/clean_csv.py](scripts/clean_csv.py)

```python
"""Limpia CSVs antes de importar al sistema.

Aplica en orden:
1. Repara mojibake UTF-8 leído como Latin-1 (`Ã©` → `é`, `Ã±` → `ñ`).
2. Strip de acentos preservando `ñ`/`Ñ` (`JIMÉNEZ` → `JIMENEZ`,
   `MUÑOZ` → `MUÑOZ`).
3. Normaliza chars nórdicos/germánicos sin equivalente NFD
   (`ø`→`o`, `å`→`a`, `ß`→`ss`, `æ`→`ae`).
4. Convierte a MAYÚSCULAS.
5. Trim de espacios en cada celda.
6. Cambia separador `;` por `,`.
7. Filtra filas vacías y filas con `card_number` negativo (el importer
   acepta 0 — útil para tarjeta-portada del álbum).

Uso:
    python scripts/clean_csv.py <archivo_in.csv> <archivo_out.csv>

El script no valida formato — solo limpia. Las validaciones (códigos
existentes, números positivos, nombres no vacíos) corren después en el
importer mismo.
"""

import sys
import unicodedata
from pathlib import Path

# Chars que NFD no descompone (no son letra+combining). Los mapeamos
# explícitamente porque suelen aparecer en nombres nórdicos / alemanes.
EXTRA_NORMALIZE = {
    "ø": "o",
    "Ø": "O",
    "å": "a",
    "Å": "A",
    "æ": "ae",
    "Æ": "AE",
    "ß": "ss",
    "ð": "d",
    "Ð": "D",
    "þ": "th",
    "Þ": "TH",
    "đ": "d",
    "Đ": "D",
    "ł": "l",
    "Ł": "L",
}


def fix_mojibake(text: str) -> str:
    """Repara doble-codificación UTF-8 → CP1252/Latin-1.

    Probamos primero cp1252 (típico en Windows: incluye ‘ ’ € ‰ … en
    el rango 0x80-0x9F, donde Latin-1 tiene slots vacíos). Si cp1252
    falla, probamos Latin-1 puro. Si ambos fallan o el resultado no
    es UTF-8 válido, devolvemos el texto original.
    """
    for encoding in ("cp1252", "latin-1"):
        try:
            return text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return text


def strip_accents_keep_n(text: str) -> str:
    """Quita acentos pero preserva la `ñ`/`Ñ`."""
    # Reservar ñ/Ñ con placeholders que NFD no toca
    placeholders = {"ñ": "\x01", "Ñ": "\x02"}
    for src, ph in placeholders.items():
        text = text.replace(src, ph)

    # NFD descompone "é" → "e" + "´"; filtrar combining marks
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Aplicar mapeo de chars que NFD no descompone (ø, å, ß, æ, …)
    for src, dst in EXTRA_NORMALIZE.items():
        stripped = stripped.replace(src, dst)

    # Restaurar ñ/Ñ
    for src, ph in placeholders.items():
        stripped = stripped.replace(ph, src)

    return stripped


def clean_cell(cell: str) -> str:
    """Aplica fix_mojibake → strip_accents → uppercase → trim."""
    cell = fix_mojibake(cell)
    cell = strip_accents_keep_n(cell)
    cell = cell.upper().strip()
    return cell


def clean_file(input_path: Path, output_path: Path) -> tuple[int, int]:
    """Lee `input_path` y escribe `output_path` limpio.

    Detecta separador (`;` o `,`) en la primera línea no vacía.
    Skips filas donde card_number ≤ 0 (segunda columna).

    Returns:
        (filas_leidas, filas_escritas)
    """
    # Probar UTF-8 primero (formato más común). Si falla, usar Latin-1
    # como fallback (tolera cualquier byte). En ambos casos `fix_mojibake`
    # reparará los chars que estaban doble-codificados.
    raw_bytes = input_path.read_bytes()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode("latin-1", errors="replace")
    lines = raw_text.splitlines()

    # Strip BOM si está presente
    if lines and lines[0].startswith("﻿"):
        lines[0] = lines[0][1:]
    if lines and lines[0].startswith("ï»¿"):
        # BOM UTF-8 mojibake leído como Latin-1
        lines[0] = lines[0][3:]

    # Detectar separador en la primera línea
    first_non_empty = next((line for line in lines if line.strip()), "")
    sep = ";" if first_non_empty.count(";") > first_non_empty.count(",") else ","

    output_lines: list[str] = []
    rows_read = 0
    rows_written = 0
    for raw_line in lines:
        if not raw_line.strip():
            continue
        rows_read += 1
        cells = [clean_cell(c) for c in raw_line.split(sep)]

        # Si parece la fila header, mantenerla
        is_header = cells and cells[0] in {"CODE_ID"}

        # Para filas de cards (3 cols con segundo numérico), skip si number < 0
        if not is_header and len(cells) >= 3:
            try:
                num = int(cells[1])
                if num < 0:
                    continue
            except ValueError:
                # No es card; podría ser code line con order. Dejar pasar.
                pass

        output_lines.append(",".join(cells))
        rows_written += 1

    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return rows_read, rows_written


def main() -> int:
    if len(sys.argv) != 3:
        print(f"uso: python {sys.argv[0]} <input.csv> <output.csv>", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    if not input_path.exists():
        print(f"error: no existe {input_path}", file=sys.stderr)
        return 1
    rows_read, rows_written = clean_file(input_path, output_path)
    print(f"OK: {input_path.name} -> {output_path.name} ({rows_read} -> {rows_written} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### [scripts/generate_context.py](scripts/generate_context.py)

```python
"""Genera documentación de contexto del proyecto para retomarla en una conversación nueva.

Produce UN ÚNICO archivo en `docs/project_structure.md` con tres
secciones, en este orden:

1. **Estructura**: árbol completo del proyecto (links a cada archivo).
2. **Código fuente**: contenido COMPLETO de cada archivo `.py` (con el
   path como encabezado y el código dentro de un bloque ʼʼʼpython).
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
    out.append("ʼʼʼpython")
    # Reemplazar fences ʼʼʼ que pudieran estar dentro del código (raro pero posible)
    # para no romper el bloque markdown.
    safe_source = source.replace("ʼʼʼ", "ʼʼʼ")
    out.append(safe_source.rstrip())
    out.append("ʼʼʼ")
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
```

# 3. Contexto (schema, modelos, repositorios)

Resumen compacto del schema SQL, los dataclasses de `core/models/` y la API pública de los Repository. Pensado como hand-off para una conversación nueva.

## Schema SQL

_(no se encontró ninguna tabla en `db/schema/`.)_

## Modelos (dataclasses en `core/models/`)

_(sin dataclasses encontrados.)_

## Repositorios (`core/repositories/`)

Una clase por tabla. Las repos NO crean conexión, la reciben (`__init__(conn)`). Los queries devuelven instancias de `core/models/`.
