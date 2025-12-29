---
description: Revisa un workplan con codex para generar propuestas de mejora y crear revisión si se aprueba
---

# Revisión de Workplan con Codex

Analiza el workplan más reciente de una tarea usando codex, genera propuestas de mejora, y crea una revisión si el usuario aprueba los cambios.

## Entradas
- ID de la tarea: `$ARGUMENTS`
- Workplans esperados: `./.claude/workplans/$ARGUMENTS/`
- Herramienta de análisis: `codex` (local CLI tool)

## Proceso

### 1. Localizar Workplan Más Reciente

**Pasos**:
1. Verificar que existe `./.claude/workplans/$ARGUMENTS/`
2. Listar archivos con patrón `workplan-*.md` ordenados por fecha de modificación
3. Seleccionar la revisión más reciente:
   - Prioridad: `workplan-{task-id}-rev-{X}.md` (X más alto)
   - Fallback: `workplan-{task-id}.md` (si no hay revisiones)
4. Si no existe ningún workplan, reportar error y sugerir ejecutar `/create-workplan` primero

### 2. Preparar Solicitud para Codex

**Criterios a incluir (resumen breve)**:
- KISS y reutilizacion de patrones existentes
- Alcance MVP vs Enhanced vs Nice-to-Have
- Decisiones tecnicas completas y justificadas
- Consistencia con MCP + RAG (async, tools, sesiones, ChromaDB)
- Testabilidad, criterios de aceptacion, secuenciacion y riesgos
- Completitud (metadatos, historial, secciones)
- **Formato esperado**: resumen corto + sugerencias en bullets (3-6) con prioridad

### 3. Ejecutar Codex

**Comando**:
```bash
codex exec "Analiza el workplan en {path_to_workplan} [criterios de revisión del paso 2]"
```

**Nota**:
- codex debe estar instalado y disponible en PATH. Si no está disponible, reportar error con instrucciones de instalación.
- Se pasa solo el PATH del workplan a codex, que lo leerá por sí mismo (más eficiente que enviar contenido completo)

**Manejo de Errores**: si codex falla o no está disponible, reportar el error y sugerir acciones simples (instalación o reintento).

### 4. Presentar Observaciones al Usuario

**Formato de presentacion (breve)**:
```markdown
# Revision del Workplan: {task-id} - {workplan-filename}
Fecha: {YYYY-MM-DD HH:MM}
Workplan: ./.claude/workplans/{task-id}/{workplan-filename}

{RESUMEN DE CODEX}

¿Deseas aplicar estas mejoras al workplan?
1. ✅ Aprobar y crear revision → Ejecutar `/create-workplan {task-id}` incorporando mejoras
2. 📝 Revisar manualmente → Editar el workplan antes de crear revision
3. ❌ Rechazar → No hacer cambios

Nota: si apruebas, se crea `workplan-{task-id}-rev-{X+1}.md` sin modificar el archivo actual.
```

### 5. Solicitar Aprobación del Usuario

**Usar herramienta `AskUserQuestion`**:
- Pregunta: "¿Deseas aplicar las mejoras sugeridas por codex al workplan?"
- Opciones:
  1. "Sí, crear revisión incorporando mejoras" (Recomendado)
  2. "Revisar manualmente primero"
  3. "No, mantener workplan actual"

**Si opción 1 (Aprobar)**:
1. Preparar contexto para `/create-workplan`:
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

2. Ejecutar `/create-workplan {task-id}` con el contexto preparado (pasar como instrucción adicional)

**Si opción 2 (Revisar manualmente)**:
- Mostrar ruta del workplan actual
- Sugerir abrir en editor
- Recordar ejecutar `/create-workplan {task-id}` cuando esté listo para crear revisión

**Si opción 3 (Rechazar)**:
- Confirmar que no se harán cambios
- Sugerir ejecutar `/review-workplan` nuevamente si cambia de opinión
- Fin del comando

### 6. Integracion con `/create-workplan`

**Importante**: `/create-workplan` debe poder recibir contexto adicional para incorporar mejoras.

## Reglas Importantes

### Reglas Generales
- **IGNORAR** todos los archivos llamados "tags"
- **NO DESARROLLAR CODIGO** - este comando es solo para revision y orquestacion
- **NO MODIFICAR WORKPLAN DIRECTAMENTE** - siempre crear revision via `/create-workplan`
- **PRESERVAR HISTORIAL** - el workplan original y revisiones anteriores se mantienen
- **VERIFICAR CODEX**: Comprobar que `codex` esta en PATH antes de ejecutar
- **TIMEOUT RAZONABLE**: Si codex tarda mas de 2 minutos, advertir al usuario
- **MANEJO DE ERRORES**: Si codex falla, mostrar error completo y sugerir alternativas
- **CONFIRMACION EXPLICITA**: No aplicar cambios sin aprobacion del usuario
- **OPCIONES CLARAS**: Presentar siempre las 3 opciones (Aprobar/Revisar/Rechazar)
- **NOMENCLATURA/RUTAS**: Seguir convenciones y rutas de `create-workplan` y `eval-task`

## Acciones Finales

1. **Confirmar estado**: revision creada, revision manual o sin cambios
2. **Mostrar ruta** del workplan relevante
3. **Sugerir siguiente paso** segun la opcion elegida

---

## Notas Técnicas

### Dependencias
- **codex**: Herramienta CLI local para análisis de texto
- **bash**: Para listar archivos y verificar rutas
- **AskUserQuestion**: Tool de Claude Code para interacción con usuario
- **Skill tool**: Para ejecutar `/create-workplan`

### Limitaciones Conocidas
- Codex debe estar instalado localmente (no hay fallback cloud)
- El análisis de codex puede tardar 1-2 minutos para workplans largos
- La integración con `/create-workplan` asume que puede recibir contexto adicional

---
