"""
CLI y Orquestador del Agente Scraper y Analizador de Documentación.
Punto de entrada principal para PROJ_001_Agente_Scraper.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path

# Permitir imports relativos dentro de src/ y acceso a 00_Core_Agentes
src_dir = Path(__file__).resolve().parent
project_dir = src_dir.parent
vault_dir = project_dir.parent.parent

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(vault_dir / "00_Core_Agentes"))

from extractor import DocExtractor
from llm_client import LLMClient
from analyzer import DocAnalyzer
from web_exporter import WebExporter
from mcp_server.client import KnowledgeGraphMCPClient


def run_scraper_agent(url: str, provider: str = None, model: str = None) -> str:
    print(f"\n[1/5] 🔍 Iniciando extracción de documentación: {url}")
    extractor = DocExtractor()
    extracted_data = extractor.extract(url)
    print(f"      ✓ Extraído: '{extracted_data['title']}' ({extracted_data['content_length']} caracteres, {extracted_data['total_code_blocks']} bloques de código)")

    print("\n[2/5] 🧠 Consultando Grafo de Conocimiento vía Servidor MCP...")
    mcp_client = KnowledgeGraphMCPClient()
    skills_nodes = mcp_client.search_graph(node_type="skill")
    existing_skills = [s.get("id") for s in skills_nodes if isinstance(s, dict) and "id" in s]
    print(f"      ✓ Grafo consultado vía MCP ({len(skills_nodes)} skills encontradas para contexto)")

    print("\n[3/5] 🤖 Analizando contenido y formulando 3 casos de uso...")
    llm = LLMClient(provider=provider, model=model)
    analyzer = DocAnalyzer(llm_client=llm)
    analysis = analyzer.analyze(extracted_data, existing_skills=existing_skills)
    analysis["source_url"] = url
    analysis["url"] = url
    print(f"      ✓ Análisis completado: '{analysis.get('title')}'")

    print("\n[4/5] 📝 Agregando Resumen y Casos de Uso al Grafo de Conocimiento vía MCP...")
    mcp_result = mcp_client.add_knowledge_summary(
        title=analysis.get("title", "Caso de Uso"),
        slug=analysis.get("slug", "caso-de-uso"),
        source_url=url,
        semantic_summary=analysis.get("semantic_summary", ""),
        cases=analysis.get("cases", []),
        tags=analysis.get("tags", []),
        skills_required=analysis.get("skills_required", []),
        dependencies=analysis.get("dependencies", []),
        complexity=analysis.get("complexity", "intermediate"),
        best_practices=analysis.get("best_practices", []),
        common_pitfalls=analysis.get("common_pitfalls", []),
        target_folder=f"03_Proyectos/{project_dir.name}/casos_de_uso"
    )
    output_path = Path(mcp_result["file_path"])
    md_content = output_path.read_text(encoding="utf-8")
    print(f"      🎉 ¡Nodo agregado al Grafo vía Tool Call de MCP!\n      📂 Nodo: {mcp_result.get('node_id')} ({output_path.name})\n      📊 Total de nodos en el Grafo: {mcp_result.get('total_nodes_in_graph')}")

    print("\n[5/5] 🌐 Generando Página Web interactiva con Botón de Descarga...")
    web_exporter = WebExporter(project_path=str(project_dir))
    web_path = web_exporter.export_web_page(analysis, md_content=md_content, filename_stem=output_path.stem)
    print(f"      🎉 ¡Página Web generada!\n      🌐 Archivo HTML: {web_path}")

    return str(output_path)


def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Agente Scraper y Generador de Casos de Uso (PROJ_001_Agente_Scraper)")
    parser.add_argument("--url", "-u", default=None, help="URL de la documentación técnica a procesar")
    parser.add_argument("--file", "-f", default=None, help="Archivo .txt con lista de URLs (una por línea)")
    parser.add_argument("--provider", "-p", default=None, help="Proveedor LLM (gemini, openai, anthropic)")
    parser.add_argument("--model", "-m", default=None, help="Modelo específico a utilizar")
    
    args = parser.parse_args()
    
    urls = []
    if args.url:
        urls.append(args.url)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            proj_file = project_dir / args.file
            if proj_file.exists():
                file_path = proj_file
            else:
                print(f"❌ Error: El archivo {args.file} no existe en {file_path} ni en {proj_file}.", file=sys.stderr)
                sys.exit(1)
        urls = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    else:
        print("❌ Error: Debes proporcionar una URL (--url) o un archivo (--file).", file=sys.stderr)
        sys.exit(1)

    for i, target_url in enumerate(urls, 1):
        if len(urls) > 1:
            print(f"\n==================== Procesando [{i}/{len(urls)}] ====================")
        try:
            run_scraper_agent(url=target_url, provider=args.provider, model=args.model)
        except Exception as e:
            print(f"\n❌ Error procesando {target_url}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
