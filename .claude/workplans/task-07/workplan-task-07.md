# Workplan: Fase 6 - RAG Vector Store

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 6: RAG Vector Store - Indexación con ChromaDB |
| **Task ID** | task-07 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.0 |
| **Estado** | Aprobado - Listo para implementación |
| **Autor** | Claude Sonnet 4.5 |
| **Fase MCP_PLAN** | Fase 6: Vector Store (línea ~1135+) |
| **Stack** | ChromaDB, sentence-transformers, asyncio, Pydantic, pytest |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Plan base para Fase 6 | Usuario |

---

## 1. Resumen Ejecutivo

### Descripción General
Implementar indexación de chunks de texto en ChromaDB con embeddings locales generados por sentence-transformers. Esta fase conecta el pipeline de PDF parsing/chunking (Fase 5) con el sistema de búsqueda semántica RAG.

### Alcance
**Objetivo:** Crear vectorstore persistente para búsqueda semántica de papers académicos mediante:
1. Servicio de embeddings con sentence-transformers (all-mpnet-base-v2)
2. Wrapper de ChromaDB para indexación y query
3. MCP tool `index_papers` para indexar PDFs de una sesión
4. Testing comprehensivo con mocks y fixtures

**Componentes MCP afectados:**
- `src/sortgs_mcp/rag/embeddings.py` (nuevo)
- `src/sortgs_mcp/rag/vectorstore.py` (nuevo)
- `src/sortgs_mcp/tools/index.py` (nuevo)
- `src/sortgs_mcp/rag/__init__.py` (actualizar exports)
- `src/sortgs_mcp/server.py` (importar tool)
- `tests/test_embeddings.py` (nuevo)
- `tests/test_vectorstore.py` (nuevo)
- `tests/test_index_tool.py` (nuevo)

**Referencia MCP_PLAN.md:** Fase 6 (líneas ~1135+, especificado en task-07-fase-6.md)

### Objetivos
- ✅ Cargar modelo de embeddings local (all-mpnet-base-v2)
- ✅ Generar embeddings en batch para eficiencia
- ✅ Indexar chunks en ChromaDB con metadata completa
- ✅ Una colección ChromaDB por sesión (aislamiento)
- ✅ Búsqueda semántica session-specific y cross-session
- ✅ MCP tool `index_papers` siguiendo patrones existentes
- ✅ Tests con ChromaDB in-memory (sin side effects)

---

## 2. Priorización del Alcance

### MVP / CORE (Obligatorio)
**Criterio de éxito:** Pipeline funcional PDFs→chunks→embeddings→ChromaDB + tool MCP + session.indexed actualizado

**Componentes obligatorios:**
1. ✅ **EmbeddingService** - Singleton con sentence-transformers
   - `embed_texts()` - Batch embedding (CORE)
   - `embed_single()` - Convenience wrapper
   - Lazy loading con threading.Lock
2. ✅ **VectorStore** - ChromaDB wrapper
   - `get_or_create_collection()` - Colección por session
   - `add_documents()` - Bulk insert con embeddings
   - `query()` - Búsqueda semántica session-specific
   - `delete_session()` - Cleanup
3. ✅ **Tool index_papers** - MCP tool
   - Load session → find PDFs → parse → chunk → embed → index
   - Validación de parámetros (chunk_size, chunk_overlap)
   - Update session.indexed = True
   - Return IndexingResult
4. ✅ **Testing básico** - Unit tests + integration tests
5. ✅ **Async integration** - asyncio.to_thread() para operaciones CPU-intensive

### Enhanced (Opcional - implementar si hay tiempo)
**Componentes opcionales:**
1. ⚠️ **Cross-session query** - Buscar en todas las sesiones
   - Query múltiples collections
   - Merge + re-ranking por distance
2. ⚠️ **VectorStore.list_collections()** - Listar sesiones indexadas
3. ⚠️ **Progress reporting** - Log cada 10% de PDFs procesados
4. ⚠️ **Sub-batching** - Procesar embeddings en batches de 1000 si total > 5000

**Justificación:** MVP permite indexar y buscar en una sesión; cross-session es nice-to-have

### Nice-to-Have (Futuro)
**Componentes futuros:**
1. 🔵 **Embedding cache** - Cache de embeddings ya generados (filesystem/Redis)
2. 🔵 **GPU support** - sentence-transformers con CUDA
3. 🔵 **Hybrid search** - Combinar búsqueda semántica + keyword (BM25)
4. 🔵 **Reranking** - Cross-encoder para mejorar resultados

**Justificación:** Complejidad vs beneficio; MVP es suficiente para RAG funcional

### Plan de Reducción de Alcance
**Si falta tiempo, recortar en orden:**
1. ❌ Cross-session query (Enhanced #1) - implementar después si se necesita
2. ❌ Progress reporting detallado (Enhanced #3) - mantener logging básico
3. ❌ Sub-batching (Enhanced #4) - asumir < 5000 chunks por sesión

**Core inamovible:**
- EmbeddingService.embed_texts() con batch processing
- VectorStore.add_documents() y query() session-specific
- Tool index_papers funcional
- session.indexed actualizado

---

## 3. Diseño Técnico

### 3.1 Arquitectura Propuesta

```
┌─────────────────┐
│  MCP Client     │
│  (Claude)       │
└────────┬────────┘
         │ index_papers(session_id, chunk_size, chunk_overlap)
         ▼
┌─────────────────────────────────────────────────────────────┐
│  index.py (MCP Tool)                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Validar inputs                                    │  │
│  │ 2. Load session (SessionManager)                     │  │
│  │ 3. Find PDFs en session_dir/pdfs/                    │  │
│  │ 4. Parse & Chunk cada PDF (asyncio.to_thread)        │  │
│  │    └─> parse_and_chunk_pdf(pdf, paper, session)     │  │
│  │ 5. Batch embed chunks (asyncio.to_thread)            │  │
│  │    └─> EmbeddingService.embed_texts(texts)          │  │
│  │ 6. Index en ChromaDB                                 │  │
│  │    └─> VectorStore.add_documents(chunks, embeddings)│  │
│  │ 7. Update session.indexed = True                     │  │
│  │ 8. Save session (SessionManager)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬─────────────────┐
         ▼              ▼              ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐
│ Embedding   │  │  VectorStore │  │ Session  │  │ PDF Parser │
│ Service     │  │  (ChromaDB)  │  │ Manager  │  │ + Chunker  │
│ (singleton) │  │              │  │          │  │ (Fase 5)   │
└─────────────┘  └──────────────┘  └──────────┘  └────────────┘
     │                  │
     ▼                  ▼
┌────────────┐    ┌──────────────────┐
│ sentence-  │    │ data/vectorstore/│
│ transformers│    │ (persistence)    │
│ (modelo)   │    └──────────────────┘
└────────────┘
```

### 3.2 Componentes Afectados

#### A. Nuevos Módulos

**1. src/sortgs_mcp/rag/embeddings.py**
- **EmbeddingService**: Clase para generar embeddings
  - `model: SentenceTransformer` - Modelo cargado
  - `model_name: str` - Nombre del modelo
  - `embed_texts(texts: list[str]) -> list[list[float]]` - Batch embedding
  - `embed_single(text: str) -> list[float]` - Single embedding wrapper
- **get_embedding_service(model_name: str) -> EmbeddingService** - Singleton factory thread-safe

**2. src/sortgs_mcp/rag/vectorstore.py**
- **VectorStore**: Wrapper sobre ChromaDB
  - `client: chromadb.PersistentClient` - Cliente ChromaDB
  - `persist_dir: Path` - Directorio de persistencia
  - `get_or_create_collection(session_id: str) -> Collection`
  - `add_documents(session_id, chunks, embeddings) -> int`
  - `query(query_embedding, session_id, k) -> list[dict]`
  - `delete_session(session_id: str) -> None`
  - `list_collections() -> list[str]` (Enhanced)

**3. src/sortgs_mcp/tools/index.py**
- **index_papers(session_id, chunk_size, chunk_overlap) -> dict**
  - MCP tool para indexar PDFs de una sesión
  - Sigue patrón de download.py (async, validación, SessionManager)

#### B. Módulos a Modificar

**4. src/sortgs_mcp/rag/__init__.py**
- Añadir exports: `EmbeddingService`, `get_embedding_service`, `VectorStore`

**5. src/sortgs_mcp/server.py**
- Importar `from sortgs_mcp.tools import index  # noqa: F401`

### 3.3 Decisiones Técnicas (KISS)

| Decisión | Opción Elegida | Alternativa | Justificación |
|----------|----------------|-------------|---------------|
| **Embeddings sync vs async** | Sync + asyncio.to_thread() | Wrapper async puro | sentence-transformers no es async-native; patrón PDFParser funciona |
| **Singleton pattern** | Module-level + threading.Lock | Framework DI | Simple, evita re-cargar 500MB modelo cada vez |
| **Collection strategy** | Una por sesión | Global con metadata filtering | Aislamiento, delete fácil, queries simples |
| **Re-indexing** | Permitir siempre (overwrite) | Skip si indexed=True | Flexibilidad para ajustar parámetros |
| **Batch processing** | Acumular todos + embed_texts() | Streaming incremental | Más simple, ~10x más rápido |
| **ChromaDB mode** | PersistentClient | EphemeralClient o Server | Persistencia sin servidor externo |
| **Error handling PDF** | Try/except por PDF individual | Fail-fast | Partial success > total failure |
| **Distance metric** | Default ChromaDB (L2) | Configurable | Suficiente para MVP, L2 estándar |

### 3.4 Flujo de Datos

**Input**: session_id (UUID de search_papers)
**Output**: IndexingResult con estadísticas

1. **Validación**:
   - chunk_size ∈ [100, 5000]
   - chunk_overlap ∈ [0, chunk_size)

2. **Load Session**:
   - SessionManager.load_session(session_id) → SearchSession

3. **Find PDFs**:
   - `pdf_dir = settings.pdf_download_dir(session_id)`
   - `pdf_files = sorted(pdf_dir.glob("*.pdf"))`
   - Si vacío → `RuntimeError("No PDFs found. Run download_papers first.")`

4. **Map PDF → Paper**:
   - Filename: `paper_{rank:03d}_{title}.pdf`
   - Regex: `r"paper_(\d{3})_"` → extraer rank
   - Buscar en `session.papers` por rank (papers[rank-1])

5. **Parse & Chunk** (loop async):
   ```python
   all_chunks = []
   failed_papers = []
   for pdf_path in pdf_files:
       try:
           paper = find_paper_by_rank(session.papers, pdf_path)
           chunks = await asyncio.to_thread(
               parse_and_chunk_pdf, pdf_path, paper, session_id,
               chunk_size=chunk_size, chunk_overlap=chunk_overlap
           )
           if chunks:
               all_chunks.extend(chunks)
           else:
               failed_papers.append(paper.title)
       except Exception as e:
           logger.error(f"Failed to parse {pdf_path.name}: {e}")
           failed_papers.append(paper.title if paper else pdf_path.name)
   ```

6. **Batch Embed**:
   ```python
   texts = [chunk["text"] for chunk in all_chunks]
   embedder = get_embedding_service(settings.embedding_model)
   embeddings = await asyncio.to_thread(embedder.embed_texts, texts)
   ```

7. **Index en ChromaDB**:
   ```python
   vectorstore = VectorStore(settings.chroma_persist_dir)
   count = vectorstore.add_documents(session_id, all_chunks, embeddings)
   ```

8. **Update Session**:
   ```python
   session.indexed = True
   session_manager.save_session(session, create_empty_csv=False)
   ```

9. **Return**:
   ```python
   return IndexingResult(
       session_id=session_id,
       papers_indexed=len(pdf_files) - len(failed_papers),
       chunks_created=len(all_chunks),
       indexing_time_sec=elapsed,
       failed_papers=failed_papers
   ).model_dump()
   ```

---

## 4. Plan de Desarrollo

### 4.1 Tareas Específicas

| ID | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-------|-----------|-------------------------|--------------|----------|
| T1 | Crear EmbeddingService | ALTA | - Clase con __init__, embed_texts, embed_single<br/>- Singleton factory thread-safe<br/>- Logging de carga | Ninguna | 1h |
| T2 | Tests EmbeddingService | ALTA | - 4+ tests (singleton, dims, batch, determinismo)<br/>- Todos pasan | T1 | 0.5h |
| T3 | Crear VectorStore básico | ALTA | - __init__ con PersistentClient<br/>- get_or_create_collection<br/>- add_documents | T1, T2 | 1h |
| T4 | VectorStore query session-specific | ALTA | - query() con session_id<br/>- Retorna chunks relevantes | T3 | 0.5h |
| T5 | VectorStore delete_session | ALTA | - Elimina colección<br/>- Handle not found | T3 | 0.5h |
| T6 | Tests VectorStore | ALTA | - 6+ tests (add, query, delete, metadata, in-memory)<br/>- Todos pasan | T3-T5 | 1h |
| T7 | Tool index_papers esqueleto | ALTA | - @mcp.tool decorator<br/>- Validación de inputs<br/>- Logging setup | T1-T6 | 0.5h |
| T8 | Pipeline load → find → parse → chunk | ALTA | - Load session<br/>- Find PDFs<br/>- Map PDF→Paper<br/>- Parse & chunk loop | T7 | 1h |
| T9 | Pipeline embed → index → update | ALTA | - Batch embed<br/>- Add to ChromaDB<br/>- Update session.indexed<br/>- Return IndexingResult | T8 | 1h |
| T10 | Error handling & logging | ALTA | - Try/except por PDF<br/>- failed_papers tracking<br/>- Progress logs | T9 | 0.5h |
| T11 | Tests index_papers | ALTA | - 6+ tests (happy path, no PDFs, partial failure, validation, re-index)<br/>- Session fixture con PDFs<br/>- Mocks de Embedder y VectorStore | T7-T10 | 1.5h |
| T12 | RAG __init__ exports | MEDIA | - Exportar EmbeddingService, get_embedding_service, VectorStore<br/>- Docstring del módulo | T1, T3 | 0.25h |
| T13 | Server integration | MEDIA | - Importar tools.index en server.py<br/>- Verificar tool registrado | T7-T10 | 0.25h |
| T14 | VectorStore cross-session query | BAJA | - Query sin session_id<br/>- Merge + re-ranking | T4, T6 | 1h |
| T15 | Manual testing end-to-end | MEDIA | - Crear sesión → download → index → verificar ChromaDB | T1-T13 | 0.5h |

**Total estimado: 11h** (MVP = 9.5h, Enhanced = 1.5h)

### 4.2 Orden Sugerido de Implementación

**Fase 1: Embeddings (2h)**
1. T1: EmbeddingService
2. T2: Tests EmbeddingService
3. Verificación manual: cargar modelo, embed 10 textos, verificar dims

**Fase 2: VectorStore (3h)**
4. T3: VectorStore básico
5. T4: Query session-specific
6. T5: Delete session
7. T6: Tests VectorStore (in-memory)

**Fase 3: Tool index_papers (4.5h)**
8. T7: Esqueleto tool
9. T8: Pipeline parse & chunk
10. T9: Pipeline embed & index
11. T10: Error handling
12. T11: Tests index_papers

**Fase 4: Integration (1h)**
13. T12: RAG __init__
14. T13: Server integration
15. T15: Manual testing end-to-end

**Fase 5: Enhanced (opcional, 1.5h)**
16. T14: Cross-session query

---

## 5. Plan de Pruebas

### 5.1 Estrategia de Testing

**Niveles de testing:**
- **Unit tests**: EmbeddingService, VectorStore (in-memory), validación tool
- **Integration tests**: Tool index_papers con session fixture
- **Manual testing**: End-to-end con MCP Inspector (si disponible)

**Cobertura objetivo:** >80% para nuevos módulos

### 5.2 Casos de Prueba Principales

#### A. EmbeddingService (tests/test_embeddings.py)

| Test | Descripción | Assertion |
|------|-------------|-----------|
| `test_singleton_pattern` | get_embedding_service() 2 veces | `assert service1 is service2` |
| `test_embed_single_dimensions` | embed_single("text") | `assert len(embedding) == 768` |
| `test_embed_batch` | embed_texts([100 textos]) | `assert embeddings.shape == (100, 768)` |
| `test_deterministic` | mismo texto 2 veces | `assert embedding1 == embedding2` |

#### B. VectorStore (tests/test_vectorstore.py)

| Test | Descripción | Assertion |
|------|-------------|-----------|
| `test_init_chromadb` | Crear VectorStore | `assert vectorstore.client is not None` |
| `test_add_documents` | Añadir 10 chunks | `assert collection.count() == 10` |
| `test_query_session_specific` | Query session A | `assert all(r["session_id"] == "A")` |
| `test_query_cross_session` (Enhanced) | Query 2 sessions | `assert len(results) > 0` from both |
| `test_delete_session` | Delete collection | `assert collection not in list_collections()` |
| `test_metadata_preservation` | Query → verificar metadata | `assert "paper_title" in result["metadata"]` |

#### C. Tool index_papers (tests/test_index_tool.py)

| Test | Descripción | Assertion |
|------|-------------|-----------|
| `test_index_papers_basic` | Session con 3 PDFs | `assert result["chunks_created"] > 0` |
| `test_index_papers_no_pdfs` | Session sin PDFs | `with pytest.raises(RuntimeError)` |
| `test_index_papers_partial_failure` | 1 corrupto + 2 OK | `assert result["papers_indexed"] == 2` |
| `test_index_papers_updates_session` | Verificar indexed=True | `assert session.indexed == True` |
| `test_index_papers_validation` | chunk_size inválido | `with pytest.raises(ValueError)` |
| `test_index_papers_reindex` | Indexar 2 veces | `assert segunda_vez sobrescribe` |

### 5.3 Fixtures y Mocks

**Fixtures reutilizables:**
- `make_paper()` - Crea Paper con defaults (ya existe en test_download_tool.py)
- `create_session()` - Crea SearchSession + persiste (ya existe)
- `tmp_vectorstore(tmp_path)` - VectorStore con ChromaDB in-memory

**Mocks necesarios:**
```python
class FakeEmbedder:
    """Mock de EmbeddingService."""
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.embed_texts_calls = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.embed_texts_calls.append(len(texts))
        return [[0.1] * self.dimension for _ in texts]

class FakeVectorStore:
    """Mock de VectorStore."""
    def __init__(self):
        self.add_documents_calls = []
        self.query_calls = []

    def add_documents(self, session_id, chunks, embeddings) -> int:
        self.add_documents_calls.append((session_id, len(chunks)))
        return len(chunks)

    def query(self, embedding, session_id, k) -> list[dict]:
        self.query_calls.append((session_id, k))
        return []
```

### 5.4 Checklist Mínima MCP + RAG

**Antes de declarar completada la tarea:**

- [ ] **Embeddings**
  - [ ] Modelo se carga correctamente (all-mpnet-base-v2)
  - [ ] Singleton funciona (mismo objeto en múltiples llamadas)
  - [ ] Batch embedding genera dims correctas (768)
  - [ ] Tests pasan

- [ ] **VectorStore**
  - [ ] ChromaDB PersistentClient se inicializa
  - [ ] Collection se crea con nombre correcto (`session_{uuid}`)
  - [ ] add_documents indexa chunks con metadata
  - [ ] query retorna resultados relevantes
  - [ ] delete_session elimina colección
  - [ ] Tests con in-memory pasan

- [ ] **Tool index_papers**
  - [ ] Tool se registra en MCP server
  - [ ] Validación de parámetros funciona
  - [ ] Pipeline completo: load → parse → chunk → embed → index
  - [ ] session.indexed se actualiza a True
  - [ ] Partial failures se manejan (failed_papers)
  - [ ] IndexingResult retorna estadísticas correctas
  - [ ] Tests con fixtures pasan

- [ ] **Integration**
  - [ ] Server.py importa tool index
  - [ ] RAG __init__ exporta clases
  - [ ] Manual test: sesión → download → index → verify ChromaDB

- [ ] **Quality**
  - [ ] Type hints completos
  - [ ] Docstrings Google style
  - [ ] Logs informativos (carga modelo, indexing progress)
  - [ ] Errores con mensajes accionables

---

## 6. Riesgos y Mitigaciones

### 6.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Modelo sentence-transformers falla al cargar** | Media | Alto | - Test manual early en implementación<br/>- Fallback a modelo más simple (all-MiniLM-L6-v2)<br/>- Documentar requisitos de RAM (~500MB) |
| **ChromaDB persistence issues** | Baja | Alto | - Tests con in-memory primero<br/>- Verificar permisos de data/vectorstore/<br/>- Logging detallado de init |
| **Memory overflow con muchos chunks** | Media | Medio | - Procesar en sub-batches de 1000 si total > 5000<br/>- Monitorear uso de RAM en tests<br/>- Documentar límites recomendados |
| **PDF → Paper mapping falla** | Media | Medio | - Regex robusto para extraer rank<br/>- Fallback a buscar por título similarity<br/>- Logs detallados de matching |
| **Embeddings muy lentos** | Baja | Medio | - Usar GPU si disponible (auto-detect)<br/>- Batch processing (ya implementado)<br/>- Progress logging |
| **Thread-safety del singleton** | Baja | Medio | - threading.Lock en get_embedding_service()<br/>- Tests de concurrencia (2+ threads) |
| **Metadata incompatible con ChromaDB** | Baja | Alto | - TextChunker ya valida metadata<br/>- Tests explícitos de ChromaDB add() |

### 6.2 Plan de Contingencia

**Punto de decisión GO/NO-GO:**
- **Después de T6** (tests VectorStore): Si ChromaDB presenta issues persistentes, considerar FAISS como alternativa
- **Después de T11** (tests index_papers): Si MVP no funciona, escalar a usuario

**Escenarios de bloqueo:**

1. **sentence-transformers no carga:**
   - Alternativa 1: all-MiniLM-L6-v2 (más ligero, 384 dims)
   - Alternativa 2: OpenAI embeddings API (cambia alcance, requiere API key)

2. **ChromaDB issues:**
   - Alternativa 1: FAISS (más rápido pero menos features)
   - Alternativa 2: Qdrant embedded mode

3. **Memory issues:**
   - Reducir chunk_size a 500 (menos chunks)
   - Procesar sessions de a 5 PDFs max

---

## 7. Entregables

### 7.1 Código

**Nuevos archivos:**
- `src/sortgs_mcp/rag/embeddings.py` - EmbeddingService completo
- `src/sortgs_mcp/rag/vectorstore.py` - VectorStore completo
- `src/sortgs_mcp/tools/index.py` - Tool index_papers completo
- `tests/test_embeddings.py` - 4+ tests
- `tests/test_vectorstore.py` - 6+ tests
- `tests/test_index_tool.py` - 6+ tests

**Archivos modificados:**
- `src/sortgs_mcp/rag/__init__.py` - Exports actualizados
- `src/sortgs_mcp/server.py` - Import tool index

### 7.2 Documentación

- Docstrings Google style en todas las clases y funciones públicas
- README actualizado con ejemplo de uso de index_papers (si hay README)
- Comentarios inline en lógica compleja (regex, cross-session query)

### 7.3 Tests

- Cobertura >80% para nuevos módulos
- Todos los tests pasan con `uv run pytest`
- Tests determinísticos (no fallan aleatoriamente)
- Fixtures reutilizables documentados

---

## 8. Criterios de Aceptación Final

**Funcionalidad:**
- ✅ index_papers indexa correctamente 5 PDFs de una sesión
- ✅ Chunks se almacenan en ChromaDB con metadata completa
- ✅ session.indexed se actualiza a True
- ✅ Partial failures se manejan gracefully (failed_papers)
- ✅ Query retorna chunks relevantes con scores

**Performance:**
- ✅ Indexar 10 PDFs (~500 chunks, 250K chars) < 60 segundos
- ✅ Memoria pico < 1.5GB (modelo + embeddings + ChromaDB)
- ✅ Batch processing de embeddings (no 1 por 1)

**Testing:**
- ✅ Cobertura > 80% nuevos módulos
- ✅ 16+ tests totales (4 embeddings + 6 vectorstore + 6 index_tool)
- ✅ Todos los tests pasan
- ✅ Tests determinísticos

**Calidad de Código:**
- ✅ Type hints completos (mypy compatible)
- ✅ Docstrings Google style
- ✅ Logs informativos (carga modelo, indexing progress)
- ✅ Errores con mensajes accionables
- ✅ No hardcoded paths (usar settings)

---

## 9. Notas de Implementación

### 9.1 Patrones a Seguir

**MCP Tool Pattern (de download.py):**
```python
@mcp.tool()
async def tool_name(param: Type) -> dict:
    # 1. Validación
    # 2. Logging inicio
    # 3. Load/create session
    # 4. Procesamiento
    # 5. Update session
    # 6. Save session
    # 7. Return model_dump()
```

**Async Integration (de PDFParser):**
```python
# En tool async:
result = await asyncio.to_thread(sync_function, args)

# Sync function tiene threading.Lock si es singleton:
_lock = threading.Lock()
def get_singleton():
    with _lock:
        if _instance is None:
            _instance = ...
        return _instance
```

### 9.2 Configuración Existente (config.py)

Ya disponible en settings:
- `chroma_persist_dir: Path` → data/vectorstore/
- `embedding_model: str` → "all-mpnet-base-v2"
- `chunk_size: int` → 1000
- `chunk_overlap: int` → 200
- `pdf_download_dir(session_id)` → data/sessions/{session_id}/pdfs/

### 9.3 Modelos Existentes (models.py)

Ya disponibles:
- `SearchSession.indexed: bool` → campo para actualizar
- `IndexingResult` → modelo de retorno del tool
- `Paper` → metadata de papers

### 9.4 Helpers Existentes

Ya disponibles:
- `parse_and_chunk_pdf(pdf_path, paper, session_id, chunk_size, chunk_overlap)` → Fase 5
- `TextChunker.REQUIRED_METADATA_FIELDS` → campos obligatorios
- `SessionManager.load_session(session_id)` → cargar sesión
- `SessionManager.save_session(session)` → persistir cambios

---

## 10. Apéndice

### 10.1 Referencias

- **Task description**: `.claude/tasks/task-07-fase-6.md`
- **MCP Plan**: `MCP_PLAN.md` Fase 6 (línea ~1135+)
- **Patrones MCP tools**: `src/sortgs_mcp/tools/search.py`, `src/sortgs_mcp/tools/download.py`
- **Patrones testing**: `tests/test_download_tool.py`, `tests/test_tool_validation.py`
- **ChromaDB docs**: https://docs.trychroma.com/
- **sentence-transformers docs**: https://www.sbert.net/

### 10.2 Comandos Útiles

```bash
# Ejecutar tests
uv run pytest tests/test_embeddings.py -v
uv run pytest tests/test_vectorstore.py -v
uv run pytest tests/test_index_tool.py -v

# Ejecutar todos los tests de RAG
uv run pytest tests/test_*embeddings* tests/test_*vectorstore* tests/test_*index* -v

# Verificar cobertura
uv run pytest --cov=sortgs_mcp.rag --cov=sortgs_mcp.tools.index --cov-report=term

# Verificar types (si mypy instalado)
mypy src/sortgs_mcp/rag/
mypy src/sortgs_mcp/tools/index.py

# Ejecutar MCP server (para testing manual)
uv run sortgs-mcp
```

### 10.3 Filosofía KISS - Checklist

- [x] **Reutilizar patrones existentes**: MCP tool pattern, asyncio.to_thread, SessionManager
- [x] **Sync + async wrapper**: No crear wrapper async innecesario para sentence-transformers
- [x] **Singleton simple**: Module-level factory con threading.Lock, no DI frameworks
- [x] **Metadata directa**: Pasar chunks["metadata"] sin transformación (ya validados por TextChunker)
- [x] **Batch processing simple**: Acumular chunks + embed_texts() en una llamada
- [x] **Collection per session**: Diseño simple con aislamiento claro
- [x] **Permitir re-indexing**: Evita complejidad de verificar estado previo
- [x] **ChromaDB PersistentClient**: Embedded, sin servidor externo
- [x] **Error handling por PDF**: Try/except individual, continuar con los demás
- [x] **Usar settings existentes**: No hardcodear paths, modelos, etc.

---

**Versión**: 1.0
**Fecha**: 2025-12-29
**Estado**: ✅ Aprobado - Listo para implementación
