# Workflow del admin: crear una colección desde cero

Esta guía describe el flujo end-to-end para configurar una colección nueva
en `collections-admin`.

## 0. Arrancar la app

```bash
collections-admin
```

La app abre con tres tabs: **Colecciones · Códigos · Cards**. El menú
**Configuración → Settings…** permite seleccionar la colección activa
(setting persistido para que la app `client` la lea).

## 1. Crear el header de códigos

Primero se define el "universo" de códigos al que pertenecerán las cards.

1. Tab **Códigos**.
2. En el bloque superior (Headers), llenar:
   - **Nombre**: `FIFA Codes`
   - **Max longitud código**: `5`
3. Enter avanza entre campos; en el último, Enter pone foco en `Guardar`.
4. Click en `Guardar`. Aparece la fila en la grilla.

## 2. Cargar las líneas (códigos individuales)

Una vez seleccionado el header recién creado, el bloque inferior
(Códigos del header: …) se habilita.

1. **Código**: `NON` (3 letras, dentro del max 5)
2. **Nombre**: `Non-football`
3. **Orden**: `1`
4. `Guardar`. La fila aparece.
5. Repetir para `GB / Great Britain / 2`, `MR / Marruecos / 3`, etc.

El campo `code_order` controla el orden visible en la grilla; lo dejás en
0 si querés orden alfabético.

## 3. Crear la colección

1. Tab **Colecciones**.
2. **Nombre**: `FIFA WC 2026`
3. **Cantidad de cards**: `300`
4. **Requiere código**: ✓
5. **Etiqueta del código**: `Código`
6. **Universo de códigos**: `FIFA Codes` (combo, cargado desde el paso 1)
7. **Premium**: dejar desmarcado (de lo contrario hace falta hash de licencia)
8. `Guardar`. La validación corre antes de persistir; si `requires_code`
   está marcado pero `code_field_name` está vacío, aparece un mensaje
   ámbar en la status bar inferior — la grilla no se modifica hasta que
   el registro guarde efectivamente.

## 4. Cargar cards desde CSV

1. Tab **Cards**.
2. En el combo superior, seleccionar `FIFA WC 2026`. El ABM se monta
   con los choices de `code_id` filtrados por las líneas del header
   `FIFA Codes`.
3. Click en `Importar CSV…`. Aparece un FileDialog. Elegí el archivo.
4. Mientras procesa, una barra de progreso muestra el avance fila a fila.
5. Al terminar, un diálogo informativo resume:
   - Total filas
   - Importadas (las que entraron al `bulk_upsert`)
   - Omitidas (con una muestra de los primeros errores)
6. La grilla se refresca con todas las cards.

### Formato del CSV

UTF-8, separador coma. La primera fila puede ser header (`code_id,
card_number, card_name`) o directamente datos. Ejemplo:

```csv
code_id,card_number,card_name
ARG,1,Lionel Messi
ARG,2,Emiliano Martínez
ARG,3,Ángel Di María
BRA,1,Vinícius Júnior
BRA,2,Neymar
FRA,1,Kylian Mbappé
```

Validaciones por fila (silenciosas: la fila inválida se omite y se
reporta en el diálogo final, **no aborta** el import):

| Validación                          | Comportamiento si falla        |
|-------------------------------------|--------------------------------|
| Tener al menos 3 columnas           | omite + error en resumen       |
| `code_id` existe en el header de la colección | omite + error en resumen |
| `card_number` es entero positivo    | omite + error en resumen       |
| `card_name` no vacío                | omite + error en resumen       |

Un archivo de prueba con 10 filas vive en
[tests/fixtures/sample_cards.csv](../tests/fixtures/sample_cards.csv).

## 5. Editar y borrar cards manualmente

Después del import:

- **Editar**: click sobre una fila → el form se llena. `code_id` y
  `card_number` quedan readonly (PK compuesta). Editás `card_name` y
  click en `Guardar`.
- **Borrar**: con la fila seleccionada, click en `Eliminar`. Aparece un
  diálogo modal pidiendo confirmación (único modal del flujo por
  diseño). Si confirmás, la card desaparece de la grilla.

## 6. Setear la colección activa para el client

Menú **Configuración → Settings…**, elegí la colección recién creada,
`Aceptar`. El setting `active_collection_id` queda persistido. La
status bar inferior actualiza el nombre de la colección activa.

A partir de ahí, la app `collections-client` (cuando se distribuya)
lee este setting al iniciar y trabaja sobre esa colección.
