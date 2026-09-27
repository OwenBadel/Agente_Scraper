"""
Exportador y Formateador OKF (Open Knowledge Format) para Casos de Uso del PROJ_001_Agente_Scraper.
Genera archivos Markdown estandarizados en 03_Proyectos/PROJ_001_Agente_Scraper/casos_de_uso/
"""

from __future__ import annotations
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


class OKFExporter:
    def __init__(self, project_path: Optional[str] = None):
        if not project_path:
            project_path = str(Path(__file__).resolve().parent.parent)
        self.project_dir = Path(project_path).resolve()
        self.casos_uso_dir = self.project_dir / "casos_de_uso"
        self.casos_uso_dir.mkdir(parents=True, exist_ok=True)

    def _get_next_id(self) -> int:
        """Determina el siguiente número correlativo para CU-XXX."""
        existing_files = list(self.casos_uso_dir.glob("CU_*.md")) + list(self.casos_uso_dir.glob("*.md"))
        max_id = 0
        pattern = re.compile(r"CU[_-](\d+)", re.IGNORECASE)
        for f in existing_files:
            match = pattern.search(f.stem)
            if match:
                num = int(match.group(1))
                if num > max_id:
                    max_id = num
        return max_id + 1

    def export_use_case(self, analysis: Dict[str, Any], source_url: str) -> Path:
        """Genera el archivo .md estructurado bajo el estándar OKF."""
        next_num = self._get_next_id()
        id_str = f"CU-{next_num:03d}"
        
        raw_slug = analysis.get("slug", "caso-de-uso").lower()
        clean_slug = re.sub(r"[^a-z0-9_-]", "-", raw_slug).strip("-")
        
        filename = f"CU_{next_num:03d}_{clean_slug}.md"
        target_path = self.casos_uso_dir / filename

        now_iso = datetime.now(timezone.utc).astimezone().isoformat()

        title = analysis.get("title", f"Caso de Uso: {clean_slug}")
        tags = analysis.get("tags", ["python", "use-case"])
        if not any(t.startswith("caso-de-uso") for t in tags):
            tags.append("caso-de-uso")

        dependencies = analysis.get("dependencies", [])
        skills_required = analysis.get("skills_required", ["[[01_Skills/SKILL_001_Scraping_y_Extraccion_Web|Scraping y Extracción Web]]"])
        complexity = analysis.get("complexity", "intermediate")
        semantic_summary = analysis.get("semantic_summary", "")

        # 1. Construir Frontmatter YAML
        frontmatter_dict = {
            "id": f"{id_str}-{clean_slug.upper()}",
            "title": title,
            "type": "use-case",
            "version": "1.0.0",
            "status": "active",
            "created_at": now_iso,
            "updated_at": now_iso,
            "source_url": source_url,
            "tags": tags,
            "skills_required": skills_required,
            "dependencies": dependencies,
            "complexity": complexity,
            "semantic_summary": semantic_summary
        }

        yaml_content = yaml.dump(frontmatter_dict, sort_keys=False, allow_unicode=True)

        # 2. Formatear cuerpo Markdown
        cases = analysis.get("cases", [])
        best_practices = analysis.get("best_practices", [])
        pitfalls = analysis.get("common_pitfalls", [])

        cases_md = ""
        for c in cases:
            c_num = c.get("case_number", 1)
            c_title = c.get("title", f"Caso {c_num}")
            c_scenario = c.get("scenario", "")
            c_code = c.get("code", "").strip()
            
            cases_md += f"""### Caso {c_num}: {c_title}
* **Escenario:** {c_scenario}
* **Código Minimalista:**

```python
{c_code}
```

---

"""

        dep_install = "pip install " + " ".join(dependencies) if dependencies else "# Sin dependencias adicionales"

        practices_md = "\n".join([f"* **Buenas Prácticas:** {p}" for p in best_practices]) if best_practices else "* Mantener scripts minimalistas y aislados."
        pitfalls_md = "\n".join([f"* **Gotcha/Alerta:** {p}" for p in pitfalls]) if pitfalls else "* Validar compatibilidad de versiones de las dependencias."

        body_content = f"""# 💡 {title}

> **Origen:** [{source_url}]({source_url})  
> **Complejidad:** `{complexity}` | **Estándar:** `OKF v1.0.0`

---

## 📌 Resumen Conceptual y Propósito
{semantic_summary}

```mermaid
graph LR
    Input["Entrada / Configuración"] --> Logic["Lógica de {clean_slug}"]
    Logic --> Output["Resultado Validado"]
```

---

## 🛠️ Requisitos de Instalación
```bash
{dep_install}
```

---

## 🚀 Casos de Uso y Scripts Minimalistas

{cases_md}
## ⚠️ Consideraciones Técnicas y Gotchas
{practices_md}
{pitfalls_md}

---

## 🔗 Nodos Relacionados en el Grafo
* [[01_Skills/SKILL_001_Scraping_y_Extraccion_Web|Habilidad Técnica: Scraping y Extracción Web]]
* [[03_Proyectos/PROJ_001_Agente_Scraper|Proyecto: Agente Scraper]]
"""

        full_doc = f"---\n{yaml_content}---\n\n{body_content}"
        target_path.write_text(full_doc, encoding="utf-8")
        return target_path
