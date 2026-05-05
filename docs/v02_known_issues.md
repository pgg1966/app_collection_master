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

## Plantilla para próximas issues

```markdown
## #NNN — Título corto

- Archivo: ruta:línea
- Síntoma: ...
- Categoría: rompe integración / no la rompe
- Propuesta de fix: ...
- Estado: pendiente / resuelto en commit X
```
