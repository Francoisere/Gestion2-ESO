"""
DAG 1: ETL Observatorio Europeo Austral (ESO Science Archive - Chile)
Asignatura: INF-522 - Gestión II
Responsabilidad:
1. Validar disponibilidad de API TAP (https://archive.eso.org/tap_obs/sync).
2. Extraer observaciones crudas en formato JSON mediante consulta ADQL sobre ivoa.ObsCore.
3. Guardar payload inmutable en raw.eso_observations_raw.
4. Transformar datos: MJD a DATE, normalizar instrumentos, discretizar declinación en franjas de 10°.
5. Cargar en staging.stg_eso_observations y poblar dw.fact_observaciones_eso e indicadores dimensionales.
6. Registrar métricas en public.etl_audit (filas, nulos, duración, estado).
7. Disparar dag_3_kpi_mart_astronomico al finalizar exitosamente.
"""

import sys
import os
from datetime import datetime, timedelta

# Asegurar disponibilidad de paquetes locales
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
except ImportError:
    PostgresHook = None

from src.extract_eso import validar_api_eso, extraer_eso_raw, guardar_eso_raw, leer_eso_raw
from src.transform import transformar_eso
from src.load import cargar_eso_pipeline
from src.audit import registrar_auditoria
from src.config import ESO_API_URL, DEFAULT_MJD_INICIO, DEFAULT_MJD_FIN

def registrar_falla_audit_eso(context):
    """Callback de falla obligatorio (Sección 5 Rúbrica): Registra caídas en public.etl_audit."""
    dag_id = context["dag"].dag_id
    run_id = str(context.get("run_id", f"fail_{datetime.utcnow().timestamp()}"))
    exception = str(context.get("exception", "Error en ejecución"))[:500]
    duracion = 0.0
    try:
        ti = context.get("task_instance")
        if ti and ti.duration:
            duracion = round(float(ti.duration), 2)
    except Exception:
        duracion = 0.0

    if PostgresHook:
        try:
            hook = PostgresHook(postgres_conn_id="postgres_dw")
            sql = """
                INSERT INTO public.etl_audit
                (dag_id, run_id, fuente, filas_leidas, filas_cargadas, porcentaje_nulos, duracion_segundos, estado, mensaje_error)
                VALUES (%s, %s, 'ESO_Science_Archive_TAP', 0, 0, 0.0, %s, 'FAILED', %s);
            """
            hook.run(sql, parameters=(dag_id, run_id, duracion, exception))
            return
        except Exception:
            pass
    
    # Fallback con conexión nativa
    registrar_auditoria(
        dag_id=dag_id,
        run_id=run_id,
        fuente="ESO_Science_Archive_TAP",
        filas_leidas=0,
        filas_cargadas=0,
        porcentaje_nulos=0.0,
        duracion_segundos=duracion,
        estado="FAILED",
        mensaje_error=exception
    )

default_args = {
    "owner": "equipo_inf522",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(seconds=15),  # 15s para demostración ágil en los 8 min de presentación
    "execution_timeout": timedelta(minutes=5),
    "on_failure_callback": registrar_falla_audit_eso,
}

def task_validar_api(**context):
    url = Variable.get("eso_api_url", default_var=ESO_API_URL)
    validar_api_eso(url=url, timeout=20)
    return True

def task_extraer_y_guardar_raw(**context):
    url = Variable.get("eso_api_url", default_var=ESO_API_URL)
    mjd_inicio = float(Variable.get("eso_mjd_inicio", default_var=DEFAULT_MJD_INICIO))
    mjd_fin = float(Variable.get("eso_mjd_fin", default_var=DEFAULT_MJD_FIN))
    run_id = str(context.get("run_id", f"run_{datetime.utcnow().timestamp()}"))
    
    t0 = datetime.now()
    payload = extraer_eso_raw(base_url=url, mjd_inicio=mjd_inicio, mjd_fin=mjd_fin, limite=1000)
    duracion_ext = round((datetime.now() - t0).total_seconds(), 2)
    
    raw_id = guardar_eso_raw(payload, run_id)
    context["ti"].xcom_push(key="raw_id", value=raw_id)
    context["ti"].xcom_push(key="run_id", value=run_id)
    context["ti"].xcom_push(key="duracion_ext", value=duracion_ext)
    return raw_id

def task_transformar_y_cargar_dw(**context):
    ti = context["ti"]
    run_id = ti.xcom_pull(task_ids="extraer_eso_raw_task", key="run_id") or str(context.get("run_id"))
    duracion_ext = float(ti.xcom_pull(task_ids="extraer_eso_raw_task", key="duracion_ext") or 0.0)
    url = Variable.get("eso_api_url", default_var=ESO_API_URL)
    mjd_inicio = float(Variable.get("eso_mjd_inicio", default_var=DEFAULT_MJD_INICIO))
    mjd_fin = float(Variable.get("eso_mjd_fin", default_var=DEFAULT_MJD_FIN))
    
    t0 = datetime.now()
    # Leer de la capa RAW inmutable previamente persistida
    payload = leer_eso_raw(run_id)
    if not payload:
        payload = extraer_eso_raw(base_url=url, mjd_inicio=mjd_inicio, mjd_fin=mjd_fin, limite=1000)
        
    df_limpio, metricas = transformar_eso(payload)
    filas_cargadas = cargar_eso_pipeline(df_limpio)
    duracion_proc = round((datetime.now() - t0).total_seconds(), 2)
    duracion_total = round(duracion_ext + duracion_proc, 2)

    registrar_auditoria(
        dag_id="dag_1_etl_eso_archive",
        run_id=run_id,
        fuente="ESO_Science_Archive_TAP",
        filas_leidas=metricas["filas_leidas"],
        filas_cargadas=filas_cargadas,
        porcentaje_nulos=metricas["porcentaje_nulos"],
        duracion_segundos=duracion_total,
        estado="SUCCESS",
        mensaje_error=None
    )
    return filas_cargadas

with DAG(
    dag_id="dag_1_etl_eso_archive",
    default_args=default_args,
    description="ETL independiente de observaciones astronómicas en Chile (ESO Science Archive)",
    schedule_interval="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["inf522", "eso", "chile", "astronomia"],
) as dag:

    validar_eso = PythonOperator(
        task_id="validar_api_eso_task",
        python_callable=task_validar_api,
    )

    extraer_eso = PythonOperator(
        task_id="extraer_eso_raw_task",
        python_callable=task_extraer_y_guardar_raw,
    )

    transformar_cargar_eso = PythonOperator(
        task_id="transformar_y_cargar_eso_task",
        python_callable=task_transformar_y_cargar_dw,
    )

    disparar_mart = TriggerDagRunOperator(
        task_id="trigger_dag_mart",
        trigger_dag_id="dag_3_kpi_mart_astronomico",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    validar_eso >> extraer_eso >> transformar_cargar_eso >> disparar_mart
