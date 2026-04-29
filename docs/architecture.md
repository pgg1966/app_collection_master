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
