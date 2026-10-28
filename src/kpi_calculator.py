"""
Módulo de Cálculo de Indicadores de Gestión (Capa MART).
Ejecuta las agregaciones dimensionales en SQL y registra trazabilidad en etl_audit.
"""

import time
import psycopg2
from src.config import get_connection
from src.audit import registrar_auditoria

def ejecutar_kpis_mart(run_id: str = "manual_mart_run") -> dict:
    """
    Lee y ejecuta sql/kpis_mart.sql contra PostgreSQL, actualizando las tablas
    del esquema mart y retornando métricas consolidadas.
    """
    t0 = time.time()
    conn = get_connection()
    resultados = {}
    try:
        with open("sql/kpis_mart.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()

        with conn.cursor() as cur:
            cur.execute(sql_script)
        conn.commit()

        # Medir filas generadas en cada tabla del mart
        with conn.cursor() as cur:
            # Filas leídas desde el DW dimensional (hechos de ESO y ALeRCE)
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM dw.fact_observaciones_eso) + 
                    (SELECT COUNT(*) FROM dw.fact_alertas_alerce);
            """)
            filas_leidas_dw = cur.fetchone()[0]

            tablas = [
                "mart.kpi_horas_efectivas_exposicion",
                "mart.kpi_volumen_datos_diario",
                "mart.kpi_tasa_calibracion_avanzada",
                "mart.kpi_confianza_alertas_alerce",
                "mart.kpi_cobertura_cielo_diaria"
            ]
            total_filas = 0
            for t in tablas:
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                cnt = cur.fetchone()[0]
                resultados[t] = cnt
                total_filas += cnt

        duracion = round(time.time() - t0, 2)
        registrar_auditoria(
            dag_id="dag_3_kpi_mart_astronomico",
            run_id=run_id,
            fuente="dw_star_schema",
            filas_leidas=filas_leidas_dw,
            filas_cargadas=total_filas,
            porcentaje_nulos=0.0,
            duracion_segundos=duracion,
            estado="SUCCESS",
            mensaje_error=None
        )
        resultados["duracion_segundos"] = duracion
        resultados["filas_leidas_dw"] = filas_leidas_dw
        resultados["total_filas_kpi"] = total_filas
        return resultados
    except Exception as e:
        duracion = round(time.time() - t0, 2)
        registrar_auditoria(
            dag_id="dag_3_kpi_mart_astronomico",
            run_id=run_id,
            fuente="dw_star_schema",
            filas_leidas=0,
            filas_cargadas=0,
            porcentaje_nulos=0.0,
            duracion_segundos=duracion,
            estado="FAILED",
            mensaje_error=str(e)[:500]
        )
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
