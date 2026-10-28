"""
Generador de Presentación de Apoyo PPTX (11 Láminas Profesionales)
Asignatura: INF-522 - Gestión II (Sistemas de Información y Data Warehousing)
Universidad Católica del Maule
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

    # Paleta de colores astronómica / ingeniería
    NAVY = RGBColor(15, 23, 42)      # Slate 900
    DARK_BLUE = RGBColor(30, 41, 59) # Slate 800
    CYAN = RGBColor(14, 165, 233)    # Sky 500
    GOLD = RGBColor(245, 158, 11)    # Amber 500
    WHITE = RGBColor(255, 255, 255)
    GRAY_TEXT = RGBColor(203, 213, 225) # Slate 300
    CARD_BG = RGBColor(30, 41, 59)
    LIGHT_BG = RGBColor(248, 250, 252)
    TEXT_DARK = RGBColor(15, 23, 42)
    BORDER_COLOR = RGBColor(51, 65, 85)

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="INF-522: GESTIÓN II | SISTEMAS DE INFORMACIÓN"):
        # Categoría superior
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
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
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

    def add_card(slide, left, top, width, height, title, items, badge=""):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD_BG
        shape.line.color.rgb = BORDER_COLOR
        shape.line.width = Pt(1.5)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.25)
        tf.margin_bottom = Inches(0.25)

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = GOLD
        p.space_after = Pt(10)

        if badge:
            p_badge = tf.add_paragraph()
            p_badge.text = f"[{badge}]"
            p_badge.font.size = Pt(11)
            p_badge.font.bold = True
            p_badge.font.color.rgb = CYAN
            p_badge.space_after = Pt(8)

        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {item}"
            p_item.font.size = Pt(13)
            p_item.font.color.rgb = GRAY_TEXT
            p_item.space_after = Pt(6)

    # -------------------------------------------------------------------------
    # SLIDE 1: Portada
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY)

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(4.5))
    tf1 = tb.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "UNIVERSIDAD CATÓLICA DEL MAULE"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = CYAN
    p0.space_after = Pt(15)

    p1 = tf1.add_paragraph()
    p1.text = "Ingeniería de Datos y Gestión Operacional Astronómica en Chile"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Pipeline ETL con Apache Airflow, PostgreSQL y Cruce Dimensional ESO Archive vs. ALeRCE Broker"
    p2.font.size = Pt(18)
    p2.font.color.rgb = GOLD
    p2.space_after = Pt(30)

    p3 = tf1.add_paragraph()
    p3.text = "Actividad Curricular: INF-522 - Gestión II (Evaluación 2 - 35%)\nDocentes: Natalia Morales | Sebastián Farías\nEstudiantes: Equipo de Ingeniería Civil Informática"
    p3.font.size = Pt(13)
    p3.font.color.rgb = GRAY_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 2: Contexto y Problema de Gestión
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, NAVY)
    add_header(s2, "1. Contexto Astronómico Nacional y Problema de Gestión")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "Chile: Capital Mundial de la Astronomía",
             [
                 "Concentra más del 50% de la capacidad de observación óptica e infrarroja del planeta.",
                 "Instalaciones de clase mundial: Paranal (VLT), La Silla, ALMA/APEX (Chajnantor).",
                 "Enorme valor científico y costo operacional por hora de observación nocturna."
             ],
             "POTENCIAL NACIONAL")

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "El Desafío de Gestión",
             [
                 "El cielo es dinámico: millones de eventos transitorios (supernovas, asteroides, núcleos activos).",
                 "¿Cómo saber si el tiempo de exposición de los telescopios chilenos está cubriendo las zonas donde ocurren las alertas?",
                 "Problema: Falta de integración de datos entre telescopios de seguimiento y brokers de alertas."
             ],
             "PREGUNTA OPERATIVA")

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "Solución de Inteligencia de Negocios",
             [
                 "Construir un Data Warehouse unificado que cruza datos de telescopios en Chile con alertas del broker ALeRCE.",
                 "Automatizar ingesta continua mediante Apache Airflow.",
                 "Proveer 5 KPIs analíticos para directores de observatorios y científicos."
             ],
             "PROPÓSITO ETL")

    # -------------------------------------------------------------------------
    # SLIDE 3: Fuentes Seleccionadas y Justificación en Chile
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, NAVY)
    add_header(s3, "2. Fuentes Seleccionadas y Justificación en Territorio Chileno")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "API 1: ESO Science Archive (TAP / IVOA)",
             [
                 "Justificación en Chile: El 100% de telescopios de ESO operan en territorio chileno (Región de Antofagasta y Coquimbo) bajo tratados con el Estado.",
                 "Protocolo IVOA TAP: Endpoint síncrono estándar https://archive.eso.org/tap_obs/sync.",
                 "Lenguaje ADQL: Consultas SQL astronómicas sobre ivoa.ObsCore.",
                 "Formato y Acceso: Respuesta JSON sin API keys requeridas para metadatos públicos.",
                 "Métricas clave: t_min (MJD), t_exptime, s_ra, s_dec, access_estsize."
             ],
             "OBSERVATORIO EUROPEO AUSTRAL")

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "API 2: ALeRCE Broker API (Chile)",
             [
                 "Justificación en Chile: Plataforma desarrollada por Universidad de Chile (CMM), Instituto Milenio de Astrofísica (MAS), UdeC y Data Observatory.",
                 "Infraestructura Nacional: Procesa flujos de alertas astronómicas con modelos de Machine Learning (lc_classifier).",
                 "REST API Pública: https://api.alerce.online/ztf/v1/objects.",
                 "Paginación Nativa: Soporta page y page_size con límites controlados.",
                 "Métricas clave: lastmjd (MJD), meanra, meandec, probability, ndet."
             ],
             "BROKER DE DATOS CHILENO")

    # -------------------------------------------------------------------------
    # SLIDE 4: Campos de Cruce y Modelo Dimensional
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, NAVY)
    add_header(s4, "3. Estrategia de Cruce: Dimensión Temporal y Dimensión Espacial")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Cruce Temporal: fecha_id (DATE)",
             [
                 "Desafío: Ambas fuentes entregan tiempo en Modified Julian Date (MJD).",
                 "Solución en Transform: Conversión unificada a fecha calendario estándar YYYY-MM-DD (MJD 0 = 1858-11-17).",
                 "Dimensión Tiempo (dw.dim_tiempo): Permite análisis por año, mes, trimestre, día de la semana y fin de semana.",
                 "Resultado: Cruce temporal exacto por noche astronómica de observación."
             ],
             "DIMENSIÓN TEMPORAL")

    add_card(s4, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Cruce Espacial: banda_declinacion_id",
             [
                 "Desafío: Ambas fuentes usan coordenadas continuas (Ascensión Recta / Declinación).",
                 "Solución en Transform: Discretización matemática de la declinación en franjas regulares de 10° celestes (ej. -30° a -20°, 0° a 10°).",
                 "Dimensión Banda Cielo (dw.dim_banda_cielo): Clasifica franjas por Hemisferio Austral (dec < 0°) y Boreal (dec >= 0°).",
                 "Resultado: Identificación de franjas celestes con alta densidad de alertas frente a tiempo de exposición asignado."
             ],
             "DIMENSIÓN ESPACIAL")

    # -------------------------------------------------------------------------
    # SLIDE 5: Arquitectura de 4 Capas en PostgreSQL
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, NAVY)
    add_header(s5, "4. Arquitectura de Datos en 4 Capas y Auditoría")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "1. Capa RAW",
             [
                 "Tablas: eso_observations_raw y alerce_objects_raw.",
                 "Payload JSONB inmutable tal como llega de la red.",
                 "Permite reprocesamiento histórico sin volver a saturar las APIs públicas."
             ],
             "INMUTABILIDAD")

    add_card(s5, Inches(3.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "2. Capa STAGING",
             [
                 "Tablas: stg_eso_observations y stg_alerce_objects.",
                 "Datos limpios, tipados, validados y desduplicados.",
                 "Filtrado de nulos y anomalías físicas (coordenadas [-90,90])."
             ],
             "DEPURACIÓN")

    add_card(s5, Inches(6.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "3. Capa DW (Star)",
             [
                 "Dimensiones: dim_tiempo, dim_instrumento, dim_banda_cielo.",
                 "Hechos: fact_observaciones_eso y fact_alertas_alerce.",
                 "Surrogate keys e integridad referencial."
             ],
             "MODELO ESTRELLA")

    add_card(s5, Inches(9.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "4. Capa MART & Audit",
             [
                 "5 tablas de KPIs agregados con métricas de gestión.",
                 "Tabla public.etl_audit con trazabilidad completa (filas, % nulos, tiempo, estado).",
                 "Idempotencia: ON CONFLICT DO UPDATE."
             ],
             "KPIs Y AUDITORÍA")

    # -------------------------------------------------------------------------
    # SLIDE 6: Orquestación en Apache Airflow (3 DAGs)
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, NAVY)
    add_header(s6, "5. Diseño de Orquestación en Apache Airflow: 3 DAGs Desacoplados")

    add_card(s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "DAG 1: ETL ESO Archive",
             [
                 "Schedule: @daily (02:00 UTC).",
                 "Tarea 1: Validar API ESO.",
                 "Tarea 2: Extraer JSON a Raw.",
                 "Tarea 3: Transformar a Staging y DW.",
                 "Tarea 4: Disparar DAG 3 (TriggerDagRunOperator).",
                 "Registra métricas en public.etl_audit."
             ],
             "dag_1_etl_eso_archive")

    add_card(s6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "DAG 2: ETL ALeRCE Chile",
             [
                 "Schedule: @daily (02:00 UTC).",
                 "Tarea 1: Validar API ALeRCE.",
                 "Tarea 2: Extracción paginada a Raw.",
                 "Tarea 3: Transformar a Staging y DW.",
                 "Tarea 4: Disparar DAG 3.",
                 "Ejecución 100% independiente del DAG 1."
             ],
             "dag_2_etl_alerce_chile")

    add_card(s6, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "DAG 3: Mart Astronómico",
             [
                 "Schedule: Disparado automáticamente por DAGs 1 y 2 (o 03:00 UTC).",
                 "Tarea: Ejecutar agregaciones en SQL sobre el DW.",
                 "Resiliencia: Procesa con los datos disponibles sin fallar si un ETL falló.",
                 "Actualiza las 5 tablas del esquema mart."
             ],
             "dag_3_kpi_mart_astronomico")

    # -------------------------------------------------------------------------
    # SLIDE 7: Tolerancia a Fallas y Demostración en Vivo
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, NAVY)
    add_header(s7, "6. Estrategia de Tolerancia a Fallas y Demostración en Vivo (8 min)")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Mecanismos de Resiliencia Implementados",
             [
                 "Validación Previa: Comprueba HTTP status antes de iniciar cualquier extracción pesada.",
                 "Reintentos con Espera: retries=2 con retry_delay=15s (rápido para la demo en vivo).",
                 "Callback de Falla Automático: on_failure_callback (registrar_falla_audit) persiste estado 'FAILED' y excepción en public.etl_audit.",
                 "Aislamiento de Fallas: Si DAG 1 falla, DAG 2 sigue ejecutando y DAG 3 calcula sobre los datos disponibles.",
                 "Idempotencia de Carga: ON CONFLICT permite relanzar tareas ('Clear') sin duplicar registros."
             ],
             "ARQUITECTURA RESILIENTE")

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Protocolo de Demostración en Vivo",
             [
                 "1. En Airflow Variables, alterar eso_api_url a una URL incorrecta.",
                 "2. Ejecutar DAG 1: Observar estado 'up_for_retry' (amarillo) y caída final a 'failed' (rojo).",
                 "3. Verificar en PostgreSQL: SELECT * FROM public.etl_audit muestra el registro FAILED con mensaje de error.",
                 "4. Constatar que DAG 2 y DAG 3 terminaron en SUCCESS (verde).",
                 "5. Restaurar URL correcta, aplicar 'Clear Task' y evidenciar recuperación exitosa e idempotente."
             ],
             "GUÍA DEMO EN VIVO")

    # -------------------------------------------------------------------------
    # SLIDE 8: Indicadores de Gestión 1, 2 y 3 (Operacionales ESO)
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, NAVY)
    add_header(s8, "7. Indicadores de Gestión: Eficiencia y Almacenamiento ESO")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "KPI 1: Horas Efectivas de Exposición",
             [
                 "Fórmula: SUM(tiempo_exposicion_seg) / 3600 por instalación (facility).",
                 "Objetivo: Medir el aprovechamiento nocturno conjunto en Paranal, La Silla y Chajnantor.",
                 "Periodicidad: Diaria.",
                 "Meta: >= 8.0 horas conjuntas por instalación.",
                 "Hallazgo: Telescopios como ESO-3.6 (HARPS + NIRPS) y ALMA acumulan entre 5 y 8 horas de observación útil por noche."
             ],
             "PRODUCTIVIDAD OBSERVACIONAL")

    add_card(s8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "KPI 2: Volumen de Datos Científicos",
             [
                 "Fórmula: SUM(tamano_estimado_mb) / 1024.",
                 "Objetivo: Dimensionar la carga de transferencia satelital/fibra óptica y almacenamiento.",
                 "Periodicidad: Diaria / Mensual.",
                 "Umbral Alerta: > 500 GB/día.",
                 "Hallazgo: Flujo regular entre 1 y 25 GB/día en productos procesados, dentro de la capacidad de red."
             ],
             "INFRAESTRUCTURA TI")

    add_card(s8, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "KPI 3: Tasa de Calibración Avanzada",
             [
                 "Fórmula: (COUNT(calib_level >= 2) / COUNT(*)) * 100.",
                 "Objetivo: Asegurar que los datos entregados estén en nivel ciencia listos para publicación.",
                 "Periodicidad: Semanal / Mensual.",
                 "Meta: >= 75% en nivel ciencia.",
                 "Hallazgo: 100% de productos de ALMA y HARPS cargados cumplen con nivel ciencia validado."
             ],
             "CALIDAD DE DATOS")

    # -------------------------------------------------------------------------
    # SLIDE 9: Indicadores 4 y 5 (ALeRCE y Cruce de Seguimiento)
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, NAVY)
    add_header(s9, "8. Indicadores 4 y 5: Machine Learning y Cruce ESO vs. ALeRCE")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "KPI 4: Confianza de Clasificación ALeRCE",
             [
                 "Fórmula: (COUNT(probabilidad >= 0.70) / COUNT(*)) * 100.",
                 "Objetivo: Evaluar la certeza del clasificador chileno lc_classifier por categoría de objeto (Supernovas, Periódicas, AGN).",
                 "Periodicidad: Diaria.",
                 "Meta: >= 60% de alertas clasificadas con alta confianza.",
                 "Hallazgo: Clases consolidadas (ej. LPV) logran mayor certidumbre, mientras que transitorios rápidos requieren más épocas de luz."
             ],
             "MACHINE LEARNING CHILENO")

    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "KPI 5: Cobertura de Seguimiento por Banda (Cruce)",
             [
                 "Fórmula: Minutos Exposición ESO / N° Alertas ALeRCE en misma fecha y franja de 10°.",
                 "Objetivo: Identificar zonas del cielo con alertas transitorias frente al tiempo de seguimiento asignado en Chile.",
                 "Periodicidad: Diaria / Semanal.",
                 "Meta: >= 5.0 min/alerta en Hemisferio Austral (dec < 0°).",
                 "Ramas de Diagnóstico: Cobertura óptima (>= 5 min), parcial (< 5 min), déficit (0 min) y observación austral sin alertas activas.",
                 "Hallazgo: En octubre 2026 se observan bandas australes con seguimiento intensivo de ESO y franjas con alertas transitorias en espera de seguimiento."
             ],
             "INDICADOR DE CRUCE PRINCIPAL")

    # -------------------------------------------------------------------------
    # SLIDE 10: Estrategia de Datos y Escalabilidad Futura
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, NAVY)
    add_header(s10, "9. Estrategia de Gobernanza, Calidad y Escalabilidad")

    add_card(s10, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "Usuarios y Decisiones",
             [
                 "Directores de Operaciones: Asignación dinámica de horas nocturnas.",
                 "Científicos de Datos (CMM/MAS): Calibración de modelos ML de ALeRCE.",
                 "Ingenieros de Redes: Monitoreo de tráfico y cuotas de almacenamiento."
             ],
             "VALOR DE NEGOCIO")

    add_card(s10, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "Calidad y Open Science",
             [
                 "Métricas de nulos automáticas en etl_audit (17.39% en campos opcionales de ALeRCE; 0% en ESO).",
                 "Datos 100% abiertos bajo políticas de Open Science (sin datos sensibles ni PII).",
                 "Cumplimiento total de normativa chilena."
             ],
             "GOBIERNO DE DATOS")

    add_card(s10, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "Escalabilidad Vera Rubin (LSST)",
             [
                 "El observatorio Vera C. Rubin generará 10 millones de alertas por noche en Cerro Pachón (Coquimbo).",
                 "Arquitectura lista para escalar: Particionamiento por rango de fecha en PostgreSQL.",
                 "Transición modular a Apache Spark / Kafka sin reescribir la lógica analítica."
             ],
             "FUTURO CIENTÍFICO")

    # -------------------------------------------------------------------------
    # SLIDE 11: Conclusiones y Ronda de Preguntas
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, NAVY)
    add_header(s11, "10. Conclusiones, Lecciones Aprendidas y Demostración")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Lecciones Aprendidas del Proyecto",
             [
                 "El desacoplamiento de DAGs es fundamental: la indisponibilidad de una API externa jamás debe colapsar el sistema.",
                 "La capa RAW inmutable garantiza reproducibilidad y evita bloqueos por límites de consulta.",
                 "El cruce dimensional (MJD a Fecha y Discretización de Coordenadas) resolvió la heterogeneidad de fuentes.",
                 "La tabla public.etl_audit proporciona visibilidad operacional instantánea para el equipo."
             ],
             "APRENDIZAJES CLAVE")

    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "¡Muchas Gracias! - Ronda de Preguntas",
             [
                 "Repositorio GitHub: Francoisere/Gestion2-ESO",
                 "Código disponible: DAGs Airflow, scripts Python, DDL PostgreSQL, Docker Compose.",
                 "Entregables completos: Informe técnico PDF y suite de pruebas CLI.",
                 "Listos para responder preguntas individuales de la comisión evaluadora."
             ],
             "CIERRE Y PREGUNTAS")

    # Guardar presentación
    os.makedirs("presentacion", exist_ok=True)
    out_path = "presentacion/Presentacion_INF522_Gestion_Datos_Astronomicos.pptx"
    prs.save(out_path)
    print(f"[OK] Presentación PowerPoint generada con éxito en: {out_path}")

if __name__ == "__main__":
    crear_presentacion()
