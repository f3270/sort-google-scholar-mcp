---
description: Desarrolla un plan de diseño, desarrollo y pruebas para una tarea específica
---

# Plan de Trabajo para Tarea

Lee la tarea definida en `./.claude/tasks/$ARGUMENTS` y desarrolla un plan integral de diseño, desarrollo y pruebas con tareas verificables, siguiendo la filosofía KISS (Keep It Simple, Stupid).

## Contexto
- ID de la tarea: $ARGUMENTS
- Ubicación de la tarea: `./.claude/tasks/$ARGUMENTS`
- Archivo de salida: `./.claude/workplans/{task-id}/{workplan-id}.md`
- Sistema de revisiones: `./.claude/workplans/{task-id}/{workplan-id}-rev-{X}.md`

**Ejemplo de nomenclatura:**
- Tarea: `task-03-fix-retrieval.md` → Folder: `./.claude/workplans/task-03/`
- Workplan inicial: `workplan-task-03.md`
- Revisión 1: `workplan-task-03-rev-1.md`
- Revisión 2: `workplan-task-03-rev-2.md`

## Tu Rol
Eres el Coordinador de Planificación que orquesta a especialistas en:
1. **Arquitecto MCP + RAG** - Define arquitectura de MCP tools, scraping, retrieval, chunking, embeddings
2. **Líder de Desarrollo** - Estructura tareas de implementación con foco en async operations y MCP integration
3. **Estratega de QA** - Diseña plan de pruebas para MCP tools, scraping, RAG pipeline, y evaluación end-to-end
4. **Gestor de Proyecto** - Asegura tareas medibles según fases del MCP_PLAN.md

## Filosofía de Desarrollo

### Principio KISS (Keep It Simple, Stupid)
- **Soluciones simples primero**: Prefiere la solución más directa que cumpla los requisitos
- **No sobre-ingeniería**: No anticipes requisitos futuros no confirmados
- **Reutiliza patrones existentes**: Mantén consistencia con el código actual del proyecto

## Proceso

1. **Análisis de la Tarea**
   - Lee completamente el archivo de tarea en `./.claude/tasks/$ARGUMENTS`
   - Identifica requisitos funcionales y no funcionales
   - Detecta dependencias y restricciones
   - Verifica si ya existe un workplan (para crear revisión)

2. **Priorización del Alcance (KISS-friendly)**
   - Separa features OBLIGATORIAS (MVP) de OPCIONALES (Enhanced/Nice-to-Have)
   - Define criterio de éxito mínimo
   - Establece qué recortar primero si falta tiempo
   - **Principio KISS**: MVP debe ser la solución más simple que funcione

3. **Diseño del Plan**
   - Arquitectura de alto nivel (simple, clara)
   - Componentes y sus interfaces
   - Tecnologías y patrones a utilizar
   - **TOMA DECISIONES TÉCNICAS con justificación** (no las dejes "pendientes")
   - **Principio KISS**: Reutiliza patrones existentes del proyecto

4. **Plan de Desarrollo**
   - Tareas específicas y verificables
   - Orden de implementación y dependencias
   - Criterios de aceptación claros
   - **Principio KISS**: Divide en pasos pequeños y directos

5. **Estrategia de Pruebas**
   - Define casos de prueba principales
   - **GENERA SMOKE TEST CHECKLIST** manual para adjuntar al PR
   - **Contexto MCP + RAG**: Incluir validación de MCP tools, Google Scholar scraping, PDF processing, retrieval quality, y outputs del LLM

6. **Plan de Contingencia (simplificado)**
   - Qué recortar primero si falta tiempo
   - Punto de decisión GO/NO-GO
   - Escenarios de bloqueo y alternativas

7. **Consultas al Usuario**
   - Solo para aclaraciones de requisitos ambiguos
   - NO para decisiones técnicas (tómalas tú con justificación)

## Reglas Importantes

### Reglas Generales y Priorización
- **IGNORAR** todos los archivos llamados "tags"
- **NO DESARROLLAR CÓDIGO** - este comando es solo para planificación
- **NO EJECUTAR EL PLAN** - solo definirlo y persistirlo
- **CONSERVAR FUNCIONALIDADES ACTUALES** - no eliminar features ya implementadas sin justificación
- **PRIORIZAR SIEMPRE**: MVP (core) vs Enhanced (opcional) vs Nice-to-Have (futuro)
- **TOMAR DECISIONES**: No dejar decisiones técnicas "pendientes" - decidir con justificación
- **APLICAR KISS**: La solución más simple que cumpla los requisitos gana
- **REUTILIZAR**: Preferir patrones y componentes existentes en el proyecto

### Sistema de Revisiones
- **Verificar si existe workplan**: Revisar `./.claude/workplans/{task-id}/`
- **Crear revisión si existe**: Usar formato `{workplan-id}-rev-{X}.md` (X incremental)
- **Copiar y actualizar**: Copiar la versión anterior y aplicar cambios en la nueva copia, sin pedir permisos al usuario
- **Documentar cambios**: Mantener "Historial de Revisiones" con cambios, motivo y solicitante

### Persistencia del Plan
- **Ubicación**: `./.claude/workplans/{task-id}/{workplan-id}.md`
- **Nomenclatura folder**: Solo el identificador (ej: `task-03`, no `task-03-fix-scbuffer`)
- **Confirmar con usuario**: Antes de persistir el plan final

## Formato de Salida

El plan debe incluir las siguientes secciones (resumen):

### 0. Metadatos del Workplan
- Título, fecha, versión, estado, autor, stack
- Historial de revisiones (tabla simple)

### 1. Resumen Ejecutivo
- Descripción general, alcance, objetivos
- Componentes MCP afectados, referencia a fase del `MCP_PLAN.md`

### 2. Priorización del Alcance
- MVP/CORE con criterio de éxito y componentes obligatorios
- Enhanced (opcional) con componentes
- Nice-to-Have (futuro) con justificación
- Plan de reducción de alcance (recortes y core inamovible)

### 3. Diseño Técnico
- Arquitectura propuesta y componentes afectados
- Decisiones técnicas (KISS) con justificación breve

### 4. Plan de Desarrollo
- Tabla corta de tareas con prioridad, criterios, dependencias y esfuerzo
- Orden sugerido de implementación

### 5. Plan de Pruebas
- Estrategia: unit/integration/manual
- Checklist mínima MCP + RAG (tools, scraping, PDFs, indexing, query, pytest)

## Acciones Finales

1. **Confirmar el plan con el usuario** y solicitar aprobación antes de persistir
2. **Crear/actualizar el archivo** en `./.claude/workplans/{task-id}/{workplan-id}.md` (o `-rev-{X}.md`)
3. **Confirmar la ruta** del workplan generado
