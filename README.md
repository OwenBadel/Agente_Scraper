# 🤖 Agente Scraper — Extractor y Analizador Autónomo de Documentación

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**Autor y Titular:** Ingeniero Owen Badel Hooker  
**GitHub:** [OwenBadel](https://github.com/OwenBadel)  
**Repositorio Oficial:** [Agente_Scraper](https://github.com/OwenBadel/Agente_Scraper)  

---

El **Agente Scraper** es una solución de software profesional e independiente capaz de ingerir documentación técnica web, limpiar ruido publicitario/navegacional, formular 3 casos de uso prácticos minimalistas con IA y generar tanto la **Nota de Conocimiento (.md para Obsidian)** como una **Página Web Interactiva (HTML)** con botón de descarga.

---

## 📂 Estructura del Proyecto

```text
PROJ_001_Agente_Scraper/
├── src/                                  <-- Código Fuente Autónomo
│   ├── extractor.py                      <-- Parsing HTML, BeautifulSoup4, Markdownify, resiliencia curl
│   ├── llm_client.py                     <-- Cliente LLM multi-modelo (Gemini API / Fallback chain)
│   ├── analyzer.py                       <-- Formulación de 3 Casos de Uso estructurados
│   ├── okf_exporter.py                   <-- Exportador de Notas .md (Estándar OKF)
│   ├── web_exporter.py                   <-- Exportador de Páginas Web HTML + Catálogo index.html
│   └── main.py                           <-- Orquestador CLI
├── casos_de_uso/                         <-- Notas Markdown OKF producidas
├── paginas_web/                          <-- Sitio Web Interactivo y Catálogo index.html
├── urls.txt                              <-- Lista de URLs a procesar (Batch 1)
├── urls_db.txt                           <-- Lista de URLs a procesar (Bases de datos)
├── requirements.txt                      <-- Dependencias independientes de Python
├── README.md                             <-- Documentación Técnica de Ejecución
└── PROJ_001_Agente_Scraper.md           <-- Ficha del Proyecto en el Grafo
```

---

## 🚀 Guía de Instalación y Ejecución

### 1. Requisitos Previos
* Python 3.10 o superior.
* Clave de API de Gemini (`GEMINI_API_KEY`) configurada en variable de entorno o archivo `.env`.

### 2. Instalación de Dependencias
```bash
git clone https://github.com/OwenBadel/Agente_Scraper.git
cd Agente_Scraper
pip install -r requirements.txt
```

### 3. Modos de Ejecución

#### A. Procesar una URL individual
```bash
python src/main.py --url "https://fastapi.tiangolo.com/tutorial/first-steps/"
```

#### B. Procesar un lote (Batch) desde un archivo de URLs
```bash
python src/main.py --file urls_db.txt
```

#### C. Iniciar Servidor Web e Interfaz Gráfica de Ingesta (FastAPI)
```bash
python src/app.py
```
Abre tu navegador en `http://127.0.0.1:8000` para acceder a la aplicación web interactiva conectada al servidor MCP.

---

## 📦 Entregables Generados

1. **Nota Markdown OKF (`casos_de_uso/CU_XXX_slug.md`):**  
   Archivo de conocimiento estructurado con Frontmatter YAML conforme al estándar OKF, listo para importar en Obsidian.

2. **Página Web Interactiva (`paginas_web/Web_CU_XXX_slug.html`):**  
   Página web autónoma con diseño dark mode glassmorphism, resaltado de sintaxis, botón de copia y el botón principal **"📥 Descargar Nota .md para Obsidian"**.

3. **Catálogo General (`paginas_web/index.html`):**  
   Sitio web central del proyecto que consolida todas las páginas generadas.
