-- ============================================================================
-- PROYECTO: INF-522 - Gestión II (Sistemas de Información y Data Warehousing)
-- CASO: Observatorio Europeo Austral (ESO) & Broker ALeRCE (Chile)
-- ARCHIVO: sql/kpis_mart.sql
-- DESCRIPCIÓN: Consultas de agregación dimensional para la Capa MART.
--              Generación y refresco de los 5 Indicadores de Gestión.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- INDICADOR 1: Horas Efectivas de Exposición Científica Diaria
-- Objetivo: Medir el aprovechamiento productivo del tiempo nocturno en telescopios
--           de ESO en Chile por instalación e instrumento.
-- Meta/Umbral: >= 8.0 horas conjuntas por noche por instalación.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.kpi_horas_efectivas_exposicion;
CREATE TABLE mart.kpi_horas_efectivas_exposicion AS
SELECT 
    t.fecha_id,
    t.anio,
    t.mes,
    t.dia_semana,
    inst.facility_name,
    inst.instrument_name,
    COUNT(f.obs_id) AS total_observaciones,
    ROUND(SUM(f.tiempo_exposicion_seg), 2) AS total_segundos_exposicion,
    ROUND(SUM(f.tiempo_exposicion_seg) / 3600.0, 2) AS horas_efectivas_exposicion,
    CASE 
        WHEN SUM(f.tiempo_exposicion_seg) / 3600.0 >= 8.0 THEN 'CUMPLE META (>= 8h)'
        ELSE 'BAJO META (< 8h)'
    END AS estado_meta
FROM dw.fact_observaciones_eso f
JOIN dw.dim_tiempo t ON f.fecha_id = t.fecha_id
JOIN dw.dim_instrumento inst ON f.instrumento_sk = inst.instrumento_sk
GROUP BY t.fecha_id, t.anio, t.mes, t.dia_semana, inst.facility_name, inst.instrument_name
ORDER BY t.fecha_id DESC, horas_efectivas_exposicion DESC;

-- ----------------------------------------------------------------------------
-- INDICADOR 2: Volumen de Datos Científicos Generados (GB/día)
-- Objetivo: Dimensionar la carga de almacenamiento y transferencia de red desde
--           los observatorios chilenos hacia los centros de datos.
-- Meta/Umbral: Alerta operativa si el volumen supera 500 GB/día.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.kpi_volumen_datos_diario;
CREATE TABLE mart.kpi_volumen_datos_diario AS
SELECT 
    t.fecha_id,
    t.anio,
    t.mes,
    COUNT(f.obs_id) AS cantidad_archivos_generados,
    ROUND(SUM(f.tamano_estimado_mb), 2) AS total_mb_generados,
    ROUND(SUM(f.tamano_estimado_mb) / 1024.0, 3) AS volumen_total_gb,
    ROUND(AVG(f.tamano_estimado_mb), 2) AS promedio_mb_por_observacion,
    CASE 
        WHEN (SUM(f.tamano_estimado_mb) / 1024.0) > 500.0 THEN 'ALERTA: SOBRECARGA (> 500 GB)'
        ELSE 'NORMAL (<= 500 GB)'
    END AS estado_almacenamiento
FROM dw.fact_observaciones_eso f
JOIN dw.dim_tiempo t ON f.fecha_id = t.fecha_id
GROUP BY t.fecha_id, t.anio, t.mes
ORDER BY t.fecha_id DESC;

-- ----------------------------------------------------------------------------
-- INDICADOR 3: Tasa de Productos con Calibración Avanzada (Nivel 2 y 3)
-- Objetivo: Evaluar la calidad de reducción de datos entregados a la comunidad
--           científica internacional y nacional (calib_level >= 2).
-- Meta/Umbral: >= 75% de las observaciones en nivel ciencia (calib_level >= 2).
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.kpi_tasa_calibracion_avanzada;
CREATE TABLE mart.kpi_tasa_calibracion_avanzada AS
SELECT 
    t.anio,
    t.mes,
    inst.facility_name,
    COUNT(f.obs_id) AS total_productos,
    COUNT(CASE WHEN f.calib_level >= 2 THEN 1 END) AS productos_calibrados_ciencia,
    COUNT(CASE WHEN f.calib_level < 2 THEN 1 END) AS productos_datos_crudos,
    ROUND(
        (COUNT(CASE WHEN f.calib_level >= 2 THEN 1 END)::NUMERIC / NULLIF(COUNT(f.obs_id), 0)) * 100.0,
        2
    ) AS porcentaje_calibracion_avanzada,
    CASE 
        WHEN ((COUNT(CASE WHEN f.calib_level >= 2 THEN 1 END)::NUMERIC / NULLIF(COUNT(f.obs_id), 0)) * 100.0) >= 75.0 
            THEN 'EXCELENTE (>= 75%)'
        ELSE 'MEJORABLE (< 75%)'
    END AS evaluacion_calidad
FROM dw.fact_observaciones_eso f
JOIN dw.dim_tiempo t ON f.fecha_id = t.fecha_id
JOIN dw.dim_instrumento inst ON f.instrumento_sk = inst.instrumento_sk
GROUP BY t.anio, t.mes, inst.facility_name
ORDER BY t.anio DESC, t.mes DESC, porcentaje_calibracion_avanzada DESC;

-- ----------------------------------------------------------------------------
-- INDICADOR 4: Índice de Clasificación de Alta Confianza en Alertas (ALeRCE)
-- Objetivo: Medir la certidumbre del clasificador de Machine Learning chileno
--           (lc_classifier) en eventos astronómicos transitorios.
-- Meta/Umbral: >= 60% de alertas con probabilidad de clasificación >= 0.70.
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.kpi_confianza_alertas_alerce;
CREATE TABLE mart.kpi_confianza_alertas_alerce AS
SELECT 
    t.fecha_id,
    f.class_name,
    COUNT(f.oid) AS total_alertas_detectadas,
    COUNT(CASE WHEN f.probabilidad_clase >= 0.70 THEN 1 END) AS alertas_alta_confianza,
    ROUND(AVG(f.probabilidad_clase), 4) AS probabilidad_promedio,
    ROUND(
        (COUNT(CASE WHEN f.probabilidad_clase >= 0.70 THEN 1 END)::NUMERIC / NULLIF(COUNT(f.oid), 0)) * 100.0,
        2
    ) AS tasa_alta_confianza,
    CASE 
        WHEN ((COUNT(CASE WHEN f.probabilidad_clase >= 0.70 THEN 1 END)::NUMERIC / NULLIF(COUNT(f.oid), 0)) * 100.0) >= 60.0 
            THEN 'ALTA CONFIANZA ML (>= 60%)'
        ELSE 'CLASIFICACIÓN INCIERTA (< 60%)'
    END AS dictamen_clasificador
FROM dw.fact_alertas_alerce f
JOIN dw.dim_tiempo t ON f.fecha_id = t.fecha_id
GROUP BY t.fecha_id, f.class_name
ORDER BY t.fecha_id DESC, total_alertas_detectadas DESC;

-- ----------------------------------------------------------------------------
-- INDICADOR 5: Cobertura de Seguimiento en Chile por Banda del Cielo (Cruce ESO vs ALeRCE)
-- Objetivo: Identificar qué franjas de declinación con alta densidad de alertas
--           están siendo cubiertas con tiempo de exposición en telescopios chilenos.
-- Meta/Umbral: >= 5.0 minutos de exposición por alerta en hemisferio austral (dec < 0°).
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS mart.kpi_cobertura_cielo_diaria;
CREATE TABLE mart.kpi_cobertura_cielo_diaria AS
SELECT 
    t.fecha_id,
    b.banda_declinacion,
    b.hemisferio,
    COALESCE(eso.total_obs_eso, 0) AS total_observaciones_eso,
    ROUND(COALESCE(eso.segundos_exposicion, 0) / 60.0, 2) AS minutos_exposicion_eso,
    COALESCE(al.total_alertas_alerce, 0) AS total_alertas_alerce,
    ROUND(
        (COALESCE(eso.segundos_exposicion, 0) / 60.0) / NULLIF(al.total_alertas_alerce, 0), 
        2
    ) AS ratio_minutos_eso_por_alerta,
    CASE 
        WHEN b.hemisferio = 'Austral' AND ((COALESCE(eso.segundos_exposicion, 0) / 60.0) / NULLIF(al.total_alertas_alerce, 0)) >= 5.0 
            THEN 'COBERTURA ÓPTIMA (>= 5 min/alerta)'
        WHEN b.hemisferio = 'Austral' AND al.total_alertas_alerce > 0 AND (eso.total_obs_eso IS NULL OR eso.total_obs_eso = 0)
            THEN 'DÉFICIT SEGUIMIENTO (0 min exposición)'
        ELSE 'COBERTURA MODERADA / BOREAL'
    END AS diagnostico_operacional
FROM dw.dim_tiempo t
CROSS JOIN dw.dim_banda_cielo b
LEFT JOIN (
    SELECT fecha_id, banda_sk, COUNT(obs_id) AS total_obs_eso, SUM(tiempo_exposicion_seg) AS segundos_exposicion
    FROM dw.fact_observaciones_eso
    GROUP BY fecha_id, banda_sk
) eso ON t.fecha_id = eso.fecha_id AND b.banda_sk = eso.banda_sk
LEFT JOIN (
    SELECT fecha_id, banda_sk, COUNT(oid) AS total_alertas_alerce
    FROM dw.fact_alertas_alerce
    GROUP BY fecha_id, banda_sk
) al ON t.fecha_id = al.fecha_id AND b.banda_sk = al.banda_sk
WHERE COALESCE(eso.total_obs_eso, 0) > 0 OR COALESCE(al.total_alertas_alerce, 0) > 0
ORDER BY t.fecha_id DESC, minutos_exposicion_eso DESC;
