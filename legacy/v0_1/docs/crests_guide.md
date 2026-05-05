# Guía de Escudos

Cada `code_id` (ej. `ARG`, `BRA`, `GBL`) tiene **un** escudo asociado en
formato PNG. El escudo se reutiliza en TODAS las cards de ese código y
en TODAS las colecciones que compartan el mismo header de códigos.

## Dónde se guardan los archivos

```
%APPDATA%\Collections\crests\
    ARG.png
    BRA.png
    GBL.png
    …
```

(En macOS/Linux: `~/Library/Application Support/Collections/crests/`
y `~/.local/share/Collections/crests/` respectivamente.)

Cada PNG es **RGBA 200×200** (con canal alpha para fondos
transparentes), creado o normalizado por la app.

## Búsqueda automática (Wikipedia)

En el admin, tab **Escudos**:

1. Seleccioná la colección.
2. Click en **🌐 Buscar automáticamente (países)**.
3. La app abre la API REST de Wikipedia inglesa para cada code que
   esté mapeado en `COUNTRY_WIKIPEDIA_MAP` y descarga el thumbnail
   del seleccionado nacional.
4. Rate limit: **1 segundo entre requests** para no abusar de la API.
5. La búsqueda corre en un QThread con `QProgressDialog` cancelable.

Solo se procesan códigos que:
- **No** están en `SPECIAL_CODES` (ver abajo).
- **No** tienen ya un escudo cacheado (la búsqueda no sobreescribe).

Al finalizar, la app reporta cuántos vinieron de Wikipedia y cuántos
quedaron como placeholder.

### Códigos especiales (sin equipo nacional)

```python
SPECIAL_CODES = {
    "GBL", "CON", "TKP", "DRK", "MMS", "GMC",
    "MRK", "EXC", "RTR", "FWC", "PAN", "CCO",
}
```

Estos sets temáticos (Golden Ballers, Master Picks, Coca Cola, etc.)
**no** tienen una página de equipo en Wikipedia. La búsqueda
automática los salta y la app genera un placeholder gris con las
iniciales del código. Para tener un escudo real hay que importarlo
manualmente.

## Importar manualmente

Cuando Wikipedia no encuentra el escudo (sets especiales o países que
fallaron) podés cargar la imagen desde una fuente local:

1. Click en una fila de la grilla.
2. Click en **📂 Importar imagen para code seleccionado**.
3. Elegir un PNG/JPG/SVG/WEBP local.
4. La app convierte a RGBA 200×200 (manteniendo aspect ratio) y
   sobreescribe el archivo en `crests/`.
5. La grilla y el preview se refrescan.

## Borrar un escudo

Click en una fila → **🗑️ Borrar escudo seleccionado** → confirmación.
Borra el PNG. La próxima búsqueda automática puede reintentar
(o se puede importar manualmente otra vez).

## Estados en la grilla

| Estado | Significado |
|---|---|
| **Sin escudo** | El PNG no existe; la card se renderizará en el PDF sin imagen. |
| **Wikipedia** | El escudo fue descargado automáticamente. |
| **Manual** | Importado por el usuario. |
| **Placeholder** | Generado por la app (círculo gris con iniciales). Indica que el code está en `SPECIAL_CODES` o que la búsqueda falló. |

## Mapeo de país → título Wikipedia

`COUNTRY_WIKIPEDIA_MAP` en
[crest_finder.py](../src/collections_app/admin/crests/crest_finder.py)
acepta los nombres de país en MAYÚSCULAS sin acentos (la forma que
produce el script `scripts/clean_csv.py`) y los traduce al título
exacto de la Wikipedia inglesa, p.ej.:

```python
"ARGENTINA":  "Argentina national football team"
"REP. COREA": "South Korea national football team"
"PAISES BAJOS": "Netherlands national football team"
```

Si agregás una colección con países nuevos, ampliá ese diccionario.

## Troubleshooting

- **El escudo descargado no es el adecuado**: borralo desde el botón
  🗑️ y luego importá uno manual.
- **Wikipedia no encuentra el país**: verificá que `code_name` esté
  en el mapping. Si no, agregalo.
- **El PNG quedó con fondo blanco en vez de transparente**: la
  imagen origen no tenía canal alpha. Importá una versión con
  transparencia o aceptá el resultado.
