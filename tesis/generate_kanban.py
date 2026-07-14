#!/usr/bin/env python3
"""Generador de Kanban VERIFEX - Horizontal"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = "/Users/maarco_serrano/Downloads/verifex-standalone 2"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Kanban VERIFEX"

# ── Colores por persona ──
MARCO_FILL = PatternFill(start_color="F3E5F5", end_color="F3E5F5", fill_type="solid")
MARCO_FONT = Font(name="Calibri", size=9, bold=True, color="4A148C")
TONY_FILL = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
TONY_FONT = Font(name="Calibri", size=9, bold=True, color="B71C1C")
LUIS_FILL = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
LUIS_FONT = Font(name="Calibri", size=9, bold=True, color="0D47A1")
ULISES_FILL = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
ULISES_FONT = Font(name="Calibri", size=9, bold=True, color="1B5E20")

# ── Colores de columnas Kanban ──
COLORS = {
    "Backlog":       PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid"),
    "Stories":       PatternFill(start_color="E8EAF6", end_color="E8EAF6", fill_type="solid"),
    "Por Hacer":     PatternFill(start_color="FFF3E0", end_color="FFF3E0", fill_type="solid"),
    "En Proceso":    PatternFill(start_color="FFF8E1", end_color="FFF8E1", fill_type="solid"),
    "Por Verificar": PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid"),
    "Acabado/Terminado": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
}

HEADER_COLORS = {
    "Backlog":       PatternFill(start_color="9E9E9E", end_color="9E9E9E", fill_type="solid"),
    "Stories":       PatternFill(start_color="3F51B5", end_color="3F51B5", fill_type="solid"),
    "Por Hacer":     PatternFill(start_color="FF9800", end_color="FF9800", fill_type="solid"),
    "En Proceso":    PatternFill(start_color="FFC107", end_color="FFC107", fill_type="solid"),
    "Por Verificar": PatternFill(start_color="2196F3", end_color="2196F3", fill_type="solid"),
    "Acabado/Terminado": PatternFill(start_color="4CAF50", end_color="4CAF50", fill_type="solid"),
}

prioridad_colors = {
    "Alta":  Font(name="Calibri", size=9, bold=True, color="C62828"),
    "Media": Font(name="Calibri", size=9, bold=True, color="F57F17"),
    "Baja":  Font(name="Calibri", size=9, bold=True, color="2E7D32"),
}

assignee_styles = {
    "Marco":  (MARCO_FILL, MARCO_FONT),
    "Luis":   (LUIS_FILL, LUIS_FONT),
    "Ulises": (ULISES_FILL, ULISES_FONT),
    "Tony":   (TONY_FILL, TONY_FONT),
}

VERSION_FILL = PatternFill(start_color="FFF8E1", end_color="FFF8E1", fill_type="solid")
VERSION_FONT = Font(name="Calibri", size=9, bold=True, color="E65100")

CHAPTER_FILL = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
CHAPTER_FONT = Font(name="Calibri", size=9, bold=True, color="1565C0")

# ── Indice de la tesis: orden de capitulos ──
THESIS_CHAPTERS = [
    ("01", "Capitulo 1: Generalidades del Proyecto"),
    ("02", "Capitulo 2: Fundamento Teorico"),
    ("03", "Capitulo 3: Metodologia de Desarrollo"),
    ("04", "Capitulo 4: Implementacion y Resultados"),
    ("05", "Conclusiones"),
]

# Mapeo de cada tarea a su capitulo de tesis
# task_id -> indice en THESIS_CHAPTERS
task_chapter = {
    # Cap 1: Generalidades
    "DOC-01": 0, "DOC-05": 0, "RF-01": 0, "TES-01": 0,
    # Cap 2: Fundamento Teorico
    "DOC-02": 1, "INV-01": 1, "TES-02": 1,
    # Cap 3: Metodologia de Desarrollo
    "DIS-01": 2, "DIS-02": 2, "DIS-03": 2, "DIS-04": 2,
    "DEV-01": 2, "DEV-02": 2, "DEV-03": 2, "DEV-04": 2,
    "DEV-05": 2, "DEV-06": 2, "DEV-07": 2, "DEV-08": 2,
    "DEV-09": 2, "DEV-10": 2, "DEV-11": 2, "DEV-12": 2,
    "DEV-13": 2, "DEV-14": 2, "DEV-15": 2,
    "TES-03": 2,
    "HU-01": 2, "HU-02": 2, "HU-03": 2, "HU-04": 2,
    "HU-05": 2, "HU-06": 2, "HU-07": 2, "HU-08": 2,
    "HU-09": 2, "HU-10": 2,
    # Cap 4: Implementacion y Resultados
    "TEST-01": 3, "TEST-02": 3, "TEST-03": 3,
    "DEP-01": 3, "DEP-02": 3, "DEP-03": 3, "DEP-04": 3,
    "RES-01": 3,
    "DIS-05": 3,
    "DOC-08": 3, "DOC-09": 3,
    "TES-04": 3,
    # Conclusiones
    "DOC-03": 4, "DOC-04": 4, "DOC-07": 4, "DOC-10": 4,
    "PDF-01": 4, "TESIS-01": 4, "DOC-06": 4,
    # Gestion del Proyecto (bajo Capitulo 4: Implementacion y Resultados)
    "GAN-00": 3, "GAN-01": 3, "KAN-01": 3,
    "SCR-01": 3, "SCR-02": 3,
    "COR-01": 3, "COR-02": 3, "COR-03": 3, "COR-04": 3,
}

def sort_by_chapter(task_list):
    """Ordena una lista de tareas por capitulo de tesis."""
    def keyfn(t):
        tid = t[0]
        if tid and isinstance(tid, str) and tid.startswith("★"):
            return (-1, 0)  # headers go first
        return (task_chapter.get(tid, 99), 0)
    return sorted(task_list, key=keyfn)

def insert_chapter_headers(task_list):
    """Inserta headers de capitulo entre grupos de tareas del mismo capitulo."""
    if not task_list:
        return task_list
    # Filter out any existing headers first
    items = [t for t in task_list if not (t[0] and isinstance(t[0], str) and t[0].startswith("★"))]
    items = sort_by_chapter(items)
    result = []
    last_ch = None
    for t in items:
        tid = t[0]
        ch = task_chapter.get(tid, 99)
        if ch != last_ch:
            if ch < len(THESIS_CHAPTERS):
                result.append((f"★ {THESIS_CHAPTERS[ch][0]}", THESIS_CHAPTERS[ch][1], None))
            last_ch = ch
        result.append(t)
    return result

col_labels = {
    "Backlog": "Backlog",
    "Por Hacer": "Por Hacer [WIP: 5]",
    "En Proceso": "En Proceso [WIP: 3]",
    "Por Verificar": "Por Verificar [WIP: 3]",
}

thin_border = Border(
    left=Side(style="thin", color="BDBDBD"),
    right=Side(style="thin", color="BDBDBD"),
    top=Side(style="thin", color="BDBDBD"),
    bottom=Side(style="thin", color="BDBDBD"),
)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_wrap = Alignment(horizontal="left", vertical="top", wrap_text=True)

# ── Columnas Kanban ──
columnas = ["Backlog", "Stories", "Por Hacer", "En Proceso", "Por Verificar", "Acabado/Terminado"]

# ── Tareas por columna ──
# Cada tarea: (id, descripcion, asignado, prioridad) — en Acabado: (id, descripcion, asignado)
# Las tareas estan ordenadas por indice de la tesis
tasks = {
    "Backlog": insert_chapter_headers([
        ("DOC-05", "Redaccion de introduccion, resumen y abstract de la tesis", None, "Media"),
        ("DOC-06", "Maquetacion y formato del documento Word (estilos, indices, referencias, portada)", None, "Media"),
        ("B-01", "Autenticacion de usuarios (login/registro)", None, "Baja"),
        ("B-02", "Historial de analisis por usuario", None, "Baja"),
        ("B-03", "Plugin de navegador (extension Chrome/Firefox)", None, "Baja"),
        ("B-04", "Dashboard de estadisticas de desinformacion", None, "Baja"),
        ("B-05", "API REST publica para terceros", None, "Baja"),
        ("B-06", "Analisis de imagenes (deteccion de deepfakes)", None, "Baja"),
        ("B-07", "Exportacion de resultados (PDF, CSV)", None, "Baja"),
        ("B-08", "Integracion con redes sociales (bot de Twitter/Telegram)", None, "Baja"),
        ("B-09", "Notificaciones de noticias falsas en tiempo real", None, "Baja"),
    ]),
    "Stories": insert_chapter_headers([
        ("HU-01", "[HU-01] Pegar URL de noticia para analizar su credibilidad", None, "Alta"),
        ("HU-02", "[HU-02] Ver veredicto claro (REAL/FALSO/ESTAFA/SATIRA/NO VERIFICABLE)", None, "Alta"),
        ("HU-03", "[HU-03] Ver nivel de confianza del analisis", None, "Alta"),
        ("HU-04", "[HU-04] Ver banderas rojas y senales positivas detectadas", None, "Media"),
        ("HU-05", "[HU-05] Ver noticias similares para contexto adicional", None, "Media"),
        ("HU-06", "[HU-06] Cambiar idioma entre espanol e ingles", None, "Media"),
        ("HU-07", "[HU-07] El analisis no almacena datos del usuario", None, "Alta"),
        ("HU-08", "[HU-08] Ver tipo de articulo (noticia, opinion, satira, etc.)", None, "Media"),
        ("HU-09", "[HU-09] Interfaz facil de usar e intuitiva", None, "Media"),
        ("HU-10", "[HU-10] Deteccion automatica de estafas", None, "Alta"),
    ]),
    "Por Hacer": insert_chapter_headers([
        ("DOC-03", "Verificar que no queden referencias a 'Ollama', 'IA local' o 'sin conexion' en el Word", "Ulises", "Alta"),
        ("DOC-07", "Revision de contenido, ortografia y consistencia de la tesis", "Tony", "Alta"),
        ("DOC-08", "Redaccion del Capitulo 5: Resultados, pruebas y conclusiones", "Ulises", "Alta"),
        ("DOC-09", "Analisis de casos de prueba y documentacion de resultados en la tesis", "Tony", "Media"),
        ("DIS-05", "Capturas de pantalla del sistema (interfaz, analisis, resultados, errores, mockups) [BLOQUEADO: espera a que el sistema este estable]", "Luis", "Media"),
        ("TESIS-01", "Unificar criterios: documento Word y PDF deben coincidir en contenido", "Ulises", "Alta"),
    ]),
    "En Proceso": insert_chapter_headers([
        ("RES-01", "Pruebas de analisis con URLs reales (positivas, negativas, estafas, satira, opinion)", "Marco", "Alta"),
        ("DEP-04", "Correccion de errores: timeouts (AbortController 60s), override de dominios confiables, edge cases", "Marco", "Alta"),
        ("DOC-04", "Correccion del documento Word (acentos, enie, formato, tabla de contenido)", "Ulises", "Alta"),
    ]),
    "Por Verificar": insert_chapter_headers([
        ("DOC-10", "Correcciones finales y ajustes segun retroalimentacion", "Ulises", "Alta"),
        ("PDF-01", "Generacion de PDF final de tesis (TESIS_VERIFEX.pdf) con todas las correcciones", "Ulises", "Alta"),
    ]),
    "Acabado/Terminado": insert_chapter_headers([
        # Cap 1: Generalidades del Proyecto
        ("DOC-01", "Eleccion del tema de tesis: deteccion de noticias falsas con IA", "Todos"),
        ("RF-01", "Definicion de requisitos funcionales (10 HU) y no funcionales (rendimiento, seguridad, usabilidad)", "Marco"),
        ("TES-01", "Capitulo 1: Introduccion (contexto, problema, objetivos, justificacion)", "Ulises"),

        # Cap 2: Fundamento Teorico
        ("DOC-02", "Investigacion preliminar y revision bibliografica (fake news, verificacion, IA)", "Todos"),
        ("INV-01", "Investigacion sobre IA, Groq API y procesamiento de lenguaje natural", "Marco"),
        ("TES-02", "Capitulo 2: Marco Teorico (fake news, IA, Groq API, verificacion)", "Ulises"),

        # Cap 3: Metodologia de Desarrollo
        ("DIS-01", "Wireframes y mockups de interfaz de usuario", "Luis"),
        ("DIS-02", "Paleta de colores y fuentes cyberpunk (Orbitron, Rajdhani, Share Tech Mono)", "Luis"),
        ("DIS-03", "Arquitectura cliente-servidor (React + Flask + Groq API)", "Marco"),
        ("DIS-04", "Diagramas UML (casos de uso, actividades, secuencia, clases, entidad-relacion)", "Tony"),
        ("DEV-01", "Setup del proyecto: Vite + React 18 + TypeScript + Tailwind CSS + PostCSS", "Marco"),
        ("DEV-02", "Setup del backend: Flask + CORS + rutas /analyze y /health", "Marco"),
        ("DEV-03", "Scraper URLs con fallback 4-capas: cloudscraper -> curl_cffi -> requests -> Playwright (Firefox)", "Marco"),
        ("DEV-04", "Integracion con Groq API (call_groq con fallback a llama-3.1-8b-instant)", "Marco"),
        ("DEV-05", "Prompt engineering: citas textuales obligatorias, 3 few-shot, banderas rojas especificas, 5 categorias", "Marco"),
        ("DEV-06", "Clasificador de credibilidad (analyze_url: REAL, FALSO, SATIRA, ESTAFA, NO VERIFICABLE)", "Marco"),
        ("DEV-07", "Lista de dominios confiables (CREDIBLE_DOMAINS con 29 fuentes noticiosas)", "Marco"),
        ("DEV-08", "Verificacion cruzada via Google News RSS (news_finder.py + find_similar_news)", "Marco"),
        ("DEV-09", "Conexion frontend-backend (fetch /analyze con AbortController 60s)", "Marco"),
        ("DEV-10", "Componentes base: UrlInput, VerdictDisplay, ConfidenceBar, RedFlags", "Luis"),
        ("DEV-11", "Componentes: SimilarNews, LanguageToggle, estados (loading/error/results)", "Luis"),
        ("DEV-12", "Soporte bilingue ES/EN en todos los componentes", "Luis"),
        ("DEV-13", "Article_type (5 tipos) y deteccion de estafas (is_scam)", "Marco"),
        ("DEV-14", "Diseno visual cyberpunk: cuadricula, glitch, vignette CRT, scanlines, clip-paths", "Luis"),
        ("DEV-15", "Creacion de build.sh para instalar Firefox durante el build de Render", "Marco"),
        ("TES-03", "Capitulo 3: Metodologia y Diseno del Sistema", "Ulises"),

        # Cap 4: Implementacion y Resultados
        ("TEST-01", "Suite de pruebas backend (pytest, 27 tests en server/test_analyzer.py)", "Marco"),
        ("TEST-02", "Suite de pruebas frontend (vitest + testing-library, 7 archivos, 52 tests)", "Marco"),
        ("TEST-03", "Pruebas de integracion: frontend + backend + Groq API en conjunto", "Marco"),
        ("DEP-01", "Configuracion de despliegue: Procfile con gunicorn, variables de entorno, CORS", "Marco"),
        ("DEP-02", "Despliegue en Railway (fallo por limitaciones de memoria), migracion a Render", "Marco"),
        ("DEP-03", "Despliegue exitoso en Render con dominio publico y certificado SSL", "Marco"),
        ("TES-04", "Capitulo 4: Desarrollo e Implementacion", "Ulises"),

        # Gestion del Proyecto
        ("GAN-00", "Creacion del diagrama de Gantt del proyecto (Gantt_VERIFEX.xlsx, 49 tareas, 12 hitos)", "Ulises"),
        ("GAN-01", "Actualizacion del Gantt con fechas (fin 15/08/2026) y reubicacion de Gantt/Kanban", "Ulises"),
        ("KAN-01", "Creacion del tablero Kanban del proyecto (Kanban_VERIFEX.xlsx)", "Todos"),
        ("SCR-01", "Script generate_gantt_excel.py para automatizar el diagrama de Gantt", "Ulises"),
        ("SCR-02", "Script generate_thesis.py para automatizar la generacion de la tesis", "Ulises"),
        ("COR-01", "Correccion de tesis: Ollama -> Groq API, local -> nube, Detector Fake News -> Verifex", "Ulises"),
        ("COR-02", "Correccion de acentos (stripped) y conservacion de enie en toda la tesis", "Ulises"),
        ("COR-03", "Correccion de referencias a 'phi3:mini', 'mistral', '4GB modelo local' en la tesis", "Ulises"),
        ("COR-04", "Correccion de prompts con cita textual, few-shot y distincion opinion/informativa", "Ulises"),
    ]),
}

# ── Construir hoja horizontal ──
# Fila 1: titulo del proyecto
ws.merge_cells("A1:V1")
title = ws.cell(row=1, column=1, value="KANBAN - VERIFEX: Analizador de Credibilidad de Noticias")
title.font = Font(name="Calibri", bold=True, size=16, color="1A237E")
title.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 35

# Fila 2: encabezados de columnas Kanban
col_inicio = {}
col_idx = 1
for col_name in columnas:
    col_inicio[col_name] = col_idx
    ncols = 3  # ID, Tarea, Asignado/Prioridad
    ws.merge_cells(start_row=2, start_column=col_idx, end_row=2, end_column=col_idx + ncols - 1)
    cell = ws.cell(row=2, column=col_idx, value=col_labels.get(col_name, col_name))
    cell.font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    cell.fill = HEADER_COLORS[col_name]
    cell.alignment = center
    cell.border = thin_border
    for c in range(col_idx, col_idx + ncols):
        ws.cell(row=2, column=c).border = thin_border
        ws.cell(row=2, column=c).fill = HEADER_COLORS[col_name]
    # Subheaders
    ws.cell(row=3, column=col_idx, value="ID").font = Font(name="Calibri", bold=True, size=9, color="FFFFFF")
    ws.cell(row=3, column=col_idx).fill = HEADER_COLORS[col_name]
    ws.cell(row=3, column=col_idx).alignment = center
    ws.cell(row=3, column=col_idx).border = thin_border
    ws.cell(row=3, column=col_idx + 1, value="Tarea / Descripcion").font = Font(name="Calibri", bold=True, size=9, color="FFFFFF")
    ws.cell(row=3, column=col_idx + 1).fill = HEADER_COLORS[col_name]
    ws.cell(row=3, column=col_idx + 1).alignment = center
    ws.cell(row=3, column=col_idx + 1).border = thin_border
    ws.cell(row=3, column=col_idx + 2, value="Asignado / Prio").font = Font(name="Calibri", bold=True, size=9, color="FFFFFF")
    ws.cell(row=3, column=col_idx + 2).fill = HEADER_COLORS[col_name]
    ws.cell(row=3, column=col_idx + 2).alignment = center
    ws.cell(row=3, column=col_idx + 2).border = thin_border
    col_idx += ncols

# Anchos de columna
col_idx = 1
for col_name in columnas:
    ws.column_dimensions[get_column_letter(col_idx)].width = 8
    ws.column_dimensions[get_column_letter(col_idx + 1)].width = 52
    ws.column_dimensions[get_column_letter(col_idx + 2)].width = 16
    col_idx += 3

# Rellenar tareas
max_filas = max(len(tasks[c]) for c in columnas)
for fila_offset in range(max_filas):
    fila = fila_offset + 4
    col_idx = 1
    for col_name in columnas:
        lista = tasks[col_name]
        if fila_offset < len(lista):
            t = lista[fila_offset]
            tid, desc, asignado, *resto = t
            prioridad = resto[0] if resto else None

            # ID
            c_id = ws.cell(row=fila, column=col_idx, value=tid)
            c_id.font = Font(name="Calibri", size=9, bold=True)
            c_id.alignment = center
            c_id.border = thin_border
            c_id.fill = COLORS[col_name]

            # Descripcion
            c_desc = ws.cell(row=fila, column=col_idx + 1, value=desc)
            c_desc.font = Font(name="Calibri", size=9)
            c_desc.alignment = left_wrap
            c_desc.border = thin_border
            c_desc.fill = COLORS[col_name]

            # Asignado / Prioridad
            c_asig = ws.cell(row=fila, column=col_idx + 2)
            c_asig.border = thin_border
            c_asig.fill = COLORS[col_name]
            c_asig.alignment = center

            # Header: version (★ v) or chapter (★ NN) - applies to all columns
            if tid and isinstance(tid, str) and tid.startswith("★"):
                is_version = len(tid) > 2 and tid[2:3] == 'v'
                ws.merge_cells(start_row=fila, start_column=col_idx, end_row=fila, end_column=col_idx + 2)
                cell = ws.cell(row=fila, column=col_idx, value=f"{tid}  {desc}")
                cell.font = VERSION_FONT if is_version else CHAPTER_FONT
                cell.fill = VERSION_FILL if is_version else CHAPTER_FILL
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.border = thin_border
                for cc in range(col_idx, col_idx + 3):
                    ws.cell(row=fila, column=cc).border = thin_border
                    ws.cell(row=fila, column=cc).fill = VERSION_FILL if is_version else CHAPTER_FILL
            elif col_name == "Acabado/Terminado":
                c_asig.value = asignado if asignado else "—"
                if asignado and asignado in assignee_styles:
                    a_fill, a_font = assignee_styles[asignado]
                    c_asig.fill = a_fill
                    c_asig.font = a_font
                else:
                    c_asig.font = Font(name="Calibri", size=9)
            else:
                if asignado and prioridad and prioridad != "Baja":
                    c_asig.value = f"{asignado} [{prioridad}]"
                elif asignado:
                    c_asig.value = asignado
                elif prioridad:
                    c_asig.value = f"[{prioridad}]"
                else:
                    c_asig.value = "—"

                if asignado and asignado in assignee_styles:
                    a_fill, a_font = assignee_styles[asignado]
                    c_asig.fill = a_fill
                    c_asig.font = a_font
                elif prioridad and prioridad in prioridad_colors:
                    c_asig.font = prioridad_colors[prioridad]

        else:
            for c in range(3):
                cell = ws.cell(row=fila, column=col_idx + c)
                cell.border = thin_border
                cell.fill = COLORS[col_name]

        col_idx += 3

# Altura de filas
for r in range(2, max_filas + 4):
    ws.row_dimensions[r].height = 28 if r <= 3 else 36

# ── Leyenda al final ──
fila_leyenda = max_filas + 7
ws.merge_cells(start_row=fila_leyenda, start_column=1, end_row=fila_leyenda, end_column=6)
ws.cell(row=fila_leyenda, column=1, value="Leyenda:").font = Font(name="Calibri", bold=True, size=11)
fila_leyenda += 1

legend_items = [
    ("Marco - Backend, frontend, IA, deploy y pruebas", MARCO_FILL, MARCO_FONT),
    ("Luis - Frontend, diseno UI/UX y estilos visuales", LUIS_FILL, LUIS_FONT),
    ("Ulises - Documentacion y redaccion de tesis", ULISES_FILL, ULISES_FONT),
    ("Tony - Diagramas UML, documentacion y revision de logica", TONY_FILL, TONY_FONT),
    ("★ vX.Y.Z - Version o hito de lanzamiento", VERSION_FILL, VERSION_FONT),
    ("★ Capitulo N - Indice de la tesis", CHAPTER_FILL, CHAPTER_FONT),
    ("[Alta] Prioridad alta", None, prioridad_colors["Alta"]),
    ("[Media] Prioridad media", None, prioridad_colors["Media"]),
    ("[Baja] Prioridad baja", None, prioridad_colors["Baja"]),
]
for text, fill, font in legend_items:
    cell = ws.cell(row=fila_leyenda, column=1, value=text)
    cell.font = font
    if fill:
        cell.fill = fill
    cell.border = thin_border
    ws.merge_cells(start_row=fila_leyenda, start_column=1, end_row=fila_leyenda, end_column=3)
    for c in range(2, 4):
        ws.cell(row=fila_leyenda, column=c).border = thin_border
        if fill:
            ws.cell(row=fila_leyenda, column=c).fill = fill
    fila_leyenda += 1

ws.freeze_panes = "A4"
ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True)
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.page_setup.orientation = "landscape"

output_path = f"{BASE}/Kanban_VERIFEX.xlsx"
wb.save(output_path)
print(f"Kanban horizontal generado: {output_path}")
