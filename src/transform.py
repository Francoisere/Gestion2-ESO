"""
Módulo de Transformación de Datos (Requisito Sección 3 Pauta INF-522).
Limpia, normaliza, valida calidad y calcula dimensiones de cruce (Temporal y Espacial).
Documenta formalmente 6 transformaciones de datos exigidas por la rúbrica.
"""

from datetime import datetime, timedelta
import math
import pandas as pd
import numpy as np

MJD_BASE_DATE = datetime(1858, 11, 17)

def calcular_banda_declinacion(dec: float) -> str:
    """
    Transformación 5 (Campo Calculado Espacial):
    Discretiza la declinación ecuatorial en franjas regulares de 10 grados celestes.
    Ejemplo: dec = -24.5 -> '-30 a -20' | dec = 5.2 -> '0 a 10'
    Permite cruzar espacialmente observaciones de ESO y alertas de ALeRCE.
    """
    if dec is None or pd.isna(dec):
        return "Banda Desconocida"
    try:
        lower = int(math.floor(float(dec) / 10.0) * 10)
        upper = lower + 10
        return f"{lower} a {upper}"
    except Exception:
        return "Banda Desconocida"

def calcular_hemisferio(dec: float) -> str:
    """Calcula el hemisferio celeste según la declinación."""
    if dec is None or pd.isna(dec):
        return "Desconocido"
    return "Austral" if float(dec) < 0.0 else "Boreal"

def mjd_a_fecha(mjd_val) -> datetime.date:
    """
    Transformación 1 (Conversión de Fechas):
    Convierte Modified Julian Date (MJD) a fecha calendario estándar DATE (YYYY-MM-DD).
    MJD 0 = 1858-11-17.
    """
    if mjd_val is None or pd.isna(mjd_val):
        return None
    try:
        return (MJD_BASE_DATE + timedelta(days=float(mjd_val))).date()
    except Exception:
        return None

# ============================================================================
# TRANSFORMACIÓN DE DATOS ESO SCIENCE ARCHIVE
# ============================================================================
def transformar_eso(raw_payload: dict) -> tuple[pd.DataFrame, dict]:
    """
    Aplica las 6 transformaciones sobre los datos crudos del Observatorio Europeo Austral:
    1. Conversión de fechas MJD -> DATE.
    2. Renombrado y estandarización de columnas.
    3. Tratamiento de nulos, valores atípicos y métricas de calidad.
    4. Normalización de textos (mayúsculas, trim).
    5. Campos calculados (MB, banda de declinación 10°, hemisferio).
    6. Eliminación de registros duplicados.
    """
    metadata = [m.get("name") for m in raw_payload.get("metadata", [])]
    rows = raw_payload.get("data", [])
    
    total_filas_crudas = len(rows)
    if total_filas_crudas == 0:
        return pd.DataFrame(), {"filas_leidas": 0, "filas_limpias": 0, "porcentaje_nulos": 0.0}
    
    df = pd.DataFrame(rows, columns=metadata)
    
    # Métricas previas de nulos
    nulos_totales = df.isna().sum().sum()
    celdas_totales = df.shape[0] * df.shape[1]
    pct_nulos_inicial = round((nulos_totales / celdas_totales) * 100.0, 2) if celdas_totales > 0 else 0.0

    # 1. Renombrado de Columnas
    df = df.rename(columns={
        "t_exptime": "tiempo_exposicion_seg",
        "access_estsize": "tamano_estimado_kb",
        "s_ra": "ra_grados",
        "s_dec": "dec_grados",
        "t_min": "mjd_obs"
    })

    # 2. Conversión de Tipos
    df["obs_id"] = df["obs_id"].astype(str)
    df["facility_name"] = df["facility_name"].fillna("ESO-Chile").astype(str).str.strip()
    df["instrument_name"] = df["instrument_name"].fillna("DESCONOCIDO").astype(str).str.strip().str.upper()
    df["dataproduct_type"] = df["dataproduct_type"].fillna("UNKNOWN").astype(str).str.strip().str.upper()
    df["calib_level"] = pd.to_numeric(df["calib_level"], errors="coerce").fillna(1).astype(int)
    df["mjd_obs"] = pd.to_numeric(df["mjd_obs"], errors="coerce")
    df["tiempo_exposicion_seg"] = pd.to_numeric(df["tiempo_exposicion_seg"], errors="coerce").fillna(0.0)
    df["tamano_estimado_kb"] = pd.to_numeric(df["tamano_estimado_kb"], errors="coerce").fillna(0).astype(int)
    df["ra_grados"] = pd.to_numeric(df["ra_grados"], errors="coerce")
    df["dec_grados"] = pd.to_numeric(df["dec_grados"], errors="coerce")

    # 3. Conversión de MJD a DATE
    df["fecha_observacion"] = df["mjd_obs"].apply(mjd_a_fecha)

    # 4. Tratamiento de Nulos y Valores Atípicos (Filtros de calidad)
    # Excluir fechas nulas, coordenadas corruptas o fuera de rango físico [-90, 90]
    df = df[df["fecha_observacion"].notna()]
    df = df[df["dec_grados"].between(-90.0, 90.0)]
    df = df[df["ra_grados"].between(0.0, 360.0)]
    df = df[df["tiempo_exposicion_seg"] > 0]

    # 5. Creación de Campos Calculados
    df["tamano_estimado_mb"] = (df["tamano_estimado_kb"] / 1024.0).round(3)
    df["banda_declinacion"] = df["dec_grados"].apply(calcular_banda_declinacion)
    df["hemisferio"] = df["dec_grados"].apply(calcular_hemisferio)

    # 6. Eliminación de Duplicados e Idempotencia
    df = df.drop_duplicates(subset=["obs_id"]).copy()

    metricas = {
        "filas_leidas": total_filas_crudas,
        "filas_limpias": len(df),
        "porcentaje_nulos": pct_nulos_inicial
    }
    return df, metricas

# ============================================================================
# TRANSFORMACIÓN DE DATOS ALERCE BROKER (CHILE)
# ============================================================================
def transformar_alerce(paginas_extraidas: list) -> tuple[pd.DataFrame, dict]:
    """
    Aplica las transformaciones sobre las páginas JSON del broker chileno ALeRCE:
    1. Aplanamiento de objetos de alerta.
    2. Conversión de fechas MJD -> DATE (lastmjd).
    3. Renombrado y estandarización de columnas.
    4. Tratamiento de nulos y validación de probabilidades de ML.
    5. Campos calculados (banda de declinación 10°, hemisferio).
    6. Eliminación de alertas duplicadas.
    """
    todos_items = []
    for pag in paginas_extraidas:
        payload = pag.get("payload", {})
        if isinstance(payload, dict):
            items = payload.get("items", [])
            todos_items.extend(items)
        elif isinstance(payload, list):
            todos_items.extend(payload)
            
    total_filas_crudas = len(todos_items)
    if total_filas_crudas == 0:
        return pd.DataFrame(), {"filas_leidas": 0, "filas_limpias": 0, "porcentaje_nulos": 0.0}

    df = pd.DataFrame(todos_items)

    # Métricas de nulos
    nulos_totales = df.isna().sum().sum()
    celdas_totales = df.shape[0] * df.shape[1]
    pct_nulos_inicial = round((nulos_totales / celdas_totales) * 100.0, 2) if celdas_totales > 0 else 0.0

    # 1. Renombrado de Columnas
    df = df.rename(columns={
        "class": "class_name",
        "classifier": "classifier_name",
        "probability": "probabilidad_clase",
        "ndet": "num_detecciones",
        "meanra": "ra_grados",
        "meandec": "dec_grados"
    })

    # Columnas esperadas obligatorias
    for col, default in [
        ("class_name", "Unknown"),
        ("classifier_name", "lc_classifier"),
        ("probabilidad_clase", 0.0),
        ("num_detecciones", 1),
        ("lastmjd", None),
        ("ra_grados", None),
        ("dec_grados", None)
    ]:
        if col not in df.columns:
            df[col] = default

    # 2. Conversión de Tipos
    df["oid"] = df["oid"].astype(str)
    df["class_name"] = df["class_name"].fillna("Unknown").astype(str).str.strip()
    df["classifier_name"] = df["classifier_name"].fillna("lc_classifier").astype(str).str.strip()
    df["probabilidad_clase"] = pd.to_numeric(df["probabilidad_clase"], errors="coerce").fillna(0.0).round(4)
    df["num_detecciones"] = pd.to_numeric(df["num_detecciones"], errors="coerce").fillna(1).astype(int)
    df["lastmjd"] = pd.to_numeric(df["lastmjd"], errors="coerce")
    df["ra_grados"] = pd.to_numeric(df["ra_grados"], errors="coerce")
    df["dec_grados"] = pd.to_numeric(df["dec_grados"], errors="coerce")

    # 3. Conversión de MJD a DATE
    df["fecha_ultima_deteccion"] = df["lastmjd"].apply(mjd_a_fecha)

    # 4. Tratamiento de Nulos y Valores Atípicos
    df = df[df["fecha_ultima_deteccion"].notna()]
    df = df[df["dec_grados"].between(-90.0, 90.0)]
    df = df[df["ra_grados"].between(0.0, 360.0)]
    df = df[df["probabilidad_clase"].between(0.0, 1.0)]

    # 5. Creación de Campos Calculados
    df["banda_declinacion"] = df["dec_grados"].apply(calcular_banda_declinacion)
    df["hemisferio"] = df["dec_grados"].apply(calcular_hemisferio)

    # 6. Eliminación de Duplicados
    df = df.drop_duplicates(subset=["oid"]).copy()

    metricas = {
        "filas_leidas": total_filas_crudas,
        "filas_limpias": len(df),
        "porcentaje_nulos": pct_nulos_inicial
    }
    return df, metricas
