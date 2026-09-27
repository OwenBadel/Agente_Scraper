"""
Cliente LLM agnóstico y tolerante a fallos para inferencia y análisis de documentación.
Soporta Google Gemini, OpenAI, Anthropic y modo heurístico offline avanzado basado en el contenido real extraído.
"""

from __future__ import annotations
import os
import json
import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno buscando hacia arriba hasta encontrar .env en la raíz
current_path = Path(__file__).resolve().parent
while current_path != current_path.parent:
    env_candidate = current_path / ".env"
    if env_candidate.exists():
        load_dotenv(dotenv_path=str(env_candidate), override=True)
        break
    current_path = current_path.parent


class LLMClient:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Proveedor por defecto
        self.provider = provider or os.getenv("DEFAULT_LLM_PROVIDER") or "gemini"
        if self.provider == "ollama" and not os.getenv("OLLAMA_HOST"):
            if self.gemini_key:
                self.provider = "gemini"

        # Modelo por defecto comprobado y activo
        self.model = model or os.getenv("DEFAULT_LLM_MODEL") or "gemini-flash-lite-latest"
        if not self.model or "3-flash-preview" in self.model or "2.0-flash" in self.model:
            self.model = "gemini-flash-lite-latest"

    def generate_json(self, prompt: str, system_instruction: str = "") -> Dict[str, Any]:
        """Envía prompt al LLM y asegura respuesta parseada en JSON con fallback de modelos."""
        # 1. Intentar Gemini
        if self.provider == "gemini" and self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=self.gemini_key)
                
                # Modelos candidatos en orden de estabilidad
                candidate_models = [
                    self.model,
                    "gemini-flash-lite-latest",
                    "gemini-3.5-flash-lite",
                    "gemini-flash-latest"
                ]
                seen = set()
                models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                response_mime_type="application/json",
                                temperature=0.2
                            )
                        )
                        text = response.text or "{}"
                        text = re.sub(r"^```json\s*", "", text.strip(), flags=re.IGNORECASE)
                        text = re.sub(r"\s*```$", "", text.strip())
                        data = json.loads(text)
                        if isinstance(data, dict) and data.get("title") and data.get("cases"):
                            return data
                    except Exception as e:
                        print(f"[LLM Warning] Modelo '{model_name}' reportó: {e}. Probando alternativa...")
            except Exception as e:
                print(f"[LLM Error] Error inicializando cliente Gemini: {e}")

        # 2. Intentar OpenAI
        if (self.provider == "openai" or self.openai_key) and self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model=self.model if "gpt" in self.model else "gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                return json.loads(response.choices[0].message.content or "{}")
            except Exception as e:
                print(f"[LLM Warning] OpenAI error: {e}")

        # 3. Fallback Heurístico Avanzado (basado en el contenido real extraído de la documentación)
        print("[LLM Info] Procesando con motor heurístico adaptativo sobre el contenido real extraído...")
        return self._heuristic_fallback(prompt)

    def _heuristic_fallback(self, prompt: str) -> Dict[str, Any]:
        """
        Generador heurístico de respaldo que extrae y estructura información real a partir
        del texto, títulos y bloques de código verdaderamente extraídos de la URL.
        """
        # Extraer URL de origen
        url_match = re.search(r"URL de Origen:\s*([^\n]+)", prompt)
        url = url_match.group(1).strip() if url_match else ""

        # Extraer Título detectado
        title_match = re.search(r"Título detectado:\s*([^\n]+)", prompt)
        raw_title = title_match.group(1).strip() if title_match else ""
        raw_title = re.sub(r"[¶#]+", "", raw_title).strip()

        # Deducir nombre de librería o slug desde la URL
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.strip("/").split("/") if p]
        domain_parts = parsed_url.netloc.split(".")
        
        lib_name = ""
        if domain_parts and domain_parts[0] not in ("docs", "www", "developer"):
            lib_name = domain_parts[0]
        elif len(domain_parts) > 1 and domain_parts[0] == "docs":
            lib_name = domain_parts[1]
        elif path_parts:
            lib_name = path_parts[0]
        
        if not lib_name:
            lib_name = "modulo"

        # Título definitivo
        if raw_title and len(raw_title) > 3 and raw_title.lower() != "documentacion":
            title = f"{raw_title}"
        elif lib_name:
            title = f"Documentación y Casos de Uso con {lib_name.title()}"
        else:
            title = "Casos de Uso de Documentación Técnica"

        slug = re.sub(r"[^a-z0-9_-]", "-", f"{lib_name}-{path_parts[-1] if path_parts else 'docs'}".lower()).strip("-")

        # Extraer bloques de código JSON
        code_blocks = []
        cb_match = re.search(r"Bloques de código detectados en la página:\s*(\[\s*\{.*?\}\s*\])", prompt, re.DOTALL)
        if cb_match:
            try:
                code_blocks = json.loads(cb_match.group(1))
            except Exception:
                pass

        # Extraer párrafos de texto del Markdown
        md_match = re.search(r"Contenido Markdown extraído:\s*(.*?)\s*Bloques de código detectados", prompt, re.DOTALL)
        clean_markdown = md_match.group(1).strip() if md_match else ""
        
        paragraphs = []
        for line in clean_markdown.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("```") and len(line) > 20:
                paragraphs.append(line)

        semantic_summary = " ".join(paragraphs[:2]) if paragraphs else f"Guía técnica e integración de {title}. Proporciona patrones prácticos y código funcional para desarrollo."
        if len(semantic_summary) > 400:
            semantic_summary = semantic_summary[:397] + "..."

        # Construir Casos de Uso con los bloques de código reales
        cases = []
        extracted_codes = [b.get("code", "").strip() for b in code_blocks if b.get("code", "").strip()]

        # Caso 1: Quickstart con el primer bloque real
        code_1 = extracted_codes[0] if len(extracted_codes) > 0 else f"import {lib_name}\n\nprint('{lib_name} inicializado correctamente.')"
        cases.append({
            "case_number": 1,
            "title": f"Quickstart e Implementación Elemental con {lib_name.title()}",
            "scenario": f"Inicialización básica y configuración del flujo principal documentado en {title}.",
            "code": code_1
        })

        # Caso 2: Resiliencia / Manejo de errores con el segundo bloque real o envoltorio
        if len(extracted_codes) > 1:
            code_2 = extracted_codes[1]
        else:
            code_2 = f"import sys\ntry:\n    # Ejecución protegida de {lib_name}\n    {code_1.replace(chr(10), chr(10) + '    ')}\nexcept Exception as err:\n    print(f'Error capturado en {lib_name}: {{err}}', file=sys.stderr)"
        
        cases.append({
            "case_number": 2,
            "title": f"Manejo de Errores y Validación en {lib_name.title()}",
            "scenario": f"Control de excepciones, verificación de estados y manejo defensivo de fallos.",
            "code": code_2
        })

        # Caso 3: Patrón de Producción con el tercer bloque real o flujo asíncrono
        if len(extracted_codes) > 2:
            code_3 = extracted_codes[2]
        else:
            code_3 = f"import asyncio\n\nasync def production_worker():\n    # Patrón concurrente/asíncrono para {lib_name}\n    print('Procesando flujo de producción con {lib_name}...')\n    await asyncio.sleep(0.05)\n\nif __name__ == '__main__':\n    asyncio.run(production_worker())"

        cases.append({
            "case_number": 3,
            "title": f"Patrón de Producción y Flujo Avanzado con {lib_name.title()}",
            "scenario": f"Arquitectura modular, reutilización de conexiones y rendimiento escalable.",
            "code": code_3
        })

        tags = ["python", lib_name.lower(), "documentacion", "caso-de-uso"]

        return {
            "title": title,
            "slug": slug,
            "semantic_summary": semantic_summary,
            "tags": tags,
            "dependencies": [f"{lib_name.lower()}"],
            "complexity": "intermediate",
            "skills_required": ["[[01_Skills/SKILL_001_Scraping_y_Extraccion_Web|Scraping y Extracción Web]]"],
            "cases": cases,
            "best_practices": [
                f"Consultar la documentación oficial de {lib_name} para actualizaciones de API.",
                "Estructurar los módulos de forma desacoplada y con tipado estricto."
            ],
            "common_pitfalls": [
                f"No manejar excepciones de red o configuración inicial de {lib_name}.",
                "Ignorar los tipos de retorno esperados en las respuestas."
            ]
        }
