---
Task-00: Fase 1 - Core Refactoring
---

## Objetivo (KISS)

**Implementa core de scraping async y gestión de sesiones para sortgs_mcp**

## Descripción

Crear los componentes fundamentales para transformar sortgs CLI en MCP Server:

1. **ScholarSearcher** (`src/sortgs_mcp/core/scholar.py`)
   - Búsqueda async de papers en Google Scholar con httpx
   - Fallback a Selenium cuando hay CAPTCHA
   - Parsing con BeautifulSoup (reutiliza parser.py existente)

2. **SessionManager** (`src/sortgs_mcp/core/session.py`)
   - Crear/guardar/cargar sesiones
   - Persistencia en JSON + CSV
   - Gestión de directorios de sesión

3. **Integración** (`src/sortgs_mcp/core/__init__.py`)
   - Exportar ScholarSearcher y SessionManager
   - Exportar funciones de parser

## Criterio de Éxito

```python
from sortgs_mcp.core import ScholarSearcher, SessionManager
from sortgs_mcp.models import SearchParams
from sortgs_mcp.config import settings

# Si estos imports funcionan → task completado ✅
```

## Referencia

- **Workplan completo**: `.claude/workplans/workplan-task-00.md`
- **Código original**: `src/sortgs/sortgs.py` (líneas 1-400)
- **Modelos**: `src/sortgs_mcp/models.py` (ya completo)
- **Parser**: `src/sortgs_mcp/core/parser.py` (ya completo)

## Estado

- [ ] ScholarSearcher implementado
- [ ] SessionManager implementado
- [ ] __init__.py actualizado
- [ ] Verificación manual exitosa
