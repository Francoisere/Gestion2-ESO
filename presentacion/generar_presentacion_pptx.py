"""
Generador de Presentación de Apoyo PPTX (12 Láminas Profesionales)
Asignatura: INF-522 - Gestión II (Sistemas de Información y Data Warehousing)
Universidad Católica del Maule - Ingeniería Civil Informática
Integrantes: Franco Vela, Renato Muñoz, Benjamín Cáceres, Vicente Vega
Docentes: Natalia Morales | Sebastián Farías
Fecha de Presentación: 12 de Noviembre del 2026
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def crear_presentacion():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Paleta de colores astronómica y moderna
    NAVY = RGBColor(15, 23, 42)          # Slate 900 (Fondo principal)
    DARK_CARD = RGBColor(30, 41, 59)     # Slate 800 (Tarjetas de contenido)
    BORDER_COLOR = RGBColor(51, 65, 85)  # Slate 700 (Bordes sutiles)
    CYAN = RGBColor(56, 189, 248)        # Sky 400 (Acentos y categorías)
    GOLD = RGBColor(251, 191, 36)        # Amber 400 (Destacados y metas)
    WHITE = RGBColor(255, 255, 255)      # Blanco puro para títulos
    TEXT_LIGHT = RGBColor(226, 232, 240) # Slate 200 (Texto de lectura)
    TEXT_MUTED = RGBColor(148, 163, 184) # Slate 400 (Detalles secundarios)
    GREEN = RGBColor(74, 222, 128)       # Emerald 400 (Éxito / Idempotencia)

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="INF-522: GESTIÓN II | SISTEMAS DE INFORMACIÓN Y DATA WAREHOUSING"):
        # Categoría superior
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN

        # Título principal
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(23)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

    def add_card(slide, left, top, width, height, title, items, badge=""):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = DARK_CARD
        shape.line.color.rgb = BORDER_COLOR
        shape.line.width = Pt(1.2)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.22)
        tf.margin_bottom = Inches(0.22)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.space_after = Pt(6)

        if badge:
            p_badge = tf.add_paragraph()
            p_badge.text = f"[{badge}]"
            p_badge.font.size = Pt(10)
            p_badge.font.bold = True
            p_badge.font.color.rgb = CYAN
            p_badge.space_after = Pt(8)

        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = TEXT_LIGHT
            p_item.space_after = Pt(5)

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # LÁMINA 1: Portada
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY)

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.3), Inches(5.0))
    tf1 = tb.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "UNIVERSIDAD CATÓLICA DEL MAULE • FACULTAD DE CIENCIAS DE LA INGENIERÍA"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = CYAN
    p0.space_after = Pt(15)

    p1 = tf1.add_paragraph()
    p1.text = "Pipeline ETL y Data Warehouse Astronómico en Chile"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Cruce Analítico de Datos Abiertos: ESO Science Archive TAP vs. ALeRCE Alert Broker"
    p2.font.size = Pt(18)
    p2.font.color.rgb = GOLD
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "Asignatura: INF-522 – Gestión II (Sistemas de Información y Data Warehousing)\n" \
              "Docentes: Natalia Morales | Sebastián Farías\n" \
              "Integrantes: Franco Vela, Renato Muñoz, Benjamín Cáceres, Vicente Vega\n" \
              "Fecha de Presentación: 12 de Noviembre del 2026 | Repositorio: github.com/Francoisere/Gestion2-ESO"
    p3.font.size = Pt(12)
    p3.font.color.rgb = TEXT_LIGHT

    set_notes(s1, "Buenos días profesores y compañeros. Hoy presentamos nuestro proyecto de Data Warehousing para INF-522, enfocado en el sector astronómico en Chile. Integramos dos fuentes de datos abiertas generadas en territorio nacional: los telescopios de ESO y el broker chileno ALeRCE, orquestados en Apache Airflow bajo PostgreSQL.")

    # =========================================================================
    # LÁMINA 2: Problema y Contexto de Gestión
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, NAVY)
    add_header(s2, "1. Contexto Astronómico Nacional y Problema de Gestión")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "El Desafío Operacional en Chile",
             [
                 "Chile alberga más del 50% de la capacidad de observación astronómica terrestre mundial en el Desierto de Atacama.",
                 "Altísimo costo operacional: una noche en un telescopio de clase mundial (VLT o ALMA) cuesta miles de dólares.",
                 "Sobredemanda científica: los telescopios reciben muchas más solicitudes de tiempo de observación de las que pueden conceder.",
                 "Flujo masivo de transitorios: el cielo produce millones de eventos efímeros por noche (supernovas, estrellas variables, quásares)."
             ],
             "POTENCIA ASTRONÓMICA")

    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Preguntas de Negocio y Decisión",
             [
                 "¿Se están aprovechando productivamente las horas nocturnas efectivas por telescopio e instrumento?",
                 "¿Qué volumen de datos diario generan los observatorios y cómo impacta en las redes e infraestructura de almacenamiento?",
                 "¿Qué tasa de calibración avanzada (nivel de ciencia utilizable) se entrega a la comunidad científica?",
                 "¿Tiene el broker nacional la certeza suficiente en sus modelos de Machine Learning para guiar telescopios de gran envergadura?",
                 "¿Existe coincidencia espacial y temporal entre las alertas transitorias detectadas y el tiempo de exposición de los telescopios en Chile?"
             ],
             "OBJETIVOS ESTRATÉGICOS")

    set_notes(s2, "El problema de gestión surge porque los telescopios en Chile tienen un costo de operación altísimo y una demanda sobreexcedida. Por otro lado, brokers como ALeRCE detectan eventos transitorios efímeros en cuestión de segundos. El Data Warehouse permite medir si estamos respondiendo con tiempo de telescopio a las alertas que se producen en el cielo visible desde Chile.")

    # =========================================================================
    # LÁMINA 3: Selección y Justificación de las 2 APIs Públicas
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, NAVY)
    add_header(s3, "2. Fuentes Seleccionadas y Justificación Territorial")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "API 1: ESO Science Archive (TAP Service)",
             [
                 "Justificación territorial: El 100% de telescopios de ESO opera en Chile bajo tratados internacionales: Paranal (VLT), La Silla (3.6m/HARPS) y Chajnantor (ALMA/APEX).",
                 "Protocolo IVOA TAP: Endpoint síncrono (https://archive.eso.org/tap_obs/sync) con consultas en lenguaje ADQL sobre la tabla ivoa.ObsCore.",
                 "Acceso abierto: Formato directo JSON (FORMAT=json) sin requerir tokens ni autenticación privada.",
                 "Atributos clave: obs_id, facility_name, instrument_name, calib_level, t_min (MJD), t_exptime, access_estsize, s_ra, s_dec.",
                 "Volumen: Consulta acotada a TOP 1000 observaciones recientes."
             ],
             "TELESCOPIOS EN CHILE")

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "API 2: ALeRCE Broker API (CMM / MAS / UdeC)",
             [
                 "Justificación territorial: Infraestructura nacional desarrollada por la U. de Chile (CMM), Instituto Milenio de Astrofísica (MAS), UdeC y Fundación Data Observatory.",
                 "Protocolo REST JSON: Endpoint público (/ztf/v1/objects) sin clave, con soporte de paginación y ordenamiento por fecha (lastmjd DESC).",
                 "Machine Learning chileno: Clasifica millones de alertas en tiempo real mediante modelos de aprendizaje automático (lc_classifier, stamp_classifier).",
                 "Atributos clave: oid, class, classifier, probability, ndet, lastmjd (MJD), meanra, meandec.",
                 "Volumen: 5 páginas de 50 objetos (hasta 250 alertas por corrida)."
             ],
             "INTELIGENCIA ARTIFICIAL CHILENA")

    set_notes(s3, "Ambas fuentes cumplen el 100% de los requisitos de la rúbrica: son datos abiertos generados u operados en territorio nacional, obtenidos por código sin descarga manual y sin requerir tokens. ESO nos da la actividad de los telescopios y ALeRCE nos da la clasificación por Machine Learning de eventos astronómicos.")

    # =========================================================================
    # LÁMINA 4: Campos de Cruce y Reglas de Transformación
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, NAVY)
    add_header(s4, "3. Dimensiones de Cruce y Limpieza de Datos")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Reglas de Cruce Espacio-Temporal",
             [
                 "Cruce Temporal (dw.dim_tiempo):",
                 "  • Ambas APIs reportan el tiempo en Modified Julian Date (MJD): t_min en ESO y lastmjd en ALeRCE.",
                 "  • Regla: Fecha = 1858-11-17 + MJD (días). Ambas convergen al tipo DATE estándar (fecha_id: YYYY-MM-DD).",
                 "Cruce Espacial (dw.dim_banda_cielo):",
                 "  • ESO entrega coordenadas s_dec y ALeRCE entrega meandec (ambas en grados de declinación).",
                 "  • Regla: Discretización matemática en franjas regulares de 10°: [floor(dec/10)*10 a floor(dec/10)*10 + 10].",
                 "  • Permite contrastar dónde apuntaron los telescopios frente a dónde ocurrieron las alertas astronómicas."
             ],
             "INTEGRACIÓN EXACTA")

    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "6 Transformaciones Implementadas (Python)",
             [
                 "1. Conversión de fechas: Aplanamiento JSON y conversión estricta MJD a DATE.",
                 "2. Renombrado y casteo tipado: Normalización de nombres de columnas y conversión numérica segura.",
                 "3. Imputación y filtros de calidad: Validación de coordenadas (ra in [0,360], dec in [-90,90]), tiempos de exposición > 0 e imputación de nulos no críticos.",
                 "4. Normalización textual: strip(), eliminación de caracteres residuales y mayúsculas.",
                 "5. Campos calculados: Tamaño en MB (KB/1024), asignación de banda_declinacion y hemisferio (Austral / Boreal).",
                 "6. Deduplicación de claves: drop_duplicates por obs_id en ESO y por oid en ALeRCE."
             ],
             "ETL PYTHON")

    set_notes(s4, "Para resolver la heterogeneidad de las APIs, construimos dos cruces dimensionales: el temporal, convirtiendo Modified Julian Date a fecha calendario estándar, y el espacial, discretizando la declinación en franjas de 10 grados. En transform.py aplicamos 6 transformaciones sistemáticas de depuración y tipado estricto.")

    # =========================================================================
    # LÁMINA 5: Arquitectura de 4 Capas en PostgreSQL
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, NAVY)
    add_header(s5, "4. Arquitectura de 4 Capas en PostgreSQL")

    w_col = Inches(2.7)
    gap = Inches(0.3)

    add_card(s5, Inches(0.8), Inches(1.8), w_col, Inches(5.1),
             "1. Capa RAW",
             [
                 "Esquema: raw.",
                 "raw.eso_observations_raw y raw.alerce_objects_raw.",
                 "Almacena payloads JSONB crudos e inmutables tal como llegan del HTTP.",
                 "Permite trazabilidad forense y reprocesamiento sin reconsultar las APIs externas.",
                 "Mantiene fecha_extraccion y run_id."
             ],
             "INMUTABILIDAD")

    add_card(s5, Inches(0.8) + (w_col + gap), Inches(1.8), w_col, Inches(5.1),
             "2. Capa STAGING",
             [
                 "Esquema: staging.",
                 "stg_eso_observations y stg_alerce_objects.",
                 "Tablas relacionales tipadas, depuradas y normalizadas.",
                 "Filtros de calidad aplicados y campos calculados generados.",
                 "Llaves de deduplicación: obs_id y oid."
             ],
             "LIMPIEZA Y TIPADO")

    add_card(s5, Inches(0.8) + (w_col + gap)*2, Inches(1.8), w_col, Inches(5.1),
             "3. Capa DW (Estrella)",
             [
                 "Esquema: dw.",
                 "Modelo dimensional en estrella optimizado para consultas analíticas.",
                 "3 Dimensiones compartidas:",
                 "  • dim_tiempo",
                 "  • dim_instrumento",
                 "  • dim_banda_cielo",
                 "2 Tablas de Hechos:",
                 "  • fact_observaciones_eso",
                 "  • fact_alertas_alerce."
             ],
             "MODELO DIMENSIONAL")

    add_card(s5, Inches(0.8) + (w_col + gap)*3, Inches(1.8), w_col, Inches(5.1),
             "4. Capa MART",
             [
                 "Esquema: mart.",
                 "5 Tablas de Indicadores de gestión materializados:",
                 "  • kpi_horas_efectivas",
                 "  • kpi_volumen_diario",
                 "  • kpi_tasa_calibracion",
                 "  • kpi_confianza_alertas",
                 "  • kpi_cobertura_cielo",
                 "Alimentan dashboards y reportes directivos."
             ],
             "BUSINESS INTELLIGENCE")

    set_notes(s5, "Diseñamos la base de datos PostgreSQL dw_astronomia organizada en 4 capas estrictas según la pauta: RAW inmutable en JSONB, STAGING relacional tipada, DW bajo modelo estrella con 3 dimensiones y 2 hechos, y MART con 5 tablas de indicadores agregados, todo auditado en public.etl_audit.")

    # =========================================================================
    # LÁMINA 6: Diseño de los 3 DAGs en Apache Airflow
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, NAVY)
    add_header(s6, "5. Diseño y Orquestación en Apache Airflow")

    w3 = Inches(3.7)
    g3 = Inches(0.3)

    add_card(s6, Inches(0.8), Inches(1.8), w3, Inches(5.1),
             "DAG 1: ETL ESO Science Archive",
             [
                 "ID: dag_1_etl_eso_archive",
                 "Frecuencia: @daily (02:00 UTC)",
                 "Tareas secuenciales:",
                 "  1. validar_api_eso_task",
                 "  2. extraer_eso_raw_task",
                 "  3. transformar_y_cargar_eso_task",
                 "  4. trigger_dag_mart",
                 "Carga observaciones científicas y sincroniza hechos de ESO en el DW."
             ],
             "DAG INDEPENDIENTE")

    add_card(s6, Inches(0.8) + (w3 + g3), Inches(1.8), w3, Inches(5.1),
             "DAG 2: ETL ALeRCE Broker Chile",
             [
                 "ID: dag_2_etl_alerce_chile",
                 "Frecuencia: @daily (02:00 UTC)",
                 "Tareas secuenciales:",
                 "  1. validar_api_alerce_task",
                 "  2. extraer_alerce_raw_task",
                 "  3. transformar_y_cargar_alerce_task",
                 "  4. trigger_dag_mart",
                 "Extrae alertas por paginación y puebla fact_alertas_alerce."
             ],
             "DAG INDEPENDIENTE")

    add_card(s6, Inches(0.8) + (w3 + g3)*2, Inches(1.8), w3, Inches(5.1),
             "DAG 3: KPIs Capa MART",
             [
                 "ID: dag_3_kpi_mart_astronomico",
                 "Frecuencia: Event-Driven y 03:00 UTC",
                 "Disparado por TriggerDagRunOperator al finalizar DAG 1 o DAG 2.",
                 "Ejecuta kpis_mart.sql sobre el DW.",
                 "Principio de Aislamiento: Calcula los KPIs con los datos disponibles sin bloquearse si un ETL falló."
             ],
             "EVENT-DRIVEN / CALCULO")

    set_notes(s6, "Los DAGs están completamente desacoplados. DAG 1 y DAG 2 operan de forma independiente para evitar puntos únicos de fallo. Ambos gatillan al DAG 3 mediante TriggerDagRunOperator, el cual recalcula los indicadores sobre los datos disponibles en el DW de forma tolerante a fallas.")

    # =========================================================================
    # LÁMINA 7: Tolerancia a Fallas y Protocolo de Demostración en Vivo
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, NAVY)
    add_header(s7, "6. Tolerancia a Fallas y Demostración en Vivo (8 min)")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Mecanismos de Resiliencia Implementados",
             [
                 "Validación Previa: Comprueba que el servicio responda antes de extraer; un error HTTP 404/500 detiene la tarea tempranamente evitando corrupción en el DW.",
                 "Política de Reintentos Automáticos: retries=2, retry_delay=15s y execution_timeout=5m.",
                 "Callback de Falla Obligatorio (on_failure_callback): Si la tarea agota sus reintentos, invoca automáticamente registrar_falla_audit().",
                 "Auditoría Centralizada (public.etl_audit): Registra dag_id, run_id, estado='FAILED', duración y mensaje de excepción exacto.",
                 "Carga Idempotente: ON CONFLICT DO UPDATE evita duplicación ante reintentos o recargas manuales."
             ],
             "ROBUSTEZ OPERACIONAL")

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Protocolo para la Exposición en Vivo",
             [
                 "Paso 1: En Airflow (Admin -> Variables), cambiar temporalmente eso_api_url a una URL rota (.../url_rota_demo).",
                 "Paso 2: Disparar dag_1_etl_eso_archive y mostrar la tarea en amarillo (up_for_retry), reintentando 2 veces cada 15s hasta pasar a rojo (failed).",
                 "Paso 3: Consultar public.etl_audit en PostgreSQL para evidenciar el registro automático FAILED con el error HTTP 404.",
                 "Paso 4: Demostrar aislamiento: dag_2_etl_alerce y dag_3_kpi_mart terminan en verde (success) sin colapsar.",
                 "Paso 5: Restaurar URL válida, hacer Clear Task y mostrar la recuperación exitosa e idempotente."
             ],
             "DEMO EN VIVO AIRFLOW")

    set_notes(s7, "Para la demostración de 8 minutos exigida por la pauta, simulamos una caída controlada modificando la variable de URL en Airflow. Se aprecia el reintento automático, el marcado en failed, el registro en etl_audit y, lo más importante, el aislamiento total: el broker ALeRCE y los KPIs siguen operando con éxito.")

    # =========================================================================
    # LÁMINA 8: Modelo Dimensional de Datos (Star Schema)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, NAVY)
    add_header(s8, "7. Modelo de Datos Dimensional (Star Schema)")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Tablas de Hechos (Facts Granulares)",
             [
                 "dw.fact_observaciones_eso (Granularidad: Observación Científica):",
                 "  • PK: obs_id VARCHAR(150)",
                 "  • FKs: fecha_id -> dim_tiempo, instrumento_sk -> dim_instrumento, banda_sk -> dim_banda_cielo",
                 "  • Métricas: tiempo_exposicion_seg NUMERIC(12,3), tamano_estimado_mb NUMERIC(12,3), calib_level INT.",
                 "dw.fact_alertas_alerce (Granularidad: Objeto Astronómico):",
                 "  • PK: oid VARCHAR(100)",
                 "  • FKs: fecha_id -> dim_tiempo, banda_sk -> dim_banda_cielo",
                 "  • Métricas/Atributos: probabilidad_clase NUMERIC(6,4), num_detecciones INT, class_name VARCHAR(50)."
             ],
             "HECHOS DEL NEGOCIO")

    add_card(s8, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Dimensiones Compartidas (Conformed)",
             [
                 "dw.dim_tiempo (Dimensión Temporal):",
                 "  • PK: fecha_id DATE (YYYY-MM-DD)",
                 "  • Atributos: anio, mes, dia, trimestre, dia_semana, es_fin_de_semana.",
                 "dw.dim_instrumento (Dimensión Instrumental):",
                 "  • PK: instrumento_sk SERIAL",
                 "  • Atributos: facility_name, instrument_name, dataproduct_type.",
                 "dw.dim_banda_cielo (Dimensión Espacial de Cruce):",
                 "  • PK: banda_sk SERIAL",
                 "  • Atributos: banda_declinacion VARCHAR(30) (franjas de 10°), hemisferio (Austral / Boreal).",
                 "Idempotencia: ON CONFLICT DO UPDATE en hechos y DO NOTHING en dimensiones."
             ],
             "DIMENSIONES COMUNES")

    set_notes(s8, "El esquema dimensional consta de dos tablas de hechos conectadas a dimensiones compartidas: dim_tiempo y dim_banda_cielo conectan tanto a ESO como a ALeRCE, habilitando el cruce analítico multi-fuente. Las dimensiones se cargan con ON CONFLICT para asegurar idempotencia matemática total.")

    # =========================================================================
    # LÁMINA 9: Los 5 Indicadores de Gestión en Capa MART
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, NAVY)
    add_header(s9, "8. Definición de los 5 Indicadores en Capa MART")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4),
             "KPI 1: Horas Efectivas de Exposición Diaria",
             [
                 "Objetivo: Medir el aprovechamiento nocturno de telescopios en Chile.",
                 "Fórmula: SUM(tiempo_exposicion_seg) / 3600 agrupado por instalación y fecha.",
                 "Meta / Umbral: >= 8.0 horas conjuntas por noche por instalación."
             ],
             "EFICIENCIA OPERACIONAL")

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.4),
             "KPI 2: Volumen Diario Generado (GB/día)",
             [
                 "Objetivo: Dimensionar tráfico de red y almacenamiento digital requerido.",
                 "Fórmula: SUM(tamano_estimado_mb) / 1024 por día.",
                 "Meta / Umbral: Alerta preventiva si supera 500 GB/día."
             ],
             "CAPACIDAD Y ALMACENAMIENTO")

    add_card(s9, Inches(0.8), Inches(4.5), Inches(3.7), Inches(2.4),
             "KPI 3: Tasa Calibración",
             [
                 "Objetivo: Calidad de datos científicos entregados a astrónomos.",
                 "Fórmula: COUNT(calib_level >= 2) / COUNT(*) * 100.",
                 "Meta: >= 75% datos listos para ciencia."
             ],
             "CALIDAD DE DATOS")

    add_card(s9, Inches(4.8), Inches(4.5), Inches(3.7), Inches(2.4),
             "KPI 4: Confianza ALeRCE",
             [
                 "Objetivo: Certeza del clasificador Machine Learning de ALeRCE.",
                 "Fórmula: COUNT(prob >= 0.70) / COUNT(*) * 100.",
                 "Meta: >= 60% alertas con alta certeza."
             ],
             "INTELIGENCIA ARTIFICIAL")

    add_card(s9, Inches(8.8), Inches(4.5), Inches(3.7), Inches(2.4),
             "KPI 5: Cobertura Cielo",
             [
                 "Objetivo: Déficit de seguimiento de telescopios frente a alertas.",
                 "Fórmula: Minutos exposición ESO / Alertas ALeRCE en misma banda y fecha.",
                 "Meta: >= 5.0 min/alerta en Austral."
             ],
             "INDICADOR DE CRUCE")

    set_notes(s9, "Diseñamos 5 indicadores materializados en el esquema mart: miden eficiencia en horas efectivas, volumen en gigabytes, tasa de datos calibrados, certeza de los modelos de Machine Learning y la cobertura de seguimiento cruzada entre telescopios y alertas.")

    # =========================================================================
    # LÁMINA 10: Resultados y Hallazgos Analíticos Reales
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, NAVY)
    add_header(s10, "9. Resultados Reales y Hallazgos Analíticos")

    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Hallazgos en Telescopios ESO (Chile)",
             [
                 "Horas Efectivas (KPI 1): En la ventana evaluada, la mayor captura diaria la lideró JAO (ALMA) con 4.45 hrs el 02-11-2026, seguido de VLT con 1.96 hrs. Ninguna instalación individual superó las 8h de exposición continua sin calibraciones intermedias.",
                 "Volumen Digital (KPI 2): Se mantuvo en niveles normales (<= 500 GB/día), alcanzando un pico de 0.515 GB (22 archivos) el 01-11-2026.",
                 "Calidad Científica (KPI 3): 100.0% de las observaciones consolidadas en el DW alcanzaron nivel de calibración científica avanzada (calib_level >= 2) para JAO, ESO-3.6 y VLT."
             ],
             "OBSERVATORIOS")

    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Hallazgos en ALeRCE y Cruce Espacial",
             [
                 "Certeza ML (KPI 4): En alertas tempranas, la probabilidad se dispersa entre múltiples clases (QSO 21.4%, AGN 14.3%, Periodic-Other 3.9%). Refleja que las alertas recientes requieren más épocas de luz para superar el 70% de confianza.",
                 "Cruce Espacio-Temporal (KPI 5):",
                 "  • Cruce simultáneo efectivo el 04-11-2026 en la banda ecuatorial [0° a 10°]: ESO dedicó 48.89 min para 23 alertas activas (ratio: 2.13 min/alerta).",
                 "  • Déficit de Seguimiento crítico detectado en banda [-10° a 0°] (Austral): se concentraron 112 alertas de ALeRCE con 0 minutos de observación asignada por ESO en esa fecha."
             ],
             "ALERTAS Y CRUCE")

    set_notes(s10, "Los resultados reales arrojaron hallazgos de gran valor: en la capa de cruce, logramos detectar una franja austral con 112 alertas transitorias que tuvieron 0 minutos de seguimiento de ESO, evidenciando exactamente el problema de gestión que nuestro Data Warehouse busca resolver.")

    # =========================================================================
    # LÁMINA 11: Estrategia de Datos, Calidad y Escalabilidad
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, NAVY)
    add_header(s11, "10. Estrategia de Gobernanza, Calidad y Escalabilidad")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.1),
             "Toma de Decisiones y Roles",
             [
                 "Operadores de Observatorio: Monitorean horas efectivas (KPI 1) y reasignan tiempo nocturno ante nubes o fallas técnicas.",
                 "Ingenieros de TI y Redes: Supervisan el volumen en GB (KPI 2) para planificar enlaces de fibra y cuotas de almacenamiento.",
                 "Equipo ALeRCE (CMM/MAS): Analizan la confianza (KPI 4) para reentrenar clasificadores.",
                 "Planificadores de Ciencia: Detectan franjas desatendidas (KPI 5) para priorizar seguimiento ToO (Target of Opportunity)."
             ],
             "STAKEHOLDERS")

    add_card(s11, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.1),
             "Calidad y Auditoría",
             [
                 "Métricas en public.etl_audit:",
                 "  • DAG 1 (ESO): 8.00% de nulos imputados (access_estsize en productos de ALMA en procesamiento).",
                 "  • DAG 2 (ALeRCE): 0.00% de nulos en columnas analíticas.",
                 "  • DAG 3 (Mart): 0.00% nulos.",
                 "Consolidación de granularidad:",
                 "  • ESO: 1.000 productos crudos -> 104 observaciones científicas únicas por obs_id.",
                 "  • ALeRCE: 250 objetos -> 135 alertas únicas desduplicadas."
             ],
             "CALIDAD DE DATOS")

    add_card(s11, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.1),
             "Escalabilidad Vera Rubin",
             [
                 "Próxima era astronómica: Observatorio Vera C. Rubin (LSST) en Cerro Pachón generará 10 millones de alertas por noche.",
                 "Capacidad de Crecimiento:",
                 "  • Nuevas fuentes: DAGs ETL modulares compartiendo dim_tiempo y dim_banda_cielo.",
                 "  • Mayor volumen: Carga incremental por ventana MJD y particionamiento mensual de hechos en PostgreSQL.",
                 "  • Transición a clusters distribuidos (Spark / Kafka) sin rehacer el modelo dimensional."
             ],
             "ESCALABILIDAD")

    set_notes(s11, "Nuestra estrategia de datos define con claridad los roles que usan cada indicador, registra la calidad en etl_audit con un 0% de nulos en ALeRCE y 8% imputado en ESO, y está diseñada para escalar hacia la llegada del Observatorio Vera Rubin en Coquimbo, que multiplicará el volumen por miles.")

    # =========================================================================
    # LÁMINA 12: Lecciones Aprendidas, Conclusiones y Cierre
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, NAVY)
    add_header(s12, "11. Lecciones Aprendidas, Conclusiones y Demostración")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Principales Aprendizajes Técnicos",
             [
                 "Desacoplamiento de DAGs: Aislar la extracción de cada API externa es imprescindible; si un servicio externo cae, el resto del DW debe seguir operando.",
                 "Idempotencia de Extremo a Extremo: Implementar ON CONFLICT DO UPDATE garantiza que reintentos y reprocesamientos no generen duplicados ni inconsistencias.",
                 "Resolución Agnóstica de Rutas: Evitar rutas relativas sensibles al CWD; usar resolución dinámica basada en la ubicación del archivo para que scripts corran igual en Airflow, CLI o Docker.",
                 "Observabilidad Centralizada: La tabla public.etl_audit provee trazabilidad total de filas, nulos, tiempos y estados para el equipo."
             ],
             "APRENDIZAJES CLAVE")

    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "Conclusiones y Demostración en Vivo",
             [
                 "Se implementó con éxito un Data Warehouse en 4 capas cumpliendo el 100% de la pauta de evaluación.",
                 "Se cruzaron datos contemporáneos de telescopios en Chile y alertas de Machine Learning nacional.",
                 "Suite completa y reproducible: Código Python, DDL SQL, DAGs Airflow y Docker Compose sincronizados en GitHub.",
                 "Demostración en Vivo (8 min): Listos para simular la falla controlada, verificar reintentos y responder las preguntas de la comisión.",
                 "Repositorio: https://github.com/Francoisere/Gestion2-ESO"
             ],
             "CIERRE Y PREGUNTAS")

    set_notes(s12, "En conclusión, logramos construir una solución robusta, idempotente y observable que transforma datos crudos de astronomía en decisiones operacionales concretas. Estamos listos para realizar la demostración de falla controlada en vivo y responder las preguntas de la comisión. Muchas gracias.")

    # Guardar presentación
    os.makedirs("presentacion", exist_ok=True)
    out_path = "presentacion/Presentacion_INF522_Gestion_Datos_Astronomicos.pptx"
    prs.save(out_path)
    print(f"[OK] Presentación PowerPoint generada exitosamente en: {out_path}")

if __name__ == "__main__":
    crear_presentacion()
