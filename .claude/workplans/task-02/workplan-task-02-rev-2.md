# Plan de Trabajo: Task-02 - Fase 2 MCP Server Skeleton

**Fecha de Creación**: 2025-12-28  
**Versión**: 1.2 (Rev-2)  
**Estado**: Pendiente de Aprobación  
**Autor**: Claude Code  
**Stack**: MCP (stdio) + ChromaDB (embedded) + Anthropic Claude + sentence-transformers + httpx + Selenium + PyMuPDF

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | 2025-12-28 | Plan inicial | Creación del workplan para Fase 2 - MCP Server Skeleton |
| 1.2 | 2025-12-28 | Ajustes KISS en logging, imports, manejo .env y CSV vacío | Incorporar feedback previo |

---

## Observaciones de revisión adicionales

- `Settings` requiere `anthropic_api_key` obligatorio; si no hay `.env` con la clave real, el servidor no arranca. Definir en el plan si se relajará el campo o se documenta como prerequisito estricto.
- `SessionManager.save_session` solo escribe `results.csv` cuando hay papers y no soporta `create_empty_csv`; si se quiere CSV vacío con headers, hay que extender esa función como parte del alcance.
- `pyproject.toml` ya declara `sortgs-mcp = sortgs_mcp.server:main`; hoy no existe `server.py`, así que crear el archivo con `main()` es necesario para que la instalación editable no quede rota.
- La versión de `mcp` en el proyecto es `>=1.25.0` (no 1.2); confirmar compatibilidad del uso de `FastMCP` y `mcp.run(transport="stdio")` con esa versión.

---

## 1. Resumen Ejecutivo

### Descripción General

Esta tarea implementa la **Fase 2 del MCP_PLAN.md**: crear un servidor MCP funcional con transporte stdio que expone un tool básico (`search_papers`) para buscar papers en Google Scholar. El servidor se integrará con Claude Code y permitirá ejecutar búsquedas académicas desde la interfaz conversacional de Claude.

La implementación reutiliza completamente los componentes desarrollados en la Fase 1 (ScholarSearcher, SessionManager, modelos Pydantic) y se enfoca en crear la capa de integración MCP que los expone como herramientas invocables.

### Alcance Principal

1. **Servidor MCP con stdio transport**: Punto de entrada ejecutable que se comunica con Claude Code vía stdio
2. **Tool `search_papers`**: Herramienta async que acepta parámetros de búsqueda, ejecuta scraping de Google Scholar, guarda sesión y retorna resumen
3. **Sistema de logging**: Configuración de logging a archivo + stderr para MCP debugging
4. **Testing manual**: Validación con MCP Inspector y Claude Code integration

### Componentes del Sistema MCP Afectados

- **MCP Tools**: Nuevo tool `search_papers` (primer tool del servidor)
- **Scraping**: Reutiliza `ScholarSearcher` de Fase 1 sin modificaciones
- **Session Management**: Reutiliza `SessionManager` de Fase 1 (posible ajuste menor para crear CSV vacío)
- **Models**: Reutiliza todos los modelos Pydantic existentes

### Referencia a MCP_PLAN.md

**Fase del MCP_PLAN.md**: Fase 2 - MCP Server Skeleton (página 554-669 del plan)

**Duración estimada**: 3-4 horas (según plan original)

**Dependencias**:
- ✅ Fase 0 completada (setup, config, models)
- ✅ Fase 1 completada (ScholarSearcher, SessionManager, parser)

**Entregables esperados**:
- ✅ Servidor MCP funcional con stdio transport
- ✅ Tool `search_papers` implementado y testeado
- ✅ Integración con Claude Code verificada
- ✅ Logging funcionando

### Estimación de Tiempo y Recursos

| Componente | Esfuerzo Estimado | Prioridad |
|------------|-------------------|-----------|
| Servidor MCP (`server.py`) | 1h | 🔴 CORE |
| Tool `search_papers` | 1h | 🔴 CORE |
| Testing con MCP Inspector | 0.5h | 🔴 CORE |
| Integración Claude Code | 0.5h | 🔴 CORE |
| Debugging y ajustes | 0.5-1h | 🔴 CORE |
| **TOTAL** | **3.5-4h** | |

**Recursos necesarios**:
- ✅ Dependencias ya instaladas (`mcp>=1.25.0` en pyproject.toml)
- ✅ Componentes de Fase 1 funcionales
- ⚠️ `.env` con `ANTHROPIC_API_KEY` (obligatorio salvo que se relaje `Settings`)
- ⚠️ MCP Inspector instalado para testing (`npm install -g @modelcontextprotocol/inspector`)
- ⚠️ Claude Code CLI configurado

---

## 2. Priorización del Alcance

### 🔴 MVP/CORE (Obligatorio)

**Criterio de éxito**: Servidor MCP funcional que permite ejecutar búsquedas de Google Scholar desde Claude Code, guardando sesiones y retornando resultados básicos.

**Funcionalidades core**:
- [x] Servidor MCP con stdio transport (`src/sortgs_mcp/server.py`)
- [x] Tool `search_papers` con parámetros básicos (keywords, num_results, sort_by)
- [x] Logging a archivo (`data/logs/sortgs_mcp.log`)
- [x] Validación de inputs con Pydantic
- [x] Integración con ScholarSearcher async
- [x] Persistencia de sesión con SessionManager
- [x] Output JSON con session_id, papers_found, top_5_titles, csv_path
- [x] Testing manual con MCP Inspector
- [x] Testing manual con Claude Code

**Componentes MVP**:
```
src/sortgs_mcp/
├── server.py          # NEW - Entry point MCP
└── tools/
    ├── __init__.py    # EXISTS (empty)
    └── search.py      # NEW - Tool search_papers
```

**Criterios de aceptación MVP**:
1. `python -m sortgs_mcp.server` arranca sin errores en stdio mode
2. MCP Inspector muestra el tool `search_papers` con schema correcto
3. Invocar tool con keywords devuelve session_id válido y papers
4. Session se guarda en `data/sessions/{session_id}/` con metadata.json y `results.csv` (si se espera CSV aun con 0 papers, ajustar `SessionManager.save_session` para generarlo)
5. Claude Code puede invocar el tool desde chat
6. Logs se escriben correctamente en `data/logs/sortgs_mcp.log`

### 🟡 Enhanced (Si hay tiempo)

**Funcionalidades que agregan valor pero no bloquean**:
- [ ] Error handling sofisticado con mensajes user-friendly
- [ ] Progress indicators en logs durante scraping largo
- [ ] Validación adicional de parámetros (ej: end_year >= start_year)
- [ ] Formateo de output con markdown para mejor UX en Claude Code
- [ ] Tool metadata enriquecida (descriptions, examples)

**Componentes Enhanced**: Mejoras en `search.py` y `server.py`

**Justificación postponer Enhanced**:
- Error handling básico (try/except + logging) es suficiente para MVP
- Validación de Pydantic ya cubre casos principales
- Formateo puede agregarse en fase posterior sin afectar funcionalidad

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

**Si se excede el tiempo estimado (>4h)**:

1. **Recorte Nivel 1** (eliminar Enhanced): Mantener error handling básico, sin progress indicators → Ahorro: 0.5h
2. **Recorte Nivel 2** (simplificar testing): Probar solo con MCP Inspector, postponer Claude Code integration → Ahorro: 0.5h
3. **Core absoluto inamovible**:
   - Servidor MCP con stdio
   - Tool `search_papers` básico funcional
   - Testing con MCP Inspector mínimo

**Punto de decisión**: Si después de 3h no hay tool funcional en MCP Inspector → Escalar a usuario para revisión de dependencias/setup.

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
│  - Logging setup             │
│  - Tool registry             │
└──────────────────────────────┘
       ↓ decorator @mcp.tool()
┌──────────────────────────────┐
│  tools/search.py             │
│  - search_papers()           │
│    ├── Validate params       │
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
2. **Session creation**: SessionManager crea UUID y directorios
3. **Search execution**: ScholarSearcher.search() ejecuta scraping async
4. **Session persistence**: SessionManager.save_session() guarda metadata.json + results.csv
5. **Output formatting**: Retorna dict con session_id, papers_found, top_5_titles, csv_path
6. **Error handling**: Try/except captura errores y logs para debugging

### Componentes Afectados

**Nuevos archivos**:
- `src/sortgs_mcp/server.py` - MCP server entry point
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

**Chunking Strategy**:
- [ ] ¿Afecta chunking? **No** - No se implementa en esta fase

**Embeddings**:
- [ ] ¿Cambios en embeddings? **No** - No se implementa en esta fase

**Retrieval**:
- [ ] ¿Cambios en retrieval? **No** - No se implementa en esta fase

**Prompt Engineering**:
- [ ] ¿Cambios en prompts? **No** - No se usa LLM en esta fase

**ChromaDB Collections**:
- [ ] ¿Cambios en collections? **No** - No se usa ChromaDB en esta fase

**PDF Processing**:
- [ ] ¿Cambios en PDF download? **No** - Se implementa en Fase 4
- [ ] ¿Cambios en PDF parsing? **No** - Se implementa en Fase 5

### Decisiones de Arquitectura MCP

**MCP Server Design**:
- [x] ¿Cambios en server.py? **Sí** - Crear desde cero
- **Transport**: stdio (fixed para Claude Code - no negociable)
- **Logging**:
  - FileHandler → `data/logs/sortgs_mcp.log` (DEBUG level, ruta fija)
  - StreamHandler → stderr explícito (WARNING level, no contaminar stdout que es usado por MCP stdio)
- **MCP Framework**: `mcp` SDK oficial >=1.25 con FastMCP helper

**Tool Design**:
- [x] ¿Tool es síncrono o asíncrono? **Asíncrono** - MCP soporta async, ScholarSearcher es async
- [x] ¿Requiere estado global? **Sí** - Singletons de SessionManager y Settings (instanciados en tools/search.py)
- [x] ¿Timeout considerado? **Sí** - httpx ya tiene timeout=30s, searches largas pueden tardar pero MCP no tiene timeout hard-coded

**Error Handling**:
- [x] Mensajes user-friendly: Try/except con logging.error() y re-raise con mensaje claro
- [x] Graceful degradation: Si falla parcialmente (ej: menos papers de lo esperado), retornar los que se obtuvieron
- [x] Logging apropiado:
  - INFO para progress (iniciando búsqueda, sesión creada, papers encontrados)
  - WARNING para issues no-bloqueantes (robot check, menos papers de lo esperado)
  - ERROR para fallos críticos (sin conexión, error de parsing)

**Testing Strategy**:
- [x] MCP Inspector testing: Manual invocation con diferentes parámetros
- [x] Claude Code integration testing: End-to-end desde chat
- [ ] Unit tests con mocks: **No prioritario en MVP** - dejar para Fase 8 (Testing)

### Decisiones Técnicas KISS

**¿Se reutilizan patrones existentes?**
- ✅ **Sí** - Reutilización completa de Fase 1 (ScholarSearcher, SessionManager)
- ✅ **Sí** - Logging pattern consistente con resto del proyecto
- ✅ **Sí** - Pydantic models para validación (patrón del proyecto)

**¿Se evita sobre-ingeniería?**
- ✅ **Sí** - No se crea abstracción de "ToolRegistry" o "ToolBase" (solo 1 tool por ahora)
- ✅ **Sí** - No se implementa sistema de plugins (YAGNI - You Aren't Gonna Need It)
- ✅ **Sí** - Logging simple con handlers built-in de Python

**¿Solución más simple posible?**
- ✅ **Sí** - FastMCP provee decorador `@mcp.tool()` que auto-registra (no necesitamos registro manual)
- ✅ **Sí** - Stdio transport es el más simple (no HTTP server, no sockets)
- ✅ **Sí** - Output como dict simple (MCP serializa automático a JSON)

**Justificación de simplicidad**:
Esta es la solución más simple porque:
1. **Delegación máxima a frameworks**: FastMCP maneja stdio, serialización, registro de tools
2. **Zero abstracciones nuevas**: Solo funciones async decoradas, no clases intermedias
3. **Reutilización total**: No se duplica lógica de Fase 1
4. **Config centralizada**: `settings` singleton evita pasar configs manualmente

---

## 4. Plan de Desarrollo

### Tareas Ordenadas por Prioridad

| ID | Prioridad | Tarea | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-----------|-------|-------------------------|--------------|----------|
| T1 | 🔴 CORE | Crear `server.py` con FastMCP setup y logging | - `python -m sortgs_mcp.server` arranca sin errores<br>- Logs se escriben en `data/logs/sortgs_mcp.log`<br>- Stderr muestra solo warnings/errors y stdout limpio | - | 0.5h |
| T2 | 🔴 CORE | Crear `tools/search.py` con tool `search_papers` básico | - Tool acepta parámetros (keywords, num_results, etc.)<br>- Integra ScholarSearcher y SessionManager<br>- Retorna dict con formato especificado | T1 | 1h |
| T3 | 🔴 CORE | Implementar error handling en `search_papers` | - Try/except captura HTTPError, ValueError, etc.<br>- Logs errors con traceback<br>- Re-raise con mensaje user-friendly | T2 | 0.5h |
| T4 | 🔴 CORE | Testing con MCP Inspector | - Tool aparece listado<br>- Invocación exitosa con keywords válidos<br>- Session guardada correctamente | T3 | 0.5h |
| T5 | 🔴 CORE | Integración con Claude Code | - `claude mcp add` exitoso<br>- Tool invocable desde chat<br>- Output legible en chat | T4 | 0.5h |
| T6 | 🟡 Enhanced | Mejorar mensajes de error y validación | - Validación end_year >= start_year<br>- Mensajes user-friendly (no stack traces) | T5 | 0.5h |
| T7 | 🟡 Enhanced | Agregar progress logging | - Logs informativos cada 10 papers<br>- "Searching page 1/10..." | T5 | 0.3h |

**Orden de implementación sugerido**: T1 → T2 → T3 → T4 → T5 → (opcional T6, T7)

### Detalles de Implementación por Tarea

#### T1: Crear `server.py`

**Archivo**: `src/sortgs_mcp/server.py`

**Pseudocódigo**:
```python
import logging
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from sortgs_mcp.config import settings


def setup_logging() -> logging.Logger:
    log_dir = Path(settings.data_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logfile = log_dir / "sortgs_mcp.log"

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[file_handler, stream_handler],
    )
    return logging.getLogger(__name__)


logger = setup_logging()
mcp = FastMCP("sortgs")

# Tools se registran automáticamente con @mcp.tool() en otros módulos


def main() -> None:
    """Entry point for MCP server."""
    # Import tools al final para evitar imports circulares
    from sortgs_mcp.tools import search  # noqa: F401

    logger.info("Starting Sort Google Scholar MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
```

**Criterios de aceptación**:
- `python -m sortgs_mcp.server` arranca y queda en espera (stdio mode)
- `data/logs/sortgs_mcp.log` se crea y contiene línea "Starting Sort Google Scholar MCP Server"
- No hay errores en stderr y stdout se mantiene limpio (solo stdio MCP)

#### T2: Crear `tools/search.py` con tool `search_papers`

**Archivo**: `src/sortgs_mcp/tools/search.py`

**Pseudocódigo**:
```python
import logging
from sortgs_mcp.server import mcp
from sortgs_mcp.config import settings
from sortgs_mcp.models import SearchParams, SearchSession
from sortgs_mcp.core.scholar import ScholarSearcher
from sortgs_mcp.core.session import SessionManager

logger = logging.getLogger(__name__)
session_manager = SessionManager(settings.data_dir)


@mcp.tool()
async def search_papers(
    keywords: str,
    num_results: int = 100,
    sort_by: str = "Citations",
    start_year: int | None = None,
    end_year: int | None = None,
    languages: list[str] | None = None,
    debug: bool = False,
) -> dict:
    """Search Google Scholar for papers and save results in a session."""
    logger.info("search_papers called", extra={"keywords": keywords, "num_results": num_results})

    params = SearchParams(
        keywords=keywords,
        num_results=num_results,
        sort_by=sort_by,
        start_year=start_year,
        end_year=end_year,
        languages=languages,
        debug=debug,
    )

    session_id = session_manager.create_session(params)
    logger.info("Created session", extra={"session_id": session_id})

    async with ScholarSearcher() as searcher:
        papers = await searcher.search(params)

    session = SearchSession(
        session_id=session_id,
        params=params,
        papers=papers,
        papers_count=len(papers),
    )
    session_manager.save_session(session)  # si se requiere CSV vacío, ajustar SessionManager para generar headers sin resultados
    logger.info("Session saved", extra={"session_id": session_id, "papers_found": len(papers)})

    top_5_titles = [p.title for p in papers[:5]]
    csv_path = str(settings.sessions_dir / session_id / "results.csv")
    return {
        "session_id": session_id,
        "papers_found": len(papers),
        "top_5_titles": top_5_titles,
        "csv_path": csv_path,
    }
```

**Nota importante**: Patrón fijo KISS para evitar imports circulares: `mcp` vive en `server.py`, `search.py` lo importa, y `server.main()` importa `tools` al final para registrar el decorador.

**Criterios de aceptación**:
- Tool registrado en MCP server
- Acepta parámetros correctos (incluye `debug` para usar páginas archivadas si no hay red)
- Retorna dict con formato esperado
- Session se guarda en filesystem y genera `results.csv` aun sin resultados

#### T3: Implementar error handling

**Modificaciones en `search.py`**:

```python
async def search_papers(...) -> dict:
    try:
        logger.info(f"search_papers called with keywords='{keywords}'...")

        # ... código existente ...

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise ValueError(f"Invalid parameters: {e}") from e

    except httpx.HTTPError as e:
        logger.error(f"HTTP error during search: {e}")
        raise RuntimeError(f"Failed to fetch results from Google Scholar: {e}") from e

    except Exception as e:
        logger.error(f"Unexpected error in search_papers: {e}", exc_info=True)
        raise RuntimeError(f"Search failed: {e}") from e
```

**Criterios de aceptación**:
- Errores se loguean con traceback completo
- Exceptions se re-lanzan con mensajes user-friendly
- Tool no crashea el servidor MCP

#### T4: Testing con MCP Inspector

**Comandos**:
```bash
# Instalar MCP Inspector (si no está)
npm install -g @modelcontextprotocol/inspector

# Ejecutar inspector
mcp inspect python -m sortgs_mcp.server
```

**Casos de prueba**:
1. **Test básico**: keywords="machine learning", num_results=10 (usar `debug=True` si no hay red)
2. **Test con filtros**: keywords="transformers", start_year=2017, end_year=2024, sort_by="cit/year"
3. **Test error**: keywords="" (vacío, debería fallar validación)

**Criterios de aceptación**:
- MCP Inspector muestra tool `search_papers` listado
- Schema muestra parámetros correctos (tipos, defaults)
- Invocación exitosa retorna session_id válido
- Verificar en filesystem: `data/sessions/{session_id}/metadata.json` y `results.csv` existen

#### T5: Integración con Claude Code

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
- No hay errores en `data/logs/sortgs_mcp.log`

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Unit tests**: No prioritario en MVP (dejar para Fase 8)

**Integration tests**: No prioritario en MVP (dejar para Fase 8)

**Manual testing**:
- **MCP Inspector**: Validación de tool registration, schema, y invocación standalone
- **Claude Code**: End-to-end testing desde chat conversacional

### Casos de Prueba Principales (MCP-specific)

**MCP Tools**:
- [x] Tool registrado correctamente en MCP server (verificar con MCP Inspector)
- [x] Tool schema válido (parámetros: keywords str, num_results int, etc.)
- [x] Tool invocable desde MCP Inspector
- [x] Tool invocable desde Claude Code
- [x] Error handling graceful (no crashes)

**Google Scholar Scraping**:
- [x] Search ejecuta sin robot check (num_results=10, delay suficiente)
- [ ] Selenium fallback funciona (si robot check) - difícil de forzar, test manual si ocurre
- [x] Parsing extrae todos los campos correctamente (verificar CSV)
- [x] CSV guardado con formato correcto (headers, data types)

**Session Management**:
- [x] Session ID es UUID válido
- [x] Directorios creados: `data/sessions/{session_id}/`, `data/sessions/{session_id}/pdfs/`
- [x] metadata.json contiene todos los campos (session_id, created_at, params, papers, papers_count)
- [x] results.csv contiene papers con todas las columnas
- [ ] Si no hay papers, results.csv igualmente existe con headers (requiere ajuste en `SessionManager.save_session`)

**Edge Cases**:
- [ ] keywords vacío → Debería fallar validación de Pydantic
- [ ] num_results=0 → Debería fallar validación (ge=10)
- [ ] num_results=5000 → Debería fallar validación (le=1000)
- [ ] end_year < start_year → **Enhanced** - No validado en MVP, pero no crashea
- [ ] Google Scholar sin resultados → Retorna lista vacía, no error

### Criterios de Calidad

**Funcionalidad**:
- Tool ejecuta búsquedas correctamente
- Session persiste en filesystem
- Output JSON es válido y completo

**Performance**:
- Búsqueda de 10 papers: <30 segundos
- Búsqueda de 100 papers: <3 minutos (depende de rate limiting)

**Logging**:
- INFO level captura flujo completo (inicio, progreso, fin)
- ERROR level captura excepciones con traceback
- No hay logs en stdout (contaminaría MCP stdio)

**UX en Claude Code**:
- Output del tool es comprensible (session_id, papers_found, top_5)
- Errores tienen mensajes claros (no stack traces técnicos)

---

## 6. Smoke Test Checklist (MCP-adapted)

**Propósito**: Checklist manual para ejecutar y adjuntar al PR como evidencia.

**Formato copiable para PR:**

```markdown
**SMOKE TEST CHECKLIST - Task-02 Fase 2 MCP Server Skeleton**

**Ejecutado por**: [Nombre]
**Fecha**: [YYYY-MM-DD]
**Ambiente**: Local Development
**MCP Server**: sortgs-mcp
**Data Directory**: ./data (local filesystem)

---

#### 1. Setup y Configuración

- [ ] **1.1** Dependencias instaladas (`pip list | grep mcp` muestra mcp>=1.25.0)
- [ ] **1.2** Estructura de directorios creada (data/sessions/ existe)
- [ ] **1.3** Fase 1 completada (ScholarSearcher, SessionManager existen y funcionan)
- [ ] **1.4** .env configurado (ANTHROPIC_API_KEY presente; si no se relaja `Settings`, es obligatorio)

---

#### 2. MCP Server Startup

- [ ] **2.1** Server arranca sin errores (`python -m sortgs_mcp.server` en terminal)
- [ ] **2.2** Log file creado (`ls data/logs/sortgs_mcp.log` existe)
- [ ] **2.3** Log contiene "Starting Sort Google Scholar MCP Server"
- [ ] **2.4** No hay errores en stderr al arrancar

**Screenshot requerido**: Terminal mostrando servidor arrancado
![Adjuntar aquí]

---

#### 3. MCP Inspector Connection

- [ ] **3.1** MCP Inspector instalado (`mcp --version` funciona)
- [ ] **3.2** Inspector conecta correctamente (`mcp inspect python -m sortgs_mcp.server`)
- [ ] **3.3** Tool `search_papers` aparece listado
- [ ] **3.4** Tool schema muestra parámetros correctos (keywords: string, num_results: number, etc.)

**Screenshot requerido**: MCP Inspector mostrando tool `search_papers` con schema
![Adjuntar aquí]

---

#### 4. Tool: search_papers - Test Básico

- [ ] **4.1** Invocar con keywords="machine learning", num_results=10 (usar `debug=True` si no hay red)
- [ ] **4.2** Tool retorna sin errores
- [ ] **4.3** Output contiene session_id (formato UUID)
- [ ] **4.4** papers_found >= 0 (esperado 10 en red real; 0 aceptable en debug)
- [ ] **4.5** top_5_titles es array con títulos válidos
- [ ] **4.6** csv_path apunta a archivo existente

**Input de prueba**:
```json
{
  "keywords": "machine learning",
  "num_results": 10
}
```

**Screenshot requerido**: Output del tool mostrando session_id y papers_found
![Adjuntar aquí]

---

#### 5. Tool: search_papers - Test con Filtros

- [ ] **5.1** Invocar con keywords="transformers", start_year=2017, end_year=2024, sort_by="cit/year"
- [ ] **5.2** Tool retorna sin errores
- [ ] **5.3** Papers filtrados por año (verificar CSV)
- [ ] **5.4** Papers ordenados por cit/year descendente

**Input de prueba**:
```json
{
  "keywords": "transformers",
  "num_results": 20,
  "sort_by": "cit/year",
  "start_year": 2017,
  "end_year": 2024
}
```

**Screenshot requerido**: Output del tool
![Adjuntar aquí]

---

#### 6. Session Persistence

- [ ] **6.1** Directorio `data/sessions/{session_id}/` existe
- [ ] **6.2** Archivo `metadata.json` existe y es JSON válido
- [ ] **6.3** metadata.json contiene: session_id, created_at, params, papers, papers_count
- [ ] **6.4** Archivo `results.csv` existe (aunque no haya papers, debe tener headers)
- [ ] **6.5** CSV tiene headers correctos (rank, title, authors, citations, year, ...)
- [ ] **6.6** Si hubo resultados, CSV contiene al menos 1 fila de paper

**Comando de verificación**:
```bash
SESSION_ID="<session_id del test 4>"
ls -la data/sessions/$SESSION_ID/
cat data/sessions/$SESSION_ID/metadata.json | jq .
head -5 data/sessions/$SESSION_ID/results.csv
```

**Screenshot requerido**: Output mostrando archivos y contenido
![Adjuntar aquí]

---

#### 7. Error Handling

- [ ] **7.1** Test con keywords vacío → Error de validación (Pydantic)
- [ ] **7.2** Test con num_results=0 → Error de validación (ge=10)
- [ ] **7.3** Test con num_results=5000 → Error de validación (le=1000)
- [ ] **7.4** Errors se loguean en `data/logs/sortgs_mcp.log`
- [ ] **7.5** Tool no crashea el servidor (puede seguir procesando requests)

**Inputs de prueba**:
```json
{"keywords": "", "num_results": 10}
{"keywords": "test", "num_results": 0}
{"keywords": "test", "num_results": 5000}
```

**Screenshot requerido**: Logs mostrando errores capturados
![Adjuntar aquí]

---

#### 8. Google Scholar Scraping (verificación indirecta)

- [ ] **8.1** Papers tienen citations > 0 (al menos top 5)
- [ ] **8.2** Papers tienen year válido (1900-2025)
- [ ] **8.3** Papers tienen authors no vacíos
- [ ] **8.4** Papers tienen source_url válido
- [ ] **8.5** Algunos papers tienen pdf_url (no todos, es opcional)

**Verificación**: Abrir CSV y revisar columnas

---

#### 9. Logging

- [ ] **9.1** `data/logs/sortgs_mcp.log` contiene logs de nivel INFO
- [ ] **9.2** Logs incluyen "search_papers called with keywords=..."
- [ ] **9.3** Logs incluyen "Created session: {uuid}"
- [ ] **9.4** Logs incluyen "Found X papers"
- [ ] **9.5** Logs incluyen "Session saved to ..."
- [ ] **9.6** No hay logs en stdout (verificar terminal)

**Comando de verificación**:
```bash
tail -50 data/logs/sortgs_mcp.log
```

**Screenshot requerido**: Logs mostrando flujo completo de búsqueda
![Adjuntar aquí]

---

#### 10. Claude Code Integration

- [ ] **10.1** Server registrado (`claude mcp add --transport stdio sortgs-mcp -- python -m sortgs_mcp.server`)
- [ ] **10.2** `claude mcp list` muestra sortgs-mcp como active
- [ ] **10.3** En chat, solicitar búsqueda ("Search for papers about neural networks")
- [ ] **10.4** Claude invoca el tool correctamente
- [ ] **10.5** Output es legible en chat (session_id, papers_found, top_5_titles)
- [ ] **10.6** No hay errores en chat

**Screenshot requerido**: Claude Code chat mostrando invocación exitosa del tool
![Adjuntar aquí]

---

#### 11. Code Quality

- [ ] **11.1** No hay print() olvidados (solo logging)
- [ ] **11.2** No hay debugger statements o breakpoints
- [ ] **11.3** Código sigue convenciones (snake_case, docstrings, type hints)
- [ ] **11.4** No hay imports no utilizados
- [ ] **11.5** Docstrings de tool son claros (Args, Returns)

---

#### 12. Documentation

- [ ] **12.1** `server.py` tiene docstrings
- [ ] **12.2** `search_papers` tiene docstring completo (descripción, Args, Returns)
- [ ] **12.3** pyproject.toml tiene entry point `sortgs-mcp = sortgs_mcp.server:main`
- [ ] **12.4** MCP_PLAN.md marcado como Fase 2 en progreso o completada

---

#### 13. Git y PR

- [ ] **13.1** Branch creado desde dev (`git branch` muestra task-02-fase-2 o similar)
- [ ] **13.2** Commits descriptivos ("feat: add MCP server skeleton", "feat: implement search_papers tool")
- [ ] **13.3** PR creado con título claro ("Task-02: Fase 2 - MCP Server Skeleton")
- [ ] **13.4** Screenshots adjuntos al PR
- [ ] **13.5** Smoke test checklist incluido en PR description

---

**RESULTADO FINAL**

- [ ] ✅ **TODOS LOS TESTS PASAN** - Feature lista para code review
- [ ] ⚠️ **HAY ISSUES MENORES** - Documentar en comentarios del PR
- [ ] ❌ **HAY ISSUES BLOQUEANTES** - No crear PR hasta resolverlos

**Notas adicionales**:
[Agregar observaciones, bugs encontrados, o mejoras sugeridas]

---
```

---

## 7. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Dependencias MCP no instaladas** | Baja | Alto | Verificar `pip list | grep mcp` antes de comenzar (esperado >=1.25). Reinstalar con `pip install -e .` si falta. |
| **FastMCP incompatible con patrón actual** | Media | Alto | Revisar docs de MCP >=1.25 para confirmar API. Alternativa: usar mcp.server.Server directamente (más verboso pero funcional). |
| **Google Scholar robot check** | Media | Medio | Usar num_results pequeño (10-20) en tests. Selenium fallback ya implementado en Fase 1. |
| **CAPTCHA manual bloquea testing** | Baja | Medio | Para testing, usar debug=True (web archive) que evita robot checks. |
| **Circular import entre server.py y tools/** | Media | Bajo | Patrón: tools importan `mcp` singleton de server, o definir tools directamente en server.py (menos modular pero funciona). |
| **Logging contamina stdout** | Baja | Alto | Verificar que StreamHandler solo escribe a stderr con nivel WARNING+. MCP stdio usa stdout exclusivamente. |
| **Claude Code no reconoce tool** | Baja | Alto | Verificar con MCP Inspector primero. Si Inspector funciona pero Claude Code no, revisar `claude mcp list` y reiniciar Claude. |

---

## 8. Plan de Contingencia

### Punto de Decisión GO/NO-GO

**Cuándo**: Después de 3 horas de desarrollo (75% del tiempo estimado)

**Verificar**:
- ✅ MVP al menos al 80% completado:
  - server.py funcional (arranca sin errores)
  - search_papers tool implementado
  - Testing con MCP Inspector exitoso (al menos 1 invocación funcional)

**Si no se cumple**:
1. Activar plan de reducción de alcance (eliminar Enhanced, simplificar testing)
2. Escalar a usuario para revisar:
   - Dependencias instaladas correctamente
   - Fase 1 funcional (ejecutar tests de Fase 1 si existen)
   - Ambiente de desarrollo configurado

### Escenarios de Bloqueo Comunes

#### 1. **FastMCP API incompatible / no funciona como se espera**

**Síntomas**: Decorador `@mcp.tool()` no registra tool, o `mcp.run()` falla

**Mitigación**:
1. Revisar docs oficiales de MCP >=1.25: https://github.com/modelcontextprotocol/python-sdk
2. Alternativa: Usar `mcp.server.Server` directamente (low-level API):
   ```python
   from mcp.server import Server
   server = Server("sortgs")

   @server.list_tools()
   async def list_tools():
       return [...]

   @server.call_tool()
   async def call_tool(name, arguments):
       if name == "search_papers":
           return await search_papers(**arguments)
   ```
3. Si ambos fallan: Consultar con usuario sobre versión exacta de `mcp` instalada

**Tiempo estimado de resolución**: 1 hora

#### 2. **Circular import entre server.py y tools/search.py**

**Síntomas**: `ImportError: cannot import name 'mcp' from partially initialized module`

**Mitigación**:
1. **Solución rápida**: Definir tool directamente en `server.py` (menos modular pero funcional)
2. **Solución estructural**: Usar patrón de registro diferido:
   ```python
   # server.py
   mcp = FastMCP("sortgs")

   # tools/search.py
   from sortgs_mcp.server import mcp  # Importa después de que mcp está definido

   @mcp.tool()
   async def search_papers(...):
       ...

   # server.py (al final)
   from sortgs_mcp.tools import search  # Importa módulo para ejecutar decoradores
   ```

**Tiempo estimado de resolución**: 30 minutos

#### 3. **Google Scholar robot check persistente en testing**

**Síntomas**: Selenium abre browser con CAPTCHA en cada request

**Mitigación**:
1. **Para testing inmediato**: Usar `debug=True` en SearchParams (usa web archive)
2. **Para tests reales**:
   - Reducir num_results a 10
   - Esperar 5-10 minutos entre tests
   - Usar VPN si disponible
3. **Solución manual CAPTCHA**: Resolver manualmente cuando aparezca (workflow de Selenium ya implementado)

**Tiempo estimado de resolución**: 0 (workaround inmediato con debug mode)

#### 4. **Claude Code no reconoce servidor MCP**

**Síntomas**: `claude mcp list` muestra servidor pero status=inactive, o no aparece

**Mitigación**:
1. Verificar que servidor arranca sin errores standalone (`python -m sortgs_mcp.server`)
2. Verificar MCP Inspector funciona (si Inspector funciona, problema es con Claude Code config)
3. Revisar comando de registro:
   ```bash
   claude mcp add --transport stdio sortgs-mcp -- python -m sortgs_mcp.server
   ```
4. Reiniciar Claude Code CLI: `claude mcp restart sortgs-mcp`
5. Verificar logs de Claude Code (ubicación depende de instalación)

**Tiempo estimado de resolución**: 30 minutos

#### 5. **Logs contaminan stdout y rompen MCP stdio**

**Síntomas**: MCP Inspector muestra errores de deserialización JSON, Claude Code no puede parsear respuestas

**Mitigación**:
1. Verificar configuración de logging:
   - FileHandler → `data/logs/sortgs_mcp.log` (DEBUG level)
   - StreamHandler → stderr only (WARNING+ level)
2. NO usar `print()` en código (solo `logger.info/warning/error()`)
3. Verificar que StreamHandler no escribe a stdout:
   ```python
   import sys
   handler = logging.StreamHandler(sys.stderr)  # Explícitamente stderr
   ```

**Tiempo estimado de resolución**: 15 minutos

---

## 9. Decisiones Técnicas TOMADAS

### 9.1 Framework MCP: FastMCP vs Server Low-Level

**Decisión TOMADA**: FastMCP (high-level helper)

**Justificación**:
- ✅ **Simplicidad**: Decorador `@mcp.tool()` registra automáticamente (no necesitamos implementar list_tools/call_tool manualmente)
- ✅ **Menos boilerplate**: FastMCP maneja serialización JSON, validación de parámetros
- ✅ **Documentación**: FastMCP es el enfoque recomendado en docs oficiales de MCP >=1.25
- ✅ **Type hints**: FastMCP genera schema automático de type hints de función

**Alternativas consideradas**:
- **Opción B: Server low-level**
  - Pro: Mayor control sobre serialización, manejo de errores
  - Contra: Más código boilerplate, necesitamos implementar list_tools/call_tool manually
  - Contra: No genera schema automático de type hints

**Trade-off aceptado**: Menos control granular sobre MCP protocol, pero código mucho más simple

**Principio KISS aplicado**: FastMCP es el wrapper más simple que expone tools con mínimo código

**Plan de migración futura**: Si necesitamos mayor control (ej: streaming responses, custom serialization), migrar a Server low-level es straightforward (misma API, solo más verboso)

---

### 9.2 Ubicación de Tool: tools/search.py vs server.py

**Decisión TOMADA**: `tools/search.py` (módulo separado)

**Justificación**:
- ✅ **Modularidad**: Fase 3-7 agregarán más tools (download, index, query) → mejor separación desde ahora
- ✅ **Testing**: Tools en módulos separados son más fáciles de unit test (importar tool sin arrancar servidor)
- ✅ **Escalabilidad**: Patrón consistente para futuros tools
- ✅ **Single Responsibility**: `server.py` solo setup, `tools/` solo lógica de negocio

**Alternativas consideradas**:
- **Opción B: Todo en server.py**
  - Pro: No hay riesgo de circular import
  - Pro: Más simple para 1 solo tool
  - Contra: server.py crece rápidamente con más tools (anti-pattern)
  - Contra: Dificulta testing unitario

**Trade-off aceptado**: Potencial circular import (manejable con patrón de importación correcta)

**Principio KISS aplicado**: Para 1 tool, todo en server.py sería más simple. Pero para 6 tools (objetivo del proyecto), separación es más simple a largo plazo.

**Plan de migración futura**: Si circular import es problemático, consolidar temporalmente en server.py y refactorizar después

---

### 9.3 Logging: Nivel y Handlers

**Decisión TOMADA**:
- FileHandler → `data/logs/sortgs_mcp.log`, nivel DEBUG (todo)
- StreamHandler → stderr, nivel WARNING (solo critical)

**Justificación**:
- ✅ **MCP stdio requirement**: stdout es exclusivo para MCP protocol → no podemos contaminar con logs
- ✅ **Debugging completo**: FileHandler con DEBUG captura flujo completo para troubleshooting en ruta estable
- ✅ **Usuario ve solo critical**: stderr con WARNING muestra solo errores importantes sin ruido
- ✅ **Separation of concerns**: Logs de desarrollo (archivo) vs logs de producción (stderr)

**Alternativas consideradas**:
- **Opción B: Solo FileHandler, sin StreamHandler**
  - Pro: Cero riesgo de contaminar stdout
  - Contra: Desarrollador no ve errores críticos en tiempo real (necesita abrir archivo)
  - Contra: Dificulta debugging interactivo

- **Opción C: StreamHandler a stdout con nivel INFO**
  - Pro: Logs visibles en consola
  - Contra: ROMPE MCP STDIO (bloqueante, no negociable)

**Trade-off aceptado**: Desarrollador necesita abrir `data/logs/sortgs_mcp.log` para ver logs detallados (no ve en terminal)

**Principio KISS aplicado**: Configuración estándar de Python logging, sin abstracciones custom

**Plan de migración futura**: Si necesitamos logs estructurados (JSON), agregar JSONFormatter en FileHandler

---

### 9.4 Validación de Parámetros: Pydantic vs Manual

**Decisión TOMADA**: Pydantic models (SearchParams)

**Justificación**:
- ✅ **Reutilización**: SearchParams ya existe en Fase 1 → cero código nuevo
- ✅ **Validación automática**: Pydantic valida types, ranges (ge, le), Literal enums
- ✅ **Error messages**: Pydantic genera mensajes de error claros automáticamente
- ✅ **Schema generation**: MCP puede generar tool schema desde Pydantic models (futuro)

**Alternativas consideradas**:
- **Opción B: Validación manual con if/else**
  - Pro: Más control sobre mensajes de error
  - Contra: Código boilerplate (validar num_results >= 10, <= 1000, etc.)
  - Contra: Duplica validación ya existente en SearchParams

**Trade-off aceptado**: Ninguno (Pydantic es win-win)

**Principio KISS aplicado**: Reutilizar modelo existente es más simple que escribir validación nueva

**Plan de migración futura**: No necesaria

---

### 9.5 Error Handling: Re-raise vs Wrap

**Decisión TOMADA**: Wrap exceptions con mensajes user-friendly y re-raise

**Justificación**:
- ✅ **UX en Claude Code**: Usuario ve mensaje claro ("Failed to fetch results from Google Scholar") no stack trace técnico
- ✅ **Debugging**: `from e` preserva stack trace original en logs (debugging sigue siendo posible)
- ✅ **Context preservation**: Logging con `exc_info=True` guarda traceback completo en archivo
- ✅ **MCP error handling**: MCP serializa exception message para mostrar en cliente

**Alternativas consideradas**:
- **Opción B: Re-raise directo (sin wrap)**
  - Pro: Stack trace completo visible para usuario
  - Contra: Usuario ve errores técnicos (httpx.ConnectTimeout, etc.) que no entiende
  - Contra: Mala UX en chat conversacional

- **Opción C: Catch all y retornar error dict**
  - Pro: Tool nunca falla (siempre retorna dict)
  - Contra: Cliente MCP no sabe que hubo error (necesita parsear dict manualmente)
  - Contra: Anti-pattern (exceptions son la forma correcta de señalar errores)

**Trade-off aceptado**: Stack traces técnicos solo visibles en logs, no en chat (puede confundir a usuario técnico que prefiere ver detalles)

**Principio KISS aplicado**: Try/except estándar de Python, no framework custom de error handling

**Plan de migración futura**: Si necesitamos error codes específicos, agregar custom exception hierarchy

---

### 9.6 Tool Output: Modelo Pydantic vs Dict

**Decisión TOMADA**: Dict simple (sin modelo Pydantic)

**Justificación**:
- ✅ **Simplicidad**: MCP serializa dict a JSON automáticamente
- ✅ **Flexibilidad**: Fácil de modificar estructura sin crear modelo nuevo
- ✅ **No over-engineering**: Output es simple (session_id, papers_found, top_5, csv_path) no requiere validación

**Alternativas consideradas**:
- **Opción B: Crear modelo `SearchPapersResult`**
  - Pro: Type safety en return value
  - Pro: Validación de output (garantiza campos requeridos)
  - Contra: Boilerplate extra (definir modelo, importar, convertir a dict con .model_dump())
  - Contra: YAGNI (You Aren't Gonna Need It) - output es para consumo inmediato, no persistencia

**Trade-off aceptado**: No hay validación de output (si olvidamos un campo, error en runtime)

**Principio KISS aplicado**: Dict es la estructura de datos más simple para JSON serialization

**Plan de migración futura**: Si agregamos más tools con outputs complejos, crear modelos compartidos

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

### Notas Adicionales

**Patrón de Importación para Evitar Circular Import**:

```
Archivo server.py:
  1. Importa FastMCP y settings, configura logging en data/logs
  2. Crea instancia mcp = FastMCP("sortgs")
  3. En main(), importa módulos de tools: from sortgs_mcp.tools import search
  4. main() llama mcp.run()

Archivo tools/search.py:
  1. Importa config, models, core components
  2. Importa mcp desde sortgs_mcp.server (ya inicializado)
  3. Tools se registran cuando server.py importa el módulo (decoradores se ejecutan)

Alternativa: Usar mcp global en tools/__init__.py
```

**Ejemplo de Estructura Final**:

```
src/sortgs_mcp/
├── server.py          # FastMCP instance, logging setup, main()
├── config.py          # Settings (ya existe)
├── models.py          # Pydantic models (ya existe)
├── core/
│   ├── scholar.py     # ScholarSearcher (ya existe)
│   ├── session.py     # SessionManager (ya existe)
│   └── parser.py      # HTML parsing (ya existe)
└── tools/
    ├── __init__.py    # Vacío o mcp instance global
    └── search.py      # Tool search_papers

data/
└── logs/
    └── sortgs_mcp.log
└── sessions/
    └── {uuid}/
        ├── metadata.json
        ├── results.csv
        └── pdfs/         # Vacío hasta Fase 4
```

---

**FIN DEL WORKPLAN**

---

## Acciones Finales Requeridas

1. ✅ **Plan creado** en `.claude/workplan/task-02/task-02-workplan.md`
2. ⏳ **Pendiente aprobación de usuario**
3. ⏳ **Próximos pasos tras aprobación**:
   - Comenzar implementación siguiendo orden de tareas (T1 → T2 → T3 → T4 → T5)
   - Ejecutar smoke test checklist
   - Crear PR con screenshots y checklist
   - Marcar Fase 2 como completada en MCP_PLAN.md

**Pregunta para el usuario**: ¿Apruebas este plan para comenzar la implementación de la Fase 2?
