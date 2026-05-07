# v0.2 — Issues heredados detectados durante integración

> Bugs / observaciones encontradas al integrar módulos preservados de
> v0.1 a v0.2 (CLAUDE.md sec 7.1). No se arreglan en la sesión de
> integración salvo que rompan la integración.

---

## #001 — `_save_card` solo atrapaba `ValueError`

- **Archivo:** [src/collections_app/views/inventory/card_loader.py:809](../src/collections_app/views/inventory/card_loader.py#L809)
- **Síntoma:** El bloque `try/except` en `_save_card` solo manejaba
  `AmbiguousCardError` y `ValueError`. En v0.1 alcanzaba porque el
  `InventoryService` legacy levantaba `ValueError` para todos los
  casos de error. En v0.2 los services levantan `InventoryError`
  (subclase de `ServiceError`); cualquier alta sobre card inexistente
  o baja sin stock suficiente provocaba un crash propagado fuera de
  la vista.
- **Categoría:** rompe la integración (cualquier flujo de error
  estándar crashea el slot de save).
- **Decisión:** **fix mínimo aplicado** durante esta sesión —
  agregada cláusula `except InventoryError as exc` con el mismo
  tratamiento que la cláusula `ValueError` original (status label en
  rojo + return). La cláusula `ValueError` se conserva como red de
  seguridad por si algún caller futuro la levanta. Comentario en el
  código documenta la adaptación.
- **Estado:** resuelto (commit del paso 11 del Prompt 2).

---

## #002 — Slowdown patológico de `QTableWidget.setItem` — relevante para futura herramienta admin

- **Decisión arquitectónica:** v0.2.0 distribuye solo la app de
  usuario. La gestión de catálogo (alta/baja/edición de cards, codes,
  collections) se va a hacer desde una herramienta admin separada que
  se construye post-Mundial. Esta separación coincide con la
  arquitectura del sistema anterior y resuelve el problema sin
  necesidad de fix técnico.
- **Archivos afectados:** todas las vistas que repueblan tablas grandes
  tras cerrar un `QDialog` modal.
  - [src/collections_app/views/collections/inventory_tab.py](../src/collections_app/views/collections/inventory_tab.py)
  - [src/collections_app/views/admin/cards_abm.py](../src/collections_app/views/admin/cards_abm.py)
  - [src/collections_app/views/admin/codes_master_detail.py](../src/collections_app/views/admin/codes_master_detail.py)
  - [src/collections_app/views/admin/collections_abm.py](../src/collections_app/views/admin/collections_abm.py)
- **Síntoma:** abrir alguna ABM (Cards / Colecciones / Códigos) contra
  un dataset real (`--profile mundial`, 994 cards) y cerrarla con X o
  con el botón Cerrar deja la `MainWindow` no respondiendo durante
  varios minutos. Solo el WM de Windows puede forzar el cierre.
- **Diagnóstico granular** (vía instrumentación temporal con `print`
  a `stderr` en `_set_row` de `InventoryTab`):
  - Refresh inicial (estado limpio): `setItem` ~0.1ms, 994 cards en
    ~170ms total.
  - Refresh post-modal: `setItem` ~73ms cada uno (294ms / 4 setItems
    por fila), constante de fila 0 a fila 993. Proyección a 994 cards:
    ~7 minutos. El comportamiento es lineal en N (no cuadrático), pero
    la constante por `setItem` es 700× la baseline.
- **QTBUGs upstream relacionados** (ninguno reproduce idénticamente
  nuestro escenario, pero los tres juntos describen el área del bug):
  - [QTBUG-126543](https://bugreports.qt.io/browse/QTBUG-126543) —
    estilo `windows11` ignora `Qt::ForegroundRole` en `QTableView`.
  - [QTBUG-123632](https://bugreports.qt.io/browse/QTBUG-123632) —
    setear background de un item rompe `alternatingRowColors`.
  - [QTBUG-126530](https://bugreports.qt.io/browse/QTBUG-126530) —
    crecimiento de memoria con accesibilidad habilitada.
- **Fixes intentados sin éxito** (en orden cronológico):
  1. Override de `closeEvent` para simetrizar X-close vs botón Cerrar
     en las ABM. Revertido — el bug persiste con cualquier path de
     cierre, no era asimetría.
  2. `QTimer.singleShot(0, refresh)` para diferir el refresh al
     próximo tick del event loop. **Mantenido** (commit `3aff4aa`) — no
     resuelve el bug pero protege contra el caso teórico de deadlock
     con el teardown del modal y no daña.
  3. `setUpdatesEnabled(False/True)` envolviendo el bulk insert para
     suprimir repaints intermedios. **Mantenido** (commit `3b1ea74`) —
     no resuelve el bug porque el costo no está en el repaint sino en
     el `setItem` mismo, pero es práctica estándar de Qt y no daña.
  4. `style.unpolish + style.polish` antes del bulk insert para
     regenerar el cache de paleta heredada upfront. Revertido — no
     resuelve.
  5. `blockSignals(True/False)` envolviendo el bulk insert para
     silenciar `itemChanged` / `cellChanged` internos. Revertido — no
     resuelve.
  6. `app.setStyle("Fusion")` para bypassear el motor `windows11`.
     Revertido — no resuelve.
  7. `QT_ACCESSIBILITY=0` antes del import de PySide6 para deshabilitar
     el bridge a Windows UI Automation. Revertido — no resuelve.
  8. Combinación Fusion + `QT_ACCESSIBILITY=0` simultáneos. Revertido
     — no resuelve.
- **Workaround vigente (D):** las tres acciones del menú
  "Administración" están deshabilitadas (`setEnabled(False)` con
  tooltip explicativo). Los slots `_open_*_abm` quedan en
  [main_window.py](../src/collections_app/views/main_window.py) para
  reactivación trivial cuando haya fix real. La carga de datos sigue
  siendo posible vía CSV import (Archivo → Nueva colección desde
  CSV...). El refresh de los tabs del detail view sigue funcionando
  (no es modal → no dispara el bug).
- **Cuando se aborde:** sesión dedicada para construir la herramienta
  admin separada. Approach probable: app standalone con
  `QTableView`+`QStandardItemModel` desde el principio (el bug está
  en `QTableWidget`; `QTableView` con modelo explícito no lo exhibe
  según documentación de Qt y reportes upstream). Comparte los
  servicios y la DB con la app de usuario, pero tiene su propio entry
  point y sus propias vistas.
- **Reproducción mínima:** `python -m collections_app.main --profile
  mundial`, abrir Cards desde el menú deshabilitado (requiere
  re-habilitar la action manualmente para reproducir), esperar la
  carga (~170ms), cerrar con X o Cerrar, observar la `MainWindow`
  congelada varios minutos.
- **Estado:** no bloqueante para v0.2.0; las ABM no son parte de la
  app distribuible. Relevante cuando se construya la herramienta
  admin separada. Workaround D activo (menú deshabilitado en
  MainWindow). Los fixes commiteados #2 y #3 (QTimer +
  setUpdatesEnabled, commits 3aff4aa y 3b1ea74) quedan en el código
  como defensa preventiva por si el path post-modal aparece en otro
  contexto.

---

## Plantilla para próximas issues

```markdown
## #NNN — Título corto

- Archivo: ruta:línea
- Síntoma: ...
- Categoría: rompe integración / no la rompe
- Propuesta de fix: ...
- Estado: pendiente / resuelto en commit X
```
