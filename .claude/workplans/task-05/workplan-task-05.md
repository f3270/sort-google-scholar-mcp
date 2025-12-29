# Workplan: Fase 4 - PDF Download

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 4: Descarga asíncrona de PDFs de papers académicos |
| **Task ID** | task-05-fase-4 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.0 |
| **Estado** | Borrador |
| **Autor** | Claude Code (Coordinador de Planificación) |
| **Stack principal** | Python 3.13, httpx, aiofiles, tenacity, MCP SDK |
| **Fase MCP_PLAN** | Fase 4 (líneas 839-966 de MCP_PLAN.md) |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Crear workplan para Fase 4 | Usuario |

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

### Componentes MCP Afectados
- **Nuevos**:
  - `src/sortgs_mcp/pdf/downloader.py` - PDFDownloader class
  - `src/sortgs_mcp/tools/download.py` - MCP tool
  - `tests/test_pdf_downloader.py` - Unit tests
- **Modificados**:
  - `src/sortgs_mcp/server.py` - Registrar nuevo tool
  - `src/sortgs_mcp/pdf/__init__.py` - Exportar PDFDownloader

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
```

**Componentes obligatorios:**
1. **PDFDownloader.download_single()**: Descarga 1 PDF con validación básica
   - ✅ Validar magic bytes `%PDF`
   - ✅ Retry logic (3 intentos)
   - ✅ Timeout 30s
   - ✅ Guardar archivo con nombre sanitizado

2. **PDFDownloader.download_batch()**: Descarga múltiple con concurrencia
   - ✅ Semaphore(5) para límite de concurrencia
   - ✅ Return PDFDownloadResult con stats

3. **MCP Tool download_papers()**: Interfaz MCP
   - ✅ Cargar sesión existente
   - ✅ Filtrar papers con PDF disponible
   - ✅ Aplicar max_papers limit
   - ✅ Actualizar session.pdfs_downloaded

4. **Tests básicos**: Smoke tests que validen el flujo
   - ✅ Test con mock httpx (descarga exitosa)
   - ✅ Test con error 404
   - ✅ Test batch mixto (éxitos + fallos)

### Enhanced (Opcional) 🌟

**Si hay tiempo extra:**
1. **Progress reporting mejorado**: Logging cada 5 papers (no solo cada 10)
2. **Retry con backoff personalizable**: Permitir configurar retry policy
3. **Content-Type fallback**: Si no hay Content-Type, intentar igual si magic bytes ok
4. **Filename collision handling**: Si archivo existe, agregar sufijo
5. **Resume capability**: Detectar PDFs ya descargados y skipear

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

**Si falta tiempo, recortar EN ESTE ORDEN:**
1. ❌ Enhanced features (todos)
2. ❌ Integration tests con PDFs reales (solo unit tests con mocks)
3. ❌ Logging detallado cada 10 papers → solo log al inicio/fin
4. ⚠️ Reduce retry de 3 a 1 intento
5. 🛑 **CORE INAMOVIBLE**: download_single + download_batch + tool básico

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
                     ├─► PDFDownloader.download_batch()
                     │   │
                     │   ├─► asyncio.Semaphore(5)
                     │   │   (limitar concurrencia)
                     │   │
                     │   ├─► [Parallel] download_single()
                     │   │   ├─► httpx.AsyncClient.get()
                     │   │   ├─► Validate magic bytes %PDF
                     │   │   ├─► Retry on failure (tenacity)
                     │   │   └─► aiofiles.open().write()
                     │   │
                     │   └─► Return PDFDownloadResult
                     │
                     ├─► SessionManager.save_session()
                     │   (actualizar pdfs_downloaded count)
                     │
                     └─► Return dict (serialized result)
```

### Componentes Afectados

**Nuevos archivos:**
- `src/sortgs_mcp/pdf/downloader.py` - 200-250 líneas
- `src/sortgs_mcp/tools/download.py` - 100-120 líneas
- `tests/test_pdf_downloader.py` - 150-200 líneas
- `tests/test_download_tool.py` - 80-100 líneas

**Archivos modificados:**
- `src/sortgs_mcp/pdf/__init__.py` - Exportar PDFDownloader
- `src/sortgs_mcp/server.py` - Import download_papers tool (auto-registro)

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

#### 5. Validación de PDFs: Magic Bytes + Content-Type ✅
**Decisión:** Doble validación (Content-Type + primeros bytes)
**Justificación:**
- Content-Type puede mentir o faltar
- Magic bytes `%PDF` son estándar PDF (ISO 32000)
- Evita guardar HTML/XML con extensión .pdf

**Código:**
```python
# Check Content-Type
if 'application/pdf' not in response.headers.get('content-type', '').lower():
    logger.warning("Content-Type is not PDF")

# CRITICAL: Validate magic bytes
if not response.content.startswith(b'%PDF'):
    raise ValueError("Content is not a valid PDF (missing %PDF header)")
```

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

---

## 4. Plan de Desarrollo

### Tabla de Tareas

| # | Tarea | Prioridad | Criterio de Aceptación | Dependencias | Esfuerzo |
|---|-------|-----------|------------------------|--------------|----------|
| 1 | Crear PDFDownloader class skeleton | CORE | Clase existe, métodos stub | Ninguna | 15min |
| 2 | Implementar download_single() | CORE | Descarga 1 PDF y valida magic bytes | Tarea 1 | 45min |
| 3 | Añadir retry logic con tenacity | CORE | Retry 3x con backoff funciona | Tarea 2 | 20min |
| 4 | Implementar download_batch() | CORE | Descarga N PDFs en paralelo con Semaphore | Tareas 2,3 | 40min |
| 5 | Crear tool download_papers() | CORE | Tool registrado en MCP, ejecuta flujo completo | Tarea 4 | 40min |
| 6 | Actualizar server.py | CORE | Tool aparece en MCP Inspector | Tarea 5 | 5min |
| 7 | Unit tests: download_single | CORE | 4 tests (success, 404, HTML, timeout) | Tarea 2 | 30min |
| 8 | Unit tests: download_batch | CORE | Test batch mixto (éxitos+fallos) | Tarea 4 | 20min |
| 9 | Unit tests: MCP tool | CORE | Test tool end-to-end con mocks | Tarea 5 | 25min |
| 10 | Integration test con PDFs reales | Enhanced | Descarga PDFs de URLs fixture | Tarea 5 | 30min |
| 11 | Manual testing con MCP Inspector | CORE | Validación manual funciona | Tareas 1-6 | 20min |
| 12 | Progress logging mejorado | Enhanced | Log cada 5 papers (no 10) | Tarea 4 | 10min |

**Total CORE:** ~4h 15min
**Total Enhanced:** +40min
**Total con buffer (20%):** ~5h 30min

### Orden Sugerido de Implementación

**Día 1 - Core Implementation (3h):**
1. PDFDownloader skeleton + download_single() básico (1h)
   - Crear clase, inicializar httpx.AsyncClient
   - Método download_single sin retry
   - Validación magic bytes
2. Retry logic + download_batch() (1h)
   - Añadir tenacity decorator
   - Implementar Semaphore y gather
3. MCP Tool + server.py (1h)
   - Tool download_papers completo
   - Integración con SessionManager

**Día 2 - Testing & Polish (2h):**
4. Unit tests (1h 15min)
   - Tests para download_single (30min)
   - Tests para download_batch (20min)
   - Tests para tool (25min)
5. Manual testing + fixes (45min)
   - MCP Inspector validation
   - Bug fixes

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Niveles de testing:**
1. **Unit tests**: Componentes aislados con mocks (principal)
2. **Integration tests**: Con URLs de PDFs reales (opcional)
3. **Manual testing**: MCP Inspector + Claude Code

### Checklist Mínima MCP + RAG

#### Unit Tests (pytest)

**test_pdf_downloader.py:**
- [ ] `test_download_single_success`: Mock httpx, PDF válido descargado
- [ ] `test_download_single_404`: Mock 404, return (False, error_msg)
- [ ] `test_download_single_html_not_pdf`: Mock HTML content, validación falla
- [ ] `test_download_single_timeout`: Mock timeout, retry funciona
- [ ] `test_download_single_invalid_magic_bytes`: Content sin %PDF rechazado
- [ ] `test_download_batch_all_success`: 3 PDFs descargados exitosamente
- [ ] `test_download_batch_mixed`: 2 éxitos, 1 fallo, stats correctas
- [ ] `test_download_batch_semaphore`: Máximo 5 concurrentes (mock sleep)
- [ ] `test_sanitize_filename`: Caracteres especiales removidos, truncado a 100

**test_download_tool.py:**
- [ ] `test_download_papers_basic`: Descarga 3 PDFs de sesión mock
- [ ] `test_download_papers_no_pdfs`: Session sin pdf_url, return downloaded=0
- [ ] `test_download_papers_invalid_session`: Session no existe, raise error
- [ ] `test_download_papers_updates_session`: pdfs_downloaded actualizado
- [ ] `test_download_papers_max_papers_limit`: Respeta max_papers=5

**Cobertura objetivo:** >85% para downloader.py y download.py

#### Integration Tests (opcional)

**test_pdf_integration.py:**
- [ ] Descargar PDF real de arXiv (https://arxiv.org/pdf/1706.03762.pdf)
- [ ] Verificar archivo guardado
- [ ] Verificar tamaño > 100KB
- [ ] Verificar magic bytes en archivo

**Nota:** Integration tests requieren conexión a internet, pueden ser skip en CI.

#### Manual Testing Checklist

**MCP Inspector:**
- [ ] Tool `download_papers` aparece listado
- [ ] Input schema correcto (session_id, paper_indices, max_papers)
- [ ] Ejecutar con session_id válido: PDFs descargados
- [ ] Ejecutar con session_id inválido: Error claro
- [ ] Verificar archivos en `data/sessions/{id}/pdfs/`

**Claude Code:**
- [ ] Workflow completo:
  1. `search_papers("transformers", num_results=10)`
  2. `download_papers(session_id, max_papers=3)`
  3. Verificar output tiene downloaded=3, pdf_paths con 3 elementos
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
- [ ] Verificar output tiene keys: downloaded, failed, pdf_paths, failed_papers
- [ ] Verificar archivos .pdf creados en data/sessions/{id}/pdfs/
- [ ] Abrir un PDF descargado: debe ser válido
- [ ] Re-ejecutar con mismo session_id: no re-descargar (Enhanced)

**Tests de error:**
- [ ] Ejecutar con session_id inexistente: error claro
- [ ] Session sin papers con PDF: downloaded=0, no crash
- [ ] URL de PDF 404: reportado en failed_papers

**Validación MCP:**
- [ ] Tool aparece en `claude mcp list`
- [ ] MCP Inspector muestra tool signature correcta
- [ ] Ejecutar desde Claude Code: funciona sin errors

**Performance:**
- [ ] Descargar 10 PDFs: completa en <30 segundos
- [ ] Verificar solo 5 descargas concurrentes (check logs)

**Logs:**
- [ ] Logs en sortgs_mcp.log son legibles
- [ ] No stack traces en caso normal (solo warnings en failed)
```

---

## 6. Plan de Contingencia

### Escenarios de Riesgo y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| URLs de PDF retornan 403/404 | Alta | Medio | Graceful degradation, reportar en failed_papers |
| Content-Type incorrecto | Media | Bajo | Validar con magic bytes (más confiable) |
| Timeouts frecuentes | Media | Medio | Retry 3x con backoff, timeout configurable (30s) |
| Filesystem issues (permisos) | Baja | Alto | Try/catch en aiofiles, error claro al usuario |
| Archivos muy grandes (>100MB) | Baja | Medio | No implementar límite ahora (KISS), añadir después si es problema |
| Magic bytes no presentes | Baja | Bajo | Loggear warning, guardar igual si Content-Type ok (fallback) |

### Puntos de Decisión GO/NO-GO

**Checkpoint 1 (después de 2h):**
- ✅ GO: download_single funciona con validación
- ❌ NO-GO: Problemas con httpx/async → Considerar sync con threads (plan B)

**Checkpoint 2 (después de 4h):**
- ✅ GO: download_batch + tool funcionan
- ❌ NO-GO: Batch complejo → Simplificar a descargas secuenciales (recortar concurrencia)

**Checkpoint Final (antes de PR):**
- ✅ MERGE: Smoke tests pasan, al menos 1 PDF descarga correctamente
- ❌ BLOCK: 0 PDFs descargan → Investigar root cause, no mergear

### Plan de Reducción Simplificado

**Si falta tiempo (<1h restante):**
1. ❌ Eliminar integration tests con PDFs reales
2. ❌ Eliminar enhanced logging (solo básico)
3. ⚠️ Reducir retry de 3 a 1
4. ⚠️ Eliminar Semaphore (descargar todo en paralelo sin límite)
5. 🛑 **Mínimo viable**: download_single + tool básico funcionando

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
   - Algunos PDFs pueden tener whitespace antes → strip primeros 10 bytes

3. **httpx best practices:**
   - Usar `follow_redirects=True` (muchos journals redirigen)
   - Timeout: 30s para PDFs grandes
   - Reuse AsyncClient (no crear uno por descarga)

4. **Error messages claros:**
   - "403 Forbidden" → "PDF requires authentication or paywall"
   - "Content is not PDF" → "Server returned HTML/XML instead of PDF"
   - Timeout → "Download timed out after 30s"

5. **Session metadata update:**
   - Actualizar `session.pdfs_downloaded` después de batch
   - No sobreescribir `session.papers` (mantener intacto)

### Patrones a Reutilizar

**Del proyecto actual:**
- Retry pattern de `openai.py` (tenacity decorator)
- Async client pattern de `scholar.py` (httpx)
- Error logging de `scholar.py` (logger.error con contexto)
- Config access: `from sortgs_mcp.config import settings`

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
- [ ] Unit tests escritos y pasando (>85% coverage)
- [ ] Smoke tests manuales pasados
- [ ] Documentación (docstrings) completa
- [ ] Sin warnings de pytest/linter
- [ ] MCP Inspector valida el tool
- [ ] PR reviewable (código limpio, commits atómicos)

**Fase 4 está COMPLETA cuando:**
- [ ] Todas las tareas CORE implementadas
- [ ] Smoke test checklist pasa 100%
- [ ] Tool download_papers descarga al menos 1 PDF correctamente
- [ ] Tests unitarios pasan: `pytest tests/test_pdf_downloader.py -v`
- [ ] Integration manual: descargar 5 PDFs de sesión real

---

## 9. Próximos Pasos (Post-Fase 4)

Después de completar esta fase:

1. **Fase 5: PDF Parsing** - Extraer texto de PDFs con PyMuPDF
2. **Fase 6: RAG Vector Store** - Indexar chunks en ChromaDB
3. **Fase 7: RAG Q&A** - Query papers con LLM

**Entregables de Fase 4 para Fase 5:**
- PDFs descargados en `data/sessions/{id}/pdfs/*.pdf`
- Session metadata con `pdfs_downloaded` actualizado
- Rutas de PDFs en `PDFDownloadResult.pdf_paths`

---

## Apéndice A: Ejemplos de Código

### Ejemplo: download_single signature

```python
async def download_single(
    self,
    url: str,
    filepath: Path,
    paper_title: str
) -> tuple[bool, str | None]:
    """Download a single PDF with retry logic.

    Args:
        url: PDF URL to download
        filepath: Destination path for PDF
        paper_title: Paper title (for logging)

    Returns:
        Tuple of (success: bool, error_message: str | None)
        - (True, None) if successful
        - (False, "error description") if failed

    Raises:
        Never raises - all errors converted to return value
    """
```

### Ejemplo: Tool output

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
      "reason": "403 Forbidden - PDF requires authentication"
    },
    {
      "rank": 7,
      "title": "Survey on Transformers",
      "reason": "Content is not a valid PDF (missing %PDF header)"
    }
  ]
}
```

---

**FIN DEL WORKPLAN**
