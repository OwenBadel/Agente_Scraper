"""
Generador de Páginas Web Interactivas para Casos de Uso del PROJ_001_Agente_Scraper.
Ubicación de entrega: 03_Proyectos/PROJ_001_Agente_Scraper/paginas_web/
"""

from __future__ import annotations
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List


class WebExporter:
    def __init__(self, project_path: Optional[str] = None):
        if not project_path:
            project_path = str(Path(__file__).resolve().parent.parent)
        self.project_dir = Path(project_path).resolve()
        # Las páginas web del Agente Scraper viven dentro de su carpeta de proyecto
        self.web_dir = self.project_dir / "paginas_web"
        self.web_dir.mkdir(parents=True, exist_ok=True)

    def export_web_page(self, analysis: Dict[str, Any], md_content: str, filename_stem: str) -> Path:
        """
        Genera una página HTML interactiva autocontenida con el botón de descarga .md para Obsidian.
        """
        title = analysis.get("title", "Caso de Uso y Patrones")
        source_url = analysis.get("source_url", analysis.get("url", "#"))
        complexity = analysis.get("complexity", "intermediate")
        dependencies = analysis.get("dependencies", [])
        tags = analysis.get("tags", [])
        summary = analysis.get("semantic_summary", "")
        cases = analysis.get("cases", [])
        best_practices = analysis.get("best_practices", [])
        pitfalls = analysis.get("common_pitfalls", [])

        # Codificar el contenido markdown en Base64 para el botón de descarga directa
        b64_md = base64.b64encode(md_content.encode("utf-8")).decode("utf-8")
        md_filename = f"{filename_stem}.md"

        # Generar código HTML de los 3 casos de uso
        cases_html = ""
        for c in cases:
            c_num = c.get("case_number", 1)
            c_title = c.get("title", f"Caso {c_num}")
            c_scenario = c.get("scenario", "")
            c_code = c.get("code", "").strip()

            escaped_code = (
                c_code.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            cases_html += f"""
            <div class="case-card">
                <div class="case-header">
                    <span class="case-badge">Caso {c_num}</span>
                    <h3 class="case-title">{c_title}</h3>
                </div>
                <p class="case-scenario">💡 <strong>Escenario:</strong> {c_scenario}</p>
                <div class="code-container">
                    <div class="code-header">
                        <span>Python Minimalista</span>
                        <button class="copy-btn" onclick="copyCode(this)">📋 Copiar</button>
                    </div>
                    <pre><code class="language-python">{escaped_code}</code></pre>
                </div>
            </div>
            """

        tags_html = "".join([f'<span class="tag">#{t}</span>' for t in tags])
        deps_html = " ".join(dependencies) if dependencies else "Ninguna"

        practices_html = "".join([f"<li>✅ <strong>Práctica:</strong> {p}</li>" for p in best_practices])
        pitfalls_html = "".join([f"<li>⚠️ <strong>Alerta:</strong> {p}</li>" for p in pitfalls])

        html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Fábrica de Software</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-code: #090d16;
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --accent-green: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            line-height: 1.6;
            padding: 2rem 1rem;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        .nav-back {{
            margin-bottom: 1.5rem;
        }}

        .nav-back a {{
            color: #818cf8;
            text-decoration: none;
            font-weight: 500;
        }}

        header {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}

        .title {{
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .meta-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            margin-top: 1rem;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .badge {{
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.4);
            padding: 0.2rem 0.8rem;
            border-radius: 20px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.75rem;
        }}

        .cta-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
        }}

        .download-btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #10b981, #059669);
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.8rem 1.5rem;
            border-radius: 10px;
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
        }}

        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
            background: linear-gradient(135deg, #059669, #047857);
        }}

        .summary-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}

        .summary-title {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #818cf8;
        }}

        .case-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.8rem;
            margin-bottom: 2rem;
        }}

        .case-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }}

        .case-badge {{
            background: #6366f1;
            color: white;
            font-weight: 700;
            padding: 0.3rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
        }}

        .case-title {{
            font-size: 1.4rem;
            font-weight: 600;
        }}

        .case-scenario {{
            color: #cbd5e1;
            margin-bottom: 1rem;
            font-size: 1rem;
        }}

        .code-container {{
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }}

        .code-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e293b;
            padding: 0.5rem 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }}

        .copy-btn {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.75rem;
            transition: all 0.2s ease;
        }}

        .copy-btn:hover {{
            background: var(--border);
            color: white;
        }}

        pre {{
            padding: 1.2rem;
            overflow-x: auto;
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
            color: #e2e8f0;
        }}

        .tags-container {{
            display: flex;
            gap: 0.5rem;
        }}

        .tag {{
            color: #94a3b8;
            font-size: 0.85rem;
        }}

        .considerations {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .consideration-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
        }}

        .consideration-box h4 {{
            margin-bottom: 0.8rem;
            font-size: 1.1rem;
        }}

        .consideration-box ul {{
            list-style: none;
        }}

        .consideration-box li {{
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
            color: #cbd5e1;
        }}

        footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-back">
            <a href="index.html">← Volver al Catálogo General de Páginas Web</a>
        </div>
        <header>
            <h1 class="title">{title}</h1>
            <p>Documentación técnica analizada por PROJ_001_Agente_Scraper</p>
            
            <div class="meta-bar">
                <span class="badge">{complexity}</span>
                <span>🌐 <strong>Documentación Oficial:</strong> <a href="{source_url}" target="_blank" style="color: #79f2f0; text-decoration: underline; font-family: monospace;">{source_url} ↗</a></span>
                <span>📦 Dependencias: <code>{deps_html}</code></span>
                <div class="tags-container">{tags_html}</div>
            </div>

            <div class="cta-bar">
                <span>Estándar de Conocimiento: <strong>OKF v1.0.0 (Obsidian)</strong></span>
                <!-- BOTÓN PRINCIPAL DE DESCARGA DIRECTA DE ARCHIVO .MD PARA OBSIDIAN -->
                <a id="downloadBtn" class="download-btn" href="data:text/markdown;base64,{b64_md}" download="{md_filename}">
                    📥 Descargar Nota .md para Obsidian
                </a>
            </div>
        </header>

        <section class="summary-card">
            <h2 class="summary-title">📌 Resumen Técnico de la Documentación</h2>
            <p>{summary}</p>
            <div style="margin-top: 0.8rem; font-size: 0.85rem; color: #94a3b8;">
                🔗 <strong>Fuente:</strong> <a href="{source_url}" target="_blank" style="color: #818cf8; text-decoration: underline;">{source_url}</a>
            </div>
        </section>

        <h2 style="margin-bottom: 1.5rem; font-size: 1.6rem; color: #f8fafc;">🚀 3 Casos de Uso Prácticos y Scripts Minimalistas</h2>
        {cases_html}

        <div class="considerations">
            <div class="consideration-box">
                <h4 style="color: #10b981;">✅ Buenas Prácticas</h4>
                <ul>{practices_html}</ul>
            </div>
            <div class="consideration-box">
                <h4 style="color: #f43f5e;">⚠️ Gotchas & Alertas</h4>
                <ul>{pitfalls_html}</ul>
            </div>
        </div>

        <footer>
            <p>PROJ_001_Agente_Scraper | Fábrica de Software Autónoma (OKF & Obsidian)</p>
        </footer>
    </div>

    <script>
        function copyCode(button) {{
            const codeBlock = button.parentElement.nextElementSibling.querySelector('code');
            navigator.clipboard.writeText(codeBlock.innerText).then(() => {{
                button.innerText = '✓ Copiado';
                setTimeout(() => {{ button.innerText = '📋 Copiar'; }}, 2000);
            }});
        }}
    </script>
</body>
</html>
"""
        target_path = self.web_dir / f"Web_{filename_stem}.html"
        target_path.write_text(html_template, encoding="utf-8")

        # Actualizar index.html del catálogo general
        self.update_index_catalog()

        return target_path

    def update_index_catalog(self) -> Path:
        """
        Genera/actualiza index.html en paginas_web/ listando todas las páginas web de casos de uso creadas.
        """
        html_files = sorted(list(self.web_dir.glob("Web_*.html")))
        cards_html = ""

        for hfile in html_files:
            rel_name = hfile.name
            clean_title = rel_name.replace("Web_", "").replace(".html", "").replace("_", " ").title()

            cards_html += f"""
            <div style="background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem; color: #818cf8;">{clean_title}</h3>
                    <p style="color: #94a3b8; font-size: 0.85rem;">Página Web entregable por Agente Scraper</p>
                </div>
                <a href="{rel_name}" style="background: #6366f1; color: white; padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem;">Ver Página Web ↗</a>
            </div>
            """

        index_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo de Páginas Web — PROJ_001_Agente_Scraper</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #334155;
        }}
        h1 {{
            font-size: 2.2rem;
            background: linear-gradient(90deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .grid {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 PROJ_001_Agente_Scraper — Catálogo de Páginas Web</h1>
            <p>Páginas web interactivas generadas autónomamente para visualización y descarga de notas .md para Obsidian.</p>
        </header>
        <div class="grid">
            {cards_html or '<p style="color: #94a3b8;">No hay páginas web generadas aún.</p>'}
        </div>
    </div>
</body>
</html>
"""
        index_path = self.web_dir / "index.html"
        index_path.write_text(index_template, encoding="utf-8")
        return index_path
