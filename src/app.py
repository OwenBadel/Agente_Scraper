"""
Servidor Backend FastAPI para PROJ_001_Agente_Scraper.
Expone API REST simplificada y sirve la interfaz web de ingesta agéntica conectada al Servidor MCP de Obsidian.
"""

from __future__ import annotations
import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Configurar rutas para imports locales
src_dir = Path(__file__).resolve().parent
project_dir = src_dir.parent
vault_dir = project_dir.parent.parent
static_dir = project_dir / "static"
paginas_web_dir = project_dir / "paginas_web"
casos_uso_dir = project_dir / "casos_de_uso"

static_dir.mkdir(parents=True, exist_ok=True)
paginas_web_dir.mkdir(parents=True, exist_ok=True)
casos_uso_dir.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(vault_dir / "00_Core_Agentes"))

from extractor import DocExtractor
from llm_client import LLMClient
from analyzer import DocAnalyzer
from web_exporter import WebExporter
from mcp_server.client import KnowledgeGraphMCPClient

# Inicializar FastAPI
app = FastAPI(
    title="Agente Scraper & Knowledge Graph MCP",
    version="1.3.0",
    description="Interfaz Web Autónoma para ingesta de documentación y adición al Grafo de Obsidian vía MCP."
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos Pydantic
class ProcessRequest(BaseModel):
    input_text: str = Field(..., description="URL individual o lista de URLs separadas por saltos de línea")
    provider: Optional[str] = None
    model: Optional[str] = None


def _process_url(url: str, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """Ejecuta el pipeline completo de un enlace y lo añade al Grafo vía MCP."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        raise ValueError(f"URL no válida: {url}")

    # 1. Extracción
    extractor = DocExtractor()
    extracted_data = extractor.extract(url)

    # 2. Consulta MCP Context
    mcp_client = KnowledgeGraphMCPClient()
    skills_nodes = mcp_client.search_graph(node_type="skill")
    existing_skills = [s.get("id") for s in skills_nodes if isinstance(s, dict) and "id" in s]

    # 3. Análisis LLM
    llm = LLMClient(provider=provider, model=model)
    analyzer = DocAnalyzer(llm_client=llm)
    analysis = analyzer.analyze(extracted_data, existing_skills=existing_skills)
    analysis["source_url"] = url
    analysis["url"] = url

    # 4. Inserción en el Grafo de Obsidian vía Tool Call MCP
    doc_title = analysis.get("title") or extracted_data.get("title") or "Documentación"
    mcp_result = mcp_client.add_knowledge_summary(
        title=doc_title,
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

    # 5. Generar Página Web Interactiva
    web_exporter = WebExporter(project_path=str(project_dir))
    web_path = web_exporter.export_web_page(analysis, md_content=md_content, filename_stem=output_path.stem)

    return {
        "status": "success",
        "url": url,
        "title": doc_title,
        "slug": analysis.get("slug", "caso-de-uso"),
        "semantic_summary": analysis.get("semantic_summary", ""),
        "complexity": analysis.get("complexity", "intermediate"),
        "tags": analysis.get("tags", []),
        "cases": analysis.get("cases", []),
        "best_practices": analysis.get("best_practices", []),
        "common_pitfalls": analysis.get("common_pitfalls", []),
        "mcp_node_id": mcp_result.get("node_id"),
        "filename": output_path.name,
        "web_page_url": f"/pages/{web_path.name}",
        "md_download_url": f"/cases/{output_path.name}",
        "total_nodes_in_graph": mcp_result.get("total_nodes_in_graph")
    }


# Endpoints API

@app.get("/api/status")
def get_system_status():
    """Retorna el estado de salud del sistema y servidor MCP."""
    client = KnowledgeGraphMCPClient()
    skills = client.search_graph(node_type="skill")
    total_skills = len(skills) if isinstance(skills, list) else 0

    existing_cases = list(casos_uso_dir.glob("CU_*.md"))
    total_cases = len(existing_cases)

    return {
        "status": "online",
        "mcp_server": "active",
        "total_skills": total_skills,
        "total_cases": total_cases
    }


@app.post("/api/process")
def process_input_urls(req: ProcessRequest):
    """Procesa una URL única o lista de URLs separadas por saltos de línea."""
    raw_lines = [l.strip() for l in req.input_text.splitlines() if l.strip() and not l.startswith("#")]
    valid_urls = [u for u in raw_lines if u.startswith("http://") or u.startswith("https://")]
    
    if not valid_urls:
        raise HTTPException(status_code=400, detail="Por favor ingresa al menos una URL válida que comience con http:// o https://")

    results = []
    for u in valid_urls:
        try:
            res = _process_url(u, provider=req.provider, model=req.model)
            results.append(res)
        except Exception as e:
            results.append({
                "status": "error",
                "url": u,
                "error": str(e)
            })

    is_single = len(results) == 1
    return {
        "status": "success",
        "mode": "single" if is_single else "batch",
        "data": results[0] if is_single else results
    }


@app.post("/api/upload")
async def upload_urls_file(file: UploadFile = File(...)):
    """Procesa un archivo .txt con enlaces."""
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="replace")
        raw_lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
        valid_urls = [u for u in raw_lines if u.startswith("http://") or u.startswith("https://")]

        if not valid_urls:
            raise HTTPException(status_code=400, detail="El archivo no contiene URLs válidas (deben empezar con http:// o https://)")

        results = []
        for u in valid_urls:
            try:
                res = _process_url(u)
                results.append(res)
            except Exception as e:
                results.append({"status": "error", "url": u, "error": str(e)})

        is_single = len(results) == 1
        return {
            "status": "success",
            "mode": "single" if is_single else "batch",
            "data": results[0] if is_single else results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo archivo: {str(e)}")


# Montar directorios estáticos
app.mount("/pages", StaticFiles(directory=str(paginas_web_dir), html=True), name="paginas_web")
app.mount("/cases", StaticFiles(directory=str(casos_uso_dir)), name="casos_uso")
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
