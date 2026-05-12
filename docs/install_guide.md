# Cómo instalar Collections App

Guía para usuarios finales (Windows 10 / 11, 64-bit).

## Instalación

1. Descargá `CollectionsApp.exe` desde:
   https://github.com/pgg1966/app_collection_master/releases/latest

2. Guardalo donde quieras (Escritorio, Documentos, etc.). No necesita
   instalador: es un único archivo standalone.

3. Doble-click en `CollectionsApp.exe`.

4. Si Windows muestra "Windows protegió tu PC" (SmartScreen):
   - Click en **"Más información"**
   - Click en **"Ejecutar de todas formas"**

   Esto pasa porque el ejecutable no está firmado con un certificado
   comercial. Es normal y seguro.

5. La primera vez puede tardar 10-20 segundos en abrir (extrae el
   bundle a una carpeta temporal). Las siguientes veces es instantáneo.

## Tus datos

Todos los datos se guardan en:

    C:\Users\<tu usuario>\AppData\Roaming\Collections\

Contenido típico:
- `collections.db` — la base de datos (default sin profile).
- `collections_<nombre>.db` — bases de datos adicionales si usás
  perfiles.
- `images/` — imágenes de guía OCR de cada colección.
- `models/` — modelos OCR (si configurás reconocimiento por foto).

**Para hacer backup:** copiá esa carpeta entera a un pendrive o nube.
**Para migrar a otra PC:** copiá la misma carpeta en la nueva máquina,
en la misma ubicación.

## Para usar la carga de fotos con OCR (opcional)

La carga por foto requiere instalar software adicional (~900 MB) que
no viene en el `.exe` para mantenerlo liviano.

### Requisito previo: Python 3.11+

El reconocimiento por foto necesita Python instalado en el sistema.

1. Descargá Python desde https://www.python.org/downloads/
2. Durante la instalación, marcá la casilla
   **"Add Python to PATH"** (importante).
3. Reiniciá la máquina (recomendado).

### Instalación de las dependencias de OCR

1. Abrí Collections App.
2. Andá a la tab **"Cargas"** → sub-tab **"Por foto"**.
3. Click en **"Instalar dependencias"**.
4. La instalación tarda varios minutos según tu conexión (~900 MB de
   descarga).
5. La primera vez que uses el OCR necesitás conexión a internet
   (descarga un modelo de lectura de texto, solo la primera vez).

Si el botón "Instalar dependencias" muestra un error sobre Python no
encontrado, instalá Python siguiendo el paso anterior y reabrí la app.

## Problemas comunes

**"Windows protegió tu PC" al abrir.**
Normal — ver paso 4 de la instalación.

**La app abre pero la tab "Por foto" muestra "Instalar dependencias".**
Eso es el estado inicial. Si querés usar OCR, seguí la sección de
instalación de OCR; si no, ignoralo (todas las demás funciones andan
sin instalar nada extra).

**"No se encontró Python en el sistema" al instalar OCR.**
Falta Python. Instalalo desde python.org marcando "Add Python to PATH"
y reabrí la app.

**Perdí mis datos al reinstalar.**
Los datos viven en `%APPDATA%\Collections\`, no en la carpeta del
`.exe`. Reinstalar la app no los borra. Para borrarlos hay que eliminar
esa carpeta a mano.
