#!/usr/bin/env python3
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter
from datetime import date

BASE = "/Users/maarco_serrano/Downloads/verifex-standalone 2"

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Gantt VERIFEX"

# ── Color palette ──
MARCO_COLOR = "7B1FA2"   # morado
MARCO_FILL = PatternFill(start_color="F3E5F5", end_color="F3E5F5", fill_type="solid")
MARCO_FONT = Font(name="Calibri", size=10, bold=True, color="4A148C")

TONY_COLOR = "D32F2F"    # rojo
TONY_FILL = PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid")
TONY_FONT = Font(name="Calibri", size=10, bold=True, color="B71C1C")

LUIS_COLOR = "1976D2"    # azul
LUIS_FILL = PatternFill(start_color="E3F2FD", end_color="E3F2FD", fill_type="solid")
LUIS_FONT = Font(name="Calibri", size=10, bold=True, color="0D47A1")

ULISES_COLOR = "388E3C"  # verde
ULISES_FILL = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")
ULISES_FONT = Font(name="Calibri", size=10, bold=True, color="1B5E20")

# ── General styles ──
header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
header_fill = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
phase_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
phase_fill = PatternFill(start_color="3949AB", end_color="3949AB", fill_type="solid")
thin_border = Border(
    left=Side(style="thin", color="BDBDBD"),
    right=Side(style="thin", color="BDBDBD"),
    top=Side(style="thin", color="BDBDBD"),
    bottom=Side(style="thin", color="BDBDBD"),
)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_wrap = Alignment(horizontal="left", vertical="center", wrap_text=True)

# ── Headers ──
headers = ["Fase", "#", "Tarea", "Asignado a", "Inicio", "Fin", "Días", "Depende de", "Estado"]
col_widths = [24, 5, 55, 14, 13, 13, 7, 14, 15]

for col_idx, (h, w) in enumerate(zip(headers, col_widths), 1):
    cell = ws.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = center
    cell.border = thin_border
    ws.column_dimensions[get_column_letter(col_idx)].width = w

# ── Data: (phase, task_num, task_name, assignee, start, end, dep, status, is_phase) ──
# assignee: "Marco", "Luis", "Ulises", "Tony"
# status: "H"=Completado, "P"=En Progreso, "N"=Pendiente
tasks = [
    # ── Fase 0 ──
    ("Fase 0: Investigación y Propuesta", None, None, None, None, None, None, None, True),
    ("", 1, "Investigación de temas de tesis", "Marco", date(2025, 9, 1), date(2025, 9, 15), "", "H", False),
    ("", 2, "Definición del problema (desinformación)", "Marco", date(2025, 9, 10), date(2025, 9, 20), "1", "H", False),
    ("", 3, "Propuesta de solución (VERIFEX)", "Marco", date(2025, 9, 18), date(2025, 9, 30), "2", "H", False),
    ("", 4, "Revisión bibliográfica inicial", "Ulises", date(2025, 9, 20), date(2025, 10, 10), "1", "H", False),
    ("", 5, "Selección de metodología (Kanban)", "Tony", date(2025, 10, 1), date(2025, 10, 10), "3", "H", False),
    # ── Fase 1 ──
    ("Fase 1: Marco Teórico (Capítulo 1)", None, None, None, None, None, None, None, True),
    ("", 6, "Redacción de antecedentes", "Ulises", date(2025, 10, 10), date(2025, 10, 25), "4", "H", False),
    ("", 7, "Marco conceptual: IA, fake news, scraping", "Ulises", date(2025, 10, 15), date(2025, 11, 5), "4", "H", False),
    ("", 8, "Estado del arte: herramientas existentes", "Ulises", date(2025, 10, 20), date(2025, 11, 10), "6", "H", False),
    ("", 9, "Definición de tecnologías (React, Flask, Groq)", "Marco", date(2025, 11, 1), date(2025, 11, 15), "7", "H", False),
    ("", 10, "Revisión y corrección Capítulo 1", "Tony", date(2025, 11, 10), date(2025, 11, 20), "8, 9", "H", False),
    # ── Fase 2 ──
    ("Fase 2: Marco Metodológico (Capítulo 2)", None, None, None, None, None, None, None, True),
    ("", 11, "Definición de metodología Kanban", "Tony", date(2025, 11, 15), date(2025, 11, 30), "5", "H", False),
    ("", 12, "Diseño del flujo de trabajo", "Tony", date(2025, 11, 25), date(2025, 12, 10), "11", "H", False),
    ("", 13, "Definición de requisitos funcionales", "Marco", date(2025, 12, 1), date(2025, 12, 15), "12", "H", False),
    ("", 14, "Definición de requisitos no funcionales", "Marco", date(2025, 12, 5), date(2025, 12, 18), "12", "H", False),
    ("", 15, "Diseño de arquitectura (cliente-servidor)", "Marco", date(2025, 12, 10), date(2025, 12, 22), "13, 14", "H", False),
    ("", 16, "Diseño de estructura de datos", "Marco", date(2025, 12, 15), date(2025, 12, 28), "13", "H", False),
    ("", 17, "Revisión y corrección Capítulo 2", "Tony", date(2025, 12, 22), date(2025, 12, 30), "15, 16", "H", False),
    # ── Fase 3 ──
    ("Fase 3: Desarrollo (Capítulo 3)", None, None, None, None, None, None, None, True),
    ("", 18, "Setup del proyecto (Vite + React + TypeScript)", "Marco", date(2026, 1, 2), date(2026, 1, 10), "9", "H", False),
    ("", 19, "Setup del backend (Flask + Python)", "Marco", date(2026, 1, 5), date(2026, 1, 12), "9", "H", False),
    ("", 20, "Diseño de UI/UX y mockups", "Luis", date(2026, 1, 8), date(2026, 1, 22), "18", "H", False),
    ("", 21, "Implementación de componentes base", "Marco", date(2026, 1, 15), date(2026, 1, 30), "18, 20", "H", False),
    ("", 22, "Implementación del scraper (BeautifulSoup)", "Marco", date(2026, 1, 20), date(2026, 2, 5), "19", "H", False),
    ("", 23, "Integración con Groq API (antes Ollama)", "Marco", date(2026, 1, 25), date(2026, 2, 10), "19", "H", False),
    ("", 24, "Implementación del prompt engineering", "Marco", date(2026, 2, 1), date(2026, 2, 12), "23", "H", False),
    ("", 25, "Clasificador de credibilidad (REAL, FALSO, etc.)", "Marco", date(2026, 2, 5), date(2026, 2, 18), "24", "H", False),
    ("", 26, "Búsqueda de noticias similares (Google News RSS)", "Marco", date(2026, 2, 8), date(2026, 2, 20), "22", "H", False),
    ("", 27, "Implementación de búsqueda semántica (Similitud)", "Marco", date(2026, 2, 12), date(2026, 2, 25), "26", "H", False),
    ("", 28, "Conexión frontend-backend (API REST)", "Marco", date(2026, 2, 15), date(2026, 2, 28), "21, 25", "H", False),
    ("", 29, "Implementación de estados (loading, error, results)", "Luis", date(2026, 2, 20), date(2026, 3, 5), "28", "H", False),
    ("", 30, "Soporte bilingüe (español/inglés)", "Luis", date(2026, 2, 25), date(2026, 3, 8), "28", "H", False),
    ("", 31, "Diseño visual cyberpunk / UI final", "Luis", date(2026, 3, 1), date(2026, 3, 15), "29, 30", "H", False),
    # ── Fase 4 ──
    ("Fase 4: Pruebas y Despliegue", None, None, None, None, None, None, None, True),
    ("", 32, "Pruebas unitarias del scraper", "Marco", date(2026, 3, 10), date(2026, 3, 18), "22", "H", False),
    ("", 33, "Pruebas de integración con Groq API", "Marco", date(2026, 3, 12), date(2026, 3, 20), "23", "H", False),
    ("", 34, "Pruebas de frontend (componentes, estados)", "Luis", date(2026, 3, 15), date(2026, 3, 25), "31", "H", False),
    ("", 35, "Migración de Ollama a Groq API", "Marco", date(2026, 3, 10), date(2026, 3, 15), "23", "H", False),
    ("", 36, "Corrección de errores y timeouts", "Marco", date(2026, 3, 18), date(2026, 3, 28), "32, 33, 34", "H", False),
    ("", 37, "Configuración de despliegue (Procfile, gunicorn)", "Marco", date(2026, 3, 22), date(2026, 3, 30), "36", "H", False),
    ("", 38, "Despliegue en Railway (falló, migración a Render)", "Marco", date(2026, 3, 28), date(2026, 4, 8), "37", "H", False),
    ("", 39, "Configuración de CORS, PORT, variables de entorno", "Marco", date(2026, 4, 1), date(2026, 4, 10), "38", "H", False),
    ("", 40, "Despliegue exitoso en Render", "Marco", date(2026, 4, 5), date(2026, 4, 15), "39", "H", False),
    # ── Fase 5 ──
    ("Fase 5: Resultados (Capítulo 4)", None, None, None, None, None, None, None, True),
    ("", 41, "Pruebas de análisis con URLs reales", "Marco", date(2026, 4, 10), date(2026, 4, 22), "40", "P", False),
    ("", 42, "Evaluación de precisión del clasificador", "Marco", date(2026, 4, 15), date(2026, 4, 28), "41", "P", False),
    ("", 43, "Análisis de casos de prueba", "Tony", date(2026, 4, 18), date(2026, 4, 30), "41", "P", False),
    ("", 44, "Redacción de resultados", "Ulises", date(2026, 4, 22), date(2026, 5, 8), "42, 43", "N", False),
    # ── Fase 6 ──
    ("Fase 6: Documentación y Revisión Final", None, None, None, None, None, None, None, True),
    ("", 45, "Redacción de Marco Teórico (Cap 1) en tesis", "Ulises", date(2026, 1, 15), date(2026, 1, 30), "10", "H", False),
    ("", 46, "Redacción de Marco Metodológico (Cap 2) en tesis", "Ulises", date(2026, 2, 1), date(2026, 2, 15), "17", "H", False),
    ("", 47, "Redacción de Desarrollo (Cap 3) en tesis", "Marco", date(2026, 3, 1), date(2026, 3, 20), "31", "H", False),
    ("", 48, "Redacción de Resultados (Cap 4) en tesis", "Ulises", date(2026, 4, 20), date(2026, 5, 8), "44", "N", False),
    ("", 49, "Generación de PDF de tesis (TESIS_VERIFEX.pdf)", "Marco", date(2026, 5, 5), date(2026, 5, 15), "48", "N", False),
    ("", 50, "Revisión por asesores", "Tony", date(2026, 5, 15), date(2026, 5, 25), "49", "N", False),
    ("", 51, "Correcciones finales y entrega", "Tony", date(2026, 5, 25), date(2026, 6, 1), "50", "N", False),
]

# Assignee color map
assignee_styles = {
    "Marco": (MARCO_FILL, MARCO_FONT),
    "Luis": (LUIS_FILL, LUIS_FONT),
    "Ulises": (ULISES_FILL, ULISES_FONT),
    "Tony": (TONY_FILL, TONY_FONT),
}

status_map = {
    "H": "Completado",
    "P": "En Progreso",
    "N": "Pendiente",
}

status_fills = {
    "H": PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid"),
    "P": PatternFill(start_color="FFF8E1", end_color="FFF8E1", fill_type="solid"),
    "N": PatternFill(start_color="FFEBEE", end_color="FFEBEE", fill_type="solid"),
}
status_fonts = {
    "H": Font(name="Calibri", size=10, bold=True, color="2E7D32"),
    "P": Font(name="Calibri", size=10, bold=True, color="F57F17"),
    "N": Font(name="Calibri", size=10, bold=True, color="C62828"),
}

row = 2
for t in tasks:
    phase, task_num, task_name, assignee, start, end, dep, status, is_phase = t
    if is_phase:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
        cell = ws.cell(row=row, column=1, value=phase)
        cell.font = phase_font
        cell.fill = phase_fill
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = thin_border
        for c in range(2, 10):
            ws.cell(row=row, column=c).border = thin_border
            ws.cell(row=row, column=c).fill = phase_fill
        row += 1
        continue

    duration = (end - start).days
    status_text = status_map.get(status, "")
    a_fill, a_font = assignee_styles.get(assignee, (None, Font(name="Calibri", size=10)))

    values = [phase, task_num, task_name, assignee, start, end, duration, dep, status_text]
    for col_idx, val in enumerate(values, 1):
        cell = ws.cell(row=row, column=col_idx, value=val if val != "" else None)
        cell.font = task_font = Font(name="Calibri", size=10)
        cell.border = thin_border
        cell.alignment = center if col_idx in (2, 4, 5, 6, 7, 8, 9) else left_wrap

        if col_idx in (5, 6):
            cell.number_format = "DD/MM/YYYY"
        elif col_idx == 4:
            cell.fill = a_fill
            cell.font = a_font
        elif col_idx == 9:
            cell.fill = status_fills.get(status)
            cell.font = status_fonts.get(status)

    row += 1

# ── Legend at bottom ──
row += 2
ws.cell(row=row, column=1, value="Leyenda de asignación:").font = Font(name="Calibri", bold=True, size=11)
row += 1
legend_items = [
    ("Marco — Programación (backend, frontend, IA, deploy)", MARCO_FILL, MARCO_FONT),
    ("Luis — Frontend y documentación", LUIS_FILL, LUIS_FONT),
    ("Ulises — Documentación (redacción de tesis)", ULISES_FILL, ULISES_FONT),
    ("Tony — Documentación y revisión de lógica", TONY_FILL, TONY_FONT),
]
for text, fill, font in legend_items:
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = font
    cell.fill = fill
    cell.border = thin_border
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    for c in range(2, 5):
        ws.cell(row=row, column=c).border = thin_border
        ws.cell(row=row, column=c).fill = fill
    row += 1

# ── Frozen panes ──
ws.freeze_panes = "A2"

# ── Auto-filter ──
ws.auto_filter.ref = f"A1:I{row - 7}"

# ── Row height ──
for r in range(2, row):
    ws.row_dimensions[r].height = 24

# ── Print setup ──
ws.sheet_properties.pageSetUpPr = openpyxl.worksheet.properties.PageSetupProperties(fitToPage=True)
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.page_setup.orientation = "landscape"

output_path = f"{BASE}/Gantt_VERIFEX.xlsx"
wb.save(output_path)
print(f"Excel generado: {output_path}")


