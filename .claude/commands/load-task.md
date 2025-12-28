---
description: Desarrolla un plan de diseño, desarrollo y pruebas para una tarea específica (sort-google-scholar-mcp)
---

# Plan de Trabajo para Tarea - Sort Google Scholar MCP

Lee la tarea definida en `./.claude/tasks/$ARGUMENTS` y desarrolla un plan integral de diseño, desarrollo y pruebas con tareas verificables, siguiendo la filosofía KISS (Keep It Simple, Stupid).

## Contexto
- ID de la tarea: $ARGUMENTS
- Ubicación de la tarea: `./.claude/tasks/$ARGUMENTS`
- Archivo de salida: `./.claude/workplans/{task-id}/{workplan-id}.md`
- Sistema de revisiones: `./.claude/workplans/{task-id}/{workplan-id}-rev-{X}.md`

**Ejemplo de nomenclatura:**
- Tarea: `task-03-fix-retrieval.md` → Folder: `./.claude/workplans/task-03/`
- Workplan inicial: `task-03-workplan.md`
- Revisión 1: `task-03-workplan-rev-1.md`
- Revisión 2: `task-03-workplan-rev-2.md`

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
- **Evita abstracciones prematuras**: Tres líneas duplicadas son mejor que una abstracción forzada
- **Documenta lo necesario**: Comenta solo lógica no obvia, no repitas lo que el código dice

### Contexto del Proyecto Sort Google Scholar MCP
Este proyecto usa:
- **MCP Framework**: `mcp>=1.2.0` (stdio server para Claude Code integration)
- **Vector Store**: ChromaDB (embedded, local persistence, NO cloud)
- **Embeddings**: sentence-transformers (all-mpnet-base-v2, 100% local, sin API)
- **LLM**: Anthropic Claude API (Haiku para keywords, Sonnet para RAG)
- **Web Scraping**: httpx (async) + BeautifulSoup + Selenium (fallback CAPTCHA)
- **PDF Processing**: PyMuPDF (fitz) para parsing, langchain-text-splitters para chunking
- **Async**: httpx para requests async, asyncio.to_thread() para Selenium sync

**Consideraciones técnicas:**
- **MCP Tools**: 6 tools expuestos (generate_keywords, search_papers, download_papers, index_papers, query_papers, list_sessions)
- **Google Scholar Scraping**: Rate limiting, robot checks, CAPTCHA manual solving, random delays (0.5-3s)
- **Chunking**: RecursiveCharacterTextSplitter (baseline MVP, semantic chunking postponed)
- **ChromaDB**: Session-based collections, embedded client, local persistence en data/vectorstore/
- **PDF Downloads**: Concurrent downloads (max 5), retry logic, validación content-type + magic bytes (%PDF)
- **Metadata**: Enriched chunks con paper info (title, authors, year, citations, rank, chunk_index, source_url)
- **Async Migration**: Mantener compatibilidad backward con sortgs CLI original (sync)

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

### Reglas Generales
- **IGNORAR** todos los archivos llamados "tags"
- **NO DESARROLLAR CÓDIGO** - este comando es solo para planificación
- **NO SE DEBE EJECUTAR EL PLAN, SOLO DEFINIRLO Y PERSISTIRLO**
- **CONSERVAR FUNCIONALIDADES ACTUALES** - no eliminar features ya implementadas sin justificación

### Priorización y Decisiones
- **PRIORIZAR SIEMPRE**: MVP (core) vs Enhanced (opcional) vs Nice-to-Have (futuro)
- **TOMAR DECISIONES**: No dejar decisiones técnicas "pendientes" - decidir con justificación
- **APLICAR KISS**: La solución más simple que cumpla los requisitos gana
- **REUTILIZAR**: Preferir patrones y componentes existentes en el proyecto

### Sistema de Revisiones
- **Verificar si existe workplan**: Antes de crear, revisar `./.claude/workplans/{task-id}/`
- **Crear revisión si existe**: Usar formato `{workplan-id}-rev-{X}.md` (X incremental)
- **Documentar cambios**: Cada revisión debe incluir sección "Historial de Revisiones" con:
  - Qué cambió respecto a la versión anterior
  - Por qué se hizo el cambio
  - Quién solicitó el cambio (usuario o detección automática)

**Ejemplo de decisión de revisión:**
- ¿Cambio menor (typos, clarificaciones)? → Modificar workplan original
- ¿Cambio de alcance, arquitectura, o requisitos? → Crear nueva revisión

### Persistencia del Plan
- **Ubicación**: `./.claude/workplans/{task-id}/{workplan-id}.md`
- **Nomenclatura folder**: Solo el identificador (ej: `task-03`, no `task-03-fix-scbuffer`)
- **Confirmar con usuario**: Antes de persistir el plan final

## Formato de Salida

El plan debe incluir las siguientes secciones:

### 0. Metadatos del Workplan

```markdown
# Plan de Trabajo: [Task ID] - [Título]

**Fecha de Creación**: YYYY-MM-DD
**Versión**: 1.0 (o rev-X si es revisión)
**Estado**: Pendiente de Aprobación | Aprobado | En Ejecución | Completado
**Autor**: Claude Code
**Stack**: MCP (stdio) + ChromaDB (embedded) + Anthropic Claude + sentence-transformers + httpx + Selenium + PyMuPDF

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | YYYY-MM-DD | Plan inicial | Creación del workplan para [tarea] |
| rev-1 | YYYY-MM-DD | [Cambios específicos] | [Motivo del cambio] |

---
```

### 1. Resumen Ejecutivo
- Descripción general de la tarea (2-3 párrafos)
- Alcance y objetivos principales
- **Componentes del sistema MCP afectados** (MCP tools/scraping/PDF processing/RAG/sessions)
- **Referencia a fase del MCP_PLAN.md** (¿Qué fase(s) toca esta tarea?)
- Estimación de tiempo y recursos

### 2. Priorización del Alcance

**Principio**: Define qué es OBLIGATORIO vs OPCIONAL para entregar valor mínimo.

#### 🔴 MVP/CORE (Obligatorio)
**Criterio de éxito**: [Estado "completo" mínimo aceptable]

Funcionalidades core:
- [ ] [Feature 1]
- [ ] [Feature 2]
- [ ] [Feature N]

**Componentes MVP**: `[lista de archivos obligatorios]`

#### 🟡 Enhanced (Si hay tiempo)
**Funcionalidades que agregan valor pero no bloquean:**
- [ ] [Feature enhanced 1]
- [ ] [Feature enhanced 2]

**Componentes Enhanced**: `[lista de archivos opcionales]`

#### 🟢 Nice-to-Have (Futuras iteraciones)
**Para versiones posteriores:**
- [ ] [Feature future 1]
- [ ] [Feature future 2]

**Justificación postponer**: [Por qué no son prioritarias ahora]

#### Plan de Reducción de Alcance
**Si se excede el tiempo estimado:**

1. **Recorte Nivel 1**: Eliminar Enhanced completo → Ahorro: X horas
2. **Recorte Nivel 2**: Simplificar componentes core → Ahorro: Y horas
3. **Core absoluto inamovible**: [Features que NUNCA se recortan]

### 3. Diseño Técnico

#### Arquitectura Propuesta
[Descripción de alto nivel de la arquitectura]

**Componentes afectados**:
- MCP Server: `src/sortgs_mcp/server.py`, `src/sortgs_mcp/tools/`
- Scraping: `src/sortgs_mcp/core/scholar.py`, `src/sortgs_mcp/core/parser.py`
- Session Management: `src/sortgs_mcp/core/session.py`
- PDF Processing: `src/sortgs_mcp/pdf/downloader.py`, `src/sortgs_mcp/pdf/parser.py`, `src/sortgs_mcp/pdf/chunker.py`
- LLM Integration: `src/sortgs_mcp/llm/claude.py`, `src/sortgs_mcp/llm/keywords.py`
- RAG System: `src/sortgs_mcp/rag/vectorstore.py`, `src/sortgs_mcp/rag/embeddings.py`, `src/sortgs_mcp/rag/retriever.py`
- Models: `src/sortgs_mcp/models.py` (pydantic)
- Config: `src/sortgs_mcp/config.py` (pydantic-settings)

#### Diagrama de Componentes (si aplica)
```mermaid
[Diagrama Mermaid si es necesario]
```

#### Consideraciones Específicas de MCP + RAG

**MCP Tools Affected**:
- [ ] ¿Requiere nuevos tools? Sí/No - ¿Cuáles?
- [ ] ¿Cambios en tool schemas? Sí/No - ¿Qué campos?
- [ ] ¿Cambios en MCP server entry point? Sí/No

**Google Scholar Scraping**:
- [ ] ¿Afecta lógica de scraping? Sí/No
- [ ] ¿Cambios en parsing HTML? Sí/No
- [ ] ¿Requiere manejo de CAPTCHA? Sí/No
- [ ] ¿Cambios en rate limiting? Sí/No

**Chunking Strategy**:
- [ ] ¿Afecta chunking? Sí/No
- Strategy: recursive (MVP) | semantic (Enhanced)
- Parámetros: chunk_size (default: 1000), chunk_overlap (default: 200)

**Embeddings**:
- [ ] ¿Cambios en embeddings? Sí/No
- Modelo: sentence-transformers (all-mpnet-base-v2, local)
- Dimensiones: 768 (fixed para all-mpnet-base-v2)

**Retrieval**:
- [ ] ¿Cambios en retrieval? Sí/No
- Tipo: similarity (ChromaDB cosine)
- Parámetros: k (top_k chunks), session_id (scope)

**Prompt Engineering**:
- [ ] ¿Cambios en prompts? Sí/No - Keyword generation | RAG answering
- Template: Ver `src/sortgs_mcp/llm/keywords.py` y `src/sortgs_mcp/llm/claude.py`

**ChromaDB Collections**:
- [ ] ¿Cambios en collections? Sí/No
- Naming: `session_{session_id}` (per-session isolation)
- Persistence: data/vectorstore/

**PDF Processing**:
- [ ] ¿Cambios en PDF download? Sí/No
- [ ] ¿Cambios en PDF parsing? Sí/No
- Concurrent downloads: max 5, retry logic con tenacity

#### Decisiones de Arquitectura MCP

**MCP Server Design**:
- [ ] ¿Cambios en server.py? Sí/No
- Transport: stdio (fixed para Claude Code)
- Logging: FileHandler + StreamHandler (stderr para MCP)

**Tool Design**:
- [ ] ¿Tool es síncrono o asíncrono? (MCP soporta async)
- [ ] ¿Requiere estado global? (SessionManager, VectorStore singletons)
- [ ] ¿Timeout considerado? (searches largas pueden timeout)

**Error Handling**:
- [ ] Mensajes user-friendly (incluir hints de solución)
- [ ] Graceful degradation (partial failures no crashean tool)
- [ ] Logging apropiado (INFO para progress, DEBUG para details)

**Testing Strategy**:
- [ ] MCP Inspector testing (manual invocation)
- [ ] Claude Code integration testing (end-to-end)
- [ ] Unit tests con mocks (independiente de MCP)

#### Decisiones Técnicas KISS
- ¿Se reutilizan patrones existentes? [Sí/No, cuáles]
- ¿Se evita sobre-ingeniería? [Justificación]
- ¿Solución más simple posible? [Por qué esta es la más simple]

### 4. Plan de Desarrollo

**Tareas ordenadas por prioridad y dependencia:**

| ID | Prioridad | Tarea | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-----------|-------|-------------------------|--------------|----------|
| T1 | 🔴 CORE | [Descripción] | [Criterios] | - | Xh |
| T2 | 🔴 CORE | [Descripción] | [Criterios] | T1 | Yh |
| T3 | 🟡 Enhanced | [Descripción] | [Criterios] | T2 | Zh |

**Orden de implementación sugerido**: T1 → T2 → T3 → ...

### 5. Plan de Pruebas

#### Estrategia de Testing
- **Unit tests**: [Qué componentes, qué frameworks]
- **Integration tests**: [Qué flujos end-to-end]
- **Manual testing**: [Qué validar manualmente con smoke test]

#### Casos de Prueba Principales (MCP + RAG-specific)

**MCP Tools**:
- [ ] Tools registrados correctamente en MCP server
- [ ] Tool schemas válidos (inputs/outputs)
- [ ] Tools invocables desde MCP Inspector
- [ ] Tools invocables desde Claude Code
- [ ] Error handling graceful (no crashes)

**Google Scholar Scraping**:
- [ ] Search ejecuta sin robot check
- [ ] Selenium fallback funciona (si robot check)
- [ ] Parsing extrae todos los campos correctamente
- [ ] CSV guardado con formato correcto

**PDF Processing & Indexing**:
- [ ] PDFs descargan correctamente (concurrent, retry)
- [ ] PDFs validan correctamente (magic bytes %PDF)
- [ ] PyMuPDF parsea texto sin errores
- [ ] Chunking produce chunks esperados (tamaño, overlap)
- [ ] Metadata enriquecida correctamente
- [ ] Indexing a ChromaDB exitoso
- [ ] Collection session_{id} creada correctamente

**Retrieval**:
- [ ] Similarity search devuelve documentos relevantes
- [ ] Score threshold filtra documentos irrelevantes
- [ ] k documentos se recuperan correctamente

**Generation**:
- [ ] LLM genera respuestas coherentes basadas en contexto
- [ ] No hay hallucinations (respuestas fuera de corpus cuando no hay info)
- [ ] Formato de respuesta es correcto

**Quality Metrics**:
- [ ] Similarity scores > threshold definido
- [ ] Retrieval precision/recall aceptables
- [ ] Latencia de respuesta < X segundos

#### Criterios de Calidad
- Similarity threshold mínimo: [valor]
- Latencia máxima aceptable: [valor]
- Cobertura de tests: [si aplica]

### 6. Smoke Test Checklist (MCP-adapted)

**Propósito**: Checklist manual para ejecutar y adjuntar al PR como evidencia.

**Formato copiable para PR:**

```markdown
**SMOKE TEST CHECKLIST - [Task ID]**

**Ejecutado por**: [Nombre]
**Fecha**: [YYYY-MM-DD]
**Ambiente**: Local Development
**MCP Server**: sortgs-mcp
**Data Directory**: ./data (local filesystem)

---

#### 1. Setup y Configuración

- [ ] **1.1** Variables de entorno configuradas (.env con ANTHROPIC_API_KEY)
- [ ] **1.2** Dependencias instaladas (`pip install -e .`)
- [ ] **1.3** ChromaDB directories creadas (data/sessions/, data/vectorstore/)
- [ ] **1.4** MCP server registrado en Claude Code (`claude mcp list` muestra sortgs-mcp)
- [ ] **1.5** Logs configurados (sortgs_mcp.log se crea correctamente)

---

#### 2. MCP Server Connection

- [ ] **2.1** MCP server arranca sin errores (`python -m sortgs_mcp.server` en stdio mode)
- [ ] **2.2** MCP Inspector conecta correctamente (`mcp inspect python -m sortgs_mcp.server`)
- [ ] **2.3** Todos los tools esperados aparecen listados (6 tools para implementación completa)
- [ ] **2.4** Tool schemas son válidos (inputs/outputs correctos)

**Screenshot requerido**: MCP Inspector mostrando tools disponibles
![Adjuntar aquí]

---

#### 3. Tool: generate_search_keywords (si aplica a la tarea)

- [ ] **3.1** Tool acepta query válida
- [ ] **3.2** Genera num_variations keywords correctamente
- [ ] **3.3** Keywords son relevantes al query
- [ ] **3.4** Respuesta JSON válida con campo "keywords"
- [ ] **3.5** No hay errores de API (Claude API key funciona)

**Query de prueba**: "papers about transformers in NLP"
**Num variations**: 3
**Screenshot requerido**: Output mostrando keywords generadas
![Adjuntar aquí]

---

#### 4. Tool: search_papers (si aplica a la tarea)

- [ ] **4.1** Tool ejecuta búsqueda en Google Scholar
- [ ] **4.2** Session ID se genera correctamente (UUID)
- [ ] **4.3** Papers encontrados >= 1 (o maneja correctamente 0 results)
- [ ] **4.4** CSV guardado en data/sessions/{session_id}/results.csv
- [ ] **4.5** metadata.json guardado correctamente
- [ ] **4.6** No hay robot check (o Selenium fallback funciona)
- [ ] **4.7** Sorting funciona (por Citations o cit/year)

**Keywords**: [indicar keywords usados]
**Num results**: 10
**Sort by**: Citations
**Screenshot requerido**: Output mostrando session_id y top 5 papers
![Adjuntar aquí]

---

#### 5. Tool: download_papers (si aplica a la tarea)

- [ ] **5.1** Tool descarga PDFs de session correcta
- [ ] **5.2** PDFs guardados en data/sessions/{session_id}/pdfs/
- [ ] **5.3** Validación de PDFs (magic bytes %PDF)
- [ ] **5.4** Retry logic funciona para PDFs temporalmente no disponibles
- [ ] **5.5** Failed downloads reportados correctamente
- [ ] **5.6** Concurrent downloads respeta max_concurrent (5)

**Session ID**: [session_id de paso 4]
**Max papers**: 5
**Screenshot requerido**: Output mostrando downloaded/failed counts
![Adjuntar aquí]

---

#### 6. Tool: index_papers (si aplica a la tarea)

- [ ] **6.1** PDFs parseados correctamente con PyMuPDF
- [ ] **6.2** Chunks creados con tamaño esperado (chunk_size ± overlap)
- [ ] **6.3** Embeddings generados (sentence-transformers funciona)
- [ ] **6.4** ChromaDB collection creada (session_{session_id})
- [ ] **6.5** Chunks indexados correctamente (count matches)
- [ ] **6.6** Metadata preservada en cada chunk
- [ ] **6.7** Session.indexed flag actualizado a True

**Session ID**: [session_id]
**Chunk size**: 1000
**Chunk overlap**: 200
**Screenshot requerido**: Output mostrando papers_indexed, chunks_created, indexing_time
![Adjuntar aquí]

---

#### 7. Tool: query_papers (RAG Query)

- [ ] **7.1** Query ejecuta sin errores
- [ ] **7.2** Retrieval devuelve chunks relevantes (top_k)
- [ ] **7.3** Claude genera respuesta coherente basada en contexto
- [ ] **7.4** Respuesta incluye citations (Author et al., Year)
- [ ] **7.5** Sources incluidas con relevance scores
- [ ] **7.6** Query no-respondible devuelve "No hay información suficiente..."
- [ ] **7.7** Cross-session query funciona (si session_id = None)

**Query respondible**: "What are the main innovations in the Transformer architecture?"
**Query no-respondible**: "What is the weather today?"
**Session ID**: [session_id] o None para cross-session
**Screenshot requerido**: Ambas queries con respuestas
![Adjuntar aquí]

---

#### 8. Tool: list_sessions

- [ ] **8.1** Lista todas las sesiones existentes
- [ ] **8.2** Metadata correcta (keywords, created_at, papers_count, indexed)
- [ ] **8.3** JSON válido

**Screenshot requerido**: Output de list_sessions
![Adjuntar aquí]

---

#### 9. Google Scholar Scraping (si aplica)

- [ ] **9.1** Scraping funciona sin robot check (delays configurados)
- [ ] **9.2** Selenium fallback funciona (si robot check ocurre)
- [ ] **9.3** CAPTCHA manual solving permite continuar (si aplica)
- [ ] **9.4** Parsing HTML extrae todos los campos (title, authors, citations, year, pdf_url)
- [ ] **9.5** Debug mode funciona (web archive)

---

#### 10. Code Quality

- [ ] **10.1** No hay print() olvidados (usar logging)
- [ ] **10.2** No hay debugger statements o breakpoints
- [ ] **10.3** Código sigue convenciones (snake_case, docstrings, type hints)
- [ ] **10.4** No hay imports no utilizados
- [ ] **10.5** Pydantic models validan correctamente
- [ ] **10.6** Error handling graceful (no crashes, mensajes claros)

---

#### 11. Tests Automatizados (si aplica)

- [ ] **11.1** Unit tests pasan (`pytest tests/`)
- [ ] **11.2** Integration tests pasan
- [ ] **11.3** Coverage > 70% (si se implementaron tests)

**Screenshot requerido**: Output de pytest
![Adjuntar aquí]

---

#### 12. Documentation

- [ ] **12.1** Funciones tienen docstrings claros
- [ ] **12.2** CLAUDE.md actualizado (si cambios arquitectónicos)
- [ ] **12.3** README actualizado (si cambios en comandos/uso MCP)
- [ ] **12.4** MCP_PLAN.md actualizado (si fase completada)
- [ ] **12.5** Comentarios solo donde lógica no es obvia (KISS)

---

#### 13. MCP Integration (Claude Code)

- [ ] **13.1** Tools invocables desde Claude Code chat
- [ ] **13.2** Errores se manejan gracefully en chat
- [ ] **13.3** Respuestas son claras y útiles
- [ ] **13.4** No hay logs verbosos en stdout (solo en archivo)

**Screenshot requerido**: Claude Code invocando un tool
![Adjuntar aquí]

---

#### 14. Git y PR

- [ ] **14.1** Branch creado desde dev (branch principal del proyecto)
- [ ] **14.2** Commits descriptivos y atómicos
- [ ] **14.3** PR creado con título y descripción clara
- [ ] **14.4** Screenshots adjuntos al PR
- [ ] **14.5** Smoke test checklist incluido en PR
- [ ] **14.6** MCP_PLAN.md referencia actualizada (marcar fase completada)

---

**RESULTADO FINAL**

- [ ] ✅ **TODOS LOS TESTS PASAN** - Feature lista para code review
- [ ] ⚠️ **HAY ISSUES MENORES** - Documentar en comentarios del PR
- [ ] ❌ **HAY ISSUES BLOQUEANTES** - No crear PR hasta resolverlos

**Notas adicionales**:
[Agregar observaciones, bugs encontrados, o mejoras sugeridas]

---
```

**IMPORTANTE**: Adaptar esta checklist según:
- **Fase del MCP_PLAN.md**: Fase 1-2 (solo MCP tools), Fase 3-5 (PDF), Fase 6-7 (RAG)
- **Tipo de tarea**: Scraping | PDF processing | Indexing | RAG | MCP tool development

### 7. Riesgos y Mitigaciones (OPCIONAL para tareas pequeñas)

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| [Riesgo 1] | Alta/Media/Baja | Alto/Medio/Bajo | [Estrategia] |

### 8. Cronograma (OPCIONAL para tareas pequeñas)

- **Fase 1**: [Descripción] - Entregable: [X]
- **Fase 2**: [Descripción] - Entregable: [Y]
- **Hito final**: [Descripción]

### 9. Plan de Contingencia (simplificado)

**Punto de Decisión GO/NO-GO**:
- **Cuándo**: [Día/hora límite]
- **Verificar**: MVP al menos al 80% completado
- **Si no se cumple**: Activar plan de reducción de alcance (Sección 2)

**Escenarios de bloqueo comunes**:
1. **Google Scholar robot check persistente**: → Aumentar delays, usar debug mode (web archive), VPN, reducir num_results
2. **Anthropic Claude API rate limit**: → Usar retry logic (tenacity), reducir llamadas, caché de keywords
3. **CAPTCHA manual en MCP context**: → NO es viable (stdio no interactivo) → Documentar workaround (usar CLI legacy para search)
4. **ChromaDB corruption**: → Limpiar data/vectorstore/, re-indexar desde PDFs guardados
5. **PDF downloads masivamente fallidos**: → Reducir concurrency, verificar URLs manualmente, reportar en issues
6. **Selenium WebDriver issues**: → Verificar chromedriver instalado, PATH configurado, versión compatible
7. **Cambios de requisitos**: → Crear revisión del workplan

### 10. Decisiones Técnicas TOMADAS

**Instrucciones**: Para cada decisión técnica crítica, documentar:

#### 10.X [Nombre de la Decisión]

**Decisión TOMADA**: [Opción seleccionada]

**Justificación**:
- ✅ [Razón 1 - pros]
- ✅ [Razón 2 - pros]
- ✅ [Razón 3 - pros]

**Alternativas consideradas**:
- **Opción B**: [Descripción] - Pro: [X], Contra: [Y]
- **Opción C**: [Descripción] - Pro: [X], Contra: [Y]

**Trade-off aceptado**: [Qué sacrificamos]

**Principio KISS aplicado**: [Cómo esta es la solución más simple]

**Plan de migración futura** (si aplica): [Cómo cambiar si es necesario]

---

**Ejemplos de decisiones a tomar (no dejar pendientes)**:
- Chunking strategy (recursive vs semantic)
- Embedding model (all-mpnet-base-v2 vs all-MiniLM-L6-v2) [local models]
- Retrieval type (similarity ChromaDB vs cross-session)
- Claude model (Haiku vs Sonnet para keywords/RAG)
- MCP tool design (sync vs async, timeout strategy)
- PDF download concurrency (max 5 vs 10)
- Testing approach (manual vs automatizado)

**Solo consultar al usuario cuando**:
- Requisitos ambiguos que afecten funcionalidad core
- Decisiones de negocio (no técnicas)
- Trade-offs que impacten significativamente costos/plazos

### 11. Apéndices (OPCIONAL)

- **Referencias**: [Links a docs, papers, etc.]
- **Glosario**: [Términos técnicos específicos]
- **Notas adicionales**: [Cualquier información relevante]

## Acciones Finales

1. **Verificar si existe workplan previo**:
   - Revisar `./.claude/workplans/{task-id}/`
   - Si existe: Crear revisión con formato `{workplan-id}-rev-{X}.md`
   - Si no existe: Crear workplan inicial

2. **Confirmar el plan con el usuario**:
   - Presentar resumen del plan
   - Solicitar aprobación antes de persistir

3. **Crear/actualizar el archivo del plan**:
   - Ubicación: `./.claude/workplans/{task-id}/{workplan-id}.md` (o `-rev-{X}.md`)
   - Asegurar que folder `{task-id}` existe

4. **Verificar persistencia**:
   - Confirmar que archivo se guardó correctamente
   - Listar archivos en `./.claude/workplans/{task-id}/` para verificar

5. **Proporcionar resumen**:
   - Resumen ejecutivo del plan
   - Próximos pasos para el usuario
   - Link al archivo del workplan

---

## Ejemplo de Estructura Completa

Ver ejemplo en secciones anteriores (Sección 0-11).

**Recordatorios finales**:
- ✅ Aplicar filosofía KISS en todas las decisiones
- ✅ Tomar decisiones técnicas (no dejarlas pendientes)
- ✅ Adaptar al contexto MCP + RAG (ChromaDB, sentence-transformers, Anthropic Claude, Google Scholar)
- ✅ Usar sistema de revisiones cuando corresponda
- ✅ Generar smoke test checklist específico para la tarea
- ✅ Priorizar MVP vs Enhanced vs Nice-to-Have
- ✅ Conservar funcionalidades actuales del sistema

---
