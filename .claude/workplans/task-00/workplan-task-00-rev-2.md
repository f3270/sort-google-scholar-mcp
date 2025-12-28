# Plan de Trabajo: Task-00 - Fase 1 Core Refactoring

**Fecha de Creación**: 2025-12-28
**Versión**: rev-2
**Estado**: Pendiente de Aprobación
**Autor**: Claude Code
**Stack**: httpx (async) + Selenium + BeautifulSoup + Pydantic + uv (deps)

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | 2024-XX-XX | Plan inicial | Creación del workplan para Fase 1 |
| rev-1 | 2025-12-28 | (1) Eliminada sección "Estimación" con horas, (2) Actualizados comandos a `uv run`, (3) Agregado contexto de uv dependency management, (4) Alineación con CLAUDE.md actualizado | Migración a uv como package manager y aplicación de best practices (no time estimates) |
| rev-2 | 2025-12-28 | (1) Documentada eliminación de archivos obsoletos (conda_environment.yml, .bumpversion.cfg), (2) Actualizada sección de Contingencia sobre uv, (3) Agregado contexto de CI/CD actualizado (GitHub Actions + Dockerfile), (4) Smoke test checklist actualizado | Completada limpieza post-migración uv: archivos legacy eliminados, CI/CD completamente migrado |

---

## 1. Resumen Ejecutivo

**Objetivo**: Implementar los componentes fundamentales (core) para transformar el CLI monolítico `sortgs` en una arquitectura async modular que servirá como base para el MCP Server `sortgs-mcp`.

Esta tarea extrae y moderniza la lógica de scraping de `src/sortgs/sortgs.py` (implementación síncrona legacy) en dos componentes async reutilizables:

1. **ScholarSearcher** (`src/sortgs_mcp/core/scholar.py`): Clase async para búsqueda en Google Scholar
2. **SessionManager** (`src/sortgs_mcp/core/session.py`): Gestión de sesiones con persistencia JSON/CSV

**Componentes del sistema afectados**:
- MCP Core: `src/sortgs_mcp/core/scholar.py` (nuevo), `src/sortgs_mcp/core/session.py` (nuevo)
- Config: `src/sortgs_mcp/core/__init__.py` (actualizar exports)
- Dependencias: Reutiliza `models.py`, `parser.py`, `config.py` existentes

**Referencia a MCP_PLAN.md**: Esta tarea corresponde a **Fase 1 - Core Refactoring** del plan maestro.

**Alcance**:
- ✅ Implementación async de scraping (httpx como primera opción)
- ✅ Fallback síncrono a Selenium (ejecutado en thread con `asyncio.to_thread()`)
- ✅ Persistencia de sesiones (JSON metadata + CSV results)
- ✅ Reutilización de código existente (parser.py, models.py)
- ❌ NO incluye MCP Server (Fase 2)
- ❌ NO incluye PDF download/indexing (Fase 3-5)
- ❌ NO incluye RAG (Fase 6-7)

**Dependency Management**: Proyecto completamente migrado a **uv** como package manager oficial. Todos los comandos usan `uv run` para asegurar consistencia con virtualenv y lockfile (`uv.lock`).

**Limpieza completada (task-01)**:
- ✅ Eliminados: `conda_environment.yml`, `.bumpversion.cfg` (obsoletos)
- ✅ CI/CD actualizado: GitHub Actions workflows usan `astral-sh/setup-uv@v1`
- ✅ Dockerfile actualizado: Construye con `uv sync --frozen --no-dev`

---

## 2. Priorización del Alcance

### 🔴 MVP/CORE (Obligatorio)

**Criterio de éxito**: Los siguientes imports funcionan sin errores:

```python
from sortgs_mcp.core import ScholarSearcher, SessionManager
from sortgs_mcp.models import SearchParams
from sortgs_mcp.config import settings
```

**Funcionalidades core**:
- [x] **ScholarSearcher.build_url()**: Construir URLs de Google Scholar con parámetros
- [x] **ScholarSearcher.fetch_page()**: Fetch async con httpx + detección robot check
- [x] **ScholarSearcher.fetch_with_selenium()**: Fallback Selenium (sync en thread)
- [x] **ScholarSearcher.search()**: Orquestador async de búsqueda completa
- [x] **SessionManager.create_session()**: Generar UUID y directorios
- [x] **SessionManager.save_session()**: Persistir JSON + CSV
- [x] **SessionManager.load_session()**: Cargar desde disco
- [x] **SessionManager.list_sessions()**: Enumerar sesiones guardadas

**Componentes MVP**:
- `src/sortgs_mcp/core/scholar.py` (nuevo)
- `src/sortgs_mcp/core/session.py` (nuevo)
- `src/sortgs_mcp/core/__init__.py` (actualizar)

### 🟡 Enhanced (Si hay tiempo)

**Funcionalidades opcionales**:
- [ ] Logging estructurado con niveles (DEBUG/INFO/WARNING)
- [ ] Retry logic con tenacity para requests HTTP
- [ ] Validación exhaustiva de URLs de Google Scholar
- [ ] Unit tests con pytest y mocks

**Componentes Enhanced**:
- `tests/test_scholar.py`
- `tests/test_session.py`

### 🟢 Nice-to-Have (Futuras iteraciones)

**Para versiones posteriores**:
- [ ] Caching de resultados de scraping
- [ ] Metrics/telemetry de scraping (success rate, latency)
- [ ] Configuración dinámica de delays para rate limiting

**Justificación postponer**: Estas features agregan complejidad sin aportar valor directo al MVP. Se implementarán cuando el sistema completo (MCP + RAG) esté funcional y se identifiquen cuellos de botella reales.

### Plan de Reducción de Alcance

**Si se excede el progreso esperado:**

1. **Recorte Nivel 1**: Eliminar Enhanced completo (tests + logging avanzado) → Continuar con manual testing
2. **Recorte Nivel 2**: Simplificar SessionManager (solo create + save, postponer load/list) → Verificación manual con `ls` y `cat`
3. **Core absoluto inamovible**: ScholarSearcher funcionando end-to-end (build_url + fetch + search) + SessionManager básico (create + save)

---

## 3. Diseño Técnico

### Arquitectura Propuesta

**Patrón**: Migración de monolito síncrono a componentes async modulares.

**Diagrama de flujo (MVP)**:

```
User/MCP Client (Fase 2)
    ↓
ScholarSearcher.search(params: SearchParams)
    ↓
    ├─→ build_url(params, offset) → URL string
    ├─→ fetch_page(url) → HTML bytes
    │   ├─→ [SUCCESS] httpx.AsyncClient.get()
    │   └─→ [ROBOT CHECK] asyncio.to_thread(fetch_with_selenium)
    ├─→ parse_google_scholar_page(html) → list[dict]
    ├─→ Convert to Paper objects + calculate cit_per_year
    └─→ Sort by params.sort_by → Return list[Paper]
        ↓
SessionManager.save_session(session)
    ├─→ JSON metadata.json (session.model_dump_json())
    └─→ CSV results.csv (pandas.DataFrame)
```

**Componentes afectados**:

- **Scraping**: `src/sortgs_mcp/core/scholar.py` (nuevo)
- **Session Management**: `src/sortgs_mcp/core/session.py` (nuevo)
- **Models**: `src/sortgs_mcp/models.py` (existente, reutilizado)
- **Parser**: `src/sortgs_mcp/core/parser.py` (existente, reutilizado)
- **Config**: `src/sortgs_mcp/config.py` (existente, reutilizado para settings.data_dir)

### Consideraciones Específicas de MCP + RAG

**MCP Tools Affected**: ❌ No (Fase 2)

**Google Scholar Scraping**: ✅ Sí
- [x] Afecta lógica de scraping: Migración de requests sync a httpx async
- [x] Cambios en parsing HTML: No (reutiliza parser.py existente)
- [x] Requiere manejo de CAPTCHA: Sí (Selenium fallback en thread)
- [x] Cambios en rate limiting: No (reutiliza random delays existentes)

**Chunking Strategy**: ❌ No aplica (Fase 4)

**Embeddings**: ❌ No aplica (Fase 6)

**Retrieval**: ❌ No aplica (Fase 6-7)

**ChromaDB Collections**: ❌ No aplica (Fase 6)

**PDF Processing**: ❌ No aplica (Fase 3-5)

### Decisiones de Arquitectura

**Async vs Sync**:
- ScholarSearcher es 100% async (métodos con `async def`)
- Selenium es sync → ejecutado en `asyncio.to_thread(fetch_with_selenium)` para no bloquear event loop
- SessionManager es sync (IO bound pero simple, no justifica async para MVP)

**Selenium Global Instance**:
- Reutilizar patrón del código original: `driver` global inicializado lazy
- Justificación: Startup de ChromeDriver es costoso (~2-3s), reutilizar mejora latencia en casos de múltiples CAPTCHA

**Error Handling**:
- Robot check → Fallback graceful a Selenium
- CAPTCHA → Pausar con `input()` (solo CLI, en MCP se debe evitar searches que triggeren CAPTCHA)
- Session not found → Raise `FileNotFoundError` con mensaje claro

**Testing Strategy** (Enhanced, opcional):
- Debug mode: `ScholarSearcher(debug=True)` usa web.archive.org (determinístico)
- Manual testing: Ejecutar snippet de verificación (ver Sección 4)
- Unit tests: Postponer para Enhanced (no bloquean MVP)

### Decisiones Técnicas KISS

✅ **Reutilización de patrones existentes**:
- Parser.py ya implementado → NO reescribir parsing HTML
- Models.py ya implementado → NO crear nuevos modelos
- Config.py ya implementado → NO añadir nueva config

✅ **Evitar sobre-ingeniería**:
- NO crear capa de abstracción para HTTP client (httpx directo)
- NO implementar retry logic sofisticado en MVP (solo fallback Selenium)
- NO agregar logging avanzado (print/logging básico suficiente)

✅ **Solución más simple posible**:
- SessionManager usa JSON stdlib + pandas (ya en deps) → NO añadir DB (SQLite, etc.)
- Selenium global en módulo → NO crear singleton pattern complejo
- Dirs de sesión basados en UUID → NO usar timestamps complejos

---

## 4. Plan de Desarrollo

**Tareas ordenadas por prioridad y dependencia:**

| ID | Prioridad | Tarea | Criterios de Aceptación | Dependencias | Componentes |
|----|-----------|-------|-------------------------|--------------|-------------|
| T1 | 🔴 CORE | Implementar `ScholarSearcher.build_url()` | Genera URL correcta con params (keywords, year range, lang, debug mode) | - | `scholar.py` |
| T2 | 🔴 CORE | Implementar `ScholarSearcher.fetch_page()` | Fetch async con httpx, detecta robot check, retorna HTML bytes | T1 | `scholar.py` |
| T3 | 🔴 CORE | Implementar `ScholarSearcher.fetch_with_selenium()` | Selenium fallback funciona, CAPTCHA manual solving, retorna HTML bytes | - | `scholar.py` |
| T4 | 🔴 CORE | Integrar `fetch_with_selenium()` en `fetch_page()` | Robot check trigger fallback automático usando `asyncio.to_thread()` | T2, T3 | `scholar.py` |
| T5 | 🔴 CORE | Implementar `ScholarSearcher.search()` | Loop paginación, parsing, conversión a Paper, sorting, retorna list[Paper] | T4 | `scholar.py` |
| T6 | 🔴 CORE | Implementar `SessionManager.create_session()` | Genera UUID, crea dirs (sessions/{id}/, sessions/{id}/pdfs/) | - | `session.py` |
| T7 | 🔴 CORE | Implementar `SessionManager.save_session()` | Guarda metadata.json + results.csv correctamente | T6 | `session.py` |
| T8 | 🔴 CORE | Implementar `SessionManager.load_session()` | Carga session desde JSON, raise error si no existe | T7 | `session.py` |
| T9 | 🔴 CORE | Implementar `SessionManager.list_sessions()` | Retorna lista de dicts con metadata de todas las sesiones | T8 | `session.py` |
| T10 | 🔴 CORE | Actualizar `core/__init__.py` | Exporta ScholarSearcher, SessionManager, parser functions | T5, T9 | `__init__.py` |
| T11 | 🔴 CORE | Verificación manual (snippet) | Ejecuta búsqueda, guarda session, carga session → todo funciona | T10 | Manual testing |
| T12 | 🟡 Enhanced | Crear `tests/test_scholar.py` | Tests de build_url, search en debug mode | T11 | `test_scholar.py` |
| T13 | 🟡 Enhanced | Crear `tests/test_session.py` | Tests de create, save, load, list | T11 | `test_session.py` |

**Orden de implementación sugerido**: T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → T9 → T10 → T11 → (T12, T13 opcional)

---

## 5. Plan de Pruebas

### Estrategia de Testing

**MVP (Manual)**:
- Ejecutar snippet de verificación manual (Python REPL o script)
- Validar que imports funcionan
- Validar que search ejecuta y retorna papers
- Validar que session se guarda como JSON + CSV
- Inspeccionar archivos generados manualmente (`ls`, `cat`)

**Enhanced (Automatizado - Opcional)**:
- Unit tests con pytest
- Mocks de httpx responses
- Fixtures de HTML de Google Scholar (web archive)

### Casos de Prueba Principales

**ScholarSearcher**:
- [ ] `build_url()` genera URL correcta con keywords, year range, lang
- [ ] `build_url()` en debug mode wraps con web.archive.org
- [ ] `fetch_page()` ejecuta request con httpx sin robot check
- [ ] `fetch_page()` detecta robot check y llama Selenium fallback
- [ ] `fetch_with_selenium()` abre Chrome, espera body, retorna HTML
- [ ] `search()` itera páginas correctamente (offset 0, 10, 20...)
- [ ] `search()` parsea papers con parser.py existente
- [ ] `search()` convierte dicts a Paper objects
- [ ] `search()` calcula cit_per_year correctamente
- [ ] `search()` ordena por Citations o cit/year según params

**SessionManager**:
- [ ] `create_session()` genera UUID válido
- [ ] `create_session()` crea dirs sessions/{id}/ y sessions/{id}/pdfs/
- [ ] `save_session()` guarda metadata.json con schema correcto
- [ ] `save_session()` guarda results.csv con pandas (columnas: title, author, citations, year, etc.)
- [ ] `load_session()` carga session correctamente desde JSON
- [ ] `load_session()` raise FileNotFoundError con mensaje útil si no existe
- [ ] `list_sessions()` retorna lista de dicts con metadata de todas las sesiones

### Criterios de Calidad

**Mínimos aceptables**:
- Imports no fallan
- Search retorna al menos 1 paper (o 0 si query no tiene resultados)
- Session JSON es válido (pydantic valida correctamente)
- CSV tiene columnas esperadas

---

## 6. Smoke Test Checklist

**Propósito**: Checklist manual para ejecutar y validar MVP antes de pasar a Fase 2.

```markdown
**SMOKE TEST CHECKLIST - Task-00 Fase 1**

**Ejecutado por**: [Nombre]
**Fecha**: [YYYY-MM-DD]
**Ambiente**: Local Development
**Python**: >=3.10
**Package Manager**: uv

---

#### 1. Setup y Configuración

- [ ] **1.1** Dependencias instaladas (`uv sync`)
- [ ] **1.2** Virtual environment activado (uv automático con `uv run`)
- [ ] **1.3** ChromeDriver instalado y en PATH (`chromedriver --version` funciona)
- [ ] **1.4** `src/sortgs_mcp/` directory existe con models.py, config.py, parser.py
- [ ] **1.5** ✅ Archivos obsoletos eliminados: NO existen `conda_environment.yml` ni `.bumpversion.cfg`

**Nota**: Desde rev-2, el proyecto usa SOLO uv. Archivos legacy de conda/pip fueron eliminados (task-01).

---

#### 2. Imports (Criterio de Éxito MVP)

- [ ] **2.1** `from sortgs_mcp.core import ScholarSearcher` → No error
- [ ] **2.2** `from sortgs_mcp.core import SessionManager` → No error
- [ ] **2.3** `from sortgs_mcp.models import SearchParams, Paper, SearchSession` → No error
- [ ] **2.4** `from sortgs_mcp.config import settings` → No error

**Comando de prueba**:
```bash
uv run python -c "from sortgs_mcp.core import ScholarSearcher, SessionManager; print('✅ Imports OK')"
```

**Screenshot requerido**: Terminal mostrando "✅ Imports OK"
![Adjuntar aquí]

---

#### 3. ScholarSearcher - build_url()

- [ ] **3.1** URL con keywords se genera correctamente
- [ ] **3.2** URL con year range incluye `as_ylo` y `as_yhi`
- [ ] **3.3** Debug mode wraps URL con web.archive.org
- [ ] **3.4** Offset correcto en URL (start=0, start=10, etc.)

**Código de prueba**:
```python
from sortgs_mcp.core import ScholarSearcher
from sortgs_mcp.models import SearchParams

searcher = ScholarSearcher(debug=False)
params = SearchParams(keywords="machine learning", num_results=10, start_year=2020, end_year=2024)
url = searcher.build_url(params, offset=0)
print(url)
# Verificar: contiene "q=machine+learning", "as_ylo=2020", "as_yhi=2024"
```

**Screenshot requerido**: URL generada
![Adjuntar aquí]

---

#### 4. ScholarSearcher - search() (Debug Mode)

- [ ] **4.1** Search ejecuta sin errores en debug mode (web archive)
- [ ] **4.2** Retorna list[Paper] con al menos 1 paper
- [ ] **4.3** Papers tienen campos obligatorios (title, author, citations, year)
- [ ] **4.4** `cit_per_year` calculado correctamente
- [ ] **4.5** Papers ordenados por `sort_by` (Citations o cit/year)

**Código de prueba**:
```python
import asyncio
from sortgs_mcp.core import ScholarSearcher
from sortgs_mcp.models import SearchParams

async def test_search():
    searcher = ScholarSearcher(debug=True)  # usa web archive
    params = SearchParams(keywords="transformers", num_results=10, sort_by="Citations", debug=True)
    papers = await searcher.search(params)
    print(f"Found {len(papers)} papers")
    if papers:
        print(f"Top paper: {papers[0].title} ({papers[0].citations} cites)")
    return papers

papers = asyncio.run(test_search())
```

**Screenshot requerido**: Output mostrando papers encontrados
![Adjuntar aquí]

---

#### 5. ScholarSearcher - Selenium Fallback (Opcional, si no robot check en debug)

- [ ] **5.1** Robot check detectado (si aplica en live search)
- [ ] **5.2** Selenium fallback ejecuta automáticamente
- [ ] **5.3** ChromeDriver abre correctamente
- [ ] **5.4** CAPTCHA manual solving funciona (input() permite continuar)

**Código de prueba** (live search, puede trigger robot check):
```python
import asyncio
from sortgs_mcp.core import ScholarSearcher
from sortgs_mcp.models import SearchParams

async def test_selenium():
    searcher = ScholarSearcher(debug=False)  # live search
    params = SearchParams(keywords="quantum computing", num_results=5)
    papers = await searcher.search(params)
    print(f"Found {len(papers)} papers with Selenium fallback")
    return papers

papers = asyncio.run(test_selenium())
```

**Screenshot requerido**: Si Selenium se usa, screenshot de Chrome abierto
![Adjuntar aquí]

---

#### 6. SessionManager - create_session()

- [ ] **6.1** Session ID generado (UUID válido)
- [ ] **6.2** Directory `data/sessions/{session_id}/` creado
- [ ] **6.3** Directory `data/sessions/{session_id}/pdfs/` creado

**Código de prueba**:
```python
from sortgs_mcp.core import SessionManager
from sortgs_mcp.config import settings
from sortgs_mcp.models import SearchParams

manager = SessionManager(settings.data_dir)
params = SearchParams(keywords="test", num_results=10)
session_id = manager.create_session(params)
print(f"Session ID: {session_id}")
# Verificar con `ls data/sessions/{session_id}/`
```

**Screenshot requerido**: `ls` mostrando directorio creado
![Adjuntar aquí]

---

#### 7. SessionManager - save_session()

- [ ] **7.1** `metadata.json` guardado correctamente
- [ ] **7.2** JSON es válido (pydantic schema)
- [ ] **7.3** `results.csv` guardado si papers > 0
- [ ] **7.4** CSV tiene columnas correctas (title, author, citations, year, etc.)

**Código de prueba**:
```python
from sortgs_mcp.core import SessionManager, ScholarSearcher
from sortgs_mcp.models import SearchParams, SearchSession
from sortgs_mcp.config import settings
import asyncio

async def test_save():
    # Search
    searcher = ScholarSearcher(debug=True)
    params = SearchParams(keywords="neural networks", num_results=5, debug=True)
    papers = await searcher.search(params)

    # Create session
    manager = SessionManager(settings.data_dir)
    session_id = manager.create_session(params)

    # Save
    session = SearchSession(session_id=session_id, params=params, papers=papers)
    manager.save_session(session)
    print(f"Session saved: {session_id}")
    return session_id

session_id = asyncio.run(test_save())
# Verificar: `cat data/sessions/{session_id}/metadata.json`
# Verificar: `head data/sessions/{session_id}/results.csv`
```

**Screenshot requerido**: `cat metadata.json` y `head results.csv`
![Adjuntar aquí]

---

#### 8. SessionManager - load_session()

- [ ] **8.1** Session cargada correctamente desde JSON
- [ ] **8.2** Papers restaurados (count matches)
- [ ] **8.3** Params restaurados correctamente

**Código de prueba**:
```python
from sortgs_mcp.core import SessionManager
from sortgs_mcp.config import settings

manager = SessionManager(settings.data_dir)
session_id = "[session_id del paso anterior]"
loaded_session = manager.load_session(session_id)
print(f"Loaded session: {loaded_session.session_id}")
print(f"Papers: {len(loaded_session.papers)}")
print(f"Keywords: {loaded_session.params.keywords}")
```

**Screenshot requerido**: Output mostrando session cargada
![Adjuntar aquí]

---

#### 9. SessionManager - load_session() Error Handling

- [ ] **9.1** `FileNotFoundError` raised si session no existe
- [ ] **9.2** Error message es claro y útil

**Código de prueba**:
```python
from sortgs_mcp.core import SessionManager
from sortgs_mcp.config import settings

manager = SessionManager(settings.data_dir)
try:
    manager.load_session("nonexistent-uuid-12345")
except FileNotFoundError as e:
    print(f"✅ Error handled: {e}")
```

**Screenshot requerido**: Error message
![Adjuntar aquí]

---

#### 10. SessionManager - list_sessions()

- [ ] **10.1** Lista todas las sesiones guardadas
- [ ] **10.2** Retorna dicts con metadata correcta (session_id, keywords, created_at, papers_count, indexed)
- [ ] **10.3** No crashea si sessions/ está vacío

**Código de prueba**:
```python
from sortgs_mcp.core import SessionManager
from sortgs_mcp.config import settings

manager = SessionManager(settings.data_dir)
sessions = manager.list_sessions()
print(f"Found {len(sessions)} sessions:")
for s in sessions:
    print(f"  - {s['session_id']}: {s['keywords']} ({s['papers_count']} papers)")
```

**Screenshot requerido**: Lista de sesiones
![Adjuntar aquí]

---

#### 11. Code Quality

- [ ] **11.1** No hay print() innecesarios (usar logging o remover)
- [ ] **11.2** Type hints en funciones principales
- [ ] **11.3** Docstrings en clases y métodos públicos
- [ ] **11.4** No hay imports no utilizados
- [ ] **11.5** Código sigue PEP 8 (snake_case, etc.)

---

#### 12. Git y Documentación

- [ ] **12.1** Branch creado desde dev
- [ ] **12.2** Commits atómicos y descriptivos
- [ ] **12.3** CLAUDE.md actualizado (si cambios arquitectónicos) ✅ (ya actualizado en task-01)
- [ ] **12.4** Este checklist incluido en PR

---

**RESULTADO FINAL**

- [ ] ✅ **TODOS LOS TESTS PASAN** - MVP Fase 1 completado, listo para Fase 2
- [ ] ⚠️ **HAY ISSUES MENORES** - Documentar en PR
- [ ] ❌ **HAY ISSUES BLOQUEANTES** - No avanzar a Fase 2

**Notas adicionales**:
[Agregar observaciones, bugs encontrados, mejoras sugeridas]

---
```

---

## 7. Plan de Contingencia

### Punto de Decisión GO/NO-GO

**Cuándo verificar**: Después de completar T10 (todos los componentes core implementados)

**Criterio mínimo**:
- Imports funcionan (T10)
- `search()` retorna al menos 1 paper en debug mode (T5)
- `save_session()` guarda JSON + CSV sin errores (T7)

**Si criterio NO se cumple**:
1. Activar plan de reducción de alcance (Sección 2)
2. Si persiste: Evaluar bloqueo técnico (ver escenarios abajo)

### Escenarios de Bloqueo

**1. httpx async no funciona con Google Scholar (timeout, SSL errors)**:
- **Solución**: Usar requests sync como fallback (similar a código original)
- **Trade-off**: Perder beneficio de async en esta fase (aceptable, MCP server en Fase 2 seguirá siendo async)

**2. Selenium ChromeDriver no disponible/compatible**:
- **Solución**: Documentar workaround (instalar chromedriver manual, skip Selenium tests)
- **Trade-off**: Robot check no manejado → Documentar en README que debug mode es requerido para CI

**3. Parser.py existente tiene bugs no detectados**:
- **Solución**: Fix inline en parser.py, documentar en commit separado
- **Trade-off**: Scope creep mínimo (necesario para MVP)

**4. Pydantic models incompatibles con SessionManager**:
- **Solución**: Ajustar models.py según necesidad (backward compatible)
- **Trade-off**: Cambiar contrato de datos (documentar breaking change si aplica)

**5. uv sync falla en entorno local (deps conflictivas, permisos)**:
- **Solución**: Verificar uv.lock está actualizado con `uv lock --upgrade`, limpiar cache con `rm -rf .uv-cache`
- **Fallback alternativo**: Si persiste, usar `pip install -e .` (documentado en CLAUDE.md)
- **Trade-off**: Perder lockfile reproducibilidad temporalmente (aceptable para desarrollo local)
- **CI/CD**: GitHub Actions ya migrado completamente a uv (astral-sh/setup-uv@v1), fallos en CI requieren debug del workflow, no usar pip

**Nota importante (rev-2)**: El proyecto ahora tiene CI/CD completamente migrado a uv:
- `.github/workflows/test.yml` → usa `uv sync` + `uv run pytest`
- `.github/workflows/deploy-to-pypi.yml` → usa `uv build`
- `Dockerfile` → usa `uv sync --frozen --no-dev`

Por lo tanto, el escenario "uv sync falla" es menos probable en CI (configuración controlada) y más probable en ambientes locales no estándar.

---

## 8. Decisiones Técnicas TOMADAS

### 8.1 HTTP Client: httpx (async) vs requests (sync)

**Decisión TOMADA**: Usar **httpx** como primera opción, con **requests** disponible como fallback documentado.

**Justificación**:
- ✅ httpx soporta async/await nativo (necesario para MCP server en Fase 2)
- ✅ API casi idéntica a requests (migración trivial si falla)
- ✅ Ya en pyproject.toml (no añade nueva dependencia)

**Alternativas consideradas**:
- **Opción B (requests)**: Sync-only - Pro: Probado en código original, Contra: Requiere threading explícito en Fase 2
- **Opción C (aiohttp)**: Async pero API diferente - Pro: Popular, Contra: Nueva dependencia, curva aprendizaje

**Trade-off aceptado**: Complejidad leve de async/await en Fase 1 (manejable con asyncio.run())

**Principio KISS aplicado**: Reutilizamos httpx que ya está en deps, API similar a requests (0 curva aprendizaje)

---

### 8.2 Selenium Execution: Thread Pool vs Process Pool

**Decisión TOMADA**: Usar **asyncio.to_thread()** (thread pool stdlib)

**Justificación**:
- ✅ Selenium es IO-bound (no CPU-bound) → threads suficientes
- ✅ `asyncio.to_thread()` es stdlib (Python 3.9+) → 0 deps adicionales
- ✅ Overhead mínimo vs multiprocessing

**Alternativas consideradas**:
- **Opción B (multiprocessing)**: Process pool - Pro: Aislamiento total, Contra: Overhead alto, compartir estado complejo
- **Opción C (sync en mismo thread)**: Bloquear event loop - Pro: Simple, Contra: Bloquea async calls

**Trade-off aceptado**: GIL de Python (aceptable, Selenium es 99% IO)

**Principio KISS aplicado**: `asyncio.to_thread()` es una línea de código, 0 config

---

### 8.3 Session Persistence: JSON + CSV vs SQLite vs NoSQL

**Decisión TOMADA**: **JSON (metadata) + CSV (results)** usando stdlib + pandas

**Justificación**:
- ✅ Pydantic models → JSON serialization nativa (.model_dump_json())
- ✅ pandas → CSV export nativa (.to_csv())
- ✅ Human-readable (fácil debug con cat/less)
- ✅ 0 schema migrations (flexibilidad para cambios en models.py)

**Alternativas consideradas**:
- **Opción B (SQLite)**: DB relacional - Pro: Queries, ACID, Contra: Overhead, migrations, overkill para MVP
- **Opción C (pickle)**: Binary serialization - Pro: Rápido, Contra: No human-readable, inseguro, no versionable

**Trade-off aceptado**: No hay queries complejas (aceptable, list_sessions() itera filesystem)

**Principio KISS aplicado**: JSON + CSV son formatos universales, 0 setup, readable

**Plan de migración futura**: Si en Fase 8-9 necesitamos queries complejas (ej: "sessions con >100 papers indexados"), migrar a SQLite con Alembic. Migración trivial: `json.loads() → INSERT INTO`.

---

### 8.4 Testing Strategy MVP: Manual vs Automated

**Decisión TOMADA**: **Manual testing (smoke test checklist)** para MVP, unit tests en Enhanced

**Justificación**:
- ✅ Smoke test valida end-to-end rápidamente (5-10 min)
- ✅ Debug interactivo más fácil sin mocks
- ✅ MVP small (2 archivos, ~400 LOC) → tests automatizados son overkill

**Alternativas consideradas**:
- **Opción B (pytest desde inicio)**: TDD - Pro: Coverage, CI, Contra: Overhead setup, mocks de httpx/Selenium complejos
- **Opción C (no testing)**: YOLO - Pro: Rápido, Contra: Riesgoso, dificulta refactors

**Trade-off aceptado**: No hay CI automation en MVP (aceptable, agregaremos en Fase 2+ cuando MCP server esté listo)

**Principio KISS aplicado**: Manual testing = 0 setup, 0 mocks, debugging real

**Plan de migración futura**: En Fase 2 (MCP server), agregar pytest + GitHub Actions para CI. Prioritario: Tests de MCP tools (integration), no tanto de scholar.py (ya validado manualmente).

---

### 8.5 Logging Strategy: print() vs logging module vs structlog

**Decisión TOMADA**: **logging module (stdlib)** con configuración básica

**Justificación**:
- ✅ stdlib (0 deps)
- ✅ Niveles (DEBUG/INFO/WARNING/ERROR) útiles para debugging
- ✅ Configurable externamente (settings.log_level en config.py)

**Alternativas consideradas**:
- **Opción B (print())**: Simple - Pro: Rápido, Contra: No configurable, dificulta debugging
- **Opción C (structlog)**: Structured logging - Pro: JSON logs, Contra: Nueva dep, overkill para MVP

**Trade-off aceptado**: No hay structured logging (aceptable, añadiremos si MCP server requiere mejor observability)

**Principio KISS aplicado**: logging.basicConfig() en 2 líneas, suficiente para MVP

---

### 8.6 Dependency Management: pip vs poetry vs uv

**Decisión TOMADA**: **uv** como package manager oficial (migración completada)

**Justificación**:
- ✅ Fast resolver (Rust-based, 10-100x más rápido que pip)
- ✅ Lockfile (uv.lock) asegura reproducibilidad
- ✅ Compatibilidad con pyproject.toml (estándar PEP 621)
- ✅ Virtualenv management automático
- ✅ CI/CD completamente migrado (GitHub Actions + Dockerfile)

**Alternativas consideradas**:
- **Opción B (pip)**: Estándar - Pro: Universal, Contra: Slow resolver, no lockfile nativo
- **Opción C (poetry)**: All-in-one - Pro: Lock, deps groups, Contra: Slower, poetry.lock propietario

**Trade-off aceptado**: uv es relativamente nuevo (1.0 en 2024) → Fallback a pip documentado en CLAUDE.md para casos edge

**Principio KISS aplicado**: uv es drop-in replacement de pip (`uv sync` ≈ `pip install -e .`), 0 curva aprendizaje

**Estado actual (rev-2)**:
- ✅ Archivos legacy eliminados: `conda_environment.yml`, `.bumpversion.cfg`
- ✅ GitHub Actions workflows actualizados: usan `astral-sh/setup-uv@v1`
- ✅ Dockerfile actualizado: usa `uv sync --frozen --no-dev`
- ✅ README actualizado: instrucciones de instalación priorizan `uv sync`

**Plan de migración futura**: Si uv tiene bugs críticos, fallback a poetry o pip. Migration: pyproject.toml es estándar → portable.

---

## 9. Próximos Pasos (Post-MVP)

Una vez completada Fase 1 (Task-00), el siguiente paso es:

**Fase 2: MCP Server Skeleton (Task-02 o similar)**
- Crear `src/sortgs_mcp/server.py` con FastMCP o mcp SDK oficial
- Implementar tool `search_papers` usando ScholarSearcher + SessionManager
- Configurar en Claude Code (`~/.config/claude/mcp_config.json`)
- Smoke test: Invocar tool desde Claude chat

**Dependencias de Fase 1 para Fase 2**:
- ✅ ScholarSearcher funcional → Fase 2 lo envuelve en MCP tool
- ✅ SessionManager funcional → Fase 2 retorna session_id al user
- ✅ Models validados → Fase 2 usa mismos models para MCP schemas

---

## 10. Apéndices

### A. Referencias

- **Código original**: `src/sortgs/sortgs.py` (líneas 1-400)
- **Pydantic models**: `src/sortgs_mcp/models.py`
- **Parser HTML**: `src/sortgs_mcp/core/parser.py`
- **Config**: `src/sortgs_mcp/config.py`
- **uv documentation**: https://docs.astral.sh/uv/
- **httpx documentation**: https://www.python-httpx.org/
- **Selenium Python docs**: https://selenium-python.readthedocs.io/

### B. Glosario

- **MCP**: Model Context Protocol (protocol for Claude Code integration)
- **RAG**: Retrieval-Augmented Generation (LLM + vector search)
- **ChromaDB**: Embedded vector database (local, no cloud)
- **CAPTCHA**: Challenge-Response test (Google Scholar anti-bot)
- **Robot check**: Google Scholar detection de scraping (redirects to CAPTCHA)
- **Debug mode**: Uses web.archive.org snapshot (deterministic, no live scraping)
- **uv**: Fast Python package manager (Rust-based, Astral project)
- **httpx**: Async HTTP client (requests-compatible API)

### C. Comandos Útiles (uv-based)

```bash
# Sync dependencies (install + lock)
uv sync

# Run Python in project env
uv run python

# Run pytest
uv run pytest

# Run script
uv run python scripts/test_scholar.py

# Add new dependency
uv add <package>

# Update dependencies
uv lock --upgrade

# Remove dependency
uv remove <package>

# Show installed packages
uv pip list

# Clean uv cache (troubleshooting)
rm -rf .uv-cache

# Rebuild lock from scratch
uv lock --upgrade
```

### D. CI/CD Configuration (rev-2)

**GitHub Actions Workflows**:

1. **`.github/workflows/test.yml`**:
   - Usa `astral-sh/setup-uv@v1` con cache habilitado
   - Ejecuta `uv sync` para instalar dependencias
   - Ejecuta `uv run pytest` para tests
   - Ejecuta `uv run sortgs 'keyword' --debug` para CLI test

2. **`.github/workflows/deploy-to-pypi.yml`**:
   - Usa `astral-sh/setup-uv@v1`
   - Ejecuta `uv build` para crear wheel + sdist
   - Ejecuta `uv tool run twine upload dist/*` para publicar a PyPI

3. **`Dockerfile`**:
   - Copia binario `uv` desde imagen oficial (`ghcr.io/astral-sh/uv:latest`)
   - Copia `pyproject.toml` + `uv.lock` para build reproducible
   - Ejecuta `uv sync --frozen --no-dev` para instalar solo deps de producción
   - Entrypoint: `uv run sortgs`

**Debugging CI failures**:
- Check workflow logs en GitHub Actions tab
- Reproducir localmente con: `uv sync && uv run pytest`
- Si falla en CI pero funciona local: verificar Python version matrix (3.10, 3.11)

---

**FIN DEL WORKPLAN - TASK-00 REV-2**
