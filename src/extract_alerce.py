"""
Módulo de Extracción: ALeRCE Broker API (Centro de Modelamiento Matemático / MAS Chile).
Endpoint: https://api.alerce.online/ztf/v1/objects (REST API JSON con paginación)
Guarda la respuesta cruda (JSONB) en raw.alerce_objects_raw.
"""

import json
import time
import requests
import psycopg2
from src.config import get_connection, ALERCE_API_URL, DEFAULT_MJD_INICIO, DEFAULT_MJD_FIN

def validar_api_alerce(url: str = ALERCE_API_URL, timeout: int = 35) -> bool:
    """
    Tarea de validación previa exigida por la pauta (Sección 5).
    Comprueba que la API pública del broker ALeRCE responda antes de iniciar la extracción.
    """
    params = {
        "page": 1,
        "page_size": 1
    }
    for attempt in range(1, 3):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return True
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)
    return False

def extraer_alerce_raw(
    base_url: str = ALERCE_API_URL,
    mjd_inicio: float = DEFAULT_MJD_INICIO,
    mjd_fin: float = DEFAULT_MJD_FIN,
    max_paginas: int = 10,
    page_size: int = 100,
    timeout: int = 25
) -> list:
    """
    Extrae objetos y alertas astronómicas clasificados por ALeRCE manejando
    paginación ordenada por lastmjd descendente.
    """
    paginas_extraidas = []
    for pagina in range(1, max_paginas + 1):
        params = {
            "classifier": "lc_classifier",
            "firstmjd": mjd_inicio,
            "lastmjd": mjd_fin,
            "page": pagina,
            "page_size": page_size,
            "order_by": "lastmjd",
            "order_mode": "DESC"
        }
        try:
            resp = requests.get(base_url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", []) if isinstance(data, dict) else []
            if not items:
                break
            paginas_extraidas.append({
                "pagina": pagina,
                "payload": data
            })
            # Pequeña pausa de cortesía para no saturar la API abierta chilena
            time.sleep(0.15)
        except Exception as e:
            print(f"[ALeRCE Extracción] Error en página {pagina}: {e}")
            raise e
    return paginas_extraidas

def guardar_alerce_raw(paginas_extraidas: list, run_id: str) -> int:
    """
    Inserta cada página extraída en raw.alerce_objects_raw de forma inmutable.
    """
    conn = get_connection()
    total_guardadas = 0
    try:
        with conn.cursor() as cur:
            for item in paginas_extraidas:
                cur.execute(
                    """
                    INSERT INTO raw.alerce_objects_raw (run_id, pagina, payload)
                    VALUES (%s, %s, %s);
                    """,
                    (run_id, item["pagina"], json.dumps(item["payload"]))
                )
                total_guardadas += 1
        conn.commit()
        return total_guardadas
    finally:
        conn.close()
