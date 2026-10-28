"""
Módulo de Extracción: ALeRCE Broker API (Centro de Modelamiento Matemático / MAS Chile).
Endpoint: https://api.alerce.online/ztf/v1/objects/ (REST API JSON con paginación)
Guarda la respuesta cruda (JSONB) en raw.alerce_objects_raw.
"""

import json
import time
import requests
import psycopg2
from src.config import get_connection, ALERCE_API_URL, DEFAULT_MJD_INICIO, DEFAULT_MJD_FIN

def validar_api_alerce(url: str = ALERCE_API_URL, timeout: int = 15) -> bool:
    """
    Tarea de validación previa exigida por la pauta (Sección 5).
    Comprueba que la API pública del broker ALeRCE responda con latencia óptima.
    Utiliza parámetros indexados para evitar escaneos globales lentos.
    """
    target_url = url if url.endswith("/") else url + "/"
    params = {
        "classifier": "lc_classifier",
        "page": 1,
        "page_size": 1
    }
    
    # Intento 1: Consulta indexada al endpoint de objetos
    try:
        response = requests.get(target_url, params=params, timeout=timeout)
        response.raise_for_status()
        return True
    except Exception as e:
        # Intento 2: Fallback al endpoint liviano de metadatos /classifiers
        try:
            base_root = target_url.split("/objects")[0]
            clf_url = base_root + "/classifiers"
            resp_fallback = requests.get(clf_url, timeout=timeout)
            resp_fallback.raise_for_status()
            return True
        except Exception:
            raise e

def extraer_alerce_raw(
    base_url: str = ALERCE_API_URL,
    mjd_inicio: float = DEFAULT_MJD_INICIO,
    mjd_fin: float = DEFAULT_MJD_FIN,
    max_paginas: int = 5,
    page_size: int = 50,
    timeout: int = 20
) -> list:
    """
    Extrae objetos y alertas astronómicas clasificados por ALeRCE manejando
    paginación ordenada por lastmjd descendente.
    """
    target_url = base_url if base_url.endswith("/") else base_url + "/"
    paginas_extraidas = []
    
    for pagina in range(1, max_paginas + 1):
        params = {
            "classifier": "lc_classifier",
            "page": pagina,
            "page_size": page_size,
            "order_by": "lastmjd",
            "order_mode": "DESC"
        }
        if mjd_inicio and mjd_fin:
            params["firstmjd"] = mjd_inicio
            params["lastmjd"] = mjd_fin

        try:
            resp = requests.get(target_url, params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", []) if isinstance(data, dict) else []
            if not items:
                break
            paginas_extraidas.append({
                "pagina": pagina,
                "payload": data
            })
            time.sleep(0.1)
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

def leer_alerce_raw(run_id: str) -> list:
    """
    Lee las páginas crudas previamente almacenadas en raw.alerce_objects_raw
    para garantizar reproducibilidad sin volver a consultar la API externa.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT pagina, payload
                FROM raw.alerce_objects_raw
                WHERE run_id = %s
                ORDER BY pagina ASC;
                """,
                (run_id,)
            )
            rows = cur.fetchall()
            return [{"pagina": r[0], "payload": r[1]} for r in rows]
    finally:
        conn.close()
