# Modo administrador

Para usuarios que necesiten acceso a las ABM administrativas
(Cards, Colecciones, Códigos), setear la variable de entorno
`COLLECTIONS_ADMIN=1` antes de ejecutar la app.

## PowerShell

```powershell
$env:COLLECTIONS_ADMIN = "1"
python -m collections_app.main --profile mundial
```

## Bash

```bash
COLLECTIONS_ADMIN=1 python -m collections_app.main --profile mundial
```

Sin esa variable, el menú "Administración" aparece deshabilitado
(gris) con tooltip explicativo. Esta es la configuración default
para usuarios finales.

## Notas de seguridad

Esta variable **NO** es un mecanismo de seguridad. Un usuario
técnico puede leer el código fuente y descubrirla. La separación
admin/usuario es una decisión arquitectónica para mejorar UX, no
para proteger datos sensibles.

Para distribución a comunidad amplia (Camino C), la herramienta
admin se construirá como aplicación separada con build distinto.
