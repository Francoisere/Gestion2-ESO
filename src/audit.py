"""
Módulo de Auditoría y Control de Procesos ETL (Requisito Sección 5 Pauta INF-522).
Registra ejecuciones exitosas y fallidas en la tabla public.etl_audit.
"""

import psycopg2
from src.config import get_connection

def registrar_auditoria(
    dag_id: str,
    run_id: str,
    fuente: str,
    filas_leidas: int = 0,
    filas_cargadas: int = 0,
    porcentaje_nulos: float = 0.0,
    duracion_segundos: float = 0.0,
    estado: str = "SUCCESS",
    mensaje_error: str = None
):
    """
    Inserta un registro de trazabilidad en public.etl_audit.
    """
    query = """
        INSERT INTO public.etl_audit (
            dag_id, run_id, fuente, filas_leidas, filas_cargadas,
            porcentaje_nulos, duracion_segundos, estado, mensaje_error
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) RETURNING audit_id;
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    dag_id,
                    run_id,
                    fuente,
                    int(filas_leidas),
                    int(filas_cargadas),
                    float(porcentaje_nulos),
                    float(duracion_segundos),
                    estado,
                    mensaje_error
                )
            )
            audit_id = cur.fetchone()[0]
        conn.commit()
        return audit_id
    except Exception as e:
        print(f"[ERROR AUDITORÍA] No se pudo registrar auditoría en etl_audit: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()
