# WORKPLAN: FASE 9 - DOCUMENTACIÓN Y PULIDO (Revisión 2)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **ID de Tarea** | task-10-fase-9 |
| **Título** | Fase 9: Docs & Polish - Documentación y mejoras UX |
| **Fecha Creación** | 2025-12-30 |
| **Versión** | 1.2 (rev-2) |
| **Estado** | Pendiente Aprobación |
| **Autor** | Claude (Coordinador de Planificación) |
| **Fase MCP_PLAN** | Fase 9 (Final) |
| **Stack** | Python, Markdown, MCP, OpenAI API, ChromaDB |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Planificación Fase 9 | Usuario |
| 1.1 (rev-1) | 2025-12-30 | Mejoras aplicadas post-revisión con codex | Incorporar sugerencias de análisis automatizado: validación de dependencias, tests automáticos para cambios funcionales, aclaración de integración MCP+RAG, mejora de dependencias entre tareas | Usuario + Codex |
| 1.2 (rev-2) | 2025-12-30 | Segunda iteración de mejoras con codex | Alinear dependencias MVP/Enhanced (promover logging a MVP), endurecer criterios MCP+RAG, formalizar testabilidad y Click | Usuario + Codex |

---

## 1. Resumen Ejecutivo

### Descripción General
La Fase 9 es la fase final del proyecto MCP sortgs. Su objetivo es **pulir el proyecto para producción** mediante documentación comprehensiva, mejoras de experiencia de usuario, optimizaciones de rendimiento, y herramientas de gestión. Esta fase NO incluye desarrollo de features nuevas, sino refinamiento de lo existente.

### Alcance
- **Documentación completa**: README actualizado, TROUBLESHOOTING, CONTRIBUTING, ejemplos de uso
- **Mejoras UX**: Error messages claros, logging estructurado, degradación elegante
- **Optimizaciones**: Connection pooling, cache de embeddings, tuning de ChromaDB
- **Tooling**: Script CLI de gestión (`scripts/manage.py`)
- **Calidad**: Revisión de docstrings, type hints, secrets, ejemplos funcionales

### Objetivos
1. Hacer el proyecto **fácil de adoptar** para nuevos usuarios (README, ejemplos)
2. Hacer el proyecto **fácil de debuggear** (logging, troubleshooting)
3. Hacer el proyecto **fácil de contribuir** (CONTRIBUTING, code quality)
4. Hacer el proyecto **production-ready** (error handling, performance)

### Componentes MCP Afectados
- **Documentación**: README.md, nuevos docs, ejemplos
- **Server**: Logging mejorado (server.py)
- **Config**: Tuning de performance (config.py)
- **Tools**: Error messages mejorados (search.py, download.py, index.py, query.py)
- **Core**: Connection pooling (scholar.py) - YA IMPLEMENTADO
- **RAG**: Cache de embeddings (embeddings.py) - YA IMPLEMENTADO

### Referencia a MCP_PLAN.md
Esta tarea implementa la **Fase 9: Docs & Polish** (líneas 1815-2053) del archivo `MCP_PLAN.md`.

---

## 2. Priorización del Alcance (ACTUALIZADO REV-2)

### MVP/CORE (Obligatorio)
**Criterio de éxito**: Usuario puede instalar, configurar y usar el MCP server sin fricción. Problemas comunes están documentados.

**Componentes obligatorios**:
1. **README actualizado** con sección MCP Server completa
   - Instalación y setup
   - Documentación de las 6 herramientas MCP
   - Ejemplo de workflow básico
2. **TROUBLESHOOTING.md** con problemas conocidos
   - Google Scholar robot check
   - PDF download failures
   - OpenAI API errors
   - **NUEVO**: Embedding model "already initialized" error
3. **examples/mcp_config.json** funcional
4. **Mejora de error messages** en tools (mensajes claros + hints)
5. **Revisión final** de docstrings y type hints en funciones públicas
6. **Logging estructurado** (PROMOVIDO DE ENHANCED) ⬆️
   - Todos los tools usan `extra={}` con contexto
   - Necesario para documentar formato de logs en TROUBLESHOOTING

**Por qué es core**: Sin documentación clara y logging consistente, el proyecto es inusable para usuarios externos y difícil de debuggear.

### Enhanced (Opcional - Alta Prioridad)
**Componentes opcionales deseables**:
1. **CONTRIBUTING.md** con guía de desarrollo
2. **examples/workflow_example.md** con caso de uso completo paso a paso
3. **scripts/manage.py** CLI helper para gestión de sesiones
4. **Optimizaciones de rendimiento**:
   - Connection pooling en httpx - **YA IMPLEMENTADO** ✅
   - Cache del modelo de embeddings (singleton) - **YA IMPLEMENTADO** ✅

**Por qué es enhanced**: Mejoran significativamente la experiencia pero el sistema funciona sin ellos.

### Nice-to-Have (Futuro)
**Componentes diferibles**:
1. ChromaDB index tuning (HNSW params)
2. Log rotation automática
3. Progress bars en downloads/indexing
4. Telemetry/metrics dashboard

**Por qué es futuro**: No impactan la usabilidad actual. Pueden añadirse en releases posteriores.

### Plan de Reducción de Alcance
Si falta tiempo, recortar en este orden:
1. **Primero**: Nice-to-Have completo (ChromaDB tuning, log rotation, progress bars)
2. **Segundo**: Scripts de management (scripts/manage.py) - se puede usar Python REPL
3. **Tercero**: CONTRIBUTING.md - sustituir con sección básica en README
4. **Último (no recortar)**: README, TROUBLESHOOTING, error messages, docstrings, **logging estructurado**

**Core inamovible** (ACTUALIZADO): README actualizado + TROUBLESHOOTING + error messages mejorados + **logging estructurado**.

---

## 3. Diseño Técnico

### Arquitectura Propuesta
No hay cambios de arquitectura. Esta fase es **refinamiento sobre infraestructura existente**.

### Componentes Afectados

#### 1. Documentación (Archivos nuevos)
```
/
├── README.md (actualizar)
├── TROUBLESHOOTING.md (crear)
├── CONTRIBUTING.md (crear)
├── examples/
│   ├── mcp_config.json (crear)
│   └── workflow_example.md (crear)
└── scripts/
    └── manage.py (crear)
```

#### 2. Código (Mejoras incrementales)
- `src/sortgs_mcp/server.py`: Logging mejorado (líneas 28-56)
- `src/sortgs_mcp/config.py`: Tuning defaults si necesario
- `src/sortgs_mcp/tools/*.py`: Error messages claros + logging estructurado
- `src/sortgs_mcp/core/scholar.py`: Connection pooling - **YA USA context manager** ✅ (líneas 59-66)
- `src/sortgs_mcp/rag/embeddings.py`: Singleton pattern - **YA IMPLEMENTADO** ✅ (líneas 67-79)

### Decisiones Técnicas (KISS) - Validadas

#### Decisión 1: README Structure
**Opción elegida**: Mantener README.md único con sección MCP expandida.

**Alternativas consideradas**:
- Crear README_MCP.md separado ❌
- Split en docs/ folder ❌

**Justificación**: Un README único es más fácil de descubrir. Los usuarios buscan primero README.md. Mantener KISS.

**Referencias al código actual**: README.md ya existe (líneas 1-179), sección MCP en líneas 11-46.

#### Decisión 2: Error Messages Format
**Opción elegida**: Error messages con hint contextual inline.

**Formato**:
```python
raise ValueError(
    f"Session '{session_id}' not found. "
    f"Available sessions: {list_sessions()}. "
    f"Hint: Use list_sessions tool to see all sessions."
)
```

**Justificación**: Usuario ve problema + solución en un solo mensaje. No necesita buscar docs.

**Referencias al código actual**:
- `src/sortgs_mcp/tools/search.py:79-83` - Ya usa este patrón
- `src/sortgs_mcp/tools/download.py` - A mejorar
- `src/sortgs_mcp/tools/index.py` - A mejorar
- `src/sortgs_mcp/tools/query.py` - A mejorar

#### Decisión 3: Logging Strategy
**Opción elegida**: Structured logging con `extra={}` dict.

**Patrón**:
```python
logger.info(
    "Downloading PDF",
    extra={
        "session_id": session_id,
        "paper_rank": paper.rank,
        "paper_title": paper.title[:50]
    }
)
```

**Justificación**: Compatible con logging actual. Permite parseo automático para dashboards futuros. No requiere librerías adicionales (structlog).

**Referencias al código actual**:
- `src/sortgs_mcp/tools/search.py:35-38` - Ya usa `extra={}`
- `src/sortgs_mcp/rag/embeddings.py:24-27` - Ya usa `extra={}`
- Otros tools y módulos - A actualizar para consistencia

#### Decisión 4: Connection Pooling ✅ YA IMPLEMENTADO
**Opción elegida**: Reutilizar httpx.AsyncClient en ScholarSearcher mediante context manager.

**Estado actual**: **Ya implementado correctamente** ✅

**Referencias al código actual**:
- `src/sortgs_mcp/core/scholar.py:59-66` - Context manager `__aenter__` y `__aexit__`
- `src/sortgs_mcp/core/scholar.py:68-74` - Método `_make_client()` crea AsyncClient con configuración
- `src/sortgs_mcp/tools/search.py:55` - Uso: `async with ScholarSearcher(debug=debug) as searcher`

**Acción**: Solo documentar en README y verificar en tests.

#### Decisión 5: Embeddings Cache ✅ YA IMPLEMENTADO
**Opción elegida**: Singleton global con lazy loading y thread-safe lock.

**Estado actual**: **Ya implementado correctamente** ✅

**Referencias al código actual**:
- `src/sortgs_mcp/rag/embeddings.py:12-14` - Variables globales con lock
- `src/sortgs_mcp/rag/embeddings.py:67-79` - Función `get_embedding_service()` con thread lock
- Protección contra cambio de modelo (líneas 74-78)

**Acción**: Solo documentar comportamiento y verificar en tests.

**Consideraciones de concurrencia**:
- Lock de threading protege inicialización
- Una vez creado, el servicio es inmutable y thread-safe para lectura
- Cambio de modelo genera ValueError (no permite múltiples modelos)
- En entorno async, el lock de threading es suficiente (no hay race conditions en inicialización)

#### Decisión 6: Script de Gestión (ACTUALIZADO REV-2)
**Opción elegida**: Click CLI en scripts/manage.py con verificación y fallback.

**Estado de dependencia**: ✅ Click ya disponible (v8.3.1) como dependencia indirecta

**Verificación**:
- `pyproject.toml` - Click NO está listado explícitamente
- `uv pip list` - Click 8.3.1 está instalado (dependencia indirecta de chromadb o mcp)

**Análisis de riesgo**:
- ⚠️ **Riesgo**: Click podría desaparecer si chromadb/mcp cambian dependencias
- ✅ **Mitigación A (recomendada)**: Añadir Click explícitamente a `[dependency-groups] dev` en pyproject.toml
- ✅ **Mitigación B (fallback)**: Agregar check en manage.py con mensaje claro si Click no disponible

**Implementación recomendada**:
1. Añadir `click>=8.0` a `[dependency-groups] dev` en pyproject.toml
2. En `scripts/manage.py`, añadir try/except al import:
```python
try:
    import click
except ImportError:
    print("Error: Click is required for manage.py")
    print("Install with: uv add --dev click")
    print("Alternative: Use Python REPL to manage sessions")
    sys.exit(1)
```

**Alternativa (si Click falla)**: Usar argparse (stdlib) - no requiere dependencias pero menos ergonómico.

**Justificación**: Click ofrece mejor UX con menos código. Añadirlo explícitamente a dev dependencies elimina el riesgo de dependencias indirectas.

---

## 4. Plan de Desarrollo (ACTUALIZADO REV-2)

### Tareas Detalladas

| # | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Bloqueadores | Esfuerzo |
|---|-------|-----------|-------------------------|--------------|--------------|----------|
| 1 | Actualizar README.md - Sección MCP | MVP | Contiene: instalación, setup OpenAI, las 6 tools documentadas, ejemplo básico | Ninguna | - | 1.5h |
| 2 | Crear examples/mcp_config.json | MVP | JSON válido, funciona con claude mcp add | Ninguna | - | 0.5h |
| 3 | Mejorar error messages en tools | MVP | Todos los ValueError/RuntimeError tienen hint contextual; tests verifican hints | Ninguna | - | 1h |
| 4 | Revisar docstrings y type hints | MVP | Todas las funciones públicas tienen docstring + types | Ninguna | - | 1h |
| 5 | Implementar logging estructurado | **MVP** ⬆️ | Todos los loggers usan extra={} con contexto; tests verifican formato | Ninguna | - | 1h |
| 6 | Crear TROUBLESHOOTING.md | **MVP** | Contiene: robot check, PDF failures, API errors, embedding error, **formato de logs** | **Tarea 5** | Logging debe estar documentado | 1h |
| 7 | Crear CONTRIBUTING.md | Enhanced | Contiene: setup dev, tests, code style | Ninguna | - | 0.5h |
| 8 | Crear examples/workflow_example.md | Enhanced | Workflow completo documentado paso a paso | Tarea 1 | README debe estar completo | 1h |
| 9 | Documentar connection pooling ✅ | Enhanced | README documenta uso de context manager; tests verifican reuso de client | Ninguna | - | 0.25h |
| 10 | Documentar embeddings cache ✅ | Enhanced | README documenta singleton; tests verifican cache funciona | Ninguna | - | 0.25h |
| 11 | Crear scripts/manage.py CLI | Enhanced | Comandos: list-sessions, delete-session, clean-data; Click explícito en deps | Ninguna | Click debe estar en pyproject.toml | 1.5h |
| 12 | Tests para manage.py | Enhanced | pytest para CLI commands | Tarea 11 | - | 0.5h |
| 13 | Tests para logging estructurado | **MVP** ⬆️ | Verificar extra={} en logs capturados; **incluir checks de isolation MCP** | Tarea 5 | - | 0.5h |
| 14 | Tests para error messages | MVP | Verificar hints en excepciones | Tarea 3 | - | 0.5h |
| 15 | Tests para connection pooling | Enhanced | Verificar reuso de httpx client con **mocks** | Tarea 9 | - | 0.5h |
| 16 | Tests para embeddings cache | Enhanced | Verificar singleton, thread-safety con **mocks/skip si requiere red** | Tarea 10 | - | 0.5h |

**Total estimado** (ACTUALIZADO):
- **MVP**: 6h (aumentó +1h por logging estructurado)
- **Enhanced**: 5.5h (disminuyó -1h)
- **Total completo**: 11.5h (sin cambio)

### Orden Sugerido de Implementación (ACTUALIZADO REV-2)

#### Sprint 1: Documentación Core + Logging (MVP) - 6h
1. Crear examples/mcp_config.json (0.5h)
2. Actualizar README.md con sección MCP (1.5h)
3. Mejorar error messages en tools (1h)
4. **Implementar logging estructurado** (1h) - **PROMOVIDO A SPRINT 1** ⬆️
5. Revisar docstrings y type hints (1h)
6. **Crear TROUBLESHOOTING.md** (1h) - **AHORA POSIBLE** (desbloqueado por Tarea 5)
7. **Tests para logging estructurado** (0.5h) - **AÑADIDO A SPRINT 1**
8. **Tests para error messages** (0.5h) - **AÑADIDO A SPRINT 1**

**Checkpoint**: Usuario puede instalar y usar MCP server sin fricción. Logging consistente permite troubleshooting efectivo.

#### Sprint 2: Documentación Enhanced (Opcional) - 2.5h
9. Crear CONTRIBUTING.md (0.5h)
10. Crear examples/workflow_example.md (1h)
11. Documentar connection pooling (0.25h)
12. Documentar embeddings cache (0.25h)

**Checkpoint**: Proyecto listo para contribuidores externos con documentación completa.

#### Sprint 3: Performance & Tooling (Opcional) - 3h
13. Añadir Click a pyproject.toml dev deps (0.1h)
14. Crear scripts/manage.py CLI con verificación de Click (1.4h)
15. Tests para manage.py (0.5h)
16. Tests para connection pooling con mocks (0.5h)
17. Tests para embeddings cache con mocks (0.5h)

**Checkpoint**: Performance documentada, herramientas de gestión disponibles, tests completos.

---

## 5. Plan de Pruebas (ACTUALIZADO REV-2)

### Estrategia de Testing

#### Unit Tests (AMPLIADO)
**Scope**: Scripts de management + cambios funcionales + **isolation MCP+RAG**

**Estrategia de mocking** (NUEVO):
- **Preferir mocks en CI**: Tests deben ejecutar rápido sin dependencias externas
- **Permitir tests de integración opcionales**: Usar marcadores pytest para tests que requieren red/modelo real
- **Skip automático si falta dependencia**: Tests de manage.py skip si Click no disponible

**Nuevos archivos de tests**:

1. **`tests/test_manage_cli.py`** (Tarea 12)
```python
import pytest

try:
    import click
    CLICK_AVAILABLE = True
except ImportError:
    CLICK_AVAILABLE = False

@pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not installed")
def test_list_sessions_command():
    """Test that list-sessions command works."""
    # Implementar

@pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not installed")
def test_delete_session_command():
    """Test that delete-session command works."""
    # Implementar

@pytest.mark.skipif(not CLICK_AVAILABLE, reason="Click not installed")
def test_clean_data_command():
    """Test that clean-data requires confirmation."""
    # Implementar
```

2. **`tests/test_logging_structured.py`** (Tarea 13 - AHORA MVP)
```python
def test_search_tool_uses_structured_logging(caplog):
    """Verify search_papers uses extra={} in logs."""
    # Capturar logs y verificar que 'keywords' y 'num_results' están en extra
    # Implementar

def test_download_tool_uses_structured_logging(caplog):
    """Verify download_papers uses extra={} in logs."""
    # Implementar

def test_index_tool_uses_structured_logging(caplog):
    """Verify index_papers uses extra={} in logs."""
    # Implementar

# NUEVO: Checks de isolation MCP+RAG
def test_list_sessions_returns_valid_metadata():
    """Verify list_sessions devuelve sesiones activas con metadata correcta."""
    # Implementar: crear sesión, listar, verificar formato JSON y campos requeridos

async def test_query_papers_session_isolation():
    """Verify query_papers en sesión aislada no ve colecciones de otras sesiones."""
    # Implementar: crear 2 sesiones, indexar en cada una, query en sesión 1 no debe retornar chunks de sesión 2
```

3. **`tests/test_error_messages.py`** (Tarea 14 - AHORA MVP)
```python
def test_search_tool_error_has_hint():
    """Verify ValueError from search_papers includes helpful hint."""
    # Trigger error con keywords vacíos
    # Verificar que mensaje incluye "Hint:"
    # Implementar

def test_download_tool_session_not_found_has_hint():
    """Verify download_papers error for missing session includes hint."""
    # Implementar

def test_index_tool_error_has_hint():
    """Verify index_papers errors include hints."""
    # Implementar

# NUEVO: Verificar JSON válido
async def test_all_mcp_tools_return_valid_json():
    """Verify todas las MCP tools retornan JSON válido y schemas correctos."""
    # Implementar: invocar cada tool, validar que retorno es dict serializable a JSON
```

4. **`tests/test_connection_pooling.py`** (Tarea 15)
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_scholar_searcher_reuses_client():
    """Verify ScholarSearcher context manager creates single AsyncClient (MOCKED)."""
    # ESTRATEGIA: Usar mock para httpx.AsyncClient para evitar red
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value = mock_instance

        async with ScholarSearcher(debug=True) as searcher:
            client_id = id(searcher._client)
            # Simular múltiples búsquedas
            # Verificar que client_id no cambia

        # Verificar que aclose() fue llamado
        mock_instance.aclose.assert_called_once()

@pytest.mark.integration  # Marcar como integration test (requiere red)
@pytest.mark.skipif(os.getenv("CI"), reason="Skip integration tests in CI")
async def test_scholar_searcher_real_network():
    """Integration test: verify pooling works with real network (OPCIONAL)."""
    # Implementar test real si se desea validar comportamiento en entorno real
```

5. **`tests/test_embeddings_cache.py`** (Tarea 16)
```python
from unittest.mock import MagicMock, patch

def test_get_embedding_service_returns_singleton():
    """Verify get_embedding_service returns same instance (MOCKED)."""
    # ESTRATEGIA: Mockear SentenceTransformer para evitar descargar modelo real
    with patch('sentence_transformers.SentenceTransformer') as mock_st:
        mock_st.return_value = MagicMock()

        service1 = get_embedding_service("all-mpnet-base-v2")
        service2 = get_embedding_service("all-mpnet-base-v2")
        assert service1 is service2

def test_get_embedding_service_different_model_raises():
    """Verify requesting different model raises ValueError (MOCKED)."""
    with patch('sentence_transformers.SentenceTransformer') as mock_st:
        mock_st.return_value = MagicMock()

        get_embedding_service("all-mpnet-base-v2")
        with pytest.raises(ValueError, match="already initialized"):
            get_embedding_service("different-model")

def test_embedding_service_thread_safety():
    """Verify singleton is thread-safe during initialization (MOCKED)."""
    # Test con threading.Thread, mockear SentenceTransformer
    # Implementar

@pytest.mark.integration
@pytest.mark.skipif(os.getenv("CI"), reason="Skip model download in CI")
def test_embedding_service_real_model():
    """Integration test: verify cache with real model (OPCIONAL)."""
    # Solo ejecutar si se quiere validar con modelo real
```

#### Integration Tests
**Scope**: No aplica (no hay nueva lógica de negocio core)

#### Manual Testing (Smoke Test Checklist)

**Pre-requisitos**:
- [ ] OpenAI API key configurada en .env
- [ ] Proyecto instalado con `uv sync`

**Checklist de Validación Manual**:

1. **Documentación**:
   - [ ] README.md renderiza correctamente en GitHub
   - [ ] Todas las secciones MCP están completas
   - [ ] Ejemplos de código en README ejecutan sin errores
   - [ ] TROUBLESHOOTING.md cubre los 4 problemas principales (robot, PDF, API, embedding)
   - [ ] TROUBLESHOOTING.md documenta formato de logs estructurados
   - [ ] examples/mcp_config.json es JSON válido
   - [ ] CONTRIBUTING.md existe (si Enhanced implementado)

2. **MCP Configuration**:
   - [ ] `claude mcp add` funciona con examples/mcp_config.json
   - [ ] MCP server inicia sin errores: `uv run sortgs-mcp`
   - [ ] Logs aparecen en data/logs/sortgs_mcp.log

3. **Error Messages**:
   - [ ] Tool con session_id inválido muestra hint útil
   - [ ] Tool sin OpenAI API key muestra error claro
   - [ ] Error de Google Scholar robot check tiene solución sugerida

4. **Logging**:
   - [ ] Logs incluyen contexto (session_id, paper_rank, etc.) vía extra={}
   - [ ] Log level configurable via .env funciona
   - [ ] Logs no contienen secrets (API keys, tokens)

5. **MCP+RAG Isolation (NUEVO)**:
   - [ ] `list_sessions` devuelve sesiones activas con metadata correcta (session_id, keywords, papers_count)
   - [ ] `query_papers` en sesión aislada no ve colecciones de otras sesiones
   - [ ] Todas las MCP tools retornan JSON válido (serializable, sin errores de encoding)

6. **Performance (si Enhanced)**:
   - [ ] Múltiples búsquedas reutilizan httpx client (verificar en logs o tests)
   - [ ] Embedding model se carga solo una vez (verificar en logs)
   - [ ] Connection pooling funciona correctamente

7. **Management CLI (si Enhanced)**:
   - [ ] Click está en `[dependency-groups] dev` de pyproject.toml
   - [ ] `python scripts/manage.py list-sessions` funciona
   - [ ] `python scripts/manage.py delete-session <id>` borra sesión
   - [ ] `python scripts/manage.py clean-data` pide confirmación
   - [ ] Si Click falta, script muestra mensaje claro con instrucciones

8. **Code Quality**:
   - [ ] No warnings de mypy (type hints correctos)
   - [ ] Todas las funciones públicas tienen docstrings
   - [ ] No secrets hardcodeados en código
   - [ ] .gitignore actualizado (no commiteamos .env, logs)

9. **Tests Automáticos (ACTUALIZADO)**:
   - [ ] `uv run pytest tests/test_logging_structured.py -v` pasa (MVP)
   - [ ] `uv run pytest tests/test_error_messages.py -v` pasa (MVP)
   - [ ] `uv run pytest tests/test_manage_cli.py -v` pasa (Enhanced, skip si no Click)
   - [ ] `uv run pytest tests/test_connection_pooling.py -v` pasa con mocks (Enhanced)
   - [ ] `uv run pytest tests/test_embeddings_cache.py -v` pasa con mocks (Enhanced)
   - [ ] Tests de integration (marcados) se pueden ejecutar opcionalmente con `pytest -m integration`

**Ejecutar tests completos**:
```bash
# Tests MVP (sin mocks opcionales)
uv run pytest tests/test_logging_structured.py tests/test_error_messages.py -v

# Tests Enhanced (con mocks)
uv run pytest tests/test_manage_cli.py tests/test_connection_pooling.py tests/test_embeddings_cache.py -v

# Todos los tests (skip integration)
uv run pytest -m "not integration" -v

# Tests de integration (opcional, requiere red/modelo)
uv run pytest -m integration -v
```

### Criterios de Éxito (ACTUALIZADO REV-2)

**MVP (mínimo aceptable)**:
- [ ] README actualizado y completo
- [ ] TROUBLESHOOTING existe con 4 problemas + formato de logs
- [ ] Error messages tienen hints útiles
- [ ] Docstrings en funciones públicas
- [ ] **Logging estructurado implementado** (extra={} en todos los tools)
- [ ] **Tests de logging pasan** (verifican extra={} y isolation)
- [ ] **Tests de error messages pasan**
- [ ] **Checks MCP+RAG**: list_sessions retorna metadata correcta, query aislado, JSON válido
- [ ] Smoke test checklist 100% pass (secciones 1-5)

**Enhanced (ideal)**:
- [ ] Todo lo de MVP
- [ ] CONTRIBUTING existe
- [ ] workflow_example.md funciona
- [ ] Performance documentada (connection pool + cache ya implementados)
- [ ] **Click añadido explícitamente a dev deps**
- [ ] scripts/manage.py funciona con verificación de Click
- [ ] Tests automáticos para pooling y cache pasan (con mocks)
- [ ] Smoke test checklist 100% pass (todas las secciones)

---

## 6. Plan de Contingencia

### Escenarios de Riesgo

#### Riesgo 1: Tiempo insuficiente
**Probabilidad**: Media
**Impacto**: Medio

**Plan de mitigación**:
1. Implementar solo Sprint 1 (MVP) - 6h (incluye logging + TROUBLESHOOTING)
2. Diferir Enhanced a release posterior
3. Core inamovible: README + logging + TROUBLESHOOTING + error messages + docstrings

**Punto de decisión**: Al terminar Sprint 1, evaluar tiempo restante.

#### Riesgo 2: Documentación demasiado extensa
**Probabilidad**: Alta
**Impacto**: Bajo

**Plan de mitigación**:
1. Mantener README conciso (< 300 líneas)
2. Enlazar a docs externos para detalles
3. Priorizar ejemplos sobre explicaciones largas

#### Riesgo 3: Scripts de management complejos
**Probabilidad**: Baja
**Impacto**: Bajo

**Plan de mitigación**:
1. Reducir comandos a lo esencial (list, delete, clean)
2. No implementar comandos avanzados (backup, restore)
3. Si toma > 2h, diferir a Nice-to-Have

#### Riesgo 4: Click no disponible o inestable (MITIGADO REV-2)
**Probabilidad**: Muy Baja (mitigado)
**Impacto**: Bajo

**Plan de mitigación** (ACTUALIZADO):
1. ✅ Añadir Click explícitamente a `[dependency-groups] dev` (elimina dependencia indirecta)
2. ✅ Verificación en manage.py con mensaje claro si falta
3. ✅ Alternativa documentada: usar argparse (stdlib) si es necesario

### Recortes Priorizados

**Si falta 50% tiempo**:
- ❌ Scripts de management completo
- ❌ workflow_example.md
- ❌ Tests automáticos para performance
- ✅ Mantener MVP completo (incluye logging + TROUBLESHOOTING)

**Si falta 30% tiempo**:
- ❌ Scripts de management completo
- ❌ Tests automáticos para performance
- ✅ Mantener resto Enhanced

**Si falta 10% tiempo**:
- Mantener todo, reducir profundidad de ejemplos

### Core Inamovible (ACTUALIZADO REV-2)

No recortar bajo ninguna circunstancia:
1. README.md actualizado con sección MCP
2. **Logging estructurado en todos los tools** (promovido a core)
3. **TROUBLESHOOTING.md con formato de logs documentado**
4. Error messages mejorados en tools
5. Docstrings en funciones públicas
6. examples/mcp_config.json

---

## 7. Consideraciones Adicionales

### Dependencias Externas (ACTUALIZADO REV-2)
- **Click** (para scripts/manage.py):
  - **Acción**: Añadir explícitamente a `[dependency-groups] dev` como `click>=8.0`
  - **Estado actual**: Disponible como indirecta (v8.3.1)
  - **Justificación**: Eliminar riesgo de pérdida por cambios en chromadb/mcp

### Integración MCP+RAG: Comportamiento con Concurrencia

#### Múltiples Sesiones Concurrentes
**Escenario**: Múltiples usuarios/clientes invocan MCP tools simultáneamente.

**Análisis**:
- **SessionManager**: Cada sesión tiene UUID único, operaciones de I/O son independientes
- **ScholarSearcher**: Context manager crea client por invocación, no hay conflicto
- **EmbeddingService**: Singleton thread-safe, lecturas paralelas son seguras
- **ChromaDB**: Una collection por sesión (isolation), queries concurrentes soportadas

**Conclusión**: ✅ Diseño soporta múltiples sesiones concurrentes sin issues

#### Múltiples Modelos de Embeddings
**Escenario**: Usuario intenta cambiar modelo de embeddings durante ejecución.

**Análisis actual**:
- `get_embedding_service()` lanza `ValueError` si modelo cambia (líneas 74-78)
- Esto previene inconsistencia pero es inflexible

**Implicaciones**:
- ✅ Ventaja: Previene bugs por modelos mixtos en vector store
- ❌ Limitación: No permite experimentar con modelos diferentes
- ⚠️ Workaround: Usuario debe reiniciar MCP server para cambiar modelo

**Documentación requerida**:
- README debe mencionar que cambio de modelo requiere restart
- TROUBLESHOOTING debe incluir error "already initialized with X"

#### Sincronización del Singleton en Entorno Async
**Análisis**:
- `threading.Lock` protege inicialización (líneas 12, 70)
- Una vez creado, `_SERVICE_INSTANCE` es inmutable (solo lectura)
- `SentenceTransformer.encode()` es thread-safe según documentación

**Conclusión**: ✅ Implementación actual es correcta para async + threads

### Impacto en Tests Existentes
- No hay cambios breaking
- Tests existentes deben seguir pasando
- Solo añadir nuevos tests (logging, errors, manage.py, performance con mocks)

### Documentación de APIs
- Todas las 6 tools MCP deben tener docstring completo
- Formato: descripción, args, returns, example

### Consideraciones de Seguridad
- Verificar que logs no exponen API keys
- Verificar que .gitignore incluye .env, logs/, data/
- Verificar que ejemplos no incluyen secrets reales

---

## 8. Anexos

### A. Checklist de Calidad Final

Antes de considerar Fase 9 completada:

**Código**:
- [ ] No hay TODOs o FIXMEs en código crítico
- [ ] Todas las funciones públicas tienen type hints
- [ ] Todas las funciones públicas tienen docstrings
- [ ] No hay secrets hardcodeados
- [ ] .gitignore completo
- [ ] **Logging estructurado implementado en todos los tools** (extra={})

**Documentación**:
- [ ] README.md actualizado y completo
- [ ] README documenta connection pooling (context manager)
- [ ] README documenta embeddings cache (singleton + limitación de modelo único)
- [ ] TROUBLESHOOTING.md existe con 4 problemas + **formato de logs**
- [ ] examples/ funciona
- [ ] CONTRIBUTING.md existe (si Enhanced)

**Testing**:
- [ ] `uv run pytest` pasa 100%
- [ ] Tests nuevos añadidos: **logging (MVP)**, **errors (MVP)**, manage.py, pooling (mocks), cache (mocks)
- [ ] **Tests verifican isolation MCP+RAG** (sesiones, JSON válido)
- [ ] Smoke test manual pasa 100%
- [ ] No warnings en logs durante tests

**Performance**:
- [ ] Connection pooling documentado (ya implementado) ✅
- [ ] Embeddings cache documentado (ya implementado) ✅
- [ ] Tests verifican reuso de client y singleton (con mocks)
- [ ] No memory leaks evidentes

**Dependencies**:
- [ ] Click añadido explícitamente a `[dependency-groups] dev`

### B. Template para TROUBLESHOOTING.md (ACTUALIZADO REV-2)

```markdown
# Troubleshooting

## Google Scholar Robot Check

**Problem**: `search_papers` fails with "Robot check detected"

**Symptoms**: Error message mentions CAPTCHA or robot verification

**Solutions**:
1. Reduce `num_results` to < 50
2. Use `debug=True` flag (uses web archive)
3. Wait 15+ minutes before retrying
4. Use VPN if repeated failures

## PDF Download Failures

**Problem**: `download_papers` reports failed downloads

**Symptoms**: Some PDFs in failed_papers list

**Solutions**:
1. Check if PDF URL is valid (some papers don't have PDFs)
2. Retry with different papers
3. Check network connectivity
4. Some publishers block automated downloads

## OpenAI API Errors

**Problem**: Tools fail with OpenAI API error

**Symptoms**: Error mentions "API key" or "rate limit"

**Solutions**:
1. Verify OPENAI_API_KEY in .env
2. Check API key is valid on OpenAI dashboard
3. Check API usage limits
4. Wait if rate limited

## Embedding Model Already Initialized

**Problem**: `index_papers` fails with "EmbeddingService already initialized with X"

**Symptoms**: Error when trying to use different embedding model

**Explanation**:
The embedding service uses a singleton pattern. Once initialized with a model,
it cannot be changed during the same MCP server session to prevent inconsistencies
in the vector store.

**Solutions**:
1. Restart the MCP server to change embedding models
2. Use the same model across all indexing operations
3. If you need multiple models, use separate MCP server instances

## Understanding Log Format (NUEVO)

**Log Structure**: All MCP tools use structured logging with contextual metadata.

**Example log entry**:
```
2025-12-30 10:30:45 - sortgs_mcp.tools.search - INFO - search_papers called
Extra context: {'keywords': 'machine learning', 'num_results': 100}
```

**What to look for**:
- **Timestamp**: When the operation occurred
- **Module**: Which tool/component logged the message
- **Level**: INFO (normal), WARNING (attention needed), ERROR (failed)
- **Extra context**: Additional metadata (session_id, paper_rank, etc.)

**Common log patterns**:
- Search operations log: keywords, num_results
- Download operations log: session_id, paper_rank, paper_title
- Indexing operations log: batch_size, total_texts

**Troubleshooting with logs**:
1. Check `data/logs/sortgs_mcp.log` for detailed operations
2. Look for ERROR level messages
3. Use extra context to trace specific sessions or operations
```

### C. Template para CONTRIBUTING.md

```markdown
# Contributing

## Development Setup

```bash
# Clone repo
git clone https://github.com/WittmannF/sort-google-scholar.git
cd sort-google-scholar

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"

# Configure OpenAI
cp .env.example .env
# Edit .env to add OPENAI_API_KEY
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sortgs_mcp

# Run specific test file
uv run pytest tests/test_search.py -v

# Run new tests for Fase 9
uv run pytest tests/test_logging_structured.py -v  # MVP
uv run pytest tests/test_error_messages.py -v      # MVP
uv run pytest tests/test_connection_pooling.py -v  # Enhanced (mocks)
uv run pytest tests/test_embeddings_cache.py -v    # Enhanced (mocks)
uv run pytest tests/test_manage_cli.py -v          # Enhanced (skip if no Click)

# Run only unit tests (skip integration)
uv run pytest -m "not integration" -v

# Run integration tests (optional, requires network/model)
uv run pytest -m integration -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small (< 50 lines)
- Prefer simple over clever

## Logging Guidelines (NUEVO)

All MCP tools should use structured logging:

```python
logger.info(
    "Operation description",
    extra={
        "session_id": session_id,
        "key_param": value,
        # Add relevant context
    }
)
```

## Performance Considerations

### Connection Pooling
ScholarSearcher uses `httpx.AsyncClient` context manager to reuse connections:

```python
async with ScholarSearcher(debug=False) as searcher:
    papers = await searcher.search(params)
# Client is automatically closed on exit
```

### Embeddings Cache
The embedding service uses a singleton pattern. Call `get_embedding_service(model_name)`
to get the cached instance. Note: changing models requires restarting the server.
```

### D. Referencias de Código Verificadas

| Componente | Archivo | Líneas | Estado |
|------------|---------|--------|--------|
| Connection Pooling | `src/sortgs_mcp/core/scholar.py` | 59-66 | ✅ Implementado |
| Embeddings Cache | `src/sortgs_mcp/rag/embeddings.py` | 67-79 | ✅ Implementado |
| Structured Logging | `src/sortgs_mcp/tools/search.py` | 35-38 | ✅ Ejemplo existente |
| Structured Logging | `src/sortgs_mcp/rag/embeddings.py` | 24-27, 52-57 | ✅ Ejemplo existente |
| Error Messages | `src/sortgs_mcp/tools/search.py` | 79-83 | ✅ Patrón existente |
| Click Dependency | `uv pip list` | - | ✅ Disponible (8.3.1) |
| Logging Setup | `src/sortgs_mcp/server.py` | 28-56 | ✅ Ya configurado |

### E. Cambios en pyproject.toml (NUEVO REV-2)

**Añadir a `[dependency-groups] dev`**:
```toml
[dependency-groups]
dev = [
    "pytest>=9.0.2",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=6.0.0",
    "reportlab>=4.4.4",
    "click>=8.0",  # NUEVO: Añadir explícitamente para scripts/manage.py
]
```

**Justificación**: Click es actualmente dependencia indirecta, pero añadirlo explícitamente garantiza disponibilidad futura.

---

## FIN DEL WORKPLAN REVISIÓN 2
