"""
Analizador Técnico de Documentación y Generador de Casos de Uso.
Aplica inteligencia agéntica para sintetizar la documentación y formular 3 casos de uso minimalistas.
"""

from __future__ import annotations
import json
from typing import Dict, Any, List
from llm_client import LLMClient


class DocAnalyzer:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    def analyze(self, extracted_data: Dict[str, Any], existing_skills: List[str] = None) -> Dict[str, Any]:
        """
        Analiza la documentación extraída y genera la estructura para el archivo OKF.
        """
        url = extracted_data.get("url", "")
        doc_title = extracted_data.get("title", "")
        clean_markdown = extracted_data.get("clean_markdown", "")[:12000]  # Limitar tamaño de contexto
        code_blocks = extracted_data.get("code_blocks", [])[:8]

        system_instruction = (
            "Eres un Arquitecto de Software y Desarrollador Senior de una Fábrica de Software autónoma. "
            "Tu misión es analizar la documentación técnica y código extraído de una librería o herramienta "
            "y generar EXACTAMENTE 3 casos de uso prácticos, progresivos y con scripts minimalistas de Python.\n\n"
            "Directivas de Calidad e Innovación (Inspirado en los casos de CSS y Node.js):\n"
            "1. Cero código mediocre o placeholders (nada de '...', '// TODO', pass sin sentido). El código debe ser completamente funcional, tipado, conciso y ejecutable.\n"
            "2. TÍTULOS Y CASOS TÉCNICOS ESPECÍFICOS: NUNCA uses títulos genéricos como 'Verificar instalación', 'Instalación básica', 'Manejo de errores genérico' o 'Quickstart básico'.\n"
            "   Cada caso debe tener un título técnico preciso que refleje una tarea real de ingeniería del dominio de la documentación (ejemplos de referencia:\n"
            "   - En CSS: 'Análisis Sintáctico de Reglas CSS', 'Extracción Asíncrona de Estilos Externos', 'Inlining de CSS para Emails de Producción'.\n"
            "   - En Node.js: 'Gestión de Sistema de Archivos y Rutas (FS & Path)', 'Cliente HTTP Asíncrono con Reintentos', 'Cifrado de Datos Sensibles (Crypto & Buffer)').\n"
            "3. TRES ESCENARIOS DIVERSOS Y REALISTAS:\n"
            "   - Caso 1: Flujo funcional medular de la tecnología (ej: parsing de datos, enrutamiento, transacciones, serialización).\n"
            "   - Caso 2: Manejo de estados, procesamiento asíncrono/concurrente, validación o transformación de datos.\n"
            "   - Caso 3: Arquitectura de integración en producción, pooling, middlewares, seguridad o pipeline modular.\n"
            "4. SLUG TÉCNICO Y ESPECÍFICO: Debe reflejar la tecnología y su aplicación (ej: 'python-css-processing', 'python-nodejs-patterns', 'fastapi-auth-pipeline'). PROHIBIDO usar 'analisis-documentacion'.\n"
            "5. Responder ÚNICAMENTE con un JSON válido con el esquema especificado."
        )

        prompt = f"""Analiza la siguiente documentación técnica y genera el análisis para el Grafo de Conocimiento:

URL de Origen: {url}
Título detectado: {doc_title}

Contenido Markdown extraído:
{clean_markdown}

Bloques de código detectados en la página:
{json.dumps(code_blocks, ensure_ascii=False, indent=2)}

Habilidades existentes en la fábrica disponibles:
{json.dumps(existing_skills or [], ensure_ascii=False)}

Genera la respuesta estrictamente en este formato JSON:
{{
  "title": "Título descriptivo y profesional (ej: Automatización y Procesamiento de CSS con Python, Patrones de Backend con Node.js)",
  "slug": "slug-tecnico-descriptivo (ej: python-css-processing, nodejs-backend-patterns)",
  "semantic_summary": "Resumen conciso de 1-2 párrafos del propósito, arquitectura y valor técnico de la herramienta.",
  "tags": ["python", "nombre-libreria", "categoria-tecnica"],
  "dependencies": ["libreria>=version", "otra-dep>=version"],
  "complexity": "basic|intermediate|advanced",
  "skills_required": ["01_Skills/SKILL_001_Scraping_y_Extraccion_Web"],
  "cases": [
    {{
      "case_number": 1,
      "title": "Título técnico preciso del Caso 1 (ej: Análisis Sintáctico de Reglas CSS / Routing de Endpoints)",
      "scenario": "Descripción detallada del escenario de ingeniería que se resuelve",
      "code": "# Código Python minimalista, completo y funcional\\n..."
    }},
    {{
      "case_number": 2,
      "title": "Título técnico preciso del Caso 2 (ej: Extracción Concurrente / Middleware de Validación)",
      "scenario": "Descripción detallada del flujo asíncrono o procesamiento",
      "code": "# Código Python minimalista, completo y funcional\\n..."
    }},
    {{
      "case_number": 3,
      "title": "Título técnico preciso del Caso 3 (ej: Inlining de Estilos para Producción / Resiliencia y Fallback)",
      "scenario": "Descripción del patrón avanzado de producción",
      "code": "# Código Python minimalista, completo y funcional\\n..."
    }}
  ],
  "best_practices": [
    "Práctica recomendada 1",
    "Práctica recomendada 2"
  ],
  "common_pitfalls": [
    "Error común 1",
    "Error común 2"
  ]
}}
"""

        result = self.llm.generate_json(prompt=prompt, system_instruction=system_instruction)
        return result
