---
Task-08: Fase 7 RAG - Question Answering
---

vamos a desarrollar la fase 7 de ../../MCP_PLAN.md

Objetivo: Sistema completo de RAG para responder preguntas sobre papers indexados

Tareas principales

1. Actualizar OpenAI Client (llm/openai.py)

- Añadir método generate_answer(question, context) con retry logic
- Prompt engineering para RAG: respuestas académicas con citas
- Logging de tokens usados

2. Crear RAG Retriever (rag/retriever.py)

Clase RAGRetriever con pipeline completo:
1. Embed question → generar embedding de la pregunta
2. Retrieve chunks → buscar top-k chunks relevantes en ChromaDB
3. Build context → formatear chunks con metadata (autor, año, título)
4. Generate answer → llamar OpenAI API con context
5. Format sources → convertir distancias a similarity scores, incluir metadata

3. Crear MCP Tools (tools/query.py)

Tool: query_papers
- Input: question, session_id (opcional), top_k (default: 5)
- Output: respuesta + fuentes citadas
- Busca en una sesión específica o en todas si no se especifica

Tool: list_sessions
- Input: ninguno
- Output: lista de sesiones con metadata (keywords, papers_count, indexed status)

4. Integration Testing

Pipeline end-to-end completo:
1. Search papers
2. Download PDFs
3. Index papers
4. Query papers ← nuevo
5. Verificar respuestas coherentes con citas

Entregables

- ✅ RAGRetriever funcional
- ✅ Integración con OpenAI para generación de respuestas
- ✅ 2 tools MCP: query_papers y list_sessions
- ✅ Tests de integración end-to-end

Flujo de una query

Pregunta → Embedding → ChromaDB (top-k chunks) → Context building →
OpenAI API → Respuesta con citas → QueryResult (answer + sources)


