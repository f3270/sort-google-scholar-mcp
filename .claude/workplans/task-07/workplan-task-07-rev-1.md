# Workplan: Fase 6 - RAG Vector Store (Rev 1)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 6: RAG Vector Store - Indexación con ChromaDB |
| **Task ID** | task-07 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.1 (rev-1) |
| **Estado** | Aprobado - Refinado post-revisión con codex |
| **Autor** | Claude Sonnet 4.5 |
| **Fase MCP_PLAN** | Fase 6: Vector Store (línea ~1135+) |
| **Stack** | ChromaDB, sentence-transformers, asyncio, Pydantic, pytest |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Plan base para Fase 6 | Usuario |
| 1.1 (rev-1) | 2025-12-29 | Mejoras: esquema IDs/metadata explícito, sub-batching MVP, configuración ChromaDB, mocks por defecto en tests | Incorporar sugerencias de análisis automatizado con codex | Usuario |

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
5. **[NUEVO]** Esquema de IDs y metadata explícitamente definido
6. **[NUEVO]** Sub-batching de embeddings integrado en MVP

**Componentes MCP afectados:**
- `src/sortgs_mcp/rag/embeddings.py` (nuevo)
- `src/sortgs_mcp/rag/vectorstore.py` (nuevo)
- `src/sortgs_mcp/tools/index.py` (nuevo)
- `src/sortgs_mcp/rag/__init__.py` (actualizar exports)
- `src/sortgs_mcp/server.py` (importar tool)
- `tests/test_embeddings.py` (nuevo)
- `tests/test_vectorstore.py` (nuevo)
- `tests/test_index_tool.py` (nuevo)

**Referencia MCP_PLAN.md:** Fase 6 (líneas ~1135+, especificado in task-07-fase-6.md)

### Objetivos
- ✅ Cargar modelo de embeddings local (all-mpnet-base-v2)
- ✅ Generar embeddings en batch con sub-batching automático
- ✅ Indexar chunks en ChromaDB con metadata completa
- ✅ Una colección ChromaDB por sesión (aislamiento)
- ✅ Búsqueda semántica session-specific y cross-session
- ✅ MCP tool `index_papers` siguiendo patrones existentes
- ✅ Tests con mocks por defecto (ChromaDB in-memory opcional)

---

## 2. Priorización del Alcance

### MVP / CORE (Obligatorio)
**Criterio de éxito:** Pipeline funcional PDFs→chunks→embeddings→ChromaDB + tool MCP + session.indexed actualizado + **esquema de datos robusto**

**Componentes obligatorios:**
1. ✅ **EmbeddingService** - Singleton con sentence-transformers
   - `embed_texts()` - Batch embedding con **sub-batching automático (batch_size=1000)**
   - `embed_single()` - Convenience wrapper
   - Lazy loading con threading.Lock
2. ✅ **VectorStore** - ChromaDB wrapper con **configuración explícita**
   - `get_or_create_collection()` - Colección por session **con metadata config**
   - `add_documents()` - Bulk insert con embeddings **+ validación de dimensiones**
   - `query()` - Búsqueda semántica session-specific
   - `delete_session()` - Cleanup
   - **[NUEVO]** Esquema de IDs: `{session_id}_chunk_{paper_rank}_{chunk_index}`
   - **[NUEVO]** Validación de embedding dimensions en `add_documents()`
3. ✅ **Tool index_papers** - MCP tool
   - Load session → find PDFs → parse → chunk → **sub-batch embed** → index
   - Validación de parámetros (chunk_size, chunk_overlap)
   - **[NUEVO]** Límite de chunks por sesión (default: 10,000)
   - Update session.indexed = True
   - Return IndexingResult
4. ✅ **Testing con mocks por defecto** - Unit tests + integration tests
   - **[NUEVO]** FakeEmbedder en tests unitarios (no cargar modelo real)
   - Tests con modelo real solo en `tests/test_embeddings_integration.py` (opcional)
5. ✅ **Async integration** - asyncio.to_thread() para operaciones CPU-intensive

### Enhanced (Opcional - implementar si hay tiempo)
**Componentes opcionales:**
1. ⚠️ **Cross-session query** - Buscar en todas las sesiones
   - Query múltiples collections
   - Merge + re-ranking por distance
2. ⚠️ **VectorStore.list_collections()** - Listar sesiones indexadas
3. ⚠️ **Progress reporting** - Log cada 10% de PDFs procesados
4. ⚠️ **Verificación de persistencia** - Test de ciclo de vida completo (index → restart → query)

**Justificación:** MVP permite indexar y buscar en una sesión con robustez; cross-session es nice-to-have

### Nice-to-Have (Futuro)
**Componentes futuros:**
1. 🔵 **Embedding cache** - Cache de embeddings ya generados (filesystem/Redis)
2. 🔵 **GPU support** - sentence-transformers con CUDA
3. 🔵 **Hybrid search** - Combinar búsqueda semántica + keyword (BM25)
4. 🔵 **Reranking** - Cross-encoder para mejorar resultados
5. 🔵 **Migration tools** - Herramientas para limpiar/migrar vectorstore

**Justificación:** Complejidad vs beneficio; MVP es suficiente para RAG funcional

### Plan de Reducción de Alcance
**Si falta tiempo, recortar en orden:**
1. ❌ Cross-session query (Enhanced #1) - implementar después si se necesita
2. ❌ Progress reporting detallado (Enhanced #3) - mantener logging básico
3. ❌ Verificación de persistencia (Enhanced #4) - asumir ChromaDB funciona

**Core inamovible:**
- EmbeddingService.embed_texts() con **sub-batching automático**
- VectorStore.add_documents() con **validación de dimensiones**
- **Esquema de IDs explícito y documentado**
- Tool index_papers funcional con límite de chunks
- session.indexed actualizado
- Tests con mocks por defecto

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
│  │ 5. Sub-batch embed chunks (asyncio.to_thread)        │  │
│  │    └─> EmbeddingService.embed_texts(batch_size=1000)│  │
│  │ 6. Index en ChromaDB con validación                  │  │
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
│ (singleton) │  │  + Schema    │  │          │  │ (Fase 5)   │
└─────────────┘  └──────────────┘  └──────────┘  └────────────┘
     │                  │
     ▼                  ▼
┌────────────┐    ┌──────────────────┐
│ sentence-  │    │ data/vectorstore/│
│ transformers│    │ + metadata.json  │
│ (modelo)   │    │ (persistence)    │
└────────────┘    └──────────────────┘
```

### 3.2 Componentes Afectados

#### A. Nuevos Módulos

**1. src/sortgs_mcp/rag/embeddings.py**
- **EmbeddingService**: Clase para generar embeddings
  - `model: SentenceTransformer` - Modelo cargado
  - `model_name: str` - Nombre del modelo
  - `embedding_dim: int` - Dimensiones del modelo (768 para all-mpnet-base-v2)
  - `embed_texts(texts: list[str], batch_size: int = 1000) -> list[list[float]]` - **Sub-batching automático**
  - `embed_single(text: str) -> list[float]` - Single embedding wrapper
- **get_embedding_service(model_name: str) -> EmbeddingService** - Singleton factory thread-safe

**2. src/sortgs_mcp/rag/vectorstore.py**
- **VectorStore**: Wrapper sobre ChromaDB
  - `client: chromadb.PersistentClient` - Cliente ChromaDB
  - `persist_dir: Path` - Directorio de persistencia
  - `embedding_dim: int` - Dimensiones esperadas (default: 768)
  - `distance_metric: str` - Métrica de distancia (default: "cosine")
  - `get_or_create_collection(session_id: str) -> Collection` - **Con metadata config**
  - `add_documents(session_id, chunks, embeddings) -> int` - **Con validación de dims**
  - `query(query_embedding, session_id, k) -> list[dict]`
  - `delete_session(session_id: str) -> None`
  - `list_collections() -> list[str]` (Enhanced)
  - **[NUEVO]** `_generate_chunk_id(session_id, paper_rank, chunk_index) -> str` - Helper para IDs

**3. src/sortgs_mcp/tools/index.py**
- **index_papers(session_id, chunk_size, chunk_overlap, max_chunks) -> dict**
  - MCP tool para indexar PDFs de una sesión
  - **[NUEVO]** Parámetro `max_chunks: int = 10000` para limitar memoria
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
| **Batch processing** | Sub-batching automático (1000/batch) | Acumular todos | **[NUEVO]** Evita memory overflow, simple de implementar |
| **ChromaDB mode** | PersistentClient | EphemeralClient o Server | Persistencia sin servidor externo |
| **Error handling PDF** | Try/except por PDF individual | Fail-fast | Partial success > total failure |
| **Distance metric** | Cosine (explícito) | L2 o configurable | **[NUEVO]** Cosine mejor para embeddings normalizados |
| **Chunk ID schema** | `{session_id}_chunk_{rank}_{index}` | UUID o hash | **[NUEVO]** Traceable, evita colisiones, readable |
| **Dimension validation** | Validar en add_documents() | Asumir correcto | **[NUEVO]** Detecta errores de modelo early |

### 3.4 Esquema de Datos (NUEVO)

#### Chunk IDs
**Formato**: `{session_id}_chunk_{paper_rank:03d}_{chunk_index:03d}`

**Ejemplos**:
- `abc123_chunk_001_000` - Primera chunk del paper rank 1
- `abc123_chunk_042_015` - Chunk 15 del paper rank 42

**Propiedades**:
- Único por chunk en toda la colección
- Traceable a paper y chunk específico
- Evita colisiones al re-indexar (overwrite)
- Readable para debugging

#### Metadata Schema
**Campos obligatorios** (de TextChunker.REQUIRED_METADATA_FIELDS):
```python
{
    "session_id": str,           # UUID de la sesión
    "paper_title": str,          # Título del paper
    "paper_authors": str,        # Autores (joined)
    "paper_year": int,           # Año de publicación
    "paper_citations": int,      # Número de citas
    "paper_rank": int,           # Rank en resultados (1-indexed)
    "source_url": str,           # URL del paper en Scholar
    "chunk_index": int,          # Índice del chunk (0-indexed)
    "total_chunks": int,         # Total de chunks del paper
}
```

**Validación**: TextChunker ya valida estos campos; VectorStore los pasa directamente a ChromaDB

#### ChromaDB Collection Metadata
**Nombre**: `session_{session_id}`
**Metadata**:
```python
{
    "hnsw:space": "cosine",      # Distance metric
    "embedding_dim": 768,        # Expected dimensions
    "created_at": "2025-12-29",  # Timestamp
    "model": "all-mpnet-base-v2" # Embedding model usado
}
```

### 3.5 Flujo de Datos

**Input**: session_id (UUID de search_papers)
**Output**: IndexingResult con estadísticas

1. **Validación**:
   - chunk_size ∈ [100, 5000]
   - chunk_overlap ∈ [0, chunk_size)
   - max_chunks >= 100 (razonable para sesión)

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
               # NUEVO: Check límite
               if len(all_chunks) > max_chunks:
                   logger.warning(f"Reached max_chunks limit ({max_chunks})")
                   break
           else:
               failed_papers.append(paper.title)
       except Exception as e:
           logger.error(f"Failed to parse {pdf_path.name}: {e}")
           failed_papers.append(paper.title if paper else pdf_path.name)
   ```

6. **Sub-Batch Embed** (NUEVO):
   ```python
   texts = [chunk["text"] for chunk in all_chunks]
   embedder = get_embedding_service(settings.embedding_model)

   # Sub-batching automático dentro de embed_texts()
   embeddings = await asyncio.to_thread(
       embedder.embed_texts, texts, batch_size=1000
   )
   # embed_texts procesa en batches de 1000 internamente
   ```

7. **Index en ChromaDB con validación** (NUEVO):
   ```python
   vectorstore = VectorStore(
       settings.chroma_persist_dir,
       embedding_dim=embedder.embedding_dim,
       distance_metric="cosine"
   )

   # add_documents valida dimensiones
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
| T1 | Crear EmbeddingService con sub-batching | ALTA | - Clase con __init__, embed_texts (batch_size param), embed_single<br/>- Singleton factory thread-safe<br/>- **Sub-batching automático**<br/>- Logging de carga y batch progress | Ninguna | 1.5h |
| T2 | Tests EmbeddingService (con mocks) | ALTA | - 5+ tests (singleton, dims, batch, **sub-batch**, determinismo)<br/>- **FakeEmbedder para tests unitarios**<br/>- Todos pasan | T1 | 0.5h |
| T3 | Crear VectorStore con schema explícito | ALTA | - __init__ con PersistentClient + **embedding_dim, distance_metric**<br/>- get_or_create_collection **con metadata**<br/>- add_documents **con validación de dims**<br/>- **_generate_chunk_id() helper** | T1, T2 | 1.5h |
| T4 | VectorStore query session-specific | ALTA | - query() con session_id<br/>- Retorna chunks relevantes con scores | T3 | 0.5h |
| T5 | VectorStore delete_session | ALTA | - Elimina colección<br/>- Handle not found | T3 | 0.5h |
| T6 | Tests VectorStore (con mocks) | ALTA | - 8+ tests (add, query, delete, metadata, **dim validation**, **ID schema**, in-memory)<br/>- **Mock ChromaDB para unit tests**<br/>- Todos pasan | T3-T5 | 1.5h |
| T7 | Tool index_papers esqueleto | ALTA | - @mcp.tool decorator<br/>- Validación de inputs **+ max_chunks**<br/>- Logging setup | T1-T6 | 0.5h |
| T8 | Pipeline load → find → parse → chunk | ALTA | - Load session<br/>- Find PDFs<br/>- Map PDF→Paper<br/>- Parse & chunk loop **con límite** | T7 | 1h |
| T9 | Pipeline sub-batch embed → index → update | ALTA | - **Sub-batch embed**<br/>- Add to ChromaDB **con validación**<br/>- Update session.indexed<br/>- Return IndexingResult | T8 | 1.5h |
| T10 | Error handling & logging | ALTA | - Try/except por PDF<br/>- failed_papers tracking<br/>- Progress logs<br/>- **Dimension mismatch errors** | T9 | 0.5h |
| T11 | Tests index_papers (con mocks) | ALTA | - 7+ tests (happy path, no PDFs, partial failure, validation, re-index, **max_chunks**, **dim mismatch**)<br/>- Session fixture con PDFs<br/>- **FakeEmbedder y FakeVectorStore por defecto** | T7-T10 | 2h |
| T12 | RAG __init__ exports | MEDIA | - Exportar EmbeddingService, get_embedding_service, VectorStore<br/>- Docstring del módulo | T1, T3 | 0.25h |
| T13 | Server integration | MEDIA | - Importar tools.index en server.py<br/>- Verificar tool registrado | T7-T10 | 0.25h |
| T14 | VectorStore cross-session query | BAJA | - Query sin session_id<br/>- Merge + re-ranking | T4, T6 | 1h |
| T15 | Integration tests con modelo real | MEDIA | - `test_embeddings_integration.py`<br/>- Cargar modelo real, embed 100 textos<br/>- Verificar dims y determinismo | T1-T13 | 0.5h |
| T16 | Manual testing end-to-end | MEDIA | - Crear sesión → download → index → verificar ChromaDB<br/>- **Verificar persistencia** (restart server, query) | T1-T13 | 0.5h |

**Total estimado: 13h** (MVP = 11.5h, Enhanced = 1.5h)

### 4.2 Orden Sugerido de Implementación

**Fase 1: Embeddings (2.5h)**
1. T1: EmbeddingService con sub-batching
2. T2: Tests EmbeddingService (mocks)
3. Verificación manual: cargar modelo, embed 10 textos, sub-batch de 2500 textos

**Fase 2: VectorStore (3.5h)**
4. T3: VectorStore con schema explícito
5. T4: Query session-specific
6. T5: Delete session
7. T6: Tests VectorStore (mocks + in-memory)

**Fase 3: Tool index_papers (5h)**
8. T7: Esqueleto tool
9. T8: Pipeline parse & chunk
10. T9: Pipeline sub-batch embed & index
11. T10: Error handling
12. T11: Tests index_papers (mocks)

**Fase 4: Integration (1.5h)**
13. T12: RAG __init__
14. T13: Server integration
15. T15: Integration tests con modelo real
16. T16: Manual testing end-to-end

**Fase 5: Enhanced (opcional, 1.5h)**
17. T14: Cross-session query

---

## 5. Plan de Pruebas

### 5.1 Estrategia de Testing (REFINADA)

**Niveles de testing:**
- **Unit tests con mocks**: EmbeddingService (FakeEmbedder), VectorStore (mock ChromaDB), validación tool
- **Integration tests opcionales**: Con modelo real y ChromaDB real (solo si tiempo permite)
- **Manual testing**: End-to-end con MCP Inspector (si disponible)

**Cobertura objetivo:** >85% para nuevos módulos (unit tests con mocks)

**Principio clave**: **Tests determinísticos con mocks por defecto, tests con dependencias reales solo en integration (opcional)**

### 5.2 Casos de Prueba Principales

#### A. EmbeddingService (tests/test_embeddings.py) - CON MOCKS

| Test | Descripción | Assertion | Mock |
|------|-------------|-----------|------|
| `test_singleton_pattern` | get_embedding_service() 2 veces | `assert service1 is service2` | - |
| `test_embed_single_dimensions` | embed_single("text") | `assert len(embedding) == 768` | FakeEmbedder |
| `test_embed_batch` | embed_texts([100 textos]) | `assert len(embeddings) == 100` | FakeEmbedder |
| `test_sub_batching` | embed_texts([2500 textos], batch_size=1000) | `assert 3 batches procesados` | FakeEmbedder + spy |
| `test_deterministic` | mismo texto 2 veces | `assert embedding1 == embedding2` | FakeEmbedder |

**FakeEmbedder**:
```python
class FakeEmbedder:
    def __init__(self, dim: int = 768):
        self.dim = dim
        self.batches_processed = []

    def embed_texts(self, texts, batch_size=1000):
        # Simular sub-batching
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            self.batches_processed.append(len(batch))
        return [[0.1] * self.dim for _ in texts]
```

#### B. VectorStore (tests/test_vectorstore.py) - CON MOCKS/IN-MEMORY

| Test | Descripción | Assertion | Setup |
|------|-------------|-----------|-------|
| `test_init_chromadb` | Crear VectorStore con dims | `assert vectorstore.embedding_dim == 768` | In-memory |
| `test_collection_metadata` | get_or_create_collection | `assert metadata["hnsw:space"] == "cosine"` | In-memory |
| `test_add_documents_valid_dims` | Añadir 10 chunks (768 dims) | `assert collection.count() == 10` | In-memory |
| `test_add_documents_invalid_dims` | Añadir chunks (384 dims) | `with pytest.raises(ValueError)` | In-memory |
| `test_chunk_id_schema` | Verificar formato IDs | `assert id == "abc_chunk_001_000"` | Mock |
| `test_query_session_specific` | Query session A | `assert all(r["metadata"]["session_id"] == "A")` | In-memory |
| `test_query_cross_session` (Enhanced) | Query 2 sessions | `assert len(results) > 0` from both | In-memory |
| `test_delete_session` | Delete collection | `assert collection not in list` | In-memory |

#### C. Tool index_papers (tests/test_index_tool.py) - CON MOCKS

| Test | Descripción | Assertion | Mocks |
|------|-------------|-----------|-------|
| `test_index_papers_basic` | Session con 3 PDFs | `assert result["chunks_created"] > 0` | FakeEmbedder, FakeVectorStore |
| `test_index_papers_no_pdfs` | Session sin PDFs | `with pytest.raises(RuntimeError)` | - |
| `test_index_papers_partial_failure` | 1 corrupto + 2 OK | `assert result["papers_indexed"] == 2` | Mocks |
| `test_index_papers_max_chunks` | 15,000 chunks, max=10,000 | `assert result["chunks_created"] == 10000` | Mocks |
| `test_index_papers_updates_session` | Verificar indexed=True | `assert session.indexed == True` | Mocks |
| `test_index_papers_validation` | chunk_size inválido | `with pytest.raises(ValueError)` | - |
| `test_index_papers_reindex` | Indexar 2 veces | `assert segunda_vez sobrescribe` | Mocks |
| `test_dimension_mismatch_error` | Embedder con dims incorrectas | `with pytest.raises(ValueError)` | FakeEmbedder(dim=384) |

#### D. Integration Tests (tests/test_embeddings_integration.py) - OPCIONAL

| Test | Descripción | Assertion | Dependencias |
|------|-------------|-----------|--------------|
| `test_real_model_loading` | Cargar all-mpnet-base-v2 | `assert model loaded` | sentence-transformers |
| `test_real_embedding_dims` | Embed 10 textos | `assert embeddings[0].shape == (768,)` | Modelo real |
| `test_real_sub_batching` | Embed 2500 textos | `assert len(embeddings) == 2500` | Modelo real |

**Nota**: Integration tests solo se ejecutan con flag `pytest -m integration` (opcional en CI)

### 5.3 Fixtures y Mocks (ACTUALIZADO)

**Fixtures reutilizables:**
- `make_paper()` - Crea Paper con defaults (ya existe)
- `create_session()` - Crea SearchSession + persiste (ya existe)
- `tmp_vectorstore(tmp_path)` - VectorStore con ChromaDB in-memory + dims config

**Mocks necesarios (AMPLIADO)**:
```python
class FakeEmbedder:
    """Mock de EmbeddingService con sub-batching."""
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.embed_texts_calls = []
        self.batches_processed = []

    def embed_texts(self, texts: list[str], batch_size: int = 1000) -> list[list[float]]:
        self.embed_texts_calls.append(len(texts))
        # Simular sub-batching
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            self.batches_processed.append(len(batch))
        return [[0.1] * self.dimension for _ in texts]

    @property
    def embedding_dim(self) -> int:
        return self.dimension

class FakeVectorStore:
    """Mock de VectorStore con validación de dims."""
    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        self.add_documents_calls = []
        self.query_calls = []
        self.stored_chunks = {}

    def add_documents(self, session_id, chunks, embeddings) -> int:
        # Validar dimensiones
        if embeddings and len(embeddings[0]) != self.embedding_dim:
            raise ValueError(f"Expected {self.embedding_dim} dims, got {len(embeddings[0])}")

        self.add_documents_calls.append((session_id, len(chunks)))
        self.stored_chunks[session_id] = chunks
        return len(chunks)

    def query(self, embedding, session_id, k) -> list[dict]:
        if len(embedding) != self.embedding_dim:
            raise ValueError("Dimension mismatch")
        self.query_calls.append((session_id, k))
        return []
```

### 5.4 Checklist Mínima MCP + RAG (ACTUALIZADA)

**Antes de declarar completada la tarea:**

- [ ] **Embeddings**
  - [ ] Modelo se carga correctamente (all-mpnet-base-v2)
  - [ ] Singleton funciona (mismo objeto en múltiples llamadas)
  - [ ] Sub-batching procesa correctamente 2500 chunks en 3 batches
  - [ ] Batch embedding genera dims correctas (768)
  - [ ] **Tests con FakeEmbedder pasan (no requieren modelo real)**

- [ ] **VectorStore**
  - [ ] ChromaDB PersistentClient se inicializa con config
  - [ ] Collection se crea con metadata correcta (cosine, 768 dims)
  - [ ] **Chunk IDs siguen schema: {session}_chunk_{rank}_{index}**
  - [ ] **Validación de dimensiones detecta mismatch**
  - [ ] add_documents indexa chunks con metadata
  - [ ] query retorna resultados relevantes
  - [ ] delete_session elimina colección
  - [ ] **Tests con ChromaDB in-memory pasan**

- [ ] **Tool index_papers**
  - [ ] Tool se registra en MCP server
  - [ ] Validación de parámetros funciona (incluido max_chunks)
  - [ ] Pipeline completo: load → parse → chunk → **sub-batch** embed → index
  - [ ] **Límite de max_chunks funciona correctamente**
  - [ ] session.indexed se actualiza a True
  - [ ] Partial failures se manejan (failed_papers)
  - [ ] **Dimension mismatch genera error claro**
  - [ ] IndexingResult retorna estadísticas correctas
  - [ ] **Tests con mocks pasan (no requieren modelo real)**

- [ ] **Integration (opcional)**
  - [ ] Server.py importa tool index
  - [ ] RAG __init__ exporta clases
  - [ ] **Integration test con modelo real pasa** (opcional)
  - [ ] Manual test: sesión → download → index → **restart → query** → verify ChromaDB

- [ ] **Quality**
  - [ ] Type hints completos
  - [ ] Docstrings Google style
  - [ ] **Esquema de IDs documentado en docstrings**
  - [ ] Logs informativos (carga modelo, sub-batch progress, indexing progress)
  - [ ] Errores con mensajes accionables (incluido dimension mismatch)

---

## 6. Riesgos y Mitigaciones (ACTUALIZADO)

### 6.1 Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Modelo sentence-transformers falla al cargar** | Media | Alto | - Test manual early en implementación<br/>- Fallback a modelo más simple (all-MiniLM-L6-v2)<br/>- Documentar requisitos de RAM (~500MB)<br/>- **Integration tests opcionales** |
| **ChromaDB persistence issues** | Baja | Alto | - Tests con in-memory primero<br/>- Verificar permisos de data/vectorstore/<br/>- Logging detallado de init<br/>- **Metadata de collection para debugging** |
| **Memory overflow con muchos chunks** | ~~Media~~ **BAJA** | ~~Medio~~ **BAJO** | - **Sub-batching automático (MVP)**<br/>- **max_chunks límite configurable**<br/>- Monitorear uso de RAM en tests<br/>- Documentar límites recomendados |
| **Dimension mismatch (modelo cambiado)** | **NUEVA** Media | Alto | - **Validación explícita en add_documents()**<br/>- **Metadata de collection guarda modelo usado**<br/>- Error claro con mensaje accionable |
| **PDF → Paper mapping falla** | Media | Medio | - Regex robusto para extraer rank<br/>- Fallback a buscar por título similarity<br/>- Logs detallados de matching |
| **Embeddings muy lentos** | Baja | Medio | - Usar GPU si disponible (auto-detect)<br/>- **Sub-batch processing (ya implementado)**<br/>- Progress logging |
| **Thread-safety del singleton** | Baja | Medio | - threading.Lock en get_embedding_service()<br/>- Tests de concurrencia (2+ threads) |
| **Chunk ID colisiones** | **NUEVA** Baja | Medio | - **Esquema de IDs explícito y validado**<br/>- Tests de unicidad de IDs |
| **Tests flaky (modelo no determinístico)** | **NUEVA** ~~Media~~ **BAJA** | Medio | - **Mocks por defecto en unit tests**<br/>- Tests con modelo real solo en integration (opcional)<br/>- Usar seed si es posible |

### 6.2 Plan de Contingencia

**Punto de decisión GO/NO-GO:**
- **Después de T6** (tests VectorStore): Si ChromaDB presenta issues persistentes, considerar FAISS como alternativa
- **Después de T11** (tests index_papers): Si MVP no funciona, escalar a usuario

**Escenarios de bloqueo:**

1. **sentence-transformers no carga:**
   - Alternativa 1: all-MiniLM-L6-v2 (más ligero, 384 dims) - **actualizar embedding_dim**
   - Alternativa 2: OpenAI embeddings API (cambia alcance, requiere API key)

2. **ChromaDB issues:**
   - Alternativa 1: FAISS (más rápido pero menos features)
   - Alternativa 2: Qdrant embedded mode

3. **Memory issues (a pesar de sub-batching):**
   - Reducir max_chunks a 5000
   - Reducir batch_size a 500
   - Procesar sessions de a 5 PDFs max

4. **Dimension mismatch no detectado:**
   - **Validación explícita ya implementada en MVP**
   - Agregar test de regresión

---

## 7. Entregables

### 7.1 Código

**Nuevos archivos:**
- `src/sortgs_mcp/rag/embeddings.py` - EmbeddingService con sub-batching
- `src/sortgs_mcp/rag/vectorstore.py` - VectorStore con schema y validación
- `src/sortgs_mcp/tools/index.py` - Tool index_papers con límite de chunks
- `tests/test_embeddings.py` - 5+ tests (con mocks)
- `tests/test_vectorstore.py` - 8+ tests (in-memory + mocks)
- `tests/test_index_tool.py` - 7+ tests (con mocks)
- `tests/test_embeddings_integration.py` - 3 tests opcionales (modelo real)

**Archivos modificados:**
- `src/sortgs_mcp/rag/__init__.py` - Exports actualizados
- `src/sortgs_mcp/server.py` - Import tool index

### 7.2 Documentación

- Docstrings Google style en todas las clases y funciones públicas
- **Esquema de IDs documentado en VectorStore docstring**
- **Metadata schema documentado en add_documents() docstring**
- README actualizado con ejemplo de uso de index_papers (si hay README)
- Comentarios inline en lógica compleja (sub-batching, validación dims, cross-session query)

### 7.3 Tests

- Cobertura >85% para nuevos módulos
- **20+ tests totales** (5 embeddings + 8 vectorstore + 7 index_tool)
- Todos los tests pasan con `uv run pytest`
- Tests determinísticos (mocks por defecto)
- **Integration tests opcionales** marcados con `@pytest.mark.integration`
- Fixtures reutilizables documentados

---

## 8. Criterios de Aceptación Final (ACTUALIZADOS)

**Funcionalidad:**
- ✅ index_papers indexa correctamente 5 PDFs de una sesión
- ✅ Chunks se almacenan en ChromaDB con metadata completa
- ✅ **Chunk IDs siguen schema explícito**
- ✅ **Sub-batching procesa correctamente sesiones grandes (>1000 chunks)**
- ✅ **Validación de dimensiones detecta mismatch**
- ✅ session.indexed se actualiza a True
- ✅ Partial failures se manejan gracefully (failed_papers)
- ✅ Query retorna chunks relevantes con scores

**Performance:**
- ✅ Indexar 10 PDFs (~500 chunks, 250K chars) < 60 segundos
- ✅ **Memoria pico < 1GB con sub-batching** (modelo + embeddings parciales + ChromaDB)
- ✅ **Sub-batching de embeddings (procesar en lotes de 1000)**
- ✅ **max_chunks límite funciona** (10,000 chunks por sesión)

**Testing:**
- ✅ Cobertura > 85% nuevos módulos
- ✅ **20+ tests totales** (5 embeddings + 8 vectorstore + 7 index_tool)
- ✅ Todos los tests pasan
- ✅ **Tests determinísticos con mocks por defecto**
- ✅ **Integration tests opcionales** (modelo real) disponibles

**Calidad de Código:**
- ✅ Type hints completos (mypy compatible)
- ✅ Docstrings Google style
- ✅ **Esquema de datos documentado** (IDs, metadata, ChromaDB config)
- ✅ Logs informativos (carga modelo, sub-batch progress, indexing progress)
- ✅ Errores con mensajes accionables (incluido dimension mismatch)
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
    # 4. Procesamiento (con sub-batching si aplica)
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

**Sub-batching Pattern (NUEVO):**
```python
def embed_texts(self, texts: list[str], batch_size: int = 1000) -> list[list[float]]:
    """Embed texts with automatic sub-batching."""
    all_embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = self.model.encode(batch, show_progress_bar=False)
        all_embeddings.extend(batch_embeddings.tolist())

        logger.info(f"Processed batch {i//batch_size + 1}/{total_batches}")

    return all_embeddings
```

### 9.2 Configuración Existente (config.py)

Ya disponible en settings:
- `chroma_persist_dir: Path` → data/vectorstore/
- `embedding_model: str` → "all-mpnet-base-v2"
- `chunk_size: int` → 1000
- `chunk_overlap: int` → 200
- `pdf_download_dir(session_id)` → data/sessions/{session_id}/pdfs/

**NUEVO en config (si es necesario)**:
- `embedding_batch_size: int = 1000` - Tamaño de sub-batch para embeddings
- `max_chunks_per_session: int = 10000` - Límite de chunks por sesión

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
- **Codex review**: Análisis automatizado que generó esta revisión

### 10.2 Comandos Útiles

```bash
# Ejecutar tests unitarios (con mocks, rápidos)
uv run pytest tests/test_embeddings.py tests/test_vectorstore.py tests/test_index_tool.py -v

# Ejecutar integration tests (con modelo real, lentos)
uv run pytest tests/test_embeddings_integration.py -v -m integration

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

### 10.3 Filosofía KISS - Checklist (ACTUALIZADO)

- [x] **Reutilizar patrones existentes**: MCP tool pattern, asyncio.to_thread, SessionManager
- [x] **Sync + async wrapper**: No crear wrapper async innecesario para sentence-transformers
- [x] **Singleton simple**: Module-level factory con threading.Lock, no DI frameworks
- [x] **Metadata directa**: Pasar chunks["metadata"] sin transformación (ya validados por TextChunker)
- [x] **Batch processing simple**: **Sub-batching automático en embed_texts()**
- [x] **Collection per session**: Diseño simple con aislamiento claro
- [x] **Permitir re-indexing**: Evita complejidad de verificar estado previo
- [x] **ChromaDB PersistentClient**: Embedded, sin servidor externo
- [x] **Error handling por PDF**: Try/except individual, continuar con los demás
- [x] **Usar settings existentes**: No hardcodear paths, modelos, etc.
- [x] **[NUEVO] Esquema de datos explícito**: IDs y metadata claramente definidos
- [x] **[NUEVO] Validación de dimensiones**: Detectar errores early
- [x] **[NUEVO] Mocks por defecto**: Tests determinísticos, modelo real opcional
- [x] **[NUEVO] Límites configurables**: max_chunks, batch_size

---

### 10.4 Cambios Principales vs v1.0 (Resumen)

**Mejoras de ALTA prioridad aplicadas**:
1. ✅ **Esquema de IDs explícito**: `{session_id}_chunk_{rank}_{index}` documentado y validado
2. ✅ **Sub-batching automático**: embed_texts() con batch_size=1000 integrado en MVP
3. ✅ **max_chunks límite**: Parámetro configurable para evitar memory overflow

**Mejoras de MEDIA prioridad aplicadas**:
4. ✅ **Configuración ChromaDB explícita**: distance_metric="cosine", embedding_dim validado
5. ✅ **Validación de dimensiones**: add_documents() detecta mismatch y lanza ValueError
6. ✅ **Mocks por defecto en tests**: FakeEmbedder, FakeVectorStore, ChromaDB in-memory
7. ✅ **Tests con modelo real opcionales**: test_embeddings_integration.py con @pytest.mark.integration

**Mejoras de BAJA prioridad (consideradas)**:
8. ⚠️ **Ciclo de vida documentado**: Añadido en checklist y manual testing (T16)

**Riesgos mitigados**:
- Memory overflow: **REDUCIDO de Media→Baja** (sub-batching + max_chunks)
- Tests flaky: **REDUCIDO de Media→Baja** (mocks por defecto)
- Dimension mismatch: **NUEVO riesgo identificado y mitigado**

---

**Versión**: 1.1 (rev-1)
**Fecha**: 2025-12-29
**Estado**: ✅ Aprobado - Refinado con mejoras de codex
