"""
Extractor y Limpiador de Documentación Técnica Web.
Extrae contenido limpio, aislando bloques de código y estructura semántica sin eliminar contenedores legítimos.
"""

from __future__ import annotations
import re
import urllib.parse
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import markdownify


class DocExtractor:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

    def fetch_url(self, url: str) -> str:
        """Descarga el HTML crudo de la URL, con fallback a curl.exe si hay bloqueo HTTP 403."""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code in (403, 406, 429):
                # Fallback resiliencia usando curl.exe nativo
                import subprocess
                cmd = [
                    "curl.exe", "-s", "-L",
                    "-A", self.headers["User-Agent"],
                    url
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                if res.returncode == 0 and len(res.stdout) > 200:
                    return res.stdout
            raise e

    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extrae y limpia la documentación, retornando título, bloques de código,
        contenido en markdown y texto plano estructurado.
        """
        html = self.fetch_url(url)
        soup = BeautifulSoup(html, "html.parser")

        # 1. Extraer título de la página
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()
        
        title = re.sub(r"[\s\n\r]+", " ", title).strip()
        title = re.sub(r"[¶#]+", "", title).strip()

        # 2. Identificar el contenedor principal de la documentación antes de limpiar
        main_content = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
        if not main_content:
            main_content = (
                soup.find(id=re.compile(r"(content|main|documentation|docs-content)", re.I)) or
                soup.find(class_=re.compile(r"(content|markdown-body|documentation|docs-content)", re.I)) or
                soup.find("body") or
                soup
            )

        # 3. Eliminar únicamente elementos ruidosos periféricos (nunca main ni contenedores padres)
        for tag in soup(["script", "style", "nav", "footer", "aside", "noscript", "svg", "iframe", "form", "button"]):
            tag.decompose()

        # Eliminar anuncios y banners específicos evitando tocar main o sus padres
        specific_noise = re.compile(r"\b(cookie-banner|cookie-notice|cookie-consent|advertisement|newsletter-signup)\b", re.I)
        for noisy in soup.find_all(attrs={"class": specific_noise}):
            if not (noisy.find("main") or noisy.name in ("main", "article", "body", "html")):
                noisy.decompose()

        # 4. Extraer bloques de código explícitos
        code_blocks: List[Dict[str, str]] = []
        for pre in main_content.find_all("pre"):
            code = pre.get_text().strip()
            lang = "python"
            code_tag = pre.find("code")
            if code_tag and code_tag.get("class"):
                for cls in code_tag["class"]:
                    if cls.startswith("language-") or cls.startswith("lang-"):
                        lang = cls.replace("language-", "").replace("lang-", "")
            
            # Detectar lenguaje automáticamente si es bash o docker
            if any(term in code.lower() for term in ["npm install", "pip install", "docker run", "curl -", "cargo add", "pnpm add"]):
                lang = "bash"

            if len(code) > 8:
                code_blocks.append({"language": lang, "code": code})

        # 5. Convertir a Markdown limpio
        md_content = markdownify.markdownify(
            str(main_content),
            heading_style="ATX",
            code_language="python",
            strip=["img", "button"]
        )
        
        # Limpieza de espacios en blanco repetitivos
        clean_md = re.sub(r"\n{3,}", "\n\n", md_content).strip()

        # Si el markdown quedó muy escueto (ej. sitio con render dinámico), respaldar con texto de párrafos
        if len(clean_md) < 80:
            paragraphs = [p.get_text().strip() for p in main_content.find_all(["p", "li"]) if len(p.get_text().strip()) > 20]
            clean_md = "\n\n".join(paragraphs)

        return {
            "url": url,
            "title": title or "Documentación Técnica",
            "clean_markdown": clean_md,
            "code_blocks": code_blocks,
            "total_code_blocks": len(code_blocks),
            "content_length": len(clean_md)
        }
