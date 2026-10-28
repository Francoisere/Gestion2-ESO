"""
Módulo de Extracción: ESO Science Archive (Chile TAP Service).
Endpoint: https://archive.eso.org/tap_obs/sync (Protocolo IVOA TAP, ADQL)
Guarda la respuesta cruda (JSONB) en raw.eso_observations_raw.
"""

import json
import time
import requests
import psycopg2
from src.config import get_connection, ESO_API_URL, DEFAULT_MJD_INICIO, DEFAULT_MJD_FIN

def validar_api_eso(url: str = ESO_API_URL, timeout: int = 15) -> bool:
    """
    Tarea de validación previa exigida por la pauta (Sección 5).
    Comprueba que el servicio TAP de ESO responda antes de iniciar la extracción.
    """
    test_query = "SELECT TOP 1 obs_id FROM ivoa.ObsCore"
    params = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "json",
        "QUERY": test_query
    }
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return True

def extraer_eso_raw(
    base_url: str = ESO_API_URL,
    mjd_inicio: float = DEFAULT_MJD_INICIO,
    mjd_fin: float = DEFAULT_MJD_FIN,
    limite: int = 1000,
    timeout: int = 45
) -> dict:
    """
    Extrae observaciones desde ESO TAP Service en formato JSON mediante consulta ADQL.
    """
    adql_query = f"""
        SELECT TOP {limite}
            obs_id, facility_name, instrument_name, dataproduct_type,
            calib_level, t_min, t_exptime, access_estsize, s_ra, s_dec
        FROM ivoa.ObsCore
        WHERE t_min >= {mjd_inicio} AND t_min < {mjd_fin}
          AND facility_name IS NOT NULL
        ORDER BY t_min DESC
    """
    params = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "json",
        "QUERY": adql_query
    }
    response = requests.get(base_url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()

def guardar_eso_raw(payload: dict, run_id: str) -> int:
    """
    Inserta el payload crudo e inmutable en raw.eso_observations_raw.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw.eso_observations_raw (run_id, payload)
                VALUES (%s, %s)
                RETURNING raw_id;
                """,
                (run_id, json.dumps(payload))
            )
            raw_id = cur.fetchone()[0]
        conn.commit()
        return raw_id
    finally:
        conn.close()
