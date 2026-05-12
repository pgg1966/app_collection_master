# Cómo instalar Collections App

Guía para usuarios finales (Windows 10 / 11, 64-bit).

## Instalación

1. Descargá `CollectionsApp.exe` desde:
   https://github.com/pgg1966/app_collection_master/releases/latest

2. Guardalo donde quieras (Escritorio, Documentos, etc.). No necesita
   instalador: es un único archivo standalone (~1 GB).

3. Doble-click en `CollectionsApp.exe`.

4. Si Windows muestra "Windows protegió tu PC" (SmartScreen):
   - Click en **"Más información"**
   - Click en **"Ejecutar de todas formas"**

   Esto pasa porque el ejecutable no está firmado con un certificado
   comercial. Es normal y seguro.

> **Primera vez:** la app puede tardar entre 30 y 60 segundos en abrir.
> Es normal — Windows está preparando los archivos y escaneándolos con
> el antivirus. Las veces siguientes abre más rápido.

## Colecciones disponibles

Al instalar la app encontrás ya cargadas:

- **Panini FIFA WC 2026 Stickers** (figuritas)
- **Panini FIFA WC 2026 Adrenalyn XL** (cards)

Solo tenés que cargar tu propio inventario (tab **"Cargas" → "Manual"**
o **"Por foto"**).

## Carga de fotos con OCR

El reconocimiento por foto **funciona out-of-the-box**. No hace falta
instalar Python, ni dependencias extra, ni nada.

La primera vez que abrís la tab **"Cargas" → "Por foto"** la app
descarga un modelo de reconocimiento (~6 MB) y una imagen de guía
(~900 KB) desde GitHub Releases. Después podés sacar fotos a tus
figuritas/cards y la app las identifica sola.

## Tus datos

Todos los datos se guardan en:

    C:\Users\<tu usuario>\AppData\Roaming\Collections\

Contenido típico:
- `collections.db` — la base de datos (default sin profile).
- `collections_<nombre>.db` — bases de datos adicionales si usás
  perfiles.
- `images/` — imágenes de guía OCR descargadas.
- `models/` — modelos OCR descargados.

**Para hacer backup:** copiá esa carpeta entera a un pendrive o nube.
**Para migrar a otra PC:** copiá la misma carpeta en la nueva máquina,
en la misma ubicación.

## Problemas comunes

**"Windows protegió tu PC" al abrir.**
Normal — ver paso 4 de la instalación.

**La tab "Por foto" dice "El modelo OCR está configurado pero no está
descargado todavía".**
Es la primera vez que abrís esa tab. Click en **"Descargar modelo"** y
esperá unos segundos (requiere conexión a internet).

**Perdí mis datos al reinstalar.**
Los datos viven en `%APPDATA%\Collections\`, no en la carpeta del
`.exe`. Reinstalar la app no los borra. Para borrarlos hay que eliminar
esa carpeta a mano.
