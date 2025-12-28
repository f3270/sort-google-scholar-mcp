---
description: Revisa un workplan con codex para generar propuestas de mejora y crear revisión si se aprueba
---

# Revisión de Workplan con Codex

Analiza el workplan más reciente de una tarea usando codex, genera propuestas de mejora, y crea una revisión si el usuario aprueba los cambios.

## Entradas
- ID de la tarea: `$ARGUMENTS`
- Workplans esperados: `./.claude/workplans/$ARGUMENTS/`
- Herramienta de análisis: `codex` (local CLI tool)

## Contexto
Este comando orquesta un flujo de revisión asistida por codex:
1. Encuentra y lee el workplan más reciente
2. Solicita análisis y propuestas de mejora a codex
3. Presenta observaciones al usuario para aprobación
4. Si se aprueba, delega a `/load-task` para crear la revisión

**Diferencia con `/eval-task`**:
- **eval-task**: Valida cumplimiento (tarea implementada vs workplan)
- **review-workplan**: Mejora calidad del plan antes de implementar

## Proceso

### 1. Localizar Workplan Más Reciente

**Pasos**:
1. Verificar que existe `./.claude/workplans/$ARGUMENTS/`
2. Listar archivos con patrón `workplan-*.md` ordenados por fecha de modificación
3. Seleccionar la revisión más reciente:
   - Prioridad: `workplan-{task-id}-rev-{X}.md` (X más alto)
   - Fallback: `workplan-{task-id}.md` (si no hay revisiones)
4. Si no existe ningún workplan, reportar error y sugerir ejecutar `/load-task` primero

**Ejemplo**:
```bash
# Directorio: ./.claude/workplans/task-03/
# Archivos encontrados:
# - workplan-task-03.md (versión inicial)
# - workplan-task-03-rev-1.md (primera revisión)
# - workplan-task-03-rev-2.md (segunda revisión) ← ESTE SE USA
```

### 2. Preparar Solicitud para Codex

**Formato de solicitud a codex**:
```
Analiza el siguiente workplan para el proyecto sortgs-mcp y genera propuestas de mejora considerando:

CONTEXTO DEL PROYECTO:
- Proyecto: sortgs-mcp (Google Scholar scraper + MCP server + RAG system)
- Stack: MCP (stdio) + ChromaDB (embedded) + Anthropic Claude + sentence-transformers + httpx + Selenium + PyMuPDF
- Filosofía: KISS (Keep It Simple, Stupid) - evitar sobre-ingeniería
- Arquitectura: Async/await patterns, session-based persistence, MCP tools integration

WORKPLAN A REVISAR:
Lee el archivo en: ./.claude/workplans/{task-id}/{workplan-filename}

CRITERIOS DE REVISIÓN:

1. **Adherencia a KISS**:
   - ¿Hay sobre-ingeniería o abstracciones prematuras?
   - ¿Se reutilizan patrones existentes del proyecto?
   - ¿La solución propuesta es la más simple que cumple requisitos?

2. **Claridad de Alcance (MVP vs Enhanced)**:
   - ¿El alcance MVP está bien definido y es mínimo viable?
   - ¿Las prioridades están bien justificadas?
   - ¿Hay features en MVP que deberían ser Enhanced o Nice-to-Have?

3. **Decisiones Técnicas**:
   - ¿Todas las decisiones críticas están tomadas (no pendientes)?
   - ¿Las justificaciones son sólidas?
   - ¿Se consideraron alternativas relevantes?
   - ¿Las decisiones son consistentes con el stack del proyecto?

4. **Consistencia con Arquitectura MCP + RAG**:
   - ¿Se respetan los patrones async del proyecto?
   - ¿El diseño de MCP tools es correcto (schemas, error handling)?
   - ¿El manejo de sesiones es consistente con SessionManager?
   - ¿El uso de ChromaDB sigue las convenciones del proyecto?

5. **Testabilidad y Validación**:
   - ¿El smoke test checklist cubre los casos críticos?
   - ¿Los criterios de aceptación son medibles?
   - ¿Falta algún escenario de prueba importante (CAPTCHA, errors, edge cases)?

6. **Viabilidad de Implementación**:
   - ¿Las tareas están bien secuenciadas?
   - ¿Hay dependencias o bloqueos no considerados?
   - ¿El plan de contingencia cubre riesgos reales del proyecto (robot checks, API limits)?

7. **Completitud del Plan**:
   - ¿Faltan secciones importantes?
   - ¿Los metadatos están completos?
   - ¿El historial de revisiones está actualizado?

FORMATO DE RESPUESTA ESPERADO:

## Resumen Ejecutivo
[Evaluación general del workplan en 2-3 párrafos]

## Fortalezas Identificadas
- ✅ [Fortaleza 1]
- ✅ [Fortaleza 2]
- ✅ [Fortaleza N]

## Oportunidades de Mejora

### Alta Prioridad (Crítico - debe corregirse)
1. **[Título del Issue]**
   - **Problema**: [Descripción del problema detectado]
   - **Impacto**: [Por qué es importante]
   - **Propuesta**: [Solución concreta sugerida]
   - **Sección afectada**: [Número de sección del workplan]

### Media Prioridad (Importante - mejoraría significativamente)
2. **[Título del Issue]**
   - **Problema**: [...]
   - **Impacto**: [...]
   - **Propuesta**: [...]
   - **Sección afectada**: [...]

### Baja Prioridad (Opcional - mejoras menores)
3. **[Título del Issue]**
   - **Problema**: [...]
   - **Impacto**: [...]
   - **Propuesta**: [...]
   - **Sección afectada**: [...]

## Decisiones Técnicas a Aclarar (si aplica)
- [ ] **Decisión X**: [Qué falta definir y por qué es importante]
- [ ] **Decisión Y**: [...]

## Checklist de Completitud
- [ ] Metadatos completos (fecha, versión, autor, stack)
- [ ] Historial de revisiones actualizado
- [ ] Alcance MVP/Enhanced/Nice-to-Have bien diferenciado
- [ ] Todas las decisiones técnicas críticas tomadas
- [ ] Smoke test checklist adaptado a la tarea
- [ ] Plan de contingencia cubre riesgos del proyecto
- [ ] Tareas tienen criterios de aceptación medibles
- [ ] Arquitectura consistente con patrones del proyecto

## Recomendación Final
- [ ] ✅ **APROBADO** - El workplan está listo para ejecutar (mejoras opcionales)
- [ ] ⚠️ **APROBADO CON RESERVAS** - Puede ejecutarse, pero aplicar mejoras de alta prioridad reduciría riesgos
- [ ] ❌ **REQUIERE REVISIÓN** - Issues críticos deben resolverse antes de implementar

**Justificación**: [Razón de la recomendación]

---

IMPORTANTE: Se específico, concreto y accionable. Cita números de sección del workplan para facilitar la ubicación de cambios.
```

### 3. Ejecutar Codex

**Comando**:
```bash
codex "Analiza el workplan en {path_to_workplan} para el proyecto sortgs-mcp [criterios de revisión del paso 2]"
```

**Nota**:
- codex debe estar instalado y disponible en PATH. Si no está disponible, reportar error con instrucciones de instalación.
- Se pasa solo el PATH del workplan a codex, que lo leerá por sí mismo (más eficiente que enviar contenido completo)

**Manejo de Errores**:
- Si codex no está instalado: Mensaje claro + link a instalación
- Si codex falla: Capturar stderr y mostrar al usuario
- Si timeout: Sugerir reintentar con workplan más pequeño o usar chunks

### 4. Presentar Observaciones al Usuario

**Formato de presentación**:
```markdown
# Revisión del Workplan: {task-id} - {workplan-filename}

**Herramienta**: codex
**Fecha**: {YYYY-MM-DD HH:MM}
**Workplan revisado**: ./.claude/workplans/{task-id}/{workplan-filename}

---

{OUTPUT COMPLETO DE CODEX}

---

## Próximos Pasos

¿Deseas aplicar estas mejoras al workplan?

**Opciones**:
1. ✅ **Aprobar y crear revisión** → Ejecutar `/load-task {task-id}` incorporando las mejoras
2. 📝 **Revisar manualmente** → Editar el workplan manualmente antes de crear revisión
3. ❌ **Rechazar** → No hacer cambios (el workplan actual se mantiene)

**IMPORTANTE**: Si apruebas, se creará una nueva revisión (`workplan-{task-id}-rev-{X+1}.md`) incorporando las observaciones de codex. El workplan actual NO se modifica (se preserva en el historial).
```

### 5. Solicitar Aprobación del Usuario

**Usar herramienta `AskUserQuestion`**:
- Pregunta: "¿Deseas aplicar las mejoras sugeridas por codex al workplan?"
- Opciones:
  1. "Sí, crear revisión incorporando mejoras" (Recomendado)
  2. "Revisar manualmente primero"
  3. "No, mantener workplan actual"

**Si opción 1 (Aprobar)**:
1. Preparar contexto para `/load-task`:
   ```
   Crea una revisión del workplan {task-id} incorporando las siguientes mejoras sugeridas por codex:

   [RESUMEN DE MEJORAS DE ALTA Y MEDIA PRIORIDAD DE CODEX]

   Workplan base: ./.claude/workplans/{task-id}/{workplan-filename}
   Nueva revisión: ./.claude/workplans/{task-id}/{workplan-id}-rev-{X+1}.md

   En la sección "Historial de Revisiones", agregar:
   | rev-{X+1} | {YYYY-MM-DD} | Mejoras aplicadas post-revisión con codex | Incorporar sugerencias de análisis automatizado |

   Asegúrate de:
   - Aplicar solo mejoras de ALTA y MEDIA prioridad (las de baja son opcionales)
   - Mantener la filosofía KISS del proyecto
   - Preservar decisiones técnicas ya tomadas (solo refinar si codex detectó inconsistencias)
   - Actualizar secciones afectadas según recomendaciones de codex
   ```

2. Ejecutar `/load-task {task-id}` con el contexto preparado (pasar como instrucción adicional)

**Si opción 2 (Revisar manualmente)**:
- Mostrar ruta del workplan actual
- Sugerir abrir en editor
- Recordar ejecutar `/load-task {task-id}` cuando esté listo para crear revisión

**Si opción 3 (Rechazar)**:
- Confirmar que no se harán cambios
- Sugerir ejecutar `/review-workplan` nuevamente si cambia de opinión
- Fin del comando

### 6. Integración con `/load-task`

**Importante**: `/load-task` debe poder recibir contexto adicional para incorporar las mejoras.

**Flujo esperado**:
1. Usuario aprueba mejoras en paso 5
2. Este comando construye un prompt con:
   - Referencia al workplan base
   - Lista de mejoras a aplicar (de codex)
   - Instrucciones de formato para revisión
3. Ejecuta `/load-task {task-id}` pasando el prompt como contexto adicional
4. `/load-task` crea `workplan-{task-id}-rev-{X+1}.md` con las mejoras incorporadas

**Nota**: Si `/load-task` no soporta contexto adicional todavía, mostrar el prompt preparado y pedir al usuario que lo pase manualmente al ejecutar `/load-task`.

## Reglas Importantes

### Reglas Generales
- **IGNORAR** todos los archivos llamados "tags"
- **NO DESARROLLAR CÓDIGO** - este comando es solo para revisión y orquestación
- **NO MODIFICAR WORKPLAN DIRECTAMENTE** - siempre crear revisión vía `/load-task`
- **PRESERVAR HISTORIAL** - el workplan original y revisiones anteriores se mantienen

### Uso de Codex
- **Verificar disponibilidad**: Comprobar que `codex` está en PATH antes de ejecutar
- **Timeout razonable**: Si codex tarda más de 2 minutos, advertir al usuario
- **Manejo de errores**: Si codex falla, mostrar error completo y sugerir alternativas
- **Output completo**: Mostrar TODO el output de codex al usuario (no resumir)

### Interacción con Usuario
- **Transparencia**: Mostrar siempre el output completo de codex
- **Confirmación explícita**: No aplicar cambios sin aprobación del usuario
- **Opciones claras**: Presentar siempre las 3 opciones (Aprobar/Revisar/Rechazar)
- **Contexto completo**: Al pasar a `/load-task`, incluir todas las mejoras relevantes

### Consistencia con Comandos Existentes
- **Nomenclatura**: Seguir convenciones de `load-task` y `eval-task`
- **Rutas**: Usar `./.claude/workplans/{task-id}/` consistentemente
- **Formato de revisiones**: `workplan-{task-id}-rev-{X}.md` (X incremental)
- **Filosofía KISS**: Aplicarla también en la revisión (no sobre-complejizar workplans)

## Casos de Uso

### Caso 1: Primera revisión de un workplan nuevo
```bash
# Usuario ejecuta:
/review-workplan task-05

# Comando busca:
# - ./.claude/workplans/task-05/workplan-task-05.md ✅ (existe)

# Codex analiza y sugiere mejoras
# Usuario aprueba
# Se crea: workplan-task-05-rev-1.md
```

### Caso 2: Revisión de un workplan ya revisado
```bash
# Usuario ejecuta:
/review-workplan task-03

# Comando busca:
# - ./.claude/workplans/task-03/workplan-task-03.md
# - ./.claude/workplans/task-03/workplan-task-03-rev-1.md
# - ./.claude/workplans/task-03/workplan-task-03-rev-2.md ✅ (más reciente)

# Codex analiza rev-2
# Usuario aprueba
# Se crea: workplan-task-03-rev-3.md
```

### Caso 3: No existe workplan para la tarea
```bash
# Usuario ejecuta:
/review-workplan task-99

# Comando reporta:
# ❌ Error: No se encontró workplan para task-99
# Sugerencia: Ejecuta `/load-task task-99` primero para crear el workplan inicial
```

### Caso 4: Codex no está disponible
```bash
# Usuario ejecuta:
/review-workplan task-01

# Comando detecta que `codex` no está en PATH
# Reporta:
# ❌ Error: Herramienta 'codex' no encontrada
# Instalación: [instrucciones según sistema operativo]
# Alternativa: Revisar el workplan manualmente en [ruta]
```

## Acciones Finales

1. **Verificar estado**:
   - Si creó revisión: Confirmar ruta del nuevo archivo
   - Si revisión manual: Mostrar ruta del workplan a editar
   - Si rechazado: Confirmar que no hubo cambios

2. **Listar workplans actuales**:
   ```bash
   ls -la ./.claude/workplans/{task-id}/
   ```
   Mostrar al usuario para que vea el estado actual

3. **Proporcionar resumen**:
   - ✅ Workplan revisado: {ruta}
   - 🔍 Observaciones de codex: {resumen ejecutivo}
   - 📝 Acción tomada: {Revisión creada | Manual | Sin cambios}
   - 🔗 Siguiente paso sugerido: {Implementar | Editar | Ejecutar nuevamente}

4. **Recordar al usuario**:
   - Si creó revisión: "Revisa el nuevo workplan antes de implementar"
   - Si manual: "Ejecuta `/load-task {task-id}` cuando termines de editar"
   - Si rechazado: "Puedes volver a ejecutar `/review-workplan` cuando lo necesites"

---

## Notas Técnicas

### Dependencias
- **codex**: Herramienta CLI local para análisis de texto
- **bash**: Para listar archivos y verificar rutas
- **AskUserQuestion**: Tool de Claude Code para interacción con usuario
- **Skill tool**: Para ejecutar `/load-task`

### Limitaciones Conocidas
- Codex debe estar instalado localmente (no hay fallback cloud)
- El análisis de codex puede tardar 1-2 minutos para workplans largos
- La integración con `/load-task` asume que puede recibir contexto adicional

### Mejoras Futuras (Opcional)
- Soporte para revisar múltiples workplans en batch
- Generación de diff visual entre workplan actual y propuestas de codex
- Cache de análisis de codex para evitar re-análisis
- Integración con git para trackear cambios en workplans

---

## Ejemplo de Ejecución Completa

```bash
$ /review-workplan task-03

🔍 Localizando workplan más reciente para task-03...
✅ Encontrado: ./.claude/workplans/task-03/workplan-task-03-rev-2.md

📤 Enviando a codex para análisis...
⏳ Analizando workplan (esto puede tardar 1-2 minutos)...

✅ Análisis completado. Presentando resultados:

---

# Revisión del Workplan: task-03 - workplan-task-03-rev-2.md

**Herramienta**: codex
**Fecha**: 2025-12-28 10:30
**Workplan revisado**: ./.claude/workplans/task-03/workplan-task-03-rev-2.md

---

## Resumen Ejecutivo
El workplan está bien estructurado y sigue la filosofía KISS. La arquitectura propuesta es sólida y consistente con el proyecto. Se identificaron 3 mejoras de alta prioridad relacionadas con el smoke test checklist y 2 de media prioridad sobre decisiones técnicas.

## Fortalezas Identificadas
- ✅ Alcance MVP claramente definido y mínimo viable
- ✅ Decisiones técnicas tomadas y bien justificadas
- ✅ Plan de contingencia cubre riesgos reales del proyecto
- ✅ Reutiliza patrones existentes (SessionManager, async patterns)

## Oportunidades de Mejora

### Alta Prioridad (Crítico - debe corregirse)
1. **Smoke test no cubre caso de CAPTCHA en MCP context**
   - **Problema**: El checklist incluye prueba de CAPTCHA manual, pero MCP stdio no permite interacción
   - **Impacto**: Si ocurre CAPTCHA, el test fallará sin workaround documentado
   - **Propuesta**: Agregar nota en smoke test explicando limitación y workaround (usar CLI legacy)
   - **Sección afectada**: 6. Smoke Test Checklist

[... más observaciones de codex ...]

## Recomendación Final
- [x] ⚠️ **APROBADO CON RESERVAS** - Puede ejecutarse, pero aplicar mejoras de alta prioridad reduciría riesgos

**Justificación**: El plan es sólido, pero las mejoras de alta prioridad previenen bloqueos durante implementación.

---

## Próximos Pasos

¿Deseas aplicar estas mejoras al workplan?

**Opciones**:
1. ✅ **Aprobar y crear revisión** → Ejecutar `/load-task task-03` incorporando las mejoras
2. 📝 **Revisar manualmente** → Editar el workplan manualmente antes de crear revisión
3. ❌ **Rechazar** → No hacer cambios (el workplan actual se mantiene)

**IMPORTANTE**: Si apruebas, se creará una nueva revisión (`workplan-task-03-rev-3.md`) incorporando las observaciones de codex.

[Usuario selecciona opción 1]

✅ Aprobado. Preparando contexto para `/load-task`...

📤 Ejecutando `/load-task task-03` con mejoras incorporadas...

[/load-task se ejecuta y crea workplan-task-03-rev-3.md]

✅ Revisión creada exitosamente:
   Ruta: ./.claude/workplans/task-03/workplan-task-03-rev-3.md

📋 Estado actual de workplans para task-03:
   - workplan-task-03.md (versión inicial)
   - workplan-task-03-rev-1.md (primera revisión)
   - workplan-task-03-rev-2.md (segunda revisión)
   - workplan-task-03-rev-3.md (última revisión - post codex) ✨

🎯 Siguiente paso sugerido: Revisar el nuevo workplan antes de comenzar implementación
```

---

**Recordatorio**: Este comando NO implementa código, solo orquesta la revisión del workplan usando codex como herramienta de análisis.
