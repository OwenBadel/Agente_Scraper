---
id: CU-017-PYTHON-REQUESTS-API
title: Consumo de APIs REST con Requests
type: use-case
version: 1.0.0
status: active
created_at: '2026-08-29T19:53:00.325360-05:00'
updated_at: '2026-08-29T19:53:00.325360-05:00'
source_url: https://docs.python-requests.org/en/latest/user/quickstart/
tags:
- python
- requests
- http-client
- caso-de-uso
skills_required:
- 01_Skills/SKILL-001-PYTHON-ASYNC
dependencies:
- requests>=2.31.0
complexity: intermediate
semantic_summary: Requests es la librería estándar de facto para realizar peticiones
  HTTP en Python de forma síncrona. Su diseño prioriza la legibilidad y simplicidad,
  abstrayendo la complejidad de la librería estándar urllib3 para manejar parámetros,
  cabeceras, autenticación y persistencia de sesiones de manera intuitiva.
---

# 💡 Consumo de APIs REST con Requests

> **Origen:** [https://docs.python-requests.org/en/latest/user/quickstart/](https://docs.python-requests.org/en/latest/user/quickstart/)  
> **Complejidad:** `intermediate` | **Estándar:** `OKF v1.0.0`

---

## 📌 Resumen Conceptual y Propósito
Requests es la librería estándar de facto para realizar peticiones HTTP en Python de forma síncrona. Su diseño prioriza la legibilidad y simplicidad, abstrayendo la complejidad de la librería estándar urllib3 para manejar parámetros, cabeceras, autenticación y persistencia de sesiones de manera intuitiva.

```mermaid
graph LR
    Input["Entrada / Configuración"] --> Logic["Lógica de python-requests-api"]
    Logic --> Output["Resultado Validado"]
```

---

## 🛠️ Requisitos de Instalación
```bash
pip install requests>=2.31.0
```

---

## 🚀 Casos de Uso y Scripts Minimalistas

### Caso 1: Implementación Base de Peticiones GET
* **Escenario:** Realizar una consulta a un endpoint externo pasando parámetros de búsqueda y procesando la respuesta JSON.
* **Código Minimalista:**

```python
import requests
from typing import Dict, Any

def get_api_data(endpoint: str, query_params: Dict[str, str]) -> Dict[str, Any]:
    response = requests.get(endpoint, params=query_params)
    return response.json()

if __name__ == "__main__":
    url = "https://httpbin.org/get"
    payload = {"user": "dev_factory", "version": "1.0"}
    data = get_api_data(url, payload)
    print(data)
```

---

### Caso 2: Manejo Robusto de Errores y Timeouts
* **Escenario:** Implementar un flujo que gestione fallos de red, tiempos de espera agotados y códigos de estado HTTP no exitosos.
* **Código Minimalista:**

```python
import requests
from requests.exceptions import RequestException, Timeout

def fetch_secure_resource(url: str):
    try:
        # Timeout de 5 segundos para evitar bloqueos infinitos
        response = requests.get(url, timeout=5.0)
        # Lanza excepción si el status code es 4xx o 5xx
        response.raise_for_status()
        return response.json()
    except Timeout:
        return {"error": "La solicitud excedió el tiempo de espera"}
    except RequestException as e:
        return {"error": f"Error de comunicación: {str(e)}"}

print(fetch_secure_resource("https://api.github.com/events"))
```

---

### Caso 3: Patrón de Sesión Resiliente con Reintentos
* **Escenario:** Configurar una sesión persistente con una estrategia de reintentos automáticos (Exponential Backoff) para entornos de producción.
* **Código Minimalista:**

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_resilient_client() -> requests.Session:
    session = requests.Session()
    # Reintentar en errores 500, 502, 503, 504 y 429 (Rate Limit)
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

with get_resilient_client() as client:
    response = client.get("https://httpbin.org/status/500")
    print(f"Final Status after retries: {response.status_code}")
```

---


## ⚠️ Consideraciones Técnicas y Gotchas
* **Buenas Prácticas:** Utilizar siempre el parámetro 'timeout' para evitar que la aplicación se cuelgue indefinidamente.
* **Buenas Prácticas:** Emplear 'requests.Session()' para reutilizar conexiones TCP y mejorar el rendimiento en múltiples peticiones al mismo host.
* **Buenas Prácticas:** Usar 'response.raise_for_status()' inmediatamente después de la petición para validar el éxito de la operación.
* **Gotcha/Alerta:** No manejar excepciones específicas, lo que puede causar cierres inesperados del programa ante fallos de red.
* **Gotcha/Alerta:** Ignorar el cierre de sesiones; se recomienda usar el gestor de contexto 'with' para asegurar la liberación de recursos.

---

## 🔗 Nodos Relacionados en el Grafo
* [[01_Skills/SKILL_001_Scraping_y_Extraccion_Web|Habilidad Técnica: Scraping y Extracción Web]]
* [[03_Proyectos/PROJ_001_Agente_Scraper|Proyecto: Agente Scraper]]
