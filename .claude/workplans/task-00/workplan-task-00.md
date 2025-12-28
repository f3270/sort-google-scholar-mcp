# Plan: Implementar Fase 1 - Core Refactoring (sortgs_mcp)

## Contexto

El proyecto sortgs_mcp busca transformar el CLI sortgs en un MCP Server con capacidades RAG.

**Estado actual (~10% completo):**
- ✅ Fase 0: Setup completado (config, models, parser, dependencias)
- ❌ Fases 1-9: Por implementar

**Este plan:** Implementar Fase 1 completa para tener la base funcional de scraping y gestión de sesiones.

---

## Objetivo de Fase 1

Extraer y modernizar la lógica de scraping de `src/sortgs/sortgs.py` en componentes async reutilizables:

1. **ScholarSearcher** (src/sortgs_mcp/core/scholar.py): Clase async para buscar en Google Scholar
2. **SessionManager** (src/sortgs_mcp/core/session.py): Gestión de sesiones con persistencia JSON

---

## Archivos a Crear

### 1. `src/sortgs_mcp/core/scholar.py`

**Clase: `ScholarSearcher`**

Responsabilidades:
- Construir URLs de Google Scholar con parámetros (keywords, año, idioma)
- Fetch async con httpx (primera opción)
- Fallback a Selenium cuando Google Scholar bloquea (CAPTCHA detection)
- Parsear resultados usando `parse_google_scholar_page()` de parser.py
- Retornar lista de objetos `Paper`

**Métodos clave:**
```python
class ScholarSearcher:
    def __init__(self, debug: bool = False)
    def build_url(self, params: SearchParams, offset: int = 0) -> str
    async def fetch_page(self, url: str) -> bytes
    def fetch_with_selenium(self, url: str) -> bytes  # sync, run in thread
    async def search(self, params: SearchParams) -> list[Paper]
```

**Detalles de implementación:**

- **`build_url()`**:
  - Base: `https://scholar.google.com/scholar?start={offset}&q={keywords}&hl=en&as_sdt=0,5`
  - Añadir `&as_ylo={start_year}` si start_year
  - Añadir `&as_yhi={end_year}` si end_year
  - Añadir `&lr={lang}` si languages
  - Si debug=True: wrap con `https://web.archive.org/web/20210314203256/`

- **`fetch_page()`**:
  - Usar `httpx.AsyncClient.get(url, timeout=30)`
  - Detectar robot check buscando keywords en HTML response
  - Si detectado → llamar `fetch_with_selenium()` en `asyncio.to_thread()`
  - Random sleep (0.5-3s) después de cada request para evitar rate limit
  - Return bytes del HTML

- **`fetch_with_selenium()`**:
  - Setup Selenium ChromeDriver (lazy init, reusar global instance)
  - `driver.get(url)`
  - WebDriverWait hasta que body esté presente
  - Detectar CAPTCHA → pausar con input("Solve CAPTCHA and press Enter")
  - Return `driver.page_source.encode()`
  - **IMPORTANTE**: Ejecutar en `asyncio.to_thread()` desde caller porque no es async

- **`search()`**:
  - Loop offset: 0, 10, 20, ... hasta alcanzar `params.num_results`
  - Para cada página:
    - `url = self.build_url(params, offset)`
    - `html = await self.fetch_page(url)`
    - `papers_data = parse_google_scholar_page(html)` (del parser.py existente)
    - Convertir cada dict a objeto `Paper` (del models.py existente)
    - Calcular `cit_per_year = citations / (2024 - year + 1)` si year > 0
    - Asignar rank incremental
  - Ordenar papers por `params.sort_by` ("Citations" o "cit/year")
  - Return lista completa de Papers

**Dependencias externas:**
- `httpx` para async HTTP
- `selenium` (mantener del código original)
- `beautifulsoup4` (ya usado en parser.py)
- `random`, `asyncio`, `logging`

**Imports de proyecto:**
```python
from sortgs_mcp.models import SearchParams, Paper
from sortgs_mcp.core.parser import parse_google_scholar_page
```

---

### 2. `src/sortgs_mcp/core/session.py`

**Clase: `SessionManager`**

Responsabilidades:
- Crear nuevas sesiones de búsqueda (generar UUID)
- Guardar sesiones como JSON + CSV
- Cargar sesiones existentes
- Listar todas las sesiones

**Métodos clave:**
```python
class SessionManager:
    def __init__(self, data_dir: Path)
    def create_session(self, params: SearchParams) -> str
    def save_session(self, session: SearchSession) -> None
    def load_session(self, session_id: str) -> SearchSession
    def list_sessions(self) -> list[dict]
```

**Detalles de implementación:**

- **`__init__()`**:
  - `self.sessions_dir = data_dir / "sessions"`
  - Crear directorio si no existe: `sessions_dir.mkdir(parents=True, exist_ok=True)`

- **`create_session()`**:
  - Generar UUID: `session_id = str(uuid.uuid4())`
  - Crear directorio de sesión: `self.sessions_dir / session_id`
  - Crear subdirectorio: `self.sessions_dir / session_id / "pdfs"`
  - Return session_id

- **`save_session()`**:
  - Path base: `session_path = self.sessions_dir / session.session_id`
  - Guardar metadata JSON:
    ```python
    metadata_path = session_path / "metadata.json"
    metadata_path.write_text(session.model_dump_json(indent=2))
    ```
  - Guardar CSV con pandas:
    ```python
    if session.papers:
        df = pd.DataFrame([p.model_dump() for p in session.papers])
        csv_path = session_path / "results.csv"
        df.to_csv(csv_path, index=False)
    ```

- **`load_session()`**:
  - Leer `metadata.json`:
    ```python
    metadata_path = self.sessions_dir / session_id / "metadata.json"
    json_data = metadata_path.read_text()
    return SearchSession.model_validate_json(json_data)
    ```
  - Raise `FileNotFoundError` si no existe con mensaje útil

- **`list_sessions()`**:
  - Iterar directorios en `self.sessions_dir`
  - Para cada directorio que tenga `metadata.json`:
    - Cargar sesión con `load_session()`
    - Extraer: session_id, keywords, created_at, papers_count, pdfs_downloaded, indexed
  - Return lista de dicts

**Dependencias:**
- `pathlib.Path`
- `uuid`
- `pandas` (para CSV export)
- `json`

**Imports de proyecto:**
```python
from sortgs_mcp.models import SearchParams, SearchSession
```

---

### 3. Actualizar `src/sortgs_mcp/core/__init__.py`

Exportar las nuevas clases:
```python
from sortgs_mcp.core.scholar import ScholarSearcher
from sortgs_mcp.core.session import SessionManager
from sortgs_mcp.core.parser import (
    get_citations,
    get_year,
    get_author,
    get_pdf_link,
    parse_google_scholar_page
)

__all__ = [
    "ScholarSearcher",
    "SessionManager",
    "get_citations",
    "get_year",
    "get_author",
    "get_pdf_link",
    "parse_google_scholar_page",
]
```

---

## Archivos Críticos Existentes (para referencia)

- **src/sortgs_mcp/models.py**: Modelos `Paper`, `SearchParams`, `SearchSession` ya completos
- **src/sortgs_mcp/core/parser.py**: Funciones de parsing HTML ya implementadas
- **src/sortgs_mcp/config.py**: Configuración con `settings.data_dir`, `settings.sessions_dir`
- **src/sortgs/sortgs.py**: Código original de referencia (líneas 1-400)

---

## Testing (Opcional pero Recomendado)

Crear tests básicos para validar:

**tests/test_scholar.py:**
- Test `build_url()` con varios SearchParams
- Test `search()` en debug mode (usa web archive, determinístico)

**tests/test_session.py:**
- Test `create_session()` crea directorio
- Test `save_session()` y `load_session()` roundtrip
- Test `list_sessions()` retorna sesiones correctas

---

## Criterios de Éxito

✅ Fase 1 estará completa cuando:

1. ✅ `ScholarSearcher` puede buscar papers en Google Scholar (async)
2. ✅ `ScholarSearcher` tiene fallback a Selenium funcionando
3. ✅ `SessionManager` puede crear, guardar y cargar sesiones
4. ✅ Las sesiones se persisten como JSON + CSV correctamente
5. ✅ No hay errores de import al ejecutar `from sortgs_mcp.core import ScholarSearcher, SessionManager`

**Verificación manual:**
```python
from sortgs_mcp.core import ScholarSearcher, SessionManager
from sortgs_mcp.models import SearchParams
from sortgs_mcp.config import settings

# Test search
params = SearchParams(keywords="machine learning", num_results=10, debug=True)
searcher = ScholarSearcher(debug=True)
papers = await searcher.search(params)
print(f"Found {len(papers)} papers")

# Test session
manager = SessionManager(settings.data_dir)
session_id = manager.create_session(params)
from sortgs_mcp.models import SearchSession
session = SearchSession(session_id=session_id, params=params, papers=papers)
manager.save_session(session)
loaded = manager.load_session(session_id)
print(f"Session saved and loaded: {loaded.session_id}")
```

---

## Próximos Pasos (Después de Fase 1)

Una vez completada Fase 1, el siguiente paso natural es:

**Fase 2: MCP Server Skeleton**
- Crear `src/sortgs_mcp/server.py` con FastMCP
- Implementar tool `search_papers` usando ScholarSearcher + SessionManager
- Configurar en Claude Code y verificar funcionamiento

---

## Notas Importantes

1. **Async vs Sync**: ScholarSearcher es async, pero Selenium es sync → usar `asyncio.to_thread()`
2. **Selenium global**: Reusar driver instance para eficiencia (como en código original)
3. **Rate limiting**: Random delays entre requests para evitar blocks
4. **Debug mode**: Usar web archive para testing determinístico
5. **Backward compat**: El paquete `sortgs` original NO se modifica

---

## Estimación

**Tiempo estimado:** 6-8 horas

- ScholarSearcher: 3-4h (async logic, Selenium integration, testing)
- SessionManager: 2-3h (JSON/CSV persistence, error handling)
- Testing y debugging: 1-2h
