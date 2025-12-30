# Workplan Task-09: Fase 8 - Suite de Tests Comprehensiva (Revisión 1)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Workplan Task-09: Fase 8 - Suite de Tests Comprehensiva |
| **Fecha de creación** | 2025-12-30 |
| **Versión** | 1.1 (rev-1) |
| **Estado** | APROBADO |
| **Autor** | Claude Sonnet 4.5 (MCP Planning Agent) |
| **Stack tecnológico** | Python 3.10+, pytest, pytest-asyncio, pytest-cov, unittest.mock |

### Historial de Revisiones

| Versión | Fecha | Cambios | Solicitante |
|---------|-------|---------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Sistema create-workplan |
| 1.1 (rev-1) | 2025-12-30 | Mejoras post-revisión con codex: (1) Aislamiento explícito ChromaDB/sesiones en test_end_to_end, (2) Checklists manuales convertidos a criterios verificables, (3) Scope de mocks clarificado, (4) Coverage por archivo con líneas críticas | Revisión automatizada codex |

---

## 1. Resumen Ejecutivo

### Descripción General
Desarrollar suite de tests comprehensiva para asegurar la calidad del código del proyecto sortgs-mcp. El proyecto ya cuenta con ~50 tests distribuidos en 15 archivos, cubriendo PDF processing, embeddings, vectorstore y algunos tools. Esta fase completará los tests faltantes para componentes core (models, parser, scholar, session, openai_client) y añadirá tests end-to-end, performance benchmarks y checklists de testing manual.

**Mejora rev-1**: Se ha fortalecido la estrategia de aislamiento para tests end-to-end (ChromaDB in-memory + tmp_path), clarificado el scope de mocks, y convertido checklists manuales en criterios trazables con outputs esperados documentados.

### Alcance
- **Completar gaps de unit tests** para 5 componentes sin tests
- **Test end-to-end** del workflow completo con **aislamiento explícito** (keywords → search → download → index → query)
- **Coverage report** con meta de 80% total + **targets por archivo para líneas críticas**
- **Manual testing checklist** con **criterios verificables y outputs esperados**
- **Performance benchmarks** básicos (Enhanced)
- **Error scenarios** comprehensivos (Enhanced)

### Objetivos
1. **Calidad**: Alcanzar 80% code coverage global + 90% en módulos críticos
2. **Confianza**: Validar todos los componentes críticos funcionan correctamente
3. **Regresión**: Prevenir bugs en futuras modificaciones
4. **Reproducibilidad**: Tests determinísticos sin dependencia de estado externo
5. **Trazabilidad**: Resultados manuales documentados con outputs esperados
6. **Performance**: Establecer baseline de performance

### Componentes MCP Afectados
- Todos los módulos de `src/sortgs_mcp/`:
  - `models.py` (sin tests)
  - `core/parser.py` (sin tests)
  - `core/scholar.py` (sin tests)
  - `core/session.py` (sin tests)
  - `llm/openai.py` (sin tests)
  - Workflow completo (MCP tools integration)

### Referencia a MCP_PLAN.md
Esta tarea corresponde a **Fase 8: Testing** del MCP_PLAN.md, líneas 1665-1811.

**Estado del proyecto antes de Fase 8:**
- ✅ Fases 0-7 completadas
- ✅ ~50 tests existentes en 15 archivos
- ✅ Coverage estimado: 50-60%
- ❌ Componentes core sin tests
- ❌ Test end-to-end faltante
- ❌ Manual testing no documentado con outputs esperados

---

## 2. Priorización del Alcance

### MVP/CORE (Obligatorio)

**Criterio de éxito:**
- ✅ Todos los tests unitarios pasando (100% pass rate)
- ✅ 80% code coverage mínimo total + **90% en archivos críticos** (models, parser, session)
- ✅ Test end-to-end exitoso con workflow completo y **aislamiento verificado**
- ✅ Manual testing checklist ejecutado en MCP Inspector con **outputs documentados**

**Componentes obligatorios:**
1. **Test Infrastructure** (2h)
   - Instalar pytest-cov
   - Configurar coverage reporting con targets por archivo
   - Setup baseline coverage report

2. **Unit Tests - Componentes Faltantes** (8-10h)
   - `tests/test_models.py`: Validación Pydantic completa
   - `tests/test_parser.py`: Parsing de HTML Google Scholar
   - `tests/test_scholar.py`: ScholarSearcher con mocks
   - `tests/test_session.py`: SessionManager persistence
   - `tests/test_openai_client.py`: OpenAI API mocked

3. **Integration Test End-to-End** (4h)
   - `tests/test_end_to_end.py`: Workflow completo con fixtures
   - **NUEVO**: Estrategia explícita de aislamiento (ChromaDB in-memory, tmp_path, limpieza)

4. **Manual Testing Checklist** (2h)
   - Checklist para MCP Inspector (6 tools) con **outputs esperados documentados**
   - Checklist para Claude Code integration con **validaciones específicas**
   - Documentar resultados en formato trazable

**Total MVP: 16-18 horas**

---

### Enhanced (Opcional)

**Criterio de éxito:**
- ✅ Performance benchmarks documentados
- ✅ Error scenarios cubiertos
- ✅ Smoke test checklist para PRs

**Componentes:**
1. **Performance Benchmarks** (3-4h)
   - Benchmark embeddings (100 chunks)
   - Benchmark vector search (1000 chunks)
   - Benchmark pipeline completo (10 papers)
   - Memory profiling básico

2. **Error Scenarios Testing** (3h)
   - Robot check de Google Scholar
   - PDF 404/corrupto
   - Rate limits OpenAI
   - Session ID inválido
   - ChromaDB connection issues

3. **Smoke Test Checklist para PR** (1h)
   - Checklist manual pre-merge
   - Tests críticos a ejecutar
   - Validación rápida

**Total Enhanced: 7-8 horas**

---

### Nice-to-Have (Futuro)

**Justificación para posposición:**
- Mutation testing y property-based testing requieren mayor inversión y son útiles para código más maduro
- Load testing no es prioritario dado que es un MCP server local (no web service)
- CI/CD integration es mejor hacerlo cuando el proyecto esté production-ready

**Componentes:**
1. Mutation testing (pytest-mutpy)
2. Property-based testing (hypothesis)
3. Load testing con múltiples sesiones concurrentes
4. CI/CD pipeline (GitHub Actions)

---

### Plan de Reducción de Alcance

**Si falta tiempo, recortar en este orden:**

1. **Recortar primero** (Enhanced):
   - Smoke test checklist (-1h): Usar manual checklist existente
   - Memory profiling (-1h): Hacer solo si hay problemas reportados
   - Error scenarios completos (-2h): Cubrir solo los 3 más comunes

2. **Recortar segundo** (Enhanced):
   - Performance benchmarks (-3h): Medir solo embedding speed

3. **CORE INAMOVIBLE** (MVP):
   - Unit tests faltantes
   - Test end-to-end con aislamiento explícito
   - 80% coverage global + 90% en críticos
   - Manual checklist con outputs documentados

**Punto de decisión GO/NO-GO:** Después de completar unit tests faltantes (10h marca), evaluar si es posible completar MVP en tiempo restante.

---

## 3. Diseño Técnico

### Arquitectura Propuesta

```
tests/
├── test_models.py                 # ✨ NUEVO - Pydantic validation
├── test_parser.py                 # ✨ NUEVO - HTML parsing utils
├── test_scholar.py                # ✨ NUEVO - Scholar scraping
├── test_session.py                # ✨ NUEVO - Session management
├── test_openai_client.py          # ✨ NUEVO - OpenAI API
├── test_end_to_end.py             # ✨ NUEVO - Full workflow (AISLADO)
├── test_performance.py            # ✨ NUEVO (Enhanced) - Benchmarks
│
├── test_download_tool.py          # ✅ EXISTE
├── test_embeddings.py             # ✅ EXISTE
├── test_index_tool.py             # ✅ EXISTE
├── test_llm_keywords.py           # ✅ EXISTE
├── test_pdf_chunker.py            # ✅ EXISTE
├── test_pdf_downloader.py         # ✅ EXISTE
├── test_pdf_parser.py             # ✅ EXISTE
├── test_rag_phase7.py             # ✅ EXISTE
├── test_vectorstore.py            # ✅ EXISTE
│
├── fixtures/
│   ├── sample.pdf                 # ✅ EXISTE
│   ├── scholar_page.html          # ✨ NUEVO - Fixture HTML
│   └── mock_responses.py          # ✨ NUEVO - Mock data
│
└── conftest.py                    # ✨ NUEVO - Shared fixtures + isolation helpers
```

### Componentes Afectados

| Componente | Archivo de Test | Estado | Prioridad | Target Coverage |
|------------|----------------|--------|-----------|----------------|
| `models.py` | `test_models.py` | ❌ FALTA | 🔴 CORE | 90%+ |
| `core/parser.py` | `test_parser.py` | ❌ FALTA | 🔴 CORE | 90%+ |
| `core/scholar.py` | `test_scholar.py` | ❌ FALTA | 🔴 CORE | 85%+ |
| `core/session.py` | `test_session.py` | ❌ FALTA | 🔴 CORE | 90%+ |
| `llm/openai.py` | `test_openai_client.py` | ❌ FALTA | 🔴 CORE | 85%+ |
| Workflow completo | `test_end_to_end.py` | ❌ FALTA | 🔴 CORE | 100% |
| Performance | `test_performance.py` | ❌ FALTA | 🟡 Enhanced | N/A |

---

### Decisiones Técnicas (KISS)

#### 1. **Mocking Strategy**
- **Decisión**: Usar `unittest.mock` (stdlib) en lugar de pytest-mock o respx
- **Justificación**: Ya está disponible, equipo familiarizado, suficiente para las necesidades
- **Patrón**: Mock en boundaries (httpx, OpenAI API, filesystem), no mock lógica interna

#### 2. **Fixtures Organization**
- **Decisión**: Centralizar fixtures compartidos en `conftest.py`
- **Justificación**: Reutilización, evita duplicación, pytest discovery automático
- **Patrón**: Fixtures simples y composables

#### 3. **HTML Fixtures para Parser**
- **Decisión**: Crear archivo `scholar_page.html` con snapshot real de Google Scholar
- **Justificación**: Tests determinísticos, no requiere red, versionable
- **Patrón**: Usar web.archive.org snapshot (2021) como en test_sortgs.py

#### 4. **Async Testing**
- **Decisión**: Usar `pytest-asyncio` con markers `@pytest.mark.asyncio`
- **Justificación**: Ya usado en tests existentes, estándar de facto
- **Patrón**: `async def test_*()` con await

#### 5. **Coverage Tool**
- **Decisión**: pytest-cov con html report
- **Justificación**: Integración directa con pytest, reportes visuales útiles
- **Comando**: `uv run pytest --cov=sortgs_mcp --cov-report=html --cov-report=term`

#### 6. **Performance Benchmarks**
- **Decisión**: Usar `time.time()` simple, no pytest-benchmark inicialmente
- **Justificación**: KISS - mediciones básicas suficientes para baseline
- **Patrón**: Decorador manual para timing, log results

#### 7. **Test Data Management**
- **Decisión**: Usar `tmp_path` fixture de pytest para archivos temporales
- **Justificación**: Cleanup automático, isolation entre tests
- **Patrón**: No compartir estado entre tests

#### 8. **Aislamiento en test_end_to_end.py** ⭐ **NUEVO (Mejora Codex - ALTA)**
- **Decisión**: Usar ChromaDB con directorio temporal + in-memory si soportado
- **Justificación**: Evitar flakiness y dependencia de estado persistente
- **Patrón**:
  ```python
  @pytest.fixture
  def isolated_vectorstore(tmp_path):
      """Create isolated ChromaDB instance for testing."""
      chroma_dir = tmp_path / "chroma_test"
      vectorstore = VectorStore(persist_dir=chroma_dir)
      yield vectorstore
      # Cleanup automático por tmp_path
  ```
- **Limpieza explícita**: `tmp_path` fixture garantiza cleanup automático
- **Estado de sesiones**: Cada test usa `tmp_path` independiente para data_dir

---

## 4. Plan de Desarrollo

### Tabla de Tareas

| # | Tarea | Prioridad | Esfuerzo | Criterios de Aceptación | Dependencias |
|---|-------|-----------|----------|------------------------|--------------|
| 1 | Instalar pytest-cov y configurar | 🔴 CORE | 0.5h | `uv add --dev pytest-cov`, coverage report funciona con targets por archivo | Ninguna |
| 2 | Crear conftest.py con fixtures + isolation helpers | 🔴 CORE | 1.5h | Fixtures para session, papers, tmp paths, **isolated_vectorstore** | Task 1 |
| 3 | Crear test_models.py | 🔴 CORE | 2h | Tests para Paper, SearchParams, SearchSession, 90%+ coverage | Task 2 |
| 4 | Crear scholar_page.html fixture | 🔴 CORE | 0.5h | HTML snapshot de Google Scholar guardado | Task 2 |
| 5 | Crear test_parser.py | 🔴 CORE | 2h | Tests para todas las funciones de parsing, 90%+ coverage | Task 4 |
| 6 | Crear test_scholar.py | 🔴 CORE | 3h | Tests para ScholarSearcher con httpx mocked, 85%+ coverage | Task 5 |
| 7 | Crear test_session.py | 🔴 CORE | 2h | Tests para SessionManager CRUD operations, 90%+ coverage | Task 3 |
| 8 | Crear test_openai_client.py | 🔴 CORE | 2h | Tests para OpenAIClient con API mocked, 85%+ coverage | Task 2 |
| 9 | Crear test_end_to_end.py con aislamiento explícito | 🔴 CORE | 4.5h | Test workflow completo, **ChromaDB in-memory + tmp_path**, mocks clarificados | Tasks 2-8 |
| 10 | Ejecutar coverage y fix gaps | 🔴 CORE | 2h | 80% coverage global + 90% en críticos alcanzado | Task 9 |
| 11 | Manual testing checklist (MCP Inspector) con outputs | 🔴 CORE | 2h | 6 tools validados, **outputs esperados documentados** | Task 9 |
| 12 | Manual testing checklist (Claude Code) | 🔴 CORE | 0.5h | Integration con Claude Code verificada | Task 11 |
| 13 | Crear test_performance.py | 🟡 Enhanced | 3h | Benchmarks documentados (embeddings, search, pipeline) | Task 9 |
| 14 | Ampliar error scenarios | 🟡 Enhanced | 3h | Tests para 5+ escenarios de error | Task 9 |
| 15 | Crear smoke test checklist para PR | 🟡 Enhanced | 1h | Checklist markdown documentado | Task 10 |

**Orden Sugerido de Implementación:**
1. Setup (Tasks 1-2): 2h (+0.5h por isolation helpers)
2. Unit Tests Batch 1 (Tasks 3-5): 4.5h
3. Unit Tests Batch 2 (Tasks 6-8): 7h
4. Integration (Task 9): 4.5h (+0.5h por aislamiento)
5. Coverage & Manual (Tasks 10-12): 4.5h (+0.5h por outputs documentados)
6. Enhanced (Tasks 13-15): 7h *(opcional)*

**Total Core: 22.5h | Total Enhanced: 7h**

---

## 5. Plan de Pruebas

### 5.1 Estrategia de Testing

**Niveles de testing:**
1. **Unit Tests**: Componentes individuales aislados con mocks
2. **Integration Tests**: Interacción entre componentes (end-to-end) con **aislamiento explícito**
3. **Manual Tests**: Validación en MCP Inspector y Claude Code con **outputs esperados**
4. **Performance Tests**: Benchmarks de operaciones críticas *(Enhanced)*

### 5.2 Unit Tests - Cobertura por Módulo

#### test_models.py

**Objetivo**: Validar modelos Pydantic (Paper, SearchParams, SearchSession, etc.)
**Target Coverage**: 90%+

```python
# Tests a implementar:
- test_paper_creation_valid
- test_paper_validation_missing_required_fields
- test_paper_cit_per_year_calculation
- test_search_params_defaults
- test_search_params_year_validation
- test_search_params_sort_by_literal
- test_search_params_num_results_bounds
- test_search_session_serialization
- test_search_session_json_roundtrip
- test_pdf_download_result_counts
- test_query_result_with_sources
- test_query_source_metadata
```

**Casos edge:**
- Campos opcionales None
- Validación de rangos (year > 0, num_results 10-1000)
- Literals para sort_by ("Citations", "cit/year")
- Serialization/deserialization JSON

---

#### test_parser.py

**Objetivo**: Validar parsing de HTML de Google Scholar
**Target Coverage**: 90%+

```python
# Tests a implementar:
- test_get_citations_match
- test_get_citations_no_match
- test_get_citations_zero
- test_get_year_match
- test_get_year_no_match
- test_get_year_multiple_matches
- test_get_author_clean_unicode
- test_get_author_split_on_dash
- test_get_author_empty
- test_get_pdf_link_found
- test_get_pdf_link_not_found
- test_parse_google_scholar_page_full
- test_parse_google_scholar_page_empty
```

**Casos edge:**
- HTML sin citations
- Múltiples años en string
- Autores con unicode (xa0)
- PDFs faltantes
- Página vacía

**Fixture HTML:**
```python
# tests/fixtures/scholar_page.html
# Snapshot de web.archive.org/web/20210314203256/
# https://scholar.google.com/scholar?q=machine+learning
```

---

#### test_scholar.py

**Objetivo**: Validar ScholarSearcher con httpx mocked
**Target Coverage**: 85%+

```python
# Tests a implementar:
- test_build_url_basic
- test_build_url_with_start_year
- test_build_url_with_end_year
- test_build_url_with_both_years
- test_build_url_with_languages
- test_build_url_debug_mode
- test_fetch_page_success (mock httpx)
- test_fetch_page_robot_detection
- test_fetch_page_timeout
- test_search_full_workflow (mock)
- test_search_sorting_by_citations
- test_search_sorting_by_cit_per_year
- test_search_pagination_multiple_pages
```

**Mocking pattern:**
```python
from unittest.mock import AsyncMock, patch
import httpx

async def test_fetch_page_success():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.content = b"<html>...</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        searcher = ScholarSearcher()
        result = await searcher.fetch_page("https://example.com")
        assert result == b"<html>...</html>"
```

---

#### test_session.py

**Objetivo**: Validar SessionManager persistence
**Target Coverage**: 90%+

```python
# Tests a implementar:
- test_create_session_generates_uuid
- test_create_session_creates_directories
- test_create_session_creates_pdfs_subdir
- test_save_session_writes_json
- test_save_session_writes_csv
- test_save_session_roundtrip
- test_load_session_from_disk
- test_load_session_not_found
- test_load_session_invalid_json
- test_list_sessions_empty
- test_list_sessions_multiple
- test_list_sessions_ordering
```

**Casos edge:**
- Session ID inválido
- JSON corrupto
- Directorio faltante
- CSV con caracteres especiales

**Test pattern:**
```python
def test_save_load_roundtrip(tmp_path):
    manager = SessionManager(data_dir=tmp_path)
    session = SearchSession(...)

    manager.save_session(session)
    loaded = manager.load_session(session.session_id)

    assert loaded.session_id == session.session_id
    assert loaded.papers == session.papers
```

---

#### test_openai_client.py

**Objetivo**: Validar OpenAI API client con mocks
**Target Coverage**: 85%+

```python
# Tests a implementar:
- test_generate_keywords_success (mock API)
- test_generate_keywords_parsing_json
- test_generate_keywords_parsing_markdown
- test_generate_keywords_retry_on_failure
- test_generate_keywords_retry_exhausted
- test_generate_answer_success (mock API)
- test_generate_answer_with_context
- test_generate_answer_retry_on_failure
- test_token_usage_logging
- test_api_key_validation
```

**Mock pattern:**
```python
from unittest.mock import AsyncMock, patch

async def test_generate_keywords():
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content='["kw1", "kw2", "kw3"]'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test")
        keywords = await client.generate_keywords("test query", 3)
        assert len(keywords) == 3
```

---

### 5.3 Integration Test End-to-End ⭐ **MEJORADO (Mejora Codex - ALTA)**

#### test_end_to_end.py

**Objetivo**: Validar workflow completo del MCP server con aislamiento explícito
**Target Coverage**: 100%

```python
import pytest
from pathlib import Path

@pytest.fixture
def isolated_environment(tmp_path):
    """
    Setup isolated test environment.

    AISLAMIENTO EXPLÍCITO (Mejora Codex):
    - Data dir: tmp_path / "data"
    - ChromaDB: tmp_path / "chroma"
    - Sessions: tmp_path / "data/sessions"
    - Cleanup: Automático por pytest tmp_path
    """
    data_dir = tmp_path / "data"
    chroma_dir = tmp_path / "chroma"
    data_dir.mkdir()
    chroma_dir.mkdir()

    return {
        "data_dir": data_dir,
        "chroma_dir": chroma_dir,
        "sessions_dir": data_dir / "sessions"
    }


async def test_full_workflow_with_explicit_isolation(isolated_environment):
    """
    Test completo del workflow con aislamiento explícito.

    ESTRATEGIA DE MOCKS CLARIFICADA (Mejora Codex - MEDIA):
    - OpenAI API: SIEMPRE mocked (AsyncMock)
    - Google Scholar: Usar fixtures HTML (scholar_page.html)
    - PDFs: Mock downloads (no red)
    - ChromaDB: Real pero en directorio temporal (isolated_environment)
    - Embeddings: Real pero con modelo pequeño/cache

    Fases:
    1. generate_search_keywords (mock OpenAI) ✅ MOCKED
    2. search_papers (HTML fixtures) ✅ FIXTURES
    3. download_papers (mock PDFs) ✅ MOCKED
    4. index_papers (ChromaDB temporal + embeddings reales) ✅ REAL + AISLADO
    5. query_papers (mock OpenAI answer) ✅ MOCKED

    Verificaciones:
    - Session creada en directorio temporal correcto
    - PDFs "descargados" a tmp_path/data/sessions/{id}/pdfs/
    - Chunks indexados en ChromaDB temporal (tmp_path/chroma/)
    - Query devuelve answer con sources
    - Metadata preservation en todo el pipeline
    - NO hay estado compartido entre tests
    """

    # Setup
    data_dir = isolated_environment["data_dir"]
    chroma_dir = isolated_environment["chroma_dir"]

    # 1. Generate keywords (MOCKED)
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(
                content='["deep learning", "neural networks", "machine learning"]'
            ))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # Llamar tool generate_search_keywords
        keywords_result = await generate_search_keywords(
            query="AI research",
            num_variations=3
        )
        assert len(keywords_result["keywords"]) == 3

    # 2. Search papers (FIXTURES)
    # Usar scholar_page.html fixture en lugar de red real
    # ... (implementación similar a test_scholar.py)

    # 3. Download papers (MOCKED)
    # Mock httpx.AsyncClient para no descargar PDFs reales
    # ... (implementación similar a test_pdf_downloader.py)

    # 4. Index papers (REAL + AISLADO)
    vectorstore = VectorStore(persist_dir=chroma_dir)
    # Embeddings reales pero ChromaDB en tmp_path
    # ... (implementación con isolated_vectorstore)

    # 5. Query papers (MOCKED)
    with patch('openai.AsyncOpenAI') as mock_openai:
        # Mock answer generation
        # ... (similar a paso 1)
        pass

    # Assertions finales
    assert session_id is not None
    assert (data_dir / "sessions" / session_id).exists()
    assert download_result["downloaded"] > 0
    assert index_result["chunks_created"] > 0
    assert len(query_result["answer"]) > 0
    assert len(query_result["sources"]) > 0

    # Verificar aislamiento
    assert chroma_dir.exists()
    assert len(list(chroma_dir.iterdir())) > 0  # ChromaDB creó archivos
```

**Estrategia de aislamiento documentada:**
- **ChromaDB**: Directorio temporal por test (tmp_path / "chroma")
- **Sessions**: Directorio temporal por test (tmp_path / "data/sessions")
- **Limpieza**: Automática vía pytest tmp_path fixture
- **Concurrencia**: Tests ejecutan en paralelo sin colisión de estado

---

### 5.4 Manual Testing Checklist - MCP Inspector ⭐ **MEJORADO (Mejora Codex - ALTA)**

**Prerequisito:** `npm install -g @modelcontextprotocol/inspector`

**Comando:** `mcp inspect uv run sortgs-mcp`

**Tests a ejecutar con outputs esperados documentados:**

| # | Tool | Input | Expected Output | Ejemplo Output | Status |
|---|------|-------|-----------------|----------------|--------|
| 1 | `generate_search_keywords` | `{"query": "transformers NLP", "num_variations": 3}` | 3 keywords distintos relacionados con transformers y NLP | `{"keywords": ["transformer architecture BERT GPT", "attention mechanism neural language models", "sequence-to-sequence NLP deep learning"]}` | ⬜ |
| 2 | `search_papers` | `{"keywords": "deep learning", "num_results": 10}` | session_id (UUID), papers_found: 10, top_5_titles (lista) | `{"session_id": "550e8400-...", "papers_found": 10, "top_5_titles": ["Deep Learning", "..."], "csv_path": "data/sessions/.../results.csv"}` | ⬜ |
| 3 | `download_papers` | `{"session_id": "<from step 2>", "max_papers": 3}` | downloaded: 0-3 (algunos pueden fallar), failed: 0-3, pdf_paths: lista | `{"downloaded": 2, "skipped": 0, "failed": 1, "pdf_paths": ["data/.../paper_0.pdf", "..."], "failed_papers": [{"rank": 2, "title": "...", "reason": "403 Forbidden"}]}` | ⬜ |
| 4 | `index_papers` | `{"session_id": "<from step 2>"}` | papers_indexed: >0, chunks_created: >0, indexing_time_sec: número | `{"session_id": "550e8400-...", "papers_indexed": 2, "chunks_created": 45, "indexing_time_sec": 12.3, "failed_papers": []}` | ⬜ |
| 5 | `query_papers` | `{"question": "What is deep learning?", "session_id": "<from step 2>"}` | answer: texto largo con citations, sources: lista de chunks con metadata | `{"question": "What is deep learning?", "answer": "Deep learning is a subset of machine learning...\n\nSources: LeCun et al. (2015), Goodfellow et al. (2016)", "sources": [{"paper_title": "...", "chunk_text": "...", "relevance_score": 0.89, "metadata": {...}}]}` | ⬜ |
| 6 | `list_sessions` | `{}` | sessions: lista con session_id, keywords, created_at, papers_count, pdfs_downloaded, indexed | `{"sessions": [{"session_id": "550e8400-...", "keywords": "deep learning", "created_at": "2025-12-30T...", "papers_count": 10, "pdfs_downloaded": 2, "indexed": true}]}` | ⬜ |

**Documentación de resultados (Mejora Codex):**
- **Crear archivo `docs/MANUAL_TESTING_RESULTS.md`** con:
  - Fecha de ejecución
  - Versión del MCP server
  - Para cada tool: input usado, output obtenido, status (✅ Pass / ❌ Fail), notas
  - Screenshots de MCP Inspector (opcional)
  - Errores encontrados con stack trace
  - Logs relevantes de `sortgs_mcp.log`

**Formato del documento:**
```markdown
# Manual Testing Results - MCP Inspector

**Fecha**: 2025-12-30
**Versión MCP Server**: sortgs-mcp v1.0
**Tester**: [Nombre]

## Test 1: generate_search_keywords

**Input**:
\```json
{"query": "transformers NLP", "num_variations": 3}
\```

**Expected Output**: 3 keywords distintos relacionados con transformers y NLP

**Actual Output**:
\```json
{"keywords": ["transformer architecture BERT GPT", "attention mechanism neural language models", "sequence-to-sequence NLP deep learning"]}
\```

**Status**: ✅ PASS

**Notes**: Keywords generados son relevantes y diversos.

---

[... repetir para cada tool ...]
```

---

### 5.5 Manual Testing Checklist - Claude Code Integration

**Prerequisito:** Configurar MCP server en Claude Code

```bash
claude mcp add --transport stdio sortgs-mcp -- uv run sortgs-mcp
```

**Tests a ejecutar:**

| # | Acción | Validación | Ejemplo Output Esperado | Status |
|---|--------|-----------|------------------------|--------|
| 1 | Verificar server aparece en `claude mcp list` | sortgs-mcp listed | `sortgs-mcp (stdio) - uv run sortgs-mcp` | ⬜ |
| 2 | En chat: "Generate keywords for transformers" | Claude invoca tool correctamente | Claude responde con keywords generados | ⬜ |
| 3 | En chat: "Search for deep learning papers" | Session creada, papers encontrados | Claude muestra session_id y top papers | ⬜ |
| 4 | En chat: "Download PDFs from session X" | PDFs descargados | Claude reporta X downloaded, Y failed | ⬜ |
| 5 | En chat: "Index the papers from session X" | Indexing completo | Claude reporta N chunks indexados | ⬜ |
| 6 | En chat: "What is attention mechanism?" | RAG answer con sources | Claude responde con answer + citations | ⬜ |
| 7 | Verificar logs en `sortgs_mcp.log` | Logs legibles, sin errores críticos | Tool invocations logged, no tracebacks | ⬜ |
| 8 | Test error handling: invalid session | Error message claro y útil | `Session 'invalid-id' not found. Use list_sessions to see available sessions.` | ⬜ |

---

### 5.6 pytest Configuration

**Actualizar `pyproject.toml`:**

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests (>1s)",
    "requires_api: Requires external API",
]

[tool.coverage.run]
source = ["src/sortgs_mcp"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

# ⭐ NUEVO (Mejora Codex - MEDIA): Fail bajo thresholds por archivo
fail_under = 80

[tool.coverage.paths]
source = [
    "src/sortgs_mcp",
]
```

---

### 5.7 Coverage Goals ⭐ **MEJORADO (Mejora Codex - MEDIA)**

**Baseline (antes de Fase 8):** ~50-60% (estimado, basado en tests existentes)

**Meta MVP:** 80% total coverage

**Prioridad de coverage por módulo con targets específicos:**
- 🔴 **Critical (90%+)**: models.py, core/parser.py, core/session.py
  - **Líneas críticas**: Validación Pydantic, parsing HTML, serialization JSON
- 🟡 **High (85%+)**: core/scholar.py, tools/*, llm/openai.py
  - **Líneas críticas**: Error handling HTTP, retry logic, mock boundaries
- 🟢 **Medium (75%+)**: rag/*, pdf/*, config.py
  - **Líneas críticas**: Embeddings, chunking, ChromaDB operations
- ⚪ **Low (60%+)**: server.py
  - **Justificación**: Principalmente boilerplate de MCP server

**Estrategia para alcanzar targets (Mejora Codex):**
1. **Ejecutar coverage por archivo** después de cada test creado:
   ```bash
   uv run pytest tests/test_models.py --cov=sortgs_mcp.models --cov-report=term-missing
   ```
2. **Identificar líneas críticas faltantes** en report term-missing
3. **Priorizar tests para líneas con lógica de negocio** (no boilerplate)
4. **Aceptar gaps en líneas defensivas** (ej: `if TYPE_CHECKING:`)

**Comandos útiles:**

```bash
# Coverage básico
uv run pytest --cov=sortgs_mcp --cov-report=term

# Coverage con HTML (visual)
uv run pytest --cov=sortgs_mcp --cov-report=html
# Abrir htmlcov/index.html en browser

# Coverage con gaps específicos (líneas faltantes)
uv run pytest --cov=sortgs_mcp --cov-report=term-missing

# ⭐ NUEVO: Coverage por archivo específico
uv run pytest tests/test_models.py --cov=sortgs_mcp.models --cov-report=term-missing
uv run pytest tests/test_parser.py --cov=sortgs_mcp.core.parser --cov-report=term-missing

# Coverage con fail si < 80%
uv run pytest --cov=sortgs_mcp --cov-report=term --cov-fail-under=80

# Coverage con markers
uv run pytest -m "unit" --cov=sortgs_mcp --cov-report=term
```

**Interpretación de resultados:**
- `Stmts`: Número total de líneas ejecutables
- `Miss`: Líneas no cubiertas por tests
- `Cover`: Porcentaje de cobertura
- **NUEVO**: Buscar líneas críticas sin coverage en term-missing (error handling, edge cases, validaciones)

---

## 6. Contingencia y Riesgos

### Escenarios de Bloqueo

#### 1. **Coverage no alcanza 80% global o 90% en críticos**
- **Probabilidad**: Media
- **Impacto**: Alto (criterio de éxito MVP)
- **Mitigación proactiva**:
  - Ejecutar coverage report **por archivo** después de cada batch de tests
  - Identificar módulos con bajo coverage early usando `--cov-report=term-missing`
  - Priorizar tests que aumenten coverage en **líneas críticas** (no boilerplate)
- **Plan B**:
  - Si coverage global queda en 75-79%, identificar las líneas críticas faltantes
  - Añadir tests específicos para error handling (suele faltar coverage)
  - Aceptar 75% global si:
    - Archivos críticos tienen 90%+
    - Líneas faltantes son edge cases no críticos o boilerplate
- **Punto de decisión**: Después de Task 10, si coverage < 75%, añadir 2h para tests adicionales

#### 2. **Test end-to-end falla por dependencias externas o estado compartido**
- **Probabilidad**: Baja (gracias a aislamiento explícito)
- **Impacto**: Alto
- **Mitigación proactiva**:
  - ⭐ **NUEVO**: Usar `isolated_environment` fixture con tmp_path
  - ⭐ **NUEVO**: ChromaDB en directorio temporal separado
  - Mocks comprehensivos para OpenAI y httpx
  - Fixtures estáticos (scholar_page.html) en lugar de red
- **Plan B**:
  - Separar en múltiples integration tests más pequeños
  - Test cada fase del workflow independientemente primero
  - Verificar limpieza de ChromaDB con `assert` en fixtures
- **Alternativa**: Si aislamiento falla, usar in-memory SQLite para ChromaDB si soportado

#### 3. **Performance benchmarks toman mucho tiempo**
- **Probabilidad**: Media
- **Impacto**: Bajo (es Enhanced, no MVP)
- **Mitigación proactiva**:
  - Limitar tamaño de datasets de prueba (10 papers, 100 chunks)
  - Usar modelo de embeddings más rápido para tests
  - Cachear modelo de embeddings entre tests
- **Plan B**:
  - Reducir scope a solo benchmark de embeddings (más crítico)
  - Usar subset más pequeño de datos
  - Marcar con `@pytest.mark.slow` y skip por default
- **Recorte**: Eliminar completamente si se va de tiempo (Enhanced, no MVP)

#### 4. **MCP Inspector installation issues**
- **Probabilidad**: Baja
- **Impacto**: Medio
- **Mitigación proactiva**:
  - Probar instalación early (Task 11)
  - Verificar Node.js está instalado
  - Documentar versiones requeridas
- **Plan B**:
  - Manual testing directo con Python scripts en lugar de Inspector
  - Usar `mcp dev` si Inspector no funciona
  - Test directo invocando tools desde Python
- **Alternativa**: Solo testing en Claude Code si Inspector no funciona

#### 5. **Mocking OpenAI API es complejo**
- **Probabilidad**: Baja
- **Impacto**: Medio
- **Mitigación proactiva**:
  - Estudiar estructura de respuestas OpenAI primero
  - Reutilizar patterns de tests existentes (test_llm_keywords.py)
- **Plan B**:
  - Usar responses reales cacheadas (guardar JSON fixtures)
  - Simplificar mocks (solo campos esenciales)
- **Alternativa**: Marcar tests con `@pytest.mark.requires_api` y skip si no hay key

---

### Plan de Reducción Detallado

**Si quedan 10 horas:**
- ✅ Completar MVP core (Tasks 1-10)
- ❌ Recortar Enhanced completo
- ❌ Recortar Task 12 (Claude Code testing)
- Resultado: 80% coverage global + 90% críticos, tests core, manual checklist MCP Inspector con outputs

**Si quedan 15 horas:**
- ✅ Completar MVP core
- ✅ Performance benchmarks básicos (solo embeddings)
- ❌ Recortar error scenarios y smoke checklist
- Resultado: MVP + baseline performance

**Si quedan 20+ horas:**
- ✅ Completar MVP + Enhanced completo
- Resultado: Suite comprehensiva completa

### Punto de Decisión GO/NO-GO

**Timing checkpoint:** Después de Task 8 (test_openai_client.py)

**Preguntas:**
1. ¿Todos los unit tests están pasando?
2. ¿El tiempo invertido está dentro del estimado ±20%?
3. ¿Quedan al menos 6 horas para end-to-end + coverage + manual?
4. ⭐ **NUEVO**: ¿Los archivos críticos ya tienen 90%+ coverage?

**Si NO a cualquiera:**
- Evaluar recorte de scope Enhanced
- Priorizar end-to-end sobre performance
- Simplificar fixtures si están tomando mucho tiempo
- **NUEVO**: Focalizar tests en líneas críticas faltantes (usar term-missing)
- Comunicar ajustes al stakeholder

---

## 7. Entregables

### MVP (CORE)

1. **6 archivos de tests nuevos:**
   - `tests/test_models.py` (~100-150 líneas, 90%+ coverage)
   - `tests/test_parser.py` (~150-200 líneas, 90%+ coverage)
   - `tests/test_scholar.py` (~200-250 líneas, 85%+ coverage)
   - `tests/test_session.py` (~150-200 líneas, 90%+ coverage)
   - `tests/test_openai_client.py` (~150-200 líneas, 85%+ coverage)
   - `tests/test_end_to_end.py` (~250-350 líneas, 100% coverage, **con aislamiento explícito**)

2. **Configuración de coverage:**
   - pytest-cov instalado (`uv add --dev pytest-cov`)
   - `pyproject.toml` configurado con targets por archivo
   - Coverage report HTML generado en `htmlcov/`
   - ⭐ **NUEVO**: `--cov-fail-under=80` configurado

3. **Fixtures compartidos:**
   - `tests/conftest.py` con fixtures reusables + **isolated_environment**
   - `tests/fixtures/scholar_page.html` (snapshot Google Scholar)
   - `tests/fixtures/mock_responses.py` (datos de prueba)

4. **Manual testing documentation:**
   - Checklist MCP Inspector ejecutado (6 tools validados)
   - ⭐ **NUEVO**: `docs/MANUAL_TESTING_RESULTS.md` con outputs esperados y obtenidos
   - Checklist Claude Code ejecutado (8 validaciones)

5. **Coverage report:**
   - HTML report en `htmlcov/index.html`
   - Terminal report mostrando 80%+ global + 90% en críticos
   - ⭐ **NUEVO**: Identificación de líneas críticas faltantes (si coverage < 80%)

---

### Enhanced (OPCIONAL)

6. **Performance tests:**
   - `tests/test_performance.py` (~150-200 líneas)
   - Benchmarks documentados:
     - Embedding generation (100 chunks): X segundos
     - Vector search (1000 chunks): Y segundos
     - Pipeline completo (10 papers): Z minutos
   - Baseline guardado en `docs/PERFORMANCE_BASELINE.md`

7. **Error scenarios:**
   - Tests para 5+ casos de error:
     - Robot check Google Scholar
     - PDF 404/corrupto
     - Rate limit OpenAI
     - Session ID inválido
     - ChromaDB connection issues
   - Documentación de error handling

8. **Smoke test checklist:**
   - `docs/SMOKE_TESTS.md`
   - Checklist manual pre-PR con tests críticos
   - Validación rápida (<5 min) de funcionalidad core

---

## 8. Implementación Detallada

### 8.1 Task 1: Instalar pytest-cov (0.5h)

```bash
# Instalar pytest-cov
uv add --dev pytest-cov

# Verificar instalación
uv run pytest --version
uv run pytest --cov --help

# Ejecutar baseline coverage
uv run pytest --cov=sortgs_mcp --cov-report=term

# Generar HTML report inicial
uv run pytest --cov=sortgs_mcp --cov-report=html
```

**Criterio de aceptación:**
- ✅ pytest-cov instalado en pyproject.toml
- ✅ Comando coverage funciona sin errores
- ✅ HTML report se genera en htmlcov/
- ⭐ **NUEVO**: Configurar `fail_under = 80` en pyproject.toml

---

### 8.2 Task 2: Crear conftest.py con isolation helpers (1.5h) ⭐ **MEJORADO**

**Archivo:** `tests/conftest.py`

```python
"""Shared pytest fixtures for sortgs_mcp tests."""

import pytest
from datetime import datetime
from pathlib import Path
from sortgs_mcp.models import Paper, SearchParams, SearchSession
from sortgs_mcp.rag.vectorstore import VectorStore
import uuid


@pytest.fixture
def sample_paper():
    """Create a sample Paper instance for testing."""
    return Paper(
        rank=1,
        title="Attention Is All You Need",
        authors="Vaswani et al.",
        citations=50000,
        year=2017,
        publisher="NeurIPS",
        venue="Conference",
        content_snippet="We propose a new simple network architecture...",
        source_url="https://arxiv.org/abs/1706.03762",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        cit_per_year=6250.0
    )


@pytest.fixture
def sample_papers():
    """Create a list of sample Papers for testing."""
    return [
        Paper(
            rank=1,
            title="Attention Is All You Need",
            authors="Vaswani et al.",
            citations=50000,
            year=2017,
            publisher="NeurIPS",
            venue="Conference",
            content_snippet="Transformers architecture...",
            source_url="https://arxiv.org/abs/1706.03762",
            pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
            cit_per_year=6250.0
        ),
        Paper(
            rank=2,
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors="Devlin et al.",
            citations=30000,
            year=2018,
            publisher="NAACL",
            venue="Conference",
            content_snippet="BERT architecture...",
            source_url="https://arxiv.org/abs/1810.04805",
            pdf_url="https://arxiv.org/pdf/1810.04805.pdf",
            cit_per_year=4285.7
        ),
    ]


@pytest.fixture
def sample_search_params():
    """Create sample SearchParams for testing."""
    return SearchParams(
        keywords="transformers attention mechanism",
        num_results=10,
        sort_by="Citations",
        start_year=2017,
        end_year=2024,
        languages=["en"]
    )


@pytest.fixture
def sample_session(sample_search_params, sample_papers):
    """Create a sample SearchSession for testing."""
    return SearchSession(
        session_id=str(uuid.uuid4()),
        created_at=datetime.now(),
        params=sample_search_params,
        papers=sample_papers,
        papers_count=len(sample_papers),
        pdfs_downloaded=0,
        indexed=False
    )


@pytest.fixture
def scholar_html_fixture():
    """Load scholar page HTML fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "scholar_page.html"
    if fixture_path.exists():
        return fixture_path.read_text(encoding='utf-8')
    return None


@pytest.fixture
def mock_openai_keywords_response():
    """Mock OpenAI response for keyword generation."""
    return {
        "choices": [
            {
                "message": {
                    "content": '["transformers neural networks", "attention mechanism BERT GPT", "sequence models deep learning"]'
                }
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        }
    }


@pytest.fixture
def mock_openai_answer_response():
    """Mock OpenAI response for answer generation."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Based on the provided papers, transformers use self-attention mechanisms..."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 500,
            "completion_tokens": 200,
            "total_tokens": 700
        }
    }


# ⭐ NUEVO: Isolation helpers (Mejora Codex - ALTA)

@pytest.fixture
def isolated_environment(tmp_path):
    """
    Setup isolated test environment for end-to-end tests.

    AISLAMIENTO EXPLÍCITO (Mejora Codex):
    - Data dir: tmp_path / "data"
    - ChromaDB: tmp_path / "chroma"
    - Sessions: tmp_path / "data/sessions"
    - Cleanup: Automático por pytest tmp_path

    Returns:
        dict: Paths to isolated directories
    """
    data_dir = tmp_path / "data"
    chroma_dir = tmp_path / "chroma"
    sessions_dir = data_dir / "sessions"

    data_dir.mkdir()
    chroma_dir.mkdir()
    sessions_dir.mkdir()

    return {
        "data_dir": data_dir,
        "chroma_dir": chroma_dir,
        "sessions_dir": sessions_dir
    }


@pytest.fixture
def isolated_vectorstore(tmp_path):
    """
    Create isolated ChromaDB instance for testing.

    AISLAMIENTO EXPLÍCITO (Mejora Codex):
    - ChromaDB en directorio temporal
    - Cleanup automático
    - Sin estado compartido entre tests

    Yields:
        VectorStore: Isolated vectorstore instance
    """
    chroma_dir = tmp_path / "chroma_test"
    chroma_dir.mkdir()

    vectorstore = VectorStore(persist_dir=chroma_dir)

    yield vectorstore

    # Cleanup explícito (aunque tmp_path ya lo hace)
    # Útil para debugging si tmp_path falla
    import shutil
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir, ignore_errors=True)
```

**Criterio de aceptación:**
- ✅ Fixtures compilables y usables
- ✅ Tests existentes pueden importar fixtures
- ✅ Datos de prueba realistas
- ⭐ **NUEVO**: Fixtures de aislamiento (`isolated_environment`, `isolated_vectorstore`) funcionan

---

### 8.3 Task 3: Crear test_models.py (2h)

*[El contenido permanece igual que en la versión 1.0, ver archivo completo más arriba]*

---

### 8.4 Patrones de Testing

#### Mock HTTP Requests (httpx)
```python
import httpx
from unittest.mock import AsyncMock, patch

async def test_fetch_page_success():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.content = b"<html>...</html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        searcher = ScholarSearcher()
        result = await searcher.fetch_page("https://example.com")
        assert result == b"<html>...</html>"
```

#### Mock OpenAI API
```python
from unittest.mock import AsyncMock, patch

async def test_generate_keywords():
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content='["kw1", "kw2", "kw3"]'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = OpenAIClient(api_key="test")
        keywords = await client.generate_keywords("test query", 3)
        assert len(keywords) == 3
```

#### Temporary Directories with Isolation
```python
def test_session_creation(tmp_path):
    session_manager = SessionManager(data_dir=tmp_path)
    session_id = session_manager.create_session(params)

    # Verificar directorio creado
    session_dir = tmp_path / "sessions" / session_id
    assert session_dir.exists()
    assert (session_dir / "pdfs").exists()

    # ⭐ NUEVO: Verificar aislamiento
    assert session_dir.parent == tmp_path / "sessions"
```

---

## 9. Checklist Final

### Pre-Implementation
- [ ] pytest-cov instalado
- [ ] conftest.py creado con isolation helpers
- [ ] Fixtures HTML preparados
- [ ] Baseline coverage medido con targets por archivo

### Unit Tests
- [ ] test_models.py completo y pasando (90%+ coverage)
- [ ] test_parser.py completo y pasando (90%+ coverage)
- [ ] test_scholar.py completo y pasando (85%+ coverage)
- [ ] test_session.py completo y pasando (90%+ coverage)
- [ ] test_openai_client.py completo y pasando (85%+ coverage)

### Integration Tests
- [ ] test_end_to_end.py completo y pasando (100% coverage)
- [ ] Workflow completo funciona (keywords → query) con aislamiento verificado
- [ ] ⭐ **NUEVO**: Aislamiento ChromaDB + sesiones confirmado (no estado compartido)

### Coverage
- [ ] Coverage report generado
- [ ] 80%+ coverage global alcanzado
- [ ] ⭐ **NUEVO**: 90%+ coverage en archivos críticos (models, parser, session)
- [ ] Gaps críticos identificados y documentados con term-missing

### Manual Testing
- [ ] MCP Inspector instalado
- [ ] 6 tools validados en Inspector
- [ ] ⭐ **NUEVO**: Outputs esperados documentados en MANUAL_TESTING_RESULTS.md
- [ ] Claude Code integration probada
- [ ] Resultados documentados en formato trazable

### Enhanced (Opcional)
- [ ] test_performance.py creado
- [ ] Benchmarks documentados
- [ ] Error scenarios cubiertos
- [ ] Smoke test checklist creado

### Documentation
- [ ] ⭐ **NUEVO**: MANUAL_TESTING_RESULTS.md creado con outputs esperados/obtenidos
- [ ] Coverage report en htmlcov/
- [ ] PERFORMANCE_BASELINE.md (si Enhanced)
- [ ] SMOKE_TESTS.md (si Enhanced)

---

## 10. Resumen Ejecutivo de Entrega

**Objetivo:** Suite de tests comprehensiva con 80% coverage global + 90% en críticos

**Entregables Core (MVP):**
1. 6 archivos de tests nuevos (~1100 líneas código)
2. Coverage report HTML con 80%+ global + 90% críticos
3. Fixtures compartidos en conftest.py con **isolation helpers**
4. Manual testing checklists ejecutados con **outputs documentados**
5. Documentación de resultados con ejemplos esperados

**Mejoras Incorporadas (Rev-1):**
1. ⭐ **Aislamiento explícito** en test_end_to_end (ChromaDB + sesiones en tmp_path)
2. ⭐ **Checklists con outputs esperados** documentados en MANUAL_TESTING_RESULTS.md
3. ⭐ **Scope de mocks clarificado** (OpenAI mocked, Scholar fixtures, ChromaDB real+aislado)
4. ⭐ **Coverage por archivo** con targets específicos (90% críticos, 85% high, 75% medium)

**Entregables Enhanced (Opcional):**
6. Performance benchmarks
7. Error scenarios tests
8. Smoke test checklist

**Tiempo estimado:**
- MVP: 16-18 horas → **22.5 horas** (ajustado por mejoras)
- Enhanced: +7-8 horas
- **Total: 29.5-30.5 horas**

**Criterios de éxito:**
- ✅ 100% tests pasando
- ✅ 80%+ code coverage global
- ⭐ **NUEVO**: 90%+ coverage en archivos críticos
- ✅ Test end-to-end exitoso con aislamiento verificado
- ⭐ **NUEVO**: Manual checklist completado con outputs trazables

**Riesgos principales:**
- Coverage difícil de alcanzar (mitigación: priorizar líneas críticas con term-missing)
- Test end-to-end falla (mitigación: aislamiento explícito con tmp_path + ChromaDB temporal)
- Performance tests lentos (mitigación: datasets pequeños, marcar @slow)

**Punto de decisión GO/NO-GO:** Después de unit tests (10h), evaluar si MVP es alcanzable y si archivos críticos tienen 90%+.

---

**FIN DEL WORKPLAN REV-1**

---

## Anexo: Cambios Detallados en Rev-1

### Cambios por Mejora de Codex

#### 1. ALTA: Aislamiento ChromaDB + Sesiones (Sección 5.3)
- **Antes**: Mención vaga de "usar in-memory si posible"
- **Después**:
  - Fixture `isolated_environment` con tmp_path explícito
  - Fixture `isolated_vectorstore` con ChromaDB en directorio temporal
  - Código de ejemplo completo en test_end_to_end.py
  - Verificación de aislamiento en assertions

#### 2. ALTA: Checklists Trazables (Secciones 5.4, 5.5)
- **Antes**: Tabla simple con inputs/outputs esperados
- **Después**:
  - Columna "Ejemplo Output" con JSON concreto
  - Documento `MANUAL_TESTING_RESULTS.md` estructurado
  - Template con formato esperado/obtenido/status/notas
  - Outputs esperados para cada tool en tabla

#### 3. MEDIA: Scope de Mocks Clarificado (Sección 5.3)
- **Antes**: "OpenAI API: siempre mocked, httpx: debug mode o mock"
- **Después**:
  - Lista explícita por componente:
    - OpenAI: SIEMPRE mocked
    - Scholar: HTML fixtures (scholar_page.html)
    - PDFs: Mock downloads
    - ChromaDB: Real pero aislado en tmp_path
    - Embeddings: Real pero con modelo pequeño/cache
  - Comentarios inline en código de ejemplo

#### 4. MEDIA: Coverage por Archivo (Sección 5.7)
- **Antes**: "80% global, priorizar módulos críticos"
- **Después**:
  - Targets específicos: 90% críticos, 85% high, 75% medium, 60% low
  - Comandos para medir coverage por archivo individual
  - `fail_under = 80` en pyproject.toml
  - Estrategia explícita: ejecutar term-missing y priorizar líneas críticas
  - Tabla con "Target Coverage" por componente

### Ajustes de Tiempo

| Tarea | Tiempo Original | Tiempo Rev-1 | Diferencia | Motivo |
|-------|----------------|--------------|------------|--------|
| Task 2 (conftest.py) | 1h | 1.5h | +0.5h | Isolation helpers |
| Task 9 (end-to-end) | 4h | 4.5h | +0.5h | Aislamiento explícito |
| Task 11 (MCP Inspector) | 1.5h | 2h | +0.5h | Documentar outputs |
| **Total MVP** | 16-18h | **22.5h** | +4.5-6.5h | Mejoras calidad |
