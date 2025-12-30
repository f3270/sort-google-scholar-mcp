# Workplan: Fase 5 - PDF Parsing & Chunking

## 0. Metadatos del Workplan

| Campo | Valor |
|-------|-------|
| **Título** | Fase 5: PDF Parsing & Text Chunking para RAG |
| **Task ID** | task-06 |
| **Fecha creación** | 2025-12-29 |
| **Versión** | 1.0 |
| **Estado** | Draft - Pendiente aprobación |
| **Autor** | Claude Sonnet 4.5 |
| **Fase MCP_PLAN** | Fase 5: PDF Parsing (línea 969-1134) |
| **Stack** | PyMuPDF (fitz), langchain-text-splitters, Pydantic, pytest |

### Historial de Revisiones

| Versión | Fecha | Cambios | Motivo | Solicitante |
|---------|-------|---------|--------|-------------|
| 1.0 | 2025-12-29 | Versión inicial | Plan base para Fase 5 | Sistema |

---

## 1. Resumen Ejecutivo

### Descripción General
Implementar extracción de texto de PDFs académicos descargados y su división en chunks semánticos para indexación RAG. Esta fase conecta el pipeline de descarga (Fase 4) con el sistema de indexación vectorial (Fase 6).

### Alcance
**Objetivo:** Preparar contenido de PDFs para consumo por RAG system mediante:
1. Extracción robusta de texto con PyMuPDF
2. División inteligente en chunks con metadata preservation
3. Pipeline integrado parse→chunk listo para indexación

**Componentes MCP afectados:**
- `src/sortgs_mcp/pdf/parser.py` (nuevo)
- `src/sortgs_mcp/pdf/chunker.py` (nuevo)
- `src/sortgs_mcp/pdf/__init__.py` (actualizar exports)
- `tests/test_pdf_parser.py` (nuevo)
- `tests/test_pdf_chunker.py` (nuevo)

**Referencia MCP_PLAN.md:** Fase 5 (líneas 969-1134)

### Objetivos
- ✅ Extraer texto de PDFs académicos (text-based)
- ✅ Crear chunks semánticos con overlap configurable
- ✅ Preservar metadata rica por chunk (paper info + chunk position)
- ✅ Manejo graceful de PDFs corruptos/imagen-based
- ✅ Tests con fixtures reales de PDFs académicos

---

## 2. Priorización del Alcance

### MVP / CORE (Obligatorio)
**Criterio de éxito:** Pipeline funcional PDF→chunks con metadata para papers text-based normales

**Componentes obligatorios:**
1. ✅ **PDFParser.extract_text()** - Extracción básica de texto multi-página
2. ✅ **TextChunker.chunk_paper()** - Chunking con RecursiveCharacterTextSplitter
3. ✅ **parse_and_chunk_pdf()** - Pipeline integrado
4. ✅ **Metadata preservation** - session_id, paper fields, chunk position
5. ✅ **Error handling** - Return None para PDFs corruptos/vacíos
6. ✅ **Tests básicos** - PDFs normales, corruptos, pipeline end-to-end

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

---

## 3. Diseño Técnico

### Arquitectura Propuesta

```
PDFs descargados (Fase 4)
    ↓
PDFParser.extract_text(pdf_path)
    ↓
[Texto completo del paper]
    ↓
TextChunker.chunk_paper(text, paper, session_id)
    ↓
[Lista de chunks con metadata]
    ↓
Vector indexing (Fase 6)
```

### Componentes Afectados

#### 1. `src/sortgs_mcp/pdf/parser.py` (NUEVO)
**Clase: PDFParser**
- Responsabilidad: Extracción de texto de PDFs usando PyMuPDF
- Sin estado (stateless), no necesita __init__
- Métodos públicos:
  - `extract_text(pdf_path: Path) -> str | None`
  - `extract_metadata(pdf_path: Path) -> dict` (Enhanced)

#### 2. `src/sortgs_mcp/pdf/chunker.py` (NUEVO)
**Clase: TextChunker**
- Responsabilidad: División de texto en chunks semánticos
- Configuración en __init__ (chunk_size, chunk_overlap)
- Métodos públicos:
  - `chunk_paper(text: str, paper: Paper, session_id: str) -> list[dict]`

#### 3. `src/sortgs_mcp/pdf/__init__.py` (ACTUALIZAR)
- Añadir exports: PDFParser, TextChunker, parse_and_chunk_pdf

#### 4. Helper function `parse_and_chunk_pdf()` en `pdf/__init__.py`
- Pipeline completo: PDF → texto → chunks
- Orquesta PDFParser + TextChunker
- Manejo de errores centralizado

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

### Estructura de Datos

#### Chunk Dict Structure
```python
{
    "text": str,  # Texto del chunk (max chunk_size caracteres)
    "metadata": {
        "session_id": str,
        "paper_title": str,
        "paper_authors": str,
        "paper_year": int,
        "paper_citations": int,
        "paper_rank": int,
        "source_url": str,
        "chunk_index": int,      # 0-based index del chunk
        "total_chunks": int,     # Total chunks para este paper
    }
}
```

**Justificación:** Metadata rica permite:
- Filtrado posterior por año/citations
- Citación correcta en respuestas RAG
- Debug y trazabilidad

---

## 4. Plan de Desarrollo

### Tareas de Implementación

| # | Tarea | Prioridad | Criterios de Aceptación | Dependencias | Esfuerzo |
|---|-------|-----------|------------------------|--------------|----------|
| 1 | Crear `pdf/parser.py` con `PDFParser.extract_text()` | 🔴 CORE | Extrae texto de PDF multi-página, retorna str o None, maneja excepciones | Ninguna | 1h |
| 2 | Crear `pdf/chunker.py` con `TextChunker` | 🔴 CORE | Divide texto con RecursiveCharacterTextSplitter, config en __init__, retorna list[dict] | Ninguna | 1h |
| 3 | Implementar `TextChunker.chunk_paper()` con metadata | 🔴 CORE | Cada chunk tiene metadata completa (9 campos), chunk_index correcto | Tarea 2 | 0.5h |
| 4 | Crear helper `parse_and_chunk_pdf()` en `pdf/__init__.py` | 🔴 CORE | Pipeline completo PDF→chunks, manejo errores, None si falla | Tareas 1, 2, 3 | 0.5h |
| 5 | Actualizar `pdf/__init__.py` exports | 🔴 CORE | Exports: PDFParser, TextChunker, parse_and_chunk_pdf | Tarea 4 | 0.1h |
| 6 | Crear fixture PDFs en `tests/fixtures/` | 🔴 CORE | 3 PDFs: normal, corrupto, muy corto | Ninguna | 0.3h |
| 7 | Crear `tests/test_pdf_parser.py` | 🔴 CORE | Tests para extract_text: normal, corrupto, imagen-based | Tareas 1, 6 | 0.8h |
| 8 | Crear `tests/test_pdf_chunker.py` | 🔴 CORE | Tests para chunking: corto, largo, overlap, metadata | Tareas 2, 3 | 0.8h |
| 9 | Crear integration test end-to-end | 🔴 CORE | Test completo parse_and_chunk_pdf con fixture | Todas CORE | 0.5h |
| 10 | (Enhanced) Implementar `extract_metadata()` | 🟡 Opcional | Extrae metadata del PDF, retorna dict | Tarea 1 | 0.3h |
| 11 | (Enhanced) Header/footer cleaning | 🟡 Opcional | Detecta y remueve líneas repetidas | Tarea 1 | 1.5h |

**Total CORE:** ~5.5 horas
**Total Enhanced:** ~1.8 horas
**Total estimado:** ~7.3 horas (dentro de rango 3-4h para CORE MVP)

### Orden Sugerido de Implementación

**Iteración 1: Parsing básico (1.5h)**
1. Crear `pdf/parser.py` → `PDFParser.extract_text()`
2. Tests básicos de parsing
3. Fixture PDF normal

**Iteración 2: Chunking (1.5h)**
1. Crear `pdf/chunker.py` → `TextChunker`
2. Implementar `chunk_paper()` con metadata
3. Tests de chunking

**Iteración 3: Integration (1h)**
1. Helper `parse_and_chunk_pdf()`
2. Actualizar `__init__.py`
3. Integration test end-to-end

**Iteración 4: Robustness (1.5h)**
1. Fixtures adicionales (corrupto, imagen)
2. Tests edge cases
3. Error handling refinement

**Iteración 5: Enhanced (opcional, 1.8h)**
1. Extract metadata
2. Header/footer cleaning

---

## 5. Plan de Pruebas

### Estrategia de Testing

**Niveles:**
1. **Unit tests** - Funciones individuales aisladas
2. **Integration tests** - Pipeline completo con fixtures
3. **Manual smoke tests** - Verificación con PDFs reales de Scholar

### Test Cases Principales

#### Unit Tests - PDFParser (`test_pdf_parser.py`)

| Test | Objetivo | Fixture | Resultado Esperado |
|------|----------|---------|-------------------|
| `test_extract_text_normal_pdf` | Extracción exitosa | PDF normal de paper académico | Texto completo, len > 1000 chars |
| `test_extract_text_corrupted_pdf` | Manejo PDF corrupto | PDF inválido/corrupto | Return None, log error |
| `test_extract_text_empty_pdf` | PDF sin texto | PDF solo imágenes | Return None o "" |
| `test_extract_text_multipage` | Múltiples páginas | PDF 5+ páginas | Texto concatenado con `\n\n` |
| `test_extract_text_nonexistent` | Archivo no existe | Path inválido | Return None o Exception manejada |

#### Unit Tests - TextChunker (`test_pdf_chunker.py`)

| Test | Objetivo | Input | Resultado Esperado |
|------|----------|-------|-------------------|
| `test_chunk_short_text` | Texto < chunk_size | 500 chars | 1 chunk, total_chunks=1 |
| `test_chunk_long_text` | Texto > chunk_size | 5000 chars | Múltiples chunks, overlap correcto |
| `test_chunk_metadata_preservation` | Metadata completa | Paper fixture | Todos campos metadata presentes |
| `test_chunk_indices` | chunk_index secuencial | Texto largo | chunk_index 0,1,2,... correcto |
| `test_chunk_overlap` | Overlap entre chunks | Texto con chunk_overlap=200 | Últimos 200 chars chunk N en primeros de N+1 |

#### Integration Tests (`test_pdf_chunker.py` o archivo separado)

| Test | Objetivo | Fixture | Resultado Esperado |
|------|----------|---------|-------------------|
| `test_parse_and_chunk_pipeline` | Pipeline completo | PDF normal | Lista de chunks con metadata |
| `test_pipeline_corrupted_pdf` | Pipeline con error | PDF corrupto | Return None |
| `test_pipeline_with_real_paper` | End-to-end realista | PDF académico real | Chunks semánticamente coherentes |

### Tests en `tests/__init__.py` (requerido por filosofía KISS)
- **No crear tests en `__init__.py`** - pytest no ejecuta tests en __init__.py
- **Usar archivos dedicados**: `test_pdf_parser.py`, `test_pdf_chunker.py`

### Smoke Test Checklist (Manual - adjuntar a PR)

```markdown
## Smoke Test Checklist - Fase 5 PDF Parsing

### Setup
- [ ] `uv sync` ejecutado sin errores
- [ ] Dependencies `pymupdf` y `langchain-text-splitters` instaladas

### Unit Tests
- [ ] `uv run pytest tests/test_pdf_parser.py -v` - todos pasan
- [ ] `uv run pytest tests/test_pdf_chunker.py -v` - todos pasan

### Integration Test
- [ ] Pipeline completo PDF→chunks funciona con fixture
- [ ] Metadata preservation verificada (9 campos)

### Manual Testing
- [ ] Descargar PDF real de Google Scholar
- [ ] Ejecutar `parse_and_chunk_pdf()` en Python REPL
- [ ] Verificar: texto extraído coherente, chunks razonables, metadata correcta

### Edge Cases
- [ ] PDF corrupto retorna None sin crash
- [ ] PDF muy corto produce 1 chunk
- [ ] PDF largo produce múltiples chunks con overlap

### Code Quality
- [ ] No warnings en pytest
- [ ] Type hints completos
- [ ] Docstrings en funciones públicas
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
- Usar PDFs de arXiv (CC-BY license)
- Crear PDF sintético con reportlab si necesario
- Tests pueden usar PDFs minimalistas (1 página)

**Plan B:** Generar fixture PDFs con reportlab o pypdf

### Punto de Decisión GO/NO-GO

**Evaluación después de Iteración 3 (Integration):**

**Criterios GO:**
- ✅ extract_text() funciona con PDFs normales
- ✅ chunk_paper() divide texto y preserva metadata
- ✅ parse_and_chunk_pdf() pipeline completo
- ✅ Al menos 5 tests unitarios pasan

**Criterios NO-GO (requiere revisión):**
- ❌ PyMuPDF no instala o falla constantemente
- ❌ Chunks generados son incoherentes (cortan palabras, metadata perdida)
- ❌ Performance inaceptable (>5s por PDF de 10 páginas)

**Acción si NO-GO:**
- Evaluar alternativas: pdfplumber, PyPDF2
- Escalar a revisión de arquitectura RAG (¿necesitamos chunking?)

### Plan de Reducción de Alcance (repetido)

**Si tiempo < 4h restantes:**
1. ❌ Skip Enhanced features (metadata extraction, cleaning)
2. ✅ Mantener CORE: extract_text, chunk_paper, pipeline
3. ❌ Reducir tests: solo happy path + 1 edge case

**Core inamovible:**
- extract_text() básico funcional
- chunk_paper() con metadata
- parse_and_chunk_pdf()
- 3 tests mínimos (normal, corrupto, pipeline)

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
        return full_text if full_text.strip() else None
    except Exception as e:
        self.logger.error(f"Failed to parse {pdf_path}: {e}")
        return None
```

### Fixture PDFs Sugeridos
1. **normal.pdf** - Paper académico típico de arXiv (5-10 páginas)
2. **corrupted.pdf** - Archivo PDF inválido (truncado o binario corrupto)
3. **short.pdf** - Paper de 1 página (test edge case < chunk_size)

---

## 8. Criterios de Completitud

### Definition of Done
- [x] Código implementado y revisado
- [x] Type hints completos en funciones públicas
- [x] Docstrings en todas las clases y métodos públicos
- [x] Tests unitarios con >80% coverage de nuevas funciones
- [x] Integration test end-to-end pasa
- [x] Smoke test manual completado
- [x] No regressions en tests existentes (`uv run pytest` pasa)
- [x] Exports actualizados en `pdf/__init__.py`
- [x] Fixtures PDFs commiteados en `tests/fixtures/`

### Entregables Esperados
1. ✅ `src/sortgs_mcp/pdf/parser.py` - PDFParser class
2. ✅ `src/sortgs_mcp/pdf/chunker.py` - TextChunker class
3. ✅ `src/sortgs_mcp/pdf/__init__.py` - Exports actualizados + helper
4. ✅ `tests/test_pdf_parser.py` - 5+ unit tests
5. ✅ `tests/test_pdf_chunker.py` - 5+ unit tests
6. ✅ `tests/fixtures/` - 3 PDFs de ejemplo
7. ✅ Smoke test checklist (en PR description)

---

## 9. Referencias

### Documentación Externa
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [langchain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter)
- [pytest fixtures guide](https://docs.pytest.org/en/stable/fixture.html)

### Archivos del Proyecto
- `MCP_PLAN.md` - Fase 5 (líneas 969-1134)
- `src/sortgs_mcp/config.py` - Configuración chunk_size/overlap
- `src/sortgs_mcp/models.py` - Modelo Paper
- `src/sortgs_mcp/pdf/downloader.py` - Patrón async y error handling
- `tests/test_pdf_downloader.py` - Patrón de tests con fixtures

### Comandos Útiles
```bash
# Run tests
uv run pytest tests/test_pdf_parser.py -v
uv run pytest tests/test_pdf_chunker.py -v
uv run pytest -k "chunk" -v

# Test single function
uv run pytest tests/test_pdf_parser.py::test_extract_text_normal_pdf -v

# Check coverage
uv run pytest --cov=sortgs_mcp.pdf --cov-report=term-missing
```

---

## 10. Aprobación

**Plan listo para revisión del usuario.**

¿Apruebas este workplan para proceder con la implementación de la Fase 5?

Cambios sugeridos o aclaraciones necesarias:
- [ ] Ajustar estimación de tiempos
- [ ] Modificar alcance MVP/Enhanced
- [ ] Cambiar decisiones técnicas
- [ ] Añadir/remover tests
- [ ] Otros: _______________________
