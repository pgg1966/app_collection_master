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

## #002 — RESUELTO: Slowdown patológico de `QTableWidget.setItem` post-modal

- **Estado:** RESUELTO (2026-05-07).
- **Resolución:**
  - Causa raíz confirmada experimentalmente: `QTableWidget.setItem`
    en loops masivos post-cierre de modal disparaba style cascade
    re-evaluation por celda, escalando el costo a ~280ms/setItem
    (vs ~0.1ms en estado limpio).
  - Refactor aplicado a Modelo/Vista nativo de Qt:
    [InventoryTab](../src/collections_app/views/collections/inventory_tab.py)
    (commit `fdb2c2c`) y
    [HistoryTab](../src/collections_app/views/collections/history_tab.py)
    (commit `441f8ac`) migrados de `QTableWidget` a
    `QTableView` + `QAbstractTableModel`. El llenado masivo se hace
    via `beginResetModel/endResetModel` (UNA operación), bypassando
    el path patológico.
  - Validación experimental (2026-05-07): import de 258 cards reales
    via Excel → cierre del dialog en <2s. Menú admin reactivado
    temporalmente confirmó que las 3 ABM (Cards, Colecciones, Códigos)
    también funcionan rápido tras el refactor.
  - La regla 2.8 de CLAUDE.md formaliza la lección: tablas con
    datasets >500 filas DEBEN usar QTableView+modelo.
- **Diagnóstico granular (referencia histórica)** — el detalle del
  proceso de debugging se preserva acá por valor para sesiones
  futuras que enfrenten síntomas similares.
- **Archivos afectados originalmente:** todas las vistas que
  repueblan tablas grandes tras cerrar un `QDialog` modal.
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
- **Estado final:** RESUELTO en raíz por el refactor a QTableView +
  QAbstractTableModel (ver bloque "Resolución" al inicio del issue).
  El menú admin permanece deshabilitado por default vía
  `COLLECTIONS_ADMIN` (decisión arquitectónica de separación
  admin/usuario para Camino C, no por el bug). Los fixes commiteados
  `3aff4aa` (QTimer defer) y `3b1ea74` (setUpdatesEnabled) quedan en
  el código como defensa preventiva — son práctica estándar de Qt y
  no dañan, aunque ya no son la línea de defensa principal.

---

## #003 — Vistas pendientes de migrar a QTableView+QAbstractTableModel

**Estado:** Deuda técnica menor.

**Vistas afectadas:**
- StatsView (52 filas, no exhibe el bug en práctica).
- ReportsView (usa QTextEdit en realidad, no QTableWidget — verificar).
- 3 ABM administrativas: CardsAbmView, CollectionsAbmView, CodesMasterDetailView (deshabilitadas por default vía COLLECTIONS_ADMIN, no exhiben el bug en condiciones normales).

**Razón de la deuda:**
Tras el refactor de InventoryTab+HistoryTab y validación experimental con menú admin reactivado, se confirmó que estas vistas no exhiben el bug del issue #002 en la práctica. Se deja la migración como deuda para no escalar trabajo sin valor inmediato.

**Cuándo abordar:**
- Si se reactiva permanentemente el menú admin.
- Si las vistas crecen significativamente en datasets (>500 filas).
- Como parte del "limpieza pre-1.0" antes de release público.

**Approach:** aplicar el mismo patrón de migración usado en commits `fdb2c2c` (InventoryTab) y `441f8ac` (HistoryTab).

---

## Nota informativa — `ocr_python_exe` huérfano en DBs pre-7e

**Contexto:** entre Prompt 7c y 7d, `OcrInstallService.install()`
persistía en `app_settings` la key `ocr_python_exe` con la ruta al
Python del sistema que se usaba para correr pip + chequear las deps.
A partir del Prompt 7e (torch incluido en el bundle), `install()` se
eliminó y la key ya no se escribe ni se lee.

**Síntoma:** las DBs creadas con un build entre 7c y 7d pueden tener
una fila `app_settings (setting_key='ocr_python_exe', setting_value=...)`
huérfana.

**Impacto:** ninguno. La app ya no consulta esa key; queda como ruido
inocuo en la tabla.

**Decisión:** no migrar. Sin SQL de limpieza. Si en un cleanup
post-1.0 se decide normalizar `app_settings`, agregar un `DELETE FROM
app_settings WHERE setting_key = 'ocr_python_exe'` en la migración.

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
