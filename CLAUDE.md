# CLAUDE.md — Convenciones del proyecto Collections

Este archivo describe las convenciones que TODO código generado en este 
proyecto debe respetar. Leer antes de cualquier cambio.

## Stack
- Python 3.11+
- PySide6 (UI)
- SQLite con WAL mode (DB)
- pytest (testing)
- black + ruff + mypy (calidad)

## Arquitectura
El proyecto se separa en TRES capas:

1. **core/** — lógica pura, sin dependencias de UI ni de PySide6.
   Contiene: db, models, repositories, services, utils.
   Esta capa debe ser testeable sin GUI.

2. **admin/** y **client/** — dos aplicaciones independientes que comparten 
   el core. Admin tiene UI completa de configuración. Client es la app 
   distribuible al usuario final, sin acceso a configuración.

3. **shared_ui/** — widgets reutilizables entre admin y client (ABM 
   genérico, theme, validators de UI).

## Convenciones de base de datos

### Naming de tablas
- Las tablas se nombran en **plural** (ej: `collections`, `codes_headers`).
- El campo identificador es el **singular del nombre + _id** 
  (ej: `collection_id` en `collections`).
- El campo descripción/nombre es el **singular + _name** 
  (ej: `collection_name`).
- FKs mantienen el nombre del campo original.

### Tipos de IDs
- IDs auto-incrementales: `INTEGER PRIMARY KEY AUTOINCREMENT`.
- IDs significativos (ej: códigos como "ARG", "MR"): `TEXT`, parte de PK 
  compuesta.

### Migraciones
- Las migraciones viven en `core/db/schema/` numeradas: `001_initial.sql`, 
  `002_xxx.sql`, etc.
- **NUNCA modificar una migración ya aplicada**. Para cambios, crear migración nueva.
- El migrator lleva control en una tabla `schema_version` dentro del .db.

### WAL y FK
- Activar WAL mode al conectar: `PRAGMA journal_mode=WAL`.
- Activar FKs al conectar: `PRAGMA foreign_keys=ON`.

## Convenciones de código Python

### Estilo
- Type hints OBLIGATORIOS en todas las funciones públicas.
- Docstrings estilo Google en módulos, clases y funciones públicas.
- Nombres en `snake_case` para variables/funciones, `PascalCase` para clases.
- No usar `print` en código de producción, siempre `logging`.
- Formatear con black (line-length=100).
- Validar con ruff antes de commit.
- Validar tipos con mypy strict.

### Internacionalización
- TODOS los strings visibles al usuario deben envolverse con `self.tr()` 
  o `tr()` (PySide6) aunque no haya traducciones todavía.
- Logs y mensajes de excepción internos NO se traducen.

### Patrón Repository
- Cada tabla tiene su Repository en `core/repositories/`.
- Los Repositories devuelven instancias de los modelos en `core/models/`.
- Los modelos son `@dataclass(frozen=True)` siempre que sea posible.
- Los repositories NO conocen UI ni signals.

### Servicios
- Los `services/` orquestan repositories cuando hay lógica que cruza tablas.
- Ejemplo: `inventory_service.add_card()` toca inventory + transactions.

## Convenciones de UI

### Navegación con teclado
- Toda pantalla de carga rápida debe navegarse con Enter:
  Enter en un campo → foco al siguiente campo.
  Enter en el último campo → ejecutar acción primaria.
- En ABMs: Enter en último campo del form → click en "Guardar" → Enter 
  → confirma y refresca.
- No usar diálogos de confirmación de éxito (cartelitos "Guardado OK"). 
  La actualización visual de la grilla es feedback suficiente.

### ABM genérico
- Existe un widget `AbmWidget` parametrizable.
- Cada nuevo ABM se construye configurando definiciones de campos + 
  repository + validators, no copiando código de otro ABM.

### Settings de la app
- La colección activa se guarda en una tabla `app_settings` (key/value).
- La app **client** lee este setting al iniciar y NO permite modificarlo 
  desde su UI (configuración solo accesible desde admin).

## Convenciones de testing

- Los tests viven en `tests/` reflejando la estructura de `src/`.
- Cada repository tiene tests con DB en memoria (`:memory:`).
- Los services tienen tests con DB en memoria.
- La UI no se testea automáticamente en este proyecto (manual).

## Logging

- Configurar logging desde `utils/logging_setup.py`.
- Nivel por defecto: INFO. En desarrollo: DEBUG.
- Logs van a archivo rotativo en `data/logs/app.log` y a consola.
