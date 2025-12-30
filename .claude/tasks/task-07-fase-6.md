---
Task-07: fase 6 RAG - Vector Store
---

Vamos a desarollar la fase 6 de ../../MCP_PLAN.md


🎯 Objetivo

Indexar chunks de texto de PDFs en ChromaDB con embeddings locales.

⏱️ Duración Estimada

5-6 horas

📋 Tareas Principales

1. Crear src/sortgs_mcp/rag/embeddings.py

Clase EmbeddingService:
- Cargar modelo de sentence-transformers (all-mpnet-base-v2)
- Lazy loading del modelo (solo cuando se usa)
- embed_texts(): Generar embeddings en batch para eficiencia
- embed_single(): Generar embedding para un solo texto
- Caching del modelo (singleton pattern)

2. Crear src/sortgs_mcp/rag/vectorstore.py

Clase VectorStore:
- Inicializar ChromaDB con PersistentClient (persistencia local)
- get_or_create_collection(): Una colección por session_id (aislamiento)
- add_documents(): Añadir chunks con embeddings y metadata
- query(): Buscar chunks relevantes por similitud semántica
- Búsqueda en sesión específica
- Búsqueda cross-session (todas las sesiones)
- delete_session(): Eliminar colección de una sesión

3. Crear tool MCP index_papers

En src/sortgs_mcp/tools/index.py:

Funcionalidad:
- Cargar sesión por session_id
- Encontrar PDFs descargados en data/sessions/{session_id}/pdfs/
- Para cada PDF:
- Parsear texto con PyMuPDF (Fase 5)
- Crear chunks con langchain (Fase 5)
- Asociar metadata del paper
- Generar embeddings en batch (eficiente)
- Indexar todos los chunks en ChromaDB
- Actualizar session.indexed = True
- Retornar estadísticas: papers indexados, chunks creados, tiempo

Parámetros:
- session_id (requerido)
- chunk_size (default: 1000 caracteres)
- chunk_overlap (default: 200 caracteres)

Output:
{
"session_id": "...",
"papers_indexed": 8,
"chunks_created": 342,
"indexing_time_sec": 45.3,
"failed_papers": ["Title of corrupted PDF"]
}

4. Testing

- EmbeddingService tests:
- Single embedding
- Batch embedding
- Verificar dimensiones correctas (768 para all-mpnet-base-v2)
- VectorStore tests:
- Add documents
- Query con resultados relevantes
- Cross-session query
- Delete collection
- ChromaDB persistencia
- Tool index_papers tests:
- End-to-end con sesión fixture
- Verificar chunks se indexan correctamente
- Verificar metadata preservation

🔑 Puntos Críticos

1. Modelo local: sentence-transformers NO requiere API key, todo es local
2. ChromaDB persistente: Los embeddings se guardan en disco en data/vectorstore/
3. Batch processing: Generar embeddings para todos los chunks de una vez (no 1 por 1)
4. Collection per session: Cada sesión tiene su propia colección para aislamiento
5. Metadata rica: Cada chunk lleva: session_id, paper_title, authors, year, citations, chunk_index, source_url

📦 Entregables

✅ EmbeddingService con sentence-transformers
✅ VectorStore con ChromaDB
✅ Tool index_papers completo
✅ Batch processing eficiente
✅ Tests comprehensivos

