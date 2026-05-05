# Contexto del Proyecto Collections

> Generado automáticamente por [`scripts/generate_context.py`](../scripts/generate_context.py). **No editar a mano** — se sobreescribe.

Contenido en orden: **(1)** árbol del proyecto, **(2)** código completo de cada `.py`, **(3)** contexto (schema SQL, modelos, repositorios).

# 1. Estructura del proyecto

- **src/**
  - **collections_app/**
    - **admin/**
      - **crests/**
        - [__init__.py](src/collections_app/admin/crests/__init__.py)
        - [crest_finder.py](src/collections_app/admin/crests/crest_finder.py)
      - **tools/**
        - [__init__.py](src/collections_app/admin/tools/__init__.py)
        - [codes_csv_importer.py](src/collections_app/admin/tools/codes_csv_importer.py)
        - [csv_importer.py](src/collections_app/admin/tools/csv_importer.py)
        - [panini_scraper.py](src/collections_app/admin/tools/panini_scraper.py)
        - [rename_legacy_cards.py](src/collections_app/admin/tools/rename_legacy_cards.py)
      - **views/**
        - [__init__.py](src/collections_app/admin/views/__init__.py)
        - [cards_abm.py](src/collections_app/admin/views/cards_abm.py)
        - [codes_master_detail.py](src/collections_app/admin/views/codes_master_detail.py)
        - [collections_abm.py](src/collections_app/admin/views/collections_abm.py)
        - [crests_view.py](src/collections_app/admin/views/crests_view.py)
      - [__init__.py](src/collections_app/admin/__init__.py)
      - [main.py](src/collections_app/admin/main.py)
    - **client/**
      - **dialogs/**
        - [__init__.py](src/collections_app/client/dialogs/__init__.py)
        - [client_settings_dialog.py](src/collections_app/client/dialogs/client_settings_dialog.py)
        - [pdf_preview_dialog.py](src/collections_app/client/dialogs/pdf_preview_dialog.py)
        - [profile_setup_dialog.py](src/collections_app/client/dialogs/profile_setup_dialog.py)
      - **views/**
        - [__init__.py](src/collections_app/client/views/__init__.py)
        - [album_view.py](src/collections_app/client/views/album_view.py)
        - [card_loader.py](src/collections_app/client/views/card_loader.py)
        - [compare_view.py](src/collections_app/client/views/compare_view.py)
        - [exchange_view.py](src/collections_app/client/views/exchange_view.py)
        - [inventory_view.py](src/collections_app/client/views/inventory_view.py)
        - [reports_view.py](src/collections_app/client/views/reports_view.py)
        - [stats_view.py](src/collections_app/client/views/stats_view.py)
      - [__init__.py](src/collections_app/client/__init__.py)
      - [main.py](src/collections_app/client/main.py)
    - **core/**
      - **db/**
        - **schema/**
          - [001_initial.sql](src/collections_app/core/db/schema/001_initial.sql)
          - [002_codes_order.sql](src/collections_app/core/db/schema/002_codes_order.sql)
          - [003_card_image_tracking.sql](src/collections_app/core/db/schema/003_card_image_tracking.sql)
          - [004_album_layout.sql](src/collections_app/core/db/schema/004_album_layout.sql)
          - [005_locked_inventory.sql](src/collections_app/core/db/schema/005_locked_inventory.sql)
        - **scripts/**
          - [__init__.py](src/collections_app/core/db/scripts/__init__.py)
          - [cleanup_orphans.py](src/collections_app/core/db/scripts/cleanup_orphans.py)
        - [__init__.py](src/collections_app/core/db/__init__.py)
        - [connection.py](src/collections_app/core/db/connection.py)
        - [migrator.py](src/collections_app/core/db/migrator.py)
      - **models/**
        - [__init__.py](src/collections_app/core/models/__init__.py)
        - [card.py](src/collections_app/core/models/card.py)
        - [card_image.py](src/collections_app/core/models/card_image.py)
        - [code_header.py](src/collections_app/core/models/code_header.py)
        - [code_line.py](src/collections_app/core/models/code_line.py)
        - [collection.py](src/collections_app/core/models/collection.py)
        - [exchange.py](src/collections_app/core/models/exchange.py)
        - [inventory_item.py](src/collections_app/core/models/inventory_item.py)
        - [transaction.py](src/collections_app/core/models/transaction.py)
      - **repositories/**
        - [__init__.py](src/collections_app/core/repositories/__init__.py)
        - [base.py](src/collections_app/core/repositories/base.py)
        - [card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)
        - [cards_repo.py](src/collections_app/core/repositories/cards_repo.py)
        - [codes_headers_repo.py](src/collections_app/core/repositories/codes_headers_repo.py)
        - [codes_lines_repo.py](src/collections_app/core/repositories/codes_lines_repo.py)
        - [collections_repo.py](src/collections_app/core/repositories/collections_repo.py)
        - [inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)
        - [settings_repo.py](src/collections_app/core/repositories/settings_repo.py)
        - [transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)
      - **services/**
        - [__init__.py](src/collections_app/core/services/__init__.py)
        - [album_service.py](src/collections_app/core/services/album_service.py)
        - [collections_service.py](src/collections_app/core/services/collections_service.py)
        - [exchange_service.py](src/collections_app/core/services/exchange_service.py)
        - [inventory_service.py](src/collections_app/core/services/inventory_service.py)
        - [license_service.py](src/collections_app/core/services/license_service.py)
        - [pdf_generator.py](src/collections_app/core/services/pdf_generator.py)
        - [profile_service.py](src/collections_app/core/services/profile_service.py)
        - [reports_service.py](src/collections_app/core/services/reports_service.py)
        - [settings_service.py](src/collections_app/core/services/settings_service.py)
        - [update_service.py](src/collections_app/core/services/update_service.py)
      - **utils/**
        - [__init__.py](src/collections_app/core/utils/__init__.py)
        - [datetime_helpers.py](src/collections_app/core/utils/datetime_helpers.py)
        - [logging_setup.py](src/collections_app/core/utils/logging_setup.py)
        - [paths.py](src/collections_app/core/utils/paths.py)
      - [__init__.py](src/collections_app/core/__init__.py)
    - **shared_ui/**
      - **dialogs/**
        - [__init__.py](src/collections_app/shared_ui/dialogs/__init__.py)
        - [settings_dialog.py](src/collections_app/shared_ui/dialogs/settings_dialog.py)
      - **widgets/**
        - [__init__.py](src/collections_app/shared_ui/widgets/__init__.py)
        - [abm_widget.py](src/collections_app/shared_ui/widgets/abm_widget.py)
        - [enter_navigator.py](src/collections_app/shared_ui/widgets/enter_navigator.py)
      - [__init__.py](src/collections_app/shared_ui/__init__.py)
      - [main_window_base.py](src/collections_app/shared_ui/main_window_base.py)
      - [theme.py](src/collections_app/shared_ui/theme.py)
    - [__init__.py](src/collections_app/__init__.py)
    - [__version__.py](src/collections_app/__version__.py)
- **tests/**
  - **admin/**
    - **crests/**
      - [__init__.py](tests/admin/crests/__init__.py)
      - [test_crest_finder.py](tests/admin/crests/test_crest_finder.py)
    - **tools/**
      - [__init__.py](tests/admin/tools/__init__.py)
      - [test_codes_csv_importer.py](tests/admin/tools/test_codes_csv_importer.py)
      - [test_csv_importer.py](tests/admin/tools/test_csv_importer.py)
      - [test_panini_scraper.py](tests/admin/tools/test_panini_scraper.py)
      - [test_rename_legacy_cards.py](tests/admin/tools/test_rename_legacy_cards.py)
    - **views/**
      - [__init__.py](tests/admin/views/__init__.py)
      - [test_cards_abm.py](tests/admin/views/test_cards_abm.py)
      - [test_codes_master_detail.py](tests/admin/views/test_codes_master_detail.py)
      - [test_collections_abm.py](tests/admin/views/test_collections_abm.py)
      - [test_crests_view.py](tests/admin/views/test_crests_view.py)
      - [test_persistence.py](tests/admin/views/test_persistence.py)
    - [__init__.py](tests/admin/__init__.py)
  - **client/**
    - **dialogs/**
      - [__init__.py](tests/client/dialogs/__init__.py)
      - [test_client_settings_dialog.py](tests/client/dialogs/test_client_settings_dialog.py)
      - [test_pdf_preview_dialog.py](tests/client/dialogs/test_pdf_preview_dialog.py)
    - **views/**
      - [__init__.py](tests/client/views/__init__.py)
      - [test_album_view.py](tests/client/views/test_album_view.py)
      - [test_card_loader.py](tests/client/views/test_card_loader.py)
      - [test_compare_view.py](tests/client/views/test_compare_view.py)
      - [test_inventory_view.py](tests/client/views/test_inventory_view.py)
      - [test_reports_view.py](tests/client/views/test_reports_view.py)
      - [test_stats_view.py](tests/client/views/test_stats_view.py)
    - [__init__.py](tests/client/__init__.py)
  - **core/**
    - **db/**
      - **scripts/**
        - [__init__.py](tests/core/db/scripts/__init__.py)
        - [test_cleanup_orphans.py](tests/core/db/scripts/test_cleanup_orphans.py)
      - [__init__.py](tests/core/db/__init__.py)
      - [test_migrator.py](tests/core/db/test_migrator.py)
    - **repositories/**
      - [__init__.py](tests/core/repositories/__init__.py)
      - [test_card_images_repo.py](tests/core/repositories/test_card_images_repo.py)
      - [test_cards_repo.py](tests/core/repositories/test_cards_repo.py)
      - [test_codes_headers_repo.py](tests/core/repositories/test_codes_headers_repo.py)
      - [test_codes_lines_repo.py](tests/core/repositories/test_codes_lines_repo.py)
      - [test_collections_repo.py](tests/core/repositories/test_collections_repo.py)
      - [test_inventory_repo.py](tests/core/repositories/test_inventory_repo.py)
      - [test_settings_repo.py](tests/core/repositories/test_settings_repo.py)
      - [test_transactions_repo.py](tests/core/repositories/test_transactions_repo.py)
    - **services/**
      - [__init__.py](tests/core/services/__init__.py)
      - [test_album_service.py](tests/core/services/test_album_service.py)
      - [test_collections_service.py](tests/core/services/test_collections_service.py)
      - [test_exchange_service.py](tests/core/services/test_exchange_service.py)
      - [test_inventory_service.py](tests/core/services/test_inventory_service.py)
      - [test_license_service.py](tests/core/services/test_license_service.py)
      - [test_pdf_generator.py](tests/core/services/test_pdf_generator.py)
      - [test_profile_service.py](tests/core/services/test_profile_service.py)
      - [test_reports_service.py](tests/core/services/test_reports_service.py)
      - [test_settings_service.py](tests/core/services/test_settings_service.py)
      - [test_update_service.py](tests/core/services/test_update_service.py)
    - **utils/**
      - [__init__.py](tests/core/utils/__init__.py)
      - [test_datetime_helpers.py](tests/core/utils/test_datetime_helpers.py)
      - [test_paths.py](tests/core/utils/test_paths.py)
    - [__init__.py](tests/core/__init__.py)
  - **fixtures/**
    - [sample_cards.csv](tests/fixtures/sample_cards.csv)
    - [sample_codes.csv](tests/fixtures/sample_codes.csv)
  - **shared_ui/**
    - **dialogs/**
      - [__init__.py](tests/shared_ui/dialogs/__init__.py)
      - [test_settings_dialog.py](tests/shared_ui/dialogs/test_settings_dialog.py)
    - **widgets/**
      - [__init__.py](tests/shared_ui/widgets/__init__.py)
      - [test_abm_widget.py](tests/shared_ui/widgets/test_abm_widget.py)
      - [test_enter_navigator.py](tests/shared_ui/widgets/test_enter_navigator.py)
    - [__init__.py](tests/shared_ui/__init__.py)
  - [__init__.py](tests/__init__.py)
  - [conftest.py](tests/conftest.py)
- **scripts/**
  - [clean_csv.py](scripts/clean_csv.py)
  - [generate_context.py](scripts/generate_context.py)
- **docs/**
  - **reference/**
    - [cards_adrenalyne.csv](docs/reference/cards_adrenalyne.csv)
    - [cards_FIFA_WC_2026_sticker_final.csv](docs/reference/cards_FIFA_WC_2026_sticker_final.csv)
    - [Clave api custom search.txt](docs/reference/Clave api custom search.txt)
    - [codes_adrenalyne.csv](docs/reference/codes_adrenalyne.csv)
    - [codes_FIFA_WC_2026_sticker_final.csv](docs/reference/codes_FIFA_WC_2026_sticker_final.csv)
    - [httpsgithub.compgg1966app_collectio.txt](docs/reference/httpsgithub.compgg1966app_collectio.txt)
  - [abm_widget_guide.md](docs/abm_widget_guide.md)
  - [admin_workflow.md](docs/admin_workflow.md)
  - [album_guide.md](docs/album_guide.md)
  - [architecture.md](docs/architecture.md)
  - [client_workflow.md](docs/client_workflow.md)
  - [crests_guide.md](docs/crests_guide.md)
  - [data_dictionary.md](docs/data_dictionary.md)
  - [data_layer_examples.md](docs/data_layer_examples.md)
  - [project_structure.md](docs/project_structure.md)

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
"""Collections — aplicación para gestionar colecciones de cards/figuritas."""

__version__ = "0.1.0"
```

### [src/collections_app/__version__.py](src/collections_app/__version__.py)

```python
"""Versión y metadatos de la aplicación.

Mantener `__version__` sincronizado con `pyproject.toml`. La política
del proyecto: SemVer (`MAJOR.MINOR.PATCH`) — `packaging.version.Version`
hace la comparación, así que `1.10.0 > 1.9.0` (no comparación lexicográfica).

`__update_url__` apunta a la fuente activa de actualizaciones. Hoy es
GitHub Releases. Para migrar a un servidor propio en el futuro, basta
con cambiar esta URL — el endpoint debe devolver el mismo JSON que
GitHub Releases (campos `tag_name`, `html_url`, `body`, `assets[]`).
"""

__version__ = "1.0.0"
__app_name__ = "CollectionsApp"

# Repo de GitHub usado por GitHubUpdateSource. Reemplazar por el repo real
# cuando se publique el primer release.
__github_repo__ = "pgg1966/app_collection_master"
__update_url__ = f"https://api.github.com/repos/{__github_repo__}/releases/latest"
```

### [src/collections_app/admin/__init__.py](src/collections_app/admin/__init__.py)

```python
"""Aplicación admin: configuración de colecciones."""
```

### [src/collections_app/admin/crests/__init__.py](src/collections_app/admin/crests/__init__.py)

```python
"""Búsqueda y descarga de escudos por code_id."""

from collections_app.admin.crests.crest_finder import (
    SOURCE_CACHE,
    SOURCE_COMMONS,
    SOURCE_COMMONS_OVERRIDE,
    SOURCE_MANUAL,
    SOURCE_NOT_FOUND,
    SOURCE_PLACEHOLDER,
    SPECIAL_CODES,
    CrestFinder,
    CrestResult,
    is_valid_crest_file,
)

__all__ = [
    "SOURCE_CACHE",
    "SOURCE_COMMONS",
    "SOURCE_COMMONS_OVERRIDE",
    "SOURCE_MANUAL",
    "SOURCE_NOT_FOUND",
    "SOURCE_PLACEHOLDER",
    "SPECIAL_CODES",
    "CrestFinder",
    "CrestResult",
    "is_valid_crest_file",
]
```

### [src/collections_app/admin/crests/crest_finder.py](src/collections_app/admin/crests/crest_finder.py)

```python
"""Búsqueda y descarga de escudos por code_id desde Wikimedia Commons.

Cada `code_id` (ej. "ARG", "BRA") tiene UN escudo en
`get_crest_path(code_id)`. La cascada de descarga es:

1. Cache local válido — si ya existe un PNG > MIN_VALID_FILE_BYTES,
   no se redescarga (`is_valid_crest_file`).
2. Si el code_id está en `SPECIAL_CODES` (sets temáticos sin equipo
   nacional asociado, p.ej. Golden Ballers), se genera placeholder
   directamente — el usuario debe importar la imagen manualmente.
3. Override manual (`COMMONS_FILE_OVERRIDES`) — si el code_name está
   en el dict, se usa ese `File:` exacto en vez de buscar.
4. Búsqueda en Wikimedia Commons API con cascada de queries (logo,
   crest, badge, federación) y filtros heurísticos para descartar
   fotos de partidos / jugadores.
5. Si todo falla, retorna `SOURCE_NOT_FOUND` SIN escribir archivo —
   permite reintento automático en la próxima ejecución.

¿Por qué Commons y no Google CSE? Google Custom Search JSON API fue
cerrada a clientes nuevos en 2025: proyectos de GCP creados después
de esa fecha reciben HTTP 403 PERMISSION_DENIED aunque la API esté
"habilitada" en consola, sin workaround. Commons es gratis, sin API
key, sin cuota práctica, y además es la fuente original de los SVG
de escudos (Google los servía referenciando a Commons).
"""

import io
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from collections_app.core.utils.paths import get_crest_path, get_crests_dir

logger = logging.getLogger(__name__)

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
# La API de Wikimedia REQUIERE un User-Agent descriptivo (políticas de uso);
# sin él pueden devolver 403 silenciosamente.
COMMONS_USER_AGENT = "CollectionsApp/1.0 (admin tool for FIFA WC 2026 album)"
COMMONS_THUMB_SIZE = 300  # px — ancho del thumbnail rasterizado
COMMONS_TIMEOUT = 15
DOWNLOAD_TIMEOUT = 15
RATE_LIMIT_DELAY = 1.0  # segundos entre find_crest cuando hay red
QUERY_DELAY = 0.5  # segundos entre queries dentro del mismo find_crest
COMMONS_SEARCH_LIMIT = 5  # resultados por query
CREST_TARGET_SIZE = (200, 200)
SVG_RENDER_SIZE = 200

# Tamaño mínimo (en bytes) que debe tener una respuesta HTTP para ser
# considerada una imagen real. Las descargas válidas (PNG/JPEG/SVG)
# están bien por encima de este umbral.
MIN_DOWNLOAD_BYTES = 500

# Tamaño mínimo (en bytes) de un PNG ya guardado para ser considerado
# un escudo válido en cache (también aplica a placeholders).
MIN_VALID_FILE_BYTES = 1_000

# "Magic bytes" de los formatos de imagen aceptados. Se chequean cuando
# el Content-Type de la respuesta no es `image/*`.
IMAGE_MAGIC_BYTES: tuple[bytes, ...] = (
    b"\x89PNG",
    b"\xff\xd8",  # JPEG
    b"GIF",
    b"RIFF",  # WebP empieza con RIFF....WEBP
    b"\x00\x00\x01\x00",  # ICO
)

# Sets especiales (no son selecciones nacionales): el escudo no se puede
# bajar automáticamente, requiere import manual.
SPECIAL_CODES = frozenset(
    {
        "GBL",
        "CON",
        "TKP",
        "DRK",
        "MMS",
        "GMC",
        "MRK",
        "EXC",
        "RTR",
        "FWC",
        "CCO",
    }
)

# Sources para `CrestResult.source`.
SOURCE_CACHE = "cache"
SOURCE_COMMONS = "commons"
SOURCE_COMMONS_OVERRIDE = "commons_override"
SOURCE_MANUAL = "manual"
SOURCE_PLACEHOLDER = "placeholder"
# `not_found`: la búsqueda no devolvió URLs descargables. NO se escribe
# archivo en disco para que la próxima ejecución reintente automáticamente.
SOURCE_NOT_FOUND = "not_found"


# Override manual: code_name (UPPER) → File: title exacto en Commons.
# Usar SOLO si la búsqueda automática falla repetidamente para ese país.
# Empieza vacío y se puebla iterativamente cuando se detecten faltantes.
COMMONS_FILE_OVERRIDES: dict[str, str] = {}


# Heurísticas para filtrar resultados de búsqueda — los títulos de archivo
# que matchean BLACKLIST_TERMS son fotos/escenas que no queremos. Los que
# matchean WHITELIST_TERMS son escudos/logos.
BLACKLIST_TERMS: tuple[str, ...] = (
    "match",
    "vs",
    "player",
    "stadium",
    "fans",
    "celebration",
    "kit",
    "jersey",
    "shirt",
    "uniform",
    "manager",
    "coach",
    "training",
    "fixtures",
)
WHITELIST_TERMS: tuple[str, ...] = (
    "logo",
    "crest",
    "badge",
    "emblem",
    "shield",
    "coat of arms",
    "federation",
    "association",
    "fa ",
    " fa",
)


@dataclass(frozen=True)
class CrestResult:
    """Resultado de buscar/descargar el escudo de un code_id."""

    code_id: str
    code_name: str
    local_path: Path
    source: str  # "cache" | "commons" | "commons_override" | "manual" | "placeholder" | "not_found"
    success: bool
    error: str | None = None


class CrestFinder:
    """Busca y descarga escudos de selecciones nacionales via Wikimedia Commons."""

    def __init__(self) -> None:
        self.crests_dir = get_crests_dir()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def find_crest(self, code_id: str, code_name: str) -> CrestResult:
        """Busca el escudo para un `code_id`.

        Cascada:
        1. Cache válido (`is_valid_crest_file`).
        2. Si está en `SPECIAL_CODES` → placeholder con iniciales.
        3. Override manual (`COMMONS_FILE_OVERRIDES`) si existe.
        4. Búsqueda en Commons con cascada de queries.
        5. `SOURCE_NOT_FOUND` — NO escribe nada en disco para permitir
           reintento automático en la próxima ejecución.
        """
        logger.info("Buscando crest para %s (%s)…", code_id, code_name)
        dest = get_crest_path(code_id)

        if is_valid_crest_file(dest):
            return CrestResult(code_id, code_name, dest, SOURCE_CACHE, True)
        if dest.exists():
            dest.unlink(missing_ok=True)
            logger.debug("Borrado crest inválido en cache: %s", dest)

        if code_id in SPECIAL_CODES:
            self._generate_placeholder_crest(code_id, dest)
            return CrestResult(
                code_id,
                code_name,
                dest,
                SOURCE_PLACEHOLDER,
                True,
                error="Set especial — importar imagen manualmente",
            )

        # Override manual: si está mapeado, no buscamos — vamos directo al File:
        override = COMMONS_FILE_OVERRIDES.get(code_name.upper())
        if override:
            url = self._get_commons_thumb_url(override)
            if url and self._download_and_process_crest(url, dest):
                logger.info("Crest %s: override Commons %r", code_id, override)
                return CrestResult(code_id, code_name, dest, SOURCE_COMMONS_OVERRIDE, True)

        # Búsqueda con cascada de queries (de más a menos específica).
        for query in self._build_commons_queries(code_name):
            titles = self._search_commons_files(query, limit=COMMONS_SEARCH_LIMIT)
            for title in titles:
                url = self._get_commons_thumb_url(title)
                if url and self._download_and_process_crest(url, dest):
                    logger.info(
                        "Crest %s: encontrado vía Commons (query=%r, file=%r)",
                        code_id,
                        query,
                        title,
                    )
                    return CrestResult(code_id, code_name, dest, SOURCE_COMMONS, True)
            # Pequeño delay entre queries para no abusar de la API
            time.sleep(QUERY_DELAY)

        logger.info("Crest %s: sin resultado — se reintentará la próxima vez", code_id)
        return CrestResult(
            code_id,
            code_name,
            dest,
            SOURCE_NOT_FOUND,
            False,
            error="No se encontró escudo en Wikimedia Commons",
        )

    def find_all_crests(
        self,
        codes: list[tuple[str, str]],
        on_progress: Callable[[int, int, str], None] | None = None,
    ) -> list[CrestResult]:
        """Procesa una lista de `(code_id, code_name)`.

        Aplica `RATE_LIMIT_DELAY` segundos entre find_crest reales (no entre
        cards cacheadas o especiales).
        """
        results: list[CrestResult] = []
        total = len(codes)
        first_network_call = True
        for i, (code_id, code_name) in enumerate(codes, start=1):
            dest = get_crest_path(code_id)
            needs_network = not is_valid_crest_file(dest) and code_id not in SPECIAL_CODES
            if needs_network and not first_network_call:
                time.sleep(RATE_LIMIT_DELAY)
            result = self.find_crest(code_id, code_name)
            if needs_network:
                first_network_call = False
            results.append(result)
            if on_progress is not None:
                on_progress(i, total, f"{code_id} {code_name}")
        return results

    def import_manual_crest(self, code_id: str, source_image: Path) -> CrestResult:
        """Importa una imagen local como escudo de un code_id."""
        dest = get_crest_path(code_id)
        try:
            with Image.open(source_image) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
        except (OSError, ValueError) as exc:
            return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, False, error=str(exc))
        return CrestResult(code_id, code_id, dest, SOURCE_MANUAL, True)

    def cleanup_failed_placeholders(self, codes: list[tuple[str, str]]) -> int:
        """Borra placeholders previos de códigos NO especiales.

        Los placeholders heredados (ej. cuando find_crest aún escribía
        `SOURCE_PLACEHOLDER` en disco para errores) siguen siendo "cache
        válido" y bloquean reintentos. Llamar antes de `find_all_crests`
        cuando el usuario pide buscar de nuevo, para que esos países se
        reintenten en vez de devolverse del cache. SPECIAL_CODES NO se
        tocan (su placeholder es intencional).

        Retorna cuántos archivos borró.
        """
        deleted = 0
        for code_id, _ in codes:
            if code_id in SPECIAL_CODES:
                continue
            path = get_crest_path(code_id)
            if path.exists():
                path.unlink(missing_ok=True)
                deleted += 1
                logger.debug("Borrado placeholder previo: %s", code_id)
        return deleted

    # ------------------------------------------------------------------
    # Wikimedia Commons
    # ------------------------------------------------------------------

    def _build_commons_queries(self, code_name: str) -> list[str]:
        """Genera queries para Commons en orden de especificidad decreciente.

        Las primeras queries hintean SVG (escudos vectoriales son los
        archivos más limpios en Commons), las últimas dejan abierto el tipo.
        """
        name = code_name.title()
        return [
            f"{name} national football team crest svg",
            f"{name} national football team logo svg",
            f"{name} football federation logo svg",
            f"{name} football association crest svg",
            f"{name} national football team crest",
            f"{name} football federation logo",
        ]

    def _search_commons_files(self, query: str, limit: int = 5) -> list[str]:
        """Busca archivos en Commons en namespace File:. Retorna títulos filtrados.

        El filtro `_is_likely_crest_file` descarta resultados que parecen
        fotos de partidos / jugadores / estadios.
        """
        params: dict[str, str | int] = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": 6,  # namespace File:
            "srlimit": limit,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                headers={"User-Agent": COMMONS_USER_AGENT},
                timeout=COMMONS_TIMEOUT,
            )
            if r.status_code != 200:
                logger.warning(
                    "[commons] search HTTP %s para %r — body=%s",
                    r.status_code,
                    query,
                    r.text[:300],
                )
                return []
            data = r.json()
            results = data.get("query", {}).get("search", []) or []
            raw_titles = [
                str(item["title"]) for item in results if isinstance(item, dict) and "title" in item
            ]
            titles = [t for t in raw_titles if self._is_likely_crest_file(t)]
            logger.info(
                "[commons] search %r → %d raw → %d filtrados",
                query,
                len(raw_titles),
                len(titles),
            )
            return titles
        except Exception as exc:  # noqa: BLE001
            logger.warning("[commons] search excepción: %s", exc)
            return []

    def _get_commons_thumb_url(self, file_title: str) -> str | None:
        """Para un `File:Foo.svg`, retorna la URL del thumbnail PNG rasterizado.

        Pide `iiurlwidth=COMMONS_THUMB_SIZE` para forzar a Commons a generar
        un PNG (incluso si el original es SVG). Esto evita depender de
        cairosvg para la mayoría de los escudos. Retorna `None` si no se
        puede resolver.
        """
        params: dict[str, str | int] = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": COMMONS_THUMB_SIZE,
            "format": "json",
        }
        try:
            r = requests.get(
                COMMONS_API_URL,
                params=params,
                headers={"User-Agent": COMMONS_USER_AGENT},
                timeout=COMMONS_TIMEOUT,
            )
            if r.status_code != 200:
                return None
            data = r.json()
            pages = data.get("query", {}).get("pages", {}) or {}
            for page in pages.values():
                if not isinstance(page, dict):
                    continue
                infos = page.get("imageinfo") or []
                if not infos or not isinstance(infos[0], dict):
                    continue
                info = infos[0]
                # 1. thumburl: PNG rasterizado al ancho pedido — preferido.
                thumb_url = info.get("thumburl")
                if thumb_url:
                    return str(thumb_url)
                # 2. url: original. Si NO es SVG, lo usamos directo.
                orig_url = info.get("url")
                mime = (info.get("mime") or "").lower()
                if orig_url and "svg" not in mime:
                    return str(orig_url)
                # 3. SVG sin thumb — `_download_and_process_crest` intentará
                #    convertirlo con cairosvg (degrada a None si no está).
                return str(orig_url) if orig_url else None
            return None
        except Exception as exc:  # noqa: BLE001
            logger.debug("[commons] imageinfo falló para %r: %s", file_title, exc)
            return None

    @staticmethod
    def _is_likely_crest_file(file_title: str) -> bool:
        """Heurística de filtrado: el título debe parecer un escudo, no una foto."""
        lower = file_title.lower()
        if any(term in lower for term in BLACKLIST_TERMS):
            return False
        return any(term in lower for term in WHITELIST_TERMS)

    # ------------------------------------------------------------------
    # Descarga y procesamiento
    # ------------------------------------------------------------------

    def _download_and_process_crest(self, url: str, dest: Path) -> bool:
        """Descarga `url`, convierte a PNG RGBA `CREST_TARGET_SIZE` y guarda.

        Devuelve True si la descarga produjo un PNG válido en `dest`. La
        validación es defensiva: status, tamaño mínimo, detección de SVG
        (con conversión vía cairosvg si está), magic bytes, conversión a
        RGBA y re-validación post-save.
        """
        try:
            r = requests.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                headers={"User-Agent": COMMONS_USER_AGENT},
            )
            if r.status_code != 200:
                return False

            content = r.content
            if len(content) < MIN_DOWNLOAD_BYTES:
                logger.debug(
                    "Descarga muy pequeña (%d bytes) para %s — descartando",
                    len(content),
                    url,
                )
                return False

            content_type = r.headers.get("Content-Type", "").lower()

            if "svg" in content_type or self._is_svg(content):
                png_bytes = self._svg_to_png(content)
                if png_bytes is None:
                    logger.debug("SVG no convertible para %s", url)
                    return False
                content = png_bytes
            elif "image" not in content_type and not self._has_image_magic(content):
                logger.debug(
                    "Respuesta no parece imagen (CT=%r) para %s",
                    content_type,
                    url,
                )
                return False

            with Image.open(io.BytesIO(content)) as img:
                rgba = img.convert("RGBA")
                rgba.thumbnail(CREST_TARGET_SIZE, Image.Resampling.LANCZOS)
                rgba.save(dest, "PNG")
        except Exception as exc:  # noqa: BLE001
            logger.debug("No se pudo descargar/procesar %s: %s", url, exc)
            dest.unlink(missing_ok=True)
            return False

        if not dest.exists() or dest.stat().st_size < MIN_VALID_FILE_BYTES:
            dest.unlink(missing_ok=True)
            logger.debug("PNG guardado demasiado pequeño o vacío para %s", url)
            return False

        return True

    # ------------------------------------------------------------------
    # Validación e introspección de bytes
    # ------------------------------------------------------------------

    @staticmethod
    def _is_svg(content: bytes) -> bool:
        """Detecta si `content` empieza con un encabezado XML/SVG."""
        snippet = content[:512].lstrip().lower()
        return snippet.startswith(b"<?xml") or snippet.startswith(b"<svg")

    @staticmethod
    def _has_image_magic(content: bytes) -> bool:
        """True si los primeros bytes coinciden con un formato de imagen conocido."""
        return any(content.startswith(magic) for magic in IMAGE_MAGIC_BYTES)

    @staticmethod
    def _svg_to_png(svg_bytes: bytes) -> bytes | None:
        """Rasteriza SVG a PNG usando cairosvg (dependencia opcional)."""
        try:
            import cairosvg
        except ImportError:
            logger.debug("cairosvg no instalado — no se puede convertir SVG a PNG")
            return None
        try:
            png = cairosvg.svg2png(
                bytestring=svg_bytes,
                output_width=SVG_RENDER_SIZE,
                output_height=SVG_RENDER_SIZE,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("cairosvg falló: %s", exc)
            return None
        return bytes(png) if png else None

    # ------------------------------------------------------------------
    # Placeholder
    # ------------------------------------------------------------------

    def _generate_placeholder_crest(self, code_id: str, dest: Path) -> None:
        """Crea un placeholder: círculo gris relleno con las iniciales."""
        size = CREST_TARGET_SIZE
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(size) // 20
        draw.ellipse(
            (margin, margin, size[0] - margin, size[1] - margin),
            fill=(230, 230, 230, 255),
            outline=(150, 150, 150, 220),
            width=3,
        )
        draw.text(
            (size[0] // 2, size[1] // 2),
            code_id[:3],
            fill=(120, 120, 120, 230),
            anchor="mm",
        )
        img.save(dest, "PNG")


# ----------------------------------------------------------------------
# Helpers de módulo (API pública usada también desde la vista)
# ----------------------------------------------------------------------


def is_valid_crest_file(path: Path) -> bool:
    """Retorna True si `path` existe y supera el tamaño mínimo válido.

    Los crests reales descargados y los placeholders generados internamente
    siempre superan `MIN_VALID_FILE_BYTES`. Cualquier archivo más chico es
    probablemente un intento previo fallido (truncado, vacío, corrupto).
    """
    return path.exists() and path.stat().st_size > MIN_VALID_FILE_BYTES
```

### [src/collections_app/admin/main.py](src/collections_app/admin/main.py)

```python
"""Entry point de la aplicación admin (configuración)."""

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTabWidget

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.admin.views.crests_view import CrestsView
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import (
    get_active_profile,
    get_database_path,
    set_active_profile,
)
from collections_app.shared_ui import (
    MainWindowBase,
    SettingsDialog,
    apply_app_style,
)

logger = logging.getLogger(__name__)

_APP_NAME = "Collections — Admin"


class AdminMainWindow(MainWindowBase):
    """Ventana principal del admin con tabs Colecciones / Códigos / Cards / Escudos."""

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name=_APP_NAME)
        title = _APP_NAME
        if get_active_profile() != "default":
            title += f"  [{get_active_profile()}]"
        self.setWindowTitle(title)
        self.setMinimumSize(1200, 800)

        self._collections_view = CollectionsAbmView(self.conn)
        self._codes_view = CodesMasterDetailView(self.conn)
        self._cards_view = CardsAbmView(self.conn)
        self._crests_view = CrestsView(self.conn)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._collections_view, self.tr("Colecciones"))
        self._tabs.addTab(self._codes_view, self.tr("Códigos"))
        self._tabs.addTab(self._cards_view, self.tr("Cards"))
        self._tabs.addTab(self._crests_view, self.tr("Escudos"))
        self.setCentralWidget(self._tabs)

        # Cuando se crea/edita o borra una colección, refrescar el combo
        # de Cards para que vea las novedades sin reiniciar la app.
        self._collections_view.abm.record_saved.connect(self._cards_view.refresh_collections_combo)
        self._collections_view.abm.record_deleted.connect(
            self._cards_view.refresh_collections_combo
        )

    def _build_menus(self) -> None:
        super()._build_menus()
        config_menu = self.menuBar().addMenu(self.tr("&Configuración"))
        action = config_menu.addAction(self.tr("Settings..."))
        action.triggered.connect(self._open_settings)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self.conn, parent=self)
        if dlg.exec():
            self._update_status_bar()


def main() -> int:
    """Entry point. Inicializa logging, abre la ventana principal."""
    # Parsear --profile antes de cualquier inicialización que toque
    # paths/DB. Ver collections_app.core.utils.paths.set_active_profile.
    parser = argparse.ArgumentParser(add_help=False, description=_APP_NAME)
    parser.add_argument(
        "--profile",
        default="default",
        help="Perfil de datos (alfanumérico). Default: 'default'.",
    )
    args, remaining = parser.parse_known_args()
    set_active_profile(args.profile)

    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info("Admin app — bootstrap OK (profile=%s, db=%s)", get_active_profile(), db_path)

    app = QApplication([sys.argv[0], *remaining])
    apply_app_style(app)
    window = AdminMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

### [src/collections_app/admin/tools/__init__.py](src/collections_app/admin/tools/__init__.py)

```python
"""Herramientas auxiliares del admin (importadores, exportadores)."""
```

### [src/collections_app/admin/tools/codes_csv_importer.py](src/collections_app/admin/tools/codes_csv_importer.py)

```python
"""Importador de codes_lines desde CSV."""

import csv
import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from collections_app.core.db.connection import transaction
from collections_app.core.models import CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)

logger = logging.getLogger(__name__)

# Mapeo posicional cuando el CSV no tiene header.
_DEFAULT_COLUMN_INDEXES = {"code_id": 0, "code_name": 1, "code_order": 2}


@dataclass
class CodesCsvImportResult:
    """Resumen del resultado de un import de códigos."""

    total_rows: int
    imported: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class CodesCsvImporter:
    """Importa codes_lines desde un CSV.

    Formato esperado (UTF-8, separador coma):

        code_id,code_name,code_order
        ARG,Argentina,1
        BRA,Brasil,2

    Si el CSV trae una columna adicional `code_max_length` (formato
    histórico), se ignora silenciosamente — esa configuración pertenece
    al header padre, no a cada línea.

    La primera fila puede ser header (detectado por `code_id` presente
    en cualquier columna) o directamente datos; en ese caso se asume
    el orden posicional `code_id, code_name, code_order` y cualquier
    columna extra se descarta.

    Validaciones por fila (filas inválidas se reportan en `errors` y se
    omiten, pero NO abortan el import):
      - `code_id` no vacío y de longitud ≤ `code_max_length` del header.
      - `code_name` no vacío.
      - `code_order` entero si está presente; default 0.

    El upsert final corre dentro de una transacción.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def import_file(
        self,
        csv_path: Path,
        code_header_id: int,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CodesCsvImportResult:
        """Lee y procesa el CSV.

        Args:
            csv_path: archivo a leer (UTF-8).
            code_header_id: id del header al que pertenecen los códigos.
            on_progress: callback `(current, total)` para barras de progreso.

        Returns:
            `CodesCsvImportResult` con totales y errores por fila.

        Raises:
            ValueError: si el header no existe.
            FileNotFoundError: si el archivo no se puede abrir.
        """
        header = CodesHeadersRepository(self.conn).get_by_id(code_header_id)
        if header is None:
            raise ValueError(f"code_header_id {code_header_id} no existe")

        max_len = header.code_max_length

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))

        if not rows:
            return CodesCsvImportResult(0, 0, 0)

        column_indexes, data_rows = self._detect_columns(rows)

        total = len(data_rows)
        lines_to_save: list[CodeLine] = []
        errors: list[str] = []
        skipped = 0

        for i, row in enumerate(data_rows, start=1):
            if on_progress:
                on_progress(i, total)
            ok, line_or_error = self._parse_row(row, code_header_id, max_len, i, column_indexes)
            if not ok:
                errors.append(line_or_error)  # type: ignore[arg-type]
                skipped += 1
                continue
            lines_to_save.append(line_or_error)  # type: ignore[arg-type]

        repo = CodesLinesRepository(self.conn)
        with transaction(self.conn):
            for line in lines_to_save:
                repo.upsert(line)

        logger.info(
            "Import codes CSV: total=%d imported=%d skipped=%d errors=%d",
            total,
            len(lines_to_save),
            skipped,
            len(errors),
        )
        return CodesCsvImportResult(
            total_rows=total,
            imported=len(lines_to_save),
            skipped=skipped,
            errors=errors,
        )

    def _detect_columns(self, rows: list[list[str]]) -> tuple[dict[str, int], list[list[str]]]:
        """Decide si la primera fila es header y construye el mapping.

        Retorna `(column_indexes, data_rows)`. Si la primera fila contiene
        `code_id` (case-insensitive), se interpreta como header y los
        índices se derivan de los nombres; columnas no reconocidas
        (incluyendo `code_max_length`) se ignoran silenciosamente. Si no
        hay header, se asume el mapping posicional por defecto.
        """
        first = [c.strip().lower() for c in rows[0]]
        if "code_id" in first:
            mapping: dict[str, int] = {}
            for i, name in enumerate(first):
                if name in {"code_id", "code_name", "code_order"}:
                    mapping[name] = i
                # cualquier otra columna (incluyendo "code_max_length") se ignora
            return mapping, rows[1:]
        return _DEFAULT_COLUMN_INDEXES, rows

    def _parse_row(
        self,
        row: list[str],
        code_header_id: int,
        max_len: int,
        row_index: int,
        column_indexes: dict[str, int],
    ) -> tuple[bool, CodeLine | str]:
        def cell(name: str) -> str:
            idx = column_indexes.get(name)
            if idx is None or idx >= len(row):
                return ""
            return row[idx].strip()

        code_id = cell("code_id")
        code_name = cell("code_name")
        order_str = cell("code_order")

        if not code_id:
            return False, f"fila {row_index}: code_id vacío"
        if len(code_id) > max_len:
            return False, f"fila {row_index}: code_id '{code_id}' excede max_length {max_len}"
        if not code_name:
            return False, f"fila {row_index}: code_name vacío"

        if order_str:
            try:
                code_order = int(order_str)
            except ValueError:
                return False, f"fila {row_index}: code_order '{order_str}' no es entero"
        else:
            code_order = 0

        return True, CodeLine(
            code_header_id=code_header_id,
            code_id=code_id,
            code_name=code_name,
            code_order=code_order,
        )
```

### [src/collections_app/admin/tools/csv_importer.py](src/collections_app/admin/tools/csv_importer.py)

```python
"""Importador de cards desde CSV."""

import csv
import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from collections_app.core.db.connection import transaction
from collections_app.core.models import Card
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
)

logger = logging.getLogger(__name__)


@dataclass
class CsvImportResult:
    """Resumen del resultado de un import."""

    total_rows: int
    imported: int
    skipped: int
    errors: list[str] = field(default_factory=list)


class CardsCsvImporter:
    """Importa cards desde un CSV.

    Formato esperado (UTF-8, separador coma):

        code_id,card_number,card_name
        NON,24,LIONEL MESSI
        MR,1,PAZ

    La primera fila puede o no ser header. Si el primer valor es
    `code_id` (case-insensitive), se asume header y se descarta.

    Validaciones por fila:
      - 3 columnas mínimas.
      - `code_id` debe existir en `codes_lines` del header de la collection.
      - `card_number` debe ser entero positivo.
      - `card_name` no vacío.

    Las filas inválidas se acumulan en `errors` y se omiten — no abortan
    el import. El bulk_upsert final corre dentro de una transacción.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def import_file(
        self,
        csv_path: Path,
        collection_id: int,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> CsvImportResult:
        """Lee y procesa el CSV.

        Args:
            csv_path: archivo a leer (UTF-8).
            collection_id: id de la colección a la que pertenecen las cards.
            on_progress: callback `(current, total)` para barras de progreso.

        Returns:
            `CsvImportResult` con totales y errores por fila.

        Raises:
            ValueError: si la collection no existe.
            FileNotFoundError: si el archivo no se puede abrir.
        """
        collection = CollectionsRepository(self.conn).get_by_id(collection_id)
        if collection is None:
            raise ValueError(f"Collection {collection_id} no existe")

        valid_codes = set(
            CodesLinesRepository(self.conn).list_codes_only(collection.code_header_id)
        )

        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            rows = list(csv.reader(fh))

        if not rows:
            return CsvImportResult(0, 0, 0)

        # Detectar header
        first = [c.strip().lower() for c in rows[0]]
        data_rows = rows[1:] if first and first[0] == "code_id" else rows

        total = len(data_rows)
        cards_to_save: list[Card] = []
        errors: list[str] = []
        skipped = 0

        for i, row in enumerate(data_rows, start=1):
            if on_progress:
                on_progress(i, total)
            valid, card_or_error = self._parse_row(row, collection_id, valid_codes, i)
            if not valid:
                errors.append(card_or_error)  # type: ignore[arg-type]
                skipped += 1
                continue
            cards_to_save.append(card_or_error)  # type: ignore[arg-type]

        with transaction(self.conn):
            CardsRepository(self.conn).bulk_upsert(cards_to_save)

        logger.info(
            "Import CSV: total=%d imported=%d skipped=%d errors=%d",
            total,
            len(cards_to_save),
            skipped,
            len(errors),
        )
        return CsvImportResult(
            total_rows=total,
            imported=len(cards_to_save),
            skipped=skipped,
            errors=errors,
        )

    def _parse_row(
        self,
        row: list[str],
        collection_id: int,
        valid_codes: set[str],
        row_index: int,
    ) -> tuple[bool, Card | str]:
        if len(row) < 3:
            return False, f"fila {row_index}: columnas insuficientes"

        code_id = row[0].strip()
        num_str = row[1].strip()
        name = row[2].strip()

        if code_id not in valid_codes:
            return False, f"fila {row_index}: code_id '{code_id}' no existe en el header"

        try:
            num = int(num_str)
        except ValueError:
            return False, f"fila {row_index}: card_number '{num_str}' no es entero"
        if num < 0:
            return False, f"fila {row_index}: card_number {num} no puede ser negativo"

        if not name:
            return False, f"fila {row_index}: card_name vacío"

        return True, Card(
            collection_id=collection_id,
            code_id=code_id,
            card_number=num,
            card_name=name,
        )
```

### [src/collections_app/admin/tools/panini_scraper.py](src/collections_app/admin/tools/panini_scraper.py)

```python
"""Scraper de cards Panini desde cartophilic-info-exch.blogspot.com.

Tool standalone (no toca la DB) que crawlea posts del blog y descarga
las imágenes de cards en alta resolución a
`%APPDATA%/Collections/generated_cards/<collection_id>/`.

Soporta dos colecciones (FIFA WC 2026):
- "adrenalyn": Adrenalyn XL trading cards (~630 cards).
- "stickers" : Sticker album (~980 stickers).

Uso CLI:
    python -m collections_app.admin.tools.panini_scraper --collection adrenalyn
    python -m collections_app.admin.tools.panini_scraper --collection stickers
    python -m collections_app.admin.tools.panini_scraper \\
        --collection adrenalyn --max-pages 3        # smoke test rápido
"""

import argparse
import logging
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup, Tag

from collections_app.core.utils.paths import (
    format_card_filename,
    get_generated_cards_dir,
)

logger = logging.getLogger(__name__)

BLOG_BASE_URL = "https://cartophilic-info-exch.blogspot.com"
USER_AGENT = "CollectionsApp/1.0 (personal album tool)"
REQUEST_TIMEOUT = 20
DELAY_BETWEEN_REQUESTS = 1.0  # segundos entre GETs
DELAY_AFTER_429 = 30.0  # backoff si nos rate-limitean
MIN_VALID_IMAGE_BYTES = 5_000  # bytes mínimos para considerar una imagen válida
PNG_MAGIC = b"\x89PNG"
JPEG_MAGIC = b"\xff\xd8\xff"

ADRENALYN_SEED_URL = (
    "https://cartophilic-info-exch.blogspot.com/2026/02/"
    "panini-adrenalyn-xl-fifa-world-cup-2026_0501236099.html"
)
STICKERS_SEED_URL = (
    "https://cartophilic-info-exch.blogspot.com/2026/03/"
    "panini-fifa-world-cup-2026-mexusacan-09_030880692.html"
)

# Términos que descalifican una página aunque su título matchee la keyword:
# son sets paralelos / accesorios / variantes que no nos interesan.
# La página seed de Stickers (Checklist) cae acá → deja de ser scrapeada
# para cards, pero `run()` igual usa sus links para descubrir otras páginas.
_BLACKLIST_TITLE_TERMS = (
    "limited edition",
    "special box",
    "upgrade",
    "xxl",
    "hologram",
    "multipack",
    "starter pack",
    "official guide",
    "checklist",
    "cosmic",
    "parallel",
    # Variantes específicas del set Stickers FIFA WC 2026:
    "album",
    "stadium kit",
    "coca-cola",
    "coca cola",
    "mcdonald",
    "free digital pack",
    "play-offs",
    "play offs",
    "extra sticker",
    "fifa rewards",
    "mobile tour",
    "crumple",
    "gold numbered",
)

# Substrings (lowercase) que descalifican una URL de imagen aunque su nombre
# matchee `filename_pattern`. Cubre hojas grupales por país, variantes
# patrocinadas y scans del álbum impreso.
FILENAME_BLACKLIST_TOKENS: tuple[str, ...] = (
    "coca-cola",
    "coca cola",
    "mcdoanld",  # typo del blog (sic)
    "mcdonald",
    "play-offs",
    "play offs",
    "playoffs",
    "free digital",
    "extra sticker",
    "album",
    "stadium",
    "starter pack",
    "crumple",
    "gold flood",
    "limited edition",
    "hologram",
    "xxl",
    # Cualquier país entre guiones suele ser hoja grupal o variante de país.
    " - germany - ",
    " - france - ",
    " - brazil - ",
    " - usa - ",
    " - mexico - ",
    " - spain - ",
)


@dataclass(frozen=True)
class CollectionConfig:
    """Parámetros que cambian por colección (Adrenalyn vs Stickers)."""

    name: str
    collection_id: int
    seed_url: str
    title_keyword: str
    filename_pattern: re.Pattern[str]
    expected_total: int


COLLECTIONS: dict[str, CollectionConfig] = {
    "adrenalyn": CollectionConfig(
        name="adrenalyn",
        collection_id=1,
        seed_url=ADRENALYN_SEED_URL,
        title_keyword="Adrenalyn XL FIFA World Cup 2026",
        # ej: "AXL World Cup 2026 -042.jpg"
        filename_pattern=re.compile(r"AXL.*?-(\d+)\.jpe?g$", re.IGNORECASE),
        expected_total=630,
    ),
    "stickers": CollectionConfig(
        name="stickers",
        collection_id=3,
        seed_url=STICKERS_SEED_URL,
        title_keyword="FIFA World Cup 2026",
        # Patrón estricto para PASO 1: solo individuales con número.
        # Exige " -NNNa.jpg" (espacio-guión-3dígitos-1a3letras), después de
        # "FIFA World Cup 2026". Esto rechaza:
        # - "...Coca-Cola -001a.jpg" (hay tokens entre "2026" y "-001")
        # - "...USA1bbb.jpg" (sin guión inmediato + número)
        # - "...- Brazil2cc.jpg" (país en lugar de número)
        # Hojas grupales por país y variantes patrocinadas se manejan en
        # PASO 2 (futuro). Adicionalmente FILENAME_BLACKLIST_TOKENS aporta
        # una segunda capa de filtrado.
        filename_pattern=re.compile(
            r"FIFA World Cup 2026 -(\d{1,3})[a-z]{1,3}\.jpe?g$",
            re.IGNORECASE,
        ),
        expected_total=980,
    ),
}


@dataclass(frozen=True)
class CardImage:
    """Una imagen de card descubierta en una página del blog."""

    card_number: int
    url: str  # URL en alta resolución (s1600)
    original_url: str  # URL como vino del HTML
    source_page: str  # URL del post donde se encontró


@dataclass
class ScrapeResult:
    """Resumen del run del scraper."""

    downloaded: int = 0
    skipped: int = 0
    failed: int = 0
    pages_visited: int = 0
    missing_numbers: list[int] = field(default_factory=list)


class PaniniScraper:
    """Crawler que recorre posts del blog y descarga las cards de una colección."""

    def __init__(
        self,
        config: CollectionConfig,
        output_dir: Path,
        force: bool = False,
        on_log: Callable[[str], None] | None = None,
        max_pages: int = 100,
    ) -> None:
        self._config = config
        self._output_dir = output_dir
        self._force = force
        self._log = on_log or (lambda _m: None)
        self._max_pages = max_pages
        self._session = requests.Session()
        self._session.headers["User-Agent"] = USER_AGENT
        self._visited_pages: set[str] = set()
        self._downloaded_numbers: set[int] = set()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def run(self) -> ScrapeResult:
        """Crawl iterativo: arranca en `seed_url`, sigue Older/Newer Post.

        Termina cuando se queda sin URLs nuevas o llega a `max_pages`.
        """
        result = ScrapeResult()
        queue: list[str] = [self._config.seed_url]

        while queue and result.pages_visited < self._max_pages:
            url = queue.pop(0)
            if url in self._visited_pages:
                continue
            self._visited_pages.add(url)
            result.pages_visited += 1

            self._info("Visitando página %d: %s", result.pages_visited, url)
            html = self._fetch_html(url)
            if html is None:
                continue

            soup = BeautifulSoup(html, "html.parser")
            if not self._is_relevant_page(soup, url):
                self._info("Página descartada (no relevante): %s", url)
                queue.extend(self._find_next_pages(soup, url))
                continue

            title = self._page_title(soup) or "(sin título)"
            self._info("Página relevante: %s", title)

            cards = self._extract_card_images(soup, url)
            self._info("Encontradas %d cards en esta página", len(cards))

            for card in cards:
                outcome = self._download_card(card)
                if outcome == "downloaded":
                    result.downloaded += 1
                    self._downloaded_numbers.add(card.card_number)
                elif outcome == "skipped":
                    result.skipped += 1
                    self._downloaded_numbers.add(card.card_number)
                else:
                    result.failed += 1

            queue.extend(self._find_next_pages(soup, url))

        expected = set(range(1, self._config.expected_total + 1))
        result.missing_numbers = sorted(expected - self._downloaded_numbers)
        return result

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> str | None:
        """GET con retry en 429. Devuelve el HTML o None si no se pudo."""
        for attempt in (1, 2):
            try:
                r = self._session.get(url, timeout=REQUEST_TIMEOUT)
            except requests.RequestException as exc:
                logger.warning("[scraper] excepción al pedir %s: %s", url, exc)
                return None

            if r.status_code == 429:
                if attempt == 1:
                    self._info("HTTP 429 — esperando %.0fs y reintentando", DELAY_AFTER_429)
                    time.sleep(DELAY_AFTER_429)
                    continue
                self._info("HTTP 429 persistente para %s — abortando", url)
                return None

            if r.status_code != 200:
                self._info("HTTP %s para %s", r.status_code, url)
                return None

            time.sleep(DELAY_BETWEEN_REQUESTS)
            return str(r.text)

        return None

    # ------------------------------------------------------------------
    # Parseo de páginas
    # ------------------------------------------------------------------

    @staticmethod
    def _page_title(soup: BeautifulSoup) -> str | None:
        node = soup.find("title")
        return node.get_text(strip=True) if node else None

    def _is_relevant_page(self, soup: BeautifulSoup, _url: str) -> bool:
        """True si el `<title>` contiene la keyword y NO matchea blacklist."""
        title = (self._page_title(soup) or "").strip()
        if not title:
            return False
        if self._config.title_keyword.lower() not in title.lower():
            return False
        lower = title.lower()
        return not any(term in lower for term in _BLACKLIST_TITLE_TERMS)

    def _extract_card_images(self, soup: BeautifulSoup, source_url: str) -> list[CardImage]:
        """Extrae cards del post.

        Estrategia:
        - Solo busca dentro del `div.post-body` cuando existe (evita el
          sidebar "Popular Posts" del blog que tiene thumbnails que
          también matchean por accidente).
        - Itera `<a href="…blogger.googleusercontent.com…">`. Aplica dos
          filtros antes de aceptar:
            1. `FILENAME_BLACKLIST_TOKENS` — descarta variantes
               (Coca-Cola, McDonald's, Album, etc.) y hojas grupales
               por país aunque el nombre matchee la regex.
            2. `filename_pattern` — extrae el card_number.
        - Upgrade de resolución reemplazando `/sNNN/` por `/s1600/`.
        - Deduplica por `card_number` dentro de la página (la primera
          aparición gana).
        """
        scope: BeautifulSoup | Tag = soup
        post_body = soup.find("div", class_="post-body")
        if isinstance(post_body, Tag):
            scope = post_body

        seen: set[int] = set()
        cards: list[CardImage] = []
        for link in scope.find_all("a", href=True):
            if not isinstance(link, Tag):
                continue
            href = link.get("href", "")
            if not isinstance(href, str):
                continue
            if "blogger.googleusercontent.com" not in href:
                continue
            decoded = unquote(href)
            decoded_lower = decoded.lower()
            if any(token in decoded_lower for token in FILENAME_BLACKLIST_TOKENS):
                continue
            match = self._config.filename_pattern.search(decoded)
            if not match:
                continue
            try:
                number = int(match.group(1))
            except (ValueError, IndexError):
                continue
            if number in seen:
                continue
            seen.add(number)
            cards.append(
                CardImage(
                    card_number=number,
                    url=re.sub(r"/s\d+/", "/s1600/", href),
                    original_url=href,
                    source_page=source_url,
                )
            )
        return cards

    def _find_next_pages(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Links a otras páginas relevantes: Older/Newer Post + Blog Archive."""
        candidates: list[str] = []

        for css_class in ("blog-pager-older-link", "blog-pager-newer-link"):
            for node in soup.find_all("a", class_=css_class, href=True):
                if isinstance(node, Tag):
                    href = node.get("href")
                    if isinstance(href, str):
                        candidates.append(href)

        # Sidebar "Blog Archive": links cuyo title o texto matchee la keyword.
        keyword_lower = self._config.title_keyword.lower()
        for node in soup.find_all("a", href=True):
            if not isinstance(node, Tag):
                continue
            href = node.get("href")
            if not isinstance(href, str) or not href:
                continue
            label = str(node.get("title") or node.get_text(strip=True) or "").lower()
            if keyword_lower in label:
                candidates.append(href)

        # Normalizar a URL absoluta y dedupe contra ya-visitadas.
        absolute: list[str] = []
        seen_local: set[str] = set()
        for href in candidates:
            full = urljoin(current_url or BLOG_BASE_URL, href)
            if full in self._visited_pages or full in seen_local:
                continue
            seen_local.add(full)
            absolute.append(full)
        return absolute

    # ------------------------------------------------------------------
    # Descarga
    # ------------------------------------------------------------------

    def _download_card(self, card: CardImage) -> str:
        """Descarga `card`. Retorna `'downloaded'` | `'skipped'` | `'failed'`."""
        dest = self._output_dir / format_card_filename(card.card_number, "jpg")

        # Dedupe cross-página: si ya bajamos la card en una visita anterior
        # del mismo run, evitar el HTTP request (la misma sticker aparece
        # en checklist + página país + páginas individuales).
        if card.card_number in self._downloaded_numbers and not self._force:
            self._info("Card %04d → ya descargada en este run, skip", card.card_number)
            return "skipped"

        if dest.exists() and not self._force:
            self._info("Card %04d → ya existe, skip", card.card_number)
            return "skipped"

        try:
            r = self._session.get(card.url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            self._info("Card %04d → falló: %s", card.card_number, exc)
            return "failed"

        if r.status_code != 200:
            self._info("Card %04d → falló: HTTP %s", card.card_number, r.status_code)
            return "failed"

        content = r.content
        if len(content) < MIN_VALID_IMAGE_BYTES:
            self._info(
                "Card %04d → falló: %d bytes (esperaba > %d)",
                card.card_number,
                len(content),
                MIN_VALID_IMAGE_BYTES,
            )
            return "failed"

        if not (content.startswith(JPEG_MAGIC) or content.startswith(PNG_MAGIC)):
            self._info("Card %04d → falló: contenido no parece JPEG/PNG", card.card_number)
            return "failed"

        dest.write_bytes(content)
        time.sleep(DELAY_BETWEEN_REQUESTS)
        self._info("Card %04d → descargada (%d KB)", card.card_number, len(content) // 1024)
        return "downloaded"

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _info(self, fmt: str, *args: object) -> None:
        """Loguea via `logging` y propaga al callback `on_log`."""
        message = fmt % args if args else fmt
        logger.info("[scraper] %s", message)
        self._log(f"[scraper] {message}")


def _compress_ranges(numbers: list[int]) -> str:
    """Comprime una lista de enteros consecutivos en rangos legibles.

    Ejemplos:
        _compress_ranges([])                  → ""
        _compress_ranges([1])                 → "001"
        _compress_ranges([1, 2, 3])           → "001-003"
        _compress_ranges([1, 2, 3, 5, 7, 8])  → "001-003, 005, 007-008"
    """
    if not numbers:
        return ""
    ranges: list[str] = []
    start = end = numbers[0]
    for n in numbers[1:]:
        if n == end + 1:
            end = n
        else:
            ranges.append(f"{start:03d}" if start == end else f"{start:03d}-{end:03d}")
            start = end = n
    ranges.append(f"{start:03d}" if start == end else f"{start:03d}-{end:03d}")
    return ", ".join(ranges)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=("Descarga cards de Panini desde cartophilic-info-exch.blogspot.com"),
    )
    parser.add_argument("--collection", required=True, choices=list(COLLECTIONS))
    parser.add_argument(
        "--collection-id",
        type=int,
        default=None,
        help="Override del collection_id (carpeta de salida)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-descargar aunque el archivo destino ya exista",
    )
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument(
        "--seed-url",
        default=None,
        help="Override de la URL semilla (útil para arrancar desde otro post)",
    )
    args = parser.parse_args(argv)

    config = COLLECTIONS[args.collection]
    if args.collection_id is not None:
        config = replace(config, collection_id=args.collection_id)
    if args.seed_url:
        config = replace(config, seed_url=args.seed_url)

    output_dir = get_generated_cards_dir() / str(config.collection_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output: {output_dir}")
    print(f"Seed:   {config.seed_url}")
    print(f"Force:  {args.force}")
    print()

    scraper = PaniniScraper(
        config=config,
        output_dir=output_dir,
        force=args.force,
        max_pages=args.max_pages,
        on_log=print,
    )
    result = scraper.run()

    print()
    print("=== Resumen ===")
    print(f"Páginas visitadas:  {result.pages_visited}")
    print(f"Cards descargadas:  {result.downloaded}")
    print(f"Cards omitidas:     {result.skipped}")
    print(f"Fallos:             {result.failed}")
    if result.missing_numbers:
        total_missing = len(result.missing_numbers)
        print(f"Cards faltantes:    {total_missing} de {config.expected_total}")
        # Comprimir en rangos y mostrar primeros 30 grupos para no saturar.
        compressed = _compress_ranges(result.missing_numbers).split(", ")
        preview = ", ".join(compressed[:30])
        suffix = f" (+{len(compressed) - 30} rangos más)" if len(compressed) > 30 else ""
        print(f"Rangos: {preview}{suffix}")
    return 0 if result.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
```

### [src/collections_app/admin/tools/rename_legacy_cards.py](src/collections_app/admin/tools/rename_legacy_cards.py)

```python
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
```

### [src/collections_app/admin/views/__init__.py](src/collections_app/admin/views/__init__.py)

```python
"""Vistas concretas del admin (ABMs y master-detail)."""
```

### [src/collections_app/admin/views/cards_abm.py](src/collections_app/admin/views/cards_abm.py)

```python
"""ABM concreto de Cards: combo de colección + ABM + import CSV."""

import logging
import sqlite3
from pathlib import Path

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.tools.csv_importer import CardsCsvImporter, CsvImportResult
from collections_app.core.models import Card, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class CardsAbmView(QWidget):
    """Vista para administrar cards de una colección.

    Layout:
        Combo de colección + botón Importar CSV
        AbmWidget reconstruido cuando cambia la colección (porque los
        choices del combo `code_id` dependen del header de la colección).
    """

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._current_collection: Collection | None = None
        self._cards_widget: AbmWidget | None = None
        # Retiene referencias a widgets descartados al cambiar de colección
        # para que sigan siendo padres válidos de cualquier evento pendiente
        # (Qt + Python GC + signals async = crashes en Windows si liberamos
        # demasiado pronto).
        self._discarded_widgets: list[AbmWidget] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addLayout(self._build_top_bar())

        self._abm_container = QVBoxLayout()
        self._abm_container.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self._abm_container, stretch=1)

        self.refresh_collections_combo()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802 — Qt naming
        """Refresca el combo cada vez que el tab se hace visible."""
        super().showEvent(event)
        self.refresh_collections_combo()

    # ------------------------------------------------------------------
    # Top bar
    # ------------------------------------------------------------------

    def _build_top_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)

        layout.addWidget(QLabel(self.tr("Colección") + ":"))
        self._collection_combo = QComboBox()
        self._collection_combo.setMinimumWidth(280)
        self._collection_combo.currentIndexChanged.connect(self._on_collection_changed)
        layout.addWidget(self._collection_combo)

        layout.addStretch()

        self._import_button = QPushButton(self.tr("Importar CSV…"))
        self._import_button.clicked.connect(self._import_csv)
        self._import_button.setEnabled(False)
        layout.addWidget(self._import_button)
        return layout

    def refresh_collections_combo(self) -> None:
        """Re-popula el combo de colecciones desde la DB.

        Preserva la selección actual si la `collection_id` sigue existiendo
        (refresca el cache del nombre por si fue editada). Si la colección
        activa fue borrada, vuelve a "(ninguna)" y el AbmWidget se
        deshabilita.
        """
        previous_id = self._current_collection.collection_id if self._current_collection else None

        repo = CollectionsRepository(self.conn)
        all_collections = repo.list_all()
        all_ids = {c.collection_id for c in all_collections if c.collection_id is not None}

        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        self._collection_combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in all_collections:
            self._collection_combo.addItem(col.collection_name, userData=col.collection_id)

        if previous_id is not None and previous_id in all_ids:
            # La colección sigue existiendo: preservar selección y refrescar
            # el cache local (puede haber cambiado de nombre).
            idx = self._collection_combo.findData(previous_id)
            self._collection_combo.setCurrentIndex(idx)
            self._collection_combo.blockSignals(False)
            self._current_collection = repo.get_by_id(previous_id)
            return

        # Sin selección previa, o la selección previa fue borrada.
        self._collection_combo.setCurrentIndex(0)
        self._collection_combo.blockSignals(False)
        self._current_collection = None
        self._import_button.setEnabled(False)
        self._clear_abm()

    # ------------------------------------------------------------------
    # Selección de colección → reconstrucción del AbmWidget
    # ------------------------------------------------------------------

    def _on_collection_changed(self, idx: int) -> None:
        collection_id = self._collection_combo.itemData(idx)
        if collection_id is None:
            self._current_collection = None
            self._import_button.setEnabled(False)
            self._clear_abm()
            return

        collection = CollectionsRepository(self.conn).get_by_id(int(collection_id))
        if collection is None:
            return

        self._current_collection = collection
        self._import_button.setEnabled(True)
        self._rebuild_cards_abm()

    def _clear_abm(self) -> None:
        if self._cards_widget is not None:
            self._cards_widget.blockSignals(True)
            self._abm_container.removeWidget(self._cards_widget)
            self._cards_widget.hide()
            # Lo retenemos en una lista para no liberar el QObject mientras
            # hay events pendientes; se libera cuando el view padre muere.
            self._discarded_widgets.append(self._cards_widget)
            self._cards_widget = None

    def _rebuild_cards_abm(self) -> None:
        assert self._current_collection is not None
        assert self._current_collection.collection_id is not None
        cid: int = self._current_collection.collection_id
        header_id = self._current_collection.code_header_id

        lines = CodesLinesRepository(self.conn).list_by_header(header_id)
        code_choices: list[tuple[str, object]] = [
            (f"{line.code_id} — {line.code_name}", line.code_id) for line in lines
        ]

        config = AbmConfig(
            title=self.tr("ABM Cards de {name}").format(
                name=self._current_collection.collection_name
            ),
            module_code="CARD001",
            fields=[
                FieldDef(
                    "code_id",
                    "Código",
                    FieldType.COMBO,
                    is_id=True,
                    combo_choices=code_choices,
                    grid_width=130,
                ),
                FieldDef(
                    "card_number",
                    "Número",
                    FieldType.INT,
                    is_id=True,
                    grid_width=80,
                ),
                FieldDef(
                    "card_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=200,
                    grid_width=300,
                ),
            ],
            filter_field="card_name",
            filter_label=self.tr("Buscar por nombre"),
            on_load_all=lambda: CardsRepository(self.conn).list_by_collection(cid),
            on_save=self._save_card,
            on_delete=self._delete_card,
            model_class=Card,
            extra_kwargs={"collection_id": cid},
        )

        self._clear_abm()
        self._cards_widget = AbmWidget(config, parent=self)
        self._abm_container.addWidget(self._cards_widget)

    def _save_card(self, card: Card) -> Card:
        saved = CardsRepository(self.conn).upsert(card)
        self.conn.commit()
        return saved

    def _delete_card(self, card: Card) -> bool:
        ok = CardsRepository(self.conn).delete(card.collection_id, card.code_id, card.card_number)
        self.conn.commit()
        return ok

    # ------------------------------------------------------------------
    # Import CSV
    # ------------------------------------------------------------------

    def _import_csv(self) -> None:
        if self._current_collection is None:
            return

        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar cards desde CSV"),
            "",
            self.tr("CSV files (*.csv)"),
        )
        if not path_str:
            return

        progress = QProgressDialog(
            self.tr("Importando cards…"),
            self.tr("Cancelar"),
            0,
            100,
            self,
        )
        progress.setWindowModality(progress.windowModality())
        progress.setMinimumDuration(0)

        def _update(current: int, total: int) -> None:
            if total > 0:
                progress.setMaximum(total)
                progress.setValue(current)

        assert self._current_collection.collection_id is not None
        cid: int = self._current_collection.collection_id
        importer = CardsCsvImporter(self.conn)
        try:
            result = importer.import_file(
                Path(path_str),
                cid,
                on_progress=_update,
            )
        except Exception as exc:  # noqa: BLE001
            progress.close()
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            logger.exception("Error importando CSV")
            return

        progress.close()
        self._show_import_result(result)
        if self._cards_widget is not None:
            self._cards_widget.refresh()

    def _show_import_result(self, result: CsvImportResult) -> None:
        text = self.tr(
            "Importación completada.\n" "Total: {total}\nImportadas: {ok}\nOmitidas: {skipped}"
        ).format(
            total=result.total_rows,
            ok=result.imported,
            skipped=result.skipped,
        )
        if result.errors:
            sample = "\n".join(result.errors[:10])
            text += "\n\n" + self.tr("Primeros errores:") + "\n" + sample
        QMessageBox.information(self, self.tr("Importar CSV"), text)
```

### [src/collections_app/admin/views/codes_master_detail.py](src/collections_app/admin/views/codes_master_detail.py)

```python
"""Vista master-detail: headers de códigos y sus líneas."""

import logging
import sqlite3
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.tools.codes_csv_importer import (
    CodesCsvImporter,
    CodesCsvImportResult,
)
from collections_app.core.models import CodeHeader, CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType

logger = logging.getLogger(__name__)


class CodesMasterDetailView(QWidget):
    """Master (codes_headers) arriba, detail (codes_lines) abajo.

    Cuando el usuario selecciona un header, el detail se habilita y
    muestra sus líneas. Crear/editar líneas usa siempre el header
    actualmente seleccionado vía `extra_kwargs`.
    """

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._current_header: CodeHeader | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # MASTER
        self.headers_abm = self._build_headers_abm()
        layout.addWidget(self.headers_abm, stretch=1)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Fila con label + botón importar CSV
        detail_header_row = QHBoxLayout()
        detail_header_row.setContentsMargins(0, 0, 0, 0)
        self.detail_label = QLabel(self.tr("Seleccione un header para ver sus códigos"))
        self.detail_label.setStyleSheet("font-weight: 500; padding: 8px;")
        detail_header_row.addWidget(self.detail_label)
        detail_header_row.addStretch()
        self._import_lines_button = QPushButton(self.tr("Importar códigos desde CSV…"))
        self._import_lines_button.setEnabled(False)
        self._import_lines_button.clicked.connect(self._import_lines_csv)
        detail_header_row.addWidget(self._import_lines_button)
        layout.addLayout(detail_header_row)

        # DETAIL
        self.lines_abm, self._lines_config = self._build_lines_abm()
        self.lines_abm.setEnabled(False)
        layout.addWidget(self.lines_abm, stretch=1)

        # Conexiones master ↔ detail
        self.headers_abm.grid_selection_changed.connect(self._on_header_selected)
        self.headers_abm.record_saved.connect(self._on_header_saved)
        self.headers_abm.record_deleted.connect(self._on_header_deleted)

    # ------------------------------------------------------------------
    # Construcción
    # ------------------------------------------------------------------

    def _build_headers_abm(self) -> AbmWidget:
        config = AbmConfig(
            title=self.tr("Headers de Códigos"),
            module_code="COD001",
            fields=[
                FieldDef(
                    "code_header_id",
                    "ID",
                    FieldType.READONLY,
                    is_id=True,
                    is_required=False,
                    grid_width=50,
                ),
                FieldDef(
                    "code_header_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=250,
                ),
                FieldDef(
                    "code_max_length",
                    "Max longitud código",
                    FieldType.INT,
                    grid_width=150,
                ),
            ],
            filter_field="code_header_name",
            on_load_all=lambda: CodesHeadersRepository(self.conn).list_all(),
            on_save=self._save_header,
            on_delete=self._delete_header,
            model_class=CodeHeader,
        )
        return AbmWidget(config)

    def _build_lines_abm(self) -> tuple[AbmWidget, AbmConfig]:
        config = AbmConfig(
            title=self.tr("Códigos del header"),
            module_code="COD002",
            fields=[
                FieldDef(
                    "code_id",
                    "Código",
                    FieldType.TEXT,
                    is_id=True,
                    max_length=10,
                    grid_width=80,
                ),
                FieldDef(
                    "code_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=250,
                ),
                FieldDef(
                    "code_order",
                    "Orden",
                    FieldType.INT,
                    is_required=False,
                    grid_width=80,
                ),
            ],
            filter_field="code_id",
            on_load_all=lambda: [],  # se reasigna al seleccionar un header
            on_save=self._save_line,
            on_delete=self._delete_line,
            on_validate=self._validate_line,
            model_class=CodeLine,
        )
        widget = AbmWidget(config)
        return widget, config

    # ------------------------------------------------------------------
    # Callbacks de master
    # ------------------------------------------------------------------

    def _save_header(self, header: CodeHeader) -> CodeHeader:
        repo = CodesHeadersRepository(self.conn)
        saved = repo.create(header) if header.code_header_id is None else repo.update(header)
        self.conn.commit()
        return saved

    def _delete_header(self, header: CodeHeader) -> bool:
        assert header.code_header_id is not None
        ok = CodesHeadersRepository(self.conn).delete(header.code_header_id)
        self.conn.commit()
        return ok

    def _on_header_selected(self, header: CodeHeader) -> None:
        self._current_header = header
        self.detail_label.setText(
            self.tr("Códigos del header: {name}").format(name=header.code_header_name)
        )
        self.lines_abm.setEnabled(True)
        self._import_lines_button.setEnabled(True)
        self._refresh_lines_for_current_header()

    def _on_header_saved(self, header: CodeHeader) -> None:
        # Si el header guardado es el actual, refresca su nombre en el label
        if self._current_header and (self._current_header.code_header_id == header.code_header_id):
            self._current_header = header
            self.detail_label.setText(
                self.tr("Códigos del header: {name}").format(name=header.code_header_name)
            )

    def _on_header_deleted(self, header: CodeHeader) -> None:
        if self._current_header and self._current_header.code_header_id == header.code_header_id:
            self._current_header = None
            self.detail_label.setText(self.tr("Seleccione un header para ver sus códigos"))
            self.lines_abm.setEnabled(False)
            self._import_lines_button.setEnabled(False)
            self._lines_config.on_load_all = lambda: []
            self._lines_config.extra_kwargs = {}
            self.lines_abm.refresh()
            self.lines_abm.clear_form()

    # ------------------------------------------------------------------
    # Detail / lines
    # ------------------------------------------------------------------

    def _refresh_lines_for_current_header(self) -> None:
        if self._current_header is None or self._current_header.code_header_id is None:
            return
        hid: int = self._current_header.code_header_id
        self._lines_config.on_load_all = lambda: CodesLinesRepository(self.conn).list_by_header(hid)
        self._lines_config.extra_kwargs = {"code_header_id": hid}
        self.lines_abm.refresh()
        self.lines_abm.clear_form()

    def _save_line(self, line: CodeLine) -> CodeLine:
        repo = CodesLinesRepository(self.conn)
        saved = repo.upsert(line)
        self.conn.commit()
        return saved

    def _delete_line(self, line: CodeLine) -> bool:
        ok = CodesLinesRepository(self.conn).delete(line.code_header_id, line.code_id)
        self.conn.commit()
        return ok

    def _validate_line(self, line: CodeLine) -> tuple[bool, str]:
        if self._current_header is None:
            return False, self.tr("No hay header seleccionado.")
        if len(line.code_id) > self._current_header.code_max_length:
            return False, self.tr("El código '{code}' excede la longitud máxima ({max}).").format(
                code=line.code_id, max=self._current_header.code_max_length
            )
        return True, ""

    # ------------------------------------------------------------------
    # Importar líneas desde CSV
    # ------------------------------------------------------------------

    def _import_lines_csv(self) -> None:
        if self._current_header is None or self._current_header.code_header_id is None:
            return

        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar códigos desde CSV"),
            "",
            self.tr("CSV files (*.csv)"),
        )
        if not path_str:
            return

        progress = QProgressDialog(
            self.tr("Importando códigos…"),
            self.tr("Cancelar"),
            0,
            100,
            self,
        )
        progress.setMinimumDuration(0)

        def _update(current: int, total: int) -> None:
            if total > 0:
                progress.setMaximum(total)
                progress.setValue(current)

        importer = CodesCsvImporter(self.conn)
        try:
            result = importer.import_file(
                Path(path_str),
                self._current_header.code_header_id,
                on_progress=_update,
            )
        except Exception as exc:  # noqa: BLE001
            progress.close()
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            logger.exception("Error importando CSV de códigos")
            return

        progress.close()
        self._show_import_result(result)
        self._refresh_lines_for_current_header()

    def _show_import_result(self, result: CodesCsvImportResult) -> None:
        text = self.tr(
            "Importación completada.\n" "Total: {total}\nImportadas: {ok}\nOmitidas: {skipped}"
        ).format(total=result.total_rows, ok=result.imported, skipped=result.skipped)
        if result.errors:
            sample = "\n".join(result.errors[:10])
            text += "\n\n" + self.tr("Primeros errores:") + "\n" + sample
        QMessageBox.information(self, self.tr("Importar CSV"), text)
```

### [src/collections_app/admin/views/collections_abm.py](src/collections_app/admin/views/collections_abm.py)

```python
"""ABM concreto de colecciones."""

import sqlite3

from PySide6.QtWidgets import QVBoxLayout, QWidget

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CollectionsRepository,
)
from collections_app.core.services import CollectionsService
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType


class CollectionsAbmView(QWidget):
    """ABM de Collections, con combo de header y validaciones de negocio."""

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn

        config = AbmConfig(
            title=self.tr("ABM Colecciones"),
            module_code="COL001",
            fields=[
                FieldDef(
                    "collection_id",
                    "ID",
                    FieldType.READONLY,
                    is_id=True,
                    is_required=False,
                    grid_width=50,
                ),
                FieldDef(
                    "collection_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=200,
                ),
                FieldDef(
                    "card_count",
                    "Cantidad de cards",
                    FieldType.INT,
                    grid_width=120,
                ),
                FieldDef(
                    "requires_code",
                    "Requiere código",
                    FieldType.BOOL,
                    is_required=False,
                    grid_width=130,
                ),
                FieldDef(
                    "code_field_name",
                    "Etiqueta del código",
                    FieldType.TEXT,
                    max_length=50,
                    is_required=False,
                    placeholder=self.tr("ej: Set, País"),
                    grid_width=150,
                ),
                FieldDef(
                    "code_header_id",
                    "Cabecera de código",
                    FieldType.COMBO,
                    combo_choices=self._get_header_choices,
                    grid_width=180,
                ),
                FieldDef(
                    "is_premium",
                    "Premium",
                    FieldType.BOOL,
                    is_required=False,
                    grid_width=80,
                ),
                FieldDef(
                    "license_key_required",
                    "Hash de licencia",
                    FieldType.TEXT,
                    max_length=100,
                    is_required=False,
                    show_in_grid=False,
                ),
                # Layout del PDF álbum: configurable por colección porque
                # cards horizontales y verticales necesitan distintas grillas.
                FieldDef(
                    "album_columns",
                    "Álbum: columnas",
                    FieldType.INT,
                    is_required=False,
                    grid_width=100,
                    default_value=3,
                ),
                FieldDef(
                    "album_rows",
                    "Álbum: filas",
                    FieldType.INT,
                    is_required=False,
                    grid_width=100,
                    default_value=4,
                ),
                FieldDef(
                    "album_orientation",
                    "Álbum: orientación",
                    FieldType.COMBO,
                    combo_choices=[
                        ("Vertical (portrait)", "portrait"),
                        ("Horizontal (landscape)", "landscape"),
                    ],
                    is_required=False,
                    grid_width=170,
                    default_value="portrait",
                ),
            ],
            filter_field="collection_name",
            filter_label=self.tr("Buscar por nombre"),
            on_load_all=self._load,
            on_save=self._save,
            on_delete=self._delete,
            on_validate=self._validate,
            model_class=Collection,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.abm = AbmWidget(config)
        layout.addWidget(self.abm)

    def _get_header_choices(self) -> list[tuple[str, object]]:
        """Choices del combo "Cabecera de código", evaluado en cada uso.

        Pasamos este método como callable a `FieldDef.combo_choices` para
        que `AbmWidget` lo re-evalúe cada vez que el form se limpia o se
        carga una fila — así nuevas cabeceras creadas en otros tabs
        aparecen sin reiniciar la app.
        """
        repo = CodesHeadersRepository(self.conn)
        return [(h.code_header_name, h.code_header_id) for h in repo.list_all()]

    def _load(self) -> list[Collection]:
        return CollectionsRepository(self.conn).list_all()

    def _save(self, collection: Collection) -> Collection:
        if collection.collection_id is None:
            saved = CollectionsService(self.conn).create_collection_with_validation(collection)
        else:
            saved = CollectionsRepository(self.conn).update(collection)
        self.conn.commit()
        return saved

    def _delete(self, collection: Collection) -> bool:
        assert collection.collection_id is not None
        ok = CollectionsRepository(self.conn).delete(collection.collection_id)
        self.conn.commit()
        return ok

    def _validate(self, collection: Collection) -> tuple[bool, str]:
        if collection.requires_code and not collection.code_field_name:
            return False, self.tr("Si requiere código, debe especificarse la etiqueta del campo.")
        if collection.is_premium and not collection.license_key_required:
            return False, self.tr("Las colecciones premium deben tener hash de licencia.")
        if not 1 <= collection.album_columns <= 8:
            return False, self.tr("Álbum: columnas debe estar entre 1 y 8.")
        if not 1 <= collection.album_rows <= 8:
            return False, self.tr("Álbum: filas debe estar entre 1 y 8.")
        if collection.album_orientation not in ("portrait", "landscape"):
            return False, self.tr("Álbum: orientación debe ser 'portrait' o 'landscape'.")
        return True, ""
```

### [src/collections_app/admin/views/crests_view.py](src/collections_app/admin/views/crests_view.py)

```python
"""Tab Escudos: gestiona el escudo de cada code_id de una colección."""

import logging
import shutil
import sqlite3
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.crests import (
    SOURCE_COMMONS,
    SOURCE_COMMONS_OVERRIDE,
    SOURCE_NOT_FOUND,
    SOURCE_PLACEHOLDER,
    SPECIAL_CODES,
    CrestFinder,
    CrestResult,
    is_valid_crest_file,
)
from collections_app.core.models import CodeLine, Collection
from collections_app.core.repositories import (
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.core.utils.paths import get_crest_path
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)

PREVIEW_SIZE = 150
ICON_SIZE = 32

STATUS_NONE = "Sin escudo"  # no hay archivo (nunca se buscó o búsqueda no encontró)
STATUS_FOUND = "✓ Encontrado"  # archivo válido descargado (Wikimedia Commons u origen)
STATUS_MANUAL = "Manual"
STATUS_PLACEHOLDER = "Placeholder"


class _CrestSearchWorker(QThread):
    """Ejecuta `CrestFinder.find_all_crests` en un thread separado.

    Wikimedia Commons no requiere credenciales ni acceso a la DB, así que
    el worker es completamente stateless respecto al storage: solo recibe
    la lista de codes y delega al finder.
    """

    progress = Signal(int, int, str)
    finished_ok = Signal(list)  # list[CrestResult]
    failed = Signal(str)

    def __init__(
        self,
        finder: CrestFinder,
        codes: list[tuple[str, str]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._finder = finder
        self._codes = codes

    def run(self) -> None:
        try:
            results = self._finder.find_all_crests(self._codes, on_progress=self._emit)
            self.finished_ok.emit(results)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error en _CrestSearchWorker")
            self.failed.emit(str(exc))

    def _emit(self, current: int, total: int, label: str) -> None:
        self.progress.emit(current, total, label)


class CrestsView(QWidget):
    """Tab admin: ver / buscar / importar escudos por code_id."""

    COL_ICON = 0
    COL_CODE = 1
    COL_NAME = 2
    COL_STATUS = 3

    def __init__(
        self,
        conn: sqlite3.Connection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._finder = CrestFinder()
        self._worker: _CrestSearchWorker | None = None
        self._build_ui()
        self._populate_collections_combo()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Gestión de Escudos"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        # Combo de colecciones
        combo_row = QHBoxLayout()
        combo_row.addWidget(QLabel(self.tr("Colección") + ":"))
        self._collection_combo = QComboBox()
        self._collection_combo.setMinimumWidth(280)
        self._collection_combo.currentIndexChanged.connect(self._on_collection_changed)
        combo_row.addWidget(self._collection_combo)
        combo_row.addStretch()
        layout.addLayout(combo_row)

        # Tabla
        self._model = QStandardItemModel(0, 4, self)
        self._model.setHorizontalHeaderLabels(
            [self.tr(""), self.tr("Code"), self.tr("Nombre"), self.tr("Estado")]
        )
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(self.COL_ICON, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_CODE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeMode.ResizeToContents)
        self._table.selectionModel().currentRowChanged.connect(self._on_row_selected)
        layout.addWidget(self._table, stretch=1)

        # Botonera
        buttons_row = QHBoxLayout()
        self._search_button = QPushButton(self.tr("🌐 Buscar automáticamente (países)"))
        self._search_button.clicked.connect(self._search_auto)
        self._import_button = QPushButton(self.tr("📂 Importar imagen para code seleccionado"))
        self._import_button.clicked.connect(self._import_manual)
        self._delete_button = QPushButton(self.tr("🗑️ Borrar escudo seleccionado"))
        self._delete_button.clicked.connect(self._delete_crest)
        buttons_row.addWidget(self._search_button)
        buttons_row.addWidget(self._import_button)
        buttons_row.addWidget(self._delete_button)
        buttons_row.addStretch()
        layout.addLayout(buttons_row)

        # Preview
        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel(self.tr("Preview") + ":"))
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(PREVIEW_SIZE, PREVIEW_SIZE)
        self._preview_label.setStyleSheet("border: 1px solid #888; background: #f0f0f0;")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_row.addWidget(self._preview_label)
        preview_row.addStretch()
        layout.addLayout(preview_row)

    def _populate_collections_combo(self) -> None:
        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        self._collection_combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in CollectionsRepository(self.conn).list_all():
            self._collection_combo.addItem(col.collection_name, userData=col.collection_id)
        self._collection_combo.blockSignals(False)
        self._on_collection_changed(self._collection_combo.currentIndex())

    # ------------------------------------------------------------------
    # Cambios de selección
    # ------------------------------------------------------------------

    def _on_collection_changed(self, idx: int) -> None:
        del idx
        cid = self._current_collection_id()
        if cid is None:
            self._model.removeRows(0, self._model.rowCount())
            self._set_buttons_enabled(False)
            self._preview_label.clear()
            return
        self._refresh_grid(cid)
        self._set_buttons_enabled(True)

    def _current_collection_id(self) -> int | None:
        data = self._collection_combo.currentData()
        return int(data) if data is not None else None

    def _current_collection(self) -> Collection | None:
        cid = self._current_collection_id()
        if cid is None:
            return None
        return CollectionsRepository(self.conn).get_by_id(cid)

    def _selected_code_line(self) -> CodeLine | None:
        idx = self._table.currentIndex()
        if not idx.isValid():
            return None
        row = idx.row()
        code_id = self._model.item(row, self.COL_CODE).text()
        code_name = self._model.item(row, self.COL_NAME).text()
        col = self._current_collection()
        header_id = col.code_header_id if col is not None else 0
        return CodeLine(code_header_id=header_id, code_id=code_id, code_name=code_name)

    def _on_row_selected(self) -> None:
        line = self._selected_code_line()
        if line is None:
            self._preview_label.clear()
            return
        path = get_crest_path(line.code_id)
        if is_valid_crest_file(path):
            pix = QPixmap(str(path)).scaled(
                PREVIEW_SIZE,
                PREVIEW_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._preview_label.setPixmap(pix)
        else:
            self._preview_label.clear()
            self._preview_label.setText(self.tr("(sin escudo)"))

    # ------------------------------------------------------------------
    # Grid
    # ------------------------------------------------------------------

    def _refresh_grid(self, collection_id: int) -> None:
        col = CollectionsRepository(self.conn).get_by_id(collection_id)
        if col is None:
            self._model.removeRows(0, self._model.rowCount())
            return
        lines = CodesLinesRepository(self.conn).list_by_header(col.code_header_id)

        # Limpieza silenciosa: archivos en disco que no superan el umbral
        # de validez son restos de descargas fallidas anteriores. Borrarlos
        # acá garantiza que la grilla no muestre iconos vacíos y que la
        # próxima búsqueda automática los reintente.
        for line in lines:
            path = get_crest_path(line.code_id)
            if path.exists() and not is_valid_crest_file(path):
                path.unlink(missing_ok=True)
                logger.debug("Eliminado crest inválido pre-existente: %s", line.code_id)

        self._model.removeRows(0, self._model.rowCount())
        for line in lines:
            self._model.appendRow(self._build_row(line))

    def _build_row(self, line: CodeLine) -> list[QStandardItem]:
        path = get_crest_path(line.code_id)
        icon_item = QStandardItem()
        if is_valid_crest_file(path):
            icon_item.setIcon(QIcon(str(path)))
        code_item = QStandardItem(line.code_id)
        name_item = QStandardItem(line.code_name)
        status_item = QStandardItem(self._compute_status(line.code_id, path))
        return [icon_item, code_item, name_item, status_item]

    def _compute_status(self, code_id: str, path: Path) -> str:
        if not is_valid_crest_file(path):
            # Sin archivo válido. Para SPECIAL_CODES seguimos mostrando
            # "Placeholder" (su placeholder se genera siempre). Para el
            # resto: "Sin escudo" — la próxima búsqueda lo intentará.
            if code_id in SPECIAL_CODES:
                return STATUS_PLACEHOLDER
            return STATUS_NONE
        # Archivo válido en disco. SPECIAL_CODES → placeholder (visualmente
        # marca al usuario que tiene que importarlo manualmente). Resto →
        # encontrado (Google CSE o import manual; el preview muestra cuál).
        return STATUS_PLACEHOLDER if code_id in SPECIAL_CODES else STATUS_FOUND

    def _set_buttons_enabled(self, enabled: bool) -> None:
        running = self._worker is not None and self._worker.isRunning()
        self._search_button.setEnabled(enabled and not running)
        self._import_button.setEnabled(enabled and not running)
        self._delete_button.setEnabled(enabled and not running)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _search_auto(self) -> None:
        cid = self._current_collection_id()
        if cid is None:
            return
        col = CollectionsRepository(self.conn).get_by_id(cid)
        if col is None:
            return
        # Procesamos sólo codes que NO están en SPECIAL_CODES y que NO
        # tienen un escudo VÁLIDO cacheado. Los archivos en disco que no
        # superan `is_valid_crest_file` (corruptos / vacíos / truncados de
        # un intento previo) se reincluyen como candidatos; CrestFinder los
        # borra y reintenta antes de descargar.
        all_lines = CodesLinesRepository(self.conn).list_by_header(col.code_header_id)
        candidates: list[tuple[str, str]] = [
            (line.code_id, line.code_name)
            for line in all_lines
            if line.code_id not in SPECIAL_CODES
            and not is_valid_crest_file(get_crest_path(line.code_id))
        ]
        if not candidates:
            QMessageBox.information(
                self,
                self.tr("Buscar escudos"),
                self.tr("No hay códigos sin escudo para procesar."),
            )
            return

        # Limpieza de placeholders previos: archivos de ejecuciones anteriores
        # (cuando find_crest aún escribía SOURCE_PLACEHOLDER en disco) seguirían
        # contando como "cache válido" y bloquearían el reintento. Después del
        # cambio a SOURCE_NOT_FOUND ya no se generan, pero borramos los heredados.
        deleted = self._finder.cleanup_failed_placeholders(candidates)
        if deleted:
            logger.info("Limpiados %d placeholders previos antes de buscar", deleted)

        progress = QProgressDialog(
            self.tr("Descargando escudos…"),
            self.tr("Cancelar"),
            0,
            len(candidates),
            self,
        )
        progress.setWindowTitle(self.tr("Buscar escudos"))
        progress.setMinimumDuration(0)

        self._worker = _CrestSearchWorker(self._finder, candidates, parent=self)
        worker = self._worker

        def on_progress(c: int, _t: int, label: str) -> None:
            progress.setValue(c)
            progress.setLabelText(label)

        def on_ok(results: list[CrestResult]) -> None:
            progress.close()
            found = sum(1 for r in results if r.source in (SOURCE_COMMONS, SOURCE_COMMONS_OVERRIDE))
            ph = sum(1 for r in results if r.source == SOURCE_PLACEHOLDER)
            not_found = sum(1 for r in results if r.source == SOURCE_NOT_FOUND)
            QMessageBox.information(
                self,
                self.tr("Buscar escudos"),
                self.tr(
                    "Procesados: {n}. Encontrados: {f}. " "Sin resultado: {nf}. Placeholder: {p}."
                ).format(n=len(results), f=found, nf=not_found, p=ph),
            )
            assert cid is not None
            self._refresh_grid(cid)
            self._on_row_selected()
            self._set_buttons_enabled(True)

        def on_failed(msg: str) -> None:
            progress.close()
            QMessageBox.critical(self, self.tr("Buscar escudos"), msg)
            self._set_buttons_enabled(True)

        def on_canceled() -> None:
            worker.requestInterruption()
            progress.close()
            self._set_buttons_enabled(True)

        worker.progress.connect(on_progress)
        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        progress.canceled.connect(on_canceled)
        worker.start()
        self._set_buttons_enabled(True)

    def _import_manual(self) -> None:
        line = self._selected_code_line()
        if line is None:
            QMessageBox.warning(
                self,
                self.tr("Importar escudo"),
                self.tr("Seleccioná una fila primero."),
            )
            return
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Elegir imagen para {code}").format(code=line.code_id),
            "",
            self.tr("Imágenes (*.png *.jpg *.jpeg *.svg *.webp);;Todos (*)"),
        )
        if not path_str:
            return
        result = self._finder.import_manual_crest(line.code_id, Path(path_str))
        if not result.success:
            QMessageBox.critical(
                self,
                self.tr("Importar escudo"),
                self.tr("No se pudo procesar la imagen: {err}").format(err=result.error or ""),
            )
            return
        # Marcar el row como manual y refrescar
        cid = self._current_collection_id()
        if cid is not None:
            self._refresh_grid(cid)
        self._set_status_for(line.code_id, STATUS_MANUAL)
        self._on_row_selected()

    def _delete_crest(self) -> None:
        line = self._selected_code_line()
        if line is None:
            return
        path = get_crest_path(line.code_id)
        if not path.exists():
            return
        confirmed = QMessageBox.question(
            self,
            self.tr("Borrar escudo"),
            self.tr("¿Borrar el escudo de {code}?").format(code=line.code_id),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return
        path.unlink(missing_ok=True)
        cid = self._current_collection_id()
        if cid is not None:
            self._refresh_grid(cid)
        self._on_row_selected()

    def _set_status_for(self, code_id: str, status: str) -> None:
        for row in range(self._model.rowCount()):
            if self._model.item(row, self.COL_CODE).text() == code_id:
                self._model.item(row, self.COL_STATUS).setText(status)
                # Refrescar icono
                path = get_crest_path(code_id)
                if is_valid_crest_file(path):
                    self._model.item(row, self.COL_ICON).setIcon(QIcon(str(path)))
                return


# Helper exportado para uso externo (tests)
def copy_crest_file(src: Path, code_id: str) -> Path:
    """Copia `src` a `get_crest_path(code_id)` (para tests / scripts)."""
    dest = get_crest_path(code_id)
    shutil.copy(src, dest)
    return dest
```

### [src/collections_app/client/__init__.py](src/collections_app/client/__init__.py)

```python
"""Aplicación client: uso final por parte del coleccionista."""
```

### [src/collections_app/client/dialogs/__init__.py](src/collections_app/client/dialogs/__init__.py)

```python
"""Diálogos específicos de la app client."""
```

### [src/collections_app/client/dialogs/client_settings_dialog.py](src/collections_app/client/dialogs/client_settings_dialog.py)

```python
"""Diálogo de configuración del cliente: elección de colección + licencia."""

import logging
import sqlite3

from PySide6.QtCore import QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.__version__ import __app_name__, __version__
from collections_app.core.repositories import CollectionsRepository, SettingsRepository
from collections_app.core.services import LicenseService, SettingsService
from collections_app.core.services.update_service import (
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)
from collections_app.core.utils.datetime_helpers import (
    format_for_display,
    parse_db_datetime,
    utc_now,
)
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)

SETTING_LAST_UPDATE_CHECK = "last_update_check"
SETTING_SERVER_URL = "server_url"
SETTING_SERVER_API_KEY = "server_api_key"


class _ManualUpdateCheckWorker(QThread):
    """Worker para el botón "Buscar actualizaciones" del diálogo.

    Idéntico en espíritu al worker de main.py pero emite SIEMPRE un
    resultado (con `is_newer=False` cuando estamos al día) o `None`
    cuando no hay conexión — la UI necesita los tres estados (nueva /
    al día / sin red) para pintar el QLabel correctamente.
    """

    finished_check = Signal(object)  # UpdateInfo | None

    def __init__(
        self,
        source: UpdateSource | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source

    def run(self) -> None:
        try:
            service = UpdateService(self._source) if self._source else UpdateService()
            self.finished_check.emit(service.check_for_updates())
        except Exception:
            logger.exception("ManualUpdateCheckWorker: fallo inesperado")
            self.finished_check.emit(None)


class ClientSettingsDialog(QDialog):
    """Permite al usuario elegir la colección activa.

    Si la colección elegida es premium y aún no fue desbloqueada, muestra
    un campo de licencia con botón "Validar". El botón Aceptar queda
    deshabilitado hasta que la licencia se valide (o si la colección es free).

    Layout:
        Colección: [combo ▼]
        ── solo si premium y no unlocked ──
        Esta colección requiere licencia.
        Clave: [____] [Validar]
        ── separator ──
        Acerca de
          CollectionsApp v1.0.0
          [Buscar actualizaciones]
          (estado del último chequeo)
        [Cancelar] [Aceptar]
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._settings = SettingsService(conn)
        self._licenses = LicenseService(conn)
        self._collections_repo = CollectionsRepository(conn)
        self._settings_repo = SettingsRepository(conn)
        self._selected_id: int | None = None
        self._update_worker: _ManualUpdateCheckWorker | None = None
        self._last_update_info: UpdateInfo | None = None

        self.setWindowTitle(self.tr("Configuración"))
        self._build_ui()
        self._load_collections()
        self._update_license_section()
        self._refresh_last_check_label()

    @property
    def selected_collection_id(self) -> int | None:
        """ID de la colección elegida al aceptar, o None si canceló."""
        return self._selected_id

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)

        form = QFormLayout()
        self._combo = QComboBox()
        self._combo.setMinimumWidth(280)
        self._combo.currentIndexChanged.connect(self._update_license_section)
        form.addRow(self.tr("Colección") + ":", self._combo)
        root.addLayout(form)

        # Sección de licencia (visible solo cuando hace falta)
        self._license_container = QWidget()
        license_layout = QVBoxLayout(self._license_container)
        license_layout.setContentsMargins(0, 0, 0, 0)
        license_layout.setSpacing(Spacing.SM)

        self._license_msg = QLabel(self.tr("Esta colección requiere licencia."))
        license_layout.addWidget(self._license_msg)

        license_row = QHBoxLayout()
        license_row.setContentsMargins(0, 0, 0, 0)
        license_row.addWidget(QLabel(self.tr("Clave") + ":"))
        self._license_input = QLineEdit()
        self._license_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._license_input.returnPressed.connect(self._on_validate_license)
        license_row.addWidget(self._license_input, stretch=1)
        self._validate_button = QPushButton(self.tr("Validar"))
        self._validate_button.clicked.connect(self._on_validate_license)
        license_row.addWidget(self._validate_button)
        license_layout.addLayout(license_row)

        self._license_status = QLabel("")
        license_layout.addWidget(self._license_status)
        root.addWidget(self._license_container)

        # Sección "Acerca de"
        root.addWidget(self._build_about_section())

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        root.addWidget(self._buttons)

    def _build_about_section(self) -> QWidget:
        """Construye el bloque "Acerca de" con versión y chequeo manual."""
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        title = QLabel("<b>" + self.tr("Acerca de") + "</b>")
        layout.addWidget(title)

        version_label = QLabel(f"{__app_name__} v{__version__}")
        layout.addWidget(version_label)

        # Botón + (eventual) "Descargar" en una fila.
        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        self._check_button = QPushButton(self.tr("Buscar actualizaciones"))
        self._check_button.clicked.connect(self._on_check_for_updates)
        button_row.addWidget(self._check_button)

        self._download_button = QPushButton(self.tr("Descargar"))
        self._download_button.setVisible(False)
        self._download_button.clicked.connect(self._on_download_clicked)
        button_row.addWidget(self._download_button)
        button_row.addStretch()
        layout.addLayout(button_row)

        # Estado del último chequeo (vacío hasta que se haga uno).
        self._update_status = QLabel("")
        self._update_status.setWordWrap(True)
        layout.addWidget(self._update_status)

        # Timestamp del último chequeo (siempre visible si hay valor).
        self._last_check_label = QLabel("")
        self._last_check_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(self._last_check_label)

        return container

    def _load_collections(self) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in self._collections_repo.list_all():
            self._combo.addItem(col.collection_name, userData=col.collection_id)

        active_id = self._settings.get_active_collection_id()
        if active_id is not None:
            idx = self._combo.findData(active_id)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Estado y validación de licencia
    # ------------------------------------------------------------------

    def _update_license_section(self) -> None:
        """Decide si mostrar el campo de licencia y habilitar 'Aceptar'."""
        collection_id = self._combo.currentData()
        if collection_id is None:
            self._license_container.setVisible(False)
            self._set_ok_enabled(False)
            return

        # Si ya está unlocked (free o premium-unlocked) → ocultar y habilitar Aceptar
        if self._licenses.is_unlocked(int(collection_id)):
            self._license_container.setVisible(False)
            self._set_ok_enabled(True)
            return

        # Necesita licencia y no está unlocked
        self._license_container.setVisible(True)
        self._license_input.clear()
        self._license_status.setText("")
        self._license_status.setStyleSheet("")
        self._set_ok_enabled(False)

    def _on_validate_license(self) -> None:
        collection_id = self._combo.currentData()
        if collection_id is None:
            return
        key = self._license_input.text().strip()
        if not key:
            self._show_license_status(self.tr("Ingresá una clave."), StatusColor.WARNING)
            return

        if self._licenses.unlock(int(collection_id), key):
            self._show_license_status(self.tr("Clave válida."), StatusColor.SUCCESS)
            self._license_container.setVisible(False)
            self._set_ok_enabled(True)
        else:
            self._show_license_status(self.tr("Clave inválida."), StatusColor.ERROR)
            self._set_ok_enabled(False)

    def _show_license_status(self, text: str, color: str) -> None:
        self._license_status.setText(text)
        self._license_status.setStyleSheet(f"color: {color};")

    def _set_ok_enabled(self, enabled: bool) -> None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(enabled)

    # ------------------------------------------------------------------
    # Update checker (botón "Buscar actualizaciones")
    # ------------------------------------------------------------------

    def _on_check_for_updates(self) -> None:
        """Lanza el chequeo manual en background — UI no se bloquea."""
        # Si ya hay un check corriendo, no relanzamos.
        if self._update_worker is not None and self._update_worker.isRunning():
            return
        self._check_button.setEnabled(False)
        self._download_button.setVisible(False)
        self._update_status.setText(self.tr("Verificando…"))
        self._update_status.setStyleSheet("")
        self._last_update_info = None

        # Si el usuario configuró servidor propio (futuro), usarlo.
        server_url = self._settings_repo.get(SETTING_SERVER_URL)
        source: UpdateSource | None = None
        if server_url:
            api_key = self._settings_repo.get(SETTING_SERVER_API_KEY) or ""
            source = ServerUpdateSource(server_url, api_key)

        self._update_worker = _ManualUpdateCheckWorker(source=source, parent=self)
        self._update_worker.finished_check.connect(self._on_update_check_finished)
        self._update_worker.start()

    def _on_update_check_finished(self, info: object) -> None:
        self._check_button.setEnabled(True)
        if info is None:
            # No hay conexión / fuente caída.
            self._update_status.setText(self.tr("No se pudo verificar (sin conexión)"))
            self._update_status.setStyleSheet(f"color: {StatusColor.WARNING};")
            return
        if not isinstance(info, UpdateInfo):
            return

        # Persistir timestamp del chequeo.
        self._settings_repo.set(SETTING_LAST_UPDATE_CHECK, utc_now().isoformat())
        self._conn.commit()
        self._refresh_last_check_label()

        if info.is_newer:
            self._last_update_info = info
            self._update_status.setText(
                self.tr("Hay una versión nueva: v{v}").format(v=info.latest_version)
            )
            self._update_status.setStyleSheet(f"color: {StatusColor.SUCCESS};")
            self._download_button.setVisible(True)
        else:
            self._update_status.setText(
                self.tr("Estás en la última versión (v{v})").format(v=info.current_version)
            )
            self._update_status.setStyleSheet(f"color: {StatusColor.SUCCESS};")

    def _on_download_clicked(self) -> None:
        if self._last_update_info is None:
            return
        QDesktopServices.openUrl(QUrl(self._last_update_info.download_url))

    def _refresh_last_check_label(self) -> None:
        """Pinta el timestamp del último chequeo (en hora local) si existe."""
        raw = self._settings_repo.get(SETTING_LAST_UPDATE_CHECK)
        if not raw:
            self._last_check_label.setText("")
            return
        try:
            dt = parse_db_datetime(raw)
        except ValueError:
            self._last_check_label.setText("")
            return
        self._last_check_label.setText(
            self.tr("Última verificación: {ts}").format(ts=format_for_display(dt))
        )

    # ------------------------------------------------------------------
    # Aceptar
    # ------------------------------------------------------------------

    def _on_accept(self) -> None:
        collection_id = self._combo.currentData()
        if collection_id is None:
            return
        cid = int(collection_id)
        if not self._licenses.is_unlocked(cid):
            return  # Defensa: no debería pasar (Aceptar disabled), pero por las dudas
        self._settings.set_active_collection(cid)
        self._conn.commit()
        self._selected_id = cid
        self.accept()
```

### [src/collections_app/client/dialogs/pdf_preview_dialog.py](src/collections_app/client/dialogs/pdf_preview_dialog.py)

```python
"""Dialog modal con preview de un PDF generado en archivo temporal.

Flujo del usuario:
  1. Click en un botón de "Generar PDF" en cualquier vista.
  2. La vista invoca el worker que genera el PDF en `%TEMP%`.
  3. Cuando el worker termina, instancia este dialog con el path temp.
  4. El usuario ve el PDF y decide:
     - "Guardar..." → QFileDialog → copia a destino → opción de abrir.
     - "Cancelar"   → borra el temp, no se guarda nada.

Si PySide6 fue compilado sin QtPdf/QtPdfWidgets (versiones viejas),
el dialog cae a un mensaje informativo: el usuario igual puede guardar
y abrir con su visor habitual.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class PdfPreviewDialog(QDialog):
    """Preview de un PDF antes de guardarlo a una ubicación final.

    `temp_pdf_path` es un archivo en `%TEMP%` que el dialog se hace
    cargo de borrar (en cancel o tras copiar al destino). Si el usuario
    cierra el dialog con la X también se limpia.
    """

    def __init__(
        self,
        temp_pdf_path: Path,
        suggested_filename: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Vista previa del PDF"))
        self.setMinimumSize(720, 820)
        self.setModal(True)

        self._temp_path = temp_pdf_path
        self._suggested_filename = suggested_filename
        self._saved_path: Path | None = None
        self._cleanup_done = False

        self._build_ui()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def saved_path(self) -> Path | None:
        """Path donde se guardó el PDF, o `None` si el usuario canceló."""
        return self._saved_path

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # Área de preview — QPdfView si está disponible, fallback si no.
        layout.addWidget(self._build_preview_area(), stretch=1)

        # Botones inferiores
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton(self.tr("Cancelar"))
        btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton(self.tr("Guardar…"))
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def _build_preview_area(self) -> QWidget:
        """Intenta crear un QPdfView; cae a QLabel informativo si no está.

        Carga el PDF a memoria via `QBuffer` en vez de pasarle el path
        a `QPdfDocument`. Razón: en Windows, `QPdfDocument.load(path)`
        mantiene un mmap sobre el archivo que sobrevive a `close()` y
        bloquea el `unlink(temp)` posterior. Cargando bytes en memoria
        no se toca el filesystem después de la lectura inicial.
        """
        try:
            from PySide6.QtCore import QBuffer, QByteArray
            from PySide6.QtPdf import QPdfDocument
            from PySide6.QtPdfWidgets import QPdfView
        except ImportError:
            return self._build_fallback_label()

        try:
            data = self._temp_path.read_bytes()
        except OSError as exc:
            logger.warning("No se pudo leer temp %s: %s", self._temp_path, exc)
            return self._build_fallback_label()

        try:
            self._pdf_buffer = QBuffer(self)
            self._pdf_buffer.setData(QByteArray(data))
            self._pdf_buffer.open(QBuffer.OpenModeFlag.ReadOnly)
            self._pdf_doc = QPdfDocument(self)
            self._pdf_doc.load(self._pdf_buffer)
            self._pdf_view = QPdfView(self)
            self._pdf_view.setDocument(self._pdf_doc)
            self._pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self._pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
            return self._pdf_view
        except Exception:  # noqa: BLE001
            logger.exception("Fallo al construir QPdfView para %s", self._temp_path)
            return self._build_fallback_label()

    def _build_fallback_label(self) -> QLabel:
        label = QLabel(
            self.tr(
                "Vista previa no disponible en esta versión.\n"
                "Guardá el PDF y abrilo con tu visor habitual."
            )
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: gray; font-size: 11pt;")
        label.setWordWrap(True)
        return label

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        default_dir = Path.home() / "Documents"
        if not default_dir.exists():
            default_dir = Path.home()
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar PDF"),
            str(default_dir / self._suggested_filename),
            self.tr("PDF (*.pdf)"),
        )
        if not path_str:
            # Usuario canceló el dialog de guardar — volver al preview,
            # NO cerrar el dialog ni borrar el temp.
            return

        dest = Path(path_str)
        try:
            shutil.copy2(self._temp_path, dest)
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error al guardar"),
                self.tr("No se pudo guardar el PDF:\n{e}").format(e=exc),
            )
            return

        self._saved_path = dest
        self._delete_temp()
        # Cerrar el visor antes de mostrar el QMessageBox: en Windows
        # QPdfDocument bloquea el archivo origen y queremos que queden
        # libres ambos archivos por si el usuario abre el destino.
        self._release_pdf_view()

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(self.tr("PDF guardado"))
        msg.setText(self.tr("PDF guardado en:\n{p}").format(p=str(dest)))
        msg.addButton(self.tr("OK"), QMessageBox.ButtonRole.AcceptRole)
        btn_open = msg.addButton(self.tr("Abrir"), QMessageBox.ButtonRole.ActionRole)
        msg.exec()

        if msg.clickedButton() is btn_open:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)))

        self.accept()

    def _on_cancel(self) -> None:
        self._release_pdf_view()
        self._delete_temp()
        self.reject()

    # closeEvent llama _release_pdf_view antes de _delete_temp también
    # (ver más abajo). Mantenemos las dos rutas (Cancelar / X) coherentes.

    def _release_pdf_view(self) -> None:
        """Cierra QPdfDocument y libera el archivo (Windows lock).

        En Windows, QPdfDocument mantiene un mmap sobre el archivo que
        sobrevive a `close()`. Para liberar el handle hay que destruir
        el QObject — usamos `deleteLater()` + processEvents para que
        Qt drene la cola de destrucción. Sin esto, `unlink(temp)` falla
        silenciosamente.
        """
        view = getattr(self, "_pdf_view", None)
        if view is not None:
            try:
                view.setDocument(None)
            except Exception:  # noqa: BLE001
                logger.debug("QPdfView.setDocument(None) falló (no crítico)")
        doc = getattr(self, "_pdf_doc", None)
        if doc is not None:
            try:
                doc.close()
                doc.deleteLater()
            except Exception:  # noqa: BLE001
                logger.debug("QPdfDocument cleanup falló (no crítico)")
            # Borramos el atributo del instance para que mypy no se queje
            # del re-asignamiento a None sobre un slot tipado.
            try:
                delattr(self, "_pdf_doc")
            except AttributeError:
                pass
        # Drenar la cola de deleteLater + IO pendiente.
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            app.processEvents()

    def _delete_temp(self) -> None:
        if self._cleanup_done:
            return
        try:
            self._temp_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.debug("No se pudo borrar temp %s: %s", self._temp_path, exc)
        self._cleanup_done = True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        """Si el usuario cierra con la X o Escape, también limpiar."""
        if self._saved_path is None:
            self._release_pdf_view()
            self._delete_temp()
        super().closeEvent(event)
```

### [src/collections_app/client/dialogs/profile_setup_dialog.py](src/collections_app/client/dialogs/profile_setup_dialog.py)

```python
"""Dialog modal de bienvenida para perfiles nuevos sin colecciones.

Se muestra una sola vez al arrancar el cliente con un perfil cuya DB
no tiene colecciones (típico tras `--profile <nuevo>`). Permite:

  1. Importar la estructura (colecciones, codes, cards) desde otro
     perfil existente — el inventario NO se importa, el usuario empieza
     con stock cero.
  2. Empezar vacío — la app sigue su flujo normal (que va a abrir el
     dialog de elegir colección, que estará vacío hasta que el admin
     cargue catálogo).

El botón X de la ventana está oculto para forzar una decisión explícita.
Tras cerrar (con cualquiera de las dos opciones), `main.py` setea el
flag `setup_completed=1` en app_settings así no vuelve a aparecer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.db.connection import create_connection
from collections_app.core.services.profile_service import (
    ProfileInfo,
    ProfileService,
)
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


class _ImportWorker(QThread):
    """Importa la estructura en un thread separado para no bloquear la UI.

    Abre su propia conexión al target_db (NO recibe `sqlite3.Connection`
    del hilo principal — convención del proyecto). El target ya tiene
    el schema aplicado (las migraciones corrieron al inicializar la
    conexión principal).
    """

    finished_ok = Signal(int)  # cantidad de colecciones importadas
    failed = Signal(str)

    def __init__(
        self,
        source_db_path: Path,
        target_db_path: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source_db_path
        self._target = target_db_path

    def run(self) -> None:
        try:
            conn = create_connection(self._target)
            try:
                count = ProfileService.import_structure(self._source, conn)
            finally:
                conn.close()
            self.finished_ok.emit(count)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error importando estructura desde %s", self._source)
            self.failed.emit(str(exc))


class ProfileSetupDialog(QDialog):
    """Dialog de primera corrida para perfiles sin colecciones.

    Pasamos `target_db_path` (no la conexión) porque el worker abre su
    propia conexión en el thread del importador. Filtramos los perfiles
    disponibles: excluye el perfil actual y los que no tienen colecciones
    (no tendría sentido importar de un perfil vacío).
    """

    def __init__(
        self,
        current_profile: str,
        available_profiles: list[ProfileInfo],
        target_db_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configurar perfil"))
        self.setMinimumWidth(440)
        self.setModal(True)
        # Sin botón X para forzar decisión explícita (Importar/Empezar vacío).
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self._target_db_path = target_db_path
        self._available = [
            p for p in available_profiles if p.name != current_profile and p.collection_count > 0
        ]
        self._radio_group: QButtonGroup | None = None
        self._worker: _ImportWorker | None = None
        self._build_ui(current_profile)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self, current_profile: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr('Bienvenido al perfil "{p}"').format(p=current_profile))
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            self.tr(
                "Este perfil no tiene colecciones configuradas.\n"
                "Podés importar la estructura desde otro perfil "
                "(sin inventario — empezás desde cero)."
            )
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if self._available:
            layout.addWidget(QLabel(self.tr("Importar desde:")))
            self._radio_group = QButtonGroup(self)
            for i, profile in enumerate(self._available):
                inv_text = (
                    self.tr("tiene datos") if profile.has_inventory else self.tr("sin inventario")
                )
                radio = QRadioButton(
                    f"{profile.display_name}  "
                    f"({profile.collection_count} {self.tr('colecciones')}, "
                    f"{inv_text})"
                )
                if i == 0:
                    radio.setChecked(True)
                self._radio_group.addButton(radio, i)
                layout.addWidget(radio)
        else:
            no_profiles = QLabel(
                self.tr(
                    "No hay otros perfiles con colecciones disponibles.\n"
                    "Podés configurar las colecciones desde la app Admin."
                )
            )
            no_profiles.setWordWrap(True)
            no_profiles.setStyleSheet("color: gray;")
            layout.addWidget(no_profiles)

        # Barra de progreso indeterminada (oculta hasta importar).
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        # Botones inferiores
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_import = QPushButton(self.tr("Importar estructura"))
        self._btn_import.setEnabled(bool(self._available))
        self._btn_import.clicked.connect(self._on_import)
        btn_row.addWidget(self._btn_import)

        self._btn_empty = QPushButton(self.tr("Empezar vacío"))
        self._btn_empty.clicked.connect(self.accept)
        btn_row.addWidget(self._btn_empty)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_import(self) -> None:
        if self._radio_group is None:
            return
        selected_id = self._radio_group.checkedId()
        if selected_id < 0 or selected_id >= len(self._available):
            return
        profile = self._available[selected_id]

        self._btn_import.setEnabled(False)
        self._btn_empty.setEnabled(False)
        self._progress.show()
        self._status_label.setText(self.tr("Importando…"))
        self._status_label.setStyleSheet("")

        self._worker = _ImportWorker(
            source_db_path=profile.db_path,
            target_db_path=self._target_db_path,
            parent=self,
        )
        self._worker.finished_ok.connect(self._on_import_done)
        self._worker.failed.connect(self._on_import_failed)
        self._worker.start()

    def _on_import_done(self, count: int) -> None:
        self._progress.hide()
        self._status_label.setText(
            self.tr("✓ {n} colecciones importadas correctamente.").format(n=count)
        )
        self._status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")
        # Pequeña pausa para que el usuario vea el mensaje de éxito.
        QTimer.singleShot(1200, self, self.accept)

    def _on_import_failed(self, error: str) -> None:
        self._progress.hide()
        self._btn_import.setEnabled(True)
        self._btn_empty.setEnabled(True)
        self._status_label.setText(self.tr("Error al importar: {e}").format(e=error))
        self._status_label.setStyleSheet(f"color: {StatusColor.ERROR};")
```

### [src/collections_app/client/main.py](src/collections_app/client/main.py)

```python
"""Entry point de la aplicación client (uso final)."""

import argparse
import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from collections_app.__version__ import __app_name__, __version__
from collections_app.client.dialogs.client_settings_dialog import ClientSettingsDialog
from collections_app.client.dialogs.profile_setup_dialog import ProfileSetupDialog
from collections_app.client.views.album_view import AlbumView
from collections_app.client.views.card_loader import CardLoaderView
from collections_app.client.views.compare_view import CompareView
from collections_app.client.views.inventory_view import InventoryView
from collections_app.client.views.reports_view import ReportsView
from collections_app.client.views.stats_view import StatsView
from collections_app.core.repositories import SettingsRepository
from collections_app.core.services.update_service import (
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import (
    get_active_profile,
    get_database_path,
    set_active_profile,
)
from collections_app.shared_ui import MainWindowBase, apply_app_style

logger = logging.getLogger(__name__)

# Settings keys usadas para persistir el estado del update checker.
SETTING_SKIPPED_VERSION = "skipped_version"
SETTING_SERVER_URL = "server_url"
SETTING_SERVER_API_KEY = "server_api_key"
# Marca que el wizard de bienvenida del perfil ya se mostró. Evita que
# vuelva a aparecer en cada arranque si el usuario eligió "Empezar vacío".
SETTING_SETUP_COMPLETED = "setup_completed"

# Delay antes de chequear updates al arrancar. Damos margen para que la
# UI quede 100% interactiva antes de tirar un request HTTP en background.
UPDATE_CHECK_DELAY_MS = 3_000


class _UpdateCheckWorker(QThread):
    """Chequea updates en un thread separado para no bloquear la UI.

    No accede a la DB ni a otros recursos compartidos: solo invoca la
    `UpdateSource` (red). El resultado se entrega via signal — el slot
    receptor corre en el thread de la UI, así que es seguro tocar widgets.
    """

    update_found = Signal(object)  # UpdateInfo
    no_update = Signal()

    def __init__(
        self,
        source: UpdateSource | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source

    def run(self) -> None:
        try:
            service = UpdateService(self._source) if self._source else UpdateService()
            info = service.check_for_updates()
            if info and info.is_newer:
                self.update_found.emit(info)
            else:
                self.no_update.emit()
        except Exception:
            logger.exception("UpdateCheckWorker: fallo inesperado")
            self.no_update.emit()


class ClientMainWindow(MainWindowBase):
    """Ventana principal del cliente.

    Al iniciar pide elegir una colección (o valida la licencia si la
    colección activa es premium). Solo expone "Cambiar colección" en el
    menú — el cliente no debe acceder a los ABMs de configuración.
    """

    def __init__(self, db_path: Path) -> None:
        super().__init__(db_path, app_name=__app_name__)
        title = f"{__app_name__} v{__version__}"
        if get_active_profile() != "default":
            title += f"  [{get_active_profile()}]"
        self.setWindowTitle(title)
        self.setMinimumSize(900, 700)
        self._card_loader: CardLoaderView | None = None
        self._update_worker: _UpdateCheckWorker | None = None
        # Diferimos la inicialización para que la ventana se muestre primero
        # y el SettingsDialog tenga un parent visible.
        QTimer.singleShot(0, self._initialize_active_collection)
        # Update check con delay: la UI debe estar viva antes de pegarle
        # a la red. Si el usuario cierra antes, el worker queda colgando
        # pero `parent=self` lo limpia al destruirse la ventana.
        QTimer.singleShot(UPDATE_CHECK_DELAY_MS, self._start_update_check)

    # ------------------------------------------------------------------
    # Menús
    # ------------------------------------------------------------------

    def _build_menus(self) -> None:
        super()._build_menus()
        config_menu = self.menuBar().addMenu(self.tr("&Configuración"))
        action = config_menu.addAction(self.tr("Cambiar colección..."))
        action.triggered.connect(self._open_settings)

    # ------------------------------------------------------------------
    # Inicialización del estado
    # ------------------------------------------------------------------

    def _initialize_active_collection(self) -> None:
        """Si no hay colección activa o no está unlocked, pedirla."""
        from collections_app.core.services import LicenseService, SettingsService

        # Wizard de primera corrida ANTES del flow de elegir colección:
        # si el perfil está vacío, ofrece importar estructura desde otro
        # perfil. Después seguimos con el resto.
        self._check_first_run()

        settings = SettingsService(self.conn)
        licenses = LicenseService(self.conn)
        active = settings.get_active_collection()

        needs_dialog = active is None
        if active is not None and active.collection_id is not None:
            needs_dialog = not licenses.is_unlocked(active.collection_id)

        if needs_dialog:
            self._open_settings()
        else:
            self._build_central_widget()

    def _check_first_run(self) -> None:
        """Si el perfil está vacío, abre el `ProfileSetupDialog`.

        Skipped si:
          - El flag `setup_completed` ya está seteado en `app_settings`.
          - O ya hay colecciones en la DB (caso típico del perfil default
            de un usuario existente — marcamos el flag y seguimos).
        """
        from collections_app.core.repositories import (
            CollectionsRepository,
            SettingsRepository,
        )
        from collections_app.core.services import ProfileService

        settings_repo = SettingsRepository(self.conn)
        if settings_repo.get(SETTING_SETUP_COMPLETED):
            return

        if CollectionsRepository(self.conn).list_all():
            # Perfil con datos preexistentes: marcar como completado para
            # no volver a chequear en arranques futuros.
            settings_repo.set(SETTING_SETUP_COMPLETED, "1")
            self.conn.commit()
            return

        dialog = ProfileSetupDialog(
            current_profile=get_active_profile(),
            available_profiles=ProfileService.get_all_profiles(),
            target_db_path=self.db_path,
            parent=self,
        )
        dialog.exec()
        # Independientemente de la elección (importar / empezar vacío),
        # marcar como completado: si el usuario eligió "vacío" y luego
        # se arrepiente, puede ir a Admin a cargar el catálogo manualmente.
        settings_repo.set(SETTING_SETUP_COMPLETED, "1")
        self.conn.commit()

    def _open_settings(self) -> None:
        dlg = ClientSettingsDialog(self.conn, parent=self)
        if dlg.exec():
            self._build_central_widget()
            self._update_status_bar()
        else:
            # Usuario canceló: si todavía no hay colección activa, mostramos
            # placeholder para que la ventana no quede vacía.
            if self.centralWidget() is None:
                self._build_placeholder()

    # ------------------------------------------------------------------
    # Construcción del central widget
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        from collections_app.core.services import SettingsService

        active = SettingsService(self.conn).get_active_collection()
        if active is None:
            self._build_placeholder()
            return

        tabs = QTabWidget()
        self._card_loader = CardLoaderView(self.conn, active)
        self._inventory_view = InventoryView(self.conn, active)
        self._album_view = AlbumView(self.conn, self.db_path, active)
        self._compare_view = CompareView(self.conn, self.db_path, active)
        self._stats_view = StatsView(self.conn, active)
        self._reports_view = ReportsView(self.conn, active)

        tabs.addTab(self._card_loader, self.tr("Cargar Cards"))
        tabs.addTab(self._inventory_view, self.tr("Inventario"))
        tabs.addTab(self._album_view, self.tr("Álbum"))
        tabs.addTab(self._compare_view, self.tr("Comparar"))
        tabs.addTab(self._stats_view, self.tr("Estadísticas"))
        tabs.addTab(self._reports_view, self.tr("Reportes"))
        self.setCentralWidget(tabs)

        # Auto-refresh de vistas afectadas tras una alta/baja en CardLoader.
        # Reports y Álbum quedan fuera: el usuario los dispara explícitamente.
        self._card_loader.card_changed.connect(self._inventory_view.refresh)
        self._card_loader.card_changed.connect(self._stats_view.refresh)

    def _build_placeholder(self) -> None:
        placeholder = QLabel(
            self.tr("Seleccione una colección desde Configuración → Cambiar colección…")
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)

    def _placeholder_widget(self) -> QWidget:
        label = QLabel(self.tr("Próximamente"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    # ------------------------------------------------------------------
    # Update checker
    # ------------------------------------------------------------------

    def _start_update_check(self) -> None:
        """Lanza el worker de chequeo. Si el usuario configuró servidor
        propio, usa `ServerUpdateSource`; si no, default a GitHub."""
        repo = SettingsRepository(self.conn)
        server_url = repo.get(SETTING_SERVER_URL)
        source: UpdateSource | None = None
        if server_url:
            api_key = repo.get(SETTING_SERVER_API_KEY) or ""
            source = ServerUpdateSource(server_url, api_key)

        skipped = repo.get(SETTING_SKIPPED_VERSION)

        self._update_worker = _UpdateCheckWorker(source=source, parent=self)
        self._update_worker.update_found.connect(lambda info: self._on_update_found(info, skipped))
        self._update_worker.start()

    def _on_update_found(self, info: object, skipped: str | None) -> None:
        # `info` viene como `object` por la firma del Signal — re-tipear acá.
        if not isinstance(info, UpdateInfo):
            return
        if skipped and skipped == info.latest_version:
            logger.debug("Versión %s ignorada por el usuario", info.latest_version)
            return
        self._show_update_banner(info)

    def _show_update_banner(self, info: UpdateInfo) -> None:
        """Banner azul no intrusivo arriba del central widget."""
        banner = QFrame(self)
        banner.setObjectName("updateBanner")
        banner.setStyleSheet(
            "#updateBanner { background-color: #2E86AB; border-radius: 4px; }"
            "#updateBanner QLabel { color: white; font-weight: bold; }"
            "#updateBanner QPushButton { color: white; border: 1px solid white;"
            "  border-radius: 3px; padding: 2px 8px; background: transparent; }"
            "#updateBanner QPushButton:hover { background-color: #1a6a8a; }"
        )

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(8, 4, 8, 4)

        label = QLabel(
            self.tr("Nueva versión disponible: v{latest} (instalada: v{current})").format(
                latest=info.latest_version, current=info.current_version
            )
        )
        layout.addWidget(label, stretch=1)

        btn_download = QPushButton(self.tr("Descargar"))
        btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_download.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(info.download_url)))
        layout.addWidget(btn_download)

        btn_notes = QPushButton(self.tr("Ver cambios"))
        btn_notes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_notes.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(info.release_url)))
        layout.addWidget(btn_notes)

        btn_skip = QPushButton(self.tr("Ignorar esta versión"))
        btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_skip.clicked.connect(lambda: self._skip_version(info.latest_version, banner))
        layout.addWidget(btn_skip)

        btn_close = QPushButton("X")
        btn_close.setFixedWidth(28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(banner.deleteLater)
        layout.addWidget(btn_close)

        # Insertar arriba del layout del widget central. Si no hay layout
        # (placeholder QLabel), no podemos insertar un banner — silencioso.
        central = self.centralWidget()
        if central is not None:
            central_layout = central.layout()
            if central_layout is not None:
                # `insertWidget` solo está en QBoxLayout; QTabWidget viene
                # con uno por default. Defensa: solo insertamos si está disponible.
                insert_widget = getattr(central_layout, "insertWidget", None)
                if insert_widget is not None:
                    insert_widget(0, banner)
                    return
        # Fallback: si no se pudo insertar arriba del central widget,
        # mostrar el banner como popup flotante junto a la ventana.
        banner.setParent(None)
        banner.setWindowFlags(Qt.WindowType.Tool)
        banner.show()

    def _skip_version(self, version: str, banner: QWidget) -> None:
        """Persiste la versión ignorada y cierra el banner."""
        SettingsRepository(self.conn).set(SETTING_SKIPPED_VERSION, version)
        self.conn.commit()
        banner.deleteLater()


def main() -> int:
    """Entry point. Inicializa logging, abre la ventana principal."""
    # Parsear --profile ANTES de cualquier import/inicialización que use
    # paths.get_app_data_dir() — sino la DB queda apuntando al perfil
    # default y el switch posterior es inconsistente.
    parser = argparse.ArgumentParser(add_help=False, description=__app_name__)
    parser.add_argument(
        "--profile",
        default="default",
        help="Perfil de datos (alfanumérico). Default: 'default'.",
    )
    args, remaining = parser.parse_known_args()
    set_active_profile(args.profile)

    setup_logging(level=logging.DEBUG)
    db_path = get_database_path()
    logger.info(
        "Client app v%s — bootstrap OK (profile=%s, db=%s)",
        __version__,
        get_active_profile(),
        db_path,
    )

    # `remaining` propaga args desconocidos a Qt (--style, --platform, etc.).
    app = QApplication([sys.argv[0], *remaining])
    apply_app_style(app)
    window = ClientMainWindow(db_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

### [src/collections_app/client/views/__init__.py](src/collections_app/client/views/__init__.py)

```python
"""Vistas específicas de la app client."""
```

### [src/collections_app/client/views/album_view.py](src/collections_app/client/views/album_view.py)

```python
"""Tab Álbum: genera PDFs (álbum + listas faltantes/repetidas/owned) con preview."""

import logging
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.client.dialogs.pdf_preview_dialog import PdfPreviewDialog
from collections_app.core.db.connection import create_connection
from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.core.services import (
    AlbumService,
    InventoryService,
    ListReportMode,
    PdfGeneratorResult,
)
from collections_app.core.utils.paths import get_crest_path
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class _PdfWorker(QThread):
    """Genera un PDF en un archivo TEMPORAL (luego el preview decide destino).

    Abre su propia conexión a la DB (NO se pueden compartir
    `sqlite3.Connection` entre threads). El kind dispatcha al método
    correspondiente del AlbumService — incluye dos variantes para
    "repetidas" (FULL / SUMMARY).
    """

    finished_ok = Signal(object)  # PdfGeneratorResult
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        output_path: Path,
        kind: str,  # "album"|"missing_full"|"missing_summary"|"duplicates_full"
        # |"duplicates_summary"|"owned"
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._output_path = output_path
        self._kind = kind

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                col = CollectionsRepository(conn).get_by_id(self._collection_id)
                if col is None:
                    raise ValueError(f"Colección {self._collection_id} no encontrada")
                service = AlbumService(conn)
                match self._kind:
                    case "album":
                        result = service.generate_album_pdf(col, self._output_path)
                    case "missing_full":
                        result = service.generate_missing_pdf(
                            col, self._output_path, mode=ListReportMode.FULL
                        )
                    case "missing_summary":
                        result = service.generate_missing_pdf(
                            col, self._output_path, mode=ListReportMode.SUMMARY
                        )
                    case "duplicates_full":
                        result = service.generate_duplicates_pdf(
                            col, self._output_path, mode=ListReportMode.FULL
                        )
                    case "duplicates_summary":
                        result = service.generate_duplicates_pdf(
                            col, self._output_path, mode=ListReportMode.SUMMARY
                        )
                    case "owned":
                        result = service.generate_owned_pdf(col, self._output_path)
                    case _:
                        raise ValueError(f"Tipo de PDF desconocido: {self._kind}")
            finally:
                conn.close()
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando PDF (%s)", self._kind)
            if self._output_path.exists():
                self._output_path.unlink(missing_ok=True)
            self.failed.emit(str(exc))


class AlbumView(QWidget):
    """Tab del cliente: genera PDFs del álbum y listas asociadas."""

    # (kind interno, label visible, descripción, prefijo del filename)
    _PDF_KINDS: tuple[tuple[str, str, str, str], ...] = (
        ("album", "📄 Álbum visual completo", "Todas las cards — con foto o placeholder.", "Album"),
        (
            "missing_full",
            "📋 Faltantes — Completo",
            "Categoría + flujo continuo número/nombre. Ideal para imprimir.",
            "Faltantes_Completo",
        ),
        (
            "missing_summary",
            "📋 Faltantes — Resumido",
            "Una línea por categoría, solo números. Compacto.",
            "Faltantes_Resumido",
        ),
        (
            "duplicates_full",
            "📋 Repetidas — Completo",
            "Categoría + flujo número/nombre con ×N. Ideal para compartir.",
            "Repetidas_Completo",
        ),
        (
            "duplicates_summary",
            "📋 Repetidas — Resumido",
            "Una línea por categoría con `número×N`. Compacto.",
            "Repetidas_Resumido",
        ),
        ("owned", "📋 PDF de lo que tengo", "Lista completa de tu colección actual.", "Tengo"),
    )

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: Path,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._db_path = db_path
        self.collection = collection
        self._worker: _PdfWorker | None = None
        self._buttons: list[QPushButton] = []
        self._build_ui()
        self._refresh_image_count()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self._refresh_image_count()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Exportar Álbum a PDF"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)

        layout.addWidget(self._build_export_section())
        layout.addWidget(self._build_info_section())
        layout.addStretch()

    def _build_export_section(self) -> QFrame:
        frame = self._section_frame()
        outer = QVBoxLayout(frame)
        outer.setSpacing(Spacing.MD)

        outer.addWidget(self._section_title(self.tr("📄 PDFs")))
        outer.addWidget(
            QLabel(
                self.tr(
                    "El layout del álbum visual (columnas/filas/orientación) "
                    "se configura en Admin → Colecciones."
                )
            )
        )

        for kind, label, subtitle, _prefix in self._PDF_KINDS:
            outer.addLayout(self._make_button_row(self.tr(label), self.tr(subtitle), kind))

        # Estado
        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        outer.addWidget(self._status_label)
        return frame

    def _make_button_row(self, label: str, subtitle: str, kind: str) -> QVBoxLayout:
        row = QVBoxLayout()
        row.setSpacing(Spacing.XS)
        button = QPushButton(label)
        button.clicked.connect(lambda: self._generate(kind))
        row.addWidget(button)
        row.addWidget(QLabel(subtitle))
        self._buttons.append(button)
        return row

    def _build_info_section(self) -> QFrame:
        frame = self._section_frame()
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.XS)
        layout.addWidget(self._section_title(self.tr("ℹ️ Info de imágenes")))
        self._image_count_label = QLabel("")
        layout.addWidget(self._image_count_label)
        self._last_run_label = QLabel(self.tr("Última generación: —"))
        layout.addWidget(self._last_run_label)
        return frame

    def _section_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(1)
        return frame

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        return label

    # ------------------------------------------------------------------
    # Info: cuántas imágenes hay generadas
    # ------------------------------------------------------------------

    def _refresh_image_count(self) -> None:
        """Muestra cuántos códigos de la colección ya tienen escudo (info)."""
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        total_cards = InventoryService(self.conn).get_stats(cid)["total_cards"]
        if total_cards == 0:
            self._image_count_label.setText(
                self.tr("La colección no tiene cards en el catálogo todavía.")
            )
            return
        lines = CodesLinesRepository(self.conn).list_by_header(self.collection.code_header_id)
        total_codes = len(lines)
        if total_codes == 0:
            self._image_count_label.setText(
                self.tr("La colección no tiene códigos definidos todavía.")
            )
            return
        with_crest = sum(1 for line in lines if get_crest_path(line.code_id).exists())
        pct = (with_crest / total_codes * 100) if total_codes > 0 else 0
        self._image_count_label.setText(
            self.tr("Escudos cargados: {n} / {t} ({pct:.1f}%)").format(
                n=with_crest, t=total_codes, pct=pct
            )
        )

    # ------------------------------------------------------------------
    # Generación con preview
    # ------------------------------------------------------------------

    def _kind_meta(self, kind: str) -> tuple[str, str]:
        """Retorna (label, prefix) para el kind dado."""
        for k, label, _sub, prefix in self._PDF_KINDS:
            if k == kind:
                return label, prefix
        return kind, kind

    def _suggested_filename(self, kind: str) -> str:
        _, prefix = self._kind_meta(kind)
        date = datetime.now().strftime("%Y-%m-%d")
        slug = (
            "".join(
                ch if ch.isalnum() or ch in " _-" else "_" for ch in self.collection.collection_name
            )
            .strip()
            .replace(" ", "_")
        )
        return f"{prefix}_{slug}_{date}.pdf"

    def _generate(self, kind: str) -> None:
        """Genera el PDF en `%TEMP%` y muestra el preview.

        El preview es donde el usuario decide guardar (con QFileDialog)
        o cancelar. No tocamos disco fuera del temp hasta que confirme.
        """
        # mkstemp para tener un path único sin abrir el handle
        fd, tmp_str = tempfile.mkstemp(suffix=".pdf", prefix="collections_")
        import os

        os.close(fd)
        tmp_path = Path(tmp_str)

        self._set_buttons_enabled(False)
        self._status_label.setText(self.tr("Generando…"))

        assert self.collection.collection_id is not None
        worker = _PdfWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            output_path=tmp_path,
            kind=kind,
            parent=self,
        )
        self._worker = worker

        label, _ = self._kind_meta(kind)
        suggested = self._suggested_filename(kind)

        def on_ok(result: object) -> None:
            assert isinstance(result, PdfGeneratorResult)
            self._set_buttons_enabled(True)
            self._status_label.setText("")
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._last_run_label.setText(self.tr("Última generación: {ts}").format(ts=ts))
            # Mostrar preview — el dialog se hace cargo de borrar el temp.
            dialog = PdfPreviewDialog(
                temp_pdf_path=tmp_path, suggested_filename=suggested, parent=self
            )
            dialog.exec()
            saved = dialog.saved_path()
            if saved is not None:
                self._status_label.setText(self.tr("✓ PDF guardado en: {p}").format(p=str(saved)))

        def on_failed(msg: str) -> None:
            self._set_buttons_enabled(True)
            self._status_label.setText("")
            tmp_path.unlink(missing_ok=True)
            QMessageBox.critical(self, label, msg)

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for b in self._buttons:
            b.setEnabled(enabled)
```

### [src/collections_app/client/views/card_loader.py](src/collections_app/client/views/card_loader.py)

```python
"""Pantalla de carga rápida de cards: alta/baja con navegación por Enter.

Comportamiento según `Collection.requires_code`:

- `requires_code=True`: el campo Código siempre está visible y es
  obligatorio. Foco inicial en Código. Búsqueda exacta `(code, number)`.
- `requires_code=False`: solo se muestran Número y Cantidad. Foco inicial
  en Número. La búsqueda se hace con `CardsRepository.find_by_number`:
    * 0 matches → status "Número X no existe en esta colección".
    * 1 match → autocompleta país/nombre, status Nueva/Repetida.
    * >1 matches → muestra el combo de Código limitado a esos códigos
      ambiguos; status pide al usuario que especifique. Cuando el usuario
      elige uno, se valida exacto.
"""

import logging
import sqlite3
from collections.abc import Callable

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QStringListModel,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QIntValidator, QKeyEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCompleter,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Card, Collection, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import AmbiguousCardError, InventoryService
from collections_app.shared_ui.theme import (
    INPUT_BG_ALTA,
    INPUT_BG_BAJA,
    READONLY_BG,
    Spacing,
    StatusColor,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

logger = logging.getLogger(__name__)


class _EmptyFieldFilter(QObject):
    """Bloquea Tab/Backtab/Enter cuando el QLineEdit watched está vacío.

    Pensado para el campo de Código (cuando requires_code=True) y el de
    Número: el usuario no debería poder saltar al siguiente campo ni
    disparar el save sin haber tipeado nada. El filter:

    - Si la tecla es Tab, Backtab, Return o Enter Y el texto stripeado
      está vacío: llama `on_empty(field_name)` y CONSUME el evento
      (return True) — el foco no avanza, el handler suele mostrar
      un flash de borde rojo en el campo.
    - Si el texto NO está vacío: deja pasar el evento (return False)
      para que el resto de la cadena (EnterNavigator, returnPressed)
      lo maneje normalmente.
    """

    def __init__(
        self,
        field_name: str,
        get_text: Callable[[], str],
        on_empty: Callable[[str], None],
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._field_name = field_name
        self._get_text = get_text
        self._on_empty = on_empty

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)
        if not isinstance(event, QKeyEvent):
            return super().eventFilter(watched, event)
        if event.key() not in (
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backtab,
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            return super().eventFilter(watched, event)
        if self._get_text().strip():
            # Hay texto → dejar pasar al navigator / returnPressed.
            return super().eventFilter(watched, event)
        # Campo vacío: feedback visual + consumir el evento (no avanzar).
        self._on_empty(self._field_name)
        return True


class _CodeOnlyCompleter(QCompleter):
    """QCompleter que muestra `"CODE - Name"` pero inserta solo `"CODE"`.

    Override de `pathFromIndex`: Qt llama este método para obtener el texto
    a insertar en el QLineEdit cuando el usuario activa una opción del
    popup (Enter, click). Por default retorna el item completo del modelo
    (`"FWC - OFFICIAL_TROPHY"`); este override devuelve solo la parte
    previa al `" - "`.

    Sin este override, activar un ítem del popup deja
    `"FWC - OFFICIAL_TROPHY"` en el campo. El handler `_on_code_selected`
    intenta limpiarlo después con `setText("FWC")`, pero el orden de los
    signals + el manejo de focus del completer hace que ese clean-up se
    pierda. Resolverlo en `pathFromIndex` evita el race entero.
    """

    def pathFromIndex(  # noqa: N802 — Qt naming
        self, index: QModelIndex | QPersistentModelIndex
    ) -> str:
        full: str = super().pathFromIndex(index)
        return full.split(" - ", 1)[0].strip()


class CardLoaderView(QWidget):
    """Pantalla principal del cliente: alta/baja rápida de cards."""

    # Emitida después de cada save exitoso. Las otras vistas (Inventario,
    # Estadísticas) la conectan para auto-refrescarse.
    card_changed = Signal()

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._navigator = EnterNavigator(self)
        # Estado: cuando hay >1 match en find_by_number, se ofrece al
        # usuario elegir el código entre los ambiguos. Con `requires_code=True`,
        # esto es siempre False; el completer se llena con todos los codes_lines.
        self._has_ambiguity = False
        # Cache del último match unívoco (cuando requires_code=False y find_by_number
        # devolvió exactamente 1) para que `_save_card` use add_card_by_number sin
        # tener que volver a buscar.
        self._unambiguous_card: Card | None = None
        # Set de code_ids válidos en el contexto actual (uppercase). Se
        # repuebla en cada llamada a `_populate_completer_*`. Sirve para
        # validación rápida sin recorrer el modelo del completer.
        self._valid_code_ids: set[str] = set()
        # Code seleccionado y validado por el usuario. None mientras el
        # texto del LineEdit no sea un código conocido. Reemplaza el
        # `_get_selected_code` viejo basado en QComboBox.currentData.
        self._selected_code_id: str | None = None
        # Flag post-carga: cuando el usuario confirma una card, el foco
        # vuelve al SET con texto seleccionado y este flag queda True.
        # Si presiona Enter sin modificar el texto, el _on_code_return_pressed
        # salta directo al número manteniendo el código actual.
        # Cualquier edición del usuario (textEdited) lo desactiva.
        self._set_confirmed: bool = False

        self._build_ui()
        self._wire_navigator()
        focus_target = self._first_active_input()
        focus_target.setFocus()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        """Cambia la colección activa, reconfigurando la UI según `requires_code`."""
        self.collection = collection
        self._has_ambiguity = False
        self._unambiguous_card = None
        if collection.requires_code:
            self._populate_completer_with_all_codes()
            self._set_code_visible(True)
        else:
            self._clear_completer()
            self._set_code_visible(False)
        self._reset_form()

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)

        container = QWidget()
        container.setMaximumWidth(500)
        outer.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)

        grid = QGridLayout(container)
        grid.setHorizontalSpacing(Spacing.MD)
        grid.setVerticalSpacing(Spacing.SM)

        row = 0
        grid.addWidget(QLabel(self.tr("Operación") + ":"), row, 0)
        grid.addWidget(self._build_operation_row(), row, 1)
        row += 1

        # Campo de código: QLineEdit con QCompleter (autocompletado por
        # contains, case-insensitive). Las opciones del completer son
        # strings tipo "ARG - Argentina" para que el usuario pueda buscar
        # tanto por code_id como por nombre. Visibilidad según contexto:
        # con requires_code=True siempre visible; con requires_code=False
        # inicia oculto y solo aparece si find_by_number devuelve >1
        # (ambigüedad).
        self._code_label = QLabel((self.collection.code_field_name or self.tr("Código")) + ":")
        self._code_edit = QLineEdit()
        self._code_edit.setPlaceholderText(self.tr("Código (ej: ARG)"))
        self._code_edit.setMaxLength(10)
        # Subclass propio: Qt inserta solo el code_id ("FWC"), no el item
        # completo ("FWC - OFFICIAL_TROPHY"). Ver _CodeOnlyCompleter.
        self._completer = _CodeOnlyCompleter([], self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        # `QCompleter.activated` tiene dos sobrecargas (str y QModelIndex);
        # el wrapper filtra por tipo para que mypy strict acepte la conexión
        # sin la sintaxis `signal[str]` (no soportada en stubs de PySide6).
        self._completer.activated.connect(self._on_completer_activated)
        self._code_edit.setCompleter(self._completer)
        # textChanged: cualquier cambio (incluyendo setText programático).
        # Sirve para mantener `_selected_code_id` sincronizado.
        self._code_edit.textChanged.connect(self._on_code_text_changed)
        # textEdited: SOLO input del usuario (no setText). Sirve para
        # invalidar `_set_confirmed` (que se setea en post-carga vía
        # selectAll, sin que cuente como edición) y para refrescar el
        # highlight del primer ítem del popup tras cada tecla.
        self._code_edit.textEdited.connect(self._on_code_text_edited)
        self._code_edit.returnPressed.connect(self._on_code_return_pressed)
        # eventFilter para que Down/Up abran el popup del completer cuando
        # está cerrado — por default QLineEdit ignora esas teclas y el
        # popup solo navega cuando ya está visible.
        self._code_edit.installEventFilter(self)
        grid.addWidget(self._code_label, row, 0)
        grid.addWidget(self._code_edit, row, 1)
        row += 1

        if self.collection.requires_code:
            self._populate_completer_with_all_codes()
            self._set_code_visible(True)
        else:
            self._set_code_visible(False)

        grid.addWidget(QLabel(self.tr("Número") + ":"), row, 0)
        grid.addLayout(self._build_number_qty_row(), row, 1)
        row += 1

        country_label_text = self.collection.code_field_name or self.tr("País / Set")
        grid.addWidget(QLabel(country_label_text + ":"), row, 0)
        self._country_input = QLineEdit()
        self._country_input.setReadOnly(True)
        self._country_input.setStyleSheet(f"background-color: {READONLY_BG};")
        grid.addWidget(self._country_input, row, 1)
        row += 1

        grid.addWidget(QLabel(self.tr("Nombre") + ":"), row, 0)
        self._name_input = QLineEdit()
        self._name_input.setReadOnly(True)
        self._name_input.setStyleSheet(f"background-color: {READONLY_BG};")
        grid.addWidget(self._name_input, row, 1)
        row += 1

        self._status_label = QLabel("")
        self._status_label.setVisible(False)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self._status_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()

        # Tinte inicial del frame de operación según el modo activo (Alta).
        self._apply_input_mode_styling()

    def _build_operation_row(self) -> QFrame:
        """Frame contenedor de los radios Alta/Baja, coloreable por modo.

        Pintamos el QFrame (no los QLineEdit) — setStyleSheet sobre
        QLineEdits dispara polish-cycles que rompen los tests de foco
        en pytest-qt. El frame no es focusable, su repolish no afecta
        a nadie y el color sigue siendo bien visible (rodea Alta/Baja).
        """
        self._operation_frame = QFrame()
        self._operation_frame.setObjectName("operationFrame")
        layout = QHBoxLayout(self._operation_frame)
        layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.SM, Spacing.XS)
        self._alta_radio = QRadioButton(self.tr("&Alta"))
        self._baja_radio = QRadioButton(self.tr("&Baja"))
        self._alta_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self._alta_radio)
        group.addButton(self._baja_radio)
        # Conectamos ambos radios. `toggled` se dispara dos veces al
        # cambiar (False para el que se desmarca, True para el que se
        # marca). El handler usa un guard para actuar SOLO en True.
        self._alta_radio.toggled.connect(self._on_operation_changed)
        self._baja_radio.toggled.connect(self._on_operation_changed)
        layout.addWidget(self._alta_radio)
        layout.addWidget(self._baja_radio)
        layout.addStretch()
        return self._operation_frame

    def _build_number_qty_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._number_input = QLineEdit()
        self._number_input.setValidator(QIntValidator(0, 99_999, self))
        self._number_input.setFixedWidth(100)
        self._number_input.textChanged.connect(lambda _: self._validate_card())
        row.addWidget(self._number_input)

        row.addWidget(QLabel(self.tr("Cantidad") + ":"))
        self._qty_input = QLineEdit("1")
        self._qty_input.setValidator(QIntValidator(1, 999, self))
        self._qty_input.setFixedWidth(70)
        self._qty_input.installEventFilter(self)
        row.addWidget(self._qty_input)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Code field: poblar completer / mostrar / leer / validar
    # ------------------------------------------------------------------

    def _populate_completer_with_all_codes(self) -> None:
        """Llena el completer con TODOS los codes_lines del header."""
        repo = CodesLinesRepository(self.conn)
        lines = repo.list_by_header(self.collection.code_header_id)
        self._set_completer_items([(line.code_id, line.code_name) for line in lines])

    def _populate_completer_with_ambiguous(self, matches: list[Card]) -> None:
        """Llena el completer con SOLO los códigos que matchearon en find_by_number."""
        items = [(card.code_id, self._lookup_code_name(card.code_id)) for card in matches]
        self._set_completer_items(items)

    def _set_completer_items(self, items: list[tuple[str, str]]) -> None:
        """Setea las opciones del completer + el set de validación."""
        self._valid_code_ids = {code_id.upper() for code_id, _ in items}
        completion_strings = [f"{code_id} - {name}" for code_id, name in items]
        model = QStringListModel(completion_strings, self)
        self._completer.setModel(model)
        self._code_edit.blockSignals(True)
        self._code_edit.clear()
        self._code_edit.blockSignals(False)
        self._selected_code_id = None

    def _clear_completer(self) -> None:
        """Vacía el completer y la selección (al cambiar a requires_code=False)."""
        self._valid_code_ids = set()
        self._completer.setModel(QStringListModel([], self))
        self._code_edit.blockSignals(True)
        self._code_edit.clear()
        self._code_edit.blockSignals(False)
        self._selected_code_id = None

    def _set_code_visible(self, visible: bool) -> None:
        self._code_label.setVisible(visible)
        self._code_edit.setVisible(visible)

    def _get_selected_code(self) -> str:
        """Lee el código seleccionado y validado (uppercase, "" si no hay)."""
        return self._selected_code_id or ""

    # ------------------------------------------------------------------
    # Code field: handlers de texto y selección
    # ------------------------------------------------------------------

    def _on_code_text_changed(self, _text: str) -> None:
        """Invalida la selección si el texto deja de matchear un código válido."""
        upper = self._code_edit.text().strip().upper()
        if upper not in self._valid_code_ids:
            self._selected_code_id = None
        else:
            # Match exacto: marcamos como seleccionado pero NO movemos el foco
            # (el usuario puede seguir escribiendo o presionar Enter después).
            self._selected_code_id = upper
        # Si estamos en modo `requires_code` o ambigüedad, recalcular el preview.
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _on_code_text_edited(self, _text: str) -> None:
        """Solo input del usuario: invalida `_set_confirmed` y refresca highlight.

        `textEdited` (a diferencia de `textChanged`) NO se dispara con
        `setText()` programático, así que el `selectAll()` de
        `_after_successful_load` no rompe el flag.
        """
        self._set_confirmed = False
        # El completer recién filtra el modelo después de que terminemos
        # con este slot — el QTimer.singleShot(0) garantiza que el
        # highlight se aplique sobre la lista ya filtrada.
        QTimer.singleShot(0, self._highlight_first_completion)

    def _highlight_first_completion(self) -> None:
        """Resalta el primer ítem del popup del completer si hay matches.

        Bloquear signals del completer durante `popup.setCurrentIndex` es
        crítico: sin eso, Qt interpreta el cambio de currentIndex como una
        "selección" y auto-inserta el `pathFromIndex` del ítem en el
        QLineEdit. Resultado visible: el usuario tipea "f", el popup
        resalta "FWC", y el campo termina con "FWC" (no "f"). Bloqueando
        el completer evitamos que ese slot interno corra.
        """
        if self._completer.completionCount() <= 0:
            return
        self._completer.setCurrentRow(0)
        popup = self._completer.popup()
        if popup is None:
            return
        self._completer.blockSignals(True)
        try:
            popup.setCurrentIndex(self._completer.currentIndex())
        finally:
            self._completer.blockSignals(False)

    def _on_completer_activated(self, value: object) -> None:
        """Slot del completer.activated que descarta el overload QModelIndex."""
        if isinstance(value, str):
            self._on_code_selected(value)

    def _on_code_selected(self, text: str) -> None:
        """El usuario eligió una opción del popup ("ARG - Argentina")."""
        code_id = text.split(" - ", 1)[0].strip().upper()
        if code_id not in self._valid_code_ids:
            return
        self._selected_code_id = code_id
        # Mostrar solo el code_id (sin el nombre) en el campo.
        self._code_edit.blockSignals(True)
        self._code_edit.setText(code_id)
        self._code_edit.blockSignals(False)
        # Mover foco al número y seleccionar lo que haya para overwrite rápido.
        self._number_input.setFocus()
        self._number_input.selectAll()
        # Refrescar preview ahora que el código quedó fijo.
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _on_code_return_pressed(self) -> None:
        """Enter en el campo de código: resolver según matches.

        - Si `_set_confirmed` y el texto coincide con `_selected_code_id`
          (post-carga sin edición): salta directo a número manteniendo
          el código actual.
        - 1 match exacto / único parcial → seleccionar y pasar foco a número.
        - >1 matches parciales → abrir popup del completer.
        - 0 matches → flash visual de borde rojo (1s).
        """
        text = self._code_edit.text().strip().upper()
        if not text:
            return
        # Atajo post-carga: el SET viene "confirmado" del último save y
        # el texto no se modificó → ir directo al número.
        if self._set_confirmed and text == (self._selected_code_id or ""):
            self._set_confirmed = False
            self._number_input.setFocus()
            self._number_input.selectAll()
            return
        # A partir de acá es un Enter normal de validación.
        self._set_confirmed = False
        if text in self._valid_code_ids:
            self._on_code_selected(text)
            return
        matches = sorted(c for c in self._valid_code_ids if text in c)
        if len(matches) == 1:
            self._on_code_selected(matches[0])
        elif len(matches) > 1:
            self._completer.setCompletionPrefix(text)
            self._completer.complete()
        else:
            self._flash_invalid_code()

    def _flash_invalid_code(self) -> None:
        """Borde rojo temporal en el campo de código (1s)."""
        self._show_field_error("code")

    def _show_field_error(self, field: str) -> None:
        """Aplica borde rojo al campo indicado y revierte tras 1s.

        Al revertir, reaplica el tinte del modo Alta/Baja para no perder
        el color de fondo. Usamos la sobrecarga `singleShot(msec, context,
        slot)` con `self` como context: si el widget se destruye antes
        de que el timer dispare (típico en tests cortos), Qt cancela el
        callback y no intenta tocar el C++ object liberado.
        """
        self._apply_field_styles(error_field=field)
        QTimer.singleShot(1000, self, lambda: self._apply_field_styles(error_field=None))

    # ------------------------------------------------------------------
    # Tinte Alta/Baja: frame de operación + campos editables
    # ------------------------------------------------------------------

    def _mode_bg_color(self) -> str:
        """Color pastel correspondiente al modo activo (alta/baja)."""
        return INPUT_BG_ALTA if self._alta_radio.isChecked() else INPUT_BG_BAJA

    def _on_operation_changed(self, checked: bool) -> None:
        """Slot del toggled de los radios Alta/Baja.

        Hace dos cosas: actualiza colores y mueve el foco al primer
        campo de entrada. El guard `if not checked` evita ejecutar dos
        veces (toggled emite False para el radio que se desmarca y True
        para el que se marca — solo nos interesa la transición a True).
        """
        if not checked:
            return
        self._apply_input_mode_styling()
        # Foco al primer campo activo + selectAll para que la próxima
        # tecla reemplace lo que haya (UX de carga rápida).
        target = self._first_active_input()
        target.setFocus()
        if isinstance(target, QLineEdit):
            target.selectAll()

    def _apply_input_mode_styling(self) -> None:
        """Pinta el frame de operación + los campos editables.

        El frame es recordatorio constante (rodea Alta/Baja). Los campos
        coloreados dan feedback visual donde el usuario está tipeando.
        Llamado al construir y al togglear el radio.
        """
        bg = self._mode_bg_color()
        self._operation_frame.setStyleSheet(
            f"#operationFrame {{ background-color: {bg}; border-radius: 4px; }}"
        )
        self._apply_field_styles(error_field=None)

    def _apply_field_styles(self, error_field: str | None = None) -> None:
        """Aplica el tinte del modo a los QLineEdits editables.

        `error_field` ∈ {"code", "number", "qty", None}: si está seteado,
        ese campo recibe borde rojo (el resto mantiene el tinte normal).
        Al expirar el flash de error se llama de nuevo con None para
        restaurar el color de fondo del modo activo.
        """
        bg = self._mode_bg_color()
        normal_style = f"QLineEdit {{ background-color: {bg}; }}"
        error_style = f"QLineEdit {{ background-color: {bg}; border: 1px solid red; }}"
        fields: dict[str, QLineEdit | None] = {
            "code": self._code_edit,
            "number": self._number_input,
            "qty": self._qty_input,
        }
        for name, widget in fields.items():
            if widget is None:
                continue
            widget.setStyleSheet(error_style if name == error_field else normal_style)

    # ------------------------------------------------------------------
    # Navegación y eventos
    # ------------------------------------------------------------------

    def _wire_navigator(self) -> None:
        self._navigator.uninstall()
        chain: list[QWidget] = []
        if self.collection.requires_code:
            chain = [self._code_edit, self._number_input, self._qty_input]
        elif self._has_ambiguity:
            # El número ya fue tipeado; saltarlo y ir directo a qty tras código.
            chain = [self._code_edit, self._qty_input]
        else:
            chain = [self._number_input, self._qty_input]
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_card
        self._navigator.install()
        # Empty-field guards: instalar DESPUÉS del navigator para que en la
        # cadena LIFO de eventFilters se ejecuten ANTES (consume Tab/Enter
        # cuando el campo está vacío y bloquea el avance al siguiente).
        self._install_empty_field_filters()

    def _install_empty_field_filters(self) -> None:
        """Bloquea Tab/Backtab/Enter en code_edit y number_input cuando vacíos."""
        # Removemos cualquier filtro previo para evitar duplicados al
        # reinstalarse el navigator. Mantenemos refs vivas en self para
        # evitar que el GC los libere mientras Qt los tiene apuntados.
        for attr in ("_code_empty_filter", "_number_empty_filter"):
            old = getattr(self, attr, None)
            if old is not None:
                # `removeEventFilter` es seguro aunque no esté instalado.
                target = self._code_edit if attr == "_code_empty_filter" else self._number_input
                target.removeEventFilter(old)
        self._code_empty_filter = _EmptyFieldFilter(
            "code", self._code_edit.text, self._show_field_error, self
        )
        self._number_empty_filter = _EmptyFieldFilter(
            "number", self._number_input.text, self._show_field_error, self
        )
        self._code_edit.installEventFilter(self._code_empty_filter)
        self._number_input.installEventFilter(self._number_empty_filter)

    def _first_active_input(self) -> QWidget:
        if self.collection.requires_code:
            return self._code_edit
        return self._number_input

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        # `_qty_input` se construye después de `_code_edit` y este filter
        # puede dispararse durante setup. Guard con getattr.
        qty_input = getattr(self, "_qty_input", None)
        if qty_input is not None and watched is qty_input and event.type() == QEvent.Type.FocusIn:
            qty_input.selectAll()
        # Up/Down sobre el code_edit: abrir popup del completer si no está
        # visible. Una vez abierto, el popup procesa las flechas nativamente.
        if (
            watched is self._code_edit
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up)
        ):
            popup = self._completer.popup()
            if popup is None or not popup.isVisible():
                # Prefijo vacío → muestra TODAS las opciones; con texto, filtra.
                self._completer.setCompletionPrefix(self._code_edit.text())
                self._completer.complete()
                return True
        return super().eventFilter(watched, event)

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def _on_code_changed(self) -> None:
        """Cuando el usuario cambia el combo (modo requires_code o ambigüedad)."""
        if self.collection.requires_code or self._has_ambiguity:
            self._validate_card()

    def _validate_card(self) -> None:
        """Llamado al editar número o código."""
        number_text = self._number_input.text().strip()
        if not number_text:
            self._clear_info()
            return

        try:
            number = int(number_text)
        except ValueError:
            self._set_status(self.tr("Inválido"), StatusColor.WARNING)
            return

        if self.collection.requires_code:
            self._validate_with_code(number)
            return

        self._validate_by_number(number)

    def _validate_with_code(self, number: int) -> None:
        """Modo requires_code=True: búsqueda exacta `(code, number)`."""
        code = self._get_selected_code()
        if not code:
            return  # esperando que el usuario elija un código
        cards_repo = CardsRepository(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        card = cards_repo.get(cid, code, number)
        if card is None:
            self._country_input.setText("")
            self._name_input.setText("")
            self._set_status(
                self.tr("{code}-{n} no existe").format(code=code, n=number),
                StatusColor.WARNING,
            )
            return
        self._show_card_info(card)

    def _validate_by_number(self, number: int) -> None:
        """Modo requires_code=False: búsqueda por número con manejo de ambigüedad."""
        cards_repo = CardsRepository(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id

        if self._has_ambiguity:
            # El usuario ya está eligiendo un código del combo limitado:
            # validar exacto contra el código elegido.
            code = self._get_selected_code()
            if not code:
                return
            card = cards_repo.get(cid, code, number)
            if card is None:
                self._country_input.setText("")
                self._name_input.setText("")
                self._set_status(
                    self.tr("{code}-{n} no existe").format(code=code, n=number),
                    StatusColor.WARNING,
                )
                return
            self._show_card_info(card)
            return

        matches = cards_repo.find_by_number(cid, number)
        if not matches:
            self._clear_info()
            self._set_status(
                self.tr("Número {n} no existe en esta colección").format(n=number),
                StatusColor.WARNING,
            )
            return

        if len(matches) == 1:
            self._unambiguous_card = matches[0]
            self._show_card_info(matches[0])
            return

        # Ambigüedad: ofrecer el campo de código limitado a los matched
        self._unambiguous_card = None
        self._has_ambiguity = True
        self._populate_completer_with_ambiguous(matches)
        self._set_code_visible(True)
        self._wire_navigator()
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_status(
            self.tr("Hay {n} cards con número {num}, especificá el código").format(
                n=len(matches), num=number
            ),
            StatusColor.WARNING,
        )
        self._code_edit.setFocus()

    def _show_card_info(self, card: Card) -> None:
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        self._country_input.setText(self._lookup_code_name(card.code_id))
        self._name_input.setText(card.card_name)
        item = InventoryRepository(self.conn).get(cid, card.code_id, card.card_number)
        if item is None or item.quantity == 0:
            self._set_status(self.tr("Nueva"), StatusColor.SUCCESS)
        else:
            self._set_status(
                self.tr("Repetida · tenés {n}").format(n=item.quantity),
                StatusColor.REPEATED,
            )

    def _clear_info(self) -> None:
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_status("", "")
        if not self.collection.requires_code and self._has_ambiguity:
            self._set_code_visible(False)
            self._has_ambiguity = False
            self._wire_navigator()
        self._unambiguous_card = None

    def _lookup_code_name(self, code_id: str) -> str:
        line = CodesLinesRepository(self.conn).get(self.collection.code_header_id, code_id)
        return line.code_name if line else code_id

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _save_card(self) -> None:
        number_text = self._number_input.text().strip()
        qty_text = self._qty_input.text().strip() or "1"
        if not number_text:
            self._set_status(self.tr("Falta número"), StatusColor.WARNING)
            return
        try:
            number = int(number_text)
            qty = int(qty_text)
        except ValueError:
            self._set_status(self.tr("Cantidad o número inválido"), StatusColor.WARNING)
            return
        if qty <= 0:
            self._set_status(self.tr("Cantidad debe ser positiva"), StatusColor.WARNING)
            return

        is_alta = self._alta_radio.isChecked()
        service = InventoryService(self.conn)
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id

        # Cuándo el usuario debió especificar un código:
        # - requires_code=True (siempre)
        # - hubo ambigüedad y el usuario eligió uno
        user_specified_code = self.collection.requires_code or self._has_ambiguity

        if user_specified_code and not self._selected_code_id:
            # No hay código válido seleccionado: bloquear save y avisar
            # visualmente (mismo flash rojo que en _on_code_return_pressed).
            self._code_edit.setFocus()
            self._flash_invalid_code()
            self._set_status(self.tr("Falta código"), StatusColor.WARNING)
            return

        try:
            updated = self._dispatch_save(service, cid, number, qty, is_alta, user_specified_code)
        except AmbiguousCardError as exc:
            # Defensa: no debería pasar (la UI ya filtra), pero por las dudas.
            logger.warning("Ambigüedad inesperada al guardar: %d matches", len(exc.matches))
            self._set_status(
                self.tr("Hay {n} cards con ese número, especificá el código").format(
                    n=len(exc.matches)
                ),
                StatusColor.WARNING,
            )
            return
        except ValueError as exc:
            self._set_status(str(exc), StatusColor.ERROR)
            return

        op_label = self.tr("alta") if is_alta else self.tr("baja")
        self._set_status(
            self.tr("OK · {op} · ahora tenés {n}").format(op=op_label, n=updated.quantity),
            StatusColor.SUCCESS,
        )
        self._after_successful_load()
        self.card_changed.emit()

    def _dispatch_save(
        self,
        service: InventoryService,
        cid: int,
        number: int,
        qty: int,
        is_alta: bool,
        user_specified_code: bool,
    ) -> InventoryItem:
        if user_specified_code:
            code = self._get_selected_code()
            if not code:
                raise ValueError(self.tr("Falta código"))
            if is_alta:
                return service.add_card(cid, code, number, qty)
            return service.remove_card(cid, code, number, qty)
        if is_alta:
            return service.add_card_by_number(cid, number, qty)
        return service.remove_card_by_number(cid, number, qty)

    def _after_successful_load(self) -> None:
        """Post-carga: limpia número/qty/preview y posiciona foco según contexto.

        Diferencia clave con `_reset_form`:
        - **`requires_code=True`**: NO limpia el SET — lo deja con el texto
          actual seleccionado (`selectAll`) y `_set_confirmed=True`. Esto
          permite que un Enter inmediato en el SET (sin tipear nada) salte
          al número manteniendo el código (flujo común: cargar varias
          cards del mismo set seguidas).
        - **`requires_code=False`**: igual que `_reset_form` — sale de
          modo ambigüedad y vuelve foco al primer input activo.
        """
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        self._unambiguous_card = None

        if self.collection.requires_code:
            # Mantener el SET actual seleccionado para edición rápida.
            # Si el usuario presiona Enter sin tipear, `_on_code_return_pressed`
            # detecta `_set_confirmed=True` y salta a número.
            self._code_edit.setFocus()
            self._code_edit.selectAll()
            self._set_confirmed = True
            return

        # Sin código: salir de ambigüedad si correspondía y foco al número.
        if self._has_ambiguity:
            self._has_ambiguity = False
            self._set_code_visible(False)
            self._clear_completer()
            self._wire_navigator()
        self._first_active_input().setFocus()

    def _reset_form(self) -> None:
        self._number_input.setText("")
        self._qty_input.setText("1")
        self._country_input.setText("")
        self._name_input.setText("")
        self._set_confirmed = False
        if self.collection.requires_code:
            # Limpiar el campo de código para la próxima alta/baja, manteniendo
            # las opciones del completer (siguen siendo todos los codes_lines).
            self._code_edit.blockSignals(True)
            self._code_edit.clear()
            self._code_edit.blockSignals(False)
            self._selected_code_id = None
        else:
            # Salir del modo ambigüedad
            self._has_ambiguity = False
            self._set_code_visible(False)
            self._clear_completer()
        self._wire_navigator()
        self._unambiguous_card = None
        self._first_active_input().setFocus()

    def _set_status(self, message: str, color: str) -> None:
        if not message:
            self._status_label.setVisible(False)
            self._status_label.setText("")
            self._status_label.setStyleSheet("")
            return
        self._status_label.setText(message)
        self._status_label.setStyleSheet(
            f"border: 1px solid {color}; border-radius: 4px;"
            f" padding: 4px 8px; color: {color}; font-size: 11pt;"
        )
        self._status_label.setVisible(True)
```

### [src/collections_app/client/views/compare_view.py](src/collections_app/client/views/compare_view.py)

```python
"""Tab Comparar Álbumes: genera/importa archivos .colexchange y compara.

Flujo del usuario:
1. "Generar archivo .colexchange" → guarda los faltantes/repetidas propios
   en un archivo y lo comparte con el otro usuario (mail, WhatsApp, etc.).
2. "Importar archivo del otro usuario" → carga el archivo del compañero,
   valida checksum, y dispara la comparación automáticamente.
3. Las dos grillas muestran el resultado: "Me hacen falta" / "Puedo ofrecer".
4. "Generar PDF" produce un PDF con ambas listas (con metadata embebida).
5. "Ejecutar intercambio" abre el `ExchangeView` (dialog modal) que
   bloquea las cartas en inventario hasta confirmar/cancelar.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.client.views.exchange_view import ExchangeView
from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Collection,
    ComparisonResult,
    ExchangeFile,
)
from collections_app.core.repositories import CodesLinesRepository
from collections_app.core.services import (
    EXCHANGE_EXTENSION,
    ExchangeService,
    PdfGeneratorResult,
)
from collections_app.core.services.pdf_generator import generate_comparison_pdf
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Workers (cada uno abre su propia conexión a la DB — NO compartir)
# ----------------------------------------------------------------------


class _GenerateFileWorker(QThread):
    """Genera el archivo .colexchange en thread separado."""

    finished_ok = Signal(object)  # ExchangeFile
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        output_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._output_path = output_path

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                ef = ExchangeService(conn).generate_exchange_file(
                    self._collection_id, self._output_path
                )
            finally:
                conn.close()
            self.finished_ok.emit(ef)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando archivo de comparación")
            self.failed.emit(str(exc))


class _ComparisonPdfWorker(QThread):
    """Genera el PDF de comparación en thread separado."""

    finished_ok = Signal(object)  # PdfGeneratorResult
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection: Collection,
        result: ComparisonResult,
        output_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection = collection
        self._result = result
        self._output_path = output_path

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                code_names = {
                    line.code_id: line.code_name
                    for line in CodesLinesRepository(conn).list_by_header(
                        self._collection.code_header_id
                    )
                }
                result = generate_comparison_pdf(
                    self._collection,
                    code_names,
                    self._result.i_need,
                    self._result.i_can_offer,
                    self._output_path,
                )
            finally:
                conn.close()
            self.finished_ok.emit(result)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error generando PDF de comparación")
            if self._output_path.exists():
                self._output_path.unlink(missing_ok=True)
            self.failed.emit(str(exc))


# ----------------------------------------------------------------------
# View principal
# ----------------------------------------------------------------------


class CompareView(QWidget):
    """Tab principal del módulo Comparar."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: Path,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._db_path = db_path
        self.collection = collection

        self._other_file: ExchangeFile | None = None
        self._comparison: ComparisonResult | None = None
        self._gen_worker: _GenerateFileWorker | None = None
        self._pdf_worker: _ComparisonPdfWorker | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        """Cambio de colección: limpiar estado para evitar comparar datos cruzados."""
        self.collection = collection
        self._other_file = None
        self._comparison = None
        self._other_status_label.setText(self.tr("Ninguno cargado"))
        self._i_need_list.clear()
        self._i_offer_list.clear()
        self._update_action_buttons()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        outer.setSpacing(Spacing.MD)

        title = QLabel(self.tr("Comparar Álbumes"))
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        outer.addWidget(title)

        outer.addWidget(self._build_steps_section())
        outer.addWidget(self._build_results_section(), stretch=1)
        outer.addLayout(self._build_actions_row())

        self._update_action_buttons()

    def _build_steps_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(Spacing.SM)

        # Paso 1
        step1 = QLabel(
            "<b>" + self.tr("Paso 1") + "</b>: " + self.tr("Generar mi archivo de comparación")
        )
        layout.addWidget(step1)
        row1 = QHBoxLayout()
        self._gen_button = QPushButton(self.tr("Generar archivo .colexchange"))
        self._gen_button.clicked.connect(self._on_generate_file)
        row1.addWidget(self._gen_button)
        self._gen_status_label = QLabel("")
        self._gen_status_label.setWordWrap(True)
        row1.addWidget(self._gen_status_label, stretch=1)
        layout.addLayout(row1)

        # Paso 2
        step2 = QLabel(
            "<b>" + self.tr("Paso 2") + "</b>: " + self.tr("Importar archivo del otro usuario")
        )
        layout.addWidget(step2)
        row2 = QHBoxLayout()
        self._import_button = QPushButton(self.tr("Importar archivo .colexchange"))
        self._import_button.clicked.connect(self._on_import_file)
        row2.addWidget(self._import_button)
        self._other_status_label = QLabel(self.tr("Ninguno cargado"))
        row2.addWidget(self._other_status_label, stretch=1)
        layout.addLayout(row2)

        return frame

    def _build_results_section(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        outer = QVBoxLayout(frame)
        outer.setSpacing(Spacing.SM)

        row = QHBoxLayout()
        # Columna izquierda: me hacen falta
        left = QVBoxLayout()
        self._i_need_title = QLabel("<b>" + self.tr("Me hacen falta") + "</b>")
        left.addWidget(self._i_need_title)
        self._i_need_list = QListWidget()
        left.addWidget(self._i_need_list)

        # Columna derecha: puedo ofrecer
        right = QVBoxLayout()
        self._i_offer_title = QLabel("<b>" + self.tr("Puedo ofrecer") + "</b>")
        right.addWidget(self._i_offer_title)
        self._i_offer_list = QListWidget()
        right.addWidget(self._i_offer_list)

        row.addLayout(left, stretch=1)
        row.addLayout(right, stretch=1)
        outer.addLayout(row)
        return frame

    def _build_actions_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self._pdf_button = QPushButton(self.tr("Generar PDF comparación"))
        self._pdf_button.clicked.connect(self._on_generate_pdf)
        self._exec_button = QPushButton(self.tr("Ejecutar intercambio"))
        self._exec_button.clicked.connect(self._on_execute_exchange)
        row.addWidget(self._pdf_button)
        row.addWidget(self._exec_button)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_generate_file(self) -> None:
        # Default: ~/Downloads (fallback a ~ si no existe — cuentas nuevas
        # de Windows o sistemas Linux mínimos pueden no tenerla).
        default_dir = Path.home() / "Downloads"
        if not default_dir.exists():
            default_dir = Path.home()

        date = datetime.now().strftime("%Y-%m-%d")
        # Sanitizar el nombre de la colección para que sea filename-safe:
        # mantener alfanuméricos, espacios, guiones y _; reemplazar el resto.
        safe_name = (
            "".join(
                ch if ch.isalnum() or ch in " _-" else "_" for ch in self.collection.collection_name
            )
            .strip()
            .replace(" ", "_")
        )
        default_name = f"MiAlbum_{safe_name}_{date}{EXCHANGE_EXTENSION}"
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Guardar archivo de comparación"),
            str(default_dir / default_name),
            self.tr("CollectionsApp Exchange (*{ext})").format(ext=EXCHANGE_EXTENSION),
        )
        if not path_str:
            return
        out = Path(path_str)
        if out.suffix != EXCHANGE_EXTENSION:
            out = out.with_suffix(EXCHANGE_EXTENSION)

        self._gen_button.setEnabled(False)
        self._gen_status_label.setText(self.tr("Generando…"))
        self._gen_status_label.setStyleSheet("")

        assert self.collection.collection_id is not None
        worker = _GenerateFileWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            output_path=out,
            parent=self,
        )
        self._gen_worker = worker

        def on_ok(_ef: object) -> None:
            self._gen_button.setEnabled(True)
            self._gen_status_label.setText(self.tr("✓ Archivo generado en: {p}").format(p=str(out)))
            self._gen_status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")

        def on_failed(msg: str) -> None:
            self._gen_button.setEnabled(True)
            self._gen_status_label.setText(self.tr("Error: {m}").format(m=msg))
            self._gen_status_label.setStyleSheet(f"color: {StatusColor.ERROR};")

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _on_import_file(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar archivo de comparación"),
            "",
            self.tr("CollectionsApp Exchange (*{ext})").format(ext=EXCHANGE_EXTENSION),
        )
        if not path_str:
            return
        path = Path(path_str)

        try:
            other = ExchangeService(self.conn).load_exchange_file(path)
        except ValueError as exc:
            QMessageBox.warning(
                self,
                self.tr("Archivo inválido"),
                str(exc),
            )
            return

        if other.collection_id != self.collection.collection_id:
            QMessageBox.warning(
                self,
                self.tr("Colección distinta"),
                self.tr(
                    'El archivo es de la colección "{name}" (id={id}) — '
                    'no coincide con la activa ("{active}").'
                ).format(
                    name=other.collection_name,
                    id=other.collection_id,
                    active=self.collection.collection_name,
                ),
            )
            return

        self._other_file = other
        self._other_status_label.setText(
            self.tr("✓ {n} faltantes / {d} repetidas").format(
                n=len(other.missing), d=len(other.duplicates)
            )
        )
        self._other_status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")
        self._run_comparison()

    def _run_comparison(self) -> None:
        """Genera mi snapshot in-memory y compara con el otro archivo."""
        if self._other_file is None:
            return

        # Snapshot propio in-memory (sin escribir a disco). Usamos un
        # path temporal que borramos enseguida — la API actual escribe
        # siempre, pero el costo es despreciable.
        import tempfile

        assert self.collection.collection_id is not None
        with tempfile.NamedTemporaryFile(suffix=EXCHANGE_EXTENSION, delete=False) as tf:
            tmp_path = Path(tf.name)
        try:
            svc = ExchangeService(self.conn)
            my_file = svc.generate_exchange_file(self.collection.collection_id, tmp_path)
            self._comparison = svc.compare(my_file, self._other_file)
        finally:
            tmp_path.unlink(missing_ok=True)

        self._populate_results()
        self._update_action_buttons()

    def _populate_results(self) -> None:
        self._i_need_list.clear()
        self._i_offer_list.clear()
        if self._comparison is None:
            return

        self._i_need_title.setText(
            "<b>" + self.tr("Me hacen falta") + f" ({len(self._comparison.i_need)})</b>"
        )
        self._i_offer_title.setText(
            "<b>" + self.tr("Puedo ofrecer") + f" ({len(self._comparison.i_can_offer)})</b>"
        )

        for card in self._comparison.i_need:
            self._i_need_list.addItem(QListWidgetItem(self._format_card(card, with_qty=False)))
        for card in self._comparison.i_can_offer:
            self._i_offer_list.addItem(
                QListWidgetItem(self._format_card(card, with_qty=card.quantity > 1))
            )

    def _format_card(self, card: object, with_qty: bool) -> str:
        from collections_app.core.models import ExchangeCard

        assert isinstance(card, ExchangeCard)
        if self.collection.requires_code:
            label = f"{card.code_id}-{card.card_number}"
        else:
            label = str(card.card_number)
        text = f"{label:<10} {card.card_name}"
        if with_qty and card.quantity > 1:
            text += f"  ×{card.quantity}"
        return text

    def _update_action_buttons(self) -> None:
        has_result = self._comparison is not None
        self._pdf_button.setEnabled(has_result)
        # Ejecutar intercambio: solo si hay AL MENOS una carta para
        # intercambiar (en cualquiera de las dos direcciones).
        has_cards = has_result and (
            len(self._comparison.i_need) > 0  # type: ignore[union-attr]
            or len(self._comparison.i_can_offer) > 0  # type: ignore[union-attr]
        )
        self._exec_button.setEnabled(has_cards)

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------

    def _on_generate_pdf(self) -> None:
        """Genera el PDF en `%TEMP%` y abre el preview para guardar.

        El usuario decide destino desde el preview (mismo flujo que en
        AlbumView). El temp se borra siempre (cancel o tras copiar).
        """
        if self._comparison is None:
            return
        import os
        import tempfile

        from collections_app.client.dialogs.pdf_preview_dialog import PdfPreviewDialog

        date = datetime.now().strftime("%Y-%m-%d")
        slug = (
            "".join(
                ch if ch.isalnum() or ch in " _-" else "_" for ch in self.collection.collection_name
            )
            .strip()
            .replace(" ", "_")
        )
        suggested = f"Comparacion_{slug}_{date}.pdf"

        fd, tmp_str = tempfile.mkstemp(suffix=".pdf", prefix="collections_")
        os.close(fd)
        tmp_path = Path(tmp_str)

        self._pdf_button.setEnabled(False)
        worker = _ComparisonPdfWorker(
            db_path=self._db_path,
            collection=self.collection,
            result=self._comparison,
            output_path=tmp_path,
            parent=self,
        )
        self._pdf_worker = worker

        def on_ok(result: object) -> None:
            self._pdf_button.setEnabled(True)
            assert isinstance(result, PdfGeneratorResult)
            dialog = PdfPreviewDialog(
                temp_pdf_path=tmp_path, suggested_filename=suggested, parent=self
            )
            dialog.exec()

        def on_failed(msg: str) -> None:
            self._pdf_button.setEnabled(True)
            tmp_path.unlink(missing_ok=True)
            QMessageBox.critical(self, self.tr("Error"), msg)

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    # ------------------------------------------------------------------
    # Ejecutar intercambio
    # ------------------------------------------------------------------

    def _on_execute_exchange(self) -> None:
        if self._comparison is None:
            return
        assert self.collection.collection_id is not None
        dlg = ExchangeView(
            conn=self.conn,
            db_path=self._db_path,
            collection=self.collection,
            comparison=self._comparison,
            parent=self,
        )
        if dlg.exec():
            # Intercambio confirmado: limpiar comparación y refrescar UI
            self._comparison = None
            self._other_file = None
            self._other_status_label.setText(self.tr("Ninguno cargado"))
            self._i_need_list.clear()
            self._i_offer_list.clear()
            self._update_action_buttons()
```

### [src/collections_app/client/views/exchange_view.py](src/collections_app/client/views/exchange_view.py)

```python
"""ExchangeView: dialog modal para ejecutar un intercambio entre dos usuarios.

Pre-puebla las dos grillas (Entrego / Recibo) con el `ComparisonResult`
del CompareView. Al abrir bloquea las cartas a entregar en inventario;
al cerrar (cancelar/X) las desbloquea automáticamente. Solo "Ejecutar
intercambio" hace cambios persistentes en inventario.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Collection,
    ComparisonResult,
    ExchangeCard,
    ExchangeSession,
)
from collections_app.core.repositories import (
    CardsRepository,
)
from collections_app.core.services import ExchangeService
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Worker para ejecutar el intercambio (no bloquea UI)
# ----------------------------------------------------------------------


class _ExecuteExchangeWorker(QThread):
    """Ejecuta `ExchangeService.execute_exchange` en thread separado."""

    finished_ok = Signal()
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        session: ExchangeSession,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._session = session

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                ExchangeService(conn).execute_exchange(self._collection_id, self._session)
            finally:
                conn.close()
            self.finished_ok.emit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error ejecutando intercambio")
            self.failed.emit(str(exc))


# ----------------------------------------------------------------------
# Dialog auxiliar: agregar carta manual al intercambio
# ----------------------------------------------------------------------


class _AddCardDialog(QDialog):
    """Mini-form para buscar una carta en el catálogo y agregarla al intercambio.

    No reusa el CardLoaderView completo (sería overkill — ese maneja
    inventario, transactions, ambigüedad, completer, etc.). Acá solo
    necesitamos: pedir un (code_id, card_number) válido contra el
    catálogo y devolver la `ExchangeCard` correspondiente.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        title: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._collection = collection
        self._result: ExchangeCard | None = None

        self.setWindowTitle(title)
        self._build_ui()

    @property
    def result_card(self) -> ExchangeCard | None:
        return self._result

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        form = QHBoxLayout()
        if self._collection.requires_code:
            form.addWidget(QLabel(self.tr("Código") + ":"))
            self._code_edit = QLineEdit()
            self._code_edit.setMaxLength(10)
            self._code_edit.setFixedWidth(80)
            form.addWidget(self._code_edit)
        else:
            self._code_edit = None  # type: ignore[assignment]
        form.addWidget(QLabel(self.tr("Número") + ":"))
        self._number_edit = QLineEdit()
        self._number_edit.setFixedWidth(80)
        form.addWidget(self._number_edit)
        form.addStretch()
        layout.addLayout(form)

        self._info_label = QLabel("")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        number_text = self._number_edit.text().strip()
        try:
            number = int(number_text)
        except ValueError:
            self._info_label.setText(self.tr("Número inválido"))
            self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
            return

        cards_repo = CardsRepository(self._conn)
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id

        if self._collection.requires_code:
            code_id = (self._code_edit.text() or "").strip().upper()
            if not code_id:
                self._info_label.setText(self.tr("Código vacío"))
                self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
                return
            card = cards_repo.get(cid, code_id, number)
            if card is None:
                self._info_label.setText(
                    self.tr("{c}-{n} no existe en el catálogo").format(c=code_id, n=number)
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.ERROR};")
                return
        else:
            matches = cards_repo.find_by_number(cid, number)
            if not matches:
                self._info_label.setText(
                    self.tr("Número {n} no existe en el catálogo").format(n=number)
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.ERROR};")
                return
            if len(matches) > 1:
                self._info_label.setText(
                    self.tr(
                        "Hay {n} cards con ese número, no se puede agregar sin "
                        "especificar código (caso ambiguo no soportado en intercambio)"
                    ).format(n=len(matches))
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
                return
            card = matches[0]

        self._result = ExchangeCard(
            code_id=card.code_id,
            card_number=card.card_number,
            card_name=card.card_name,
            quantity=1,
        )
        self.accept()


# ----------------------------------------------------------------------
# ExchangeView principal
# ----------------------------------------------------------------------


class ExchangeView(QDialog):
    """Dialog modal de ejecución de intercambio."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: Path,
        collection: Collection,
        comparison: ComparisonResult,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._db_path = db_path
        self.collection = collection
        self._comparison = comparison
        self._exec_worker: _ExecuteExchangeWorker | None = None
        # Flag para distinguir cierres "esperados" (Ejecutar/Cancelar) de
        # cierres por la X — en el segundo caso necesitamos unlock.
        self._cleanup_done = False

        self.setWindowTitle(self.tr("Ejecutar Intercambio"))
        self.setMinimumSize(700, 500)
        self._build_ui()
        # Pre-poblar grillas + bloquear cartas a entregar.
        self._populate_initial()
        self._lock_initial_to_give()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        outer.setSpacing(Spacing.MD)

        # Dos columnas
        cols = QHBoxLayout()
        # Entrego
        give_layout = QVBoxLayout()
        give_layout.addWidget(QLabel("<b>" + self.tr("Entrego") + "</b>"))
        self._give_list = QListWidget()
        give_layout.addWidget(self._give_list, stretch=1)
        self._add_give_button = QPushButton(self.tr("+ Agregar figurita"))
        self._add_give_button.clicked.connect(self._on_add_give)
        give_layout.addWidget(self._add_give_button)

        # Recibo
        recv_layout = QVBoxLayout()
        recv_layout.addWidget(QLabel("<b>" + self.tr("Recibo") + "</b>"))
        self._recv_list = QListWidget()
        recv_layout.addWidget(self._recv_list, stretch=1)
        self._add_recv_button = QPushButton(self.tr("+ Agregar figurita"))
        self._add_recv_button.clicked.connect(self._on_add_recv)
        recv_layout.addWidget(self._add_recv_button)

        cols.addLayout(give_layout, stretch=1)
        cols.addLayout(recv_layout, stretch=1)
        outer.addLayout(cols, stretch=1)

        # Botones inferiores
        buttons = QHBoxLayout()
        self._exec_button = QPushButton(self.tr("✓ Ejecutar intercambio"))
        self._exec_button.clicked.connect(self._on_execute)
        cancel_button = QPushButton(self.tr("✕ Cancelar"))
        cancel_button.clicked.connect(self._on_cancel)
        buttons.addWidget(self._exec_button)
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        outer.addLayout(buttons)

    # ------------------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------------------

    def _populate_initial(self) -> None:
        """Pre-puebla las grillas con el ComparisonResult, todo chequeado."""
        for card in self._comparison.i_can_offer:
            self._add_card_to_list(self._give_list, card)
        for card in self._comparison.i_need:
            self._add_card_to_list(self._recv_list, card)

    def _lock_initial_to_give(self) -> None:
        """Bloquea en inventario las cartas pre-pobladas en `Entrego`."""
        if not self._comparison.i_can_offer:
            return
        assert self.collection.collection_id is not None
        ExchangeService(self.conn).lock_cards(
            self.collection.collection_id, self._comparison.i_can_offer
        )

    def _add_card_to_list(self, target: QListWidget, card: ExchangeCard) -> None:
        item = QListWidgetItem(self._format_card(card))
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        # Guardamos el ExchangeCard en el data role para reconstruirlo.
        item.setData(Qt.ItemDataRole.UserRole, card)
        target.addItem(item)

    def _format_card(self, card: ExchangeCard) -> str:
        if self.collection.requires_code:
            label = f"{card.code_id}-{card.card_number}"
        else:
            label = str(card.card_number)
        return f"{label:<10} {card.card_name}"

    # ------------------------------------------------------------------
    # Agregar cartas manualmente
    # ------------------------------------------------------------------

    def _on_add_give(self) -> None:
        # Confirmación: el usuario está agregando una carta para regalar.
        confirm = QMessageBox.question(
            self,
            self.tr("Agregar figurita a entregar"),
            self.tr(
                "¿Seguro que querés agregar una carta para entregar?\n"
                "Se dará de baja del inventario al confirmar el intercambio."
            ),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        dlg = _AddCardDialog(
            self.conn,
            self.collection,
            self.tr("Agregar carta a entregar"),
            parent=self,
        )
        if not dlg.exec() or dlg.result_card is None:
            return
        card = dlg.result_card

        # Bloquear en inventario inmediatamente
        assert self.collection.collection_id is not None
        ExchangeService(self.conn).lock_cards(self.collection.collection_id, [card])
        self._add_card_to_list(self._give_list, card)

    def _on_add_recv(self) -> None:
        dlg = _AddCardDialog(
            self.conn,
            self.collection,
            self.tr("Agregar carta a recibir"),
            parent=self,
        )
        if not dlg.exec() or dlg.result_card is None:
            return
        self._add_card_to_list(self._recv_list, dlg.result_card)

    # ------------------------------------------------------------------
    # Ejecutar / Cancelar
    # ------------------------------------------------------------------

    def _checked_cards(self, target: QListWidget) -> list[ExchangeCard]:
        out: list[ExchangeCard] = []
        for i in range(target.count()):
            item = target.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                card = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(card, ExchangeCard):
                    out.append(card)
        return out

    def _on_execute(self) -> None:
        to_give = self._checked_cards(self._give_list)
        to_receive = self._checked_cards(self._recv_list)

        confirm = QMessageBox.question(
            self,
            self.tr("Confirmar intercambio"),
            self.tr(
                "¿Confirmás el intercambio?\n\n"
                "Entregás: {g} figurita(s)\n"
                "Recibís: {r} figurita(s)\n\n"
                "Esta acción no se puede deshacer."
            ).format(g=len(to_give), r=len(to_receive)),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        session = ExchangeSession(to_give=to_give, to_receive=to_receive)
        self._exec_button.setEnabled(False)

        assert self.collection.collection_id is not None
        worker = _ExecuteExchangeWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            session=session,
            parent=self,
        )
        self._exec_worker = worker

        def on_ok() -> None:
            QMessageBox.information(
                self,
                self.tr("Intercambio ejecutado"),
                self.tr("Intercambio ejecutado correctamente."),
            )
            self._cleanup_done = True
            self.accept()

        def on_failed(msg: str) -> None:
            self._exec_button.setEnabled(True)
            QMessageBox.critical(
                self,
                self.tr("Error al ejecutar"),
                self.tr("No se pudo ejecutar el intercambio:\n{m}").format(m=msg),
            )

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _on_cancel(self) -> None:
        self._unlock_inventory()
        self._cleanup_done = True
        self.reject()

    def _unlock_inventory(self) -> None:
        """Resetea locked=0 para toda la colección."""
        assert self.collection.collection_id is not None
        try:
            ExchangeService(self.conn).unlock_all_cards(self.collection.collection_id)
        except Exception:
            logger.exception("Error desbloqueando inventario al cerrar dialog")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        """Si se cierra con la X sin Ejecutar/Cancelar, desbloquear igual."""
        if not self._cleanup_done:
            self._unlock_inventory()
            self._cleanup_done = True
        super().closeEvent(event)
```

### [src/collections_app/client/views/inventory_view.py](src/collections_app/client/views/inventory_view.py)

```python
"""Tab Inventario: lista todas las cards del catálogo con su estado."""

import sqlite3

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.shared_ui.theme import Spacing

# Colores sutiles para las filas según estado
COLOR_OWNED = QColor("#FFFFFF")  # blanco normal
COLOR_REPEATED = QColor("#FFF8DC")  # crema claro
COLOR_MISSING = QColor("#F5F5F5")  # gris muy claro

STATUS_OWNED = "Tengo"
STATUS_REPEATED = "Repetida"
STATUS_MISSING = "Falta"

FILTER_ALL = "Todas"


class _StateFilterProxy(QSortFilterProxyModel):
    """Filtra por la combinación de estado, código y substring del nombre."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state_filter: str = FILTER_ALL
        self._code_filter: str = FILTER_ALL
        self._name_substring: str = ""
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def set_state_filter(self, state: str) -> None:
        self._state_filter = state
        self.invalidate()

    def set_code_filter(self, code: str) -> None:
        self._code_filter = code
        self.invalidate()

    def set_name_substring(self, text: str) -> None:
        self._name_substring = text.strip().lower()
        self.invalidate()

    def filterAcceptsRow(  # noqa: N802
        self,
        source_row: int,
        source_parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        del source_parent  # Modelo plano, ignoramos el parent
        model = self.sourceModel()
        code = model.index(source_row, InventoryView.COL_CODE).data() or ""
        name = (model.index(source_row, InventoryView.COL_NAME).data() or "").lower()
        state = model.index(source_row, InventoryView.COL_STATE).data() or ""

        if self._state_filter != FILTER_ALL and state != self._state_filter:
            return False
        if self._code_filter != FILTER_ALL and code != self._code_filter:
            return False
        return not (self._name_substring and self._name_substring not in name)


class InventoryView(QWidget):
    """Tab que lista todas las cards con su estado de inventario."""

    COL_CODE = 0
    COL_NUMBER = 1
    COL_NAME = 2
    COL_QUANTITY = 3
    COL_STATE = 4

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self._populate_code_filter()
        self.refresh()

    def refresh(self) -> None:
        self._populate_grid()
        self._update_status_bar()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        # Crear modelos antes que los filtros que los referencian.
        self._grid_model = QStandardItemModel(0, 5, self)
        self._grid_model.setHorizontalHeaderLabels(
            [
                self.tr("Código"),
                self.tr("Número"),
                self.tr("Nombre"),
                self.tr("Cantidad"),
                self.tr("Estado"),
            ]
        )
        self._proxy = _StateFilterProxy(self)
        self._proxy.setSourceModel(self._grid_model)

        layout.addLayout(self._build_filter_row())

        self._grid_view = QTableView()
        self._grid_view.setModel(self._proxy)
        self._grid_view.setSortingEnabled(True)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setStretchLastSection(False)
        self._grid_view.horizontalHeader().setSectionResizeMode(
            self.COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        self._grid_view.sortByColumn(self.COL_CODE, Qt.SortOrder.AscendingOrder)
        layout.addWidget(self._grid_view, stretch=1)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def _build_filter_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        row.addWidget(QLabel(self.tr("Estado") + ":"))
        self._state_filter = QComboBox()
        self._state_filter.addItems([FILTER_ALL, STATUS_OWNED, STATUS_REPEATED, STATUS_MISSING])
        self._state_filter.currentTextChanged.connect(self._proxy.set_state_filter)
        row.addWidget(self._state_filter)

        row.addWidget(QLabel(self.tr("Código") + ":"))
        self._code_filter = QComboBox()
        self._populate_code_filter()
        self._code_filter.currentTextChanged.connect(self._proxy.set_code_filter)
        row.addWidget(self._code_filter)

        row.addWidget(QLabel(self.tr("Buscar") + ":"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self.tr("nombre…"))
        self._search_input.textChanged.connect(self._proxy.set_name_substring)
        row.addWidget(self._search_input, stretch=1)
        return row

    # ------------------------------------------------------------------
    # Población de combos / grilla
    # ------------------------------------------------------------------

    def _populate_code_filter(self) -> None:
        repo = CodesLinesRepository(self.conn)
        self._code_filter.blockSignals(True)
        self._code_filter.clear()
        self._code_filter.addItem(FILTER_ALL)
        for line in repo.list_by_header(self.collection.code_header_id):
            self._code_filter.addItem(line.code_id)
        self._code_filter.blockSignals(False)

    def _populate_grid(self) -> None:
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id
        cards = CardsRepository(self.conn).list_by_collection(cid)
        inv = InventoryRepository(self.conn)
        inv_by_key = {(i.code_id, i.card_number): i for i in inv.list_by_collection(cid)}

        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for card in cards:
            item = inv_by_key.get((card.code_id, card.card_number))
            qty = item.quantity if item else 0
            if qty == 0:
                state = STATUS_MISSING
                color = COLOR_MISSING
            elif qty == 1:
                state = STATUS_OWNED
                color = COLOR_OWNED
            else:
                state = STATUS_REPEATED
                color = COLOR_REPEATED

            row = [
                self._make_item(card.code_id, color),
                self._make_item(str(card.card_number), color, numeric=card.card_number),
                self._make_item(card.card_name, color),
                self._make_item(str(qty), color, numeric=qty),
                self._make_item(state, color),
            ]
            self._grid_model.appendRow(row)

    def _make_item(
        self,
        text: str,
        color: QColor,
        numeric: int | None = None,
    ) -> QStandardItem:
        item = QStandardItem(text)
        item.setEditable(False)
        item.setBackground(QBrush(color))
        if numeric is not None:
            # Para que el sort numérico funcione (no alfabético sobre strings)
            item.setData(numeric, Qt.ItemDataRole.UserRole + 1)
        return item

    # ------------------------------------------------------------------
    # Status bar inferior
    # ------------------------------------------------------------------

    def _update_status_bar(self) -> None:
        total = self._grid_model.rowCount()
        owned = 0
        repeated = 0
        for row in range(total):
            state = self._grid_model.item(row, self.COL_STATE).text()
            if state == STATUS_OWNED:
                owned += 1
            elif state == STATUS_REPEATED:
                repeated += 1
        owned_total = owned + repeated  # cards distintas con qty>0
        missing = total - owned_total
        pct = (owned_total / total * 100) if total > 0 else 0.0
        self._status_label.setText(
            self.tr(
                "Total: {total} cards | Tengo: {owned} ({pct:.1f}%) | "
                "Faltan: {missing} | Repetidas: {repeated}"
            ).format(
                total=total,
                owned=owned_total,
                pct=pct,
                missing=missing,
                repeated=repeated,
            )
        )
```

### [src/collections_app/client/views/reports_view.py](src/collections_app/client/views/reports_view.py)

```python
"""Tab Reportes: bitácora de altas/bajas con presets y export CSV."""

import csv
import logging
import sqlite3
from datetime import UTC, datetime, time, timedelta
from pathlib import Path

from PySide6.QtCore import QDate
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection, OperationType
from collections_app.core.services import ReportsService, TransactionWithCard
from collections_app.core.utils.datetime_helpers import (
    format_for_display,
    to_local,
)
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)

# Presets para el combo "Período"
PRESET_TODAY = "Hoy"
PRESET_LAST_7 = "Últimos 7 días"
PRESET_LAST_30 = "Últimos 30 días"
PRESET_THIS_MONTH = "Este mes"
PRESET_LAST_MONTH = "Mes anterior"
PRESET_CUSTOM = "Personalizado…"

OP_ALL = "Todas"


class ReportsView(QWidget):
    """Tab de reportes: filtros de período y operación + grilla + export CSV."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self.refresh()

    def refresh(self) -> None:
        start, end = self._compute_range()
        op = self._selected_operation()
        assert self.collection.collection_id is not None
        rows = ReportsService(self.conn).get_transactions_in_period(
            self.collection.collection_id, start, end, op
        )
        self._populate_grid(rows)
        self._update_summary(rows)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)

        layout.addLayout(self._build_filters_row())
        layout.addLayout(self._build_custom_row())

        self._grid_model = QStandardItemModel(0, 5, self)
        self._grid_model.setHorizontalHeaderLabels(
            [
                self.tr("Fecha"),
                self.tr("Op"),
                self.tr("Code"),
                self.tr("Nombre"),
                self.tr("Cant."),
            ]
        )
        self._grid_view = QTableView()
        self._grid_view.setModel(self._grid_model)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._grid_view, stretch=1)

        bottom = QHBoxLayout()
        self._summary_label = QLabel("")
        bottom.addWidget(self._summary_label)
        bottom.addStretch()
        self._export_button = QPushButton(self.tr("Exportar a CSV…"))
        self._export_button.clicked.connect(self._export_csv)
        bottom.addWidget(self._export_button)
        layout.addLayout(bottom)

    def _build_filters_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        row.addWidget(QLabel(self.tr("Período") + ":"))
        self._period_combo = QComboBox()
        self._period_combo.addItems(
            [
                PRESET_TODAY,
                PRESET_LAST_7,
                PRESET_LAST_30,
                PRESET_THIS_MONTH,
                PRESET_LAST_MONTH,
                PRESET_CUSTOM,
            ]
        )
        self._period_combo.setCurrentText(PRESET_LAST_7)
        self._period_combo.currentTextChanged.connect(self._on_period_changed)
        row.addWidget(self._period_combo)

        row.addWidget(QLabel(self.tr("Operación") + ":"))
        self._op_combo = QComboBox()
        self._op_combo.addItem(OP_ALL)
        self._op_combo.addItem(self.tr("Alta"), userData=OperationType.ALTA)
        self._op_combo.addItem(self.tr("Baja"), userData=OperationType.BAJA)
        self._op_combo.currentTextChanged.connect(lambda _: self.refresh())
        row.addWidget(self._op_combo)
        row.addStretch()
        return row

    def _build_custom_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self._custom_from_label = QLabel(self.tr("Desde") + ":")
        self._custom_to_label = QLabel(self.tr("Hasta") + ":")
        self._date_from = QDateEdit(QDate.currentDate().addDays(-7))
        self._date_to = QDateEdit(QDate.currentDate())
        for d in (self._date_from, self._date_to):
            d.setCalendarPopup(True)
            d.setDisplayFormat("yyyy-MM-dd")
            d.dateChanged.connect(lambda _: self.refresh())

        row.addWidget(self._custom_from_label)
        row.addWidget(self._date_from)
        row.addWidget(self._custom_to_label)
        row.addWidget(self._date_to)
        row.addStretch()
        # Visibilidad inicial según preset
        self._set_custom_visibility(False)
        return row

    def _set_custom_visibility(self, visible: bool) -> None:
        self._custom_from_label.setVisible(visible)
        self._custom_to_label.setVisible(visible)
        self._date_from.setVisible(visible)
        self._date_to.setVisible(visible)

    # ------------------------------------------------------------------
    # Período: cálculo y sincronización
    # ------------------------------------------------------------------

    def _on_period_changed(self, preset: str) -> None:
        if preset == PRESET_CUSTOM:
            self._set_custom_visibility(True)
        else:
            self._set_custom_visibility(False)
        self.refresh()

    def _compute_range(self) -> tuple[datetime, datetime]:
        """Calcula `(start, end)` en UTC para el preset/custom seleccionado.

        Los presets se calculan sobre la fecha LOCAL (lo que el usuario
        espera ver) y se convierten a UTC antes de retornar.
        """
        preset = self._period_combo.currentText()
        today_local = datetime.now().astimezone()
        local_tz = today_local.tzinfo
        today_date = today_local.date()

        if preset == PRESET_TODAY:
            start_local = datetime.combine(today_date, time.min, tzinfo=local_tz)
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_7:
            start_local = datetime.combine(
                today_date - timedelta(days=6), time.min, tzinfo=local_tz
            )
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_30:
            start_local = datetime.combine(
                today_date - timedelta(days=29), time.min, tzinfo=local_tz
            )
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_THIS_MONTH:
            first = today_date.replace(day=1)
            start_local = datetime.combine(first, time.min, tzinfo=local_tz)
            end_local = datetime.combine(today_date, time.max, tzinfo=local_tz)
        elif preset == PRESET_LAST_MONTH:
            first_this = today_date.replace(day=1)
            last_prev = first_this - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            start_local = datetime.combine(first_prev, time.min, tzinfo=local_tz)
            end_local = datetime.combine(last_prev, time.max, tzinfo=local_tz)
        else:  # PRESET_CUSTOM
            d_from = self._date_from.date()
            d_to = self._date_to.date()
            start_local = datetime(d_from.year(), d_from.month(), d_from.day(), tzinfo=local_tz)
            end_local = datetime(
                d_to.year(),
                d_to.month(),
                d_to.day(),
                23,
                59,
                59,
                tzinfo=local_tz,
            )
        return (
            start_local.astimezone(UTC),
            end_local.astimezone(UTC),
        )

    def _selected_operation(self) -> OperationType | None:
        data = self._op_combo.currentData()
        if data is None:
            return None
        # PySide6 puede deserializar el StrEnum como str; aceptamos ambos.
        if isinstance(data, OperationType):
            return data
        if isinstance(data, str):
            try:
                return OperationType(data)
            except ValueError:
                return None
        return None

    # ------------------------------------------------------------------
    # Grilla y resumen
    # ------------------------------------------------------------------

    def _populate_grid(self, rows: list[TransactionWithCard]) -> None:
        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for r in rows:
            items = [
                QStandardItem(format_for_display(r.transaction_date)),
                QStandardItem(
                    self.tr("Alta") if r.operation == OperationType.ALTA else self.tr("Baja")
                ),
                QStandardItem(f"{r.code_id}-{r.card_number}"),
                QStandardItem(r.card_name),
                QStandardItem(str(r.quantity)),
            ]
            for item in items:
                item.setEditable(False)
            self._grid_model.appendRow(items)

    def _update_summary(self, rows: list[TransactionWithCard]) -> None:
        altas = sum(1 for r in rows if r.operation == OperationType.ALTA)
        bajas = sum(1 for r in rows if r.operation == OperationType.BAJA)
        self._summary_label.setText(
            self.tr("Resumen del período: {a} altas, {b} bajas").format(a=altas, b=bajas)
        )

    # ------------------------------------------------------------------
    # Export CSV
    # ------------------------------------------------------------------

    def _export_csv(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Exportar reporte"),
            "report.csv",
            self.tr("CSV files (*.csv)"),
        )
        if not path_str:
            return

        start, end = self._compute_range()
        op = self._selected_operation()
        assert self.collection.collection_id is not None
        rows = ReportsService(self.conn).get_transactions_in_period(
            self.collection.collection_id, start, end, op
        )

        try:
            self._write_csv(Path(path_str), rows, start, end)
        except OSError as exc:
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            logger.exception("Error escribiendo CSV de reporte")
            return

        QMessageBox.information(
            self,
            self.tr("Exportar reporte"),
            self.tr("Exportadas {n} filas a {path}").format(n=len(rows), path=path_str),
        )

    def _write_csv(
        self,
        path: Path,
        rows: list[TransactionWithCard],
        start: datetime,
        end: datetime,
    ) -> None:
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            # Comentario inicial con metadata: nombre y rango (en hora local)
            writer.writerow(
                [
                    f"# {self.collection.collection_name}",
                    f"desde={format_for_display(start, with_seconds=True)}",
                    f"hasta={format_for_display(end, with_seconds=True)}",
                ]
            )
            writer.writerow(["fecha", "operacion", "codigo", "numero", "nombre", "cantidad"])
            for r in rows:
                writer.writerow(
                    [
                        to_local(r.transaction_date).isoformat(timespec="seconds"),
                        r.operation.value,
                        r.code_id,
                        r.card_number,
                        r.card_name,
                        r.quantity,
                    ]
                )
```

### [src/collections_app/client/views/stats_view.py](src/collections_app/client/views/stats_view.py)

```python
"""Tab Estadísticas: progreso general, por código y top repetidas."""

import sqlite3

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService
from collections_app.shared_ui.theme import Spacing


class StatsView(QWidget):
    """Tab de estadísticas: progreso global, por código y top repetidas."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self.refresh()

    def refresh(self) -> None:
        self._update_overall()
        self._update_per_code()
        self._update_top_duplicates()
        self._update_summary()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.LG)

        layout.addWidget(self._make_section_label(self.tr("Progreso general")))
        self._overall_bar = QProgressBar()
        self._overall_bar.setMinimum(0)
        self._overall_bar.setMaximum(100)
        layout.addWidget(self._overall_bar)
        self._overall_label = QLabel("")
        layout.addWidget(self._overall_label)

        layout.addWidget(self._make_section_label(self.tr("Por código")))
        self._per_code_container = QWidget()
        self._per_code_layout = QVBoxLayout(self._per_code_container)
        self._per_code_layout.setContentsMargins(0, 0, 0, 0)
        self._per_code_layout.setSpacing(Spacing.XS)
        layout.addWidget(self._per_code_container)

        layout.addWidget(self._make_section_label(self.tr("Top repetidas")))
        self._top_dup_container = QWidget()
        self._top_dup_layout = QVBoxLayout(self._top_dup_container)
        self._top_dup_layout.setContentsMargins(0, 0, 0, 0)
        self._top_dup_layout.setSpacing(Spacing.XS)
        layout.addWidget(self._top_dup_container)

        layout.addWidget(self._make_section_label(self.tr("Resumen de inventario")))
        self._summary_label = QLabel("")
        layout.addWidget(self._summary_label)
        layout.addStretch()

    def _make_section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; font-size: 13pt;")
        return label

    # ------------------------------------------------------------------
    # Refresco
    # ------------------------------------------------------------------

    def _update_overall(self) -> None:
        assert self.collection.collection_id is not None
        stats = InventoryService(self.conn).get_stats(self.collection.collection_id)
        total = int(stats["total_cards"])
        owned = int(stats["owned"])
        pct = float(stats["percentage"])
        self._overall_bar.setMaximum(max(total, 1))
        self._overall_bar.setValue(owned)
        self._overall_label.setText(
            self.tr("{owned}/{total} ({pct:.1f}%)").format(owned=owned, total=total, pct=pct)
        )

    def _update_per_code(self) -> None:
        assert self.collection.collection_id is not None
        self._clear_layout(self._per_code_layout)
        stats = CardsRepository(self.conn).get_stats_by_code(self.collection.collection_id)
        for entry in stats:
            row = self._make_per_code_row(
                code_id=entry["code_id"],
                code_name=entry["code_name"],
                owned=entry["owned"],
                total=entry["total"],
                percentage=entry["percentage"],
            )
            self._per_code_layout.addWidget(row)

    def _make_per_code_row(
        self,
        code_id: str,
        code_name: str,
        owned: int,
        total: int,
        percentage: float,
    ) -> QWidget:
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(f"{code_id} — {code_name}")
        label.setMinimumWidth(180)
        layout.addWidget(label)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(max(total, 1))
        bar.setValue(owned)
        bar.setTextVisible(False)
        layout.addWidget(bar, stretch=1)

        layout.addWidget(
            QLabel(self.tr("{o}/{t} ({p:.0f}%)").format(o=owned, t=total, p=percentage))
        )
        return container

    def _update_top_duplicates(self) -> None:
        assert self.collection.collection_id is not None
        self._clear_layout(self._top_dup_layout)
        inv_repo = InventoryRepository(self.conn)
        items = inv_repo.get_top_duplicates(self.collection.collection_id, limit=10)
        if not items:
            self._top_dup_layout.addWidget(QLabel(self.tr("(sin repetidas todavía)")))
            return
        cards_repo = CardsRepository(self.conn)
        for item in items:
            card = cards_repo.get(self.collection.collection_id, item.code_id, item.card_number)
            name = card.card_name if card else ""
            self._top_dup_layout.addWidget(
                QLabel(
                    f"{item.code_id}-{item.card_number} {name} ".ljust(40, ".")
                    + f" x{item.quantity}"
                )
            )

    def _update_summary(self) -> None:
        assert self.collection.collection_id is not None
        stats = InventoryService(self.conn).get_stats(self.collection.collection_id)
        total_physical = int(stats["total_physical"])
        owned = int(stats["owned"])
        extras = int(stats["total_duplicate_copies"])
        self._summary_label.setText(
            self.tr(
                "Total figuritas físicas: {tp}\n"
                "Cards únicas (que tenés): {own}\n"
                "Copias extra (repetidas): {ex}"
            ).format(tp=total_physical, own=owned, ex=extras)
        )

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget() if child else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
```

### [src/collections_app/core/__init__.py](src/collections_app/core/__init__.py)

```python
"""Lógica pura del proyecto: db, models, repositories, services, utils."""
```

### [src/collections_app/core/db/__init__.py](src/collections_app/core/db/__init__.py)

```python
"""Conexión SQLite y sistema de migraciones."""
```

### [src/collections_app/core/db/connection.py](src/collections_app/core/db/connection.py)

```python
"""Manejo de conexiones SQLite."""

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
    """Context manager para transacciones con rollback automático.

    Uso:
        with transaction(conn):
            conn.execute("INSERT ...")
            conn.execute("UPDATE ...")
        # commit automático si no hubo excepción
    """
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
"""Sistema simple de migraciones de schema."""

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
        # Tabla no existe → schema vacío
        return 0


def run_migrations(conn: sqlite3.Connection, schema_dir: Path | None = None) -> int:
    """Aplica todas las migraciones pendientes.

    Args:
        conn: conexión SQLite.
        schema_dir: directorio con los SQLs. Si None, usa get_schema_dir().

    Returns:
        Versión final del schema.
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

    logger.info("Aplicando %d migraciones (de v%d a v%d)", len(pending), current, pending[-1][0])

    for version, path in pending:
        logger.info("Aplicando migración %03d: %s", version, path.name)
        sql = path.read_text(encoding="utf-8")
        conn.executescript(sql)
        # La migración debe insertar su propio INSERT INTO schema_version
        # Verificar que efectivamente quedó registrada
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

### [src/collections_app/core/db/scripts/__init__.py](src/collections_app/core/db/scripts/__init__.py)

_(archivo vacío)_

### [src/collections_app/core/db/scripts/cleanup_orphans.py](src/collections_app/core/db/scripts/cleanup_orphans.py)

```python
"""Limpia registros huérfanos de colecciones borradas.

Si en algún momento se ejecutó `DELETE FROM collections` sin tener el
PRAGMA `foreign_keys=ON` activado (típicamente desde el shell sqlite3
o un script externo), las cards/inventory/transactions de esa
colección quedaron huérfanas. Este script las elimina.

Las conexiones que abre `create_connection()` en este proyecto siempre
prenden el pragma, así que el problema no se reproduce desde la app.

Uso:
    python -m collections_app.core.db.scripts.cleanup_orphans
"""

import logging

from collections_app.core.db.connection import create_connection, transaction
from collections_app.core.utils.logging_setup import setup_logging
from collections_app.core.utils.paths import get_database_path

logger = logging.getLogger(__name__)


def cleanup_orphans(db_path: str | None = None) -> dict[str, int]:
    """Elimina cards/inventory/transactions huérfanas.

    Args:
        db_path: path a la DB. Si None, usa la default del usuario.

    Returns:
        Dict con la cuenta de filas eliminadas por tabla.
    """
    path = db_path or str(get_database_path())
    conn = create_connection(path)
    deleted: dict[str, int] = {}
    try:
        with transaction(conn):
            for table, fk_cols in (
                # `cards` cuelga directo de `collections`
                ("cards", "collection_id"),
                # `inventory` cuelga de `cards`; basta con orphans en collection_id
                ("inventory", "collection_id"),
                # `transactions` no tiene CASCADE — se acumulan huérfanos
                ("transactions", "collection_id"),
                # `card_images` (migración 003) cascadea desde cards, pero
                # si el bug ocurrió antes de migrar, podría tener huérfanos
                ("card_images", "collection_id"),
            ):
                cur = conn.execute(
                    f"DELETE FROM {table} "  # noqa: S608 — table whitelist arriba
                    f"WHERE {fk_cols} NOT IN (SELECT collection_id FROM collections)"
                )
                deleted[table] = cur.rowcount
                logger.info("%s: %d filas huérfanas eliminadas", table, cur.rowcount)
    finally:
        conn.close()
    return deleted


def main() -> int:
    setup_logging(level=logging.INFO)
    deleted = cleanup_orphans()
    print("=== Limpieza de huérfanos ===")
    for table, n in deleted.items():
        print(f"  {table}: {n} filas")
    print("Listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### [src/collections_app/core/models/__init__.py](src/collections_app/core/models/__init__.py)

```python
"""Modelos de dominio (dataclasses inmutables)."""

from collections_app.core.models.card import Card
from collections_app.core.models.card_image import CardImage
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.models.exchange import (
    ComparisonResult,
    ExchangeCard,
    ExchangeFile,
    ExchangeSession,
)
from collections_app.core.models.inventory_item import InventoryItem
from collections_app.core.models.transaction import OperationType, Transaction

__all__ = [
    "Card",
    "CardImage",
    "CodeHeader",
    "CodeLine",
    "Collection",
    "ComparisonResult",
    "ExchangeCard",
    "ExchangeFile",
    "ExchangeSession",
    "InventoryItem",
    "OperationType",
    "Transaction",
]
```

### [src/collections_app/core/models/card.py](src/collections_app/core/models/card.py)

```python
"""Modelo Card: una entrada del catálogo de una colección."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    """Card del catálogo (PK compuesta collection+code+number).

    Attributes:
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG"). Si la colección no
            requiere código, suele usarse uno vacío o un placeholder.
        card_number: número correlativo dentro del code_id.
        card_name: nombre legible (ej. "Lionel Messi").
    """

    collection_id: int
    code_id: str
    card_number: int
    card_name: str

    @property
    def card_key(self) -> str:
        """Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1')."""
        return f"{self.code_id}-{self.card_number}"
```

### [src/collections_app/core/models/card_image.py](src/collections_app/core/models/card_image.py)

```python
"""Modelo CardImage: tracking de imágenes generadas por card."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CardImage:
    """Registro de la imagen generada para una card.

    Una card tiene exactamente una entrada en `card_images` (PK compuesta
    igual que `cards`). Si todavía no se procesó, no aparece — usar el
    repo `get_pending(collection_id)` para listar las cards sin imagen.

    Attributes:
        collection_id: FK a la Collection contenedora.
        code_id: subdivisión por código (ej. "ARG").
        card_number: número correlativo dentro del code_id.
        found_photo: True si la imagen final usa una foto real,
            False si quedó como placeholder.
        image_source: fuente de la imagen ("wikipedia", "duckduckgo",
            "google", "placeholder", "cache") o None si no se sabe.
        image_path: path al PNG generado, o None si no se grabó.
        generated_at: ISO datetime UTC de la generación, o None.
    """

    collection_id: int
    code_id: str
    card_number: int
    found_photo: bool
    image_source: str | None = None
    image_path: str | None = None
    generated_at: str | None = None
```

### [src/collections_app/core/models/code_header.py](src/collections_app/core/models/code_header.py)

```python
"""Modelo CodeHeader: universo de códigos (ej. "Países FIFA", "Sets de Magic")."""

from dataclasses import dataclass


@dataclass(frozen=True)
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

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeLine:
    """Línea de código asociada a un header (PK compuesta header+code).

    Attributes:
        code_header_id: FK al CodeHeader contenedor.
        code_id: identificador del código (ej. "ARG", "MR"). Texto libre con
            longitud máxima validada por `CodeHeader.code_max_length`.
        code_name: descripción legible del código (ej. "Argentina", "Mirage").
        code_order: posición para ordenar manualmente dentro del header.
            Lower = primero. Default 0 (alfabético si no se configura).
    """

    code_header_id: int
    code_id: str
    code_name: str
    code_order: int = 0
```

### [src/collections_app/core/models/collection.py](src/collections_app/core/models/collection.py)

```python
"""Modelo Collection: una colección configurada de cards."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Collection:
    """Representa una colección a juntar (catálogo de cards).

    Attributes:
        collection_id: PK auto-incremental. None si aún no fue persistido.
        collection_name: nombre único de la colección.
        card_count: cantidad total esperada de cards.
        requires_code: si True, las cards de la colección se subdividen por code_id.
        code_field_name: etiqueta visible del campo de código en la UI (ej. "Set").
        code_header_id: FK al CodeHeader que define el universo de códigos.
        is_premium: si True, requiere licencia para usar.
        license_key_required: hash de la key requerida (None si free).
        album_columns: cards por fila en el PDF álbum (default 3).
        album_rows: filas por página en el PDF álbum (default 4).
        album_orientation: 'portrait' o 'landscape' — algunas colecciones
            tienen cards horizontales y necesitan landscape (default portrait).
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

### [src/collections_app/core/models/exchange.py](src/collections_app/core/models/exchange.py)

```python
"""Modelos para el sistema de comparación e intercambio de álbumes.

Estos modelos NO se persisten en la DB — son DTOs in-memory + payload del
archivo `.colexchange`. La DB solo se entera del intercambio cuando se
ejecuta (vía `InventoryService.add_card` / `remove_card`) y cuando se
bloquea (vía `InventoryRepository.lock` / `unlock_all`).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExchangeCard:
    """Una carta dentro de un archivo de intercambio.

    `quantity` es 0 cuando la carta está en `missing` (faltante del
    usuario) o ≥1 cuando está en `duplicates` (cantidad disponible
    para regalar = quantity - 1, pero acá guardamos la cantidad total
    visible en el archivo para que el otro usuario sepa el rango).
    """

    code_id: str
    card_number: int
    card_name: str
    quantity: int = 0


@dataclass
class ExchangeFile:
    """Contenido del archivo `.colexchange` generado por un usuario.

    `checksum` es un SHA256 truncado calculado sobre los campos estables
    (NO incluye `generated_at` para que el checksum sea reproducible).
    Se usa para detectar archivos manipulados manualmente.
    """

    app: str  # "CollectionsApp"
    version: str  # "1.0"
    collection_id: int
    collection_name: str
    generated_at: str  # UTC ISO
    missing: list[ExchangeCard] = field(default_factory=list)
    duplicates: list[ExchangeCard] = field(default_factory=list)
    checksum: str = ""


@dataclass
class ComparisonResult:
    """Resultado de comparar dos `ExchangeFile`.

    Calculado siempre desde la perspectiva del usuario "yo" (`my_file`):
    - `i_need`: mis faltantes que el otro tiene como repetidas.
    - `i_can_offer`: mis repetidas que al otro le faltan.
    """

    i_need: list[ExchangeCard] = field(default_factory=list)
    i_can_offer: list[ExchangeCard] = field(default_factory=list)


@dataclass
class ExchangeSession:
    """Estado in-memory de un intercambio en proceso de ejecución.

    Lo construye el ExchangeView a partir del ComparisonResult + las
    decisiones del usuario (qué chequear/desmarcar, qué cartas extra
    agregar manualmente). `locked_items` registra qué cartas fueron
    bloqueadas en inventario para poder revertirlas si se cancela.
    """

    to_give: list[ExchangeCard] = field(default_factory=list)
    to_receive: list[ExchangeCard] = field(default_factory=list)
    locked_items: list[ExchangeCard] = field(default_factory=list)
```

### [src/collections_app/core/models/inventory_item.py](src/collections_app/core/models/inventory_item.py)

```python
"""Modelo InventoryItem: cantidad poseída por el usuario de una Card específica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryItem:
    """Stock del usuario para una Card.

    Attributes:
        collection_id: FK a la Collection.
        code_id: parte de la PK compuesta de Card.
        card_number: parte de la PK compuesta de Card.
        quantity: cantidad poseída total. 0 = no tiene; >1 = duplicados.
        image_path: path al archivo de imagen subido por el usuario.
        locked: cantidad reservada para un intercambio en curso. Las
            cartas bloqueadas siguen contando para `quantity` pero NO
            están disponibles para una nueva baja/intercambio. Se
            resetea a 0 al cancelar o ejecutar el intercambio.
    """

    collection_id: int
    code_id: str
    card_number: int
    quantity: int = 0
    image_path: str | None = None
    locked: int = 0

    @property
    def is_owned(self) -> bool:
        """True si el usuario tiene al menos una copia."""
        return self.quantity > 0

    @property
    def has_duplicates(self) -> bool:
        """True si el usuario tiene más de una copia (sin descontar locked)."""
        return self.quantity > 1

    @property
    def available_quantity(self) -> int:
        """Cantidad disponible para nuevas operaciones = quantity - locked."""
        return max(0, self.quantity - self.locked)

    @property
    def has_available_duplicates(self) -> bool:
        """True si tiene >1 copias DESCONTANDO las bloqueadas."""
        return self.available_quantity > 1
```

### [src/collections_app/core/models/transaction.py](src/collections_app/core/models/transaction.py)

```python
"""Modelo Transaction: bitácora de altas/bajas de inventario."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OperationType(StrEnum):
    """Tipo de operación registrada en la bitácora."""

    ALTA = "alta"
    BAJA = "baja"


@dataclass(frozen=True)
class Transaction:
    """Registro inmutable de un movimiento sobre el inventario.

    Attributes:
        transaction_id: PK auto-incremental. None si aún no fue persistido.
        collection_id: FK a la Collection afectada.
        code_id: parte de la PK compuesta de Card.
        card_number: parte de la PK compuesta de Card.
        operation: alta o baja (ver OperationType).
        quantity: unidades movidas (siempre positivo; el signo lo da `operation`).
        transaction_date: timestamp del movimiento.
    """

    transaction_id: int | None
    collection_id: int
    code_id: str
    card_number: int
    operation: OperationType
    quantity: int
    transaction_date: datetime
```

### [src/collections_app/core/repositories/__init__.py](src/collections_app/core/repositories/__init__.py)

```python
"""Repositorios: una clase por tabla, encapsulan SQL."""

from collections_app.core.repositories.base import BaseRepository
from collections_app.core.repositories.card_images_repo import CardImagesRepository
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.codes_headers_repo import CodesHeadersRepository
from collections_app.core.repositories.codes_lines_repo import CodesLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.settings_repo import SettingsRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository

__all__ = [
    "BaseRepository",
    "CardImagesRepository",
    "CardsRepository",
    "CodesHeadersRepository",
    "CodesLinesRepository",
    "CollectionsRepository",
    "InventoryRepository",
    "SettingsRepository",
    "TransactionsRepository",
]
```

### [src/collections_app/core/repositories/base.py](src/collections_app/core/repositories/base.py)

```python
"""Clase base abstracta para todos los repositorios."""

import sqlite3
from abc import ABC


class BaseRepository(ABC):  # noqa: B024 — marker del patrón Repository, no agrega API abstracta
    """Repository base. Todas las repos reciben una conexión SQLite.

    Las repositories NO crean la conexión, la reciben (inversion of control).
    Esto permite usar la misma conexión para varias operaciones en una
    transacción coordinada por el caller.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
```

### [src/collections_app/core/repositories/card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)

```python
"""Repository para la tabla card_images."""

import sqlite3

from collections_app.core.models import Card, CardImage
from collections_app.core.repositories.base import BaseRepository


def _row_to_card_image(row: sqlite3.Row) -> CardImage:
    return CardImage(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        found_photo=bool(row["found_photo"]),
        image_source=row["image_source"],
        image_path=row["image_path"],
        generated_at=row["generated_at"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardImagesRepository(BaseRepository):
    """Tracking de imágenes generadas por card.

    Cada card tiene como mucho una fila acá. Si no aparece, todavía no
    se procesó (la pipeline la consideraría "pending"). Si aparece con
    `found_photo=False`, salió placeholder y se puede reintentar.
    """

    def upsert(self, image: CardImage) -> None:
        """Inserta o actualiza el tracking de una card."""
        self.conn.execute(
            """
            INSERT INTO card_images (
                collection_id, code_id, card_number,
                found_photo, image_source, image_path, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET
                found_photo = excluded.found_photo,
                image_source = excluded.image_source,
                image_path = excluded.image_path,
                generated_at = excluded.generated_at
            """,
            (
                image.collection_id,
                image.code_id,
                image.card_number,
                int(image.found_photo),
                image.image_source,
                image.image_path,
                image.generated_at,
            ),
        )

    def get(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> CardImage | None:
        """Retorna la entry por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ? AND code_id = ? AND card_number = ?
            """,
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card_image(row) if row else None

    def list_by_collection(self, collection_id: int) -> list[CardImage]:
        """Todas las imágenes registradas de una colección."""
        rows = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ?
            ORDER BY code_id, card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card_image(r) for r in rows]

    def get_pending(self, collection_id: int) -> list[Card]:
        """Cards que todavía no tienen imagen generada (no aparecen en card_images)."""
        rows = self.conn.execute(
            """
            SELECT c.collection_id, c.code_id, c.card_number, c.card_name
            FROM cards c
            LEFT JOIN card_images i
                ON c.collection_id = i.collection_id
                AND c.code_id = i.code_id
                AND c.card_number = i.card_number
            WHERE c.collection_id = ? AND i.collection_id IS NULL
            ORDER BY c.code_id, c.card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_placeholders(self, collection_id: int) -> list[CardImage]:
        """Cards generadas pero con `found_photo=False` (placeholder)."""
        rows = self.conn.execute(
            """
            SELECT collection_id, code_id, card_number,
                   found_photo, image_source, image_path, generated_at
            FROM card_images
            WHERE collection_id = ? AND found_photo = 0
            ORDER BY code_id, card_number
            """,
            (collection_id,),
        ).fetchall()
        return [_row_to_card_image(r) for r in rows]

    def get_found_count(self, collection_id: int) -> int:
        """Cuántas cards tienen `found_photo=True`."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM card_images " "WHERE collection_id = ? AND found_photo = 1",
            (collection_id,),
        ).fetchone()
        return int(row["n"]) if row else 0

    def get_total_generated(self, collection_id: int) -> int:
        """Cuántas cards tienen alguna imagen (real o placeholder)."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS n FROM card_images WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        return int(row["n"]) if row else 0

    def delete(self, collection_id: int, code_id: str, card_number: int) -> None:
        """Borra el tracking de una card (forzando que vuelva a "pending")."""
        self.conn.execute(
            "DELETE FROM card_images "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        )
```

### [src/collections_app/core/repositories/cards_repo.py](src/collections_app/core/repositories/cards_repo.py)

```python
"""Repository para la tabla cards."""

import sqlite3
from typing import TypedDict

from collections_app.core.models import Card
from collections_app.core.repositories.base import BaseRepository


class CodeStats(TypedDict):
    """Stats agregadas por código (ver `CardsRepository.get_stats_by_code`)."""

    code_id: str
    code_name: str
    total: int
    owned: int
    percentage: float


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class CardsRepository(BaseRepository):
    """CRUD sobre `cards`."""

    def list_by_collection(self, collection_id: int) -> list[Card]:
        """Retorna todas las cards de una colección ordenadas por (code_id, card_number)."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get(self, collection_id: int, code_id: str, card_number: int) -> Card | None:
        """Retorna la card por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_card(row) if row else None

    def upsert(self, card: Card) -> Card:
        """Inserta o actualiza la card según exista."""
        self.conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "card_name = excluded.card_name",
            (card.collection_id, card.code_id, card.card_number, card.card_name),
        )
        return card

    def delete(self, collection_id: int, code_id: str, card_number: int) -> bool:
        """Borra la card. Cascade borra el inventory item asociado."""
        cursor = self.conn.execute(
            "DELETE FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        )
        return cursor.rowcount > 0

    def count_by_collection(self, collection_id: int) -> int:
        """Cuenta cuántas cards tiene una colección."""
        row = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE collection_id = ?",
            (collection_id,),
        ).fetchone()
        count: int = row["c"]
        return count

    def find_by_number(self, collection_id: int, card_number: int) -> list[Card]:
        """Busca cards en la colección por número, sin filtrar por code_id.

        Útil cuando `Collection.requires_code=False` y el usuario solo
        ingresa el número. Retorna lista para soportar el caso edge de
        múltiples cards con el mismo número en distintos códigos.
        """
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND card_number = ? "
            "ORDER BY code_id",
            (collection_id, card_number),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def list_by_code(self, collection_id: int, code_id: str) -> list[Card]:
        """Retorna las cards de una colección filtradas por code_id."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, card_name FROM cards "
            "WHERE collection_id = ? AND code_id = ? "
            "ORDER BY card_number",
            (collection_id, code_id),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def get_stats_by_code(self, collection_id: int) -> list[CodeStats]:
        """Stats agregadas por code_id de la colección.

        Para cada código del catálogo: total de cards, cuántas tiene el
        usuario (quantity > 0), porcentaje. Ordenado por `code_order` del
        header (luego alfabético) para que coincida con el orden visible.

        Returns:
            list[dict] con keys: code_id, code_name, total, owned, percentage.
        """
        rows = self.conn.execute(
            "SELECT c.code_id AS code_id, "
            "       COALESCE(cl.code_name, c.code_id) AS code_name, "
            "       COALESCE(cl.code_order, 0) AS code_order, "
            "       COUNT(*) AS total, "
            "       SUM(CASE WHEN i.quantity > 0 THEN 1 ELSE 0 END) AS owned "
            "FROM cards c "
            "LEFT JOIN inventory i "
            "  ON c.collection_id = i.collection_id "
            " AND c.code_id = i.code_id "
            " AND c.card_number = i.card_number "
            "LEFT JOIN codes_lines cl "
            "  ON cl.code_id = c.code_id "
            " AND cl.code_header_id = ("
            "       SELECT code_header_id FROM collections WHERE collection_id = ?"
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

    def bulk_upsert(self, cards: list[Card]) -> int:
        """Inserta o actualiza muchas cards en un batch.

        Usa `executemany` para performance. NO commitea.

        Returns:
            Cantidad de cards procesadas.
        """
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
```

### [src/collections_app/core/repositories/codes_headers_repo.py](src/collections_app/core/repositories/codes_headers_repo.py)

```python
"""Repository para la tabla codes_headers."""

import sqlite3

from collections_app.core.models import CodeHeader
from collections_app.core.repositories.base import BaseRepository


def _row_to_header(row: sqlite3.Row) -> CodeHeader:
    return CodeHeader(
        code_header_id=row["code_header_id"],
        code_header_name=row["code_header_name"],
        code_max_length=row["code_max_length"],
    )


class CodesHeadersRepository(BaseRepository):
    """CRUD sobre `codes_headers`."""

    def list_all(self) -> list[CodeHeader]:
        """Retorna todos los headers ordenados por nombre."""
        rows = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers ORDER BY code_header_name"
        ).fetchall()
        return [_row_to_header(r) for r in rows]

    def get_by_id(self, code_header_id: int) -> CodeHeader | None:
        """Retorna el header por id, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_id = ?",
            (code_header_id,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def get_by_name(self, name: str) -> CodeHeader | None:
        """Retorna el header por nombre exacto, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_header_name, code_max_length "
            "FROM codes_headers WHERE code_header_name = ?",
            (name,),
        ).fetchone()
        return _row_to_header(row) if row else None

    def create(self, header: CodeHeader) -> CodeHeader:
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

    def update(self, header: CodeHeader) -> CodeHeader:
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

    def delete(self, code_header_id: int) -> bool:
        """Borra un header. Cascade borra `codes_lines` asociadas.

        Returns:
            True si se borró efectivamente, False si no existía.
        """
        cursor = self.conn.execute(
            "DELETE FROM codes_headers WHERE code_header_id = ?",
            (code_header_id,),
        )
        return cursor.rowcount > 0
```

### [src/collections_app/core/repositories/codes_lines_repo.py](src/collections_app/core/repositories/codes_lines_repo.py)

```python
"""Repository para la tabla codes_lines."""

import sqlite3

from collections_app.core.models import CodeLine
from collections_app.core.repositories.base import BaseRepository


def _row_to_line(row: sqlite3.Row) -> CodeLine:
    return CodeLine(
        code_header_id=row["code_header_id"],
        code_id=row["code_id"],
        code_name=row["code_name"],
        code_order=row["code_order"],
    )


class CodesLinesRepository(BaseRepository):
    """CRUD sobre `codes_lines` con validación de longitud contra el header."""

    def list_by_header(self, code_header_id: int) -> list[CodeLine]:
        """Retorna las líneas de un header ordenadas por (code_order, code_id)."""
        rows = self.conn.execute(
            "SELECT code_header_id, code_id, code_name, code_order FROM codes_lines "
            "WHERE code_header_id = ? ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [_row_to_line(r) for r in rows]

    def get(self, code_header_id: int, code_id: str) -> CodeLine | None:
        """Retorna la línea por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT code_header_id, code_id, code_name, code_order FROM codes_lines "
            "WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        ).fetchone()
        return _row_to_line(row) if row else None

    def upsert(self, line: CodeLine) -> CodeLine:
        """Inserta o actualiza la línea según exista.

        Valida que `len(code_id)` no exceda `code_max_length` del header
        contenedor.

        Raises:
            ValueError: si el code_id excede el max_length del header, o si el
                header no existe.
        """
        max_len_row = self.conn.execute(
            "SELECT code_max_length FROM codes_headers WHERE code_header_id = ?",
            (line.code_header_id,),
        ).fetchone()
        if max_len_row is None:
            raise ValueError(f"code_header_id {line.code_header_id} no existe")
        if len(line.code_id) > max_len_row["code_max_length"]:
            raise ValueError(
                f"code_id '{line.code_id}' excede max_length {max_len_row['code_max_length']}"
            )

        self.conn.execute(
            "INSERT INTO codes_lines (code_header_id, code_id, code_name, code_order) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(code_header_id, code_id) DO UPDATE SET "
            "code_name = excluded.code_name, code_order = excluded.code_order",
            (line.code_header_id, line.code_id, line.code_name, line.code_order),
        )
        return line

    def delete(self, code_header_id: int, code_id: str) -> bool:
        """Borra una línea. Retorna True si se borró efectivamente."""
        cursor = self.conn.execute(
            "DELETE FROM codes_lines WHERE code_header_id = ? AND code_id = ?",
            (code_header_id, code_id),
        )
        return cursor.rowcount > 0

    def list_codes_only(self, code_header_id: int) -> list[str]:
        """Solo los IDs de los códigos de un header (útil para autocomplete)."""
        rows = self.conn.execute(
            "SELECT code_id FROM codes_lines WHERE code_header_id = ? "
            "ORDER BY code_order, code_id",
            (code_header_id,),
        ).fetchall()
        return [r["code_id"] for r in rows]

    def reorder(self, code_header_id: int, ordered_code_ids: list[str]) -> None:
        """Reasigna code_order según el índice (1-based) en la lista.

        Útil para drag&drop: pasás los code_id en el orden deseado y este
        método actualiza `code_order` con 1, 2, 3, ... respectivamente.
        Los códigos no incluidos en la lista quedan con su `code_order` actual.
        """
        for i, cid in enumerate(ordered_code_ids, start=1):
            self.conn.execute(
                "UPDATE codes_lines SET code_order = ? " "WHERE code_header_id = ? AND code_id = ?",
                (i, code_header_id, cid),
            )
```

### [src/collections_app/core/repositories/collections_repo.py](src/collections_app/core/repositories/collections_repo.py)

```python
"""Repository para la tabla collections."""

import sqlite3

from collections_app.core.models import Collection
from collections_app.core.repositories.base import BaseRepository


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


_SELECT_COLS = (
    "collection_id, collection_name, card_count, requires_code, "
    "code_field_name, code_header_id, is_premium, license_key_required, "
    "album_columns, album_rows, album_orientation"
)


class CollectionsRepository(BaseRepository):
    """CRUD sobre `collections`."""

    def list_all(self) -> list[Collection]:
        """Retorna todas las colecciones ordenadas por nombre."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections ORDER BY collection_name"  # noqa: S608
        ).fetchall()
        return [_row_to_collection(r) for r in rows]

    def get_by_id(self, collection_id: int) -> Collection | None:
        """Retorna la colección por id, o None si no existe."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections WHERE collection_id = ?",  # noqa: S608
            (collection_id,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def get_by_name(self, name: str) -> Collection | None:
        """Retorna la colección por nombre exacto, o None si no existe."""
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM collections WHERE collection_name = ?",  # noqa: S608
            (name,),
        ).fetchone()
        return _row_to_collection(row) if row else None

    def create(self, collection: Collection) -> Collection:
        """Inserta y retorna la colección con `collection_id` poblado."""
        cursor = self.conn.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, requires_code, code_field_name, "
            " code_header_id, is_premium, license_key_required, "
            " album_columns, album_rows, album_orientation) "
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

    def update(self, collection: Collection) -> Collection:
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

    def delete(self, collection_id: int) -> bool:
        """Borra la colección. Cascade borra cards e inventory."""
        cursor = self.conn.execute(
            "DELETE FROM collections WHERE collection_id = ?",
            (collection_id,),
        )
        return cursor.rowcount > 0
```

### [src/collections_app/core/repositories/inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)

```python
"""Repository para la tabla inventory."""

import sqlite3

from collections_app.core.models import Card, InventoryItem
from collections_app.core.repositories.base import BaseRepository


def _row_to_item(row: sqlite3.Row) -> InventoryItem:
    return InventoryItem(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        quantity=row["quantity"],
        image_path=row["image_path"],
        locked=row["locked"],
    )


def _row_to_card(row: sqlite3.Row) -> Card:
    return Card(
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        card_name=row["card_name"],
    )


class InventoryRepository(BaseRepository):
    """CRUD y queries específicas sobre `inventory`."""

    def get(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
    ) -> InventoryItem | None:
        """Retorna el inventario por PK compuesta, o None si no existe."""
        row = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (collection_id, code_id, card_number),
        ).fetchone()
        return _row_to_item(row) if row else None

    def list_by_collection(self, collection_id: int) -> list[InventoryItem]:
        """Lista todo el inventario de una colección."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory WHERE collection_id = ? "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_owned(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 0."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 0 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_top_duplicates(
        self,
        collection_id: int,
        limit: int = 10,
    ) -> list[InventoryItem]:
        """Las cards con mayor cantidad (quantity > 1), ordenadas desc."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY quantity DESC, code_id, card_number "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_duplicates(self, collection_id: int) -> list[InventoryItem]:
        """Solo los items con quantity > 1."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND quantity > 1 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_locked(self, collection_id: int) -> list[InventoryItem]:
        """Items con locked > 0 (reservados para un intercambio en curso)."""
        rows = self.conn.execute(
            "SELECT collection_id, code_id, card_number, quantity, image_path, locked "
            "FROM inventory "
            "WHERE collection_id = ? AND locked > 0 "
            "ORDER BY code_id, card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def list_missing(self, collection_id: int) -> list[Card]:
        """Cards que el usuario aún no tiene (sin inventory o quantity=0)."""
        rows = self.conn.execute(
            "SELECT c.collection_id, c.code_id, c.card_number, c.card_name "
            "FROM cards c "
            "LEFT JOIN inventory i "
            "  ON c.collection_id = i.collection_id "
            " AND c.code_id = i.code_id "
            " AND c.card_number = i.card_number "
            "WHERE c.collection_id = ? "
            "  AND (i.quantity IS NULL OR i.quantity = 0) "
            "ORDER BY c.code_id, c.card_number",
            (collection_id,),
        ).fetchall()
        return [_row_to_card(r) for r in rows]

    def upsert(self, item: InventoryItem) -> InventoryItem:
        """Crea o actualiza el inventory item.

        IMPORTANTE: este upsert NO toca la columna `locked` para no
        pisar reservas de intercambio en curso. Para mover el locked,
        usar `lock` / `unlock` / `unlock_all`.
        """
        self.conn.execute(
            "INSERT INTO inventory "
            "(collection_id, code_id, card_number, quantity, image_path, locked) "
            "VALUES (?, ?, ?, ?, ?, COALESCE("
            "  (SELECT locked FROM inventory "
            "    WHERE collection_id=? AND code_id=? AND card_number=?), 0)) "
            "ON CONFLICT(collection_id, code_id, card_number) DO UPDATE SET "
            "quantity = excluded.quantity, image_path = excluded.image_path",
            (
                item.collection_id,
                item.code_id,
                item.card_number,
                item.quantity,
                item.image_path,
                item.collection_id,
                item.code_id,
                item.card_number,
            ),
        )
        return item

    def adjust_quantity(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        delta: int,
    ) -> InventoryItem:
        """Suma `delta` a la quantity (delta puede ser negativo).

        Si el item no existe, se crea con `quantity = max(0, delta)`.

        Raises:
            ValueError: si el resultado quedaría en negativo.
        """
        existing = self.get(collection_id, code_id, card_number)
        current_qty = existing.quantity if existing else 0
        new_qty = current_qty + delta

        if new_qty < 0:
            raise ValueError(
                f"Cantidad resultante negativa para ({collection_id}, {code_id}, "
                f"{card_number}): actual={current_qty}, delta={delta}"
            )

        item = InventoryItem(
            collection_id=collection_id,
            code_id=code_id,
            card_number=card_number,
            quantity=new_qty,
            image_path=existing.image_path if existing else None,
            locked=existing.locked if existing else 0,
        )
        return self.upsert(item)

    def set_image(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        image_path: str,
    ) -> None:
        """Setea el image_path del inventory item, creándolo con quantity=0 si no existe."""
        existing = self.get(collection_id, code_id, card_number)
        quantity = existing.quantity if existing else 0
        self.upsert(
            InventoryItem(
                collection_id=collection_id,
                code_id=code_id,
                card_number=card_number,
                quantity=quantity,
                image_path=image_path,
            )
        )

    # ------------------------------------------------------------------
    # Bloqueo para intercambios
    # ------------------------------------------------------------------

    def lock(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        amount: int = 1,
    ) -> InventoryItem:
        """Incrementa `locked` en `amount`. NO modifica `quantity`.

        Si el item no existe, se crea con quantity=0 y locked=amount —
        caso usado al agregar manualmente una carta a "Entrego" en el
        ExchangeView (la carta saldrá del inventario al ejecutar).
        """
        if amount <= 0:
            raise ValueError(f"amount debe ser > 0 (recibido: {amount})")
        existing = self.get(collection_id, code_id, card_number)
        if existing is None:
            self.conn.execute(
                "INSERT INTO inventory "
                "(collection_id, code_id, card_number, quantity, image_path, locked) "
                "VALUES (?, ?, ?, 0, NULL, ?)",
                (collection_id, code_id, card_number, amount),
            )
        else:
            self.conn.execute(
                "UPDATE inventory SET locked = locked + ? "
                "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
                (amount, collection_id, code_id, card_number),
            )
        result = self.get(collection_id, code_id, card_number)
        assert result is not None
        return result

    def unlock(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        amount: int = 1,
    ) -> InventoryItem:
        """Decrementa `locked` en `amount`. Mínimo 0 (clamp)."""
        if amount <= 0:
            raise ValueError(f"amount debe ser > 0 (recibido: {amount})")
        self.conn.execute(
            "UPDATE inventory SET locked = MAX(0, locked - ?) "
            "WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (amount, collection_id, code_id, card_number),
        )
        result = self.get(collection_id, code_id, card_number)
        if result is None:
            # No había nada, retornamos un item sintético con todo en 0
            # para mantener la firma consistente.
            return InventoryItem(
                collection_id=collection_id,
                code_id=code_id,
                card_number=card_number,
            )
        return result

    def unlock_all(self, collection_id: int) -> int:
        """Resetea locked=0 para toda la colección. Retorna filas afectadas."""
        cursor = self.conn.execute(
            "UPDATE inventory SET locked = 0 " "WHERE collection_id = ? AND locked > 0",
            (collection_id,),
        )
        return cursor.rowcount
```

### [src/collections_app/core/repositories/settings_repo.py](src/collections_app/core/repositories/settings_repo.py)

```python
"""Repository simple key/value para la tabla app_settings."""

from collections_app.core.repositories.base import BaseRepository


class SettingsRepository(BaseRepository):
    """Acceso clave/valor a `app_settings`."""

    def get(self, key: str) -> str | None:
        """Retorna el valor de `key`, o None si no existe."""
        row = self.conn.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = ?",
            (key,),
        ).fetchone()
        if row is None:
            return None
        value: str | None = row["setting_value"]
        return value

    def set(self, key: str, value: str) -> None:
        """Inserta o actualiza el valor de `key`."""
        self.conn.execute(
            "INSERT INTO app_settings (setting_key, setting_value) VALUES (?, ?) "
            "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
            (key, value),
        )

    def delete(self, key: str) -> bool:
        """Borra la entrada. Retorna True si se borró efectivamente."""
        cursor = self.conn.execute(
            "DELETE FROM app_settings WHERE setting_key = ?",
            (key,),
        )
        return cursor.rowcount > 0

    def get_int(self, key: str) -> int | None:
        """Retorna el valor parseado como int, o None si no existe o no es int válido."""
        raw = self.get(key)
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError:
            return None
```

### [src/collections_app/core/repositories/transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)

```python
"""Repository para la tabla transactions."""

import sqlite3
from datetime import datetime

from collections_app.core.models import OperationType, Transaction
from collections_app.core.repositories.base import BaseRepository
from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    parse_db_datetime,
)


def _row_to_transaction(row: sqlite3.Row) -> Transaction:
    return Transaction(
        transaction_id=row["transaction_id"],
        collection_id=row["collection_id"],
        code_id=row["code_id"],
        card_number=row["card_number"],
        operation=OperationType(row["operation"]),
        quantity=row["quantity"],
        transaction_date=parse_db_datetime(row["transaction_date"]),
    )


_SELECT_COLS = (
    "transaction_id, collection_id, code_id, card_number, " "operation, quantity, transaction_date"
)


class TransactionsRepository(BaseRepository):
    """Bitácora de operaciones (alta/baja) sobre el inventario."""

    def log(self, txn: Transaction) -> Transaction:
        """Inserta una transacción.

        El `transaction_id` y `transaction_date` del input son ignorados — se
        asignan en la DB.

        Returns:
            La transacción persistida con id y fecha reales.
        """
        cursor = self.conn.execute(
            "INSERT INTO transactions "
            "(collection_id, code_id, card_number, operation, quantity) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                txn.collection_id,
                txn.code_id,
                txn.card_number,
                txn.operation.value,
                txn.quantity,
            ),
        )
        new_id = cursor.lastrowid
        row = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions WHERE transaction_id = ?",  # noqa: S608
            (new_id,),
        ).fetchone()
        return _row_to_transaction(row)

    def list_by_collection(self, collection_id: int, limit: int = 100) -> list[Transaction]:
        """Transacciones de una colección, las más recientes primero."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
            "WHERE collection_id = ? "
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (collection_id, limit),
        ).fetchall()
        return [_row_to_transaction(r) for r in rows]

    def list_by_date_range(
        self,
        start: datetime,
        end: datetime,
        collection_id: int | None = None,
    ) -> list[Transaction]:
        """Transacciones en un rango [start, end] inclusivo, opcionalmente filtradas.

        `start` y `end` se convierten a UTC antes de comparar contra los
        timestamps de la DB (también UTC).
        """
        start_str = format_for_db(start)
        end_str = format_for_db(end)
        if collection_id is None:
            rows = self.conn.execute(
                f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
                "WHERE transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (start_str, end_str),
            ).fetchall()
        else:
            rows = self.conn.execute(
                f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
                "WHERE collection_id = ? AND transaction_date BETWEEN ? AND ? "
                "ORDER BY transaction_date DESC, transaction_id DESC",
                (collection_id, start_str, end_str),
            ).fetchall()
        return [_row_to_transaction(r) for r in rows]

    def list_recent(self, limit: int = 20) -> list[Transaction]:
        """Las N transacciones más recientes globalmente."""
        rows = self.conn.execute(
            f"SELECT {_SELECT_COLS} FROM transactions "  # noqa: S608
            "ORDER BY transaction_date DESC, transaction_id DESC "
            "LIMIT ?",
            (limit,),
        ).fetchall()
        return [_row_to_transaction(r) for r in rows]
```

### [src/collections_app/core/services/__init__.py](src/collections_app/core/services/__init__.py)

```python
"""Servicios: orquestan repositorios para lógica que cruza tablas."""

from collections_app.core.services.album_service import AlbumService
from collections_app.core.services.collections_service import CollectionsService
from collections_app.core.services.exchange_service import (
    EXCHANGE_APP_ID,
    EXCHANGE_EXTENSION,
    EXCHANGE_FORMAT_VERSION,
    ExchangeService,
)
from collections_app.core.services.inventory_service import (
    AmbiguousCardError,
    InventoryService,
)
from collections_app.core.services.license_service import (
    SETTING_KEY_LICENSE_PREFIX,
    LicenseService,
    LicenseValidator,
    LocalHashLicenseValidator,
)
from collections_app.core.services.pdf_generator import (
    AlbumCard,
    DuplicatesReportMode,
    ListReportMode,
    PdfGeneratorResult,
    generate_album_pdf,
    generate_comparison_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
    validate_exchange_pdf_metadata,
)
from collections_app.core.services.profile_service import (
    ProfileInfo,
    ProfileService,
)
from collections_app.core.services.reports_service import (
    ReportsService,
    TransactionWithCard,
)
from collections_app.core.services.settings_service import (
    SETTING_KEY_ACTIVE_COLLECTION,
    SettingsService,
)
from collections_app.core.services.update_service import (
    GitHubUpdateSource,
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)

__all__ = [
    "EXCHANGE_APP_ID",
    "EXCHANGE_EXTENSION",
    "EXCHANGE_FORMAT_VERSION",
    "SETTING_KEY_ACTIVE_COLLECTION",
    "SETTING_KEY_LICENSE_PREFIX",
    "AlbumCard",
    "AlbumService",
    "AmbiguousCardError",
    "CollectionsService",
    "DuplicatesReportMode",
    "ExchangeService",
    "ListReportMode",
    "GitHubUpdateSource",
    "InventoryService",
    "LicenseService",
    "LicenseValidator",
    "LocalHashLicenseValidator",
    "PdfGeneratorResult",
    "ProfileInfo",
    "ProfileService",
    "ReportsService",
    "ServerUpdateSource",
    "SettingsService",
    "TransactionWithCard",
    "UpdateInfo",
    "UpdateService",
    "UpdateSource",
    "generate_album_pdf",
    "generate_comparison_pdf",
    "generate_duplicates_pdf",
    "generate_missing_pdf",
    "generate_owned_pdf",
    "validate_exchange_pdf_metadata",
]
```

### [src/collections_app/core/services/album_service.py](src/collections_app/core/services/album_service.py)

```python
"""Service de álbum: orquesta cards + inventario + nombres de código + imágenes.

Es la capa de **datos** entre la DB y los renderers de PDF. Mantiene
`pdf_generator.py` ignorante del schema/repositorios — solo recibe
`AlbumCard` ya armadas.

Uso típico desde la vista cliente:

    from collections_app.core.services import AlbumService

    service = AlbumService(conn)
    service.generate_album_pdf(collection, output_path)
"""

import logging
import sqlite3
from pathlib import Path

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services.pdf_generator import (
    AlbumCard,
    DuplicatesReportMode,
    ListReportMode,
    PdfGeneratorResult,
    generate_album_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
)
from collections_app.core.utils.paths import find_card_image

logger = logging.getLogger(__name__)


class AlbumService:
    """Carga datos del álbum desde DB y delega la generación al renderer."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Carga de datos (data layer)
    # ------------------------------------------------------------------

    def build_album_cards(self, collection: Collection) -> list[AlbumCard]:
        """Cruza cards con inventario + nombres de código + orden + imágenes.

        Ordenado por `(code_order, code_id, card_number)`: las categorías
        respetan el `CodeLine.code_order` configurado en Admin (no alfabético
        por code_id). El secundario `code_id` desempata casos de igual
        code_order. Las cards sin entrada en inventario quedan con `quantity=0`.
        """
        assert collection.collection_id is not None
        cid: int = collection.collection_id

        cards = CardsRepository(self._conn).list_by_collection(cid)
        inv = {
            (i.code_id, i.card_number): i.quantity
            for i in InventoryRepository(self._conn).list_by_collection(cid)
        }
        # Una sola lectura de codes_lines: nombre + orden por code_id.
        code_meta = self._get_code_meta(collection)

        result: list[AlbumCard] = []
        for card in cards:
            name, order = code_meta.get(card.code_id, (card.code_id, 0))
            qty = inv.get((card.code_id, card.card_number), 0)
            result.append(
                AlbumCard(
                    card=card,
                    quantity=qty,
                    image_path=find_card_image(cid, card.card_number),
                    requires_code=collection.requires_code,
                    code_name=name,
                    code_order=order,
                )
            )
        result.sort(key=lambda ac: (ac.code_order, ac.card.code_id, ac.card.card_number))
        return result

    def get_code_names(self, collection: Collection) -> dict[str, str]:
        """Mapeo `code_id → code_name` desde `codes_lines`.

        Útil para renderear headers de categoría con el nombre humano
        ("ARGENTINA") en vez del id corto ("ARG").
        """
        return {code_id: name for code_id, (name, _) in self._get_code_meta(collection).items()}

    def _get_code_meta(self, collection: Collection) -> dict[str, tuple[str, int]]:
        """Mapeo `code_id → (code_name, code_order)`. Una sola query."""
        lines = CodesLinesRepository(self._conn).list_by_header(collection.code_header_id)
        return {line.code_id: (line.code_name, line.code_order) for line in lines}

    # ------------------------------------------------------------------
    # Wrappers de generación (render layer)
    # ------------------------------------------------------------------

    def generate_album_pdf(self, collection: Collection, output_path: Path) -> PdfGeneratorResult:
        """PDF álbum visual (todas las cards, foto o placeholder)."""
        cards = self.build_album_cards(collection)
        return generate_album_pdf(collection, cards, output_path)

    def generate_missing_pdf(
        self,
        collection: Collection,
        output_path: Path,
        mode: ListReportMode = ListReportMode.FULL,
    ) -> PdfGeneratorResult:
        """PDF lista de cards faltantes (`quantity == 0`)."""
        cards = self.build_album_cards(collection)
        return generate_missing_pdf(collection, cards, output_path, mode=mode)

    def generate_duplicates_pdf(
        self,
        collection: Collection,
        output_path: Path,
        mode: DuplicatesReportMode = DuplicatesReportMode.FULL,
    ) -> PdfGeneratorResult:
        """PDF lista de cards repetidas (`quantity > 1`)."""
        cards = self.build_album_cards(collection)
        return generate_duplicates_pdf(collection, cards, output_path, mode=mode)

    def generate_owned_pdf(self, collection: Collection, output_path: Path) -> PdfGeneratorResult:
        """PDF lista de cards en posesión (`quantity >= 1`)."""
        cards = self.build_album_cards(collection)
        return generate_owned_pdf(collection, cards, output_path)
```

### [src/collections_app/core/services/collections_service.py](src/collections_app/core/services/collections_service.py)

```python
"""Servicio que orquesta operaciones que cruzan collections + codes_headers + cards."""

import sqlite3
from typing import Any

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CodesLinesRepository,
    CollectionsRepository,
)


class CollectionsService:
    """Operaciones de alto nivel sobre `collections`."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._collections = CollectionsRepository(conn)
        self._headers = CodesHeadersRepository(conn)
        self._lines = CodesLinesRepository(conn)
        self._cards = CardsRepository(conn)

    def create_collection_with_validation(self, collection: Collection) -> Collection:
        """Crea una colección validando que el code_header_id exista.

        Raises:
            ValueError: si el `code_header_id` no apunta a un header existente.
        """
        if self._headers.get_by_id(collection.code_header_id) is None:
            raise ValueError(f"code_header_id {collection.code_header_id} no existe")
        return self._collections.create(collection)

    def get_full_collection_info(self, collection_id: int) -> dict[str, Any] | None:
        """Retorna info enriquecida de una colección.

        Returns:
            Dict con `collection`, `code_header`, `num_cards`, `num_codes`,
            o None si la colección no existe.
        """
        collection = self._collections.get_by_id(collection_id)
        if collection is None:
            return None

        header = self._headers.get_by_id(collection.code_header_id)
        num_cards = self._cards.count_by_collection(collection_id)
        num_codes = len(self._lines.list_codes_only(collection.code_header_id))

        return {
            "collection": collection,
            "code_header": header,
            "num_cards": num_cards,
            "num_codes": num_codes,
        }

    def can_be_deleted(self, collection_id: int) -> tuple[bool, str]:
        """Indica si una colección puede borrarse.

        Por ahora siempre permite (el cascade borra cards e inventory).
        Más adelante podemos prohibir si está activa, etc.

        Returns:
            (puede_borrarse, razón_si_no).
        """
        if self._collections.get_by_id(collection_id) is None:
            return False, f"La colección {collection_id} no existe"
        return True, ""
```

### [src/collections_app/core/services/exchange_service.py](src/collections_app/core/services/exchange_service.py)

```python
"""Servicio de comparación e intercambio entre álbumes de dos usuarios.

Flujo end-to-end:

1. Usuario A: `generate_exchange_file()` → escribe `MiAlbum.colexchange`
   con sus faltantes y repetidas. Lo comparte con el usuario B.
2. Usuario B: `load_exchange_file()` → lee + valida el JSON + checksum.
3. `compare(my_file, other_file)` → `ComparisonResult` con cartas
   intercambiables.
4. `lock_cards()` antes de ejecutar (mientras el dialog está abierto).
5. `execute_exchange()` → bajas + altas + unlock dentro de una
   transacción. Rollback si algo falla.
6. Si el usuario cancela: `unlock_all_cards()`.

El checksum del archivo es deliberadamente truncado a 16 chars
(SHA256). No es criptográficamente fuerte — el objetivo es detectar
ediciones casuales, no impedir manipulación maliciosa.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from collections_app.core.db.connection import transaction
from collections_app.core.models import (
    ComparisonResult,
    ExchangeCard,
    ExchangeFile,
    ExchangeSession,
)
from collections_app.core.repositories import (
    CardsRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.services.inventory_service import InventoryService
from collections_app.core.utils.datetime_helpers import utc_now

EXCHANGE_APP_ID = "CollectionsApp"
EXCHANGE_FORMAT_VERSION = "1.0"
EXCHANGE_EXTENSION = ".colexchange"
_CHECKSUM_LEN = 16


class ExchangeService:
    """Genera/lee archivos `.colexchange` y orquesta el intercambio."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Generación de archivo
    # ------------------------------------------------------------------

    def generate_exchange_file(
        self,
        collection_id: int,
        output_path: Path,
    ) -> ExchangeFile:
        """Genera el archivo `.colexchange` con faltantes y repetidas.

        Las repetidas se calculan sobre `available_quantity` (descuenta
        las cartas bloqueadas por un intercambio en curso) — no tendría
        sentido ofrecer al otro usuario una carta que ya prometiste.
        """
        col = CollectionsRepository(self._conn).get_by_id(collection_id)
        if col is None:
            raise ValueError(f"Colección {collection_id} no encontrada")

        cards = {
            (c.code_id, c.card_number): c
            for c in CardsRepository(self._conn).list_by_collection(collection_id)
        }
        inventory = InventoryRepository(self._conn).list_by_collection(collection_id)
        owned = {(i.code_id, i.card_number): i for i in inventory if i.quantity > 0}

        missing: list[ExchangeCard] = []
        duplicates: list[ExchangeCard] = []

        for (code_id, number), card in sorted(cards.items()):
            inv = owned.get((code_id, number))
            if inv is None or inv.available_quantity == 0:
                missing.append(
                    ExchangeCard(
                        code_id=code_id,
                        card_number=number,
                        card_name=card.card_name,
                        quantity=0,
                    )
                )
            elif inv.available_quantity > 1:
                # Lo que el usuario realmente puede ofrecer = disponible - 1
                # (siempre conservamos UNA copia para que el álbum del
                # usuario no quede incompleto después del intercambio).
                oferable = inv.available_quantity - 1
                duplicates.append(
                    ExchangeCard(
                        code_id=code_id,
                        card_number=number,
                        card_name=card.card_name,
                        quantity=oferable,
                    )
                )

        ef = ExchangeFile(
            app=EXCHANGE_APP_ID,
            version=EXCHANGE_FORMAT_VERSION,
            collection_id=collection_id,
            collection_name=col.collection_name,
            generated_at=utc_now().isoformat(),
            missing=missing,
            duplicates=duplicates,
        )
        ef.checksum = self._compute_checksum(ef)
        self._write_file(ef, output_path)
        return ef

    # ------------------------------------------------------------------
    # Importación
    # ------------------------------------------------------------------

    def load_exchange_file(self, path: Path) -> ExchangeFile:
        """Carga + valida un `.colexchange`.

        Raises:
            ValueError: archivo inválido (JSON corrupto), no generado por
                CollectionsApp, o con checksum que no matchea (modificado
                manualmente).
        """
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Archivo inválido: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("Archivo inválido: estructura JSON inesperada")
        if data.get("app") != EXCHANGE_APP_ID:
            raise ValueError("El archivo no fue generado por CollectionsApp")

        stored_checksum = str(data.pop("checksum", ""))
        ef = self._dict_to_exchange_file(data)
        # Re-calculamos sin el checksum guardado y comparamos.
        computed = self._compute_checksum(ef)
        if computed != stored_checksum:
            raise ValueError("El archivo fue modificado externamente (checksum inválido)")
        ef.checksum = stored_checksum
        return ef

    # ------------------------------------------------------------------
    # Comparación
    # ------------------------------------------------------------------

    def compare(
        self,
        my_file: ExchangeFile,
        other_file: ExchangeFile,
    ) -> ComparisonResult:
        """Compara dos `ExchangeFile` y devuelve qué intercambiar."""
        if my_file.collection_id != other_file.collection_id:
            raise ValueError("Los archivos son de colecciones distintas y no se pueden comparar")

        other_duplicates = {(c.code_id, c.card_number) for c in other_file.duplicates}
        other_missing = {(c.code_id, c.card_number) for c in other_file.missing}

        i_need = [c for c in my_file.missing if (c.code_id, c.card_number) in other_duplicates]
        i_can_offer = [c for c in my_file.duplicates if (c.code_id, c.card_number) in other_missing]
        return ComparisonResult(i_need=i_need, i_can_offer=i_can_offer)

    # ------------------------------------------------------------------
    # Bloqueo
    # ------------------------------------------------------------------

    def lock_cards(
        self,
        collection_id: int,
        cards: list[ExchangeCard],
    ) -> None:
        """Bloquea las cartas en inventario (1 por carta). Commit incluido."""
        repo = InventoryRepository(self._conn)
        for card in cards:
            repo.lock(collection_id, card.code_id, card.card_number)
        self._conn.commit()

    def unlock_all_cards(self, collection_id: int) -> None:
        """Resetea locked=0 para toda la colección. Commit incluido."""
        InventoryRepository(self._conn).unlock_all(collection_id)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Ejecución del intercambio
    # ------------------------------------------------------------------

    def execute_exchange(
        self,
        collection_id: int,
        session: ExchangeSession,
    ) -> None:
        """Ejecuta el intercambio dentro de una transacción.

        Pasos:
          1. Baja de cada carta en `to_give` (1 unidad).
          2. Alta de cada carta en `to_receive` (1 unidad).
          3. unlock_all del inventario.

        Si CUALQUIER paso falla, se hace rollback y se propaga la
        excepción. NO commit parcial.
        """
        svc = InventoryService(self._conn)
        with transaction(self._conn):
            for card in session.to_give:
                svc._inventory.adjust_quantity(  # noqa: SLF001
                    collection_id, card.code_id, card.card_number, -1
                )
                self._log_transaction(svc, collection_id, card, alta=False)
            for card in session.to_receive:
                # add_card valida que la carta exista en el catálogo;
                # si la carta a recibir es nueva (no está en cards),
                # primero la creamos para que el FK no rompa.
                self._ensure_card_in_catalog(collection_id, card)
                svc._inventory.adjust_quantity(  # noqa: SLF001
                    collection_id, card.code_id, card.card_number, 1
                )
                self._log_transaction(svc, collection_id, card, alta=True)
            InventoryRepository(self._conn).unlock_all(collection_id)

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _ensure_card_in_catalog(self, collection_id: int, card: ExchangeCard) -> None:
        """Asegura que la carta exista en `cards` antes de la alta.

        Caso de uso: el otro usuario me ofrece una carta que mi catálogo
        ya tiene (por convención los catálogos son simétricos), pero
        protegemos contra ediciones manuales del archivo.
        """
        from collections_app.core.models import Card

        repo = CardsRepository(self._conn)
        if repo.get(collection_id, card.code_id, card.card_number) is None:
            repo.upsert(
                Card(
                    collection_id=collection_id,
                    code_id=card.code_id,
                    card_number=card.card_number,
                    card_name=card.card_name,
                )
            )

    def _log_transaction(
        self,
        svc: InventoryService,
        collection_id: int,
        card: ExchangeCard,
        alta: bool,
    ) -> None:
        """Registra la transacción en `transactions` (sin tocar inventory)."""
        from collections_app.core.models import OperationType, Transaction

        op = OperationType.ALTA if alta else OperationType.BAJA
        svc._transactions.log(  # noqa: SLF001
            Transaction(
                transaction_id=None,
                collection_id=collection_id,
                code_id=card.code_id,
                card_number=card.card_number,
                operation=op,
                quantity=1,
                transaction_date=utc_now(),
            )
        )

    def _compute_checksum(self, ef: ExchangeFile) -> str:
        """SHA256 truncado sobre los campos estables del archivo.

        NO incluye `generated_at` (para que el checksum sea reproducible
        dado el mismo input) ni `checksum` (obvio).
        """
        payload = {
            "app": ef.app,
            "version": ef.version,
            "collection_id": ef.collection_id,
            "collection_name": ef.collection_name,
            "missing": [self._card_to_dict(c) for c in ef.missing],
            "duplicates": [self._card_to_dict(c) for c in ef.duplicates],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:_CHECKSUM_LEN]

    @staticmethod
    def _card_to_dict(c: ExchangeCard) -> dict[str, Any]:
        return {
            "code_id": c.code_id,
            "card_number": c.card_number,
            "card_name": c.card_name,
            "quantity": c.quantity,
        }

    def _write_file(self, ef: ExchangeFile, path: Path) -> None:
        data = {
            "app": ef.app,
            "version": ef.version,
            "collection_id": ef.collection_id,
            "collection_name": ef.collection_name,
            "generated_at": ef.generated_at,
            "missing": [self._card_to_dict(c) for c in ef.missing],
            "duplicates": [self._card_to_dict(c) for c in ef.duplicates],
            "checksum": ef.checksum,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _dict_to_exchange_file(self, data: dict[str, Any]) -> ExchangeFile:
        def parse_cards(lst: list[dict[str, Any]]) -> list[ExchangeCard]:
            return [
                ExchangeCard(
                    code_id=str(c["code_id"]),
                    card_number=int(c["card_number"]),
                    card_name=str(c["card_name"]),
                    quantity=int(c.get("quantity", 0)),
                )
                for c in lst
            ]

        return ExchangeFile(
            app=str(data.get("app", "")),
            version=str(data.get("version", "")),
            collection_id=int(data["collection_id"]),
            collection_name=str(data.get("collection_name", "")),
            generated_at=str(data.get("generated_at", "")),
            missing=parse_cards(data.get("missing", []) or []),
            duplicates=parse_cards(data.get("duplicates", []) or []),
        )
```

### [src/collections_app/core/services/inventory_service.py](src/collections_app/core/services/inventory_service.py)

```python
"""Servicio que coordina inventory + transactions de forma consistente."""

import sqlite3

from collections_app.core.db.connection import transaction
from collections_app.core.models import (
    Card,
    InventoryItem,
    OperationType,
    Transaction,
)
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
    TransactionsRepository,
)
from collections_app.core.utils.datetime_helpers import utc_now


class AmbiguousCardError(Exception):
    """Lanzado cuando una búsqueda por número devuelve múltiples cards."""

    def __init__(self, matches: list[Card]) -> None:
        self.matches = matches
        super().__init__(f"{len(matches)} cards con ese número")


class InventoryService:
    """Orquesta inventory + transactions para alta/baja consistente."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._cards = CardsRepository(conn)
        self._inventory = InventoryRepository(conn)
        self._transactions = TransactionsRepository(conn)

    def add_card(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Suma al inventario y registra transacción 'alta'.

        Validaciones:
        - quantity > 0
        - La (collection_id, code_id, card_number) debe existir en cards.

        Toda la operación corre dentro de una transacción SQLite.
        """
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")

        if self._cards.get(collection_id, code_id, card_number) is None:
            raise ValueError(f"Card ({collection_id}, {code_id}, {card_number}) no existe en cards")

        with transaction(self.conn):
            updated = self._inventory.adjust_quantity(collection_id, code_id, card_number, quantity)
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    collection_id=collection_id,
                    code_id=code_id,
                    card_number=card_number,
                    operation=OperationType.ALTA,
                    quantity=quantity,
                    transaction_date=utc_now(),
                )
            )
        return updated

    def remove_card(
        self,
        collection_id: int,
        code_id: str,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Resta del inventario y registra transacción 'baja'.

        Validaciones:
        - quantity > 0
        - El item debe existir y tener `quantity` >= cantidad pedida.

        Toda la operación corre dentro de una transacción SQLite.
        """
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")

        existing = self._inventory.get(collection_id, code_id, card_number)
        if existing is None:
            raise ValueError(f"No hay inventario para ({collection_id}, {code_id}, {card_number})")
        if existing.quantity < quantity:
            raise ValueError(f"Cantidad insuficiente: hay {existing.quantity}, se piden {quantity}")

        with transaction(self.conn):
            updated = self._inventory.adjust_quantity(
                collection_id, code_id, card_number, -quantity
            )
            self._transactions.log(
                Transaction(
                    transaction_id=None,
                    collection_id=collection_id,
                    code_id=code_id,
                    card_number=card_number,
                    operation=OperationType.BAJA,
                    quantity=quantity,
                    transaction_date=utc_now(),
                )
            )
        return updated

    def add_card_by_number(
        self,
        collection_id: int,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Alta usando solo el número (cuando la colección no requiere código).

        Resuelve el `code_id` vía `CardsRepository.find_by_number`.

        Raises:
            ValueError: si `quantity <= 0` o no hay cards con ese número.
            AmbiguousCardError: si hay >1 card con ese número en distintos
                códigos. La excepción incluye `matches` para que la UI
                pueda pedir al usuario que elija uno.
        """
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")
        matches = self._cards.find_by_number(collection_id, card_number)
        if not matches:
            raise ValueError(f"Card número {card_number} no existe en collection {collection_id}")
        if len(matches) > 1:
            raise AmbiguousCardError(matches)
        card = matches[0]
        return self.add_card(collection_id, card.code_id, card.card_number, quantity)

    def remove_card_by_number(
        self,
        collection_id: int,
        card_number: int,
        quantity: int = 1,
    ) -> InventoryItem:
        """Baja usando solo el número. Misma semántica que add_card_by_number."""
        if quantity <= 0:
            raise ValueError(f"quantity debe ser > 0 (recibido: {quantity})")
        matches = self._cards.find_by_number(collection_id, card_number)
        if not matches:
            raise ValueError(f"Card número {card_number} no existe en collection {collection_id}")
        if len(matches) > 1:
            raise AmbiguousCardError(matches)
        card = matches[0]
        return self.remove_card(collection_id, card.code_id, card.card_number, quantity)

    def get_stats(self, collection_id: int) -> dict[str, int | float]:
        """Estadísticas agregadas para una colección.

        Returns:
            Dict con:
            - total_cards: cantidad de cards en el catálogo.
            - owned: cards distintas con quantity > 0.
            - missing: cards sin stock (no en inventory o quantity = 0).
            - percentage: owned / total_cards * 100 (0.0 si total_cards = 0).
            - total_physical: suma de todas las quantities (todas las copias).
            - cards_with_duplicates: cards distintas con quantity > 1.
            - total_duplicate_copies: suma de (quantity - 1) sobre las que tienen duplicados.
        """
        total_cards = self._cards.count_by_collection(collection_id)
        owned_items = self._inventory.list_owned(collection_id)
        owned = len(owned_items)
        missing = max(0, total_cards - owned)
        percentage = (owned / total_cards * 100) if total_cards > 0 else 0.0
        total_physical = sum(i.quantity for i in owned_items)
        dup_items = [i for i in owned_items if i.quantity > 1]
        cards_with_duplicates = len(dup_items)
        total_duplicate_copies = sum(i.quantity - 1 for i in dup_items)

        return {
            "total_cards": total_cards,
            "owned": owned,
            "missing": missing,
            "percentage": percentage,
            "total_physical": total_physical,
            "cards_with_duplicates": cards_with_duplicates,
            "total_duplicate_copies": total_duplicate_copies,
        }
```

### [src/collections_app/core/services/license_service.py](src/collections_app/core/services/license_service.py)

```python
"""Servicio de licencias para colecciones premium.

Diseño en dos niveles:
- Nivel 1 (actual): honor system local. Cada `Collection` premium guarda
  un SHA256 de la clave válida en `license_key_required`. El usuario
  ingresa una clave, se hashea y se compara. Suficiente como gate
  inicial para empezar a vender.
- Nivel 2 (futuro): validación online. Migración: solo cambiar la
  implementación de `LicenseValidator` sin tocar la UI ni el `LicenseService`.

Las claves desbloqueadas se persisten por colección en `app_settings`,
con la clave `license_unlocked:{collection_id}` y como valor el hash
que validó. Si el admin cambia el `license_key_required` de la
colección, el unlock anterior queda invalidado automáticamente.
"""

import hashlib
import sqlite3
from abc import ABC, abstractmethod

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CollectionsRepository,
    SettingsRepository,
)

SETTING_KEY_LICENSE_PREFIX = "license_unlocked:"


class LicenseValidator(ABC):
    """Interfaz abstracta para validar licencias.

    Una implementación concreta puede ser local (hash) u online (HTTP).
    """

    @abstractmethod
    def validate(self, collection_id: int, license_key: str) -> bool:
        """Retorna True si la clave es válida para la colección."""

    @abstractmethod
    def is_required(self, collection: Collection) -> bool:
        """Retorna True si la colección requiere licencia para usarse."""


class LocalHashLicenseValidator(LicenseValidator):
    """Valida la clave comparando su SHA256 con `collection.license_key_required`.

    NO es seguro contra usuarios técnicos (la clave válida no se transmite
    en cleartext, pero el `license_key_required` es legible en la DB
    distribuida). Sirve como gate inicial. Migración a Nivel 2 (online)
    cambia solo esta clase.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def validate(self, collection_id: int, license_key: str) -> bool:
        col = CollectionsRepository(self.conn).get_by_id(collection_id)
        if col is None:
            return False
        if not self.is_required(col):
            return True
        if not col.license_key_required:
            return False
        return self.hash_key(license_key) == col.license_key_required

    def is_required(self, collection: Collection) -> bool:
        return bool(collection.is_premium and collection.license_key_required)

    @staticmethod
    def hash_key(key: str) -> str:
        """SHA256 hex digest. Útil para que admin genere los hashes."""
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


class LicenseService:
    """Wrapper de alto nivel: usa un validador y persiste unlocks en settings."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        validator: LicenseValidator | None = None,
    ) -> None:
        self.conn = conn
        self._validator = validator or LocalHashLicenseValidator(conn)
        self._collections = CollectionsRepository(conn)
        self._settings = SettingsRepository(conn)

    def is_unlocked(self, collection_id: int) -> bool:
        """True si la colección no requiere licencia o ya fue desbloqueada."""
        col = self._collections.get_by_id(collection_id)
        if col is None:
            return False
        if not self._validator.is_required(col):
            return True
        stored = self._settings.get(SETTING_KEY_LICENSE_PREFIX + str(collection_id))
        if stored is None:
            return False
        # Si el admin cambió el license_key_required, el unlock previo
        # queda inválido automáticamente.
        return stored == col.license_key_required

    def unlock(self, collection_id: int, license_key: str) -> bool:
        """Valida la clave y persiste el unlock si pasa.

        Returns:
            True si la clave es válida (y se persistió, si aplica).
        """
        if not self._validator.validate(collection_id, license_key):
            return False
        col = self._collections.get_by_id(collection_id)
        if col is not None and self._validator.is_required(col):
            assert col.license_key_required is not None
            self._settings.set(
                SETTING_KEY_LICENSE_PREFIX + str(collection_id),
                col.license_key_required,
            )
            self.conn.commit()
        return True

    def lock(self, collection_id: int) -> None:
        """Quita el unlock persistido (no afecta colecciones free)."""
        deleted = self._settings.delete(SETTING_KEY_LICENSE_PREFIX + str(collection_id))
        if deleted:
            self.conn.commit()
```

### [src/collections_app/core/services/pdf_generator.py](src/collections_app/core/services/pdf_generator.py)

```python
"""Generadores de PDF: álbum visual + listas (faltantes/repetidas/lo que tengo).

API funcional, sin estado: cada `generate_*_pdf(...)` recibe los datos ya
resueltos (vía `AlbumService.build_album_cards`) y escribe el PDF en
`output_path`.

Layout del álbum visual:
- A4 (portrait o landscape según `Collection.album_orientation`).
- Grilla configurable por colección (`album_columns × album_rows`),
  default 3×4 portrait = 12 cards/hoja A4.
- Cada `code_id` arranca en página nueva con header oscuro de categoría.
- Celdas:
  * CASO A — con imagen (foto descargada por scraper Panini): se dibuja.
  * CASO B — sin imagen, en inventario: rectángulo celeste + texto.
  * CASO C — sin imagen, no en inventario: rectángulo blanco + borde gris.
- Badge ×N en esquina superior derecha si `quantity > 1`.

PDFs de lista (faltantes / repetidas / owned):
- Texto puro Helvetica 9pt, 2 columnas por página.
- Header global (nombre colección, tipo, fecha) en primera página.
- Header de categoría cuando cambia `code_id`.
- Metadata de intercambio embebida en `Subject` + `Keywords` con
  checksum SHA256 truncado para detectar manipulaciones.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from itertools import groupby
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from collections_app.core.models import Card, Collection, ExchangeCard

logger = logging.getLogger(__name__)

# Geometría base
MARGIN_PT = 28.35  # 10mm
HEADER_PT = 22.68  # 8mm
CELL_PADDING_PT = 2.84  # 1mm
LIST_LINE_HEIGHT_PT = 13.0
LIST_COL_GAP_PT = 14.0
LIST_HEADER_FONT_SIZE = 14
LIST_BODY_FONT_SIZE = 9
ALBUM_CELL_NUM_FONT_SIZE = 9
ALBUM_CELL_NAME_FONT_SIZE = 8
ALBUM_CELL_CODE_FONT_SIZE = 7
ALBUM_HEADER_FONT_SIZE = 10
ALBUM_PAGE_NUM_FONT_SIZE = 7

# Colores
COLOR_CELESTE = Color(174 / 255, 214 / 255, 241 / 255)
COLOR_WHITE = Color(1.0, 1.0, 1.0)
COLOR_GRAY_BORDER = Color(0.67, 0.67, 0.67)
COLOR_HEADER_BG = Color(0.2, 0.2, 0.2)
COLOR_HEADER_FG = white
COLOR_DARK_TEXT = Color(0.15, 0.15, 0.15)
COLOR_BADGE_BG = COLOR_CELESTE
COLOR_BADGE_FG = white
COLOR_PAGE_NUM_FG = Color(0.5, 0.5, 0.5)
COLOR_LIST_SEPARATOR = HexColor("#d0d0d0")
COLOR_LIST_CATEGORY_FG = Color(0.1, 0.1, 0.1)

# Constantes de metadata de intercambio
EXCHANGE_APP_NAME = "CollectionsApp"
EXCHANGE_PROTOCOL_VERSION = "1.0"
EXCHANGE_CHECKSUM_LEN = 16

MAX_NAME_CHARS = 20


# ----------------------------------------------------------------------
# Modelos de input / output
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class AlbumCard:
    """Una card del álbum con su contexto enriquecido para renderear.

    `image_path` es `None` si la imagen no está descargada todavía. En ese
    caso se usa placeholder celeste (si `quantity > 0`) o blanco.

    `code_order` es la posición de la categoría dentro del header (ver
    `CodeLine.code_order`). El renderer lo usa para mostrar las categorías
    en el orden definido por el admin, no en orden alfabético del code_id.
    """

    card: Card
    quantity: int
    image_path: Path | None
    requires_code: bool
    code_name: str  # nombre humano del código (ej. "ARGENTINA")
    code_order: int = 0  # default 0 → cae al final si está sin ordenar


@dataclass
class PdfGeneratorResult:
    """Resumen del PDF generado."""

    pages: int = 0
    cards_with_image: int = 0
    cards_celeste_placeholder: int = 0
    cards_missing: int = 0
    output_path: Path = field(default_factory=Path)


# ----------------------------------------------------------------------
# Helpers de label / chunks
# ----------------------------------------------------------------------


def format_label(card_number: int, code_id: str, requires_code: bool) -> str:
    """`requires_code=True` → 'ARG-5'; sino → '5'."""
    if requires_code:
        return f"{code_id}-{card_number}"
    return str(card_number)


def _chunks(items: list[AlbumCard], size: int) -> list[list[AlbumCard]]:
    """Parte `items` en grupos de `size`. El último puede ser más chico."""
    if size <= 0:
        return []
    return [items[i : i + size] for i in range(0, len(items), size)]


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


# ----------------------------------------------------------------------
# Metadata de intercambio
# ----------------------------------------------------------------------


def _build_exchange_metadata(
    subtype: str,
    collection_id: int,
    collection_name: str,
    cards: list[dict[str, object]],
) -> str:
    """Construye el JSON de metadata embebida en PDFs de lista.

    El checksum es un SHA256 truncado a `EXCHANGE_CHECKSUM_LEN` chars,
    calculado sobre los campos estables (excluyendo `generated_at` para
    que el PDF sea reproducible bit-a-bit dado el mismo input). La idea
    es que la futura función "Intercambio" pueda detectar PDFs manipulados.
    """
    payload: dict[str, object] = {
        "app": EXCHANGE_APP_NAME,
        "version": EXCHANGE_PROTOCOL_VERSION,
        "type": "exchange",
        "subtype": subtype,
        "collection_id": collection_id,
        "collection_name": collection_name,
        "generated_at": datetime.now(UTC).isoformat(),
        "cards": cards,
    }
    base = json.dumps(
        {k: v for k, v in payload.items() if k != "generated_at"},
        sort_keys=True,
        ensure_ascii=False,
    )
    payload["checksum"] = hashlib.sha256(base.encode("utf-8")).hexdigest()[:EXCHANGE_CHECKSUM_LEN]
    return json.dumps(payload, ensure_ascii=False)


def validate_exchange_pdf_metadata(pdf_path: Path) -> dict[str, object] | None:
    """Lee la metadata de intercambio de un PDF generado por CollectionsApp.

    Retorna el dict si el checksum es válido, `None` si:
    - no es un PDF de CollectionsApp (no tiene la metadata o `app != ...`),
    - el JSON está corrupto,
    - el checksum no matchea (PDF manipulado).
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        if reader.metadata is None:
            return None
        keywords = reader.metadata.get("/Keywords", "")
        if not keywords:
            return None
        data = json.loads(keywords)
    except Exception as exc:  # noqa: BLE001
        logger.debug("validate_exchange_pdf_metadata: parsing falló: %s", exc)
        return None

    if not isinstance(data, dict) or data.get("app") != EXCHANGE_APP_NAME:
        return None

    stored_checksum = data.get("checksum")
    if not isinstance(stored_checksum, str):
        return None

    base = json.dumps(
        {k: v for k, v in data.items() if k not in ("checksum", "generated_at")},
        sort_keys=True,
        ensure_ascii=False,
    )
    computed = hashlib.sha256(base.encode("utf-8")).hexdigest()[:EXCHANGE_CHECKSUM_LEN]
    if computed != stored_checksum:
        return None
    return data


# ----------------------------------------------------------------------
# Render de álbum visual
# ----------------------------------------------------------------------


def generate_album_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """Genera el PDF álbum visual (todas las cards, foto o placeholder).

    Cada `code_id` empieza en página nueva con header oscuro. Layout
    `album_columns × album_rows` desde `collection`.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pagesize = landscape(A4) if collection.album_orientation == "landscape" else A4
    page_w, page_h = pagesize
    cols = max(1, collection.album_columns)
    rows = max(1, collection.album_rows)
    cell_w, cell_h = _cell_geometry(page_w, page_h, cols, rows)

    c = canvas.Canvas(str(output_path), pagesize=pagesize)
    result = PdfGeneratorResult(output_path=output_path)

    if not album_cards:
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_w / 2, page_h / 2, "(sin cards para mostrar)")
        c.showPage()
        c.save()
        result.pages = 1
        return result

    # Agrupar por code_id manteniendo el orden de entrada.
    grouped = groupby(album_cards, key=lambda ac: ac.card.code_id)
    page_num = 0
    for _, items_iter in grouped:
        items = list(items_iter)
        code_name = items[0].code_name
        for chunk in _chunks(items, cols * rows):
            page_num += 1
            _draw_album_header(c, code_name, page_w, page_h)
            _draw_page_number(c, page_num, page_w)
            for idx, ac in enumerate(chunk):
                col_i = idx % cols
                row_i = idx // cols
                x, y = _cell_origin(col_i, row_i, cell_w, cell_h, page_h)
                _draw_album_cell(c, ac, x, y, cell_w, cell_h, result)
            c.showPage()

    c.save()
    result.pages = page_num
    return result


def _cell_geometry(page_w: float, page_h: float, cols: int, rows: int) -> tuple[float, float]:
    """Ancho/alto de cada celda dado el espacio útil de la página."""
    usable_w = page_w - 2 * MARGIN_PT
    usable_h = page_h - 2 * MARGIN_PT - HEADER_PT
    return usable_w / cols, usable_h / rows


def _cell_origin(
    col_i: int, row_i: int, cell_w: float, cell_h: float, page_h: float
) -> tuple[float, float]:
    """Esquina inferior-izquierda de una celda en coords reportlab."""
    x = MARGIN_PT + col_i * cell_w
    y = page_h - MARGIN_PT - HEADER_PT - (row_i + 1) * cell_h
    return x, y


def _draw_album_header(c: canvas.Canvas, text: str, page_w: float, page_h: float) -> None:
    x = MARGIN_PT
    y = page_h - MARGIN_PT - HEADER_PT
    bar_w = page_w - 2 * MARGIN_PT
    c.setFillColor(COLOR_HEADER_BG)
    c.rect(x, y, bar_w, HEADER_PT, stroke=0, fill=1)
    c.setFillColor(COLOR_HEADER_FG)
    c.setFont("Helvetica-Bold", ALBUM_HEADER_FONT_SIZE)
    c.drawCentredString(page_w / 2, y + HEADER_PT / 2 - 4, text.upper())


def _draw_page_number(c: canvas.Canvas, page_num: int, page_w: float) -> None:
    c.setFillColor(COLOR_PAGE_NUM_FG)
    c.setFont("Helvetica", ALBUM_PAGE_NUM_FONT_SIZE)
    c.drawCentredString(page_w / 2, MARGIN_PT / 2, str(page_num))


def _draw_album_cell(
    c: canvas.Canvas,
    ac: AlbumCard,
    x: float,
    y: float,
    w: float,
    h: float,
    result: PdfGeneratorResult,
) -> None:
    """Dibuja una celda según el caso (A/B/C) y actualiza contadores.

    REGLA IMPORTANTE: la foto solo se dibuja si la card está en inventario
    (`quantity > 0`). Si no la tengo, siempre va al placeholder blanco —
    aunque la foto exista en disco — porque el álbum representa MI
    colección, no el catálogo.
    """
    inner_x = x + CELL_PADDING_PT
    inner_y = y + CELL_PADDING_PT
    inner_w = w - 2 * CELL_PADDING_PT
    inner_h = h - 2 * CELL_PADDING_PT

    if ac.quantity > 0 and ac.image_path is not None and ac.image_path.exists():
        # CASO A: tengo la card y hay foto descargada → mostrar foto
        try:
            img = ImageReader(str(ac.image_path))
            c.drawImage(
                img,
                inner_x,
                inner_y,
                width=inner_w,
                height=inner_h,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
            result.cards_with_image += 1
        except Exception as exc:  # noqa: BLE001
            logger.debug("Falló drawImage para card %s: %s", ac.card.card_number, exc)
            _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
            result.cards_celeste_placeholder += 1
    elif ac.quantity > 0:
        # CASO B: tengo la card pero sin foto → placeholder celeste
        _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
        result.cards_celeste_placeholder += 1
    else:
        # CASO C: NO la tengo → placeholder blanco con borde gris.
        # Aunque la foto esté en disco, no se muestra: el álbum
        # representa la colección del usuario, no el catálogo.
        _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
        result.cards_missing += 1

    if ac.quantity > 1:
        _draw_quantity_badge(c, ac.quantity, x + w, y + h)


def _draw_placeholder_cell(
    c: canvas.Canvas, ac: AlbumCard, x: float, y: float, w: float, h: float
) -> None:
    """Rectángulo celeste (en inventario) o blanco con borde (no inventario)."""
    if ac.quantity > 0:
        c.setFillColor(COLOR_CELESTE)
        c.rect(x, y, w, h, stroke=0, fill=1)
    else:
        c.setFillColor(COLOR_WHITE)
        c.setStrokeColor(COLOR_GRAY_BORDER)
        c.setLineWidth(1)
        c.rect(x, y, w, h, stroke=1, fill=1)

    # Texto centrado: número/código-número (bold), nombre, code_id
    cx = x + w / 2
    cy = y + h / 2
    label = format_label(ac.card.card_number, ac.card.code_id, ac.requires_code)
    name = _truncate(ac.card.card_name, MAX_NAME_CHARS)

    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", ALBUM_CELL_NUM_FONT_SIZE)
    c.drawCentredString(cx, cy + 8, label)
    c.setFont("Helvetica", ALBUM_CELL_NAME_FONT_SIZE)
    c.drawCentredString(cx, cy - 2, name)
    c.setFont("Helvetica", ALBUM_CELL_CODE_FONT_SIZE)
    c.drawCentredString(cx, cy - 12, ac.card.code_id)


def _draw_quantity_badge(
    c: canvas.Canvas, quantity: int, top_right_x: float, top_right_y: float
) -> None:
    """Círculo celeste con número blanco en esquina superior derecha."""
    radius = 7.0
    cx = top_right_x - radius - 1
    cy = top_right_y - radius - 1
    c.setFillColor(COLOR_BADGE_BG)
    c.circle(cx, cy, radius, stroke=0, fill=1)
    c.setFillColor(COLOR_BADGE_FG)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(cx, cy - 2, f"×{quantity}")


# ----------------------------------------------------------------------
# Render de PDFs de lista (faltantes / repetidas / owned)
# ----------------------------------------------------------------------


class ListReportMode(StrEnum):
    """Modo visual de los reportes de lista (faltantes / repetidas).

    - FULL: un título por categoría + flujo continuo
      "número nombre / número nombre" con saltos de línea por ancho.
      Para repetidas agrega "×N" al final del item. Pensado para
      imprimir y compartir.
    - SUMMARY: una línea por categoría, solo números separados por " / ".
      Para repetidas pega la cantidad inline ("24×3 / 7×2"). Compacto.
    """

    FULL = "full"
    SUMMARY = "summary"


# Backward-compat: el commit anterior expuso `DuplicatesReportMode`.
# Mantenemos el alias para no romper imports en otros módulos / tests.
DuplicatesReportMode = ListReportMode


def generate_missing_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
    mode: ListReportMode = ListReportMode.FULL,
) -> PdfGeneratorResult:
    """PDF de cards que faltan (`quantity == 0`).

    `mode` controla el layout (FULL / SUMMARY). Ambos modos embeben
    metadata `subtype="missing"`. show_quantity está hardcoded en
    False — los faltantes nunca tienen cantidad para mostrar.
    """
    missing = [ac for ac in album_cards if ac.quantity == 0]
    if mode == ListReportMode.SUMMARY:
        return _generate_list_summary(
            collection,
            missing,
            output_path,
            subtype="missing",
            title="Faltantes",
            show_quantity=False,
        )
    return _generate_list_full(
        collection,
        missing,
        output_path,
        subtype="missing",
        title="Faltantes",
        show_quantity=False,
    )


def generate_duplicates_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
    mode: ListReportMode = ListReportMode.FULL,
) -> PdfGeneratorResult:
    """PDF de cards repetidas (`quantity > 1`).

    Despacha al renderer correspondiente según `mode`. Ambos modos
    embeben metadata `subtype="duplicates"`. show_quantity=True para
    que aparezca "×N" en cada item / inline junto al número.
    """
    dups = [ac for ac in album_cards if ac.quantity > 1]
    if mode == ListReportMode.SUMMARY:
        return _generate_list_summary(
            collection,
            dups,
            output_path,
            subtype="duplicates",
            title="Repetidas",
            show_quantity=True,
        )
    return _generate_list_full(
        collection,
        dups,
        output_path,
        subtype="duplicates",
        title="Repetidas",
        show_quantity=True,
    )


# ----------------------------------------------------------------------
# Render compartido: lista FULL (categoría + flujo de items)
# Usado por faltantes y repetidas (parametrizado por show_quantity).
# ----------------------------------------------------------------------


def _generate_list_full(
    collection: Collection,
    cards: list[AlbumCard],
    output_path: Path,
    subtype: str,
    title: str,
    show_quantity: bool,
) -> PdfGeneratorResult:
    """Modo completo: título por categoría + flujo continuo de items.

    Layout 2 columnas. Cada categoría arranca con su header y debajo
    un flujo "ARG-24 Messi ×2 / ARG-7 Di María / ..." con saltos de
    línea cuando el siguiente item no entra. El separador " / " NUNCA
    queda al final de línea (el wrap ocurre antes).

    `show_quantity=True` (repetidas) agrega " ×N" al final de cada
    item. `show_quantity=False` (faltantes) los omite.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)
    _set_list_metadata(c, collection, cards, subtype, f"{title} (Completo)")

    col_w = (page_w - 2 * MARGIN_PT - LIST_COL_GAP_PT) / 2
    column_xs = (MARGIN_PT, MARGIN_PT + col_w + LIST_COL_GAP_PT)

    y = page_h - MARGIN_PT
    y = _draw_list_global_header(c, collection, f"{title} — Completo", cards, page_w, y)
    y_top_after_global = y
    col_idx = 0
    page_num = 1
    result = PdfGeneratorResult(output_path=output_path, pages=1)

    if not cards:
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_w / 2, page_h / 2, f"(no hay {title.lower()})")
        c.showPage()
        c.save()
        return result

    def new_column() -> None:
        nonlocal col_idx, y, page_num
        col_idx += 1
        if col_idx >= 2:
            c.showPage()
            page_num += 1
            result.pages = page_num
            col_idx = 0
            y = page_h - MARGIN_PT
        else:
            y = y_top_after_global

    def ensure_room(lines: int = 1) -> None:
        if y - lines * LIST_LINE_HEIGHT_PT < MARGIN_PT:
            new_column()

    grouped = groupby(cards, key=lambda ac: ac.card.code_id)
    for code_id, items_iter in grouped:
        items = list(items_iter)
        code_name = items[0].code_name

        # Header de categoría
        ensure_room(2)
        _draw_category_header(c, code_id, code_name, column_xs[col_idx], y, col_w)
        y -= LIST_LINE_HEIGHT_PT * 1.4

        # Flujo de items
        c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
        c.setFillColor(COLOR_DARK_TEXT)
        line_x = column_xs[col_idx]
        max_x = column_xs[col_idx] + col_w
        first_in_line = True

        for ac in items:
            item_text = _format_full_item(ac, collection.requires_code, show_quantity)
            separator = "" if first_in_line else " / "
            full = separator + item_text
            text_w = c.stringWidth(full, "Helvetica", LIST_BODY_FONT_SIZE)

            if not first_in_line and line_x + text_w > max_x:
                # No entra: saltar a línea siguiente sin el separador.
                y -= LIST_LINE_HEIGHT_PT
                ensure_room(1)
                line_x = column_xs[col_idx]
                full = item_text
                text_w = c.stringWidth(full, "Helvetica", LIST_BODY_FONT_SIZE)
                first_in_line = True

            c.drawString(line_x, y, full)
            line_x += text_w
            first_in_line = False

        # Espacio entre categorías
        y -= int(LIST_LINE_HEIGHT_PT * 1.6)

    c.showPage()
    c.save()
    result.cards_celeste_placeholder = len(cards)
    return result


def _format_full_item(ac: AlbumCard, requires_code: bool, show_quantity: bool) -> str:
    """Formato de cada item en modo FULL.

    show_quantity=True y quantity>1 → "ARG-24 Messi ×3"
    show_quantity=True y quantity<=1 → "ARG-24 Messi" (sin ×N)
    show_quantity=False → "ARG-24 Messi"
    """
    label = format_label(ac.card.card_number, ac.card.code_id, requires_code)
    text = f"{label} {_truncate(ac.card.card_name, MAX_NAME_CHARS)}"
    if show_quantity and ac.quantity > 1:
        text += f" ×{ac.quantity}"
    return text


# ----------------------------------------------------------------------
# Render compartido: lista SUMMARY (línea por categoría, solo números)
# ----------------------------------------------------------------------


def _generate_list_summary(
    collection: Collection,
    cards: list[AlbumCard],
    output_path: Path,
    subtype: str,
    title: str,
    show_quantity: bool,
) -> PdfGeneratorResult:
    """Modo resumido: una línea por categoría con solo los números.

    `show_quantity=True` (repetidas) pega la cantidad inline:
        "ARG:  24×3 / 7×2 / 11×2"
    `show_quantity=False` (faltantes) solo los números:
        "ARG:  24 / 7 / 11 / 18"

    Si la línea no entra, continúa en la siguiente con sangría a la
    altura del primer número (alineado bajo el código, no del prefijo).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)
    _set_list_metadata(c, collection, cards, subtype, f"{title} (Resumido)")

    col_w = (page_w - 2 * MARGIN_PT - LIST_COL_GAP_PT) / 2
    column_xs = (MARGIN_PT, MARGIN_PT + col_w + LIST_COL_GAP_PT)

    y = page_h - MARGIN_PT
    y = _draw_list_global_header(c, collection, f"{title} — Resumido", cards, page_w, y)
    y_top_after_global = y
    col_idx = 0
    page_num = 1
    result = PdfGeneratorResult(output_path=output_path, pages=1)

    if not cards:
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_w / 2, page_h / 2, f"(no hay {title.lower()})")
        c.showPage()
        c.save()
        return result

    def new_column() -> None:
        nonlocal col_idx, y, page_num
        col_idx += 1
        if col_idx >= 2:
            c.showPage()
            page_num += 1
            result.pages = page_num
            col_idx = 0
            y = page_h - MARGIN_PT
        else:
            y = y_top_after_global

    def ensure_room() -> None:
        if y - LIST_LINE_HEIGHT_PT < MARGIN_PT:
            new_column()

    grouped = groupby(cards, key=lambda ac: ac.card.code_id)
    for code_id, items_iter in grouped:
        items = list(items_iter)
        ensure_room()

        prefix = f"{code_id}:  " if collection.requires_code else ""
        c.setFont("Helvetica-Bold", LIST_BODY_FONT_SIZE)
        c.setFillColor(COLOR_DARK_TEXT)
        c.drawString(column_xs[col_idx], y, prefix)
        prefix_w = c.stringWidth(prefix, "Helvetica-Bold", LIST_BODY_FONT_SIZE)
        indent_x = column_xs[col_idx] + prefix_w
        max_x = column_xs[col_idx] + col_w

        c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
        line_x = indent_x
        first = True
        for ac in items:
            num_text = _format_summary_number(ac, show_quantity)
            text = num_text if first else f" / {num_text}"
            w = c.stringWidth(text, "Helvetica", LIST_BODY_FONT_SIZE)
            if not first and line_x + w > max_x:
                # Continuar en línea siguiente, alineado al indent_x.
                y -= LIST_LINE_HEIGHT_PT
                ensure_room()
                line_x = indent_x
                text = num_text
                w = c.stringWidth(text, "Helvetica", LIST_BODY_FONT_SIZE)
                first = True
            c.drawString(line_x, y, text)
            line_x += w
            first = False

        y -= LIST_LINE_HEIGHT_PT

    c.showPage()
    c.save()
    result.cards_celeste_placeholder = len(cards)
    return result


def _format_summary_number(ac: AlbumCard, show_quantity: bool) -> str:
    """Número solo o con cantidad inline (`24` vs `24×3`)."""
    if show_quantity and ac.quantity > 1:
        return f"{ac.card.card_number}×{ac.quantity}"
    return str(ac.card.card_number)


def _set_list_metadata(
    c: canvas.Canvas,
    collection: Collection,
    cards: list[AlbumCard],
    subtype: str,
    title: str,
) -> None:
    """Setea Title/Subject/Keywords con metadata de intercambio.

    Compartido entre faltantes y repetidas: el `subtype` distingue
    cuál es para `validate_exchange_pdf_metadata`.
    """
    assert collection.collection_id is not None
    cards_meta: list[dict[str, object]] = [
        {
            "code_id": ac.card.code_id,
            "card_number": ac.card.card_number,
            "quantity": ac.quantity,
        }
        for ac in cards
    ]
    metadata_json = _build_exchange_metadata(
        subtype=subtype,
        collection_id=collection.collection_id,
        collection_name=collection.collection_name,
        cards=cards_meta,
    )
    c.setTitle(f"{collection.collection_name} — {title}")
    c.setSubject("CollectionsApp Exchange Data")
    c.setKeywords(metadata_json)
    c.setCreator(EXCHANGE_APP_NAME)


def generate_owned_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """PDF de cards en posesión (`quantity >= 1`)."""
    owned = [ac for ac in album_cards if ac.quantity >= 1]
    return _generate_list_pdf(collection, owned, output_path, subtype="owned", title="Lo que tengo")


def _generate_list_pdf(
    collection: Collection,
    items: list[AlbumCard],
    output_path: Path,
    subtype: str,
    title: str,
    show_quantity: bool = False,
) -> PdfGeneratorResult:
    """Helper: layout 2 columnas con header global + categorías + items."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)

    # Metadata embebida (futura función intercambio)
    assert collection.collection_id is not None
    cards_meta: list[dict[str, object]] = [
        {
            "code_id": ac.card.code_id,
            "card_number": ac.card.card_number,
            "quantity": ac.quantity,
        }
        for ac in items
    ]
    metadata_json = _build_exchange_metadata(
        subtype=subtype,
        collection_id=collection.collection_id,
        collection_name=collection.collection_name,
        cards=cards_meta,
    )
    c.setSubject("CollectionsApp Exchange Data")
    c.setKeywords(metadata_json)
    c.setCreator(EXCHANGE_APP_NAME)

    # Layout
    col_w = (page_w - 2 * MARGIN_PT - LIST_COL_GAP_PT) / 2
    column_xs = (MARGIN_PT, MARGIN_PT + col_w + LIST_COL_GAP_PT)

    # Cursor: y arranca debajo del header global
    y = page_h - MARGIN_PT
    y = _draw_list_global_header(c, collection, title, items, page_w, y)
    y_top_after_global = y  # primera columna arranca acá
    col_idx = 0
    page_num = 1
    result = PdfGeneratorResult(output_path=output_path, pages=1)

    if not items:
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_w / 2, page_h / 2, f"(no hay {title.lower()})")
        c.showPage()
        c.save()
        return result

    def new_column() -> None:
        nonlocal col_idx, y, page_num
        col_idx += 1
        if col_idx >= 2:
            c.showPage()
            page_num += 1
            result.pages = page_num
            col_idx = 0
            y = page_h - MARGIN_PT
        else:
            y = y_top_after_global

    def ensure_room(needed: float) -> None:
        nonlocal y
        if y - needed < MARGIN_PT:
            new_column()

    # Iterar agrupado por code_id; al cambiar, escribir header de categoría.
    last_code: str | None = None
    for ac in items:
        if ac.card.code_id != last_code:
            ensure_room(LIST_LINE_HEIGHT_PT * 2)
            _draw_category_header(c, ac.card.code_id, ac.code_name, column_xs[col_idx], y, col_w)
            y -= LIST_LINE_HEIGHT_PT * 1.4
            last_code = ac.card.code_id

        ensure_room(LIST_LINE_HEIGHT_PT)
        _draw_list_item(
            c,
            ac,
            column_xs[col_idx],
            y,
            col_w,
            show_quantity=show_quantity,
        )
        y -= LIST_LINE_HEIGHT_PT

        # Contadores
        if ac.quantity == 0:
            result.cards_missing += 1
        elif ac.image_path is not None and ac.image_path.exists():
            result.cards_with_image += 1
        else:
            result.cards_celeste_placeholder += 1

    # Total al pie
    ensure_room(LIST_LINE_HEIGHT_PT * 3)
    _draw_list_total(c, items, title, column_xs[col_idx], y, col_w, show_quantity)

    c.showPage()
    c.save()
    return result


def _draw_list_global_header(
    c: canvas.Canvas,
    collection: Collection,
    title: str,
    items: list[AlbumCard],
    page_w: float,
    y_top: float,
) -> float:
    del items  # firmado por simetría con futuras variantes
    x_left = MARGIN_PT
    x_right = page_w - MARGIN_PT
    y = y_top - LIST_HEADER_FONT_SIZE
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", LIST_HEADER_FONT_SIZE)
    c.drawString(x_left, y, collection.collection_name)
    y -= LIST_LINE_HEIGHT_PT
    c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
    c.drawString(x_left, y, title)
    y -= LIST_LINE_HEIGHT_PT * 0.85
    c.setFont("Helvetica", 8)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.drawString(x_left, y, f"Generado: {ts}")
    # separador horizontal
    y -= 6
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.5)
    c.line(x_left, y, x_right, y)
    y -= LIST_LINE_HEIGHT_PT
    return y


def _draw_category_header(
    c: canvas.Canvas, code_id: str, code_name: str, x: float, y: float, col_w: float
) -> None:
    c.setFillColor(COLOR_LIST_CATEGORY_FG)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"▶ {code_name.upper()} ({code_id})")
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.4)
    c.line(x, y - 2, x + col_w, y - 2)


def _draw_list_item(
    c: canvas.Canvas,
    ac: AlbumCard,
    x: float,
    y: float,
    col_w: float,
    show_quantity: bool,
) -> None:
    label = format_label(ac.card.card_number, ac.card.code_id, ac.requires_code)
    name = _truncate(ac.card.card_name, 32)
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
    # Columna izquierda: label en ancho fijo de ~40pt, alineado a la derecha.
    label_x = x + 40
    c.drawRightString(label_x, y, label)
    c.drawString(label_x + 6, y, name)
    if show_quantity:
        c.drawRightString(x + col_w, y, f"×{ac.quantity}")


def _draw_list_total(
    c: canvas.Canvas,
    items: list[AlbumCard],
    title: str,
    x: float,
    y: float,
    col_w: float,
    show_quantity: bool,
) -> None:
    y -= LIST_LINE_HEIGHT_PT
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.5)
    c.line(x, y, x + col_w, y)
    y -= LIST_LINE_HEIGHT_PT
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", LIST_BODY_FONT_SIZE)
    n = len(items)
    if show_quantity:
        units = sum(ac.quantity for ac in items)
        c.drawString(x, y, f"Total {title.lower()}: {n}, total unidades: {units}")
    else:
        c.drawString(x, y, f"Total {title.lower()}: {n}")


# ----------------------------------------------------------------------
# PDF de comparación entre dos álbumes
# ----------------------------------------------------------------------


def generate_comparison_pdf(
    collection: Collection,
    code_names: dict[str, str],
    i_need: list[ExchangeCard],
    i_can_offer: list[ExchangeCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """PDF de comparación con dos secciones: ME HACEN FALTA / PUEDO OFRECER.

    Layout: 2 columnas, cada sección arranca en columna nueva (la primera
    de cada sección puede estar en la misma página que la anterior si
    sobra espacio). Headers de categoría agrupan por code_id dentro de
    cada sección.

    Reutilizamos el mismo formato visual que los PDFs de faltantes /
    repetidas para mantener consistencia.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)

    # Metadata embebida (mismo formato que faltantes/repetidas pero con
    # subtype distinto para que un futuro lector pueda filtrar).
    assert collection.collection_id is not None
    cards_meta: list[dict[str, object]] = [
        *(
            {"section": "i_need", "code_id": c.code_id, "card_number": c.card_number}
            for c in i_need
        ),
        *(
            {
                "section": "i_can_offer",
                "code_id": c.code_id,
                "card_number": c.card_number,
                "quantity": c.quantity,
            }
            for c in i_can_offer
        ),
    ]
    metadata_json = _build_exchange_metadata(
        subtype="comparison",
        collection_id=collection.collection_id,
        collection_name=collection.collection_name,
        cards=cards_meta,
    )
    c.setSubject("CollectionsApp Exchange Data")
    c.setKeywords(metadata_json)
    c.setCreator(EXCHANGE_APP_NAME)

    # Layout
    col_w = (page_w - 2 * MARGIN_PT - LIST_COL_GAP_PT) / 2
    column_xs = (MARGIN_PT, MARGIN_PT + col_w + LIST_COL_GAP_PT)
    y = page_h - MARGIN_PT
    y = _draw_list_global_header(c, collection, "Comparación de álbumes", [], page_w, y)
    y_top_after_global = y
    col_idx = 0
    page_num = 1
    result = PdfGeneratorResult(output_path=output_path, pages=1)

    def new_column() -> None:
        nonlocal col_idx, y, page_num
        col_idx += 1
        if col_idx >= 2:
            c.showPage()
            page_num += 1
            result.pages = page_num
            col_idx = 0
            y = page_h - MARGIN_PT
        else:
            y = y_top_after_global

    def ensure_room(needed: float) -> None:
        if y - needed < MARGIN_PT:
            new_column()

    def draw_section_header(title: str, count: int) -> None:
        nonlocal y
        ensure_room(LIST_LINE_HEIGHT_PT * 2.5)
        x = column_xs[col_idx]
        c.setFillColor(COLOR_DARK_TEXT)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, f"▶ {title.upper()} ({count})")
        c.setStrokeColor(COLOR_DARK_TEXT)
        c.setLineWidth(0.6)
        c.line(x, y - 3, x + col_w, y - 3)
        y -= LIST_LINE_HEIGHT_PT * 1.6

    def draw_section(title: str, items: list[ExchangeCard], show_quantity: bool) -> None:
        nonlocal y
        draw_section_header(title, len(items))
        if not items:
            ensure_room(LIST_LINE_HEIGHT_PT)
            c.setFillColor(COLOR_DARK_TEXT)
            c.setFont("Helvetica-Oblique", LIST_BODY_FONT_SIZE)
            c.drawString(column_xs[col_idx], y, "(ninguna)")
            y -= LIST_LINE_HEIGHT_PT
            return
        last_code: str | None = None
        for card in items:
            if card.code_id != last_code:
                ensure_room(LIST_LINE_HEIGHT_PT * 2)
                _draw_category_header(
                    c,
                    card.code_id,
                    code_names.get(card.code_id, card.code_id),
                    column_xs[col_idx],
                    y,
                    col_w,
                )
                y -= LIST_LINE_HEIGHT_PT * 1.4
                last_code = card.code_id
            ensure_room(LIST_LINE_HEIGHT_PT)
            _draw_exchange_item(
                c,
                card,
                collection.requires_code,
                column_xs[col_idx],
                y,
                col_w,
                show_quantity=show_quantity,
            )
            y -= LIST_LINE_HEIGHT_PT

    # Sección 1: me hacen falta
    draw_section("Me hacen falta", i_need, show_quantity=False)
    # Forzar columna nueva para separar visualmente las secciones.
    new_column()
    draw_section("Puedo ofrecer", i_can_offer, show_quantity=True)

    c.showPage()
    c.save()
    result.cards_missing = len(i_need)
    result.cards_celeste_placeholder = len(i_can_offer)
    return result


def _draw_exchange_item(
    c: canvas.Canvas,
    card: ExchangeCard,
    requires_code: bool,
    x: float,
    y: float,
    col_w: float,
    show_quantity: bool,
) -> None:
    """Versión de _draw_list_item que toma ExchangeCard (sin AlbumCard)."""
    label = format_label(card.card_number, card.code_id, requires_code)
    name = _truncate(card.card_name, 32)
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
    label_x = x + 40
    c.drawRightString(label_x, y, label)
    c.drawString(label_x + 6, y, name)
    if show_quantity and card.quantity > 1:
        c.drawRightString(x + col_w, y, f"×{card.quantity}")
```

### [src/collections_app/core/services/profile_service.py](src/collections_app/core/services/profile_service.py)

```python
"""Servicio para descubrir perfiles e importar la estructura entre ellos.

Un perfil tiene su propio `collections.db`. `get_all_profiles()` escanea
la carpeta base buscando esos archivos. `import_structure()` copia las
tablas de catálogo (colecciones, codes, cards) desde un perfil fuente
hacia el target — NO copia inventory ni transactions, así el usuario
empieza con stock cero pero sin tener que recrear el catálogo.

Usado por `ProfileSetupDialog` cuando el cliente arranca con un perfil
sin colecciones.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from collections_app.core.utils.paths import get_base_app_dir

logger = logging.getLogger(__name__)

# Tablas a copiar (en orden que respeta FKs de `001_initial.sql`):
# headers → lines, collections → cards.
_STRUCTURE_TABLES = (
    "codes_headers",
    "codes_lines",
    "collections",
    "cards",
)


@dataclass(frozen=True)
class ProfileInfo:
    """Snapshot de un perfil detectado en el filesystem.

    `display_name` es lo que se muestra en la UI (ej. "Principal" para
    "default"). `collection_count` y `has_inventory` se leen de la DB
    para que el usuario sepa de qué perfil está importando.
    """

    name: str
    db_path: Path
    display_name: str
    collection_count: int
    has_inventory: bool


class ProfileService:
    """Operaciones sobre perfiles. Sin estado — todos los métodos son estáticos."""

    @staticmethod
    def get_all_profiles() -> list[ProfileInfo]:
        """Detecta todos los perfiles con `collections.db` en disco.

        Incluye el perfil "default" (raíz `Collections/`) y cualquier
        subdirectorio que contenga un `collections.db`. Subdirectorios
        sin DB se ignoran (carpetas dejadas a medias o de otras apps).
        """
        base = get_base_app_dir()
        profiles: list[ProfileInfo] = []

        # Perfil default (raíz)
        default_db = base / "collections.db"
        if default_db.exists():
            profiles.append(ProfileService._read_profile_info("default", default_db, "Principal"))

        # Perfiles en subdirectorios
        if base.exists():
            for subdir in sorted(base.iterdir()):
                if not subdir.is_dir():
                    continue
                db = subdir / "collections.db"
                if not db.exists():
                    continue
                profiles.append(
                    ProfileService._read_profile_info(subdir.name, db, subdir.name.capitalize())
                )

        return profiles

    @staticmethod
    def _read_profile_info(name: str, db_path: Path, display_name: str) -> ProfileInfo:
        """Lee count de colecciones y existencia de inventario via read-only.

        Modo `?mode=ro` evita crear archivos `-wal`/`-shm` en la
        carpeta del otro perfil al solo leerlo.
        """
        collection_count = 0
        has_inventory = False
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            try:
                row = conn.execute("SELECT COUNT(*) FROM collections").fetchone()
                collection_count = int(row[0]) if row else 0
                try:
                    row = conn.execute(
                        "SELECT COUNT(*) FROM inventory WHERE quantity > 0"
                    ).fetchone()
                    has_inventory = bool(row and row[0] > 0)
                except sqlite3.OperationalError:
                    # DB vieja sin tabla inventory todavía.
                    has_inventory = False
            finally:
                conn.close()
        except Exception as exc:  # noqa: BLE001 — diagnóstico, no rompe al usuario
            logger.debug("No se pudo leer perfil %s en %s: %s", name, db_path, exc)
        return ProfileInfo(
            name=name,
            db_path=db_path,
            display_name=display_name,
            collection_count=collection_count,
            has_inventory=has_inventory,
        )

    @staticmethod
    def import_structure(
        source_db_path: Path,
        target_conn: sqlite3.Connection,
    ) -> int:
        """Copia codes_headers/lines + collections + cards de fuente a target.

        - Idempotente: usa `INSERT OR IGNORE`, las filas existentes no se duplican.
        - NO toca `inventory` ni `transactions` — el usuario nuevo empieza
          con stock cero.
        - Asume que `target_conn` ya tiene el schema aplicado (las
          migraciones corrieron al inicializar la conexión).
        - Source se abre read-only con URI mode para no crear `-wal`/`-shm`.

        Retorna la cantidad TOTAL de colecciones en target después de la
        importación (útil para mostrar "N colecciones disponibles").
        """
        src = sqlite3.connect(f"file:{source_db_path}?mode=ro", uri=True)
        try:
            for table in _STRUCTURE_TABLES:
                # PRAGMA table_info sería más robusto que SELECT LIMIT 0
                # pero ambos funcionan; usamos description del cursor.
                cursor = src.execute(f"SELECT * FROM {table}")  # noqa: S608
                rows = cursor.fetchall()
                if not rows:
                    continue
                cols = [d[0] for d in cursor.description]
                placeholders = ", ".join("?" * len(cols))
                cols_str = ", ".join(cols)
                target_conn.executemany(
                    f"INSERT OR IGNORE INTO {table} ({cols_str}) "  # noqa: S608
                    f"VALUES ({placeholders})",
                    rows,
                )
            target_conn.commit()

            row = target_conn.execute("SELECT COUNT(*) FROM collections").fetchone()
            return int(row[0]) if row else 0
        finally:
            src.close()
```

### [src/collections_app/core/services/reports_service.py](src/collections_app/core/services/reports_service.py)

```python
"""Servicio de reportes: transacciones con info de la card asociada.

Las queries se hacen con un único JOIN entre `transactions` y `cards`
para evitar N+1 al armar la grilla del reporte.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime

from collections_app.core.models import OperationType
from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    parse_db_datetime,
)


@dataclass(frozen=True)
class TransactionWithCard:
    """Transacción enriquecida con el nombre de la card afectada."""

    transaction_date: datetime
    operation: OperationType
    code_id: str
    card_number: int
    card_name: str
    quantity: int


class ReportsService:
    """Queries optimizadas para el tab de reportes."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def get_transactions_in_period(
        self,
        collection_id: int,
        start: datetime,
        end: datetime,
        operation: OperationType | None = None,
    ) -> list[TransactionWithCard]:
        """Retorna transacciones del rango con el nombre de la card.

        `start` y `end` se convierten a UTC antes de filtrar. Si la card
        del registro fue borrada del catálogo, `card_name` será una cadena
        vacía (LEFT JOIN preserva la transacción aunque no exista la card).
        """
        start_str = format_for_db(start)
        end_str = format_for_db(end)
        params: list[object] = [collection_id, start_str, end_str]
        sql = (
            "SELECT t.transaction_date AS transaction_date, "
            "       t.operation AS operation, "
            "       t.code_id AS code_id, "
            "       t.card_number AS card_number, "
            "       COALESCE(c.card_name, '') AS card_name, "
            "       t.quantity AS quantity "
            "FROM transactions t "
            "LEFT JOIN cards c "
            "  ON c.collection_id = t.collection_id "
            " AND c.code_id = t.code_id "
            " AND c.card_number = t.card_number "
            "WHERE t.collection_id = ? "
            "  AND t.transaction_date BETWEEN ? AND ? "
        )
        if operation is not None:
            sql += "  AND t.operation = ? "
            params.append(operation.value)
        sql += "ORDER BY t.transaction_date DESC, t.transaction_id DESC"

        rows = self.conn.execute(sql, params).fetchall()
        return [
            TransactionWithCard(
                transaction_date=parse_db_datetime(r["transaction_date"]),
                operation=OperationType(r["operation"]),
                code_id=r["code_id"],
                card_number=r["card_number"],
                card_name=r["card_name"],
                quantity=r["quantity"],
            )
            for r in rows
        ]
```

### [src/collections_app/core/services/settings_service.py](src/collections_app/core/services/settings_service.py)

```python
"""Servicio para configuración de la app (colección activa, etc.)."""

import sqlite3

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository, SettingsRepository

SETTING_KEY_ACTIVE_COLLECTION = "active_collection_id"


class SettingsService:
    """Operaciones de alto nivel sobre `app_settings`."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self._settings = SettingsRepository(conn)
        self._collections = CollectionsRepository(conn)

    def get_active_collection_id(self) -> int | None:
        """Retorna el id de la colección activa, o None si no hay una configurada."""
        return self._settings.get_int(SETTING_KEY_ACTIVE_COLLECTION)

    def set_active_collection(self, collection_id: int) -> None:
        """Persiste el id de la colección activa."""
        self._settings.set(SETTING_KEY_ACTIVE_COLLECTION, str(collection_id))

    def clear_active_collection(self) -> None:
        """Elimina la configuración de colección activa."""
        self._settings.delete(SETTING_KEY_ACTIVE_COLLECTION)

    def get_active_collection(self) -> Collection | None:
        """Retorna la Collection activa o None si no hay configurada o no existe.

        Si el setting apunta a una colección que ya no existe, retorna None
        (no levanta error). Esto permite recuperarse de DBs reseteadas.
        """
        active_id = self.get_active_collection_id()
        if active_id is None:
            return None
        return self._collections.get_by_id(active_id)
```

### [src/collections_app/core/services/update_service.py](src/collections_app/core/services/update_service.py)

```python
"""Servicio de detección de actualizaciones de la app.

Diseño: la fuente de updates está abstraída via `UpdateSource` (Protocol).
Hoy se usa `GitHubUpdateSource` (consulta GitHub Releases API). Para
cambiar a un servidor propio en el futuro, solo hace falta inyectar
`ServerUpdateSource(...)` en `UpdateService(source=...)` — el resto
del código (worker en main.py, banner UI, sección Acerca de) sigue
funcionando sin tocar nada más.

El protocolo es deliberadamente mínimo: `fetch_latest()` retorna el JSON
del release o `None` si la fuente falla. NO levanta excepciones — los
errores de red son normales (sin internet, GitHub caído, rate limit) y
no deben romper el flujo del usuario.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import requests
from packaging.version import InvalidVersion, Version

from collections_app.__version__ import __update_url__, __version__

logger = logging.getLogger(__name__)

# Timeout deliberadamente corto: el chequeo es opcional. Si tarda más,
# es preferible asumir "sin red" y no bloquear al usuario.
CHECK_TIMEOUT = 8


@dataclass(frozen=True)
class UpdateInfo:
    """Resultado del chequeo de actualizaciones.

    `is_newer` ya está pre-calculado contra `__version__` actual — la UI
    no debería re-comparar versions. `download_url` es la URL directa al
    `.exe` si existe entre los assets, o cae al `release_url` (página
    HTML del release) como fallback.
    """

    current_version: str
    latest_version: str
    download_url: str
    release_url: str
    release_notes: str
    is_newer: bool


@runtime_checkable
class UpdateSource(Protocol):
    """Protocolo para fuentes de actualizaciones.

    Implementaciones:
      - GitHubUpdateSource: usa GitHub Releases API (hoy)
      - ServerUpdateSource: usa servidor propio (futuro)

    El servidor propio debe exponer un endpoint GET que devuelva el
    mismo formato JSON que GitHub Releases, o al menos los campos:
      tag_name, html_url, body, assets[].name, assets[].browser_download_url
    """

    def fetch_latest(self) -> dict[str, Any] | None:
        """Retorna el JSON del release más reciente, o None si falla.

        NUNCA debe lanzar excepciones — capturar todo error de red y
        retornar None. La UI interpreta None como "no se pudo verificar".
        """
        ...


class GitHubUpdateSource:
    """Fuente de actualizaciones via GitHub Releases API.

    URL configurada por default en `__version__.__update_url__`. Pasar
    una URL custom es útil para tests (apuntar a un mock server) o si
    se quiere consultar un repo distinto al configurado en el proyecto.
    """

    def __init__(self, url: str = __update_url__) -> None:
        self._url = url

    def fetch_latest(self) -> dict[str, Any] | None:
        try:
            r = requests.get(
                self._url,
                timeout=CHECK_TIMEOUT,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "CollectionsApp",
                },
            )
            if r.status_code != 200:
                logger.debug("GitHubUpdateSource HTTP %s", r.status_code)
                return None
            data: dict[str, Any] = dict(r.json())
            return data
        except Exception as exc:  # noqa: BLE001 — la API debe ser silenciosa
            logger.debug("GitHubUpdateSource fetch failed: %s", exc)
            return None


class ServerUpdateSource:
    """Fuente de actualizaciones via servidor propio (futuro).

    El servidor debe exponer:
      GET <server_url>/api/v1/updates/latest
      Authorization: Bearer <api_key>   (solo si api_key no es vacío)

    Respuesta esperada (mismo formato que GitHub Releases):
        {
          "tag_name": "v1.2.0",
          "html_url": "https://tuservidor.com/releases/v1.2.0",
          "body": "Changelog...",
          "assets": [
            {
              "name": "collections-client.exe",
              "browser_download_url": "https://tuservidor.com/dl/v1.2.0/collections-client.exe"
            }
          ]
        }
    """

    def __init__(self, server_url: str, api_key: str = "") -> None:
        self._url = server_url.rstrip("/") + "/api/v1/updates/latest"
        self._api_key = api_key

    def fetch_latest(self) -> dict[str, Any] | None:
        headers: dict[str, str] = {"User-Agent": "CollectionsApp"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        try:
            r = requests.get(self._url, timeout=CHECK_TIMEOUT, headers=headers)
            if r.status_code != 200:
                logger.debug("ServerUpdateSource HTTP %s", r.status_code)
                return None
            data: dict[str, Any] = dict(r.json())
            return data
        except Exception as exc:  # noqa: BLE001 — la API debe ser silenciosa
            logger.debug("ServerUpdateSource fetch failed: %s", exc)
            return None


class UpdateService:
    """Servicio de detección de actualizaciones.

    Usa `UpdateSource` (Protocol) para abstraer la fuente. Por defecto
    usa `GitHubUpdateSource`. Para usar servidor propio:

        service = UpdateService(
            source=ServerUpdateSource(
                server_url=settings.get("server_url"),
                api_key=settings.get("server_api_key") or "",
            )
        )
    """

    def __init__(self, source: UpdateSource | None = None) -> None:
        self._source: UpdateSource = source if source is not None else GitHubUpdateSource()

    def check_for_updates(self) -> UpdateInfo | None:
        """Verifica si hay una versión más nueva disponible.

        Retorna:
          - `UpdateInfo` con el resultado (puede tener `is_newer=False`
            si estamos al día — sirve para mostrar "estás actualizado").
          - `None` si la fuente falló (sin red, JSON inválido, version
            no parseable). La UI debe mostrar "no se pudo verificar".

        NO levanta excepciones.
        """
        data = self._source.fetch_latest()
        if not data:
            return None

        latest_tag = str(data.get("tag_name", "")).lstrip("v")
        if not latest_tag:
            return None

        try:
            current = Version(__version__)
            latest = Version(latest_tag)
        except InvalidVersion as exc:
            logger.debug("Version parse failed: %s", exc)
            return None

        # Buscar asset .exe; si no hay, caer a la página HTML del release.
        assets = data.get("assets", []) or []
        exe_asset = next(
            (a for a in assets if str(a.get("name", "")).endswith(".exe")),
            None,
        )
        release_url = str(data.get("html_url", ""))
        download_url = str(exe_asset["browser_download_url"]) if exe_asset else release_url

        return UpdateInfo(
            current_version=str(current),
            latest_version=str(latest),
            download_url=download_url,
            release_url=release_url,
            release_notes=str(data.get("body", ""))[:500],
            is_newer=latest > current,
        )
```

### [src/collections_app/core/utils/__init__.py](src/collections_app/core/utils/__init__.py)

```python
"""Utilidades: paths del SO, configuración de logging."""
```

### [src/collections_app/core/utils/datetime_helpers.py](src/collections_app/core/utils/datetime_helpers.py)

```python
"""Utilidades para manejo de timestamps.

Política del proyecto:
- La DB siempre guarda UTC (SQLite `datetime('now')` retorna UTC).
- Los `datetime` que circulan en código tienen `tzinfo=UTC`.
- La conversión a hora local sucede SOLO al mostrar al usuario.
"""

from datetime import UTC, datetime

DB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def utc_now() -> datetime:
    """Retorna el datetime actual en UTC con tzinfo."""
    return datetime.now(UTC)


def to_local(dt: datetime) -> datetime:
    """Convierte un datetime UTC a hora local del sistema.

    Si `dt` es naive (sin tzinfo), se asume que ya está en UTC.
    Solo debe usarse para display; nunca persistir el resultado.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone()


def parse_db_datetime(s: str) -> datetime:
    """Parsea un timestamp de SQLite (`YYYY-MM-DD HH:MM:SS`) como UTC.

    Acepta también el formato ISO con `T` y microsegundos por flexibilidad.
    """
    try:
        dt = datetime.strptime(s, DB_DATE_FORMAT)
    except ValueError:
        # Fallback: ISO format
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def format_for_db(dt: datetime) -> str:
    """Formatea un datetime para insertarlo como string en SQLite (UTC).

    Si el datetime es naive se asume UTC; si tiene tzinfo, se convierte a
    UTC antes de formatear.
    """
    if dt.tzinfo is None:
        return dt.strftime(DB_DATE_FORMAT)
    return dt.astimezone(UTC).strftime(DB_DATE_FORMAT)


def format_for_display(dt: datetime, with_seconds: bool = False) -> str:
    """Formatea un datetime para mostrar al usuario, en hora local."""
    local = to_local(dt)
    fmt = "%Y-%m-%d %H:%M:%S" if with_seconds else "%Y-%m-%d %H:%M"
    return local.strftime(fmt)
```

### [src/collections_app/core/utils/logging_setup.py](src/collections_app/core/utils/logging_setup.py)

```python
"""Configuración centralizada de logging."""

import logging
import logging.handlers
from pathlib import Path

from collections_app.core.utils.paths import get_logs_dir


def setup_logging(level: int = logging.INFO, log_filename: str = "app.log") -> None:
    """Configura logging para toda la app.

    Args:
        level: nivel de logging (logging.INFO, logging.DEBUG, etc.)
        log_filename: nombre del archivo de log
    """
    log_path: Path = get_logs_dir() / log_filename

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,  # 2 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    logging.getLogger(__name__).info("Logging inicializado en %s", log_path)
```

### [src/collections_app/core/utils/paths.py](src/collections_app/core/utils/paths.py)

```python
"""Resolver paths estándar de la aplicación.

Soporta múltiples PERFILES de datos en la misma máquina. Cada perfil
tiene su propia DB, escudos, imágenes y logs — útil para separar
"personal" / "test" / "trabajo" sin tener que copiar archivos.

El perfil se setea UNA VEZ al arranque vía `set_active_profile()`
(típicamente desde el `main()` parseando `--profile`). El default
("default") usa la carpeta base sin subdirectorio para mantener
compatibilidad retro con instalaciones existentes.
"""

import os
import sys
from pathlib import Path

# Perfil activo. Se setea desde main() al parsear --profile.
# "default" → no agrega subdirectorio (compat con instalaciones viejas).
_active_profile: str = "default"


def set_active_profile(profile: str) -> None:
    """Setea el perfil activo. Llamar al inicio del main() de la app.

    Sanitiza: solo alfanumérico y guiones; el resto se reemplaza por `_`.
    Si queda vacío tras strip, vuelve a "default".

    Cualquier llamada a `get_app_data_dir()` posterior reflejará el cambio.
    """
    global _active_profile
    safe = "".join(c if c.isalnum() or c == "-" else "_" for c in profile.strip()).strip("_")
    _active_profile = safe or "default"


def get_active_profile() -> str:
    """Retorna el perfil activo (default si no se llamó set_active_profile)."""
    return _active_profile


def _get_bundle_dir() -> Path:
    """Directorio base de los assets EMBEBIDOS en el paquete.

    Resolución según el entorno:
    - **Desarrollo / instalación pip**: la raíz del paquete `collections_app`
      (sube dos niveles desde `core/utils/paths.py`).
    - **PyInstaller onefile**: `sys._MEIPASS` (carpeta temporal donde el
      bootloader extrae los datos al arrancar el .exe).

    Solo afecta a recursos READ-ONLY que viajan con la app — los archivos
    SQL de migración, por ejemplo. Los datos del usuario (DB, escudos,
    cards descargadas) NO van por acá; siempre viven en
    `get_app_data_dir()`.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # En el bundle de PyInstaller los datas se montan en
        # sys._MEIPASS/<dest_path>. El spec mapea schema/ a
        # "collections_app/core/db/schema", así que la raíz del bundle
        # es _MEIPASS y el paquete sigue desde "collections_app/".
        return Path(sys._MEIPASS) / "collections_app"
    # `paths.py` vive en collections_app/core/utils/, así que hay que
    # subir tres niveles para llegar a la raíz del paquete.
    return Path(__file__).resolve().parent.parent.parent


def get_base_app_dir() -> Path:
    """Retorna la carpeta raíz `Collections` (sin subdirectorio de perfil).

    Útil para herramientas que necesitan listar todos los perfiles
    existentes (ver `ProfileService.get_all_profiles`).
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "Collections"


def get_app_data_dir() -> Path:
    r"""Retorna el directorio donde guardar datos del PERFIL ACTIVO.

    Layout:
      default:  %APPDATA%\Collections\
      personal: %APPDATA%\Collections\personal\
      test:     %APPDATA%\Collections\test\

    Las funciones derivadas (`get_database_path`, `get_crests_dir`,
    `get_generated_cards_dir`, `get_logs_dir`) heredan el perfil
    automáticamente.
    """
    app_dir = get_base_app_dir()
    if _active_profile != "default":
        app_dir = app_dir / _active_profile
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path(filename: str = "collections.db") -> Path:
    """Path al archivo de base de datos del usuario."""
    return get_app_data_dir() / filename


def get_logs_dir() -> Path:
    """Path al directorio de logs."""
    logs = get_app_data_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def get_schema_dir() -> Path:
    """Path al directorio con los SQLs de migración (dentro del paquete).

    Funciona tanto en desarrollo (paquete instalado) como en el .exe
    de PyInstaller (asset embebido en `_MEIPASS`).
    """
    return _get_bundle_dir() / "core" / "db" / "schema"


def get_crests_dir() -> Path:
    """Directorio donde el admin guarda los escudos por code_id.

    Un solo escudo por código (ej. `ARG.png`, `BRA.png`), compartido
    entre TODAS las colecciones que usen ese mismo header de códigos.
    """
    d = get_app_data_dir() / "crests"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_crest_path(code_id: str) -> Path:
    """Path al escudo de un code_id específico (puede no existir aún)."""
    return get_crests_dir() / f"{code_id}.png"


def get_generated_cards_dir() -> Path:
    """Directorio raíz para imágenes de cards descargadas/generadas.

    Cada colección ocupa una subcarpeta (`<id>/`); el scraper de Panini
    y otras herramientas escriben acá. Los archivos se nombran por
    `card_number` zero-padded a 4 dígitos (ej. `0042.jpg`).
    """
    d = get_app_data_dir() / "generated_cards"
    d.mkdir(parents=True, exist_ok=True)
    return d


def format_card_filename(card_number: int, extension: str = "jpg") -> str:
    """Retorna el nombre de archivo de una card con padding de 4 dígitos.

    El padding fijo evita que `1.jpg` y `001.jpg` convivan en la misma
    carpeta y se vea desordenado en el explorador. La DB sigue guardando
    el `card_number` como INTEGER — el padding solo aplica al filename.

    Ejemplo:
        format_card_filename(1)         -> "0001.jpg"
        format_card_filename(42, "png") -> "0042.png"
        format_card_filename(42, ".png") -> "0042.png"   # acepta con o sin punto
    """
    return f"{card_number:04d}.{extension.lstrip('.')}"


def get_card_image_path(
    collection_id: int,
    card_number: int,
    extension: str = "jpg",
) -> Path:
    """Retorna el path completo esperado de la imagen de una card.

    Útil para escribir o consultar un path determinístico. Si necesitás
    encontrar la imagen probando varias extensiones, usá `find_card_image`.

    Ejemplo:
        %APPDATA%/Collections/generated_cards/1/0042.jpg
    """
    return (
        get_generated_cards_dir()
        / str(collection_id)
        / format_card_filename(card_number, extension)
    )


def find_card_image(collection_id: int, card_number: int) -> Path | None:
    """Busca la imagen de una card probando extensiones comunes.

    Retorna el primer path que existe entre `.jpg`, `.jpeg`, `.png`.
    Retorna `None` si ninguno existe (la imagen aún no se descargó o
    se generó).
    """
    base_dir = get_generated_cards_dir() / str(collection_id)
    stem = f"{card_number:04d}"
    for ext in ("jpg", "jpeg", "png"):
        candidate = base_dir / f"{stem}.{ext}"
        if candidate.exists():
            return candidate
    return None
```

### [src/collections_app/shared_ui/__init__.py](src/collections_app/shared_ui/__init__.py)

```python
"""Capa de UI compartida entre admin y client."""

from collections_app.shared_ui.dialogs.settings_dialog import SettingsDialog
from collections_app.shared_ui.main_window_base import MainWindowBase
from collections_app.shared_ui.theme import (
    FontSize,
    Spacing,
    StatusColor,
    apply_app_style,
)
from collections_app.shared_ui.widgets.abm_widget import (
    AbmConfig,
    AbmWidget,
    FieldDef,
    FieldType,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

__all__ = [
    "AbmConfig",
    "AbmWidget",
    "EnterNavigator",
    "FieldDef",
    "FieldType",
    "FontSize",
    "MainWindowBase",
    "SettingsDialog",
    "Spacing",
    "StatusColor",
    "apply_app_style",
]
```

### [src/collections_app/shared_ui/dialogs/__init__.py](src/collections_app/shared_ui/dialogs/__init__.py)

```python
"""Diálogos reutilizables de la capa shared_ui."""
```

### [src/collections_app/shared_ui/dialogs/settings_dialog.py](src/collections_app/shared_ui/dialogs/settings_dialog.py)

```python
"""Diálogo de configuración: selección de la colección activa."""

import sqlite3

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import SettingsService
from collections_app.shared_ui.theme import Spacing


class SettingsDialog(QDialog):
    """Permite al usuario elegir la colección activa.

    Al aceptar persiste el setting con `SettingsService.set_active_collection`
    y commitea. Cancelar no toca el estado.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._settings = SettingsService(conn)
        self._collections_repo = CollectionsRepository(conn)
        self._selected_id: int | None = None

        self.setWindowTitle(self.tr("Configuración"))
        self._build_ui()
        self._load_collections()

    @property
    def selected_collection_id(self) -> int | None:
        """ID de la colección seleccionada al aceptar, o None si canceló."""
        return self._selected_id

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        root.setSpacing(Spacing.MD)

        form = QFormLayout()
        self._combo = QComboBox()
        self._combo.setMinimumWidth(280)
        form.addRow(self.tr("Colección activa") + ":", self._combo)
        root.addLayout(form)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._on_accept)
        self._buttons.rejected.connect(self.reject)
        root.addWidget(self._buttons)

    def _load_collections(self) -> None:
        self._combo.clear()
        self._combo.addItem(self.tr("(ninguna)"), userData=None)
        for col in self._collections_repo.list_all():
            self._combo.addItem(col.collection_name, userData=col.collection_id)

        active_id = self._settings.get_active_collection_id()
        if active_id is not None:
            idx = self._combo.findData(active_id)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)

    def _on_accept(self) -> None:
        chosen = self._combo.currentData()
        if chosen is None:
            self._settings.clear_active_collection()
        else:
            self._settings.set_active_collection(int(chosen))
        self._conn.commit()
        self._selected_id = chosen
        self.accept()
```

### [src/collections_app/shared_ui/main_window_base.py](src/collections_app/shared_ui/main_window_base.py)

```python
"""Base común de QMainWindow para admin y client."""

import logging
import sqlite3
from pathlib import Path

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.services import SettingsService

logger = logging.getLogger(__name__)


class MainWindowBase(QMainWindow):
    """Ventana base con conexión a DB, migraciones, status bar y menús.

    Las subclases deben overridear `_build_menus()` para agregar acciones
    propias. La conexión queda accesible via `self.conn` y se cierra
    automáticamente en `closeEvent`.
    """

    def __init__(self, db_path: Path, app_name: str = "Collections") -> None:
        super().__init__()
        self._app_name = app_name
        self.setWindowTitle(app_name)

        self._db_path = db_path
        self._conn = create_connection(db_path)
        run_migrations(self._conn)
        self._conn.commit()

        self._build_menus()
        self.statusBar()
        self._update_status_bar()

    @property
    def conn(self) -> sqlite3.Connection:
        """Conexión SQLite compartida para toda la ventana."""
        return self._conn

    @property
    def db_path(self) -> Path:
        """Path al archivo de DB. Útil para abrir conexiones nuevas en threads."""
        return self._db_path

    def _build_menus(self) -> None:
        """Hook para que subclases agreguen menús específicos."""
        file_menu = self.menuBar().addMenu(self.tr("&Archivo"))
        exit_action = file_menu.addAction(self.tr("Salir"))
        exit_action.triggered.connect(self.close)

    def _update_status_bar(self) -> None:
        """Refresca el texto de la status bar (colección activa)."""
        active = SettingsService(self._conn).get_active_collection()
        if active is None:
            text = self.tr("Colección activa: ninguna")
        else:
            text = self.tr("Colección activa: {name}").format(name=active.collection_name)
        self.statusBar().showMessage(text)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        try:
            self._conn.close()
        except Exception:
            logger.exception("Error cerrando conexión SQLite")
        super().closeEvent(event)
```

### [src/collections_app/shared_ui/theme.py](src/collections_app/shared_ui/theme.py)

```python
"""Constantes y helpers visuales reutilizables."""

from PySide6.QtWidgets import QApplication


class Spacing:
    """Constantes de espaciado en píxeles."""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24


class FontSize:
    """Tamaños de fuente en puntos."""

    SM = 11
    MD = 13
    LG = 16
    XL = 20


class StatusColor:
    """Colores semánticos sutiles para mensajes (no agresivos)."""

    SUCCESS = "#3B6D11"  # verde tenue (alta exitosa, "Nueva")
    INFO = "#1F4E79"  # azul tenue (info general)
    REPEATED = "#993C1D"  # coral tenue (card repetida en inventario)
    WARNING = "#854F0B"  # ámbar tenue (validación, input inválido)
    ERROR = "#A32D2D"  # rojo tenue (error de save, baja sin stock)


# Colores estructurales (header del ABM, fondos, etc.)
HEADER_BG = "#2B2B2B"
HEADER_FG = "#FFFFFF"
READONLY_BG = "#F0F0F0"

# Tintes pastel para los inputs según el modo Alta/Baja en CardLoader.
# Sirven como recordatorio visual constante (el usuario carga muchas
# cards seguidas y el radio button solo es una pista chica). Texto
# negro mantiene legibilidad total sobre ambos.
INPUT_BG_ALTA = "#D5F5E3"  # verde menta suave — modo Alta activo
INPUT_BG_BAJA = "#FADBD8"  # rosa salmón suave — modo Baja activo


def apply_app_style(app: QApplication) -> None:
    """Aplica el estilo de la app.

    Por ahora respeta el estilo nativo del SO. Si en el futuro se quiere
    forzar Fusion para uniformidad cross-platform: `app.setStyle("Fusion")`.
    """
    # Default: estilo nativo de Qt en cada plataforma.
    _ = app  # Placeholder para evitar warnings de variable no usada.
```

### [src/collections_app/shared_ui/widgets/__init__.py](src/collections_app/shared_ui/widgets/__init__.py)

```python
"""Widgets reutilizables de la capa shared_ui."""
```

### [src/collections_app/shared_ui/widgets/abm_widget.py](src/collections_app/shared_ui/widgets/abm_widget.py)

```python
"""Widget genérico de ABM (alta/baja/modificación) parametrizable.

El widget se construye a partir de una `AbmConfig` que define los campos del
formulario, callbacks de persistencia y el `model_class` a instanciar. La idea
es escribir un ABM nuevo configurando, no copiando código.

Layout (de arriba a abajo):
    Header oscuro:   Módulo: {title} ({module_code})
    Filtro:          Buscar: [____________]
    Body horizontal: [Listado QTableView] | [Formulario QFormLayout]
    Botonera:        [Guardar] [Nuevo] [Eliminar]
    Status:          mensaje no-bloqueante (warn/error)
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from PySide6.QtCore import (
    QItemSelection,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.shared_ui.theme import (
    HEADER_BG,
    HEADER_FG,
    READONLY_BG,
    Spacing,
    StatusColor,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator


class FieldType(StrEnum):
    """Tipos de campo soportados por el ABM."""

    TEXT = "text"
    INT = "int"
    BOOL = "bool"
    COMBO = "combo"
    READONLY = "readonly"


# Tipo para choices de COMBO: lista estática o callable que la genera al vuelo.
ComboChoices = list[tuple[str, Any]] | Callable[[], list[tuple[str, Any]]]


@dataclass(frozen=True)
class FieldDef:
    """Definición de un campo del ABM.

    Attributes:
        name: nombre del atributo en el modelo.
        label: texto del label visible.
        field_type: tipo del input (ver `FieldType`).
        is_id: si True, forma parte de la PK.
        is_required: si True, no puede estar vacío al guardar.
        max_length: longitud máxima del input TEXT.
        combo_choices: opciones del combo. Puede ser una lista estática
            `[(label_visible, value), ...]` o un callable que la retorna.
            Pasá un callable cuando los choices dependen de datos que
            pueden cambiar después de instanciar el widget; entonces
            `refresh_combo_choices()` (o las acciones que llaman a
            `clear_form` / `_populate_form`) re-evalúan el callable.
        placeholder: placeholder del input TEXT.
        show_in_grid: si False, el campo no aparece en la grilla.
        grid_width: ancho fijo de la columna en la grilla (px), opcional.
    """

    name: str
    label: str
    field_type: FieldType
    is_id: bool = False
    is_required: bool = True
    max_length: int | None = None
    combo_choices: ComboChoices | None = None
    placeholder: str = ""
    show_in_grid: bool = True
    grid_width: int | None = None
    # Valor inicial al hacer "Nuevo" — útil para INT (default numérico) o
    # COMBO (key seleccionada por default). Si es None, el widget arranca
    # con su default nativo de Qt (0 para SpinBox, primer item para Combo).
    default_value: Any = None


@dataclass
class AbmConfig:
    """Configuración completa de un ABM.

    Los callbacks son responsabilidad del caller. Los repositories no
    commitean: si `on_save` u `on_delete` involucra DB, debe commitear.
    """

    title: str
    module_code: str
    fields: list[FieldDef]
    on_load_all: Callable[[], list[Any]]
    on_save: Callable[[Any], Any]
    on_delete: Callable[[Any], bool]
    model_class: type
    list_label: str = "Listado"
    edit_label: str = "Edición"
    filter_label: str = "Buscar"
    filter_field: str | None = None
    on_validate: Callable[[Any], tuple[bool, str]] | None = None
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


class AbmWidget(QWidget):
    """Widget genérico que implementa el patrón ABM (filtro + grilla + form)."""

    record_saved = Signal(object)
    record_deleted = Signal(object)
    grid_selection_changed = Signal(object)

    def __init__(self, config: AbmConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.config = config
        self._current_record: Any | None = None
        self._inputs: dict[str, QWidget] = {}
        self._grid_columns: list[FieldDef] = [f for f in config.fields if f.show_in_grid]
        self._id_fields: list[FieldDef] = [f for f in config.fields if f.is_id]
        self._navigator = EnterNavigator(self)

        self._build_ui()
        self._wire_navigator()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """Recarga la grilla desde `on_load_all`."""
        self._grid_model.removeRows(0, self._grid_model.rowCount())
        for rec in self.config.on_load_all():
            self._append_record_to_grid(rec)

    def select_record(self, record: Any) -> None:
        """Selecciona una fila específica y carga el form."""
        for row in range(self._grid_model.rowCount()):
            stored = self._grid_model.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if self._records_equal(stored, record):
                source_index = self._grid_model.index(row, 0)
                proxy_index = self._proxy_model.mapFromSource(source_index)
                self._grid_view.selectRow(proxy_index.row())
                self._current_record = stored
                self._populate_form(stored)
                return

    def clear_form(self) -> None:
        """Limpia el formulario para crear un registro nuevo.

        Antes de limpiar, re-evalúa los `combo_choices` que sean callables
        para reflejar cambios en otros tabs sin reconstruir el widget.
        """
        self.refresh_combo_choices()
        self._current_record = None
        self._grid_view.clearSelection()
        for fdef in self.config.fields:
            self._set_input_value(fdef, None)
        self._update_pk_editability()
        self._set_status("", "")
        first_editable = self._first_editable_input()
        if first_editable is not None:
            first_editable.setFocus()

    def refresh_combo_choices(self) -> None:
        """Re-popula los QComboBox del form llamando los callables.

        Preserva el valor seleccionado actual si todavía existe en los
        nuevos choices; si no, queda en el primer item (o vacío si no hay).
        Los `combo_choices` que son listas estáticas también se repueblan,
        pero no cambian — esto es seguro y mantiene la lógica simple.
        """
        for fdef in self.config.fields:
            if fdef.field_type != FieldType.COMBO:
                continue
            widget = self._inputs.get(fdef.name)
            if not isinstance(widget, QComboBox):
                continue
            previous = widget.currentData()
            new_choices = self._resolve_combo_choices(fdef)
            widget.blockSignals(True)
            widget.clear()
            for label, value in new_choices:
                widget.addItem(label, userData=value)
            if previous is not None:
                idx = widget.findData(previous)
                if idx >= 0:
                    widget.setCurrentIndex(idx)
            widget.blockSignals(False)

    def _resolve_combo_choices(self, fdef: FieldDef) -> list[tuple[str, Any]]:
        choices = fdef.combo_choices
        if choices is None:
            return []
        if callable(choices):
            return list(choices())
        return list(choices)

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addWidget(self._build_filter_row())
        root.addWidget(self._build_body(), stretch=1)
        root.addWidget(self._build_status_bar())

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setStyleSheet(
            f"background-color: {HEADER_BG}; color: {HEADER_FG};"
            f" padding: {Spacing.SM}px {Spacing.MD}px;"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        title = QLabel(
            self.tr("Módulo: {title} ({code})").format(
                title=self.config.title,
                code=self.config.module_code,
            )
        )
        title.setStyleSheet(f"color: {HEADER_FG}; font-weight: bold;")
        layout.addWidget(title)
        layout.addStretch()
        return header

    def _build_filter_row(self) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        layout.addStretch()
        layout.addWidget(QLabel(self.tr(self.config.filter_label) + ":"))
        self._filter_input = QLineEdit()
        self._filter_input.setMinimumWidth(220)
        self._filter_input.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter_input)
        return row

    def _build_body(self) -> QWidget:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_grid_panel())
        splitter.addWidget(self._build_form_panel())
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        return splitter

    def _build_grid_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(Spacing.MD, Spacing.XS, Spacing.SM, Spacing.SM)

        layout.addWidget(QLabel(self.tr(self.config.list_label)))

        self._grid_model = QStandardItemModel(0, len(self._grid_columns), self)
        self._grid_model.setHorizontalHeaderLabels([self.tr(c.label) for c in self._grid_columns])

        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._grid_model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._configure_filter_column()

        self._grid_view = QTableView()
        self._grid_view.setModel(self._proxy_model)
        self._grid_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._grid_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self._grid_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._grid_view.verticalHeader().setVisible(False)
        self._grid_view.horizontalHeader().setStretchLastSection(True)
        self._grid_view.clicked.connect(self._on_row_clicked)
        self._grid_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        for i, col in enumerate(self._grid_columns):
            if col.grid_width:
                self._grid_view.horizontalHeader().resizeSection(i, col.grid_width)
            else:
                self._grid_view.horizontalHeader().setSectionResizeMode(
                    i, QHeaderView.ResizeMode.Interactive
                )
        layout.addWidget(self._grid_view)
        return panel

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(Spacing.SM, Spacing.XS, Spacing.MD, Spacing.SM)

        layout.addWidget(QLabel(self.tr(self.config.edit_label)))

        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        for fdef in self.config.fields:
            widget = self._build_input(fdef)
            self._inputs[fdef.name] = widget
            form.addRow(self.tr(fdef.label) + ":", widget)
        layout.addWidget(form_container)

        layout.addLayout(self._build_buttons())
        layout.addStretch()
        return panel

    def _build_input(self, fdef: FieldDef) -> QWidget:
        match fdef.field_type:
            case FieldType.TEXT | FieldType.READONLY:
                line = QLineEdit()
                if fdef.placeholder:
                    line.setPlaceholderText(fdef.placeholder)
                if fdef.max_length:
                    line.setMaxLength(fdef.max_length)
                if fdef.field_type == FieldType.READONLY:
                    line.setReadOnly(True)
                    line.setStyleSheet(f"background-color: {READONLY_BG};")
                return line
            case FieldType.INT:
                spin = QSpinBox()
                spin.setRange(0, 999_999)
                if fdef.default_value is not None:
                    spin.setValue(int(fdef.default_value))
                return spin
            case FieldType.BOOL:
                return QCheckBox()
            case FieldType.COMBO:
                combo = QComboBox()
                for label, value in self._resolve_combo_choices(fdef):
                    combo.addItem(label, userData=value)
                if fdef.default_value is not None:
                    idx = combo.findData(fdef.default_value)
                    if idx >= 0:
                        combo.setCurrentIndex(idx)
                return combo

    def _build_buttons(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self._save_button = QPushButton(self.tr("Guardar"))
        self._new_button = QPushButton(self.tr("Nuevo"))
        self._delete_button = QPushButton(self.tr("Eliminar"))
        self._save_button.clicked.connect(self._on_save_clicked)
        self._new_button.clicked.connect(self.clear_form)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        layout.addWidget(self._save_button)
        layout.addWidget(self._new_button)
        layout.addWidget(self._delete_button)
        layout.addStretch()
        return layout

    def _build_status_bar(self) -> QWidget:
        self._status_label = QLabel("")
        self._status_label.setContentsMargins(Spacing.MD, Spacing.XS, Spacing.MD, Spacing.XS)
        return self._status_label

    # ------------------------------------------------------------------
    # Eventos / callbacks
    # ------------------------------------------------------------------

    def _on_row_clicked(self, proxy_index: QModelIndex) -> None:
        source_index = self._proxy_model.mapToSource(proxy_index)
        record = self._grid_model.item(source_index.row(), 0).data(Qt.ItemDataRole.UserRole)
        self._current_record = record
        self._populate_form(record)
        self._set_status("", "")

    def _on_selection_changed(
        self,
        selected: QItemSelection,
        deselected: QItemSelection,
    ) -> None:
        del deselected  # parámetro requerido por la signature de Qt
        indexes = selected.indexes()
        if not indexes:
            return
        proxy_idx = indexes[0]
        if not proxy_idx.isValid():
            return
        source_idx = self._proxy_model.mapToSource(proxy_idx)
        record = self._grid_model.item(source_idx.row(), 0).data(Qt.ItemDataRole.UserRole)
        if record is not None:
            self.grid_selection_changed.emit(record)

    def _on_save_clicked(self) -> None:
        record, error = self._build_model_from_form()
        if record is None:
            self._set_status(error, StatusColor.WARNING)
            return

        if self.config.on_validate is not None:
            ok, reason = self.config.on_validate(record)
            if not ok:
                self._set_status(reason, StatusColor.WARNING)
                return

        try:
            saved = self.config.on_save(record)
        except Exception as exc:  # noqa: BLE001 — mostramos cualquier error al usuario
            self._set_status(str(exc), StatusColor.ERROR)
            return

        self.refresh()
        self.select_record(saved)
        self.record_saved.emit(saved)
        self._set_status("", "")

    def _on_delete_clicked(self) -> None:
        if self._current_record is None:
            self._set_status(
                self.tr("No hay registro seleccionado."),
                StatusColor.WARNING,
            )
            return

        record = self._current_record
        name = self._record_label(record)
        confirmed = QMessageBox.question(
            self,
            self.tr("Eliminar"),
            self.tr("¿Eliminar registro {name}?").format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmed != QMessageBox.StandardButton.Yes:
            return

        try:
            ok = self.config.on_delete(record)
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), StatusColor.ERROR)
            return

        if not ok:
            self._set_status(self.tr("No se pudo eliminar."), StatusColor.WARNING)
            return

        self.record_deleted.emit(record)
        self.clear_form()
        self.refresh()

    def _apply_filter(self, text: str) -> None:
        self._proxy_model.setFilterFixedString(text)

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _configure_filter_column(self) -> None:
        if self.config.filter_field is None:
            self._proxy_model.setFilterKeyColumn(-1)
            return
        for i, col in enumerate(self._grid_columns):
            if col.name == self.config.filter_field:
                self._proxy_model.setFilterKeyColumn(i)
                return
        self._proxy_model.setFilterKeyColumn(-1)

    def _wire_navigator(self) -> None:
        chain: list[QWidget] = []
        for fdef in self.config.fields:
            widget = self._inputs[fdef.name]
            if fdef.field_type == FieldType.READONLY:
                continue
            chain.append(widget)
        self._navigator.set_chain(chain)
        self._navigator.on_last_enter = self._save_button.setFocus
        self._navigator.install()

    def _append_record_to_grid(self, record: Any) -> None:
        items: list[QStandardItem] = []
        for i, col in enumerate(self._grid_columns):
            value = getattr(record, col.name)
            item = QStandardItem(self._format_for_grid(col, value))
            item.setEditable(False)
            if i == 0:
                item.setData(record, Qt.ItemDataRole.UserRole)
            items.append(item)
        self._grid_model.appendRow(items)

    def _format_for_grid(self, fdef: FieldDef, value: Any) -> str:
        if value is None:
            return ""
        if fdef.field_type == FieldType.BOOL:
            return self.tr("Sí") if value else self.tr("No")
        if fdef.field_type == FieldType.COMBO:
            for label, val in self._resolve_combo_choices(fdef):
                if val == value:
                    return label
        return str(value)

    def _populate_form(self, record: Any) -> None:
        # Asegurar que los combos tengan los choices actuales antes de
        # intentar seleccionar un valor (puede haberse agregado un item
        # nuevo en otro tab desde la última vez).
        self.refresh_combo_choices()
        for fdef in self.config.fields:
            value = getattr(record, fdef.name, None)
            self._set_input_value(fdef, value)
        self._update_pk_editability()

    def _set_input_value(self, fdef: FieldDef, value: Any) -> None:
        widget = self._inputs[fdef.name]
        # Si no hay valor explícito y existe `default_value` definido, usarlo.
        # Esto hace que "Nuevo" pre-rellene los campos con sus defaults
        # (importante para INT y COMBO con valores semánticos como
        # `album_columns=3` o `album_orientation="portrait"`).
        if value is None and fdef.default_value is not None:
            value = fdef.default_value
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            assert isinstance(widget, QLineEdit)
            widget.setText("" if value is None else str(value))
        elif fdef.field_type == FieldType.INT:
            assert isinstance(widget, QSpinBox)
            widget.setValue(int(value) if value is not None else 0)
        elif fdef.field_type == FieldType.BOOL:
            assert isinstance(widget, QCheckBox)
            widget.setChecked(bool(value))
        elif fdef.field_type == FieldType.COMBO:
            assert isinstance(widget, QComboBox)
            idx = widget.findData(value)
            widget.setCurrentIndex(idx if idx >= 0 else 0)

    def _read_input(self, fdef: FieldDef, widget: QWidget) -> Any:
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            assert isinstance(widget, QLineEdit)
            return widget.text().strip() or None
        if fdef.field_type == FieldType.INT:
            assert isinstance(widget, QSpinBox)
            return widget.value()
        if fdef.field_type == FieldType.BOOL:
            assert isinstance(widget, QCheckBox)
            return widget.isChecked()
        if fdef.field_type == FieldType.COMBO:
            assert isinstance(widget, QComboBox)
            return widget.currentData()
        return None

    def _build_model_from_form(self) -> tuple[Any | None, str]:
        kwargs: dict[str, Any] = dict(self.config.extra_kwargs)
        for fdef in self.config.fields:
            widget = self._inputs[fdef.name]
            if fdef.field_type == FieldType.READONLY:
                if self._current_record is not None:
                    kwargs[fdef.name] = getattr(self._current_record, fdef.name)
                else:
                    kwargs[fdef.name] = None
                continue
            value = self._read_input(fdef, widget)
            if fdef.is_required and self._is_empty(fdef, value):
                return None, self.tr("El campo '{label}' es obligatorio").format(label=fdef.label)
            kwargs[fdef.name] = value

        try:
            return self.config.model_class(**kwargs), ""
        except (TypeError, ValueError) as exc:
            return None, str(exc)

    def _is_empty(self, fdef: FieldDef, value: Any) -> bool:
        if fdef.field_type in (FieldType.TEXT, FieldType.READONLY):
            return value is None or value == ""
        if fdef.field_type == FieldType.COMBO:
            return value is None
        return False

    def _update_pk_editability(self) -> None:
        """Hace readonly TODOS los campos `is_id` cuando se edita un existente.

        Soporta PK simple y compuesta. Cada tipo se maneja con la API
        adecuada: QLineEdit/QSpinBox vía setReadOnly, QComboBox/QCheckBox
        vía setEnabled (no tienen modo readonly nativo).
        """
        editing = self._current_record is not None
        for fdef in self.config.fields:
            if not fdef.is_id or fdef.field_type == FieldType.READONLY:
                continue
            widget = self._inputs[fdef.name]
            if isinstance(widget, (QLineEdit, QSpinBox)):
                widget.setReadOnly(editing)
                widget.setStyleSheet(f"background-color: {READONLY_BG};" if editing else "")
            elif isinstance(widget, (QComboBox, QCheckBox)):
                widget.setEnabled(not editing)

    def _first_editable_input(self) -> QWidget | None:
        for fdef in self.config.fields:
            if fdef.field_type == FieldType.READONLY:
                continue
            widget = self._inputs[fdef.name]
            if isinstance(widget, QLineEdit) and widget.isReadOnly():
                continue
            if isinstance(widget, QSpinBox) and widget.isReadOnly():
                continue
            if isinstance(widget, (QComboBox, QCheckBox)) and not widget.isEnabled():
                continue
            return widget
        return None

    def _records_equal(self, a: Any, b: Any) -> bool:
        if a is None or b is None:
            return False
        if self._id_fields:
            return all(getattr(a, f.name) == getattr(b, f.name) for f in self._id_fields)
        return bool(a == b)

    def _record_label(self, record: Any) -> str:
        # Buscar el primer campo show_in_grid no-id para mostrar
        for fdef in self.config.fields:
            if fdef.show_in_grid and not fdef.is_id:
                value = getattr(record, fdef.name, None)
                if value is not None:
                    return str(value)
        if self._id_fields:
            return ", ".join(str(getattr(record, f.name)) for f in self._id_fields)
        return str(record)

    def _set_status(self, message: str, color: str) -> None:
        self._status_label.setText(message)
        if color:
            self._status_label.setStyleSheet(f"color: {color};")
        else:
            self._status_label.setStyleSheet("")
```

### [src/collections_app/shared_ui/widgets/enter_navigator.py](src/collections_app/shared_ui/widgets/enter_navigator.py)

```python
"""Navegación con Enter entre widgets de un formulario."""

from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QWidget


class EnterNavigator(QObject):
    """Hace que `Enter` avance al siguiente widget de una cadena ordenada.

    En el último widget de la cadena, dispara `on_last_enter` (si está
    seteado). Funciona con cualquier QWidget; usa un `eventFilter` que
    detecta `QEvent.KeyPress` con `Key_Return` o `Key_Enter`.

    Uso típico:
        nav = EnterNavigator(self)
        nav.set_chain([self.code_input, self.number_input, self.qty_input])
        nav.on_last_enter = self._save_card
        nav.install()
    """

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._chain: list[QWidget] = []
        self.on_last_enter: Callable[[], None] | None = None
        self._installed = False

    def set_chain(self, widgets: list[QWidget]) -> None:
        """Define el orden de navegación. No instala los filters todavía."""
        self._chain = list(widgets)

    def install(self) -> None:
        """Instala el event filter en cada widget de la cadena."""
        if self._installed:
            return
        for widget in self._chain:
            widget.installEventFilter(self)
        self._installed = True

    def uninstall(self) -> None:
        """Desinstala los event filters (útil para tests o cleanup)."""
        if not self._installed:
            return
        for widget in self._chain:
            widget.removeEventFilter(self)
        self._installed = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Intercepta KeyPress de Enter/Return en la cadena."""
        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(watched, event)

        key_event = event
        if not isinstance(key_event, QKeyEvent):
            return super().eventFilter(watched, event)
        if key_event.key() not in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return super().eventFilter(watched, event)

        try:
            idx = self._chain.index(watched)  # type: ignore[arg-type]
        except ValueError:
            return super().eventFilter(watched, event)

        if idx == len(self._chain) - 1:
            if self.on_last_enter is not None:
                self.on_last_enter()
            return True

        self._chain[idx + 1].setFocus()
        return True
```

### [tests/__init__.py](tests/__init__.py)

_(archivo vacío)_

### [tests/admin/__init__.py](tests/admin/__init__.py)

_(archivo vacío)_

### [tests/admin/crests/__init__.py](tests/admin/crests/__init__.py)

_(archivo vacío)_

### [tests/admin/crests/test_crest_finder.py](tests/admin/crests/test_crest_finder.py)

```python
"""Tests del CrestFinder (Wikimedia Commons backend).

Cubre la cascada cache → SPECIAL → override → Commons search → not_found,
las heurísticas de filtrado y las validaciones defensivas de descarga.
"""

import io
import os
from unittest.mock import patch

import responses
from PIL import Image

from collections_app.admin.crests.crest_finder import (
    COMMONS_API_URL,
    COMMONS_FILE_OVERRIDES,
    COMMONS_USER_AGENT,
    MIN_VALID_FILE_BYTES,
    SOURCE_CACHE,
    SOURCE_COMMONS,
    SOURCE_COMMONS_OVERRIDE,
    SOURCE_NOT_FOUND,
    SOURCE_PLACEHOLDER,
    SPECIAL_CODES,
    CrestFinder,
    is_valid_crest_file,
)


def _png_bytes(w: int = 200, h: int = 200) -> bytes:
    """PNG RGBA con ruido (alta entropía → siempre > MIN_VALID_FILE_BYTES)."""
    img = Image.frombytes("RGBA", (w, h), os.urandom(w * h * 4))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _redirect_crest_paths(monkeypatch, tmp_path):
    """Hace que get_crests_dir y get_crest_path apunten a tmp_path."""
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crests_dir", lambda: tmp_path
    )
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )


def _no_query_delay(monkeypatch):
    """Evita el sleep entre queries en tests."""
    monkeypatch.setattr("collections_app.admin.crests.crest_finder.time.sleep", lambda _s: None)


# ----------------------------------------------------------------------
# Cache, SPECIAL_CODES, import manual, helpers básicos
# ----------------------------------------------------------------------


def test_uses_cache_if_crest_exists(tmp_path, monkeypatch):
    """Si el escudo ya está en disco y es válido, no toca la red."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    cached = tmp_path / "ARG.png"
    cached.write_bytes(_png_bytes())

    finder = CrestFinder()
    with responses.RequestsMock():  # explícito: no se debe llamar a nadie
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_CACHE
    assert result.local_path == cached


def test_special_codes_make_placeholder(tmp_path, monkeypatch):
    """code_id en SPECIAL_CODES → placeholder con iniciales, sin red."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    code_id = next(iter(SPECIAL_CODES))
    with responses.RequestsMock():
        result = finder.find_crest(code_id, code_id)

    assert result.source == SOURCE_PLACEHOLDER
    assert result.local_path.exists()


def test_pan_not_in_special_codes():
    assert "PAN" not in SPECIAL_CODES


def test_placeholder_meets_min_valid_file_size(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "PLH.png"
    finder._generate_placeholder_crest("PLH", dest)
    assert dest.stat().st_size > MIN_VALID_FILE_BYTES
    assert is_valid_crest_file(dest) is True


def test_import_manual_crest(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    src = tmp_path / "src.jpg"
    rgb = Image.new("RGB", (300, 300), (0, 0, 255))
    rgb.save(src, format="JPEG")

    finder = CrestFinder()
    result = finder.import_manual_crest("GBL", src)
    assert result.success is True
    saved = Image.open(result.local_path)
    assert saved.mode == "RGBA"


def test_is_valid_crest_file(tmp_path):
    missing = tmp_path / "missing.png"
    too_small = tmp_path / "small.png"
    too_small.write_bytes(b"x" * 100)
    big_enough = tmp_path / "ok.png"
    big_enough.write_bytes(b"x" * (MIN_VALID_FILE_BYTES + 1))

    assert is_valid_crest_file(missing) is False
    assert is_valid_crest_file(too_small) is False
    assert is_valid_crest_file(big_enough) is True


# ----------------------------------------------------------------------
# Validación defensiva en _download_and_process_crest
# ----------------------------------------------------------------------


def test_download_converts_to_rgba_png(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    img_url = "https://example.com/jpg-image.jpg"
    rgb = Image.frombytes("RGB", (200, 200), os.urandom(200 * 200 * 3))
    buf = io.BytesIO()
    rgb.save(buf, format="JPEG")

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=buf.getvalue(), status=200)
        ok = finder._download_and_process_crest(img_url, tmp_path / "BRA.png")

    assert ok is True
    saved = Image.open(tmp_path / "BRA.png")
    assert saved.mode == "RGBA"
    assert saved.format == "PNG"


def test_download_rejects_empty_response(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "EMP.png"
    img_url = "https://example.com/empty.png"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"", status=200)
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_download_rejects_html_content(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "HTM.png"
    img_url = "https://example.com/redirected.html"
    html = b"<html><body>" + (b"x" * 1000) + b"</body></html>"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=html, status=200, content_type="text/html")
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_download_rejects_too_small_response(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    dest = tmp_path / "SML.png"
    img_url = "https://example.com/tiny.png"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, img_url, body=b"x" * 200, status=200)
        ok = finder._download_and_process_crest(img_url, dest)
    assert ok is False
    assert not dest.exists()


def test_svg_detected_correctly():
    finder = CrestFinder()
    assert finder._is_svg(b'<?xml version="1.0"?><svg></svg>') is True
    assert finder._is_svg(b'<svg xmlns="http://www.w3.org/2000/svg"></svg>') is True
    assert finder._is_svg(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100) is False
    assert finder._is_svg(b"\xff\xd8\xff\xe0" + b"\x00" * 100) is False


def test_has_image_magic():
    finder = CrestFinder()
    assert finder._has_image_magic(b"\x89PNG\r\n\x1a\n") is True
    assert finder._has_image_magic(b"\xff\xd8\xff\xe0") is True
    assert finder._has_image_magic(b"GIF89a") is True
    assert finder._has_image_magic(b"RIFF\x00\x00\x00\x00WEBP") is True
    assert finder._has_image_magic(b"<html>") is False


# ----------------------------------------------------------------------
# Wikimedia Commons: _search_commons_files
# ----------------------------------------------------------------------


def _commons_search_response(titles: list[str]) -> dict:
    return {"query": {"search": [{"title": t} for t in titles]}}


def test_search_commons_files_returns_titles_on_success():
    titles_returned = [
        "File:Argentina FA logo.svg",
        "File:Brazil federation crest.svg",
        "File:France national football team logo.svg",
    ]
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_search_response(titles_returned),
            status=200,
        )
        titles = finder._search_commons_files("Argentina national football team", limit=5)
        # rsps.calls se vacía al salir del context — verificamos adentro
        assert len(rsps.calls) == 1
        assert rsps.calls[0].request.headers["User-Agent"] == COMMONS_USER_AGENT
        assert "commons.wikimedia.org/w/api.php" in rsps.calls[0].request.url

    assert titles == titles_returned


def test_search_commons_files_returns_empty_on_http_error():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, COMMONS_API_URL, json={}, status=500)
        titles = finder._search_commons_files("Argentina")
    assert titles == []


def test_search_commons_files_filters_out_non_crest_results():
    """La búsqueda devuelve fotos pero el filtro las descarta."""
    raw_titles = [
        "File:Argentina vs Brazil 2022 match.jpg",  # match → descarta
        "File:Argentina FA logo.svg",  # logo → pasa
        "File:Messi celebration.jpg",  # celebration → descarta
    ]
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_search_response(raw_titles),
            status=200,
        )
        titles = finder._search_commons_files("Argentina")
    assert titles == ["File:Argentina FA logo.svg"]


# ----------------------------------------------------------------------
# Wikimedia Commons: _get_commons_thumb_url
# ----------------------------------------------------------------------


def _commons_imageinfo_response(info: dict) -> dict:
    return {"query": {"pages": {"1": {"imageinfo": [info]}}}}


def test_get_commons_thumb_url_prefers_thumburl_over_url():
    """Cuando hay thumburl (PNG), se prefiere sobre url (puede ser SVG)."""
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_imageinfo_response(
                {
                    "thumburl": "https://upload.wikimedia.org/foo-300px.png",
                    "url": "https://upload.wikimedia.org/foo.svg",
                    "mime": "image/svg+xml",
                }
            ),
            status=200,
        )
        url = finder._get_commons_thumb_url("File:Foo.svg")
    assert url == "https://upload.wikimedia.org/foo-300px.png"


def test_get_commons_thumb_url_returns_url_when_not_svg():
    """Sin thumburl, si el original NO es SVG, lo devuelve directo."""
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json=_commons_imageinfo_response(
                {"url": "https://example.com/foo.png", "mime": "image/png"}
            ),
            status=200,
        )
        url = finder._get_commons_thumb_url("File:Foo.png")
    assert url == "https://example.com/foo.png"


def test_get_commons_thumb_url_returns_none_when_no_imageinfo():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            COMMONS_API_URL,
            json={"query": {"pages": {"1": {}}}},
            status=200,
        )
        url = finder._get_commons_thumb_url("File:NoExist.svg")
    assert url is None


def test_get_commons_thumb_url_returns_none_on_http_error():
    finder = CrestFinder()
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, COMMONS_API_URL, json={}, status=503)
        url = finder._get_commons_thumb_url("File:Foo.svg")
    assert url is None


# ----------------------------------------------------------------------
# Heurística _is_likely_crest_file
# ----------------------------------------------------------------------


def test_is_likely_crest_file_accepts_logo_or_crest():
    f = CrestFinder()
    assert f._is_likely_crest_file("File:Argentina FA logo.svg") is True
    assert f._is_likely_crest_file("File:Brazil_national_football_team_crest.svg") is True
    assert f._is_likely_crest_file("File:Federation logo.png") is True
    assert f._is_likely_crest_file("File:Football association badge.svg") is True


def test_is_likely_crest_file_rejects_match_or_player_photo():
    f = CrestFinder()
    assert f._is_likely_crest_file("File:Argentina vs Brazil 2022 match.jpg") is False
    assert f._is_likely_crest_file("File:Messi celebration logo.jpg") is False
    assert f._is_likely_crest_file("File:Stadium logo.jpg") is False
    assert f._is_likely_crest_file("File:Players training crest.jpg") is False
    assert f._is_likely_crest_file("File:Random photo.jpg") is False  # ni crest


# ----------------------------------------------------------------------
# Cascada de find_crest
# ----------------------------------------------------------------------


def test_find_crest_uses_override_when_present(tmp_path, monkeypatch):
    """Si hay override en COMMONS_FILE_OVERRIDES, se usa sin buscar."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)
    monkeypatch.setitem(COMMONS_FILE_OVERRIDES, "TESTLAND", "File:Testland.svg")

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_get_commons_thumb_url", return_value="https://example.com/x.png"
        ) as mock_url,
        patch.object(finder, "_download_and_process_crest", return_value=True) as mock_dl,
        patch.object(finder, "_search_commons_files") as mock_search,
    ):
        result = finder.find_crest("TST", "TESTLAND")

    mock_url.assert_called_once_with("File:Testland.svg")
    mock_dl.assert_called_once()
    mock_search.assert_not_called()  # NO se buscó porque hubo override
    assert result.source == SOURCE_COMMONS_OVERRIDE
    assert result.success is True


def test_find_crest_falls_back_to_search_when_no_override(tmp_path, monkeypatch):
    """Sin override, se itera sobre la cascada de queries."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_search_commons_files", return_value=["File:Argentina FA logo.svg"]
        ) as mock_search,
        patch.object(finder, "_get_commons_thumb_url", return_value="https://example.com/arg.png"),
        patch.object(finder, "_download_and_process_crest", return_value=True),
    ):
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_COMMONS
    assert result.success is True
    mock_search.assert_called()  # se buscó


def test_find_crest_returns_not_found_when_all_queries_fail(tmp_path, monkeypatch):
    """Cuando todas las queries fallan, NO se escribe archivo (permite reintento)."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with patch.object(finder, "_search_commons_files", return_value=[]):
        result = finder.find_crest("XYZ", "FAKELAND")

    assert result.source == SOURCE_NOT_FOUND
    assert result.success is False
    assert (
        not result.local_path.exists()
    ), "find_crest no debe escribir archivo cuando no hay resultado"


def test_find_crest_returns_not_found_when_all_downloads_fail(tmp_path, monkeypatch):
    """Si Commons devuelve titles pero ninguna descarga sale → NOT_FOUND."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    with (
        patch.object(
            finder, "_search_commons_files", return_value=["File:Foo.svg", "File:Bar.svg"]
        ),
        patch.object(finder, "_get_commons_thumb_url", return_value="https://example.com/x.png"),
        patch.object(finder, "_download_and_process_crest", return_value=False),
    ):
        result = finder.find_crest("ARG", "ARGENTINA")

    assert result.source == SOURCE_NOT_FOUND
    assert not result.local_path.exists()


def test_not_found_crest_is_retried_next_time(tmp_path, monkeypatch):
    """Después de NOT_FOUND, la siguiente llamada vuelve a buscar (no devuelve cache)."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    _no_query_delay(monkeypatch)

    finder = CrestFinder()
    call_count = {"n": 0}

    def fake_search(_q: str, limit: int = 5) -> list[str]:
        del limit
        call_count["n"] += 1
        return []

    with patch.object(finder, "_search_commons_files", side_effect=fake_search):
        first = finder.find_crest("ARG", "ARGENTINA")
        before = call_count["n"]
        second = finder.find_crest("ARG", "ARGENTINA")

    assert first.source == SOURCE_NOT_FOUND
    assert second.source == SOURCE_NOT_FOUND
    # La SEGUNDA llamada efectivamente reintentó búsqueda — no devolvió cache
    assert call_count["n"] > before


def test_find_crest_special_codes_make_placeholder(tmp_path, monkeypatch):
    """SPECIAL_CODES SÍ siguen escribiendo placeholder en disco (recordatorio)."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    result = finder.find_crest("GBL", "Golden Ballers")

    assert result.source == SOURCE_PLACEHOLDER
    assert result.success is True
    assert result.local_path.exists()
    assert result.local_path.stat().st_size > MIN_VALID_FILE_BYTES


def test_find_crest_skips_search_for_special_codes(tmp_path, monkeypatch):
    """Para SPECIAL_CODES, _search_commons_files NO se llama."""
    _redirect_crest_paths(monkeypatch, tmp_path)

    finder = CrestFinder()
    with patch.object(finder, "_search_commons_files") as mock_search:
        finder.find_crest("GBL", "Golden Ballers")

    mock_search.assert_not_called()


def test_user_agent_is_descriptive():
    """El User-Agent debe identificar la app, no ser el genérico de requests."""
    assert "CollectionsApp" in COMMONS_USER_AGENT
    assert "python-requests" not in COMMONS_USER_AGENT.lower()


# ----------------------------------------------------------------------
# cleanup_failed_placeholders
# ----------------------------------------------------------------------


def test_cleanup_failed_placeholders_deletes_non_special(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    arg = tmp_path / "ARG.png"
    gbl = tmp_path / "GBL.png"
    arg.write_bytes(b"placeholder-arg")
    gbl.write_bytes(b"placeholder-gbl")

    finder = CrestFinder()
    deleted = finder.cleanup_failed_placeholders([("ARG", "Argentina"), ("GBL", "Golden Ballers")])

    assert deleted == 1
    assert not arg.exists(), "Placeholder de ARG (no special) debió borrarse"
    assert gbl.exists(), "Placeholder de GBL (special) NO debe borrarse"


def test_cleanup_failed_placeholders_returns_zero_when_no_files(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    finder = CrestFinder()
    deleted = finder.cleanup_failed_placeholders([("ARG", "Argentina"), ("BRA", "Brazil")])
    assert deleted == 0


# ----------------------------------------------------------------------
# find_all_crests
# ----------------------------------------------------------------------


def test_find_all_respects_rate_limiting(tmp_path, monkeypatch):
    _redirect_crest_paths(monkeypatch, tmp_path)
    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    finder = CrestFinder()
    # Sin red real: _search_commons_files retorna [] sin tocar HTTP.
    with patch.object(finder, "_search_commons_files", return_value=[]):
        finder.find_all_crests([("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("FRA", "FRANCE")])

    # Hubo dos sleeps a 1.0s (rate limit entre find_crest reales). También hubo
    # sleeps a 0.5s entre queries del find_crest (QUERY_DELAY). Verificamos
    # solo los del rate-limit.
    rate_sleeps = [s for s in sleep_calls if s >= 1.0]
    assert len(rate_sleeps) == 2


def test_find_all_does_not_sleep_for_cached_or_special(tmp_path, monkeypatch):
    """No se aplica rate-limit para entradas cacheadas o SPECIAL."""
    _redirect_crest_paths(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(_png_bytes())

    sleep_calls: list[float] = []
    monkeypatch.setattr(
        "collections_app.admin.crests.crest_finder.time.sleep",
        lambda s: sleep_calls.append(s),
    )

    finder = CrestFinder()
    finder.find_all_crests([("ARG", "ARGENTINA"), ("GBL", "Global")])

    # Ningún rate-limit (1.0s) — solo cache hit y SPECIAL. Tampoco hubo
    # query loops para meter delays de 0.5s.
    assert sleep_calls == []
```

### [tests/admin/tools/__init__.py](tests/admin/tools/__init__.py)

_(archivo vacío)_

### [tests/admin/tools/test_codes_csv_importer.py](tests/admin/tools/test_codes_csv_importer.py)

```python
"""Tests del CodesCsvImporter."""

from pathlib import Path

import pytest

from collections_app.admin.tools.codes_csv_importer import CodesCsvImporter
from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_import_valid_csv(memory_db, sample_code_header):
    """Importa el sample completo respetando code_max_length=5."""
    result = CodesCsvImporter(memory_db).import_file(
        FIXTURES / "sample_codes.csv",
        sample_code_header.code_header_id,
    )
    assert result.total_rows == 4
    assert result.imported == 4
    assert result.skipped == 0
    assert result.errors == []
    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    assert len(lines) == 4
    codes = {line.code_id for line in lines}
    assert codes == {"ARG", "BRA", "FRA", "ESP"}


def test_import_skips_codes_exceeding_max_length(memory_db, sample_code_header, tmp_path):
    """sample_code_header tiene max_length=5; 'ABCDEFG' (7 chars) debe omitirse."""
    csv = tmp_path / "long.csv"
    csv.write_text(
        "code_id,code_name,code_order\n"
        "ARG,Argentina,1\n"
        "ABCDEFG,Demasiado,2\n"
        "BRA,Brasil,3\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.total_rows == 3
    assert result.imported == 2
    assert result.skipped == 1
    assert any("ABCDEFG" in e for e in result.errors)
    assert any("max_length" in e for e in result.errors)


def test_import_overwrites_existing(memory_db, sample_code_header, tmp_path):
    """Códigos existentes se actualizan vía upsert."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Old Name", code_order=99))
    memory_db.commit()

    csv = tmp_path / "update.csv"
    csv.write_text("ARG,Argentina,1\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, hid)

    assert result.imported == 1
    fresh = repo.get(hid, "ARG")
    assert fresh is not None
    assert fresh.code_name == "Argentina"
    assert fresh.code_order == 1


def test_import_handles_unicode(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "unicode.csv"
    csv.write_text(
        "code_id,code_name,code_order\n" "ARG,Árgentîna,1\n" "ESP,España,2\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 2
    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    names = {line.code_name for line in lines}
    assert "Árgentîna" in names
    assert "España" in names


def test_import_with_progress(memory_db, sample_code_header):
    progress_calls: list[tuple[int, int]] = []
    CodesCsvImporter(memory_db).import_file(
        FIXTURES / "sample_codes.csv",
        sample_code_header.code_header_id,
        on_progress=lambda c, t: progress_calls.append((c, t)),
    )
    assert len(progress_calls) == 4
    assert progress_calls[-1] == (4, 4)


def test_import_rejects_unknown_header(memory_db):
    with pytest.raises(ValueError, match="no existe"):
        CodesCsvImporter(memory_db).import_file(FIXTURES / "sample_codes.csv", 999)


def test_import_handles_missing_header_row(memory_db, sample_code_header, tmp_path):
    """Si la primera fila no es header, se trata como dato."""
    csv = tmp_path / "no_header.csv"
    csv.write_text("ARG,Argentina,1\nBRA,Brasil,2\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.total_rows == 2
    assert result.imported == 2


def test_import_skips_empty_code_id(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "empty_id.csv"
    csv.write_text(",Empty,1\nARG,Argentina,2\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 1
    assert result.skipped == 1


def test_import_uses_default_order_when_missing(memory_db, sample_code_header, tmp_path):
    csv = tmp_path / "no_order.csv"
    csv.write_text("ARG,Argentina\n", encoding="utf-8")
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 1
    line = CodesLinesRepository(memory_db).get(sample_code_header.code_header_id, "ARG")
    assert line is not None
    assert line.code_order == 0


def test_import_csv_without_max_length_column(memory_db, sample_code_header, tmp_path):
    """El formato nuevo (3 columnas) importa sin warnings ni errores."""
    csv = tmp_path / "new_format.csv"
    csv.write_text(
        "code_id,code_name,code_order\n" "ARG,Argentina,1\n" "BRA,Brasil,2\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 2
    assert result.skipped == 0
    assert result.errors == []


def test_import_csv_with_max_length_column_ignored(memory_db, sample_code_header, tmp_path):
    """El formato viejo (con code_max_length) sigue importando; la columna se ignora."""
    csv = tmp_path / "old_format.csv"
    csv.write_text(
        "code_id,code_name,code_order,code_max_length\n" "ARG,Argentina,1,5\n" "BRA,Brasil,2,5\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 2
    assert result.skipped == 0
    assert result.errors == []
    line = CodesLinesRepository(memory_db).get(sample_code_header.code_header_id, "ARG")
    assert line is not None
    assert line.code_name == "Argentina"
    assert line.code_order == 1


def test_import_csv_columns_in_different_order(memory_db, sample_code_header, tmp_path):
    """Con header, las columnas se mapean por nombre, no por posición."""
    csv = tmp_path / "reordered.csv"
    csv.write_text(
        "code_order,code_name,code_id\n" "1,Argentina,ARG\n",
        encoding="utf-8",
    )
    result = CodesCsvImporter(memory_db).import_file(csv, sample_code_header.code_header_id)
    assert result.imported == 1
    line = CodesLinesRepository(memory_db).get(sample_code_header.code_header_id, "ARG")
    assert line is not None
    assert line.code_name == "Argentina"
    assert line.code_order == 1
```

### [tests/admin/tools/test_csv_importer.py](tests/admin/tools/test_csv_importer.py)

```python
"""Tests del CardsCsvImporter."""

from pathlib import Path

import pytest

from collections_app.admin.tools.csv_importer import CardsCsvImporter
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.fixture
def collection_with_codes(memory_db, sample_collection):
    """Carga ARG/BRA/FRA en codes_lines del header de la collection."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in ("ARG", "BRA", "FRA"):
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()
    return sample_collection


def test_import_valid_csv(memory_db, collection_with_codes):
    importer = CardsCsvImporter(memory_db)
    result = importer.import_file(
        FIXTURES / "sample_cards.csv",
        collection_with_codes.collection_id,
    )
    assert result.total_rows == 10
    assert result.imported == 10
    assert result.skipped == 0
    assert result.errors == []
    cards = CardsRepository(memory_db).list_by_collection(collection_with_codes.collection_id)
    assert len(cards) == 10


def test_import_skips_invalid_code_id(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "bad_codes.csv"
    csv.write_text(
        "code_id,card_number,card_name\n" "ARG,1,Messi\n" "ZZZ,1,Desconocido\n" "BRA,1,Vinicius\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 3
    assert result.imported == 2
    assert result.skipped == 1
    assert any("ZZZ" in e for e in result.errors)


def test_import_handles_missing_header_row(memory_db, collection_with_codes, tmp_path):
    """Si la primera fila no es header, se trata como dato."""
    csv = tmp_path / "no_header.csv"
    csv.write_text(
        "ARG,1,Messi\nBRA,2,Neymar\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 2
    assert result.imported == 2


def test_import_handles_unicode_names_with_accents(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "unicode.csv"
    csv.write_text(
        "code_id,card_number,card_name\n" "ARG,1,Ángel Di María\n" "FRA,2,Kylian Mbappé\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 2
    cards = CardsRepository(memory_db).list_by_collection(collection_with_codes.collection_id)
    names = {c.card_name for c in cards}
    assert "Ángel Di María" in names
    assert "Kylian Mbappé" in names


def test_import_with_progress_callback(memory_db, collection_with_codes):
    progress_calls: list[tuple[int, int]] = []
    CardsCsvImporter(memory_db).import_file(
        FIXTURES / "sample_cards.csv",
        collection_with_codes.collection_id,
        on_progress=lambda c, t: progress_calls.append((c, t)),
    )
    assert len(progress_calls) == 10
    assert progress_calls[-1] == (10, 10)


def test_import_skips_invalid_card_number(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "bad_num.csv"
    csv.write_text(
        "ARG,abc,X\nARG,-1,Y\nARG,5,Z\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    assert result.skipped == 2


def test_import_accepts_card_number_zero(memory_db, collection_with_codes, tmp_path):
    """card_number=0 es válido (típicamente la portada del álbum)."""
    csv = tmp_path / "zero.csv"
    csv.write_text(
        "code_id,card_number,card_name\nARG,0,Album Cover\nARG,1,Messi\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 2
    assert result.skipped == 0
    cards = CardsRepository(memory_db).list_by_collection(collection_with_codes.collection_id)
    assert any(c.card_number == 0 and c.card_name == "Album Cover" for c in cards)


def test_import_skips_empty_name(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "empty_name.csv"
    csv.write_text(
        "ARG,1,\nARG,2,Messi\n",
        encoding="utf-8",
    )
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    assert result.skipped == 1


def test_import_rejects_unknown_collection(memory_db):
    importer = CardsCsvImporter(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        importer.import_file(FIXTURES / "sample_cards.csv", 999)


def test_import_empty_csv(memory_db, collection_with_codes, tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("", encoding="utf-8")
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.total_rows == 0
    assert result.imported == 0


def test_import_overwrites_existing_card(memory_db, collection_with_codes, tmp_path):
    """bulk_upsert debe sobrescribir el card_name si la card ya existía."""
    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(collection_with_codes.collection_id, "ARG", 1, "Old Name"))
    memory_db.commit()
    csv = tmp_path / "update.csv"
    csv.write_text("ARG,1,New Name\n", encoding="utf-8")
    result = CardsCsvImporter(memory_db).import_file(csv, collection_with_codes.collection_id)
    assert result.imported == 1
    fresh = cards_repo.get(collection_with_codes.collection_id, "ARG", 1)
    assert fresh is not None
    assert fresh.card_name == "New Name"
```

### [tests/admin/tools/test_panini_scraper.py](tests/admin/tools/test_panini_scraper.py)

```python
"""Tests del scraper de Panini.

Mockean requests con `responses` para no tocar la red. Cubren:
- Parseo de HTML de Blogger (`_extract_card_images`).
- Filtros de relevancia (`_is_relevant_page`).
- Validación defensiva en `_download_card` (size + magic bytes).
- Loop de `run()` (rate-limit, dedupe, max_pages, missing_numbers).
- CLI `main()` (creación de output dir).
"""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
import responses
from bs4 import BeautifulSoup

from collections_app.admin.tools import panini_scraper
from collections_app.admin.tools.panini_scraper import (
    COLLECTIONS,
    DELAY_AFTER_429,
    JPEG_MAGIC,
    CardImage,
    PaniniScraper,
    ScrapeResult,
    _compress_ranges,
    main,
)

ADRENALYN = COLLECTIONS["adrenalyn"]


# ----------------------------------------------------------------------
# Fixtures HTML
# ----------------------------------------------------------------------


def _post_body(inner_html: str, title: str = "Adrenalyn XL FIFA World Cup 2026 (09)") -> str:
    """Envuelve `inner_html` en una página estilo Blogger."""
    return f"""
    <html><head><title>{title}</title></head><body>
      <div class="post-body">
        {inner_html}
      </div>
      <a class="blog-pager-older-link" href="/2026/02/older.html">Older Post</a>
      <a class="blog-pager-newer-link" href="/2026/02/newer.html">Newer Post</a>
    </body></html>
    """


def _make_scraper(tmp_path: Path) -> PaniniScraper:
    return PaniniScraper(config=ADRENALYN, output_dir=tmp_path, force=False)


def _valid_jpeg(size_kb: int = 10) -> bytes:
    return JPEG_MAGIC + b"\x00" * (size_kb * 1024)


# ----------------------------------------------------------------------
# _extract_card_images
# ----------------------------------------------------------------------


def test_extract_card_images_parses_blogger_html(tmp_path):
    inner = "".join(
        f'<a href="https://blogger.googleusercontent.com/img/abc/s620/'
        f'AXL%20World%20Cup%202026%20-{n:03d}.jpg">link</a>'
        for n in (1, 2, 3, 10, 42)
    )
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    scraper = _make_scraper(tmp_path)

    cards = scraper._extract_card_images(soup, "https://example.com/post.html")

    numbers = sorted(c.card_number for c in cards)
    assert numbers == [1, 2, 3, 10, 42]
    assert all(c.source_page == "https://example.com/post.html" for c in cards)


def test_extract_card_images_upgrades_to_s1600(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-010.jpg">x</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert len(cards) == 1
    assert "/s1600/" in cards[0].url
    assert "/s620/" not in cards[0].url
    assert cards[0].original_url.endswith("/s620/AXL-010.jpg")


def test_extract_card_images_dedupes_by_number(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-007.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/zzz/s403/AXL-007.jpg">y</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert len(cards) == 1
    assert cards[0].card_number == 7
    # Quedó la primera aparición
    assert "/img/abc/" in cards[0].original_url


def test_extract_card_images_ignores_non_blogger_urls(tmp_path):
    inner = """
    <a href="https://example.com/AXL-001.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-002.jpg">ok</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [2]


def test_extract_card_images_ignores_unrelated_filenames(tmp_path):
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/random-photo.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-005.jpg">ok</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [5]


def test_extract_card_images_url_decodes_filename(tmp_path):
    """Blogger sirve URLs URL-encoded; el regex aplica sobre el unquote."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL%20World%20Cup%20-099.jpg">x</a>
    """
    soup = BeautifulSoup(_post_body(inner), "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [99]


def test_extract_card_images_only_searches_post_body(tmp_path):
    """No tocar el sidebar 'Popular Posts' que también tiene <img>."""
    html = """
    <html><head><title>Adrenalyn XL FIFA World Cup 2026</title></head><body>
      <div class="popular-posts">
        <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-666.jpg">sidebar</a>
      </div>
      <div class="post-body">
        <a href="https://blogger.googleusercontent.com/img/abc/s620/AXL-001.jpg">x</a>
      </div>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    cards = _make_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [1]


# ----------------------------------------------------------------------
# _is_relevant_page
# ----------------------------------------------------------------------


def test_is_relevant_page_accepts_card_pages(tmp_path):
    soup = BeautifulSoup(
        "<html><head><title>Adrenalyn XL FIFA World Cup 2026 (09) - 010-045</title></head></html>",
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is True


def _title_html(title: str) -> str:
    return f"<html><head><title>{title}</title></head></html>"


def test_is_relevant_page_rejects_limited_edition(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 - Limited Edition"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_checklist(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 (07) - Checklist"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_official_guide(tmp_path):
    soup = BeautifulSoup(
        _title_html("Adrenalyn XL FIFA World Cup 2026 - Official Guide"),
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_non_collection_post(tmp_path):
    soup = BeautifulSoup(
        "<html><head><title>Cards from Euro 2024</title></head></html>",
        "html.parser",
    )
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


def test_is_relevant_page_rejects_empty_title(tmp_path):
    soup = BeautifulSoup("<html></html>", "html.parser")
    assert _make_scraper(tmp_path)._is_relevant_page(soup, "u") is False


# ----------------------------------------------------------------------
# _download_card
# ----------------------------------------------------------------------


def _card(n: int = 42, url: str = "https://example.com/img.jpg") -> CardImage:
    return CardImage(card_number=n, url=url, original_url=url, source_page="src")


def test_download_card_skips_existing_unless_force(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    existing = tmp_path / "0042.jpg"
    existing.write_bytes(b"old")

    scraper = _make_scraper(tmp_path)
    with responses.RequestsMock():  # ningún request debe ocurrir
        outcome = scraper._download_card(_card(42))
    assert outcome == "skipped"
    assert existing.read_bytes() == b"old"

    # Con force=True, sí se baja y reescribe.
    forced = PaniniScraper(config=ADRENALYN, output_dir=tmp_path, force=True)
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, "https://example.com/img.jpg", body=_valid_jpeg(20), status=200)
        outcome = forced._download_card(_card(42))
    assert outcome == "downloaded"
    assert existing.read_bytes().startswith(JPEG_MAGIC)


def test_download_card_validates_content_size(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/tiny.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=b"\xff\xd8\xff" + b"x" * 100, status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(1, url))
    assert outcome == "failed"
    assert not (tmp_path / "0001.jpg").exists()


def test_download_card_validates_magic_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/fake.jpg"
    body = b"<html>" + b"x" * 6000 + b"</html>"  # > MIN_VALID_IMAGE_BYTES, magic incorrecto
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=body, status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(1, url))
    assert outcome == "failed"
    assert not (tmp_path / "0001.jpg").exists()


def test_download_card_writes_valid_jpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/ok.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, body=_valid_jpeg(15), status=200)
        outcome = _make_scraper(tmp_path)._download_card(_card(7, url))
    assert outcome == "downloaded"
    saved = tmp_path / "0007.jpg"
    assert saved.exists()
    assert saved.read_bytes().startswith(JPEG_MAGIC)


def test_download_card_handles_http_error(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/missing.jpg"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=404)
        outcome = _make_scraper(tmp_path)._download_card(_card(13, url))
    assert outcome == "failed"


# ----------------------------------------------------------------------
# _fetch_html / 429
# ----------------------------------------------------------------------


def test_fetch_html_handles_http_429_with_backoff(tmp_path, monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda s: sleeps.append(s))

    url = "https://example.com/post"
    scraper = _make_scraper(tmp_path)
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=429)
        rsps.add(responses.GET, url, body="<html><title>OK</title></html>", status=200)
        html = scraper._fetch_html(url)

    assert html is not None
    assert "<title>OK</title>" in html
    assert DELAY_AFTER_429 in sleeps  # se respetó el backoff


def test_fetch_html_returns_none_on_persistent_429(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/post"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=429)
        rsps.add(responses.GET, url, status=429)
        html = _make_scraper(tmp_path)._fetch_html(url)
    assert html is None


def test_fetch_html_returns_none_on_non_200(tmp_path, monkeypatch):
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    url = "https://example.com/missing"
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, url, status=404)
        assert _make_scraper(tmp_path)._fetch_html(url) is None


# ----------------------------------------------------------------------
# _find_next_pages
# ----------------------------------------------------------------------


def test_find_next_pages_returns_older_and_newer_links(tmp_path):
    soup = BeautifulSoup(_post_body("", "Adrenalyn XL FIFA World Cup 2026"), "html.parser")
    pages = _make_scraper(tmp_path)._find_next_pages(soup, "https://x.com/cur")
    # Older + Newer (urljoineados) están en la lista
    assert any(p.endswith("/2026/02/older.html") for p in pages)
    assert any(p.endswith("/2026/02/newer.html") for p in pages)


def test_find_next_pages_excludes_already_visited(tmp_path):
    soup = BeautifulSoup(_post_body(""), "html.parser")
    scraper = _make_scraper(tmp_path)
    older = "https://cartophilic-info-exch.blogspot.com/2026/02/older.html"
    scraper._visited_pages.add(older)
    pages = scraper._find_next_pages(soup, "https://cartophilic-info-exch.blogspot.com/cur")
    assert older not in pages


# ----------------------------------------------------------------------
# run()
# ----------------------------------------------------------------------


def test_run_respects_max_pages(tmp_path, monkeypatch):
    """Cada página linkea a una página nueva; el loop se corta en max_pages."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    page_idx = {"n": 0}

    def fake_fetch(_url: str) -> str:
        page_idx["n"] += 1
        next_n = page_idx["n"] + 1
        # Cada página linkea a la próxima
        return _post_body(
            f"""
            <a href="https://blogger.googleusercontent.com/img/x/s620/AXL-{page_idx['n']:03d}.jpg">x</a>
            """,
        ).replace(
            "/2026/02/older.html",
            f"https://cartophilic-info-exch.blogspot.com/2026/02/page-{next_n}.html",
        )

    scraper = PaniniScraper(config=ADRENALYN, output_dir=tmp_path, max_pages=5)
    with (
        patch.object(scraper, "_fetch_html", side_effect=fake_fetch),
        patch.object(scraper, "_download_card", return_value="downloaded"),
    ):
        result = scraper.run()

    assert result.pages_visited == 5


def test_run_dedupes_visited_pages(tmp_path, monkeypatch):
    """A linkea B y B linkea A: cada URL se procesa una sola vez."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    base = "https://cartophilic-info-exch.blogspot.com"
    seed = f"{base}/A.html"
    fetched: list[str] = []

    def fake_fetch(url: str) -> str:
        fetched.append(url)
        if url.endswith("A.html"):
            return (
                _post_body("")
                .replace("/2026/02/older.html", f"{base}/B.html")
                .replace("/2026/02/newer.html", f"{base}/B.html")
            )
        return (
            _post_body("")
            .replace("/2026/02/older.html", f"{base}/A.html")
            .replace("/2026/02/newer.html", f"{base}/A.html")
        )

    scraper = PaniniScraper(
        config=replace(ADRENALYN, seed_url=seed),
        output_dir=tmp_path,
        max_pages=20,
    )
    with patch.object(scraper, "_fetch_html", side_effect=fake_fetch):
        result = scraper.run()

    assert result.pages_visited == 2  # A y B, no más
    assert fetched == [f"{base}/A.html", f"{base}/B.html"]


def test_run_reports_missing_numbers(tmp_path, monkeypatch):
    """Si solo se descargan algunas cards, missing_numbers lista el resto."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    inner = "".join(
        f'<a href="https://blogger.googleusercontent.com/img/x/s620/AXL-{n:03d}.jpg">x</a>'
        for n in (1, 2, 5)
    )
    config_small = replace(ADRENALYN, expected_total=10)
    scraper = PaniniScraper(config=config_small, output_dir=tmp_path, max_pages=1)

    with (
        patch.object(scraper, "_fetch_html", return_value=_post_body(inner)),
        patch.object(scraper, "_download_card", return_value="downloaded"),
    ):
        result = scraper.run()

    assert result.downloaded == 3
    assert result.missing_numbers == [3, 4, 6, 7, 8, 9, 10]


def test_run_skips_pages_marked_as_irrelevant(tmp_path, monkeypatch):
    """Una página que no matchea title_keyword no se procesa para cards."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    irrelevant_html = "<html><head><title>Some other album</title></head><body></body></html>"
    scraper = _make_scraper(tmp_path)
    with (
        patch.object(scraper, "_fetch_html", return_value=irrelevant_html),
        patch.object(scraper, "_download_card") as mock_dl,
    ):
        scraper.run()
    mock_dl.assert_not_called()


# ----------------------------------------------------------------------
# CLI main()
# ----------------------------------------------------------------------


def test_main_creates_output_dir(tmp_path, monkeypatch):
    """El CLI crea la carpeta {generated_cards}/{collection_id}/ antes de correr."""
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )

    captured: dict = {}

    class _StubScraper:
        def __init__(self, **kwargs):
            captured["output_dir"] = kwargs["output_dir"]

        def run(self):
            return ScrapeResult()

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)

    rc = main(["--collection", "adrenalyn"])

    assert rc == 0
    expected = tmp_path / str(ADRENALYN.collection_id)
    assert expected.exists()
    assert captured["output_dir"] == expected


def test_main_returns_nonzero_when_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )

    class _StubScraper:
        def __init__(self, **_kwargs):
            pass

        def run(self):
            return ScrapeResult(downloaded=1, failed=2)

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)

    rc = main(["--collection", "adrenalyn"])
    assert rc == 1


def test_main_collection_id_override_uses_custom_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "collections_app.admin.tools.panini_scraper.get_generated_cards_dir",
        lambda: tmp_path,
    )
    captured: dict = {}

    class _StubScraper:
        def __init__(self, **kwargs):
            captured["output_dir"] = kwargs["output_dir"]

        def run(self):
            return ScrapeResult()

    monkeypatch.setattr(panini_scraper, "PaniniScraper", _StubScraper)
    main(["--collection", "adrenalyn", "--collection-id", "99"])
    assert captured["output_dir"] == tmp_path / "99"


# ----------------------------------------------------------------------
# Sanity
# ----------------------------------------------------------------------


@pytest.mark.parametrize("name", ["adrenalyn", "stickers"])
def test_collections_config_complete(name):
    """COLLECTIONS tiene los dos sets esperados con campos válidos."""
    cfg = COLLECTIONS[name]
    assert cfg.name == name
    assert cfg.collection_id > 0
    assert cfg.seed_url.startswith("https://cartophilic-info-exch.blogspot.com")
    assert cfg.title_keyword
    assert cfg.expected_total > 0
    assert cfg.filename_pattern.pattern  # regex no vacía


# ----------------------------------------------------------------------
# Stickers — regex y blacklist (PASO 1)
# ----------------------------------------------------------------------


STICKERS = COLLECTIONS["stickers"]


def test_collections_stickers_config_is_id_3():
    """La colección stickers debe usar collection_id=3 y el seed correcto."""
    assert STICKERS.collection_id == 3
    assert STICKERS.expected_total == 980
    assert STICKERS.seed_url.startswith("https://cartophilic-info-exch.blogspot.com")
    # Seed actualizado al post de Checklist (mexusacan)
    assert "mexusacan" in STICKERS.seed_url


def test_stickers_pattern_matches_basic_filename():
    """El regex matchea filenames de stickers individuales."""
    pat = STICKERS.filename_pattern
    cases = {
        "2026 Panini - FIFA World Cup 2026 -001aa.jpg": 1,
        "2026 Panini - FIFA World Cup 2026 -042b.jpg": 42,
        "2026 Panini - FIFA World Cup 2026 -301a.jpg": 301,
        "2026 Panini - FIFA World Cup 2026 -980abc.jpg": 980,
    }
    for filename, expected in cases.items():
        m = pat.search(filename)
        assert m is not None, f"Esperaba match para {filename!r}"
        assert int(m.group(1)) == expected


def test_stickers_pattern_rejects_country_filenames():
    """El regex NO matchea filenames con código de país en lugar de número."""
    pat = STICKERS.filename_pattern
    rejected = (
        "2026 Panini - FIFA World Cup 2026 -USA1bbb.jpg",
        "2026 Panini - FIFA World Cup 2026 - Brazil2cc.jpg",
        "2026 Panini - FIFA World Cup - Brazil2cc.jpg",  # falta "2026"
    )
    for filename in rejected:
        assert pat.search(filename) is None, f"NO debería matchear {filename!r}"


def test_stickers_pattern_rejects_variants():
    """El regex NO matchea variantes patrocinadas / Play-Offs / Free Digital."""
    pat = STICKERS.filename_pattern
    rejected = (
        # Hay tokens entre "2026" y "-001a" (Coca-Cola, Play-Offs, etc.)
        "2026 Panini - FIFA World Cup 2026 - Coca-Cola -001a.jpg",
        "2026 Panini - FIFA World Cup 2026 - Play-Offs - 001a.jpg",
        "2026 Panini - FIFA World Cup 2026 - Free Digital Pack -001aa.jpg",
        "2026 Panini - FIFA World Cup 2026 - McDoanlds - Mexico2.jpg",
    )
    for filename in rejected:
        assert pat.search(filename) is None, f"NO debería matchear {filename!r}"


def _stickers_scraper(tmp_path: Path) -> PaniniScraper:
    return PaniniScraper(config=STICKERS, output_dir=tmp_path)


def _stickers_post(inner_html: str, title: str = "FIFA World Cup 2026 (07)") -> str:
    return f"""
    <html><head><title>{title}</title></head><body>
      <div class="post-body">{inner_html}</div>
      <a class="blog-pager-older-link" href="/2026/03/older.html">Older</a>
      <a class="blog-pager-newer-link" href="/2026/03/newer.html">Newer</a>
    </body></html>
    """


def test_blacklist_filters_country_grupal_sheets(tmp_path):
    """URL con ' - germany - ' es hoja grupal — descartar aunque tenga regex válido."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 - Germany - Album1a.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 -005aa.jpg">ok</a>
    """  # noqa: E501
    soup = BeautifulSoup(_stickers_post(inner), "html.parser")
    cards = _stickers_scraper(tmp_path)._extract_card_images(soup, "src")
    numbers = [c.card_number for c in cards]
    assert numbers == [5]  # solo el individual válido


def test_blacklist_filters_coca_cola(tmp_path):
    """URL con 'coca-cola' se descarta vía FILENAME_BLACKLIST_TOKENS."""
    inner = """
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini FIFA WC 2026 Coca-Cola -001a.jpg">x</a>
    <a href="https://blogger.googleusercontent.com/img/x/s620/2026 Panini - FIFA World Cup 2026 -042a.jpg">ok</a>
    """  # noqa: E501
    soup = BeautifulSoup(_stickers_post(inner), "html.parser")
    cards = _stickers_scraper(tmp_path)._extract_card_images(soup, "src")
    assert [c.card_number for c in cards] == [42]


def test_seed_page_not_relevant_but_provides_links(tmp_path, monkeypatch):
    """Página seed (Checklist) no se scrapea para cards pero sí para links."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    title = "Panini FIFA World Cup 2026 - Checklist"
    inner = (
        '<a href="https://blogger.googleusercontent.com/img/x/s620/'
        "2026 Panini - FIFA World Cup 2026 -010aa.jpg"
        '">x</a>'
    )
    html = _stickers_post(inner, title=title)
    scraper = _stickers_scraper(tmp_path)
    soup = BeautifulSoup(html, "html.parser")

    # 1) La página NO se considera relevante (matchea blacklist 'checklist')
    assert scraper._is_relevant_page(soup, "u") is False

    # 2) Pero `_find_next_pages` SÍ devuelve links (Older/Newer Post)
    links = scraper._find_next_pages(soup, "https://cartophilic-info-exch.blogspot.com/cur")
    assert any(link.endswith("/2026/03/older.html") for link in links)
    assert any(link.endswith("/2026/03/newer.html") for link in links)

    # 3) El loop de run() también: visitamos la seed y NO bajamos cards
    #    (las descarta por título), pero el link aporta páginas a la queue.
    with (
        patch.object(scraper, "_fetch_html", return_value=html),
        patch.object(scraper, "_download_card") as mock_dl,
    ):
        # Restringimos a 1 página para acotar el test (la primera es la seed)
        scraper._max_pages = 1
        result = scraper.run()
    mock_dl.assert_not_called()
    assert result.pages_visited == 1


def test_run_skips_already_downloaded_numbers(tmp_path, monkeypatch):
    """Misma card en 3 páginas: solo la primera baja, las demás 'skipped'."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)

    page_idx = {"n": 0}
    base = "https://cartophilic-info-exch.blogspot.com"

    def fake_fetch(_url: str) -> str:
        page_idx["n"] += 1
        # Cada página linkea a la siguiente y contiene la misma card 042
        next_n = page_idx["n"] + 1
        inner = (
            '<a href="https://blogger.googleusercontent.com/img/x/s620/'
            "2026 Panini - FIFA World Cup 2026 -042aa.jpg"
            '">x</a>'
        )
        return (
            _stickers_post(inner)
            .replace("/2026/03/older.html", f"{base}/p{next_n}.html")
            .replace("/2026/03/newer.html", f"{base}/p{next_n}.html")
        )

    scraper = PaniniScraper(config=STICKERS, output_dir=tmp_path, max_pages=3)
    download_calls: list[int] = []

    def fake_download(card: CardImage) -> str:
        download_calls.append(card.card_number)
        # La primera retorna 'downloaded'; las siguientes el dedupe del run
        # (en _download_card real) las marca skipped sin entrar acá.
        # Pero como acá mockeamos _download_card completamente, contamos
        # cuántas veces lo llama el loop principal.
        return "downloaded"

    with (
        patch.object(scraper, "_fetch_html", side_effect=fake_fetch),
        patch.object(scraper, "_download_card", side_effect=fake_download),
    ):
        result = scraper.run()

    # _download_card se invoca para cada aparición de la card en cada página.
    # El dedupe real vive DENTRO de _download_card (chequea
    # _downloaded_numbers); ese path se ejercita en su propio test abajo.
    assert len(download_calls) == 3
    # Pero result.downloaded sigue siendo 3 sólo porque mockeamos el outcome.
    assert result.downloaded == 3


def test_download_card_skips_when_already_in_downloaded_numbers(tmp_path, monkeypatch):
    """`_download_card` detecta dedupe vía `_downloaded_numbers` antes del HTTP."""
    monkeypatch.setattr(panini_scraper.time, "sleep", lambda _s: None)
    scraper = _stickers_scraper(tmp_path)
    scraper._downloaded_numbers.add(42)

    card = CardImage(
        card_number=42,
        url="https://example.com/should-not-be-called.jpg",
        original_url="...",
        source_page="src",
    )
    with responses.RequestsMock():  # cero requests permitidos
        outcome = scraper._download_card(card)
    assert outcome == "skipped"


# ----------------------------------------------------------------------
# _compress_ranges
# ----------------------------------------------------------------------


def test_compress_ranges_basic():
    assert _compress_ranges([]) == ""
    assert _compress_ranges([1]) == "001"
    assert _compress_ranges([1, 2, 3]) == "001-003"
    assert _compress_ranges([1, 2, 3, 5, 7, 8, 9]) == "001-003, 005, 007-009"
    assert _compress_ranges([42, 100, 101, 102, 200]) == "042, 100-102, 200"


def test_compress_ranges_padding_at_three_digits():
    """El formato siempre usa 3 dígitos, incluso para números pequeños."""
    assert _compress_ranges([7]) == "007"
    assert _compress_ranges([7, 8, 9]) == "007-009"
```

### [tests/admin/tools/test_rename_legacy_cards.py](tests/admin/tools/test_rename_legacy_cards.py)

```python
"""Tests del script de migración rename_legacy_cards."""

import logging

from collections_app.admin.tools import rename_legacy_cards
from collections_app.admin.tools.rename_legacy_cards import (
    main,
)
from collections_app.admin.tools.rename_legacy_cards import (
    rename_legacy_cards as do_rename,
)


def test_renames_legacy_files_to_padded(tmp_path):
    """`1.jpg` y `42.png` se renombran a `0001.jpg` y `0042.png`."""
    (tmp_path / "1.jpg").write_bytes(b"a")
    (tmp_path / "42.png").write_bytes(b"b")

    result = do_rename(tmp_path)

    assert result.renamed == 2
    assert result.errors == 0
    assert (tmp_path / "0001.jpg").exists()
    assert (tmp_path / "0042.png").exists()
    assert not (tmp_path / "1.jpg").exists()
    assert not (tmp_path / "42.png").exists()


def test_skips_already_padded_files(tmp_path):
    """Archivos ya con padding no se tocan."""
    (tmp_path / "0001.jpg").write_bytes(b"x")
    (tmp_path / "0042.png").write_bytes(b"y")

    result = do_rename(tmp_path)

    assert result.renamed == 0
    assert result.skipped_already_padded == 2
    assert (tmp_path / "0001.jpg").read_bytes() == b"x"
    assert (tmp_path / "0042.png").read_bytes() == b"y"


def test_dry_run_does_not_modify_files(tmp_path):
    """Con dry_run no se toca el filesystem, pero se cuenta lo que se haría."""
    (tmp_path / "1.jpg").write_bytes(b"x")

    result = do_rename(tmp_path, dry_run=True)

    assert result.renamed == 1  # contado pero no aplicado
    assert (tmp_path / "1.jpg").exists()
    assert not (tmp_path / "0001.jpg").exists()


def test_does_not_overwrite_existing_padded(tmp_path, caplog):
    """Si ya existe `0001.jpg`, no se sobreescribe con `1.jpg` legacy."""
    (tmp_path / "1.jpg").write_bytes(b"legacy")
    (tmp_path / "0001.jpg").write_bytes(b"original")

    with caplog.at_level(logging.WARNING, logger="collections_app.admin.tools.rename_legacy_cards"):
        result = do_rename(tmp_path)

    assert result.skipped_collision == 1
    assert result.renamed == 0
    assert (tmp_path / "0001.jpg").read_bytes() == b"original"  # intacto
    assert (tmp_path / "1.jpg").read_bytes() == b"legacy"  # también intacto
    msgs = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("Colisión" in m or "0001.jpg" in m for m in msgs)


def test_skips_unrecognized_files(tmp_path):
    """Archivos que no matcheen el patrón legacy (ej. README) se ignoran."""
    (tmp_path / "README.txt").write_bytes(b"x")
    (tmp_path / "thumb.gif").write_bytes(b"y")
    (tmp_path / "1.jpg").write_bytes(b"z")

    result = do_rename(tmp_path)

    assert result.renamed == 1
    assert result.skipped_unrecognized == 2
    assert (tmp_path / "README.txt").exists()
    assert (tmp_path / "thumb.gif").exists()
    assert (tmp_path / "0001.jpg").exists()


def test_handles_missing_directory(tmp_path):
    """Si el directorio no existe, retorna result vacío sin levantar."""
    result = do_rename(tmp_path / "no-existe")
    assert result.renamed == 0
    assert result.errors == 0


def test_extension_normalized_to_lowercase(tmp_path):
    """Extensiones en mayúscula (`1.JPG`) se normalizan a minúscula."""
    (tmp_path / "5.JPG").write_bytes(b"x")
    do_rename(tmp_path)
    assert (tmp_path / "0005.jpg").exists()
    assert not (tmp_path / "5.JPG").exists()


# ----------------------------------------------------------------------
# CLI main()
# ----------------------------------------------------------------------


def test_main_returns_zero_when_no_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(rename_legacy_cards, "get_generated_cards_dir", lambda: tmp_path)
    (tmp_path / "1").mkdir()
    (tmp_path / "1" / "1.jpg").write_bytes(b"x")

    rc = main(["--collection-id", "1"])

    assert rc == 0
    assert (tmp_path / "1" / "0001.jpg").exists()


def test_main_dry_run_does_not_write(tmp_path, monkeypatch):
    monkeypatch.setattr(rename_legacy_cards, "get_generated_cards_dir", lambda: tmp_path)
    (tmp_path / "1").mkdir()
    (tmp_path / "1" / "42.jpg").write_bytes(b"x")

    rc = main(["--collection-id", "1", "--dry-run"])

    assert rc == 0
    assert (tmp_path / "1" / "42.jpg").exists()
    assert not (tmp_path / "1" / "0042.jpg").exists()
```

### [tests/admin/views/__init__.py](tests/admin/views/__init__.py)

_(archivo vacío)_

### [tests/admin/views/test_cards_abm.py](tests/admin/views/test_cards_abm.py)

```python
"""Tests del CardsAbmView."""

from PySide6.QtCore import Qt

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.core.models import CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)


def _seed(memory_db, sample_collection):
    """Inserta codes_lines necesarios para el header de la collection."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in ("ARG", "BRA"):
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()


def test_cards_view_initial_state(qtbot, memory_db):
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # Sin colecciones → no hay ABM montado, importar deshabilitado
    assert view._import_button.isEnabled() is False
    assert view._cards_widget is None


def test_cards_view_lists_collections_in_combo(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # combo: 1 placeholder + 1 colección
    assert view._collection_combo.count() == 2


def test_cards_view_rebuilds_abm_on_collection_change(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)  # procesa eventos pendientes antes del teardown
    assert view._cards_widget is not None
    assert view._import_button.isEnabled() is True


def test_cards_view_save_card(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)
    assert view._cards_widget is not None

    view._cards_widget._inputs["code_id"].setCurrentIndex(0)
    view._cards_widget._inputs["card_number"].setValue(7)
    view._cards_widget._inputs["card_name"].setText("Test Card")
    qtbot.mouseClick(view._cards_widget._save_button, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    cards = CardsRepository(memory_db).list_by_collection(sample_collection.collection_id)
    assert len(cards) == 1
    assert cards[0].card_name == "Test Card"
    assert cards[0].collection_id == sample_collection.collection_id


def test_cards_combo_choices_use_codes_of_header(qtbot, memory_db, sample_collection):
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)
    code_combo = view._cards_widget._inputs["code_id"]
    values = [code_combo.itemData(i) for i in range(code_combo.count())]
    assert set(values) == {"ARG", "BRA"}


def test_collections_combo_reflects_new_collection(qtbot, memory_db, sample_collection):
    """Una colección creada después de instanciar el view aparece en el combo
    al llamar refresh_collections_combo (sin reiniciar)."""
    from collections_app.core.models import Collection
    from collections_app.core.repositories import CollectionsRepository

    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    initial_count = view._collection_combo.count()

    CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Nueva Colección",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_collection.code_header_id,
        )
    )
    memory_db.commit()

    view.refresh_collections_combo()
    assert view._collection_combo.count() == initial_count + 1
    labels = [view._collection_combo.itemText(i) for i in range(view._collection_combo.count())]
    assert "Nueva Colección" in labels


def test_collections_combo_handles_deleted_active_collection(qtbot, memory_db, sample_collection):
    """Si la colección activa se borra, el combo vuelve a (ninguna) y el
    AbmWidget queda deshabilitado."""
    from collections_app.core.repositories import CollectionsRepository

    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Selecciona la colección sample
    view._on_collection_changed(1)
    qtbot.wait(50)
    assert view._cards_widget is not None
    assert view._import_button.isEnabled() is True

    # Borra esa colección desde fuera y refresca
    CollectionsRepository(memory_db).delete(sample_collection.collection_id)
    memory_db.commit()
    view.refresh_collections_combo()
    qtbot.wait(50)

    assert view._collection_combo.currentData() is None
    assert view._cards_widget is None
    assert view._import_button.isEnabled() is False
    assert view._current_collection is None


def test_collections_combo_preserves_selection_on_refresh(qtbot, memory_db, sample_collection):
    """Si la colección activa sigue existiendo, refresh la mantiene."""
    _seed(memory_db, sample_collection)
    view = CardsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    view._on_collection_changed(1)
    qtbot.wait(50)

    view.refresh_collections_combo()
    qtbot.wait(50)
    assert view._collection_combo.currentData() == sample_collection.collection_id
    assert view._current_collection is not None
    assert view._current_collection.collection_id == sample_collection.collection_id
```

### [tests/admin/views/test_codes_master_detail.py](tests/admin/views/test_codes_master_detail.py)

```python
"""Tests del CodesMasterDetailView."""

from PySide6.QtCore import Qt

from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.core.models import CodeHeader, CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CodesLinesRepository,
)


def test_master_loads_headers(qtbot, memory_db):
    headers_repo = CodesHeadersRepository(memory_db)
    headers_repo.create(CodeHeader(None, "FIFA", 5))
    headers_repo.create(CodeHeader(None, "Pokemon", 4))
    memory_db.commit()

    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()
    assert view.headers_abm._grid_model.rowCount() == 2


def test_detail_disabled_until_header_selected(qtbot, memory_db, sample_code_header):
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()
    assert view.lines_abm.isEnabled() is False


def test_detail_loads_lines_of_selected_header(qtbot, memory_db, sample_code_header):
    lines_repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    memory_db.commit()

    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Simular selección en master
    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    assert view.lines_abm.isEnabled() is True
    assert view.lines_abm._grid_model.rowCount() == 2


def test_create_line_uses_current_header_id(qtbot, memory_db, sample_code_header):
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Seleccionar el header sample
    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    view.lines_abm._inputs["code_id"].setText("ARG")
    view.lines_abm._inputs["code_name"].setText("Argentina")
    view.lines_abm._inputs["code_order"].setValue(1)
    qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)

    lines = CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id)
    assert len(lines) == 1
    assert lines[0].code_id == "ARG"
    assert lines[0].code_header_id == sample_code_header.code_header_id


def test_validate_line_rejects_too_long_code(qtbot, memory_db, sample_code_header):
    """sample_code_header tiene max_length=5; un código de 6 chars debe fallar."""
    view = CodesMasterDetailView(memory_db)
    qtbot.addWidget(view)
    view.show()

    view.headers_abm._grid_view.selectRow(0)
    qtbot.wait(50)

    view.lines_abm._inputs["code_id"].setText("ABCDEF")  # 6 chars
    view.lines_abm._inputs["code_name"].setText("Demasiado")
    qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)
    assert "longitud" in view.lines_abm._status_label.text().lower()
    assert CodesLinesRepository(memory_db).list_by_header(sample_code_header.code_header_id) == []
```

### [tests/admin/views/test_collections_abm.py](tests/admin/views/test_collections_abm.py)

```python
"""Tests del CollectionsAbmView."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QLineEdit

from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.core.repositories import CollectionsRepository


def test_collections_abm_loads(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    # Sin colecciones todavía → grilla vacía
    assert view.abm._grid_model.rowCount() == 0


def test_collections_abm_save_creates_record(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    # Setear inputs mínimos válidos
    view.abm._inputs["collection_name"].setText("Test Collection")
    view.abm._inputs["card_count"].setValue(50)
    # Combo header: index 0 está poblado
    view.abm._inputs["code_header_id"].setCurrentIndex(0)

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)

    cols = CollectionsRepository(memory_db).list_all()
    assert len(cols) == 1
    assert cols[0].collection_name == "Test Collection"


def test_collections_abm_validate_requires_code_field_name(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    name_input = view.abm._inputs["collection_name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("Premium Collection")
    view.abm._inputs["card_count"].setValue(10)
    view.abm._inputs["code_header_id"].setCurrentIndex(0)
    requires_code = view.abm._inputs["requires_code"]
    assert isinstance(requires_code, QCheckBox)
    requires_code.setChecked(True)
    # code_field_name vacío → debería fallar validación

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    assert "etiqueta" in view.abm._status_label.text().lower()
    assert CollectionsRepository(memory_db).list_all() == []


def test_collections_combo_reflects_new_headers(qtbot, memory_db, sample_code_header):
    """Headers creados después de instanciar el ABM aparecen al hacer Nuevo."""
    from collections_app.core.models import CodeHeader
    from collections_app.core.repositories import CodesHeadersRepository

    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    combo = view.abm._inputs["code_header_id"]
    initial_count = combo.count()
    assert initial_count >= 1  # sample_code_header

    # Crear un nuevo header desde el repo (simula creación en otro tab)
    CodesHeadersRepository(memory_db).create(CodeHeader(None, "Adrenalyne XL", 5))
    memory_db.commit()

    # Click en "Nuevo" debe re-evaluar el combo callable
    qtbot.mouseClick(view.abm._new_button, Qt.MouseButton.LeftButton)
    assert combo.count() == initial_count + 1
    labels = [combo.itemText(i) for i in range(combo.count())]
    assert "Adrenalyne XL" in labels


def test_collections_combo_label_is_cabecera_de_codigo(qtbot, memory_db, sample_code_header):
    """El label del campo de header se llama 'Cabecera de código'."""
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()
    code_header_field = next(f for f in view.abm.config.fields if f.name == "code_header_id")
    assert code_header_field.label == "Cabecera de código"


def test_collections_abm_validate_premium_requires_license(qtbot, memory_db, sample_code_header):
    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    view.abm._inputs["collection_name"].setText("Premium")
    view.abm._inputs["card_count"].setValue(10)
    view.abm._inputs["code_header_id"].setCurrentIndex(0)
    is_premium = view.abm._inputs["is_premium"]
    assert isinstance(is_premium, QCheckBox)
    is_premium.setChecked(True)
    # license_key_required vacío

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    assert "licencia" in view.abm._status_label.text().lower()
    assert CollectionsRepository(memory_db).list_all() == []


def test_collections_abm_album_inputs_have_defaults(qtbot, memory_db, sample_code_header):
    """Al instanciar el ABM, los inputs de álbum arrancan con sus defaults."""
    from PySide6.QtWidgets import QComboBox, QSpinBox

    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    cols = view.abm._inputs["album_columns"]
    rows = view.abm._inputs["album_rows"]
    orient = view.abm._inputs["album_orientation"]
    assert isinstance(cols, QSpinBox) and cols.value() == 3
    assert isinstance(rows, QSpinBox) and rows.value() == 4
    assert isinstance(orient, QComboBox) and orient.currentData() == "portrait"


def test_collections_abm_save_persists_album_layout(qtbot, memory_db, sample_code_header):
    """El save guarda los valores custom de álbum."""
    from PySide6.QtWidgets import QComboBox

    view = CollectionsAbmView(memory_db)
    qtbot.addWidget(view)
    view.show()

    view.abm._inputs["collection_name"].setText("LandscapeColl")
    view.abm._inputs["card_count"].setValue(50)
    view.abm._inputs["code_header_id"].setCurrentIndex(0)
    view.abm._inputs["album_columns"].setValue(5)
    view.abm._inputs["album_rows"].setValue(2)
    orient = view.abm._inputs["album_orientation"]
    assert isinstance(orient, QComboBox)
    orient.setCurrentIndex(orient.findData("landscape"))

    qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)

    cols = CollectionsRepository(memory_db).list_all()
    assert len(cols) == 1
    assert cols[0].album_columns == 5
    assert cols[0].album_rows == 2
    assert cols[0].album_orientation == "landscape"
```

### [tests/admin/views/test_crests_view.py](tests/admin/views/test_crests_view.py)

```python
"""Tests del CrestsView (admin).

Foco: la vista NO trate como válidos los archivos en disco que no
superan `is_valid_crest_file` (corruptos / vacíos / truncados de un
intento previo). Cubre los puntos donde la vista decide si un escudo
está disponible y la integración con el worker.
"""

import importlib
import io
import os

from PIL import Image

from collections_app.admin.crests.crest_finder import CrestFinder
from collections_app.admin.views import crests_view as view_mod
from collections_app.admin.views.crests_view import (
    STATUS_FOUND,
    STATUS_NONE,
    STATUS_PLACEHOLDER,
    CrestsView,
)
from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository

# Tamaño chico bajo el umbral (MIN_VALID_FILE_BYTES = 1000).
INVALID_BYTES = b"x" * 50


def _valid_png_bytes() -> bytes:
    """PNG real de 200x200 con ruido (siempre > MIN_VALID_FILE_BYTES)."""
    img = Image.frombytes("RGBA", (200, 200), os.urandom(200 * 200 * 4))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


VALID_BYTES = _valid_png_bytes()


def _redirect_crest_dir(monkeypatch, tmp_path):
    """Hace que get_crest_path apunte a tmp_path en TODOS los call sites.

    `crests_view` importa `get_crest_path` directamente, así que hay que
    parchearlo en ese módulo (no en `core.utils.paths`).
    """
    monkeypatch.setattr(
        "collections_app.admin.views.crests_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )


def _seed_lines(memory_db, sample_collection, codes):
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in codes:
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()


# ----------------------------------------------------------------------
# is_valid_crest_file está exportado en el paquete
# ----------------------------------------------------------------------


def test_is_valid_crest_file_exported():
    """`is_valid_crest_file` debe ser importable desde el paquete crests."""
    pkg = importlib.import_module("collections_app.admin.crests")
    assert hasattr(pkg, "is_valid_crest_file")
    assert "is_valid_crest_file" in pkg.__all__


# ----------------------------------------------------------------------
# _build_row no setea icono para archivos inválidos
# ----------------------------------------------------------------------


def test_invalid_crest_not_shown_as_icon(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    line = CodeLine(code_header_id=1, code_id="ARG", code_name="ARGENTINA")
    icon_item, _code, _name, _status = view._build_row(line)

    assert icon_item.icon().isNull() is True


def test_valid_crest_shown_as_icon(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    line = CodeLine(code_header_id=1, code_id="ARG", code_name="ARGENTINA")
    icon_item, *_ = view._build_row(line)

    assert icon_item.icon().isNull() is False


# ----------------------------------------------------------------------
# _compute_status reporta STATUS_NONE para archivos inválidos
# ----------------------------------------------------------------------


def test_invalid_crest_shown_as_sin_escudo(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "ARG.png"
    path.write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("ARG", path) == STATUS_NONE


def test_valid_crest_shown_as_found(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "ARG.png"
    path.write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("ARG", path) == STATUS_FOUND


def test_special_code_invalid_falls_to_placeholder(qtbot, tmp_path, monkeypatch, memory_db):
    """Un code SPECIAL sin escudo válido reporta STATUS_PLACEHOLDER."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "GBL.png"  # GBL ∈ SPECIAL_CODES
    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("GBL", path) == STATUS_PLACEHOLDER


# ----------------------------------------------------------------------
# _search_auto: candidatos correctos para la búsqueda
# ----------------------------------------------------------------------


def _make_stub_worker(captured: dict) -> type:
    """Stub de _CrestSearchWorker que captura los `codes` recibidos."""

    class _StubWorker:
        progress = type("S", (), {"connect": lambda *a, **k: None})()
        finished_ok = type("S", (), {"connect": lambda *a, **k: None})()
        failed = type("S", (), {"connect": lambda *a, **k: None})()

        def __init__(self, finder, codes, parent=None):
            del finder, parent
            captured["codes"] = codes

        def start(self):
            pass

        def isRunning(self):  # noqa: N802 — mimetiza la API de QThread
            return False

    return _StubWorker


def test_invalid_crest_included_as_candidate_for_search(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    """Un archivo inválido en disco no impide que el code_id sea candidato."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    (tmp_path / "ARG.png").write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)

    captured: dict = {}
    monkeypatch.setattr(view_mod, "_CrestSearchWorker", _make_stub_worker(captured))
    view._collection_combo.setCurrentIndex(1)
    view._search_auto()

    code_ids = {c[0] for c in captured["codes"]}
    assert "ARG" in code_ids  # inválido en disco → reincluido
    assert "BRA" in code_ids  # sin archivo → incluido


def test_valid_crest_excluded_from_search_candidates(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    """Un escudo válido en disco no debe re-procesarse."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    (tmp_path / "ARG.png").write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)

    captured: dict = {}
    monkeypatch.setattr(view_mod, "_CrestSearchWorker", _make_stub_worker(captured))
    view._collection_combo.setCurrentIndex(1)
    view._search_auto()

    code_ids = {c[0] for c in captured["codes"]}
    assert "ARG" not in code_ids
    assert "BRA" in code_ids


# ----------------------------------------------------------------------
# _refresh_grid limpia archivos inválidos pre-existentes
# ----------------------------------------------------------------------


def test_refresh_grid_cleans_invalid_files(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    invalid = tmp_path / "ARG.png"
    valid = tmp_path / "BRA.png"
    invalid.write_bytes(INVALID_BYTES)
    valid.write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert sample_collection.collection_id is not None
    view._refresh_grid(sample_collection.collection_id)

    assert not invalid.exists(), "El archivo inválido debió ser eliminado"
    assert valid.exists(), "El archivo válido NO debe tocarse"


# ----------------------------------------------------------------------
# Worker
# ----------------------------------------------------------------------


def test_worker_signature_is_finder_codes_parent_only():
    """El worker NO debe recibir db_path: Commons no necesita acceso a DB."""
    from collections_app.admin.views.crests_view import _CrestSearchWorker

    finder = CrestFinder()
    # Si la firma cambia y vuelve a requerir db_path, este test rompe en TypeError.
    worker = _CrestSearchWorker(finder, [])
    assert worker is not None
```

### [tests/admin/views/test_persistence.py](tests/admin/views/test_persistence.py)

```python
"""Tests de regresión para garantizar que los saves/deletes de las views
hacen commit a la DB y son visibles desde una conexión fresca.

Estos tests existen como guardrail tras un bug observado donde un combo
no veía cambios "en vivo" entre tabs. La causa real era de visibilidad
en runtime (combo construido una vez), pero estos tests blindan también
el escenario de "abrir la DB con otra conn y ver los cambios", para que
si alguna vez se omite un `conn.commit()` en una view se detecte de inmediato.
"""

from pathlib import Path

from PySide6.QtCore import Qt

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.core.db.connection import create_connection
from collections_app.core.models import CodeHeader, CodeLine, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CodesLinesRepository,
    CollectionsRepository,
)


def _read_with_fresh_conn(db_path: Path):
    """Helper: abre una conn nueva al mismo archivo."""
    return create_connection(db_path)


# ----------------------------------------------------------------------
# CodesMasterDetailView — header
# ----------------------------------------------------------------------


def test_save_header_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()

        view.headers_abm._inputs["code_header_name"].setText("Test Header")
        view.headers_abm._inputs["code_max_length"].setValue(5)
        qtbot.mouseClick(view.headers_abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT code_header_name FROM codes_headers").fetchall()
    finally:
        fresh.close()
    names = [r["code_header_name"] for r in rows]
    assert "Test Header" in names


def test_delete_header_persists_to_fresh_conn(qtbot, file_db_path):
    # Pre-poblar con un header
    conn = create_connection(file_db_path)
    try:
        repo = CodesHeadersRepository(conn)
        header = repo.create(CodeHeader(None, "DeleteMe", 5))
        conn.commit()

        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view.headers_abm.select_record(header)

        # delete via callback directo (evita confirmación modal en tests)
        ok = view._delete_header(header)
        assert ok is True
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM codes_headers").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CodesMasterDetailView — line
# ----------------------------------------------------------------------


def test_save_line_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        conn.commit()
        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view.headers_abm.select_record(header)
        qtbot.wait(50)

        view.lines_abm._inputs["code_id"].setText("ARG")
        view.lines_abm._inputs["code_name"].setText("Argentina")
        view.lines_abm._inputs["code_order"].setValue(1)
        qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT code_id FROM codes_lines").fetchall()
    finally:
        fresh.close()
    assert any(r["code_id"] == "ARG" for r in rows)


def test_delete_line_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        line = CodeLine(header.code_header_id, "ARG", "Argentina")
        CodesLinesRepository(conn).upsert(line)
        conn.commit()

        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view._current_header = header
        view._delete_line(line)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM codes_lines").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CollectionsAbmView
# ----------------------------------------------------------------------


def test_save_collection_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        # Necesita un header como FK
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        conn.commit()

        view = CollectionsAbmView(conn)
        qtbot.addWidget(view)
        view.show()

        view.abm._inputs["collection_name"].setText("FIFA WC 2026")
        view.abm._inputs["card_count"].setValue(300)
        view.abm._inputs["code_header_id"].setCurrentIndex(
            view.abm._inputs["code_header_id"].findData(header.code_header_id)
        )
        qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT collection_name FROM collections").fetchall()
    finally:
        fresh.close()
    names = [r["collection_name"] for r in rows]
    assert "FIFA WC 2026" in names


def test_delete_collection_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        col = CollectionsRepository(conn).create(
            Collection(None, "ToDelete", 10, False, None, header.code_header_id)
        )
        conn.commit()

        view = CollectionsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._delete(col)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM collections").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CardsAbmView
# ----------------------------------------------------------------------


def _seed_cards_setup(conn) -> Collection:
    """Crea un header con código + una collection para cards."""
    header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
    CodesLinesRepository(conn).upsert(CodeLine(header.code_header_id, "ARG", "ARG"))
    col = CollectionsRepository(conn).create(
        Collection(None, "WC", 10, True, "País", header.code_header_id)
    )
    conn.commit()
    return col


def test_save_card_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _seed_cards_setup(conn)

        view = CardsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._on_collection_changed(view._collection_combo.findData(col.collection_id))
        qtbot.wait(50)

        view._cards_widget._inputs["code_id"].setCurrentIndex(0)
        view._cards_widget._inputs["card_number"].setValue(7)
        view._cards_widget._inputs["card_name"].setText("Persisted Card")
        qtbot.mouseClick(view._cards_widget._save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT card_name FROM cards").fetchall()
    finally:
        fresh.close()
    names = [r["card_name"] for r in rows]
    assert "Persisted Card" in names


def test_delete_card_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _seed_cards_setup(conn)
        from collections_app.core.models import Card

        card = Card(col.collection_id, "ARG", 1, "ToDelete")
        CardsRepository(conn).upsert(card)
        conn.commit()

        view = CardsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._on_collection_changed(view._collection_combo.findData(col.collection_id))
        qtbot.wait(50)
        view._delete_card(card)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# E2E: header creado en MasterDetail → visible en CollectionsAbmView combo
# ----------------------------------------------------------------------


def test_header_from_master_detail_visible_in_collections_combo(qtbot, file_db_path):
    """Reproduce el bug original: crear un header en CodesMasterDetailView y
    luego, con la MISMA conn (como hace AdminMainWindow), ver que aparece en el
    combo de CollectionsAbmView al hacer Nuevo, sin reiniciar."""
    conn = create_connection(file_db_path)
    try:
        codes_view = CodesMasterDetailView(conn)
        collections_view = CollectionsAbmView(conn)
        qtbot.addWidget(codes_view)
        qtbot.addWidget(collections_view)
        codes_view.show()
        collections_view.show()

        # Crear un header desde la UI de Cabeceras
        codes_view.headers_abm._inputs["code_header_name"].setText("New Header")
        codes_view.headers_abm._inputs["code_max_length"].setValue(5)
        qtbot.mouseClick(codes_view.headers_abm._save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

        # Ahora simular click en "Nuevo" del ABM de Colecciones
        qtbot.mouseClick(collections_view.abm._new_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

        combo = collections_view.abm._inputs["code_header_id"]
        labels = [combo.itemText(i) for i in range(combo.count())]
        assert "New Header" in labels
    finally:
        conn.close()
```

### [tests/client/__init__.py](tests/client/__init__.py)

_(archivo vacío)_

### [tests/client/dialogs/__init__.py](tests/client/dialogs/__init__.py)

_(archivo vacío)_

### [tests/client/dialogs/test_client_settings_dialog.py](tests/client/dialogs/test_client_settings_dialog.py)

```python
"""Tests del ClientSettingsDialog."""

import pytest

from collections_app.client.dialogs.client_settings_dialog import ClientSettingsDialog
from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import (
    LicenseService,
    LocalHashLicenseValidator,
    SettingsService,
)

VALID_KEY = "secret-123"


def _make_free(memory_db, sample_code_header, name="Free") -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()
    return col


def _make_premium(memory_db, sample_code_header, name="Premium") -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=True,
            license_key_required=LocalHashLicenseValidator.hash_key(VALID_KEY),
        )
    )
    memory_db.commit()
    return col


@pytest.fixture
def free_col(memory_db, sample_code_header):
    return _make_free(memory_db, sample_code_header)


@pytest.fixture
def premium_col(memory_db, sample_code_header):
    return _make_premium(memory_db, sample_code_header)


def test_dialog_lists_all_collections(qtbot, memory_db, free_col, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # placeholder + 2 colecciones
    assert dlg._combo.count() == 3


def test_free_collection_enables_ok_directly(qtbot, memory_db, free_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    idx = dlg._combo.findData(free_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert dlg._license_container.isVisible() is False


def test_premium_collection_shows_license_field(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is False
    assert dlg._license_container.isVisible() is True


def test_validate_correct_key_unlocks_premium(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    dlg._license_input.setText(VALID_KEY)
    dlg._on_validate_license()

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert LicenseService(memory_db).is_unlocked(premium_col.collection_id) is True


def test_validate_wrong_key_keeps_locked(qtbot, memory_db, premium_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    dlg._license_input.setText("wrong")
    dlg._on_validate_license()

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is False
    assert "inválida" in dlg._license_status.text().lower()
    assert LicenseService(memory_db).is_unlocked(premium_col.collection_id) is False


def test_accept_persists_active_collection(qtbot, memory_db, free_col):
    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    idx = dlg._combo.findData(free_col.collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg._on_accept()
    assert dlg.selected_collection_id == free_col.collection_id
    assert SettingsService(memory_db).get_active_collection_id() == free_col.collection_id


def test_already_unlocked_premium_does_not_show_license_section(qtbot, memory_db, premium_col):
    """Si la premium fue desbloqueada antes, el dialog no pide la clave de nuevo."""
    LicenseService(memory_db).unlock(premium_col.collection_id, VALID_KEY)

    dlg = ClientSettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg.show()
    idx = dlg._combo.findData(premium_col.collection_id)
    dlg._combo.setCurrentIndex(idx)

    from PySide6.QtWidgets import QDialogButtonBox

    ok_btn = dlg._buttons.button(QDialogButtonBox.StandardButton.Ok)
    assert ok_btn.isEnabled() is True
    assert dlg._license_container.isVisible() is False
```

### [tests/client/dialogs/test_pdf_preview_dialog.py](tests/client/dialogs/test_pdf_preview_dialog.py)

```python
"""Tests del PdfPreviewDialog: cancel borra temp, save copia y opcionalmente abre."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox

from collections_app.client.dialogs.pdf_preview_dialog import PdfPreviewDialog

# Bytes mínimos válidos de un PDF (header + EOF). Suficiente para que
# QPdfDocument lo reconozca como PDF al abrirlo (puede mostrar página
# vacía o fallar silenciosamente — el dialog cae al fallback).
_MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
    b"xref\n0 4\n"
    b"0000000000 65535 f\n"
    b"0000000009 00000 n\n"
    b"0000000052 00000 n\n"
    b"0000000101 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n160\n%%EOF\n"
)


@pytest.fixture
def temp_pdf(tmp_path) -> Path:
    """Crea un archivo .pdf mínimo válido en tmp_path."""
    p = tmp_path / "preview_input.pdf"
    p.write_bytes(_MINIMAL_PDF)
    return p


def test_cancel_deletes_temp_file(qtbot, temp_pdf):
    """Click Cancelar borra el archivo temp y devuelve None."""
    assert temp_pdf.exists()
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_cancel()
    qtbot.wait(50)
    assert not temp_pdf.exists()
    assert dialog.saved_path() is None


def test_save_copies_to_destination(qtbot, temp_pdf, tmp_path, monkeypatch):
    """Click Guardar copia al destino, borra el temp y setea saved_path."""
    dest = tmp_path / "saved_output.pdf"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *a, **kw: (str(dest), "PDF (*.pdf)")),
    )
    # Mockear QMessageBox.exec para que no bloquee con el "Abrir/OK".
    # En PySide6 QMessageBox.exec retorna el StandardButton presionado.
    monkeypatch.setattr(QMessageBox, "exec", lambda self: None)
    # clickedButton() devuelve None tras nuestro mock → no se intenta abrir.

    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_save()
    qtbot.wait(50)

    assert dest.exists()
    assert dest.read_bytes() == _MINIMAL_PDF
    assert not temp_pdf.exists()
    assert dialog.saved_path() == dest


def test_save_canceled_keeps_temp(qtbot, temp_pdf, monkeypatch):
    """Si el usuario cancela el QFileDialog: NO borra el temp ni cierra dialog."""
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *a, **kw: ("", "")),  # path vacío = cancelado
    )
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog._on_save()
    qtbot.wait(50)
    # El temp sigue ahí, saved_path sigue None
    assert temp_pdf.exists()
    assert dialog.saved_path() is None


def test_close_event_cleans_temp(qtbot, temp_pdf):
    """Cerrar el dialog con la X (o reject) también borra el temp."""
    dialog = PdfPreviewDialog(
        temp_pdf_path=temp_pdf,
        suggested_filename="output.pdf",
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    dialog.close()
    qtbot.wait(50)
    assert not temp_pdf.exists()
```

### [tests/client/views/__init__.py](tests/client/views/__init__.py)

_(archivo vacío)_

### [tests/client/views/test_album_view.py](tests/client/views/test_album_view.py)

```python
"""Tests del AlbumView (cliente)."""

from pathlib import Path

import pytest

from collections_app.client.views import album_view as view_mod
from collections_app.client.views.album_view import AlbumView
from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)

# `db_path` dummy: el worker real nunca arranca (lo stubeamos), por lo
# tanto el path no se usa para abrir conexiones.
_DUMMY_DB_PATH = Path(":memory:")


@pytest.fixture
def album_setup(memory_db, sample_collection):
    """Cards y inventory parcial: ARG-1 repetida, ARG-2 tengo, ARG-3 falta."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "ARGENTINA"))

    cards = CardsRepository(memory_db)
    cards.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    cards.upsert(Card(cid, "ARG", 2, "Emi Martinez"))
    cards.upsert(Card(cid, "ARG", 3, "Nahuel Molina"))

    inv = InventoryRepository(memory_db)
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=3))
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=1))
    memory_db.commit()
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, album_setup):
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    v.show()
    return v


# ----------------------------------------------------------------------
# Construcción
# ----------------------------------------------------------------------


def test_album_view_loads_without_error(qtbot, view):
    """Construye los 6 botones (album / missing_full / missing_summary /
    duplicates_full / duplicates_summary / owned)."""
    assert len(view._buttons) == 6


def test_image_count_shows_zero_when_no_crests(
    qtbot, memory_db, album_setup, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    text = v._image_count_label.text()
    # 0 escudos cargados / 1 total
    assert "0 / 1" in text


def test_image_count_shows_loaded_crests(qtbot, memory_db, album_setup, tmp_path, monkeypatch):
    (tmp_path / "ARG.png").touch()
    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    v = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(v)
    assert "1 / 1" in v._image_count_label.text()


# ----------------------------------------------------------------------
# Botones de generación: dispatch al worker con el kind correcto
# ----------------------------------------------------------------------


def _stub_worker(captured: dict):
    """Crea una clase _StubWorker que captura los args al construirse."""

    class _StubWorker:
        finished_ok = type("S", (), {"connect": lambda *a, **k: None})()
        failed = type("S", (), {"connect": lambda *a, **k: None})()

        def __init__(self, db_path, collection_id, output_path, kind, parent=None):
            captured["db_path"] = db_path
            captured["collection_id"] = collection_id
            captured["output_path"] = output_path
            captured["kind"] = kind

        def start(self):
            pass

    return _StubWorker


@pytest.mark.parametrize(
    ("button_idx", "expected_kind", "expected_prefix"),
    [
        (0, "album", "Album"),
        (1, "missing_full", "Faltantes_Completo"),
        (2, "missing_summary", "Faltantes_Resumido"),
        (3, "duplicates_full", "Repetidas_Completo"),
        (4, "duplicates_summary", "Repetidas_Resumido"),
        (5, "owned", "Tengo"),
    ],
)
def test_each_button_dispatches_correct_kind_to_worker(
    qtbot, view, monkeypatch, button_idx, expected_kind, expected_prefix
):
    """Cada uno de los 5 botones lanza el worker con el `kind` correcto.

    Bajo el flujo nuevo, el botón NO abre QFileDialog — genera a un
    archivo temporal y luego abre el preview. Solo verificamos que el
    worker arranca con los args correctos.
    """
    captured: dict = {}
    monkeypatch.setattr(view_mod, "_PdfWorker", _stub_worker(captured))

    view._buttons[button_idx].click()

    assert captured["kind"] == expected_kind
    assert captured["collection_id"] == view.collection.collection_id
    # output_path es un archivo temporal (.pdf) — verificamos forma.
    out = captured["output_path"]
    assert isinstance(out, Path)
    assert out.suffix == ".pdf"
    # El nombre sugerido (que pasaría al preview) tiene el prefijo correcto.
    suggested = view._suggested_filename(expected_kind)
    assert suggested.startswith(expected_prefix + "_")


def test_buttons_disabled_during_generation(qtbot, view, monkeypatch):
    """Mientras el worker corre, los botones quedan deshabilitados."""
    captured: dict = {}
    monkeypatch.setattr(view_mod, "_PdfWorker", _stub_worker(captured))
    view._buttons[0].click()
    # Después del click, todos los botones quedan deshabilitados hasta on_ok.
    assert all(not b.isEnabled() for b in view._buttons)


# ----------------------------------------------------------------------
# set_active_collection
# ----------------------------------------------------------------------


def test_set_active_collection_refreshes_image_count(
    qtbot, memory_db, album_setup, sample_code_header, tmp_path, monkeypatch
):
    """Cambiar la colección activa refresca el contador de escudos."""
    from collections_app.core.models import Collection
    from collections_app.core.repositories import CollectionsRepository

    other = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Other",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()

    monkeypatch.setattr(
        "collections_app.client.views.album_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )
    view = AlbumView(memory_db, _DUMMY_DB_PATH, album_setup)
    qtbot.addWidget(view)
    initial = view._image_count_label.text()
    view.set_active_collection(other)
    assert view._image_count_label.text() != initial
```

### [tests/client/views/test_card_loader.py](tests/client/views/test_card_loader.py)

```python
"""Tests del CardLoaderView.

Reescritos tras rediseño en el cual:
- Se removió el checkbox "Tiene código de prefijo".
- Se removió el DEFAULT_CODE = "NON" hardcodeado.
- requires_code=False → solo Número/Cantidad, búsqueda por find_by_number.
- requires_code=True → Código siempre obligatorio.
- Ambigüedad (>1 match en find_by_number) muestra combo limitado.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox

from collections_app.client.views.card_loader import CardLoaderView
from collections_app.core.models import Card, CodeLine, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def collection_no_code(memory_db, sample_code_header):
    """Collection con requires_code=False y cards de ejemplo.

    Los códigos del header son `ARG`, `BRA`, `MR`. Hay un número repetido
    (24) en ARG y BRA para tests de ambigüedad.
    """
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("MR", "MASTER ROOKIES")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Adrenalyne",
            card_count=100,
            requires_code=False,  # ← clave del nuevo diseño
            code_field_name=None,
            code_header_id=hid,
        )
    )
    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(col.collection_id, "ARG", 24, "LIONEL MESSI"))
    cards_repo.upsert(Card(col.collection_id, "BRA", 24, "VINICIUS"))  # ambiguo con ARG-24
    cards_repo.upsert(Card(col.collection_id, "ARG", 1, "GOLDEN BALLERS"))
    cards_repo.upsert(Card(col.collection_id, "MR", 5, "PAZ"))
    memory_db.commit()
    return col


@pytest.fixture
def collection_with_code(memory_db, sample_code_header):
    """Collection con requires_code=True (modo Stickers Panini)."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("S1", "Set 1"), ("S2", "Set 2")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Stickers",
            card_count=20,
            requires_code=True,
            code_field_name="Set",
            code_header_id=hid,
        )
    )
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S1", 1, "Sticker A"))
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S2", 1, "Sticker B"))
    memory_db.commit()
    return col


# ----------------------------------------------------------------------
# Tests de visibilidad y foco
# ----------------------------------------------------------------------


def test_no_checkbox_visible(qtbot, memory_db, collection_no_code):
    """El checkbox de prefijo ya no existe en ningún caso."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    checkboxes = view.findChildren(QCheckBox)
    assert checkboxes == []


def test_no_code_field_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_edit.isVisible() is False
    assert view._code_label.isVisible() is False


def test_code_field_always_visible_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_edit.isVisible() is True
    assert view._code_label.isVisible() is True


def test_focus_on_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._number_input.hasFocus()


def test_focus_on_code_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._code_edit.hasFocus()


# ----------------------------------------------------------------------
# Validación con find_by_number (requires_code=False)
# ----------------------------------------------------------------------


def test_find_by_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    """Con número único MR-5, autocompleta país/nombre y muestra Nueva."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    assert view._name_input.text() == "PAZ"
    assert "MASTER ROOKIES" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


def test_unknown_number_shows_clear_message(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("9999")
    assert "9999" in view._status_label.text()
    assert "no existe" in view._status_label.text().lower()
    assert view._name_input.text() == ""


def test_ambiguous_number_shows_code_selector(qtbot, memory_db, collection_no_code):
    """Número 24 está en ARG y BRA → debe mostrar el campo y pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    assert view._has_ambiguity is True
    assert view._code_edit.isVisible() is True
    # El completer solo debe contener los códigos ambiguos (ARG y BRA, no MR)
    assert view._valid_code_ids == {"ARG", "BRA"}
    assert (
        "especificá" in view._status_label.text().lower()
        or "especifica" in view._status_label.text().lower()
    )


def test_choosing_code_after_ambiguity_validates_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Elegir ARG escribiéndolo y disparando Enter
    view._code_edit.setText("ARG")
    view._on_code_return_pressed()
    assert view._name_input.text() == "LIONEL MESSI"
    assert "ARGENTINA" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


# ----------------------------------------------------------------------
# Save: dispatch correcto entre by_number y con código
# ----------------------------------------------------------------------


def test_save_uses_add_card_by_number_when_unambiguous(qtbot, memory_db, collection_no_code):
    """Caso Adrenalyn: número único → save sin pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_save_uses_add_card_when_user_specified_code(qtbot, memory_db, collection_no_code):
    """Tras desambiguar, el save usa el código elegido."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Ambigüedad: el campo de código aparece. Elegir BRA.
    view._code_edit.setText("BRA")
    view._on_code_return_pressed()
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item_arg = InventoryRepository(memory_db).get(collection_no_code.collection_id, "ARG", 24)
    item_bra = InventoryRepository(memory_db).get(collection_no_code.collection_id, "BRA", 24)
    assert item_arg is None or item_arg.quantity == 0
    assert item_bra is not None
    assert item_bra.quantity == 1


def test_save_alta_increments_inventory_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    view._qty_input.setText("3")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 3


def test_save_baja_decrements_inventory_correctly(qtbot, memory_db, collection_no_code):
    InventoryService(memory_db).add_card_by_number(collection_no_code.collection_id, 5, 3)
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._baja_radio.setChecked(True)
    view._number_input.setText("5")
    view._qty_input.setText("2")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_form_resets_after_save_keeping_focus(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._number_input.text() == ""
    assert view._qty_input.text() == "1"
    assert view._country_input.text() == ""
    assert view._number_input.hasFocus()


# ----------------------------------------------------------------------
# Regresión: bug original (NON-24 hardcodeado)
# ----------------------------------------------------------------------


def test_typing_number_24_finds_messi_in_adrenalyn_like_setup(qtbot, memory_db, collection_no_code):
    """Reproduce el bug: con requires_code=False, tipear '24' debe encontrar
    la card sin importar el código (vía find_by_number, no NON-24)."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # No debe decir "NON-24 no existe"; o muestra info (si fuera unívoco)
    # o pide desambiguar (este caso, es ambiguo).
    msg = view._status_label.text().lower()
    assert "non-24" not in msg
    assert "no existe" not in msg or "especificá" in msg


# ----------------------------------------------------------------------
# Autocompletado: QLineEdit + QCompleter (reemplazo del QComboBox)
# ----------------------------------------------------------------------


def test_completer_contains_code_and_name(qtbot, memory_db, collection_with_code):
    """El modelo del completer tiene strings tipo 'S1 - Set 1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    model = view._completer.model()
    items = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "S1 - Set 1" in items
    assert "S2 - Set 2" in items


def test_enter_exact_match_selects_code(qtbot, memory_db, collection_with_code):
    """Texto 'S1' + Enter → _selected_code_id='S1' y foco en número."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    qtbot.wait(50)  # dejar que Qt procese los focus events
    assert view._selected_code_id == "S1"
    assert view._number_input.hasFocus()


def test_enter_case_insensitive(qtbot, memory_db, collection_with_code):
    """Texto en minúsculas 's1' + Enter → matchea 'S1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("s1")
    view._on_code_return_pressed()
    assert view._selected_code_id == "S1"


def test_enter_no_match_does_not_select(qtbot, memory_db, collection_with_code):
    """Texto que no matchea ningún code → _selected_code_id queda en None."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("ZZZ")
    view._on_code_return_pressed()
    assert view._selected_code_id is None


def test_enter_single_partial_match_auto_selects(qtbot, memory_db, sample_code_header):
    """Solo 'ARG' empieza con 'AR' → tipear 'AR' + Enter selecciona 'ARG'."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")]:
        lines_repo.upsert(CodeLine(hid, code, name))
    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Test",
            card_count=10,
            requires_code=True,
            code_field_name="P",
            code_header_id=hid,
        )
    )
    memory_db.commit()
    view = CardLoaderView(memory_db, col)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("AR")  # 'AR' contained only in 'ARG'
    view._on_code_return_pressed()
    assert view._selected_code_id == "ARG"


def test_text_change_after_selection_clears_selection(qtbot, memory_db, collection_with_code):
    """Si el usuario cambia el texto después de seleccionar, _selected_code_id se invalida."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    assert view._selected_code_id == "S1"
    # Cambiar texto a algo que no matchea
    view._code_edit.setText("S")  # prefix incompleto: no matchea exactamente
    assert view._selected_code_id is None


def test_on_code_selected_extracts_code_id(qtbot, memory_db, collection_with_code):
    """Llamar _on_code_selected('S1 - Set 1') → extrae 'S1' y setea el text."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._on_code_selected("S1 - Set 1")
    qtbot.wait(50)  # dejar que Qt procese los focus events
    assert view._selected_code_id == "S1"
    assert view._code_edit.text() == "S1"
    assert view._number_input.hasFocus()


def test_on_code_selected_ignores_invalid(qtbot, memory_db, collection_with_code):
    """Si pasamos un string inválido, no se setea selected_code_id."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._on_code_selected("FAKE - No existe")
    assert view._selected_code_id is None


def test_add_card_blocked_when_no_code_selected(qtbot, memory_db, collection_with_code):
    """requires_code=True + sin code seleccionado: save bloqueado."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Tipear número y cantidad sin haber seleccionado código
    view._number_input.setText("1")
    view._qty_input.setText("1")
    view._save_card()
    # Inventario debe seguir vacío
    item = InventoryRepository(memory_db).get(collection_with_code.collection_id, "S1", 1)
    assert item is None or item.quantity == 0
    # Status debe avisar la falta de código
    assert "código" in view._status_label.text().lower()


def test_completer_uses_contains_match_filter(qtbot, memory_db, collection_with_code):
    """El completer está configurado en MatchContains (no MatchStartsWith)."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert view._completer.filterMode() == Qt.MatchFlag.MatchContains
    assert view._completer.caseSensitivity() == Qt.CaseSensitivity.CaseInsensitive


def test_arrow_down_opens_completer_popup(qtbot, memory_db, collection_with_code):
    """Down/Up con popup cerrado: abrir el popup para que se pueda navegar."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    qtbot.wait(50)

    popup = view._completer.popup()
    assert popup is not None
    assert popup.isVisible() is False
    qtbot.keyClick(view._code_edit, Qt.Key.Key_Down)
    # waitUntil es más robusto que wait fijo: poll hasta que el popup
    # se muestre o timeout (focus events son flaky en pytest-qt headless).
    qtbot.waitUntil(lambda: popup.isVisible(), timeout=2000)
    assert popup.isVisible() is True


def test_arrow_down_uses_text_as_prefix_filter(qtbot, memory_db, sample_code_header):
    """Tipear 'AR' + Down filtra el popup a los matches que contienen 'AR'."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("MAR", "MOROCCO")]:
        lines_repo.upsert(CodeLine(hid, code, name))
    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=True,
            code_field_name="P",
            code_header_id=hid,
        )
    )
    memory_db.commit()
    view = CardLoaderView(memory_db, col)
    qtbot.addWidget(view)
    view.show()

    view._code_edit.setText("AR")
    qtbot.keyClick(view._code_edit, Qt.Key.Key_Down)
    # Tras complete() con prefix "AR", el modelo de completion solo
    # contiene los matches con "AR" (ARG y MAR, no BRA).
    matches = []
    completion_model = view._completer.completionModel()
    for i in range(completion_model.rowCount()):
        matches.append(completion_model.data(completion_model.index(i, 0)))
    assert any("ARG" in m for m in matches)
    assert any("MAR" in m for m in matches)
    assert not any("BRA - " in m for m in matches)


# ----------------------------------------------------------------------
# Flujo post-carga: mantener SET seleccionado + Enter inmediato → número
# ----------------------------------------------------------------------


def _save_one_card(view, qtbot) -> None:
    """Helper: completa un alta válida (S1, número 1, qty 1)."""
    view._code_edit.setText("S1")
    view._on_code_return_pressed()  # confirma S1, foco va al número
    view._number_input.setText("1")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)


def test_after_load_focus_goes_to_code_field(qtbot, memory_db, collection_with_code):
    """Post-carga (requires_code): foco vuelve al SET con texto seleccionado."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._code_edit.hasFocus()
    # selectedText() == text() significa "todo el contenido seleccionado"
    assert view._code_edit.selectedText() == view._code_edit.text() == "S1"


def test_after_load_set_confirmed_flag_is_true(qtbot, memory_db, collection_with_code):
    """Post-carga setea `_set_confirmed=True` para el atajo de Enter."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._set_confirmed is True


def test_enter_on_set_without_change_goes_to_number(qtbot, memory_db, collection_with_code):
    """Set confirmado + Enter sin tipear nada → foco al número, set intacto."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    # Estado pre-Enter: set confirmado, "S1" seleccionado.
    assert view._set_confirmed is True
    # Enter sobre el SET (sin tipear nada extra)
    view._on_code_return_pressed()
    assert view._number_input.hasFocus()
    assert view._selected_code_id == "S1"
    # El flag se consume al saltar
    assert view._set_confirmed is False


def test_typing_in_set_clears_confirmed_flag(qtbot, memory_db, collection_with_code):
    """Input real del usuario en el SET invalida `_set_confirmed`."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._set_confirmed is True
    # Tipear (qtbot.keyClicks dispara textEdited a diferencia de setText).
    qtbot.keyClicks(view._code_edit, "X")
    assert view._set_confirmed is False
    # Tampoco quedó código seleccionado (X no matchea ningún code_id).
    assert view._selected_code_id is None


def test_enter_on_set_with_change_validates_new_code(qtbot, memory_db, collection_with_code):
    """Si el usuario cambia el SET a otro válido, Enter selecciona el nuevo."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    # Reemplazar S1 por S2 con input real (selectAll ya hizo qtbot)
    view._code_edit.clear()
    qtbot.keyClicks(view._code_edit, "S2")
    view._on_code_return_pressed()
    # Debió validar y seleccionar S2 (no haber tomado el atajo de set_confirmed).
    assert view._selected_code_id == "S2"
    assert view._number_input.hasFocus()


def test_highlight_first_completion_sets_row_zero(qtbot, memory_db, collection_with_code):
    """`_highlight_first_completion` resalta el primer ítem visible."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Forzar al completer a tener completions disponibles.
    view._completer.setCompletionPrefix("")  # sin filtro: todos los items
    view._highlight_first_completion()
    assert view._completer.currentRow() == 0


# ----------------------------------------------------------------------
# Regresión: el campo de código se LIMPIA en colecciones sin requires_code
# ----------------------------------------------------------------------


def test_no_requires_code_after_load_focuses_number_directly(qtbot, memory_db, collection_no_code):
    """Sin requires_code: post-carga vuelve directo al número (sin SET)."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")  # MR-5 está en el catálogo, único
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._number_input.hasFocus()
    assert view._number_input.text() == ""


# ----------------------------------------------------------------------
# Regresión: el completer inserta solo el code_id, no la etiqueta completa
# ----------------------------------------------------------------------


def test_completer_inserts_only_code_id_not_full_label(qtbot, memory_db, collection_with_code):
    """Activar un ítem del popup deja solo 'S1' en el campo, no 'S1 - Set 1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()

    view._completer.setCompletionPrefix("")
    completion_model = view._completer.completionModel()
    assert completion_model.rowCount() > 0
    first_idx = completion_model.index(0, 0)
    full_label = completion_model.data(first_idx)
    assert " - " in full_label

    inserted = view._completer.pathFromIndex(first_idx)
    assert " - " not in inserted
    assert inserted.upper() in view._valid_code_ids
    assert inserted == full_label.split(" - ", 1)[0].strip()


# ----------------------------------------------------------------------
# Regresión: tipear sobre SET seleccionado no debe auto-insertar
# el ítem resaltado (era 'FWC' tras tipear 'f' por culpa de
# popup.setCurrentIndex disparando el slot interno del completer).
# ----------------------------------------------------------------------


def test_typing_letter_on_selected_set_does_not_autoinsert_completion(
    qtbot, memory_db, collection_with_code
):
    """Post-carga con SET seleccionado: tipear una letra reemplaza el texto.

    Antes del fix, `_highlight_first_completion` llamaba
    `popup.setCurrentIndex(...)` sin bloquear signals del completer,
    lo que disparaba el auto-insert: tipear 'f' dejaba 'FWC' (o el
    primer match del popup) en el campo en vez de 'f'.
    """
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    # Cargar una card para llegar al estado post-carga (SET seleccionado).
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    view._number_input.setText("1")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(100)
    assert view._code_edit.text() == "S1"
    assert view._code_edit.selectedText() == "S1"
    assert view._set_confirmed is True

    # Tipear 'S' debería reemplazar la selección (texto = 'S'), NO
    # auto-completar a 'S1' o 'S2'.
    qtbot.keyClick(view._code_edit, Qt.Key.Key_S)
    qtbot.wait(100)
    assert view._code_edit.text() == "s", f"Esperado 's', got {view._code_edit.text()!r}"
    assert view._set_confirmed is False


# ----------------------------------------------------------------------
# Tinte de los inputs según el modo Alta/Baja
# ----------------------------------------------------------------------


def test_operation_frame_bg_reflects_alta_mode_by_default(qtbot, memory_db, collection_with_code):
    """Al construir la view (Alta por default), el frame trae el verde."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert INPUT_BG_ALTA.lower() in view._operation_frame.styleSheet().lower()


def test_operation_frame_bg_changes_to_baja_when_radio_toggled(
    qtbot, memory_db, collection_with_code
):
    """Al togglear Baja, el frame pasa al tinte rojo."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA, INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()

    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._operation_frame.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() not in view._operation_frame.styleSheet().lower()
    # Y volver a Alta restaura el verde
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._operation_frame.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() not in view._operation_frame.styleSheet().lower()


# ----------------------------------------------------------------------
# Tinte Alta/Baja también pinta los campos editables (no solo el frame)
# ----------------------------------------------------------------------


def test_alta_applies_green_background_to_fields(qtbot, memory_db, collection_with_code):
    """Modo Alta: número/qty/código tienen fondo verde."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() in view._qty_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() in view._code_edit.styleSheet().lower()


def test_baja_applies_pink_background_to_fields(qtbot, memory_db, collection_with_code):
    """Modo Baja: número/qty/código tienen fondo rosa."""
    from collections_app.shared_ui.theme import INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() in view._qty_input.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() in view._code_edit.styleSheet().lower()


def test_field_color_changes_when_radio_toggles(qtbot, memory_db, collection_with_code):
    """Toggle Alta→Baja→Alta cambia el color del fondo de los campos."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA, INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Estado inicial Alta
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()
    # Cambiar a Baja
    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() not in view._number_input.styleSheet().lower()
    # Volver a Alta
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()


def test_error_shows_red_border_keeping_bg_color(qtbot, memory_db, collection_with_code):
    """Tras error: borde rojo + bg del modo. Tras revert: solo bg."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    # Modo Alta + disparar error en el código.
    view._alta_radio.setChecked(True)
    view._show_field_error("code")
    style_during = view._code_edit.styleSheet().lower()
    assert "red" in style_during
    assert INPUT_BG_ALTA.lower() in style_during  # bg conservado durante el error
    # Esperar a que expire el QTimer de 1000ms.
    qtbot.wait(1200)
    style_after = view._code_edit.styleSheet().lower()
    assert "red" not in style_after
    assert INPUT_BG_ALTA.lower() in style_after  # vuelve al verde, no a vacío


def test_code_field_gets_color_when_visible(qtbot, memory_db, collection_with_code):
    """Con requires_code=True el campo de código también se tinta."""
    from collections_app.shared_ui.theme import INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._baja_radio.setChecked(True)
    assert view._code_edit.isVisible() is True
    assert INPUT_BG_BAJA.lower() in view._code_edit.styleSheet().lower()


# ----------------------------------------------------------------------
# Fix 2: bloquear Tab/Enter cuando el campo está vacío
# ----------------------------------------------------------------------


def test_empty_number_field_blocks_return(qtbot, memory_db, collection_no_code):
    """Number vacío + Enter: NO se busca card, foco permanece en number."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._number_input.setFocus()
    view._number_input.clear()
    qtbot.wait(50)

    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    # No se buscó card → no se autocompletó nombre/país.
    assert view._name_input.text() == ""
    assert view._country_input.text() == ""
    # Foco permanece en number_input.
    assert view._number_input.hasFocus()


def test_empty_number_field_blocks_tab(qtbot, memory_db, collection_no_code):
    """Number vacío + Tab: el foco NO sale del número."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._number_input.setFocus()
    view._number_input.clear()
    qtbot.wait(50)

    qtbot.keyClick(view._number_input, Qt.Key.Key_Tab)
    qtbot.wait(50)
    # Tab fue consumido → foco sigue en number_input.
    assert view._number_input.hasFocus()


def test_empty_code_field_blocks_return(qtbot, memory_db, collection_with_code):
    """Code vacío + Enter (requires_code=True): no avanza, foco permanece."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    view._code_edit.clear()
    view._selected_code_id = None  # asegurar estado limpio
    qtbot.wait(50)

    qtbot.keyClick(view._code_edit, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._code_edit.hasFocus()
    assert view._selected_code_id is None  # nada se validó


def test_nonempty_number_field_allows_navigation(qtbot, memory_db, collection_no_code):
    """Number con contenido + Enter: SÍ avanza al siguiente campo."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._number_input.setText("5")  # MR-5 existe en el catálogo
    view._number_input.setFocus()
    qtbot.wait(50)

    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    # Avance correcto: el navigator pasa de number a qty.
    assert view._qty_input.hasFocus()
    # Y la card fue encontrada (validación lateral por textChanged).
    assert "PAZ" in view._name_input.text()


def test_empty_field_shows_red_border_then_reverts(qtbot, memory_db, collection_no_code):
    """Vacío + Enter: borde rojo durante 1s, luego vuelve al color del modo."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._alta_radio.setChecked(True)
    view._number_input.setFocus()
    view._number_input.clear()
    qtbot.wait(50)

    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    style_during = view._number_input.styleSheet().lower()
    assert "red" in style_during
    qtbot.wait(1200)
    style_after = view._number_input.styleSheet().lower()
    assert "red" not in style_after
    assert INPUT_BG_ALTA.lower() in style_after


# ----------------------------------------------------------------------
# Fix 3: foco automático al togglear el radio Alta/Baja
# ----------------------------------------------------------------------


def test_radio_alta_focuses_code_field_when_requires_code(qtbot, memory_db, collection_with_code):
    """requires_code=True + click Alta → foco en SET."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    # Sacar el foco primero para verificar que el toggle lo trae de vuelta.
    view._qty_input.setFocus()
    qtbot.wait(50)
    # Forzar transición False→True: ir a Baja, luego a Alta.
    view._baja_radio.setChecked(True)
    view._qty_input.setFocus()
    qtbot.wait(50)
    view._alta_radio.setChecked(True)
    qtbot.wait(50)
    assert view._code_edit.hasFocus()


def test_radio_alta_focuses_number_field_when_no_code(qtbot, memory_db, collection_no_code):
    """requires_code=False + click Alta → foco en NÚMERO."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._qty_input.setFocus()
    qtbot.wait(50)
    view._baja_radio.setChecked(True)
    view._qty_input.setFocus()
    qtbot.wait(50)
    view._alta_radio.setChecked(True)
    qtbot.wait(50)
    assert view._number_input.hasFocus()


def test_radio_baja_focuses_code_field_when_requires_code(qtbot, memory_db, collection_with_code):
    """requires_code=True + click Baja → foco en SET."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._qty_input.setFocus()
    qtbot.wait(50)
    view._baja_radio.setChecked(True)
    qtbot.wait(50)
    assert view._code_edit.hasFocus()


def test_radio_baja_focuses_number_when_no_code(qtbot, memory_db, collection_no_code):
    """requires_code=False + click Baja → foco en NÚMERO."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._qty_input.setFocus()
    qtbot.wait(50)
    view._baja_radio.setChecked(True)
    qtbot.wait(50)
    assert view._number_input.hasFocus()


def test_toggled_false_does_not_change_focus(qtbot, memory_db, collection_with_code):
    """Llamar el slot directamente con checked=False es no-op (no cambia foco)."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._qty_input.setFocus()
    qtbot.wait(50)
    # Invocar el slot con checked=False explícitamente.
    view._on_operation_changed(False)
    qtbot.wait(50)
    # El foco NO se movió a code_edit ni number_input — sigue en qty.
    assert view._qty_input.hasFocus()
```

### [tests/client/views/test_compare_view.py](tests/client/views/test_compare_view.py)

```python
"""Tests del CompareView (smoke + flujos clave).

No tocamos QFileDialog (no se puede headless). Para los flujos de
generación e importación, escribimos directamente el archivo y llamamos
los handlers internos (`_run_comparison`, etc.). Los workers se ejecutan
síncrono usando `worker.run()` en el thread del test cuando es necesario.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from collections_app.client.views.compare_view import CompareView
from collections_app.core.models import Card, ExchangeCard, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services import ExchangeService

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def collection_with_inv(file_db_path):
    """File DB (necesaria porque los workers abren conexiones nuevas).

    Construimos: collection requires_code=True con cards y un inventario
    inicial. Devolvemos (db_path, conn_principal, collection).
    """
    from collections_app.core.db.connection import create_connection
    from collections_app.core.models import CodeHeader, Collection
    from collections_app.core.repositories import (
        CodesHeadersRepository,
        CollectionsRepository,
    )

    conn = create_connection(file_db_path)
    hdr = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name="Test", code_max_length=5)
    )
    col = CollectionsRepository(conn).create(
        Collection(
            collection_id=None,
            collection_name="TestCol",
            card_count=4,
            requires_code=True,
            code_field_name="País",
            code_header_id=hdr.code_header_id,
        )
    )
    cards_repo = CardsRepository(conn)
    cards = [
        Card(col.collection_id, "ARG", 1, "Messi"),
        Card(col.collection_id, "ARG", 2, "Martínez"),
        Card(col.collection_id, "BRA", 1, "Vinícius"),
        Card(col.collection_id, "BRA", 2, "Neymar"),
    ]
    cards_repo.bulk_upsert(cards)
    inv = InventoryRepository(conn)
    inv.upsert(InventoryItem(col.collection_id, "ARG", 2, quantity=2))
    inv.upsert(InventoryItem(col.collection_id, "BRA", 2, quantity=1))
    conn.commit()
    return file_db_path, conn, col


# ----------------------------------------------------------------------
# Smoke
# ----------------------------------------------------------------------


def test_compare_view_constructs_and_disables_actions_initially(qtbot, collection_with_inv):
    db_path, conn, col = collection_with_inv
    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()
    # Sin comparación cargada los botones de acción están deshabilitados
    assert view._pdf_button.isEnabled() is False
    assert view._exec_button.isEnabled() is False


def test_set_active_collection_clears_state(qtbot, collection_with_inv, tmp_path):
    db_path, conn, col = collection_with_inv
    # Pre-cargar comparación manualmente
    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    # Generar archivo del propio usuario y simular importación del mismo
    # archivo (compare consigo mismo → resultado vacío pero válido).
    out = tmp_path / "self.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)
    view._other_file = ExchangeService(conn).load_exchange_file(out)
    view._run_comparison()

    # Cambiar de colección debe limpiar el estado
    view.set_active_collection(col)
    assert view._comparison is None
    assert view._other_file is None
    assert view._exec_button.isEnabled() is False


# ----------------------------------------------------------------------
# Flujo completo de comparación
# ----------------------------------------------------------------------


def test_compare_two_users_populates_grids_correctly(qtbot, collection_with_inv, tmp_path):
    db_path, conn, col = collection_with_inv
    cid = col.collection_id

    # Usuario 1 (yo): tengo ARG-2 ×2, BRA-2 ×1, no tengo ARG-1 ni BRA-1.
    # Generamos mi snapshot en otro path (que el view ignora — el view
    # genera su propio snapshot al comparar) pero usamos el mismo path
    # como "archivo del otro usuario" tras editar el inventario.

    # Construimos un "otro usuario" con inventario diferente:
    # tiene ARG-1 ×2 (repetida) y BRA-1 ×1 (una sola). Le faltan ARG-2 y BRA-2.
    # Para eso reutilizamos la DB pero generamos manualmente el ExchangeFile.
    from collections_app.core.models import ExchangeFile

    other_file = ExchangeFile(
        app="CollectionsApp",
        version="1.0",
        collection_id=cid,
        collection_name=col.collection_name,
        generated_at="2026-05-04T00:00:00+00:00",
        missing=[
            ExchangeCard("ARG", 2, "Martínez"),  # le falta lo que yo tengo
            ExchangeCard("BRA", 2, "Neymar"),  # le falta lo que yo tengo
        ],
        duplicates=[
            ExchangeCard("ARG", 1, "Messi", 2),  # tiene repetida lo que yo necesito
            ExchangeCard("BRA", 1, "Vinícius", 2),  # tiene repetida lo que yo necesito
        ],
    )
    # Recalculamos su checksum y escribimos al disco para load_exchange_file
    svc = ExchangeService(conn)
    other_file.checksum = svc._compute_checksum(other_file)  # noqa: SLF001
    other_path = tmp_path / "other.colexchange"
    svc._write_file(other_file, other_path)  # noqa: SLF001

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    # Simular importación (sin pasar por el QFileDialog): cargamos manual
    loaded = ExchangeService(conn).load_exchange_file(other_path)
    view._other_file = loaded
    view._run_comparison()

    # i_need: ARG-1 y BRA-1 (mis faltantes que el otro tiene repetidas)
    # i_can_offer: ARG-2 (qty=2 → repetida) — BRA-2 tengo qty=1, no es repetida
    assert view._comparison is not None
    need_codes = {(c.code_id, c.card_number) for c in view._comparison.i_need}
    offer_codes = {(c.code_id, c.card_number) for c in view._comparison.i_can_offer}
    assert need_codes == {("ARG", 1), ("BRA", 1)}
    assert offer_codes == {("ARG", 2)}

    # Las grillas reflejan el resultado
    assert view._i_need_list.count() == 2
    assert view._i_offer_list.count() == 1
    # Botones habilitados ahora que hay comparación
    assert view._pdf_button.isEnabled() is True
    assert view._exec_button.isEnabled() is True


def test_import_rejects_different_collection(qtbot, collection_with_inv, tmp_path, monkeypatch):
    """Si el archivo del otro usuario es de otra colección, mostrar warning."""
    db_path, conn, col = collection_with_inv
    from collections_app.core.models import ExchangeFile

    # Archivo de OTRA colección
    other_file = ExchangeFile(
        app="CollectionsApp",
        version="1.0",
        collection_id=999,  # ← distinta a la activa
        collection_name="Otra",
        generated_at="2026-05-04T00:00:00+00:00",
    )
    svc = ExchangeService(conn)
    other_file.checksum = svc._compute_checksum(other_file)  # noqa: SLF001
    path = tmp_path / "wrong.colexchange"
    svc._write_file(other_file, path)  # noqa: SLF001

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    # Mockear QFileDialog y QMessageBox para no abrir UI
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", staticmethod(lambda *a, **kw: (str(path), ""))
    )
    captured = {}

    def fake_warning(parent, title, text):
        captured["title"] = title
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", staticmethod(fake_warning))

    view._on_import_file()

    assert "Colección distinta" in captured.get("title", "")
    assert view._other_file is None  # no se cargó


def test_import_rejects_invalid_checksum(qtbot, collection_with_inv, tmp_path, monkeypatch):
    """Archivo con checksum inválido: warning + no se carga."""
    db_path, conn, col = collection_with_inv
    import json

    # Generar archivo válido y luego corromperlo
    out = tmp_path / "tampered.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["duplicates"].append(
        {"code_id": "FAKE", "card_number": 999, "card_name": "Hacked", "quantity": 5}
    )
    out.write_text(json.dumps(data), encoding="utf-8")

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", staticmethod(lambda *a, **kw: (str(out), ""))
    )
    captured = {}

    def fake_warning(parent, title, text):
        captured["title"] = title
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", staticmethod(fake_warning))

    view._on_import_file()

    assert "Archivo inválido" in captured.get("title", "")
    assert "checksum" in captured.get("text", "").lower()
    assert view._other_file is None
```

### [tests/client/views/test_inventory_view.py](tests/client/views/test_inventory_view.py)

```python
"""Tests del InventoryView."""

import pytest

from collections_app.client.views.inventory_view import (
    FILTER_ALL,
    STATUS_MISSING,
    STATUS_OWNED,
    STATUS_REPEATED,
    InventoryView,
)
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def inventory_setup(memory_db, sample_collection):
    """Catálogo con 5 cards (3 ARG + 2 BRA) e inventario parcial."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines.upsert(CodeLine(hid, "BRA", "Brasil"))

    cards = CardsRepository(memory_db)
    cards.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    cards.upsert(Card(cid, "ARG", 2, "Emiliano Martinez"))
    cards.upsert(Card(cid, "ARG", 3, "Nahuel Molina"))
    cards.upsert(Card(cid, "BRA", 1, "Vinicius"))
    cards.upsert(Card(cid, "BRA", 2, "Neymar"))

    inv = InventoryService(memory_db)
    inv.add_card(cid, "ARG", 1, 2)  # repetida
    inv.add_card(cid, "ARG", 2, 1)  # tengo
    inv.add_card(cid, "BRA", 1, 1)  # tengo
    # ARG-3 y BRA-2 no se cargaron → faltan
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, inventory_setup):
    v = InventoryView(memory_db, inventory_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def _row_count_visible(view: InventoryView) -> int:
    return view._proxy.rowCount()


def test_inventory_loads_all_cards(qtbot, view):
    """Por default muestra las 5 cards."""
    assert _row_count_visible(view) == 5


def test_filter_by_owned_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_OWNED)
    # Sólo las que tienen quantity == 1: ARG-2 y BRA-1
    assert _row_count_visible(view) == 2


def test_filter_by_missing_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_MISSING)
    # ARG-3 y BRA-2
    assert _row_count_visible(view) == 2


def test_filter_by_duplicates_status(qtbot, view):
    view._state_filter.setCurrentText(STATUS_REPEATED)
    # ARG-1 (qty=2)
    assert _row_count_visible(view) == 1


def test_filter_by_code(qtbot, view):
    view._code_filter.setCurrentText("ARG")
    assert _row_count_visible(view) == 3


def test_search_by_name(qtbot, view):
    view._search_input.setText("Messi")
    assert _row_count_visible(view) == 1


def test_filters_combine_with_and(qtbot, view):
    """Filtros se combinan: estado=Tengo + código=ARG → solo ARG-2."""
    view._state_filter.setCurrentText(STATUS_OWNED)
    view._code_filter.setCurrentText("ARG")
    assert _row_count_visible(view) == 1


def test_status_bar_shows_correct_counts(qtbot, view):
    """Total 5, tengo 3 (ARG-1 repetida + ARG-2 + BRA-1), faltan 2, repetidas 1."""
    text = view._status_label.text()
    assert "Total: 5" in text
    assert "Tengo: 3" in text  # owned + repeated
    assert "Faltan: 2" in text
    assert "Repetidas: 1" in text


def test_refresh_after_card_changed_signal(qtbot, memory_db, view, inventory_setup):
    """refresh() recalcula filas al cambiar el inventario externamente."""
    InventoryService(memory_db).add_card(inventory_setup.collection_id, "ARG", 3, 1)
    view.refresh()
    text = view._status_label.text()
    assert "Tengo: 4" in text
    assert "Faltan: 1" in text


def test_color_coding_by_status(qtbot, view):
    """Las celdas tienen color de fondo según el estado."""
    from collections_app.client.views.inventory_view import (
        COLOR_MISSING,
        COLOR_OWNED,
        COLOR_REPEATED,
    )

    # Buscar una fila por estado y comparar el background
    found_states = set()
    for row in range(view._grid_model.rowCount()):
        state = view._grid_model.item(row, view.COL_STATE).text()
        bg = view._grid_model.item(row, view.COL_STATE).background().color()
        found_states.add(state)
        if state == STATUS_OWNED:
            assert bg == COLOR_OWNED
        elif state == STATUS_REPEATED:
            assert bg == COLOR_REPEATED
        elif state == STATUS_MISSING:
            assert bg == COLOR_MISSING
    # Cubrimos los 3 estados
    assert found_states == {STATUS_OWNED, STATUS_REPEATED, STATUS_MISSING}


def test_initial_filter_is_all(qtbot, view):
    assert view._state_filter.currentText() == FILTER_ALL
    assert view._code_filter.currentText() == FILTER_ALL


def test_clearing_search_restores_all(qtbot, view):
    view._search_input.setText("Messi")
    assert _row_count_visible(view) == 1
    view._search_input.setText("")
    assert _row_count_visible(view) == 5
```

### [tests/client/views/test_reports_view.py](tests/client/views/test_reports_view.py)

```python
"""Tests del ReportsView."""

import csv
from datetime import UTC, datetime

import pytest
from PySide6.QtCore import QDate

from collections_app.client.views.reports_view import (
    PRESET_CUSTOM,
    PRESET_LAST_7,
    PRESET_TODAY,
    ReportsView,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def reports_setup(memory_db, sample_cards, sample_collection):
    inv = InventoryService(memory_db)
    inv.add_card(sample_collection.collection_id, "ARG", 1, 1)
    inv.add_card(sample_collection.collection_id, "ARG", 2, 1)
    inv.add_card(sample_collection.collection_id, "BRA", 1, 2)
    inv.remove_card(sample_collection.collection_id, "BRA", 1, 1)
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, reports_setup):
    v = ReportsView(memory_db, reports_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def test_default_period_is_last_7_days(qtbot, view):
    assert view._period_combo.currentText() == PRESET_LAST_7


def test_period_preset_changes_dates(qtbot, view):
    """Cambiar a 'Hoy' cambia el rango computado."""
    view._period_combo.setCurrentText(PRESET_TODAY)
    start, end = view._compute_range()
    # Ambos en UTC con tzinfo
    assert start.tzinfo == UTC
    assert end.tzinfo == UTC
    # El rango cubre menos de 25 horas
    assert (end - start).total_seconds() < 25 * 3600


def test_custom_period_enables_date_editors(qtbot, view):
    assert view._date_from.isVisible() is False
    view._period_combo.setCurrentText(PRESET_CUSTOM)
    assert view._date_from.isVisible() is True
    assert view._date_to.isVisible() is True


def test_filter_by_operation(qtbot, view):
    """Filtrando solo Altas, las 3 altas aparecen y las bajas no."""
    view._op_combo.setCurrentIndex(1)  # Alta
    view.refresh()
    assert view._grid_model.rowCount() == 3
    for row in range(3):
        assert "Alta" in view._grid_model.item(row, 1).text()


def test_filter_baja_only(qtbot, view):
    view._op_combo.setCurrentIndex(2)  # Baja
    view.refresh()
    assert view._grid_model.rowCount() == 1


def test_default_loads_recent_transactions(qtbot, view):
    """Con el preset default, la grilla muestra las 4 transactions hechas hoy."""
    assert view._grid_model.rowCount() == 4


def test_summary_shows_altas_y_bajas_counts(qtbot, view):
    text = view._summary_label.text()
    assert "3 altas" in text
    assert "1 bajas" in text


def test_export_csv_creates_valid_file(qtbot, view, tmp_path, monkeypatch):
    """El export crea un archivo con header de metadata + columnas + filas."""
    csv_path = tmp_path / "out.csv"

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **kw: (str(csv_path), "csv"))
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **kw: QMessageBox.StandardButton.Ok)

    view._export_csv()

    assert csv_path.exists()
    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    # Fila 0: metadata, fila 1: header columnas, resto: datos.
    assert rows[0][0].startswith("#")
    assert rows[1] == ["fecha", "operacion", "codigo", "numero", "nombre", "cantidad"]
    assert len(rows) == 2 + 4  # 4 transactions


def test_csv_dates_in_local_time(qtbot, view, tmp_path, monkeypatch):
    """Las fechas en el CSV están en hora local con offset (ISO format)."""
    csv_path = tmp_path / "out.csv"
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **kw: (str(csv_path), "csv"))
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **kw: QMessageBox.StandardButton.Ok)

    view._export_csv()

    with csv_path.open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    first_data_row = rows[2]  # fecha, op, ...
    fecha = first_data_row[0]
    # ISO format con offset: "YYYY-MM-DDTHH:MM:SS±HH:MM" o sin offset
    # La fecha re-parseada debe coincidir aproximadamente con "ahora"
    parsed = datetime.fromisoformat(fecha)
    assert parsed.tzinfo is not None
    delta = abs((parsed.astimezone(UTC) - datetime.now(UTC)).total_seconds())
    assert delta < 60  # menos de 1 minuto de diferencia


def test_custom_date_range_filters_correctly(qtbot, memory_db, view):
    """Con un rango futuro, no aparece nada."""
    view._period_combo.setCurrentText(PRESET_CUSTOM)
    future = QDate.currentDate().addDays(30)
    view._date_from.setDate(future)
    view._date_to.setDate(future.addDays(1))
    view.refresh()
    assert view._grid_model.rowCount() == 0
```

### [tests/client/views/test_stats_view.py](tests/client/views/test_stats_view.py)

```python
"""Tests del StatsView."""

import pytest

from collections_app.client.views.stats_view import StatsView
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
)
from collections_app.core.services import InventoryService


@pytest.fixture
def stats_setup(memory_db, sample_collection):
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    lines.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines.upsert(CodeLine(hid, "BRA", "Brasil"))

    cards = CardsRepository(memory_db)
    # Catálogo: 4 ARG, 4 BRA
    for n in (1, 2, 3, 4):
        cards.upsert(Card(cid, "ARG", n, f"Player ARG-{n}"))
        cards.upsert(Card(cid, "BRA", n, f"Player BRA-{n}"))

    inv = InventoryService(memory_db)
    inv.add_card(cid, "ARG", 1, 3)  # repetida x3
    inv.add_card(cid, "ARG", 2, 1)  # tengo
    inv.add_card(cid, "BRA", 1, 2)  # repetida x2
    return sample_collection


@pytest.fixture
def view(qtbot, memory_db, stats_setup):
    v = StatsView(memory_db, stats_setup)
    qtbot.addWidget(v)
    v.show()
    return v


def test_overall_progress_calculated_correctly(qtbot, view):
    """3 owned / 8 total = 37.5%."""
    text = view._overall_label.text()
    assert "3/8" in text
    assert "37.5" in text


def test_overall_bar_value_matches(qtbot, view):
    assert view._overall_bar.maximum() == 8
    assert view._overall_bar.value() == 3


def test_progress_by_code_shown(qtbot, view):
    """Debe haber un row por cada code (ARG y BRA)."""
    # Cada row es un widget hijo del container
    assert view._per_code_layout.count() == 2


def test_top_duplicates_displayed(qtbot, view):
    """Las dos cards repetidas (ARG-1 x3, BRA-1 x2) aparecen."""
    # 2 widgets en el layout (no el placeholder de "sin repetidas")
    count = view._top_dup_layout.count()
    assert count == 2


def test_top_duplicates_placeholder_when_none(qtbot, memory_db, sample_collection):
    """Sin duplicados, muestra placeholder."""
    v = StatsView(memory_db, sample_collection)
    qtbot.addWidget(v)
    v.show()
    # 1 widget (label "sin repetidas todavía")
    assert v._top_dup_layout.count() == 1


def test_summary_shows_correct_numbers(qtbot, view):
    text = view._summary_label.text()
    # Total físico = 3 + 1 + 2 = 6
    assert "6" in text
    # Cards únicas = 3
    assert "3" in text
    # Copias extra = (3-1) + (2-1) = 3
    assert "3" in text


def test_refresh_updates_numbers(qtbot, memory_db, view, stats_setup):
    """Cambiar el inventario externamente y refrescar refleja los nuevos valores."""
    InventoryService(memory_db).add_card(stats_setup.collection_id, "BRA", 2, 1)
    view.refresh()
    # Ahora 4 owned / 8 total = 50%
    assert "4/8" in view._overall_label.text()
    assert "50.0" in view._overall_label.text()
```

### [tests/conftest.py](tests/conftest.py)

```python
"""Fixtures compartidas de pytest."""

import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import Card, CodeHeader, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
)


@pytest.fixture
def memory_db() -> Iterator[sqlite3.Connection]:
    """DB SQLite en memoria con todas las migraciones aplicadas."""
    conn = create_connection(":memory:")
    run_migrations(conn)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def file_db_path(tmp_path: Path) -> Path:
    """Path a una DB SQLite en archivo, ya migrada al schema actual.

    Útil para tests que necesitan abrir una conexión 'fresca' al mismo
    archivo y verificar que un commit es visible desde otra conexión.
    """
    db_path = tmp_path / "test.db"
    conn = create_connection(db_path)
    run_migrations(conn)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def sample_code_header(memory_db: sqlite3.Connection) -> CodeHeader:
    """Crea y persiste un CodeHeader 'FIFA Codes' con max_length 5."""
    repo = CodesHeadersRepository(memory_db)
    header = repo.create(
        CodeHeader(code_header_id=None, code_header_name="FIFA Codes", code_max_length=5)
    )
    memory_db.commit()
    return header


@pytest.fixture
def sample_collection(
    memory_db: sqlite3.Connection,
    sample_code_header: CodeHeader,
) -> Collection:
    """Crea y persiste una Collection 'FIFA WC 2026' con sample_code_header."""
    assert sample_code_header.code_header_id is not None
    repo = CollectionsRepository(memory_db)
    collection = repo.create(
        Collection(
            collection_id=None,
            collection_name="FIFA WC 2026",
            card_count=5,
            requires_code=True,
            code_field_name="País",
            code_header_id=sample_code_header.code_header_id,
        )
    )
    memory_db.commit()
    return collection


@pytest.fixture
def sample_cards(
    memory_db: sqlite3.Connection,
    sample_collection: Collection,
) -> list[Card]:
    """Crea y persiste 5 cards de prueba en sample_collection."""
    assert sample_collection.collection_id is not None
    cid = sample_collection.collection_id
    cards = [
        Card(collection_id=cid, code_id="ARG", card_number=1, card_name="Lionel Messi"),
        Card(collection_id=cid, code_id="ARG", card_number=2, card_name="Emiliano Martínez"),
        Card(collection_id=cid, code_id="BRA", card_number=1, card_name="Vinícius Jr."),
        Card(collection_id=cid, code_id="BRA", card_number=2, card_name="Neymar"),
        Card(collection_id=cid, code_id="FRA", card_number=1, card_name="Kylian Mbappé"),
    ]
    repo = CardsRepository(memory_db)
    repo.bulk_upsert(cards)
    memory_db.commit()
    return cards
```

### [tests/core/__init__.py](tests/core/__init__.py)

_(archivo vacío)_

### [tests/core/db/__init__.py](tests/core/db/__init__.py)

_(archivo vacío)_

### [tests/core/db/scripts/__init__.py](tests/core/db/scripts/__init__.py)

_(archivo vacío)_

### [tests/core/db/scripts/test_cleanup_orphans.py](tests/core/db/scripts/test_cleanup_orphans.py)

```python
"""Tests del script cleanup_orphans."""

import sqlite3

from collections_app.core.db.connection import create_connection
from collections_app.core.db.scripts.cleanup_orphans import cleanup_orphans
from collections_app.core.models import Card, CodeHeader, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
)


def _insert_without_fk(db_path, sql: str, params: tuple = ()) -> None:
    """Inserta una fila bypaseando FK (conexión cruda sin el PRAGMA)."""
    raw = sqlite3.connect(str(db_path))
    try:
        raw.execute(sql, params)
        raw.commit()
    finally:
        raw.close()


def _make_collection(conn, name: str = "C1") -> Collection:
    header = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name=f"H_{name}", code_max_length=5)
    )
    return CollectionsRepository(conn).create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=3,
            requires_code=True,
            code_field_name="País",
            code_header_id=header.code_header_id,
        )
    )


def test_cleanup_removes_orphan_cards(file_db_path):
    """Cards apuntando a collection_id que no existe → eliminadas."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        cards = CardsRepository(conn)
        cards.upsert(Card(col.collection_id, "ARG", 1, "X"))
        cards.upsert(Card(col.collection_id, "ARG", 2, "Y"))
        conn.commit()
    finally:
        conn.close()

    # Insertar card huérfana sin FK enforcement (simula bug del usuario)
    _insert_without_fk(
        file_db_path,
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
        "VALUES (9999, 'ZZZ', 1, 'Orphan')",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["cards"] == 1

    # Verificar que las cards reales siguen
    conn = create_connection(file_db_path)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM cards").fetchone()["n"]
        assert n == 2
    finally:
        conn.close()


def test_cleanup_removes_orphan_transactions(file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        # transacciones con collection_id válido
        conn.execute(
            "INSERT INTO transactions (collection_id, code_id, card_number, operation, quantity) "
            "VALUES (?, 'ARG', 1, 'alta', 1)",
            (col.collection_id,),
        )
        conn.commit()
    finally:
        conn.close()

    # Transacción huérfana (collection_id no existe)
    _insert_without_fk(
        file_db_path,
        "INSERT INTO transactions (collection_id, code_id, card_number, operation, quantity) "
        "VALUES (9999, 'XX', 1, 'alta', 1)",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["transactions"] == 1


def test_cleanup_returns_zero_when_no_orphans(file_db_path):
    """Sin huérfanos, todas las cuentas son 0."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        CardsRepository(conn).upsert(Card(col.collection_id, "ARG", 1, "X"))
        conn.commit()
    finally:
        conn.close()

    deleted = cleanup_orphans(str(file_db_path))
    assert all(n == 0 for n in deleted.values())


def test_cleanup_includes_card_images_table(file_db_path):
    """La tabla card_images también se limpia."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        CardsRepository(conn).upsert(Card(col.collection_id, "ARG", 1, "X"))
        conn.commit()
    finally:
        conn.close()

    # Entry huérfana en card_images
    _insert_without_fk(
        file_db_path,
        "INSERT INTO card_images (collection_id, code_id, card_number, found_photo) "
        "VALUES (9999, 'XX', 1, 1)",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["card_images"] == 1
```

### [tests/core/db/test_migrator.py](tests/core/db/test_migrator.py)

```python
"""Tests del migrator."""

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations


def test_migrator_applies_all_migrations():
    """Verifica que el migrator aplica todas las migraciones disponibles."""
    conn = create_connection(":memory:")
    final_version = run_migrations(conn)
    assert final_version >= 4  # 001 + 002 + 003 + 004


def test_migrator_creates_all_expected_tables(memory_db: sqlite3.Connection):
    """Verifica que se crearon todas las tablas esperadas."""
    rows = memory_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = {row["name"] for row in rows}

    expected = {
        "schema_version",
        "app_settings",
        "codes_headers",
        "codes_lines",
        "collections",
        "cards",
        "inventory",
        "transactions",
        "card_images",
    }
    # SQLite agrega sqlite_sequence automáticamente con AUTOINCREMENT
    assert expected.issubset(table_names)


def test_migration_003_creates_card_images_table(memory_db: sqlite3.Connection):
    """La migración 003 crea card_images con FK CASCADE desde cards."""
    cols = memory_db.execute("PRAGMA table_info(card_images)").fetchall()
    col_names = {row["name"] for row in cols}
    expected_cols = {
        "collection_id",
        "code_id",
        "card_number",
        "found_photo",
        "image_source",
        "image_path",
        "generated_at",
    }
    assert expected_cols.issubset(col_names)

    # FK con ON DELETE CASCADE hacia cards
    fks = memory_db.execute("PRAGMA foreign_key_list(card_images)").fetchall()
    assert any(fk["table"] == "cards" and fk["on_delete"] == "CASCADE" for fk in fks)

    # Index para queries por found_photo
    indexes = memory_db.execute("PRAGMA index_list(card_images)").fetchall()
    assert any(idx["name"] == "idx_card_images_found" for idx in indexes)


def test_migrator_is_idempotent(memory_db: sqlite3.Connection):
    """Correr migraciones dos veces no debe fallar ni duplicar nada."""
    initial_version = run_migrations(memory_db)
    second_version = run_migrations(memory_db)
    assert initial_version == second_version


def test_foreign_keys_are_enabled(memory_db: sqlite3.Connection):
    """Verifica que el PRAGMA foreign_keys está activo."""
    result = memory_db.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1


def test_cannot_create_collection_with_invalid_code_header(memory_db: sqlite3.Connection):
    """FK debe impedir crear colección con code_header_id inexistente."""
    with pytest.raises(sqlite3.IntegrityError):
        memory_db.execute(
            "INSERT INTO collections (collection_name, card_count, code_header_id) "
            "VALUES ('Test', 100, 999)"
        )
        memory_db.commit()


def test_migration_002_adds_code_order_column(memory_db: sqlite3.Connection):
    """Migración 002 debe agregar la columna code_order a codes_lines."""
    cols = {row["name"] for row in memory_db.execute("PRAGMA table_info(codes_lines)").fetchall()}
    assert "code_order" in cols


def test_migration_002_assigns_alphabetical_order_to_existing():
    """Aplicada en una DB con datos preexistentes, asigna orden alfabético."""
    conn = create_connection(":memory:")
    # Aplicar solo migración 001 simulando estado pre-002
    # Schema mínimo de la versión 1: incluye `collections` (mínimas) porque
    # migraciones posteriores (003, 004) la alteran. Si se omite, ALTER TABLE
    # falla en cuanto se aplique cualquier migración futura sobre `collections`.
    schema_001 = (
        "CREATE TABLE schema_version (version INTEGER PRIMARY KEY, "
        "applied_at TEXT NOT NULL DEFAULT (datetime('now')));"
        "CREATE TABLE codes_headers ("
        "  code_header_id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  code_header_name TEXT NOT NULL UNIQUE,"
        "  code_max_length INTEGER NOT NULL DEFAULT 5);"
        "CREATE TABLE codes_lines ("
        "  code_header_id INTEGER NOT NULL,"
        "  code_id TEXT NOT NULL,"
        "  code_name TEXT NOT NULL,"
        "  PRIMARY KEY (code_header_id, code_id),"
        "  FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id));"
        "CREATE TABLE collections ("
        "  collection_id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  collection_name TEXT NOT NULL UNIQUE,"
        "  card_count INTEGER NOT NULL,"
        "  requires_code INTEGER NOT NULL DEFAULT 0,"
        "  code_field_name TEXT,"
        "  code_header_id INTEGER NOT NULL,"
        "  is_premium INTEGER NOT NULL DEFAULT 0,"
        "  license_key_required TEXT,"
        "  FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id));"
        "CREATE TABLE cards ("
        "  collection_id INTEGER NOT NULL,"
        "  code_id TEXT NOT NULL,"
        "  card_number INTEGER NOT NULL,"
        "  card_name TEXT NOT NULL,"
        "  PRIMARY KEY (collection_id, code_id, card_number),"
        "  FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE);"
        # Migración 005 hace ALTER TABLE inventory; necesitamos la tabla
        # presente en el schema base aunque este test solo testee 002.
        "CREATE TABLE inventory ("
        "  collection_id INTEGER NOT NULL,"
        "  code_id TEXT NOT NULL,"
        "  card_number INTEGER NOT NULL,"
        "  quantity INTEGER NOT NULL DEFAULT 0,"
        "  image_path TEXT,"
        "  PRIMARY KEY (collection_id, code_id, card_number));"
        "INSERT INTO schema_version (version) VALUES (1);"
        "INSERT INTO codes_headers (code_header_name) VALUES ('FIFA');"
        "INSERT INTO codes_lines (code_header_id, code_id, code_name) VALUES "
        "  (1, 'BRA', 'Brasil'), (1, 'ARG', 'Argentina'), (1, 'CHI', 'Chile');"
    )
    conn.executescript(schema_001)
    conn.commit()
    # Aplicar todas las migraciones (debería aplicar 002)
    run_migrations(conn)

    rows = conn.execute("SELECT code_id, code_order FROM codes_lines ORDER BY code_id").fetchall()
    orders = {r["code_id"]: r["code_order"] for r in rows}
    assert orders == {"ARG": 1, "BRA": 2, "CHI": 3}


# ----------------------------------------------------------------------
# Migración 004 — layout álbum por colección
# ----------------------------------------------------------------------


def test_migration_004_adds_album_layout_columns(memory_db: sqlite3.Connection):
    """La migración 004 agrega album_columns/rows/orientation a collections."""
    cols = {row["name"] for row in memory_db.execute("PRAGMA table_info(collections)").fetchall()}
    assert "album_columns" in cols
    assert "album_rows" in cols
    assert "album_orientation" in cols


def test_migration_004_defaults_for_existing_rows(memory_db: sqlite3.Connection):
    """Colecciones creadas antes de la 004 reciben defaults razonables (3, 4, portrait)."""
    # Insertar header + colección omitiendo los nuevos campos (deben default)
    memory_db.execute("INSERT INTO codes_headers (code_header_name) VALUES ('TestHdr')")
    memory_db.execute(
        "INSERT INTO collections "
        "(collection_name, card_count, requires_code, code_field_name, code_header_id) "
        "VALUES ('TestCol', 100, 0, NULL, 1)"
    )
    memory_db.commit()

    row = memory_db.execute(
        "SELECT album_columns, album_rows, album_orientation "
        "FROM collections WHERE collection_name = 'TestCol'"
    ).fetchone()
    assert row["album_columns"] == 3
    assert row["album_rows"] == 4
    assert row["album_orientation"] == "portrait"


def test_migration_004_orientation_check_constraint(memory_db: sqlite3.Connection):
    """`album_orientation` solo acepta 'portrait' | 'landscape' (CHECK)."""
    memory_db.execute("INSERT INTO codes_headers (code_header_name) VALUES ('Hdr')")
    with pytest.raises(sqlite3.IntegrityError):
        memory_db.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, requires_code, code_field_name, "
            " code_header_id, album_orientation) "
            "VALUES ('C', 1, 0, NULL, 1, 'invalid')"
        )
```

### [tests/core/repositories/__init__.py](tests/core/repositories/__init__.py)

_(archivo vacío)_

### [tests/core/repositories/test_card_images_repo.py](tests/core/repositories/test_card_images_repo.py)

```python
"""Tests del CardImagesRepository (migración 003)."""

from collections_app.core.models import CardImage
from collections_app.core.repositories import CardImagesRepository


def _img(
    cid: int,
    code: str = "ARG",
    num: int = 1,
    found: bool = True,
    source: str | None = "wikipedia",
    path: str | None = "/tmp/x.png",
    when: str | None = "2026-01-01 12:00:00",
) -> CardImage:
    return CardImage(
        collection_id=cid,
        code_id=code,
        card_number=num,
        found_photo=found,
        image_source=source,
        image_path=path,
        generated_at=when,
    )


def test_upsert_creates_record(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    img = _img(cid, "ARG", 1, found=True, source="wikipedia")
    repo.upsert(img)
    fetched = repo.get(cid, "ARG", 1)
    assert fetched == img


def test_upsert_updates_existing(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=False, source="placeholder"))
    repo.upsert(_img(cid, "ARG", 1, found=True, source="google", path="/tmp/new.png"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.found_photo is True
    assert fetched.image_source == "google"
    assert fetched.image_path == "/tmp/new.png"


def test_get_missing_returns_none(memory_db, sample_collection):
    repo = CardImagesRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ZZZ", 999) is None


def test_list_by_collection(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.upsert(_img(cid, "BRA", 1, source="duckduckgo"))
    rows = repo.list_by_collection(cid)
    assert len(rows) == 2
    assert {r.code_id for r in rows} == {"ARG", "BRA"}


def test_get_pending_returns_cards_without_image(memory_db, sample_cards, sample_collection):
    """Cards en `cards` que NO están en `card_images`."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.upsert(_img(cid, "BRA", 1))
    pending = repo.get_pending(cid)
    pending_keys = {(p.code_id, p.card_number) for p in pending}
    # sample_cards tiene 5 cards: ARG-1, ARG-2, BRA-1, BRA-2, FRA-1.
    # Procesamos ARG-1 y BRA-1 → quedan 3 pendientes.
    assert pending_keys == {("ARG", 2), ("BRA", 2), ("FRA", 1)}


def test_get_placeholders_returns_found_photo_false(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True, source="wikipedia"))
    repo.upsert(_img(cid, "ARG", 2, found=False, source="placeholder"))
    repo.upsert(_img(cid, "BRA", 1, found=False, source="placeholder"))
    placeholders = repo.get_placeholders(cid)
    keys = {(p.code_id, p.card_number) for p in placeholders}
    assert keys == {("ARG", 2), ("BRA", 1)}


def test_get_found_count(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True))
    repo.upsert(_img(cid, "ARG", 2, found=True))
    repo.upsert(_img(cid, "BRA", 1, found=False))
    assert repo.get_found_count(cid) == 2


def test_get_total_generated(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True))
    repo.upsert(_img(cid, "ARG", 2, found=False))
    assert repo.get_total_generated(cid) == 2


def test_delete_removes_record(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.delete(cid, "ARG", 1)
    assert repo.get(cid, "ARG", 1) is None


def test_cascade_delete_when_card_deleted(memory_db, sample_cards, sample_collection):
    """FK ON DELETE CASCADE: si se borra la card, su entry de card_images desaparece."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    memory_db.execute(
        "DELETE FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
        (cid, "ARG", 1),
    )
    memory_db.commit()
    assert repo.get(cid, "ARG", 1) is None


def test_pending_excludes_cards_with_existing_image(memory_db, sample_cards, sample_collection):
    """Si TODAS las cards tienen image, get_pending devuelve lista vacía."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    for code, num in [("ARG", 1), ("ARG", 2), ("BRA", 1), ("BRA", 2), ("FRA", 1)]:
        repo.upsert(_img(cid, code, num))
    assert repo.get_pending(cid) == []


def test_collection_isolation(memory_db, sample_cards, sample_collection):
    """Los queries filtran por collection_id."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    # Otra collection_id no debería encontrar nada
    other_cid = cid + 999
    assert repo.list_by_collection(other_cid) == []
    assert repo.get_found_count(other_cid) == 0
    assert repo.get_total_generated(other_cid) == 0
```

### [tests/core/repositories/test_cards_repo.py](tests/core/repositories/test_cards_repo.py)

```python
"""Tests del CardsRepository."""

import sqlite3

import pytest

from collections_app.core.models import Card
from collections_app.core.repositories import CardsRepository


def test_upsert_insert(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    card = Card(sample_collection.collection_id, "ARG", 1, "Messi")
    repo.upsert(card)
    fetched = repo.get(sample_collection.collection_id, "ARG", 1)
    assert fetched == card


def test_upsert_update_existing(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 1, "Messi"))
    repo.upsert(Card(cid, "ARG", 1, "Lionel Messi"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.card_name == "Lionel Messi"


def test_get_missing_returns_none(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ARG", 99) is None


def test_list_by_collection_with_data(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    cards = repo.list_by_collection(sample_collection.collection_id)
    assert len(cards) == 5


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_by_code(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    arg_cards = repo.list_by_code(sample_collection.collection_id, "ARG")
    assert len(arg_cards) == 2
    assert all(c.code_id == "ARG" for c in arg_cards)


def test_count_by_collection(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.count_by_collection(sample_collection.collection_id) == 5


def test_count_by_collection_empty(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.count_by_collection(sample_collection.collection_id) == 0


def test_delete_existing(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id, "ARG", 1) is True
    assert repo.get(sample_collection.collection_id, "ARG", 1) is None


def test_delete_nonexistent(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id, "XXX", 99) is False


def test_bulk_upsert_inserts(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    cards = [Card(cid, "X", n, f"Card-{n}") for n in range(1, 21)]
    inserted = repo.bulk_upsert(cards)
    assert inserted == 20
    assert repo.count_by_collection(cid) == 20


def test_bulk_upsert_empty_list(memory_db):
    repo = CardsRepository(memory_db)
    assert repo.bulk_upsert([]) == 0


def test_bulk_upsert_updates_existing(memory_db, sample_collection):
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 1, "Old"))
    repo.bulk_upsert([Card(cid, "ARG", 1, "New")])
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.card_name == "New"


def test_card_key_property():
    card = Card(1, "ARG", 24, "Lionel Messi")
    assert card.card_key == "ARG-24"


def test_invalid_collection_fk(memory_db):
    repo = CardsRepository(memory_db)
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(Card(999, "X", 1, "ghost"))


def test_cascade_delete_from_collection(memory_db, sample_cards, sample_collection):
    """Borrar la colección elimina sus cards en cascade."""
    from collections_app.core.repositories import CollectionsRepository

    cards_repo = CardsRepository(memory_db)
    CollectionsRepository(memory_db).delete(sample_collection.collection_id)
    assert cards_repo.list_by_collection(sample_collection.collection_id) == []


def test_find_by_number_returns_match(memory_db, sample_cards, sample_collection):
    """Si hay un solo card con ese número, lo retorna."""
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    # sample_cards tiene FRA-1 (número 1 en code "FRA"). ARG-1, BRA-1 también.
    matches = repo.find_by_number(cid, 1)
    assert len(matches) == 3  # ARG-1, BRA-1, FRA-1
    codes = {c.code_id for c in matches}
    assert codes == {"ARG", "BRA", "FRA"}


def test_find_by_number_returns_empty_when_not_exists(memory_db, sample_cards, sample_collection):
    repo = CardsRepository(memory_db)
    assert repo.find_by_number(sample_collection.collection_id, 9999) == []


def test_find_by_number_returns_multiple_when_ambiguous(memory_db, sample_collection):
    """Cuando varias cards comparten número en distintos códigos, retorna todas."""
    repo = CardsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(Card(cid, "ARG", 24, "Messi"))
    repo.upsert(Card(cid, "BRA", 24, "Vinicius"))
    matches = repo.find_by_number(cid, 24)
    assert len(matches) == 2
    assert {m.code_id for m in matches} == {"ARG", "BRA"}


def test_get_stats_by_code(memory_db, sample_cards, sample_collection):
    """Para cada code: total de cards y cuántas tiene el usuario."""
    from collections_app.core.models import CodeLine, InventoryItem
    from collections_app.core.repositories import (
        CodesLinesRepository,
        InventoryRepository,
    )

    repo = CardsRepository(memory_db)
    inv = InventoryRepository(memory_db)
    lines = CodesLinesRepository(memory_db)
    cid = sample_collection.collection_id
    hid = sample_collection.code_header_id

    lines.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines.upsert(CodeLine(hid, "BRA", "Brasil"))
    lines.upsert(CodeLine(hid, "FRA", "Francia"))
    # sample_cards: ARG-1, ARG-2, BRA-1, BRA-2, FRA-1.
    # El usuario tiene ARG-1 y FRA-1.
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=1))
    inv.upsert(InventoryItem(cid, "FRA", 1, quantity=2))
    memory_db.commit()

    stats = repo.get_stats_by_code(cid)
    by_code = {s["code_id"]: s for s in stats}
    assert by_code["ARG"]["total"] == 2
    assert by_code["ARG"]["owned"] == 1
    assert by_code["ARG"]["percentage"] == 50.0
    assert by_code["BRA"]["owned"] == 0
    assert by_code["FRA"]["percentage"] == 100.0
    assert by_code["FRA"]["code_name"] == "Francia"
```

### [tests/core/repositories/test_codes_headers_repo.py](tests/core/repositories/test_codes_headers_repo.py)

```python
"""Tests del CodesHeadersRepository."""

import sqlite3

import pytest

from collections_app.core.models import CodeHeader
from collections_app.core.repositories import CodesHeadersRepository


def test_create_returns_header_with_id(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    assert created.code_header_id is not None
    assert created.code_header_name == "FIFA"
    assert created.code_max_length == 4


def test_get_by_id_returns_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    found = repo.get_by_id(created.code_header_id)
    assert found == created


def test_get_by_id_returns_none_when_missing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.get_by_id(999) is None


def test_get_by_name_returns_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "FIFA", 4))
    found = repo.get_by_name("FIFA")
    assert found is not None
    assert found.code_header_name == "FIFA"


def test_get_by_name_returns_none_when_missing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.get_by_name("NOPE") is None


def test_list_all_empty(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.list_all() == []


def test_list_all_with_data_sorted_by_name(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "Zeta", 5))
    repo.create(CodeHeader(None, "Alpha", 3))
    repo.create(CodeHeader(None, "Mid", 4))
    names = [h.code_header_name for h in repo.list_all()]
    assert names == ["Alpha", "Mid", "Zeta"]


def test_update_existing(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    updated = repo.update(CodeHeader(created.code_header_id, "FIFA Codes", 6))
    assert updated.code_header_name == "FIFA Codes"
    fresh = repo.get_by_id(created.code_header_id)
    assert fresh is not None
    assert fresh.code_max_length == 6


def test_update_without_id_raises(memory_db):
    repo = CodesHeadersRepository(memory_db)
    with pytest.raises(ValueError, match="code_header_id"):
        repo.update(CodeHeader(None, "FIFA", 5))


def test_delete_existing_returns_true(memory_db):
    repo = CodesHeadersRepository(memory_db)
    created = repo.create(CodeHeader(None, "FIFA", 4))
    assert repo.delete(created.code_header_id) is True
    assert repo.get_by_id(created.code_header_id) is None


def test_delete_nonexistent_returns_false(memory_db):
    repo = CodesHeadersRepository(memory_db)
    assert repo.delete(999) is False


def test_unique_name_constraint(memory_db):
    repo = CodesHeadersRepository(memory_db)
    repo.create(CodeHeader(None, "FIFA", 4))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(CodeHeader(None, "FIFA", 5))
```

### [tests/core/repositories/test_codes_lines_repo.py](tests/core/repositories/test_codes_lines_repo.py)

```python
"""Tests del CodesLinesRepository."""

import pytest

from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository


def test_upsert_insert(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    line = CodeLine(sample_code_header.code_header_id, "ARG", "Argentina")
    saved = repo.upsert(line)
    assert saved == line
    fetched = repo.get(sample_code_header.code_header_id, "ARG")
    assert fetched == line


def test_upsert_update_existing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "ARG", "ARG (Argentina)"))
    fetched = repo.get(hid, "ARG")
    assert fetched is not None
    assert fetched.code_name == "ARG (Argentina)"


def test_upsert_validates_max_length(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    too_long = "X" * 10  # max_length es 5
    with pytest.raises(ValueError, match="excede max_length"):
        repo.upsert(CodeLine(hid, too_long, "Demasiado largo"))


def test_upsert_rejects_unknown_header(memory_db):
    repo = CodesLinesRepository(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        repo.upsert(CodeLine(999, "ARG", "Argentina"))


def test_get_returns_none_when_missing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.get(sample_code_header.code_header_id, "NOPE") is None


def test_list_by_header_empty(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.list_by_header(sample_code_header.code_header_id) == []


def test_list_by_header_sorted(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "FRA", "Francia"))
    codes = [line.code_id for line in repo.list_by_header(hid)]
    assert codes == ["ARG", "BRA", "FRA"]


def test_list_codes_only(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    assert repo.list_codes_only(hid) == ["ARG", "BRA"]


def test_delete_existing(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    assert repo.delete(hid, "ARG") is True
    assert repo.get(hid, "ARG") is None


def test_delete_nonexistent_returns_false(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    assert repo.delete(sample_code_header.code_header_id, "NOPE") is False


def test_cascade_delete_from_header(memory_db, sample_code_header):
    """Si borro el header, las lines se borran por cascade."""
    from collections_app.core.repositories import CodesHeadersRepository

    lines_repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brasil"))

    CodesHeadersRepository(memory_db).delete(hid)
    assert lines_repo.list_by_header(hid) == []


def test_default_order_is_zero(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    line = repo.get(hid, "ARG")
    assert line is not None
    assert line.code_order == 0


def test_codes_lines_ordered_by_code_order(memory_db, sample_code_header):
    """list_by_header ordena primero por code_order, después por code_id."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina", code_order=3))
    repo.upsert(CodeLine(hid, "BRA", "Brasil", code_order=1))
    repo.upsert(CodeLine(hid, "CHI", "Chile", code_order=2))
    codes = [line.code_id for line in repo.list_by_header(hid)]
    assert codes == ["BRA", "CHI", "ARG"]


def test_upsert_preserves_code_order(memory_db, sample_code_header):
    """Upsert con un code_order explícito lo persiste."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina", code_order=5))
    line = repo.get(hid, "ARG")
    assert line is not None
    assert line.code_order == 5


def test_upsert_updates_code_order(memory_db, sample_code_header):
    """Upsert sobre un line existente actualiza también su code_order."""
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina", code_order=3))
    repo.upsert(CodeLine(hid, "ARG", "Argentina (updated)", code_order=7))
    line = repo.get(hid, "ARG")
    assert line is not None
    assert line.code_order == 7


def test_reorder_changes_order(memory_db, sample_code_header):
    repo = CodesLinesRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    repo.upsert(CodeLine(hid, "BRA", "Brasil"))
    repo.upsert(CodeLine(hid, "CHI", "Chile"))

    repo.reorder(hid, ["CHI", "ARG", "BRA"])

    codes = [line.code_id for line in repo.list_by_header(hid)]
    assert codes == ["CHI", "ARG", "BRA"]
```

### [tests/core/repositories/test_collections_repo.py](tests/core/repositories/test_collections_repo.py)

```python
"""Tests del CollectionsRepository."""

import sqlite3

import pytest

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository


def _build(header_id: int, name: str = "Test", **kwargs) -> Collection:
    base = {
        "collection_id": None,
        "collection_name": name,
        "card_count": 100,
        "requires_code": True,
        "code_field_name": "Set",
        "code_header_id": header_id,
        "is_premium": False,
        "license_key_required": None,
    }
    base.update(kwargs)
    return Collection(**base)


def test_create_returns_with_id(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    created = repo.create(_build(sample_code_header.code_header_id))
    assert created.collection_id is not None


def test_create_persists_premium_and_license(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    created = repo.create(
        _build(
            sample_code_header.code_header_id,
            name="Premium",
            is_premium=True,
            license_key_required="hash-abc",
        )
    )
    found = repo.get_by_id(created.collection_id)
    assert found is not None
    assert found.is_premium is True
    assert found.license_key_required == "hash-abc"


def test_get_by_id_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    found = repo.get_by_id(sample_collection.collection_id)
    assert found == sample_collection


def test_get_by_id_missing(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.get_by_id(999) is None


def test_get_by_name_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    found = repo.get_by_name("FIFA WC 2026")
    assert found is not None
    assert found.collection_id == sample_collection.collection_id


def test_get_by_name_missing(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.get_by_name("NOPE") is None


def test_list_all_empty(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.list_all() == []


def test_list_all_sorted_by_name(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.create(_build(hid, name="Zeta"))
    repo.create(_build(hid, name="Alpha"))
    names = [c.collection_name for c in repo.list_all()]
    assert names == ["Alpha", "Zeta"]


def test_update_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    updated = Collection(
        collection_id=sample_collection.collection_id,
        collection_name="FIFA WC 2026 (revised)",
        card_count=400,
        requires_code=False,
        code_field_name=None,
        code_header_id=sample_collection.code_header_id,
        is_premium=True,
        license_key_required="hash-xyz",
    )
    repo.update(updated)
    fresh = repo.get_by_id(sample_collection.collection_id)
    assert fresh == updated


def test_update_without_id_raises(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    with pytest.raises(ValueError, match="collection_id"):
        repo.update(_build(sample_code_header.code_header_id))


def test_delete_existing(memory_db, sample_collection):
    repo = CollectionsRepository(memory_db)
    assert repo.delete(sample_collection.collection_id) is True
    assert repo.get_by_id(sample_collection.collection_id) is None


def test_delete_nonexistent(memory_db):
    repo = CollectionsRepository(memory_db)
    assert repo.delete(999) is False


def test_unique_name(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    hid = sample_code_header.code_header_id
    repo.create(_build(hid, name="X"))
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_build(hid, name="X"))


def test_invalid_code_header_fk(memory_db):
    repo = CollectionsRepository(memory_db)
    with pytest.raises(sqlite3.IntegrityError):
        repo.create(_build(header_id=999))


# ----------------------------------------------------------------------
# Layout álbum (migración 004)
# ----------------------------------------------------------------------


def test_create_uses_default_album_layout(memory_db, sample_code_header):
    """Sin pasar campos de álbum, se persisten los defaults 3×4 portrait."""
    repo = CollectionsRepository(memory_db)
    created = repo.create(_build(sample_code_header.code_header_id))
    found = repo.get_by_id(created.collection_id)
    assert found is not None
    assert found.album_columns == 3
    assert found.album_rows == 4
    assert found.album_orientation == "portrait"


def test_create_persists_custom_album_layout(memory_db, sample_code_header):
    """Layout custom (5×3 landscape) se persiste y se lee correctamente."""
    repo = CollectionsRepository(memory_db)
    created = repo.create(
        _build(
            sample_code_header.code_header_id,
            name="LandscapeCol",
            album_columns=5,
            album_rows=3,
            album_orientation="landscape",
        )
    )
    found = repo.get_by_id(created.collection_id)
    assert found is not None
    assert found.album_columns == 5
    assert found.album_rows == 3
    assert found.album_orientation == "landscape"


def test_update_modifies_album_layout(memory_db, sample_collection):
    """update() persiste cambios en los 3 campos de álbum."""
    from dataclasses import replace

    repo = CollectionsRepository(memory_db)
    modified = replace(
        sample_collection,
        album_columns=4,
        album_rows=6,
        album_orientation="landscape",
    )
    repo.update(modified)
    found = repo.get_by_id(sample_collection.collection_id)
    assert found is not None
    assert found.album_columns == 4
    assert found.album_rows == 6
    assert found.album_orientation == "landscape"
```

### [tests/core/repositories/test_inventory_repo.py](tests/core/repositories/test_inventory_repo.py)

```python
"""Tests del InventoryRepository."""

import pytest

from collections_app.core.models import Card, InventoryItem
from collections_app.core.repositories import InventoryRepository


def _item(cid: int, code: str = "ARG", num: int = 1, qty: int = 1, image=None) -> InventoryItem:
    return InventoryItem(cid, code, num, qty, image)


def test_upsert_creates_item(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    item = _item(sample_collection.collection_id, qty=3)
    repo.upsert(item)
    fetched = repo.get(sample_collection.collection_id, "ARG", 1)
    assert fetched == item


def test_upsert_updates_existing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1))
    repo.upsert(_item(cid, qty=5, image="/tmp/messi.png"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.quantity == 5
    assert fetched.image_path == "/tmp/messi.png"


def test_get_missing(memory_db, sample_collection):
    repo = InventoryRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ZZZ", 999) is None


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = InventoryRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_owned_filters_zero(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=0))
    repo.upsert(_item(cid, "ARG", 2, qty=2))
    repo.upsert(_item(cid, "BRA", 1, qty=1))
    owned = repo.list_owned(cid)
    assert len(owned) == 2
    assert all(i.quantity > 0 for i in owned)


def test_list_duplicates(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=1))
    repo.upsert(_item(cid, "ARG", 2, qty=3))
    repo.upsert(_item(cid, "BRA", 1, qty=2))
    dups = repo.list_duplicates(cid)
    assert len(dups) == 2
    assert {(i.code_id, i.card_number) for i in dups} == {("ARG", 2), ("BRA", 1)}


def test_list_missing_returns_cards_without_inventory(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=2))
    # Las otras 4 cards no tienen inventario
    missing = repo.list_missing(cid)
    assert len(missing) == 4
    assert all(isinstance(c, Card) for c in missing)
    assert ("ARG", 1) not in {(c.code_id, c.card_number) for c in missing}


def test_list_missing_treats_zero_qty_as_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=0))
    repo.upsert(_item(cid, "ARG", 2, qty=1))
    missing = repo.list_missing(cid)
    keys = {(c.code_id, c.card_number) for c in missing}
    assert ("ARG", 1) in keys  # qty=0 cuenta como missing
    assert ("ARG", 2) not in keys


def test_adjust_quantity_creates_when_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    item = repo.adjust_quantity(cid, "ARG", 1, 3)
    assert item.quantity == 3


def test_adjust_quantity_increments(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=2))
    item = repo.adjust_quantity(cid, "ARG", 1, 3)
    assert item.quantity == 5


def test_adjust_quantity_decrements(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=5))
    item = repo.adjust_quantity(cid, "ARG", 1, -3)
    assert item.quantity == 2


def test_adjust_quantity_negative_raises(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1))
    with pytest.raises(ValueError, match="negativa"):
        repo.adjust_quantity(cid, "ARG", 1, -5)


def test_adjust_quantity_preserves_image(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=1, image="/img/messi.png"))
    item = repo.adjust_quantity(cid, "ARG", 1, 1)
    assert item.image_path == "/img/messi.png"


def test_set_image_creates_record_if_missing(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.set_image(cid, "ARG", 1, "/img/messi.png")
    item = repo.get(cid, "ARG", 1)
    assert item is not None
    assert item.quantity == 0
    assert item.image_path == "/img/messi.png"


def test_set_image_preserves_quantity(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, qty=4))
    repo.set_image(cid, "ARG", 1, "/img/messi.png")
    item = repo.get(cid, "ARG", 1)
    assert item is not None
    assert item.quantity == 4


def test_inventory_item_is_owned_property():
    assert InventoryItem(1, "X", 1, quantity=0).is_owned is False
    assert InventoryItem(1, "X", 1, quantity=2).is_owned is True


def test_inventory_item_has_duplicates_property():
    assert InventoryItem(1, "X", 1, quantity=1).has_duplicates is False
    assert InventoryItem(1, "X", 1, quantity=2).has_duplicates is True


def test_get_top_duplicates(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=5))
    repo.upsert(_item(cid, "ARG", 2, qty=3))
    repo.upsert(_item(cid, "BRA", 1, qty=2))
    repo.upsert(_item(cid, "BRA", 2, qty=1))  # no es duplicada
    top = repo.get_top_duplicates(cid)
    assert [(t.code_id, t.card_number, t.quantity) for t in top] == [
        ("ARG", 1, 5),
        ("ARG", 2, 3),
        ("BRA", 1, 2),
    ]


def test_get_top_duplicates_respects_limit(memory_db, sample_cards, sample_collection):
    repo = InventoryRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_item(cid, "ARG", 1, qty=5))
    repo.upsert(_item(cid, "ARG", 2, qty=4))
    repo.upsert(_item(cid, "BRA", 1, qty=3))
    top = repo.get_top_duplicates(cid, limit=2)
    assert len(top) == 2
```

### [tests/core/repositories/test_settings_repo.py](tests/core/repositories/test_settings_repo.py)

```python
"""Tests del SettingsRepository."""

from collections_app.core.repositories import SettingsRepository


def test_get_missing_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.get("nope") is None


def test_set_and_get(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    assert repo.get("foo") == "bar"


def test_set_overwrites_existing(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    repo.set("foo", "baz")
    assert repo.get("foo") == "baz"


def test_delete_existing(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "bar")
    assert repo.delete("foo") is True
    assert repo.get("foo") is None


def test_delete_missing_returns_false(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.delete("nope") is False


def test_get_int_returns_parsed(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("count", "42")
    assert repo.get_int("count") == 42


def test_get_int_missing_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    assert repo.get_int("nope") is None


def test_get_int_invalid_returns_none(memory_db):
    repo = SettingsRepository(memory_db)
    repo.set("foo", "not-a-number")
    assert repo.get_int("foo") is None
```

### [tests/core/repositories/test_transactions_repo.py](tests/core/repositories/test_transactions_repo.py)

```python
"""Tests del TransactionsRepository."""

from datetime import UTC, datetime, timedelta

from collections_app.core.models import OperationType, Transaction
from collections_app.core.repositories import TransactionsRepository
from collections_app.core.utils.datetime_helpers import utc_now


def _txn(cid: int, op: OperationType = OperationType.ALTA, qty: int = 1) -> Transaction:
    return Transaction(
        transaction_id=None,
        collection_id=cid,
        code_id="ARG",
        card_number=1,
        operation=op,
        quantity=qty,
        transaction_date=utc_now(),
    )


def test_log_returns_with_id_and_date(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    saved = repo.log(_txn(sample_collection.collection_id))
    assert saved.transaction_id is not None
    assert isinstance(saved.transaction_date, datetime)
    assert saved.operation == OperationType.ALTA


def test_log_preserves_operation_type(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    saved = repo.log(_txn(sample_collection.collection_id, OperationType.BAJA))
    assert saved.operation == OperationType.BAJA


def test_list_by_collection_descending(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(3):
        repo.log(_txn(cid))
    txns = repo.list_by_collection(cid)
    assert len(txns) == 3
    ids = [t.transaction_id for t in txns]
    assert ids == sorted(ids, reverse=True)


def test_list_by_collection_respects_limit(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(5):
        repo.log(_txn(cid))
    txns = repo.list_by_collection(cid, limit=2)
    assert len(txns) == 2


def test_list_by_collection_empty(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    assert repo.list_by_collection(sample_collection.collection_id) == []


def test_list_recent(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(3):
        repo.log(_txn(cid))
    recent = repo.list_recent(limit=2)
    assert len(recent) == 2


def test_list_recent_default_limit(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    for _ in range(25):
        repo.log(_txn(cid))
    recent = repo.list_recent()
    assert len(recent) == 20  # default limit


def test_list_by_date_range(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    now = utc_now()
    # Ahora que la DB y Python están unificados en UTC, una ventana
    # estrecha (±1 minuto) basta.
    txns = repo.list_by_date_range(now - timedelta(minutes=1), now + timedelta(minutes=1))
    assert len(txns) == 1


def test_list_by_date_range_excludes_outside(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    future_start = utc_now() + timedelta(hours=1)
    future_end = utc_now() + timedelta(hours=2)
    assert repo.list_by_date_range(future_start, future_end) == []


def test_list_by_date_range_filtered_by_collection(memory_db, sample_collection):
    repo = TransactionsRepository(memory_db)
    cid = sample_collection.collection_id
    repo.log(_txn(cid))
    now = utc_now()
    same_collection = repo.list_by_date_range(
        now - timedelta(minutes=1), now + timedelta(minutes=1), collection_id=cid
    )
    other_collection = repo.list_by_date_range(
        now - timedelta(minutes=1), now + timedelta(minutes=1), collection_id=999
    )
    assert len(same_collection) == 1
    assert other_collection == []


def test_log_returns_transaction_with_utc_tzinfo(memory_db, sample_collection):
    """Las transacciones leídas siempre vienen con tzinfo=UTC."""
    repo = TransactionsRepository(memory_db)
    saved = repo.log(_txn(sample_collection.collection_id))
    assert saved.transaction_date.tzinfo is UTC
```

### [tests/core/services/__init__.py](tests/core/services/__init__.py)

_(archivo vacío)_

### [tests/core/services/test_album_service.py](tests/core/services/test_album_service.py)

```python
"""Tests del AlbumService (data layer entre DB y renderers)."""

from collections_app.core.models import Card, CodeLine, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.services import AlbumService


def _seed(memory_db, sample_collection, codes_lines, cards, inventory=None):
    """Helper: popula codes_lines, cards e (opcional) inventory.

    `codes_lines` es lista de `(code_id, code_name)` o `(code_id, code_name, order)`.
    """
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    cl_repo = CodesLinesRepository(memory_db)
    for entry in codes_lines:
        if len(entry) == 2:
            code_id, code_name = entry
            order = 0
        else:
            code_id, code_name, order = entry
        cl_repo.upsert(CodeLine(hid, code_id, code_name, code_order=order))
    c_repo = CardsRepository(memory_db)
    for code_id, n, name in cards:
        c_repo.upsert(Card(cid, code_id, n, name))
    if inventory:
        i_repo = InventoryRepository(memory_db)
        for code_id, n, qty in inventory:
            i_repo.upsert(InventoryItem(cid, code_id, n, quantity=qty))
    memory_db.commit()


# ----------------------------------------------------------------------
# build_album_cards
# ----------------------------------------------------------------------


def test_build_album_cards_all_present(memory_db, sample_collection):
    """3 cards en DB, 3 en inventario → 3 AlbumCards con qty>0."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "A"), ("ARG", 2, "B"), ("ARG", 3, "C")],
        [("ARG", 1, 1), ("ARG", 2, 2), ("ARG", 3, 1)],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert len(cards) == 3
    assert all(ac.quantity > 0 for ac in cards)


def test_build_album_cards_missing_have_quantity_zero(memory_db, sample_collection):
    """3 cards, solo 1 en inventario → las otras 2 tienen quantity=0."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "A"), ("ARG", 2, "B"), ("ARG", 3, "C")],
        [("ARG", 2, 1)],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_n = {ac.card.card_number: ac.quantity for ac in cards}
    assert by_n == {1: 0, 2: 1, 3: 0}


def test_build_album_cards_sorted_by_code_order_then_number(memory_db, sample_collection):
    """Categorías ordenadas por `code_order` (no alfabético por code_id)."""
    # ZIM (Zimbabwe) tiene code_order=1, ALG (Argelia) tiene order=2,
    # ARG order=3. Si fuera alfabético, ALG iría primero. Con el sort
    # nuevo, ZIM va primero porque tiene order menor.
    _seed(
        memory_db,
        sample_collection,
        [
            ("ZIM", "ZIMBABWE", 1),
            ("ALG", "ALGERIA", 2),
            ("ARG", "ARGENTINA", 3),
        ],
        [
            ("ARG", 1, "Messi"),
            ("ALG", 2, "Mahrez"),
            ("ZIM", 3, "Player"),
            ("ALG", 1, "Brahimi"),
        ],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    keys = [(ac.card.code_id, ac.card.card_number) for ac in cards]
    # ZIM (order=1) → ALG (order=2) → ARG (order=3); dentro de cada
    # categoría, por card_number ascendente.
    assert keys == [
        ("ZIM", 3),
        ("ALG", 1),
        ("ALG", 2),
        ("ARG", 1),
    ]


def test_build_album_cards_falls_back_to_alpha_when_orders_tied(memory_db, sample_collection):
    """Si dos categorías tienen el mismo code_order (default 0), desempata code_id alfa."""
    _seed(
        memory_db,
        sample_collection,
        [("BRA", "BRAZIL"), ("ARG", "ARGENTINA")],  # ambos order=0 implícito
        [("BRA", 1, "Vini"), ("ARG", 1, "Messi")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    keys = [ac.card.code_id for ac in cards]
    assert keys == ["ARG", "BRA"]


def test_build_album_cards_populates_code_order(memory_db, sample_collection):
    """AlbumCard.code_order viene poblado desde codes_lines."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA", 5), ("BRA", "BRAZIL", 7)],
        [("ARG", 1, "Messi"), ("BRA", 1, "Vini")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_code = {ac.card.code_id: ac.code_order for ac in cards}
    assert by_code == {"ARG": 5, "BRA": 7}


def test_build_album_cards_unknown_code_has_order_zero(memory_db, sample_collection):
    """Card con code_id no registrado en codes_lines → code_order=0 (default)."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA", 5)],
        [("XYZ", 1, "Player")],  # XYZ no está en codes_lines
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].code_order == 0


def test_build_album_cards_resolves_code_name(memory_db, sample_collection):
    """El AlbumCard incluye `code_name` del codes_lines, no el id corto."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")],
        [("ARG", 1, "Messi"), ("BRA", 1, "Vini")],
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    by_code = {ac.card.code_id: ac.code_name for ac in cards}
    assert by_code == {"ARG": "ARGENTINA", "BRA": "BRAZIL"}


def test_build_album_cards_unknown_code_falls_back_to_id(memory_db, sample_collection):
    """Card con code_id no presente en codes_lines → code_name = code_id."""
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("XYZ", 1, "Player")],  # code_id no está en codes_lines
    )
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert len(cards) == 1
    assert cards[0].code_name == "XYZ"


def test_build_album_cards_image_path_none_when_not_downloaded(
    memory_db, sample_collection, monkeypatch
):
    """Sin foto descargada → image_path es None."""
    monkeypatch.setattr(
        "collections_app.core.services.album_service.find_card_image",
        lambda _cid, _n: None,
    )
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].image_path is None


def test_build_album_cards_image_path_resolved_when_present(
    memory_db, sample_collection, tmp_path, monkeypatch
):
    """Cuando find_card_image retorna un path existente, AlbumCard lo lleva."""
    fake = tmp_path / "0001.jpg"
    fake.write_bytes(b"x")
    monkeypatch.setattr(
        "collections_app.core.services.album_service.find_card_image",
        lambda _cid, _n: fake,
    )
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert cards[0].image_path == fake


def test_build_album_cards_propagates_requires_code(memory_db, sample_collection):
    """`requires_code` del Collection se replica en cada AlbumCard."""
    _seed(memory_db, sample_collection, [("ARG", "ARGENTINA")], [("ARG", 1, "Messi")])
    cards = AlbumService(memory_db).build_album_cards(sample_collection)
    assert all(ac.requires_code is sample_collection.requires_code for ac in cards)


# ----------------------------------------------------------------------
# get_code_names
# ----------------------------------------------------------------------


def test_get_code_names_returns_mapping(memory_db, sample_collection):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")],
        [],
    )
    names = AlbumService(memory_db).get_code_names(sample_collection)
    assert names == {"ARG": "ARGENTINA", "BRA": "BRAZIL"}


def test_get_code_names_empty_when_no_lines(memory_db, sample_collection):
    assert AlbumService(memory_db).get_code_names(sample_collection) == {}


# ----------------------------------------------------------------------
# Wrappers de generación: smoke (delegan al renderer)
# ----------------------------------------------------------------------


def test_generate_album_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi"), ("ARG", 2, "Otamendi")],
        [("ARG", 1, 1)],
    )
    out = tmp_path / "album.pdf"
    result = AlbumService(memory_db).generate_album_pdf(sample_collection, out)
    assert out.exists()
    assert result.pages >= 1


def test_generate_missing_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi"), ("ARG", 2, "Otamendi")],
        # ninguna en inventario → ambas son faltantes
    )
    out = tmp_path / "missing.pdf"
    AlbumService(memory_db).generate_missing_pdf(sample_collection, out)
    assert out.exists()


def test_generate_duplicates_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi")],
        [("ARG", 1, 3)],
    )
    out = tmp_path / "dups.pdf"
    AlbumService(memory_db).generate_duplicates_pdf(sample_collection, out)
    assert out.exists()


def test_generate_owned_pdf_writes_file(memory_db, sample_collection, tmp_path):
    _seed(
        memory_db,
        sample_collection,
        [("ARG", "ARGENTINA")],
        [("ARG", 1, "Messi")],
        [("ARG", 1, 1)],
    )
    out = tmp_path / "owned.pdf"
    AlbumService(memory_db).generate_owned_pdf(sample_collection, out)
    assert out.exists()
```

### [tests/core/services/test_collections_service.py](tests/core/services/test_collections_service.py)

```python
"""Tests del CollectionsService."""

import pytest

from collections_app.core.models import Collection
from collections_app.core.services import CollectionsService


def test_create_collection_validates_header_exists(memory_db, sample_code_header):
    svc = CollectionsService(memory_db)
    created = svc.create_collection_with_validation(
        Collection(
            collection_id=None,
            collection_name="Test",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
        )
    )
    assert created.collection_id is not None


def test_create_collection_rejects_missing_header(memory_db):
    svc = CollectionsService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.create_collection_with_validation(
            Collection(
                collection_id=None,
                collection_name="Test",
                card_count=10,
                requires_code=False,
                code_field_name=None,
                code_header_id=999,
            )
        )


def test_get_full_collection_info_returns_dict(memory_db, sample_collection, sample_cards):
    svc = CollectionsService(memory_db)
    info = svc.get_full_collection_info(sample_collection.collection_id)
    assert info is not None
    assert info["collection"].collection_id == sample_collection.collection_id
    assert info["code_header"] is not None
    assert info["num_cards"] == 5
    assert info["num_codes"] == 0  # no hay codes_lines en sample fixtures


def test_get_full_collection_info_missing(memory_db):
    svc = CollectionsService(memory_db)
    assert svc.get_full_collection_info(999) is None


def test_can_be_deleted_existing(memory_db, sample_collection):
    svc = CollectionsService(memory_db)
    can, reason = svc.can_be_deleted(sample_collection.collection_id)
    assert can is True
    assert reason == ""


def test_can_be_deleted_missing(memory_db):
    svc = CollectionsService(memory_db)
    can, reason = svc.can_be_deleted(999)
    assert can is False
    assert "no existe" in reason
```

### [tests/core/services/test_exchange_service.py](tests/core/services/test_exchange_service.py)

```python
"""Tests del ExchangeService: archivos .colexchange, comparación e intercambio."""

import json

import pytest

from collections_app.core.models import (
    ExchangeCard,
    ExchangeFile,
    ExchangeSession,
    InventoryItem,
)
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services.exchange_service import (
    EXCHANGE_APP_ID,
    ExchangeService,
)

# ----------------------------------------------------------------------
# Fixtures locales
# ----------------------------------------------------------------------


@pytest.fixture
def populated_db(memory_db, sample_collection, sample_cards):
    """memory_db con sample_collection + sample_cards + inventario inicial.

    Inventario (collection FIFA WC 2026, requires_code=True):
      ARG-1 Messi:        quantity=1
      ARG-2 Martínez:     quantity=2  (repetida)
      BRA-1 Vinícius:     quantity=0  (faltante)
      BRA-2 Neymar:       quantity=3  (repetida)
      FRA-1 Mbappé:       quantity=0  (faltante)
    """
    cid = sample_collection.collection_id
    inv = InventoryRepository(memory_db)
    inv.upsert(InventoryItem(cid, "ARG", 1, quantity=1))
    inv.upsert(InventoryItem(cid, "ARG", 2, quantity=2))
    inv.upsert(InventoryItem(cid, "BRA", 2, quantity=3))
    memory_db.commit()
    return memory_db, sample_collection


# ----------------------------------------------------------------------
# Generación + carga + checksum
# ----------------------------------------------------------------------


def test_generate_creates_colexchange_file(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"

    ef = ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    assert out.exists()
    assert ef.app == EXCHANGE_APP_ID
    assert ef.collection_id == col.collection_id
    # Faltantes: BRA-1 y FRA-1. Repetidas: ARG-2, BRA-2.
    assert {(c.code_id, c.card_number) for c in ef.missing} == {("BRA", 1), ("FRA", 1)}
    assert {(c.code_id, c.card_number) for c in ef.duplicates} == {("ARG", 2), ("BRA", 2)}


def test_generated_file_has_valid_checksum(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    # load_exchange_file verifica el checksum y NO lanza si es válido.
    ef = ExchangeService(conn).load_exchange_file(out)
    assert ef.collection_id == col.collection_id
    assert ef.checksum != ""


def test_load_rejects_tampered_file(populated_db, tmp_path):
    conn, col = populated_db
    out = tmp_path / "user1.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)

    # Modificamos el archivo agregando una "carta extra" sin tocar el checksum.
    data = json.loads(out.read_text(encoding="utf-8"))
    data["duplicates"].append(
        {"code_id": "FAKE", "card_number": 999, "card_name": "Hacked", "quantity": 5}
    )
    out.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="checksum"):
        ExchangeService(conn).load_exchange_file(out)


def test_load_rejects_non_colexchange_app(memory_db, tmp_path):
    out = tmp_path / "fake.colexchange"
    out.write_text(
        json.dumps(
            {
                "app": "OtherApp",
                "version": "1.0",
                "collection_id": 1,
                "collection_name": "x",
                "missing": [],
                "duplicates": [],
                "checksum": "deadbeef",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="CollectionsApp"):
        ExchangeService(memory_db).load_exchange_file(out)


def test_load_rejects_invalid_json(memory_db, tmp_path):
    out = tmp_path / "bad.colexchange"
    out.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="Archivo inválido"):
        ExchangeService(memory_db).load_exchange_file(out)


# ----------------------------------------------------------------------
# Comparación
# ----------------------------------------------------------------------


def _make_file(collection_id: int, *, missing=None, duplicates=None) -> ExchangeFile:
    return ExchangeFile(
        app=EXCHANGE_APP_ID,
        version="1.0",
        collection_id=collection_id,
        collection_name="X",
        generated_at="2026-01-01T00:00:00+00:00",
        missing=missing or [],
        duplicates=duplicates or [],
    )


def test_compare_i_need_correct(memory_db):
    # Yo necesito ARG-24. El otro lo tiene repetido.
    me = _make_file(1, missing=[ExchangeCard("ARG", 24, "Messi")])
    other = _make_file(
        1,
        duplicates=[ExchangeCard("ARG", 24, "Messi", 2), ExchangeCard("BRA", 7, "Vini", 3)],
    )
    result = ExchangeService(memory_db).compare(me, other)
    assert [(c.code_id, c.card_number) for c in result.i_need] == [("ARG", 24)]
    assert result.i_can_offer == []


def test_compare_i_can_offer_correct(memory_db):
    me = _make_file(1, duplicates=[ExchangeCard("NON", 42, "Álvarez", 2)])
    other = _make_file(1, missing=[ExchangeCard("NON", 42, "Álvarez"), ExchangeCard("BRA", 5, "X")])
    result = ExchangeService(memory_db).compare(me, other)
    assert [(c.code_id, c.card_number) for c in result.i_can_offer] == [("NON", 42)]
    assert result.i_need == []


def test_compare_no_overlap_returns_empty(memory_db):
    me = _make_file(
        1, missing=[ExchangeCard("ARG", 1, "x")], duplicates=[ExchangeCard("BRA", 1, "y", 2)]
    )
    other = _make_file(
        1, missing=[ExchangeCard("FRA", 1, "z")], duplicates=[ExchangeCard("ESP", 1, "w", 2)]
    )
    result = ExchangeService(memory_db).compare(me, other)
    assert result.i_need == []
    assert result.i_can_offer == []


def test_compare_different_collections_raises(memory_db):
    me = _make_file(1)
    other = _make_file(2)
    with pytest.raises(ValueError, match="colecciones distintas"):
        ExchangeService(memory_db).compare(me, other)


# ----------------------------------------------------------------------
# Lock / Unlock
# ----------------------------------------------------------------------


def test_lock_increments_locked_column(populated_db):
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    # ARG-2 quantity=2, locked=0
    item = repo.get(cid, "ARG", 2)
    assert item.quantity == 2 and item.locked == 0

    ExchangeService(conn).lock_cards(cid, [ExchangeCard("ARG", 2, "Martínez", 2)])

    item = repo.get(cid, "ARG", 2)
    assert item.locked == 1
    assert item.available_quantity == 1


def test_lock_creates_item_when_missing(populated_db):
    """Bloquear una carta sin inventario crea el item con qty=0, locked=1."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    assert repo.get(cid, "FRA", 1) is None  # no existía

    ExchangeService(conn).lock_cards(cid, [ExchangeCard("FRA", 1, "Mbappé")])

    item = repo.get(cid, "FRA", 1)
    assert item is not None
    assert item.quantity == 0
    assert item.locked == 1


def test_unlock_all_resets_locked(populated_db):
    conn, col = populated_db
    cid = col.collection_id
    svc = ExchangeService(conn)
    svc.lock_cards(
        cid,
        [
            ExchangeCard("ARG", 2, "Martínez"),
            ExchangeCard("BRA", 2, "Neymar"),
        ],
    )
    svc.unlock_all_cards(cid)

    repo = InventoryRepository(conn)
    assert repo.get(cid, "ARG", 2).locked == 0
    assert repo.get(cid, "BRA", 2).locked == 0
    assert repo.list_locked(cid) == []


# ----------------------------------------------------------------------
# Generación: cantidad ofrecida = available_quantity - 1 (conservar 1)
# ----------------------------------------------------------------------


def test_duplicates_quantity_is_available_minus_one(populated_db, tmp_path):
    """qty=3, locked=0 → available=3 → ofrece 2 (conserva 1)."""
    conn, col = populated_db
    cid = col.collection_id
    out = tmp_path / "user1.colexchange"
    # En el fixture BRA-2 tiene qty=3 y locked=0.
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    bra2 = next((c for c in ef.duplicates if c.code_id == "BRA" and c.card_number == 2), None)
    assert bra2 is not None
    assert bra2.quantity == 2  # 3 - 1


def test_duplicates_quantity_2_offers_1(populated_db, tmp_path):
    """qty=2, locked=0 → available=2 → ofrece 1."""
    conn, col = populated_db
    cid = col.collection_id
    out = tmp_path / "user1.colexchange"
    # En el fixture ARG-2 tiene qty=2.
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    arg2 = next((c for c in ef.duplicates if c.code_id == "ARG" and c.card_number == 2), None)
    assert arg2 is not None
    assert arg2.quantity == 1


def test_duplicates_quantity_1_not_included(populated_db, tmp_path):
    """qty=1 → available=1 → NO aparece (no puede ofrecer nada)."""
    conn, col = populated_db
    cid = col.collection_id
    # ARG-1 tiene qty=1 en el fixture.
    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    codes = {(c.code_id, c.card_number) for c in ef.duplicates}
    assert ("ARG", 1) not in codes


def test_duplicates_with_locked_reduces_oferable(populated_db, tmp_path):
    """qty=3, locked=1 → available=2 → ofrece 1 (2 - 1)."""
    conn, col = populated_db
    cid = col.collection_id
    # BRA-2 qty=3; bloqueamos 1.
    InventoryRepository(conn).lock(cid, "BRA", 2)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    bra2 = next((c for c in ef.duplicates if c.code_id == "BRA" and c.card_number == 2), None)
    assert bra2 is not None
    assert bra2.quantity == 1


def test_duplicates_with_locked_equal_quantity_not_included(populated_db, tmp_path):
    """qty=2, locked=1 → available=1 → NO aparece en duplicates."""
    conn, col = populated_db
    cid = col.collection_id
    # ARG-2 qty=2; bloqueamos 1 → available=1.
    InventoryRepository(conn).lock(cid, "ARG", 2)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    codes = {(c.code_id, c.card_number) for c in ef.duplicates}
    assert ("ARG", 2) not in codes


# ----------------------------------------------------------------------
# Generación: las cartas bloqueadas no aparecen en duplicates
# ----------------------------------------------------------------------


def test_duplicates_excludes_locked_items(populated_db, tmp_path):
    """ARG-2 quantity=2, locked=1 → available=1 → NO aparece en duplicates."""
    conn, col = populated_db
    cid = col.collection_id

    InventoryRepository(conn).lock(cid, "ARG", 2)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    codes = {(c.code_id, c.card_number) for c in ef.duplicates}
    assert ("ARG", 2) not in codes
    # BRA-2 sigue disponible
    assert ("BRA", 2) in codes


def test_missing_includes_card_with_only_locked_unit(populated_db, tmp_path):
    """Si una carta tiene qty=1 y locked=1, available=0 → faltante."""
    conn, col = populated_db
    cid = col.collection_id
    # ARG-1 tiene qty=1. La bloqueamos.
    InventoryRepository(conn).lock(cid, "ARG", 1)
    conn.commit()

    out = tmp_path / "user1.colexchange"
    ef = ExchangeService(conn).generate_exchange_file(cid, out)

    missing_codes = {(c.code_id, c.card_number) for c in ef.missing}
    assert ("ARG", 1) in missing_codes


# ----------------------------------------------------------------------
# Ejecución del intercambio
# ----------------------------------------------------------------------


def test_execute_exchange_gives_and_receives(populated_db):
    """to_give resta del inventario, to_receive suma, locked queda en 0."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    assert repo.get(cid, "ARG", 2).quantity == 2  # entrego 1
    assert repo.get(cid, "BRA", 1) is None  # recibo 1

    session = ExchangeSession(
        to_give=[ExchangeCard("ARG", 2, "Martínez")],
        to_receive=[ExchangeCard("BRA", 1, "Vinícius")],
    )
    # Pre-lock como hace el dialog
    ExchangeService(conn).lock_cards(cid, session.to_give)

    ExchangeService(conn).execute_exchange(cid, session)

    arg2 = repo.get(cid, "ARG", 2)
    bra1 = repo.get(cid, "BRA", 1)
    assert arg2.quantity == 1
    assert arg2.locked == 0
    assert bra1.quantity == 1
    assert bra1.locked == 0


def test_execute_exchange_rollback_on_error(populated_db):
    """Si una baja falla, todas las operaciones revierten."""
    conn, col = populated_db
    cid = col.collection_id
    repo = InventoryRepository(conn)
    arg2_before = repo.get(cid, "ARG", 2).quantity
    bra2_before = repo.get(cid, "BRA", 2).quantity

    # Pedimos bajar 1 de FRA-1 que no tenemos → debe fallar y revertir todo
    session = ExchangeSession(
        to_give=[
            ExchangeCard("ARG", 2, "Martínez"),
            ExchangeCard("FRA", 1, "Mbappé"),  # no la tengo → ValueError
        ],
        to_receive=[ExchangeCard("BRA", 1, "Vinícius")],
    )
    with pytest.raises(ValueError):
        ExchangeService(conn).execute_exchange(cid, session)

    # Estado inalterado: rollback exitoso
    assert repo.get(cid, "ARG", 2).quantity == arg2_before
    assert repo.get(cid, "BRA", 2).quantity == bra2_before
    assert repo.get(cid, "BRA", 1) is None  # no se creó


def test_execute_exchange_creates_card_in_catalog_if_missing(populated_db):
    """Si la carta a recibir no está en cards (raro), se crea silenciosamente."""
    conn, col = populated_db
    cid = col.collection_id

    cards_repo = CardsRepository(conn)
    # ZZZ-99 no existe
    assert cards_repo.get(cid, "ZZZ", 99) is None

    session = ExchangeSession(
        to_give=[],
        to_receive=[ExchangeCard("ZZZ", 99, "Foreign Card")],
    )
    ExchangeService(conn).execute_exchange(cid, session)

    # Carta creada en catálogo + inventario con quantity=1
    assert cards_repo.get(cid, "ZZZ", 99) is not None
    assert InventoryRepository(conn).get(cid, "ZZZ", 99).quantity == 1
```

### [tests/core/services/test_inventory_service.py](tests/core/services/test_inventory_service.py)

```python
"""Tests del InventoryService."""

import pytest

from collections_app.core.models import OperationType
from collections_app.core.repositories import (
    InventoryRepository,
    TransactionsRepository,
)
from collections_app.core.services import InventoryService


def test_add_card_creates_inventory_and_logs(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    item = svc.add_card(cid, "ARG", 1, quantity=2)
    assert item.quantity == 2

    txns = TransactionsRepository(memory_db).list_by_collection(cid)
    assert len(txns) == 1
    assert txns[0].operation == OperationType.ALTA
    assert txns[0].quantity == 2


def test_add_card_increments_existing(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    item = svc.add_card(cid, "ARG", 1, quantity=3)
    assert item.quantity == 4


def test_add_card_rejects_zero_or_negative(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="quantity"):
        svc.add_card(cid, "ARG", 1, quantity=0)
    with pytest.raises(ValueError, match="quantity"):
        svc.add_card(cid, "ARG", 1, quantity=-1)


def test_add_card_rejects_unknown_card(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="no existe"):
        svc.add_card(cid, "ZZZ", 999, quantity=1)


def test_remove_card_decrements_and_logs(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=5)
    item = svc.remove_card(cid, "ARG", 1, quantity=2)
    assert item.quantity == 3

    txns = TransactionsRepository(memory_db).list_by_collection(cid)
    operations = [t.operation for t in txns]
    assert OperationType.BAJA in operations


def test_remove_card_rejects_zero_or_negative(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    with pytest.raises(ValueError, match="quantity"):
        svc.remove_card(cid, "ARG", 1, quantity=0)
    with pytest.raises(ValueError, match="quantity"):
        svc.remove_card(cid, "ARG", 1, quantity=-1)


def test_remove_card_rejects_when_no_inventory(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError, match="No hay inventario"):
        svc.remove_card(cid, "ARG", 1, quantity=1)


def test_remove_card_rejects_when_insufficient(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    with pytest.raises(ValueError, match="insuficiente"):
        svc.remove_card(cid, "ARG", 1, quantity=5)


def test_remove_card_rollback_does_not_log_on_error(memory_db, sample_cards, sample_collection):
    """Si la baja falla validación, no se debe loguear ninguna transacción."""
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(ValueError):
        svc.remove_card(cid, "ARG", 1, quantity=1)
    assert TransactionsRepository(memory_db).list_by_collection(cid) == []


def test_get_stats_empty_collection(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    stats = svc.get_stats(sample_collection.collection_id)
    assert stats["total_cards"] == 0
    assert stats["owned"] == 0
    assert stats["missing"] == 0
    assert stats["percentage"] == 0.0
    assert stats["total_physical"] == 0
    assert stats["cards_with_duplicates"] == 0
    assert stats["total_duplicate_copies"] == 0


def test_get_stats_with_data(memory_db, sample_cards, sample_collection):
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=3)  # con duplicados (2 extras)
    svc.add_card(cid, "ARG", 2, quantity=1)
    svc.add_card(cid, "BRA", 1, quantity=2)  # 1 extra

    stats = svc.get_stats(cid)
    assert stats["total_cards"] == 5
    assert stats["owned"] == 3
    assert stats["missing"] == 2
    assert stats["percentage"] == pytest.approx(60.0)
    assert stats["total_physical"] == 6
    assert stats["cards_with_duplicates"] == 2
    assert stats["total_duplicate_copies"] == 3


def test_add_card_by_number_unique_match(memory_db, sample_cards, sample_collection):
    """Cuando find_by_number retorna 1, alta_by_number agrega normalmente."""
    from collections_app.core.models import Card
    from collections_app.core.repositories import CardsRepository

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    # Insertar una card con número único
    CardsRepository(memory_db).upsert(Card(cid, "FRA", 99, "Único"))
    memory_db.commit()
    item = svc.add_card_by_number(cid, 99, quantity=3)
    assert item.quantity == 3
    assert item.code_id == "FRA"
    assert item.card_number == 99


def test_add_card_by_number_zero_matches_raises_value_error(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.add_card_by_number(sample_collection.collection_id, 9999)


def test_add_card_by_number_ambiguous_raises(memory_db, sample_cards, sample_collection):
    """Si hay >1 card con ese número (en distintos códigos), AmbiguousCardError."""
    from collections_app.core.services import AmbiguousCardError

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    # En sample_cards, número 1 aparece en ARG, BRA, FRA → ambiguo
    with pytest.raises(AmbiguousCardError) as exc_info:
        svc.add_card_by_number(cid, 1)
    assert len(exc_info.value.matches) == 3


def test_remove_card_by_number_unique_match(memory_db, sample_cards, sample_collection):
    from collections_app.core.models import Card
    from collections_app.core.repositories import CardsRepository

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    CardsRepository(memory_db).upsert(Card(cid, "FRA", 99, "Único"))
    memory_db.commit()
    svc.add_card_by_number(cid, 99, quantity=5)
    item = svc.remove_card_by_number(cid, 99, quantity=2)
    assert item.quantity == 3


def test_remove_card_by_number_zero_matches_raises(memory_db, sample_collection):
    svc = InventoryService(memory_db)
    with pytest.raises(ValueError, match="no existe"):
        svc.remove_card_by_number(sample_collection.collection_id, 9999)


def test_remove_card_by_number_ambiguous_raises(memory_db, sample_cards, sample_collection):
    from collections_app.core.services import AmbiguousCardError

    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    with pytest.raises(AmbiguousCardError):
        svc.remove_card_by_number(cid, 1)


def test_add_card_inside_transaction_does_not_partial_commit(
    memory_db, sample_cards, sample_collection
):
    """Verifica que la operación es atómica (alta + log juntos)."""
    svc = InventoryService(memory_db)
    cid = sample_collection.collection_id
    svc.add_card(cid, "ARG", 1, quantity=1)
    inv_count = len(InventoryRepository(memory_db).list_owned(cid))
    txn_count = len(TransactionsRepository(memory_db).list_by_collection(cid))
    assert inv_count == txn_count == 1
```

### [tests/core/services/test_license_service.py](tests/core/services/test_license_service.py)

```python
"""Tests del LicenseService y LocalHashLicenseValidator."""

import pytest

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import (
    LicenseService,
    LicenseValidator,
    LocalHashLicenseValidator,
)

VALID_KEY = "secret-123"


@pytest.fixture
def free_collection(memory_db, sample_code_header) -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Free",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=False,
            license_key_required=None,
        )
    )
    memory_db.commit()
    return col


@pytest.fixture
def premium_collection(memory_db, sample_code_header) -> Collection:
    repo = CollectionsRepository(memory_db)
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Premium",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=True,
            license_key_required=LocalHashLicenseValidator.hash_key(VALID_KEY),
        )
    )
    memory_db.commit()
    return col


def test_free_collection_is_always_unlocked(memory_db, free_collection):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(free_collection.collection_id) is True


def test_premium_collection_locked_by_default(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_unlock_with_correct_key_persists(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.unlock(premium_collection.collection_id, VALID_KEY) is True
    assert svc.is_unlocked(premium_collection.collection_id) is True
    # Persiste tras reinstanciar el service
    svc2 = LicenseService(memory_db)
    assert svc2.is_unlocked(premium_collection.collection_id) is True


def test_unlock_with_wrong_key_fails(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    assert svc.unlock(premium_collection.collection_id, "wrong") is False
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_already_unlocked_returns_true(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    # Llamar unlock de nuevo con la misma key debe seguir true
    assert svc.unlock(premium_collection.collection_id, VALID_KEY) is True
    assert svc.is_unlocked(premium_collection.collection_id) is True


def test_lock_removes_persisted_key(memory_db, premium_collection):
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    svc.lock(premium_collection.collection_id)
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_hash_key_is_deterministic():
    a = LocalHashLicenseValidator.hash_key("foo")
    b = LocalHashLicenseValidator.hash_key("foo")
    assert a == b
    assert a != LocalHashLicenseValidator.hash_key("bar")


def test_validator_swappable(memory_db, premium_collection):
    """Se puede inyectar un validador alternativo (futuro: HTTP)."""

    class AcceptAllValidator(LicenseValidator):
        def validate(self, collection_id: int, license_key: str) -> bool:
            return True

        def is_required(self, collection: Collection) -> bool:
            return False

    svc = LicenseService(memory_db, validator=AcceptAllValidator())
    assert svc.is_unlocked(premium_collection.collection_id) is True
    assert svc.unlock(premium_collection.collection_id, "anything") is True


def test_unknown_collection_returns_false(memory_db):
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(9999) is False


def test_admin_changes_required_key_invalidates_unlock(memory_db, premium_collection):
    """Si el admin cambia el license_key_required, el unlock previo se invalida."""
    svc = LicenseService(memory_db)
    svc.unlock(premium_collection.collection_id, VALID_KEY)
    assert svc.is_unlocked(premium_collection.collection_id) is True

    # Admin cambia la key
    repo = CollectionsRepository(memory_db)
    new_required = LocalHashLicenseValidator.hash_key("new-secret")
    updated = Collection(
        collection_id=premium_collection.collection_id,
        collection_name=premium_collection.collection_name,
        card_count=premium_collection.card_count,
        requires_code=premium_collection.requires_code,
        code_field_name=premium_collection.code_field_name,
        code_header_id=premium_collection.code_header_id,
        is_premium=True,
        license_key_required=new_required,
    )
    repo.update(updated)
    memory_db.commit()

    # El unlock previo ya no vale
    assert svc.is_unlocked(premium_collection.collection_id) is False


def test_is_required_only_when_premium_with_key(memory_db, sample_code_header):
    repo = CollectionsRepository(memory_db)
    # Premium pero sin license_key_required → NO requerida (datos inconsistentes;
    # tratamos como free para no lockear al usuario por error de admin).
    col = repo.create(
        Collection(
            collection_id=None,
            collection_name="Inconsistent",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=sample_code_header.code_header_id,
            is_premium=True,
            license_key_required=None,
        )
    )
    memory_db.commit()
    svc = LicenseService(memory_db)
    assert svc.is_unlocked(col.collection_id) is True
```

### [tests/core/services/test_pdf_generator.py](tests/core/services/test_pdf_generator.py)

```python
"""Tests de los generadores de PDF (álbum + listas + metadata de intercambio)."""

import json
import os
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter

from collections_app.core.models import Card, Collection
from collections_app.core.services.pdf_generator import (
    EXCHANGE_APP_NAME,
    AlbumCard,
    DuplicatesReportMode,
    ListReportMode,
    _build_exchange_metadata,
    _chunks,
    format_label,
    generate_album_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
    validate_exchange_pdf_metadata,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _collection(
    name: str = "WC2026",
    cid: int = 1,
    requires_code: bool = True,
    cols: int = 3,
    rows: int = 4,
    orientation: str = "portrait",
) -> Collection:
    return Collection(
        collection_id=cid,
        collection_name=name,
        card_count=100,
        requires_code=requires_code,
        code_field_name="País" if requires_code else None,
        code_header_id=1,
        album_columns=cols,
        album_rows=rows,
        album_orientation=orientation,
    )


def _card(code: str, n: int, name: str = "Player") -> Card:
    return Card(collection_id=1, code_id=code, card_number=n, card_name=name)


def _ac(
    code: str,
    n: int,
    qty: int = 0,
    image_path: Path | None = None,
    requires_code: bool = True,
    code_name: str | None = None,
    name: str = "Player",
) -> AlbumCard:
    return AlbumCard(
        card=_card(code, n, name),
        quantity=qty,
        image_path=image_path,
        requires_code=requires_code,
        code_name=code_name or code,
    )


def _make_jpeg(path: Path, w: int = 100, h: int = 100) -> Path:
    """Genera un JPEG simple para usar como image_path en tests."""
    img = Image.frombytes("RGB", (w, h), os.urandom(w * h * 3))
    img.save(path, format="JPEG")
    return path


# ----------------------------------------------------------------------
# Helpers básicos: format_label / _chunks
# ----------------------------------------------------------------------


def test_format_label_requires_code():
    assert format_label(5, "ARG", requires_code=True) == "ARG-5"


def test_format_label_no_code():
    assert format_label(42, "ANY", requires_code=False) == "42"


def test_chunks_basic():
    assert _chunks([], 3) == []
    items = [_ac("X", n) for n in range(1, 6)]
    chunks = _chunks(items, 2)
    assert [len(c) for c in chunks] == [2, 2, 1]


# ----------------------------------------------------------------------
# Álbum visual
# ----------------------------------------------------------------------


def test_album_pdf_creates_nonempty_file(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=2, image_path=_make_jpeg(tmp_path / "img1.jpg")),  # CASO A
        _ac("ARG", 2, qty=1, code_name="ARGENTINA"),  # CASO B
        _ac("ARG", 3, qty=0, code_name="ARGENTINA"),  # CASO C
    ]
    out = tmp_path / "album.pdf"
    result = generate_album_pdf(col, cards, out)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages == 1


def test_album_pdf_new_category_new_page(tmp_path):
    """12 cards de ARG (llenan 1 página) + 1 de BRA = 2 páginas."""
    col = _collection(cols=3, rows=4)  # 12 cards/página
    cards_arg = [_ac("ARG", n, qty=1) for n in range(1, 13)]
    cards_bra = [_ac("BRA", 1, qty=1)]
    out = tmp_path / "album.pdf"
    result = generate_album_pdf(col, cards_arg + cards_bra, out)
    assert result.pages == 2


def test_album_pdf_12_same_category_one_page(tmp_path):
    col = _collection(cols=3, rows=4)
    cards = [_ac("ARG", n, qty=1) for n in range(1, 13)]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.pages == 1


def test_album_pdf_13_same_category_two_pages(tmp_path):
    col = _collection(cols=3, rows=4)
    cards = [_ac("ARG", n, qty=1) for n in range(1, 14)]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.pages == 2


def test_album_pdf_stats_count_each_case(tmp_path):
    col = _collection()
    img1 = _make_jpeg(tmp_path / "img1.jpg")
    img2 = _make_jpeg(tmp_path / "img2.jpg")
    cards = [
        _ac("ARG", 1, qty=1, image_path=img1),  # A
        _ac("ARG", 2, qty=2, image_path=img2),  # A
        _ac("ARG", 3, qty=1),  # B
        _ac("ARG", 4, qty=0),  # C
        _ac("ARG", 5, qty=0),  # C
    ]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    assert result.cards_with_image == 2
    assert result.cards_celeste_placeholder == 1
    assert result.cards_missing == 2


def test_album_pdf_no_photo_when_quantity_zero(tmp_path):
    """Aunque la foto exista en disco, si quantity=0 NO se muestra (CASO C).

    El álbum representa la colección del usuario, no el catálogo.
    """
    col = _collection()
    img = _make_jpeg(tmp_path / "exists.jpg")
    cards = [
        _ac("ARG", 1, qty=0, image_path=img),  # foto en disco PERO no la tengo
    ]
    result = generate_album_pdf(col, cards, tmp_path / "album.pdf")
    # Debe contar como missing (CASO C), NO como with_image (CASO A).
    assert result.cards_with_image == 0
    assert result.cards_missing == 1


def test_album_pdf_landscape_uses_landscape_pagesize(tmp_path):
    """Si la colección es landscape, el PDF también lo es (ancho > alto)."""
    col = _collection(orientation="landscape")
    cards = [_ac("ARG", 1, qty=1)]
    out = tmp_path / "album.pdf"
    generate_album_pdf(col, cards, out)
    reader = PdfReader(str(out))
    page = reader.pages[0]
    assert float(page.mediabox.width) > float(page.mediabox.height)


def test_album_pdf_portrait_uses_portrait_pagesize(tmp_path):
    col = _collection(orientation="portrait")
    cards = [_ac("ARG", 1, qty=1)]
    out = tmp_path / "album.pdf"
    generate_album_pdf(col, cards, out)
    reader = PdfReader(str(out))
    page = reader.pages[0]
    assert float(page.mediabox.height) > float(page.mediabox.width)


def test_album_pdf_empty_input_creates_one_page(tmp_path):
    col = _collection()
    result = generate_album_pdf(col, [], tmp_path / "album.pdf")
    assert result.pages == 1


# ----------------------------------------------------------------------
# Faltantes
# ----------------------------------------------------------------------


def test_missing_pdf_creates_file(tmp_path):
    col = _collection()
    cards = [_ac("ARG", n, qty=0) for n in range(1, 6)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)
    assert out.exists()
    assert out.stat().st_size > 1000


def test_missing_pdf_only_includes_quantity_zero(tmp_path):
    """Solo las cards con qty==0 entran en faltantes."""
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=0),
        _ac("BRA", 1, qty=2),
        _ac("BRA", 2, qty=0),
    ]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)
    # Inspeccionamos la metadata embebida para verificar conteo
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    # 3 faltantes: ARG-1, ARG-3, BRA-2
    assert len(meta["cards"]) == 3
    assert all(card["quantity"] == 0 for card in meta["cards"])


# ----------------------------------------------------------------------
# Repetidas
# ----------------------------------------------------------------------


def test_duplicates_pdf_only_includes_quantity_gt_1(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=2),
        _ac("ARG", 4, qty=3),
        _ac("ARG", 5, qty=1),
    ]
    out = tmp_path / "duplicates.pdf"
    generate_duplicates_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert len(meta["cards"]) == 2
    assert {c["card_number"] for c in meta["cards"]} == {3, 4}


# ----------------------------------------------------------------------
# Repetidas — modos FULL / SUMMARY
# ----------------------------------------------------------------------


def test_duplicates_mode_enum_values():
    assert DuplicatesReportMode.FULL == "full"
    assert DuplicatesReportMode.SUMMARY == "summary"


def test_duplicates_full_creates_file(tmp_path):
    """Modo FULL: archivo existe y > 1000 bytes."""
    col = _collection()
    cards = [
        _ac("ARG", 24, qty=2, code_name="ARGENTINA"),
        _ac("ARG", 7, qty=3, code_name="ARGENTINA"),
        _ac("BRA", 10, qty=2, code_name="BRAZIL"),
    ]
    out = tmp_path / "full.pdf"
    result = generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.FULL)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages >= 1


def test_duplicates_summary_creates_file(tmp_path):
    """Modo SUMMARY: archivo existe y > 1000 bytes."""
    col = _collection()
    cards = [
        _ac("ARG", 24, qty=2, code_name="ARGENTINA"),
        _ac("ARG", 7, qty=3, code_name="ARGENTINA"),
        _ac("BRA", 10, qty=2, code_name="BRAZIL"),
    ]
    out = tmp_path / "summary.pdf"
    result = generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.SUMMARY)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages >= 1


def test_duplicates_full_groups_by_category(tmp_path):
    """Cards de ARG y BRA mezcladas: no lanza excepción y al menos 1 página."""
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=2, code_name="ARGENTINA"),
        _ac("BRA", 1, qty=2, code_name="BRAZIL"),
        _ac("ARG", 2, qty=3, code_name="ARGENTINA"),
        _ac("BRA", 2, qty=2, code_name="BRAZIL"),
    ]
    out = tmp_path / "full.pdf"
    result = generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.FULL)
    assert result.pages >= 1


def test_duplicates_summary_smaller_than_full(tmp_path):
    """Mismo input: el SUMMARY ocupa menos bytes que el FULL (sin nombres)."""
    col = _collection()
    cards = [_ac("ARG", n, qty=2, code_name="ARGENTINA") for n in range(1, 30)] + [
        _ac("BRA", n, qty=2, code_name="BRAZIL") for n in range(1, 30)
    ]
    full_out = tmp_path / "full.pdf"
    summary_out = tmp_path / "summary.pdf"
    generate_duplicates_pdf(col, cards, full_out, mode=DuplicatesReportMode.FULL)
    generate_duplicates_pdf(col, cards, summary_out, mode=DuplicatesReportMode.SUMMARY)
    assert summary_out.stat().st_size < full_out.stat().st_size


def test_duplicates_full_handles_long_names(tmp_path):
    """Con nombres muy largos no lanza excepción y mantiene metadata válida."""
    col = _collection()
    long_name = "A" * 80  # mucho más largo que MAX_NAME_CHARS
    cards = [
        _ac("ARG", 1, qty=2, code_name="ARGENTINA"),
    ]
    cards[0] = AlbumCard(
        card=Card(collection_id=1, code_id="ARG", card_number=1, card_name=long_name),
        quantity=2,
        image_path=None,
        requires_code=True,
        code_name="ARGENTINA",
    )
    out = tmp_path / "full.pdf"
    result = generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.FULL)
    assert result.pages >= 1
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None


def test_duplicates_full_metadata_subtype_is_duplicates(tmp_path):
    """Aunque el layout cambie, el subtype embebido sigue siendo 'duplicates'."""
    col = _collection()
    cards = [_ac("ARG", 1, qty=2, code_name="ARGENTINA")]
    out = tmp_path / "full.pdf"
    generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.FULL)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["subtype"] == "duplicates"


def test_duplicates_summary_metadata_subtype_is_duplicates(tmp_path):
    col = _collection()
    cards = [_ac("ARG", 1, qty=2, code_name="ARGENTINA")]
    out = tmp_path / "summary.pdf"
    generate_duplicates_pdf(col, cards, out, mode=DuplicatesReportMode.SUMMARY)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["subtype"] == "duplicates"


def test_duplicates_default_mode_is_full(tmp_path):
    """Sin pasar mode, usa FULL por compat con la API anterior."""
    col = _collection()
    cards = [_ac("ARG", 1, qty=2, code_name="ARGENTINA")]
    out = tmp_path / "default.pdf"
    # No pasamos mode → debe usar FULL
    generate_duplicates_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["subtype"] == "duplicates"


# ----------------------------------------------------------------------
# Faltantes — modos FULL / SUMMARY (Fix nuevo)
# ----------------------------------------------------------------------


def _extract_pdf_text(path: Path) -> str:
    """Extrae el texto de TODAS las páginas de un PDF (concatenado)."""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_list_report_mode_enum():
    assert ListReportMode.FULL == "full"
    assert ListReportMode.SUMMARY == "summary"


def test_duplicates_report_mode_alias():
    """`DuplicatesReportMode` es alias de `ListReportMode` (back-compat)."""
    assert DuplicatesReportMode is ListReportMode


def test_missing_full_creates_file(tmp_path):
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA") for n in range(1, 6)]
    out = tmp_path / "missing_full.pdf"
    result = generate_missing_pdf(col, cards, out, mode=ListReportMode.FULL)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages >= 1


def test_missing_summary_creates_file(tmp_path):
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA") for n in range(1, 6)]
    out = tmp_path / "missing_summary.pdf"
    result = generate_missing_pdf(col, cards, out, mode=ListReportMode.SUMMARY)
    assert out.exists()
    assert out.stat().st_size > 1000
    assert result.pages >= 1


def test_missing_default_mode_is_full(tmp_path):
    col = _collection()
    cards = [_ac("ARG", 1, qty=0, code_name="ARGENTINA")]
    out = tmp_path / "default.pdf"
    generate_missing_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["subtype"] == "missing"


def test_missing_full_no_quantity_shown(tmp_path):
    """Faltantes nunca muestran '×N' (show_quantity=False hardcoded)."""
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA") for n in range(1, 4)]
    out = tmp_path / "missing_full.pdf"
    generate_missing_pdf(col, cards, out, mode=ListReportMode.FULL)
    text = _extract_pdf_text(out)
    assert "×" not in text


def test_missing_summary_no_quantity_shown(tmp_path):
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA") for n in range(1, 4)]
    out = tmp_path / "missing_summary.pdf"
    generate_missing_pdf(col, cards, out, mode=ListReportMode.SUMMARY)
    text = _extract_pdf_text(out)
    assert "×" not in text


def test_duplicates_full_shows_quantity(tmp_path):
    """En modo FULL de repetidas, '×N' aparece después de cada item."""
    col = _collection()
    cards = [
        _ac("ARG", 24, qty=3, code_name="ARGENTINA", name="Messi"),
        _ac("ARG", 7, qty=2, code_name="ARGENTINA", name="DiMaria"),
    ]
    out = tmp_path / "dups_full.pdf"
    generate_duplicates_pdf(col, cards, out, mode=ListReportMode.FULL)
    text = _extract_pdf_text(out)
    assert "×3" in text
    assert "×2" in text


def test_duplicates_summary_shows_quantity_inline(tmp_path):
    """En modo SUMMARY de repetidas, la cantidad va inline: '24×3'."""
    col = _collection()
    cards = [
        _ac("ARG", 24, qty=3, code_name="ARGENTINA"),
        _ac("ARG", 7, qty=2, code_name="ARGENTINA"),
    ]
    out = tmp_path / "dups_summary.pdf"
    generate_duplicates_pdf(col, cards, out, mode=ListReportMode.SUMMARY)
    text = _extract_pdf_text(out).replace("\n", "").replace(" ", "")
    # Forma inline: "24×3" y "7×2" deben aparecer juntos (sin espacio).
    assert "24×3" in text
    assert "7×2" in text


def test_summary_continuation_with_indent(tmp_path):
    """Categoría con muchos números: el PDF se genera sin lanzar (wrap OK)."""
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA") for n in range(1, 50)]
    out = tmp_path / "long.pdf"
    result = generate_missing_pdf(col, cards, out, mode=ListReportMode.SUMMARY)
    assert out.exists()
    assert result.pages >= 1


def test_full_flow_wraps_at_column_boundary(tmp_path):
    """Muchas cards: el PDF se genera (potencialmente con varias páginas)."""
    col = _collection()
    cards = [_ac("ARG", n, qty=0, code_name="ARGENTINA", name=f"Player {n}") for n in range(1, 50)]
    out = tmp_path / "wrap.pdf"
    result = generate_missing_pdf(col, cards, out, mode=ListReportMode.FULL)
    assert out.exists()
    assert result.pages >= 1


# ----------------------------------------------------------------------
# Owned
# ----------------------------------------------------------------------


def test_owned_pdf_only_includes_quantity_gte_1(tmp_path):
    col = _collection()
    cards = [
        _ac("ARG", 1, qty=0),
        _ac("ARG", 2, qty=1),
        _ac("ARG", 3, qty=5),
    ]
    out = tmp_path / "owned.pdf"
    generate_owned_pdf(col, cards, out)
    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert {c["card_number"] for c in meta["cards"]} == {2, 3}


# ----------------------------------------------------------------------
# Metadata de intercambio
# ----------------------------------------------------------------------


def test_exchange_metadata_roundtrip(tmp_path):
    """Generar PDF de faltantes → validate retorna metadata coherente."""
    col = _collection(name="WC2026", cid=42)
    cards = [_ac("ARG", 1, qty=0), _ac("BRA", 5, qty=0)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)

    meta = validate_exchange_pdf_metadata(out)
    assert meta is not None
    assert meta["app"] == EXCHANGE_APP_NAME
    assert meta["subtype"] == "missing"
    assert meta["collection_id"] == 42
    assert meta["collection_name"] == "WC2026"
    assert "checksum" in meta
    assert len(meta["checksum"]) == 16
    assert "generated_at" in meta


def test_exchange_metadata_tampered_checksum_fails(tmp_path):
    """Si modificamos los Keywords del PDF, validate retorna None."""
    col = _collection()
    cards = [_ac("ARG", 1, qty=0)]
    out = tmp_path / "missing.pdf"
    generate_missing_pdf(col, cards, out)

    # Reescribir el PDF con Keywords manipulados
    reader = PdfReader(str(out))
    writer = PdfWriter(clone_from=reader)
    bad_data = json.loads(reader.metadata["/Keywords"])
    bad_data["cards"].append({"code_id": "FAKE", "card_number": 999, "quantity": 0})
    writer.add_metadata({"/Keywords": json.dumps(bad_data)})
    tampered = tmp_path / "tampered.pdf"
    with open(tampered, "wb") as fp:
        writer.write(fp)

    assert validate_exchange_pdf_metadata(tampered) is None


def test_exchange_metadata_unrelated_pdf_returns_none(tmp_path):
    """Un PDF cualquiera (sin metadata de CollectionsApp) → None."""
    plain = tmp_path / "plain.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    with open(plain, "wb") as fp:
        writer.write(fp)
    assert validate_exchange_pdf_metadata(plain) is None


def test_build_exchange_metadata_includes_required_keys():
    raw = _build_exchange_metadata(
        subtype="missing",
        collection_id=1,
        collection_name="X",
        cards=[{"code_id": "ARG", "card_number": 5, "quantity": 0}],
    )
    data = json.loads(raw)
    assert data["app"] == EXCHANGE_APP_NAME
    assert data["subtype"] == "missing"
    assert data["cards"][0]["card_number"] == 5
    assert "checksum" in data
    # Generated_at no participa en el checksum: dos invocaciones tienen el
    # mismo checksum incluso en distinto microsegundo.
    raw2 = _build_exchange_metadata(
        subtype="missing",
        collection_id=1,
        collection_name="X",
        cards=[{"code_id": "ARG", "card_number": 5, "quantity": 0}],
    )
    assert json.loads(raw2)["checksum"] == data["checksum"]
```

### [tests/core/services/test_profile_service.py](tests/core/services/test_profile_service.py)

```python
"""Tests del ProfileService: detección de perfiles + import_structure."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import (
    Card,
    CodeHeader,
    Collection,
    InventoryItem,
    OperationType,
    Transaction,
)
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
    InventoryRepository,
    TransactionsRepository,
)
from collections_app.core.services.profile_service import (
    _STRUCTURE_TABLES,
    ProfileService,
)
from collections_app.core.utils import paths
from collections_app.core.utils.datetime_helpers import utc_now

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _new_db(path: Path) -> sqlite3.Connection:
    """Crea una DB SQLite migrada al schema actual en `path`."""
    conn = create_connection(path)
    run_migrations(conn)
    conn.commit()
    return conn


def _populate_source(conn: sqlite3.Connection) -> tuple[int, int]:
    """Inserta 2 colecciones, 1 header con 2 lines, 5 cards.

    Devuelve (cantidad_colecciones, cantidad_cards) para asserts.
    """
    hdr = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name="FIFA", code_max_length=5)
    )
    hid = hdr.code_header_id

    from collections_app.core.models import CodeLine
    from collections_app.core.repositories import CodesLinesRepository

    lines_repo = CodesLinesRepository(conn)
    lines_repo.upsert(CodeLine(hid, "ARG", "Argentina"))
    lines_repo.upsert(CodeLine(hid, "BRA", "Brazil"))

    col_repo = CollectionsRepository(conn)
    col1 = col_repo.create(
        Collection(
            collection_id=None,
            collection_name="WC 2026",
            card_count=3,
            requires_code=True,
            code_field_name="País",
            code_header_id=hid,
        )
    )
    col2 = col_repo.create(
        Collection(
            collection_id=None,
            collection_name="Stickers",
            card_count=2,
            requires_code=True,
            code_field_name="Set",
            code_header_id=hid,
        )
    )

    cards_repo = CardsRepository(conn)
    cards_repo.bulk_upsert(
        [
            Card(col1.collection_id, "ARG", 1, "Messi"),
            Card(col1.collection_id, "ARG", 2, "Martínez"),
            Card(col1.collection_id, "BRA", 1, "Vinícius"),
            Card(col2.collection_id, "ARG", 1, "Sticker A"),
            Card(col2.collection_id, "BRA", 1, "Sticker B"),
        ]
    )
    conn.commit()
    return 2, 5


# ----------------------------------------------------------------------
# import_structure
# ----------------------------------------------------------------------


def test_import_structure_copies_collections(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    n_cols, _ = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    count = ProfileService.import_structure(src_path, tgt)
    assert count == n_cols
    assert len(CollectionsRepository(tgt).list_all()) == n_cols
    tgt.close()


def test_import_structure_copies_cards(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _, n_cards = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # Sumar cards de todas las colecciones del target
    cards_repo = CardsRepository(tgt)
    total = sum(
        len(cards_repo.list_by_collection(c.collection_id))
        for c in CollectionsRepository(tgt).list_all()
    )
    assert total == n_cards
    tgt.close()


def test_import_structure_skips_inventory(tmp_path):
    """Inventario en source con qty>0 NO se copia al target."""
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _populate_source(src)
    # Cargar 1 unidad en cada colección (card_number=1 existe en ambas).
    for col in CollectionsRepository(src).list_all():
        InventoryRepository(src).upsert(InventoryItem(col.collection_id, "ARG", 1, quantity=5))
    src.commit()
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # En target NO debe haber items con quantity > 0 en NINGUNA colección
    for col in CollectionsRepository(tgt).list_all():
        owned = InventoryRepository(tgt).list_owned(col.collection_id)
        assert owned == []
    tgt.close()


def test_import_structure_skips_transactions(tmp_path):
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    _populate_source(src)
    cid = CollectionsRepository(src).list_all()[0].collection_id
    tx_repo = TransactionsRepository(src)
    for _ in range(3):
        tx_repo.log(
            Transaction(
                transaction_id=None,
                collection_id=cid,
                code_id="ARG",
                card_number=1,
                operation=OperationType.ALTA,
                quantity=1,
                transaction_date=utc_now(),
            )
        )
    src.commit()
    src.close()

    tgt = _new_db(tgt_path)
    ProfileService.import_structure(src_path, tgt)
    # En target NO debe haber transactions
    row = tgt.execute("SELECT COUNT(*) FROM transactions").fetchone()
    assert row[0] == 0
    tgt.close()


def test_import_structure_is_idempotent(tmp_path):
    """Correr import dos veces no duplica nada (INSERT OR IGNORE)."""
    src_path = tmp_path / "source.db"
    tgt_path = tmp_path / "target.db"
    src = _new_db(src_path)
    n_cols, n_cards = _populate_source(src)
    src.close()

    tgt = _new_db(tgt_path)
    first = ProfileService.import_structure(src_path, tgt)
    second = ProfileService.import_structure(src_path, tgt)
    assert first == n_cols
    assert second == n_cols  # mismo count, no duplicó
    cards_repo = CardsRepository(tgt)
    total = sum(
        len(cards_repo.list_by_collection(c.collection_id))
        for c in CollectionsRepository(tgt).list_all()
    )
    assert total == n_cards
    tgt.close()


def test_structure_tables_constant_excludes_user_data():
    """Sanity: la lista de tablas a copiar NO incluye inventory ni transactions."""
    assert "inventory" not in _STRUCTURE_TABLES
    assert "transactions" not in _STRUCTURE_TABLES


# ----------------------------------------------------------------------
# get_all_profiles
# ----------------------------------------------------------------------


@pytest.fixture
def isolated_app_data(monkeypatch, tmp_path):
    """Apunta APPDATA a tmp_path y restaura el perfil al final."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    monkeypatch.setattr(paths.sys, "platform", "win32")
    yield tmp_path / "Collections"
    paths.set_active_profile("default")


def test_get_all_profiles_finds_default(isolated_app_data):
    base = isolated_app_data
    base.mkdir(parents=True, exist_ok=True)
    # Crear DB en la raíz (perfil default)
    conn = _new_db(base / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "default" in names


def test_get_all_profiles_finds_subdirectories(isolated_app_data):
    base = isolated_app_data
    (base / "personal").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "personal" / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "personal" in names


def test_get_all_profiles_ignores_dirs_without_db(isolated_app_data):
    base = isolated_app_data
    (base / "empty_dir").mkdir(parents=True, exist_ok=True)
    # Sin collections.db dentro

    profiles = ProfileService.get_all_profiles()
    names = [p.name for p in profiles]
    assert "empty_dir" not in names


def test_profile_info_reads_collection_count(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)  # 2 colecciones
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.collection_count == 2


def test_profile_info_detects_inventory(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)
    cid = CollectionsRepository(conn).list_all()[0].collection_id
    InventoryRepository(conn).upsert(InventoryItem(cid, "ARG", 1, quantity=5))
    conn.commit()
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.has_inventory is True


def test_profile_info_no_inventory(isolated_app_data):
    base = isolated_app_data
    (base / "test").mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "test" / "collections.db")
    _populate_source(conn)
    conn.close()

    profiles = ProfileService.get_all_profiles()
    test_profile = next(p for p in profiles if p.name == "test")
    assert test_profile.has_inventory is False


def test_default_profile_display_name_is_principal(isolated_app_data):
    base = isolated_app_data
    base.mkdir(parents=True, exist_ok=True)
    conn = _new_db(base / "collections.db")
    conn.close()

    profiles = ProfileService.get_all_profiles()
    default = next(p for p in profiles if p.name == "default")
    assert default.display_name == "Principal"
```

### [tests/core/services/test_reports_service.py](tests/core/services/test_reports_service.py)

```python
"""Tests del ReportsService."""

from datetime import UTC, timedelta

from collections_app.core.models import OperationType
from collections_app.core.services import (
    InventoryService,
    ReportsService,
)
from collections_app.core.utils.datetime_helpers import utc_now


def _add_some_cards(memory_db, collection_id: int) -> None:
    svc = InventoryService(memory_db)
    svc.add_card(collection_id, "ARG", 1, 1)
    svc.add_card(collection_id, "ARG", 2, 1)
    svc.add_card(collection_id, "BRA", 1, 2)
    svc.remove_card(collection_id, "BRA", 1, 1)


def test_get_transactions_in_period_returns_card_info(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    # 4 movimientos: 3 altas + 1 baja
    assert len(rows) == 4
    # Cada uno trae el card_name del JOIN
    by_card = {(r.code_id, r.card_number): r for r in rows}
    assert by_card[("ARG", 1)].card_name == "Lionel Messi"
    assert by_card[("BRA", 1)].card_name == "Vinícius Jr."


def test_get_transactions_in_period_filters_by_date(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    # Un rango futuro no debería tener nada
    future = utc_now() + timedelta(hours=1)
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id, future, future + timedelta(hours=1)
    )
    assert rows == []


def test_get_transactions_in_period_filters_by_operation(
    memory_db, sample_cards, sample_collection
):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    altas = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
        operation=OperationType.ALTA,
    )
    bajas = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
        operation=OperationType.BAJA,
    )
    assert len(altas) == 3
    assert len(bajas) == 1
    assert all(t.operation == OperationType.ALTA for t in altas)
    assert all(t.operation == OperationType.BAJA for t in bajas)


def test_empty_period_returns_empty_list(memory_db, sample_collection):
    svc = ReportsService(memory_db)
    now = utc_now()
    assert (
        svc.get_transactions_in_period(
            sample_collection.collection_id,
            now - timedelta(minutes=1),
            now + timedelta(minutes=1),
        )
        == []
    )


def test_transactions_have_utc_tzinfo(memory_db, sample_cards, sample_collection):
    """Las fechas devueltas son siempre UTC."""

    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    assert rows
    for r in rows:
        assert r.transaction_date.tzinfo is UTC


def test_transactions_ordered_by_date_desc(memory_db, sample_cards, sample_collection):
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    # Los más recientes (la baja final) primero
    assert rows[0].operation == OperationType.BAJA


def test_only_collection_transactions(memory_db, sample_cards, sample_collection):
    """Verifica que el filtro por collection_id funciona."""
    _add_some_cards(memory_db, sample_collection.collection_id)
    svc = ReportsService(memory_db)
    now = utc_now()
    other = svc.get_transactions_in_period(
        9999, now - timedelta(minutes=1), now + timedelta(minutes=1)
    )
    assert other == []


def test_card_name_empty_when_card_deleted(memory_db, sample_cards, sample_collection):
    """Si la card fue borrada del catálogo, el reporte sigue funcionando."""
    from collections_app.core.repositories import CardsRepository

    _add_some_cards(memory_db, sample_collection.collection_id)
    # Borrar la card del catálogo (las transactions sobreviven)
    CardsRepository(memory_db).delete(sample_collection.collection_id, "ARG", 1)
    memory_db.commit()

    svc = ReportsService(memory_db)
    now = utc_now()
    rows = svc.get_transactions_in_period(
        sample_collection.collection_id,
        now - timedelta(minutes=1),
        now + timedelta(minutes=1),
    )
    arg_1 = next((r for r in rows if r.code_id == "ARG" and r.card_number == 1), None)
    assert arg_1 is not None
    assert arg_1.card_name == ""
```

### [tests/core/services/test_settings_service.py](tests/core/services/test_settings_service.py)

```python
"""Tests del SettingsService."""

from collections_app.core.services import SettingsService


def test_get_active_collection_id_when_unset(memory_db):
    svc = SettingsService(memory_db)
    assert svc.get_active_collection_id() is None


def test_set_and_get_active_collection_id(memory_db):
    svc = SettingsService(memory_db)
    svc.set_active_collection(42)
    assert svc.get_active_collection_id() == 42


def test_clear_active_collection(memory_db):
    svc = SettingsService(memory_db)
    svc.set_active_collection(42)
    svc.clear_active_collection()
    assert svc.get_active_collection_id() is None


def test_get_active_collection_returns_none_when_unset(memory_db):
    svc = SettingsService(memory_db)
    assert svc.get_active_collection() is None


def test_get_active_collection_returns_full_object(memory_db, sample_collection):
    svc = SettingsService(memory_db)
    svc.set_active_collection(sample_collection.collection_id)
    found = svc.get_active_collection()
    assert found is not None
    assert found.collection_id == sample_collection.collection_id


def test_get_active_collection_handles_stale_id(memory_db):
    """Si el setting apunta a un id inexistente, retorna None sin romper."""
    svc = SettingsService(memory_db)
    svc.set_active_collection(9999)
    assert svc.get_active_collection() is None
```

### [tests/core/services/test_update_service.py](tests/core/services/test_update_service.py)

```python
"""Tests del UpdateService y sus UpdateSources."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from collections_app.core.services.update_service import (
    GitHubUpdateSource,
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
    """Crea un mock de requests.Response con el status y JSON dados."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


def _release_payload(
    tag: str = "v1.1.0",
    html_url: str = "https://github.com/x/y/releases/tag/v1.1.0",
    body: str = "Notas del release",
    exe_url: str | None = "https://example.com/app.exe",
) -> dict:
    """Construye un payload tipo GitHub Releases para los tests."""
    assets = []
    if exe_url is not None:
        assets.append({"name": "collections-client.exe", "browser_download_url": exe_url})
    return {"tag_name": tag, "html_url": html_url, "body": body, "assets": assets}


# ----------------------------------------------------------------------
# GitHubUpdateSource
# ----------------------------------------------------------------------


def test_github_source_returns_dict_on_success():
    """fetch_latest retorna el JSON parseado cuando HTTP 200."""
    payload = _release_payload()
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        result = GitHubUpdateSource("http://x").fetch_latest()
    assert result == payload


def test_github_source_returns_none_on_http_error():
    """HTTP 404/500/etc → None sin excepción."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404)
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_returns_none_on_connection_error():
    """ConnectionError → None (sin red, host no resuelve)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("no route to host")
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_returns_none_on_timeout():
    """Timeout → None (la red está pero GitHub no responde a tiempo)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("read timeout")
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_sends_user_agent_and_accept_headers():
    """Sanity: la API de GitHub requiere User-Agent y Accept conocidos."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        GitHubUpdateSource("http://x").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["User-Agent"] == "CollectionsApp"
    assert headers["Accept"] == "application/vnd.github+json"


# ----------------------------------------------------------------------
# ServerUpdateSource
# ----------------------------------------------------------------------


def test_server_source_sends_bearer_token():
    """Si hay api_key, manda header Authorization: Bearer <token>."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv", api_key="mytoken").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer mytoken"


def test_server_source_no_token_no_auth_header():
    """Sin api_key NO se manda Authorization (servidor podría rechazarlo)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv", api_key="").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert "Authorization" not in headers


def test_server_source_appends_endpoint_path():
    """La URL final debe ser <server_url>/api/v1/updates/latest."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv/", api_key="").fetch_latest()
    assert mock_get.call_args.args[0] == "https://srv/api/v1/updates/latest"


def test_server_source_returns_none_on_http_error():
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(401)
        assert ServerUpdateSource("https://srv").fetch_latest() is None


def test_server_source_returns_none_on_exception():
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("nope")
        assert ServerUpdateSource("https://srv").fetch_latest() is None


# ----------------------------------------------------------------------
# Protocol satisfaction
# ----------------------------------------------------------------------


def test_update_source_protocol_satisfied_by_implementations():
    """Las dos implementaciones cumplen el Protocol UpdateSource (runtime check)."""
    assert isinstance(GitHubUpdateSource("http://x"), UpdateSource)
    assert isinstance(ServerUpdateSource("http://x"), UpdateSource)


# ----------------------------------------------------------------------
# UpdateService — composición e inyección
# ----------------------------------------------------------------------


class _FakeSource:
    """UpdateSource stub para tests: retorna lo que se le configura."""

    def __init__(self, payload: dict | None) -> None:
        self.payload = payload
        self.calls = 0

    def fetch_latest(self) -> dict | None:
        self.calls += 1
        return self.payload


def test_update_service_uses_injected_source():
    """UpdateService.check_for_updates() consulta la fuente inyectada (no requests reales)."""
    fake = _FakeSource(_release_payload(tag="v2.0.0"))
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        result = UpdateService(source=fake).check_for_updates()
    assert fake.calls == 1
    mock_get.assert_not_called()
    assert result is not None
    assert result.latest_version == "2.0.0"


def test_check_returns_none_when_source_returns_none():
    """Sin red / fuente caída: check_for_updates retorna None."""
    assert UpdateService(source=_FakeSource(None)).check_for_updates() is None


def test_check_returns_none_when_tag_missing():
    """Payload sin tag_name → None (no podemos comparar versions)."""
    fake = _FakeSource({"html_url": "x", "body": "y", "assets": []})
    assert UpdateService(source=fake).check_for_updates() is None


def test_check_returns_none_when_tag_invalid():
    """tag_name no parseable como Version → None."""
    fake = _FakeSource(_release_payload(tag="not-a-version"))
    assert UpdateService(source=fake).check_for_updates() is None


# ----------------------------------------------------------------------
# UpdateService — comparación de versiones
# ----------------------------------------------------------------------


def _patch_current(version: str):
    """Helper: parchea __version__ tal como lo lee update_service."""
    return patch("collections_app.core.services.update_service.__version__", version)


def test_check_returns_is_newer_true():
    fake = _FakeSource(_release_payload(tag="v1.1.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is True
    assert info.current_version == "1.0.0"
    assert info.latest_version == "1.1.0"


def test_check_returns_is_newer_false_same_version():
    fake = _FakeSource(_release_payload(tag="v1.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is False


def test_check_returns_is_newer_false_older():
    """Si lo "último" del servidor es viejo, no es nueva."""
    fake = _FakeSource(_release_payload(tag="v0.9.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is False


def test_version_semver_comparison_not_lexicographic():
    """Regresión: '1.10.0' > '1.9.0' (string comparison sería al revés)."""
    fake = _FakeSource(_release_payload(tag="v1.10.0"))
    with _patch_current("1.9.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is True


def test_tag_v_prefix_stripped():
    """tag_name='v2.0.0' → latest_version='2.0.0'."""
    fake = _FakeSource(_release_payload(tag="v2.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.latest_version == "2.0.0"


def test_tag_without_v_prefix_also_works():
    """tag_name sin 'v' debe funcionar igual."""
    fake = _FakeSource(_release_payload(tag="2.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.latest_version == "2.0.0"


# ----------------------------------------------------------------------
# UpdateService — selección de download_url
# ----------------------------------------------------------------------


def test_exe_asset_url_preferred():
    """Si hay un .exe entre los assets, usar su browser_download_url."""
    fake = _FakeSource(_release_payload(tag="v1.1.0", exe_url="https://example.com/app.exe"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.download_url == "https://example.com/app.exe"


def test_no_exe_asset_falls_back_to_html_url():
    """Sin .exe en assets, download_url == release_url (página HTML)."""
    fake = _FakeSource(
        _release_payload(tag="v1.1.0", html_url="https://github.com/x/y/r/v1", exe_url=None)
    )
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.download_url == info.release_url
    assert info.download_url == "https://github.com/x/y/r/v1"


def test_release_notes_truncated_to_500_chars():
    """Notas largas se cortan a 500 chars (banner / about no necesitan más)."""
    long_body = "a" * 1000
    fake = _FakeSource(_release_payload(tag="v1.1.0", body=long_body))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert len(info.release_notes) == 500


# ----------------------------------------------------------------------
# UpdateInfo dataclass
# ----------------------------------------------------------------------


def test_update_info_is_frozen():
    """UpdateInfo es @dataclass(frozen=True): no se puede mutar."""
    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="x",
        release_url="y",
        release_notes="z",
        is_newer=True,
    )
    from dataclasses import FrozenInstanceError

    with pytest.raises(FrozenInstanceError):
        info.is_newer = False  # type: ignore[misc]
```

### [tests/core/utils/__init__.py](tests/core/utils/__init__.py)

_(archivo vacío)_

### [tests/core/utils/test_datetime_helpers.py](tests/core/utils/test_datetime_helpers.py)

```python
"""Tests de datetime_helpers."""

from datetime import UTC, datetime, timedelta, timezone

from collections_app.core.utils.datetime_helpers import (
    format_for_db,
    format_for_display,
    parse_db_datetime,
    to_local,
    utc_now,
)


def test_utc_now_has_utc_tzinfo():
    now = utc_now()
    assert now.tzinfo is UTC


def test_utc_now_is_close_to_real_now():
    now = utc_now()
    real = datetime.now(UTC)
    assert abs((real - now).total_seconds()) < 1


def test_to_local_converts_utc_to_local():
    utc_dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    local = to_local(utc_dt)
    # El resultado tiene tzinfo (no UTC necesariamente)
    assert local.tzinfo is not None
    # Debe representar el mismo instante
    assert local.timestamp() == utc_dt.timestamp()


def test_to_local_assumes_utc_for_naive():
    naive = datetime(2026, 4, 30, 18, 0)
    local = to_local(naive)
    # Mismo instante que naive interpretado como UTC
    expected_utc = naive.replace(tzinfo=UTC)
    assert local.timestamp() == expected_utc.timestamp()


def test_parse_db_datetime_returns_utc():
    dt = parse_db_datetime("2026-04-30 18:00:00")
    assert dt.tzinfo is UTC
    assert dt.year == 2026 and dt.hour == 18


def test_parse_db_datetime_accepts_iso():
    """Fallback para timestamps ISO (microsegundos)."""
    dt = parse_db_datetime("2026-04-30T18:00:00.123456")
    assert dt.tzinfo is UTC


def test_format_for_db_with_utc_datetime():
    dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    assert format_for_db(dt) == "2026-04-30 18:00:00"


def test_format_for_db_converts_local_to_utc():
    """Un datetime con tzinfo no-UTC se convierte antes de formatear."""
    # Forzar tzinfo +03:00 → 21:00 local equivale a 18:00 UTC
    tz_3 = timezone(timedelta(hours=3))
    dt = datetime(2026, 4, 30, 21, 0, tzinfo=tz_3)
    assert format_for_db(dt) == "2026-04-30 18:00:00"


def test_format_for_db_naive_is_treated_as_utc():
    naive = datetime(2026, 4, 30, 18, 0)
    assert format_for_db(naive) == "2026-04-30 18:00:00"


def test_format_for_display_uses_local_time():
    """Lo que sale es la hora del sistema; verificamos que el instante coincide."""
    utc_dt = datetime(2026, 4, 30, 18, 0, tzinfo=UTC)
    out = format_for_display(utc_dt)
    # Re-parsear lo formateado y comparar instantes
    local_dt = datetime.strptime(out, "%Y-%m-%d %H:%M").astimezone()
    # Diferencia menor a un minuto (formato sin segundos)
    assert abs(local_dt.timestamp() - utc_dt.timestamp()) < 60


def test_format_for_display_with_seconds():
    utc_dt = datetime(2026, 4, 30, 18, 5, 17, tzinfo=UTC)
    out = format_for_display(utc_dt, with_seconds=True)
    assert len(out) == len("2026-04-30 18:05:17")
```

### [tests/core/utils/test_paths.py](tests/core/utils/test_paths.py)

```python
"""Tests de los helpers de paths del módulo `core.utils.paths`."""

from collections_app.core.utils import paths


def _redirect_generated_cards_dir(monkeypatch, tmp_path):
    """Hace que get_generated_cards_dir apunte a tmp_path."""
    monkeypatch.setattr(paths, "get_generated_cards_dir", lambda: tmp_path)


# ----------------------------------------------------------------------
# format_card_filename
# ----------------------------------------------------------------------


def test_format_card_filename_default_extension():
    assert paths.format_card_filename(1) == "0001.jpg"
    assert paths.format_card_filename(42) == "0042.jpg"
    assert paths.format_card_filename(630) == "0630.jpg"


def test_format_card_filename_custom_extension():
    assert paths.format_card_filename(1, "png") == "0001.png"
    # Acepta extensión con o sin punto
    assert paths.format_card_filename(1, ".png") == "0001.png"
    assert paths.format_card_filename(1, "jpeg") == "0001.jpeg"


def test_format_card_filename_zero_padding_at_boundaries():
    assert paths.format_card_filename(9999) == "9999.jpg"
    # Si supera 4 dígitos, igual lo formatea sin truncar
    assert paths.format_card_filename(10000) == "10000.jpg"


# ----------------------------------------------------------------------
# get_card_image_path
# ----------------------------------------------------------------------


def test_get_card_image_path_constructs_full_path(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.get_card_image_path(1, 42) == tmp_path / "1" / "0042.jpg"


def test_get_card_image_path_respects_custom_extension(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.get_card_image_path(2, 5, "png") == tmp_path / "2" / "0005.png"


# ----------------------------------------------------------------------
# find_card_image
# ----------------------------------------------------------------------


def test_find_card_image_returns_existing_jpg(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    target = tmp_path / "1" / "0042.jpg"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == target


def test_find_card_image_prefers_jpg_over_png(tmp_path, monkeypatch):
    """Si conviven .jpg y .png, gana .jpg (orden de búsqueda)."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    folder = tmp_path / "1"
    folder.mkdir()
    jpg = folder / "0042.jpg"
    png = folder / "0042.png"
    jpg.write_bytes(b"x")
    png.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == jpg


def test_find_card_image_returns_none_when_missing(tmp_path, monkeypatch):
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    assert paths.find_card_image(1, 42) is None


def test_find_card_image_falls_back_to_png(tmp_path, monkeypatch):
    """Sin .jpg pero con .png → devuelve el .png."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    png = tmp_path / "1" / "0042.png"
    png.parent.mkdir(parents=True)
    png.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == png


def test_find_card_image_falls_back_to_jpeg(tmp_path, monkeypatch):
    """Sin .jpg ni .png pero con .jpeg → devuelve el .jpeg."""
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    jpeg = tmp_path / "1" / "0042.jpeg"
    jpeg.parent.mkdir(parents=True)
    jpeg.write_bytes(b"x")
    assert paths.find_card_image(1, 42) == jpeg


def test_find_card_image_does_not_match_legacy_unpadded(tmp_path, monkeypatch):
    """Un archivo legacy sin padding (`42.jpg`) NO se debe encontrar.

    Forzar a `find_card_image` a buscar SOLO con padding garantiza que el
    consumidor llame a `rename_legacy_cards` antes que confiar en magia.
    """
    _redirect_generated_cards_dir(monkeypatch, tmp_path)
    legacy = tmp_path / "1" / "42.jpg"
    legacy.parent.mkdir(parents=True)
    legacy.write_bytes(b"x")
    assert paths.find_card_image(1, 42) is None


# ----------------------------------------------------------------------
# _get_bundle_dir / get_schema_dir — detección de PyInstaller frozen
# ----------------------------------------------------------------------


def test_bundle_dir_returns_package_root_in_dev():
    """En desarrollo (sys.frozen ausente) apunta al paquete instalado."""
    bundle = paths._get_bundle_dir()
    # Debe ser la raíz de `collections_app/` — `core/utils/paths.py`
    # vive 2 niveles abajo, así que la subida nos lleva ahí.
    assert bundle.name == "collections_app"
    assert (bundle / "core" / "utils" / "paths.py").exists()


def test_get_schema_dir_returns_existing_directory_in_dev():
    """En dev, el schema_dir existe y tiene los .sql de migración."""
    schema = paths.get_schema_dir()
    assert schema.exists()
    sql_files = sorted(p.name for p in schema.glob("*.sql"))
    assert sql_files  # al menos uno
    assert all(name.endswith(".sql") for name in sql_files)


def test_bundle_dir_uses_meipass_when_frozen(monkeypatch, tmp_path):
    """Simulando sys.frozen + sys._MEIPASS, _get_bundle_dir() apunta ahí."""
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    bundle = paths._get_bundle_dir()
    assert bundle == tmp_path / "collections_app"


def test_get_schema_dir_uses_meipass_when_frozen(monkeypatch, tmp_path):
    """En modo frozen, get_schema_dir resuelve a _MEIPASS/.../schema."""
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    expected = tmp_path / "collections_app" / "core" / "db" / "schema"
    assert paths.get_schema_dir() == expected


def test_app_data_dir_does_not_depend_on_meipass(monkeypatch, tmp_path):
    """Datos del usuario (DB, escudos, cards) viven en %APPDATA%, NO en _MEIPASS.

    Si get_app_data_dir o las funciones que delegan en él dependieran de
    _MEIPASS, los datos se perderían cada vez que el bootloader recreara
    la carpeta temp. Este test garantiza esa separación.
    """
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)

    app_dir = paths.get_app_data_dir()
    # No debe estar dentro de _MEIPASS
    assert tmp_path not in app_dir.parents
    assert app_dir != tmp_path


# ----------------------------------------------------------------------
# Perfiles de datos: set_active_profile / get_active_profile
# ----------------------------------------------------------------------


import pytest  # noqa: E402


@pytest.fixture(autouse=False)
def reset_profile_after_test():
    """Restaura el perfil a 'default' después del test (estado global)."""
    yield
    paths.set_active_profile("default")


def test_set_active_profile_sanitizes_input(reset_profile_after_test):
    """Caracteres no [a-zA-Z0-9-] se reemplazan por _."""
    paths.set_active_profile("Mi Perfil!")
    assert paths.get_active_profile() == "Mi_Perfil"
    paths.set_active_profile("with.dots/and:colons")
    assert paths.get_active_profile() == "with_dots_and_colons"


def test_set_active_profile_empty_falls_back_to_default(reset_profile_after_test):
    paths.set_active_profile("")
    assert paths.get_active_profile() == "default"
    paths.set_active_profile("   ")
    assert paths.get_active_profile() == "default"
    # También si quedan solo separadores tras sanitizar.
    paths.set_active_profile("!!!")
    assert paths.get_active_profile() == "default"


def test_set_active_profile_keeps_valid_chars(reset_profile_after_test):
    paths.set_active_profile("test-profile-2")
    assert paths.get_active_profile() == "test-profile-2"


def test_default_profile_uses_base_dir(monkeypatch, tmp_path, reset_profile_after_test):
    """default → APPDATA/Collections (sin subdirectorio extra)."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("default")
    app_dir = paths.get_app_data_dir()
    assert app_dir == tmp_path / "Collections"


def test_named_profile_uses_subdirectory(monkeypatch, tmp_path, reset_profile_after_test):
    """test → APPDATA/Collections/test."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("test")
    app_dir = paths.get_app_data_dir()
    assert app_dir == tmp_path / "Collections" / "test"


def test_get_database_path_includes_profile(monkeypatch, tmp_path, reset_profile_after_test):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("personal")
    db = paths.get_database_path()
    assert db == tmp_path / "Collections" / "personal" / "collections.db"


def test_profile_isolates_generated_cards_dir(monkeypatch, tmp_path, reset_profile_after_test):
    """Las imágenes derivan de get_app_data_dir → también heredan el perfil."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    paths.set_active_profile("test")
    cards_dir = paths.get_generated_cards_dir()
    assert cards_dir == tmp_path / "Collections" / "test" / "generated_cards"
```

### [tests/shared_ui/__init__.py](tests/shared_ui/__init__.py)

_(archivo vacío)_

### [tests/shared_ui/dialogs/__init__.py](tests/shared_ui/dialogs/__init__.py)

_(archivo vacío)_

### [tests/shared_ui/dialogs/test_settings_dialog.py](tests/shared_ui/dialogs/test_settings_dialog.py)

```python
"""Tests del SettingsDialog."""

from collections_app.core.models import Collection
from collections_app.core.repositories import CollectionsRepository
from collections_app.core.services import SettingsService
from collections_app.shared_ui.dialogs.settings_dialog import SettingsDialog


def _create_collections(memory_db, code_header_id: int) -> list[Collection]:
    repo = CollectionsRepository(memory_db)
    a = repo.create(Collection(None, "Alpha", 10, False, None, code_header_id))
    b = repo.create(Collection(None, "Beta", 20, False, None, code_header_id))
    memory_db.commit()
    return [a, b]


def test_dialog_lists_all_collections(qtbot, memory_db, sample_code_header):
    _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # Combo: 1 placeholder ("(ninguna)") + 2 colecciones
    assert dlg._combo.count() == 3
    labels = [dlg._combo.itemText(i) for i in range(dlg._combo.count())]
    assert "Alpha" in labels
    assert "Beta" in labels


def test_dialog_preselects_current_active(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    SettingsService(memory_db).set_active_collection(cols[1].collection_id)
    memory_db.commit()

    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    assert dlg._combo.currentData() == cols[1].collection_id


def test_accept_saves_setting(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)

    idx = dlg._combo.findData(cols[0].collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg._on_accept()

    assert dlg.selected_collection_id == cols[0].collection_id
    assert SettingsService(memory_db).get_active_collection_id() == cols[0].collection_id


def test_cancel_does_not_save_setting(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)

    idx = dlg._combo.findData(cols[0].collection_id)
    dlg._combo.setCurrentIndex(idx)
    dlg.reject()

    assert dlg.selected_collection_id is None
    assert SettingsService(memory_db).get_active_collection_id() is None


def test_dialog_with_no_collections(qtbot, memory_db):
    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    # Solo el placeholder "(ninguna)"
    assert dlg._combo.count() == 1
    assert dlg._combo.currentData() is None


def test_accepting_none_clears_active(qtbot, memory_db, sample_code_header):
    cols = _create_collections(memory_db, sample_code_header.code_header_id)
    SettingsService(memory_db).set_active_collection(cols[0].collection_id)
    memory_db.commit()

    dlg = SettingsDialog(memory_db)
    qtbot.addWidget(dlg)
    dlg._combo.setCurrentIndex(0)  # "(ninguna)"
    dlg._on_accept()

    assert SettingsService(memory_db).get_active_collection_id() is None
```

### [tests/shared_ui/widgets/__init__.py](tests/shared_ui/widgets/__init__.py)

_(archivo vacío)_

### [tests/shared_ui/widgets/test_abm_widget.py](tests/shared_ui/widgets/test_abm_widget.py)

```python
"""Tests del AbmWidget genérico."""

from dataclasses import dataclass

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QMessageBox

from collections_app.shared_ui.widgets.abm_widget import (
    AbmConfig,
    AbmWidget,
    FieldDef,
    FieldType,
)

# ----------------------------------------------------------------------
# Modelos y store de prueba
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class FakeItem:
    """Modelo de prueba con PK auto-id."""

    item_id: int | None
    name: str
    quantity: int = 0


@dataclass(frozen=True)
class FakeCode:
    """Modelo de prueba con PK significativa de texto."""

    code_id: str
    code_name: str


class FakeStore:
    """Store en memoria para simular un repository."""

    def __init__(self) -> None:
        self.items: list[FakeItem] = []
        self._next_id = 1

    def list_all(self) -> list[FakeItem]:
        return list(self.items)

    def save(self, item: FakeItem) -> FakeItem:
        if item.item_id is None:
            saved = FakeItem(item_id=self._next_id, name=item.name, quantity=item.quantity)
            self._next_id += 1
            self.items.append(saved)
            return saved
        self.items = [it if it.item_id != item.item_id else item for it in self.items]
        return item

    def delete(self, item: FakeItem) -> bool:
        before = len(self.items)
        self.items = [it for it in self.items if it.item_id != item.item_id]
        return len(self.items) < before


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


def _build_item_config(store: FakeStore) -> AbmConfig:
    return AbmConfig(
        title="Items",
        module_code="ITM001",
        fields=[
            FieldDef(
                name="item_id",
                label="ID",
                field_type=FieldType.READONLY,
                is_id=True,
                is_required=False,
            ),
            FieldDef(name="name", label="Nombre", field_type=FieldType.TEXT),
            FieldDef(
                name="quantity",
                label="Cantidad",
                field_type=FieldType.INT,
                is_required=False,
            ),
        ],
        on_load_all=store.list_all,
        on_save=store.save,
        on_delete=store.delete,
        model_class=FakeItem,
        filter_field="name",
    )


def _build_code_config(store: list[FakeCode]) -> AbmConfig:
    return AbmConfig(
        title="Códigos",
        module_code="COD001",
        fields=[
            FieldDef(
                name="code_id",
                label="Código",
                field_type=FieldType.TEXT,
                is_id=True,
                max_length=3,
            ),
            FieldDef(name="code_name", label="Nombre", field_type=FieldType.TEXT),
        ],
        on_load_all=lambda: list(store),
        on_save=lambda c: store.append(c) or c,
        on_delete=lambda c: bool(store.remove(c)) or True,  # noqa: SIM222
        model_class=FakeCode,
    )


@pytest.fixture
def store() -> FakeStore:
    return FakeStore()


@pytest.fixture
def widget(qtbot, store):
    config = _build_item_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()
    qtbot.waitExposed(w)
    return w


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------


def test_abm_loads_records_into_grid(qtbot, store):
    store.save(FakeItem(None, "alpha", 1))
    store.save(FakeItem(None, "beta", 2))
    config = _build_item_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    assert w._grid_model.rowCount() == 2


def test_clicking_row_populates_form(qtbot, store, widget):
    store.save(FakeItem(None, "first", 5))
    widget.refresh()

    proxy_index = widget._proxy_model.index(0, 0)
    widget._grid_view.clicked.emit(proxy_index)

    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    assert name_input.text() == "first"


def test_save_new_record_appears_in_grid(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("nuevo")

    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1
    assert store.items[0].name == "nuevo"
    assert widget._grid_model.rowCount() == 1


def test_save_existing_record_updates_grid(qtbot, store, widget):
    saved = store.save(FakeItem(None, "old", 0))
    widget.refresh()

    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("updated")
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1
    assert store.items[0].name == "updated"
    assert store.items[0].item_id == saved.item_id


def test_filter_filters_grid_in_realtime(qtbot, store, widget):
    for n in ("apple", "banana", "apricot"):
        store.save(FakeItem(None, n, 0))
    widget.refresh()
    assert widget._proxy_model.rowCount() == 3

    widget._filter_input.setText("ap")
    assert widget._proxy_model.rowCount() == 2


def test_pk_field_is_readonly_when_editing_significant_id(qtbot):
    codes: list[FakeCode] = []
    config = _build_code_config(codes)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    codes.append(FakeCode("ARG", "Argentina"))
    w.refresh()
    w._grid_view.clicked.emit(w._proxy_model.index(0, 0))

    code_input = w._inputs["code_id"]
    assert isinstance(code_input, QLineEdit)
    assert code_input.isReadOnly() is True


def test_pk_field_is_editable_when_creating_significant_id(qtbot):
    codes: list[FakeCode] = []
    config = _build_code_config(codes)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    code_input = w._inputs["code_id"]
    assert isinstance(code_input, QLineEdit)
    assert code_input.isReadOnly() is False


def test_validation_failure_shows_status_message(qtbot, store):
    config = _build_item_config(store)
    config.on_validate = lambda _: (False, "razón inválida")
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    name_input = w._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("xx")
    qtbot.mouseClick(w._save_button, Qt.MouseButton.LeftButton)

    assert "razón inválida" in w._status_label.text()
    assert store.items == []  # no se guardó


def test_required_field_empty_blocks_save(qtbot, store, widget):
    # name está vacío y es required
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)
    assert "obligatorio" in widget._status_label.text().lower()
    assert store.items == []


def test_delete_with_confirmation_yes(qtbot, store, widget, monkeypatch):
    saved = store.save(FakeItem(None, "to_delete", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes)
    qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)

    assert saved not in store.items
    assert widget._grid_model.rowCount() == 0


def test_delete_with_confirmation_no(qtbot, store, widget, monkeypatch):
    store.save(FakeItem(None, "stay", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.No)
    qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1


def test_enter_in_last_field_focuses_save_button(qtbot, store, widget):
    name_input = widget._inputs["name"]
    quantity_input = widget._inputs["quantity"]

    name_input.setFocus()
    qtbot.keyClick(name_input, Qt.Key.Key_Return)
    assert quantity_input.hasFocus()

    qtbot.keyClick(quantity_input, Qt.Key.Key_Return)
    assert widget._save_button.hasFocus()


def test_record_saved_signal_emitted(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("emit-test")

    with qtbot.waitSignal(widget.record_saved, timeout=1000) as blocker:
        qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)
    saved = blocker.args[0]
    assert saved.name == "emit-test"
    assert saved.item_id is not None


def test_record_deleted_signal_emitted(qtbot, store, widget, monkeypatch):
    store.save(FakeItem(None, "del-emit", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes)
    with qtbot.waitSignal(widget.record_deleted, timeout=1000) as blocker:
        qtbot.mouseClick(widget._delete_button, Qt.MouseButton.LeftButton)
    deleted = blocker.args[0]
    assert deleted.name == "del-emit"


def test_clear_form_resets_inputs(qtbot, store, widget):
    name_input = widget._inputs["name"]
    assert isinstance(name_input, QLineEdit)
    name_input.setText("dirty")
    widget.clear_form()
    assert name_input.text() == ""
    assert widget._current_record is None


def test_new_button_clears_form(qtbot, store, widget):
    store.save(FakeItem(None, "first", 0))
    widget.refresh()
    widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))
    assert widget._current_record is not None
    qtbot.mouseClick(widget._new_button, Qt.MouseButton.LeftButton)
    assert widget._current_record is None


def test_grid_selection_changed_emits_with_model(qtbot, store, widget):
    saved = store.save(FakeItem(None, "selectable", 0))
    widget.refresh()

    with qtbot.waitSignal(widget.grid_selection_changed, timeout=1000) as blocker:
        widget._grid_view.selectRow(0)
    received = blocker.args[0]
    assert received.item_id == saved.item_id


# --------------------------------------------------------------------
# Multi-PK readonly al editar (PK compuesta)
# --------------------------------------------------------------------


@dataclass(frozen=True)
class FakeComposite:
    """Modelo con PK compuesta (code + número)."""

    code_id: str
    number: int
    name: str


def _build_composite_config(store: list[FakeComposite]) -> AbmConfig:
    return AbmConfig(
        title="Composite",
        module_code="CMP001",
        fields=[
            FieldDef(
                name="code_id",
                label="Code",
                field_type=FieldType.COMBO,
                is_id=True,
                combo_choices=[("ARG", "ARG"), ("BRA", "BRA")],
            ),
            FieldDef(name="number", label="Num", field_type=FieldType.INT, is_id=True),
            FieldDef(name="name", label="Nombre", field_type=FieldType.TEXT),
        ],
        on_load_all=lambda: list(store),
        on_save=lambda c: store.append(c) or c,
        on_delete=lambda c: bool(store.remove(c)) or True,  # noqa: SIM222
        model_class=FakeComposite,
    )


def test_composite_pk_all_readonly_when_editing(qtbot):
    store: list[FakeComposite] = []
    config = _build_composite_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    store.append(FakeComposite("ARG", 1, "Messi"))
    w.refresh()
    w._grid_view.clicked.emit(w._proxy_model.index(0, 0))

    code_combo = w._inputs["code_id"]
    number_spin = w._inputs["number"]
    name_edit = w._inputs["name"]
    # COMBO: deshabilitado al editar
    assert code_combo.isEnabled() is False
    # INT: readonly al editar
    assert number_spin.isReadOnly() is True
    # Campo no-id: editable
    from PySide6.QtWidgets import QLineEdit  # noqa: PLC0415

    assert isinstance(name_edit, QLineEdit)
    assert name_edit.isReadOnly() is False


def test_composite_pk_all_editable_when_creating(qtbot):
    store: list[FakeComposite] = []
    config = _build_composite_config(store)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    code_combo = w._inputs["code_id"]
    number_spin = w._inputs["number"]
    assert code_combo.isEnabled() is True
    assert number_spin.isReadOnly() is False


# --------------------------------------------------------------------
# combo_choices callable + refresh_combo_choices
# --------------------------------------------------------------------


@dataclass(frozen=True)
class FakeWithCombo:
    item_id: int | None
    name: str
    code: str | None = None


def _build_combo_config(
    store: list[FakeWithCombo],
    choices_provider,
) -> AbmConfig:
    return AbmConfig(
        title="With Combo",
        module_code="WC001",
        fields=[
            FieldDef(
                "item_id",
                "ID",
                FieldType.READONLY,
                is_id=True,
                is_required=False,
            ),
            FieldDef("name", "Nombre", FieldType.TEXT),
            FieldDef(
                "code",
                "Code",
                FieldType.COMBO,
                is_required=False,
                combo_choices=choices_provider,
            ),
        ],
        on_load_all=lambda: list(store),
        on_save=lambda c: store.append(c) or c,
        on_delete=lambda c: bool(store.remove(c)) or True,  # noqa: SIM222
        model_class=FakeWithCombo,
    )


def test_combo_choices_can_be_callable(qtbot):
    """`combo_choices` acepta una función y la llama al construir el widget."""
    calls: list[int] = []

    def provider() -> list[tuple[str, object]]:
        calls.append(1)
        return [("Argentina", "ARG"), ("Brasil", "BRA")]

    config = _build_combo_config([], provider)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    combo = w._inputs["code"]
    values = [combo.itemData(i) for i in range(combo.count())]
    assert set(values) == {"ARG", "BRA"}
    assert calls  # se llamó al menos una vez


def test_refresh_combo_choices_calls_callable_again(qtbot):
    """Al llamar refresh_combo_choices, el callable se re-evalúa."""
    state = {"choices": [("A", "a")]}

    def provider() -> list[tuple[str, object]]:
        return list(state["choices"])

    config = _build_combo_config([], provider)
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()
    assert w._inputs["code"].count() == 1

    state["choices"] = [("A", "a"), ("B", "b"), ("C", "c")]
    w.refresh_combo_choices()
    assert w._inputs["code"].count() == 3


def test_refresh_combo_preserves_current_selection(qtbot):
    """Si el valor seleccionado sigue existiendo, se mantiene seleccionado."""
    state = {"choices": [("A", "a"), ("B", "b")]}

    config = _build_combo_config([], lambda: list(state["choices"]))
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    combo = w._inputs["code"]
    combo.setCurrentIndex(combo.findData("b"))

    state["choices"] = [("A", "a"), ("B", "b"), ("C", "c")]
    w.refresh_combo_choices()
    assert combo.currentData() == "b"


def test_refresh_combo_drops_selection_when_value_gone(qtbot):
    """Si el valor seleccionado ya no está en los nuevos choices, queda en el primero."""
    state = {"choices": [("A", "a"), ("B", "b")]}

    config = _build_combo_config([], lambda: list(state["choices"]))
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    combo = w._inputs["code"]
    combo.setCurrentIndex(combo.findData("b"))

    state["choices"] = [("A", "a")]
    w.refresh_combo_choices()
    assert combo.currentData() == "a"


def test_new_clicked_refreshes_combos_first(qtbot):
    """Click en 'Nuevo' (clear_form) re-evalúa los callables antes de limpiar."""
    state = {"choices": [("A", "a")]}

    config = _build_combo_config([], lambda: list(state["choices"]))
    w = AbmWidget(config)
    qtbot.addWidget(w)
    w.show()

    state["choices"] = [("A", "a"), ("B", "b")]
    qtbot.mouseClick(w._new_button, Qt.MouseButton.LeftButton)
    assert w._inputs["code"].count() == 2
```

### [tests/shared_ui/widgets/test_enter_navigator.py](tests/shared_ui/widgets/test_enter_navigator.py)

```python
"""Tests del EnterNavigator."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QSpinBox, QWidget

from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator


@pytest.fixture
def parent_widget(qtbot):
    w = QWidget()
    qtbot.addWidget(w)
    return w


def _ensure_focus(qtbot, widget) -> None:
    """Setea foco y espera a que efectivamente lo tenga (resiliente a flakiness)."""
    widget.window().activateWindow()
    widget.window().raise_()
    widget.setFocus(Qt.FocusReason.OtherFocusReason)
    qtbot.waitUntil(widget.hasFocus, timeout=500)


def test_enter_advances_to_next_widget(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()

    _ensure_focus(qtbot, a)
    qtbot.keyClick(a, Qt.Key.Key_Return)
    assert b.hasFocus()


def test_enter_on_last_calls_callback(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    calls: list[bool] = []
    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.on_last_enter = lambda: calls.append(True)
    nav.install()

    _ensure_focus(qtbot, b)
    qtbot.keyClick(b, Qt.Key.Key_Return)
    assert calls == [True]


def test_navigator_with_combobox(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    combo = QComboBox(parent_widget)
    combo.addItems(["one", "two"])
    spin = QSpinBox(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, combo, spin])
    nav.install()

    _ensure_focus(qtbot, a)
    qtbot.keyClick(a, Qt.Key.Key_Return)
    assert combo.hasFocus()
    qtbot.keyClick(combo, Qt.Key.Key_Return)
    assert spin.hasFocus()


def test_navigator_handles_empty_chain(qtbot, parent_widget):
    nav = EnterNavigator(parent_widget)
    nav.set_chain([])
    nav.install()
    # No debe romper aunque no haya widgets en la cadena
    assert nav._installed is True


def test_navigator_uninstall_removes_filters(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()
    nav.uninstall()

    _ensure_focus(qtbot, a)
    qtbot.keyClick(a, Qt.Key.Key_Return)
    # Sin filter, Enter no salta a b
    assert not b.hasFocus()


def test_navigator_keypad_enter_also_works(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()

    _ensure_focus(qtbot, a)
    qtbot.keyClick(a, Qt.Key.Key_Enter)
    assert b.hasFocus()
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

- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `found_photo INTEGER NOT NULL DEFAULT 0`
- `image_source TEXT`
- `image_path TEXT`
- `generated_at TEXT`
- _PRIMARY KEY (collection_id, code_id, card_number)_

**Foreign keys:**
- `FOREIGN KEY (collection_id, code_id, card_number)
        REFERENCES cards(collection_id, code_id, card_number)
        ON DELETE CASCADE`

**Índices:** `idx_card_images_found`

### Tabla `cards`

- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `card_name TEXT NOT NULL`
- _PRIMARY KEY (collection_id, code_id, card_number)_

**Foreign keys:**
- `FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
        ON DELETE CASCADE`

**Índices:** `idx_cards_collection`

### Tabla `codes_headers`

- `code_header_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `code_header_name TEXT NOT NULL UNIQUE`
- `code_max_length INTEGER NOT NULL DEFAULT 5`

### Tabla `codes_lines`

- `code_header_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `code_name TEXT NOT NULL`
- `code_order INTEGER NOT NULL DEFAULT 0`
- _PRIMARY KEY (code_header_id, code_id)_

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
- `album_orientation TEXT NOT NULL DEFAULT 'portrait' CHECK (album_orientation IN ('portrait', 'landscape'))`

**Foreign keys:**
- `FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)`

### Tabla `inventory`

- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `quantity INTEGER NOT NULL DEFAULT 0`
- `image_path TEXT`
- `locked INTEGER NOT NULL DEFAULT 0`
- _PRIMARY KEY (collection_id, code_id, card_number)_

**Foreign keys:**
- `FOREIGN KEY (collection_id, code_id, card_number)
        REFERENCES cards(collection_id, code_id, card_number)
        ON DELETE CASCADE`

### Tabla `schema_version`

- `version INTEGER PRIMARY KEY`
- `applied_at TEXT NOT NULL DEFAULT (datetime('now'))`

### Tabla `transactions`

- `transaction_id INTEGER PRIMARY KEY AUTOINCREMENT`
- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `operation TEXT NOT NULL CHECK (operation IN ('alta', 'baja'))`
- `quantity INTEGER NOT NULL`
- `transaction_date TEXT NOT NULL DEFAULT (datetime('now'))`

**Foreign keys:**
- `FOREIGN KEY (collection_id) REFERENCES collections(collection_id)`

**Índices:** `idx_transactions_date`, `idx_transactions_collection`

## Modelos (dataclasses en `core/models/`)

### `Card` — [src/collections_app/core/models/card.py](src/collections_app/core/models/card.py)

> Card del catálogo (PK compuesta collection+code+number).

- `collection_id: int`
- `code_id: str`
- `card_number: int`
- `card_name: str`

**Métodos:**
- `card_key(self) -> str` — Identificador legible: CODE-NUM (ej: 'NON-24', 'MR-1').

### `CardImage` — [src/collections_app/core/models/card_image.py](src/collections_app/core/models/card_image.py)

> Registro de la imagen generada para una card.

- `collection_id: int`
- `code_id: str`
- `card_number: int`
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

> Línea de código asociada a un header (PK compuesta header+code).

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

### `ExchangeCard` — [src/collections_app/core/models/exchange.py](src/collections_app/core/models/exchange.py)

> Una carta dentro de un archivo de intercambio.

- `code_id: str`
- `card_number: int`
- `card_name: str`
- `quantity: int`

### `ExchangeFile` — [src/collections_app/core/models/exchange.py](src/collections_app/core/models/exchange.py)

> Contenido del archivo `.colexchange` generado por un usuario.

- `app: str`
- `version: str`
- `collection_id: int`
- `collection_name: str`
- `generated_at: str`
- `missing: list[ExchangeCard]`
- `duplicates: list[ExchangeCard]`
- `checksum: str`

### `ComparisonResult` — [src/collections_app/core/models/exchange.py](src/collections_app/core/models/exchange.py)

> Resultado de comparar dos `ExchangeFile`.

- `i_need: list[ExchangeCard]`
- `i_can_offer: list[ExchangeCard]`

### `ExchangeSession` — [src/collections_app/core/models/exchange.py](src/collections_app/core/models/exchange.py)

> Estado in-memory de un intercambio en proceso de ejecución.

- `to_give: list[ExchangeCard]`
- `to_receive: list[ExchangeCard]`
- `locked_items: list[ExchangeCard]`

### `InventoryItem` — [src/collections_app/core/models/inventory_item.py](src/collections_app/core/models/inventory_item.py)

> Stock del usuario para una Card.

- `collection_id: int`
- `code_id: str`
- `card_number: int`
- `quantity: int`
- `image_path: str | None`
- `locked: int`

**Métodos:**
- `is_owned(self) -> bool` — True si el usuario tiene al menos una copia.
- `has_duplicates(self) -> bool` — True si el usuario tiene más de una copia (sin descontar locked).
- `available_quantity(self) -> int` — Cantidad disponible para nuevas operaciones = quantity - locked.
- `has_available_duplicates(self) -> bool` — True si tiene >1 copias DESCONTANDO las bloqueadas.

### `Transaction` — [src/collections_app/core/models/transaction.py](src/collections_app/core/models/transaction.py)

> Registro inmutable de un movimiento sobre el inventario.

- `transaction_id: int | None`
- `collection_id: int`
- `code_id: str`
- `card_number: int`
- `operation: OperationType`
- `quantity: int`
- `transaction_date: datetime`

## Repositorios (`core/repositories/`)

Una clase por tabla. Las repos NO crean conexión, la reciben (`__init__(conn)`). Los queries devuelven instancias de `core/models/`.

### `BaseRepository` — [src/collections_app/core/repositories/base.py](src/collections_app/core/repositories/base.py)

> Repository base. Todas las repos reciben una conexión SQLite.

**API pública:**
- `__init__(self, conn: sqlite3.Connection) -> None`

### `CardImagesRepository` — [src/collections_app/core/repositories/card_images_repo.py](src/collections_app/core/repositories/card_images_repo.py)

> Tracking de imágenes generadas por card.

**API pública:**
- `upsert(self, image: CardImage) -> None` — Inserta o actualiza el tracking de una card.
- `get(self, collection_id: int, code_id: str, card_number: int) -> CardImage | None` — Retorna la entry por PK compuesta, o None si no existe.
- `list_by_collection(self, collection_id: int) -> list[CardImage]` — Todas las imágenes registradas de una colección.
- `get_pending(self, collection_id: int) -> list[Card]` — Cards que todavía no tienen imagen generada (no aparecen en card_images).
- `get_placeholders(self, collection_id: int) -> list[CardImage]` — Cards generadas pero con `found_photo=False` (placeholder).
- `get_found_count(self, collection_id: int) -> int` — Cuántas cards tienen `found_photo=True`.
- `get_total_generated(self, collection_id: int) -> int` — Cuántas cards tienen alguna imagen (real o placeholder).
- `delete(self, collection_id: int, code_id: str, card_number: int) -> None` — Borra el tracking de una card (forzando que vuelva a "pending").

### `CardsRepository` — [src/collections_app/core/repositories/cards_repo.py](src/collections_app/core/repositories/cards_repo.py)

> CRUD sobre `cards`.

**API pública:**
- `list_by_collection(self, collection_id: int) -> list[Card]` — Retorna todas las cards de una colección ordenadas por (code_id, card_number).
- `get(self, collection_id: int, code_id: str, card_number: int) -> Card | None` — Retorna la card por PK compuesta, o None si no existe.
- `upsert(self, card: Card) -> Card` — Inserta o actualiza la card según exista.
- `delete(self, collection_id: int, code_id: str, card_number: int) -> bool` — Borra la card. Cascade borra el inventory item asociado.
- `count_by_collection(self, collection_id: int) -> int` — Cuenta cuántas cards tiene una colección.
- `find_by_number(self, collection_id: int, card_number: int) -> list[Card]` — Busca cards en la colección por número, sin filtrar por code_id.
- `list_by_code(self, collection_id: int, code_id: str) -> list[Card]` — Retorna las cards de una colección filtradas por code_id.
- `get_stats_by_code(self, collection_id: int) -> list[CodeStats]` — Stats agregadas por code_id de la colección.
- `bulk_upsert(self, cards: list[Card]) -> int` — Inserta o actualiza muchas cards en un batch.

### `CodesHeadersRepository` — [src/collections_app/core/repositories/codes_headers_repo.py](src/collections_app/core/repositories/codes_headers_repo.py)

> CRUD sobre `codes_headers`.

**API pública:**
- `list_all(self) -> list[CodeHeader]` — Retorna todos los headers ordenados por nombre.
- `get_by_id(self, code_header_id: int) -> CodeHeader | None` — Retorna el header por id, o None si no existe.
- `get_by_name(self, name: str) -> CodeHeader | None` — Retorna el header por nombre exacto, o None si no existe.
- `create(self, header: CodeHeader) -> CodeHeader` — Inserta y retorna el header con `code_header_id` poblado.
- `update(self, header: CodeHeader) -> CodeHeader` — Actualiza un header existente. Requiere `code_header_id` no None.
- `delete(self, code_header_id: int) -> bool` — Borra un header. Cascade borra `codes_lines` asociadas.

### `CodesLinesRepository` — [src/collections_app/core/repositories/codes_lines_repo.py](src/collections_app/core/repositories/codes_lines_repo.py)

> CRUD sobre `codes_lines` con validación de longitud contra el header.

**API pública:**
- `list_by_header(self, code_header_id: int) -> list[CodeLine]` — Retorna las líneas de un header ordenadas por (code_order, code_id).
- `get(self, code_header_id: int, code_id: str) -> CodeLine | None` — Retorna la línea por PK compuesta, o None si no existe.
- `upsert(self, line: CodeLine) -> CodeLine` — Inserta o actualiza la línea según exista.
- `delete(self, code_header_id: int, code_id: str) -> bool` — Borra una línea. Retorna True si se borró efectivamente.
- `list_codes_only(self, code_header_id: int) -> list[str]` — Solo los IDs de los códigos de un header (útil para autocomplete).
- `reorder(self, code_header_id: int, ordered_code_ids: list[str]) -> None` — Reasigna code_order según el índice (1-based) en la lista.

### `CollectionsRepository` — [src/collections_app/core/repositories/collections_repo.py](src/collections_app/core/repositories/collections_repo.py)

> CRUD sobre `collections`.

**API pública:**
- `list_all(self) -> list[Collection]` — Retorna todas las colecciones ordenadas por nombre.
- `get_by_id(self, collection_id: int) -> Collection | None` — Retorna la colección por id, o None si no existe.
- `get_by_name(self, name: str) -> Collection | None` — Retorna la colección por nombre exacto, o None si no existe.
- `create(self, collection: Collection) -> Collection` — Inserta y retorna la colección con `collection_id` poblado.
- `update(self, collection: Collection) -> Collection` — Actualiza una colección existente. Requiere `collection_id` no None.
- `delete(self, collection_id: int) -> bool` — Borra la colección. Cascade borra cards e inventory.

### `InventoryRepository` — [src/collections_app/core/repositories/inventory_repo.py](src/collections_app/core/repositories/inventory_repo.py)

> CRUD y queries específicas sobre `inventory`.

**API pública:**
- `get(self, collection_id: int, code_id: str, card_number: int) -> InventoryItem | None` — Retorna el inventario por PK compuesta, o None si no existe.
- `list_by_collection(self, collection_id: int) -> list[InventoryItem]` — Lista todo el inventario de una colección.
- `list_owned(self, collection_id: int) -> list[InventoryItem]` — Solo los items con quantity > 0.
- `get_top_duplicates(self, collection_id: int, limit: int = 10) -> list[InventoryItem]` — Las cards con mayor cantidad (quantity > 1), ordenadas desc.
- `list_duplicates(self, collection_id: int) -> list[InventoryItem]` — Solo los items con quantity > 1.
- `list_locked(self, collection_id: int) -> list[InventoryItem]` — Items con locked > 0 (reservados para un intercambio en curso).
- `list_missing(self, collection_id: int) -> list[Card]` — Cards que el usuario aún no tiene (sin inventory o quantity=0).
- `upsert(self, item: InventoryItem) -> InventoryItem` — Crea o actualiza el inventory item.
- `adjust_quantity(self, collection_id: int, code_id: str, card_number: int, delta: int) -> InventoryItem` — Suma `delta` a la quantity (delta puede ser negativo).
- `set_image(self, collection_id: int, code_id: str, card_number: int, image_path: str) -> None` — Setea el image_path del inventory item, creándolo con quantity=0 si no existe.
- `lock(self, collection_id: int, code_id: str, card_number: int, amount: int = 1) -> InventoryItem` — Incrementa `locked` en `amount`. NO modifica `quantity`.
- `unlock(self, collection_id: int, code_id: str, card_number: int, amount: int = 1) -> InventoryItem` — Decrementa `locked` en `amount`. Mínimo 0 (clamp).
- `unlock_all(self, collection_id: int) -> int` — Resetea locked=0 para toda la colección. Retorna filas afectadas.

### `SettingsRepository` — [src/collections_app/core/repositories/settings_repo.py](src/collections_app/core/repositories/settings_repo.py)

> Acceso clave/valor a `app_settings`.

**API pública:**
- `get(self, key: str) -> str | None` — Retorna el valor de `key`, o None si no existe.
- `set(self, key: str, value: str) -> None` — Inserta o actualiza el valor de `key`.
- `delete(self, key: str) -> bool` — Borra la entrada. Retorna True si se borró efectivamente.
- `get_int(self, key: str) -> int | None` — Retorna el valor parseado como int, o None si no existe o no es int válido.

### `TransactionsRepository` — [src/collections_app/core/repositories/transactions_repo.py](src/collections_app/core/repositories/transactions_repo.py)

> Bitácora de operaciones (alta/baja) sobre el inventario.

**API pública:**
- `log(self, txn: Transaction) -> Transaction` — Inserta una transacción.
- `list_by_collection(self, collection_id: int, limit: int = 100) -> list[Transaction]` — Transacciones de una colección, las más recientes primero.
- `list_by_date_range(self, start: datetime, end: datetime, collection_id: int | None = None) -> list[Transaction]` — Transacciones en un rango [start, end] inclusivo, opcionalmente filtradas.
- `list_recent(self, limit: int = 20) -> list[Transaction]` — Las N transacciones más recientes globalmente.
