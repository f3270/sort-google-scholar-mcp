---
Task-02: Fase 2 - MCP Server skeleton
---

Crear un servidor MCP funcional con un tool básico que permita buscar papers en Google Scholar.

✅ Tareas Principales

1. Crear el servidor MCP (src/sortgs_mcp/server.py)

- Inicializar FastMCP con transporte stdio
- Configurar logging (archivo + consola)
- Entry point main() para ejecutar el servidor

2. Implementar tool search_papers (src/sortgs_mcp/tools/search.py)

@mcp.tool()
async def search_papers(
  keywords: str,
  num_results: int = 100,
  sort_by: str = "Citations",
  start_year: int | None = None,
  end_year: int | None = None,
  languages: list[str] | None = None
) -> dict:

Lógica del tool:
1. Crear SearchParams con los parámetros recibidos
2. Generar sesión con SessionManager.create_session()
3. Buscar papers con ScholarSearcher.search(params)
4. Guardar sesión con SessionManager.save_session()
5. Retornar resumen (session_id, papers_found, top_5_titles, csv_path)

3. Testing

- MCP Inspector: Verificar que el tool aparece y funciona
- Claude Code: Agregar el servidor y probar invocación
- Verificar: Logs, sesiones guardadas, CSVs generados

📦 Entregables

- ✅ Servidor MCP corriendo con stdio
- ✅ Tool search_papers implementado
- ✅ Integración con Claude Code funcionando
- ✅ Sistema de logging activo

Dependencias: Requiere que la Fase 1 esté completa (ScholarSearcher, SessionManager, modelos Pydantic).
