# Diccionario de Datos

> Generado automáticamente por [`scripts/generate_context.py`](../scripts/generate_context.py). Pensado como contexto compacto para alimentar una conversación nueva.

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

**Foreign keys:**
- `FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)`

### Tabla `inventory`

- `collection_id INTEGER NOT NULL`
- `code_id TEXT NOT NULL`
- `card_number INTEGER NOT NULL`
- `quantity INTEGER NOT NULL DEFAULT 0`
- `image_path TEXT`
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

### `InventoryItem` — [src/collections_app/core/models/inventory_item.py](src/collections_app/core/models/inventory_item.py)

> Stock del usuario para una Card.

- `collection_id: int`
- `code_id: str`
- `card_number: int`
- `quantity: int`
- `image_path: str | None`

**Métodos:**
- `is_owned(self) -> bool` — True si el usuario tiene al menos una copia.
- `has_duplicates(self) -> bool` — True si el usuario tiene más de una copia.

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
- `list_missing(self, collection_id: int) -> list[Card]` — Cards que el usuario aún no tiene (sin inventory o quantity=0).
- `upsert(self, item: InventoryItem) -> InventoryItem` — Crea o actualiza el inventory item.
- `adjust_quantity(self, collection_id: int, code_id: str, card_number: int, delta: int) -> InventoryItem` — Suma `delta` a la quantity (delta puede ser negativo).
- `set_image(self, collection_id: int, code_id: str, card_number: int, image_path: str) -> None` — Setea el image_path del inventory item, creándolo con quantity=0 si no existe.

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
