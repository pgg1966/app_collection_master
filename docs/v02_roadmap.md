# Roadmap v0.2.0 — Camino al Mundial 2026

> Plan estratégico del proyecto Collections App v0.2.0.
> Última actualización: 5 mayo 2026 (post-Prompt 1).

---

## Contexto y horizonte

- **Hoy:** 5 mayo 2026.
- **Inauguración Mundial 2026:** 11 junio 2026.
- **Días disponibles hasta lanzamiento:** 37.
- **Estado de la ventana de mercado:** abriéndose (álbum Panini circulando recientemente).
- **Modelo de negocio:** app gratis + álbumes pagos. Mundial 2026 gratis (gancho de adopción).
- **Diferencial competitivo:** sistema de pairing automatizado vía archivo `.colexchange`.

---

## Fases del proyecto

### Fase 1 — Construcción técnica (Semanas 1-3)

**Objetivo:** v0.2 instalable, funcional, con álbum del Mundial cargado y pairing operativo.

| Semana | Sesiones | Entregable |
|--------|----------|------------|
| 1 (5-12 mayo) | Prompt 2, Prompt 3 | Services + UI mínima end-to-end |
| 2 (12-19 mayo) | Prompt 4, Prompt 5 | Mundial cargado + pairing funcional |
| 3 (19-26 mayo) | Prompt 6, Prompt 7 | Pulido Nivel 1 + empaquetado Windows |

### Fase 2 — Distribución entre amigos (Semana 4)

**Objetivo:** validar la app con usuarios reales y testear pairing entre papás del mismo círculo.

- Distribución a 3-5 papás seleccionados.
- Al menos un par de ellos del mismo círculo (escuela/club) para testear pairing real.
- Recolección activa de feedback.
- Categorización de feedback: bugs / UX / preferencias.

### Fase 3 — Iteración crítica (Semana 5)

**Objetivo:** corregir bugs reales y problemas de UX que afectan uso. NO agregar features.

- Solo categoría "bugs reales" se aborda.
- Categoría "preferencias" se ignora salvo patrones (3+ personas dicen lo mismo).
- Backlog post-Mundial alimentado con todo el resto.

### Fase 4 — Mundial + distribución amplia (junio en adelante)

**Objetivo:** distribución a comunidad amplia con respaldo (testimonios de Camino B).

- Lanzamiento amplio coincidiendo con el inicio del Mundial.
- Difusión por redes / grupos de Facebook / Discord de coleccionistas.
- Métrica clave: adopción + retención durante el evento.

### Fase 5 — Decisiones post-Mundial

**Objetivo:** según resultado de Camino C, decidir el siguiente paso.

- Si tracción: comenzar trabajo de v0.3 (móvil) y monetización con segundo álbum pago.
- Si tracción media: iterar con feedback amplio.
- Si poca tracción: replantear o cerrar el experimento.

---

## Cronograma detallado al detalle

### Semana 1 — Services + UI mínima (5-12 mayo)

**Lunes-Martes:**
- Sesión Prompt 2 (services + integración de la vista preservada CardLoaderView).
- Verificación: app arranca, vista CardLoaderView funciona contra services nuevos.

**Miércoles-Jueves:**
- Sesión Prompt 3 (UI mínima end-to-end).
- Verificación: flow completo seleccionar colección → ver cards → cargar stock → ver historial.

**Viernes:**
- Buffer para imprevistos o cierre de detalles.

### Semana 2 — Mundial + pairing (12-19 mayo)

**Lunes-Martes:**
- Sesión Prompt 4 (CSV importer + carga del álbum del Mundial 2026).
- Pre-requisito: archivo CSV del Mundial listo en formato esperado.

**Miércoles-Jueves:**
- Sesión Prompt 5 (pairing con `.colexchange`).
- Sesión más densa del proyecto. Posible partir en 5a (export/import + firma) y 5b (matching + UI).

**Viernes:**
- Verificación de pairing entre dos archivos de prueba.

### Semana 3 — Pulido + empaquetado (19-26 mayo)

**Lunes:**
- Sesión Prompt 6 (pulido Nivel 1).
- Acotado: layouts, mensajes de error, tipografía. NO rediseño.

**Martes-Miércoles:**
- Sesión Prompt 7 (empaquetado Windows con PyInstaller).
- Verificación en máquina sin Python instalado.

**Jueves-Viernes:**
- Testing manual completo del flow end-to-end empaquetado.
- Preparación del paquete distribuible.

### Semana 4 — Distribución (26 mayo - 2 junio)

**Lunes:**
- Distribución a los 3-5 papás seleccionados.
- Mensaje claro con instrucciones simples.

**Martes a domingo:**
- Recolección activa de feedback.
- Coordinación de testing de pairing entre dos papás del mismo círculo.

### Semana 5 — Iteración (2-9 junio)

**Lunes-Miércoles:**
- Arreglo de bugs críticos reportados.
- Sin features nuevos.

**Jueves-Viernes:**
- Re-distribución de versión iterada.
- Confirmación de estabilidad.

### Semana 6 — Mundial empieza (10-11 junio)

**11 de junio:** inauguración del Mundial. Tu app ya está instalada entre amigos, con pairing testado, lista para ampliar distribución según resultado.

---

## Definición de "v0.2 lista para Camino B"

Para distribuir entre amigos, la app tiene que cumplir:

- [ ] Instalable con un click en Windows (`.exe` desde PyInstaller).
- [ ] Arranca sin errores con DB vacía.
- [ ] Importa el álbum del Mundial sin fallar.
- [ ] Permite registrar altas y bajas de stock.
- [ ] Muestra inventario, faltantes y repetidas con claridad.
- [ ] Exporta archivo `.colexchange` con firma válida.
- [ ] Importa archivo `.colexchange` y verifica firma.
- [ ] Calcula matching y muestra propuesta editable.
- [ ] Confirma intercambio aplicando bajas + altas atómicamente.
- [ ] Pulido Nivel 1: layouts limpios, mensajes de error decentes.
- [ ] No crashea en flow normal de uso.

**No es necesario** (post-Mundial):

- ❌ Onboarding tutorial.
- ❌ Documentación formal.
- ❌ Pulido Nivel 2.
- ❌ Soporte Mac / Linux.
- ❌ Telemetría.
- ❌ Sistema de licencias activo.
- ❌ Marca / branding.

---

## Anti-patrones a evitar durante el proyecto

Patrones que matan el cronograma. **Resistir activamente:**

### Scope creep
- "Ya que estoy con Prompt 4, también arreglo X."
- "Esto se ve feo, le doy una vuelta de pulido."
- "Mejor agrego una feature más antes de distribuir."

**Regla:** todo lo no-crítico va al `post_mundial_backlog.md`. Sin excepciones que no sean bugs bloqueantes.

### Perfeccionismo prematuro
- Refactor de código que ya funciona.
- Optimización de performance sin evidencia de que sea problema.
- Generalización de features para casos hipotéticos.

**Regla:** "evidencia, no anticipación". Si no hay un bug reportado o un caso real, no se toca.

### Sub-uso de CC
- Hacer cosas a mano que CC haría más rápido y más consistente.
- Saltarse el Plan Mode "porque es algo simple".
- Aprobar planes sin leerlos.

**Regla:** disciplina del proceso = velocidad del proyecto.

### Exceso de uso de CC
- Pedirle que arregle cosas que vos podés hacer en 2 minutos.
- Sesiones para cambios triviales.

**Regla:** CC se usa para cambios estructurados, no para typos.

---

## Reusabilidad técnica para los saltos futuros

Lo que estamos construyendo en v0.2 sobrevive así a los saltos:

| Capa | Reuso en v0.3 móvil (Flutter) | Reuso en v1.0 nube |
|------|-------------------------------|---------------------|
| Schema SQL | 100% (SQLite en móvil) | 80% (PostgreSQL en server) |
| Modelos | 50% (traducir a Dart) | 80% (con cambios de tipos) |
| Repositorios | 0% (nuevo lenguaje) | 40% (queries similares) |
| Servicios | 0% (nuevo lenguaje) pero **diseño 100%** | 0% (nuevo lenguaje) pero **diseño 100%** |
| Vistas Qt | 0% | 0% |
| Formato `.colexchange` | 100% (transición) | 0% (reemplazado por API) |
| Lógica de matching | **función pura agnóstica** = diseño 100% | diseño 100% |

**Conclusión:** el activo más valioso a largo plazo es el **diseño de los servicios y la lógica de matching**, no el código. Por eso son tan importantes los tests y la separación de capas.

---

## Decisiones diferidas (NO tomar todavía)

- Framework móvil: Flutter probablemente, pero se confirma cuando llegue v0.3.
- Backend en la nube: dependerá del lenguaje y stack disponible cuando llegue v1.0.
- Sistema de pago para álbumes: se diseña con el segundo álbum, no antes.
- Marca y nombre comercial: se decide para Camino C amplio.
- Política de privacidad / términos: cuando aplique GDPR / Ley 25.326.
- Telemetría: cuando haya volumen suficiente para que sea útil.

Estas decisiones son **caras si se anticipan, baratas si se posponen**.

---

## Métricas de éxito por fase

### Camino B (Semana 4-5)
- ≥3 papás instalan la app.
- ≥2 papás cargan el álbum del Mundial completo.
- ≥1 par de papás completa un intercambio vía pairing.
- Feedback recibido: bugs vs UX vs preferencias categorizado.

### Camino C (junio en adelante)
- Adopción: número de descargas durante el Mundial.
- Retención: porcentaje que sigue usándola después de la primera semana.
- Pairing: cantidad de archivos `.colexchange` exportados (proxy de uso).
- Calidad: cantidad de bugs críticos reportados.

### Decisión post-Mundial
- Si retención >30% y feedback positivo → invertir en v0.3 móvil.
- Si retención 10-30% → iterar con feedback antes de decidir.
- Si retención <10% → replantear el modelo o cerrar.

---

## Estado actual del proyecto

- ✅ Prompt 0: scaffolding + estructura archivada.
- ✅ Prompt 1: schema + modelos + repos (cobertura 98% en `core/`).
- 🔄 Prompt 2: services + vista preservada *(siguiente)*.
- ⏳ Prompt 3: UI mínima end-to-end.
- ⏳ Prompt 4: importer + Mundial cargado.
- ⏳ Prompt 5: pairing con `.colexchange`.
- ⏳ Prompt 6: pulido Nivel 1.
- ⏳ Prompt 7: empaquetado Windows.

---

## Notas finales

Este cronograma es exigente pero realista si CC mantiene el ritmo del Prompt 0 (1-2 horas por sesión, sin atascamientos graves). Los hitos están calibrados para llegar al Mundial con margen de iteración, no apenas.

Si en algún momento el cronograma se desvía, **el primer recurso es renunciar a alcance, no acelerar trabajo**. Siempre se puede sacrificar el Prompt 6 (pulido) o reducir el Prompt 7 (empaquetado mínimo) si hace falta. Lo que NO se sacrifica es la calidad estructural del Prompt 5 (pairing es el diferencial).
