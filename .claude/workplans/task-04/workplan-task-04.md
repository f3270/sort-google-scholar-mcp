# Plan de Trabajo: Task-04 - Fase 3 LLM Keyword Generation

**Fecha de Creación**: 2025-12-29
**Versión**: 1.0
**Estado**: Pendiente de Aprobación
**Autor**: Claude Code
**Stack**: OpenAI API (AsyncOpenAI) + tenacity + MCP (stdio) + pydantic

---

## Historial de Revisiones

| Versión | Fecha | Cambios | Motivo |
|---------|-------|---------|--------|
| 1.0 | 2025-12-29 | Plan inicial | Creación del workplan para Fase 3 - LLM Keyword Generation |

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

### Alcance y Objetivos

**Objetivo Principal**: Habilitar generación automática de keywords usando LLM (gpt-4o-mini) accesible via MCP tool.

**Componentes del sistema MCP afectados**:
- ✅ LLM Integration: `src/sortgs_mcp/llm/openai.py` (NUEVO)
- ✅ Prompt System: `src/sortgs_mcp/llm/keywords.py` (NUEVO)
- ✅ MCP Tool: `src/sortgs_mcp/tools/search.py` (MODIFICAR - agregar tool)
- ✅ Tests: `tests/test_llm_keywords.py` (NUEVO)
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
- [x] Error handling robusto con mensajes claros
- [x] Logging de tokens usados

**Componentes MVP**:
- `src/sortgs_mcp/llm/openai.py`
- `src/sortgs_mcp/llm/keywords.py`
- `src/sortgs_mcp/tools/search.py` (modificación)

### 🟡 Enhanced (Si hay tiempo)

Funcionalidades que agregan valor pero no bloquean:
- [ ] Tests unitarios exhaustivos con mocking de OpenAI
- [ ] Tests de casos edge (JSON malformado, markdown code blocks)
- [ ] Test de integración con API real (pequeño - consume tokens)
- [ ] Método `generate_answer()` stub para Fase 7 (solo signature, no implementación)
- [ ] Validación de calidad de keywords generadas
- [ ] Métricas de costo (tokens usados, costo estimado)

**Componentes Enhanced**:
- `tests/test_llm_keywords.py`
- `tests/test_llm_openai_client.py`

### 🟢 Nice-to-Have (Futuras iteraciones)

Para versiones posteriores:
- [ ] Cache de keywords generadas (evitar llamadas duplicadas)
- [ ] Sistema de templates de prompts configurable
- [ ] Multiple LLM providers (fallback a Anthropic si OpenAI falla)
- [ ] Evaluación automática de calidad de keywords

**Justificación postponer**: Son mejoras de optimización que pueden agregarse después del MVP funcional.

### Plan de Reducción de Alcance

**Si se excede el tiempo estimado:**

1. **Recorte Nivel 1**: Eliminar Enhanced completo → Ahorro: 1-1.5h
2. **Recorte Nivel 2**: Solo tests manuales con MCP Inspector, sin unit tests → Ahorro: 1h adicional
3. **Core absoluto inamovible**:
   - `OpenAIClient.generate_keywords()` funcional
   - Tool `generate_search_keywords` invocable
   - Parsing básico de respuestas (JSON directo)

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

**LLM Integration**:
- [x] **Cliente**: `AsyncOpenAI` (async nativo)
- [x] **Modelo**: `gpt-4o-mini` (config: `settings.openai_model_keywords`)
- [x] **API Key**: `settings.openai_api_key` (opcional - tool no disponible si None)
- [x] **Retry**: 3 intentos, exponential backoff (1s, 4s, 10s)
- [x] **Timeout**: 30s per request (default httpx)
- [x] **Cost tracking**: Log tokens usados (input/output)

**Error Handling Strategy**:
- `openai.APIError` → Retry 3x → RuntimeError con mensaje claro
- `openai.RateLimitError` → Retry con backoff → RuntimeError "Rate limit exceeded"
- `ValueError` (validation) → No retry → ValueError directo
- `JSONDecodeError` → Intentar fallbacks de parsing → RuntimeError si todos fallan

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
| T8 | 🔴 CORE | Error handling y logging | Try/except bloques, logger.info/error | T6 | 15min |
| T9 | 🔴 CORE | Testing manual con MCP Inspector | Tool invocable, retorna keywords válidas | T6, T7, T8 | 20min |
| T10 | 🟡 Enhanced | Unit tests - OpenAIClient mock | Test con mock de AsyncOpenAI, verifica llamadas correctas | T2 | 30min |
| T11 | 🟡 Enhanced | Unit tests - parsing edge cases | Tests para JSON, markdown, malformado | T5 | 20min |
| T12 | 🟡 Enhanced | Integration test con API real | Test pequeño (consume ~$0.00006) | T6 | 15min |

**Orden de implementación sugerido**:
T1 → T3 → T4 → T5 → T2 → T6 → T7 → T8 → T9 → [T10 → T11 → T12 si hay tiempo]

**Total tiempo core**: ~3.5h
**Total tiempo con enhanced**: ~5h

---

## 5. Plan de Pruebas

### Estrategia de Testing

- **Unit tests**: Mocking de `AsyncOpenAI`, tests de funciones de parsing
- **Integration tests**: Test pequeño con API real (opcional)
- **Manual testing**: MCP Inspector + Claude Code invocation

### Casos de Prueba Principales

**OpenAIClient**:
- [ ] Inicialización con API key
- [ ] `generate_keywords()` llama OpenAI con parámetros correctos
- [ ] Retry logic funciona (3 intentos en fallos transitorios)
- [ ] Logging de tokens usados
- [ ] Error handling de APIError, RateLimitError

**Sistema de Prompts**:
- [ ] `build_keyword_prompt()` inserta query y num_variations correctamente
- [ ] Template es claro y válido
- [ ] `parse_keyword_response()` parsea JSON directo
- [ ] `parse_keyword_response()` extrae de markdown code block
- [ ] `parse_keyword_response()` fallback a quoted strings
- [ ] `parse_keyword_response()` maneja respuesta vacía

**MCP Tool**:
- [ ] Tool registrado en MCP server
- [ ] Tool invocable desde MCP Inspector
- [ ] Validación rechaza num_variations < 1 o > 5
- [ ] Validación rechaza query vacío
- [ ] Return dict tiene formato correcto: `{"keywords": [...]}`
- [ ] Error messages son claros y user-friendly

**End-to-end**:
- [ ] Usuario pide keywords desde Claude Code
- [ ] Keywords generadas son académicas y relevantes
- [ ] Keywords son 3-8 palabras cada una
- [ ] Número de keywords match num_variations solicitadas

### Criterios de Calidad

- Keywords relevantes al query (validación manual)
- Latencia < 5s para llamada típica (gpt-4o-mini es rápido)
- Costo típico: ~$0.00006 por generación (input ~200 tokens, output ~50 tokens)

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

**Screenshot requerido**: MCP Inspector mostrando tool
![Adjuntar aquí]

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

**Screenshot requerido**: Output del test case 1
![Adjuntar aquí]

**Test Case 2**: Validación de inputs

- [ ] **4.9** num_variations = 0 → Error de validación
- [ ] **4.10** num_variations = 10 → Error de validación
- [ ] **4.11** query = "" → Error de validación
- [ ] **4.12** Error messages son claros

---

### 5. Claude Code Integration

- [ ] **5.1** Desde Claude Code, invocar:
  ```
  Generate keywords for researching "quantum computing applications in cryptography"
  ```
- [ ] **5.2** Tool se invoca correctamente
- [ ] **5.3** Keywords generadas visibles en chat
- [ ] **5.4** Usuario puede copiar keywords para usar con `search_papers`

**Screenshot requerido**: Claude Code mostrando keywords generadas
![Adjuntar aquí]

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
- [ ] **7.4** Error claro retornado (no crash)
- [ ] **7.5** Log muestra error de autenticación

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

### 9. Tests Unitarios (si implementados)

- [ ] **9.1** `pytest tests/test_llm_*.py` pasa
- [ ] **9.2** Coverage de código core > 70%
- [ ] **9.3** Tests de parsing edge cases pasan

**Screenshot requerido**: Output de pytest
![Adjuntar aquí]

---

### 10. Documentation

- [ ] **10.1** Docstrings en `OpenAIClient`
- [ ] **10.2** Docstrings en tool `generate_search_keywords`
- [ ] **10.3** MCP_PLAN.md actualizado (marcar Fase 3 como implementada)
- [ ] **10.4** README actualizado (si aplica)

---

### 11. Git y PR

- [ ] **11.1** Branch `feature/fase-3` tiene commits descriptivos
- [ ] **11.2** PR creado con título: "Implementa Fase 3: LLM Keyword Generation"
- [ ] **11.3** PR description clara con ejemplos de uso
- [ ] **11.4** Screenshots adjuntos al PR
- [ ] **11.5** Smoke test checklist incluido en PR

---

**RESULTADO FINAL**

- [ ] ✅ **TODOS LOS TESTS PASAN** - Ready para merge
- [ ] ⚠️ **HAY ISSUES MENORES** - Documentar en PR
- [ ] ❌ **HAY ISSUES BLOQUEANTES** - NO crear PR

**Notas adicionales**:
[Agregar observaciones]

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

### 10.4 Parsing de Respuesta: Fallbacks en Cascada

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

### 10.5 Template de Prompt: Single Static Template

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

## 11. Implementación Detallada

### Archivo 1: `src/sortgs_mcp/llm/openai.py`

**Contenido clave**:
```python
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

class OpenAIClient:
    """Async client for OpenAI API with retry logic."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_keywords(self, query: str, num_variations: int = 3) -> list[str]:
        """Generate keyword variations for Google Scholar search."""
        from sortgs_mcp.llm.keywords import build_keyword_prompt, parse_keyword_response

        prompt = build_keyword_prompt(query, num_variations)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
        )

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

**Líneas**: ~50

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
    """Parse OpenAI response to extract keywords list."""
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
    return [response.strip()]
```

**Líneas**: ~60

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

    # Validation
    if not query.strip():
        raise ValueError("query must not be empty")

    if not (1 <= num_variations <= 5):
        raise ValueError("num_variations must be between 1 and 5")

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

    try:
        client = OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model_keywords
        )

        keywords = await client.generate_keywords(query, num_variations)

        logger.info(f"Generated {len(keywords)} keywords successfully")

        return {"keywords": keywords}

    except Exception as exc:
        logger.error(f"Keyword generation failed: {exc}", exc_info=True)
        raise RuntimeError(f"Failed to generate keywords: {exc}") from exc
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

**FIN DEL WORKPLAN**
