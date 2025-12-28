---
description: Evalúa si una tarea se ejecutó conforme al workplan (KISS, sin sobre-ingeniería).
---

# Evaluación de Tarea vs Workplan

Revisa el trabajo realizado contra el workplan más reciente y determina si el alcance se cumplió. Mantén el proceso KISS.

## Entradas
- ID de la tarea: `$ARGUMENTS`
- Workplans esperados: `./.claude/workplans/$ARGUMENTS/` (elige la revisión más reciente)
- Cambios de código: git diff/worktree

## Pasos
1. **Cargar workplan**: abrir el archivo de revisión más reciente en `./.claude/workplans/$ARGUMENTS/`. Si no existe, reportar bloqueo.
2. **Listar cambios**: usar `git status --short` y `git diff --stat` (o `git show HEAD` si ya hay commit) para ver qué se tocó.
3. **Mapear tareas → evidencia**: cruzar las tareas MVP del workplan con los archivos cambiados/creados. Nota hallazgos claros:
   - Cumplido (evidencia de archivos/funciones)
   - Parcial (qué falta)
   - No iniciado (sin evidencia)
4. **Pruebas**: revisar si hay scripts/tests añadidos. Si existen, sugerir correrlos (no asumas que ya se ejecutaron). Mantén KISS en recomendaciones.
5. **Output**: redacta un breve informe con:
   - Estado general: ✅/⚠️/❌
   - Hallazgos por tarea clave (ruta de archivo como referencia)
   - Huecos pendientes y riesgos
   - Checks sugeridos para validar (comandos simples, e.g., `uv run python ...`, `pytest` si aplica)

## Reglas
- No inventar evidencia: si no está en código o git, márcalo como faltante.
- No ejecutes planes nuevos ni expandas alcance; solo evalúa contra el workplan.
- KISS: informe breve, accionable, sin sobrecarga.
