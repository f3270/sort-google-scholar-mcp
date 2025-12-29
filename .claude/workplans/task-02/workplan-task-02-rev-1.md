# Plan de Trabajo: Task-02 - Fase 2 MCP Server Skeleton (Rev-1)

**Fecha de Creación**: 2025-12-28
**Versión**: rev-1
**Estado**: Pendiente de Aprobación
**Autor**: Claude Code
**Stack**: MCP (stdio) + ChromaDB (embedded) + Anthropic Claude + sentence-transformers + httpx + Selenium + PyMuPDF

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | 2025-12-28 | Plan inicial | Creación del workplan para Fase 2 - MCP Server Skeleton |
| rev-1 | 2025-12-28 | Mejoras aplicadas post-revisión con codex: patrón imports/registro tool fijado, logging stdio exacto, tests deterministas con debug=True, alcance MVP reducido a 3 verificaciones core, rutas desde settings, defaults seguros | Incorporar sugerencias de análisis automatizado para reducir riesgo de bloqueos y mantener KISS |

---

## 1. Resumen Ejecutivo

### Descripción General

Esta tarea implementa la **Fase 2 del MCP_PLAN.md**: crear un servidor MCP funcional con transporte stdio que expone un tool básico (`search_papers`) para buscar papers en Google Scholar. El servidor se integrará con Claude Code y permitirá ejecutar búsquedas académicas desde la interfaz conversacional de Claude.

La implementación reutiliza completamente los componentes desarrollados en la Fase 1 (ScholarSearcher, SessionManager, modelos Pydantic) y se enfoca en crear la capa de integración MCP que los expone como herramientas invocables.

**MEJORA REV-1**: Alcance MVP simplificado a 3 verificaciones esenciales para reducir sobrecarga y mantener foco KISS.

### Alcance Principal

1. **Servidor MCP con stdio transport**: Punto de entrada ejecutable que se comunica con Claude Code vía stdio
2. **Tool `search_papers`**: Herramienta async que acepta parámetros de búsqueda, ejecuta scraping de Google Scholar, guarda sesión y retorna resumen
3. **Sistema de logging**: Configuración exacta de logging a archivo + stderr (no stdout) para MCP debugging
4. **Testing manual simplificado**: Validación con MCP Inspector usando debug mode (determinista)

**MEJORA REV-1**: Testing MVP ahora usa `debug=True` por defecto para validación determinista sin dependencia de red.

### Componentes del Sistema MCP Afectados

- **MCP Tools**: Nuevo tool `search_papers` (primer tool del servidor)
- **Scraping**: Reutiliza `ScholarSearcher` de Fase 1 sin modificaciones
- **Session Management**: Reutiliza `SessionManager` de Fase 1 sin modificaciones
- **Models**: Reutiliza todos los modelos Pydantic existentes

### Referencia a MCP_PLAN.md

**Fase del MCP_PLAN.md**: Fase 2 - MCP Server Skeleton

**Duración estimada**: 2.5-3h (reducido de 3-4h por simplificación de testing)

**Dependencias**:
- ✅ Fase 0 completada (setup, config, models)
- ✅ Fase 1 completada (ScholarSearcher, SessionManager, parser)

**Entregables esperados**:
- ✅ Servidor MCP funcional con stdio transport
- ✅ Tool `search_papers` implementado y testeado con debug mode
- ✅ Logging funcionando correctamente (archivo + stderr, no stdout)
- ✅ Validación determinista con MCP Inspector

### Estimación de Tiempo y Recursos

| Componente | Esfuerzo Estimado | Prioridad |
|------------|-------------------|-----------|
| Servidor MCP (`server.py`) con patrón imports definitivo | 0.5h | 🔴 CORE |
| Tool `search_papers` con defaults seguros | 1h | 🔴 CORE |
| Testing con MCP Inspector (debug mode) | 0.5h | 🔴 CORE |
| Debugging y ajustes | 0.5h | 🔴 CORE |
| **TOTAL** | **2.5-3h** | |

**Recursos necesarios**:
- ✅ Dependencias ya instaladas (`mcp>=1.2.0` en pyproject.toml)
- ✅ Componentes de Fase 1 funcionales
- ⚠️ MCP Inspector instalado para testing (`npm install -g @modelcontextprotocol/inspector`)

**MEJORA REV-1**: Eliminada necesidad de Anthropic API key para MVP (se usa debug mode), eliminada necesidad de Claude Code CLI (opcional para Enhanced).

---

## 2. Priorización del Alcance

### 🔴 MVP/CORE (Obligatorio)

**Criterio de éxito**: Servidor MCP funcional que permite ejecutar búsquedas deterministas de Google Scholar usando páginas archivadas, guardando sesiones y retornando resultados básicos.

**MEJORA REV-1**: MVP reducido a 3 verificaciones esenciales para eliminar sobrecarga de testing y mantener KISS.

**Funcionalidades core**:
- [x] Servidor MCP con stdio transport (`src/sortgs_mcp/server.py`)
- [x] Patrón de imports/registro definitivo (server.py define mcp, importa tools al final)
- [x] Tool `search_papers` con defaults seguros (debug=True, num_results=20)
- [x] Logging exacto a stderr + archivo con rutas desde settings
- [x] Validación de inputs con Pydantic
- [x] Integración con ScholarSearcher async
- [x] Persistencia de sesión con SessionManager usando settings.sessions_dir
- [x] Output JSON con session_id, papers_found, top_5_titles, csv_path
- [x] Testing manual con MCP Inspector usando debug mode

**Componentes MVP**:
```
src/sortgs_mcp/
├── server.py          # NEW - Entry point MCP con patrón imports definitivo
└── tools/
    ├── __init__.py    # EXISTS (empty)
    └── search.py      # NEW - Tool search_papers con defaults seguros
```

**Criterios de aceptación MVP (SIMPLIFICADOS)**:

**MEJORA REV-1**: Reducido de 6 a 3 verificaciones core.

1. **MCP Inspector + Debug Mode**: Inspector lista `search_papers` y ejecuta OK con `debug=True` (usa web archive, determinista)
2. **Persistencia de sesión**: Session dir `data/sessions/{session_id}/` existe con `metadata.json` y `results.csv`
3. **Logging sin contaminar stdio**: Logs en archivo con rutas desde settings, stderr solo warnings, stdout limpio

### 🟡 Enhanced (Si hay tiempo)

**Funcionalidades que agregan valor pero no bloquean**:

**MEJORA REV-1**: Screenshots, Claude Code integration, y casos de prueba ampliados movidos de MVP a Enhanced.

- [ ] Integración con Claude Code CLI (testing end-to-end desde chat)
- [ ] Error handling sofisticado con mensajes user-friendly detallados
- [ ] Progress indicators en logs durante scraping largo
- [ ] Validación adicional de parámetros (ej: end_year >= start_year)
- [ ] Formateo de output con markdown para mejor UX en Claude Code
- [ ] Tool metadata enriquecida (descriptions, examples)
- [ ] Screenshots de MCP Inspector y Claude Code (para PR)
- [ ] Casos de prueba con red real (num_results altos, filtros complejos)

**Componentes Enhanced**: Mejoras en `search.py`, `server.py`, y testing ampliado

**Justificación postponer Enhanced**:
- Error handling básico (try/except + logging) es suficiente para MVP
- Validación de Pydantic ya cubre casos principales
- Screenshots pueden agregarse al crear PR sin afectar funcionalidad
- Testing con red real puede fallar por CAPTCHA (no determinista)

### 🟢 Nice-to-Have (Futuras iteraciones)

**Para versiones posteriores**:
- [ ] Tool adicional `list_sessions` (será implementado en Fase 7)
- [ ] Telemetría de uso de tools
- [ ] Auto-retry con backoff en caso de robot check
- [ ] Cache de búsquedas recientes

**Justificación postponer Nice-to-Have**:
- Fase 2 es skeleton básico, features adicionales vienen en fases posteriores
- `list_sessions` está planificado para Fase 7 según MCP_PLAN.md

### Plan de Reducción de Alcance

**Si se excede el tiempo estimado (>3h)**:

1. **Recorte Nivel 1** (eliminar Enhanced completo): Mantener solo testing con debug mode, sin Claude Code integration → Ahorro: 1h
2. **Recorte Nivel 2** (simplificar error handling): Usar solo try/except básico, sin mensajes custom → Ahorro: 0.5h
3. **Core absoluto inamovible**:
   - Servidor MCP con stdio y patrón imports fijado
   - Tool `search_papers` funcional con debug=True
   - 3 verificaciones MVP completadas

**Punto de decisión**: Si después de 2.5h no hay tool funcional en MCP Inspector con debug mode → Escalar a usuario para revisión de dependencias/setup.

---

## 3. Diseño Técnico

### Arquitectura Propuesta

**Arquitectura de alto nivel**:

```
Claude Code (client)
       ↓ stdio
┌──────────────────────────────┐
│  sortgs_mcp.server           │
│  - FastMCP instance          │
│  - Logging setup (EXACTO)    │
│  - Tool registry (PATRÓN)    │
└──────────────────────────────┘
       ↓ imports al final
┌──────────────────────────────┐
│  tools/search.py             │
│  - from server import mcp    │
│  - @mcp.tool() decorator     │
│  - search_papers()           │
│    ├── Defaults seguros      │
│    ├── Rutas desde settings  │
│    ├── Create session        │
│    ├── Search with Scholar   │
│    ├── Save session          │
│    └── Return summary        │
└──────────────────────────────┘
       ↓ uses
┌──────────────────────────────┐
│  Fase 1 Components           │
│  - ScholarSearcher (async)   │
│  - SessionManager            │
│  - Pydantic Models           │
│  - Config (settings)         │
└──────────────────────────────┘
```

**Flujo de ejecución de `search_papers` tool**:

1. **Input validation**: Pydantic valida parámetros del tool (automático por MCP)
2. **Session creation**: SessionManager crea UUID y directorios usando settings.sessions_dir
3. **Search execution**: ScholarSearcher.search() ejecuta scraping async (debug=True por defecto)
4. **Session persistence**: SessionManager.save_session() guarda metadata.json + results.csv
5. **Output formatting**: Retorna dict con session_id, papers_found, top_5_titles, csv_path
6. **Error handling**: Try/except captura errores y logs para debugging

**MEJORA REV-1**: Rutas ahora usan `settings.sessions_dir` y `settings.log_dir` (no hardcodeadas).

### Componentes Afectados

**Nuevos archivos**:
- `src/sortgs_mcp/server.py` - MCP server entry point con patrón imports fijado
- `src/sortgs_mcp/tools/search.py` - Tool implementation

**Archivos modificados**:
- Ninguno (reutilización pura de Fase 1)

**Archivos leídos** (dependencias):
- `src/sortgs_mcp/config.py` - Settings singleton
- `src/sortgs_mcp/models.py` - SearchParams, SearchSession, Paper
- `src/sortgs_mcp/core/scholar.py` - ScholarSearcher
- `src/sortgs_mcp/core/session.py` - SessionManager

### Consideraciones Específicas de MCP + RAG

**MCP Tools Affected**:
- [x] ¿Requiere nuevos tools? **Sí** - `search_papers` (primer tool del servidor)
- [ ] ¿Cambios en tool schemas? No - schema se genera automático de parámetros async def
- [x] ¿Cambios en MCP server entry point? **Sí** - Crear `server.py` desde cero

**Google Scholar Scraping**:
- [ ] ¿Afecta lógica de scraping? **No** - Reutiliza ScholarSearcher sin cambios
- [ ] ¿Cambios en parsing HTML? **No**
- [x] ¿Requiere manejo de CAPTCHA? **Sí** - Ya implementado en ScholarSearcher.fetch_with_selenium()
- [ ] ¿Cambios en rate limiting? **No** - Ya implementado con random delays en fetch_page()

**Chunking/Embeddings/Retrieval/ChromaDB/PDF**: No aplica a esta fase

### Decisiones de Arquitectura MCP

**MCP Server Design**:
- [x] ¿Cambios en server.py? **Sí** - Crear desde cero con patrón definitivo
- **Transport**: stdio (fixed para Claude Code - no negociable)
- **Logging** (EXACTO):
  - FileHandler → `settings.log_dir / "sortgs_mcp.log"` (DEBUG level)
  - StreamHandler → `sys.stderr` EXPLÍCITO con `setLevel(logging.WARNING)`
  - **CRÍTICO**: NO stdout (contaminaría MCP stdio protocol)
- **MCP Framework**: `mcp` SDK oficial v1.2+ con FastMCP helper

**MEJORA REV-1**: Logging ahora especifica exactamente `sys.stderr` y ruta desde `settings.log_dir`.

**Tool Design**:
- [x] ¿Tool es síncrono o asíncrono? **Asíncrono** - MCP soporta async, ScholarSearcher es async
- [x] ¿Requiere estado global? **Sí** - Singletons de SessionManager y Settings (instanciados en tools/search.py)
- [x] ¿Timeout considerado? **Sí** - httpx ya tiene timeout=30s, searches largas pueden tardar pero MCP no tiene timeout hard-coded
- **Defaults seguros MVP**: `debug=True`, `num_results=20` (producción puede override a False/100)

**MEJORA REV-1**: Defaults seguros para MVP (debug=True, num_results=20) documentados explícitamente.

**Error Handling**:
- [x] Mensajes user-friendly: Try/except con logging.error() y re-raise con mensaje claro
- [x] Graceful degradation: Si falla parcialmente (ej: menos papers de lo esperado), retornar los que se obtuvieron
- [x] Logging apropiado:
  - INFO para progress (iniciando búsqueda, sesión creada, papers encontrados)
  - WARNING para issues no-bloqueantes (robot check, menos papers de lo esperado)
  - ERROR para fallos críticos (sin conexión, error de parsing)

**Testing Strategy**:
- [x] MCP Inspector testing: Manual invocation con `debug=True` (determinista)
- [ ] Claude Code integration testing: **Enhanced** - End-to-end desde chat
- [ ] Unit tests con mocks: **No prioritario en MVP** - dejar para Fase 8 (Testing)

**MEJORA REV-1**: Testing MVP ahora es solo Inspector + debug mode (determinista), Claude Code movido a Enhanced.

### Patrón de Imports/Registro Definitivo

**MEJORA REV-1**: Patrón fijado para evitar circular imports.

#### server.py (Orden EXACTO):
```python
# 1. Imports estándar
import logging
import sys
from pathlib import Path

# 2. Imports terceros
from mcp.server.fastmcp import FastMCP

# 3. Imports locales (config)
from sortgs_mcp.config import settings

# 4. Setup logging (ANTES de crear mcp)
log_path = settings.log_dir / "sortgs_mcp.log"
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stderr)  # EXPLÍCITO: sys.stderr
    ]
)

# Ajustar StreamHandler a WARNING (EXPLÍCITO)
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
        handler.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# 5. Initialize MCP server
mcp = FastMCP("sortgs")

# 6. Import tools DESPUÉS de definir mcp (para ejecutar decoradores)
from sortgs_mcp.tools import search  # noqa: F401 E402

# 7. Main
def main():
    """Entry point for MCP server."""
    logger.info("Starting Sort Google Scholar MCP Server")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
```

#### tools/search.py (Orden EXACTO):
```python
# 1. Imports estándar
import logging
from pathlib import Path

# 2. Import MCP instance desde server
from sortgs_mcp.server import mcp

# 3. Imports locales
from sortgs_mcp.config import settings
from sortgs_mcp.models import SearchParams, SearchSession
from sortgs_mcp.core.scholar import ScholarSearcher
from sortgs_mcp.core.session import SessionManager

logger = logging.getLogger(__name__)

# Singleton SessionManager
session_manager = SessionManager(settings.sessions_dir)

# Tool registration con decorador
@mcp.tool()
async def search_papers(
    keywords: str,
    num_results: int = 20,  # MEJORA: Default seguro para MVP
    sort_by: str = "Citations",
    start_year: int | None = None,
    end_year: int | None = None,
    languages: list[str] | None = None
) -> dict:
    """Search Google Scholar for papers and save results in a session.

    Args:
        keywords: Search query keywords
        num_results: Number of results to fetch (10-1000, default 20 for MVP)
        sort_by: Sort by "Citations" or "cit/year"
        start_year: Filter papers from this year onwards
        end_year: Filter papers up to this year
        languages: Language codes (e.g., ["en", "es"])

    Returns:
        Dictionary with session_id, papers_found, top_5_titles, csv_path
    """
    logger.info(f"search_papers called with keywords='{keywords}', num_results={num_results}")

    # 1. Create SearchParams (pydantic validates)
    params = SearchParams(
        keywords=keywords,
        num_results=num_results,
        sort_by=sort_by,
        start_year=start_year,
        end_year=end_year,
        languages=languages,
        debug=True  # MEJORA: Default True para MVP (determinista)
    )

    # 2. Create session (usa settings.sessions_dir)
    session_id = session_manager.create_session(params)
    logger.info(f"Created session: {session_id}")

    # 3. Search papers
    async with ScholarSearcher() as searcher:
        papers = await searcher.search(params)

    logger.info(f"Found {len(papers)} papers")

    # 4. Save session
    session = SearchSession(
        session_id=session_id,
        params=params,
        papers=papers,
        papers_count=len(papers)
    )
    session_manager.save_session(session)
    logger.info(f"Session saved to {settings.sessions_dir / session_id}")

    # 5. Return summary
    top_5_titles = [p.title for p in papers[:5]]
    csv_path = str(settings.sessions_dir / session_id / "results.csv")

    return {
        "session_id": session_id,
        "papers_found": len(papers),
        "top_5_titles": top_5_titles,
        "csv_path": csv_path
    }
```

**MEJORA REV-1**: Patrón completo documentado con snippets exactos y orden de imports.

### Decisiones Técnicas KISS

**¿Se reutilizan patrones existentes?**
- ✅ **Sí** - Reutilización completa de Fase 1 (ScholarSearcher, SessionManager)
- ✅ **Sí** - Logging pattern consistente con resto del proyecto
- ✅ **Sí** - Pydantic models para validación (patrón del proyecto)
- ✅ **Sí** - Settings singleton para rutas (config centralizada)

**MEJORA REV-1**: Agregado uso de `settings` para rutas.

**¿Se evita sobre-ingeniería?**
- ✅ **Sí** - No se crea abstracción de "ToolRegistry" o "ToolBase" (solo 1 tool por ahora)
- ✅ **Sí** - No se implementa sistema de plugins (YAGNI - You Aren't Gonna Need It)
- ✅ **Sí** - Logging simple con handlers built-in de Python
- ✅ **Sí** - Testing MVP simplificado a 3 verificaciones core

**MEJORA REV-1**: Alcance MVP reducido de 6 a 3 verificaciones para eliminar sobre-ingeniería.

**¿Solución más simple posible?**
- ✅ **Sí** - FastMCP provee decorador `@mcp.tool()` que auto-registra (no necesitamos registro manual)
- ✅ **Sí** - Stdio transport es el más simple (no HTTP server, no sockets)
- ✅ **Sí** - Output como dict simple (MCP serializa automático a JSON)
- ✅ **Sí** - Debug mode por defecto elimina dependencia de red para MVP

**MEJORA REV-1**: Debug mode por defecto hace testing determinista (más simple).

**Justificación de simplicidad**:
Esta es la solución más simple porque:
1. **Delegación máxima a frameworks**: FastMCP maneja stdio, serialización, registro de tools
2. **Zero abstracciones nuevas**: Solo funciones async decoradas, no clases intermedias
3. **Reutilización total**: No se duplica lógica de Fase 1
4. **Config centralizada**: `settings` singleton evita pasar configs manualmente y hardcodear paths
5. **Testing determinista**: Debug mode elimina variables de red/CAPTCHA para MVP

**MEJORA REV-1**: Agregado punto 4 (settings) y 5 (debug mode).

---

## 4. Plan de Desarrollo

### Tareas Ordenadas por Prioridad

| ID | Prioridad | Tarea | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-----------|-------|-------------------------|--------------|----------|
| T1 | 🔴 CORE | Crear `server.py` con patrón imports definitivo y logging exacto | - `python -m sortgs_mcp.server` arranca sin errores<br>- Logs en `settings.log_dir/sortgs_mcp.log`<br>- Stderr solo warnings, stdout limpio<br>- Patrón imports correcto (mcp definido, tools importados al final) | - | 0.5h |
| T2 | 🔴 CORE | Crear `tools/search.py` con defaults seguros y rutas desde settings | - Tool importa `mcp` desde server.py<br>- Defaults: debug=True, num_results=20<br>- Usa settings.sessions_dir para persistencia<br>- Retorna dict con formato especificado | T1 | 1h |
| T3 | 🔴 CORE | Testing con MCP Inspector (debug mode) | - Inspector lista `search_papers`<br>- Invocación exitosa con defaults (debug=True)<br>- Session guardada en settings.sessions_dir/{uuid}/<br>- metadata.json y results.csv existen<br>- Logs en archivo sin stdout | T2 | 0.5h |
| T4 | 🟡 Enhanced | Integración con Claude Code | - `claude mcp add` exitoso<br>- Tool invocable desde chat<br>- Output legible en chat | T3 | 0.5h |
| T5 | 🟡 Enhanced | Mejorar error handling y validación | - Validación end_year >= start_year<br>- Mensajes user-friendly detallados | T3 | 0.5h |

**Orden de implementación sugerido**: T1 → T2 → T3 → (opcional T4, T5)

**MEJORA REV-1**: T3 ahora incluye verificación de logs sin stdout. T4-T5 movidos a Enhanced. T3 eliminado (error handling básico incluido en T2).

### Detalles de Implementación por Tarea

#### T1: Crear `server.py` con patrón imports definitivo

**Archivo**: `src/sortgs_mcp/server.py`

**Implementación**: Ver snippet completo en sección "Patrón de Imports/Registro Definitivo"

**Criterios de aceptación**:
- `python -m sortgs_mcp.server` arranca y queda en espera (stdio mode)
- `settings.log_dir/sortgs_mcp.log` se crea y contiene línea "Starting Sort Google Scholar MCP Server"
- Stderr configurado explícitamente con `sys.stderr` y nivel WARNING
- Stdout limpio (sin logs)
- Patrón imports correcto: mcp definido arriba, `from sortgs_mcp.tools import search` al final

**MEJORA REV-1**: Agregados criterios sobre stderr/stdout y patrón imports.

#### T2: Crear `tools/search.py` con defaults seguros

**Archivo**: `src/sortgs_mcp/tools/search.py`

**Implementación**: Ver snippet completo en sección "Patrón de Imports/Registro Definitivo"

**Criterios de aceptación**:
- Tool importa `mcp` desde `sortgs_mcp.server` correctamente (no circular import)
- Parámetros: debug=True (default), num_results=20 (default)
- SessionManager usa `settings.sessions_dir` (no hardcodeado)
- Retorna dict con: session_id, papers_found, top_5_titles, csv_path
- Try/except básico captura errores y loguea
- Tool se registra automáticamente con decorador @mcp.tool()

**MEJORA REV-1**: Agregados criterios sobre defaults seguros, rutas desde settings, y try/except básico.

#### T3: Testing con MCP Inspector (debug mode)

**Comandos**:
```bash
# Instalar MCP Inspector (si no está)
npm install -g @modelcontextprotocol/inspector

# Ejecutar inspector
mcp inspect python -m sortgs_mcp.server
```

**Casos de prueba MVP (SIMPLIFICADOS)**:

**MEJORA REV-1**: Solo 1 caso de prueba core con debug=True (determinista).

1. **Test MVP con debug mode**: keywords="machine learning", num_results=10 (usa defaults debug=True)
   - Tool debe retornar session_id válido
   - Verificar filesystem: `settings.sessions_dir/{session_id}/metadata.json` y `results.csv` existen
   - Verificar logs: archivo tiene INFO, stderr solo warnings, stdout limpio
   - Papers encontrados >= 1 (debug mode usa archivo web archivado, siempre tiene resultados)

**Casos Enhanced (OPCIONALES)**:
2. Test con filtros: keywords="transformers", start_year=2017, end_year=2024, sort_by="cit/year", debug=False
3. Test error: keywords="" (vacío, debería fallar validación)

**Criterios de aceptación**:
- MCP Inspector muestra tool `search_papers` listado
- Schema muestra parámetros correctos con defaults (debug=True, num_results=20)
- Invocación MVP exitosa retorna session_id válido
- Verificar en filesystem: `settings.sessions_dir/{session_id}/metadata.json` y `results.csv` existen
- Logs: archivo completo, stderr solo warnings, stdout limpio

**MEJORA REV-1**: Reducido a 1 caso core + 2 opcionales Enhanced.

#### T4: Integración con Claude Code (ENHANCED)

**MEJORA REV-1**: Movido de CORE a Enhanced.

**Comandos**:
```bash
# Agregar servidor a Claude Code
claude mcp add --transport stdio sortgs-mcp -- python -m sortgs_mcp.server

# Verificar registro
claude mcp list

# Probar en chat
# "Search for papers about 'neural networks' using sortgs"
```

**Criterios de aceptación**:
- `claude mcp list` muestra `sortgs-mcp` con status active
- En chat, Claude puede invocar el tool correctamente
- Output del tool es legible (session_id, papers_found, top_5_titles)
- No hay errores en logs

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Unit tests**: No prioritario en MVP (dejar para Fase 8)

**Integration tests**: No prioritario en MVP (dejar para Fase 8)

**Manual testing**:
- **MCP Inspector**: Validación de tool registration, schema, y invocación con debug mode (determinista)
- **Claude Code (Enhanced)**: End-to-end testing desde chat conversacional

**MEJORA REV-1**: Claude Code testing movido a Enhanced.

### Casos de Prueba Principales (MCP-specific)

**MCP Tools** (CORE):
- [x] Tool registrado correctamente en MCP server (verificar con MCP Inspector)
- [x] Tool schema válido (parámetros: keywords str, num_results int con default 20, debug bool con default True)
- [x] Tool invocable desde MCP Inspector con debug mode
- [x] Error handling básico (try/except, no crashes)

**MCP Tools** (Enhanced):
- [ ] Tool invocable desde Claude Code
- [ ] Error handling sofisticado (mensajes user-friendly detallados)

**Google Scholar Scraping** (CORE con debug mode):
- [x] Search ejecuta con debug=True sin robot check (usa web archive)
- [x] Parsing extrae todos los campos correctamente (verificar CSV)
- [x] CSV guardado con formato correcto (headers, data types)

**Google Scholar Scraping** (Enhanced con red real):
- [ ] Search ejecuta sin robot check (num_results pequeño, delay suficiente)
- [ ] Selenium fallback funciona (si robot check) - difícil de forzar, test manual si ocurre

**Session Management** (CORE):
- [x] Session ID es UUID válido
- [x] Directorios creados en `settings.sessions_dir/{session_id}/`, `{session_id}/pdfs/`
- [x] metadata.json contiene todos los campos esperados
- [x] results.csv contiene papers con todas las columnas

**Logging** (CORE):
- [x] Archivo de log en `settings.log_dir/sortgs_mcp.log`
- [x] INFO level captura flujo completo
- [x] Stderr solo warnings/errors
- [x] Stdout limpio (no contamina MCP stdio)

**Edge Cases** (Enhanced):
- [ ] keywords vacío → Debería fallar validación de Pydantic
- [ ] num_results=0 → Debería fallar validación (ge=10)
- [ ] num_results=5000 → Debería fallar validación (le=1000)
- [ ] Google Scholar sin resultados → Retorna lista vacía, no error

**MEJORA REV-1**: Casos separados en CORE (debug mode) vs Enhanced (red real), logging verificado explícitamente.

### Criterios de Calidad

**Funcionalidad**:
- Tool ejecuta búsquedas correctamente con debug mode
- Session persiste en filesystem usando rutas desde settings
- Output JSON es válido y completo

**Performance**:
- Búsqueda con debug=True: <5 segundos (local, sin red)
- Búsqueda con debug=False (Enhanced): depende de red y num_results

**Logging**:
- INFO level captura flujo completo (inicio, progreso, fin)
- ERROR level captura excepciones con traceback
- Stderr solo WARNING+, stdout limpio

**MEJORA REV-1**: Performance con debug mode es <5s (determinista).

---

## 6. Smoke Test Checklist (MCP-adapted)

**Propósito**: Checklist manual SIMPLIFICADO para ejecutar y adjuntar al PR como evidencia.

**MEJORA REV-1**: Checklist reducido de 14 secciones a 6 secciones core para MVP.

**Formato copiable para PR:**

```markdown
**SMOKE TEST CHECKLIST - Task-02 Fase 2 MCP Server Skeleton (MVP)**

**Ejecutado por**: [Nombre]
**Fecha**: [YYYY-MM-DD]
**Ambiente**: Local Development
**MCP Server**: sortgs-mcp
**Data Directory**: ./data (local filesystem)
**Test Mode**: Debug (web archive)

---

#### 1. Setup y Configuración

- [ ] **1.1** Dependencias instaladas (`pip list | grep mcp` muestra mcp>=1.2.0)
- [ ] **1.2** Estructura de directorios creada (`settings.sessions_dir` y `settings.log_dir` existen)
- [ ] **1.3** Fase 1 completada (ScholarSearcher, SessionManager existen y funcionan)

---

#### 2. MCP Server Startup

- [ ] **2.1** Server arranca sin errores (`python -m sortgs_mcp.server` en terminal)
- [ ] **2.2** Log file creado en `settings.log_dir/sortgs_mcp.log`
- [ ] **2.3** Log contiene "Starting Sort Google Scholar MCP Server"
- [ ] **2.4** Stdout limpio (no hay logs), stderr solo warnings

---

#### 3. MCP Inspector Connection

- [ ] **3.1** MCP Inspector instalado (`mcp --version` funciona)
- [ ] **3.2** Inspector conecta correctamente (`mcp inspect python -m sortgs_mcp.server`)
- [ ] **3.3** Tool `search_papers` aparece listado
- [ ] **3.4** Tool schema muestra defaults correctos (debug=True, num_results=20)

**Screenshot requerido** (Enhanced): MCP Inspector mostrando tool con schema

---

#### 4. Tool: search_papers - Test MVP (Debug Mode)

- [ ] **4.1** Invocar con keywords="machine learning", num_results=10 (usa defaults debug=True)
- [ ] **4.2** Tool retorna sin errores
- [ ] **4.3** Output contiene session_id (formato UUID)
- [ ] **4.4** papers_found >= 1 (debug mode siempre tiene resultados)
- [ ] **4.5** top_5_titles es array con títulos válidos
- [ ] **4.6** csv_path apunta a archivo existente

**Input de prueba**:
```json
{
  "keywords": "machine learning",
  "num_results": 10
}
```

**Screenshot requerido** (Enhanced): Output del tool mostrando session_id

---

#### 5. Session Persistence

- [ ] **5.1** Directorio `settings.sessions_dir/{session_id}/` existe
- [ ] **5.2** Archivo `metadata.json` existe y es JSON válido
- [ ] **5.3** metadata.json contiene: session_id, created_at, params (con debug=True), papers, papers_count
- [ ] **5.4** Archivo `results.csv` existe
- [ ] **5.5** CSV tiene headers correctos (rank, title, authors, citations, year, ...)
- [ ] **5.6** CSV contiene datos (mínimo 1 fila de paper)

**Comando de verificación**:
```bash
SESSION_ID="<session_id del test 4>"
ls -la $(python -c "from sortgs_mcp.config import settings; print(settings.sessions_dir)")/$SESSION_ID/
cat $(python -c "from sortgs_mcp.config import settings; print(settings.sessions_dir)")/$SESSION_ID/metadata.json | jq .
head -5 $(python -c "from sortgs_mcp.config import settings; print(settings.sessions_dir)")/$SESSION_ID/results.csv
```

---

#### 6. Logging

- [ ] **6.1** `settings.log_dir/sortgs_mcp.log` contiene logs de nivel INFO
- [ ] **6.2** Logs incluyen "search_papers called with keywords=..."
- [ ] **6.3** Logs incluyen "Created session: {uuid}"
- [ ] **6.4** Logs incluyen "Found X papers"
- [ ] **6.5** Logs incluyen "Session saved to ..."
- [ ] **6.6** Stdout limpio (verificar terminal donde corre server)
- [ ] **6.7** Stderr solo muestra warnings/errors

**Comando de verificación**:
```bash
tail -50 $(python -c "from sortgs_mcp.config import settings; print(settings.log_dir)")/sortgs_mcp.log
```

---

**RESULTADO FINAL**

- [ ] ✅ **TODOS LOS TESTS PASAN** - Feature lista para code review
- [ ] ⚠️ **HAY ISSUES MENORES** - Documentar en comentarios del PR
- [ ] ❌ **HAY ISSUES BLOQUEANTES** - No crear PR hasta resolverlos

**Notas adicionales**:
[Agregar observaciones, bugs encontrados, o mejoras sugeridas]

---

**ENHANCED CHECKLIST** (Opcional - si hay tiempo):
- [ ] Claude Code Integration (sección 7): Tool invocable desde chat
- [ ] Error Handling (sección 8): Tests con parámetros inválidos
- [ ] Code Quality (sección 9): No print(), docstrings, type hints
- [ ] Documentation (sección 10): Docstrings, entry point en pyproject.toml
- [ ] Git y PR (sección 11): Branch, commits, PR description

---
```

**MEJORA REV-1**: Checklist reducido de 14 a 6 secciones core + 5 secciones Enhanced opcionales.

---

## 7. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Circular import entre server.py y tools/** | Baja | Alto | **RESUELTO**: Patrón fijado en rev-1 (mcp en server, tools importado al final) |
| **Logs contaminan stdout y rompen MCP stdio** | Baja | Alto | **RESUELTO**: StreamHandler a `sys.stderr` explícito, nivel WARNING |
| **Testing falla por CAPTCHA/red** | Alta | Medio | **RESUELTO**: Debug mode por defecto (usa web archive, sin red) |
| **Dependencias MCP no instaladas** | Baja | Alto | Verificar `pip list | grep mcp` antes de comenzar. Reinstalar con `pip install -e .` si falta. |
| **FastMCP incompatible con patrón actual** | Media | Alto | Revisar docs de MCP v1.2+ para confirmar API. Alternativa: usar mcp.server.Server directamente (más verboso pero funcional). |

**MEJORA REV-1**: Primeros 3 riesgos marcados como RESUELTOS por mejoras aplicadas.

---

## 8. Plan de Contingencia

### Punto de Decisión GO/NO-GO

**Cuándo**: Después de 2.5 horas de desarrollo (83% del tiempo estimado)

**Verificar**:
- ✅ MVP al menos al 80% completado:
  - server.py funcional (arranca sin errores, patrón imports correcto)
  - search_papers tool implementado con defaults seguros
  - Testing con MCP Inspector exitoso con debug=True (al menos 1 invocación funcional)

**Si no se cumple**:
1. Activar plan de reducción de alcance (eliminar Enhanced completo)
2. Escalar a usuario para revisar:
   - Dependencias instaladas correctamente
   - Fase 1 funcional (ejecutar tests de Fase 1 si existen)
   - Ambiente de desarrollo configurado

### Escenarios de Bloqueo Comunes

#### 1. **Circular import entre server.py y tools/search.py**

**RESUELTO EN REV-1**: Patrón fijado.

**Síntomas**: `ImportError: cannot import name 'mcp' from partially initialized module`

**Mitigación**:
- **Solución ya definida**: Usar patrón de rev-1 (ver sección "Patrón de Imports/Registro")
- Si aún persiste: Mover tool a server.py temporalmente (menos modular pero funcional)

**Tiempo estimado de resolución**: 15 minutos (patrón ya está definido)

#### 2. **Logs contaminan stdout y rompen MCP stdio**

**RESUELTO EN REV-1**: StreamHandler a sys.stderr explícito.

**Síntomas**: MCP Inspector muestra errores de deserialización JSON

**Mitigación**:
- **Solución ya definida**: Usar snippet de logging de rev-1 con `sys.stderr` explícito
- Verificar que NO hay `print()` en código

**Tiempo estimado de resolución**: 10 minutos (patrón ya está definido)

#### 3. **Testing falla por CAPTCHA/robot check**

**RESUELTO EN REV-1**: Debug mode por defecto.

**Síntomas**: Selenium abre browser con CAPTCHA

**Mitigación**:
- **Solución ya definida**: Usar debug=True (default en rev-1) que usa web archive
- Para tests Enhanced con red real: Reducir num_results, esperar entre tests, usar VPN

**Tiempo estimado de resolución**: 0 (workaround inmediato con debug mode)

#### 4. **FastMCP API incompatible / no funciona como se espera**

**Síntomas**: Decorador `@mcp.tool()` no registra tool, o `mcp.run()` falla

**Mitigación**:
1. Revisar docs oficiales de MCP v1.2+: https://github.com/modelcontextprotocol/python-sdk
2. Alternativa: Usar `mcp.server.Server` directamente (low-level API)
3. Si ambos fallan: Consultar con usuario sobre versión exacta de `mcp` instalada

**Tiempo estimado de resolución**: 1 hora

#### 5. **Claude Code no reconoce servidor MCP** (Enhanced)

**Síntomas**: `claude mcp list` muestra servidor pero status=inactive

**Mitigación**:
1. Verificar que servidor arranca sin errores standalone (`python -m sortgs_mcp.server`)
2. Verificar MCP Inspector funciona (si Inspector funciona, problema es con Claude Code config)
3. Reiniciar Claude Code CLI: `claude mcp restart sortgs-mcp`

**Tiempo estimado de resolución**: 30 minutos

---

## 9. Decisiones Técnicas TOMADAS

### 9.1 Patrón de Imports/Registro: Definitivo

**Decisión TOMADA**: Patrón fijado en rev-1

**Justificación**:
- ✅ **Elimina riesgo de circular import**: mcp definido en server, tools importado al final
- ✅ **Modularidad**: Tools en módulo separado (escalable para 6 tools futuros)
- ✅ **Testing**: Tools importables sin arrancar servidor (facilita unit tests futuros)
- ✅ **Claridad**: Orden de imports explícito y documentado

**Alternativas consideradas**:
- **Opción B: Todo en server.py** - Pro: No hay circular import. Contra: No escala para 6 tools, dificulta testing.

**Trade-off aceptado**: Requiere seguir orden de imports específico (documentado en plan)

**Principio KISS aplicado**: Patrón simple de importación estándar de Python

**Plan de migración futura**: No necesaria (patrón escalable)

**NUEVA EN REV-1**

---

### 9.2 Logging: Stderr Explícito y Rutas desde Settings

**Decisión TOMADA**: StreamHandler a `sys.stderr` explícito, FileHandler con rutas desde `settings`

**Justificación**:
- ✅ **MCP stdio requirement**: stdout es exclusivo para MCP protocol → stderr evita contaminación
- ✅ **Debugging completo**: FileHandler con DEBUG captura flujo completo para troubleshooting
- ✅ **Usuario ve solo critical**: stderr con WARNING muestra solo errores importantes
- ✅ **Rutas consistentes**: `settings.log_dir` evita escribir en CWD variable

**Alternativas consideradas**:
- **Opción B: StreamHandler sin especificar stream** - Pro: Menos verboso. Contra: RIESGO ALTO de ir a stdout.
- **Opción C: Hardcodear path del log** - Pro: Más simple. Contra: Inconsistente con config centralizada.

**Trade-off aceptado**: Código de logging ligeramente más verboso

**Principio KISS aplicado**: Configuración estándar de Python logging, no framework custom

**Plan de migración futura**: Si necesitamos logs estructurados (JSON), agregar JSONFormatter

**MEJORA EN REV-1**: Agregado stderr explícito y rutas desde settings

---

### 9.3 Testing MVP: Debug Mode por Defecto

**Decisión TOMADA**: debug=True default, testing MVP con web archive (sin red)

**Justificación**:
- ✅ **Determinista**: Siempre funciona, no depende de estado de Google Scholar
- ✅ **Sin CAPTCHA**: Web archive no requiere resolver CAPTCHAs
- ✅ **Rápido**: Respuesta <5s vs minutos con red real
- ✅ **Confiable**: No falla por rate limiting o robot checks

**Alternativas consideradas**:
- **Opción B: debug=False default, testing con red real** - Pro: Más realista. Contra: Frágil, puede fallar por CAPTCHA.

**Trade-off aceptado**: Testing MVP no valida scraping en vivo (pero Fase 1 ya lo validó)

**Principio KISS aplicado**: Testing más simple y confiable

**Plan de migración futura**: Enhanced puede agregar tests con red real

**NUEVA EN REV-1**

---

### 9.4 Alcance MVP: 3 Verificaciones Core

**Decisión TOMADA**: MVP simplificado a 3 verificaciones esenciales

**Justificación**:
- ✅ **KISS**: Elimina sobrecarga de screenshots, múltiples casos, checklists extensos
- ✅ **Foco en funcionalidad**: Las 3 verificaciones cubren lo crítico (tool funciona, persiste, loguea)
- ✅ **Tiempo realista**: 2.5-3h es alcanzable vs 3-4h con 6+ verificaciones
- ✅ **Enhanced disponible**: Features adicionales no se pierden, se postponen

**Alternativas consideradas**:
- **Opción B: Mantener 6 verificaciones en MVP** - Pro: Más completo. Contra: Sobrecarga, excede tiempo, no KISS.

**Trade-off aceptado**: Screenshots y Claude Code testing postponed a Enhanced

**Principio KISS aplicado**: MVP mínimo viable real

**Plan de migración futura**: Enhanced agrega verificaciones adicionales

**NUEVA EN REV-1**

---

### 9.5 Defaults Seguros: num_results=20, debug=True

**Decisión TOMADA**: Para MVP, defaults seguros que minimizan riesgo

**Justificación**:
- ✅ **num_results=20**: Balance entre rapidez y resultados suficientes para validar
- ✅ **debug=True**: Elimina dependencia de red, CAPTCHA, rate limiting para MVP
- ✅ **Documentado**: Plan explica que producción puede override a False/100
- ✅ **Escalable**: Usuario puede pasar debug=False cuando invoque tool

**Alternativas consideradas**:
- **Opción B: debug=False, num_results=100** - Pro: Más "real". Contra: Testing frágil.

**Trade-off aceptado**: MVP no valida scraping en vivo (pero Fase 1 ya lo hizo)

**Principio KISS aplicado**: Defaults que "just work" para MVP

**Plan de migración futura**: Enhanced puede cambiar defaults o hacerlos configurables

**NUEVA EN REV-1**

---

### 9.6 Framework MCP: FastMCP

**Decisión TOMADA**: FastMCP (high-level helper)

**Justificación**:
- ✅ **Simplicidad**: Decorador `@mcp.tool()` registra automáticamente
- ✅ **Menos boilerplate**: FastMCP maneja serialización JSON, validación
- ✅ **Documentación**: Enfoque recomendado en docs oficiales
- ✅ **Type hints**: Genera schema automático

**Alternativas consideradas**:
- **Opción B: Server low-level** - Pro: Mayor control. Contra: Más código boilerplate.

**Trade-off aceptado**: Menos control granular sobre MCP protocol

**Principio KISS aplicado**: FastMCP es el wrapper más simple

**Plan de migración futura**: Si necesitamos mayor control, migrar a Server low-level

**SIN CAMBIOS EN REV-1** (decisión original correcta)

---

### 9.7 Tool Output: Dict Simple

**Decisión TOMADA**: Dict simple (sin modelo Pydantic)

**Justificación**:
- ✅ **Simplicidad**: MCP serializa dict a JSON automáticamente
- ✅ **Flexibilidad**: Fácil de modificar sin crear modelo nuevo
- ✅ **No over-engineering**: Output simple no requiere validación

**Alternativas consideradas**:
- **Opción B: Crear modelo `SearchPapersResult`** - Pro: Type safety. Contra: Boilerplate extra.

**Trade-off aceptado**: No hay validación de output

**Principio KISS aplicado**: Dict es la estructura más simple

**Plan de migración futura**: Si agregamos más tools, crear modelos compartidos

**SIN CAMBIOS EN REV-1** (decisión original correcta)

---

## 10. Apéndices

### Referencias

- **MCP Protocol Documentation**: https://github.com/modelcontextprotocol/specification
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **FastMCP Documentation**: https://github.com/modelcontextprotocol/python-sdk/tree/main/src/mcp/server/fastmcp
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **httpx Async Client**: https://www.python-httpx.org/async/

### Glosario

| Término | Definición |
|---------|------------|
| **MCP** | Model Context Protocol - Protocolo para exponer herramientas a LLMs |
| **stdio** | Standard Input/Output - Método de comunicación del servidor MCP con cliente |
| **FastMCP** | High-level wrapper del MCP SDK que simplifica creación de servidores |
| **Tool** | Función invocable por LLM que realiza una acción (ej: search_papers) |
| **Session** | Instancia de búsqueda guardada con metadata y resultados |
| **ScholarSearcher** | Clase async que scrape Google Scholar (implementada en Fase 1) |
| **SessionManager** | Clase que maneja persistencia de sesiones (implementada en Fase 1) |
| **Debug mode** | Modo que usa páginas web archivadas en vez de scraping en vivo (determinista) |

**MEJORA REV-1**: Agregado "Debug mode" al glosario.

### Estructura Final del Proyecto

```
src/sortgs_mcp/
├── server.py          # NEW - MCP entry point con patrón imports definitivo
├── config.py          # Settings (ya existe)
├── models.py          # Pydantic models (ya existe)
├── core/
│   ├── scholar.py     # ScholarSearcher (ya existe)
│   ├── session.py     # SessionManager (ya existe)
│   └── parser.py      # HTML parsing (ya existe)
└── tools/
    ├── __init__.py    # Vacío (ya existe)
    └── search.py      # NEW - Tool search_papers con defaults seguros

data/
├── sessions/          # settings.sessions_dir
│   └── {uuid}/
│       ├── metadata.json
│       ├── results.csv
│       └── pdfs/      # Vacío hasta Fase 4
└── logs/              # settings.log_dir
    └── sortgs_mcp.log
```

**MEJORA REV-1**: Agregado `data/logs/` para logging centralizado.

---

**FIN DEL WORKPLAN REV-1**

---

## Resumen de Cambios Rev-1

### Mejoras de Alta Prioridad Aplicadas

✅ **1. Patrón de Imports/Registro Fijado**:
- Documentado orden exacto de imports en server.py y tools/search.py
- Snippets completos incluidos
- Elimina riesgo de circular imports

✅ **2. Logging Stdio Exacto**:
- StreamHandler a `sys.stderr` explícitamente
- Nivel WARNING para stderr
- Rutas desde `settings.log_dir` (no hardcodeadas)

✅ **3. Tests Deterministas con Debug Mode**:
- Default `debug=True` en tool
- Testing MVP usa web archive (sin red)
- Casos con red real movidos a Enhanced

✅ **4. Alcance MVP Reducido**:
- Simplificado de 6 a 3 verificaciones core
- Smoke test checklist reducido de 14 a 6 secciones
- Screenshots y Claude Code movidos a Enhanced

### Mejoras de Media Prioridad Aplicadas

✅ **1. Rutas desde Settings**:
- `settings.sessions_dir` para sesiones
- `settings.log_dir` para logs
- Documentado en snippets y verificaciones

✅ **2. Import Explícito de Tools**:
- Paso agregado a T1: importar `sortgs_mcp.tools.search` al final de server.py
- Documentado en patrón de imports

✅ **3. Defaults Seguros**:
- `num_results=20` (vs 100 original)
- `debug=True` (vs False original)
- Documentado que producción puede override

### Impacto en Viabilidad

- **Tiempo estimado**: Reducido de 3-4h a 2.5-3h
- **Riesgos bloqueantes**: Eliminados (circular imports, stdio, CAPTCHA)
- **Complejidad MVP**: Reducida (3 verificaciones vs 6)
- **Determinismo**: 100% (debug mode elimina variables de red)

### Próximos Pasos

1. ✅ **Workplan rev-1 creado** en `./.claude/workplans/task-02/task-02-workplan-rev-1.md`
2. ⏳ **Pendiente aprobación de usuario**
3. ⏳ **Próximos pasos tras aprobación**:
   - Comenzar implementación siguiendo orden de tareas (T1 → T2 → T3)
   - Ejecutar smoke test checklist MVP (6 secciones)
   - Crear PR con screenshots opcionales
   - Marcar Fase 2 como completada en MCP_PLAN.md

**Pregunta para el usuario**: ¿Apruebas este plan revisado para comenzar la implementación de la Fase 2?
