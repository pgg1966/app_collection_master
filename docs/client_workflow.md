# Workflow del cliente

Esta guía describe los cuatro tabs de `collections-client` y el flujo
típico de uso.

## 0. Arrancar la app

```bash
collections-client
```

La primera vez (o si la colección activa no está desbloqueada) abre el
**ClientSettingsDialog** automáticamente. Elegí una colección (y validá
la licencia si es premium) y aceptá. La elección queda persistida en
`app_settings`; la próxima vez que abras la app, te lleva directo al
último estado.

## 1. Tab "Cargar Cards"

Pantalla principal. Carga rápida con Enter:

- **Operación**: Alta (default) o Baja. Atajos `Alt+A` / `Alt+B`.
- **Número**: tipear → autocompleta país y nombre, muestra status:
  - Verde: "Nueva" (no la tenés).
  - Coral: "Repetida · tenés N".
  - Ámbar: "Número X no existe en esta colección".
- **Cantidad**: default `1`. Enter en este campo guarda la operación.

Si la colección requiere código (estilo Stickers Panini), el campo
"Código" aparece arriba de "Número". Si la colección NO requiere código
y un número está en varios códigos a la vez, aparece un combo limitado
para que elijas cuál.

Cada save dispara la señal `card_changed`, que refresca **Inventario** y
**Estadísticas** automáticamente.

## 2. Tab "Inventario"

Lista todas las cards del catálogo con su estado actual.

Filtros (se combinan con AND):
- **Estado**: Todas / Tengo / Faltan / Repetidas.
- **Código**: Todas / `ARG` / `BRA` / …
- **Buscar**: substring del nombre, case insensitive.

Color por fila según estado:
- Tengo (qty=1) → blanco.
- Repetida (qty>1) → crema claro.
- Falta (qty=0) → gris muy claro.

Status bar inferior:
> Total: 630 cards | Tengo: 12 (1.9%) | Faltan: 618 | Repetidas: 3

Click en columnas para ordenar ascendente; click again para descendente.

## 3. Tab "Estadísticas"

- **Progreso general**: barra global de `owned/total` con porcentaje.
- **Por código**: una barra por cada código del header con `owned/total
  (pct%)`.
- **Top repetidas**: top 10 cards con mayor cantidad.
- **Resumen de inventario**: total de figuritas físicas, cards únicas
  poseídas, copias extras.

Auto-refresh al cargar/quitar cards desde "Cargar Cards".

## 4. Tab "Reportes"

Bitácora de altas/bajas con filtros de período y operación.

Presets de período (combo):
- Hoy, Últimos 7 días (default), Últimos 30 días, Este mes, Mes anterior,
  Personalizado…

Custom: muestra date editors `Desde` / `Hasta` (calendario popup).

Filtro de operación: Todas / Alta / Baja.

Grilla con columnas:

| Fecha (local) | Op | Code | Nombre | Cant |
|--|--|--|--|--|
| 2026-04-30 14:11 | Alta | ARG-24 | LIONEL MESSI | 1 |
| 2026-04-30 14:10 | Alta | ARG-25 | EMI MARTINEZ | 1 |
| ... |

**Exportar a CSV**: botón abajo a la derecha. El CSV incluye:
- Fila 0: comentario con `# {nombre_colección}, desde=…, hasta=…` (en
  hora local).
- Fila 1: header `fecha,operacion,codigo,numero,nombre,cantidad`.
- Resto: una fila por transacción. Las fechas en formato ISO con offset
  de zona horaria local.

**Reportes NO se auto-refresca** al cargar cards en otro tab — el período
es estable durante una sesión. Para ver lo nuevo, cambiá un filtro o
re-seleccioná el preset.

## E2E completo

1. Abrir `collections-client`, elegir colección.
2. **Cargar Cards** → tipear `24` + Enter → ver "ARGENTINA / LIONEL
   MESSI / Nueva" → Enter → guarda. Repetir con `25` y `26`. Volver a
   `24` → "Repetida · tenés 1" → Enter → ahora 2.
3. **Inventario** → ver `ARG-24` con cantidad 2 ("Repetida"), `ARG-25` y
   `ARG-26` con cantidad 1 ("Tengo"). Filtrar "Repetidas" → solo `24`.
4. **Estadísticas** → progreso 3/630 (0.5%). Top repetidas: `ARG-24
   LIONEL MESSI x2`.
5. **Reportes** → preset "Últimos 7 días" muestra 4 transacciones (3
   altas de números distintos + 1 alta repitiendo `24`).
6. Volver a Cargar, `Alt+B` (Baja), `24` Enter Enter → resta. Total: 1.
7. Reportes refresca (cambiando filtro) → ahora 5 transacciones (1 baja
   adicional).
8. Cerrar y abrir el cliente → estado persistido (colección activa,
   inventario, transactions).
