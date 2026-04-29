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

## Capa UI compartida (shared_ui)

```
+----------------------------------------------------------+
|                    admin/main.py / client/main.py         |
|                  (subclases concretas de MainWindowBase)  |
+--------------------------+-------------------------------+
                           |
                           v
+----------------------------------------------------------+
|                       MainWindowBase                      |
|     (conn + migrations + status bar + menú base)          |
+--------------------------+-------------------------------+
                           |
            +--------------+---------------+
            v                              v
+-------------------------+   +-----------------------------+
|     SettingsDialog      |   |       AbmWidget             |
| (combo de colección     |   |   (filtro + grilla + form,  |
|  activa, persiste el    |   |    parametrizado por        |
|  setting al aceptar)    |   |    AbmConfig + FieldDef)    |
+-------------------------+   +-----------------------------+
                                       |
                                       v
                              +-----------------+
                              | EnterNavigator  |
                              | (Enter avanza   |
                              |  entre inputs)  |
                              +-----------------+
```

### Componentes principales

- **`theme.py`** — constantes de espaciado, tamaños de fuente, colores de
  status (success/info/warning/error) y `apply_app_style()`.
- **`EnterNavigator`** — `QObject` que instala event filters para que `Enter`
  avance al siguiente widget de una cadena ordenada y dispare un callback
  en el último.
- **`AbmWidget`** — widget genérico parametrizado por `AbmConfig`. Presenta
  filtro arriba, grilla a la izquierda y formulario a la derecha. Soporta
  campos TEXT/INT/BOOL/COMBO/READONLY, validación inline (status bar
  inferior) y único diálogo modal en la confirmación de borrado.
- **`SettingsDialog`** — `QDialog` con combo para elegir la colección
  activa; al aceptar persiste vía `SettingsService.set_active_collection`.
- **`MainWindowBase`** — `QMainWindow` que abre la conexión a SQLite,
  corre migraciones, monta menú "Archivo → Salir" y status bar con la
  colección activa. Subclases overridean `_build_menus()` para sumar
  acciones propias.

### Construir un ABM en ~30 líneas

```python
from collections_app.core.repositories import CodesHeadersRepository
from collections_app.core.models import CodeHeader
from collections_app.shared_ui import (
    AbmConfig, AbmWidget, FieldDef, FieldType,
)

repo = CodesHeadersRepository(conn)

def _save(header: CodeHeader) -> CodeHeader:
    if header.code_header_id is None:
        saved = repo.create(header)
    else:
        saved = repo.update(header)
    conn.commit()
    return saved

def _delete(header: CodeHeader) -> bool:
    ok = repo.delete(header.code_header_id)
    conn.commit()
    return ok

config = AbmConfig(
    title="Headers de códigos",
    module_code="HDR001",
    fields=[
        FieldDef("code_header_id", "ID", FieldType.READONLY, is_id=True, is_required=False),
        FieldDef("code_header_name", "Nombre", FieldType.TEXT),
        FieldDef("code_max_length", "Long. máx.", FieldType.INT, is_required=False),
    ],
    on_load_all=repo.list_all,
    on_save=_save,
    on_delete=_delete,
    model_class=CodeHeader,
    filter_field="code_header_name",
)
widget = AbmWidget(config, parent=main_window)
```

Más recetas y ejemplos en `docs/abm_widget_guide.md`.

## App Admin

La app admin (`collections-admin`) presenta tres tabs sobre `MainWindowBase`:

```
+-----------------------------------------------------------+
|  Archivo  Configuración                                    |
+-----------------------------------------------------------+
|  [ Colecciones | Códigos | Cards ]                         |
+-----------------------------------------------------------+
|                                                            |
|  ( contenido del tab seleccionado )                        |
|                                                            |
+-----------------------------------------------------------+
|  Colección activa: …                                       |
+-----------------------------------------------------------+
```

- **Tab Colecciones** (`CollectionsAbmView`): ABM directo sobre
  `collections`, con combo de `code_header`. Validaciones de negocio:
  si `requires_code` exige `code_field_name`; si `is_premium` exige
  `license_key_required`.
- **Tab Códigos** (`CodesMasterDetailView`): master-detail con dos
  AbmWidgets apilados verticalmente. El de arriba es ABM de
  `codes_headers`. Al seleccionar uno, se habilita el de abajo, que
  muestra sus `codes_lines` y permite alta/baja con `code_order`.
- **Tab Cards** (`CardsAbmView`): combo arriba para elegir colección,
  botón "Importar CSV…" y un AbmWidget que se reconstruye al cambiar
  de colección (porque los choices del combo `code_id` dependen del
  header de la colección).

### Diagrama master-detail (CodesMasterDetailView)

```
+----------------------------------------------------------+
|  Headers de Códigos                                       |
|  ┌────────────────────────┐  ┌────────────────────────┐  |
|  │ ID │ Nombre   │ Maxlen │  │  Edición Header        │  |
|  │ 1  │ FIFA     │ 5      │  │  …                     │  |
|  │ 2  │ Pokemon  │ 4      │  │  [Guardar][Nuevo][Del] │  |
|  └────────────────────────┘  └────────────────────────┘  |
+----------------------------------------------------------+
|  Códigos del header: FIFA                                 |
|  ┌────────────────────────┐  ┌────────────────────────┐  |
|  │ Code │ Nombre   │ Ord  │  │  Edición Código        │  |
|  │ ARG  │ Argentina│ 1    │  │  …                     │  |
|  │ BRA  │ Brasil   │ 2    │  │  [Guardar][Nuevo][Del] │  |
|  └────────────────────────┘  └────────────────────────┘  |
+----------------------------------------------------------+
```

El detail usa la señal `grid_selection_changed` del master para
escuchar cambios de header. Al seleccionar uno, reconfigura
`on_load_all` y `extra_kwargs` del config del detail (para inyectar
`code_header_id`) y refresca.

Ver flujo completo en `docs/admin_workflow.md`.
