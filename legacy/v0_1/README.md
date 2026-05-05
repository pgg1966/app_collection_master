# legacy/v0_1/

Snapshot del código y documentación de v0.1, archivado al iniciar el rewrite v0.2.0.

## Por qué está acá

v0.2.0 es un rewrite arquitectónico. La auditoría de v0.1 detectó deuda
significativa (PKs compuestas en todas las tablas de dominio, columnas que
guardan nombres de otras columnas, datos duplicados "por las dudas",
vistas que importan repositorios, etc.). Conservamos v0.1 acá porque:

1. La integración del módulo preservado (`preserved/card_loader.py`) en v0.2
   va a necesitar mirar cómo cableaba el `InventoryService` original.
2. La documentación (`docs/`) describe convenciones de v0.1 que sirven de
   referencia histórica para entender por qué v0.2 invierte ciertas decisiones.
3. Si en algún momento necesitamos resucitar una funcionalidad puntual
   (ej. importadores, scrapers, reportes PDF), tenemos el código a mano.

## Qué hay adentro

```
legacy/v0_1/
├── README.md              # este archivo
├── src/
│   └── collections_app/   # paquete fuente original
├── tests/                 # tests originales (espejo de src/)
├── docs/                  # documentación de v0.1 (architecture.md, abm_widget_guide.md, etc.)
└── preserved/
    ├── README.md          # detalle del único módulo preservado
    └── card_loader.py     # CardLoaderView — pantalla de alta de stock
```

## Política

- **No se ejecuta** desde acá. `pytest` no recorre `legacy/`.
- **No se modifica.** Si encontrás un bug o una regla que querés actualizar,
  hacelo en v0.2; este árbol queda congelado.
- **Se elimina** cuando v0.2 alcance paridad funcional. La pantalla preservada
  se elimina cuando se integra con éxito en `src/collections_app/views/`.

## Stash relacionado

Al iniciar el bootstrap se stashearon cambios pendientes sobre `csv_importer.py`
con el mensaje `v0.1 WIP - csv_importer`. Recuperables con `git stash list`.
