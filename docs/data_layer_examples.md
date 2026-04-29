# Capa de datos — Ejemplos copy-paste

Recetas para usar la capa de datos. Todos los snippets asumen que ya tenés:

```python
from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations

conn = create_connection("collections.db")  # o ":memory:" para tests
run_migrations(conn)
```

---

## Headers de códigos

```python
from collections_app.core.models import CodeHeader, CodeLine
from collections_app.core.repositories import (
    CodesHeadersRepository, CodesLinesRepository,
)

headers = CodesHeadersRepository(conn)
lines = CodesLinesRepository(conn)

fifa = headers.create(CodeHeader(None, "FIFA", code_max_length=3))
lines.upsert(CodeLine(fifa.code_header_id, "ARG", "Argentina"))
lines.upsert(CodeLine(fifa.code_header_id, "BRA", "Brasil"))
conn.commit()

print(lines.list_codes_only(fifa.code_header_id))  # ['ARG', 'BRA']
```

`upsert` valida `len(code_id) <= code_max_length`. Si excede, lanza `ValueError`.

---

## Crear una colección con validación

```python
from collections_app.core.models import Collection
from collections_app.core.services import CollectionsService

svc = CollectionsService(conn)
collection = svc.create_collection_with_validation(Collection(
    collection_id=None,
    collection_name="FIFA WC 2026",
    card_count=300,
    requires_code=True,
    code_field_name="País",
    code_header_id=fifa.code_header_id,
))
conn.commit()
```

Si `code_header_id` no existe, levanta `ValueError`.

---

## Cargar muchas cards a la vez (batch)

```python
from collections_app.core.models import Card
from collections_app.core.repositories import CardsRepository

cards = CardsRepository(conn)
batch = [
    Card(collection.collection_id, "ARG", n, f"Card-ARG-{n}")
    for n in range(1, 31)
]
cards.bulk_upsert(batch)
conn.commit()
```

`bulk_upsert` usa `executemany` y NO commitea.

---

## Alta de inventario (atómica con log)

```python
from collections_app.core.services import InventoryService

inventory = InventoryService(conn)
item = inventory.add_card(
    collection.collection_id, "ARG", 1, quantity=2,
)
# Inserta/actualiza el inventory item Y registra una transacción 'alta'
# en la misma transacción SQLite. Si algo falla, rollback total.
```

Si la card no existe en el catálogo, levanta `ValueError`.
Si `quantity <= 0`, levanta `ValueError`.

---

## Baja de inventario

```python
inventory.remove_card(collection.collection_id, "ARG", 1, quantity=1)
```

Levanta `ValueError` si no hay inventario o si `quantity` excede el stock
actual. Nunca deja inventario en negativo.

---

## Consultar inventario

```python
from collections_app.core.repositories import InventoryRepository

inv = InventoryRepository(conn)

# Todo lo que tiene el usuario
inv.list_owned(collection.collection_id)  # InventoryItem[] con qty > 0

# Cards repetidas
inv.list_duplicates(collection.collection_id)  # InventoryItem[] con qty > 1

# Lo que falta para completar
inv.list_missing(collection.collection_id)  # Card[] (no InventoryItem)

# Stats agregadas
stats = InventoryService(conn).get_stats(collection.collection_id)
# {
#   "total_cards": 300, "owned": 42, "missing": 258,
#   "percentage": 14.0, "total_physical": 55,
#   "cards_with_duplicates": 8, "total_duplicate_copies": 13,
# }
```

---

## Bitácora de transacciones

```python
from collections_app.core.repositories import TransactionsRepository

txns = TransactionsRepository(conn)
recientes = txns.list_by_collection(collection.collection_id, limit=50)

# Por rango de fechas (acepta collection_id opcional)
from datetime import datetime, timedelta
ayer = datetime.now() - timedelta(days=1)
ahora = datetime.now()
txns.list_by_date_range(ayer, ahora, collection_id=collection.collection_id)
```

---

## Settings clave/valor (colección activa)

```python
from collections_app.core.services import SettingsService

settings = SettingsService(conn)
settings.set_active_collection(collection.collection_id)
conn.commit()

# En la app client:
active = settings.get_active_collection()  # Collection | None
```

`get_active_collection()` retorna `None` si el setting apunta a una
colección que ya no existe (no rompe).

---

## Patrón de transacciones explícitas

Para agrupar varias operaciones de repositories en una sola transacción:

```python
from collections_app.core.db.connection import transaction

with transaction(conn):
    cards_repo.upsert(...)
    inventory_repo.upsert(...)
    transactions_repo.log(...)
# commit automático al salir; rollback si hubo excepción
```

---

## Tips

- Todos los modelos son `frozen=True`: para "modificar" creá uno nuevo con
  `dataclasses.replace(modelo, campo=valor)`.
- Los repositories devuelven `None` cuando algo no existe (nunca raisean
  por "not found").
- Los repositories propagan `sqlite3.IntegrityError` ante violaciones de
  constraints (PK duplicada, FK inválido, etc.) — no los silencian.
- Los services validan inputs antes de tocar SQL y agrupan operaciones
  multi-tabla en transacciones atómicas.
