"""
DAG 2: ETL Broker de Alertas Astronómicas ALeRCE (MAS / CMM Chile)
Asignatura: INF-522 - Gestión II
Responsabilidad:
1. Validar disponibilidad de API REST (https://api.alerce.online/ztf/v1/objects).
2. Extraer alertas astronómicas transitorias crudas con paginación controlada.
3. Guardar páginas inmutables en raw.alerce_objects_raw.
4. Transformar datos: conversión MJD a DATE, validación de probabilidades ML, banda 10°.
5. Cargar en staging.stg_alerce_objects y poblar dw.fact_alertas_alerce.
6. Registrar métricas en public.etl_audit (filas leídas/cargadas, % nulos, tiempo, estado).
7. Disparar dag_3_kpi_mart_astronomico sin depender de la finalización de otros DAGs.
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

from src.extract_alerce import validar_api_alerce, extraer_alerce_raw, guardar_alerce_raw, leer_alerce_raw
from src.transform import transformar_alerce
from src.load import cargar_alerce_pipeline
from src.audit import registrar_auditoria
from src.config import ALERCE_API_URL, DEFAULT_MJD_INICIO, DEFAULT_MJD_FIN

def registrar_falla_audit_alerce(context):
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
                VALUES (%s, %s, 'ALeRCE_Broker_Chile_API', 0, 0, 0.0, %s, 'FAILED', %s);
            """
            hook.run(sql, parameters=(dag_id, run_id, duracion, exception))
            return
        except Exception:
            pass

    registrar_auditoria(
        dag_id=dag_id,
        run_id=run_id,
        fuente="ALeRCE_Broker_Chile_API",
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
    "retry_delay": timedelta(seconds=15),
    "execution_timeout": timedelta(minutes=5),
    "on_failure_callback": registrar_falla_audit_alerce,
}

def task_validar_api(**context):
    url = Variable.get("alerce_api_url", default_var=ALERCE_API_URL)
    validar_api_alerce(url=url, timeout=20)
    return True

def task_extraer_y_guardar_raw(**context):
    url = Variable.get("alerce_api_url", default_var=ALERCE_API_URL)
    mjd_inicio = float(Variable.get("alerce_mjd_inicio", default_var=DEFAULT_MJD_INICIO))
    mjd_fin = float(Variable.get("alerce_mjd_fin", default_var=DEFAULT_MJD_FIN))
    run_id = str(context.get("run_id", f"run_{datetime.utcnow().timestamp()}"))
    
    t0 = datetime.now()
    paginas = extraer_alerce_raw(base_url=url, mjd_inicio=mjd_inicio, mjd_fin=mjd_fin, max_paginas=5, page_size=50)
    duracion_ext = round((datetime.now() - t0).total_seconds(), 2)
    
    total_guardadas = guardar_alerce_raw(paginas, run_id)
    context["ti"].xcom_push(key="total_paginas", value=total_guardadas)
    context["ti"].xcom_push(key="run_id", value=run_id)
    context["ti"].xcom_push(key="duracion_ext", value=duracion_ext)
    return total_guardadas

def task_transformar_y_cargar_dw(**context):
    ti = context["ti"]
    run_id = ti.xcom_pull(task_ids="extraer_alerce_raw_task", key="run_id") or str(context.get("run_id"))
    duracion_ext = float(ti.xcom_pull(task_ids="extraer_alerce_raw_task", key="duracion_ext") or 0.0)
    url = Variable.get("alerce_api_url", default_var=ALERCE_API_URL)
    mjd_inicio = float(Variable.get("alerce_mjd_inicio", default_var=DEFAULT_MJD_INICIO))
    mjd_fin = float(Variable.get("alerce_mjd_fin", default_var=DEFAULT_MJD_FIN))
    
    t0 = datetime.now()
    # Leer de capa RAW previamente persistida para reproducibilidad
    paginas = leer_alerce_raw(run_id)
    if not paginas:
        paginas = extraer_alerce_raw(base_url=url, mjd_inicio=mjd_inicio, mjd_fin=mjd_fin, max_paginas=5, page_size=50)
        
    df_limpio, metricas = transformar_alerce(paginas)
    filas_cargadas = cargar_alerce_pipeline(df_limpio)
    duracion_proc = round((datetime.now() - t0).total_seconds(), 2)
    duracion_total = round(duracion_ext + duracion_proc, 2)

    registrar_auditoria(
        dag_id="dag_2_etl_alerce_chile",
        run_id=run_id,
        fuente="ALeRCE_Broker_Chile_API",
        filas_leidas=metricas["filas_leidas"],
        filas_cargadas=filas_cargadas,
        porcentaje_nulos=metricas["porcentaje_nulos"],
        duracion_segundos=duracion_total,
        estado="SUCCESS",
        mensaje_error=None
    )
    return filas_cargadas

with DAG(
    dag_id="dag_2_etl_alerce_chile",
    default_args=default_args,
    description="ETL independiente de alertas astronómicas de ALeRCE (Chile)",
    schedule_interval="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["inf522", "alerce", "chile", "machine_learning"],
) as dag:

    validar_alerce = PythonOperator(
        task_id="validar_api_alerce_task",
        python_callable=task_validar_api,
    )

    extraer_alerce = PythonOperator(
        task_id="extraer_alerce_raw_task",
        python_callable=task_extraer_y_guardar_raw,
    )

    transformar_cargar_alerce = PythonOperator(
        task_id="transformar_y_cargar_alerce_task",
        python_callable=task_transformar_y_cargar_dw,
    )

    disparar_mart = TriggerDagRunOperator(
        task_id="trigger_dag_mart",
        trigger_dag_id="dag_3_kpi_mart_astronomico",
        wait_for_completion=False,
        reset_dag_run=True,
    )

    validar_alerce >> extraer_alerce >> transformar_cargar_alerce >> disparar_mart
