# Workplan: Fase 7 - RAG Question Answering (Rev 1)

---

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 7: RAG Question Answering |
| **Fecha creación** | 2025-12-30 |
| **Versión** | 1.1 (rev-1) |
| **Estado** | Revisado |
| **Autor** | Claude Code (Coordinador de Planificación) |
| **Tarea relacionada** | task-08-fase-7.md |
| **Fase MCP_PLAN.md** | Fase 7 (líneas 1396-1662) |
| **Dependencias** | Fases 0-6 (Setup, Core, MCP Server, Keywords, PDF, RAG VectorStore) |

**Stack Tecnológico:**
- OpenAI API (GPT-4o-mini) para answer generation
- ChromaDB para retrieval
- sentence-transformers embeddings (reutilizado de Fase 6)
- AsyncIO para operaciones concurrentes
- Pydantic para validación

**Historial de Revisiones:**
| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Primera planificación | Usuario |
| 1.1 (rev-1) | 2025-12-30 | Mejoras post-revisión codex | Unificar tests, precisar QueryResult, aclarar instanciación, separar Enhanced | Codex + Usuario |

**Cambios en Rev-1:**
1. ✅ Unificado plan de tests en un solo archivo: `tests/test_rag_phase7.py`
2. ✅ Precisado contrato de `QueryResult` con validaciones específicas (sección 3.3 nueva)
3. ✅ Aclarada estrategia de instanciación de componentes en tools (sección 3.4 nueva)
4. ✅ Separado Enhanced del flujo principal (T7.10 removida de Fase 2)

---

## 1. Resumen Ejecutivo

**Descripción General:**
Implementar el sistema completo de RAG (Retrieval-Augmented Generation) para responder preguntas académicas sobre papers indexados, con citas a las fuentes.

**Alcance:**
- Completar método `generate_answer()` en `OpenAIClient` (actualmente NotImplementedError)
- Crear clase `RAGRetriever` con pipeline completo: embed → retrieve → generate
- Implementar 2 MCP tools: `query_papers` (principal) y `list_sessions` (helper)
- Tests de integración end-to-end para validar el pipeline completo

**Objetivos:**
1. ✅ Pipeline RAG funcional de pregunta a respuesta con citas
2. ✅ Integración fluida con componentes de Fase 6 (VectorStore, Embeddings)
3. ✅ Tools MCP listos para uso en Claude Code
4. ✅ Calidad de respuestas académicas con citations correctas

**Componentes MCP Afectados:**
- `src/sortgs_mcp/llm/openai.py` - añadir `generate_answer()`
- `src/sortgs_mcp/rag/retriever.py` - **NUEVO** archivo con `RAGRetriever`
- `src/sortgs_mcp/tools/query.py` - **NUEVO** archivo con 2 tools
- `tests/test_rag_phase7.py` - **NUEVO** tests unificados (unit + integration)

**Referencia a MCP_PLAN.md:**
Fase 7 (líneas 1396-1662) - "RAG - Question Answering"

---

## 2. Priorización del Alcance

### 2.1 MVP/CORE (Obligatorio)

**Criterio de Éxito:**
- Usuario puede hacer una pregunta sobre papers indexados
- Sistema retorna respuesta coherente con citas académicas en formato esperado
- Pipeline completo `search → download → index → query` funciona end-to-end
- Tests básicos pasan con fixtures locales (sin dependencias de red)

**Componentes Obligatorios:**
1. **`generate_answer()` en OpenAIClient** - Prompt engineering + API call
2. **`RAGRetriever` básico** - Pipeline simple embed→query→generate
3. **Tool `query_papers`** - Funcionalidad principal de Q&A
4. **Tool `list_sessions`** - Helper para ver sesiones disponibles
5. **1 test de integración end-to-end** - Validar pipeline completo con mocks
6. **Unit tests básicos** - Test `generate_answer()` con mock

**Recortable si falta tiempo:**
- ❌ NADA - todos los componentes MVP son esenciales

### 2.2 Enhanced (Opcional - si sobra tiempo)

**Componentes:**
1. **Cross-session query** - Buscar en todas las sesiones si no se especifica `session_id`
2. **Citation extraction** - Parsear y validar citas en la respuesta
3. **Logging avanzado** - Logs estructurados con contexto completo
4. **Tests comprehensivos** - Casos edge, validación de prompts, etc.

**Justificación:**
- Cross-session query es útil pero no crítico para MVP
- Citation extraction puede hacerse manualmente revisando la respuesta
- Logging básico ya existe en componentes actuales

### 2.3 Nice-to-Have (Futuro)

**Componentes:**
1. **Streaming de respuestas** - Respuestas incrementales (requiere cambios en MCP protocol)
2. **Cache de query embeddings** - Optimización de queries repetidas
3. **Re-ranking de chunks** - Mejorar calidad de retrieval con modelo adicional
4. **Feedback loop** - Evaluar calidad de respuestas y ajustar

**Justificación:**
- Requieren arquitectura adicional fuera del scope de Fase 7
- No son necesarios para funcionalidad básica
- Pueden añadirse iterativamente en fases futuras

### 2.4 Plan de Reducción de Alcance

**Si falta 30% de tiempo:**
- Recortar Enhanced: cross-session query, citation extraction
- Simplificar tests: solo 1 integration test end-to-end
- Mantener TODO: Core MVP completo

**Si falta 50% de tiempo:**
- Recortar todo Enhanced
- Reducir unit tests al mínimo (solo test `generate_answer()`)
- Mantener TODO: Core MVP sin tests comprehensivos

**Core Inamovible:**
- `generate_answer()` implementation
- `RAGRetriever` class
- Tool `query_papers`
- Tool `list_sessions`
- 1 test end-to-end básico

---

## 3. Diseño Técnico

### 3.1 Arquitectura Propuesta

**Diagrama de Flujo:**
```
User Question
    ↓
query_papers(question, session_id?, top_k=5)
    ↓
RAGRetriever.answer_question()
    ├─ 1. EmbeddingService.embed_single(question)
    ├─ 2. VectorStore.query(embedding, session_id, k)
    ├─ 3. Build context from chunks
    ├─ 4. OpenAIClient.generate_answer(question, context)
    └─ 5. Format QueryResult with sources
    ↓
Return QueryResult.model_dump()
```

**Componentes Afectados:**

| Componente | Cambio | Tipo |
|------------|--------|------|
| `llm/openai.py` | Implementar `generate_answer()` | Modificación |
| `rag/retriever.py` | Nueva clase `RAGRetriever` | Creación |
| `tools/query.py` | Nuevos tools MCP | Creación |
| `tests/test_rag_phase7.py` | **Tests unificados** (unit + integration) | Creación |

### 3.2 Decisiones Técnicas (KISS)

**DT-1: Prompt Template para RAG**
- **Decisión:** Prompt hardcoded en `generate_answer()` siguiendo patrón de `generate_keywords()`
- **Alternativas rechazadas:** Sistema de templates configurables (sobre-ingeniería para MVP)
- **Justificación KISS:** Un solo prompt bien diseñado es suficiente; configuración añade complejidad sin valor inmediato

**DT-2: Formato de Context Building**
- **Decisión:** Formato numerado simple `[1] Paper Title (Authors, Year):\nChunk text`
- **Alternativas rechazadas:** Markdown complejo, JSON estructurado
- **Justificación KISS:** Formato legible que el LLM entiende fácilmente; menos parsing = menos bugs

**DT-3: Similarity Score Conversion**
- **Decisión:** `similarity = 1.0 - distance` (ChromaDB retorna distancia coseno)
- **Alternativas rechazadas:** Normalización compleja, múltiples métricas
- **Justificación KISS:** Conversión directa y matemáticamente correcta para cosine distance

**DT-4: Cross-Session Query (Enhanced)**
- **Decisión:** Si `session_id=None`, iterar sobre todas las collections y merge results
- **Alternativas rechazadas:** Collection global compartida (pérdida de aislamiento)
- **Justificación KISS:** Reutiliza `VectorStore.query()` existente; merge simple por distance

**DT-5: Error Handling en Pipeline**
- **Decisión:** Raise exceptions en validación; return QueryResult con mensaje en casos sin resultados
- **Alternativas rechazadas:** Return None, códigos de error custom
- **Justificación KISS:** Sigue patrón de tools existentes (ver `index.py`); consistente con Pydantic validation

**DT-6: Async/Sync Boundaries**
- **Decisión:** `asyncio.to_thread()` para embeddings sync (siguiendo patrón de `index.py`)
- **Alternativas rechazadas:** Hacer todo sync, crear wrapper async para embeddings
- **Justificación KISS:** Reutiliza patrón probado en Fase 6; no modifica `EmbeddingService`

### 3.3 Contrato de QueryResult (NUEVO en Rev-1)

**Definición del Modelo (ya existe en `models.py`):**
```python
class QuerySource(BaseModel):
    paper_title: str
    chunk_text: str
    relevance_score: float  # Range [0.0, 1.0]
    metadata: dict  # Debe incluir: authors, year, citations, source_url

class QueryResult(BaseModel):
    question: str
    answer: str  # Debe contener citas en formato académico
    sources: list[QuerySource]
    session_id: str | None
```

**Formato Esperado de Citas en `answer`:**
- Estilo académico: `(Author et al., Year)`
- Ejemplo: `"The Transformer architecture uses self-attention (Vaswani et al., 2017) to..."`
- Citas deben corresponder a papers en `sources`

**Validaciones en Tests:**
1. `answer` no vacío (len > 10 caracteres)
2. `sources` contiene al menos 1 elemento si answer no es "No relevant information found"
3. Cada `QuerySource.relevance_score` en rango [0.0, 1.0]
4. Cada `QuerySource.metadata` contiene keys: `authors`, `year`, `citations`, `source_url`
5. Si `answer` contiene paréntesis con año (ej: "2017"), al menos un `source` debe tener `year: 2017`

**Comportamiento ante Sesiones Vacías:**
- Si `session_id` no existe → Raise `ValueError("Session not found")`
- Si session existe pero no indexada (`session.indexed == False`) → Raise `RuntimeError("Session not indexed")`
- Si session indexada pero query no retorna chunks → Return `QueryResult` con `answer="No relevant information found in indexed papers."`

### 3.4 Estrategia de Instanciación de Componentes (NUEVO en Rev-1)

**Problema:** Tools MCP pueden ser llamados múltiples veces; necesitamos evitar sobrecosto de instanciación repetida y problemas de concurrencia.

**Solución (siguiendo patrón de `index.py`):**

**En `tools/query.py`:**
```python
from sortgs_mcp.config import settings
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.rag import VectorStore, get_embedding_service
from sortgs_mcp.llm.openai import OpenAIClient

# Instancias globales (creadas una vez al import del módulo)
session_manager = SessionManager(settings.data_dir)

# Para componentes costosos, lazy initialization
_openai_client = None
_vectorstore = None
_embedder = None

def _get_openai_client() -> OpenAIClient:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model_rag
        )
    return _openai_client

def _get_vectorstore() -> VectorStore:
    global _vectorstore
    if _vectorstore is None:
        embedder = _get_embedder()
        _vectorstore = VectorStore(
            settings.chroma_persist_dir,
            embedding_dim=embedder.embedding_dim,
            distance_metric="cosine",
            model_name=embedder.model_name,
        )
    return _vectorstore

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = get_embedding_service(settings.embedding_model)
    return _embedder
```

**Ciclo de Vida:**
- Instancias se crean al primer uso (lazy)
- Se reutilizan entre múltiples llamadas al tool
- Thread-safe: AsyncOpenAI client es thread-safe; ChromaDB client también
- No hay teardown explícito (Python garbage collection al exit)

**Justificación KISS:**
- Reutiliza patrón de `index.py` (SessionManager global)
- Evita overhead de recrear sentence-transformers model (>1s carga) por cada query
- No requiere dependency injection framework (sobre-ingeniería)

---

## 4. Plan de Desarrollo

### 4.1 Tareas de Implementación

| ID | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-------|-----------|------------------------|--------------|----------|
| **T7.1** | Implementar `generate_answer()` en `OpenAIClient` | 🔴 CORE | - Método acepta `question: str` y `context: str`<br>- Llama OpenAI API con retry logic<br>- Retorna respuesta como string<br>- Logging de tokens usados | Ninguna | 1h |
| **T7.2** | Crear prompt template para RAG | 🔴 CORE | - Prompt instruye respuestas académicas con citas<br>- Formato context numerado<br>- Include instrucciones "based ONLY on context" | T7.1 | 30m |
| **T7.3** | Crear `RAGRetriever` class en `rag/retriever.py` | 🔴 CORE | - Constructor acepta vectorstore, embedder, openai_client<br>- Método `answer_question()` implementado<br>- Pipeline completo funciona | T7.1 | 2h |
| **T7.4** | Implementar pipeline en `RAGRetriever.answer_question()` | 🔴 CORE | - Embed question con EmbeddingService<br>- Query VectorStore con embedding<br>- Build context from top-k chunks<br>- Generate answer con OpenAIClient<br>- Format QueryResult con sources (validar contrato sección 3.3) | T7.3 | 1.5h |
| **T7.5** | Crear `tools/query.py` con tool `query_papers` | 🔴 CORE | - Decorator `@mcp.tool()`<br>- Parámetros: question, session_id?, top_k=5<br>- Lazy initialization de componentes (ver sección 3.4)<br>- Return QueryResult.model_dump() | T7.4 | 1h |
| **T7.6** | Crear tool `list_sessions` en `tools/query.py` | 🔴 CORE | - Decorator `@mcp.tool()`<br>- Call SessionManager.list_sessions()<br>- Return dict con sessions list | Ninguna | 30m |
| **T7.7** | Unit tests en `tests/test_rag_phase7.py` | 🔴 CORE | - Test `generate_answer()` con mock OpenAI API<br>- Verificar prompt construction<br>- Verificar retry logic | T7.1 | 45m |
| **T7.8** | Integration tests en `tests/test_rag_phase7.py` | 🔴 CORE | - Pipeline completo con mocks<br>- Verificar QueryResult contrato (sección 3.3)<br>- Test edge cases (session not found, not indexed, no results) | T7.5, T7.6 | 1.5h |
| **T7.9** | Implementar cross-session query | 🟡 Enhanced | - Si session_id=None, query all collections<br>- Merge results por distance<br>- Sort y return top-k global | T7.4 | 1h |
| **T7.10** | Tests comprehensivos en `tests/test_rag_phase7.py` | 🟡 Enhanced | - Test cross-session query<br>- Test validación de citas en answer<br>- Test metadata completitud | T7.9 | 1h |

**Tiempo Total Estimado:**
- **CORE:** ~9 horas
- **Enhanced:** ~2 horas
- **TOTAL:** ~11 horas

### 4.2 Orden de Implementación Sugerido

**Fase 1: OpenAI Integration (2h)**
1. T7.1 - Implementar `generate_answer()`
2. T7.2 - Crear prompt template
3. T7.7 - Unit test con mock

**Fase 2: RAG Retriever (3.5h)** *(Enhanced removido de esta fase)*
4. T7.3 - Crear clase `RAGRetriever`
5. T7.4 - Implementar pipeline completo

**Fase 3: MCP Tools (1.5h)**
6. T7.5 - Tool `query_papers` (con lazy initialization)
7. T7.6 - Tool `list_sessions`

**Fase 4: Validación Core (1.5h)**
8. T7.8 - Integration tests con validación de contrato

**Fase 5: Enhanced (2h - opcional)**
9. T7.9 - Cross-session query
10. T7.10 - Tests comprehensivos

---

## 5. Plan de Pruebas

### 5.1 Estrategia de Testing

**Niveles de Testing:**
1. **Unit Tests** - Mock dependencies externas (OpenAI API, VectorStore)
2. **Integration Tests** - Pipeline con mocks (sin red)
3. **Manual Smoke Tests** - Validación con MCP Inspector y Claude Code

**Herramientas:**
- pytest para automatización
- pytest-asyncio para async tests
- unittest.mock para mocking OpenAI API, VectorStore, EmbeddingService
- **NO dependencias de red:** fixtures locales para todas las pruebas automatizadas

**Archivo Unificado:** `tests/test_rag_phase7.py` (contiene unit + integration tests)

### 5.2 Test Cases en `tests/test_rag_phase7.py`

**Sección 1: Unit Tests para `generate_answer()`**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_generate_answer_success` | Mock OpenAI API retorna respuesta | - Prompt contiene question y context<br>- Response extraída correctamente<br>- Tokens logged |
| `test_generate_answer_auth_error` | API key inválida | - AuthenticationError se propaga<br>- No retry para auth errors |
| `test_generate_answer_retry` | API falla primero, éxito después | - Retry ejecuta<br>- Finalmente retorna respuesta |

**Sección 2: Unit Tests para `RAGRetriever`**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_retriever_pipeline_mock` | Mock embedder + vectorstore + openai | - Embedding se genera<br>- Query ejecuta<br>- Context building correcto<br>- QueryResult válido según contrato (3.3) |
| `test_retriever_no_results` | VectorStore retorna lista vacía | - QueryResult.answer = "No relevant information found..." |
| `test_similarity_conversion` | Distance → similarity score | - `similarity = 1.0 - distance`<br>- Range [0.0, 1.0] |

**Sección 3: Integration Tests para Tools**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_query_papers_with_mocks` | Tool `query_papers` con pipeline mocked | - QueryResult completo<br>- Sources con metadata completa<br>- Validar contrato (sección 3.3) |
| `test_list_sessions` | Tool retorna sessions | - Dict con key "sessions"<br>- Cada session tiene metadata keys |
| `test_query_session_not_found` | session_id inválido | - Raise ValueError con mensaje claro |
| `test_query_session_not_indexed` | Session existe pero indexed=False | - Raise RuntimeError |

**Sección 4: Enhanced Tests (Opcional)**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_cross_session_query` | session_id=None busca en todos | - Merge results correcto<br>- Top-k global respetado |
| `test_citation_validation` | Validar formato de citas en answer | - Regex match `\(.*\d{4}\)`<br>- Years en sources |

**Tiempo Estimado:**
- Sección 1: 30m
- Sección 2: 45m
- Sección 3: 1h
- Sección 4: 1h (Enhanced)

### 5.3 Smoke Test Checklist (Manual - para adjuntar al PR)

**Pre-requisitos:**
- [ ] MCP server running: `uv run sortgs-mcp`
- [ ] Existe al menos 1 sesión indexada con PDFs

**Test Manual en MCP Inspector:**

1. **Tool `list_sessions`**
   - [ ] Ejecutar sin parámetros
   - [ ] Retorna lista de sesiones
   - [ ] Cada sesión muestra: session_id, keywords, papers_count, indexed status

2. **Tool `query_papers` - Query básica**
   - [ ] Ejecutar con: `{"question": "What is the main contribution?", "session_id": "<id>", "top_k": 3}`
   - [ ] Retorna `QueryResult` con answer (no vacío)
   - [ ] Sources contiene ≤3 chunks
   - [ ] Metadata incluye: paper_title, authors, year, citations, source_url

3. **Tool `query_papers` - Sin resultados**
   - [ ] Ejecutar con pregunta irrelevante: `{"question": "How to cook pasta?", ...}`
   - [ ] Retorna mensaje "No relevant information found in indexed papers."

4. **Validación de Citas**
   - [ ] Respuesta incluye referencias académicas (ej: "(Vaswani et al., 2017)")
   - [ ] Years en citas coinciden con sources

**Test Manual en Claude Code:**

5. **Workflow Completo**
   - [ ] Generar keywords para un tema
   - [ ] Buscar papers
   - [ ] Descargar PDFs
   - [ ] Indexar papers
   - [ ] **Hacer pregunta sobre papers indexados**
   - [ ] Verificar respuesta coherente con citas

6. **Logging**
   - [ ] Verificar logs en `sortgs_mcp.log`
   - [ ] Logs incluyen: tokens usados, chunks retrieved, timing

**Criterios de Pase:**
- ✅ Todos los checks marcados
- ✅ No crashes ni exceptions no manejadas
- ✅ Respuestas tienen calidad académica (coherentes, con citas)

---

## 6. Plan de Contingencia

### 6.1 Escenarios de Bloqueo

**Bloqueo B1: OpenAI API Rate Limiting**
- **Señal:** Tests fallan con RateLimitError frecuente
- **Impacto:** No se puede validar generate_answer()
- **Mitigación:**
  1. Usar mocks para todos los tests automatizados (OBLIGATORIO)
  2. Manual smoke tests con delays entre calls
  3. Upgrade a tier con mayor límite (si crítico para producción)

**Bloqueo B2: Calidad de Respuestas Pobre**
- **Señal:** LLM genera respuestas genéricas sin citas
- **Impacto:** No cumple criterio de "respuestas académicas"
- **Mitigación:**
  1. Iterar en prompt engineering (añadir ejemplos, instrucciones más específicas)
  2. Aumentar top_k para más contexto (default: 5 → 7)
  3. Upgrade a modelo mejor (gpt-4o en vez de mini) - cambiar solo `openai_model_rag` en settings

**Bloqueo B3: ChromaDB Query Performance Lento**
- **Señal:** Queries toman >5s para top_k=5
- **Impacto:** UX pobre en Claude Code
- **Mitigación:**
  1. Reducir top_k default a 3
  2. Revisar tamaño de collections (max_chunks limit en Fase 6)
  3. Implementar timeout en query (future work)

**Bloqueo B4: Metadata Incompleta en Sources** *(NUEVO en Rev-1)*
- **Señal:** Tests fallan por KeyError en metadata
- **Impacto:** QueryResult inválido
- **Mitigación:**
  1. Revisar chunking en Fase 6 (metadata debe incluir todos los campos)
  2. Añadir defaults en RAGRetriever si metadata falta
  3. Validar metadata antes de crear QuerySource

### 6.2 Punto de Decisión GO/NO-GO

**Después de T7.4 (RAG Pipeline implementado):**

**GO si:**
- ✅ Pipeline embed→query→generate funciona con mocks
- ✅ Unit tests pasan
- ✅ No hay blockers técnicos

**NO-GO si:**
- ❌ OpenAI API authentication falla (revisar API key en `.env`)
- ❌ ChromaDB query retorna errores (revisar Fase 6 indexing completado)
- ❌ Metadata en chunks incompleta (revisar chunking en Fase 6)

**Acción NO-GO:**
1. Pausar desarrollo
2. Debuggear bloqueo específico
3. Re-evaluar con usuario si continuar o recortar scope

### 6.3 Qué Recortar Primero

**Si falta 30% tiempo:**
1. ❌ Recortar Enhanced: cross-session query (T7.9), tests comprehensivos (T7.10)
2. ✅ Mantener: Core MVP completo

**Si falta 50% tiempo:**
1. ❌ Recortar todo Enhanced
2. ❌ Reducir integration tests: solo 1 test básico (skip edge cases)
3. ✅ Mantener: `generate_answer()`, `RAGRetriever`, 2 tools, unit tests

**Core Inamovible (nunca recortar):**
- T7.1 - `generate_answer()` implementation
- T7.4 - `RAGRetriever` pipeline
- T7.5 - Tool `query_papers`
- T7.6 - Tool `list_sessions`
- T7.7 - Unit tests básicos

---

## 7. Criterios de Aceptación Final

**El workplan se considera completo cuando:**

1. ✅ **Funcionalidad Core:**
   - Tool `query_papers` funciona en MCP Inspector
   - Tool `list_sessions` funciona en MCP Inspector
   - Pipeline end-to-end ejecuta sin errores

2. ✅ **Calidad de Código:**
   - Reutiliza patrones de fases previas (no inventa nuevos)
   - Type hints completos en funciones públicas
   - Docstrings claros
   - Error handling consistente con tools existentes
   - Lazy initialization de componentes (ver sección 3.4)

3. ✅ **Testing:**
   - Tests unificados en `tests/test_rag_phase7.py` pasan
   - Unit tests para `generate_answer()` pasan
   - Integration test con mocks pasa
   - Validación de contrato QueryResult (sección 3.3) implementada
   - Smoke test manual ejecutado (checklist completado)

4. ✅ **Calidad de Outputs:**
   - Respuestas son coherentes (no gibberish)
   - Citas académicas presentes en formato `(Author et al., Year)`
   - Sources en QueryResult cumplen contrato (metadata completa, relevance_score en [0.0, 1.0])

5. ✅ **Documentación:**
   - Logs informativos en ejecución (tokens, chunks retrieved, timing)

---

## 8. Notas Adicionales

**Reutilización de Patrones Existentes:**
- `generate_answer()` sigue mismo patrón que `generate_keywords()`: retry logic, logging, error handling
- Tools usan `@mcp.tool()` decorator como en `search.py`, `download.py`, `index.py`
- `asyncio.to_thread()` para embeddings sync (patrón de `index.py`)
- Return `model.model_dump()` para serialización (patrón universal en tools)
- **Lazy initialization** de componentes globales (patrón de `index.py`)

**Filosofía KISS Aplicada:**
- No crear abstracciones innecesarias (ej: no PromptManager class, solo string templates)
- No optimización prematura (ej: no cache de embeddings hasta tener datos de uso)
- Reutilizar componentes existentes sin modificarlos (EmbeddingService, VectorStore)
- Prompt simple que funciona > sistema configurable complejo
- Tests unificados en un solo archivo > arquitectura compleja de testing

**Dependencias Externas:**
- OpenAI API key requerida (ya configurada en `.env` de fases previas)
- ChromaDB collections creadas en Fase 6 (indexing)
- Sentence-transformers model descargado en Fase 6

**Riesgos Conocidos:**
- Calidad de respuestas depende del modelo LLM (gpt-4o-mini puede ser limitado para papers técnicos)
- Citas pueden no ser 100% precisas (LLM puede alucinar autores - mitigado con validación en tests)
- Performance de query depende de tamaño de collections (mitigado con max_chunks limit)
- Metadata en chunks debe ser completa (dependencia de Fase 6 - validar antes de empezar Fase 7)

---

**Workplan persistido:** `.claude/workplans/task-08/workplan-task-08-rev-1.md`
