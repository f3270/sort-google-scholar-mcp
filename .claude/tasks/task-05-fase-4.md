---
Task-05: fase 5
---

Vamos a desarrollar la fase 5 de ../../MCP_PLAN.md

Objetivo: Descargar PDFs de los papers encontrados en las búsquedas de Google Scholar

Componentes a desarrollar:

1. PDFDownloader (src/sortgs_mcp/pdf/downloader.py)

Clase para descarga asíncrona de PDFs con las siguientes características:

- Método download_single():
- Descarga un PDF individual con retry logic (3 intentos con exponential backoff usando tenacity)
- Validación de contenido (verificar Content-Type y magic bytes %PDF)
- Control de concurrencia con asyncio.Semaphore
- Sanitización de nombres de archivo
- Escritura asíncrona con aiofiles
- Manejo de errores (404, timeouts, HTML en lugar de PDF)
- Método download_batch():
- Descarga múltiple de PDFs en paralelo
- Límite de concurrencia configurable (default: 5)
- Tracking de éxitos/fallos
- Progress logging
- Retorna PDFDownloadResult con estadísticas

2. MCP Tool download_papers (src/sortgs_mcp/tools/download.py)

Tool expuesto al servidor MCP con la siguiente firma:

@mcp.tool()
async def download_papers(
  session_id: str,
  paper_indices: list[int] | None = None,  # None = todos los papers con PDF
  max_papers: int = 10
) -> dict

Flujo de trabajo:
1. Cargar sesión con SessionManager
2. Filtrar papers (por índices especificados + que tengan pdf_url)
3. Aplicar límite max_papers
4. Llamar a PDFDownloader.download_batch()
5. Actualizar metadata de sesión (pdfs_downloaded count)
6. Guardar sesión actualizada
7. Retornar resultado con paths y fallos

Output esperado:
{
"downloaded": 8,
"failed": 2,
"pdf_paths": ["data/sessions/{id}/pdfs/paper_0.pdf", "..."],
"failed_papers": [
  {"rank": 3, "title": "...", "reason": "403 Forbidden"}
]
}

3. Testing

- Unit tests para download_single (mockeando httpx):
- Descarga exitosa
- Error 404
- HTML en lugar de PDF
- Timeout
- Unit tests para download_batch:
- Batch mixto (algunos éxito, algunos fallos)
- Integration tests:
- Con URLs de PDFs reales (fixtures)
- Verificar archivos guardados correctamente
- MCP Inspector: Probar el tool manualmente

Características técnicas clave:

- Async HTTP: Usa httpx.AsyncClient para descargas asíncronas
- Retry logic: tenacity con 3 intentos y exponential backoff (2-10s)
- Concurrency control: asyncio.Semaphore para limitar descargas simultáneas
- Validación: No solo confiar en Content-Type, verificar magic bytes %PDF
- Graceful degradation: Reportar fallos pero continuar con los demás
- Progress tracking: Logging cada 10 papers

Dependencias:

- Requiere completadas: Fases 0, 1, 2 (Setup, Core, MCP Server)
- No requiere: Fase 3 (LLM Keywords) - puede desarrollarse en paralelo

Entregables:

✅ PDFDownloader async con límite de concurrencia
✅ Retry logic y error handling robusto
✅ Tool download_papers funcional
✅ Validación de PDFs (content-type, magic bytes)
✅ Tests comprehensivos (unit + integration)

