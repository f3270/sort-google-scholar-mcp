---
Task-04: fase 3 LLM Keyword Generation
---

Vamos a desarrollar la Fase 3 del ../../MCP_PLAN.md

1. Crear Cliente OpenAI (src/sortgs_mcp/llm/openai.py)

Clase OpenAIClient:
- Constructor que recibe API key y modelo (default: gpt-4o-mini)
- Método generate_keywords(query, num_variations) para generar keywords
- Usa el cliente AsyncOpenAI
- Implementa retry logic con tenacity (3 intentos, exponential backoff)
- Logging de tokens usados
- Método generate_answer(question, context) (se usa en Fase 7)

Tecnología:
- openai SDK oficial de OpenAI
- Cliente asíncrono: AsyncOpenAI
- Retry: tenacity library

---
2. Crear Sistema de Prompts (src/sortgs_mcp/llm/keywords.py)

Funciones:

1. build_keyword_prompt(query, num_variations)
- Construye el prompt usando template
- Template pide al LLM generar variaciones de keywords optimizadas para Google Scholar
- Cada variación debe tener 3-8 palabras
- Debe usar terminología académica
2. parse_keyword_response(response)
- Parsea la respuesta del LLM para extraer lista de keywords
- Maneja múltiples formatos:
    - JSON directo: ["keyword1", "keyword2"]
  - JSON en markdown code block: ```json [...] ```
  - Fallback: extrae strings entre comillas

Ejemplo de prompt:
You are an expert research assistant specializing in academic literature search.

Given a user's research query, generate {num_variations} optimized keyword variations
for Google Scholar search.

User query: "papers about transformers in NLP"

Requirements:
- Each variation should approach the topic from a different angle
- Use academic terminology and synonyms
- Include both broad and specific terms
- Optimize for Google Scholar's search algorithm
- Each variation should be 3-8 words

Return ONLY a JSON list of keyword strings, nothing else.

---
3. Crear MCP Tool (src/sortgs_mcp/tools/search.py)

Tool: generate_search_keywords

Input:
- query (str): Pregunta de investigación del usuario
- num_variations (int): Número de variaciones (1-5, default: 3)

Output:
{
"keywords": [
  "transformers neural networks natural language processing",
  "attention mechanism BERT GPT language models",
  "sequence-to-sequence models deep learning NLP"
]
}

Implementación:
1. Validar inputs (num_variations entre 1-5)
2. Crear instancia de OpenAIClient con settings
3. Llamar client.generate_keywords(query, num_variations)
4. Return resultado como dict

---
4. Testing

Unit tests:
- Test OpenAIClient con mock de API OpenAI
- Test prompt building
- Test parsing de respuestas (casos edge: markdown, JSON malformado)
- Test retry logic

Integration tests:
- Test pequeño con API real (opcional, consume tokens)
- Test con MCP Inspector
- Test desde Claude Code

---
Entregables de la Fase 3

✅ OpenAIClient con retry logic
✅ Sistema de prompts para keywords
✅ Tool generate_search_keywords funcional
✅ Tests unitarios y de integración

---
Dependencias

Requiere:
- Fase 0: Setup completado (dependencias instaladas, config.py con openai_api_key)
- Fase 1: Core Refactoring (modelos pydantic)
- Fase 2: MCP Server Skeleton (servidor funcionando)

No requiere:
- Fase 4-7 pueden desarrollarse en paralelo o después

---
Ejemplo de Uso

Una vez implementada, desde Claude Code:

User: "Generate keywords for researching transformers in NLP"

Tool call: generate_search_keywords
- query: "transformers in natural language processing"
- num_variations: 3

Result:
{
"keywords": [
  "transformer architecture BERT GPT language models",
  "attention mechanism neural machine translation",
  "pre-trained models transfer learning NLP"
]
}

Luego el usuario puede usar esos keywords con el tool search_papers.

---
Notas Importantes

- Esta fase es opcional para MVP - el usuario puede proporcionar keywords manualmente
- Usa gpt-4o-mini por defecto (más económico: $0.15/$0.60 por 1M tokens)
- El costo típico por generación: ~$0.00006 (muy barato)
- Si no hay OPENAI_API_KEY configurada, este tool simplemente no estará disponible

