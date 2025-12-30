# WORKPLAN: FASE 9 - DOCUMENTACIÓN Y PULIDO (Revisión 1)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **ID de Tarea** | task-10-fase-9 |
| **Título** | Fase 9: Docs & Polish - Documentación y mejoras UX |
| **Fecha Creación** | 2025-12-30 |
| **Versión** | 1.1 (rev-1) |
| **Estado** | Pendiente Aprobación |
| **Autor** | Claude (Coordinador de Planificación) |
| **Fase MCP_PLAN** | Fase 9 (Final) |
| **Stack** | Python, Markdown, MCP, OpenAI API, ChromaDB |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Planificación Fase 9 | Usuario |
| 1.1 (rev-1) | 2025-12-30 | Mejoras aplicadas post-revisión con codex | Incorporar sugerencias de análisis automatizado: validación de dependencias, tests automáticos para cambios funcionales, aclaración de integración MCP+RAG, mejora de dependencias entre tareas | Usuario + Codex |

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

## 2. Priorización del Alcance

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
3. **examples/mcp_config.json** funcional
4. **Mejora de error messages** en tools (mensajes claros + hints)
5. **Revisión final** de docstrings y type hints en funciones públicas

**Por qué es core**: Sin documentación clara, el proyecto es inusable para usuarios externos.

### Enhanced (Opcional - Alta Prioridad)
**Componentes opcionales deseables**:
1. **CONTRIBUTING.md** con guía de desarrollo
2. **examples/workflow_example.md** con caso de uso completo paso a paso
3. **scripts/manage.py** CLI helper para gestión de sesiones
4. **Logging mejorado** (structured logging con contexto rico)
5. **Optimizaciones de rendimiento**:
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
4. **Último (no recortar)**: README, TROUBLESHOOTING, error messages, docstrings

**Core inamovible**: README actualizado + TROUBLESHOOTING + error messages mejorados.

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
- `src/sortgs_mcp/tools/*.py`: Error messages claros
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

#### Decisión 6: Script de Gestión
**Opción elegida**: Click CLI en scripts/manage.py.

**Estado de dependencia**: ✅ Click ya disponible

**Verificación**:
- `pyproject.toml` - Click NO está listado explícitamente
- `uv pip list` - Click 8.3.1 está instalado (dependencia indirecta de chromadb o mcp)

**Justificación**: Click ya está disponible como dependencia indirecta. Sintaxis declarativa y fácil de extender.

**Acción**:
1. Verificar en qué dependencia viene Click (chromadb o mcp)
2. Si es estable, usarlo directamente
3. Si no, añadir explícitamente a `[dependency-groups] dev`

---

## 4. Plan de Desarrollo

### Tareas Detalladas (ACTUALIZADO)

| # | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Bloqueadores | Esfuerzo |
|---|-------|-----------|-------------------------|--------------|--------------|----------|
| 1 | Actualizar README.md - Sección MCP | MVP | Contiene: instalación, setup OpenAI, las 6 tools documentadas, ejemplo básico | Ninguna | - | 1.5h |
| 2 | Crear TROUBLESHOOTING.md | MVP | Contiene: robot check, PDF failures, API errors, soluciones | Tarea 8 (logging) | Logging debe estar documentado | 1h |
| 3 | Crear examples/mcp_config.json | MVP | JSON válido, funciona con claude mcp add | Ninguna | - | 0.5h |
| 4 | Mejorar error messages en tools | MVP | Todos los ValueError/RuntimeError tienen hint contextual; tests verifican hints | Ninguna | - | 1h |
| 5 | Revisar docstrings y type hints | MVP | Todas las funciones públicas tienen docstring + types | Ninguna | - | 1h |
| 6 | Crear CONTRIBUTING.md | Enhanced | Contiene: setup dev, tests, code style | Ninguna | - | 0.5h |
| 7 | Crear examples/workflow_example.md | Enhanced | Workflow completo documentado paso a paso | Tarea 1 | README debe estar completo | 1h |
| 8 | Implementar logging estructurado | Enhanced | Todos los loggers usan extra={} con contexto; tests verifican formato | Ninguna | - | 1h |
| 9 | Documentar connection pooling ✅ | Enhanced | README documenta uso de context manager; tests verifican reuso de client | Ninguna | - | 0.25h |
| 10 | Documentar embeddings cache ✅ | Enhanced | README documenta singleton; tests verifican cache funciona | Ninguna | - | 0.25h |
| 11 | Crear scripts/manage.py CLI | Enhanced | Comandos: list-sessions, delete-session, clean-data | Ninguna | Verificar Click disponible | 1.5h |
| 12 | Tests para manage.py | Enhanced | pytest para CLI commands | Tarea 11 | - | 0.5h |
| 13 | Tests para logging estructurado | Enhanced | Verificar extra={} en logs capturados | Tarea 8 | - | 0.5h |
| 14 | Tests para error messages | Enhanced | Verificar hints en excepciones | Tarea 4 | - | 0.5h |
| 15 | Tests para connection pooling | Enhanced | Verificar reuso de httpx client | Tarea 9 | - | 0.5h |
| 16 | Tests para embeddings cache | Enhanced | Verificar singleton, thread-safety | Tarea 10 | - | 0.5h |

**Total estimado**:
- MVP: 5h
- Enhanced: 6.5h (aumentó por tests automáticos)
- **Total completo**: 11.5h

### Orden Sugerido de Implementación

#### Sprint 1: Documentación Core (MVP) - 5h
1. Crear examples/mcp_config.json (0.5h)
2. Actualizar README.md con sección MCP (1.5h)
3. Mejorar error messages en tools (1h)
4. Revisar docstrings y type hints (1h)
5. **BLOQUEADO**: Crear TROUBLESHOOTING.md - esperar a Sprint 2 tarea 8

**Checkpoint**: Usuario puede instalar y usar MCP server sin fricción (excepto TROUBLESHOOTING pendiente).

#### Sprint 2: Documentación Enhanced + Tests (Opcional) - 4.5h
6. Implementar logging estructurado (1h) - **DESBLOQUEA Tarea 2**
7. Crear TROUBLESHOOTING.md (1h) - ahora desbloqueado
8. Crear CONTRIBUTING.md (0.5h)
9. Crear examples/workflow_example.md (1h) - **REQUIERE Tarea 1 completada**
10. Tests para logging estructurado (0.5h)
11. Tests para error messages (0.5h)

**Checkpoint**: Proyecto listo para contribuidores externos con cobertura de tests.

#### Sprint 3: Performance & Tooling (Opcional) - 2h
12. Documentar connection pooling (0.25h)
13. Documentar embeddings cache (0.25h)
14. Crear scripts/manage.py CLI (1.5h) - verificar Click primero
15. Tests para manage.py (0.5h)
16. Tests para connection pooling (0.5h)
17. Tests para embeddings cache (0.5h)

**Checkpoint**: Performance documentada, herramientas de gestión disponibles, tests completos.

---

## 5. Plan de Pruebas (ACTUALIZADO)

### Estrategia de Testing

#### Unit Tests (AMPLIADO)
**Scope**: Scripts de management + cambios funcionales

**Nuevos archivos de tests**:

1. **`tests/test_manage_cli.py`** (Tarea 12)
```python
def test_list_sessions_command():
    """Test that list-sessions command works."""
    # Implementar

def test_delete_session_command():
    """Test that delete-session command works."""
    # Implementar

def test_clean_data_command():
    """Test that clean-data requires confirmation."""
    # Implementar
```

2. **`tests/test_logging_structured.py`** (Tarea 13)
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
```

3. **`tests/test_error_messages.py`** (Tarea 14)
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
```

4. **`tests/test_connection_pooling.py`** (Tarea 15)
```python
async def test_scholar_searcher_reuses_client():
    """Verify ScholarSearcher context manager creates single AsyncClient."""
    async with ScholarSearcher(debug=True) as searcher:
        client_id_1 = id(searcher._client)
        # Simular múltiples búsquedas
        # Verificar que client_id no cambia
    # Implementar

async def test_scholar_searcher_closes_client():
    """Verify AsyncClient is properly closed on exit."""
    # Implementar con mock
```

5. **`tests/test_embeddings_cache.py`** (Tarea 16)
```python
def test_get_embedding_service_returns_singleton():
    """Verify get_embedding_service returns same instance."""
    service1 = get_embedding_service("all-mpnet-base-v2")
    service2 = get_embedding_service("all-mpnet-base-v2")
    assert service1 is service2
    # Implementar

def test_get_embedding_service_different_model_raises():
    """Verify requesting different model raises ValueError."""
    get_embedding_service("all-mpnet-base-v2")
    with pytest.raises(ValueError, match="already initialized"):
        get_embedding_service("different-model")
    # Implementar

def test_embedding_service_thread_safety():
    """Verify singleton is thread-safe during initialization."""
    # Test con threading.Thread
    # Implementar
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
   - [ ] TROUBLESHOOTING.md cubre los 3 problemas principales
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

5. **Performance (si Enhanced)**:
   - [ ] Múltiples búsquedas reutilizan httpx client (verificar en logs o tests)
   - [ ] Embedding model se carga solo una vez (verificar en logs)
   - [ ] Connection pooling funciona correctamente

6. **Management CLI (si Enhanced)**:
   - [ ] `python scripts/manage.py list-sessions` funciona
   - [ ] `python scripts/manage.py delete-session <id>` borra sesión
   - [ ] `python scripts/manage.py clean-data` pide confirmación

7. **Code Quality**:
   - [ ] No warnings de mypy (type hints correctos)
   - [ ] Todas las funciones públicas tienen docstrings
   - [ ] No secrets hardcodeados en código
   - [ ] .gitignore actualizado (no commiteamos .env, logs)

8. **Tests Automáticos**:
   - [ ] `uv run pytest tests/test_manage_cli.py -v` pasa
   - [ ] `uv run pytest tests/test_logging_structured.py -v` pasa
   - [ ] `uv run pytest tests/test_error_messages.py -v` pasa
   - [ ] `uv run pytest tests/test_connection_pooling.py -v` pasa
   - [ ] `uv run pytest tests/test_embeddings_cache.py -v` pasa

**Ejecutar tests completos**:
```bash
uv run pytest tests/test_manage_cli.py tests/test_logging_structured.py tests/test_error_messages.py tests/test_connection_pooling.py tests/test_embeddings_cache.py -v
```

### Criterios de Éxito (ACTUALIZADO)

**MVP (mínimo aceptable)**:
- [ ] README actualizado y completo
- [ ] TROUBLESHOOTING existe con 3+ problemas
- [ ] Error messages tienen hints útiles
- [ ] Docstrings en funciones públicas
- [ ] Smoke test checklist 100% pass (secciones 1-4)

**Enhanced (ideal)**:
- [ ] Todo lo de MVP
- [ ] CONTRIBUTING existe
- [ ] workflow_example.md funciona
- [ ] Logging estructurado implementado
- [ ] Performance documentada (connection pool + cache ya implementados)
- [ ] scripts/manage.py funciona
- [ ] Tests automáticos para logging, errors, pooling, cache pasan
- [ ] Smoke test checklist 100% pass (todas las secciones)

---

## 6. Plan de Contingencia

### Escenarios de Riesgo

#### Riesgo 1: Tiempo insuficiente
**Probabilidad**: Media
**Impacto**: Medio

**Plan de mitigación**:
1. Implementar solo Sprint 1 (MVP) - 5h (TROUBLESHOOTING diferido)
2. Diferir Enhanced a release posterior
3. Core inamovible: README + error messages + docstrings

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

#### Riesgo 4: Click no disponible o inestable (NUEVO)
**Probabilidad**: Baja
**Impacto**: Medio

**Plan de mitigación**:
1. Verificar que Click viene de chromadb o mcp (dependencias estables)
2. Si no es estable, añadir Click explícitamente a dev dependencies
3. Como última opción, usar argparse (stdlib) en lugar de Click

### Recortes Priorizados

**Si falta 50% tiempo**:
- ❌ Scripts de management completo
- ❌ workflow_example.md
- ❌ Tests automáticos para performance
- ✅ Mantener MVP completo (sin TROUBLESHOOTING si falta logging)

**Si falta 30% tiempo**:
- ❌ Scripts de management completo
- ❌ Tests automáticos para performance
- ✅ Mantener resto Enhanced

**Si falta 10% tiempo**:
- Mantener todo, reducir profundidad de ejemplos

### Core Inamovible

No recortar bajo ninguna circunstancia:
1. README.md actualizado con sección MCP
2. Error messages mejorados en tools
3. Docstrings en funciones públicas
4. examples/mcp_config.json

Diferible solo si tiempo crítico:
5. TROUBLESHOOTING.md (requiere logging completado primero)

---

## 7. Consideraciones Adicionales

### Dependencias Externas (ACTUALIZADO)
- **Click** (para scripts/manage.py): ✅ Ya disponible como dependencia indirecta
  - Verificado: Click 8.3.1 instalado vía chromadb o mcp
  - Acción: Confirmar estabilidad antes de usar

### Integración MCP+RAG: Comportamiento con Concurrencia (NUEVO)

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
- Solo añadir nuevos tests (manage.py, logging, errors, performance)

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

**Documentación**:
- [ ] README.md actualizado y completo
- [ ] README documenta connection pooling (context manager)
- [ ] README documenta embeddings cache (singleton + limitación de modelo único)
- [ ] TROUBLESHOOTING.md existe con error "already initialized"
- [ ] examples/ funciona
- [ ] CONTRIBUTING.md existe (si Enhanced)

**Testing**:
- [ ] `uv run pytest` pasa 100%
- [ ] Tests nuevos añadidos: logging, errors, pooling, cache, manage.py
- [ ] Smoke test manual pasa 100%
- [ ] No warnings en logs durante tests

**Performance**:
- [ ] Connection pooling documentado (ya implementado) ✅
- [ ] Embeddings cache documentado (ya implementado) ✅
- [ ] Tests verifican reuso de client y singleton
- [ ] No memory leaks evidentes

### B. Template para TROUBLESHOOTING.md (ACTUALIZADO)

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
uv run pytest tests/test_logging_structured.py -v
uv run pytest tests/test_error_messages.py -v
uv run pytest tests/test_connection_pooling.py -v
uv run pytest tests/test_embeddings_cache.py -v
uv run pytest tests/test_manage_cli.py -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small (< 50 lines)
- Prefer simple over clever

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

---

## FIN DEL WORKPLAN REVISIÓN 1
