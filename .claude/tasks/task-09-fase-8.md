---
Task-09: fase 8
---

Vamos a  desarrollar la fase 8 de ../../MCP_PLAN.md

Objetivo: Crear una suite de tests comprehensiva para asegurar la calidad del código.

Tareas principales:

1. Unit Tests

Crear tests unitarios para cada componente:
- test_models.py: Validación de modelos Pydantic
- test_parser.py: Parsing de HTML de Google Scholar
- test_scholar.py: Búsqueda con mocks de httpx
- test_session.py: Gestión de sesiones
- test_pdf_parser.py: Extracción de texto de PDFs
- test_chunker.py: Chunking con metadata
- test_embeddings.py: Generación de embeddings
- test_vectorstore.py: ChromaDB operations
- test_openai_client.py: Llamadas a OpenAI API (mocked)

2. Integration Tests

- test_mcp_tools.py: Cada MCP tool independientemente
- test_end_to_end.py: Workflow completo (keywords → search → download → index → query)

3. Manual Testing

- MCP Inspector: Probar los 6 tools manualmente
- Claude Code: Integración real con Claude

4. Performance Testing

- Benchmark de embeddings (100 chunks)
- Benchmark de vector search (1000 chunks)
- Pipeline completo con 10 papers
- Memory profiling

5. Error Scenarios

- Robot check de Google Scholar
- PDF 404 / corrupto
- Rate limits de OpenAI
- Session ID inválido

80% code coverage
- Tests pasando
- Validación en MCP Inspector y Claude Code
- Performance benchmarks documentados

