-- ============================================================================
-- PROYECTO: INF-522 - Gestión II (Sistemas de Información y Data Warehousing)
-- CASO: Observatorio Europeo Austral (ESO) & Broker ALeRCE (Chile)
-- ARCHIVO: sql/ddl_estructura.sql
-- DESCRIPCIÓN: DDL de las 4 capas arquitecturales (RAW, STAGING, DW, MART)
--              y tabla de auditoría de procesos ETL en PostgreSQL.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. CREACIÓN DE ESQUEMAS OBLIGATORIOS
-- ----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dw;
CREATE SCHEMA IF NOT EXISTS mart;

-- ----------------------------------------------------------------------------
-- 2. TABLA DE AUDITORÍA Y TOLERANCIA A FALLAS (Control y Gobernanza de Datos)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.etl_audit (
    audit_id SERIAL PRIMARY KEY,
    dag_id VARCHAR(100) NOT NULL,
    run_id VARCHAR(150) NOT NULL,
    fuente VARCHAR(50) NOT NULL,
    filas_leidas INT DEFAULT 0,
    filas_cargadas INT DEFAULT 0,
    porcentaje_nulos NUMERIC(5,2) DEFAULT 0.00,
    duracion_segundos NUMERIC(10,2) DEFAULT 0.00,
    estado VARCHAR(30) NOT NULL, -- 'SUCCESS', 'FAILED', 'RETRYING'
    mensaje_error TEXT,
    fecha_ejecucion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_dag_run ON public.etl_audit(dag_id, run_id);
CREATE INDEX IF NOT EXISTS idx_audit_fecha ON public.etl_audit(fecha_ejecucion);

-- ============================================================================
-- CAPA RAW: Datos crudos inmutables tal como se reciben de las APIs
-- ============================================================================
CREATE TABLE IF NOT EXISTS raw.eso_observations_raw (
    raw_id SERIAL PRIMARY KEY,
    run_id VARCHAR(150),
    payload JSONB NOT NULL,
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw.alerce_objects_raw (
    raw_id SERIAL PRIMARY KEY,
    run_id VARCHAR(150),
    pagina INT,
    payload JSONB NOT NULL,
    fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CAPA STAGING: Datos limpios, normalizados, tipados y desduplicados
-- ============================================================================
CREATE TABLE IF NOT EXISTS staging.stg_eso_observations (
    obs_id VARCHAR(150) PRIMARY KEY,
    facility_name VARCHAR(100),
    instrument_name VARCHAR(100),
    dataproduct_type VARCHAR(50),
    calib_level INT,
    fecha_observacion DATE NOT NULL,
    mjd_obs NUMERIC(12,5),
    tiempo_exposicion_seg NUMERIC(12,3),
    tamano_estimado_kb BIGINT,
    tamano_estimado_mb NUMERIC(12,3),
    ra_grados NUMERIC(10,6),
    dec_grados NUMERIC(10,6),
    banda_declinacion VARCHAR(30),
    hemisferio VARCHAR(20),
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_alerce_objects (
    oid VARCHAR(100) PRIMARY KEY,
    class_name VARCHAR(50),
    classifier_name VARCHAR(50),
    probabilidad_clase NUMERIC(6,4),
    num_detecciones INT,
    fecha_ultima_deteccion DATE NOT NULL,
    lastmjd NUMERIC(12,5),
    ra_grados NUMERIC(10,6),
    dec_grados NUMERIC(10,6),
    banda_declinacion VARCHAR(30),
    hemisferio VARCHAR(20),
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CAPA DW: Modelo Dimensional en Estrella (Star Schema)
-- ============================================================================

-- Dimensión 1: Tiempo (Obligatoria para análisis histórico y cruce)
CREATE TABLE IF NOT EXISTS dw.dim_tiempo (
    fecha_id DATE PRIMARY KEY,
    anio INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    trimestre INT NOT NULL,
    dia_semana VARCHAR(20) NOT NULL,
    es_fin_de_semana BOOLEAN NOT NULL
);

-- Dimensión 2: Instrumento e Instalación en Chile (ESO)
CREATE TABLE IF NOT EXISTS dw.dim_instrumento (
    instrumento_sk SERIAL PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL,
    instrument_name VARCHAR(100) NOT NULL,
    dataproduct_type VARCHAR(50) NOT NULL,
    CONSTRAINT uq_instrumento UNIQUE (facility_name, instrument_name, dataproduct_type)
);

-- Dimensión 3: Banda Espacial de Declinación del Cielo (Cruce Astronómico)
CREATE TABLE IF NOT EXISTS dw.dim_banda_cielo (
    banda_sk SERIAL PRIMARY KEY,
    banda_declinacion VARCHAR(30) UNIQUE NOT NULL,
    hemisferio VARCHAR(20) NOT NULL
);

-- Tabla de Hechos 1: Operaciones y Captura de Observaciones en Chile (ESO)
CREATE TABLE IF NOT EXISTS dw.fact_observaciones_eso (
    obs_id VARCHAR(150) PRIMARY KEY,
    fecha_id DATE NOT NULL REFERENCES dw.dim_tiempo(fecha_id),
    instrumento_sk INT NOT NULL REFERENCES dw.dim_instrumento(instrumento_sk),
    banda_sk INT NOT NULL REFERENCES dw.dim_banda_cielo(banda_sk),
    calib_level INT,
    tiempo_exposicion_seg NUMERIC(12,3),
    tamano_estimado_mb NUMERIC(12,3),
    cargado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_eso_fecha ON dw.fact_observaciones_eso(fecha_id);
CREATE INDEX IF NOT EXISTS idx_fact_eso_inst ON dw.fact_observaciones_eso(instrumento_sk);
CREATE INDEX IF NOT EXISTS idx_fact_eso_banda ON dw.fact_observaciones_eso(banda_sk);

-- Tabla de Hechos 2: Alertas Astronómicas Clasificadas por ALeRCE (Chile)
CREATE TABLE IF NOT EXISTS dw.fact_alertas_alerce (
    oid VARCHAR(100) PRIMARY KEY,
    fecha_id DATE NOT NULL REFERENCES dw.dim_tiempo(fecha_id),
    banda_sk INT NOT NULL REFERENCES dw.dim_banda_cielo(banda_sk),
    class_name VARCHAR(50),
    probabilidad_clase NUMERIC(6,4),
    num_detecciones INT,
    cargado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fact_alerce_fecha ON dw.fact_alertas_alerce(fecha_id);
CREATE INDEX IF NOT EXISTS idx_fact_alerce_banda ON dw.fact_alertas_alerce(banda_sk);
CREATE INDEX IF NOT EXISTS idx_fact_alerce_class ON dw.fact_alertas_alerce(class_name);
