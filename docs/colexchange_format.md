# Formato `.colexchange` — especificación pública

> Especificación del formato de archivo `.colexchange` usado por **Collections App** para el intercambio offline de inventarios entre dos coleccionistas.
>
> Este documento describe la **estructura del archivo** y las **reglas de validación** que aplica el importador. **No** describe el algoritmo de firma ni la clave usada para firmar el archivo: la firma existe para que la app pueda detectar archivos que no fueron generados por ella, y publicar el algoritmo de firma anularía esa garantía.

---

## 1. Visión general

Un archivo `.colexchange` es un documento **JSON UTF-8** que contiene:

- Metadata sobre la app que lo generó y la colección a la que se refiere.
- La lista de cards **faltantes** del usuario que exportó (lo que necesita).
- La lista de cards **repetidas** del usuario que exportó (lo que tiene de más).
- Una **firma** que la app usa para verificar autenticidad y detectar manipulación.

El archivo es **portable** y **offline**: se puede enviar por cualquier canal (email, WhatsApp, USB, etc.) y abrirse en otra instalación de la app que tenga la misma colección instalada.

### Qué NO contiene

- No contiene el inventario completo del usuario (solo faltantes y duplicados).
- No contiene paths locales, IDs internos de base de datos, ni datos personales más allá de un label opcional libre.
- No contiene fotos ni cualquier otro recurso binario.

---

## 2. Estructura del JSON

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
  "signature": "..."
}
```

---

## 3. Campos del nivel raíz

| Campo                     | Tipo            | Obligatorio | Descripción |
|---------------------------|-----------------|-------------|-------------|
| `format`                  | string          | sí          | Identificador fijo. Debe ser exactamente `"collections_app_exchange"`. |
| `format_version`          | int             | sí          | Versión del schema del archivo. Entero positivo (≥ 1). En v0.2 vale `1`. |
| `exported_at`             | string ISO 8601 | sí          | Timestamp UTC de generación, sin zona (ej. `"2026-05-15T14:30:00"`). |
| `exported_by_app_version` | string          | sí          | Versión de la app que generó el archivo (ej. `"0.2.0"`). Informativo. |
| `collection`              | object          | sí          | Bloque que identifica la colección a la que pertenece este intercambio. Ver §4. |
| `user_label`              | string \| null  | no          | Etiqueta libre del usuario que exportó (ej. `"PGG"`, `"Juan"`). Útil para que el receptor sepa quién mandó el archivo. Puede omitirse o ser `null`. |
| `missing`                 | array           | sí          | Lista de cards que el usuario que exportó **necesita**. Puede estar vacía. Ver §5. |
| `duplicates`              | array           | sí          | Lista de cards que el usuario que exportó **tiene de más**. Puede estar vacía. Ver §6. |
| `signature`               | string          | sí          | Firma generada por la app sobre el contenido del archivo. Permite a la app detectar archivos no generados por ella o manipulados. El valor exacto y su cálculo no son parte de esta especificación pública. |

---

## 4. Bloque `collection`

| Campo            | Tipo   | Obligatorio | Descripción |
|------------------|--------|-------------|-------------|
| `name`           | string | sí          | Nombre de la colección. **Debe coincidir** con el nombre de una colección instalada localmente para poder importar el archivo. |
| `card_count`     | int    | sí          | Cantidad total de cards del catálogo de la colección. Informativo (ayuda al receptor a confirmar que las dos apps tienen el mismo álbum). |

---

## 5. Entradas de `missing`

Cada entrada de `missing` describe **una card del catálogo** que el exportador **no posee** (o de la que necesita más unidades) y que estaría dispuesto a recibir en un intercambio.

| Campo             | Tipo   | Obligatorio | Descripción |
|-------------------|--------|-------------|-------------|
| `code_id`         | string | sí          | Código que identifica la sub-sección dentro de la colección (ej. el país en un álbum del Mundial: `"ARG"`, `"BRA"`). Si la colección no usa códigos, el exportador completa este campo con un valor estable. |
| `card_number`     | int    | sí          | Número de la card dentro del `code_id`. Junto con `code_id` identifica unívocamente una card del catálogo. |
| `card_name`       | string | sí          | Nombre de la card. Informativo (la identidad sigue siendo `code_id` + `card_number`). |
| `needed_quantity` | int    | sí          | Cuántas unidades necesita el exportador. Mínimo `1`. |

---

## 6. Entradas de `duplicates`

Cada entrada de `duplicates` describe **una card del catálogo** que el exportador **tiene en exceso** y que estaría dispuesto a entregar en un intercambio.

| Campo                | Tipo   | Obligatorio | Descripción |
|----------------------|--------|-------------|-------------|
| `code_id`            | string | sí          | Igual que en `missing`. |
| `card_number`        | int    | sí          | Igual que en `missing`. |
| `card_name`          | string | sí          | Igual que en `missing`. |
| `available_quantity` | int    | sí          | Cuántas unidades tiene de más disponibles para intercambio. Mínimo `1`. La unidad que ocupa el lugar en el álbum **no** se cuenta como duplicado. |

---

## 7. Validación al importar

El importador aplica las siguientes verificaciones en orden. Si alguna falla, se rechaza el archivo y **no se modifica nada en la base local**.

1. **JSON parsea**: el archivo debe ser JSON UTF-8 válido. Falla → `Archivo inválido: JSON malformado`.
2. **`format` correcto**: debe ser exactamente `"collections_app_exchange"`. Falla → `Archivo inválido o no generado por esta aplicación`.
3. **`format_version` presente y bien formada**: entero ≥ 1. Falla → `Archivo inválido: campo "format_version" ausente o incorrecto`.
4. **`format_version` soportada**: la app actual soporta versiones hasta un cierto número (en v0.2: `1`). Si el archivo declara una versión mayor, se rechaza pidiendo al usuario que actualice la app. Falla → `Archivo de versión N — esta app soporta hasta versión M. Actualizá la app para abrirlo`.
5. **Firma válida**: la app calcula la firma esperada sobre el contenido y la compara con el campo `signature`. Falla → `Archivo inválido o no generado por esta aplicación`.
6. **Colección existente**: el `collection.name` del archivo debe coincidir con una colección instalada localmente. Falla → `La colección «X» no está instalada en esta app`.
7. **Cards conocidas**: las cards de `missing` y `duplicates` que **no existen** en el catálogo local se omiten silenciosamente del cómputo de matching y se reportan al usuario como **advertencias** (no detienen el import). Esto cubre tipográficos del exportador y diferencias menores de catálogo.

---

## 8. Reglas de versionado

- `format_version` es un entero monótono creciente. Cada cambio incompatible con el formato anterior incrementa el número.
- Una app que entiende hasta la versión `N` debe **rechazar** archivos de versión `> N` con un mensaje que pida al usuario actualizar.
- Una app puede aceptar archivos de versiones anteriores siempre que las haya documentado como compatibles.
- v0.2 de Collections App soporta hasta `format_version: 1`.

---

## 9. Reglas que el importador asume sobre el contenido

Estas reglas son responsabilidad del **exportador**. El importador no las re-valida exhaustivamente.

- Una misma card (mismo `code_id` + `card_number`) **no aparece simultáneamente** en `missing` y en `duplicates` del mismo archivo (un usuario o necesita una card o le sobra, no ambas).
- Las cantidades (`needed_quantity`, `available_quantity`) son enteros positivos.
- `exported_at` está en UTC.

---

## 10. Convención de nombre de archivo

El exportador genera el archivo con la forma:

```
{collection_name}_{user_label}_{YYYY-MM-DD}.colexchange
```

Caracteres no válidos en el sistema de archivos del exportador (`<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`, espacios) se reemplazan por `_`. Por ejemplo:

```
Mundial_2026_PGG_2026-05-15.colexchange
```

Esta convención es informativa: el importador acepta cualquier nombre de archivo con extensión `.colexchange` (o sin ella, si el usuario la quitó al renombrar).
