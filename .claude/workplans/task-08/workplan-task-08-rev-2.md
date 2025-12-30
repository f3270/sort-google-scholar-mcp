# Workplan: Fase 7 - RAG Question Answering (Rev 2)

---

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 7: RAG Question Answering |
| **Fecha creación** | 2025-12-30 |
| **Versión** | 1.2 (rev-2) |
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
| 1.1 (rev-1) | 2025-12-30 | Mejoras post-revisión codex (1ra) | Unificar tests, precisar QueryResult, aclarar instanciación, separar Enhanced | Codex + Usuario |
| 1.2 (rev-2) | 2025-12-30 | Mejoras post-revisión codex (2da) | Aclarar async/sync, validación de citas tolerante, mapeo session_id, consistencia sources | Codex + Usuario |

**Cambios en Rev-2:**
1. ✅ Aclarado contrato async de `OpenAIClient.generate_answer()` (sección 3.2 DT-7 NUEVO)
2. ✅ Precisado validación tolerante de citas en tests (sección 3.3 actualizada)
3. ✅ Definido mapping de `session_id` a ChromaDB collections (sección 3.5 NUEVA)
4. ✅ Añadido criterio de consistencia `sources` con chunks (sección 7 actualizada)

---

## 1. Resumen Ejecutivo

**Descripción General:**
Implementar el sistema completo de RAG (Retrieval-Augmented Generation) para responder preguntas académicas sobre papers indexados, con citas a las fuentes.

**Alcance:**
- Completar método `generate_answer()` **async** en `OpenAIClient` (actualmente NotImplementedError)
- Crear clase `RAGRetriever` con pipeline completo: embed → retrieve → generate
- Implementar 2 MCP tools: `query_papers` (principal) y `list_sessions` (helper)
- Tests de integración end-to-end para validar el pipeline completo

**Objetivos:**
1. ✅ Pipeline RAG funcional de pregunta a respuesta con citas
2. ✅ Integración fluida con componentes de Fase 6 (VectorStore, Embeddings)
3. ✅ Tools MCP listos para uso en Claude Code
4. ✅ Calidad de respuestas académicas con citations correctas

**Componentes MCP Afectados:**
- `src/sortgs_mcp/llm/openai.py` - añadir `generate_answer()` **async**
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
1. **`generate_answer()` en OpenAIClient** - Prompt engineering + async API call
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
- `generate_answer()` implementation (async)
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
RAGRetriever.answer_question() [async]
    ├─ 1. await asyncio.to_thread(embedder.embed_single, question)
    ├─ 2. vectorstore.query(embedding, session_id, k)
    ├─ 3. Build context from chunks
    ├─ 4. await openai_client.generate_answer(question, context)
    └─ 5. Format QueryResult with sources
    ↓
Return QueryResult.model_dump()
```

**Componentes Afectados:**

| Componente | Cambio | Tipo |
|------------|--------|------|
| `llm/openai.py` | Implementar `generate_answer()` **async** | Modificación |
| `rag/retriever.py` | Nueva clase `RAGRetriever` con métodos **async** | Creación |
| `tools/query.py` | Nuevos tools MCP (async compatible) | Creación |
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
- **Límite de contexto:** Truncar a ~6000 caracteres si top_k alto excede límites del prompt (nota en sección 8)

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

**DT-7: Contrato Async de `generate_answer()` (NUEVO en Rev-2)**
- **Decisión:** Método `async def generate_answer()` que hace `await self.client.chat.completions.create()`
- **Implementación:** Sigue patrón exacto de `generate_keywords()` (líneas 43-65 de `openai.py`)
- **Cliente:** `AsyncOpenAI` ya instanciado en `__init__` (thread-safe, reusable)
- **Retry:** Decorator `@retry` de tenacity funciona con async functions
- **Justificación:** Consistencia total con método existente; `AsyncOpenAI` es nativamente async

**Código de Referencia:**
```python
# Patrón existente en generate_keywords()
@retry(...)
async def generate_keywords(...) -> list[str]:
    response = await self.client.chat.completions.create(...)
    # parse response
    return keywords

# Nuevo método generate_answer() seguirá mismo patrón
@retry(...)
async def generate_answer(self, question: str, context: str) -> str:
    response = await self.client.chat.completions.create(...)
    return response.choices[0].message.content or ""
```

**Impacto en Tools:**
- Tools MCP son async por defecto (`@mcp.tool()` soporta async)
- `RAGRetriever.answer_question()` será `async def`
- No necesita `asyncio.to_thread()` para llamar `generate_answer()` (ya es async)

### 3.3 Contrato de QueryResult (Actualizado en Rev-2)

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
- Citas **deben corresponder** a papers en `sources`

**Validaciones en Tests (TOLERANTES - Rev-2):**
1. `answer` no vacío (len > 10 caracteres)
2. `sources` contiene al menos 1 elemento si answer no es "No relevant information found"
3. Cada `QuerySource.relevance_score` en rango [0.0, 1.0]
4. Cada `QuerySource.metadata` contiene keys: `authors`, `year`, `citations`, `source_url`
5. **TOLERANTE:** Si `answer` contiene paréntesis con año (ej: "2017"), validar con regex flexible:
   - Match pattern: `\(\w+.*\d{4}\)` (permite variaciones en formato de autor)
   - **Fallback:** Si LLM no cita correctamente, test NO falla si answer es coherente y sources están presentes
   - **Validación estricta solo en Enhanced tests** (T7.10)

**Comportamiento ante Sesiones Vacías:**
- Si `session_id` no existe → Raise `ValueError("Session {session_id} not found")`
- Si session existe pero no indexada (`session.indexed == False`) → Raise `RuntimeError("Session {session_id} not indexed. Run index_papers first.")`
- Si session indexada pero query no retorna chunks → Return `QueryResult` con `answer="No relevant information found in indexed papers."`

### 3.4 Estrategia de Instanciación de Componentes

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
- **Thread-safe:** `AsyncOpenAI` client es thread-safe; ChromaDB client también; sentence-transformers usa numpy (thread-safe para inferencia)
- No hay teardown explícito (Python garbage collection al exit)

**Justificación KISS:**
- Reutiliza patrón de `index.py` (SessionManager global)
- Evita overhead de recrear sentence-transformers model (>1s carga) por cada query
- No requiere dependency injection framework (sobre-ingeniería)

### 3.5 Mapping de `session_id` a ChromaDB (NUEVO en Rev-2)

**Problema:** Necesitamos definir explícitamente cómo `session_id` se mapea a collections de ChromaDB y dónde se valida su existencia.

**Decisión:**
- **Collection naming:** `f"session_{session_id}"` (patrón de `vectorstore.py` línea 35)
- **Validación en Tool (`query_papers`):**
  1. Cargar session con `SessionManager.load_session(session_id)` → Raise `ValueError` si no existe
  2. Verificar `session.indexed == True` → Raise `RuntimeError` si False
  3. Pasar session_id a `RAGRetriever.answer_question()`

- **Validación en RAGRetriever:**
  - **NO duplicar** validación de existencia (ya hecha en tool)
  - Asumir session_id válido cuando se recibe
  - `VectorStore.query()` llamará `get_or_create_collection()` que retorna collection (o crea vacía si no existe)

**División de Responsabilidades:**
- **Tool:** Valida session existe y está indexada (business logic)
- **RAGRetriever:** Ejecuta retrieval asumiendo inputs válidos (pure function)
- **VectorStore:** Maneja ChromaDB collections (infraestructura)

**Código de Referencia (`vectorstore.py`):**
```python
def _collection_name(self, session_id: str) -> str:
    return f"session_{session_id}"

def get_or_create_collection(self, session_id: str):
    return self.client.get_or_create_collection(
        name=self._collection_name(session_id),
        metadata=self._collection_metadata(),
    )
```

**Justificación KISS:**
- No duplicar validación entre capas
- Tool layer = validación + orchestration
- RAGRetriever = pure pipeline execution

---

## 4. Plan de Desarrollo

### 4.1 Tareas de Implementación

| ID | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-------|-----------|------------------------|--------------|----------|
| **T7.1** | Implementar `generate_answer()` en `OpenAIClient` | 🔴 CORE | - Método **async** acepta `question: str` y `context: str`<br>- Llama `await self.client.chat.completions.create()`<br>- Sigue patrón de `generate_keywords()` (líneas 43-65)<br>- Retorna respuesta como string<br>- Logging de tokens usados | Ninguna | 1h |
| **T7.2** | Crear prompt template para RAG | 🔴 CORE | - Prompt instruye respuestas académicas con citas<br>- Formato context numerado<br>- Include instrucciones "based ONLY on context"<br>- Truncar context si >6000 chars | T7.1 | 30m |
| **T7.3** | Crear `RAGRetriever` class en `rag/retriever.py` | 🔴 CORE | - Constructor acepta vectorstore, embedder, openai_client<br>- Método `answer_question()` es **async**<br>- Pipeline completo funciona | T7.1 | 2h |
| **T7.4** | Implementar pipeline en `RAGRetriever.answer_question()` | 🔴 CORE | - `await asyncio.to_thread(embedder.embed_single, question)`<br>- Query VectorStore con embedding<br>- Build context from top-k chunks<br>- `await openai_client.generate_answer(question, context)`<br>- Format QueryResult con sources (validar contrato sección 3.3) | T7.3 | 1.5h |
| **T7.5** | Crear `tools/query.py` con tool `query_papers` | 🔴 CORE | - Decorator `@mcp.tool()` (async compatible)<br>- Parámetros: question, session_id?, top_k=5<br>- **Validar session existe y indexed** (ver sección 3.5)<br>- Lazy initialization de componentes (sección 3.4)<br>- Return QueryResult.model_dump() | T7.4 | 1h |
| **T7.6** | Crear tool `list_sessions` en `tools/query.py` | 🔴 CORE | - Decorator `@mcp.tool()`<br>- Call SessionManager.list_sessions()<br>- Return dict con sessions list | Ninguna | 30m |
| **T7.7** | Unit tests en `tests/test_rag_phase7.py` | 🔴 CORE | - Test `generate_answer()` con mock `AsyncOpenAI`<br>- Verificar prompt construction<br>- Verificar retry logic<br>- Test async execution | T7.1 | 45m |
| **T7.8** | Integration tests en `tests/test_rag_phase7.py` | 🔴 CORE | - Pipeline completo con mocks<br>- Verificar QueryResult contrato (sección 3.3 tolerante)<br>- Test edge cases (session not found, not indexed, no results)<br>- Test consistencia sources con chunks retrieved | T7.5, T7.6 | 1.5h |
| **T7.9** | Implementar cross-session query | 🟡 Enhanced | - Si session_id=None, query all collections<br>- Merge results por distance<br>- Sort y return top-k global | T7.4 | 1h |
| **T7.10** | Tests comprehensivos en `tests/test_rag_phase7.py` | 🟡 Enhanced | - Test cross-session query<br>- Test validación **estricta** de citas en answer<br>- Test metadata completitud | T7.9 | 1h |

**Tiempo Total Estimado:**
- **CORE:** ~9 horas
- **Enhanced:** ~2 horas
- **TOTAL:** ~11 horas

### 4.2 Orden de Implementación Sugerido

**Fase 1: OpenAI Integration (2h)**
1. T7.1 - Implementar `generate_answer()` **async**
2. T7.2 - Crear prompt template con truncado
3. T7.7 - Unit test con mock (async)

**Fase 2: RAG Retriever (3.5h)**
4. T7.3 - Crear clase `RAGRetriever` (async)
5. T7.4 - Implementar pipeline completo

**Fase 3: MCP Tools (1.5h)**
6. T7.5 - Tool `query_papers` (con validación session)
7. T7.6 - Tool `list_sessions`

**Fase 4: Validación Core (1.5h)**
8. T7.8 - Integration tests con validación tolerante

**Fase 5: Enhanced (2h - opcional)**
9. T7.9 - Cross-session query
10. T7.10 - Tests comprehensivos (validación estricta)

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
- unittest.mock con `AsyncMock` para mocking `AsyncOpenAI`
- **NO dependencias de red:** fixtures locales para todas las pruebas automatizadas

**Archivo Unificado:** `tests/test_rag_phase7.py` (contiene unit + integration tests)

### 5.2 Test Cases en `tests/test_rag_phase7.py`

**Sección 1: Unit Tests para `generate_answer()` (Async)**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_generate_answer_success` | Mock `AsyncOpenAI` retorna respuesta | - Prompt contiene question y context<br>- `await` ejecuta correctamente<br>- Response extraída<br>- Tokens logged |
| `test_generate_answer_auth_error` | API key inválida | - AuthenticationError se propaga<br>- No retry para auth errors |
| `test_generate_answer_retry` | API falla primero, éxito después | - Retry ejecuta (async)<br>- Finalmente retorna respuesta |

**Sección 2: Unit Tests para `RAGRetriever` (Async)**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_retriever_pipeline_mock` | Mock embedder + vectorstore + openai | - `await embedder.embed_single()` ejecuta<br>- Query ejecuta<br>- Context building correcto<br>- `await generate_answer()` ejecuta<br>- QueryResult válido según contrato (3.3 tolerante) |
| `test_retriever_no_results` | VectorStore retorna lista vacía | - QueryResult.answer = "No relevant information found..." |
| `test_similarity_conversion` | Distance → similarity score | - `similarity = 1.0 - distance`<br>- Range [0.0, 1.0] |
| `test_sources_consistency` | Sources alineados con chunks | - Sources en QueryResult == chunks retrieved<br>- Orden preservado<br>- top_k respetado |

**Sección 3: Integration Tests para Tools**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_query_papers_with_mocks` | Tool `query_papers` con pipeline mocked | - QueryResult completo<br>- Sources con metadata completa<br>- Validar contrato (sección 3.3 tolerante) |
| `test_list_sessions` | Tool retorna sessions | - Dict con key "sessions"<br>- Cada session tiene metadata keys |
| `test_query_session_not_found` | session_id inválido | - Raise ValueError("Session ... not found") |
| `test_query_session_not_indexed` | Session existe pero indexed=False | - Raise RuntimeError("Session ... not indexed...") |

**Sección 4: Enhanced Tests (Opcional)**

| Test Case | Descripción | Aserciones |
|-----------|-------------|------------|
| `test_cross_session_query` | session_id=None busca en todos | - Merge results correcto<br>- Top-k global respetado |
| `test_citation_validation_strict` | Validación **estricta** de citas | - Regex match `\(\w+.*\d{4}\)`<br>- Years en sources<br>- Test falla si formato incorrecto |

**Tiempo Estimado:**
- Sección 1: 30m
- Sección 2: 1h (incluye test nuevo de consistencia)
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
   - [ ] **NUEVO:** Sources orden == chunks retrieved orden

3. **Tool `query_papers` - Sin resultados**
   - [ ] Ejecutar con pregunta irrelevante: `{"question": "How to cook pasta?", ...}`
   - [ ] Retorna mensaje "No relevant information found in indexed papers."

4. **Validación de Citas (Tolerante)**
   - [ ] Respuesta incluye referencias académicas (ej: "(Vaswani et al., 2017)")
   - [ ] Si no incluye citas, verificar que respuesta sea coherente y sources estén presentes
   - [ ] Years en citas coinciden aproximadamente con sources

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
- ✅ Respuestas tienen calidad académica (coherentes, con citas cuando posible)

---

## 6. Plan de Contingencia

### 6.1 Escenarios de Bloqueo

**Bloqueo B1: OpenAI API Rate Limiting**
- **Señal:** Tests fallan con RateLimitError frecuente
- **Impacto:** No se puede validar generate_answer()
- **Mitigación:**
  1. Usar mocks con `AsyncMock` para todos los tests automatizados (OBLIGATORIO)
  2. Manual smoke tests con delays entre calls
  3. Upgrade a tier con mayor límite (si crítico para producción)

**Bloqueo B2: Calidad de Respuestas Pobre**
- **Señal:** LLM genera respuestas genéricas sin citas
- **Impacto:** No cumple criterio de "respuestas académicas"
- **Mitigación:**
  1. Iterar en prompt engineering (añadir ejemplos, instrucciones más específicas)
  2. Aumentar top_k para más contexto (default: 5 → 7)
  3. Truncar context si muy largo (>6000 chars) para evitar dilución
  4. Upgrade a modelo mejor (gpt-4o en vez de mini) - cambiar solo `openai_model_rag` en settings

**Bloqueo B3: ChromaDB Query Performance Lento**
- **Señal:** Queries toman >5s para top_k=5
- **Impacto:** UX pobre en Claude Code
- **Mitigación:**
  1. Reducir top_k default a 3
  2. Revisar tamaño de collections (max_chunks limit en Fase 6)
  3. Implementar timeout en query (future work)

**Bloqueo B4: Metadata Incompleta en Sources**
- **Señal:** Tests fallan por KeyError en metadata
- **Impacto:** QueryResult inválido
- **Mitigación:**
  1. Revisar chunking en Fase 6 (metadata debe incluir todos los campos)
  2. Añadir defaults en RAGRetriever si metadata falta
  3. Validar metadata antes de crear QuerySource

**Bloqueo B5: Async/Await Issues (NUEVO en Rev-2)**
- **Señal:** RuntimeError: "coroutine was never awaited" o deadlocks
- **Impacto:** Pipeline no ejecuta
- **Mitigación:**
  1. Verificar todos los async methods usan `await`
  2. Verificar `asyncio.to_thread()` para sync calls (embeddings)
  3. No mezclar `asyncio.run()` dentro de event loop ya running
  4. Usar `pytest-asyncio` para tests async

### 6.2 Punto de Decisión GO/NO-GO

**Después de T7.4 (RAG Pipeline implementado):**

**GO si:**
- ✅ Pipeline embed→query→generate funciona con mocks (async)
- ✅ Unit tests pasan
- ✅ No hay blockers técnicos
- ✅ Async execution correcta (no deadlocks)

**NO-GO si:**
- ❌ OpenAI API authentication falla (revisar API key en `.env`)
- ❌ ChromaDB query retorna errores (revisar Fase 6 indexing completado)
- ❌ Metadata en chunks incompleta (revisar chunking en Fase 6)
- ❌ Async issues no resueltos (revisar DT-7 y código de referencia)

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
2. ❌ Reducir integration tests: solo 1 test básico (skip edge cases, skip consistencia sources)
3. ✅ Mantener: `generate_answer()` async, `RAGRetriever`, 2 tools, unit tests

**Core Inamovible (nunca recortar):**
- T7.1 - `generate_answer()` implementation (async)
- T7.4 - `RAGRetriever` pipeline (async)
- T7.5 - Tool `query_papers` (con validación session)
- T7.6 - Tool `list_sessions`
- T7.7 - Unit tests básicos (async)

---

## 7. Criterios de Aceptación Final

**El workplan se considera completo cuando:**

1. ✅ **Funcionalidad Core:**
   - Tool `query_papers` funciona en MCP Inspector
   - Tool `list_sessions` funciona en MCP Inspector
   - Pipeline end-to-end ejecuta sin errores (async)

2. ✅ **Calidad de Código:**
   - Reutiliza patrones de fases previas (no inventa nuevos)
   - Type hints completos en funciones públicas
   - Docstrings claros
   - Error handling consistente con tools existentes
   - Lazy initialization de componentes (ver sección 3.4)
   - **Async methods** donde corresponde (OpenAIClient, RAGRetriever)

3. ✅ **Testing:**
   - Tests unificados en `tests/test_rag_phase7.py` pasan
   - Unit tests para `generate_answer()` pasan (async con `AsyncMock`)
   - Integration test con mocks pasa
   - Validación **tolerante** de contrato QueryResult (sección 3.3)
   - **Test de consistencia sources** implementado (sección 5.2)
   - Smoke test manual ejecutado (checklist completado)

4. ✅ **Calidad de Outputs:**
   - Respuestas son coherentes (no gibberish)
   - Citas académicas presentes cuando posible (validación tolerante)
   - Sources en QueryResult cumplen contrato (metadata completa, relevance_score en [0.0, 1.0])
   - **Sources consistentes** con chunks retrieved (orden, top_k)

5. ✅ **Documentación:**
   - Logs informativos en ejecución (tokens, chunks retrieved, timing)

---

## 8. Notas Adicionales

**Reutilización de Patrones Existentes:**
- `generate_answer()` sigue mismo patrón **async** que `generate_keywords()`: retry logic, logging, error handling
- Tools usan `@mcp.tool()` decorator como en `search.py`, `download.py`, `index.py`
- `asyncio.to_thread()` para embeddings sync (patrón de `index.py`)
- Return `model.model_dump()` para serialización (patrón universal en tools)
- **Lazy initialization** de componentes globales (patrón de `index.py`)
- **AsyncOpenAI** ya usado en `generate_keywords()` (líneas 34, 48 de `openai.py`)

**Filosofía KISS Aplicada:**
- No crear abstracciones innecesarias (ej: no PromptManager class, solo string templates)
- No optimización prematura (ej: no cache de embeddings hasta tener datos de uso)
- Reutilizar componentes existentes sin modificarlos (EmbeddingService, VectorStore)
- Prompt simple que funciona > sistema configurable complejo
- Tests unificados en un solo archivo > arquitectura compleja de testing
- Validación tolerante en MVP > validación estricta prematura

**Dependencias Externas:**
- OpenAI API key requerida (ya configurada en `.env` de fases previas)
- ChromaDB collections creadas en Fase 6 (indexing)
- Sentence-transformers model descargado en Fase 6

**Riesgos Conocidos:**
- Calidad de respuestas depende del modelo LLM (gpt-4o-mini puede ser limitado para papers técnicos)
- Citas pueden no ser 100% precisas (LLM puede alucinar autores - mitigado con validación tolerante)
- Performance de query depende de tamaño de collections (mitigado con max_chunks limit)
- Metadata en chunks debe ser completa (dependencia de Fase 6 - validar antes de empezar Fase 7)
- **Context truncado:** Si top_k muy alto + chunks largos, context puede exceder límites del modelo (mitigado con truncado a ~6000 chars)

**Límites de Contexto en Prompts (Rev-2):**
- GPT-4o-mini: ~128k tokens input, pero mejor mantener prompts <8k tokens para respuestas de calidad
- Context building: ~6000 caracteres (~1500 tokens) para chunks + prompt template
- Si top_k=5 y cada chunk ~1200 chars → total ~6000 chars (safe)
- Si top_k >7 o chunks muy largos → truncar context concatenado a 6000 chars
- Log warning si se trunca context

---

**Workplan persistido:** `.claude/workplans/task-08/workplan-task-08-rev-2.md`
