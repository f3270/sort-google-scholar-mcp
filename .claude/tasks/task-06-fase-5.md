---
Task-06: fase 5
---

Vamos a desarrollar la fase 5 del ../../MCP_PLAN.md

Objetivo: Extraer texto de PDFs descargados y crear chunks para indexación

Tareas principales

1. Crear src/sortgs_mcp/pdf/parser.py

Implementar la clase PDFParser con PyMuPDF (fitz):

- extract_text(pdf_path):
- Abre el PDF con PyMuPDF
- Itera sobre todas las páginas extrayendo texto
- Une el texto con separadores \n\n
- Retorna texto completo o None si falla
- Maneja PDFs corruptos con error handling
- extract_metadata(pdf_path):
- Extrae metadata del PDF (título, autor, etc.)
- Retorna diccionario con metadata

2. Crear src/sortgs_mcp/pdf/chunker.py

Implementar la clase TextChunker usando langchain:

- Usa RecursiveCharacterTextSplitter de langchain
- Configuración:
- chunk_size: 1000 caracteres (configurable)
- chunk_overlap: 200 caracteres (configurable)
- separators: ["\n\n", "\n", ". ", " ", ""]
- chunk_paper(text, paper, session_id):
- Divide el texto en chunks
- Añade metadata rica a cada chunk:
    - session_id, paper_title, paper_authors, paper_year
  - paper_citations, paper_rank, source_url
  - chunk_index, total_chunks
- Retorna lista de dicts con texto y metadata

3. Pipeline de integración

Crear función helper parse_and_chunk_pdf():
- Combina PDFParser + TextChunker
- Flujo: PDF → texto → chunks con metadata
- Retorna chunks listos para indexación o None si falla

4. Testing

- PDFParser: Probar con PDFs normales, basados en imágenes, corruptos
- TextChunker: Verificar chunks cortos/largos, overlap, metadata
- Integration test: Pipeline completo end-to-end

Entregables esperados

✅ PDFParser robusto con PyMuPDF
✅ TextChunker con configuración óptima para papers académicos
✅ Pipeline integrado parse + chunk
✅ Metadata preservation en todos los chunks
✅ Tests con PDFs reales (fixtures)

Notas importantes

- Se acepta extracción imperfecta (el RAG tolera ruido en el texto)
- PDFs multi-columna: best-effort (PyMuPDF puede tener issues)
- No se implementa OCR (PDFs basados en imágenes retornarán texto vacío/None)
- La limpieza de headers/footers repetidos es opcional

Esta fase prepara el contenido de los PDFs para la indexación vectorial que se hará en la Fase 6.

