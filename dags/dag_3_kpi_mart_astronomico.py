"""
DAG 3: Cálculo y Refresco de Indicadores de Gestión en Capa MART
Asignatura: INF-522 - Gestión II
Responsabilidad:
1. Ejecutar las consultas agregadas en SQL (sql/kpis_mart.sql) sobre el Data Warehouse dimensional.
2. Actualizar las 5 tablas de indicadores en el esquema mart:
   - mart.kpi_horas_efectivas_exposicion (KPI 1)
   - mart.kpi_volumen_datos_diario (KPI 2)
   - mart.kpi_tasa_calibracion_avanzada (KPI 3)
   - mart.kpi_confianza_alertas_alerce (KPI 4)
   - mart.kpi_cobertura_cielo_diaria (KPI 5 - Cruce ESO vs ALeRCE)
3. Funciona de manera tolerante a fallas: se ejecuta con los datos disponibles sin bloquearse si un ETL falló.
4. Registra métricas de ejecución y rendimiento en public.etl_audit.
"""

import sys
import os
from datetime import datetime, timedelta

# Asegurar disponibilidad de paquetes locales
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
except ImportError:
    PostgresHook = None

from src.kpi_calculator import ejecutar_kpis_mart
from src.audit import registrar_auditoria

def registrar_falla_audit_mart(context):
    dag_id = context["dag"].dag_id
    run_id = str(context.get("run_id", f"fail_{datetime.utcnow().timestamp()}"))
    exception = str(context.get("exception", "Error en cálculo de Mart"))[:500]

    registrar_auditoria(
        dag_id=dag_id,
        run_id=run_id,
        fuente="dw_star_schema",
        filas_leidas=0,
        filas_cargadas=0,
        porcentaje_nulos=0.0,
        duracion_segundos=0.0,
        estado="FAILED",
        mensaje_error=exception
    )

default_args = {
    "owner": "equipo_inf522",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=15),
    "execution_timeout": timedelta(minutes=5),
    "on_failure_callback": registrar_falla_audit_mart,
}

def task_calcular_mart(**context):
    run_id = str(context.get("run_id", f"mart_run_{datetime.utcnow().timestamp()}"))
    res = ejecutar_kpis_mart(run_id=run_id)
    return res

with DAG(
    dag_id="dag_3_kpi_mart_astronomico",
    default_args=default_args,
    description="Cálculo agregado de KPIs de gestión astronómica en esquema MART",
    schedule_interval="0 3 * * *",  # 03:00 UTC diario o disparado por DAG 1 / DAG 2
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["inf522", "kpi", "mart", "analytics"],
) as dag:

    calcular_mart = PythonOperator(
        task_id="calcular_indicadores_mart_task",
        python_callable=task_calcular_mart,
    )

    calcular_mart
