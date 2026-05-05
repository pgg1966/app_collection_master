# CLAUDE.md — Collections App v0.2.0

> Reglas obligatorias para cualquier agente de IA (Claude Code u otro) que trabaje sobre este repo.
> v0.2.0 es un **rewrite arquitectónico** desde cero. Las decisiones de diseño de v0.1 NO son referencia.
> Si una regla acá entra en conflicto con un pedido del usuario, **gana esta guía**: pedir confirmación antes de violarla.

---

## 1. Contexto del proyecto

- Aplicación de escritorio Python (PySide/PyQt) para gestionar colecciones de cards/cromos.
- Versión actual: **0.2.0** — rewrite con lecciones aprendidas del informe de auditoría de v0.1.
- Arquitectura en capas estricta:
  ```
  views (Qt) → services → repositories → db / models (dataclasses)
  ```
- Persistencia: SQLite local, migraciones versionadas en `core/db/schema/NNN_*.sql`.
- Contexto canónico se regenera con `scripts/generate_context.py` → `data_dictionary.md` y `project_structure.md`. **No editar a mano.**

---

## 2. Reglas duras de arquitectura (NO regresables)

Estas reglas existen porque v0.1 las violó y eso causó la deuda que estamos remediando. **Romperlas es regresión, no flexibilidad.**

### 2.1 Capas y dirección de dependencias
- `views` solo importan de `services` y `core.models`. **Nunca** de `repositories` ni de `sqlite3`.
- `services` importan de `repositories`, `core.models` y otros `services`. **Nunca** de Qt ni de vistas.
- `repositories` importan solo de `core.models`, `sqlite3` y utilidades de DB. **Nunca** de Qt, services o vistas.
- `core.models` son `@dataclass` puros: sin I/O, sin SQL, sin Qt.

**Test automático en CI:** un script en `tests/architecture/test_layers.py` que falla si hay imports incorrectos. Ese test es no-skippable.

### 2.2 Paridad persistencia ↔ dominio
Por cada tabla SQL (excepto `schema_version`) debe existir:
- Un dataclass en `core/models/`.
- Un repositorio en `core/repositories/`.

Nombres consistentes (`Card` ↔ `cards` ↔ `CardsRepository`). El test de arquitectura también verifica esto.

### 2.3 Contratos de retorno de los repositorios
Métodos públicos de un repo retornan **únicamente** uno de:
- `Model` (instancia del dataclass de dominio).
- `list[Model]`.
- `None` (cuando hay variante "get or null").
- `bool` (existencia, success de delete).
- `int` (counts agregados, exclusivamente).

**Prohibido retornar:** `tuple`, `dict`, `sqlite3.Row`, `Any`, valores primitivos crudos como `str` (envolver en dataclass aunque sea un solo campo, ej: `AppSetting`).

### 2.4 PKs subrogadas obligatorias
Toda tabla nueva tiene `id INTEGER PRIMARY KEY AUTOINCREMENT`. Las business keys van como `UNIQUE` constraint, **no** como PK.

Tabla típica:
```sql
CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    card_name TEXT NOT NULL,
    UNIQUE (collection_id, code_id, card_number),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id) ON DELETE CASCADE
);
```

### 2.5 Trazabilidad obligatoria de transacciones
Toda tabla de log/auditoría (`transactions` y similares) tiene FK a la entidad atómica afectada, **no a su contenedor**. Una transacción de inventario apunta a `card_id`, no solo a `collection_id`.

### 2.6 Una sola fuente de verdad por dato
Antes de agregar una columna, **buscar en `data_dictionary.md`** si el dato ya existe. Prohibido el patrón "tengo el path acá y también allá por las dudas". Si dos columnas guardan el mismo dato, una está mal.

### 2.7 Migraciones inmutables
- Numeradas `001_*.sql`, `002_*.sql`, etc.
- Una vez committeadas y aplicadas en cualquier entorno, **no se editan**. Si un cambio requiere ajuste, va en una migración nueva.
- Toda migración:
  - Envuelta en transacción.
  - Idempotente (correrla 2 veces no rompe nada).
  - Probada con un test que la aplica sobre `:memory:` y verifica el schema resultante.

---

## 3. Workflow obligatorio del agente

### 3.1 Plan Mode (obligatorio)
Para cualquiera de estos casos:
- Cambio de schema SQL.
- Nuevo modelo, repositorio o servicio.
- Refactor que toca >3 archivos.
- Cambio en firma pública de un método público de service o repo.

→ El agente **debe** producir primero un plan textual con: qué cambia, por qué, qué archivos toca, qué tests agrega. **Esperar confirmación humana antes de codear.**

### 3.2 TDD
- `services/` y `repositories/`: **test primero, debe fallar, después implementación.**
- Modelos (dataclasses puros): test si tienen lógica (helpers tipo `as_int()`, `card_key()`); sin tests si son data containers triviales.
- Vistas Qt: tests opcionales, pero la lógica que se pueda extraer del slot debe vivir en un service y sí estar testeada.

### 3.3 Rewind Protocol
- Si una implementación falla en **2 iteraciones consecutivas** (test rojo, runtime error, refactor que rompe otra cosa) → **parar**, reportar el problema, sugerir `Esc Esc` / `/rewind` o `/clear`.
- **Prohibido** parche-sobre-parche en la misma sesión.

### 3.4 Higiene de contexto
- Si la sesión supera ~50% de uso de contexto → `/compact` o reiniciar antes de tomar decisiones arquitectónicas.
- Al iniciar sesión nueva sobre tema previo → leer primero `data_dictionary.md` y la sección relevante de este archivo. **No** asumir desde memoria.

### 3.5 Ámbito de la sesión
Cada sesión tiene un objetivo único declarado. Si el agente detecta que "ya que estoy" podría arreglar X que no es parte del objetivo:
- Listarlo en una sección "Detectado pero no abordado" al final de la sesión.
- **No** tocarlo.
- Crear un issue / TODO para una sesión futura.

---

## 4. Convenciones de código

- **Python ≥ 3.11**, type hints obligatorios. `from __future__ import annotations` cuando ayude.
- Modelos: `@dataclass(slots=True)` salvo justificación explícita.
- Nombres: `snake_case` funciones/variables, `PascalCase` clases, módulos en minúscula con guión bajo.
- Errores: excepciones de dominio por service (`InventoryError`, `LicenseError`, etc.). Nada de `Exception` o `RuntimeError` genéricos en lógica de negocio.
- Logging: logger configurado en `core/utils/logging_setup.py`. Nada de `print()` fuera de `scripts/`.
- SQL: parametrizado con `?`, nunca f-strings con valores. Para queries dinámicas (`IN (...)`), construir solo placeholders.

---

## 5. Tests

- Framework: `pytest`. Estructura espejo en `tests/`.
- Cada repo nuevo: tests CRUD + edge cases (PK inexistente, cascade, restricciones UNIQUE).
- Cada service nuevo: tests con repos reales contra SQLite `":memory:"` + migrador. **No** mocks de la DB.
- Coverage mínimo en `core/`: **80%**. PR que baje cobertura sin justificación: rechazar.
- Tests de arquitectura (`tests/architecture/`): no-skippables.

---

## 6. Patrones explícitamente prohibidos

Estos patrones aparecieron en v0.1 y causaron deuda. **Prohibido reintroducirlos.**

- ❌ Columna que guarda "el nombre de otra columna" (`code_field_name TEXT` en v0.1).
- ❌ Dos columnas con el mismo dato "por las dudas" (`inventory.image_path` + `card_images.image_path` en v0.1).
- ❌ Repos que retornan tuplas o dicts.
- ❌ Tablas sin contraparte de modelo o repo.
- ❌ Tablas de log/auditoría sin FK granular a la entidad afectada.
- ❌ PKs compuestas de 3+ columnas (usar UNIQUE en su lugar).
- ❌ Edits a migraciones ya aplicadas.
- ❌ Imports cross-layer (vistas importando repos, repos importando services, etc.).

---

## 7. Módulos preservados de v0.1

Algunos módulos de v0.1 funcionan correctamente y se conservan en v0.2 con cambios mínimos.

### 7.1 Pantalla de alta de stock / inventario
- Ubicación esperada en v0.2: `views/inventory/stock_entry_view.py` (nombre tentativo, ajustar al definitivo de v0.1).
- **Política:** la lógica de UI (signals, slots, layout) se preserva sin modificaciones funcionales. Cambios permitidos:
  - Estéticos (colores, spacing, fuentes) si son explícitamente pedidos.
  - Adaptación de los **callsites a services**, porque los services tienen API nueva.
  - Adaptación de imports si los modelos de dominio cambian de paquete.
- **Política:** la lógica interna de la vista (validaciones, cálculos en el slot, máquinas de estado) **NO se toca** salvo bug encontrado durante integración.
- Si durante la integración aparece un bug heredado: documentarlo, NO arreglarlo en la misma sesión, abrir issue.

---

## 8. Checklist obligatorio antes de cada commit del agente

- [ ] ¿Cambié schema? → ¿migración nueva, no edité una existente?
- [ ] ¿Agregué tabla? → ¿modelo + repo + tests creados?
- [ ] ¿Agregué método de repo? → ¿devuelve modelo de dominio, no tupla/dict?
- [ ] ¿Toqué la pantalla preservada de alta de stock? → ¿solo callsites, no lógica?
- [ ] ¿Tests verdes? (`pytest`)
- [ ] ¿Tests de arquitectura verdes? (`pytest tests/architecture/`)
- [ ] ¿Pre-commit limpio?
- [ ] ¿`data_dictionary.md` regenerado si cambió el schema o los modelos?

---

## 9. Lo que NO hace este archivo

- No reemplaza la revisión humana de PRs.
- No cubre detalles de UX / look & feel de Qt; eso vive en `docs/ui_guidelines.md` (futuro).
- No define el modelo de licenciamiento; vive en `services/license_service.py`.

> Si algo de este doc contradice el estado real del repo, **avisar al humano antes de ejecutar nada**. La discordancia se resuelve actualizando este archivo, no ignorándolo.
