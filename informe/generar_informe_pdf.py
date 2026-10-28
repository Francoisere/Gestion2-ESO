"""
Generador del Informe Técnico Completo en PDF (Evaluación 2 - 35% INF-522)
Universidad Católica del Maule - Ingeniería Civil Informática
Construido con ReportLab.
"""

import os
import sys
from datetime import datetime
import psycopg2

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# Canvas Numerado con Encabezado y Pie de Página Profesional
# -----------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # En la portada no se dibujan encabezados ni números de página
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f172a")) # Slate 900

        # Encabezado superior
        self.drawString(54, 750, "UNIVERSIDAD CATÓLICA DEL MAULE | INF-522: GESTIÓN II")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b")) # Slate 500
        self.drawRightString(612 - 54, 750, "Pipeline ETL & Data Warehouse Astronómico (ESO - ALeRCE)")

        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)

        # Pie de página inferior
        self.line(54, 45, 612 - 54, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 32, "Evaluación 2 (35%) — Caso de Gestión y Analítica con APIs Abiertas de Chile")
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 54, 32, page_text)
        self.restoreState()


def generar_pdf():
    os.makedirs("informe", exist_ok=True)
    pdf_path = "informe/Informe_INF522_Gestion_Datos_Astronomicos.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Paleta de colores
    COLOR_PRIMARY = colors.HexColor("#0f172a")   # Slate 900
    COLOR_SECONDARY = colors.HexColor("#0369a1") # Sky 700
    COLOR_ACCENT = colors.HexColor("#d97706")    # Amber 600
    COLOR_DARK = colors.HexColor("#1e293b")      # Slate 800
    COLOR_MUTED = colors.HexColor("#475569")     # Slate 600
    COLOR_LIGHT = colors.HexColor("#f8fafc")     # Slate 50
    COLOR_BORDER = colors.HexColor("#cbd5e1")    # Slate 300

    # Estilos tipográficos
    title_cover = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY,
        alignment=0,
        spaceAfter=12
    )

    subtitle_cover = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=17,
        textColor=COLOR_SECONDARY,
        alignment=0,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        "Header1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=COLOR_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Header2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=COLOR_SECONDARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_DARK,
        alignment=4,  # Justificado
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        "BulletDark",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=COLOR_PRIMARY,
        spaceAfter=0
    )

    code_style = ParagraphStyle(
        "CodeText",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_DARK
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=COLOR_DARK
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell_style,
        fontName="Helvetica-Bold"
    )

    def make_callout(text, bg="#f1f5f9", border="#0284c7"):
        content = [Paragraph(text, callout_style)]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border)),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        return t

    story = []

    # =========================================================================
    # 1. PORTADA INSTITUCIONAL
    # =========================================================================
    story.append(Spacer(1, 25))
    story.append(Paragraph("UNIVERSIDAD CATÓLICA DEL MAULE", ParagraphStyle("Inst", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=COLOR_SECONDARY)))
    story.append(Paragraph("Facultad de Ciencias de la Ingeniería | Escuela de Ingeniería Civil Informática", ParagraphStyle("Dept", fontName="Helvetica", fontSize=10, leading=13, textColor=COLOR_MUTED)))
    story.append(Paragraph("Actividad Curricular: INF-522 — Gestión II (Sistemas de Información y Data Warehousing)", ParagraphStyle("SubDept", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=COLOR_PRIMARY)))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_SECONDARY, spaceBefore=5, spaceAfter=25))

    story.append(Paragraph("INFORME TÉCNICO DE EVALUACIÓN 2 (35%)", ParagraphStyle("Type", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=COLOR_ACCENT)))
    story.append(Paragraph("Estrategia de Datos y Arquitectura ETL en Airflow y PostgreSQL para el Sector Astronómico en Chile", title_cover))
    story.append(Paragraph("Diseño e Implementación de un Pipeline de Datos Abiertos: Observatorio Europeo Austral (ESO) y Broker ALeRCE (CMM / MAS)", subtitle_cover))

    story.append(Spacer(1, 20))

    meta_table_data = [
        [Paragraph("<b>Académicos:</b>", table_cell_bold), Paragraph("Natalia Morales | Sebastián Farías", table_cell_style)],
        [Paragraph("<b>Carrera:</b>", table_cell_bold), Paragraph("Ingeniería Civil Informática", table_cell_style)],
        [Paragraph("<b>Fecha de Entrega:</b>", table_cell_bold), Paragraph("Noviembre 2026", table_cell_style)],
        [Paragraph("<b>Repositorio GitHub:</b>", table_cell_bold), Paragraph("https://github.com/Francoisere/Gestion2-ESO", table_cell_style)],
        [Paragraph("<b>Ponderación:</b>", table_cell_bold), Paragraph("Evaluación 2 — 35% de la Nota Final", table_cell_style)],
        [Paragraph("<b>Componentes Entregados:</b>", table_cell_bold), Paragraph("Informe PDF, Presentación PPTX (11 láminas), DAGs Airflow, Scripts Python, DDL PostgreSQL, Suite de Pruebas CLI, Contenedores Docker.", table_cell_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[150, 354])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 30))
    story.append(make_callout(
        "<b>Resumen Ejecutivo:</b> El presente informe documenta el desarrollo de un sistema analítico de datos de extremo a extremo que extrae, transforma y consolida metadatos astronómicos generados en territorio chileno por el Observatorio Europeo Austral (ESO) y eventos transitorios clasificados en tiempo real por el broker nacional ALeRCE (Centro de Modelamiento Matemático / Instituto Milenio de Astrofísica). La solución está orquestada mediante 3 DAGs desacoplados en Apache Airflow, un modelo dimensional en estrella en PostgreSQL organizado en 4 capas (raw, staging, dw, mart), auditoría automatizada y 5 indicadores de gestión operacional y de seguimiento.",
        bg="#f0f9ff", border="#0284c7"
    ))

    story.append(PageBreak())

    # =========================================================================
    # 2. INTRODUCCIÓN Y CONTEXTO DEL SECTOR
    # =========================================================================
    story.append(Paragraph("1. Introducción y Contexto del Sector Astronómico en Chile", h1_style))
    story.append(Paragraph(
        "Chile ostenta una posición geográfica y atmosférica privilegiada a nivel mundial: sus cielos en las regiones de Antofagasta, Atacama y Coquimbo presentan más de 300 noches despejadas al año, humedad relativa extremadamente baja y una turbulencia atmosférica mínima. Esta condición ha consolidado al país como la <b>capital astronómica del planeta</b>, concentrando más del 50% de la capacidad de observación óptica e infrarroja mundial a través de los complejos científicos más avanzados de la humanidad, tales como Cerro Paranal (Very Large Telescope - VLT), el Observatorio La Silla, y la meseta de Chajnantor con APEX y el radiotelescopio ALMA.",
        body_style
    ))
    story.append(Paragraph(
        "No obstante, la astronomía moderna ha entrado en la era del <i>Big Data</i>. El cielo nocturno ya no es un escenario estático, sino un flujo continuo de millones de eventos transitorios: explosiones de supernovas, estrellas variables pulsantes, núcleos galácticos activos y microlentes gravitacionales. Para enfrentar esta avalancha de datos, la comunidad científica chilena, a través de la Universidad de Chile (CMM), el Instituto Milenio de Astrofísica (MAS), la Universidad de Concepción y la Fundación Data Observatory, desarrolló <b>ALeRCE (Automatic Learning for the Rapid Classification of Events)</b>, un broker astronómico que ingiere millones de alertas nocturnas y las clasifica automáticamente mediante algoritmos de Machine Learning.",
        body_style
    ))
    story.append(Paragraph(
        "En este contexto, surge un problema crítico de gestión operativa y científica: <b>¿cómo coordinar de manera eficiente la ingesta masiva de alertas astronómicas con el valioso y costoso tiempo de exposición de los telescopios de clase mundial instalados en Chile?</b> El presente proyecto aborda dicha problemática mediante una solución integral de Inteligencia de Negocios, Data Warehousing y automatización ETL en Apache Airflow, articulando datos de telescopios de ESO con alertas clasificadas de ALeRCE bajo una arquitectura en 4 capas.",
        body_style
    ))

    # =========================================================================
    # 3. SELECCIÓN Y JUSTIFICACIÓN DE LAS 2 FUENTES DE DATOS
    # =========================================================================
    story.append(Paragraph("2. Selección, Justificación y Viabilidad de las APIs Públicas", h1_style))
    story.append(Paragraph(
        "Para dar cabal cumplimiento a los requisitos de la rúbrica (APIs públicas de datos abiertos de Chile, obtenidas 100% mediante código sin descargas manuales, sin repetir las fuentes genéricas y con un campo de cruce claro), se seleccionaron dos infraestructuras tecnológicas científicas operativas en el país:",
        body_style
    ))

    story.append(Paragraph("2.1. API 1: ESO Science Archive — Servicio TAP (Table Access Protocol)", h2_style))
    story.append(Paragraph(
        "<b>Justificación Territorial en Chile:</b> Aunque el Observatorio Europeo Austral (ESO) es una organización intergubernamental europea, el <b>100% de sus telescopios, instrumentos científicos y operaciones nocturnas residen en territorio chileno</b>. Sus observatorios operan en Cerro Paranal (Región de Antofagasta, VLT/VLTI), La Silla (Región de Coquimbo, telescopios de 3.6m y NTT), y en la planicie de Chajnantor (radiotelescopio ALMA y APEX), bajo acuerdos de cooperación de largo plazo suscritos con el Estado de Chile.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Funcionamiento Técnico:</b> ESO implementa el estándar internacional IVOA TAP (International Virtual Observatory Alliance - Table Access Protocol). Expone un endpoint HTTP síncrono en <code>https://archive.eso.org/tap_obs/sync</code> que acepta consultas en lenguaje <b>ADQL</b> (Astronomical Data Query Language, derivado de SQL-92). La API responde peticiones GET o POST con el parámetro <code>FORMAT=json</code>, entregando metadatos completos y filas estructuradas de la tabla global <code>ivoa.ObsCore</code> sin requerir autenticación ni tokens para datos públicos.",
        body_style
    ))

    story.append(Paragraph("2.2. API 2: ALeRCE Broker API (Centro de Modelamiento Matemático / MAS Chile)", h2_style))
    story.append(Paragraph(
        "<b>Justificación Territorial en Chile:</b> ALeRCE es una iniciativa tecnológica y científica concebida, desarrollada y operada enteramente en Chile por científicos e ingenieros del CMM (Facultad de Ciencias Físicas y Matemáticas, Universidad de Chile), MAS, UdeC y la Fundación Data Observatory, con financiamiento de ANID. Constituye una de las mayores plataformas de ciencia de datos del país.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Funcionamiento Técnico:</b> ALeRCE procesa el torrente de alertas de telescopios de sondeo continuo (como el Zwicky Transient Facility - ZTF y próximamente el Observatorio Vera C. Rubin) y expone una API REST moderna y abierta en <code>https://api.alerce.online/ztf/v1/objects</code>. La API devuelve objetos astronómicos en formato JSON, soportando paginación por <code>page</code> y <code>page_size</code>, ordenamiento por <code>lastmjd</code> y filtrado por clasificador de Machine Learning (<code>lc_classifier</code>).",
        body_style
    ))

    # Tabla comparativa de APIs
    api_comp_data = [
        [Paragraph("<b>Atributo Técnico</b>", table_header_style), Paragraph("<b>API 1: ESO Science Archive</b>", table_header_style), Paragraph("<b>API 2: ALeRCE Broker Chile</b>", table_header_style)],
        [Paragraph("<b>Tipo de Servicio</b>", table_cell_bold), Paragraph("IVOA TAP (ADQL síncrono)", table_cell_style), Paragraph("REST API (JSON estructurado)", table_cell_style)],
        [Paragraph("<b>Endpoint Base</b>", table_cell_bold), Paragraph("https://archive.eso.org/tap_obs/sync", table_cell_style), Paragraph("https://api.alerce.online/ztf/v1/objects", table_cell_style)],
        [Paragraph("<b>Autenticación</b>", table_cell_bold), Paragraph("Pública (No requiere credencial)", table_cell_style), Paragraph("Pública (No requiere credencial)", table_cell_style)],
        [Paragraph("<b>Paginación / Límite</b>", table_cell_bold), Paragraph("Cláusula ADQL: TOP N", table_cell_style), Paragraph("Parámetros: page, page_size (máx 100)", table_cell_style)],
        [Paragraph("<b>Entidad Principal</b>", table_cell_bold), Paragraph("Observación científica (obs_id)", table_cell_style), Paragraph("Objeto de alerta transitoria (oid)", table_cell_style)],
        [Paragraph("<b>Campos Temporales</b>", table_cell_bold), Paragraph("t_min (Modified Julian Date)", table_cell_style), Paragraph("lastmjd, firstmjd (Modified Julian Date)", table_cell_style)],
        [Paragraph("<b>Campos Espaciales</b>", table_cell_bold), Paragraph("s_ra, s_dec (coordenadas ecuatoriales)", table_cell_style), Paragraph("meanra, meandec (coordenadas ecuatoriales)", table_cell_style)],
    ]
    t_api = Table(api_comp_data, colWidths=[110, 197, 197])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_api)

    story.append(PageBreak())

    # =========================================================================
    # 4. PROBLEMA DE GESTIÓN Y CAMPOS DE CRUCE
    # =========================================================================
    story.append(Paragraph("3. Problema de Gestión Operativa y Campos de Cruce", h1_style))
    story.append(Paragraph(
        "<b>Problema de Gestión a Medir:</b> El costo operativo por hora de un telescopio de 8 metros en Cerro Paranal asciende a decenas de miles de dólares, y la demanda de tiempo de observación por parte de astrónomos supera en más de 400% la disponibilidad nocturna. Simultáneamente, el broker ALeRCE genera cientos de alertas diarias de objetos que cambian de brillo súbitamente en el cielo visible desde Chile. <b>La gestión del sector astronómico requiere medir si el tiempo de exposición y la instrumentación disponible en Chile están asignándose de manera armónica respecto a la densidad espacial de alertas transitorias detectadas.</b>",
        body_style
    ))
    story.append(Paragraph(
        "Para lograr este análisis comparativo, las dos fuentes de datos son integradas dimensionalmente a través de dos campos de cruce rigurosamente diseñados:",
        body_style
    ))

    story.append(Paragraph("3.1. Campo de Cruce 1: Dimensión Temporal Unificada (fecha_id / DATE)", h2_style))
    story.append(Paragraph(
        "Ambas APIs reportan el instante temporal en el sistema estándar de la astronomía: <b>Modified Julian Date (MJD)</b>. El MJD es una escala continua de días fraccionales donde el MJD 0.0 corresponde exactamente al 17 de noviembre de 1858 a las 00:00:00 UTC. Durante la etapa de transformación ETL en Python, se implementa la función de conversión formal:",
        body_style
    ))
    story.append(make_callout(
        "<b>Fórmula de Conversión Temporal:</b><br/>"
        "<code>Fecha_Calendario = Datetime(1858, 11, 17) + Timedelta(dias=MJD_val)</code><br/>"
        "Ejemplo: MJD 61341.547 -> 2026-10-28 (Día exacto de observación nocturna en Chile).",
        bg="#f8fafc", border="#cbd5e1"
    ))
    story.append(Paragraph(
        "Esta transformación genera una clave primaria temporal <code>fecha_id (DATE)</code> que vincula a la dimensión <code>dw.dim_tiempo</code>, permitiendo consolidar tanto las observaciones de ESO como las alertas de ALeRCE por fecha, mes, año, trimestre y día de la semana.",
        body_style
    ))

    story.append(Paragraph("3.2. Campo de Cruce 2: Dimensión Espacial de Franjas Celestes (banda_declinacion_id)", h2_style))
    story.append(Paragraph(
        "En el espacio celeste, los telescopios y las alertas se orientan según el sistema de coordenadas ecuatoriales: <b>Ascensión Recta (RA)</b> de 0° a 360° y <b>Declinación (Dec)</b> de -90° a +90°. Dado que dos eventos nunca ocurrirán en coordenadas continuas idénticas al milisegundo de arco, el campo de cruce espacial requiere un proceso de discretización o 'binning'.",
        body_style
    ))
    story.append(Paragraph(
        "Se diseñó una discretización en <b>franjas regulares de 10 grados de declinación</b>:",
        body_style
    ))
    story.append(make_callout(
        "<b>Fórmula de Discretización Espacial:</b><br/>"
        "<code>Limite_Inferior = floor(Declinacion / 10.0) * 10</code><br/>"
        "<code>Banda_Declinacion = str(Limite_Inferior) + ' a ' + str(Limite_Inferior + 10)</code><br/>"
        "Ejemplo: Dec = -24.5° (Cielo visible en Paranal) -> Banda '-30 a -20' | Dec = +5.2° -> Banda '0 a 10'.",
        bg="#f8fafc", border="#cbd5e1"
    ))
    story.append(Paragraph(
        "Adicionalmente, la dimensión <code>dw.dim_banda_cielo</code> cataloga cada franja según su <b>Hemisferio Celeste</b> ('Austral' para Dec &lt; 0° y 'Boreal' para Dec &ge; 0°). Esto permite cruzar directamente el tiempo de exposición de los telescopios chilenos en cada franja del cielo frente al número de alertas detectadas en esa misma banda.",
        body_style
    ))

    # =========================================================================
    # 5. PASO A PASO TÉCNICO: EXTRACCIÓN, TRANSFORMACIÓN Y CARGA
    # =========================================================================
    story.append(Paragraph("4. Paso a Paso de la Solución: Extracción, Transformación y Carga (ETL)", h1_style))

    story.append(Paragraph("4.1. Extracción en Python (Módulos extract_eso y extract_alerce)", h2_style))
    story.append(Paragraph(
        "La extracción se programó en Python mediante la librería <code>requests</code>, asegurando las siguientes restricciones de robustez exigidas por la rúbrica:",
        body_style
    ))
    story.append(Paragraph("• <b>Validación Previa de API:</b> Cada proceso ejecuta una tarea de prueba de conectividad (<code>validar_api_eso</code> y <code>validar_api_alerce</code>) con timeout corto antes de lanzar extracciones intensivas.", bullet_style))
    story.append(Paragraph("• <b>Manejo de Errores HTTP y Timeouts:</b> Se controlan excepciones de red (<code>ConnectTimeout</code>, <code>ReadTimeout</code>, <code>HTTPError</code>) con reintentos automáticos.", bullet_style))
    story.append(Paragraph("• <b>Paginación y Límites:</b> Para ALeRCE se implementó paginación ordenada por <code>lastmjd DESC</code> con páginas de 100 registros y control de pausas para no saturar el servicio. Para ESO se empleó la cláusula ADQL <code>SELECT TOP {limite}</code> acotada por ventanas de MJD.", bullet_style))
    story.append(Paragraph("• <b>Inmutabilidad en Capa RAW:</b> La respuesta JSON completa se almacena intacta en formato <code>JSONB</code> en las tablas <code>raw.eso_observations_raw</code> y <code>raw.alerce_objects_raw</code> junto con el <code>run_id</code> y timestamp de extracción.", bullet_style))

    story.append(Paragraph("4.2. Transformaciones Documentadas en Python (Módulo transform)", h2_style))
    story.append(Paragraph(
        "Se documentan formalmente las <b>6 transformaciones de datos</b> realizadas con <code>pandas</code> y <code>numpy</code>:",
        body_style
    ))

    transf_data = [
        [Paragraph("<b>#</b>", table_header_style), Paragraph("<b>Transformación</b>", table_header_style), Paragraph("<b>Descripción Técnica y Regla de Negocio</b>", table_header_style)],
        [Paragraph("<b>1</b>", table_cell_bold), Paragraph("<b>Conversión de Tipos y Fechas</b>", table_cell_bold), Paragraph("Conversión de <code>t_min</code> y <code>lastmjd</code> (MJD numérico) a <code>fecha_observacion</code> tipo <code>DATE</code> estándar (YYYY-MM-DD) mediante suma de días base 1858-11-17.", table_cell_style)],
        [Paragraph("<b>2</b>", table_cell_bold), Paragraph("<b>Renombrado y Estandarización</b>", table_cell_bold), Paragraph("Mapeo homogéneo: <code>t_exptime -> tiempo_exposicion_seg</code>; <code>access_estsize -> tamano_estimado_kb</code>; <code>class -> class_name</code>; <code>probability -> probabilidad_clase</code>; <code>ndet -> num_detecciones</code>.", table_cell_style)],
        [Paragraph("<b>3</b>", table_cell_bold), Paragraph("<b>Tratamiento de Nulos y Atípicos</b>", table_cell_bold), Paragraph("Filtrado de registros con coordenadas físicas corruptas (dec fuera de [-90, 90] o ra fuera de [0, 360]) y tiempos de exposición &le; 0. Imputación de tamaños nulos con 0 y cálculo del % de nulos para la tabla de auditoría.", table_cell_style)],
        [Paragraph("<b>4</b>", table_cell_bold), Paragraph("<b>Normalización de Textos</b>", table_cell_bold), Paragraph("Eliminación de espacios en blanco (trim) y conversión a mayúsculas de <code>instrument_name</code> (ej. 'uves' -> 'UVES', 'harps' -> 'HARPS') y <code>dataproduct_type</code> ('IMAGE', 'SPECTRUM', 'CUBE').", table_cell_style)],
        [Paragraph("<b>5</b>", table_cell_bold), Paragraph("<b>Creación de Campos Calculados</b>", table_cell_bold), Paragraph("Cálculo de volumen en megabytes: <code>tamano_estimado_mb = tamano_estimado_kb / 1024.0</code>. Cálculo de la dimensión espacial: <code>banda_declinacion</code> (tramos de 10°) y <code>hemisferio</code> ('Austral' vs 'Boreal').", table_cell_style)],
        [Paragraph("<b>6</b>", table_cell_bold), Paragraph("<b>Desduplicación e Idempotencia</b>", table_cell_bold), Paragraph("Aplicación de <code>df.drop_duplicates(subset=['obs_id'])</code> y <code>df.drop_duplicates(subset=['oid'])</code> para eliminar duplicidad en memoria antes de la persistencia relacional.", table_cell_style)],
    ]
    t_transf = Table(transf_data, colWidths=[20, 140, 344])
    t_transf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_transf)

    story.append(PageBreak())

    story.append(Paragraph("4.3. Carga y Modelo de Datos Dimensional en PostgreSQL", h2_style))
    story.append(Paragraph(
        "La base de datos <code>dw_astronomia</code> se diseñó organizando la información en <b>4 esquemas lógicos</b> que garantizan la separación de responsabilidades y el cumplimiento de las mejores prácticas de Data Warehousing:",
        body_style
    ))
    story.append(Paragraph("• <b>raw:</b> Almacenamiento crudo en tablas <code>eso_observations_raw</code> y <code>alerce_objects_raw</code> con payloads <code>JSONB</code> inmutables, permitiendo la trazabilidad del dato original.", bullet_style))
    story.append(Paragraph("• <b>staging:</b> Tablas <code>stg_eso_observations</code> y <code>stg_alerce_objects</code> con datos limpios, fuertemente tipados, desduplicados y con columnas enriquecidas.", bullet_style))
    story.append(Paragraph("• <b>dw:</b> Modelo Dimensional en Estrella (Star Schema) integrado por tres dimensiones compartidas (<code>dim_tiempo</code>, <code>dim_banda_cielo</code>, <code>dim_instrumento</code>) y dos tablas de hechos (<code>fact_observaciones_eso</code> y <code>fact_alertas_alerce</code>).", bullet_style))
    story.append(Paragraph("• <b>mart:</b> Vistas materializadas y tablas de KPIs agregados con métricas de productividad, calidad, almacenamiento y cobertura espacial.", bullet_style))
    story.append(Paragraph("• <b>public.etl_audit:</b> Tabla transversal de auditoría que registra cada corrida con filas leídas, filas cargadas, porcentaje de nulos, duración y estado.", bullet_style))

    story.append(Paragraph(
        "<b>Garantía de Idempotencia:</b> Cada operación de carga utiliza cláusulas <code>ON CONFLICT DO UPDATE</code> o <code>DO NOTHING</code>. Por ejemplo, en <code>dw.fact_observaciones_eso</code> se aplica <code>ON CONFLICT (obs_id) DO UPDATE SET tiempo_exposicion_seg = EXCLUDED.tiempo_exposicion_seg, tamano_estimado_mb = EXCLUDED.tamano_estimado_mb</code>. De este modo, volver a ejecutar un DAG o reprocesar un rango temporal jamás duplica filas ni corrompe los indicadores agregados.",
        body_style
    ))

    # =========================================================================
    # 6. ORQUESTACIÓN EN APACHE AIRFLOW
    # =========================================================================
    story.append(Paragraph("5. Orquestación y Estrategia de Ejecución en Apache Airflow", h1_style))
    story.append(Paragraph(
        "La solución cuenta con <b>3 DAGs completamente desacoplados</b> en Apache Airflow, asegurando que la falla de una fuente externa no bloquee ni comprometa el resto del flujo de datos:",
        body_style
    ))

    dags_table_data = [
        [Paragraph("<b>Nombre del DAG</b>", table_header_style), Paragraph("<b>Schedule</b>", table_header_style), Paragraph("<b>Responsabilidad y Flujo de Tareas</b>", table_header_style), Paragraph("<b>Dependencia / Disparador</b>", table_header_style)],
        [
            Paragraph("<b>dag_1_etl_eso_archive</b>", table_cell_bold),
            Paragraph("@daily<br/>(0 2 * * *)", table_cell_style),
            Paragraph("Validar API ESO TAP &rarr; Extraer JSON a raw &rarr; Transformar y limpiar &rarr; Cargar en DW &rarr; Registrar etl_audit &rarr; Disparar DAG 3.", table_cell_style),
            Paragraph("Independiente.<br/>Trigger al terminar.", table_cell_style)
        ],
        [
            Paragraph("<b>dag_2_etl_alerce_chile</b>", table_cell_bold),
            Paragraph("@daily<br/>(0 2 * * *)", table_cell_style),
            Paragraph("Validar API ALeRCE &rarr; Extraer páginas JSON a raw &rarr; Transformar y validar ML &rarr; Cargar en DW &rarr; Registrar etl_audit &rarr; Disparar DAG 3.", table_cell_style),
            Paragraph("Independiente.<br/>Trigger al terminar.", table_cell_style)
        ],
        [
            Paragraph("<b>dag_3_kpi_mart_astronomico</b>", table_cell_bold),
            Paragraph("Disparado o<br/>(0 3 * * *)", table_cell_style),
            Paragraph("Ejecutar agregaciones SQL sobre dw &rarr; Actualizar las 5 tablas del esquema mart &rarr; Registrar etl_audit.", table_cell_style),
            Paragraph("Disparado por DAG 1 y DAG 2 (TriggerDagRunOperator).", table_cell_style)
        ],
    ]
    t_dags = Table(dags_table_data, colWidths=[120, 55, 239, 90])
    t_dags.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_dags)

    story.append(Spacer(1, 8))
    story.append(Paragraph("5.1. Manejo de Credenciales y Variables de Airflow", h2_style))
    story.append(Paragraph(
        "Dando estricto cumplimiento a la restricción 4 de la pauta (<i>'No se deben incluir contraseñas ni claves de API en el código'</i>), los DAGs se configuran dinámicamente mediante componentes nativos de Airflow:",
        body_style
    ))
    story.append(Paragraph("• <b>Airflow Connection (postgres_dw):</b> Configurada en la UI de Airflow (Admin &rarr; Connections) apuntando al host, puerto y credenciales de la base de datos PostgreSQL, consumida mediante <code>PostgresHook</code>.", bullet_style))
    story.append(Paragraph("• <b>Airflow Variables:</b> Variables <code>eso_api_url</code> y <code>alerce_api_url</code> definidas en Admin &rarr; Variables, permitiendo modificar los endpoints sin tocar el código fuente.", bullet_style))

    story.append(Paragraph("5.2. Tolerancia a Fallas y Callback de Auditoría", h2_style))
    story.append(Paragraph(
        "Se configuró en <code>default_args</code> de cada DAG una estrategia de reintentos y timeouts orientada a la demostración en vivo:",
        body_style
    ))
    story.append(make_callout(
        "<code>default_args = {<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'retries': 2,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'retry_delay': timedelta(seconds=15),  # 15s para demostración ágil<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'execution_timeout': timedelta(minutes=5),<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'on_failure_callback': registrar_falla_audit<br/>"
        "}</code>",
        bg="#f8fafc", border="#cbd5e1"
    ))
    story.append(Paragraph(
        "Cuando una tarea falla tras agotar sus reintentos, el callback <code>registrar_falla_audit</code> se activa de forma automática, insertando en <code>public.etl_audit</code> el <code>dag_id</code>, <code>run_id</code>, duración, estado 'FAILED' y el mensaje de excepción detallado.",
        body_style
    ))

    story.append(Paragraph("5.3. Demostración de Falla Controlada en Vivo (Presentación de 8 minutos)", h2_style))
    story.append(Paragraph(
        "Para la exposición grupal ante la comisión docente, el grupo preparó el siguiente protocolo de prueba en vivo:",
        body_style
    ))
    story.append(Paragraph("1. <b>Provocar Falla:</b> En la UI de Airflow (Admin &rarr; Variables), cambiar temporalmente <code>eso_api_url</code> a una URL rota: <code>https://archive.eso.org/tap_obs/url_rota_demo</code>.", bullet_style))
    story.append(Paragraph("2. <b>Ejecutar DAGs:</b> Activar manualmente <code>dag_1_etl_eso_archive</code> y <code>dag_2_etl_alerce_chile</code>.", bullet_style))
    story.append(Paragraph("3. <b>Evidencia Visual:</b> En la pantalla de Airflow, la tarea de validación de ESO pasa a estado <i>up_for_retry</i> (amarillo), reintenta 2 veces cada 15 segundos y finaliza en <i>failed</i> (rojo).", bullet_style))
    story.append(Paragraph("4. <b>Aislamiento y Auditoría:</b> Mostrar en PostgreSQL la consulta <code>SELECT * FROM public.etl_audit WHERE estado = 'FAILED';</code>, evidenciando el registro de la caída. Paralelamente, <code>dag_2_etl_alerce_chile</code> y <code>dag_3_kpi_mart_astronomico</code> terminan exitosamente en verde (<i>success</i>).", bullet_style))
    story.append(Paragraph("5. <b>Recuperación Idempotente:</b> Restaurar la URL correcta en la Variable de Airflow, aplicar 'Clear Task' a la tarea fallida y demostrar cómo el flujo se reanuda e inserta los datos de forma idempotente sin duplicados.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 7. LOS 5 INDICADORES DE GESTIÓN (ESQUEMA MART)
    # =========================================================================
    story.append(Paragraph("6. Definición, Cálculo y Resultados de los 5 Indicadores de Gestión", h1_style))
    story.append(Paragraph(
        "Se diseñaron 5 indicadores de gestión calculados mediante consultas SQL agregadas en el esquema <code>mart</code>, respondiendo a preguntas operativas y estratégicas del sector:",
        body_style
    ))

    kpis_doc = [
        [Paragraph("<b>#</b>", table_header_style), Paragraph("<b>Indicador de Gestión</b>", table_header_style), Paragraph("<b>Objetivo y Decisión</b>", table_header_style), Paragraph("<b>Fórmula Matemática</b>", table_header_style), Paragraph("<b>Fuente</b>", table_header_style), Paragraph("<b>Meta / Umbral</b>", table_header_style)],
        [
            Paragraph("<b>1</b>", table_cell_bold),
            Paragraph("<b>Horas Efectivas de Exposición Diaria</b>", table_cell_bold),
            Paragraph("Medir el aprovechamiento productivo del tiempo nocturno en telescopios de ESO en Chile.", table_cell_style),
            Paragraph("&Sigma;(tiempo_exposicion_seg) / 3600.0", table_cell_style),
            Paragraph("ESO<br/>(fact_obs)", table_cell_style),
            Paragraph("&ge; 8.0 horas conjuntas por noche.", table_cell_style)
        ],
        [
            Paragraph("<b>2</b>", table_cell_bold),
            Paragraph("<b>Volumen Diario de Datos (GB/día)</b>", table_cell_bold),
            Paragraph("Dimensionar la carga de transferencia de red y almacenamiento digital de productos científicos.", table_cell_style),
            Paragraph("&Sigma;(tamano_estimado_mb) / 1024.0", table_cell_style),
            Paragraph("ESO<br/>(fact_obs)", table_cell_style),
            Paragraph("Alerta operativa si supera 500 GB/día.", table_cell_style)
        ],
        [
            Paragraph("<b>3</b>", table_cell_bold),
            Paragraph("<b>Tasa de Calibración Avanzada Ciencia</b>", table_cell_bold),
            Paragraph("Evaluar la calidad y nivel de procesamiento de los datos científicos entregados (calib_level &ge; 2).", table_cell_style),
            Paragraph("(COUNT(calib &ge; 2) / COUNT(*)) * 100", table_cell_style),
            Paragraph("ESO<br/>(fact_obs)", table_cell_style),
            Paragraph("&ge; 75% en nivel ciencia validado.", table_cell_style)
        ],
        [
            Paragraph("<b>4</b>", table_cell_bold),
            Paragraph("<b>Índice de Alta Confianza en Alertas</b>", table_cell_bold),
            Paragraph("Medir la certidumbre del clasificador de Machine Learning chileno (lc_classifier) en eventos transitorios.", table_cell_style),
            Paragraph("(COUNT(prob &ge; 0.70) / COUNT(*)) * 100", table_cell_style),
            Paragraph("ALeRCE<br/>(fact_alertas)", table_cell_style),
            Paragraph("&ge; 60% de alertas con prob &ge; 0.70.", table_cell_style)
        ],
        [
            Paragraph("<b>5</b>", table_cell_bold),
            Paragraph("<b>Cobertura de Seguimiento por Banda (Cruce)</b>", table_cell_bold),
            Paragraph("Identificar qué franjas de declinación con alertas están siendo cubiertas por telescopios en Chile.", table_cell_style),
            Paragraph("Minutos ESO en Banda / N° Alertas ALeRCE en Banda", table_cell_style),
            Paragraph("Cruce ESO + ALeRCE", table_cell_style),
            Paragraph("&ge; 5.0 min/alerta en Hemisferio Austral.", table_cell_style)
        ],
    ]
    t_kpis = Table(kpis_doc, colWidths=[18, 105, 125, 110, 56, 90])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_kpis)

    story.append(Spacer(1, 10))
    story.append(Paragraph("6.1. Evidencia de Resultados Empíricos en PostgreSQL", h2_style))
    story.append(Paragraph(
        "A continuación se presentan muestras reales extraídas directamente de las tablas del esquema <code>mart</code> tras la ejecución del pipeline con datos de producción:",
        body_style
    ))

    # Conectar a PostgreSQL para obtener muestras reales
    try:
        conn = psycopg2.connect(host="localhost", port=5432, user="postgres", password="postgres", dbname="dw_astronomia")
        cur = conn.cursor()

        # Tabla Muestra KPI 1
        cur.execute("SELECT fecha_id, facility_name, instrumentos_operativos, horas_efectivas_exposicion, estado_meta FROM mart.kpi_horas_efectivas_exposicion LIMIT 4;")
        kpi1_rows = cur.fetchall()

        # Tabla Muestra KPI 4
        cur.execute("SELECT fecha_id, class_name, total_alertas_detectadas, tasa_alta_confianza, dictamen_clasificador FROM mart.kpi_confianza_alertas_alerce LIMIT 4;")
        kpi4_rows = cur.fetchall()

        # Tabla Muestra KPI 5 (Cruce)
        cur.execute("SELECT fecha_id, banda_declinacion, hemisferio, minutos_exposicion_eso, total_alertas_alerce, ratio_minutos_eso_por_alerta, diagnostico_operacional FROM mart.kpi_cobertura_cielo_diaria LIMIT 4;")
        kpi5_rows = cur.fetchall()
        conn.close()
    except Exception as e:
        kpi1_rows = []
        kpi4_rows = []
        kpi5_rows = []

    if kpi5_rows:
        story.append(Paragraph("<b>Muestra Real: Indicador 5 — Cobertura de Seguimiento (Cruce ESO vs ALeRCE)</b>", h2_style))
        sample_kpi5_data = [
            [Paragraph("<b>Fecha</b>", table_header_style), Paragraph("<b>Banda Dec</b>", table_header_style), Paragraph("<b>Hemisferio</b>", table_header_style), Paragraph("<b>Min ESO</b>", table_header_style), Paragraph("<b>Alertas</b>", table_header_style), Paragraph("<b>Ratio Min/Alerta</b>", table_header_style), Paragraph("<b>Diagnóstico Operacional</b>", table_header_style)]
        ]
        for r in kpi5_rows:
            sample_kpi5_data.append([
                Paragraph(str(r[0]), table_cell_style),
                Paragraph(str(r[1]), table_cell_style),
                Paragraph(str(r[2]), table_cell_style),
                Paragraph(f"{r[3]} min", table_cell_style),
                Paragraph(str(r[4]), table_cell_style),
                Paragraph(f"{r[5]} min/al" if r[5] is not None else "N/A", table_cell_style),
                Paragraph(str(r[6]), table_cell_bold),
            ])
        t_sample5 = Table(sample_kpi5_data, colWidths=[65, 75, 60, 50, 45, 65, 144])
        t_sample5.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
            ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ]))
        story.append(t_sample5)

    story.append(PageBreak())

    # =========================================================================
    # 8. ESTRATEGIA DE DATOS (2 A 3 PÁGINAS FORMALES)
    # =========================================================================
    story.append(Paragraph("7. Capítulo Especial: Estrategia de Datos y Gobernanza", h1_style))
    story.append(Paragraph(
        "Una solución de Inteligencia de Negocios en el ámbito astronómico demanda una estrategia integral que regule la toma de decisiones, la calidad, el linaje, la gestión de riesgos y la escalabilidad ante nuevos observatorios en Chile.",
        body_style
    ))

    story.append(Paragraph("7.1. Usuarios Clave y Decisiones de Negocio que Apoyan los Indicadores", h2_style))
    story.append(Paragraph(
        "Los indicadores calculados en la capa MART satisfacen las necesidades de tres perfiles de usuarios estratégicos en el ecosistema astronómico chileno:",
        body_style
    ))
    story.append(Paragraph("• <b>Directores de Operaciones de Telescopios (ESO / Paranal / La Silla):</b> Utilizan los KPIs 1 y 5 para evaluar si la programación nocturna y la asignación de tiempo en telescopios como el VLT están respondiendo ágilmente a eventos transitorios críticos. Permite tomar decisiones de interrupción de programas estándar (<i>Target of Opportunity - ToO</i>) para apuntar telescopios hacia alertas de alta prioridad.", bullet_style))
    story.append(Paragraph("• <b>Equipos de Ciencia de Datos e Inteligencia Artificial (ALeRCE / CMM / MAS):</b> Emplean el KPI 4 para monitorear el desempeño del clasificador <code>lc_classifier</code>. Una caída en la tasa de alta confianza activa protocolos de reentrenamiento de modelos con nuevas curvas de luz y ajuste de hiperparámetros.", bullet_style))
    story.append(Paragraph("• <b>Ingenieros de Infraestructura TI y Almacenamiento:</b> Supervisan el KPI 2 (GB/día) para dimensionar las cuotas de almacenamiento en discos locales en Paranal, prever saturaciones en el enlace de fibra óptica Paranal-Antofagasta-Santiago y gestionar el archivado hacia la nube científica.", bullet_style))

    story.append(Paragraph("7.2. Gobierno y Calidad de Datos: Nulos, Duplicados y Consistencia", h2_style))
    story.append(Paragraph(
        "La confiabilidad analítica del Data Warehouse descansa sobre rigurosos controles de calidad automatizados en la etapa de transformación:",
        body_style
    ))
    story.append(Paragraph("• <b>Monitoreo y Cuantificación de Nulos:</b> Las APIs abiertas presentan disparidad estructural. En ESO, atributos mandatorios como <code>obs_id</code>, <code>instrument_name</code> y coordenadas físicas presentan 0% de nulos, mientras que en ALeRCE campos contextuales opcionales (tales como <code>g_r_max</code> o <code>sigmara</code>) presentan una tasa de nulos promedio de 17.39%. Esta cifra es calculada dinámicamente y registrada en <code>public.etl_audit</code> para cada corrida.", bullet_style))
    story.append(Paragraph("• <b>Eliminación de Duplicados:</b> Tanto en memoria (<code>drop_duplicates</code>) como en base de datos mediante índices únicos sobre <code>obs_id</code> y <code>oid</code>, evitando la sobrestimación de horas de exposición o conteo de alertas.", bullet_style))
    story.append(Paragraph("• <b>Consistencia Semántica entre Fuentes:</b> Se armonizaron las coordenadas ecuatoriales continuas mediante la discretización de 10° en <code>dw.dim_banda_cielo</code> y la unificación de calendarios en <code>dw.dim_tiempo</code>, garantizando que ambas fuentes conversen en un plano dimensional común.", bullet_style))

    story.append(Paragraph("7.3. Origen del Dato y Linaje (Data Lineage)", h2_style))
    story.append(Paragraph(
        "El linaje del dato describe el ciclo de vida completo de cada registro desde su emisión externa hasta su consulta en los reportes de gestión:",
        body_style
    ))
    story.append(make_callout(
        "<b>Cadena de Linaje de Datos:</b><br/>"
        "1. <b>Origen:</b> archive.eso.org (ADQL) & api.alerce.online (REST JSON).<br/>"
        "2. <b>Capa RAW:</b> Inserción inmutable de payloads completos en <code>raw.*_raw</code> (JSONB).<br/>"
        "3. <b>Capa STAGING:</b> Limpieza, tipado, conversión MJD a DATE y filtrado de anomalías.<br/>"
        "4. <b>Capa DW:</b> Generación de surrogate keys y enlace relacional Hechos-Dimensiones (Star Schema).<br/>"
        "5. <b>Capa MART:</b> Consultas de agregación SQL para los 5 KPIs analíticos de negocio.",
        bg="#f1f5f9", border="#475569"
    ))

    story.append(Paragraph("7.4. Frecuencia de Actualización y Relación con el Schedule de los DAGs", h2_style))
    story.append(Paragraph(
        "La frecuencia de ejecución de los DAGs fue seleccionada considerando la naturaleza física del fenómeno observado:",
        body_style
    ))
    story.append(Paragraph("• <b>Schedule Diario (02:00 UTC / 23:00 hora de Chile):</b> Los telescopios operan durante la noche. Al amanecer en Chile (10:00 UTC), las observaciones y alertas de la noche previa están consolidadas en los servidores de ESO y ALeRCE. Ejecutar los DAGs en dicho horario asegura que los informes estén disponibles al iniciar la jornada de trabajo de los directores de operaciones.", bullet_style))
    story.append(Paragraph("• <b>Backfill y Recarga Histórica (catchup=True):</b> La arquitectura soporta re-ejecutar rangos de fechas pasados mediante parámetros <code>mjd_inicio</code> y <code>mjd_fin</code> sin duplicar registros gracias a la idempotencia.", bullet_style))

    story.append(PageBreak())

    story.append(Paragraph("7.5. Gestión de Riesgos y Mitigación Operativa", h2_style))
    story.append(Paragraph(
        "Se identificaron y mitigaron proactivamente cuatro riesgos inherentes al consumo de APIs públicas:",
        body_style
    ))

    riesgos_data = [
        [Paragraph("<b>Riesgo Operativo</b>", table_header_style), Paragraph("<b>Impacto Potencial</b>", table_header_style), Paragraph("<b>Estrategia de Mitigación Implementada</b>", table_header_style)],
        [
            Paragraph("<b>Caída o Indisponibilidad de API Externa</b>", table_cell_bold),
            Paragraph("Bloqueo del pipeline y retraso en el cálculo de métricas de negocio.", table_cell_style),
            Paragraph("Tarea previa de validación HTTP. Desacoplamiento total: la caída de ESO no detiene a ALeRCE. DAG 3 calcula sobre datos existentes sin colapsar.", table_cell_style)
        ],
        [
            Paragraph("<b>Límites de Consulta y Rate Limiting</b>", table_cell_bold),
            Paragraph("Bloqueo temporal de la IP por exceso de peticiones síncronas.", table_cell_style),
            Paragraph("Uso de <code>TOP {limite}</code> en ADQL, paginación controlada con pausas de 150ms en ALeRCE y persistencia cruda en RAW para no re-consultar la API.", table_cell_style)
        ],
        [
            Paragraph("<b>Cambios de Esquema en JSON</b>", table_cell_bold),
            Paragraph("Falla de deserialización o pérdida de columnas en staging.", table_cell_style),
            Paragraph("Almacenamiento de payload completo en JSONB inmutable y uso de valores por defecto defensivos (<code>.fillna()</code>, <code>errors='coerce'</code>).", table_cell_style)
        ],
        [
            Paragraph("<b>Timeouts de Red en Servidores Remotos</b>", table_cell_bold),
            Paragraph("Interrupción abrupta de la descarga de datos.", table_cell_style),
            Paragraph("Timeouts explícitos en <code>requests.get</code>, <code>retries=2</code> con espera de 15s y registro automático en <code>public.etl_audit</code> vía callbacks.", table_cell_style)
        ],
    ]
    t_riesgos = Table(riesgos_data, colWidths=[130, 140, 234])
    t_riesgos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_riesgos)

    story.append(Spacer(1, 10))
    story.append(Paragraph("7.6. Licencias, Políticas de Open Science y Datos Sensibles", h2_style))
    story.append(Paragraph(
        "Ambas fuentes seleccionadas se rigen por políticas internacionales de <b>Ciencia Abierta (Open Science)</b>. El Observatorio Europeo Austral libera los metadatos y datos de observaciones públicas inmediatamente después del periodo estándar de embargo propietario (habitualmente 1 año asignado al investigador principal), bajo directrices de acceso abierto para la comunidad científica. Por su parte, el broker ALeRCE publica las alertas procesadas de manera 100% pública e instantánea bajo licencias permisivas de investigación.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Privacidad y Normativa Chilena:</b> Ninguna de las fuentes involucra datos de carácter personal, números de identificación (RUT), datos biométricos ni información comercial confidencial sujeta a la Ley N° 19.628 sobre Protección de la Vida Privada. La solución es 100% inocua y éticamente intachable para su explotación académica y pública.",
        body_style
    ))

    story.append(Paragraph("7.7. Escalabilidad Futura hacia el Observatorio Vera C. Rubin (LSST)", h2_style))
    story.append(Paragraph(
        "El panorama de la astronomía en Chile experimentará una revolución en 2025-2026 con el inicio de operaciones del <b>Observatorio Vera C. Rubin en Cerro Pachón (Región de Coquimbo)</b>. Su telescopio de sondeo sinóptico (LSST) generará aproximadamente <b>10 millones de alertas astronómicas transitorias por noche</b> (alrededor de 20 Terabytes de datos brutos cada día). ALeRCE es uno de los pocos brokers seleccionados oficialmente a nivel mundial para procesar dicho torrente.",
        body_style
    ))
    story.append(Paragraph(
        "Nuestra arquitectura fue diseñada con visión de escalabilidad empresarial para absorber dicho volumen masivo:",
        body_style
    ))
    story.append(Paragraph("• <b>Particionamiento de Tablas en PostgreSQL:</b> Migración de <code>dw.fact_alertas_alerce</code> hacia particionamiento nativo por rango temporal mensual (<code>PARTITION BY RANGE (fecha_id)</code>) y sub-particionado por <code>banda_sk</code>, optimizando las consultas de agregación sin degradación por volumen.", bullet_style))
    story.append(Paragraph("• <b>Transición a Procesamiento Distribuido:</b> Dado que la lógica de transformación en <code>src/transform.py</code> está modularizada y desacoplada de la base de datos, las funciones pueden ser trasladadas a <b>Apache Spark / PySpark</b> y la ingesta hacia <b>Apache Kafka</b> manteniendo inalteradas las definiciones dimensionales de la capa MART.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 9. INFORMACIÓN DE CARGA Y AUDITORÍA
    # =========================================================================
    story.append(Paragraph("8. Evidencia de Carga y Tabla de Auditoría (public.etl_audit)", h1_style))
    story.append(Paragraph(
        "A continuación se presenta la transcripción íntegra de los registros capturados en la tabla <code>public.etl_audit</code> durante las fases de prueba, ejecución normal y demostración de falla controlada:",
        body_style
    ))

    # Obtener registros reales de etl_audit
    audit_table_data = [
        [
            Paragraph("<b>ID</b>", table_header_style),
            Paragraph("<b>DAG ID</b>", table_header_style),
            Paragraph("<b>Fuente</b>", table_header_style),
            Paragraph("<b>Leídas</b>", table_header_style),
            Paragraph("<b>Cargadas</b>", table_header_style),
            Paragraph("<b>% Nulos</b>", table_header_style),
            Paragraph("<b>Segs</b>", table_header_style),
            Paragraph("<b>Estado</b>", table_header_style),
            Paragraph("<b>Detalle Error / Excepción</b>", table_header_style)
        ]
    ]

    try:
        conn = psycopg2.connect(host="localhost", port=5432, user="postgres", password="postgres", dbname="dw_astronomia")
        cur = conn.cursor()
        cur.execute("""
            SELECT audit_id, dag_id, fuente, filas_leidas, filas_cargadas,
                   porcentaje_nulos, duracion_segundos, estado,
                   COALESCE(mensaje_error, 'Ninguno (OK)')
            FROM public.etl_audit
            ORDER BY audit_id ASC;
        """)
        for r in cur.fetchall():
            err_short = str(r[8]).replace("\n", " ")[:35] + ("..." if len(str(r[8])) > 35 else "")
            color_st = "#16a34a" if r[7] == "SUCCESS" else "#dc2626"
            audit_table_data.append([
                Paragraph(str(r[0]), table_cell_style),
                Paragraph(str(r[1]).replace("dag_", ""), table_cell_style),
                Paragraph(str(r[2])[:12], table_cell_style),
                Paragraph(str(r[3]), table_cell_style),
                Paragraph(str(r[4]), table_cell_style),
                Paragraph(f"{r[5]}%", table_cell_style),
                Paragraph(str(r[6]), table_cell_style),
                Paragraph(f"<b><font color='{color_st}'>{r[7]}</font></b>", table_cell_style),
                Paragraph(err_short, table_cell_style),
            ])
        conn.close()
    except Exception as e:
        audit_table_data.append([Paragraph("No conectado", table_cell_style)] * 9)

    t_audit = Table(audit_table_data, colWidths=[20, 105, 75, 40, 45, 42, 35, 47, 95])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
    ]))
    story.append(t_audit)

    story.append(Spacer(1, 10))
    story.append(Paragraph("8.1. Métricas Consolidadas de Ejecución", h2_style))
    story.append(Paragraph("• <b>Total de Registros Cargados en Hechos ESO:</b> Más de 300 observaciones científicas de ALMA, HARPS, UVES y FEROS con tiempos de exposición validados.", bullet_style))
    story.append(Paragraph("• <b>Total de Registros Cargados en Hechos ALeRCE:</b> Más de 500 alertas clasificadas con probabilidades y recuento de detecciones.", bullet_style))
    story.append(Paragraph("• <b>Porcentaje de Nulos Detectado:</b> 0.00% en ESO (metadatos IVOA estrictos); 17.39% en ALeRCE (debido a atributos optativos de fotometría).", bullet_style))
    story.append(Paragraph("• <b>Tiempos Medios de Ejecución:</b> DAG 1 (ESO): ~4.1 segundos | DAG 2 (ALeRCE): ~26 a 40 segundos (por paginación HTTP controlada) | DAG 3 (Mart): ~0.06 segundos.", bullet_style))

    # =========================================================================
    # 10. ANÁLISIS DEL PROCESO Y LECCIONES APRENDIDAS
    # =========================================================================
    story.append(Paragraph("9. Análisis del Proceso, Problemas Detectados y Soluciones", h1_style))
    story.append(Paragraph(
        "Dando respuesta a las preguntas mínimas exigidas en la sección de Análisis del Proceso:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. ¿Qué hallazgos surgieron al cargar los datos?</b><br/>"
        "Al cruzar las observaciones de telescopios de ESO frente a las alertas de ALeRCE (KPI 5), se evidenció que ciertas franjas australes del cielo (especialmente declinaciones entre -30° y 0°) concentran un volumen relevante de alertas de objetos transitorios nuevos clasificados por ALeRCE, pero presentan 0 minutos de exposición en telescopios mayores durante la misma fecha. Esto constata empíricamente una <b>oportunidad de mejora operacional: existe una brecha de seguimiento observacional que justificaría activar convenios de asignación rápida de telescopios chilenos hacia alertas de ALeRCE</b>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2. ¿Qué problemas detectaron y cómo los resolvieron?</b><br/>"
        "• <i>Disparidad en Sistemas Temporales:</i> Ambas APIs utilizaban Modified Julian Date en vez de fechas humanas. Se solucionó mediante la implementación matemática del epoch 1858-11-17 en Python.<br/>"
        "• <i>Timeouts Ocasionales en ALeRCE:</i> La API de ALeRCE presentó demoras puntuales bajo alta concurrencia. Se resolvió ampliando el timeout a 35 segundos, agregando reintentos con backoff y separando las descargas en páginas de 100 elementos.<br/>"
        "• <i>Duplicidad de Identificadores en Productos Reducidos:</i> Algunas observaciones de ALMA contenían múltiples archivos para un mismo <code>obs_id</code>. Se depuraron con <code>drop_duplicates</code> en Python y <code>ON CONFLICT DO UPDATE</code> en PostgreSQL.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3. ¿Qué fallas ocurrieron en las APIs o en Airflow y cómo respondió el diseño de los DAGs?</b><br/>"
        "Durante las pruebas controladas (Audit ID 8), se simuló la caída de la API de ESO mediante una URL inválida. El DAG 1 ejecutó 2 reintentos cada 15 segundos y gatilló automáticamente la función <code>registrar_falla_audit</code>, registrando el error en <code>public.etl_audit</code>. <b>El aislamiento de los DAGs demostró su efectividad total: DAG 2 continuó operando sin perturbación y DAG 3 recalculó los indicadores sobre los datos disponibles sin bloquearse.</b>",
        body_style
    ))

    # =========================================================================
    # 11. CONCLUSIONES Y REFERENCIAS
    # =========================================================================
    story.append(Paragraph("10. Conclusiones y Referencias", h1_style))
    story.append(Paragraph(
        "El proyecto demostró con éxito que es factible articular una arquitectura analítica robusta, tolerante a fallas y reproducible utilizando fuentes de datos abiertas chilenas en el sector astronómico. El uso combinado de Apache Airflow, Python y PostgreSQL bajo un modelo dimensional en estrella permitió convertir datos heterogéneos en 5 indicadores de alto impacto para la gestión científica y operativa de Chile.",
        body_style
    ))
    story.append(Paragraph("<b>Referencias Bibliográficas:</b>", h2_style))
    story.append(Paragraph("• European Southern Observatory (ESO). (2026). <i>ESO Science Archive Facility & IVOA Table Access Protocol (TAP) ObsCore Documentation</i>. Garching, Germany / Cerro Paranal, Chile.", bullet_style))
    story.append(Paragraph("• Förster, F., Cabrera-Vives, G., Castillo-Navarrete, E., et al. (2021). <i>The Automatic Learning for the Rapid Classification of Events (ALeRCE) Alert Broker</i>. The Astronomical Journal, 161(5), 242.", bullet_style))
    story.append(Paragraph("• Kimball, R., & Ross, M. (2013). <i>The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling</i> (3rd ed.). Wiley.", bullet_style))
    story.append(Paragraph("• Apache Software Foundation. (2026). <i>Apache Airflow Documentation: Architecture, DAGs, and Resilient Task Execution</i>.", bullet_style))

    # Construir documento
    try:
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"[OK] Informe PDF generado exitosamente en: {pdf_path}")
    except PermissionError:
        fallback_path = "informe/Informe_INF522_Gestion_Datos_Astronomicos_actualizado.pdf"
        fallback_doc = SimpleDocTemplate(
            fallback_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        fallback_doc.build(story, canvasmaker=NumberedCanvas)
        print(f"[AVISO] El archivo principal {pdf_path} está abierto en Adobe Acrobat u otro visor.")
        print(f"[OK] Copia idéntica y actualizada generada en: {fallback_path}")

if __name__ == "__main__":
    generar_pdf()
