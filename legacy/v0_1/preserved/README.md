# Módulo preservado: pantalla de alta de stock (CardLoaderView)

> Origen único de la lógica de carga rápida (alta/baja) de cards. v0.2
> conserva la **lógica funcional** y solo adapta los **callsites** según
> CLAUDE.md sec. 7.1.

## Origen exacto en v0.1

Archivo único: [`legacy/v0_1/src/collections_app/client/views/card_loader.py`](../src/collections_app/client/views/card_loader.py)

Test asociado en v0.1: [`legacy/v0_1/tests/client/views/test_card_loader.py`](../tests/client/views/test_card_loader.py)

`legacy/v0_1/preserved/card_loader.py` es una **copia textual** del archivo
de v0.1, mantenida acá para que la integración de Prompt 2/3 trabaje contra
una copia estable aunque legacy/v0_1/src/ se reorganice o se elimine.

## Punto de entrada

```python
class CardLoaderView(QWidget):
    card_changed = Signal()  # se emite tras cada save exitoso

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None: ...

    def set_active_collection(self, collection: Collection) -> None: ...
```

## Estado en v0.2

**No integrado todavía.** Pendiente Prompt 2/3 (cuando existan los
services e InventoryService.add_card / remove_card / etc.).

## Helpers internos del archivo

Convive en el mismo `.py`, no se reparte:

- `_EmptyFieldFilter(QObject)` — bloquea Tab/Backtab/Enter cuando un
  QLineEdit está vacío.
- `_CodeOnlyCompleter(QCompleter)` — `pathFromIndex` devuelve solo el
  prefijo antes de `" - "`.

Al mover el módulo a v0.2 estos helpers viajan con él.

## Dependencias y callsites a adaptar

| Import en v0.1                                                       | Destino en v0.2                                  | Acción                                                                                                                                |
| -------------------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `from collections_app.core.models import Card, Collection, InventoryItem` | `collections_app.core.models.{...}`              | Renombre directo cuando los models existan (Prompt 1).                                                                                |
| `from collections_app.core.repositories import CardsRepository, CodesLinesRepository, InventoryRepository` | **eliminar**                                     | **Mover queries a `InventoryService`**. Agregar a IS los métodos: `lookup_card(cid, code, n)`, `find_by_number(cid, n)`, `code_name(header_id, code)`, `inventory_get(cid, code, n)`. La vista deja de tocar repos. |
| `from collections_app.core.services import InventoryService, AmbiguousCardError` | `collections_app.services.inventory_service.{...}` | Renombre. `services/` deja de estar adentro de `core/` en v0.2.                                                                       |
| `from collections_app.shared_ui.theme import INPUT_BG_ALTA, INPUT_BG_BAJA, READONLY_BG, Spacing, StatusColor` | `collections_app.views.shared.theme.{...}`       | Reconstruir `views/shared/theme.py` con los **mismos nombres y valores**. Origen referencia: [`legacy/v0_1/src/collections_app/shared_ui/theme.py`](../src/collections_app/shared_ui/theme.py). |
| `from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator` | `collections_app.views.shared.widgets.enter_navigator.EnterNavigator` | Migrar tal cual el archivo. Origen: [`legacy/v0_1/src/collections_app/shared_ui/widgets/enter_navigator.py`](../src/collections_app/shared_ui/widgets/enter_navigator.py). |
| `import sqlite3` + `conn: sqlite3.Connection` en `__init__`           | **eliminar import + cambiar firma**              | La vista no debe ver sqlite3 (CLAUDE.md sec 2.1). El `__init__` recibe **un `InventoryService`** en lugar de `conn`. Las dependencias de codes/cards las consume vía métodos del service. |

## Política durante la integración (Prompt 2/3)

- **Lógica interna** (validaciones, máquina de estado de ambigüedad,
  signals/slots, layout, navegación por Enter, tinte Alta/Baja, manejo
  del completer) **NO se toca**. La política de CLAUDE.md sec 7.1 lo
  confirma.
- Solo se reemplazan imports y los puntos de uso de repos por llamadas
  al service.
- Cualquier bug heredado detectado durante la integración: documentar
  en una sección "Detectado pero no abordado", abrir issue, **NO
  arreglar en la sesión de integración**.

## Tests

`legacy/v0_1/tests/client/views/test_card_loader.py` cubre el comportamiento
funcional. En la integración:

- **Opción A** — portar los tests a `tests/views/inventory/` adaptando
  los fixtures (que hoy crean repos directos) a fixtures que crean un
  `InventoryService` real contra `:memory:`.
- **Opción B** — reescribir desde cero usando `pytest-qt` con la API nueva.

Decisión final cuando la integración suceda. Esta nota queda como
recordatorio.
