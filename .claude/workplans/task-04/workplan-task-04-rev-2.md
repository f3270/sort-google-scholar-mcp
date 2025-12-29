# Plan de Trabajo: Task-04 - Fase 3 LLM Keyword Generation

**Fecha de Creación**: 2025-12-29
**Versión**: rev-2
**Estado**: Pendiente de Aprobación
**Autor**: Claude Code
**Stack**: OpenAI API (AsyncOpenAI) + tenacity + MCP (stdio) + pydantic

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | 2025-12-29 | Plan inicial | Creación del workplan para Fase 3 - LLM Keyword Generation |
| rev-1 | 2025-12-29 | Mejoras post-revisión con codex: tests en MVP, clarificación MCP/session, error handling OpenAI, simplificación smoke test, documentación timeouts | Incorporar sugerencias de análisis automatizado |
| rev-2 | 2025-12-29 | Mejoras post-revisión codex (round 2): alineación LLM stack justificada, tests obligatorios en MVP protegidos, error handling granular sin RuntimeError wrapper, integración sesiones clarificada, criterios QA medibles definidos | Resolver desalineaciones críticas detectadas por codex |

---

## 1. Resumen Ejecutivo

### Descripción General

Implementar la **Fase 3 del MCP_PLAN.md**: Sistema de generación inteligente de keywords usando OpenAI GPT-4o-mini. Esta fase agrega capacidades de LLM al proyecto Sort Google Scholar MCP, permitiendo que el sistema genere variaciones optimizadas de keywords de búsqueda para mejorar la exploración de literatura académica.

La tarea consiste en crear:
1. **Cliente OpenAI async** (`OpenAIClient`) con retry logic
2. **Sistema de prompts** para keyword generation
3. **MCP tool** `generate_search_keywords` accesible desde Claude Code
4. **Tests unitarios** con mocking de API OpenAI

**Beneficio**: Los usuarios podrán pedir al sistema que genere keywords académicas optimizadas en lugar de crearlas manualmente, mejorando la cobertura y relevancia de búsquedas en Google Scholar.

### Justificación: OpenAI vs Anthropic Claude

**IMPORTANTE - Alineación con Stack del Proyecto**:

El proyecto **sortgs-mcp** declara en su stack principal el uso de **Anthropic Claude** para RAG (Fase 7: Answer Generation). Sin embargo, **para la Fase 3 (Keyword Generation) se usa OpenAI GPT-4o-mini** por las siguientes razones técnicas y estratégicas:

**Razones para usar OpenAI en Fase 3**:
1. **Costo**: gpt-4o-mini es significativamente más económico ($0.15/$0.60 por 1M tokens) vs Claude Haiku ($0.25/$1.25 por 1M tokens) - ~40% ahorro
2. **Velocidad**: gpt-4o-mini optimizado para generación rápida (<2s típico)
3. **Simplicidad MVP**: Task-03 ya migró configuración a OpenAI, aprovechar infraestructura existente
4. **Scope limitado**: Keyword generation es tarea simple (no requiere razonamiento complejo de Claude)
5. **Separación de concerns**: RAG (Fase 7) usará Claude para razonamiento profundo; keywords son generación ligera

**Plan de consistencia futura**:
- **Fase 7 (RAG Answer Generation)**: Usará **Anthropic Claude** (Sonnet/Opus) para razonamiento complejo
- **Fase 3 (Keyword Generation)**: Mantiene **OpenAI gpt-4o-mini** para generación rápida y económica
- **Arquitectura final**: Sistema híbrido multi-LLM optimizando cada proveedor para su fortaleza
- **Alternativa futura**: Si se requiere unificar, implementar fallback Claude → OpenAI para keywords

**Esta decisión está alineada con KISS**: usar la herramienta más simple y económica para cada tarea específica, sin sobre-ingeniería de abstracción multi-provider en MVP.

### Alcance y Objetivos

**Objetivo Principal**: Habilitar generación automática de keywords usando LLM (gpt-4o-mini) accesible via MCP tool.

**Componentes del sistema MCP afectados**:
- ✅ LLM Integration: `src/sortgs_mcp/llm/openai.py` (NUEVO)
- ✅ Prompt System: `src/sortgs_mcp/llm/keywords.py` (NUEVO)
- ✅ MCP Tool: `src/sortgs_mcp/tools/search.py` (MODIFICAR - agregar tool)
- ✅ Tests: `tests/test_llm_keywords.py` (NUEVO - OBLIGATORIO MVP)
- ✅ Tests: `tests/test_tool_validation.py` (NUEVO - OBLIGATORIO MVP)
- ❌ Scraping/PDF/RAG: Sin cambios (fuera de alcance)

**Referencia a fase del MCP_PLAN.md**:
- **Fase 3**: LLM Keyword Generation (líneas 672-836 de MCP_PLAN.md)
- Duración estimada: 4-5 horas
- Prioridad: 🟡 Alta (no crítica - sistema funciona sin ella)

**Dependencias cumplidas**:
- ✅ Fase 0: Setup completado (task-03 migró configuración a OpenAI)
- ✅ Fase 1: Core Refactoring (modelos pydantic funcionales)
- ✅ Fase 2: MCP Server Skeleton (servidor funcionando, `search_papers` implementado)

### Estimación de Tiempo

**Total estimado**: 4-5 horas

- Implementar `OpenAIClient`: 1.5h
- Implementar sistema de prompts: 1h
- Implementar MCP tool: 1h
- Testing: 1-1.5h
- Buffer: 0.5h

---

## 2. Priorización del Alcance

### 🔴 MVP/CORE (Obligatorio)

**Criterio de éxito**: Tool `generate_search_keywords` funcional, invocable desde Claude Code, genera keywords válidas usando OpenAI API.

Funcionalidades core:
- [x] Clase `OpenAIClient` en `llm/openai.py` con método `generate_keywords()`
- [x] Cliente `AsyncOpenAI` funcional con retry logic (tenacity)
- [x] Funciones de prompts en `llm/keywords.py`: `build_keyword_prompt()`, `parse_keyword_response()`
- [x] MCP tool `generate_search_keywords` en `tools/search.py`
- [x] Validación de inputs (num_variations 1-5)
- [x] Error handling granular con tipos específicos (sin RuntimeError wrapper genérico)
- [x] Logging de tokens usados
- [x] **Tests unitarios mínimos** (OBLIGATORIO - NUNCA RECORTAR):
  - `parse_keyword_response()` con casos edge (JSON, markdown, malformado)
  - Validación de inputs del tool (num_variations, query vacío)

**Componentes MVP**:
- `src/sortgs_mcp/llm/openai.py`
- `src/sortgs_mcp/llm/keywords.py`
- `src/sortgs_mcp/tools/search.py` (modificación)
- `tests/test_llm_keywords.py` (parsing tests - **OBLIGATORIO EN MVP**)
- `tests/test_tool_validation.py` (input validation - **OBLIGATORIO EN MVP**)

**IMPORTANTE - Tests en MVP**: Los tests unitarios básicos son **OBLIGATORIOS** y **NO SE ELIMINAN** en reducción de alcance. KISS no significa omitir tests mínimos, significa tests simples pero suficientes para garantizar calidad.

### 🟡 Enhanced (Si hay tiempo)

Funcionalidades que agregan valor pero no bloquean:
- [ ] Tests unitarios exhaustivos con mocking completo de OpenAI (más allá de parsing básico)
- [ ] Test de integración con API real (pequeño - consume tokens)
- [ ] Método `generate_answer()` stub para Fase 7 (solo signature, no implementación)
- [ ] Validación automática de calidad de keywords generadas
- [ ] Métricas de costo (tokens usados, costo estimado)

**Componentes Enhanced**:
- `tests/test_llm_openai_client.py` (mocking completo de AsyncOpenAI)

### 🟢 Nice-to-Have (Futuras iteraciones)

Para versiones posteriores:
- [ ] Cache de keywords generadas (evitar llamadas duplicadas)
- [ ] Sistema de templates de prompts configurable
- [ ] Multiple LLM providers (fallback a Anthropic si OpenAI falla)
- [ ] Evaluación automática de calidad de keywords

**Justificación postponer**: Son mejoras de optimización que pueden agregarse después del MVP funcional.

### Plan de Reducción de Alcance

**Si se excede el tiempo estimado:**

1. **Recorte Nivel 1**: Eliminar Enhanced completo (tests exhaustivos, API real) → Ahorro: 1-1.5h
2. **Recorte Nivel 2**: Simplificar parsing a solo JSON directo (sin fallbacks markdown) → Ahorro: 20min
3. **Core absoluto inamovible (NUNCA RECORTAR)**:
   - `OpenAIClient.generate_keywords()` funcional
   - Tool `generate_search_keywords` invocable
   - Parsing básico de respuestas (JSON directo mínimo)
   - **Tests unitarios obligatorios** (parsing + validation) ← **NO ELIMINAR**
   - Error handling granular

**CRÍTICO**: Los tests CORE (T9, T10) son **requisitos del criterio de aceptación** y **NUNCA se eliminan** en reducción de alcance. Si falta tiempo, se recortan features Enhanced o se simplifica parsing, pero tests mínimos se mantienen.

---

## 3. Diseño Técnico

### Arquitectura Propuesta

**Flujo de datos**:
```
User (Claude Code)
  ↓
MCP Tool: generate_search_keywords
  ↓
OpenAIClient.generate_keywords()
  ├─ build_keyword_prompt(query, num_variations)
  ├─ AsyncOpenAI.chat.completions.create()
  └─ parse_keyword_response(response)
  ↓
Return: {"keywords": ["kw1", "kw2", "kw3"]}
```

**Componentes nuevos**:

1. **`llm/openai.py`**: Cliente OpenAI async
   - `OpenAIClient` class
   - Método `generate_keywords(query, num_variations)` → list[str]
   - Método `generate_answer(question, context)` → str (stub para Fase 7)
   - Retry logic con `tenacity`
   - Logging de uso de tokens

2. **`llm/keywords.py`**: Sistema de prompts
   - `KEYWORD_GENERATION_PROMPT` constant (template)
   - `build_keyword_prompt(query, num_variations)` → str
   - `parse_keyword_response(response)` → list[str]
   - Manejo de múltiples formatos de respuesta

3. **`tools/search.py`**: Tool MCP (modificación)
   - Agregar decorador `@mcp.tool()` para `generate_search_keywords`
   - Validación de inputs
   - Instanciación de `OpenAIClient` con `settings.openai_api_key`
   - Return dict con formato MCP

### Diagrama de Componentes

```mermaid
graph TD
    A[Claude Code User] -->|invoke tool| B[MCP Server]
    B -->|@mcp.tool| C[generate_search_keywords]
    C -->|validate inputs| C
    C -->|create client| D[OpenAIClient]
    D -->|build prompt| E[keywords.py: build_keyword_prompt]
    E -->|template| F[KEYWORD_GENERATION_PROMPT]
    D -->|API call| G[AsyncOpenAI.chat.completions.create]
    G -->|response| D
    D -->|parse| H[keywords.py: parse_keyword_response]
    H -->|retry 3x| I{JSON valid?}
    I -->|Yes| J[Return keywords list]
    I -->|No| K[Try markdown extraction]
    K -->|Still no| L[Fallback: extract quoted strings]
    L --> J
    J -->|format dict| C
    C -->|return| B
    B -->|stdio| A
```

### Consideraciones Específicas de MCP + OpenAI

**MCP Tools Affected**:
- [x] ¿Requiere nuevos tools? **SÍ** - `generate_search_keywords`
- [ ] ¿Cambios en tool schemas? **NO** - Solo agregar tool nuevo
- [ ] ¿Cambios en MCP server entry point? **NO** - Pattern de import lateral se mantiene

**MCP Session Management - Integración con Arquitectura Session-Based**:

Este tool es **stateless** (sin sesión propia), pero se integra con la arquitectura session-based del MCP server de las siguientes maneras:

1. **No requiere SessionManager**: Es un utility tool puro (input → output)
2. **Justificación**: Keyword generation es operación independiente sin estado persistente
3. **Diferencia con otros tools**:
   - `search_papers` y `index_papers` crean/modifican sesiones → usan `SessionManager`
   - `generate_search_keywords` genera keywords on-demand → NO usa `SessionManager`
4. **Implicación**: No requiere `session_id` como parámetro, no guarda resultados en disco

**Integración con flujo session-based**:
- **Patrón de uso**: Usuario primero genera keywords, luego las usa con `search_papers` (que SÍ crea sesión)
- **Workflow típico**:
  ```
  1. generate_search_keywords(query="transformers NLP") → keywords list
  2. search_papers(keywords=keywords[0], ...) → crea session_id
  3. index_papers(session_id) → modifica session existente
  ```
- **Registro/Auditoría**:
  - Tool logs llamadas vía logger (query, num_variations, tokens usados)
  - No persiste resultados (keywords efímeras, usuario las usa inmediatamente)
  - Si se requiere auditoría completa futura, implementar logger centralizado MCP (fuera de alcance Fase 3)

**Patrón arquitectónico**: Similar a un helper/utility tool - pure function sin side effects persistentes.

**LLM Integration**:
- [x] **Cliente**: `AsyncOpenAI` (async nativo)
- [x] **Modelo**: `gpt-4o-mini` (config: `settings.openai_model_keywords`)
- [x] **API Key**: `settings.openai_api_key` (opcional - tool no disponible si None)
- [x] **Retry**: 3 intentos, exponential backoff (1s, 4s, 10s)
- [x] **Timeout**: AsyncOpenAI usa httpx internamente con timeout default de 30s (configurable via `timeout` param en constructor si se requiere ajustar)
- [x] **Cost tracking**: Log tokens usados (input/output)

**Error Handling Strategy - Política Clara de Errores MCP**:

**Principio**: Preservar tipos específicos de error para debugging y manejo granular. **NO envolver todo en RuntimeError genérico**.

**Clasificación de errores**:

1. **SDK Exceptions (openai module)** - https://github.com/openai/openai-python:
   ```python
   from openai import (
       APIError,              # Base exception para errores de API
       RateLimitError,        # Subclase de APIError - rate limits
       AuthenticationError,   # API key inválida o sin permisos
       APIConnectionError     # Errores de red/conexión
   )
   ```
   - **`RateLimitError`**: Retry 3x con backoff → Si falla, propagar directo (MCP tool devolverá error al cliente)
   - **`APIConnectionError`**: Retry 3x con backoff → Si falla, propagar directo
   - **`AuthenticationError`**: NO retry → Propagar directo (hint: verificar API key)
   - **`APIError`** (otros): Retry 3x → Si falla, propagar directo

2. **Application Exceptions**:
   - **`ValueError`** (validation de inputs): NO retry → Propagar directo (input inválido)
   - **`json.JSONDecodeError`** (parsing): Intentar fallbacks → Si todos fallan, `ValueError` con mensaje claro

3. **MCP Tool Error Reporting**:
   - **Errores propagados**: MCP framework convierte exceptions en error responses automáticamente
   - **Formato MCP error**: `{"error": {"type": "ValueError", "message": "num_variations must be between 1 and 5"}}`
   - **NO WRAPPER**: Dejar que excepciones específicas lleguen al cliente MCP (mejor debugging)
   - **Logging**: `logger.error()` con `exc_info=True` para stacktrace completo

**Ejemplo de error handling en tool**:
```python
@mcp.tool()
async def generate_search_keywords(query: str, num_variations: int = 3) -> dict:
    # Validation - ValueError propagado directo
    if not (1 <= num_variations <= 5):
        raise ValueError("num_variations must be between 1 and 5")

    # OpenAI call - Exceptions propagadas directo (MCP las maneja)
    try:
        client = OpenAIClient(...)
        keywords = await client.generate_keywords(query, num_variations)
        return {"keywords": keywords}
    except AuthenticationError as exc:
        logger.error(f"OpenAI auth failed: {exc}", exc_info=True)
        raise  # Propagar directo - MCP formatea error
    except RateLimitError as exc:
        logger.error(f"OpenAI rate limit: {exc}", exc_info=True)
        raise  # Propagar directo
    # NO catch genérico Exception - dejar propagar
```

**Beneficios**:
- ✅ Cliente MCP recibe tipo específico de error (`AuthenticationError` vs `RateLimitError`)
- ✅ Debugging más fácil (stacktrace completo, tipo exacto)
- ✅ Retry logic en tenacity maneja errores retriables automáticamente
- ✅ No se pierde información envolviendo en `RuntimeError` genérico

**Trade-off aceptado**: Más líneas de código (imports explícitos, logging), pero mejor manejo de errores.

**Prompt Engineering**:
- Template claro y específico para Google Scholar
- Instrucción explícita: "Return ONLY a JSON list"
- Formato de ejemplo incluido en prompt
- Validación de num_variations (1-5 razonable)

### Decisiones de Arquitectura

**Tool Design**:
- [x] **Asíncrono**: Tool es `async def` (MCP soporta async)
- [ ] **Estado global**: NO requiere (stateless)
- [x] **Timeout**: 30s suficiente para llamada OpenAI (rápida con gpt-4o-mini)
- [x] **Ubicación**: `tools/search.py` (lógicamente agrupado con `search_papers`)

**Client Design**:
- Pattern: Similar a `ScholarSearcher` (async context manager)
- Lifecycle: NO usa context manager (stateless, no necesita cleanup)
- Simplificación: Instancia directa `AsyncOpenAI(api_key=...)` sin complexity

**Testing Strategy**:
- [x] Unit tests con mocking de `AsyncOpenAI` usando `unittest.mock` o `pytest-mock`
- [x] Test parsing con respuestas fixture (JSON válido, markdown, malformado)
- [ ] Integration test con API real: **Opcional** (consume tokens, $0.00006 típico)
- [x] MCP Inspector testing: **Manual** (validación funcional)

### Decisiones Técnicas KISS

**¿Se reutilizan patrones existentes?**
- ✅ SÍ - Tool pattern de `search_papers`: decorador @mcp.tool(), docstring, validación, error handling
- ✅ SÍ - Config pattern: `settings.openai_api_key`, `settings.openai_model_keywords`
- ✅ SÍ - Logging pattern: `logger.info()` con contexto

**¿Se evita sobre-ingeniería?**
- ✅ SÍ - No implementamos cache complejo (futuro)
- ✅ SÍ - No implementamos múltiples LLM providers (MVP solo OpenAI)
- ✅ SÍ - No implementamos evaluación automática de keywords (manual validation suficiente)

**¿Solución más simple posible?**
- ✅ SÍ - Cliente OpenAI directo sin wrapper excesivo
- ✅ SÍ - Parsing con fallbacks simples (JSON → markdown → quoted strings)
- ✅ SÍ - Un solo template de prompt (no sistema de templates)

---

## 4. Plan de Desarrollo

### Tareas ordenadas por prioridad y dependencia

| ID | Prioridad | Tarea | Criterios de Aceptación | Dependencias | Esfuerzo |
|----|-----------|-------|-------------------------|--------------|----------|
| T1 | 🔴 CORE | Crear `llm/openai.py` - estructura base | Archivo creado, `OpenAIClient` class con `__init__`, imports | - | 15min |
| T2 | 🔴 CORE | Implementar `OpenAIClient.generate_keywords()` | Método async funcional, llama OpenAI API, retry logic | T1 | 1h |
| T3 | 🔴 CORE | Crear `llm/keywords.py` - template de prompt | `KEYWORD_GENERATION_PROMPT` constant definida | - | 15min |
| T4 | 🔴 CORE | Implementar `build_keyword_prompt()` | Función retorna prompt formateado con query y num_variations | T3 | 10min |
| T5 | 🔴 CORE | Implementar `parse_keyword_response()` | Parsea JSON, markdown, fallback a quoted strings | T3 | 30min |
| T6 | 🔴 CORE | Agregar tool en `tools/search.py` | `generate_search_keywords` con @mcp.tool() decorador | T2, T4, T5 | 45min |
| T7 | 🔴 CORE | Validación de inputs en tool | num_variations 1-5, query no vacío | T6 | 10min |
| T8 | 🔴 CORE | Error handling granular y logging | Propagación de excepciones específicas, logger.info/error | T6 | 15min |
| T9 | 🔴 CORE | **Unit tests - parsing edge cases (OBLIGATORIO)** | Tests para `parse_keyword_response()`: JSON, markdown, malformado, vacío | T5 | 20min |
| T10 | 🔴 CORE | **Unit tests - tool validation (OBLIGATORIO)** | Tests para validación de inputs del tool (num_variations, query vacío) | T7 | 15min |
| T11 | 🔴 CORE | Testing manual con MCP Inspector | Tool invocable, retorna keywords válidas | T6, T7, T8 | 20min |
| T12 | 🟡 Enhanced | Unit tests - OpenAIClient mock | Test con mock de AsyncOpenAI, verifica llamadas correctas | T2 | 30min |
| T13 | 🟡 Enhanced | Integration test con API real | Test pequeño (consume ~$0.00006) | T6 | 15min |

**Orden de implementación sugerido**:
T1 → T3 → T4 → T5 → T2 → T6 → T7 → T8 → **T9 → T10** → T11 → [T12 → T13 si hay tiempo]

**Total tiempo core**: ~4h (incluye tests mínimos obligatorios)
**Total tiempo con enhanced**: ~4.75h

**IMPORTANTE**: T9 y T10 son **OBLIGATORIOS** y deben ejecutarse incluso si se aplica reducción de alcance.

---

## 5. Plan de Pruebas

### Estrategia de Testing

- **Unit tests CORE (MVP - OBLIGATORIO)**: Tests de `parse_keyword_response()` con casos edge, validación de inputs del tool
- **Unit tests Enhanced**: Mocking completo de `AsyncOpenAI` (opcional)
- **Integration tests**: Test pequeño con API real (opcional)
- **Manual testing**: MCP Inspector + Claude Code invocation (obligatorio)

### Casos de Prueba Principales

**🔴 CORE - Sistema de Prompts (tests obligatorios)**:
- [x] **UNIT TEST OBLIGATORIO**: `parse_keyword_response()` parsea JSON directo
- [x] **UNIT TEST OBLIGATORIO**: `parse_keyword_response()` extrae de markdown code block
- [x] **UNIT TEST OBLIGATORIO**: `parse_keyword_response()` fallback a quoted strings
- [x] **UNIT TEST OBLIGATORIO**: `parse_keyword_response()` maneja respuesta vacía

**🔴 CORE - MCP Tool Validation (tests obligatorios)**:
- [x] **UNIT TEST OBLIGATORIO**: Validación rechaza num_variations < 1 o > 5
- [x] **UNIT TEST OBLIGATORIO**: Validación rechaza num_variations no-int
- [x] **UNIT TEST OBLIGATORIO**: Validación rechaza query vacío
- [x] **UNIT TEST OBLIGATORIO**: Validación rechaza query None

**🔴 CORE - Manual Testing (obligatorio)**:
- [ ] Tool registrado en MCP server
- [ ] Tool invocable desde MCP Inspector
- [ ] Return dict tiene formato correcto: `{"keywords": [...]}`
- [ ] Error messages son claros y user-friendly

**🟡 Enhanced - OpenAIClient (opcional)**:
- [ ] Inicialización con API key
- [ ] `generate_keywords()` llama OpenAI con parámetros correctos
- [ ] Retry logic funciona (3 intentos en fallos transitorios)
- [ ] Logging de tokens usados
- [ ] Error handling de APIError, RateLimitError, AuthenticationError

**End-to-end**:
- [ ] Usuario pide keywords desde Claude Code
- [ ] Keywords generadas son académicas y relevantes
- [ ] Keywords son 3-8 palabras cada una
- [ ] Número de keywords match num_variations solicitadas

### Criterios de Calidad de Keywords (Medibles)

**Métricas Cuantitativas Definidas**:

1. **Longitud por keyword**:
   - Mínimo: 3 palabras
   - Máximo: 8 palabras
   - Validación: Contar tokens separados por espacios

2. **Número exacto de keywords**:
   - Debe ser exactamente `num_variations` solicitadas (1-5)
   - Validación: `len(keywords) == num_variations`

3. **Unicidad**:
   - No duplicados en la lista retornada
   - Validación: `len(keywords) == len(set(keywords))`

4. **No vacías**:
   - Cada keyword debe ser string no vacío
   - Validación: `all(k.strip() for k in keywords)`

5. **Formato válido**:
   - Solo caracteres alfanuméricos, espacios, y guiones básicos
   - Sin caracteres especiales excesivos (ej: emojis, símbolos raros)
   - Validación: Regex básico `^[a-zA-Z0-9\s\-]+$`

**Enlace con Tests Unitarios**:

```python
# tests/test_keyword_quality.py (Enhanced - opcional)
def test_keyword_quality_metrics():
    """Test cuantitativo de calidad de keywords."""
    keywords = parse_keyword_response(sample_response)

    # Longitud (3-8 palabras)
    for kw in keywords:
        word_count = len(kw.split())
        assert 3 <= word_count <= 8, f"Keyword '{kw}' tiene {word_count} palabras"

    # Unicidad
    assert len(keywords) == len(set(keywords)), "Keywords duplicadas detectadas"

    # No vacías
    assert all(k.strip() for k in keywords), "Keywords vacías detectadas"

    # Formato válido
    import re
    for kw in keywords:
        assert re.match(r'^[a-zA-Z0-9\s\-]+$', kw), f"Keyword '{kw}' tiene formato inválido"
```

**Validación Manual vs Automatizada**:
- **Automatizada (Unit Tests)**: Métricas cuantitativas (longitud, número, unicidad, formato)
- **Manual (Smoke Test)**: Relevancia académica, calidad semántica, pertinencia al query

**Criterios de Aceptación MVP Actualizados**:
- ✅ Todas las métricas cuantitativas pasan tests unitarios
- ✅ Validación manual confirma relevancia académica (smoke test)
- ✅ Latencia < 5s para llamada típica (gpt-4o-mini es rápido)
- ✅ Costo típico: ~$0.00006 por generación (input ~200 tokens, output ~50 tokens)

---

## 6. Smoke Test Checklist

```markdown
**SMOKE TEST CHECKLIST - Task-04 (Fase 3 LLM Keyword Generation)**

**Ejecutado por**: [Nombre]
**Fecha**: [YYYY-MM-DD]
**Ambiente**: Local Development
**MCP Server**: sortgs-mcp
**OpenAI API**: gpt-4o-mini

---

### 1. Pre-requisitos

- [ ] **1.1** `.env` tiene `OPENAI_API_KEY` válida
- [ ] **1.2** `uv sync` ejecutado sin errores
- [ ] **1.3** MCP server arranca: `uv run python -m sortgs_mcp.server`
- [ ] **1.4** Log muestra: "Starting Sort Google Scholar MCP Server"
- [ ] **1.5** NO hay warning de "OPENAI_API_KEY not set"

---

### 2. Código Implementado

- [ ] **2.1** `src/sortgs_mcp/llm/openai.py` existe
- [ ] **2.2** `src/sortgs_mcp/llm/keywords.py` existe
- [ ] **2.3** `src/sortgs_mcp/tools/search.py` modificado (tool agregado)
- [ ] **2.4** `OpenAIClient` class definida
- [ ] **2.5** Método `generate_keywords()` implementado
- [ ] **2.6** Template `KEYWORD_GENERATION_PROMPT` definido
- [ ] **2.7** Funciones `build_keyword_prompt()` y `parse_keyword_response()` implementadas

---

### 3. Tool Registration

- [ ] **3.1** MCP Inspector conecta sin errores
- [ ] **3.2** Tool `generate_search_keywords` aparece en lista
- [ ] **3.3** Tool schema muestra inputs correctos (query: str, num_variations: int)
- [ ] **3.4** Tool schema muestra output correcto (keywords: list[str])

---

### 4. Funcionalidad Básica

**Test Case 1**: Query simple, 3 variaciones

- [ ] **4.1** Ejecutar desde MCP Inspector:
  ```json
  {
    "query": "papers about transformers in NLP",
    "num_variations": 3
  }
  ```
- [ ] **4.2** Respuesta recibida en < 5 segundos
- [ ] **4.3** JSON válido retornado
- [ ] **4.4** Campo "keywords" presente
- [ ] **4.5** Exactamente 3 keywords retornadas
- [ ] **4.6** Keywords son strings no vacíos
- [ ] **4.7** Keywords son académicas y relevantes
- [ ] **4.8** Keywords tienen 3-8 palabras aprox
- [ ] **4.9** **MÉTRICA**: Verificar longitud 3-8 palabras por keyword
- [ ] **4.10** **MÉTRICA**: Verificar unicidad (no duplicados)
- [ ] **4.11** **MÉTRICA**: Verificar formato válido (sin caracteres raros)

**Test Case 2**: Validación de inputs

- [ ] **4.12** num_variations = 0 → Error de validación (ValueError)
- [ ] **4.13** num_variations = 10 → Error de validación (ValueError)
- [ ] **4.14** query = "" → Error de validación (ValueError)
- [ ] **4.15** Error messages son claros y específicos (tipo de error visible)

---

### 5. Claude Code Integration

- [ ] **5.1** Desde Claude Code, invocar:
  ```
  Generate keywords for researching "quantum computing applications in cryptography"
  ```
- [ ] **5.2** Tool se invoca correctamente
- [ ] **5.3** Keywords generadas visibles en chat
- [ ] **5.4** Usuario puede copiar keywords para usar con `search_papers`

---

### 6. Logging

- [ ] **6.1** Log file `data/logs/sortgs_mcp.log` contiene:
  - Llamada a OpenAI API
  - Tokens usados (input/output)
  - Keywords generadas
- [ ] **6.2** Formato de log es legible
- [ ] **6.3** Nivel de log apropiado (INFO para success, ERROR para fails)

**Sample log snippet**:
```
[Copiar 5-10 líneas del log aquí]
```

---

### 7. Error Scenarios

**Test Case 3**: API key inválida

- [ ] **7.1** Modificar `.env` con API key falsa
- [ ] **7.2** Reiniciar MCP server
- [ ] **7.3** Invocar tool
- [ ] **7.4** Error claro retornado (AuthenticationError propagado, no crash)
- [ ] **7.5** Log muestra error de autenticación con stacktrace

**Test Case 4**: Respuesta OpenAI malformada (manual simulation)

- [ ] **7.6** (Si es posible) Simular respuesta no-JSON
- [ ] **7.7** Parsing fallback funciona (extrae keywords de todos modos)

---

### 8. Code Quality

- [ ] **8.1** No hay `print()` olvidados
- [ ] **8.2** Imports organizados
- [ ] **8.3** Docstrings en funciones públicas
- [ ] **8.4** Type hints correctos
- [ ] **8.5** Convenciones: snake_case, nombres descriptivos
- [ ] **8.6** No hay TODOs/FIXMEs sin resolver

---

### 9. Tests Unitarios CORE (OBLIGATORIO - NUNCA OMITIR)

- [ ] **9.1** `pytest tests/test_llm_keywords.py` pasa (parsing tests)
- [ ] **9.2** `pytest tests/test_tool_validation.py` pasa (input validation tests)
- [ ] **9.3** Tests de parsing edge cases pasan (JSON, markdown, quoted, vacío)
- [ ] **9.4** Tests de validación pasan (num_variations, query)
- [ ] **9.5** **MÉTRICAS**: Tests de calidad cuantitativa pasan (longitud, unicidad, formato)

**IMPORTANTE**: Si estos tests no pasan, NO proceder con commit/PR.

---

**RESULTADO TÉCNICO FINAL**

- [ ] ✅ **FUNCIONALIDAD COMPLETA** - Tool funciona, tests CORE pasan, métricas OK
- [ ] ⚠️ **ISSUES MENORES** - Documentar para resolver antes de commit
- [ ] ❌ **ISSUES BLOQUEANTES** - NO proceder con commit/PR

**Notas de implementación**:
[Agregar observaciones técnicas]

---

### POST-IMPLEMENTACIÓN (Ejecutar después del smoke test técnico)

#### 10. Documentation (Pre-commit)

- [ ] **10.1** Docstrings en `OpenAIClient` completos
- [ ] **10.2** Docstrings en tool `generate_search_keywords` completos
- [ ] **10.3** MCP_PLAN.md actualizado (marcar Fase 3 como implementada)
- [ ] **10.4** README actualizado (si aplica)

#### 11. Git y PR (Pre-merge)

- [ ] **11.1** Branch `feature/fase-3` creado desde `dev`
- [ ] **11.2** Commits descriptivos y atómicos
- [ ] **11.3** PR creado con título: "Implementa Fase 3: LLM Keyword Generation"
- [ ] **11.4** PR description clara con ejemplos de uso
- [ ] **11.5** Screenshots de funcionalidad adjuntos al PR
- [ ] **11.6** Este smoke test checklist incluido en PR

**Notas para PR**:
[Agregar contexto para reviewers]

---
```

---

## 7. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| OpenAI API rate limit durante testing | Media | Medio | Usar mocks para unit tests, limitar integration tests |
| API key no configurada por usuario | Alta | Bajo | Warning claro al arrancar server, tool gracefully unavailable |
| Respuesta OpenAI en formato inesperado | Media | Medio | Múltiples fallbacks de parsing (JSON → markdown → quoted) |
| Costo acumulado de testing | Baja | Bajo | Costo típico $0.00006/test, total < $0.01 |
| Latencia alta de OpenAI | Baja | Bajo | gpt-4o-mini es muy rápido (<2s típico), timeout 30s |

---

## 8. Plan de Contingencia

**Punto de Decisión GO/NO-GO**:
- **Cuándo**: Después de T8 (antes de testing manual)
- **Verificar**: Tool invocable desde MCP Inspector, retorna keywords
- **Si no se cumple**: Revisar logs de OpenAI API, verificar API key válida

**Escenarios de bloqueo comunes**:

1. **OpenAI API authentication error**:
   - → Verificar API key en `.env`
   - → Verificar balance de cuenta OpenAI
   - → Verificar que key tiene permisos para chat.completions

2. **Parsing de respuesta siempre falla**:
   - → Revisar prompt (quizás OpenAI no entiende instrucciones)
   - → Agregar log de respuesta raw para debugging
   - → Ajustar template de prompt

3. **Tool no aparece en MCP Inspector**:
   - → Verificar import en `server.py`: `from sortgs_mcp.tools import search`
   - → Verificar decorador `@mcp.tool()` presente
   - → Reiniciar MCP server

4. **Retry logic no funciona**:
   - → Verificar configuración de tenacity (@retry decorator)
   - → Verificar que excepción es manejable (no todas se retry-an)

5. **Claude Code no puede invocar tool**:
   - → Verificar MCP server registrado: `claude mcp list`
   - → Verificar logs de MCP server (stderr)
   - → Re-registrar server si necesario

---

## 9. Dependencias y Configuración

### Dependencias Requeridas

**Python Packages** (ya presentes en `pyproject.toml`):
- `openai>=1.0.0` - SDK oficial de OpenAI (AsyncOpenAI client)
- `tenacity>=9.1.2` - Retry logic con exponential backoff (✅ CONFIRMADO en pyproject.toml)
- `pydantic>=2.0.0` - Validación de datos
- `pydantic-settings>=2.0.0` - Settings management

**System Requirements**:
- Python >=3.8
- Variable de entorno: `OPENAI_API_KEY` (opcional - tool no disponible si ausente)

### Configuración en `config.py`

Variables de entorno utilizadas:
```python
class Settings(BaseSettings):
    openai_api_key: str | None = None  # Optional - warning si None
    openai_model_keywords: str = "gpt-4o-mini"  # Default model
    # ... otras configs existentes
```

**Valores por defecto**:
- Model: `gpt-4o-mini` (económico: $0.15/$0.60 por 1M tokens input/output)
- Timeout: 30s (httpx default en AsyncOpenAI)
- Retry: 3 intentos con exponential backoff

---

## 10. Decisiones Técnicas TOMADAS

### 10.1 Cliente OpenAI: Sin Context Manager

**Decisión TOMADA**: `OpenAIClient` NO usa async context manager (no `__aenter__`/`__aexit__`)

**Justificación**:
- ✅ `AsyncOpenAI` client no requiere explicit cleanup (httpx client interno se maneja solo)
- ✅ Stateless: No mantiene conexiones persistentes
- ✅ Más simple: Instanciación directa sin complejidad de context manager
- ✅ Pattern común para clientes API (requests, anthropic, etc.)

**Alternativas consideradas**:
- **Opción B (Context Manager)**: Pro: Más "correcto" async, Contra: Overhead innecesario para client stateless
- **Opción C (Singleton global)**: Pro: Reutiliza instancia, Contra: Complejidad de lifecycle management

**Trade-off aceptado**: Crear nueva instancia por llamada (overhead mínimo)

**Principio KISS aplicado**: Menos código = más simple de mantener

---

### 10.2 Ubicación del Tool: tools/search.py

**Decisión TOMADA**: Agregar `generate_search_keywords` en `tools/search.py` existente

**Justificación**:
- ✅ Lógicamente relacionado: keywords → search papers (workflow natural)
- ✅ Evita crear archivo nuevo para un solo tool
- ✅ Consistente con estructura actual (solo existe `tools/search.py`)
- ✅ Imports simplificados en `server.py`

**Alternativas consideradas**:
- **Opción B (tools/keywords.py nuevo)**: Pro: Separación de concerns, Contra: Overhead para un solo tool
- **Opción C (tools/llm.py nuevo)**: Pro: Agrupa tools LLM, Contra: Solo hay un tool LLM en Fase 3

**Trade-off aceptado**: Archivo más largo (~150 líneas total), pero más cohesivo

**Plan de migración futura**: Si agregamos 3+ tools LLM, refactorizar a `tools/llm.py`

---

### 10.3 Retry Logic: Tenacity con 3 Intentos

**Decisión TOMADA**: Usar `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))`

**Justificación**:
- ✅ Maneja transient errors (network glitches, temporary rate limits)
- ✅ Exponential backoff: 1s → 4s → 10s (no spam a API)
- ✅ 3 intentos es balance entre resilience y latencia
- ✅ Tenacity es standard en el proyecto (ya usado en otras partes)

**Alternativas consideradas**:
- **Opción B (5 intentos)**: Pro: Más resiliente, Contra: Latencia muy alta en fail (~30s)
- **Opción C (Sin retry)**: Pro: Simple, Contra: Frágil ante errors transitorios

**Trade-off aceptado**: Latencia máxima ~15s en worst case (3 intentos)

**Principio KISS aplicado**: Usar config standard (no fine-tuning de backoff)

---

### 10.4 Error Handling: Granular sin RuntimeError Wrapper

**Decisión TOMADA**: Propagar excepciones específicas del SDK OpenAI sin envolver en `RuntimeError` genérico

**Clases de excepciones utilizadas** (openai-python v1.x):
```python
from openai import (
    APIError,           # Base exception para errores de API
    RateLimitError,     # Subclase de APIError - rate limits alcanzados
    AuthenticationError, # API key inválida o sin permisos
    APIConnectionError  # Errores de red/conexión
)
```

**Justificación**:
- ✅ Imports explícitos previenen errores de AttributeError
- ✅ Permite retry selectivo (AuthenticationError no se retry-a)
- ✅ Mensajes de error específicos por tipo (mejora UX y debugging)
- ✅ MCP framework maneja excepciones correctamente (formatea en error response)
- ✅ Cliente recibe tipo exacto de error (no `RuntimeError` genérico)

**Strategy aplicada**:
- `APIError` y subclases retriables (`RateLimitError`, `APIConnectionError`) → 3 intentos con tenacity
- `AuthenticationError` → No retry, propagar directo con hint de verificar API key
- `ValueError` (validation) → No retry, propagar directo
- Otros exceptions → Log y propagar (fail fast)

**Alternativas consideradas**:
- **Opción B (Envolver todo en RuntimeError)**: Pro: Unifica errores, Contra: Pierde información de tipo, debugging difícil
- **Opción C (Catch genérico Exception)**: Pro: Simple, Contra: Oculta bugs, retry innecesario

**Trade-off aceptado**: Más líneas de imports pero mejor error handling y debugging

**Principio KISS aplicado**: Usar SDK oficial sin wrappers custom que ocultan información

**Beneficio para MCP**: Cliente recibe errores estructurados con tipos específicos, puede tomar decisiones (ej: pedir nueva API key si `AuthenticationError`)

---

### 10.5 Parsing de Respuesta: Fallbacks en Cascada

**Decisión TOMADA**: Intentar parsing en orden: JSON directo → markdown extraction → quoted strings

**Justificación**:
- ✅ Robusto: Maneja variaciones de formato de OpenAI
- ✅ Graceful degradation: Siempre retorna algo útil
- ✅ Simple: 3 fallbacks claros (no complicado)
- ✅ Testeable: Cada fallback es función independiente

**Alternativas consideradas**:
- **Opción B (Solo JSON)**: Pro: Simple, Contra: Frágil si OpenAI devuelve markdown
- **Opción C (Regex complejo)**: Pro: Más flexible, Contra: Difícil de mantener

**Trade-off aceptado**: Puede extraer keywords de respuestas subóptimas (tolerancia)

**Principio KISS aplicado**: Try simple approaches first, fallback solo si necesario

---

### 10.6 Template de Prompt: Single Static Template

**Decisión TOMADA**: Un solo template hardcoded en `keywords.py`

**Justificación**:
- ✅ Suficiente para MVP: Un template bien diseñado funciona para todos los casos
- ✅ Simple: No necesita sistema de templates complejo
- ✅ Testeable: Prompt es constante, fácil de validar
- ✅ Configurable después: Fácil agregar sistema de templates si se necesita

**Alternativas consideradas**:
- **Opción B (Sistema de templates)**: Pro: Flexible, Contra: Over-engineering para Fase 3
- **Opción C (Template en config.py)**: Pro: User-configurable, Contra: Complejidad innecesaria

**Trade-off aceptado**: Un solo estilo de keywords (académico Google Scholar)

**Plan de migración futura**: Si usuarios piden estilos distintos, agregar templates configurables

---

### 10.7 Timeout Configuration: Explicit and Configurable

**Decisión TOMADA**: AsyncOpenAI client con timeout explícito de 30s (configurable)

**Justificación**:
- ✅ **Transparente**: Timeout documentado explícitamente en constructor (no implicit)
- ✅ **Suficiente para gpt-4o-mini**: Respuestas típicas <2s, 30s es amplio margen
- ✅ **Configurable**: Parámetro `timeout` en `__init__` permite ajustar si necesario
- ✅ **httpx default**: AsyncOpenAI usa httpx internamente con timeout configurable

**Implementación**:
```python
def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: float = 30.0):
    self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
```

**Alternativas consideradas**:
- **Opción B (Sin timeout explícito)**: Pro: Menos código, Contra: Timeout indefinido si httpx cambia defaults
- **Opción C (Timeout muy corto 5s)**: Pro: Falla rápido, Contra: False positives en red lenta

**Trade-off aceptado**: Timeout generoso (30s) previene timeouts en conexiones lentas

**Principio KISS aplicado**: Usar default razonable, permitir override vía constructor

**Valores recomendados**:
- Default: 30s (suficiente para gpt-4o-mini)
- Si se usa modelo más grande (gpt-4): considerar aumentar a 60s
- Si red es muy confiable y rápida: puede reducirse a 10s

---

## 11. Implementación Detallada

### Archivo 1: `src/sortgs_mcp/llm/openai.py`

**Contenido clave**:
```python
from openai import AsyncOpenAI, APIError, RateLimitError, AuthenticationError, APIConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

class OpenAIClient:
    """Async client for OpenAI API with retry logic.

    Uses AsyncOpenAI with default httpx timeout of 30s.
    Timeout can be customized via timeout parameter if needed.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", timeout: float = 30.0):
        # AsyncOpenAI uses httpx internally with configurable timeout
        # Default 30s is sufficient for gpt-4o-mini (typically <2s response)
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_keywords(self, query: str, num_variations: int = 3) -> list[str]:
        """Generate keyword variations for Google Scholar search.

        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded (after retries)
            APIConnectionError: Connection failed (after retries)
            APIError: Other API errors (after retries)
        """
        from sortgs_mcp.llm.keywords import build_keyword_prompt, parse_keyword_response

        prompt = build_keyword_prompt(query, num_variations)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )
        except AuthenticationError as exc:
            self.logger.error(f"OpenAI authentication failed: {exc}", exc_info=True)
            raise  # Propagar directo - no retry
        except (RateLimitError, APIConnectionError, APIError) as exc:
            self.logger.error(f"OpenAI API error: {exc}", exc_info=True)
            raise  # Retry via tenacity, luego propagar

        content = response.choices[0].message.content
        keywords = parse_keyword_response(content)

        # Log token usage
        self.logger.info(
            f"OpenAI keyword generation: {response.usage.prompt_tokens} input tokens, "
            f"{response.usage.completion_tokens} output tokens"
        )

        return keywords

    async def generate_answer(self, question: str, context: str) -> str:
        """Generate answer from context using RAG. (Stub for Phase 7)"""
        raise NotImplementedError("RAG answer generation will be implemented in Phase 7")
```

**Líneas**: ~60

---

### Archivo 2: `src/sortgs_mcp/llm/keywords.py`

**Contenido clave**:
```python
import json
import re

KEYWORD_GENERATION_PROMPT = """You are an expert research assistant specializing in academic literature search.

Given a user's research query, generate {num_variations} optimized keyword variations for Google Scholar search.

User query: "{query}"

Requirements:
- Each variation should approach the topic from a different angle
- Use academic terminology and synonyms
- Include both broad and specific terms
- Optimize for Google Scholar's search algorithm
- Each variation should be 3-8 words

Return ONLY a JSON list of keyword strings, nothing else.

Example output format:
["keyword variation 1", "keyword variation 2", "keyword variation 3"]
"""

def build_keyword_prompt(query: str, num_variations: int) -> str:
    """Build prompt for keyword generation."""
    return KEYWORD_GENERATION_PROMPT.format(
        query=query,
        num_variations=num_variations
    )

def parse_keyword_response(response: str) -> list[str]:
    """Parse OpenAI response to extract keywords list.

    Raises:
        ValueError: If no keywords could be extracted from response
    """
    # Try 1: Direct JSON parse
    try:
        keywords = json.loads(response)
        if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
            return keywords
    except json.JSONDecodeError:
        pass

    # Try 2: Extract JSON from markdown code block
    match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response, re.DOTALL)
    if match:
        try:
            keywords = json.loads(match.group(1))
            if isinstance(keywords, list):
                return keywords
        except json.JSONDecodeError:
            pass

    # Try 3: Fallback - extract quoted strings
    keywords = re.findall(r'"([^"]+)"', response)
    if keywords:
        return keywords

    # Last resort: return cleaned response as single keyword
    cleaned = response.strip()
    if cleaned:
        return [cleaned]

    # No keywords extracted - error
    raise ValueError(f"Could not extract keywords from response: {response[:100]}")
```

**Líneas**: ~70

---

### Archivo 3: `src/sortgs_mcp/tools/search.py` (modificación)

**Agregar al final del archivo**:
```python
@mcp.tool()
async def generate_search_keywords(
    query: str,
    num_variations: int = 3
) -> dict:
    """Generate optimized Google Scholar search keywords using OpenAI LLM.

    Args:
        query: User's research question or topic
        num_variations: Number of keyword variations to generate (1-5)

    Returns:
        Dictionary with "keywords" list

    Raises:
        ValueError: Invalid input parameters
        AuthenticationError: Invalid OpenAI API key
        RateLimitError: OpenAI rate limit exceeded
        APIError: Other OpenAI API errors

    Example:
        >>> generate_search_keywords("papers about transformers in NLP", 3)
        {
            "keywords": [
                "transformer architecture BERT GPT language models",
                "attention mechanism neural machine translation",
                "pre-trained models transfer learning NLP"
            ]
        }
    """
    from sortgs_mcp.config import settings
    from sortgs_mcp.llm.openai import OpenAIClient
    from openai import AuthenticationError, RateLimitError, APIError

    # Validation - propagar ValueError directo
    if not query.strip():
        raise ValueError("query must not be empty")

    if not isinstance(num_variations, int) or not (1 <= num_variations <= 5):
        raise ValueError("num_variations must be an integer between 1 and 5")

    # Check API key availability
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not configured. "
            "Please set it in .env file to use keyword generation."
        )

    logger.info(
        "generate_search_keywords called",
        extra={"query": query[:100], "num_variations": num_variations}
    )

    # Create client and generate keywords
    # Excepciones se propagan directamente (MCP las maneja)
    client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model_keywords
    )

    keywords = await client.generate_keywords(query, num_variations)

    logger.info(f"Generated {len(keywords)} keywords successfully")

    return {"keywords": keywords}
```

**Líneas agregadas**: ~60

---

## 12. Próximos Pasos Post-Implementación

1. ✅ Merge de PR a `dev`
2. ✅ Tag release: `v1.3.0-fase3`
3. ✅ Actualizar MCP_PLAN.md: Marcar Fase 3 como completada
4. ✅ Documentar en README ejemplo de uso del tool
5. 🚧 Preparar para Fase 4: PDF Download (siguiente fase del plan)

---

**FIN DEL WORKPLAN - rev-2**
