# Backlog Post-Mundial 2026

> Lista de todo lo diferido durante el camino crítico al Mundial.
> Organizado por prioridad y dependencias.

---

## Cómo usar este backlog

1. **Después del Mundial 2026** (julio 2026 en adelante), cuando tengas feedback real de Camino C.
2. Revisar las métricas de éxito definidas en `v02_roadmap.md`.
3. Decidir si seguir invirtiendo en el proyecto o no.
4. Si sí: tomar items de este backlog en orden de prioridad para los siguientes prompts.

**No agregar nada del backlog al camino crítico actual.** El propósito de este archivo es justamente proteger el cronograma.

---

## Tier 1 — Alta prioridad (post-Mundial inmediato)

Cosas que el feedback de Camino B/C va a demandar.

### Pulido visual Nivel 2 — dirigido por feedback
- Iconografía consistente (Material Design o similar).
- Paleta de colores definida.
- Estados visuales mejorados.
- Modales y diálogos con estilo coherente.
- Tablas con highlight, scroll suave.

**Cuándo hacerlo:** después de recolectar feedback de Camino B y C. Pulir lo que los usuarios quejaron, no lo que vos creés feo.

### Onboarding tutorial
- Primera vez que un usuario abre la app: tutorial mínimo.
- Cómo cargar una colección.
- Cómo registrar stock.
- Cómo hacer un pairing.

**Cuándo hacerlo:** si los amigos preguntan repetidas veces "cómo hago X". Antes no, es overengineering.

### Soporte Mac y Linux
- PyInstaller para macOS (probablemente Briefcase es mejor opción).
- PyInstaller o AppImage para Linux.
- Verificación en cada plataforma.

**Cuándo hacerlo:** si llega un usuario con Mac o Linux específicamente pidiendo. Si nadie lo pide, no es prioridad.

### Tools de adquisición de datos
- Estructura `tools/` con utilities mínimas.
- Plantilla por álbum.
- Scripts ad-hoc por cada nuevo álbum a agregar.

**Cuándo hacerlo:** cuando quieras incorporar el segundo álbum (probablemente el primero pago). Ver el Prompt 5 original que estaba diseñado para esto.

---

## Tier 2 — Media prioridad

Mejoras que aumentan calidad pero no son urgentes.

### Sistema de licencias activo
- Verificación de claves de álbumes pagos.
- Generación y distribución de claves.
- UI para activar álbum con clave.

**Cuándo hacerlo:** cuando estés por lanzar el primer álbum pago. El schema ya está preparado (`is_premium`, `license_key_required`).

### Backup automático de la DB
- Snapshots periódicos de `app.db` a `app.db.bak`.
- UI para restaurar desde backup.
- Backup antes de operaciones destructivas.

**Cuándo hacerlo:** si algún usuario reporta pérdida de datos. Antes no.

### Búsqueda y filtrado
- Búsqueda por nombre de card.
- Filtros por estado (mías, faltantes, repetidas).
- Filtros por código.

**Cuándo hacerlo:** cuando una colección típica supere 200 cards y la navegación se vuelva incómoda.

### Generación de PDF del álbum
- Vista impresa del álbum con cards marcadas como "tengo" o "no".
- Útil para llevar al kiosko.

**Cuándo hacerlo:** si los usuarios lo piden. La feature es atractiva pero costosa de implementar (`reportlab`).

### Telemetría opt-in
- Métricas anónimas de uso.
- Crashes reportados automáticamente.
- Tiempo en cada vista.

**Cuándo hacerlo:** cuando tengas suficientes usuarios para que el dato sea útil (>50). Antes no.

### Mejoras al script `generate_context.py`
- Que respete `.gitignore`.
- Que genere también `data_dictionary.md`.
- Que se incluya en pre-commit.

**Cuándo hacerlo:** cuando moleste lo suficiente como para justificar la sesión.

### Aggregate `CodeStats` extendido
- Agregar `last_updated`, `pending_for_album_completion`, etc.
- Solo si UI lo pide.

---

## Tier 3 — Decisiones estratégicas

Cosas que requieren decisión tuya antes de implementar.

### v0.3 móvil
- Framework: probablemente Flutter.
- Reescritura completa de UI.
- SQLite local mantiene compatibilidad.
- Pairing por archivo se mantiene como fallback.

**Cuándo hacerlo:** cuando v0.2 demuestre tracción suficiente y feedback indique demanda real. **No antes**.

**Pre-requisitos para arrancar:**
- Definir framework (Flutter vs alternativas).
- Aprender el framework (curva de varios meses si no lo conocés).
- Replantear UX para celular (no es portar Qt).

### v1.0 cloud + multi-usuario
- Backend en la nube (lenguaje y framework por decidir).
- API REST para sync.
- Sistema de usuarios y autenticación.
- Pairing en tiempo real sin archivos.
- Servidor de licencias.

**Cuándo hacerlo:** cuando v0.3 móvil demuestre tracción y modelo de negocio sostenible.

**Pre-requisitos:**
- Decisión de stack server.
- Decisión de hosting y costos asociados.
- Diseño de modelo de datos multi-tenant.
- Términos legales (privacidad, GDPR, Ley 25.326).

### Marca y comunicación
- Nombre comercial (no "Collections App").
- Logo.
- Landing page.
- Capturas profesionales.
- Texto de marketing.

**Cuándo hacerlo:** antes de Camino C amplio o de la primera salida pública. Si te quedás en Camino B, no es necesario.

**Trabajo NO técnico:** este es trabajo tuyo de marketing/diseño, no de CC.

### Modelo de monetización detallado
- ¿Pago único por álbum?
- ¿Suscripción?
- ¿Bundle de varios álbumes?
- ¿Plataforma de pago (Stripe, MercadoPago)?

**Cuándo hacerlo:** con el segundo álbum, o cuando v0.2 demuestre que hay mercado.

---

## Tier 4 — Deuda técnica conocida

Cosas que CC detectó durante los Prompts pero no abordó.

### Datetime ISO format en `transactions`
- Detectado en Prompt 1.
- Persiste con espacio-separator. ISO estándar usa `T`.
- `fromisoformat` acepta ambos en Python 3.11+, así que funciona.
- Riesgo si en futuro código asume formato canónico.
- **Acción:** test explícito de roundtrip mixto cuando aterricen datos antiguos. Migración formal si cambia el formato.

### `adjust_quantity` permite quantity negativo a nivel repo
- Detectado en Prompt 1.
- La invariante "quantity >= 0" se enforce solo en service.
- Repo no tiene CHECK constraint.
- **Acción:** confirmar que el service del Prompt 2 efectivamente lo valida. Si no, corregir.

### Script `generate_context.py`
- No respeta `.gitignore`.
- No genera `data_dictionary.md` aunque CLAUDE.md lo dice.
- Incluye archivos personales (Album_.pdf, etc.).
- **Acción:** sesión chica de fix cuando moleste lo suficiente.

---

## Tier 5 — Features eventualmente útiles pero no críticas

Cosas que estarían bueno tener en algún momento.

### Atajos de teclado
- Navegación rápida sin mouse.
- Particularmente útil para gente que carga muchas cards seguidas.

### Modo claro/oscuro
- Más estético que funcional.
- Algunos usuarios lo van a pedir.

### Animaciones sutiles
- Transiciones entre vistas.
- Feedback visual al confirmar acciones.

### Multi-idioma
- Inglés principalmente.
- Permitiría expandir el mercado más allá de Argentina/Latam.

### Compartir directamente desde la app
- Botón "Enviar por WhatsApp" después de exportar `.colexchange`.
- Requiere integración con APIs del SO.

### Estadísticas avanzadas
- Cuántos intercambios hiciste por mes.
- Con qué contrapartes intercambiaste más.
- Progresión de completitud del álbum.

---

## Cómo se prioriza después del Mundial

1. **Recolectar feedback** de Camino B y C durante junio-julio 2026.
2. **Categorizar** lo recibido en bugs / UX / features / preferencias.
3. **Cruzar** con este backlog para identificar qué items del Tier 1-2 alinean con el feedback.
4. **Decidir** según métricas de éxito si el proyecto continúa.
5. **Si continúa:** elegir el Tier 1 más alineado con feedback como próximo prompt.

**Nunca priorizar por "lo que parece divertido implementar".** Priorizar por:
- Frecuencia de mención en feedback.
- Severidad del problema que resuelve.
- Costo de implementación vs. valor entregado.

---

## Notas finales

Este backlog es un documento vivo. Después de cada distribución (Camino B, Camino C) y de cada feedback recibido, conviene:

1. Agregar nuevos items detectados.
2. Re-priorizar según evidencia.
3. Mover items al "completado" cuando se hagan.
4. Eliminar items que dejaron de tener sentido.

La existencia de este backlog **es lo que protege la disciplina del proyecto**. Sin él, cada idea nueva tiene tentación de meterse al camino crítico. Con él, las ideas tienen un lugar donde vivir hasta que sea su turno.
