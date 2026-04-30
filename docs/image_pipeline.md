# Pipeline de generación de imágenes

El admin genera automáticamente las imágenes para todas las cards del
álbum. El cliente solo las consume (no genera nada). El proceso corre
una sola vez al preparar la colección y queda cacheado en disco.

## ¿Por qué en el admin?

- Pesa: descargar fotos + procesarlas con OpenCV + componer es lento.
- Necesita internet: la app cliente puede correr offline.
- Requiere supervisión humana: el log debe mirarse para detectar
  jugadores que cayeron al placeholder.

## Tres etapas en cascada

### 1. PhotoFinder

Busca y descarga la mejor foto disponible para cada jugador. Fallback
en cascada:

| Orden | Fuente        | Cómo                                    |
|-------|---------------|------------------------------------------|
| 1     | Caché local   | `data/photo_cache/{card_key}.jpg`        |
| 2     | DuckDuckGo    | `DDGS().images(query, type_image=photo)` |
| 3     | Wikipedia API | `/api/rest_v1/page/summary/{name}`       |
| 4     | Placeholder   | Imagen B&W generada con PIL              |

Una imagen se considera válida si:
- Status HTTP 200.
- OpenCV puede decodificarla (`cv2.imread` retorna no-None).
- Sus dimensiones son ≥ 100x100.

Si no, se descarta y se prueba la siguiente URL/fuente.

### 2. SketchGenerator (Nivel 3)

Convierte una foto a sketch artístico B&W:

1. **Face detection**: Haar cascade frontal. Recorta con +40% arriba
   (cabello), +20% lados, +10% abajo. Si no detecta cara, usa la
   imagen completa.
2. **Edge-preserving filter**: `cv2.edgePreservingFilter(sigma_s=60,
   sigma_r=0.4)` suaviza zonas planas sin perder bordes.
3. **Pencil dodge & burn**: invertir + Gaussian blur + division.
4. **Bordes Canny**: `cv2.Canny(30, 100)` + dilate 2x2 + oscurecer 60.
5. **Suavizado final**: GaussianBlur 3x3.
6. Resize manteniendo aspect ratio a 260x310 con padding blanco.

### 3. CardComposer

Compone la imagen final 280x380 px:

```
┌──────────────────────────────┐
│ marco gris 2px               │
│ ┌──────────────────────────┐ │
│ │  fondo (celeste o gris)  │ │
│ │  [SKETCH B&W centrado]   │ │
│ │                          │ │
│ │  ─── separador ───       │ │
│ │  [#NUM] NOMBRE TRUNC…    │ │
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

- Fondo: celeste (`#ADD8E6`) si la card está en inventory; gris claro
  (`#F5F5F5`) si falta.
- Caja oscura para el número, label en negro.
- `compose_with_duplicate_badge` agrega un círculo rojo "x{n}" en la
  esquina superior derecha cuando `quantity > 1`.

## Directorio de salida

Cada colección tiene su propio subdirectorio:

```
%APPDATA%/Collections/generated_cards/
├── 1/             ← collection_id 1
│   ├── ARG-1.png
│   ├── ARG-2.png
│   └── ...
└── 2/
    └── ...
```

Helpers en [`core/utils/paths.py`](../src/collections_app/core/utils/paths.py):

```python
from collections_app.core.utils.paths import (
    get_generated_cards_dir,
    get_generated_card_path,
)

dir_for_collection = get_generated_cards_dir(1)
specific_card = get_generated_card_path(1, "ARG-24")
```

El cliente debe priorizar:
1. Si existe `get_generated_card_path(cid, key)` → usarlo (sketch).
2. Si no, `inventory.image_path` (foto subida por el usuario).
3. Si tampoco → slot vacío con número.

## UI del admin

Tab "Generar Imágenes" en `collections-admin`:

- Combo de colección: muestra "X / Y (Z%)" generadas.
- Botón **Generar pendientes**: solo procesa las cards sin PNG aún.
- Botón **Regenerar todas**: pide confirmación; force=True.
- Botón **Detener**: pide al worker que pare al terminar la card en curso.
- Log con timestamp + card_key + fuente + ✓/✗ (color por nivel).

El log truncado a 500 líneas (auto-scroll). El procesamiento corre en
un `QThread` (`PipelineWorker`) — la UI no se bloquea.

## Cómo forzar regeneración de una card específica

Borrá su PNG del directorio:

```bash
rm "%APPDATA%/Collections/generated_cards/1/ARG-24.png"
```

Click en "Generar pendientes" → solo regenera ARG-24 (las demás siguen
en caché).

## Interpretar el log

```
[18:30:22] ARG-24 → duckduckgo ✓     # foto encontrada vía DDG
[18:30:23] ARG-25 → wikipedia ✓      # DDG falló, Wikipedia OK
[18:30:24] ARG-26 → cache ✓          # ya estaba descargada
[18:30:25] ALG-11 → placeholder ✓    # ninguna fuente devolvió foto válida
[18:30:26] XYZ-99 → error ✗ (...)    # error real (loggeado en errors[])
```

Las cards que cayeron al placeholder son **candidatas a revisar
manualmente**: editá su PNG en `generated_cards/{cid}/` o reemplazá la
foto cacheada en `data/photo_cache/{card_key}.jpg` y borrá el PNG para
que se regenere.

## Tests

Todos los tests del pipeline mockean internet:

- `test_photo_finder.py` usa `responses` para HTTP y `unittest.mock`
  para `_search_duckduckgo` (DDGS no es HTTP estándar).
- `test_sketch_generator.py` genera imágenes sintéticas con NumPy/OpenCV.
- `test_card_composer.py` verifica dimensiones, colores y formato PNG.
- `test_pipeline.py` inyecta mocks de finder/sketch/composer (DI por
  constructor) para no tocar internet ni OpenCV.
