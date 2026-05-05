# Diseño del Sistema de Pairing — `.colexchange`

> Documento de decisiones consolidadas para el sistema de intercambios de Collections App v0.2.0.
> Input para el Prompt 5 (pairing) y referencia para sesiones futuras.

---

## Filosofía del sistema

El pairing es el **diferencial competitivo** de la app sobre otras herramientas de coleccionistas. Permite que dos usuarios con sus respectivos inventarios calculen automáticamente qué pueden intercambiar entre sí.

**Modelo offline peer-to-peer:** cada usuario maneja su data localmente, y el archivo `.colexchange` es el medio de intercambio. No hay servidor central en v0.2.

**Sistema transitorio:** este formato basado en archivos vive en v0.2 (escritorio) y v0.3 (móvil). Cuando llegue v1.0 con servidor en la nube, será reemplazado por API REST que hace el matching server-side. El diseño de v0.2 anticipa esa migración manteniendo la **lógica de matching como función pura agnóstica** del medio de transporte.

---

## Flujo del usuario

### Exportación

1. Usuario selecciona una colección en su app.
2. Click en "Exportar para intercambio".
3. App genera archivo `.colexchange` con:
   - Sus cards faltantes (lo que necesita).
   - Sus cards repetidas (lo que tiene de más).
   - Metadata + firma de autenticidad.
4. Archivo se guarda en disco con nombre canónico.
5. Usuario lo manda por WhatsApp / email / etc. al otro coleccionista.

### Importación + matching

1. Otro usuario recibe el archivo `.colexchange`.
2. Click en "Importar archivo de intercambio" en su app.
3. App valida firma y versión. Si falla, rechaza con mensaje claro.
4. App calcula:
   - **Match A:** "tus faltantes ∩ sus repetidas" → cards que él te puede dar.
   - **Match B:** "tus repetidas ∩ sus faltantes" → cards que vos le podés dar.
5. App muestra propuesta editable con cantidades pre-llenadas.
6. Usuario ajusta cantidades a la baja si quiere.
7. Click en "Confirmar intercambio".
8. App aplica las transacciones agrupadas:
   - Bajas para las cards de Match B (le diste).
   - Altas para las cards de Match A (recibiste).
   - Todas con el mismo `exchange_event_id` para reconstruir el evento en el historial.

---

## Formato del archivo `.colexchange`

### Estructura JSON

```json
{
  "format": "collections_app_exchange",
  "format_version": 1,
  "exported_at": "2026-05-15T14:30:00",
  "exported_by_app_version": "0.2.0",
  "collection": {
    "name": "Mundial 2026",
    "card_count": 670
  },
  "user_label": "PGG",
  "missing": [
    {
      "code_id": "ARG",
      "card_number": 4,
      "card_name": "Lautaro Martínez",
      "needed_quantity": 1
    }
  ],
  "duplicates": [
    {
      "code_id": "ARG",
      "card_number": 7,
      "card_name": "Di María",
      "available_quantity": 3
    }
  ],
  "signature": "hmac_sha256_hexdigest_aquí"
}
```

### Campos detallados

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `format` | string | sí | Identificador fijo: `"collections_app_exchange"` |
| `format_version` | int | sí | Versión del schema del archivo. v0.2 = 1 |
| `exported_at` | ISO 8601 | sí | Timestamp de generación |
| `exported_by_app_version` | string | sí | Versión de la app que generó el archivo |
| `collection.name` | string | sí | Nombre de la colección (para validar match) |
| `collection.card_count` | int | sí | Total de cards de la colección |
| `user_label` | string | no | Etiqueta opcional libre del usuario (ej: "PGG", "Juan") |
| `missing` | array | sí | Cards faltantes con cantidad necesaria |
| `duplicates` | array | sí | Cards repetidas con cantidad disponible |
| `signature` | string | sí | HMAC-SHA256 hex sobre el contenido (sin este campo) |

### Cálculo de la firma

1. Tomar el JSON completo **sin** el campo `signature`.
2. Serializar a string con campos ordenados alfabéticamente, sin espacios extra.
3. Calcular HMAC-SHA256 con la clave secreta hardcodeada en la app.
4. Resultado en hexadecimal va al campo `signature`.

### Validación al importar

1. Parsear JSON.
2. Verificar que `format == "collections_app_exchange"`.
3. Verificar que `format_version` es soportado por la app actual.
4. Extraer `signature`, recalcular sobre el resto del JSON.
5. Comparar hex a hex. Si no coincide → rechazar con mensaje "Archivo inválido o no generado por esta aplicación".
6. Verificar que `collection.name` coincide con una colección instalada localmente.

---

## Decisión de arquitectura: matching como función pura

La lógica que calcula los matches **NO** debe conocer si los datos vienen de un archivo `.colexchange`, una API REST, una base de datos compartida o cualquier otro medio.

### Interfaz del servicio

```python
@dataclass(frozen=True)
class InventorySnapshot:
    """Foto de inventario, agnóstica del medio."""
    user_label: str | None
    collection_name: str
    missing: list[MissingCard]
    duplicates: list[DuplicateCard]


@dataclass(frozen=True)
class MissingCard:
    code_id: str
    card_number: int
    card_name: str
    needed_quantity: int


@dataclass(frozen=True)
class DuplicateCard:
    code_id: str
    card_number: int
    card_name: str
    available_quantity: int


@dataclass(frozen=True)
class ExchangeProposal:
    """Resultado del matching."""
    cards_to_receive: list[ProposedExchange]  # Match A
    cards_to_give: list[ProposedExchange]     # Match B


@dataclass(frozen=True)
class ProposedExchange:
    code_id: str
    card_number: int
    card_name: str
    proposed_quantity: int      # default greedy
    max_quantity: int           # límite superior


class MatchingService:
    def calculate_proposal(
        self,
        my_inventory: InventorySnapshot,
        their_inventory: InventorySnapshot,
    ) -> ExchangeProposal:
        ...
```

**Esta función es pura.** No accede a archivos, no llama servicios externos, no muta estado. Recibe dos snapshots, devuelve una propuesta. Determinista.

**Implicación:** la misma función va a usarse en v0.2 leyendo de archivo, en v0.3 móvil leyendo de archivo, y en v1.0 nube recibiendo dos snapshots desde la base de datos del servidor. Solo cambia **de dónde vienen los snapshots**, no la lógica de matching.

---

## Reglas de matching

### Match A (cards que él te puede dar)

```
para cada card C en my_missing:
    si C también está en their_duplicates:
        proposed_quantity = min(C.needed_quantity, their_C.available_quantity)
        agregar a cards_to_receive con max_quantity = their_C.available_quantity
```

### Match B (cards que vos le podés dar)

```
para cada card C en their_missing:
    si C también está en my_duplicates:
        proposed_quantity = min(C.needed_quantity, my_C.available_quantity)
        agregar a cards_to_give con max_quantity = my_C.available_quantity
```

### Default greedy

`proposed_quantity` se inicializa con el **mínimo entre lo que el otro necesita y lo que vos tenés disponible**. La UI permite al usuario ajustar a la baja antes de confirmar, pero no a la subida (eso violaría el max).

---

## Aplicación del intercambio

Cuando el usuario confirma la propuesta:

1. Generar un `exchange_event_id` único (sugerencia: epoch en milisegundos + número aleatorio de 4 dígitos, garantiza unicidad sin coordinación).
2. Para cada card en `cards_to_give`:
   - Crear `Transaction(operation='baja', card_id, quantity, exchange_event_id)`.
   - Aplicar baja en `inventory` (decrementar `quantity`).
3. Para cada card en `cards_to_receive`:
   - Crear `Transaction(operation='alta', card_id, quantity, exchange_event_id)`.
   - Aplicar alta en `inventory` (incrementar `quantity`, crear entry si no existía).
4. Todo en una transacción SQL atómica. Si algo falla, rollback completo.

### Reconstrucción del intercambio en historial

Para mostrar "el día X hice este intercambio":

```sql
SELECT * FROM transactions
WHERE exchange_event_id = ?
ORDER BY transaction_date;
```

Las filas devueltas reconstruyen el evento completo: lista de cards entregadas (operation='baja') y recibidas (operation='alta').

---

## Seguridad: HMAC-SHA256 con clave hardcodeada

### Nivel de protección: 2

- ✅ Detecta archivos no generados por la app.
- ✅ Detecta archivos editados a mano.
- ✅ Detecta archivos corruptos.
- ❌ NO detecta a alguien que decompila la app y extrae la clave.

### Justificación de Nivel 2

- Repo de GitHub es privado, la clave no está expuesta públicamente.
- Para una app de coleccionistas entre amigos, Nivel 2 es proporcional al riesgo.
- Si en el futuro el proyecto justifica Nivel 3 (servidor central), se migra entonces.

### Implementación de la clave

- Constante en un módulo dedicado (ej: `core/security/exchange_signing.py`).
- **No** en variables de entorno ni archivos de configuración (la app debe funcionar offline).
- Generada una sola vez para v0.2, mantenida estable por toda la línea v0.x.
- Si en el futuro se compromete, requiere bump de `format_version` y re-publicación de la app.

---

## Documentación pública del formato

Decisión: **estructura del JSON documentada mínimamente** en `docs/colexchange_format.md` (a crear por el Prompt 5).

- Se documenta: campos, tipos, semántica, validación de versión.
- NO se documenta: cómo se calcula la firma, cuál es la clave HMAC, qué bytes exactos se hashean.

Esto permite que un coleccionista técnico entienda el formato si abre un archivo, pero no pueda reproducir la firma sin la app.

---

## Antipatrones explícitos (NO hacer)

### En el archivo `.colexchange`

- ❌ Incluir el inventario completo (solo missing + duplicates filtrado).
- ❌ Incluir información personal del usuario (más allá del label opcional).
- ❌ Incluir paths locales o IDs internos de la base.
- ❌ Versionado libre (siempre número entero, monótono creciente).

### En el matching

- ❌ Modificar el inventario durante el cálculo del matching (función pura, sin side effects).
- ❌ Decidir cantidades automáticamente sin permitir override del usuario.
- ❌ Asumir que las cards en el archivo del otro existen en tu DB local (validar primero, ignorar las desconocidas).

### En la aplicación del intercambio

- ❌ Aplicar bajas y altas en pasos separados sin transacción atómica.
- ❌ Permitir que `quantity` quede negativo (validación en service, no solo en DB).
- ❌ Borrar el `exchange_event_id` después (es la única forma de reconstruir el evento).

---

## Casos límite a considerar en tests

- Archivo con firma inválida → rechaza.
- Archivo de versión futura (`format_version: 2`) → rechaza con mensaje claro.
- Colección del archivo no existe localmente → rechaza con sugerencia.
- Card en el archivo no existe en la DB local (otro álbum, error tipográfico) → ignora silenciosamente o lista al final.
- Match vacío en ambos lados → mostrar "No hay intercambio posible".
- Match solo en un lado (yo le puedo dar pero él no me puede dar nada) → permitir igual con confirmación explícita.
- Cantidades en cero después del ajuste → no aplicar esa transacción.
- Confirmar sin cambios (todo en cero) → cancelar sin aplicar nada.

---

## Migración futura a v1.0 (cloud)

Cuando llegue el momento, los pasos serán:

1. **Servidor REST** expone endpoints `/users/me/inventory/snapshot` que devuelve un `InventorySnapshot`.
2. **App cliente** consume dos snapshots (el suyo y el del otro usuario tras invitación aceptada).
3. **`MatchingService` se reusa tal cual** (función pura, no le importa el origen).
4. **`exchange_event_id`** se reemplaza por UUID server-side.
5. **Archivos `.colexchange`** se mantienen disponibles como fallback offline durante la transición.

El diseño de v0.2 está pensado para minimizar el costo de esta migración.
