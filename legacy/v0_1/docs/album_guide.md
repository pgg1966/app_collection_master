# Guía del Álbum PDF

El cliente tiene un tab **Álbum** que genera dos tipos de PDF
imprimibles y dos listas TXT exportables a partir del catálogo de
cards y el inventario.

## Álbum de Únicas

PDF A4 vertical con TODAS las cards de la colección, agrupadas por
`code_id` (cada grupo arranca en una nueva página).

Cada slot de card muestra:

```
┌──────────────────────┐
│                      │
│   [ESCUDO DEL CODE]  │  ← PNG con alpha sobre fondo
│   centrado, ~60% del │
│   alto del slot      │
│                      │
│ ──── separador ────  │
│ #NUM  NOMBRE JUGADOR │
└──────────────────────┘
```

- **Fondo celeste** (`#b8d4e8`) si la card está en el inventario.
- **Fondo blanco hueso** (`#f5f5f0`) si falta.
- **Escudo** del `code_id`: lo provee `get_crest_path(code_id)`. Si
  no existe, el slot queda solo con el fondo + el `#NUM NOMBRE`.

### Header y footer de página

- **Header oscuro** (`#2c3e50`) de 12mm con:
  - Nombre del grupo a la izquierda en blanco bold.
  - "Pág. N" a la derecha en blanco regular.
- **Footer gris** de 6mm con nombre de la colección + fecha local.

### Layout configurable

```
Layout: [4 ▼] cols × [3 ▼] filas = 12 por página
```

Cambiá `cols` y `rows` antes de generar. Default = 4×3 = 12.

### Filtros

| Checkbox | Efecto |
|---|---|
| **Tengo** | Incluye cards con `quantity ≥ 1`. |
| **Faltan** | Incluye cards con `quantity = 0`. |

Por defecto ambos están activos (álbum completo).

### Generar

1. Click **📄 Generar álbum de únicas**.
2. Elegí destino (default
   `album_unicas_{collection}_{YYYY-MM-DD}.pdf`).
3. La generación corre en un `QThread` con `QProgressDialog` cancelable.
4. Al terminar, el PDF se abre automáticamente con el visor del SO.

## Álbum de Repetidas

Mismo layout que el principal, pero **solo cards con `quantity > 1`**.
Cada slot incluye un **badge circular rojo** con `x{N}` en la esquina
superior derecha indicando cuántas copias EXTRAS tenés (`N = qty - 1`).

Si no tenés repetidas, el cliente muestra un diálogo informativo y
**no abre** el FileDialog (evita generar un PDF vacío). En el caso
poco común que se invoque sin repetidas, el PDF generado tiene una
sola página con el mensaje `"No tenés repetidas en esta colección."`.

## Exportar listas TXT

### Lista de faltantes

Click **📋 Lista de faltantes** → guardar como
`faltantes_{collection}_{YYYY-MM-DD}.txt`.

Formato:

```
═══════════════════════════════════
FALTANTES — FIFA WC 2026 Adrenalyn XL
Generado: 2026-04-30 14:11:32
Total faltantes: 618 / 630
═══════════════════════════════════

ARGENTINA (ARG)
  #22  JULIAN ALVAREZ
  #26  NAHUEL MOLINA

BRAZIL (BRA)
  #73  ALISSON
  …
```

Pensado para copiar y pegar en mensajes a otros coleccionistas.

### Lista de repetidas

Click **📋 Lista de repetidas** → guardar como
`repetidas_{collection}_{YYYY-MM-DD}.txt`.

Formato:

```
═══════════════════════════════════
REPETIDAS — FIFA WC 2026 Adrenalyn XL
Generado: 2026-04-30 14:11:32
Total copias extra: 4
═══════════════════════════════════

ARGENTINA (ARG)
  #24  LIONEL MESSI .................. ×2
  #28  EMI MARTINEZ .................. ×1
```

`×N` indica cuántas copias EXTRAS tenés (qty - 1).

Tras exportar, el archivo se abre automáticamente con el editor de
texto del sistema operativo.

## Info de escudos

La sección inferior del tab muestra cuántos códigos de la colección
tienen escudo cargado:

```
Escudos cargados: 41 / 51 (80.4%)
Los códigos sin escudo se renderizan solo con número y nombre.
```

Si no hay ninguno, sugiere ir al admin → **Escudos** para configurarlos.

## Troubleshooting

- **El PDF tarda mucho**: 600+ cards toman varios segundos. La barra
  de progreso muestra cards procesadas / total.
- **El escudo se ve recortado**: el PNG no es cuadrado. La app
  preserva aspect ratio; si querés rellenar el slot, usá un PNG
  cuadrado al importar.
- **No se abre el PDF al terminar**: el SO no tiene un visor por
  defecto asociado a `.pdf`. Abrilo manualmente desde el path que
  reporta el diálogo.
