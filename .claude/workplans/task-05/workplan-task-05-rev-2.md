# Workplan: Fase 4 - PDF Download (Revisión 2)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 4: Descarga asíncrona de PDFs de papers académicos |
| **Task ID** | task-05-fase-4 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.2 (rev-2) |
| **Estado** | Listo para Implementación |
| **Autor** | Claude Code (Coordinador de Planificación) |
| **Stack principal** | Python 3.13, httpx, aiofiles, tenacity, MCP SDK |
| **Fase MCP_PLAN** | Fase 4 (líneas 839-966 de MCP_PLAN.md) |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Crear workplan para Fase 4 | Usuario |
| 1.1 (rev-1) | 2025-12-29 | Mejoras post-revisión con codex | Alinear validación PDF, ajustar plan de reducción, completar ciclo de vida async, añadir testabilidad offline | Codex + Usuario |
| 1.2 (rev-2) | 2025-12-29 | Refinamiento final | Definir modelo PDFDownloadResult explícitamente, alinear plan de contingencia con context manager, formalizar metadatos de descarga, añadir criterio max_concurrent_downloads | Codex + Usuario |

---

## 1. Resumen Ejecutivo

### Descripción General
Implementar sistema completo de descarga asíncrona de PDFs para papers encontrados en Google Scholar, con validación robusta, manejo de errores y control de concurrencia.

### Alcance
- **Componente core**: `PDFDownloader` (clase async para descarga de PDFs)
- **MCP Tool**: `download_papers` (expone funcionalidad vía MCP)
- **Testing**: Suite completa de unit tests + integration tests
- **No incluye**: Parsing de PDFs (eso es Fase 5), OCR, ni modificación de PDFs

### Objetivos
1. Descargar PDFs de forma asíncrona y eficiente (max 5 concurrentes)
2. Validar contenido descargado (Content-Type + magic bytes `%PDF`)
3. Manejar fallos gracefully (continuar con otros PDFs si uno falla)
4. Tracking detallado de éxitos/fallos
5. Integración perfecta con sesiones existentes
6. Gestión correcta del ciclo de vida de AsyncClient
7. Tests offline con fixtures deterministas
8. **[NUEVO REV-2]** Modelo de output claramente definido y documentado
9. **[NUEVO REV-2]** Metadatos de descarga persistidos para RAG

### Componentes MCP Afectados
- **Nuevos**:
  - `src/sortgs_mcp/pdf/downloader.py` - PDFDownloader class
  - `src/sortgs_mcp/tools/download.py` - MCP tool
  - `tests/test_pdf_downloader.py` - Unit tests
  - `tests/fixtures/pdf_responses.py` - Fixtures para tests offline
- **Modificados**:
  - `src/sortgs_mcp/server.py` - Registrar nuevo tool
  - `src/sortgs_mcp/pdf/__init__.py` - Exportar PDFDownloader
  - `src/sortgs_mcp/config.py` - Añadir pdf_download_dir property
  - `src/sortgs_mcp/models.py` - **[NUEVO REV-2]** Extender PDFDownloadResult con campos documentados

### Referencia a MCP_PLAN.md
Fase 4 (líneas 839-966): PDF Download con duración estimada 4-5 horas.

---

## 2. Priorización del Alcance

### MVP/CORE ⭐ (Imprescindible)

**Criterio de éxito mínimo:**
```python
# Debe funcionar este flujo:
session = await search_papers("machine learning", num_results=10)
result = await download_papers(session["session_id"], max_papers=3)

assert result["downloaded"] >= 0  # Al menos intenta descargar
assert result["failed"] >= 0       # Reporta fallos
assert len(result["pdf_paths"]) == result["downloaded"]
assert "download_metadata" in result  # [NUEVO REV-2] Metadatos presentes
```

**Componentes obligatorios:**
1. **PDFDownloader.download_single()**: Descarga 1 PDF con validación consistente
   - ✅ Validar magic bytes `%PDF` como criterio OBLIGATORIO
   - ✅ Content-Type como warning si falta/incorrecto (no bloquear)
   - ✅ Retry logic (3 intentos)
   - ✅ Timeout 30s
   - ✅ Guardar archivo con nombre sanitizado
   - ✅ **[NUEVO REV-2]** Retornar metadatos (size, timestamp)

2. **PDFDownloader ciclo de vida async**:
   - ✅ AsyncClient se crea en `__aenter__` y se cierra en `__aexit__`
   - ✅ Usar context manager: `async with PDFDownloader() as downloader:`
   - ✅ No fugas de recursos

3. **PDFDownloader.download_batch()**: Descarga múltiple con concurrencia
   - ✅ Semaphore(5) para límite de concurrencia
   - ✅ Return PDFDownloadResult con stats completas
   - ✅ **[NUEVO REV-2]** Incluir download_metadata por PDF

4. **MCP Tool download_papers()**: Interfaz MCP
   - ✅ Cargar sesión existente
   - ✅ Filtrar papers con PDF disponible
   - ✅ Aplicar max_papers limit
   - ✅ Actualizar session.pdfs_downloaded
   - ✅ Usar PDFDownloader como context manager
   - ✅ **[NUEVO REV-2]** Guardar download_metadata en session

5. **Config.pdf_download_dir**:
   - ✅ Property en Settings que retorna session-specific path
   - ✅ `sessions_dir / session_id / "pdfs"`

6. **PDFDownloadResult Model** (models.py): **[NUEVO REV-2]**
   - ✅ Campos: session_id, downloaded, failed, pdf_paths, failed_papers
   - ✅ **Campo nuevo**: `download_metadata: list[DownloadMetadata]`
   - ✅ Tipos explícitos, validación Pydantic
   - ✅ Ejemplo JSON schema documentado

7. **DownloadMetadata Model** (models.py): **[NUEVO REV-2]**
   - ✅ Campos mínimos: rank, title, pdf_path, file_size_bytes, download_timestamp
   - ✅ Tipo: Pydantic BaseModel
   - ✅ Serializable a JSON para persistencia en session

8. **Tests básicos offline**:
   - ✅ Test con mock httpx (descarga exitosa)
   - ✅ Test con error 404
   - ✅ Test batch mixto (éxitos + fallos)
   - ✅ Fixtures deterministas (no red)
   - ✅ Marcador `@pytest.mark.integration` para tests con red
   - ✅ **[NUEVO REV-2]** Test que valida max_concurrent_downloads de settings

### Enhanced (Opcional) 🌟

**Si hay tiempo extra:**
1. **Progress reporting mejorado**: Logging cada 5 papers (no solo cada 10)
2. **Retry con backoff personalizable**: Permitir configurar retry policy
3. **Filename collision handling**: Si archivo existe, agregar sufijo
4. **Resume capability**: Detectar PDFs ya descargados y skipear
5. **Metadatos extendidos**: Hash SHA256 del PDF (no solo size + timestamp)

**Esfuerzo estimado Enhanced:** +1-2 horas

### Nice-to-Have (Futuro) 💡

**No implementar ahora (sobre-ingeniería):**
1. Caché de PDFs global (cross-session) - complejidad innecesaria
2. Download progress bars individuales - no útil en MCP stdio
3. Parallel sessions download - un tool descarga una sesión a la vez
4. PDF compression/optimization - fuera de alcance
5. Bandwidth throttling - no requerido en uso normal

**Justificación:** KISS - implementar solo lo necesario para el flujo básico funcional.

### Plan de Reducción de Alcance

**[MODIFICADO REV-2] Si falta tiempo, recortar EN ESTE ORDEN:**
1. ❌ Enhanced features (todos)
2. ❌ Integration tests con PDFs reales (solo unit tests con mocks)
3. ❌ Logging detallado cada 10 papers → solo log al inicio/fin
4. ⚠️ Reduce retry de 3 a 1 intento
5. ⚠️ Reduce concurrencia de 5 a 2 (secuencial degradado, NO "todo en paralelo")
6. ⚠️ **[MODIFICADO REV-2]** Si context manager muy complejo: simplificar a `try/finally` con close explícito (mantener cierre garantizado)
7. 🛑 **CORE INAMOVIBLE**: download_single + validación magic bytes + tool básico + metadatos MVP

**Nota crítica REV-2**: Si se degrada context manager (punto 6), **mantener** cierre de AsyncClient en `finally` block. NO usar client global sin cleanup.

---

## 3. Diseño Técnico

### Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────┐
│ MCP Tool: download_papers()                             │
│ (src/sortgs_mcp/tools/download.py)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─► SessionManager.load_session()
                     │   (obtener papers de la sesión)
                     │
                     ├─► Filter papers con pdf_url
                     │   (eliminar papers sin PDF link)
                     │
                     ├─► Apply max_papers limit
                     │   (limitar cantidad a descargar)
                     │
                     ├─► async with PDFDownloader() as downloader:
                     │   │   (context manager crea/cierra AsyncClient)
                     │   │
                     │   ├─► downloader.download_batch()
                     │   │   │
                     │   │   ├─► asyncio.Semaphore(5)
                     │   │   │   (limitar concurrencia)
                     │   │   │
                     │   │   ├─► [Parallel] download_single()
                     │   │   │   ├─► httpx.AsyncClient.get()
                     │   │   │   ├─► [CRITICAL] Validate magic bytes %PDF
                     │   │   │   ├─► [WARNING] Check Content-Type
                     │   │   │   ├─► Retry on failure (tenacity)
                     │   │   │   ├─► aiofiles.open().write()
                     │   │   │   └─► [NEW] Return DownloadMetadata
                     │   │   │
                     │   │   └─► Return PDFDownloadResult (con metadata)
                     │
                     ├─► SessionManager.save_session()
                     │   │   (actualizar pdfs_downloaded + metadata)
                     │   │
                     │   └─► [NEW] Persist download_metadata to JSON
                     │
                     └─► Return dict (serialized PDFDownloadResult)
```

### Componentes Afectados

**Nuevos archivos:**
- `src/sortgs_mcp/pdf/downloader.py` - 230-280 líneas (+metadata tracking)
- `src/sortgs_mcp/tools/download.py` - 120-140 líneas (+metadata persistence)
- `tests/test_pdf_downloader.py` - 160-210 líneas (+metadata tests)
- `tests/test_download_tool.py` - 90-110 líneas (+metadata validation)
- `tests/fixtures/pdf_responses.py` - 50-80 líneas (fixtures)

**Archivos modificados:**
- `src/sortgs_mcp/pdf/__init__.py` - Exportar PDFDownloader
- `src/sortgs_mcp/server.py` - Import download_papers tool (auto-registro)
- `src/sortgs_mcp/config.py` - Añadir `pdf_download_dir(session_id)` method
- `src/sortgs_mcp/models.py` - **[MODIFICADO REV-2]** Extender PDFDownloadResult, añadir DownloadMetadata

### **[NUEVO REV-2]** Definición Explícita de Modelos

#### DownloadMetadata (nuevo en models.py)

```python
from datetime import datetime
from pydantic import BaseModel, Field

class DownloadMetadata(BaseModel):
    """Metadata for a single downloaded PDF."""

    rank: int = Field(..., description="Paper rank in search results")
    title: str = Field(..., description="Paper title")
    pdf_path: str = Field(..., description="Relative path to PDF file")
    file_size_bytes: int = Field(..., description="PDF file size in bytes")
    download_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the PDF was downloaded"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "title": "Attention Is All You Need",
                "pdf_path": "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                "file_size_bytes": 1234567,
                "download_timestamp": "2025-12-29T16:15:00"
            }
        }
```

#### PDFDownloadResult (extendido en models.py)

```python
class PDFDownloadResult(BaseModel):
    """Result of PDF download operation."""

    session_id: str = Field(..., description="Session ID")
    downloaded: int = Field(..., description="Number of successfully downloaded PDFs")
    failed: int = Field(..., description="Number of failed downloads")
    pdf_paths: list[str] = Field(default_factory=list, description="Paths to downloaded PDFs")
    failed_papers: list[dict] = Field(
        default_factory=list,
        description="Papers that failed to download with reasons"
    )
    download_metadata: list[DownloadMetadata] = Field(
        default_factory=list,
        description="[NEW REV-2] Detailed metadata for each downloaded PDF"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "downloaded": 8,
                "failed": 2,
                "pdf_paths": [
                    "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                    "data/sessions/550e.../pdfs/paper_002_bert.pdf"
                ],
                "failed_papers": [
                    {"rank": 3, "title": "...", "reason": "403 Forbidden"}
                ],
                "download_metadata": [
                    {
                        "rank": 1,
                        "title": "Attention Is All You Need",
                        "pdf_path": "data/sessions/550e.../pdfs/paper_001_attention.pdf",
                        "file_size_bytes": 1234567,
                        "download_timestamp": "2025-12-29T16:15:00"
                    }
                ]
            }
        }
```

**Mapeo a MCP Schema:**
- El tool `download_papers` retorna `PDFDownloadResult.model_dump()`
- MCP SDK auto-genera schema JSON desde Pydantic model
- No requiere definición manual de schema

### Decisiones Técnicas (KISS)

#### 1. HTTP Client: httpx.AsyncClient ✅
**Decisión:** Usar httpx (ya usado en `scholar.py`)
**Justificación:**
- Ya es dependencia del proyecto
- Async nativo
- Excelente manejo de timeouts y redirects
- API similar a requests (familiar)

**Alternativas descartadas:**
- aiohttp: Mayor complejidad, otra dependencia
- requests + threading: No async, menos eficiente

#### 2. Retry Logic: tenacity ✅
**Decisión:** Retry con tenacity (3 intentos, exponential backoff 2-10s)
**Justificación:**
- Ya usado en `openai.py` (consistencia)
- Declarativo (decorador `@retry`)
- Backoff exponencial evita martillar servidores

**Configuración:**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError))
)
```

#### 3. Concurrency Control: asyncio.Semaphore ✅
**Decisión:** Semaphore(5) para limitar descargas concurrentes
**Justificación:**
- Evita saturar conexiones de red
- Settings.max_concurrent_downloads ya definido (5)
- Patrón estándar async Python

**Código:**
```python
self.semaphore = asyncio.Semaphore(max_concurrent)

async with self.semaphore:
    # Download PDF
```

#### 4. File I/O: aiofiles ✅
**Decisión:** Usar aiofiles para escritura asíncrona
**Justificación:**
- Evita bloquear event loop durante escritura
- API simple: `async with aiofiles.open(path, 'wb') as f: await f.write()`

**Alternativa descartada:**
- `asyncio.to_thread(open().write)`: Más verboso, menos elegante

#### 5. Validación de PDFs: Magic Bytes (OBLIGATORIO) + Content-Type (WARNING) ✅

**Decisión CLARA (alineada):**
- **Magic bytes `%PDF`**: Criterio OBLIGATORIO - rechazar si falta
- **Content-Type**: Solo advertencia (logger.warning) - no bloquear descarga

**Justificación:**
- Magic bytes son más confiables (ISO 32000)
- Content-Type puede faltar en servidores mal configurados
- Evita guardar HTML/XML con extensión .pdf

**Código:**
```python
# Step 1: Validate magic bytes (CRITICAL - MUST PASS)
if not response.content.startswith(b'%PDF'):
    raise ValueError("Content is not a valid PDF (missing %PDF header)")

# Step 2: Check Content-Type (WARNING only - don't fail)
if 'application/pdf' not in response.headers.get('content-type', '').lower():
    logger.warning(f"Content-Type is not PDF for {url} - but magic bytes valid, proceeding")
```

**Política única**: Si magic bytes ok → guardar (aunque Content-Type sea incorrecto). Si magic bytes fail → rechazar (aunque Content-Type sea pdf).

#### 6. Filename Sanitization ✅
**Decisión:** Formato `paper_{rank}_{safe_title}.pdf`
**Justificación:**
- Rank asegura unicidad
- Safe title (remove special chars) evita filesystem issues
- Max 100 chars para título (evitar path too long)

**Código:**
```python
import re

def sanitize_filename(title: str, rank: int) -> str:
    # Remove non-alphanumeric (keep spaces and hyphens)
    safe_title = re.sub(r'[^\w\s-]', '', title)
    # Collapse whitespace
    safe_title = re.sub(r'\s+', '_', safe_title)
    # Truncate to 100 chars
    safe_title = safe_title[:100]
    return f"paper_{rank:03d}_{safe_title}.pdf"
```

#### 7. Error Handling: Graceful Degradation ✅
**Decisión:** Continuar descargando aunque algunos fallen
**Justificación:**
- User experience: mejor tener 8/10 PDFs que 0/10
- Reportar fallos claramente en `failed_papers`
- No usar `raise` que aborte todo el batch

**Patrón:**
```python
results = await asyncio.gather(*tasks, return_exceptions=True)

for result in results:
    if isinstance(result, Exception):
        failed_papers.append({"rank": rank, "reason": str(result)})
    else:
        downloaded_paths.append(result)
```

#### 8. Ciclo de Vida Async: Context Manager Pattern ✅

**Decisión:** PDFDownloader como async context manager
**Justificación:**
- AsyncClient debe cerrarse correctamente (evitar resource leaks)
- Pattern pythonic: `async with PDFDownloader() as downloader:`
- Garantiza cleanup incluso si hay excepciones

**Implementación:**
```python
class PDFDownloader:
    def __init__(self, max_concurrent: int = 5, timeout: int = 30):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client: httpx.AsyncClient | None = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Create AsyncClient on context entry."""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": "sortgs-mcp/1.0"}
        )
        self.logger.info("PDFDownloader AsyncClient initialized")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close AsyncClient on context exit."""
        if self.client:
            await self.client.aclose()
            self.logger.info("PDFDownloader AsyncClient closed")
```

**[MODIFICADO REV-2] Degradación si es necesario:**
Si context manager es muy complejo, degradar a:
```python
# Alternative simpler pattern (NOT RECOMMENDED, only if blocked)
downloader = PDFDownloader(...)
try:
    downloader.client = httpx.AsyncClient(...)  # Manual init
    result = await downloader.download_batch(...)
finally:
    if downloader.client:
        await downloader.client.aclose()  # Guaranteed close
```

**Nota**: Preferir context manager (mejor práctica), solo degradar si hay bloqueo técnico.

#### 9. Configuración de Rutas: Config.pdf_download_dir ✅

**Decisión:** Añadir method en Settings para rutas de descarga
**Justificación:**
- Centralizar lógica de paths (no hardcodear en tool)
- Consistencia con sessions_dir, chroma_persist_dir
- Facilita testing (mock settings)

**Código en config.py:**
```python
def pdf_download_dir(self, session_id: str) -> Path:
    """Directory for downloaded PDFs of a session."""
    pdf_dir = self.sessions_dir / session_id / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir
```

**Uso en tool:**
```python
pdf_dir = settings.pdf_download_dir(session_id)
```

#### 10. **[NUEVO REV-2]** Persistencia de Metadatos de Descarga ✅

**Decisión:** Guardar download_metadata en SearchSession
**Justificación:**
- Fase 5 (PDF parsing) necesita saber qué PDFs descargar
- Fase 6 (RAG indexing) necesita file paths + metadata
- Mantener todo en session.json centralizado (no archivos separados)

**Implementación:**

1. **Extender SearchSession model** (models.py):
```python
class SearchSession(BaseModel):
    # ... campos existentes ...
    pdfs_downloaded: int = Field(default=0, description="Number of PDFs downloaded")
    indexed: bool = Field(default=False, description="Whether papers have been indexed in vector DB")
    download_metadata: list[DownloadMetadata] = Field(
        default_factory=list,
        description="[NEW REV-2] Metadata for downloaded PDFs"
    )
```

2. **Guardar en tool** (download.py):
```python
# After download_batch
result = await downloader.download_batch(papers, pdf_dir)

# Update session
session.pdfs_downloaded = result.downloaded
session.download_metadata = result.download_metadata  # [NEW]
session_manager.save_session(session)
```

3. **SessionManager persiste automáticamente** (ya implementado):
```python
# session.json ahora incluye:
{
  "session_id": "...",
  "pdfs_downloaded": 8,
  "download_metadata": [
    {
      "rank": 1,
      "title": "Attention Is All You Need",
      "pdf_path": "data/sessions/.../pdfs/paper_001.pdf",
      "file_size_bytes": 1234567,
      "download_timestamp": "2025-12-29T16:15:00"
    }
  ]
}
```

**Formato mínimo MVP:** rank, title, pdf_path, file_size_bytes, download_timestamp

**Enhanced (opcional):** añadir pdf_sha256 hash para deduplicación

---

## 4. Plan de Desarrollo

### Tabla de Tareas

| # | Tarea | Prioridad | Criterio de Aceptación | Dependencias | Esfuerzo |
|---|-------|-----------|------------------------|--------------|----------|
| 1 | Actualizar models.py | CORE | DownloadMetadata + PDFDownloadResult extendido | Ninguna | 15min |
| 2 | Actualizar config.py | CORE | Method pdf_download_dir funciona | Ninguna | 10min |
| 3 | Crear PDFDownloader class skeleton | CORE | Clase existe, context manager, métodos stub | Tareas 1,2 | 20min |
| 4 | Implementar download_single() | CORE | Descarga 1 PDF, valida magic bytes, retorna metadata | Tarea 3 | 55min |
| 5 | Añadir retry logic con tenacity | CORE | Retry 3x con backoff funciona | Tarea 4 | 20min |
| 6 | Implementar download_batch() | CORE | Descarga N PDFs en paralelo, retorna metadata completa | Tareas 4,5 | 45min |
| 7 | Crear tool download_papers() | CORE | Tool usa context manager, persiste metadata en session | Tarea 6 | 50min |
| 8 | Actualizar server.py | CORE | Tool aparece en MCP Inspector | Tarea 7 | 5min |
| 9 | Crear fixtures offline | CORE | tests/fixtures/pdf_responses.py con mocks | Ninguna | 25min |
| 10 | Unit tests: download_single | CORE | 6 tests (success, 404, HTML, timeout, magic bytes, metadata) | Tareas 4,9 | 40min |
| 11 | Unit tests: download_batch | CORE | Test batch mixto + metadata validation | Tarea 6,9 | 25min |
| 12 | Unit tests: MCP tool | CORE | Test tool + session persistence + max_concurrent | Tareas 7,9 | 35min |
| 13 | Integration test con PDFs reales | Enhanced | Descarga PDFs de URLs fixture, marcado @pytest.mark.integration | Tarea 7 | 30min |
| 14 | Manual testing con MCP Inspector | CORE | Validación manual funciona | Tareas 1-8 | 20min |
| 15 | Progress logging mejorado | Enhanced | Log cada 5 papers (no 10) | Tarea 6 | 10min |

**Total CORE:** ~5h 5min (+ models + metadata tracking)
**Total Enhanced:** +40min
**Total con buffer (20%):** ~6h 30min

### Orden Sugerido de Implementación

**Día 1 - Core Implementation (3.5h):**
1. Models + Config (25min)
   - Actualizar models.py con DownloadMetadata + PDFDownloadResult
   - Actualizar config.py con pdf_download_dir
2. PDFDownloader skeleton (20min)
   - Crear clase con context manager
   - Métodos stub
3. download_single() + retry (1h 15min)
   - Implementar descarga + validación (magic bytes obligatorio)
   - Añadir tenacity decorator
   - Retornar metadata (size, timestamp)
4. download_batch() (45min)
   - Implementar Semaphore y gather
   - Agregar metadata tracking
5. MCP Tool + server.py (55min)
   - Tool download_papers con context manager
   - Integración con SessionManager
   - Persistencia de metadata

**Día 2 - Testing & Polish (2.5h):**
6. Fixtures offline (25min)
   - Crear tests/fixtures/pdf_responses.py
7. Unit tests (1h 40min)
   - Tests para download_single + metadata (40min)
   - Tests para download_batch + metadata (25min)
   - Tests para tool + max_concurrent (35min)
8. Manual testing + fixes (45min)
   - MCP Inspector validation
   - Bug fixes

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Niveles de testing:**
1. **Unit tests**: Componentes aislados con mocks (principal) - con fixtures deterministas
2. **Integration tests**: Con URLs de PDFs reales (opcional) - marcados `@pytest.mark.integration`
3. **Manual testing**: MCP Inspector + Claude Code

### Testabilidad Offline

**Fixtures deterministas (tests/fixtures/pdf_responses.py):**
```python
import pytest

@pytest.fixture
def mock_pdf_response():
    """Mock httpx.Response for valid PDF download."""
    return MockResponse(
        status_code=200,
        content=b'%PDF-1.4\n%test content here',
        headers={'content-type': 'application/pdf'}
    )

@pytest.fixture
def mock_pdf_no_content_type():
    """PDF válido pero sin Content-Type header."""
    return MockResponse(
        status_code=200,
        content=b'%PDF-1.4\n%mock pdf content',
        headers={}  # Sin Content-Type
    )

@pytest.fixture
def mock_html_response():
    """Mock httpx.Response for HTML (not PDF)."""
    return MockResponse(
        status_code=200,
        content=b'<html><body>Access Denied</body></html>',
        headers={'content-type': 'text/html'}
    )

@pytest.fixture
def mock_404_response():
    """Mock httpx.Response for 404."""
    return MockResponse(status_code=404, content=b'Not Found')
```

**Marcadores pytest:**
- Tests con mocks: sin marcador (run siempre)
- Tests con red: `@pytest.mark.integration` (skip en CI si `--skip-integration`)

**Configuración pytest.ini:**
```ini
[pytest]
markers =
    integration: tests requiring internet connection (can be skipped with --skip-integration)
```

### Checklist Mínima MCP + RAG

#### Unit Tests (pytest) - Offline

**test_pdf_downloader.py:**
- [ ] `test_download_single_success`: Mock httpx, PDF válido descargado + metadata retornada
- [ ] `test_download_single_404`: Mock 404, return (False, error_msg)
- [ ] `test_download_single_html_not_pdf`: Mock HTML content, validación falla (magic bytes)
- [ ] `test_download_single_timeout`: Mock timeout, retry funciona
- [ ] `test_download_single_invalid_magic_bytes`: Content sin %PDF rechazado **[CRÍTICO]**
- [ ] `test_download_single_missing_content_type`: Content-Type falta pero magic bytes ok → success + warning
- [ ] `test_download_single_metadata`: Metadata incluye size, timestamp **[NUEVO REV-2]**
- [ ] `test_download_batch_all_success`: 3 PDFs descargados exitosamente + metadata completa
- [ ] `test_download_batch_mixed`: 2 éxitos, 1 fallo, stats correctas
- [ ] `test_download_batch_semaphore`: Máximo 5 concurrentes (mock sleep)
- [ ] `test_download_batch_metadata_list`: download_metadata tiene 3 elementos **[NUEVO REV-2]**
- [ ] `test_sanitize_filename`: Caracteres especiales removidos, truncado a 100
- [ ] `test_context_manager_lifecycle`: AsyncClient se crea/cierra correctamente

**test_download_tool.py:**
- [ ] `test_download_papers_basic`: Descarga 3 PDFs de sesión mock
- [ ] `test_download_papers_no_pdfs`: Session sin pdf_url, return downloaded=0
- [ ] `test_download_papers_invalid_session`: Session no existe, raise error
- [ ] `test_download_papers_updates_session`: pdfs_downloaded actualizado
- [ ] `test_download_papers_persists_metadata`: session.download_metadata guardada **[NUEVO REV-2]**
- [ ] `test_download_papers_max_papers_limit`: Respeta max_papers=5
- [ ] `test_download_papers_respects_max_concurrent`: Respeta settings.max_concurrent_downloads **[NUEVO REV-2]**
- [ ] `test_download_papers_uses_context_manager`: Verifica client se cierra

**Cobertura objetivo:** >85% para downloader.py y download.py

#### Integration Tests (opcional) - Marcados

**test_pdf_integration.py:**
```python
@pytest.mark.integration
def test_download_real_pdf_from_arxiv():
    """Integration test: descarga PDF real de arXiv."""
    # Requiere conexión a internet
    # Skip con: pytest --skip-integration
    ...
```

- [ ] Descargar PDF real de arXiv (https://arxiv.org/pdf/1706.03762.pdf)
- [ ] Verificar archivo guardado
- [ ] Verificar tamaño > 100KB
- [ ] Verificar magic bytes en archivo
- [ ] **[NUEVO REV-2]** Verificar metadata contiene size real

**Nota:** Integration tests pueden ser skip en CI con `pytest -m "not integration"`.

#### Manual Testing Checklist

**MCP Inspector:**
- [ ] Tool `download_papers` aparece listado
- [ ] Input schema correcto (session_id, paper_indices, max_papers)
- [ ] Ejecutar con session_id válido: PDFs descargados
- [ ] Ejecutar con session_id inválido: Error claro
- [ ] Verificar archivos en `data/sessions/{id}/pdfs/`
- [ ] **[NUEVO REV-2]** Verificar session.json incluye download_metadata

**Claude Code:**
- [ ] Workflow completo:
  1. `search_papers("transformers", num_results=10)`
  2. `download_papers(session_id, max_papers=3)`
  3. Verificar output tiene downloaded=3, pdf_paths con 3 elementos
  4. **[NUEVO REV-2]** Verificar output tiene download_metadata con 3 elementos
- [ ] Verificar logs en `sortgs_mcp.log`
- [ ] Re-ejecutar download_papers: debería skipear archivos existentes (Enhanced)

### Smoke Test Checklist para PR

```markdown
## Smoke Test: Fase 4 - PDF Download

**Pre-requisitos:**
- [ ] Fase 2 completada (MCP server funciona)
- [ ] Session con papers disponible (ejecutar search_papers)

**Tests básicos:**
- [ ] Importar PDFDownloader: `from sortgs_mcp.pdf import PDFDownloader`
- [ ] Ejecutar tool download_papers con session_id válido
- [ ] Verificar output tiene keys: downloaded, failed, pdf_paths, failed_papers, download_metadata
- [ ] Verificar archivos .pdf creados en data/sessions/{id}/pdfs/
- [ ] Abrir un PDF descargado: debe ser válido (magic bytes %PDF)
- [ ] Verificar Content-Type warning en logs si header falta
- [ ] [NEW REV-2] Verificar download_metadata tiene size > 0, timestamp válido
- [ ] [NEW REV-2] Verificar session.json incluye download_metadata
- [ ] Re-ejecutar con mismo session_id: no re-descargar (Enhanced)

**Tests de error:**
- [ ] Ejecutar con session_id inexistente: error claro
- [ ] Session sin papers con PDF: downloaded=0, no crash
- [ ] URL de PDF 404: reportado en failed_papers
- [ ] URL retorna HTML: rechazado por magic bytes validation

**Validación MCP:**
- [ ] Tool aparece en `claude mcp list`
- [ ] MCP Inspector muestra tool signature correcta
- [ ] Ejecutar desde Claude Code: funciona sin errors
- [ ] [NEW REV-2] Schema JSON incluye download_metadata field

**Performance:**
- [ ] Descargar 10 PDFs: completa en <30 segundos
- [ ] Verificar solo 5 descargas concurrentes (check logs)
- [ ] [NEW REV-2] Verificar que usa settings.max_concurrent_downloads

**Logs:**
- [ ] Logs en sortgs_mcp.log son legibles
- [ ] AsyncClient lifecycle logged (init + close)
- [ ] No stack traces en caso normal (solo warnings en failed)

**Tests offline:**
- [ ] `pytest tests/test_pdf_downloader.py -v` pasa sin internet
- [ ] `pytest -m "not integration"` skipea tests de red
```

---

## 6. Plan de Contingencia

### Escenarios de Riesgo y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| URLs de PDF retornan 403/404 | Alta | Medio | Graceful degradation, reportar en failed_papers |
| Content-Type incorrecto/faltante | Media | Bajo | Solo warning, magic bytes es criterio obligatorio |
| Timeouts frecuentes | Media | Medio | Retry 3x con backoff, timeout configurable (30s) |
| Filesystem issues (permisos) | Baja | Alto | Try/catch en aiofiles, error claro al usuario |
| Archivos muy grandes (>100MB) | Baja | Medio | No implementar límite ahora (KISS), añadir después si es problema |
| AsyncClient leaks | Baja | Alto | Context manager garantiza cierre |
| Magic bytes no presentes | Media | Alto | RECHAZAR descarga (no guardar basura) |
| **[NUEVO REV-2]** Metadata serialization error | Baja | Medio | Pydantic valida tipos, catch + log si falla JSON dump |

### Puntos de Decisión GO/NO-GO

**Checkpoint 1 (después de 2h):**
- ✅ GO: download_single funciona con validación magic bytes + metadata
- ❌ NO-GO: Problemas con httpx/async → Considerar sync con threads (plan B)

**Checkpoint 2 (después de 4.5h):**
- ✅ GO: download_batch + tool + context manager + metadata persistence funcionan
- ❌ NO-GO: Context manager complejo → **[MODIFICADO REV-2]** Degradar a try/finally con close explícito (NO client global sin cleanup)

**Checkpoint Final (antes de PR):**
- ✅ MERGE: Smoke tests pasan, al menos 1 PDF descarga correctamente, unit tests offline pasan, metadata persiste
- ❌ BLOCK: 0 PDFs descargan O unit tests fallan O metadata no se guarda → Investigar root cause, no mergear

### **[MODIFICADO REV-2]** Plan de Reducción Simplificado

**Si falta tiempo (<1h restante):**
1. ❌ Eliminar integration tests con PDFs reales
2. ❌ Eliminar enhanced logging (solo básico)
3. ⚠️ Reducir retry de 3 a 1
4. ⚠️ Reducir concurrencia de 5 a 2 (NO eliminar Semaphore)
5. ⚠️ **[MODIFICADO REV-2]** Si context manager problemático: usar try/finally con close garantizado
   ```python
   downloader = PDFDownloader(...)
   try:
       downloader.client = httpx.AsyncClient(...)
       result = await downloader.download_batch(...)
   finally:
       if downloader.client:
           await downloader.client.aclose()  # MUST close
   ```
6. ⚠️ **[NUEVO REV-2]** Si metadata muy complejo: solo guardar paths mínimos (sin size/timestamp)
7. 🛑 **CORE INAMOVIBLE**: download_single + validación magic bytes + tool básico + AsyncClient close garantizado

**Nota crítica REV-2**: Nunca usar "client global sin cleanup" - siempre garantizar cierre con try/finally mínimo.

---

## 7. Notas de Implementación

### Consideraciones Especiales

1. **Sanitización de filenames:**
   - Importante en Windows: evitar `< > : " / \ | ? *`
   - Truncar a 100 chars (algunos filesystems tienen límite 255 para path completo)
   - Formato: `paper_{rank:03d}_{safe_title}.pdf`

2. **Magic bytes validation:**
   - PDFs válidos empiezan con `%PDF-1.X` (X = versión)
   - Suficiente verificar primeros 4 bytes: `b'%PDF'`
   - Algunos PDFs pueden tener whitespace antes → verificar primeros 10 bytes: `content[:10].startswith(b'%PDF')`

3. **httpx best practices:**
   - Usar `follow_redirects=True` (muchos journals redirigen)
   - Timeout: 30s para PDFs grandes
   - AsyncClient via context manager (no crear uno por descarga)
   - Headers: User-Agent custom para evitar bloqueos

4. **Error messages claros:**
   - "403 Forbidden" → "PDF requires authentication or paywall"
   - "Content is not PDF" → "Magic bytes validation failed - content is not a valid PDF"
   - "Content-Type missing" → "Warning: Content-Type header missing, but magic bytes valid"
   - Timeout → "Download timed out after 30s"

5. **Session metadata update:**
   - Actualizar `session.pdfs_downloaded` después de batch
   - **[NUEVO REV-2]** Actualizar `session.download_metadata` con lista completa
   - No sobreescribir `session.papers` (mantener intacto)

6. **[MODIFICADO REV-2] Conexión con RAG/ChromaDB (Fase 5-6):**
   - **Fase 5 (PDF parsing)**: Itera sobre `session.download_metadata` para saber qué PDFs parsear
   - **Fase 6 (RAG indexing)**: Usa `pdf_path` + metadata para crear chunks con contexto
   - Metadatos persistidos en session.json (MVP):
     - `rank`: Mapea paper a resultado de búsqueda
     - `title`: Para logging y contexto RAG
     - `pdf_path`: Ruta para parsing
     - `file_size_bytes`: Validar archivo completo
     - `download_timestamp`: Tracking temporal
   - **Enhanced (opcional)**: `pdf_sha256` para deduplicación cross-session

### Patrones a Reutilizar

**Del proyecto actual:**
- Retry pattern de `openai.py` (tenacity decorator)
- Async client pattern de `scholar.py` (httpx) - mejorado con context manager
- Error logging de `scholar.py` (logger.error con contexto)
- Config access: `from sortgs_mcp.config import settings`
- **[NUEVO REV-2]** Pydantic models de `models.py` (extender existentes)

### Dependencias Externas

**PyPI packages (ya instaladas):**
- httpx (async HTTP)
- tenacity (retry logic)
- aiofiles (async file I/O)

**No requiere nuevas dependencias** ✅

---

## 8. Definición de "Hecho" (DoD)

Una tarea está COMPLETA cuando:

- [ ] Código implementado y funcional
- [ ] Context manager implementado y testeado
- [ ] Validación de magic bytes como criterio obligatorio
- [ ] **[NUEVO REV-2]** DownloadMetadata y PDFDownloadResult definidos en models.py
- [ ] **[NUEVO REV-2]** Metadata persiste en session.json
- [ ] Unit tests escritos y pasando (>85% coverage)
- [ ] Tests offline con fixtures pasan sin internet
- [ ] Smoke tests manuales pasados
- [ ] Documentación (docstrings) completa
- [ ] Sin warnings de pytest/linter
- [ ] MCP Inspector valida el tool
- [ ] PR reviewable (código limpio, commits atómicos)

**Fase 4 está COMPLETA cuando:**
- [ ] Todas las tareas CORE implementadas
- [ ] Context manager funciona correctamente (AsyncClient se cierra)
- [ ] **[NUEVO REV-2]** Metadata de descarga persiste en session
- [ ] Smoke test checklist pasa 100%
- [ ] Tool download_papers descarga al menos 1 PDF correctamente
- [ ] Tests unitarios pasan: `pytest tests/test_pdf_downloader.py -v` (sin internet)
- [ ] Integration manual: descargar 5 PDFs de sesión real
- [ ] Config.pdf_download_dir funciona
- [ ] **[NUEVO REV-2]** Test de max_concurrent_downloads pasa

---

## 9. Próximos Pasos (Post-Fase 4)

Después de completar esta fase:

1. **Fase 5: PDF Parsing** - Extraer texto de PDFs con PyMuPDF
2. **Fase 6: RAG Vector Store** - Indexar chunks en ChromaDB
3. **Fase 7: RAG Q&A** - Query papers con LLM

**Entregables de Fase 4 para Fase 5:**
- PDFs descargados en `data/sessions/{id}/pdfs/*.pdf`
- Session metadata con `pdfs_downloaded` actualizado
- **[MODIFICADO REV-2]** `session.download_metadata` con lista completa de metadatos:
  - `rank`: Identificar paper
  - `title`: Contexto para parsing
  - `pdf_path`: Ruta al archivo
  - `file_size_bytes`: Validar integridad
  - `download_timestamp`: Tracking

**Uso en Fase 5:**
```python
# En PDF Parser
session = session_manager.load_session(session_id)

for metadata in session.download_metadata:
    pdf_path = Path(metadata.pdf_path)
    if not pdf_path.exists() or pdf_path.stat().st_size != metadata.file_size_bytes:
        logger.warning(f"PDF corrupted or missing: {metadata.title}")
        continue

    # Parse PDF
    text = pdf_parser.extract_text(pdf_path)
    # ... chunking, embedding, etc.
```

---

## Apéndice A: Ejemplos de Código

### Ejemplo: download_single signature con metadata

```python
async def download_single(
    self,
    url: str,
    filepath: Path,
    paper: Paper
) -> tuple[bool, str | None, DownloadMetadata | None]:
    """Download a single PDF with retry logic.

    Args:
        url: PDF URL to download
        filepath: Destination path for PDF
        paper: Paper model (for rank, title)

    Returns:
        Tuple of (success: bool, error_message: str | None, metadata: DownloadMetadata | None)
        - (True, None, metadata) if successful
        - (False, "error description", None) if failed

    Raises:
        Never raises - all errors converted to return value
    """
    # ... implementation ...

    if success:
        metadata = DownloadMetadata(
            rank=paper.rank,
            title=paper.title,
            pdf_path=str(filepath),
            file_size_bytes=filepath.stat().st_size,
            download_timestamp=datetime.now()
        )
        return (True, None, metadata)
    else:
        return (False, error_message, None)
```

### Ejemplo: Context Manager Usage con metadata

```python
# En tool download_papers()
async def download_papers(
    session_id: str,
    paper_indices: list[int] | None = None,
    max_papers: int = 10
) -> dict:
    # Load session
    session = session_manager.load_session(session_id)

    # Filter papers
    papers_to_download = [p for p in session.papers if p.pdf_url]
    if paper_indices:
        papers_to_download = [papers_to_download[i] for i in paper_indices]
    papers_to_download = papers_to_download[:max_papers]

    # Download with context manager
    async with PDFDownloader(
        max_concurrent=settings.max_concurrent_downloads,
        timeout=30
    ) as downloader:
        pdf_dir = settings.pdf_download_dir(session_id)
        result = await downloader.download_batch(papers_to_download, pdf_dir)

    # AsyncClient auto-closed here

    # Update session with metadata
    session.pdfs_downloaded = result.downloaded
    session.download_metadata = result.download_metadata  # [NEW REV-2]
    session_manager.save_session(session)

    return result.model_dump()
```

### Ejemplo: Fixtures para Tests Offline

```python
# tests/fixtures/pdf_responses.py
import pytest
from unittest.mock import Mock

class MockResponse:
    def __init__(self, status_code, content, headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}

@pytest.fixture
def mock_pdf_response():
    return MockResponse(
        status_code=200,
        content=b'%PDF-1.4\n%mock pdf content',
        headers={'content-type': 'application/pdf'}
    )

@pytest.fixture
def mock_pdf_no_content_type():
    """PDF válido pero sin Content-Type header."""
    return MockResponse(
        status_code=200,
        content=b'%PDF-1.4\n%mock pdf content',
        headers={}  # Sin Content-Type
    )

@pytest.fixture
def mock_html_response():
    return MockResponse(
        status_code=200,
        content=b'<html><body>Access Denied</body></html>',
        headers={'content-type': 'text/html'}
    )

@pytest.fixture
def mock_404_response():
    return MockResponse(status_code=404, content=b'Not Found')
```

### Ejemplo: Tool output con metadata

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "downloaded": 8,
  "failed": 2,
  "pdf_paths": [
    "data/sessions/550e8400.../pdfs/paper_001_attention_is_all_you_need.pdf",
    "data/sessions/550e8400.../pdfs/paper_002_bert_pretraining.pdf",
    "..."
  ],
  "failed_papers": [
    {
      "rank": 3,
      "title": "Deep Learning for NLP",
      "reason": "Magic bytes validation failed - content is not a valid PDF"
    },
    {
      "rank": 7,
      "title": "Survey on Transformers",
      "reason": "403 Forbidden - PDF requires authentication"
    }
  ],
  "download_metadata": [
    {
      "rank": 1,
      "title": "Attention Is All You Need",
      "pdf_path": "data/sessions/550e8400.../pdfs/paper_001_attention_is_all_you_need.pdf",
      "file_size_bytes": 1234567,
      "download_timestamp": "2025-12-29T16:15:00"
    },
    {
      "rank": 2,
      "title": "BERT: Pre-training of Deep Bidirectional Transformers",
      "pdf_path": "data/sessions/550e8400.../pdfs/paper_002_bert_pretraining.pdf",
      "file_size_bytes": 987654,
      "download_timestamp": "2025-12-29T16:15:05"
    }
  ]
}
```

---

## Apéndice B: Cambios Principales por Revisión

### Cambios en Revisión 1

1. **[ALTA] Alinear validación de PDFs:**
   - ✅ Magic bytes `%PDF` ahora es criterio OBLIGATORIO
   - ✅ Content-Type solo genera warning (no bloquea)
   - ✅ Política única y consistente en código, tests y docs

2. **[ALTA] Ajustar plan de reducción:**
   - ✅ Eliminado "descargar todo en paralelo" (contradecía KISS)
   - ✅ Nueva estrategia: degradar a 1-2 concurrentes si necesario
   - ✅ Mantener Semaphore siempre (estabilidad)

3. **[MEDIA] Ciclo de vida async:**
   - ✅ PDFDownloader ahora es async context manager
   - ✅ AsyncClient se crea en `__aenter__` y cierra en `__aexit__`
   - ✅ Evita resource leaks

4. **[MEDIA] Testabilidad offline:**
   - ✅ Fixtures deterministas en `tests/fixtures/pdf_responses.py`
   - ✅ Marcador `@pytest.mark.integration` para tests con red
   - ✅ Tests unitarios corren sin internet

5. **[MEDIA] Config centralizado:**
   - ✅ Añadido `Settings.pdf_download_dir(session_id)` method
   - ✅ No hardcodear paths en tool

### **[NUEVO]** Cambios en Revisión 2

1. **[ALTA REV-2] Definir modelo PDFDownloadResult explícitamente:**
   - ✅ Añadido `DownloadMetadata` model en models.py
   - ✅ Extendido `PDFDownloadResult` con campo `download_metadata`
   - ✅ Campos: rank, title, pdf_path, file_size_bytes, download_timestamp
   - ✅ Ejemplo JSON schema documentado

2. **[ALTA REV-2] Alinear plan de contingencia con context manager:**
   - ✅ Degradación clarificada: try/finally con close garantizado (NO client global)
   - ✅ Eliminada contradicción con política de resources
   - ✅ Mantener cleanup siempre

3. **[MEDIA REV-2] Formalizar persistencia de metadatos:**
   - ✅ `session.download_metadata` persiste en session.json
   - ✅ Fase 5/6 tienen acceso a pdf_path + metadata
   - ✅ No depende de Enhanced - es MVP

4. **[MEDIA REV-2] Criterio de aceptación max_concurrent_downloads:**
   - ✅ Test específico que valida settings.max_concurrent_downloads
   - ✅ Añadido a checklist de tests

### Impacto en Esfuerzo

- **Rev-1 agregó**: ~30min (context manager + fixtures + config)
- **Rev-2 agregó**: ~25min (models + metadata tracking + tests)
- **Nuevo total CORE**: ~5h 5min (vs 4h 15min original)
- **Beneficio**: Modelo claro, metadata para RAG, plan de contingencia alineado, tests completos

---

**FIN DEL WORKPLAN REVISIÓN 2**
