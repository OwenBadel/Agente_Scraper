---
id: CU-037-PYTHON-REQUESTS-QUICKSTART
title: Consumo de APIs y Peticiones HTTP con Requests
type: use-case
version: 1.0.0
status: active
created_at: '2026-09-03T17:56:34.612065-05:00'
updated_at: '2026-09-03T17:56:34.612065-05:00'
source_url: https://docs.python-requests.org/en/latest/user/quickstart/
tags:
- python
- requests
- http-client
- api-rest
- caso-de-uso
skills_required:
- 01_Skills/SKILL_001_SCRAPING_EXTRACCION_WEB
dependencies:
- requests>=2.31.0
complexity: basic
semantic_summary: Guía práctica para realizar peticiones HTTP de forma elegante y
  sencilla utilizando la librería Requests de Python. Cubre desde operaciones básicas
  como GET y POST hasta el manejo de parámetros en URLs, respuestas JSON, contenido
  binario y subida de archivos multipart.
---

# 💡 Consumo de APIs y Peticiones HTTP con Requests

> **Origen:** [https://docs.python-requests.org/en/latest/user/quickstart/](https://docs.python-requests.org/en/latest/user/quickstart/)  
> **Complejidad:** `basic` | **Estándar:** `OKF v1.0.0`

---

## 📌 Resumen Conceptual y Propósito
Guía práctica para realizar peticiones HTTP de forma elegante y sencilla utilizando la librería Requests de Python. Cubre desde operaciones básicas como GET y POST hasta el manejo de parámetros en URLs, respuestas JSON, contenido binario y subida de archivos multipart.

```mermaid
graph LR
    Input["Entrada / Configuración"] --> Logic["Lógica de python-requests-quickstart"]
    Logic --> Output["Resultado Validado"]
```

---

## 🛠️ Requisitos de Instalación
```bash
pip install requests>=2.31.0
```

---

## 🚀 Casos de Uso y Scripts Minimalistas

### Caso 1: Quickstart / Implementación elemental básica
* **Escenario:** Realizar una petición GET simple con parámetros en la URL y procesar una respuesta en formato JSON.
* **Código Minimalista:**

```python
import requests

# Definir parámetros para la consulta en la URL
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}

# Realizar la petición GET con parámetros
response = requests.get('https://httpbin.org/get', params=payload)

# Imprimir la URL construida y codificada automáticamente
print(f"URL Final: {response.url}")

# Validar y procesar la respuesta JSON
if response.status_code == 200:
    data = response.json()
    print("Respuesta JSON decodificada exitosamente:", data.get('args'))
```

---

### Caso 2: Manejo de errores y decodificación de respuestas
* **Escenario:** Enviar datos mediante POST utilizando el parámetro JSON automático y manejar posibles excepciones de decodificación o códigos de error HTTP.
* **Código Minimalista:**

```python
import requests

url = 'https://httpbin.org/post'
payload = {'username': 'developer', 'active': True}

try:
    # Envío automático de datos serializados como JSON
    response = requests.post(url, json=payload, timeout=5)
    
    # Lanzar excepción si el código de estado indica un error HTTP (4xx o 5xx)
    response.raise_for_status()
    
    result = response.json()
    print("POST exitoso. Datos recibidos por el servidor:", result.get('json'))

except requests.exceptions.HTTPError as err:
    print(f"Error HTTP ocurrido: {err}")
except requests.exceptions.JSONDecodeError:
    print("La respuesta no contiene un JSON válido.")
except requests.exceptions.RequestException as err:
    print(f"Error en la conexión o petición: {err}")
```

---

### Caso 3: Patrón de producción / Streaming y Subida de Archivos
* **Escenario:** Implementar un patrón resiliente para descargar archivos grandes utilizando streaming por bloques (chunks) y realizar envíos multipart de archivos.
* **Código Minimalista:**

```python
import requests
from io import BytesIO

# 1. Patrón de producción para descarga mediante Streaming
download_url = 'https://httpbin.org/bytes/1024'

try:
    with requests.get(download_url, stream=True, timeout=10) as r:
        r.raise_for_status()
        buffer = BytesIO()
        
        # Iterar sobre el contenido en fragmentos (chunks) para optimizar memoria
        for chunk in r.iter_content(chunk_size=128):
            if chunk:
                buffer.write(chunk)
                
        print(f"Descarga por streaming completada. Bytes descargados: {len(buffer.getvalue())}")

except requests.exceptions.RequestException as e:
    print(f"Fallo en la descarga por streaming: {e}")

# 2. Subida de archivos Multipart-Encoded
upload_url = 'https://httpbin.org/post'
file_data = {'file': ('report.csv', 'id,name\n1,test\n', 'text/csv')}

response = requests.post(upload_url, files=file_data)
print("Estado de subida de archivo:", response.status_code)
```

---


## ⚠️ Consideraciones Técnicas y Gotchas
* **Buenas Prácticas:** Siempre utiliza `response.raise_for_status()` después de una petición para detectar rápidamente fallos HTTP.
* **Buenas Prácticas:** Emplea el parámetro `json=...` en lugar de `data=json.dumps(...)` para que Requests configure automáticamente el Content-Type adecuado.
* **Buenas Prácticas:** Utiliza `stream=True` junto con `iter_content()` al descargar archivos pesados para evitar agotar la memoria RAM.
* **Gotcha/Alerta:** Olvidar capturar excepciones específicas como `requests.exceptions.RequestException`, lo que puede romper la aplicación ante fallos de red.
* **Gotcha/Alerta:** Asumir que un código de estado 200 está garantizado al llamar a `r.json()`, lo que puede generar fallos si el servidor responde con HTML o contenido vacío.
* **Gotcha/Alerta:** Pasar datos al parámetro `data` esperando que se serialicen como JSON sin configurar explícitamente las cabeceras ni la serialización.

---

## 🔗 Nodos Relacionados en el Grafo
* [[01_Skills/SKILL_001_Scraping_y_Extraccion_Web|Habilidad Técnica: Scraping y Extracción Web]]
* [[03_Proyectos/PROJ_001_Agente_Scraper|Proyecto: Agente Scraper]]
