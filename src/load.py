"""
Módulo de Carga e Idempotencia (Requisito Sección 4 Pauta INF-522).
Carga datos limpios a la capa STAGING y puebla el modelo dimensional en estrella en DW.
Garantiza idempotencia total mediante INSERT ... ON CONFLICT (DO UPDATE / DO NOTHING).
"""

from datetime import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from src.config import get_connection

DIAS_SEMANA_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles",
    3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
}

def poblar_dim_tiempo(conn, fechas_unicas: set):
    """
    Puebla la dimensión de tiempo con atributos ricos de calendario.
    Idempotente: ON CONFLICT (fecha_id) DO NOTHING.
    """
    if not fechas_unicas:
        return
    
    filas = []
    for f in fechas_unicas:
        if isinstance(f, str):
            f_dt = datetime.strptime(f, "%Y-%m-%d").date()
        else:
            f_dt = f
        
        anio = f_dt.year
        mes = f_dt.month
        dia = f_dt.day
        trimestre = (mes - 1) // 3 + 1
        dia_sem = DIAS_SEMANA_ES[f_dt.weekday()]
        es_fds = f_dt.weekday() in (5, 6)
        filas.append((f_dt, anio, mes, dia, trimestre, dia_sem, es_fds))

    query = """
        INSERT INTO dw.dim_tiempo (fecha_id, anio, mes, dia, trimestre, dia_semana, es_fin_de_semana)
        VALUES %s
        ON CONFLICT (fecha_id) DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_values(cur, query, filas)

def poblar_dim_banda_cielo(conn, bandas_unicas: set):
    """
    Puebla la dimensión espacial de franjas celestes de 10 grados.
    Idempotente: ON CONFLICT (banda_declinacion) DO NOTHING.
    """
    if not bandas_unicas:
        return
    
    filas = []
    for b in bandas_unicas:
        # Calcular hemisferio según el rango
        hem = "Austral" if "-" in b or b.startswith("-") else "Boreal"
        filas.append((b, hem))

    query = """
        INSERT INTO dw.dim_banda_cielo (banda_declinacion, hemisferio)
        VALUES %s
        ON CONFLICT (banda_declinacion) DO UPDATE SET hemisferio = EXCLUDED.hemisferio;
    """
    with conn.cursor() as cur:
        execute_values(cur, query, filas)

def poblar_dim_instrumento(conn, instrumentos_unicos: set):
    """
    Puebla la dimensión de telescopios e instrumentos de ESO en Chile.
    Idempotente: ON CONFLICT (facility_name, instrument_name, dataproduct_type) DO NOTHING.
    """
    if not instrumentos_unicos:
        return
    
    filas = list(instrumentos_unicos)
    query = """
        INSERT INTO dw.dim_instrumento (facility_name, instrument_name, dataproduct_type)
        VALUES %s
        ON CONFLICT (facility_name, instrument_name, dataproduct_type) DO NOTHING;
    """
    with conn.cursor() as cur:
        execute_values(cur, query, filas)

# ============================================================================
# CARGA PIPELINE 1: ESO SCIENCE ARCHIVE
# ============================================================================
def cargar_eso_pipeline(df: pd.DataFrame) -> int:
    """
    Carga observaciones de ESO a staging.stg_eso_observations y dw.fact_observaciones_eso.
    Retorna la cantidad de filas cargadas exitosamente.
    """
    if df.empty:
        return 0

    conn = get_connection()
    try:
        # 1. Poblar Dimensiones
        fechas = set(df["fecha_observacion"].unique())
        poblar_dim_tiempo(conn, fechas)

        bandas = set(df["banda_declinacion"].unique())
        poblar_dim_banda_cielo(conn, bandas)

        insts = set(zip(df["facility_name"], df["instrument_name"], df["dataproduct_type"]))
        poblar_dim_instrumento(conn, insts)

        # 2. Cargar en Capa Staging (Upsert)
        stg_rows = [
            (
                row["obs_id"], row["facility_name"], row["instrument_name"],
                row["dataproduct_type"], row["calib_level"], row["fecha_observacion"],
                row["mjd_obs"], row["tiempo_exposicion_seg"], row["tamano_estimado_kb"],
                row["tamano_estimado_mb"], row["ra_grados"], row["dec_grados"],
                row["banda_declinacion"], row["hemisferio"]
            )
            for _, row in df.iterrows()
        ]

        stg_query = """
            INSERT INTO staging.stg_eso_observations (
                obs_id, facility_name, instrument_name, dataproduct_type,
                calib_level, fecha_observacion, mjd_obs, tiempo_exposicion_seg,
                tamano_estimado_kb, tamano_estimado_mb, ra_grados, dec_grados,
                banda_declinacion, hemisferio
            ) VALUES %s
            ON CONFLICT (obs_id) DO UPDATE SET
                facility_name = EXCLUDED.facility_name,
                instrument_name = EXCLUDED.instrument_name,
                dataproduct_type = EXCLUDED.dataproduct_type,
                calib_level = EXCLUDED.calib_level,
                fecha_observacion = EXCLUDED.fecha_observacion,
                tiempo_exposicion_seg = EXCLUDED.tiempo_exposicion_seg,
                tamano_estimado_mb = EXCLUDED.tamano_estimado_mb,
                banda_declinacion = EXCLUDED.banda_declinacion,
                hemisferio = EXCLUDED.hemisferio,
                actualizado_en = CURRENT_TIMESTAMP;
        """
        with conn.cursor() as cur:
            execute_values(cur, stg_query, stg_rows)

        # 3. Lookup de Surrogate Keys para DW
        with conn.cursor() as cur:
            cur.execute("SELECT facility_name, instrument_name, dataproduct_type, instrumento_sk FROM dw.dim_instrumento;")
            inst_map = {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}

            cur.execute("SELECT banda_declinacion, banda_sk FROM dw.dim_banda_cielo;")
            banda_map = {r[0]: r[1] for r in cur.fetchall()}

        # 4. Cargar en Capa DW: Fact Observaciones ESO
        fact_rows = []
        for _, row in df.iterrows():
            inst_key = (row["facility_name"], row["instrument_name"], row["dataproduct_type"])
            inst_sk = inst_map.get(inst_key)
            banda_sk = banda_map.get(row["banda_declinacion"])
            
            if inst_sk and banda_sk:
                fact_rows.append((
                    row["obs_id"],
                    row["fecha_observacion"],
                    inst_sk,
                    banda_sk,
                    row["calib_level"],
                    row["tiempo_exposicion_seg"],
                    row["tamano_estimado_mb"]
                ))

        fact_query = """
            INSERT INTO dw.fact_observaciones_eso (
                obs_id, fecha_id, instrumento_sk, banda_sk,
                calib_level, tiempo_exposicion_seg, tamano_estimado_mb
            ) VALUES %s
            ON CONFLICT (obs_id) DO UPDATE SET
                fecha_id = EXCLUDED.fecha_id,
                instrumento_sk = EXCLUDED.instrumento_sk,
                banda_sk = EXCLUDED.banda_sk,
                calib_level = EXCLUDED.calib_level,
                tiempo_exposicion_seg = EXCLUDED.tiempo_exposicion_seg,
                tamano_estimado_mb = EXCLUDED.tamano_estimado_mb;
        """
        with conn.cursor() as cur:
            execute_values(cur, fact_query, fact_rows)

        conn.commit()
        return len(fact_rows)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# ============================================================================
# CARGA PIPELINE 2: ALERCE BROKER CHILE
# ============================================================================
def cargar_alerce_pipeline(df: pd.DataFrame) -> int:
    """
    Carga alertas de ALeRCE a staging.stg_alerce_objects y dw.fact_alertas_alerce.
    Retorna la cantidad de filas cargadas exitosamente.
    """
    if df.empty:
        return 0

    conn = get_connection()
    try:
        # 1. Poblar Dimensiones
        fechas = set(df["fecha_ultima_deteccion"].unique())
        poblar_dim_tiempo(conn, fechas)

        bandas = set(df["banda_declinacion"].unique())
        poblar_dim_banda_cielo(conn, bandas)

        # 2. Cargar en Capa Staging (Upsert)
        stg_rows = [
            (
                row["oid"], row["class_name"], row["classifier_name"],
                row["probabilidad_clase"], row["num_detecciones"],
                row["fecha_ultima_deteccion"], row["lastmjd"], row["ra_grados"],
                row["dec_grados"], row["banda_declinacion"], row["hemisferio"]
            )
            for _, row in df.iterrows()
        ]

        stg_query = """
            INSERT INTO staging.stg_alerce_objects (
                oid, class_name, classifier_name, probabilidad_clase,
                num_detecciones, fecha_ultima_deteccion, lastmjd,
                ra_grados, dec_grados, banda_declinacion, hemisferio
            ) VALUES %s
            ON CONFLICT (oid) DO UPDATE SET
                class_name = EXCLUDED.class_name,
                probabilidad_clase = EXCLUDED.probabilidad_clase,
                num_detecciones = EXCLUDED.num_detecciones,
                fecha_ultima_deteccion = EXCLUDED.fecha_ultima_deteccion,
                banda_declinacion = EXCLUDED.banda_declinacion,
                hemisferio = EXCLUDED.hemisferio,
                actualizado_en = CURRENT_TIMESTAMP;
        """
        with conn.cursor() as cur:
            execute_values(cur, stg_query, stg_rows)

        # 3. Lookup de Surrogate Keys para DW
        with conn.cursor() as cur:
            cur.execute("SELECT banda_declinacion, banda_sk FROM dw.dim_banda_cielo;")
            banda_map = {r[0]: r[1] for r in cur.fetchall()}

        # 4. Cargar en Capa DW: Fact Alertas ALeRCE
        fact_rows = []
        for _, row in df.iterrows():
            banda_sk = banda_map.get(row["banda_declinacion"])
            if banda_sk:
                fact_rows.append((
                    row["oid"],
                    row["fecha_ultima_deteccion"],
                    banda_sk,
                    row["class_name"],
                    row["probabilidad_clase"],
                    row["num_detecciones"]
                ))

        fact_query = """
            INSERT INTO dw.fact_alertas_alerce (
                oid, fecha_id, banda_sk, class_name,
                probabilidad_clase, num_detecciones
            ) VALUES %s
            ON CONFLICT (oid) DO UPDATE SET
                fecha_id = EXCLUDED.fecha_id,
                banda_sk = EXCLUDED.banda_sk,
                class_name = EXCLUDED.class_name,
                probabilidad_clase = EXCLUDED.probabilidad_clase,
                num_detecciones = EXCLUDED.num_detecciones;
        """
        with conn.cursor() as cur:
            execute_values(cur, fact_query, fact_rows)

        conn.commit()
        return len(fact_rows)
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
