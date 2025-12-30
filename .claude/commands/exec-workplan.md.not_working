---
description: Ejecuta un workplan con codex usando el task-id
---

# Ejecución de Workplan con Codex

Ejecuta el workplan más reciente de una tarea usando codex. Mantén el alcance KISS y no expandas el plan.

## Entradas
- ID de la tarea: `$ARGUMENTS`
- Workplans esperados: `./.claude/workplans/$ARGUMENTS/`
- Herramienta de ejecución: `codex` (CLI local)

## Proceso

### 1. Localizar Workplan Más Reciente
1. Verificar que existe `./.claude/workplans/$ARGUMENTS/`
2. Listar archivos `workplan-*.md` ordenados por fecha de modificación
3. Seleccionar el más reciente:
   - Prioridad: `workplan-{task-id}-rev-{X}.md` (X más alto)
   - Fallback: `workplan-{task-id}.md`
4. Si no hay workplan, reportar y sugerir `/create-workplan {task-id}`

### 2. Ejecutar Codex

**Comando**:
```bash
codex exec "Ejecuta el workplan en {path_to_workplan}. Sigue el plan al pie de la letra, mantén KISS y no expandas alcance. Asegura que los tests definidos por la tarea pasen; si no hay tests específicos, ejecuta la suite relevante (por defecto `pytest -q`) cuando sea viable. Si necesitas consultar mas de 6-8 archivos o pierdes el hilo del workplan, ejecuta `/compact` y continua."
```

**Notas**:
- Verificar que `codex` esté en PATH antes de ejecutar.
- Si codex falla, reportar el error completo y sugerir reintentar o instalar codex.
- Si codex se queda sin contexto, usar el comando `/compact` y continuar.

### 3. Reportar Resultado
Entregar un resumen breve con:
- Estado general (ok/bloqueado)
- Archivos cambiados o creados
- Pruebas ejecutadas (si aplica)
- Siguientes pasos recomendados (si aplica)

## Reglas Importantes
- **IGNORAR** archivos llamados "tags"
- **NO INVENTAR** cambios o resultados: solo reporta lo ejecutado
- **NO EXPANDIR** el alcance del workplan
- **MANTENER KISS** y reutilizar patrones del proyecto
