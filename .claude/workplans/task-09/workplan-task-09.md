# Workplan Task-09: Fase 8 - Suite de Tests Comprehensiva

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Workplan Task-09: Fase 8 - Suite de Tests Comprehensiva |
| **Fecha de creación** | 2025-12-30 |
| **Versión** | 1.0 |
| **Estado** | APROBADO |
| **Autor** | Claude Sonnet 4.5 (MCP Planning Agent) |
| **Stack tecnológico** | Python 3.10+, pytest, pytest-asyncio, pytest-cov, unittest.mock |

### Historial de Revisiones

| Versión | Fecha | Cambios | Solicitante |
|---------|-------|---------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Sistema create-workplan |

---

## 1. Resumen Ejecutivo

### Descripción General
Desarrollar suite de tests comprehensiva para asegurar la calidad del código del proyecto sortgs-mcp. El proyecto ya cuenta con ~50 tests distribuidos en 15 archivos, cubriendo PDF processing, embeddings, vectorstore y algunos tools. Esta fase completará los tests faltantes para componentes core (models, parser, scholar, session, openai_client) y añadirá tests end-to-end, performance benchmarks y checklists de testing manual.

### Alcance
- **Completar gaps de unit tests** para 5 componentes sin tests
- **Test end-to-end** del workflow completo (keywords → search → download → index → query)
- **Coverage report** con meta de 80%
- **Manual testing checklist** para MCP Inspector y Claude Code
- **Performance benchmarks** básicos (Enhanced)
- **Error scenarios** comprehensivos (Enhanced)

### Objetivos
1. **Calidad**: Alcanzar 80% code coverage
2. **Confianza**: Validar todos los componentes críticos funcionan correctamente
3. **Regresión**: Prevenir bugs en futuras modificaciones
4. **Documentación**: Tests sirven como documentación de uso
5. **Performance**: Establecer baseline de performance

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
- ❌ Manual testing no documentado

---

## 2. Priorización del Alcance

### MVP/CORE (Obligatorio)

**Criterio de éxito:**
- ✅ Todos los tests unitarios pasando (100% pass rate)
- ✅ 80% code coverage mínimo
- ✅ Test end-to-end exitoso con workflow completo
- ✅ Manual testing checklist ejecutado en MCP Inspector

**Componentes obligatorios:**
1. **Test Infrastructure** (2h)
   - Instalar pytest-cov
   - Configurar coverage reporting
   - Setup baseline coverage report

2. **Unit Tests - Componentes Faltantes** (8-10h)
   - `tests/test_models.py`: Validación Pydantic completa
   - `tests/test_parser.py`: Parsing de HTML Google Scholar
   - `tests/test_scholar.py`: ScholarSearcher con mocks
   - `tests/test_session.py`: SessionManager persistence
   - `tests/test_openai_client.py`: OpenAI API mocked

3. **Integration Test End-to-End** (4h)
   - `tests/test_end_to_end.py`: Workflow completo con fixtures

4. **Manual Testing Checklist** (2h)
   - Checklist para MCP Inspector (6 tools)
   - Checklist para Claude Code integration
   - Documentar resultados

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
   - Test end-to-end
   - 80% coverage
   - Manual checklist básico

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
├── test_end_to_end.py             # ✨ NUEVO - Full workflow
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
└── conftest.py                    # ✨ NUEVO - Shared fixtures
```

### Componentes Afectados

| Componente | Archivo de Test | Estado | Prioridad |
|------------|----------------|--------|-----------|
| `models.py` | `test_models.py` | ❌ FALTA | 🔴 CORE |
| `core/parser.py` | `test_parser.py` | ❌ FALTA | 🔴 CORE |
| `core/scholar.py` | `test_scholar.py` | ❌ FALTA | 🔴 CORE |
| `core/session.py` | `test_session.py` | ❌ FALTA | 🔴 CORE |
| `llm/openai.py` | `test_openai_client.py` | ❌ FALTA | 🔴 CORE |
| Workflow completo | `test_end_to_end.py` | ❌ FALTA | 🔴 CORE |
| Performance | `test_performance.py` | ❌ FALTA | 🟡 Enhanced |

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

---

## 4. Plan de Desarrollo

### Tabla de Tareas

| # | Tarea | Prioridad | Esfuerzo | Criterios de Aceptación | Dependencias |
|---|-------|-----------|----------|------------------------|--------------|
| 1 | Instalar pytest-cov y configurar | 🔴 CORE | 0.5h | `uv add --dev pytest-cov`, coverage report funciona | Ninguna |
| 2 | Crear conftest.py con fixtures compartidos | 🔴 CORE | 1h | Fixtures para session, papers, tmp paths | Task 1 |
| 3 | Crear test_models.py | 🔴 CORE | 2h | Tests para Paper, SearchParams, SearchSession, validation | Task 2 |
| 4 | Crear scholar_page.html fixture | 🔴 CORE | 0.5h | HTML snapshot de Google Scholar guardado | Task 2 |
| 5 | Crear test_parser.py | 🔴 CORE | 2h | Tests para todas las funciones de parsing | Task 4 |
| 6 | Crear test_scholar.py | 🔴 CORE | 3h | Tests para ScholarSearcher con httpx mocked | Task 5 |
| 7 | Crear test_session.py | 🔴 CORE | 2h | Tests para SessionManager CRUD operations | Task 3 |
| 8 | Crear test_openai_client.py | 🔴 CORE | 2h | Tests para OpenAIClient con API mocked | Task 2 |
| 9 | Crear test_end_to_end.py | 🔴 CORE | 4h | Test workflow completo con todas las fases | Tasks 3-8 |
| 10 | Ejecutar coverage y fix gaps | 🔴 CORE | 2h | 80% coverage alcanzado | Task 9 |
| 11 | Manual testing checklist (MCP Inspector) | 🔴 CORE | 1.5h | 6 tools validados, checklist documentado | Task 9 |
| 12 | Manual testing checklist (Claude Code) | 🔴 CORE | 0.5h | Integration con Claude Code verificada | Task 11 |
| 13 | Crear test_performance.py | 🟡 Enhanced | 3h | Benchmarks documentados (embeddings, search, pipeline) | Task 9 |
| 14 | Ampliar error scenarios | 🟡 Enhanced | 3h | Tests para 5+ escenarios de error | Task 9 |
| 15 | Crear smoke test checklist para PR | 🟡 Enhanced | 1h | Checklist markdown documentado | Task 10 |

**Orden Sugerido de Implementación:**
1. Setup (Tasks 1-2): 1.5h
2. Unit Tests Batch 1 (Tasks 3-5): 4.5h
3. Unit Tests Batch 2 (Tasks 6-8): 7h
4. Integration (Task 9): 4h
5. Coverage & Manual (Tasks 10-12): 4h
6. Enhanced (Tasks 13-15): 7h *(opcional)*

**Total Core: 21h | Total Enhanced: 7h**

---

## 5. Plan de Pruebas

### 5.1 Estrategia de Testing

**Niveles de testing:**
1. **Unit Tests**: Componentes individuales aislados con mocks
2. **Integration Tests**: Interacción entre componentes (end-to-end)
3. **Manual Tests**: Validación en MCP Inspector y Claude Code
4. **Performance Tests**: Benchmarks de operaciones críticas *(Enhanced)*

### 5.2 Unit Tests - Cobertura por Módulo

#### test_models.py

**Objetivo**: Validar modelos Pydantic (Paper, SearchParams, SearchSession, etc.)

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

### 5.3 Integration Test End-to-End

#### test_end_to_end.py

**Objetivo**: Validar workflow completo del MCP server

```python
async def test_full_workflow_with_mocks():
    """
    Test completo del workflow:
    1. generate_search_keywords (mock OpenAI)
    2. search_papers (debug mode o mock httpx)
    3. download_papers (mock PDFs)
    4. index_papers (real embeddings pero dataset pequeño)
    5. query_papers (mock OpenAI answer generation)

    Verificar:
    - Session creada correctamente
    - PDFs descargados a directorio correcto
    - Chunks indexados en ChromaDB
    - Query devuelve answer con sources
    - Metadata preservation en todo el pipeline
    """

    # 1. Generate keywords
    # 2. Search papers
    # 3. Download papers
    # 4. Index papers
    # 5. Query papers
    # 6. List sessions

    # Assertions
    assert session_id is not None
    assert download_result["downloaded"] > 0
    assert index_result["chunks_created"] > 0
    assert len(query_result["answer"]) > 0
    assert len(query_result["sources"]) > 0
```

**Estrategia de mocking:**
- OpenAI API: siempre mocked
- httpx requests: usar debug mode (web.archive.org) o mock
- PDFs: crear fixtures pequeños o mock downloads
- ChromaDB: usar in-memory si posible
- Filesystem: usar tmp_path fixture

---

### 5.4 Manual Testing Checklist - MCP Inspector

**Prerequisito:** `npm install -g @modelcontextprotocol/inspector`

**Comando:** `mcp inspect uv run sortgs-mcp`

**Tests a ejecutar:**

| # | Tool | Input | Expected Output | Status |
|---|------|-------|-----------------|--------|
| 1 | `generate_search_keywords` | `{"query": "transformers NLP", "num_variations": 3}` | 3 keywords distintos | ⬜ |
| 2 | `search_papers` | `{"keywords": "deep learning", "num_results": 10}` | session_id, 10 papers | ⬜ |
| 3 | `download_papers` | `{"session_id": "<from step 2>", "max_papers": 3}` | 3 PDFs descargados (algunos pueden fallar) | ⬜ |
| 4 | `index_papers` | `{"session_id": "<from step 2>"}` | chunks_created > 0 | ⬜ |
| 5 | `query_papers` | `{"question": "What is deep learning?", "session_id": "<from step 2>"}` | answer con citations | ⬜ |
| 6 | `list_sessions` | `{}` | Lista con session de step 2 | ⬜ |

**Documentación de resultados:**
- Crear archivo `docs/MANUAL_TESTING_RESULTS.md`
- Capturar screenshots de MCP Inspector
- Documentar errores encontrados
- Verificar logs en `sortgs_mcp.log`

---

### 5.5 Manual Testing Checklist - Claude Code Integration

**Prerequisito:** Configurar MCP server en Claude Code

```bash
claude mcp add --transport stdio sortgs-mcp -- uv run sortgs-mcp
```

**Tests a ejecutar:**

| # | Acción | Validación | Status |
|---|--------|-----------|--------|
| 1 | Verificar server aparece en `claude mcp list` | sortgs-mcp listed | ⬜ |
| 2 | En chat: "Generate keywords for transformers" | Claude invoca tool correctamente | ⬜ |
| 3 | En chat: "Search for deep learning papers" | Session creada, papers encontrados | ⬜ |
| 4 | En chat: "Download PDFs from session X" | PDFs descargados | ⬜ |
| 5 | En chat: "Index the papers from session X" | Indexing completo | ⬜ |
| 6 | En chat: "What is attention mechanism?" | RAG answer con sources | ⬜ |
| 7 | Verificar logs en `sortgs_mcp.log` | Logs legibles, sin errores críticos | ⬜ |
| 8 | Test error handling: invalid session | Error message claro y útil | ⬜ |

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
```

---

### 5.7 Coverage Goals

**Baseline (antes de Fase 8):** ~50-60% (estimado, basado en tests existentes)

**Meta MVP:** 80% total coverage

**Prioridad de coverage por módulo:**
- 🔴 **Critical (90%+)**: models.py, core/parser.py, core/session.py
- 🟡 **High (85%+)**: core/scholar.py, tools/*, llm/openai.py
- 🟢 **Medium (75%+)**: rag/*, pdf/*, config.py
- ⚪ **Low (60%+)**: server.py (principalmente boilerplate)

**Comandos útiles:**

```bash
# Coverage básico
uv run pytest --cov=sortgs_mcp --cov-report=term

# Coverage con HTML (visual)
uv run pytest --cov=sortgs_mcp --cov-report=html
# Abrir htmlcov/index.html en browser

# Coverage con gaps específicos
uv run pytest --cov=sortgs_mcp --cov-report=term-missing

# Coverage solo para módulo específico
uv run pytest tests/test_models.py --cov=sortgs_mcp.models --cov-report=term

# Coverage incremental (solo archivos modificados)
uv run pytest --cov=sortgs_mcp --cov-report=term --cov-branch

# Coverage con markers
uv run pytest -m "unit" --cov=sortgs_mcp --cov-report=term
```

**Interpretación de resultados:**
- `Stmts`: Número total de líneas ejecutables
- `Miss`: Líneas no cubiertas por tests
- `Cover`: Porcentaje de cobertura
- Buscar líneas críticas sin coverage (error handling, edge cases)

---

## 6. Contingencia y Riesgos

### Escenarios de Bloqueo

#### 1. **Coverage no alcanza 80%**
- **Probabilidad**: Media
- **Impacto**: Alto (criterio de éxito MVP)
- **Mitigación proactiva**:
  - Ejecutar coverage report después de cada batch de tests
  - Identificar módulos con bajo coverage early
  - Priorizar tests que aumenten coverage más rápido
- **Plan B**:
  - Si coverage queda en 75-79%, identificar las líneas críticas faltantes
  - Añadir tests específicos para error handling (suele faltar coverage)
  - Aceptar 75% si las líneas faltantes son edge cases no críticos
- **Punto de decisión**: Después de Task 10, si coverage < 75%, añadir 2h para tests adicionales

#### 2. **Test end-to-end falla por dependencias externas**
- **Probabilidad**: Media
- **Impacto**: Alto
- **Mitigación proactiva**:
  - Usar debug mode (`--debug` flag) que usa web.archive.org
  - Mocks comprehensivos para OpenAI y httpx
  - Fixtures estáticos siempre que sea posible
- **Plan B**:
  - Separar en múltiples integration tests más pequeños
  - Test cada fase del workflow independientemente primero
  - Usar solo fixtures para test end-to-end si red falla
- **Alternativa**: Si Google Scholar bloquea, documentar y usar solo tests con fixtures

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
- Resultado: 80% coverage, tests core, manual checklist MCP Inspector

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

**Si NO a cualquiera:**
- Evaluar recorte de scope Enhanced
- Priorizar end-to-end sobre performance
- Simplificar fixtures si están tomando mucho tiempo
- Comunicar ajustes al stakeholder

---

## 7. Entregables

### MVP (CORE)

1. **6 archivos de tests nuevos:**
   - `tests/test_models.py` (~100-150 líneas)
   - `tests/test_parser.py` (~150-200 líneas)
   - `tests/test_scholar.py` (~200-250 líneas)
   - `tests/test_session.py` (~150-200 líneas)
   - `tests/test_openai_client.py` (~150-200 líneas)
   - `tests/test_end_to_end.py` (~200-300 líneas)

2. **Configuración de coverage:**
   - pytest-cov instalado (`uv add --dev pytest-cov`)
   - `pyproject.toml` configurado con [tool.pytest.ini_options]
   - Coverage report HTML generado en `htmlcov/`

3. **Fixtures compartidos:**
   - `tests/conftest.py` con fixtures reusables
   - `tests/fixtures/scholar_page.html` (snapshot Google Scholar)
   - `tests/fixtures/mock_responses.py` (datos de prueba)

4. **Manual testing documentation:**
   - Checklist MCP Inspector ejecutado (6 tools validados)
   - Checklist Claude Code ejecutado (8 validaciones)
   - Resultados documentados en `docs/MANUAL_TESTING_RESULTS.md`

5. **Coverage report:**
   - HTML report en `htmlcov/index.html`
   - Terminal report mostrando 80%+ coverage
   - Identificación de gaps críticos (si coverage < 80%)

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

---

### 8.2 Task 2: Crear conftest.py (1h)

**Archivo:** `tests/conftest.py`

```python
"""Shared pytest fixtures for sortgs_mcp tests."""

import pytest
from datetime import datetime
from pathlib import Path
from sortgs_mcp.models import Paper, SearchParams, SearchSession
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
```

**Criterio de aceptación:**
- ✅ Fixtures compilables y usables
- ✅ Tests existentes pueden importar fixtures
- ✅ Datos de prueba realistas

---

### 8.3 Task 3: Crear test_models.py (2h)

**Archivo:** `tests/test_models.py`

```python
"""Unit tests for sortgs_mcp.models."""

import pytest
from pydantic import ValidationError
from datetime import datetime
from sortgs_mcp.models import (
    Paper,
    SearchParams,
    SearchSession,
    PDFDownloadResult,
    DownloadMetadata,
    QueryResult,
    QuerySource
)


class TestPaper:
    """Test Paper model validation."""

    def test_paper_creation_valid(self, sample_paper):
        """Test creating a valid Paper instance."""
        assert sample_paper.rank == 1
        assert sample_paper.title == "Attention Is All You Need"
        assert sample_paper.citations == 50000
        assert sample_paper.cit_per_year == 6250.0

    def test_paper_validation_missing_required_fields(self):
        """Test Paper validation fails with missing required fields."""
        with pytest.raises(ValidationError):
            Paper(rank=1)  # Missing required fields

    def test_paper_optional_fields_none(self):
        """Test Paper with optional fields as None."""
        paper = Paper(
            rank=1,
            title="Test Paper",
            authors="Author",
            citations=100,
            year=2020,
            publisher="",
            venue="",
            content_snippet="",
            source_url="http://example.com",
            pdf_url=None,  # Optional
            cit_per_year=0.0
        )
        assert paper.pdf_url is None

    def test_paper_serialization(self, sample_paper):
        """Test Paper serialization to dict."""
        data = sample_paper.model_dump()
        assert data["rank"] == 1
        assert data["title"] == "Attention Is All You Need"
        assert "pdf_url" in data


class TestSearchParams:
    """Test SearchParams model validation."""

    def test_search_params_defaults(self):
        """Test SearchParams with default values."""
        params = SearchParams(keywords="test")
        assert params.num_results == 100
        assert params.sort_by == "Citations"
        assert params.start_year is None
        assert params.end_year is None
        assert params.languages is None
        assert params.debug is False

    def test_search_params_year_validation(self):
        """Test year validation (must be positive)."""
        # Valid years
        params = SearchParams(keywords="test", start_year=2000, end_year=2024)
        assert params.start_year == 2000

        # Invalid year (negative)
        with pytest.raises(ValidationError):
            SearchParams(keywords="test", start_year=-1)

    def test_search_params_sort_by_literal(self):
        """Test sort_by accepts only valid literals."""
        # Valid
        params1 = SearchParams(keywords="test", sort_by="Citations")
        params2 = SearchParams(keywords="test", sort_by="cit/year")

        # Invalid
        with pytest.raises(ValidationError):
            SearchParams(keywords="test", sort_by="invalid")

    def test_search_params_num_results_bounds(self):
        """Test num_results validation (10-1000)."""
        # Valid
        params = SearchParams(keywords="test", num_results=50)
        assert params.num_results == 50

        # Too low
        with pytest.raises(ValidationError):
            SearchParams(keywords="test", num_results=5)

        # Too high
        with pytest.raises(ValidationError):
            SearchParams(keywords="test", num_results=2000)


class TestSearchSession:
    """Test SearchSession model."""

    def test_search_session_serialization(self, sample_session):
        """Test SearchSession serialization."""
        data = sample_session.model_dump()
        assert "session_id" in data
        assert "created_at" in data
        assert "params" in data
        assert "papers" in data

    def test_search_session_json_roundtrip(self, sample_session):
        """Test JSON serialization and deserialization."""
        json_str = sample_session.model_dump_json()
        loaded = SearchSession.model_validate_json(json_str)

        assert loaded.session_id == sample_session.session_id
        assert loaded.papers_count == sample_session.papers_count
        assert len(loaded.papers) == len(sample_session.papers)


class TestPDFDownloadResult:
    """Test PDFDownloadResult model."""

    def test_pdf_download_result_counts(self):
        """Test PDFDownloadResult with counts."""
        result = PDFDownloadResult(
            session_id="test-123",
            downloaded=5,
            skipped=2,
            failed=1,
            pdf_paths=["path1.pdf", "path2.pdf"],
            failed_papers=[],
            metadata=[]
        )
        assert result.downloaded == 5
        assert result.skipped == 2
        assert result.failed == 1


class TestQueryResult:
    """Test QueryResult model."""

    def test_query_result_with_sources(self):
        """Test QueryResult with sources."""
        source = QuerySource(
            paper_title="Test Paper",
            chunk_text="Sample chunk text...",
            relevance_score=0.95,
            metadata={"year": 2020}
        )

        result = QueryResult(
            question="What is X?",
            answer="X is...",
            sources=[source],
            session_id="test-123"
        )

        assert result.question == "What is X?"
        assert len(result.sources) == 1
        assert result.sources[0].relevance_score == 0.95
```

**Criterio de aceptación:**
- ✅ Tests pasan para todos los modelos
- ✅ Validación Pydantic funciona correctamente
- ✅ Serialization/deserialization funciona

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

#### Temporary Directories
```python
def test_session_creation(tmp_path):
    session_manager = SessionManager(data_dir=tmp_path)
    session_id = session_manager.create_session(params)

    # Verificar directorio creado
    session_dir = tmp_path / "sessions" / session_id
    assert session_dir.exists()
    assert (session_dir / "pdfs").exists()
```

---

## 9. Checklist Final

### Pre-Implementation
- [ ] pytest-cov instalado
- [ ] conftest.py creado
- [ ] Fixtures HTML preparados
- [ ] Baseline coverage medido

### Unit Tests
- [ ] test_models.py completo y pasando
- [ ] test_parser.py completo y pasando
- [ ] test_scholar.py completo y pasando
- [ ] test_session.py completo y pasando
- [ ] test_openai_client.py completo y pasando

### Integration Tests
- [ ] test_end_to_end.py completo y pasando
- [ ] Workflow completo funciona (keywords → query)

### Coverage
- [ ] Coverage report generado
- [ ] 80%+ coverage alcanzado
- [ ] Gaps críticos identificados y documentados

### Manual Testing
- [ ] MCP Inspector instalado
- [ ] 6 tools validados en Inspector
- [ ] Claude Code integration probada
- [ ] Resultados documentados

### Enhanced (Opcional)
- [ ] test_performance.py creado
- [ ] Benchmarks documentados
- [ ] Error scenarios cubiertos
- [ ] Smoke test checklist creado

### Documentation
- [ ] MANUAL_TESTING_RESULTS.md creado
- [ ] Coverage report en htmlcov/
- [ ] PERFORMANCE_BASELINE.md (si Enhanced)
- [ ] SMOKE_TESTS.md (si Enhanced)

---

## 10. Resumen Ejecutivo de Entrega

**Objetivo:** Suite de tests comprehensiva con 80% coverage

**Entregables Core (MVP):**
1. 6 archivos de tests nuevos (~1000 líneas código)
2. Coverage report HTML con 80%+ coverage
3. Fixtures compartidos en conftest.py
4. Manual testing checklists ejecutados
5. Documentación de resultados

**Entregables Enhanced (Opcional):**
6. Performance benchmarks
7. Error scenarios tests
8. Smoke test checklist

**Tiempo estimado:**
- MVP: 16-18 horas
- Enhanced: +7-8 horas
- **Total: 23-26 horas**

**Criterios de éxito:**
- ✅ 100% tests pasando
- ✅ 80%+ code coverage
- ✅ Test end-to-end exitoso
- ✅ Manual checklist completado

**Riesgos principales:**
- Coverage difícil de alcanzar (mitigación: priorizar módulos críticos)
- Test end-to-end falla (mitigación: usar debug mode + mocks)
- Performance tests lentos (mitigación: datasets pequeños, marcar @slow)

**Punto de decisión GO/NO-GO:** Después de unit tests (10h), evaluar si MVP es alcanzable.

---

**FIN DEL WORKPLAN**
