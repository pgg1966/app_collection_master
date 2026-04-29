# Arquitectura — Collections

## Visión general

Collections se compone de dos aplicaciones de escritorio (admin y client) que
comparten un núcleo común de lógica y persistencia. El admin se usa para
construir la base de datos de una colección (catálogo, códigos, cards) y el
client es la aplicación que el usuario final ejecuta para gestionar su
inventario.

## Diagrama de capas

```
+-----------------------------------------------------------+
|                       admin/   client/                     |  ← UIs
|              (PySide6, entry points por app)               |
+---------------------+----------------+--------------------+
                      |                |
                      v                v
              +-----------------------------+
              |        shared_ui/           |  ← widgets reutilizables
              |  (AbmWidget, theme, etc.)   |
              +--------------+--------------+
                             |
                             v
              +-----------------------------+
              |          core/              |  ← lógica pura, sin Qt
              |  models / repositories /    |
              |  services / db / utils      |
              +--------------+--------------+
                             |
                             v
                    +-----------------+
                    |   SQLite (WAL)  |
                    +-----------------+
```

La regla básica es **una sola dirección de dependencias**: las UIs dependen
de `shared_ui` y `core`; `shared_ui` depende de `core`; y `core` no depende
de nada relacionado con la UI.

## Modelo de datos (schema 001)

| Tabla            | Propósito                                                    |
|------------------|--------------------------------------------------------------|
| `schema_version` | Tracking de migraciones aplicadas.                           |
| `app_settings`   | Configuración runtime clave/valor (ej. colección activa).    |
| `codes_headers`  | Universos de códigos (ej. "Países FIFA", "Sets de Magic").  |
| `codes_lines`    | Códigos individuales dentro de un header (ej. "ARG", "MR"). |
| `collections`    | Una colección configurada (catálogo de cards a juntar).     |
| `cards`          | Cards individuales del catálogo de cada colección.           |
| `inventory`      | Cantidades del usuario por card.                             |
| `transactions`   | Bitácora de altas/bajas con timestamp.                       |

Decisiones clave del schema:

- **Plural en tablas, singular + `_id` en PK**: convención uniforme.
- **PK compuesta** en `cards` y `inventory`: el `code_id` es significativo
  (no surrogate) y permite duplicados de número entre códigos.
- **FK con `ON DELETE CASCADE`** en relaciones contenedor/contenido para
  evitar inventory huérfano cuando se borra una colección o card.

## Flujo end-to-end

1. **Configuración (admin)**: el operador define `codes_headers`,
   `codes_lines`, crea una `collection` y carga sus `cards`.
2. **Distribución**: se exporta el archivo `.db` resultante.
3. **Uso (client)**: el usuario final recibe el `.db`, lo coloca en su
   directorio de datos y la app lee la colección activa desde
   `app_settings`. El client modifica `inventory` y graba en
   `transactions`, pero no toca el catálogo.

## Decisiones de diseño

- **SQLite en lugar de un servidor**: la app es de escritorio y monousuario;
  no hay valor agregado en correr Postgres. WAL mode da concurrencia
  suficiente para lecturas mientras escribimos.
- **Dos apps en lugar de una con "modo admin"**: separar los entry points
  reduce la superficie del binario distribuible y elimina por construcción
  la posibilidad de que el usuario final modifique el catálogo.
- **Repository pattern**: aísla SQL del resto del código, hace los
  servicios testeables con DB en memoria y mantiene la opción abierta de
  cambiar de motor en el futuro.
- **Migraciones inmutables numeradas**: simplicidad sobre frameworks
  como alembic; el proyecto es chico y las migraciones son lineales.

## Capa de datos

```
+--------------------------------------------------------+
|                     Services                            |
|   SettingsService   InventoryService   CollectionsService
|   (SETTING_KEY_*)   (alta/baja, stats)  (validate, info)
+--------------------------------------------------------+
                          |
                          v
+--------------------------------------------------------+
|                   Repositories                          |
|   CodesHeadersRepository    CardsRepository             |
|   CodesLinesRepository      InventoryRepository         |
|   CollectionsRepository     TransactionsRepository      |
|                             SettingsRepository          |
+--------------------------------------------------------+
                          |
                          v
+--------------------------------------------------------+
|                    Models (frozen)                      |
|   CodeHeader, CodeLine, Collection, Card,               |
|   InventoryItem, Transaction, OperationType             |
+--------------------------------------------------------+
                          |
                          v
                  +-----------------+
                  |   sqlite3.Connection
                  +-----------------+
```

### Manejo de transacciones

Los **repositories** NUNCA llaman a `commit()` o `rollback()`. Solo ejecutan
SQL. El caller (típicamente un service o el código de UI) decide cuándo
commitear, lo cual permite agrupar varias operaciones en una transacción
atómica.

Los **services** que cruzan tablas usan el helper `transaction()` definido
en `core/db/connection.py`:

```python
from collections_app.core.db.connection import transaction

with transaction(conn):
    inventory_repo.adjust_quantity(...)
    transactions_repo.log(...)
# commit automático; rollback ante cualquier excepción
```

`InventoryService.add_card` y `remove_card` siguen este patrón para
garantizar que el ajuste de inventario y el log de la operación viajen
juntos.

### Flujo end-to-end

```python
from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import CodeHeader, Collection, Card
from collections_app.core.repositories import (
    CodesHeadersRepository, CollectionsRepository, CardsRepository,
)
from collections_app.core.services import InventoryService

conn = create_connection("collections.db")
run_migrations(conn)

# 1) Crear el universo de códigos
headers = CodesHeadersRepository(conn)
fifa_codes = headers.create(CodeHeader(None, "FIFA Codes", code_max_length=3))

# 2) Crear la colección
collections = CollectionsRepository(conn)
wc26 = collections.create(Collection(
    None, "FIFA WC 2026", card_count=300, requires_code=True,
    code_field_name="País", code_header_id=fifa_codes.code_header_id,
))
conn.commit()

# 3) Cargar el catálogo de cards (batch)
cards_repo = CardsRepository(conn)
cards_repo.bulk_upsert([
    Card(wc26.collection_id, "ARG", n, f"Card-ARG-{n}") for n in range(1, 31)
])
conn.commit()

# 4) Alta de inventario (transaccional)
inventory = InventoryService(conn)
inventory.add_card(wc26.collection_id, "ARG", 1, quantity=2)

# 5) Consultar stats
print(inventory.get_stats(wc26.collection_id))
```

Ver `docs/data_layer_examples.md` para más recetas copy-paste.
