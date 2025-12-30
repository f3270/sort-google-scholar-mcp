# WORKPLAN: FASE 9 - DOCUMENTACIÓN Y PULIDO

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **ID de Tarea** | task-10-fase-9 |
| **Título** | Fase 9: Docs & Polish - Documentación y mejoras UX |
| **Fecha Creación** | 2025-12-30 |
| **Versión** | 1.0 |
| **Estado** | Pendiente Aprobación |
| **Autor** | Claude (Coordinador de Planificación) |
| **Fase MCP_PLAN** | Fase 9 (Final) |
| **Stack** | Python, Markdown, MCP, OpenAI API, ChromaDB |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-30 | Versión inicial | Planificación Fase 9 | Usuario |

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
- **Core**: Connection pooling (scholar.py), cache de embeddings (embeddings.py)

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
   - Connection pooling en httpx
   - Cache del modelo de embeddings (singleton)

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
- `src/sortgs_mcp/server.py`: Logging mejorado
- `src/sortgs_mcp/config.py`: Tuning defaults
- `src/sortgs_mcp/tools/*.py`: Error messages claros
- `src/sortgs_mcp/core/scholar.py`: Connection pooling
- `src/sortgs_mcp/rag/embeddings.py`: Singleton pattern

### Decisiones Técnicas (KISS)

#### Decisión 1: README Structure
**Opción elegida**: Mantener README.md único con sección MCP expandida.

**Alternativas consideradas**:
- Crear README_MCP.md separado ❌
- Split en docs/ folder ❌

**Justificación**: Un README único es más fácil de descubrir. Los usuarios buscan primero README.md. Mantener KISS.

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

#### Decisión 4: Connection Pooling
**Opción elegida**: Reutilizar httpx.AsyncClient en ScholarSearcher mediante context manager.

**Implementación**:
```python
class ScholarSearcher:
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30, limits=httpx.Limits(max_connections=10))
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()
```

**Justificación**: Ya existe pattern de context manager en el código. No requiere cambios en callers.

#### Decisión 5: Embeddings Cache
**Opción elegida**: Singleton global con lazy loading.

**Implementación**:
```python
_embedding_service_instance = None

def get_embedding_service(model_name: str) -> EmbeddingService:
    global _embedding_service_instance
    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService(model_name)
    return _embedding_service_instance
```

**Justificación**: Modelo pesa ~400MB. Cargar una vez ahorra RAM y tiempo. Pattern común en ML applications.

#### Decisión 6: Script de Gestión
**Opción elegida**: Click CLI en scripts/manage.py.

**Justificación**: Click ya es dependencia indirecta (via otras libs). Sintaxis declarativa y fácil de extender.

---

## 4. Plan de Desarrollo

### Tareas Detalladas

| # | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|---|-------|-----------|-------------------------|--------------|----------|
| 1 | Actualizar README.md - Sección MCP | MVP | Contiene: instalación, setup OpenAI, las 6 tools documentadas, ejemplo básico | Ninguna | 1.5h |
| 2 | Crear TROUBLESHOOTING.md | MVP | Contiene: robot check, PDF failures, API errors, soluciones | Ninguna | 1h |
| 3 | Crear examples/mcp_config.json | MVP | JSON válido, funciona con claude mcp add | Ninguna | 0.5h |
| 4 | Mejorar error messages en tools | MVP | Todos los ValueError/RuntimeError tienen hint contextual | Ninguna | 1h |
| 5 | Revisar docstrings y type hints | MVP | Todas las funciones públicas tienen docstring + types | Ninguna | 1h |
| 6 | Crear CONTRIBUTING.md | Enhanced | Contiene: setup dev, tests, code style | Ninguna | 0.5h |
| 7 | Crear examples/workflow_example.md | Enhanced | Workflow completo documentado paso a paso | Tarea 1 | 1h |
| 8 | Implementar logging estructurado | Enhanced | Todos los loggers usan extra={} con contexto | Ninguna | 1h |
| 9 | Implementar connection pooling | Enhanced | ScholarSearcher reutiliza httpx client | Ninguna | 0.5h |
| 10 | Implementar embeddings cache | Enhanced | Singleton para EmbeddingService | Ninguna | 0.5h |
| 11 | Crear scripts/manage.py CLI | Enhanced | Comandos: list-sessions, delete-session, clean-data | Ninguna | 1.5h |
| 12 | Tests para manage.py | Enhanced | pytest para CLI commands | Tarea 11 | 0.5h |

**Total estimado**:
- MVP: 5h
- Enhanced: 5.5h
- **Total completo**: 10.5h

### Orden Sugerido de Implementación

#### Sprint 1: Documentación Core (MVP) - 5h
1. Crear TROUBLESHOOTING.md (1h)
2. Crear examples/mcp_config.json (0.5h)
3. Actualizar README.md con sección MCP (1.5h)
4. Mejorar error messages en tools (1h)
5. Revisar docstrings y type hints (1h)

**Checkpoint**: Usuario puede instalar y usar MCP server sin fricción.

#### Sprint 2: Documentación Enhanced (Opcional) - 2.5h
6. Crear CONTRIBUTING.md (0.5h)
7. Crear examples/workflow_example.md (1h)
8. Implementar logging estructurado (1h)

**Checkpoint**: Proyecto listo para contribuidores externos.

#### Sprint 3: Performance & Tooling (Opcional) - 3h
9. Implementar connection pooling (0.5h)
10. Implementar embeddings cache (0.5h)
11. Crear scripts/manage.py CLI (1.5h)
12. Tests para manage.py (0.5h)

**Checkpoint**: Performance optimizada y herramientas de gestión disponibles.

---

## 5. Plan de Pruebas

### Estrategia de Testing

#### Unit Tests
**Scope**: Scripts de management (manage.py)
- Test list_sessions command
- Test delete_session command
- Test clean_data command

#### Integration Tests
**Scope**: No aplica (no hay nueva lógica de negocio)

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
   - [ ] Logs incluyen contexto (session_id, paper_rank, etc.)
   - [ ] Log level configurable via .env funciona
   - [ ] Logs no contienen secrets (API keys, tokens)

5. **Performance (si Enhanced)**:
   - [ ] Múltiples búsquedas no crean múltiples httpx clients
   - [ ] Embedding model se carga solo una vez
   - [ ] Connection pooling funciona (verificar en logs)

6. **Management CLI (si Enhanced)**:
   - [ ] `python scripts/manage.py list-sessions` funciona
   - [ ] `python scripts/manage.py delete-session <id>` borra sesión
   - [ ] `python scripts/manage.py clean-data` pide confirmación

7. **Code Quality**:
   - [ ] No warnings de mypy (type hints correctos)
   - [ ] Todas las funciones públicas tienen docstrings
   - [ ] No secrets hardcodeados en código
   - [ ] .gitignore actualizado (no commiteamos .env, logs)

### Tests Automatizados Nuevos

**Archivo**: `tests/test_manage_cli.py`

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

**Ejecutar tests**:
```bash
uv run pytest tests/test_manage_cli.py -v
```

### Criterios de Éxito

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
- [ ] Performance optimizada (connection pool + cache)
- [ ] scripts/manage.py funciona
- [ ] Smoke test checklist 100% pass (todas las secciones)

---

## 6. Plan de Contingencia

### Escenarios de Riesgo

#### Riesgo 1: Tiempo insuficiente
**Probabilidad**: Media
**Impacto**: Medio

**Plan de mitigación**:
1. Implementar solo Sprint 1 (MVP) - 5h
2. Diferir Enhanced a release posterior
3. Core inamovible: README + TROUBLESHOOTING + error messages

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

### Recortes Priorizados

**Si falta 50% tiempo**:
- ❌ Scripts de management completo
- ❌ workflow_example.md
- ✅ Mantener MVP completo

**Si falta 30% tiempo**:
- ❌ Scripts de management completo
- ✅ Mantener resto Enhanced

**Si falta 10% tiempo**:
- Mantener todo, reducir profundidad de ejemplos

### Core Inamovible

No recortar bajo ninguna circunstancia:
1. README.md actualizado con sección MCP
2. TROUBLESHOOTING.md con problemas comunes
3. Error messages mejorados en tools
4. Docstrings en funciones públicas

---

## 7. Consideraciones Adicionales

### Dependencias Externas
- Click (para scripts/manage.py) - ya está disponible como dependencia indirecta

### Impacto en Tests Existentes
- No hay cambios breaking
- Tests existentes deben seguir pasando
- Solo añadir tests para manage.py

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
- [ ] TROUBLESHOOTING.md existe
- [ ] examples/ funciona
- [ ] CONTRIBUTING.md existe (si Enhanced)

**Testing**:
- [ ] `uv run pytest` pasa 100%
- [ ] Smoke test manual pasa 100%
- [ ] No warnings en logs durante tests

**Performance**:
- [ ] Connection pooling implementado (si Enhanced)
- [ ] Embeddings cache implementado (si Enhanced)
- [ ] No memory leaks evidentes

### B. Template para TROUBLESHOOTING.md

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
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small (< 50 lines)
- Prefer simple over clever
```

---

## FIN DEL WORKPLAN
