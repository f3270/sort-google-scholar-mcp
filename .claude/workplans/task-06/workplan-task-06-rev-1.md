# Workplan: Fase 5 - PDF Parsing & Chunking (Rev 1)

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 5: PDF Parsing & Text Chunking para RAG |
| **Task ID** | task-06 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.1 (rev-1) |
| **Estado** | Draft - Revisión post-análisis codex |
| **Autor** | Claude Sonnet 4.5 |
| **Fase MCP_PLAN** | Fase 5: PDF Parsing (línea 969-1134) |
| **Stack** | PyMuPDF (fitz), langchain-text-splitters, Pydantic, pytest |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Plan base para Fase 5 | Sistema |
| 1.1 (rev-1) | 2025-12-29 | Mejoras en integración MCP+RAG, decisiones async, criterios verificables, tests contractuales | Incorporar sugerencias de análisis automatizado con codex | Usuario |

---

## 1. Resumen Ejecutivo

### Descripción General
Implementar extracción de texto de PDFs académicos descargados y su división en chunks semánticos para indexación RAG. Esta fase conecta el pipeline de descarga (Fase 4) con el sistema de indexación vectorial (Fase 6).

### Alcance
**Objetivo:** Preparar contenido de PDFs para consumo por RAG system mediante:
1. Extracción robusta de texto con PyMuPDF
2. División inteligente en chunks con metadata preservation
3. Pipeline integrado parse→chunk listo para indexación
4. **[NUEVO]** Contrato de datos explícito para integración con Fase 6

**Componentes MCP afectados:**
- `src/sortgs_mcp/pdf/parser.py` (nuevo)
- `src/sortgs_mcp/pdf/chunker.py` (nuevo)
- `src/sortgs_mcp/pdf/__init__.py` (actualizar exports)
- `tests/test_pdf_parser.py` (nuevo)
- `tests/test_pdf_chunker.py` (nuevo)
- **[NUEVO]** `tests/test_pdf_integration.py` (nuevo - tests contractuales)

**Referencia MCP_PLAN.md:** Fase 5 (líneas 969-1134)

### Objetivos
- ✅ Extraer texto de PDFs académicos (text-based)
- ✅ Crear chunks semánticos con overlap configurable
- ✅ Preservar metadata rica por chunk (paper info + chunk position)
- ✅ Manejo graceful de PDFs corruptos/imagen-based
- ✅ Tests con fixtures reales de PDFs académicos
- ✅ **[NUEVO]** Contrato de metadata validado para Fase 6 (ChromaDB)
- ✅ **[NUEVO]** Modelo de ejecución async-compatible definido

---

## 2. Priorización del Alcance

### MVP / CORE (Obligatorio)
**Criterio de éxito:** Pipeline funcional PDF→chunks con metadata para papers text-based normales + **contrato de datos validado para indexación**

**Componentes obligatorios:**
1. ✅ **PDFParser.extract_text()** - Extracción básica de texto multi-página
2. ✅ **TextChunker.chunk_paper()** - Chunking con RecursiveCharacterTextSplitter
3. ✅ **parse_and_chunk_pdf()** - Pipeline integrado
4. ✅ **Metadata preservation** - session_id, paper fields, chunk position
5. ✅ **Error handling** - Return None para PDFs corruptos/vacíos
6. ✅ **Tests básicos** - PDFs normales, corruptos, pipeline end-to-end
7. ✅ **[NUEVO]** **Tests contractuales** - Validar esquema de metadata esperado por Fase 6
8. ✅ **[NUEVO]** **Async compatibility** - Funciones ejecutables desde contexto async

### Enhanced (Opcional - implementar si hay tiempo)
**Componentes opcionales:**
1. ⚠️ **PDFParser.extract_metadata()** - Extracción de metadata del PDF (título, autor del PDF)
2. ⚠️ **Header/footer cleaning** - Detección y remoción de elementos repetidos
3. ⚠️ **Multi-column detection** - Mejor handling de papers en columnas
4. ⚠️ **Chunk quality metrics** - Estadísticas de longitud, tokens, etc.

**Justificación:** RAG tolera ruido en texto; metadata del PDF puede no coincidir con scraping de Scholar

### Nice-to-Have (Futuro)
**Componentes futuros:**
1. 🔵 **OCR integration** - Tesseract para PDFs imagen-based
2. 🔵 **Table extraction** - Parsing específico de tablas
3. 🔵 **Figure caption extraction** - Extracción de captions de figuras
4. 🔵 **Reference parsing** - Extracción estructurada de referencias

**Justificación:** Complejidad alta, beneficio marginal para MVP RAG

### Plan de Reducción de Alcance
**Si falta tiempo, recortar en orden:**
1. ❌ Header/footer cleaning (Enhanced #2)
2. ❌ Multi-column detection (Enhanced #3)
3. ❌ Chunk quality metrics (Enhanced #4)
4. ❌ PDF metadata extraction (Enhanced #1) - usar solo metadata de scraping

**Core inamovible:**
- extract_text() básico
- chunk_paper() con RecursiveCharacterTextSplitter
- parse_and_chunk_pdf() pipeline
- Metadata preservation
- Tests con fixtures
- **[NUEVO]** Tests contractuales de metadata schema

---

## 3. Diseño Técnico

### Arquitectura Propuesta

```
PDFs descargados (Fase 4)
    ↓
PDFParser.extract_text(pdf_path)  [SYNC - ejecutable en asyncio.to_thread()]
    ↓
[Texto completo del paper]
    ↓
TextChunker.chunk_paper(text, paper, session_id)  [SYNC - ejecutable en asyncio.to_thread()]
    ↓
[Lista de chunks con metadata]
    ↓
Vector indexing (Fase 6) - ChromaDB
```

**[NUEVO] Modelo de ejecución:**
- PDFParser y TextChunker son **síncronos** (PyMuPDF no es async-native)
- MCP tools que los usen (Fase 6) ejecutarán vía `asyncio.to_thread()` para no bloquear event loop
- Pattern consistente con downloader.py que usa httpx async

### Componentes Afectados

#### 1. `src/sortgs_mcp/pdf/parser.py` (NUEVO)
**Clase: PDFParser**
- Responsabilidad: Extracción de texto de PDFs usando PyMuPDF
- Sin estado (stateless), no necesita __init__
- **[NUEVO]** Logging con contexto (paper_rank, filename)
- Métodos públicos:
  - `extract_text(pdf_path: Path) -> str | None`
  - `extract_metadata(pdf_path: Path) -> dict` (Enhanced)

**Signature actualizada:**
```python
class PDFParser:
    """PDF text extraction using PyMuPDF.

    Note: Methods are synchronous. Use asyncio.to_thread() when calling from async context.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_path: Path) -> str | None:
        """Extract text from PDF. Returns None if extraction fails or PDF is empty."""
```

#### 2. `src/sortgs_mcp/pdf/chunker.py` (NUEVO)
**Clase: TextChunker**
- Responsabilidad: División de texto en chunks semánticos
- Configuración en __init__ (chunk_size, chunk_overlap)
- **[NUEVO]** Validación de metadata schema compatible con ChromaDB
- Métodos públicos:
  - `chunk_paper(text: str, paper: Paper, session_id: str) -> list[dict]`
  - **[NUEVO]** `validate_chunk_metadata(chunk: dict) -> bool` - Validar schema antes de retornar

**Signature actualizada:**
```python
class TextChunker:
    """Text chunking for RAG indexing.

    Chunks are returned as dicts compatible with ChromaDB metadata schema.
    Note: Methods are synchronous. Use asyncio.to_thread() when calling from async context.
    """

    REQUIRED_METADATA_FIELDS = {
        "session_id", "paper_title", "paper_authors", "paper_year",
        "paper_citations", "paper_rank", "source_url", "chunk_index", "total_chunks"
    }
```

#### 3. `src/sortgs_mcp/pdf/__init__.py` (ACTUALIZAR)
- Añadir exports: PDFParser, TextChunker, parse_and_chunk_pdf
- **[NUEVO]** Docstring con ejemplo de uso desde async context

#### 4. Helper function `parse_and_chunk_pdf()` en `pdf/__init__.py`
- Pipeline completo: PDF → texto → chunks
- Orquesta PDFParser + TextChunker
- Manejo de errores centralizado
- **[NUEVO]** Logging estructurado para debugging

**Signature actualizada:**
```python
def parse_and_chunk_pdf(
    pdf_path: Path,
    paper: Paper,
    session_id: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> list[dict] | None:
    """Parse PDF and create chunks with metadata.

    Returns:
        List of chunk dicts with 'text' and 'metadata' keys, or None if parsing fails.
        Chunks are ready for ChromaDB indexing (Fase 6).

    Usage from async context:
        chunks = await asyncio.to_thread(
            parse_and_chunk_pdf, pdf_path, paper, session_id
        )
    """
```

### Decisiones Técnicas (KISS)

#### ✅ Decisión 1: PyMuPDF (fitz) para parsing
**Opciones evaluadas:**
- PyPDF2: Menos robusto, parsing más lento
- pdfplumber: Más complejo, overhead innecesario
- **PyMuPDF (fitz)**: Rápido, robusto, ya en dependencies

**Decisión:** PyMuPDF (fitz)
**Justificación:** Ya instalado, performance probado, API simple

#### ✅ Decisión 2: langchain RecursiveCharacterTextSplitter
**Opciones evaluadas:**
- Implementar chunking custom: Reinventar rueda
- CharacterTextSplitter simple: No respeta estructura semántica
- **RecursiveCharacterTextSplitter**: Inteligente con separators jerárquicos

**Decisión:** RecursiveCharacterTextSplitter con separators `["\n\n", "\n", ". ", " ", ""]`
**Justificación:** Respeta párrafos → líneas → oraciones → palabras. Óptimo para papers académicos.

#### ✅ Decisión 3: Metadata en dict simple (no nuevo modelo Pydantic)
**Opciones evaluadas:**
- Crear modelo `Chunk(BaseModel)`: Más validación, más overhead
- **Dict simple con metadata conocida**: Flexible, ChromaDB acepta dicts

**Decisión:** Dict con keys fijas: text, metadata{session_id, paper_*, chunk_index, total_chunks}
**Justificación:** KISS - no necesitamos validación Pydantic en chunks intermedios. ChromaDB serializa dicts nativamente.

#### ✅ Decisión 4: No implementar OCR en MVP
**Opciones evaluadas:**
- Tesseract OCR para PDFs imagen: Complejo, lento, resultados variables
- **Skip PDFs sin texto**: Return None, log warning

**Decisión:** Aceptar que PDFs imagen-based no serán parseables
**Justificación:** Mayoría de papers académicos modernos son text-based. OCR añade complejidad sin ROI claro en MVP.

#### ✅ Decisión 5: No limpiar headers/footers automáticamente
**Opciones evaluadas:**
- Detección heurística de líneas repetidas: Frágil, muchos edge cases
- **Aceptar ruido en texto**: RAG con embeddings tolera texto repetitivo

**Decisión:** No cleaning automático de headers/footers en MVP
**Justificación:** KISS - embeddings semánticos minimizan impacto de ruido. Complejidad no justificada.

#### ✅ **[NUEVO]** Decisión 6: Funciones síncronas, async via to_thread()
**Opciones evaluadas:**
- Hacer PDFParser/TextChunker async nativos: PyMuPDF no soporta async, requiere wrappers complejos
- **Mantener sync, usar asyncio.to_thread()**: Patrón estándar para librerías sync en contexto async

**Decisión:** PDFParser y TextChunker son síncronos, MCP tools los ejecutan en thread pool
**Justificación:**
- PyMuPDF es sync-only (bindings de C++)
- `asyncio.to_thread()` es patrón recomendado para I/O sync en event loop
- Consistencia con patrón ya usado en downloader.py para Selenium fallback
- Permite testing más simple (no mock asyncio)

#### ✅ **[NUEVO]** Decisión 7: Errores se propagan a MCP tools, no se suprimen
**Opciones evaluadas:**
- Suprimir todos los errores y retornar None: Debugging difícil
- **Log error + retornar None para errores esperados, raise para inesperados**: Balance entre robustez y debugging

**Decisión:**
- PDFs corruptos/vacíos → log warning + return None (esperado)
- Errores de filesystem/permisos → raise Exception (inesperado, debe propagarse al tool)
- MCP server captura excepciones y las serializa para el cliente

**Justificación:** MCP tools deben poder reportar errores específicos al usuario (ej: "PDF corrupto" vs "permiso denegado")

### Estructura de Datos

#### Chunk Dict Structure (Contrato con Fase 6)
```python
{
    "text": str,  # Texto del chunk (max chunk_size caracteres)
    "metadata": {
        # === Campos requeridos por ChromaDB indexing (Fase 6) ===
        "session_id": str,          # UUID de la sesión
        "paper_title": str,         # Título del paper (para citación)
        "paper_authors": str,       # Autores (para citación)
        "paper_year": int,          # Año (para filtrado temporal)
        "paper_citations": int,     # Citations (para ranking de relevancia)
        "paper_rank": int,          # Rank en resultados originales
        "source_url": str,          # URL fuente (para referencia)
        "chunk_index": int,         # 0-based index del chunk
        "total_chunks": int,        # Total chunks para este paper
    }
}
```

**[NUEVO] Validaciones del contrato:**
- Todos los campos metadata son obligatorios (ChromaDB los requiere para filtering)
- `session_id` debe ser UUID válido
- `paper_year`, `paper_citations`, `paper_rank`, `chunk_index`, `total_chunks` deben ser int >= 0
- `text` no puede estar vacío (len > 0)
- `chunk_index` < `total_chunks`

**Justificación:** Metadata rica permite:
- Filtrado posterior por año/citations
- Citación correcta en respuestas RAG
- Debug y trazabilidad
- **[NUEVO]** Compatibilidad garantizada con ChromaDB schema en Fase 6

---

## 4. Plan de Desarrollo

### Tareas de Implementación

| # | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|---|-------|-----------|------------------------|--------------|----------|
| 1 | Crear `pdf/parser.py` con `PDFParser.extract_text()` | 🔴 CORE | Extrae texto de PDF multi-página, retorna str o None, maneja excepciones, **logging con contexto** | Ninguna | 1h |
| 2 | Crear `pdf/chunker.py` con `TextChunker` | 🔴 CORE | Divide texto con RecursiveCharacterTextSplitter, config en __init__, retorna list[dict], **valida metadata schema** | Ninguna | 1.2h |
| 3 | Implementar `TextChunker.chunk_paper()` con metadata | 🔴 CORE | Cada chunk tiene metadata completa (9 campos), chunk_index correcto, **validación de contrato** | Tarea 2 | 0.5h |
| 4 | Crear helper `parse_and_chunk_pdf()` en `pdf/__init__.py` | 🔴 CORE | Pipeline completo PDF→chunks, manejo errores, None si falla, **logging estructurado, docstring con ejemplo async** | Tareas 1, 2, 3 | 0.6h |
| 5 | Actualizar `pdf/__init__.py` exports | 🔴 CORE | Exports: PDFParser, TextChunker, parse_and_chunk_pdf, **docstring con ejemplo de uso desde async** | Tarea 4 | 0.2h |
| 6 | Crear fixture PDFs en `tests/fixtures/` | 🔴 CORE | **3 PDFs de arXiv con licencia CC-BY documentada**: normal (5-10 pág), corrupto, corto (1 pág) | Ninguna | 0.4h |
| 7 | Crear `tests/test_pdf_parser.py` | 🔴 CORE | Tests para extract_text: normal, corrupto, imagen-based, **verificar longitud mínima texto extraído (>100 chars para normal.pdf)** | Tareas 1, 6 | 1h |
| 8 | Crear `tests/test_pdf_chunker.py` | 🔴 CORE | Tests para chunking: corto, largo, overlap, metadata, **verificar longitud chunks 800-1200 chars, overlap exacto** | Tareas 2, 3 | 1h |
| 9 | **[NUEVO]** Crear `tests/test_pdf_integration.py` | 🔴 CORE | **Tests contractuales**: validar schema metadata, tipos, rangos; simular uso desde asyncio.to_thread() | Todas CORE | 0.8h |
| 10 | Crear integration test end-to-end | 🔴 CORE | Test completo parse_and_chunk_pdf con fixture, **verificar número exacto de chunks para normal.pdf (expect 8-12 chunks)** | Todas CORE | 0.5h |
| 11 | (Enhanced) Implementar `extract_metadata()` | 🟡 Opcional | Extrae metadata del PDF, retorna dict | Tarea 1 | 0.3h |
| 12 | (Enhanced) Header/footer cleaning | 🟡 Opcional | Detecta y remueve líneas repetidas | Tarea 1 | 1.5h |

**Total CORE:** ~7.2 horas (ajustado de 5.5h para incluir tests contractuales y criterios verificables)
**Total Enhanced:** ~1.8 horas
**Total estimado:** ~9 horas

**[NUEVO] Nota sobre estimación:** La diferencia con el rango original (3-4h) del MCP_PLAN se debe a:
- Tests contractuales adicionales para integración Fase 6 (+0.8h)
- Criterios de aceptación verificables más estrictos (+0.5h)
- Logging estructurado y documentación async (+0.4h)

### Orden Sugerido de Implementación

**Iteración 1: Parsing básico (1.5h)**
1. Crear `pdf/parser.py` → `PDFParser.extract_text()`
2. Tests básicos de parsing
3. Fixture PDF normal (arXiv)

**Iteración 2: Chunking (1.7h)**
1. Crear `pdf/chunker.py` → `TextChunker`
2. Implementar `chunk_paper()` con metadata + validación
3. Tests de chunking con criterios verificables

**Iteración 3: Integration (1.3h)**
1. Helper `parse_and_chunk_pdf()` con logging estructurado
2. Actualizar `__init__.py` con docstrings async
3. Integration test end-to-end con criterios numéricos

**Iteración 4: Robustness + Contractual tests (2h)**
1. Fixtures adicionales (corrupto, imagen)
2. Tests edge cases
3. **[NUEVO]** Tests contractuales de metadata schema
4. **[NUEVO]** Test de uso desde asyncio.to_thread()
5. Error handling refinement

**Iteración 5: Enhanced (opcional, 1.8h)**
1. Extract metadata
2. Header/footer cleaning

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Niveles:**
1. **Unit tests** - Funciones individuales aisladas
2. **Integration tests** - Pipeline completo con fixtures
3. **[NUEVO] Contractual tests** - Validación de schema para Fase 6
4. **Manual smoke tests** - Verificación con PDFs reales de Scholar

### Test Cases Principales

#### Unit Tests - PDFParser (`test_pdf_parser.py`)

| Test | Objetivo | Fixture | Resultado Esperado (Verificable) |
|------|----------|---------|----------------------------------|
| `test_extract_text_normal_pdf` | Extracción exitosa | PDF normal de arXiv | **Texto len > 100 chars, contiene palabras clave del paper** |
| `test_extract_text_corrupted_pdf` | Manejo PDF corrupto | PDF inválido/corrupto | Return None, **log.warning llamado 1 vez** |
| `test_extract_text_empty_pdf` | PDF sin texto | PDF solo imágenes | Return None o "", **log.warning con mensaje "empty"** |
| `test_extract_text_multipage` | Múltiples páginas | PDF 5+ páginas | **Texto contiene "\n\n" (separador), len > 5000 chars** |
| `test_extract_text_nonexistent` | Archivo no existe | Path inválido | **Exception raised (no None)** - error inesperado debe propagarse |

#### Unit Tests - TextChunker (`test_pdf_chunker.py`)

| Test | Objetivo | Input | Resultado Esperado (Verificable) |
|------|----------|-------|----------------------------------|
| `test_chunk_short_text` | Texto < chunk_size | 500 chars | **1 chunk, total_chunks=1, chunk_index=0, len(text) == 500** |
| `test_chunk_long_text` | Texto > chunk_size | 5000 chars | **4-6 chunks, cada chunk 800-1200 chars** |
| `test_chunk_metadata_preservation` | Metadata completa | Paper fixture | **9 campos presentes, tipos correctos (str/int)** |
| `test_chunk_indices` | chunk_index secuencial | Texto largo | **chunk_index == [0,1,2,...,N-1], chunk_index < total_chunks** |
| `test_chunk_overlap` | Overlap entre chunks | Texto con overlap=200 | **chunk[i].text[-50:] in chunk[i+1].text[:250]** (verifica overlap aproximado) |
| **[NUEVO]** `test_metadata_schema_validation` | Contrato ChromaDB | Texto normal | **Todos campos REQUIRED_METADATA_FIELDS presentes, paper_year >= 1900** |

#### **[NUEVO]** Contractual Tests (`test_pdf_integration.py`)

| Test | Objetivo | Fixture | Resultado Esperado |
|------|----------|---------|-------------------|
| `test_chunk_metadata_schema_compatibility` | Schema compatible con ChromaDB | PDF normal | **Metadata dict serializable a JSON, campos compatibles con ChromaDB types** |
| `test_chunk_metadata_types` | Tipos correctos | PDF normal | **session_id: str, paper_year: int, chunk_index: int, etc.** |
| `test_chunk_metadata_ranges` | Valores válidos | PDF normal | **paper_year >= 1900, citations >= 0, chunk_index < total_chunks** |
| `test_async_compatibility` | Ejecutable desde async | PDF normal | **asyncio.to_thread(parse_and_chunk_pdf) retorna chunks válidos** |
| `test_error_propagation` | Errores se propagan | PDF con permisos denegados | **Exception raised, no None** |

#### Integration Tests (`test_pdf_parser.py` - sección de integration)

| Test | Objetivo | Fixture | Resultado Esperado (Verificable) |
|------|----------|---------|----------------------------------|
| `test_parse_and_chunk_pipeline` | Pipeline completo | PDF normal (arXiv, 5-10 pág) | **8-12 chunks, metadata completa en todos** |
| `test_pipeline_corrupted_pdf` | Pipeline con error | PDF corrupto | **Return None, log.warning llamado** |
| `test_pipeline_with_real_paper` | End-to-end realista | PDF académico arXiv | **Chunks contienen abstract/intro/conclusiones (keywords verificables)** |

### Tests en `tests/__init__.py` (requerido por filosofía KISS)
- **No crear tests en `__init__.py`** - pytest no ejecuta tests en __init__.py
- **Usar archivos dedicados**: `test_pdf_parser.py`, `test_pdf_chunker.py`, `test_pdf_integration.py`

### Smoke Test Checklist (Manual - adjuntar a PR)

```markdown
## Smoke Test Checklist - Fase 5 PDF Parsing

### Setup
- [ ] `uv sync` ejecutado sin errores
- [ ] Dependencies `pymupdf` y `langchain-text-splitters` instaladas
- [ ] Fixtures PDFs descargados de arXiv con licencia verificada

### Unit Tests
- [ ] `uv run pytest tests/test_pdf_parser.py -v` - todos pasan (5+ tests)
- [ ] `uv run pytest tests/test_pdf_chunker.py -v` - todos pasan (6+ tests)

### Contractual Tests (NUEVO)
- [ ] `uv run pytest tests/test_pdf_integration.py -v` - todos pasan (5+ tests)
- [ ] Metadata schema compatible con ChromaDB verificado
- [ ] Async compatibility (asyncio.to_thread) funciona

### Integration Test
- [ ] Pipeline completo PDF→chunks funciona con fixture
- [ ] Metadata preservation verificada (9 campos, tipos correctos)
- [ ] Número de chunks en rango esperado (8-12 para normal.pdf)

### Manual Testing
- [ ] Descargar PDF real de arXiv (ej: 1706.03762 - "Attention Is All You Need")
- [ ] Ejecutar `parse_and_chunk_pdf()` en Python REPL
- [ ] Verificar: texto extraído contiene "abstract", chunks 800-1200 chars, metadata correcta
- [ ] Probar desde async context: `asyncio.run(asyncio.to_thread(parse_and_chunk_pdf, ...))`

### Edge Cases
- [ ] PDF corrupto retorna None sin crash
- [ ] PDF muy corto (1 página) produce 1-2 chunks
- [ ] PDF largo (10 páginas) produce 8-15 chunks con overlap verificable

### Code Quality
- [ ] No warnings en pytest
- [ ] Type hints completos
- [ ] Docstrings en funciones públicas con ejemplo async
- [ ] Logging estructurado funciona (verificar en sortgs_mcp.log)
```

---

## 6. Plan de Contingencia

### Escenarios de Riesgo

#### Riesgo 1: PyMuPDF extrae texto malformado de PDFs multi-columna
**Probabilidad:** Media
**Impacto:** Bajo (RAG tolera ruido)

**Mitigación:**
- Aceptar extracción imperfecta como "best-effort"
- Documentar limitación en docstring
- Considerar Enhanced: multi-column detection (fuera de MVP)

**Plan B:** Ninguno necesario - RAG embeddings son robustos a ruido

#### Riesgo 2: PDFs académicos tienen formatos no estándar
**Probabilidad:** Media
**Impacto:** Medio

**Mitigación:**
- Tests con fixtures de varios publishers (Springer, IEEE, arXiv)
- Logging detallado de errores de parsing
- Graceful degradation: skip PDFs problemáticos

**Plan B:** Skip papers con PDFs no parseables, continuar con resto

#### Riesgo 3: Chunk size no óptimo para papers académicos
**Probabilidad:** Baja
**Impacto:** Medio (afecta calidad RAG)

**Mitigación:**
- Usar defaults probados: chunk_size=1000, overlap=200
- Hacer configurable en Settings
- Documentar que puede ajustarse post-MVP

**Plan B:** Ajustar configuración basado en feedback de Fase 6

#### Riesgo 4: Fixture PDFs no disponibles o con licencias restrictivas
**Probabilidad:** Baja
**Impacto:** Bajo

**Mitigación:**
- **[NUEVO]** Usar PDFs de arXiv con licencia CC-BY explícita (documentar en fixtures/README.md)
- Crear PDF sintético con reportlab si necesario
- Tests pueden usar PDFs minimalistas (1 página)

**Plan B:** Generar fixture PDFs con reportlab o pypdf

#### **[NUEVO]** Riesgo 5: asyncio.to_thread() causa overhead excesivo
**Probabilidad:** Muy baja
**Impacto:** Bajo

**Mitigación:**
- Profiling con PDFs típicos (5-10 páginas)
- Overhead esperado: <100ms adicionales por PDF
- Alternativa: ProcessPoolExecutor si thread pool no es suficiente

**Plan B:** Si overhead >500ms, considerar ProcessPoolExecutor para parsing batch

#### **[NUEVO]** Riesgo 6: ChromaDB rechaza metadata por incompatibilidad de schema
**Probabilidad:** Baja (mitigado por tests contractuales)
**Impacto:** Alto (bloquea Fase 6)

**Mitigación:**
- Tests contractuales validan schema antes de Fase 6
- Coordinación con implementador de Fase 6 para validar contrato
- Documentar schema en docstring de chunk_paper()

**Plan B:** Si schema cambia en Fase 6, ajustar metadata en hotfix (cambio menor)

### Punto de Decisión GO/NO-GO

**Evaluación después de Iteración 3 (Integration):**

**Criterios GO:**
- ✅ extract_text() funciona con PDFs normales (len > 100 chars)
- ✅ chunk_paper() divide texto y preserva metadata (9 campos)
- ✅ parse_and_chunk_pdf() pipeline completo retorna chunks válidos
- ✅ Al menos 5 tests unitarios pasan
- ✅ **[NUEVO]** Tests contractuales básicos pasan (schema validation)

**Criterios NO-GO (requiere revisión):**
- ❌ PyMuPDF no instala o falla constantemente
- ❌ Chunks generados son incoherentes (cortan palabras, metadata perdida)
- ❌ Performance inaceptable (>5s por PDF de 10 páginas)
- ❌ **[NUEVO]** Metadata schema incompatible con ChromaDB (tests contractuales fallan)

**Acción si NO-GO:**
- Evaluar alternativas: pdfplumber, PyPDF2
- Escalar a revisión de arquitectura RAG (¿necesitamos chunking?)
- **[NUEVO]** Si problema es schema: coordinar con Fase 6 para ajustar contrato

### Plan de Reducción de Alcance (repetido)

**Si tiempo < 4h restantes:**
1. ❌ Skip Enhanced features (metadata extraction, cleaning)
2. ✅ Mantener CORE: extract_text, chunk_paper, pipeline
3. ❌ Reducir tests: solo happy path + 1 edge case
4. ✅ **[NUEVO]** Mantener tests contractuales (críticos para Fase 6)

**Core inamovible:**
- extract_text() básico funcional
- chunk_paper() con metadata
- parse_and_chunk_pdf()
- 3 tests mínimos (normal, corrupto, pipeline)
- **[NUEVO]** 2 tests contractuales mínimos (schema validation, async compatibility)

---

## 7. Notas de Implementación

### Imports Necesarios
```python
# parser.py
import fitz  # PyMuPDF
from pathlib import Path
import logging

# chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sortgs_mcp.models import Paper

# __init__.py
from sortgs_mcp.pdf.parser import PDFParser
from sortgs_mcp.pdf.chunker import TextChunker

# [NUEVO] Para tests contractuales
import asyncio  # test_pdf_integration.py
```

### Configuración RecursiveCharacterTextSplitter
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,          # De settings.chunk_size
    chunk_overlap=200,        # De settings.chunk_overlap
    separators=["\n\n", "\n", ". ", " ", ""],  # Jerárquico
    length_function=len,      # Contar caracteres (no tokens)
)
```

### Error Handling Pattern
```python
def extract_text(self, pdf_path: Path) -> str | None:
    try:
        doc = fitz.open(pdf_path)
        # ... extraction logic
        doc.close()

        if not full_text.strip():
            self.logger.warning(f"PDF is empty or contains no extractable text: {pdf_path}")
            return None

        return full_text
    except FileNotFoundError as e:
        # Unexpected error - propagate to caller (MCP tool will handle)
        raise
    except Exception as e:
        # PDF corruption or parsing error - expected, log and return None
        self.logger.error(f"Failed to parse {pdf_path}: {e}")
        return None
```

### **[NUEVO]** Async Usage Pattern
```python
# En MCP tool (Fase 6 - index_papers)
from sortgs_mcp.pdf import parse_and_chunk_pdf
import asyncio

async def index_papers_tool(session_id: str):
    # ... cargar session y PDFs

    for pdf_file in pdf_files:
        # Ejecutar parsing sync en thread pool
        chunks = await asyncio.to_thread(
            parse_and_chunk_pdf,
            pdf_file,
            paper,
            session_id,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        if chunks:
            # ... proceder con indexación
```

### Fixture PDFs Sugeridos
1. **normal.pdf** - Paper de arXiv con licencia CC-BY (5-10 páginas)
   - Ejemplo: arXiv:1706.03762 "Attention Is All You Need"
   - Documentar URL y licencia en `tests/fixtures/README.md`
2. **corrupted.pdf** - Archivo PDF inválido (truncado o binario corrupto)
3. **short.pdf** - Paper de 1 página (test edge case < chunk_size)

**[NUEVO]** Crear `tests/fixtures/README.md`:
```markdown
# PDF Fixtures for Testing

## Sources and Licenses

- **normal.pdf**: arXiv:1706.03762 "Attention Is All You Need"
  - License: arXiv perpetual, non-exclusive license (CC-BY compatible)
  - URL: https://arxiv.org/abs/1706.03762
  - Downloaded: 2025-12-29

- **corrupted.pdf**: Synthetically corrupted version of normal.pdf (first 50% truncated)

- **short.pdf**: Single-page excerpt from normal.pdf (abstract only)

All fixtures are used for testing purposes only and fall under fair use for software testing.
```

---

## 8. Criterios de Completitud

### Definition of Done
- [x] Código implementado y revisado
- [x] Type hints completos en funciones públicas
- [x] Docstrings en todas las clases y métodos públicos **con ejemplo async**
- [x] Tests unitarios con >80% coverage de nuevas funciones
- [x] **[NUEVO]** Tests contractuales para metadata schema pasan
- [x] **[NUEVO]** Test de async compatibility pasa
- [x] Integration test end-to-end pasa
- [x] Smoke test manual completado
- [x] No regressions en tests existentes (`uv run pytest` pasa)
- [x] Exports actualizados en `pdf/__init__.py`
- [x] Fixtures PDFs commiteados en `tests/fixtures/` **con README.md de licencias**
- [x] **[NUEVO]** Logging estructurado funciona (verificado en log file)

### Entregables Esperados
1. ✅ `src/sortgs_mcp/pdf/parser.py` - PDFParser class
2. ✅ `src/sortgs_mcp/pdf/chunker.py` - TextChunker class con validación de schema
3. ✅ `src/sortgs_mcp/pdf/__init__.py` - Exports actualizados + helper + docstring async
4. ✅ `tests/test_pdf_parser.py` - 5+ unit tests con criterios verificables
5. ✅ `tests/test_pdf_chunker.py` - 6+ unit tests con criterios verificables
6. ✅ **[NUEVO]** `tests/test_pdf_integration.py` - 5+ tests contractuales
7. ✅ `tests/fixtures/` - 3 PDFs de ejemplo + README.md con licencias
8. ✅ Smoke test checklist (en PR description)

---

## 9. Referencias

### Documentación Externa
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [langchain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter)
- [pytest fixtures guide](https://docs.pytest.org/en/stable/fixture.html)
- **[NUEVO]** [asyncio.to_thread() docs](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
- **[NUEVO]** [ChromaDB metadata filtering](https://docs.trychroma.com/usage-guide#filtering-by-metadata)

### Archivos del Proyecto
- `MCP_PLAN.md` - Fase 5 (líneas 969-1134), Fase 6 (líneas 1137-1394)
- `src/sortgs_mcp/config.py` - Configuración chunk_size/overlap
- `src/sortgs_mcp/models.py` - Modelo Paper
- `src/sortgs_mcp/pdf/downloader.py` - Patrón async y error handling
- `tests/test_pdf_downloader.py` - Patrón de tests con fixtures
- **[NUEVO]** `src/sortgs_mcp/rag/vectorstore.py` (Fase 6) - Consumidor de chunks, schema ChromaDB

### Comandos Útiles
```bash
# Run tests
uv run pytest tests/test_pdf_parser.py -v
uv run pytest tests/test_pdf_chunker.py -v
uv run pytest tests/test_pdf_integration.py -v  # NUEVO
uv run pytest -k "chunk" -v

# Test single function
uv run pytest tests/test_pdf_parser.py::test_extract_text_normal_pdf -v

# Check coverage
uv run pytest --cov=sortgs_mcp.pdf --cov-report=term-missing

# Run all PDF tests
uv run pytest tests/test_pdf*.py -v
```

---

## 10. Aprobación

**Plan revisado listo para aprobación del usuario.**

### Cambios aplicados en rev-1:

**ALTA Prioridad (aplicados):**
- ✅ Añadidos criterios de aceptación explícitos para integración MCP+RAG
- ✅ Completadas decisiones técnicas sobre threading/async (Decisión 6)
- ✅ Definido cómo se reportan errores al MCP server (Decisión 7)
- ✅ Añadido contrato de metadata explícito para Fase 6

**MEDIA Prioridad (aplicados):**
- ✅ Definidos tests de integración contractuales (test_pdf_integration.py)
- ✅ Ajustados criterios de aceptación de chunking para ser verificables (rangos numéricos, keywords)
- ✅ Añadido test de async compatibility

**BAJA Prioridad (documentadas):**
- ✅ Aclarado cómo se obtienen fixtures PDF (arXiv CC-BY, con README.md)
- ✅ Unificados tiempos estimados (7.2h CORE, nota explicativa de diferencia con rango original)

¿Apruebas este workplan revisado para proceder con la implementación de la Fase 5?

Cambios sugeridos o aclaraciones necesarias:
- [ ] Ajustar estimación de tiempos
- [ ] Modificar alcance MVP/Enhanced
- [ ] Revisar decisiones técnicas async
- [ ] Ajustar tests contractuales
- [ ] Otros: _______________________
