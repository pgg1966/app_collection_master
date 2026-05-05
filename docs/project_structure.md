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
          - [001_initial.sql](src/collections_app/core/db/schema/001_initial.sql)
        - [__init__.py](src/collections_app/core/db/__init__.py)
        - [connection.py](src/collections_app/core/db/connection.py)
        - [migrator.py](src/collections_app/core/db/migrator.py)
      - **models/**
        - **aggregates/**
          - [__init__.py](src/collections_app/core/models/aggregates/__init__.py)
          - [code_stats.py](src/collections_app/core/models/aggregates/code_stats.py)
        - [__init__.py](src/collections_app/core/models/__init__.py)
        - [app_setting.py](src/collections_app/core/models/app_setting.py)
        - [card.py](src/collections_app/core/models/card.py)
        - [card_image.py](src/collections_app/core/models/card_image.py)
        - [code_header.py](src/collections_app/core/models/code_header.py)
        - [code_line.py](src/collections_app/core/models/code_line.py)
        - [collection.py](src/collections_app/core/models/collection.py)
        - [inventory_item.py](src/collections_app/core/models/inventory_item.py)
        - [transaction.py](src/collections_app/core/models/transaction.py)
      - **repositories/**
        - [__init__.py](src/collections_app/core/repositories/__init__.py)
        - [app_settings_repo.py](src/collections_app/core/repositories/app_settings_repo.py)
        - [base.py](src/collections_app/core/repositories/base.py)
        - [card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)
        - [cards_repo.py](src/collections_app/core/repositories/cards_repo.py)
        - [code_headers_repo.py](src/collections_app/core/repositories/code_headers_repo.py)
        - [code_lines_repo.py](src/collections_app/core/repositories/code_lines_repo.py)
        - [collections_repo.py](src/collections_app/core/repositories/collections_repo.py)
        - [inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)
        - [transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)
      - **utils/**
        - [__init__.py](src/collections_app/core/utils/__init__.py)
        - [paths.py](src/collections_app/core/utils/paths.py)
      - [__init__.py](src/collections_app/core/__init__.py)
    - **services/**
      - [__init__.py](src/collections_app/services/__init__.py)
    - **views/**
      - [__init__.py](src/collections_app/views/__init__.py)
    - [__init__.py](src/collections_app/__init__.py)
- **tests/**
  - **architecture/**
    - [__init__.py](tests/architecture/__init__.py)
    - [test_layers.py](tests/architecture/test_layers.py)
    - [test_repo_return_contracts.py](tests/architecture/test_repo_return_contracts.py)
    - [test_table_model_repo_parity.py](tests/architecture/test_table_model_repo_parity.py)
  - **core/**
    - **db/**
      - [__init__.py](tests/core/db/__init__.py)
      - [test_migration_001_schema.py](tests/core/db/test_migration_001_schema.py)
      - [test_migrator_smoke.py](tests/core/db/test_migrator_smoke.py)
    - **models/**
      - [__init__.py](tests/core/models/__init__.py)
      - [test_app_setting.py](tests/core/models/test_app_setting.py)
      - [test_card.py](tests/core/models/test_card.py)
      - [test_card_image.py](tests/core/models/test_card_image.py)
      - [test_code_header.py](tests/core/models/test_code_header.py)
      - [test_code_line.py](tests/core/models/test_code_line.py)
      - [test_code_stats.py](tests/core/models/test_code_stats.py)
      - [test_collection.py](tests/core/models/test_collection.py)
      - [test_inventory_item.py](tests/core/models/test_inventory_item.py)
      - [test_transaction.py](tests/core/models/test_transaction.py)
    - **repositories/**
      - [__init__.py](tests/core/repositories/__init__.py)
      - [test_app_settings_repo.py](tests/core/repositories/test_app_settings_repo.py)
      - [test_base_repository.py](tests/core/repositories/test_base_repository.py)
      - [test_card_images_repo.py](tests/core/repositories/test_card_images_repo.py)
      - [test_cards_repo.py](tests/core/repositories/test_cards_repo.py)
      - [test_cards_repo_stats.py](tests/core/repositories/test_cards_repo_stats.py)
      - [test_code_headers_repo.py](tests/core/repositories/test_code_headers_repo.py)
      - [test_code_lines_repo.py](tests/core/repositories/test_code_lines_repo.py)
      - [test_collections_repo.py](tests/core/repositories/test_collections_repo.py)
      - [test_inventory_repo.py](tests/core/repositories/test_inventory_repo.py)
      - [test_transactions_repo.py](tests/core/repositories/test_transactions_repo.py)
    - [__init__.py](tests/core/__init__.py)
  - [__init__.py](tests/__init__.py)
  - [conftest.py](tests/conftest.py)
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
  - [project_structure.md](docs/project_structure.md)

**Archivos sueltos en raíz:**
- [.coverage](.coverage)
- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
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

### [src/collections_app/core/models/aggregates/__init__.py](src/collections_app/core/models/aggregates/__init__.py)

```python
"""Modelos agregados — resultados de queries que combinan tablas.

A diferencia de los modelos de tabla en `core.models.*`, estos NO se
persisten directamente y NO tienen un repositorio dedicado: son
contenedores tipados para resultados de queries de stats / agregaciones.

Aún así viven dentro de la capa `models` (la regla de imports los trata
igual que cualquier otro dataclass) y son `@dataclass(slots=True)` para
que el contrato de retorno de los repos cumpla CLAUDE.md sec 2.3.
"""
```

### [src/collections_app/core/models/aggregates/code_stats.py](src/collections_app/core/models/aggregates/code_stats.py)

```python
"""Aggregate CodeStats: stats por código dentro de una colección."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeStats:
    """Stats agregadas por code_id (resultado de `CardsRepository.get_stats_by_code`).

    Attributes:
        code_id: identificador del código (ej. "ARG").
        code_name: descripción legible del código (ej. "Argentina").
            Si no hay entrada en codes_lines, fallbackea al code_id.
        total: cantidad de cards del catálogo con ese code_id.
        owned: cantidad de cards con `inventory.quantity > 0`.
        percentage: owned/total * 100. 0.0 si total es 0.
    """

    code_id: str
    code_name: str
    total: int
    owned: int
    percentage: float
```

### [src/collections_app/core/models/app_setting.py](src/collections_app/core/models/app_setting.py)

```python
"""Modelo AppSetting: par clave/valor de configuración persistido en `app_settings`.

Existe como dataclass aunque la tabla solo tenga 2 columnas porque CLAUDE.md
sec 2.3 prohíbe que un repo retorne `str | None` crudo. El casteo a tipos
derivados (`int`, `bool`) vive acá para que el caller pueda elegir entre el
string original y un tipo parseado sin que el repo sepa nada del contenido.
"""

from __future__ import annotations

from dataclasses import dataclass

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_FALSY = frozenset({"0", "false", "no", "off"})


@dataclass(slots=True)
class AppSetting:
    """Setting clave/valor.

    Attributes:
        key: clave única.
        value: valor crudo como string, o None.
    """

    key: str
    value: str | None

    def as_int(self: AppSetting) -> int | None:
        """Parsea `value` como int. None si `value` es None o no es un entero válido."""
        if self.value is None:
            return None
        try:
            return int(self.value)
        except ValueError:
            return None

    def as_bool(self: AppSetting) -> bool | None:
        """Parsea `value` como bool. None si `value` es None o no reconocible.

        Acepta como verdaderos: '1', 'true', 'yes', 'on' (case/whitespace-insensitive).
        Acepta como falsos:    '0', 'false', 'no', 'off' (idem).
        Cualquier otra cosa retorna None — el caller decide el default.
        """
        if self.value is None:
            return None
        normalized = self.value.strip().lower()
        if normalized in _TRUTHY:
            return True
        if normalized in _FALSY:
            return False
        return None
```

### [src/collections_app/core/models/card.py](src/collections_app/core/models/card.py)

```python
"""Modelo Card: una entrada del catálogo de una colección."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Card:
    """Card del catálogo.

    PK subrogada `card_id`; UNIQUE sobre (collection_id, code_id, card_number).

    Attributes:
        card_id: PK auto-incremental. None pre-persistencia.
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG"). Si la colección no
            requiere código, suele usarse uno vacío o un placeholder.
        card_number: número correlativo dentro del code_id.
        card_name: nombre legible (ej. "Lionel Messi").
    """

    card_id: int | None
    collection_id: int
    code_id: str
    card_number: int
    card_name: str

    @property
    def card_key(self: Card) -> str:
        """Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1')."""
        return f"{self.code_id}-{self.card_number}"
```

### [src/collections_app/core/models/card_image.py](src/collections_app/core/models/card_image.py)

```python
"""Modelo CardImage: tracking de imágenes generadas por card."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CardImage:
    """Registro de la imagen generada para una card.

    PK subrogada `card_image_id`; UNIQUE sobre `card_id` (1:1 con cards).
    Si una card todavía no tiene imagen procesada, no aparece — usar
    `CardImagesRepository.get_pending(collection_id)` para listar las
    cards sin imagen.

    Esta tabla es la **única fuente** del path de imagen (sec 6 prohíbe
    duplicar el dato en `inventory`).

    Attributes:
        card_image_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card asociada (UNIQUE).
        found_photo: True si la imagen final usa una foto real,
            False si quedó como placeholder.
        image_source: fuente ("wikipedia", "duckduckgo", "google",
            "placeholder", "cache") o None si no se sabe.
        image_path: path al PNG generado, o None si no se grabó.
        generated_at: ISO datetime UTC de la generación, o None.
    """

    card_image_id: int | None
    card_id: int
    found_photo: bool
    image_source: str | None = None
    image_path: str | None = None
    generated_at: str | None = None
```

### [src/collections_app/core/models/code_header.py](src/collections_app/core/models/code_header.py)

```python
"""Modelo CodeHeader: universo de códigos (ej. "Países FIFA", "Sets de Magic")."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeHeader:
    """Representa un universo de códigos.

    Attributes:
        code_header_id: PK auto-incremental. None si aún no fue persistido.
        code_header_name: nombre único del header.
        code_max_length: longitud máxima permitida para los `code_id` hijos.
    """

    code_header_id: int | None
    code_header_name: str
    code_max_length: int = 5
```

### [src/collections_app/core/models/code_line.py](src/collections_app/core/models/code_line.py)

```python
"""Modelo CodeLine: un código individual dentro de un CodeHeader."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CodeLine:
    """Línea de código asociada a un header.

    PK subrogada `code_line_id`; UNIQUE sobre (code_header_id, code_id).

    Attributes:
        code_line_id: PK auto-incremental. None si aún no fue persistido.
        code_header_id: FK al CodeHeader contenedor.
        code_id: identificador del código (ej. "ARG", "MR"). Texto libre con
            longitud máxima validada por `CodeHeader.code_max_length`.
        code_name: descripción legible del código (ej. "Argentina", "Mirage").
        code_order: posición para ordenar manualmente dentro del header.
            Lower = primero. Default 0 (alfabético si no se configura).
    """

    code_line_id: int | None
    code_header_id: int
    code_id: str
    code_name: str
    code_order: int = 0
```

### [src/collections_app/core/models/collection.py](src/collections_app/core/models/collection.py)

```python
"""Modelo Collection: catálogo de cards configurable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Collection:
    """Representa una colección a juntar (catálogo de cards).

    Attributes:
        collection_id: PK auto-incremental. None si aún no fue persistido.
        collection_name: nombre único de la colección.
        card_count: cantidad total esperada de cards.
        requires_code: si True, las cards se subdividen por code_id.
        code_field_name: label visible del campo de código en la UI
            (ej. "Set", "País"). Metadata de presentación; nunca se usa
            como referencia dinámica a otra columna (CLAUDE.md sec 6).
        code_header_id: FK al CodeHeader que define el universo de códigos.
        is_premium: si True, requiere licencia para usar.
        license_key_required: hash de la key requerida (None si free).
        album_columns: cards por fila en el PDF álbum (default 3).
        album_rows: filas por página en el PDF álbum (default 4).
        album_orientation: 'portrait' o 'landscape' — algunas colecciones
            tienen cards horizontales y necesitan landscape.
    """

    collection_id: int | None
    collection_name: str
    card_count: int
    requires_code: bool
    code_field_name: str | None
    code_header_id: int
    is_premium: bool = False
    license_key_required: str | None = None
    album_columns: int = 3
    album_rows: int = 4
    album_orientation: str = "portrait"
```

### [src/collections_app/core/models/inventory_item.py](src/collections_app/core/models/inventory_item.py)

```python
"""Modelo InventoryItem: cantidad poseída por el usuario de una Card específica."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InventoryItem:
    """Stock del usuario para una Card.

    Tabla normalizada via FK a card_id (UNIQUE — 1:1 con cards). El path
    de imagen vive solo en `card_images`, no acá (CLAUDE.md sec 6).

    Attributes:
        inventory_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card asociada (UNIQUE).
        quantity: cantidad poseída total. 0 = no tiene; >1 = duplicados.
    """

    inventory_id: int | None
    card_id: int
    quantity: int = 0

    @property
    def is_owned(self: InventoryItem) -> bool:
        """True si el usuario tiene al menos una copia."""
        return self.quantity > 0

    @property
    def has_duplicates(self: InventoryItem) -> bool:
        """True si el usuario tiene más de una copia."""
        return self.quantity > 1
```

### [src/collections_app/core/models/transaction.py](src/collections_app/core/models/transaction.py)

```python
"""Modelo Transaction: bitácora de altas/bajas de inventario."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OperationType(StrEnum):
    """Tipo de operación registrada en la bitácora."""

    ALTA = "alta"
    BAJA = "baja"


@dataclass(slots=True)
class Transaction:
    """Registro inmutable de un movimiento sobre el inventario.

    FK granular a `card_id` (sec 2.5: bitácoras apuntan a la entidad
    atómica afectada, no a su contenedor). `exchange_event_id` agrupa
    transacciones que pertenecen a un mismo intercambio (mismo valor
    en todas las altas y bajas del evento); NULL para movimientos
    aislados que no son parte de un intercambio.

    Attributes:
        transaction_id: PK auto-incremental. None pre-persistencia.
        card_id: FK a la Card afectada.
        operation: alta o baja (ver OperationType).
        quantity: unidades movidas (siempre positivo, CHECK > 0).
        transaction_date: timestamp del movimiento.
        exchange_event_id: agrupador de transacciones de un intercambio,
            o None.
    """

    transaction_id: int | None
    card_id: int
    operation: OperationType
    quantity: int
    transaction_date: datetime
    exchange_event_id: int | None = None
```

### [src/collections_app/core/repositories/__init__.py](src/collections_app/core/repositories/__init__.py)

```python
"""Capa de repositorios — acceso a la DB.

Cada tabla del schema (excepto `schema_version`) tiene su propia
`*Repository` que recibe una `sqlite3.Connection` y expone CRUD/queries
retornando dataclasses de `core.models`. Nunca tuplas, dicts ni
`sqlite3.Row` (CLAUDE.md sec 2.3).
"""

from collections_app.core.repositories.base import BaseRepository

__all__ = ["BaseRepository"]
```

### [src/collections_app/core/repositories/app_settings_repo.py](src/collections_app/core/repositories/app_settings_repo.py)

```python
"""Repositorio para `app_settings`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.app_setting import AppSetting
from collections_app.core.repositories.base import BaseRepository


def _row_to_setting(row: sqlite3.Row) -> AppSetting:
    return AppSetting(key=row["setting_key"], value=row["setting_value"])


class AppSettingsRepository(BaseRepository):
    """CRUD sobre `app_settings`."""

    def get(self: AppSettingsRepository, key: str) -> AppSetting | None:
        """Retorna el setting por clave, o None si no existe."""
        row = self.conn.execute(
            "SELECT setting_key, setting_value FROM app_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        return _row_to_setting(row) if row else None

    def set(self: AppSettingsRepository, setting: AppSetting) -> None:
        """Inserta o actualiza el setting."""
        self.conn.execute(
            "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
            (setting.key, setting.value),
        )

    def delete(self: AppSettingsRepository, key: str) -> bool:
        """Borra el setting. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM app_settings WHERE setting_key = ?", (key,))
        return cursor.rowcount > 0

    def list_all(self: AppSettingsRepository) -> list[AppSetting]:
        """Lista todos los settings ordenados por clave."""
        rows = self.conn.execute(
            "SELECT setting_key, setting_value FROM app_settings ORDER BY setting_key"
        ).fetchall()
        return [_row_to_setting(r) for r in rows]
```

### [src/collections_app/core/repositories/base.py](src/collections_app/core/repositories/base.py)

```python
"""Repository base.

Todas las repos reciben una `sqlite3.Connection` por `__init__` y la
guardan en `self.conn`. La conexión la construye el caller (típicamente
un service o el bootstrap de la app); las repos nunca abren ni cierran.
"""

from __future__ import annotations

import sqlite3


class BaseRepository:
    """Repositorio base — almacena la conexión SQLite recibida."""

    def __init__(self: BaseRepository, conn: sqlite3.Connection) -> None:
        self.conn = conn
```

### [src/collections_app/core/repositories/card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)

```python
"""Repositorio para `card_images`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.card import Card
from collections_app.core.models.card_image import CardImage
from collections_app.core.repositories.base import BaseRepository


def _row_to_image(row: sqlite3.Row) -> CardImage:
    return CardImage(
        card_image_id=row["card_image_id"],
        card_id=row["card_id"],
        found_photo=bool(row["found_photo"]),
        image_source=row["image_source"],
        image_path=row["image_path"],
        generated_at=row["generated_at"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardImagesRepository(BaseRepository):
    """CRUD y queries de tracking sobre `card_images`."""

    def get_by_card_id(self: CardImagesRepository, card_id: int) -> CardImage | None:
        """Imagen registrada para una card. None si nunca se procesó."""
        row = self.conn.execute(
            "SELECT card_image_id, card_id, found_photo, image_source, "
            "image_path, generated_at "
            "FROM card_images WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_image(row) if row else None

    def list_by_collection(self: CardImagesRepository, collection_id: int) -> list[CardImage]:
        """Imágenes registradas de cards de la colección."""
        rows = self.conn.execute(
            "SELECT ci.card_image_id, ci.card_id, ci.found_photo, "
            "       ci.image_source, ci.image_path, ci.generated_at "
            "FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def upsert(self: CardImagesRepository, image: CardImage) -> CardImage:
        """Inserta o actualiza por card_id UNIQUE."""
        self.conn.execute(
            "INSERT INTO card_images "
            "(card_id, found_photo, image_source, image_path, generated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET "
            "found_photo = excluded.found_photo, "
            "image_source = excluded.image_source, "
            "image_path = excluded.image_path, "
            "generated_at = excluded.generated_at",
            (
                image.card_id,
                int(image.found_photo),
                image.image_source,
                image.image_path,
                image.generated_at,
            ),
        )
        fetched = self.get_by_card_id(image.card_id)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def delete_by_card_id(self: CardImagesRepository, card_id: int) -> bool:
        """Borra el tracking de una card. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM card_images WHERE card_id = ?", (card_id,))
        return cursor.rowcount > 0

    def get_pending(self: CardImagesRepository, collection_id: int) -> list[Card]:
        """Cards sin entry en card_images (todavía no procesadas)."""
        rows = self.conn.execute(
            "SELECT c.card_id, c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN card_images ci ON ci.card_id = c.card_id "
            "WHERE c.collection_id = ? AND ci.card_id IS NULL "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_placeholders(self: CardImagesRepository, collection_id: int) -> list[CardImage]:
        """Imágenes generadas pero con `found_photo=False`."""
        rows = self.conn.execute(
            "SELECT ci.card_image_id, ci.card_id, ci.found_photo, "
            "       ci.image_source, ci.image_path, ci.generated_at "
            "FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? AND ci.found_photo = 0 "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def count_with_photo(self: CardImagesRepository, collection_id: int) -> int:
        """Cantidad de cards con `found_photo=True`."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ? AND ci.found_photo = 1",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def count_total_generated(self: CardImagesRepository, collection_id: int) -> int:
        """Cantidad de cards con cualquier imagen (real o placeholder)."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM card_images ci "
            "INNER JOIN cards c ON c.card_id = ci.card_id "
            "WHERE c.collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count
```

### [src/collections_app/core/repositories/cards_repo.py](src/collections_app/core/repositories/cards_repo.py)

```python
"""Repositorio para `cards`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.card import Card
from collections_app.core.repositories.base import BaseRepository


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardsRepository(BaseRepository):
    """CRUD y queries específicas sobre `cards`."""

    def get_by_id(self: CardsRepository, card_id: int) -> Card | None:
        """Card por PK subrogada, o None."""
        row = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_card(row) if row else None

    def get(
        self: CardsRepository,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> Card | None:
        """Card por business key (collection, code, number), o None."""
        row = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card(row) if row else None

    def list_by_collection(self: CardsRepository, collection_id: int) -> list[Card]:
        """Cards de la colección ordenadas por (code_id, card_number)."""
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def list_by_code(self: CardsRepository, collection_id: int, code_id: str) -> list[Card]:
        """Cards filtradas por code_id, ordenadas por card_number."""
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND code_id = ? "
            "ORDER BY card_number",
            (collection_id, code_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def find_by_number(self: CardsRepository, collection_id: int, card_number: int) -> list[Card]:
        """Busca cards por número sin filtrar por code_id.

        Útil cuando `Collection.requires_code=False`: el usuario solo
        ingresa el número y la lógica de servicio resuelve ambigüedad
        si hay >1 match. Ordenado por code_id para determinismo.
        """
        rows = self.conn.execute(
            "SELECT card_id, collection_id, code_id, card_number, card_name "
            "FROM cards WHERE collection_id = ? AND card_number = ? "
            "ORDER BY code_id",
            (collection_id, card_number),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def count_by_collection(self: CardsRepository, collection_id: int) -> int:
        """Cuántas cards tiene la colección."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def create(self: CardsRepository, card: Card) -> Card:
        """Inserta y retorna la card con `card_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?)",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        return Card(
            card_id=cursor.lastrowid,
            collection_id=card.collection_id,
            code_id=card.code_id,
            card_number=card.card_number,
            card_name=card.card_name,
        )

    def upsert(self: CardsRepository, card: Card) -> Card:
        """Inserta o actualiza por business key. Retorna con id poblado."""
        self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        fetched = self.get(card.collection_id, card.code_id, card.card_number)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def bulk_upsert(self: CardsRepository, cards: list[Card]) -> int:
        """Inserta o actualiza muchas cards en un batch. Retorna cantidad procesada."""
        if not cards:
            return 0
        params = [(c.collection_id, c.code_id, c.card_number, c.card_name) for c in cards]
        self.conn.executemany(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            params,
        )
        return len(params)

    def delete_by_id(self: CardsRepository, card_id: int) -> bool:
        """Borra la card. Cascade borra inventory y card_images. Retorna True si existía."""
        cursor = self.conn.execute("DELETE FROM cards WHERE card_id = ?", (card_id,))
        return cursor.rowcount > 0

    def get_stats_by_code(self: CardsRepository, collection_id: int) -> list[CodeStats]:
        """Stats agregadas por code_id de la colección.

        Para cada code_id presente en `cards`: total de cards, cuántas
        tiene el usuario (inventory.quantity > 0), porcentaje. code_name
        se resuelve desde `codes_lines` filtrando por el header de la
        colección; fallbackea al code_id si no hay match. Orden:
        codes_lines.code_order primero, code_id alfabético como
        tiebreak — coincide con el orden visible al usuario.

        Retorna lista de CodeStats (dataclass slots, sec 2.3).
        """
        rows = self.conn.execute(
            "SELECT c.code_id AS code_id, "
            "       COALESCE(cl.code_name, c.code_id) AS code_name, "
            "       COALESCE(cl.code_order, 0) AS code_order, "
            "       COUNT(*) AS total, "
            "       SUM(CASE WHEN i.quantity > 0 THEN 1 ELSE 0 END) AS owned "
            "FROM cards c "
            "LEFT JOIN inventory i ON i.card_id = c.card_id "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections "
            "       WHERE collection_id = ?"
            "    ) "
            "WHERE c.collection_id = ? "
            "GROUP BY c.code_id "
            "ORDER BY code_order, c.code_id",
            (collection_id, collection_id),
        ).fetchall()
        result: list[CodeStats] = []
        for row in rows:
            total = int(row["total"])
            owned = int(row["owned"] or 0)
            percentage = (owned / total * 100) if total > 0 else 0.0
            result.append(
                CodeStats(
                    code_id=str(row["code_id"]),
                    code_name=str(row["code_name"]),
                    total=total,
                    owned=owned,
                    percentage=percentage,
                )
            )
        return result
```

### [src/collections_app/core/repositories/code_headers_repo.py](src/collections_app/core/repositories/code_headers_repo.py)

```python
"""Repositorio para `codes_headers`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.repositories.base import BaseRepository


def _row_to_header(row: sqlite3.Row) -> CodeHeader:
    return CodeHeader(
        code_header_id=row["code_header_id"],
        code_header_name=row["code_header_name"],
        code_max_length=row["code_max_length"],
    )


class CodeHeadersRepository(BaseRepository):
    """CRUD sobre `codes_headers`."""

    def list_all(self: CodeHeadersRepository) -> list[CodeHeader]:
        """Retorna todos los headers ordenados por nombre."""
        rows = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers ORDER BY code_header_name"
        ).fetchall()
        return [_row_to_header(r) for r in rows]

    def get_by_id(self: CodeHeadersRepository, code_header_id: int) -> CodeHeader | None:
        """Retorna el header por id, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_id = ?",
            (code_header_id,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def get_by_name(self: CodeHeadersRepository, name: str) -> CodeHeader | None:
        """Retorna el header por nombre exacto (case-sensitive), o None."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_name = ?",
            (name,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def create(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader:
        """Inserta y retorna el header con `code_header_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
            (header.code_header_name, header.code_max_length),
        )
        return CodeHeader(
            code_header_id=cursor.lastrowid,
            code_header_name=header.code_header_name,
            code_max_length=header.code_max_length,
        )

    def update(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader:
        """Actualiza un header existente. Requiere `code_header_id` no None."""
        if header.code_header_id is None:
            raise ValueError("update requiere code_header_id no None")
        self.conn.execute(
            "UPDATE codes_headers "
            "SET code_header_name = ?, code_max_length = ? "
            "WHERE code_header_id = ?",
            (header.code_header_name, header.code_max_length, header.code_header_id),
        )
        return header

    def delete(self: CodeHeadersRepository, code_header_id: int) -> bool:
        """Borra un header. Cascade borra `codes_lines` asociadas."""
        cursor = self.conn.execute(
            "DELETE FROM codes_headers WHERE code_header_id = ?", (code_header_id,)
        )
        return cursor.rowcount > 0
```

### [src/collections_app/core/repositories/code_lines_repo.py](src/collections_app/core/repositories/code_lines_repo.py)

```python
"""Repositorio para `codes_lines`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.base import BaseRepository


def _row_to_line(row: sqlite3.Row) -> CodeLine:
    return CodeLine(
        code_line_id=row["code_line_id"],
        code_header_id=row["code_header_id"],
        code_id=row["code_id"],
        code_name=row["code_name"],
        code_order=row["code_order"],
    )


class CodeLinesRepository(BaseRepository):
    """CRUD sobre `codes_lines` con soporte de reordenamiento manual."""

    def list_by_header(self: CodeLinesRepository, code_header_id: int) -> list[CodeLine]:
        """Líneas del header ordenadas por (code_order, code_id)."""
        rows = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_header_id = ? "
            "ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [_row_to_line(r) for r in rows]

    def get(self: CodeLinesRepository, code_header_id: int, code_id: str) -> CodeLine | None:
        """Línea por business key (header_id, code_id), o None si no existe."""
        row = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        ).fetchone()
        return _row_to_line(row) if row else None

    def get_by_id(self: CodeLinesRepository, code_line_id: int) -> CodeLine | None:
        """Línea por PK subrogada, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_line_id, code_header_id, code_id, code_name, code_order "
            "FROM codes_lines WHERE code_line_id = ?",
            (code_line_id,),
        ).fetchone()
        return _row_to_line(row) if row else None

    def upsert(self: CodeLinesRepository, line: CodeLine) -> CodeLine:
        """Inserta o actualiza la línea según (code_header_id, code_id) UNIQUE.

        Retorna el modelo con `code_line_id` poblado (incluso para updates,
        donde se relee la fila).
        """
        self.conn.execute(
            "INSERT INTO codes_lines "
            "(code_header_id, code_id, code_name, code_order) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(code_header_id, code_id) DO UPDATE SET "
            "code_name = excluded.code_name, code_order = excluded.code_order",
            (line.code_header_id, line.code_id, line.code_name, line.code_order),
        )
        # Releer para devolver el id (sea recién creado o preexistente).
        fetched = self.get(line.code_header_id, line.code_id)
        assert fetched is not None  # acabamos de upsertarla
        return fetched

    def delete(self: CodeLinesRepository, code_header_id: int, code_id: str) -> bool:
        """Borra una línea por business key. Retorna True si existía."""
        cursor = self.conn.execute(
            "DELETE FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        )
        return cursor.rowcount > 0

    def reorder(
        self: CodeLinesRepository,
        code_header_id: int,
        ordered_code_ids: list[str],
    ) -> None:
        """Reasigna `code_order` según el índice (1-based) en la lista.

        Líneas no incluidas en `ordered_code_ids` mantienen su order previo.
        Útil cuando el usuario reordena visualmente solo un subconjunto.
        """
        for index, code_id in enumerate(ordered_code_ids, start=1):
            self.conn.execute(
                "UPDATE codes_lines SET code_order = ? " "WHERE code_header_id = ? AND code_id = ?",
                (index, code_header_id, code_id),
            )
```

### [src/collections_app/core/repositories/collections_repo.py](src/collections_app/core/repositories/collections_repo.py)

```python
"""Repositorio para `collections`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.collection import Collection
from collections_app.core.repositories.base import BaseRepository

# Constante de columnas SELECT — interpolada en queries via f-string. NO
# proviene de input externo, por lo que las advertencias S608 (SQL
# injection) en este archivo son falsos positivos.
_SELECT_COLUMNS = (
    "collection_id, collection_name, card_count, requires_code, "
    "code_field_name, code_header_id, is_premium, license_key_required, "
    "album_columns, album_rows, album_orientation"
)


def _row_to_collection(row: sqlite3.Row) -> Collection:
    return Collection(
        collection_id=row["collection_id"],
        collection_name=row["collection_name"],
        card_count=row["card_count"],
        requires_code=bool(row["requires_code"]),
        code_field_name=row["code_field_name"],
        code_header_id=row["code_header_id"],
        is_premium=bool(row["is_premium"]),
        license_key_required=row["license_key_required"],
        album_columns=row["album_columns"],
        album_rows=row["album_rows"],
        album_orientation=row["album_orientation"],
    )


class CollectionsRepository(BaseRepository):
    """CRUD sobre `collections`."""

    def list_all(self: CollectionsRepository) -> list[Collection]:
        """Todas las colecciones ordenadas por nombre."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM collections ORDER BY collection_name"  # noqa: S608
        ).fetchall()
        return [_row_to_collection(r) for r in rows]

    def get_by_id(self: CollectionsRepository, collection_id: int) -> Collection | None:
        """Colección por id, o None."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM collections WHERE collection_id = ?",  # noqa: S608
            (collection_id,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def get_by_name(self: CollectionsRepository, name: str) -> Collection | None:
        """Colección por nombre exacto, o None."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLUMNS} FROM collections WHERE collection_name = ?",  # noqa: S608
            (name,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def create(self: CollectionsRepository, collection: Collection) -> Collection:
        """Inserta y retorna la colección con `collection_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, requires_code, code_field_name, "
            "code_header_id, is_premium, license_key_required, "
            "album_columns, album_rows, album_orientation) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                collection.collection_name,
                collection.card_count,
                int(collection.requires_code),
                collection.code_field_name,
                collection.code_header_id,
                int(collection.is_premium),
                collection.license_key_required,
                collection.album_columns,
                collection.album_rows,
                collection.album_orientation,
            ),
        )
        return Collection(
            collection_id=cursor.lastrowid,
            collection_name=collection.collection_name,
            card_count=collection.card_count,
            requires_code=collection.requires_code,
            code_field_name=collection.code_field_name,
            code_header_id=collection.code_header_id,
            is_premium=collection.is_premium,
            license_key_required=collection.license_key_required,
            album_columns=collection.album_columns,
            album_rows=collection.album_rows,
            album_orientation=collection.album_orientation,
        )

    def update(self: CollectionsRepository, collection: Collection) -> Collection:
        """Actualiza una colección existente. Requiere `collection_id` no None."""
        if collection.collection_id is None:
            raise ValueError("update requiere collection_id no None")
        self.conn.execute(
            "UPDATE collections SET "
            "collection_name = ?, card_count = ?, requires_code = ?, "
            "code_field_name = ?, code_header_id = ?, is_premium = ?, "
            "license_key_required = ?, album_columns = ?, album_rows = ?, "
            "album_orientation = ? "
            "WHERE collection_id = ?",
            (
                collection.collection_name,
                collection.card_count,
                int(collection.requires_code),
                collection.code_field_name,
                collection.code_header_id,
                int(collection.is_premium),
                collection.license_key_required,
                collection.album_columns,
                collection.album_rows,
                collection.album_orientation,
                collection.collection_id,
            ),
        )
        return collection

    def delete(self: CollectionsRepository, collection_id: int) -> bool:
        """Borra la colección. Cascade borra cards e inventory."""
        cursor = self.conn.execute(
            "DELETE FROM collections WHERE collection_id = ?", (collection_id,)
        )
        return cursor.rowcount > 0
```

### [src/collections_app/core/repositories/inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)

```python
"""Repositorio para `inventory`."""

from __future__ import annotations

import sqlite3

from collections_app.core.models.card import Card
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.repositories.base import BaseRepository


def _row_to_item(row: sqlite3.Row) -> InventoryItem:
    return InventoryItem(
        inventory_id=row["inventory_id"],
        card_id=row["card_id"],
        quantity=row["quantity"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        card_id=row["card_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class InventoryRepository(BaseRepository):
    """CRUD y queries específicas sobre `inventory`.

    `inventory` es 1:1 con `cards` via card_id UNIQUE. Las queries que
    necesitan filtrar por colección hacen JOIN con `cards`.
    """

    def get_by_card_id(self: InventoryRepository, card_id: int) -> InventoryItem | None:
        """Inventory item de una card. None si nunca se grabó."""
        row = self.conn.execute(
            "SELECT inventory_id, card_id, quantity " "FROM inventory WHERE card_id = ?",
            (card_id,),
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_by_collection(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory de todas las cards de la colección (incluye qty=0)."""
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "WHERE c.collection_id = ? "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_owned(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory items con quantity > 0 de la colección."""
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "WHERE c.collection_id = ? AND i.quantity > 0 "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_duplicates(self: InventoryRepository, collection_id: int) -> list[InventoryItem]:
        """Inventory items con quantity > 1 de la colección."""
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "WHERE c.collection_id = ? AND i.quantity > 1 "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_top_duplicates(
        self: InventoryRepository, collection_id: int, limit: int = 10
    ) -> list[InventoryItem]:
        """Las cards con mayor cantidad (quantity > 1), descendente."""
        rows = self.conn.execute(
            "SELECT i.inventory_id, i.card_id, i.quantity "
            "FROM inventory i "
            "INNER JOIN cards c ON c.card_id = i.card_id "
            "WHERE c.collection_id = ? AND i.quantity > 1 "
            "ORDER BY i.quantity DESC, c.code_id, c.card_number "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_missing(self: InventoryRepository, collection_id: int) -> list[Card]:
        """Cards que el usuario aún no tiene (sin inventory o quantity=0)."""
        rows = self.conn.execute(
            "SELECT c.card_id, c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN inventory i ON i.card_id = c.card_id "
            "WHERE c.collection_id = ? AND COALESCE(i.quantity, 0) = 0 "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def upsert(self: InventoryRepository, item: InventoryItem) -> InventoryItem:
        """Inserta o actualiza el inventory item por card_id UNIQUE."""
        self.conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET quantity = excluded.quantity",
            (item.card_id, item.quantity),
        )
        fetched = self.get_by_card_id(item.card_id)
        assert fetched is not None  # acabamos de upsertarlo
        return fetched

    def adjust_quantity(self: InventoryRepository, card_id: int, delta: int) -> InventoryItem:
        """Suma `delta` a la quantity (puede ser negativo).

        Crea la entrada con quantity=0 si no existía antes de aplicar el
        delta. La operación se hace en SQL para evitar race conditions.
        """
        self.conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?) "
            "ON CONFLICT(card_id) DO UPDATE SET quantity = quantity + excluded.quantity",
            (card_id, delta),
        )
        fetched = self.get_by_card_id(card_id)
        assert fetched is not None  # acabamos de insertar/actualizar
        return fetched
```

### [src/collections_app/core/repositories/transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)

```python
"""Repositorio para `transactions`."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.base import BaseRepository


def _row_to_txn(row: sqlite3.Row) -> Transaction:
    return Transaction(
        transaction_id=row["transaction_id"],
        card_id=row["card_id"],
        operation=OperationType(row["operation"]),
        quantity=row["quantity"],
        transaction_date=datetime.fromisoformat(row["transaction_date"]),
        exchange_event_id=row["exchange_event_id"],
    )


class TransactionsRepository(BaseRepository):
    """Bitácora de operaciones (alta/baja) sobre el inventario.

    FK granular a `card_id` (sec 2.5). Cada `log()` persiste el ISO del
    `transaction_date`; el repo lo parsea de vuelta en lecturas.
    `exchange_event_id` agrupa transacciones de un mismo intercambio.
    """

    def log(self: TransactionsRepository, txn: Transaction) -> Transaction:
        """Inserta una transacción y la retorna con `transaction_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO transactions "
            "(card_id, operation, quantity, transaction_date, exchange_event_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                txn.card_id,
                txn.operation.value,
                txn.quantity,
                txn.transaction_date.isoformat(sep=" "),
                txn.exchange_event_id,
            ),
        )
        return Transaction(
            transaction_id=cursor.lastrowid,
            card_id=txn.card_id,
            operation=txn.operation,
            quantity=txn.quantity,
            transaction_date=txn.transaction_date,
            exchange_event_id=txn.exchange_event_id,
        )

    def list_by_card(
        self: TransactionsRepository, card_id: int, limit: int = 100
    ) -> list[Transaction]:
        """Transacciones de una card, las más recientes primero."""
        rows = self.conn.execute(
            "SELECT transaction_id, card_id, operation, quantity, "
            "       transaction_date, exchange_event_id "
            "FROM transactions WHERE card_id = ? "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (card_id, limit),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_by_collection(
        self: TransactionsRepository,
        collection_id: int,
        limit: int = 100,
    ) -> list[Transaction]:
        """Transacciones de cards de la colección, recientes primero."""
        rows = self.conn.execute(
            "SELECT t.transaction_id, t.card_id, t.operation, t.quantity, "
            "       t.transaction_date, t.exchange_event_id "
            "FROM transactions t "
            "INNER JOIN cards c ON c.card_id = t.card_id "
            "WHERE c.collection_id = ? "
            "ORDER BY t.transaction_date DESC, t.transaction_id DESC "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_recent(self: TransactionsRepository, limit: int = 20) -> list[Transaction]:
        """Las N transacciones más recientes globalmente."""
        rows = self.conn.execute(
            "SELECT transaction_id, card_id, operation, quantity, "
            "       transaction_date, exchange_event_id "
            "FROM transactions "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (limit,),
        ).fetchall()
        return [_row_to_txn(r) for r in rows]

    def list_by_date_range(
        self: TransactionsRepository,
        start: datetime,
        end: datetime,
        collection_id: int | None = None,
    ) -> list[Transaction]:
        """Transacciones en `[start, end]` (inclusivo).

        Si `collection_id` se provee, JOIN con cards y filtra por colección.
        """
        start_str = start.isoformat(sep=" ")
        end_str = end.isoformat(sep=" ")
        if collection_id is None:
            rows = self.conn.execute(
                "SELECT transaction_id, card_id, operation, quantity, "
                "       transaction_date, exchange_event_id "
                "FROM transactions "
                "WHERE transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (start_str, end_str),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT t.transaction_id, t.card_id, t.operation, t.quantity, "
                "       t.transaction_date, t.exchange_event_id "
                "FROM transactions t "
                "INNER JOIN cards c ON c.card_id = t.card_id "
                "WHERE t.transaction_date BETWEEN ? AND ? "
                "  AND c.collection_id = ? "
                "ORDER BY t.transaction_date DESC, t.transaction_id DESC",
                (start_str, end_str, collection_id),
            ).fetchall()
        return [_row_to_txn(r) for r in rows]
```

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

### [tests/__init__.py](tests/__init__.py)

_(archivo vacío)_

### [tests/architecture/__init__.py](tests/architecture/__init__.py)

_(archivo vacío)_

### [tests/architecture/test_layers.py](tests/architecture/test_layers.py)

```python
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
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
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

    assert not violations, "Imports cross-layer detectados:\n" + "\n".join(violations)


def test_all_expected_layers_have_files() -> None:
    """Sanity del harness: las 4 capas existen y al menos tienen `__init__.py`.

    Sin esto, una regresión en `_layer_of` o en la estructura del paquete
    haría que `parametrize` se quede vacío y el test pase silenciosamente.
    """
    layers_seen = {layer for _, layer in _LAYER_FILES}
    missing = EXPECTED_LAYERS - layers_seen
    assert not missing, (
        f"Capas sin archivos detectadas: {missing}. " f"Esto rompe el harness de tests de capas."
    )
```

### [tests/architecture/test_repo_return_contracts.py](tests/architecture/test_repo_return_contracts.py)

```python
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
```

### [tests/architecture/test_table_model_repo_parity.py](tests/architecture/test_table_model_repo_parity.py)

```python
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
```

### [tests/conftest.py](tests/conftest.py)

```python
"""Fixtures compartidas para todos los tests.

Fixtures expuestas:

- `db_conn`: conexión SQLite `:memory:` con la migración 001 (y futuras)
  aplicadas. Scope `function` — DB fresca por test, sin leakage entre
  casos. Construida vía el migrator real (no setup paralelo en SQL): si
  una migración rompe, los tests de repos se enteran inmediatamente.

Tests de migrator y de schema NO usan esta fixture (tienen las suyas o
manejan la conexión inline) para no acoplarse al estado pre-migrado.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


@pytest.fixture
def db_conn() -> Iterator[sqlite3.Connection]:
    """Conexión `:memory:` con todas las migraciones aplicadas."""
    conn = create_connection(":memory:")
    run_migrations(conn)
    try:
        yield conn
    finally:
        conn.close()
```

### [tests/core/__init__.py](tests/core/__init__.py)

_(archivo vacío)_

### [tests/core/db/__init__.py](tests/core/db/__init__.py)

_(archivo vacío)_

### [tests/core/db/test_migration_001_schema.py](tests/core/db/test_migration_001_schema.py)

```python
"""Smoke test del schema producido por la migración 001.

Aplica `001_initial.sql` sobre `:memory:` y verifica el shape final:
- `schema_version = 1`.
- Las 9 tablas esperadas existen.
- Cada tabla con PK subrogada usa `<entidad>_id INTEGER` AUTOINCREMENT.
- UNIQUE constraints sobre business keys.
- FKs granulares (inventory/card_images/transactions → card_id).
- CHECKs y CASCADE funcionan.
- Índices presentes.

No prueba el contenido de las queries de los repos — eso vive en
`tests/core/repositories/`. Acá solo validamos el schema.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations

EXPECTED_TABLES = {
    "schema_version",
    "app_settings",
    "codes_headers",
    "codes_lines",
    "collections",
    "cards",
    "inventory",
    "card_images",
    "transactions",
}

# Tablas con PK subrogada AUTOINCREMENT y nombre de columna esperado.
EXPECTED_SURROGATE_PKS = {
    "codes_headers": "code_header_id",
    "codes_lines": "code_line_id",
    "collections": "collection_id",
    "cards": "card_id",
    "inventory": "inventory_id",
    "card_images": "card_image_id",
    "transactions": "transaction_id",
}

EXPECTED_INDEXES = {
    "idx_codes_lines_order",
    "idx_cards_collection",
    "idx_card_images_found",
    "idx_transactions_date",
    "idx_transactions_card",
    "idx_transactions_exchange_event",
}


@pytest.fixture
def conn() -> sqlite3.Connection:
    """Conexión :memory: con migración 001 aplicada."""
    c = create_connection(":memory:")
    run_migrations(c)
    return c


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }


def _index_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
        ).fetchall()
    }


def _columns(conn: sqlite3.Connection, table: str) -> dict[str, sqlite3.Row]:
    return {row["name"]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _foreign_keys(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f"PRAGMA foreign_key_list({table})").fetchall())


def _index_list(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f"PRAGMA index_list({table})").fetchall())


def _is_unique_on(conn: sqlite3.Connection, table: str, expected_cols: tuple[str, ...]) -> bool:
    """True si existe un UNIQUE sobre exactamente esas columnas (en orden)."""
    for idx in _index_list(conn, table):
        if not idx["unique"]:
            continue
        cols = [r["name"] for r in conn.execute(f"PRAGMA index_info({idx['name']})").fetchall()]
        if tuple(cols) == expected_cols:
            return True
    return False


# ---------------------------------------------------------------------
# Versionado y existencia de tablas
# ---------------------------------------------------------------------


def test_schema_version_is_one(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    assert row["v"] == 1


def test_all_expected_tables_exist(conn: sqlite3.Connection) -> None:
    actual = _table_names(conn)
    missing = EXPECTED_TABLES - actual
    extra = actual - EXPECTED_TABLES - {"sqlite_sequence"}
    assert not missing, f"Tablas faltantes: {missing}"
    assert not extra, f"Tablas inesperadas: {extra}"


def test_all_expected_indexes_exist(conn: sqlite3.Connection) -> None:
    actual = _index_names(conn)
    missing = EXPECTED_INDEXES - actual
    assert not missing, f"Índices faltantes: {missing}"


# ---------------------------------------------------------------------
# PKs subrogadas + AUTOINCREMENT
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "table,pk_col",
    list(EXPECTED_SURROGATE_PKS.items()),
    ids=list(EXPECTED_SURROGATE_PKS.keys()),
)
def test_surrogate_pk_is_integer_and_autoincrement(
    conn: sqlite3.Connection, table: str, pk_col: str
) -> None:
    """Cada tabla con PK subrogada tiene `<x>_id INTEGER PK AUTOINCREMENT`.

    AUTOINCREMENT en SQLite se detecta porque crea filas en `sqlite_sequence`
    cuando se insertan filas. Probamos insertando una fila válida y verificando
    que `sqlite_sequence` registra la tabla.
    """
    cols = _columns(conn, table)
    assert pk_col in cols, f"{table}: falta columna PK {pk_col}"
    col = cols[pk_col]
    assert col["type"].upper() == "INTEGER", f"{table}.{pk_col} no es INTEGER"
    assert col["pk"] == 1, f"{table}.{pk_col} no es PRIMARY KEY"


def test_codes_headers_autoincrement_works(conn: sqlite3.Connection) -> None:
    """Smoke de AUTOINCREMENT real: insertar dos filas y verificar IDs incrementales."""
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("Test1", 5),
    )
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("Test2", 5),
    )
    rows = conn.execute(
        "SELECT code_header_id FROM codes_headers ORDER BY code_header_id"
    ).fetchall()
    ids = [r["code_header_id"] for r in rows]
    assert ids == [1, 2]


# ---------------------------------------------------------------------
# UNIQUE constraints sobre business keys
# ---------------------------------------------------------------------


def test_codes_lines_unique_on_header_code(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "codes_lines", ("code_header_id", "code_id"))


def test_cards_unique_on_business_key(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "cards", ("collection_id", "code_id", "card_number"))


def test_inventory_card_id_is_unique(conn: sqlite3.Connection) -> None:
    """inventory es 1:1 con cards via card_id UNIQUE."""
    assert _is_unique_on(conn, "inventory", ("card_id",))


def test_card_images_card_id_is_unique(conn: sqlite3.Connection) -> None:
    """card_images es 1:1 con cards via card_id UNIQUE."""
    assert _is_unique_on(conn, "card_images", ("card_id",))


def test_collections_name_is_unique(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "collections", ("collection_name",))


def test_codes_headers_name_is_unique(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "codes_headers", ("code_header_name",))


# ---------------------------------------------------------------------
# Foreign keys granulares (sec 2.5)
# ---------------------------------------------------------------------


def test_inventory_fk_targets_cards(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "inventory")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"
    assert fk["to"] == "card_id"
    assert fk["on_delete"] == "CASCADE"


def test_card_images_fk_targets_cards(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "card_images")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"
    assert fk["to"] == "card_id"
    assert fk["on_delete"] == "CASCADE"


def test_transactions_fk_targets_card_not_collection(
    conn: sqlite3.Connection,
) -> None:
    """sec 2.5: bitácoras apuntan a la entidad atómica, no al contenedor."""
    fks = _foreign_keys(conn, "transactions")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"


def test_cards_fk_targets_collections_with_cascade(
    conn: sqlite3.Connection,
) -> None:
    fks = _foreign_keys(conn, "cards")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "collections"
    assert fk["from"] == "collection_id"
    assert fk["on_delete"] == "CASCADE"


def test_codes_lines_fk_cascade_from_header(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "codes_lines")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "codes_headers"
    assert fk["on_delete"] == "CASCADE"


# ---------------------------------------------------------------------
# Columnas prohibidas que NO deben existir (sec 6 patrones prohibidos)
# ---------------------------------------------------------------------


def test_inventory_has_no_image_path(conn: sqlite3.Connection) -> None:
    """sec 6: única fuente del path es card_images, no inventory."""
    assert "image_path" not in _columns(conn, "inventory")


def test_inventory_has_no_locked_column(conn: sqlite3.Connection) -> None:
    """Locked era para exchanges con estado; en v0.2 no se persiste."""
    assert "locked" not in _columns(conn, "inventory")


def test_inventory_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    """sec 2.6: collection_id/code_id/card_number viven en cards, no en inventory."""
    cols = _columns(conn, "inventory")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"inventory.{forbidden} duplica un dato que vive en cards"


def test_card_images_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    cols = _columns(conn, "card_images")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"card_images.{forbidden} duplica un dato que vive en cards"


def test_transactions_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    cols = _columns(conn, "transactions")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"transactions.{forbidden} duplica un dato que vive en cards"


# ---------------------------------------------------------------------
# Columnas específicas relevantes
# ---------------------------------------------------------------------


def test_transactions_has_exchange_event_id(conn: sqlite3.Connection) -> None:
    """Agrupa transacciones que pertenecen al mismo intercambio."""
    cols = _columns(conn, "transactions")
    assert "exchange_event_id" in cols
    # Nullable: NULL cuando no es parte de un intercambio.
    assert cols["exchange_event_id"]["notnull"] == 0


def test_collections_has_album_layout_columns(conn: sqlite3.Connection) -> None:
    cols = _columns(conn, "collections")
    for c in ("album_columns", "album_rows", "album_orientation"):
        assert c in cols, f"collections.{c} faltante"


def test_collections_has_code_field_name(conn: sqlite3.Connection) -> None:
    """Label visible del campo de código por colección (UI metadata, no magic column)."""
    cols = _columns(conn, "collections")
    assert "code_field_name" in cols
    assert cols["code_field_name"]["notnull"] == 0


# ---------------------------------------------------------------------
# CHECK constraints y comportamiento runtime
# ---------------------------------------------------------------------


def _seed_minimal_card(conn: sqlite3.Connection) -> int:
    """Crea un universo + colección + card y retorna card_id."""
    conn.execute("INSERT INTO codes_headers (code_header_name) VALUES (?)", ("H",))
    header_id = conn.execute("SELECT code_header_id FROM codes_headers").fetchone()[0]
    conn.execute(
        "INSERT INTO collections (collection_name, card_count, code_header_id) VALUES (?, ?, ?)",
        ("C", 1, header_id),
    )
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) VALUES (?, ?, ?, ?)",
        (coll_id, "X", 1, "Test"),
    )
    card_id: int = conn.execute("SELECT card_id FROM cards").fetchone()[0]
    return card_id


def test_transactions_quantity_must_be_positive(conn: sqlite3.Connection) -> None:
    card_id = _seed_minimal_card(conn)
    with pytest.raises(sqlite3.IntegrityError, match="quantity"):
        conn.execute(
            "INSERT INTO transactions (card_id, operation, quantity) VALUES (?, 'alta', ?)",
            (card_id, 0),
        )


def test_transactions_operation_must_be_alta_or_baja(
    conn: sqlite3.Connection,
) -> None:
    card_id = _seed_minimal_card(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO transactions (card_id, operation, quantity) VALUES (?, 'foo', 1)",
            (card_id,),
        )


def test_collections_album_orientation_check(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT INTO codes_headers (code_header_name) VALUES (?)", ("H2",))
    header_id = conn.execute(
        "SELECT code_header_id FROM codes_headers WHERE code_header_name = 'H2'"
    ).fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, code_header_id, album_orientation) "
            "VALUES (?, ?, ?, ?)",
            ("BadOrient", 1, header_id, "diagonal"),
        )


def test_cards_unique_violation_raises(conn: sqlite3.Connection) -> None:
    _seed_minimal_card(conn)
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?)",
            (coll_id, "X", 1, "Dup"),
        )


def test_inventory_unique_card_id(conn: sqlite3.Connection) -> None:
    card_id = _seed_minimal_card(conn)
    conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 1))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 2))


def test_cascade_delete_collection_removes_cards_and_inventory(
    conn: sqlite3.Connection,
) -> None:
    card_id = _seed_minimal_card(conn)
    conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 3))
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    conn.execute("DELETE FROM collections WHERE collection_id = ?", (coll_id,))
    assert conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"] == 0
    assert conn.execute("SELECT COUNT(*) AS c FROM inventory").fetchone()["c"] == 0


def test_run_migrations_is_idempotent_on_real_schema(
    conn: sqlite3.Connection,
) -> None:
    """Re-aplicar la migración no debe fallar (no hay pendientes)."""
    final = run_migrations(conn)
    assert final == 1
```

### [tests/core/db/test_migrator_smoke.py](tests/core/db/test_migrator_smoke.py)

```python
"""Smoke tests del migrator y de la conexión.

Verifican el comportamiento básico del scaffold antes de que existan
migraciones reales (Prompt 1). Cuando la primera migración aterrice,
extender `legacy/v0_1/tests/core/db/test_migrator.py` como referencia.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import (
    _get_current_version,
    run_migrations,
)


def test_create_connection_enables_foreign_keys() -> None:
    """`PRAGMA foreign_keys` debe quedar en 1 al crear la conexión."""
    conn = create_connection(":memory:")
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_create_connection_uses_row_factory() -> None:
    """Las filas vienen como `sqlite3.Row` (acceso por nombre de columna)."""
    conn = create_connection(":memory:")
    row = conn.execute("SELECT 1 AS n").fetchone()
    assert isinstance(row, sqlite3.Row)
    assert row["n"] == 1


def test_get_current_version_returns_zero_when_table_absent() -> None:
    """En una DB virgen sin `schema_version`, la versión actual es 0."""
    conn = create_connection(":memory:")
    assert _get_current_version(conn) == 0


def test_run_migrations_with_empty_schema_dir_returns_zero(tmp_path) -> None:
    """`schema_dir` existente pero sin .sql: no crea schema_version, retorna 0."""
    conn = create_connection(":memory:")
    final = run_migrations(conn, schema_dir=tmp_path)
    assert final == 0
    # Verificar que no se creó la tabla schema_version (no había migración
    # 001 que la incluyera).
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert "schema_version" not in tables


def test_run_migrations_is_idempotent_with_empty_dir(tmp_path) -> None:
    """Correr migraciones dos veces sobre schema_dir vacío no rompe."""
    conn = create_connection(":memory:")
    first = run_migrations(conn, schema_dir=tmp_path)
    second = run_migrations(conn, schema_dir=tmp_path)
    assert first == second == 0


def test_run_migrations_raises_on_missing_schema_dir(tmp_path) -> None:
    """`schema_dir` inexistente debe lanzar FileNotFoundError descriptivo."""
    conn = create_connection(":memory:")
    missing = tmp_path / "no_existe"
    with pytest.raises(FileNotFoundError, match=str(missing.name)):
        run_migrations(conn, schema_dir=missing)


def test_run_migrations_applies_a_minimal_fake_migration(tmp_path) -> None:
    """End-to-end: una migración fake escrita en disco se aplica y bumpea schema_version.

    Sirve para validar que el pipeline (ordenamiento por número, lectura,
    `executescript`, verificación de schema_version) está bien armado,
    sin depender de las migraciones reales que va a aterrizar Prompt 1.
    """
    sql = (
        "CREATE TABLE schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ");\n"
        "INSERT INTO schema_version (version) VALUES (1);\n"
    )
    (tmp_path / "001_initial.sql").write_text(sql, encoding="utf-8")
    conn = create_connection(":memory:")
    final = run_migrations(conn, schema_dir=tmp_path)
    assert final == 1
    # Re-correr es idempotente.
    second = run_migrations(conn, schema_dir=tmp_path)
    assert second == 1


def test_run_migrations_fails_if_migration_does_not_bump_schema_version(
    tmp_path,
) -> None:
    """Una migración que no inserta en `schema_version` debe disparar RuntimeError."""
    bad_sql = (
        "CREATE TABLE schema_version ("
        "  version INTEGER PRIMARY KEY,"
        "  applied_at TEXT NOT NULL DEFAULT (datetime('now'))"
        ");\n"
        # Falta INSERT INTO schema_version → debe romper.
        "CREATE TABLE foo (id INTEGER PRIMARY KEY);\n"
    )
    (tmp_path / "001_no_bump.sql").write_text(bad_sql, encoding="utf-8")
    conn = create_connection(":memory:")
    with pytest.raises(RuntimeError, match="schema_version"):
        run_migrations(conn, schema_dir=tmp_path)
```

### [tests/core/models/__init__.py](tests/core/models/__init__.py)

_(archivo vacío)_

### [tests/core/models/test_app_setting.py](tests/core/models/test_app_setting.py)

```python
"""Tests del dataclass AppSetting (helpers de casteo).

El repo retorna `AppSetting | None` (CLAUDE.md sec 2.3 prohíbe que un
repo devuelva `str | None` o `int | None` crudo). Toda lógica de
casteo vive en el dataclass para que el caller pueda decidir si
quiere el string crudo o un tipo derivado.
"""

from __future__ import annotations

from collections_app.core.models.app_setting import AppSetting


def test_as_int_parses_valid_integer() -> None:
    s = AppSetting(key="max_retries", value="42")
    assert s.as_int() == 42


def test_as_int_returns_none_when_value_is_none() -> None:
    s = AppSetting(key="optional", value=None)
    assert s.as_int() is None


def test_as_int_returns_none_for_non_integer_string() -> None:
    s = AppSetting(key="bad", value="not-a-number")
    assert s.as_int() is None


def test_as_int_handles_negative_integers() -> None:
    s = AppSetting(key="offset", value="-5")
    assert s.as_int() == -5


def test_as_bool_true_for_truthy_strings() -> None:
    for value in ("1", "true", "True", "TRUE", "yes", "YES", "on"):
        assert AppSetting(key="k", value=value).as_bool() is True, value


def test_as_bool_false_for_falsy_strings() -> None:
    for value in ("0", "false", "False", "FALSE", "no", "NO", "off"):
        assert AppSetting(key="k", value=value).as_bool() is False, value


def test_as_bool_returns_none_when_value_is_none() -> None:
    s = AppSetting(key="k", value=None)
    assert s.as_bool() is None


def test_as_bool_returns_none_for_unknown_string() -> None:
    s = AppSetting(key="k", value="maybe")
    assert s.as_bool() is None


def test_as_bool_strips_whitespace() -> None:
    assert AppSetting(key="k", value="  true  ").as_bool() is True
```

### [tests/core/models/test_card.py](tests/core/models/test_card.py)

```python
"""Tests del dataclass Card."""

from __future__ import annotations

from collections_app.core.models.card import Card


def test_card_key_combines_code_and_number() -> None:
    card = Card(card_id=1, collection_id=1, code_id="ARG", card_number=24, card_name="Messi")
    assert card.card_key == "ARG-24"


def test_card_key_with_short_code() -> None:
    card = Card(card_id=2, collection_id=1, code_id="MR", card_number=1, card_name="X")
    assert card.card_key == "MR-1"


def test_card_id_can_be_none_pre_persistence() -> None:
    card = Card(card_id=None, collection_id=1, code_id="X", card_number=1, card_name="X")
    assert card.card_id is None
```

### [tests/core/models/test_card_image.py](tests/core/models/test_card_image.py)

```python
"""Tests del dataclass CardImage."""

from __future__ import annotations

from collections_app.core.models.card_image import CardImage


def test_card_image_minimal() -> None:
    img = CardImage(card_image_id=None, card_id=1, found_photo=False)
    assert img.image_source is None
    assert img.image_path is None
    assert img.generated_at is None


def test_card_image_with_all_fields() -> None:
    img = CardImage(
        card_image_id=10,
        card_id=1,
        found_photo=True,
        image_source="wikipedia",
        image_path="/tmp/x.png",
        generated_at="2026-05-05T10:00:00Z",
    )
    assert img.found_photo is True
    assert img.image_source == "wikipedia"
    assert img.image_path == "/tmp/x.png"
    assert img.generated_at == "2026-05-05T10:00:00Z"
```

### [tests/core/models/test_code_header.py](tests/core/models/test_code_header.py)

```python
"""Tests del dataclass CodeHeader."""

from __future__ import annotations

from collections_app.core.models.code_header import CodeHeader


def test_code_header_default_max_length_is_5() -> None:
    h = CodeHeader(code_header_id=None, code_header_name="Foo")
    assert h.code_max_length == 5


def test_code_header_with_explicit_max_length() -> None:
    h = CodeHeader(code_header_id=1, code_header_name="Foo", code_max_length=10)
    assert h.code_max_length == 10


def test_code_header_id_can_be_none_for_unsaved() -> None:
    h = CodeHeader(code_header_id=None, code_header_name="Unsaved")
    assert h.code_header_id is None
```

### [tests/core/models/test_code_line.py](tests/core/models/test_code_line.py)

```python
"""Tests del dataclass CodeLine."""

from __future__ import annotations

from collections_app.core.models.code_line import CodeLine


def test_code_line_default_order_is_zero() -> None:
    line = CodeLine(code_line_id=None, code_header_id=1, code_id="ARG", code_name="Argentina")
    assert line.code_order == 0


def test_code_line_id_can_be_none() -> None:
    line = CodeLine(code_line_id=None, code_header_id=1, code_id="ARG", code_name="Argentina")
    assert line.code_line_id is None


def test_code_line_with_explicit_order() -> None:
    line = CodeLine(
        code_line_id=5,
        code_header_id=1,
        code_id="MR",
        code_name="Mirage",
        code_order=10,
    )
    assert line.code_order == 10
```

### [tests/core/models/test_code_stats.py](tests/core/models/test_code_stats.py)

```python
"""Tests del aggregate CodeStats."""

from __future__ import annotations

from collections_app.core.models.aggregates.code_stats import CodeStats


def test_code_stats_holds_fields() -> None:
    s = CodeStats(code_id="ARG", code_name="Argentina", total=10, owned=4, percentage=40.0)
    assert s.code_id == "ARG"
    assert s.code_name == "Argentina"
    assert s.total == 10
    assert s.owned == 4
    assert s.percentage == 40.0
```

### [tests/core/models/test_collection.py](tests/core/models/test_collection.py)

```python
"""Tests del dataclass Collection."""

from __future__ import annotations

from collections_app.core.models.collection import Collection


def _minimal(**overrides: object) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": "Test",
        "card_count": 100,
        "requires_code": False,
        "code_field_name": None,
        "code_header_id": 1,
    }
    base.update(overrides)
    return Collection(**base)  # type: ignore[arg-type]


def test_collection_minimal_uses_album_defaults() -> None:
    c = _minimal()
    assert c.album_columns == 3
    assert c.album_rows == 4
    assert c.album_orientation == "portrait"


def test_collection_default_is_premium_is_false() -> None:
    c = _minimal()
    assert c.is_premium is False
    assert c.license_key_required is None


def test_collection_with_premium_and_license() -> None:
    c = _minimal(is_premium=True, license_key_required="hash123")
    assert c.is_premium is True
    assert c.license_key_required == "hash123"


def test_collection_with_landscape_album() -> None:
    c = _minimal(album_orientation="landscape", album_columns=2, album_rows=3)
    assert c.album_orientation == "landscape"
    assert c.album_columns == 2
    assert c.album_rows == 3
```

### [tests/core/models/test_inventory_item.py](tests/core/models/test_inventory_item.py)

```python
"""Tests del dataclass InventoryItem."""

from __future__ import annotations

from collections_app.core.models.inventory_item import InventoryItem


def test_is_owned_true_when_quantity_positive() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=1).is_owned is True
    assert InventoryItem(inventory_id=1, card_id=1, quantity=99).is_owned is True


def test_is_owned_false_when_quantity_zero() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=0).is_owned is False


def test_has_duplicates_true_when_quantity_above_one() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=2).has_duplicates is True


def test_has_duplicates_false_when_quantity_one_or_less() -> None:
    assert InventoryItem(inventory_id=1, card_id=1, quantity=1).has_duplicates is False
    assert InventoryItem(inventory_id=1, card_id=1, quantity=0).has_duplicates is False


def test_inventory_id_can_be_none_pre_persistence() -> None:
    item = InventoryItem(inventory_id=None, card_id=1, quantity=0)
    assert item.inventory_id is None
```

### [tests/core/models/test_transaction.py](tests/core/models/test_transaction.py)

```python
"""Tests del dataclass Transaction y OperationType."""

from __future__ import annotations

from datetime import datetime

from collections_app.core.models.transaction import OperationType, Transaction


def test_operation_type_values() -> None:
    assert OperationType.ALTA.value == "alta"
    assert OperationType.BAJA.value == "baja"


def test_operation_type_str_enum_compat() -> None:
    """OperationType es StrEnum: comparable a strings sin .value."""
    assert OperationType.ALTA == "alta"
    assert OperationType.BAJA == "baja"


def test_transaction_minimal_fields() -> None:
    txn = Transaction(
        transaction_id=None,
        card_id=1,
        operation=OperationType.ALTA,
        quantity=2,
        transaction_date=datetime(2026, 5, 5, 12, 0, 0),
    )
    assert txn.exchange_event_id is None  # default


def test_transaction_with_exchange_event_id() -> None:
    txn = Transaction(
        transaction_id=None,
        card_id=1,
        operation=OperationType.BAJA,
        quantity=1,
        transaction_date=datetime(2026, 5, 5),
        exchange_event_id=42,
    )
    assert txn.exchange_event_id == 42
```

### [tests/core/repositories/__init__.py](tests/core/repositories/__init__.py)

_(archivo vacío)_

### [tests/core/repositories/test_app_settings_repo.py](tests/core/repositories/test_app_settings_repo.py)

```python
"""Tests CRUD de AppSettingsRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.app_setting import AppSetting
from collections_app.core.repositories.app_settings_repo import AppSettingsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> AppSettingsRepository:
    return AppSettingsRepository(db_conn)


def test_get_returns_none_for_missing_key(repo: AppSettingsRepository) -> None:
    assert repo.get("missing") is None


def test_set_then_get_round_trips(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="theme", value="dark"))
    fetched = repo.get("theme")
    assert fetched is not None
    assert fetched.key == "theme"
    assert fetched.value == "dark"


def test_set_overwrites_existing_value(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="theme", value="dark"))
    repo.set(AppSetting(key="theme", value="light"))
    fetched = repo.get("theme")
    assert fetched is not None
    assert fetched.value == "light"


def test_set_can_store_none_value(repo: AppSettingsRepository) -> None:
    """value es nullable en el schema."""
    repo.set(AppSetting(key="optional", value=None))
    fetched = repo.get("optional")
    assert fetched is not None
    assert fetched.value is None


def test_delete_returns_true_when_existed(repo: AppSettingsRepository) -> None:
    repo.set(AppSetting(key="k", value="v"))
    assert repo.delete("k") is True
    assert repo.get("k") is None


def test_delete_returns_false_when_missing(repo: AppSettingsRepository) -> None:
    assert repo.delete("never_existed") is False


def test_list_all_empty(repo: AppSettingsRepository) -> None:
    assert repo.list_all() == []


def test_list_all_returns_all_entries_sorted_by_key(
    repo: AppSettingsRepository,
) -> None:
    repo.set(AppSetting(key="zebra", value="z"))
    repo.set(AppSetting(key="alpha", value="a"))
    repo.set(AppSetting(key="mike", value="m"))
    items = repo.list_all()
    assert [s.key for s in items] == ["alpha", "mike", "zebra"]
    assert all(isinstance(s, AppSetting) for s in items)
```

### [tests/core/repositories/test_base_repository.py](tests/core/repositories/test_base_repository.py)

```python
"""Smoke tests del BaseRepository y de la fixture `db_conn`.

Verifica que:
- `BaseRepository` guarda la conexión recibida en `self.conn`.
- `db_conn` aplica las migraciones (schema_version >= 1, FKs ON).
"""

from __future__ import annotations

import sqlite3

from collections_app.core.repositories.base import BaseRepository


def test_base_repository_stores_connection() -> None:
    conn = sqlite3.connect(":memory:")
    repo = BaseRepository(conn)
    assert repo.conn is conn


def test_db_conn_fixture_has_migrations_applied(
    db_conn: sqlite3.Connection,
) -> None:
    """La fixture aplica al menos la migración 001."""
    row = db_conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    assert row["v"] >= 1


def test_db_conn_fixture_has_foreign_keys_enabled(
    db_conn: sqlite3.Connection,
) -> None:
    result = db_conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_db_conn_fixture_provides_fresh_db_per_test_step1(
    db_conn: sqlite3.Connection,
) -> None:
    """Primer test: inserta y verifica que aparece."""
    db_conn.execute(
        "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?)", ("k", "v")
    )
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM app_settings").fetchone()
    assert rows["c"] == 1


def test_db_conn_fixture_provides_fresh_db_per_test_step2(
    db_conn: sqlite3.Connection,
) -> None:
    """Segundo test: la inserción del test anterior NO debe persistir."""
    rows = db_conn.execute("SELECT COUNT(*) AS c FROM app_settings").fetchone()
    assert rows["c"] == 0
```

### [tests/core/repositories/test_card_images_repo.py](tests/core/repositories/test_card_images_repo.py)

```python
"""Tests CRUD + queries de CardImagesRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.card_image import CardImage
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.card_images_repo import CardImagesRepository
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CardImagesRepository:
    return CardImagesRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make_card(cards_repo: CardsRepository, collection_id: int, n: int) -> int:
    saved = cards_repo.create(
        Card(
            card_id=None,
            collection_id=collection_id,
            code_id="X",
            card_number=n,
            card_name=f"X-{n}",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def test_get_by_card_id_returns_none_when_no_image(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.get_by_card_id(card_id) is None


def test_upsert_inserts_new(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=True,
            image_source="wikipedia",
            image_path="/tmp/a.png",
            generated_at="2026-05-05",
        )
    )
    assert saved.card_image_id is not None
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.image_source == "wikipedia"
    assert fetched.image_path == "/tmp/a.png"
    assert fetched.found_photo is True


def test_upsert_updates_existing_by_card_id(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=False,
            image_source="placeholder",
        )
    )
    repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=True,
            image_source="wikipedia",
            image_path="/tmp/new.png",
        )
    )
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.found_photo is True
    assert fetched.image_source == "wikipedia"
    assert fetched.image_path == "/tmp/new.png"


def test_upsert_violates_fk_when_card_not_exists(
    repo: CardImagesRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(CardImage(card_image_id=None, card_id=999, found_photo=False))


def test_delete_by_card_id_returns_true_when_existed(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=card_id, found_photo=False))
    assert repo.delete_by_card_id(card_id) is True
    assert repo.get_by_card_id(card_id) is None


def test_delete_by_card_id_returns_false_when_missing(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.delete_by_card_id(card_id) is False


def test_list_by_collection_filters_correctly(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=True))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_get_pending_excludes_cards_with_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    pending = repo.get_pending(collection_id)
    pending_ids = {c.card_id for c in pending}
    assert b in pending_ids
    assert a not in pending_ids


def test_get_pending_returns_card_dataclasses(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    pending = repo.get_pending(collection_id)
    assert all(isinstance(c, Card) for c in pending)


def test_get_placeholders_only_found_photo_false(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=False))
    placeholders = repo.get_placeholders(collection_id)
    placeholder_card_ids = {p.card_id for p in placeholders}
    assert b in placeholder_card_ids
    assert a not in placeholder_card_ids


def test_count_with_photo_only_found_true(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=c, found_photo=False))
    assert repo.count_with_photo(collection_id) == 2


def test_count_total_generated_includes_placeholders(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=False))
    _ = c  # card sin imagen, no cuenta
    assert repo.count_total_generated(collection_id) == 2


def test_count_zero_when_no_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    assert repo.count_with_photo(collection_id) == 0
    assert repo.count_total_generated(collection_id) == 0


def test_card_delete_cascades_to_card_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    """Borrar la card debe borrar la entry en card_images (CASCADE)."""
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=card_id, found_photo=True))
    cards_repo.delete_by_id(card_id)
    assert repo.get_by_card_id(card_id) is None
```

### [tests/core/repositories/test_cards_repo.py](tests/core/repositories/test_cards_repo.py)

```python
"""Tests CRUD + queries específicas de CardsRepository (sin stats — paso 8)."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    collections = CollectionsRepository(db_conn)
    c = collections.create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make(collection_id: int, **overrides: object) -> Card:
    base = {
        "card_id": None,
        "collection_id": collection_id,
        "code_id": "X",
        "card_number": 1,
        "card_name": "Test",
    }
    base.update(overrides)
    return Card(**base)  # type: ignore[arg-type]


def test_list_by_collection_empty(repo: CardsRepository, collection_id: int) -> None:
    assert repo.list_by_collection(collection_id) == []


def test_create_returns_card_with_id(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    assert saved.card_number == 1


def test_create_violates_unique_business_key(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="X", card_number=1))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(collection_id, code_id="X", card_number=1))


def test_get_by_id_returns_card(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_name="Hello"))
    assert saved.card_id is not None
    fetched = repo.get_by_id(saved.card_id)
    assert fetched is not None
    assert fetched.card_name == "Hello"


def test_get_by_id_returns_none_for_missing(repo: CardsRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_business_key_returns_card(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="ARG", card_number=24, card_name="Messi"))
    fetched = repo.get(collection_id, "ARG", 24)
    assert fetched is not None
    assert fetched.card_name == "Messi"


def test_get_by_business_key_returns_none_for_missing(
    repo: CardsRepository, collection_id: int
) -> None:
    assert repo.get(collection_id, "X", 999) is None


def test_list_by_collection_orders_by_code_then_number(
    repo: CardsRepository, collection_id: int
) -> None:
    repo.create(_make(collection_id, code_id="B", card_number=2, card_name="b2"))
    repo.create(_make(collection_id, code_id="A", card_number=1, card_name="a1"))
    repo.create(_make(collection_id, code_id="A", card_number=2, card_name="a2"))
    items = repo.list_by_collection(collection_id)
    assert [(c.code_id, c.card_number) for c in items] == [
        ("A", 1),
        ("A", 2),
        ("B", 2),
    ]


def test_list_by_collection_only_returns_that_collections_cards(
    repo: CardsRepository, collection_id: int, db_conn: sqlite3.Connection
) -> None:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="OtherH"))
    assert h.code_header_id is not None
    other = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OtherC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert other.collection_id is not None
    repo.create(_make(collection_id, code_id="X", card_number=1))
    repo.create(_make(other.collection_id, code_id="X", card_number=1))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].collection_id == collection_id


def test_list_by_code_filters_correctly(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="A", card_number=1))
    repo.create(_make(collection_id, code_id="A", card_number=2))
    repo.create(_make(collection_id, code_id="B", card_number=1))
    items = repo.list_by_code(collection_id, "A")
    assert [c.card_number for c in items] == [1, 2]


def test_find_by_number_zero_matches(repo: CardsRepository, collection_id: int) -> None:
    assert repo.find_by_number(collection_id, 999) == []


def test_find_by_number_one_match(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, code_id="A", card_number=42, card_name="x"))
    items = repo.find_by_number(collection_id, 42)
    assert len(items) == 1
    assert items[0].code_id == "A"


def test_find_by_number_multiple_matches(repo: CardsRepository, collection_id: int) -> None:
    """Mismo número en distintos códigos: retorna todos ordenados por code_id."""
    repo.create(_make(collection_id, code_id="B", card_number=10))
    repo.create(_make(collection_id, code_id="A", card_number=10))
    repo.create(_make(collection_id, code_id="C", card_number=10))
    items = repo.find_by_number(collection_id, 10)
    assert [c.code_id for c in items] == ["A", "B", "C"]


def test_count_by_collection(repo: CardsRepository, collection_id: int) -> None:
    assert repo.count_by_collection(collection_id) == 0
    repo.create(_make(collection_id, card_number=1))
    repo.create(_make(collection_id, code_id="Y", card_number=2))
    assert repo.count_by_collection(collection_id) == 2


def test_upsert_inserts_when_new(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.upsert(_make(collection_id, card_number=5, card_name="V1"))
    assert saved.card_id is not None
    fetched = repo.get(collection_id, "X", 5)
    assert fetched is not None
    assert fetched.card_name == "V1"


def test_upsert_updates_on_conflict(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, card_number=5, card_name="Old"))
    repo.upsert(_make(collection_id, card_number=5, card_name="New"))
    fetched = repo.get(collection_id, "X", 5)
    assert fetched is not None
    assert fetched.card_name == "New"


def test_bulk_upsert_returns_count(repo: CardsRepository, collection_id: int) -> None:
    cards = [_make(collection_id, card_number=i) for i in range(1, 6)]
    count = repo.bulk_upsert(cards)
    assert count == 5
    assert repo.count_by_collection(collection_id) == 5


def test_bulk_upsert_empty_list_returns_zero(repo: CardsRepository) -> None:
    assert repo.bulk_upsert([]) == 0


def test_bulk_upsert_updates_existing(repo: CardsRepository, collection_id: int) -> None:
    repo.create(_make(collection_id, card_number=1, card_name="Old1"))
    repo.create(_make(collection_id, card_number=2, card_name="Old2"))
    new = [
        _make(collection_id, card_number=1, card_name="New1"),
        _make(collection_id, card_number=2, card_name="New2"),
        _make(collection_id, card_number=3, card_name="New3"),
    ]
    repo.bulk_upsert(new)
    assert repo.count_by_collection(collection_id) == 3
    one = repo.get(collection_id, "X", 1)
    assert one is not None
    assert one.card_name == "New1"


def test_delete_by_id_returns_true_when_existed(repo: CardsRepository, collection_id: int) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    assert repo.delete_by_id(saved.card_id) is True
    assert repo.get_by_id(saved.card_id) is None


def test_delete_by_id_returns_false_when_missing(repo: CardsRepository) -> None:
    assert repo.delete_by_id(999) is False


def test_delete_by_id_cascades_to_inventory(
    repo: CardsRepository, collection_id: int, db_conn: sqlite3.Connection
) -> None:
    saved = repo.create(_make(collection_id, card_number=1))
    assert saved.card_id is not None
    db_conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (saved.card_id, 3))
    repo.delete_by_id(saved.card_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM inventory WHERE card_id = ?", (saved.card_id,)
    ).fetchone()
    assert remaining["c"] == 0
```

### [tests/core/repositories/test_cards_repo_stats.py](tests/core/repositories/test_cards_repo_stats.py)

```python
"""Tests de CardsRepository.get_stats_by_code (aggregate query)."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.aggregates.code_stats import CodeStats
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def fixture_setup(
    db_conn: sqlite3.Connection,
) -> tuple[int, int]:
    """Crea header con codes_lines + colección. Retorna (collection_id, header_id)."""
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    lines = CodeLinesRepository(db_conn)
    lines.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="ARG",
            code_name="Argentina",
            code_order=2,
        )
    )
    lines.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="BRA",
            code_name="Brasil",
            code_order=1,
        )
    )
    collections = CollectionsRepository(db_conn)
    c = collections.create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id, h.code_header_id


def _create_card(
    db_conn: sqlite3.Connection,
    collection_id: int,
    code_id: str,
    card_number: int,
    quantity: int = 0,
) -> int:
    """Crea card y opcionalmente inventory; retorna card_id."""
    cur = db_conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) " "VALUES (?, ?, ?, ?)",
        (collection_id, code_id, card_number, f"{code_id}-{card_number}"),
    )
    card_id = cur.lastrowid
    assert card_id is not None
    if quantity > 0:
        db_conn.execute(
            "INSERT INTO inventory (card_id, quantity) VALUES (?, ?)",
            (card_id, quantity),
        )
    return card_id


def test_get_stats_by_code_empty_collection(
    repo: CardsRepository, fixture_setup: tuple[int, int]
) -> None:
    collection_id, _ = fixture_setup
    assert repo.get_stats_by_code(collection_id) == []


def test_get_stats_by_code_returns_dataclasses(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    items = repo.get_stats_by_code(collection_id)
    assert all(isinstance(s, CodeStats) for s in items)


def test_get_stats_groups_by_code_id_with_counts(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """Para ARG: 3 cards total, 2 owned (qty>0). Para BRA: 2 total, 0 owned."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    _create_card(db_conn, collection_id, "ARG", 2, quantity=3)
    _create_card(db_conn, collection_id, "ARG", 3, quantity=0)
    _create_card(db_conn, collection_id, "BRA", 1)
    _create_card(db_conn, collection_id, "BRA", 2)
    items = repo.get_stats_by_code(collection_id)
    by_code = {s.code_id: s for s in items}
    assert by_code["ARG"].total == 3
    assert by_code["ARG"].owned == 2
    assert by_code["BRA"].total == 2
    assert by_code["BRA"].owned == 0


def test_get_stats_percentage_calculation(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1, quantity=1)
    _create_card(db_conn, collection_id, "ARG", 2, quantity=2)
    _create_card(db_conn, collection_id, "ARG", 3, quantity=0)
    _create_card(db_conn, collection_id, "ARG", 4, quantity=0)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.total == 4
    assert arg.owned == 2
    assert arg.percentage == 50.0


def test_get_stats_resolves_code_name_from_codes_lines(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """code_name debe venir de codes_lines, no del code_id."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.code_name == "Argentina"


def test_get_stats_falls_back_to_code_id_when_no_codes_lines_match(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """Card con un code_id que no está en codes_lines: code_name = code_id."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ZZZ", 1)
    items = repo.get_stats_by_code(collection_id)
    zzz = next(s for s in items if s.code_id == "ZZZ")
    assert zzz.code_name == "ZZZ"


def test_get_stats_orders_by_code_order_then_code_id(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    """BRA tiene code_order=1, ARG=2 → BRA primero."""
    collection_id, _ = fixture_setup
    _create_card(db_conn, collection_id, "ARG", 1)
    _create_card(db_conn, collection_id, "BRA", 1)
    items = repo.get_stats_by_code(collection_id)
    assert [s.code_id for s in items] == ["BRA", "ARG"]


def test_get_stats_only_counts_target_collection(
    repo: CardsRepository,
    fixture_setup: tuple[int, int],
    db_conn: sqlite3.Connection,
) -> None:
    collection_id, header_id = fixture_setup
    other = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="Other",
            card_count=10,
            requires_code=True,
            code_field_name="País",
            code_header_id=header_id,
        )
    )
    assert other.collection_id is not None
    _create_card(db_conn, collection_id, "ARG", 1)
    _create_card(db_conn, other.collection_id, "ARG", 1)
    items = repo.get_stats_by_code(collection_id)
    arg = next(s for s in items if s.code_id == "ARG")
    assert arg.total == 1


def test_get_stats_handles_zero_total_percentage(
    repo: CardsRepository, fixture_setup: tuple[int, int]
) -> None:
    """Sin cards, get_stats retorna lista vacía (no hay división por cero)."""
    collection_id, _ = fixture_setup
    items = repo.get_stats_by_code(collection_id)
    assert items == []
```

### [tests/core/repositories/test_code_headers_repo.py](tests/core/repositories/test_code_headers_repo.py)

```python
"""Tests CRUD de CodeHeadersRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CodeHeadersRepository:
    return CodeHeadersRepository(db_conn)


def test_list_all_empty(repo: CodeHeadersRepository) -> None:
    assert repo.list_all() == []


def test_create_returns_header_with_id_populated(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="FIFA"))
    assert created.code_header_id is not None
    assert created.code_header_name == "FIFA"


def test_create_assigns_unique_incremental_ids(repo: CodeHeadersRepository) -> None:
    a = repo.create(CodeHeader(code_header_id=None, code_header_name="A"))
    b = repo.create(CodeHeader(code_header_id=None, code_header_name="B"))
    assert a.code_header_id != b.code_header_id


def test_create_violates_unique_name(repo: CodeHeadersRepository) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Dup"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(CodeHeader(code_header_id=None, code_header_name="Dup"))


def test_get_by_id_returns_header(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="X", code_max_length=8))
    assert created.code_header_id is not None
    fetched = repo.get_by_id(created.code_header_id)
    assert fetched is not None
    assert fetched.code_header_name == "X"
    assert fetched.code_max_length == 8


def test_get_by_id_returns_none_for_missing(repo: CodeHeadersRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_header(repo: CodeHeadersRepository) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Magic"))
    fetched = repo.get_by_name("Magic")
    assert fetched is not None
    assert fetched.code_header_name == "Magic"


def test_get_by_name_is_case_sensitive(repo: CodeHeadersRepository) -> None:
    """get_by_name no normaliza case (matchea exacto)."""
    repo.create(CodeHeader(code_header_id=None, code_header_name="Magic"))
    assert repo.get_by_name("MAGIC") is None
    assert repo.get_by_name("magic") is None


def test_get_by_name_returns_none_for_missing(repo: CodeHeadersRepository) -> None:
    assert repo.get_by_name("ghost") is None


def test_update_changes_name_and_max_length(repo: CodeHeadersRepository) -> None:
    created = repo.create(
        CodeHeader(code_header_id=None, code_header_name="Old", code_max_length=3)
    )
    updated = repo.update(
        CodeHeader(
            code_header_id=created.code_header_id,
            code_header_name="New",
            code_max_length=7,
        )
    )
    assert updated.code_header_name == "New"
    assert updated.code_max_length == 7
    fetched = repo.get_by_id(created.code_header_id) if created.code_header_id else None
    assert fetched is not None
    assert fetched.code_header_name == "New"


def test_update_requires_id(repo: CodeHeadersRepository) -> None:
    with pytest.raises(ValueError, match="code_header_id"):
        repo.update(CodeHeader(code_header_id=None, code_header_name="X"))


def test_delete_returns_true_when_existed(repo: CodeHeadersRepository) -> None:
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="X"))
    assert created.code_header_id is not None
    assert repo.delete(created.code_header_id) is True
    assert repo.get_by_id(created.code_header_id) is None


def test_delete_returns_false_when_missing(repo: CodeHeadersRepository) -> None:
    assert repo.delete(999) is False


def test_delete_cascades_to_codes_lines(
    repo: CodeHeadersRepository, db_conn: sqlite3.Connection
) -> None:
    """Borrar header debe borrar sus codes_lines (FK ON DELETE CASCADE)."""
    created = repo.create(CodeHeader(code_header_id=None, code_header_name="Casc"))
    assert created.code_header_id is not None
    db_conn.execute(
        "INSERT INTO codes_lines (code_header_id, code_id, code_name) VALUES (?, ?, ?)",
        (created.code_header_id, "ARG", "Argentina"),
    )
    repo.delete(created.code_header_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM codes_lines WHERE code_header_id = ?",
        (created.code_header_id,),
    ).fetchone()
    assert remaining["c"] == 0


def test_list_all_returns_headers_sorted_by_name(
    repo: CodeHeadersRepository,
) -> None:
    repo.create(CodeHeader(code_header_id=None, code_header_name="Zebra"))
    repo.create(CodeHeader(code_header_id=None, code_header_name="Alpha"))
    repo.create(CodeHeader(code_header_id=None, code_header_name="Mike"))
    items = repo.list_all()
    assert [h.code_header_name for h in items] == ["Alpha", "Mike", "Zebra"]
    assert all(isinstance(h, CodeHeader) for h in items)
```

### [tests/core/repositories/test_code_lines_repo.py](tests/core/repositories/test_code_lines_repo.py)

```python
"""Tests CRUD de CodeLinesRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CodeLinesRepository:
    return CodeLinesRepository(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    """Crea un header y retorna su id (las lines lo necesitan como FK)."""
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def test_list_by_header_empty(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.list_by_header(header_id) == []


def test_upsert_inserts_new_line(repo: CodeLinesRepository, header_id: int) -> None:
    line = CodeLine(
        code_line_id=None, code_header_id=header_id, code_id="ARG", code_name="Argentina"
    )
    saved = repo.upsert(line)
    assert saved.code_line_id is not None
    assert saved.code_id == "ARG"


def test_upsert_updates_existing_by_business_key(repo: CodeLinesRepository, header_id: int) -> None:
    """Upsert sobre (code_header_id, code_id) reemplaza nombre y orden."""
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="ARG",
            code_name="Old",
            code_order=1,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="ARG",
            code_name="New",
            code_order=5,
        )
    )
    line = repo.get(header_id, "ARG")
    assert line is not None
    assert line.code_name == "New"
    assert line.code_order == 5


def test_get_returns_line(repo: CodeLinesRepository, header_id: int) -> None:
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="MR",
            code_name="Mirage",
        )
    )
    fetched = repo.get(header_id, "MR")
    assert fetched is not None
    assert fetched.code_name == "Mirage"


def test_get_returns_none_for_missing(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.get(header_id, "ZZZ") is None


def test_get_by_id_returns_line(repo: CodeLinesRepository, header_id: int) -> None:
    saved = repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="X",
            code_name="X-name",
        )
    )
    assert saved.code_line_id is not None
    fetched = repo.get_by_id(saved.code_line_id)
    assert fetched is not None
    assert fetched.code_id == "X"


def test_get_by_id_returns_none_for_missing(repo: CodeLinesRepository) -> None:
    assert repo.get_by_id(999) is None


def test_delete_returns_true_when_existed(repo: CodeLinesRepository, header_id: int) -> None:
    repo.upsert(CodeLine(code_line_id=None, code_header_id=header_id, code_id="A", code_name="A"))
    assert repo.delete(header_id, "A") is True
    assert repo.get(header_id, "A") is None


def test_delete_returns_false_when_missing(repo: CodeLinesRepository, header_id: int) -> None:
    assert repo.delete(header_id, "ghost") is False


def test_list_by_header_orders_by_code_order_then_code_id(
    repo: CodeLinesRepository, header_id: int
) -> None:
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="C",
            code_name="C",
            code_order=2,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="A",
            code_name="A",
            code_order=2,
        )
    )
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=header_id,
            code_id="B",
            code_name="B",
            code_order=1,
        )
    )
    items = repo.list_by_header(header_id)
    # order=1 first, then order=2 ordered alphabetically by code_id.
    assert [i.code_id for i in items] == ["B", "A", "C"]


def test_list_by_header_only_returns_that_headers_lines(
    repo: CodeLinesRepository,
    header_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    headers = CodeHeadersRepository(db_conn)
    other = headers.create(CodeHeader(code_header_id=None, code_header_name="Other"))
    assert other.code_header_id is not None
    repo.upsert(CodeLine(code_line_id=None, code_header_id=header_id, code_id="A", code_name="A"))
    repo.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=other.code_header_id,
            code_id="B",
            code_name="B",
        )
    )
    items = repo.list_by_header(header_id)
    assert len(items) == 1
    assert items[0].code_id == "A"


def test_reorder_assigns_orders_starting_at_one(repo: CodeLinesRepository, header_id: int) -> None:
    """reorder asigna code_order = índice 1-based según la lista provista."""
    for code_id in ("A", "B", "C"):
        repo.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=header_id,
                code_id=code_id,
                code_name=code_id,
            )
        )
    repo.reorder(header_id, ["B", "A", "C"])
    items = repo.list_by_header(header_id)
    assert [(i.code_id, i.code_order) for i in items] == [
        ("B", 1),
        ("A", 2),
        ("C", 3),
    ]


def test_reorder_ignores_codes_not_in_list(repo: CodeLinesRepository, header_id: int) -> None:
    """Códigos no incluidos en la lista mantienen su order anterior."""
    for code_id, order in (("A", 5), ("B", 6), ("C", 7)):
        repo.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=header_id,
                code_id=code_id,
                code_name=code_id,
                code_order=order,
            )
        )
    repo.reorder(header_id, ["A", "C"])  # B no se toca
    b = repo.get(header_id, "B")
    assert b is not None
    assert b.code_order == 6
```

### [tests/core/repositories/test_collections_repo.py](tests/core/repositories/test_collections_repo.py)

```python
"""Tests CRUD de CollectionsRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CollectionsRepository:
    return CollectionsRepository(db_conn)


@pytest.fixture
def header_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    return h.code_header_id


def _make(header_id: int, **overrides: object) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": "Test",
        "card_count": 100,
        "requires_code": False,
        "code_field_name": None,
        "code_header_id": header_id,
    }
    base.update(overrides)
    return Collection(**base)  # type: ignore[arg-type]


def test_list_all_empty(repo: CollectionsRepository) -> None:
    assert repo.list_all() == []


def test_create_returns_collection_with_id(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id, collection_name="FIFA"))
    assert saved.collection_id is not None
    assert saved.collection_name == "FIFA"


def test_create_violates_unique_name(repo: CollectionsRepository, header_id: int) -> None:
    repo.create(_make(header_id, collection_name="Dup"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(header_id, collection_name="Dup"))


def test_create_persists_album_defaults(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id))
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.album_columns == 3
    assert fetched.album_rows == 4
    assert fetched.album_orientation == "portrait"


def test_create_persists_album_overrides(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="Land",
            album_columns=2,
            album_rows=3,
            album_orientation="landscape",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.album_columns == 2
    assert fetched.album_rows == 3
    assert fetched.album_orientation == "landscape"


def test_create_persists_premium_and_license(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="Pro",
            is_premium=True,
            license_key_required="hash",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.is_premium is True
    assert fetched.license_key_required == "hash"


def test_create_persists_requires_code_and_field_name(
    repo: CollectionsRepository, header_id: int
) -> None:
    saved = repo.create(
        _make(
            header_id,
            collection_name="WithCode",
            requires_code=True,
            code_field_name="Set",
        )
    )
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.requires_code is True
    assert fetched.code_field_name == "Set"


def test_create_violates_album_orientation_check(
    repo: CollectionsRepository, header_id: int
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_make(header_id, album_orientation="diagonal"))


def test_get_by_id_returns_none_for_missing(repo: CollectionsRepository) -> None:
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_collection(repo: CollectionsRepository, header_id: int) -> None:
    repo.create(_make(header_id, collection_name="Magic"))
    fetched = repo.get_by_name("Magic")
    assert fetched is not None
    assert fetched.collection_name == "Magic"


def test_get_by_name_returns_none_for_missing(
    repo: CollectionsRepository,
) -> None:
    assert repo.get_by_name("ghost") is None


def test_update_changes_card_count(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id, card_count=100))
    updated = repo.update(
        Collection(
            collection_id=saved.collection_id,
            collection_name=saved.collection_name,
            card_count=200,
            requires_code=saved.requires_code,
            code_field_name=saved.code_field_name,
            code_header_id=saved.code_header_id,
        )
    )
    assert updated.card_count == 200
    fetched = repo.get_by_id(saved.collection_id) if saved.collection_id else None
    assert fetched is not None
    assert fetched.card_count == 200


def test_update_requires_id(repo: CollectionsRepository, header_id: int) -> None:
    with pytest.raises(ValueError, match="collection_id"):
        repo.update(_make(header_id))


def test_delete_returns_true_when_existed(repo: CollectionsRepository, header_id: int) -> None:
    saved = repo.create(_make(header_id))
    assert saved.collection_id is not None
    assert repo.delete(saved.collection_id) is True
    assert repo.get_by_id(saved.collection_id) is None


def test_delete_returns_false_when_missing(repo: CollectionsRepository) -> None:
    assert repo.delete(999) is False


def test_delete_cascades_to_cards(
    repo: CollectionsRepository, header_id: int, db_conn: sqlite3.Connection
) -> None:
    saved = repo.create(_make(header_id))
    assert saved.collection_id is not None
    db_conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) " "VALUES (?, ?, ?, ?)",
        (saved.collection_id, "X", 1, "Test"),
    )
    repo.delete(saved.collection_id)
    remaining = db_conn.execute(
        "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
        (saved.collection_id,),
    ).fetchone()
    assert remaining["c"] == 0


def test_list_all_returns_collections_sorted_by_name(
    repo: CollectionsRepository, header_id: int
) -> None:
    repo.create(_make(header_id, collection_name="Zebra"))
    repo.create(_make(header_id, collection_name="Alpha"))
    repo.create(_make(header_id, collection_name="Mike"))
    items = repo.list_all()
    assert [c.collection_name for c in items] == ["Alpha", "Mike", "Zebra"]
    assert all(isinstance(c, Collection) for c in items)
```

### [tests/core/repositories/test_inventory_repo.py](tests/core/repositories/test_inventory_repo.py)

```python
"""Tests CRUD + queries específicas de InventoryRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> InventoryRepository:
    return InventoryRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    headers = CodeHeadersRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make_card(cards_repo: CardsRepository, collection_id: int, n: int) -> int:
    saved = cards_repo.create(
        Card(
            card_id=None,
            collection_id=collection_id,
            code_id="X",
            card_number=n,
            card_name=f"X-{n}",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def test_get_by_card_id_returns_none_when_no_inventory(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.get_by_card_id(card_id) is None


def test_upsert_inserts_new(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=3))
    assert saved.inventory_id is not None
    assert saved.quantity == 3


def test_upsert_updates_existing_by_card_id(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=3))
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=7))
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.quantity == 7


def test_upsert_violates_fk_when_card_not_exists(
    repo: InventoryRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(InventoryItem(inventory_id=None, card_id=999, quantity=1))


def test_adjust_quantity_creates_entry_when_missing(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    item = repo.adjust_quantity(card_id, 3)
    assert item.quantity == 3
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.quantity == 3


def test_adjust_quantity_increments(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=5))
    item = repo.adjust_quantity(card_id, 3)
    assert item.quantity == 8


def test_adjust_quantity_decrements(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=5))
    item = repo.adjust_quantity(card_id, -2)
    assert item.quantity == 3


def test_list_by_collection_filters_correctly(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    """Solo retorna inventory cuyas cards pertenecen a esa colección."""
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=5))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_owned_excludes_zero_quantity(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=0))
    items = repo.list_owned(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_duplicates_only_above_one(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=1))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=c, quantity=5))
    items = repo.list_duplicates(collection_id)
    card_ids = {i.card_id for i in items}
    assert card_ids == {b, c}


def test_get_top_duplicates_sorted_desc_with_limit(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    for n, qty in enumerate([2, 5, 3, 7, 4], start=1):
        card_id = _make_card(cards_repo, collection_id, n)
        repo.upsert(InventoryItem(inventory_id=None, card_id=card_id, quantity=qty))
    top = repo.get_top_duplicates(collection_id, limit=3)
    assert [i.quantity for i in top] == [7, 5, 4]


def test_list_missing_includes_cards_with_zero_quantity(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=2))
    repo.upsert(InventoryItem(inventory_id=None, card_id=b, quantity=0))
    items = repo.list_missing(collection_id)
    card_ids = {c.card_id for c in items}
    assert b in card_ids
    assert a not in card_ids


def test_list_missing_includes_cards_without_inventory_entry(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(InventoryItem(inventory_id=None, card_id=a, quantity=3))
    items = repo.list_missing(collection_id)
    card_ids = {c.card_id for c in items}
    assert b in card_ids
    assert a not in card_ids


def test_list_missing_returns_card_dataclasses(
    repo: InventoryRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    items = repo.list_missing(collection_id)
    assert all(isinstance(c, Card) for c in items)
```

### [tests/core/repositories/test_transactions_repo.py](tests/core/repositories/test_transactions_repo.py)

```python
"""Tests CRUD + queries de TransactionsRepository."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.transaction import OperationType, Transaction
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> TransactionsRepository:
    return TransactionsRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make_card(cards_repo: CardsRepository, collection_id: int, n: int) -> int:
    saved = cards_repo.create(
        Card(
            card_id=None,
            collection_id=collection_id,
            code_id="X",
            card_number=n,
            card_name=f"X-{n}",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def _make_txn(
    card_id: int,
    operation: OperationType = OperationType.ALTA,
    quantity: int = 1,
    when: datetime | None = None,
    exchange_event_id: int | None = None,
) -> Transaction:
    return Transaction(
        transaction_id=None,
        card_id=card_id,
        operation=operation,
        quantity=quantity,
        transaction_date=when or datetime(2026, 5, 5, 12, 0, 0),
        exchange_event_id=exchange_event_id,
    )


def test_log_returns_txn_with_id_populated(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.log(_make_txn(card_id))
    assert saved.transaction_id is not None
    assert saved.card_id == card_id


def test_log_violates_quantity_check_when_zero(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    with pytest.raises(sqlite3.IntegrityError):
        repo.log(_make_txn(card_id, quantity=0))


def test_log_violates_fk_when_card_not_exists(
    repo: TransactionsRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.log(_make_txn(999))


def test_log_persists_exchange_event_id(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.log(_make_txn(card_id, exchange_event_id=77))
    assert saved.exchange_event_id == 77
    assert saved.transaction_id is not None
    fetched = repo.list_by_card(card_id)
    assert fetched[0].exchange_event_id == 77


def test_list_by_card_returns_transactions_desc(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, quantity=1, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(card_id, quantity=2, when=datetime(2026, 5, 3)))
    repo.log(_make_txn(card_id, quantity=3, when=datetime(2026, 5, 2)))
    items = repo.list_by_card(card_id)
    assert [t.quantity for t in items] == [2, 3, 1]


def test_list_by_card_respects_limit(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    for i in range(5):
        repo.log(_make_txn(card_id, when=datetime(2026, 5, i + 1)))
    items = repo.list_by_card(card_id, limit=3)
    assert len(items) == 3


def test_list_by_collection_joins_cards(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    repo.log(_make_txn(a))
    repo.log(_make_txn(b))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_list_recent_globally_returns_most_recent_first(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.log(_make_txn(a, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(b, when=datetime(2026, 5, 5)))
    repo.log(_make_txn(a, when=datetime(2026, 5, 3)))
    items = repo.list_recent(limit=10)
    dates = [t.transaction_date for t in items]
    assert dates == sorted(dates, reverse=True)


def test_list_by_date_range_inclusive(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 1)))
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 5)))
    repo.log(_make_txn(card_id, when=datetime(2026, 5, 10)))
    items = repo.list_by_date_range(start=datetime(2026, 5, 5), end=datetime(2026, 5, 10))
    assert len(items) == 2


def test_list_by_date_range_filters_by_collection_when_provided(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    when = datetime(2026, 5, 5)
    repo.log(_make_txn(a, when=when))
    repo.log(_make_txn(b, when=when))
    items = repo.list_by_date_range(
        start=datetime(2026, 5, 1),
        end=datetime(2026, 5, 31),
        collection_id=collection_id,
    )
    assert len(items) == 1
    assert items[0].card_id == a


def test_log_round_trips_operation_type(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id, operation=OperationType.ALTA))
    repo.log(_make_txn(card_id, operation=OperationType.BAJA))
    items = repo.list_by_card(card_id)
    ops = {t.operation for t in items}
    assert OperationType.ALTA in ops
    assert OperationType.BAJA in ops
    assert all(isinstance(t.operation, OperationType) for t in items)


def test_log_round_trips_datetime(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    when = datetime(2026, 5, 5, 14, 30, 0)
    repo.log(_make_txn(card_id, when=when))
    items = repo.list_by_card(card_id)
    assert items[0].transaction_date == when


def test_card_delete_does_not_break_transactions(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    """transactions.card_id no tiene ON DELETE CASCADE: borrar la card
    levanta IntegrityError porque la transaccion sigue referenciandola.
    Esa es la decision: las bitacoras no se borran al borrar cards.
    """
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.log(_make_txn(card_id))
    with pytest.raises(sqlite3.IntegrityError):
        cards_repo.delete_by_id(card_id)


def test_list_by_collection_respects_limit(
    repo: TransactionsRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    base = datetime(2026, 5, 1)
    for i in range(5):
        repo.log(_make_txn(card_id, when=base + timedelta(days=i)))
    items = repo.list_by_collection(collection_id, limit=2)
    assert len(items) == 2
```

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

### Tabla `app_settings`

- `setting_key TEXT PRIMARY KEY`
- `setting_value TEXT`

### Tabla `card_images`

- `card_image_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `card_id INTEGER NOT NULL UNIQUE`
- `found_photo INTEGER NOT NULL DEFAULT 0`
- `image_source TEXT`
- `image_path TEXT`
- `generated_at TEXT`

**Foreign keys:**
- `FOREIGN KEY (card_id) REFERENCES cards(card_id)
        ON DELETE CASCADE`

**Índices:** `idx_card_images_found`

### Tabla `cards`

- `card_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `card_name TEXT NOT NULL`
- `UNIQUE (collection_id, code_id, card_number)`

**Foreign keys:**
- `FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
        ON DELETE CASCADE`

**Índices:** `idx_cards_collection`

### Tabla `codes_headers`

- `code_header_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `code_header_name TEXT NOT NULL UNIQUE`
- `code_max_length INTEGER NOT NULL DEFAULT 5`

### Tabla `codes_lines`

- `code_line_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `code_header_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `code_name TEXT NOT NULL`
- `code_order INTEGER NOT NULL DEFAULT 0`
- `UNIQUE (code_header_id, code_id)`

**Foreign keys:**
- `FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)
        ON DELETE CASCADE`

**Índices:** `idx_codes_lines_order`

### Tabla `collections`

- `collection_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `collection_name TEXT NOT NULL UNIQUE`
- `card_count INTEGER NOT NULL`
- `requires_code INTEGER NOT NULL DEFAULT 0`
- `code_field_name TEXT`
- `code_header_id INTEGER NOT NULL`
- `is_premium INTEGER NOT NULL DEFAULT 0`
- `license_key_required TEXT`
- `album_columns INTEGER NOT NULL DEFAULT 3`
- `album_rows INTEGER NOT NULL DEFAULT 4`
- `album_orientation TEXT NOT NULL DEFAULT 'portrait'
        CHECK (album_orientation IN ('portrait', 'landscape'))`

**Foreign keys:**
- `FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)`

### Tabla `inventory`

- `inventory_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `card_id INTEGER NOT NULL UNIQUE`
- `quantity INTEGER NOT NULL DEFAULT 0`

**Foreign keys:**
- `FOREIGN KEY (card_id) REFERENCES cards(card_id)
        ON DELETE CASCADE`

### Tabla `schema_version`

- `version INTEGER PRIMARY KEY`
- `applied_at TEXT NOT NULL DEFAULT (datetime('now'))`

### Tabla `transactions`

- `transaction_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `card_id INTEGER NOT NULL`
- `operation TEXT NOT NULL CHECK (operation IN ('alta', 'baja'))`
- `quantity INTEGER NOT NULL CHECK (quantity > 0)`
- `transaction_date TEXT NOT NULL DEFAULT (datetime('now'))`
- `exchange_event_id INTEGER`

**Foreign keys:**
- `FOREIGN KEY (card_id) REFERENCES cards(card_id)`

**Índices:** `idx_transactions_date`, `idx_transactions_card`, `idx_transactions_exchange_event`

## Modelos (dataclasses en `core/models/`)

### `CodeStats` — [src/collections_app/core/models/aggregates/code_stats.py](src/collections_app/core/models/aggregates/code_stats.py)

> Stats agregadas por code_id (resultado de `CardsRepository.get_stats_by_code`).

- `code_id: str`
- `code_name: str`
- `total: int`
- `owned: int`
- `percentage: float`

### `AppSetting` — [src/collections_app/core/models/app_setting.py](src/collections_app/core/models/app_setting.py)

> Setting clave/valor.

- `key: str`
- `value: str | None`

**Métodos:**
- `as_int(self: AppSetting) -> int | None` — Parsea `value` como int. None si `value` es None o no es un entero válido.
- `as_bool(self: AppSetting) -> bool | None` — Parsea `value` como bool. None si `value` es None o no reconocible.

### `Card` — [src/collections_app/core/models/card.py](src/collections_app/core/models/card.py)

> Card del catálogo.

- `card_id: int | None`
- `collection_id: int`
- `code_id: str`
- `card_number: int`
- `card_name: str`

**Métodos:**
- `card_key(self: Card) -> str` — Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1').

### `CardImage` — [src/collections_app/core/models/card_image.py](src/collections_app/core/models/card_image.py)

> Registro de la imagen generada para una card.

- `card_image_id: int | None`
- `card_id: int`
- `found_photo: bool`
- `image_source: str | None`
- `image_path: str | None`
- `generated_at: str | None`

### `CodeHeader` — [src/collections_app/core/models/code_header.py](src/collections_app/core/models/code_header.py)

> Representa un universo de códigos.

- `code_header_id: int | None`
- `code_header_name: str`
- `code_max_length: int`

### `CodeLine` — [src/collections_app/core/models/code_line.py](src/collections_app/core/models/code_line.py)

> Línea de código asociada a un header.

- `code_line_id: int | None`
- `code_header_id: int`
- `code_id: str`
- `code_name: str`
- `code_order: int`

### `Collection` — [src/collections_app/core/models/collection.py](src/collections_app/core/models/collection.py)

> Representa una colección a juntar (catálogo de cards).

- `collection_id: int | None`
- `collection_name: str`
- `card_count: int`
- `requires_code: bool`
- `code_field_name: str | None`
- `code_header_id: int`
- `is_premium: bool`
- `license_key_required: str | None`
- `album_columns: int`
- `album_rows: int`
- `album_orientation: str`

### `InventoryItem` — [src/collections_app/core/models/inventory_item.py](src/collections_app/core/models/inventory_item.py)

> Stock del usuario para una Card.

- `inventory_id: int | None`
- `card_id: int`
- `quantity: int`

**Métodos:**
- `is_owned(self: InventoryItem) -> bool` — True si el usuario tiene al menos una copia.
- `has_duplicates(self: InventoryItem) -> bool` — True si el usuario tiene más de una copia.

### `Transaction` — [src/collections_app/core/models/transaction.py](src/collections_app/core/models/transaction.py)

> Registro inmutable de un movimiento sobre el inventario.

- `transaction_id: int | None`
- `card_id: int`
- `operation: OperationType`
- `quantity: int`
- `transaction_date: datetime`
- `exchange_event_id: int | None`

## Repositorios (`core/repositories/`)

Una clase por tabla. Las repos NO crean conexión, la reciben (`__init__(conn)`). Los queries devuelven instancias de `core/models/`.

### `AppSettingsRepository` — [src/collections_app/core/repositories/app_settings_repo.py](src/collections_app/core/repositories/app_settings_repo.py)

> CRUD sobre `app_settings`.

**API pública:**
- `get(self: AppSettingsRepository, key: str) -> AppSetting | None` — Retorna el setting por clave, o None si no existe.
- `set(self: AppSettingsRepository, setting: AppSetting) -> None` — Inserta o actualiza el setting.
- `delete(self: AppSettingsRepository, key: str) -> bool` — Borra el setting. Retorna True si existía.
- `list_all(self: AppSettingsRepository) -> list[AppSetting]` — Lista todos los settings ordenados por clave.

### `BaseRepository` — [src/collections_app/core/repositories/base.py](src/collections_app/core/repositories/base.py)

> Repositorio base — almacena la conexión SQLite recibida.

**API pública:**
- `__init__(self: BaseRepository, conn: sqlite3.Connection) -> None`

### `CardImagesRepository` — [src/collections_app/core/repositories/card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)

> CRUD y queries de tracking sobre `card_images`.

**API pública:**
- `get_by_card_id(self: CardImagesRepository, card_id: int) -> CardImage | None` — Imagen registrada para una card. None si nunca se procesó.
- `list_by_collection(self: CardImagesRepository, collection_id: int) -> list[CardImage]` — Imágenes registradas de cards de la colección.
- `upsert(self: CardImagesRepository, image: CardImage) -> CardImage` — Inserta o actualiza por card_id UNIQUE.
- `delete_by_card_id(self: CardImagesRepository, card_id: int) -> bool` — Borra el tracking de una card. Retorna True si existía.
- `get_pending(self: CardImagesRepository, collection_id: int) -> list[Card]` — Cards sin entry en card_images (todavía no procesadas).
- `get_placeholders(self: CardImagesRepository, collection_id: int) -> list[CardImage]` — Imágenes generadas pero con `found_photo=False`.
- `count_with_photo(self: CardImagesRepository, collection_id: int) -> int` — Cantidad de cards con `found_photo=True`.
- `count_total_generated(self: CardImagesRepository, collection_id: int) -> int` — Cantidad de cards con cualquier imagen (real o placeholder).

### `CardsRepository` — [src/collections_app/core/repositories/cards_repo.py](src/collections_app/core/repositories/cards_repo.py)

> CRUD y queries específicas sobre `cards`.

**API pública:**
- `get_by_id(self: CardsRepository, card_id: int) -> Card | None` — Card por PK subrogada, o None.
- `get(self: CardsRepository, collection_id: int, code_id: str, card_number: int) -> Card | None` — Card por business key (collection, code, number), o None.
- `list_by_collection(self: CardsRepository, collection_id: int) -> list[Card]` — Cards de la colección ordenadas por (code_id, card_number).
- `list_by_code(self: CardsRepository, collection_id: int, code_id: str) -> list[Card]` — Cards filtradas por code_id, ordenadas por card_number.
- `find_by_number(self: CardsRepository, collection_id: int, card_number: int) -> list[Card]` — Busca cards por número sin filtrar por code_id.
- `count_by_collection(self: CardsRepository, collection_id: int) -> int` — Cuántas cards tiene la colección.
- `create(self: CardsRepository, card: Card) -> Card` — Inserta y retorna la card con `card_id` poblado.
- `upsert(self: CardsRepository, card: Card) -> Card` — Inserta o actualiza por business key. Retorna con id poblado.
- `bulk_upsert(self: CardsRepository, cards: list[Card]) -> int` — Inserta o actualiza muchas cards en un batch. Retorna cantidad procesada.
- `delete_by_id(self: CardsRepository, card_id: int) -> bool` — Borra la card. Cascade borra inventory y card_images. Retorna True si existía.
- `get_stats_by_code(self: CardsRepository, collection_id: int) -> list[CodeStats]` — Stats agregadas por code_id de la colección.

### `CodeHeadersRepository` — [src/collections_app/core/repositories/code_headers_repo.py](src/collections_app/core/repositories/code_headers_repo.py)

> CRUD sobre `codes_headers`.

**API pública:**
- `list_all(self: CodeHeadersRepository) -> list[CodeHeader]` — Retorna todos los headers ordenados por nombre.
- `get_by_id(self: CodeHeadersRepository, code_header_id: int) -> CodeHeader | None` — Retorna el header por id, o None si no existe.
- `get_by_name(self: CodeHeadersRepository, name: str) -> CodeHeader | None` — Retorna el header por nombre exacto (case-sensitive), o None.
- `create(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader` — Inserta y retorna el header con `code_header_id` poblado.
- `update(self: CodeHeadersRepository, header: CodeHeader) -> CodeHeader` — Actualiza un header existente. Requiere `code_header_id` no None.
- `delete(self: CodeHeadersRepository, code_header_id: int) -> bool` — Borra un header. Cascade borra `codes_lines` asociadas.

### `CodeLinesRepository` — [src/collections_app/core/repositories/code_lines_repo.py](src/collections_app/core/repositories/code_lines_repo.py)

> CRUD sobre `codes_lines` con soporte de reordenamiento manual.

**API pública:**
- `list_by_header(self: CodeLinesRepository, code_header_id: int) -> list[CodeLine]` — Líneas del header ordenadas por (code_order, code_id).
- `get(self: CodeLinesRepository, code_header_id: int, code_id: str) -> CodeLine | None` — Línea por business key (header_id, code_id), o None si no existe.
- `get_by_id(self: CodeLinesRepository, code_line_id: int) -> CodeLine | None` — Línea por PK subrogada, o None si no existe.
- `upsert(self: CodeLinesRepository, line: CodeLine) -> CodeLine` — Inserta o actualiza la línea según (code_header_id, code_id) UNIQUE.
- `delete(self: CodeLinesRepository, code_header_id: int, code_id: str) -> bool` — Borra una línea por business key. Retorna True si existía.
- `reorder(self: CodeLinesRepository, code_header_id: int, ordered_code_ids: list[str]) -> None` — Reasigna `code_order` según el índice (1-based) en la lista.

### `CollectionsRepository` — [src/collections_app/core/repositories/collections_repo.py](src/collections_app/core/repositories/collections_repo.py)

> CRUD sobre `collections`.

**API pública:**
- `list_all(self: CollectionsRepository) -> list[Collection]` — Todas las colecciones ordenadas por nombre.
- `get_by_id(self: CollectionsRepository, collection_id: int) -> Collection | None` — Colección por id, o None.
- `get_by_name(self: CollectionsRepository, name: str) -> Collection | None` — Colección por nombre exacto, o None.
- `create(self: CollectionsRepository, collection: Collection) -> Collection` — Inserta y retorna la colección con `collection_id` poblado.
- `update(self: CollectionsRepository, collection: Collection) -> Collection` — Actualiza una colección existente. Requiere `collection_id` no None.
- `delete(self: CollectionsRepository, collection_id: int) -> bool` — Borra la colección. Cascade borra cards e inventory.

### `InventoryRepository` — [src/collections_app/core/repositories/inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)

> CRUD y queries específicas sobre `inventory`.

**API pública:**
- `get_by_card_id(self: InventoryRepository, card_id: int) -> InventoryItem | None` — Inventory item de una card. None si nunca se grabó.
- `list_by_collection(self: InventoryRepository, collection_id: int) -> list[InventoryItem]` — Inventory de todas las cards de la colección (incluye qty=0).
- `list_owned(self: InventoryRepository, collection_id: int) -> list[InventoryItem]` — Inventory items con quantity > 0 de la colección.
- `list_duplicates(self: InventoryRepository, collection_id: int) -> list[InventoryItem]` — Inventory items con quantity > 1 de la colección.
- `get_top_duplicates(self: InventoryRepository, collection_id: int, limit: int = 10) -> list[InventoryItem]` — Las cards con mayor cantidad (quantity > 1), descendente.
- `list_missing(self: InventoryRepository, collection_id: int) -> list[Card]` — Cards que el usuario aún no tiene (sin inventory o quantity=0).
- `upsert(self: InventoryRepository, item: InventoryItem) -> InventoryItem` — Inserta o actualiza el inventory item por card_id UNIQUE.
- `adjust_quantity(self: InventoryRepository, card_id: int, delta: int) -> InventoryItem` — Suma `delta` a la quantity (puede ser negativo).

### `TransactionsRepository` — [src/collections_app/core/repositories/transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)

> Bitácora de operaciones (alta/baja) sobre el inventario.

**API pública:**
- `log(self: TransactionsRepository, txn: Transaction) -> Transaction` — Inserta una transacción y la retorna con `transaction_id` poblado.
- `list_by_card(self: TransactionsRepository, card_id: int, limit: int = 100) -> list[Transaction]` — Transacciones de una card, las más recientes primero.
- `list_by_collection(self: TransactionsRepository, collection_id: int, limit: int = 100) -> list[Transaction]` — Transacciones de cards de la colección, recientes primero.
- `list_recent(self: TransactionsRepository, limit: int = 20) -> list[Transaction]` — Las N transacciones más recientes globalmente.
- `list_by_date_range(self: TransactionsRepository, start: datetime, end: datetime, collection_id: int | None = None) -> list[Transaction]` — Transacciones en `[start, end]` (inclusivo).
