from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIAGRAMS_DIR = PROJECT_ROOT / "docs" / "diagramas"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)


WIDTH, HEIGHT = 2200, 3000
BACKGROUND = "#F7F4EE"
INK = "#20252B"
MUTED = "#5B6670"
BLUE = "#DCEAF5"
BLUE_DARK = "#2E6F95"
GREEN = "#DDEEDB"
GREEN_DARK = "#427A46"
RED = "#F6D9D3"
RED_DARK = "#A4473A"
YELLOW = "#F7EBC5"
PURPLE = "#E7DDF2"
WHITE = "#FFFFFF"


def font(size, bold=False):
    name = "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"
    return ImageFont.truetype(name, size)


title_font = font(58, True)
section_font = font(34, True)
box_font = font(27)
box_bold = font(29, True)
small_font = font(24)
tiny_font = font(21)


image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
draw = ImageDraw.Draw(image)


def centered_text(box, text, text_font, fill=INK, spacing=6):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = [draw.textbbox((0, 0), line, font=text_font)[3] for line in lines]
    total = sum(heights) + spacing * (len(lines) - 1)
    y = (y1 + y2 - total) / 2
    for line, height in zip(lines, heights):
        width = draw.textbbox((0, 0), line, font=text_font)[2]
        draw.text(((x1 + x2 - width) / 2, y), line, font=text_font, fill=fill)
        y += height + spacing


def box(x, y, w, h, text, fill=WHITE, outline=INK, radius=24, text_font=box_font):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=outline, width=4)
    centered_text((x + 18, y + 10, x + w - 18, y + h - 10), text, text_font)


def dark_box(x, y, w, h, text):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=24, fill=INK, outline=INK, width=4)
    centered_text((x + 18, y + 10, x + w - 18, y + h - 10), text, box_bold, WHITE)


def diamond(cx, cy, w, h, text, fill=YELLOW, outline=INK):
    points = [(cx, cy - h // 2), (cx + w // 2, cy), (cx, cy + h // 2), (cx - w // 2, cy)]
    draw.polygon(points, fill=fill, outline=outline)
    draw.line(points + [points[0]], fill=outline, width=4, joint="curve")
    centered_text((cx - w // 2 + 35, cy - h // 2 + 20, cx + w // 2 - 35, cy + h // 2 - 20), text, small_font)


def arrow(x1, y1, x2, y2, label=None, color=INK):
    draw.line((x1, y1, x2, y2), fill=color, width=5)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 20
    spread = 0.55
    p1 = (x2 - length * math.cos(angle - spread), y2 - length * math.sin(angle - spread))
    p2 = (x2 - length * math.cos(angle + spread), y2 - length * math.sin(angle + spread))
    draw.polygon([(x2, y2), p1, p2], fill=color)
    if label:
        lx, ly = (x1 + x2) // 2, (y1 + y2) // 2
        bounds = draw.textbbox((0, 0), label, font=tiny_font)
        pad = 8
        draw.rounded_rectangle((lx - (bounds[2] - bounds[0]) // 2 - pad, ly - 18, lx + (bounds[2] - bounds[0]) // 2 + pad, ly + 18), radius=8, fill=BACKGROUND)
        draw.text((lx - (bounds[2] - bounds[0]) // 2, ly - 13), label, font=tiny_font, fill=color)


def section(x, y, w, text, color):
    draw.rounded_rectangle((x, y, x + w, y + 58), radius=16, fill=color)
    centered_text((x, y, x + w, y + 58), text, section_font, WHITE)


# Header
centered_text((100, 50, WIDTH - 100, 150), "Diagrama de flujo del sistema de reserva de vuelos", title_font)
centered_text((150, 145, WIDTH - 150, 205), "FastAPI + SQLAlchemy + PostgreSQL | Control de concurrencia", small_font, MUTED)

# Main flow
section(100, 250, 2000, "1. Flujo general de la API", BLUE_DARK)
dark_box(820, 350, 560, 100, "Inicio")
draw.text((1050, 385), "", font=box_font)
arrow(1100, 450, 1100, 510)
box(760, 510, 680, 115, "Cliente envía una solicitud HTTP", fill=BLUE)
arrow(1100, 625, 1100, 700)
diamond(1100, 790, 780, 180, "¿Qué endpoint se solicita?")

# Branch endpoints
box(170, 930, 480, 125, "POST /seed\nInicializar datos", fill=PURPLE)
box(860, 930, 480, 125, "POST /reset\nRestablecer datos", fill=PURPLE)
box(1530, 930, 480, 125, "POST /reservar/*\nCrear reserva", fill=PURPLE)
arrow(950, 865, 410, 930, "seed")
arrow(1100, 880, 1100, 930, "reset")
arrow(1250, 865, 1770, 930, "reservar")

box(170, 1110, 480, 125, "¿Ya existen datos?\nSí: devuelve datos actuales", fill=YELLOW)
arrow(410, 1055, 410, 1110)
box(170, 1290, 480, 125, "No: crea vuelo, asiento\ny 10 usuarios", fill=GREEN)
arrow(410, 1235, 410, 1290, "No")
box(170, 1470, 480, 105, "HTTP 200 + IDs", fill=GREEN)
arrow(410, 1415, 410, 1470)

box(860, 1110, 480, 125, "Elimina reservas\ny libera asientos", fill=GREEN)
arrow(1100, 1055, 1100, 1110)
box(860, 1290, 480, 105, "HTTP 200 + confirmación", fill=GREEN)
arrow(1100, 1235, 1100, 1290)

# Reservation branch
box(1530, 1110, 480, 125, "Recibe usuario_id\ny asiento_id", fill=BLUE)
arrow(1770, 1055, 1770, 1110)
diamond(1770, 1370, 600, 180, "¿Ruta segura?")
arrow(1770, 1235, 1770, 1280)

# Secure / insecure columns
section(140, 1650, 900, "2. Reserva insegura", RED_DARK)
section(1160, 1650, 900, "3. Reserva segura/provisional", GREEN_DARK)

box(180, 1750, 820, 110, "Busca el asiento sin bloqueo", fill=RED)
arrow(1770, 1460, 590, 1750, "No")
box(180, 1920, 820, 110, "¿Existe y está DISPONIBLE?", fill=YELLOW)
arrow(590, 1860, 590, 1920)
box(180, 2090, 360, 105, "404 / 400", fill=RED)
arrow(400, 2030, 360, 2090, "No")
box(590, 2090, 410, 105, "Espera corta\n0.5 segundos", fill=RED)
arrow(700, 2030, 760, 2090, "Sí")
box(180, 2260, 820, 110, "Confirma asiento y crea reserva", fill=RED)
arrow(795, 2195, 590, 2260)
box(180, 2430, 820, 110, "Confirma transacción", fill=RED)
arrow(590, 2370, 590, 2430)
box(180, 2600, 820, 120, "HTTP 200\nPuede haber varias reservas", fill=RED, text_font=box_bold)
arrow(590, 2540, 590, 2600)

box(1200, 1750, 820, 110, "SELECT ... FOR UPDATE\nBloquea el asiento", fill=GREEN)
arrow(1770, 1460, 1610, 1750, "Sí")
box(1200, 1920, 820, 110, "¿Existe y está DISPONIBLE?", fill=YELLOW)
arrow(1610, 1860, 1610, 1920)
box(1200, 2090, 360, 105, "404 / 400", fill=RED)
arrow(1450, 2030, 1380, 2090, "No")
box(1610, 2090, 410, 105, "Mantiene bloqueo\n1 minuto (60 s)", fill=GREEN)
arrow(1720, 2030, 1810, 2090, "Sí")
box(1200, 2260, 820, 110, "Crea reserva provisional\no confirma reserva segura", fill=GREEN)
arrow(1840, 2195, 1610, 2260)
box(1200, 2430, 820, 110, "Confirma transacción y libera bloqueo", fill=GREEN)
arrow(1610, 2370, 1610, 2430)
box(1200, 2600, 820, 120, "HTTP 200\nSolo una reserva confirmada", fill=GREEN, text_font=box_bold)
arrow(1610, 2540, 1610, 2600)

# Concurrency test
section(100, 2790, 2000, "4. Prueba de concurrencia: tests/test_concurrency.py", BLUE_DARK)
box(160, 2890, 430, 85, "Reset + seed", fill=BLUE, text_font=small_font)
arrow(590, 2932, 650, 2932)
box(650, 2890, 500, 85, "Envía 5 solicitudes simultáneas", fill=BLUE, text_font=small_font)
arrow(1150, 2932, 1210, 2932)
box(1210, 2890, 390, 85, "Compara HTTP 200", fill=YELLOW, text_font=small_font)
arrow(1600, 2932, 1660, 2932)
box(1660, 2890, 380, 85, "Inseguro: >1 posible\nSeguro: 1", fill=GREEN, text_font=tiny_font)

image.save(DIAGRAMS_DIR / "diagrama_flujo_reserva_vuelos.png", "PNG", optimize=True)


def make_diagram_canvas(width, height, title, subtitle):
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    canvas_draw = ImageDraw.Draw(canvas)
    canvas_draw.text((width // 2, 55), title, font=title_font, fill=INK, anchor="ma")
    canvas_draw.text((width // 2, 125), subtitle, font=small_font, fill=MUTED, anchor="ma")
    return canvas, canvas_draw


def diagram_text(canvas_draw, bounds, text, text_font=box_font, fill=INK):
    x1, y1, x2, y2 = bounds
    lines = text.split("\n")
    heights = [canvas_draw.textbbox((0, 0), line, font=text_font)[3] for line in lines]
    total = sum(heights) + 5 * (len(lines) - 1)
    y = (y1 + y2 - total) / 2
    for line, height in zip(lines, heights):
        width = canvas_draw.textbbox((0, 0), line, font=text_font)[2]
        canvas_draw.text(((x1 + x2 - width) / 2, y), line, font=text_font, fill=fill)
        y += height + 5


def diagram_box(canvas_draw, x, y, width, height, text, fill=WHITE, outline=INK, text_font=box_font):
    canvas_draw.rounded_rectangle((x, y, x + width, y + height), radius=22, fill=fill, outline=outline, width=4)
    diagram_text(canvas_draw, (x + 18, y + 12, x + width - 18, y + height - 12), text, text_font)


def diagram_arrow(canvas_draw, x1, y1, x2, y2, color=INK):
    import math
    canvas_draw.line((x1, y1, x2, y2), fill=color, width=5)
    angle = math.atan2(y2 - y1, x2 - x1)
    length = 20
    points = [
        (x2, y2),
        (x2 - length * math.cos(angle - 0.55), y2 - length * math.sin(angle - 0.55)),
        (x2 - length * math.cos(angle + 0.55), y2 - length * math.sin(angle + 0.55)),
    ]
    canvas_draw.polygon(points, fill=color)


def create_er_diagram():
    canvas, canvas_draw = make_diagram_canvas(2400, 1700, "Diagrama entidad-relación", "Modelo transaccional de reserva de vuelos")
    diagram_box(canvas_draw, 110, 360, 470, 430, "USUARIOS\n\nPK id\nnombre\nemail UNIQUE", fill=BLUE)
    diagram_box(canvas_draw, 965, 220, 470, 470, "VUELOS\n\nPK id\norigen\ndestino\nfecha\ncapacidad", fill=PURPLE)
    diagram_box(canvas_draw, 1780, 360, 470, 500, "ASIENTOS\n\nPK id\nFK vuelo_id\nnumero\nestado\nfecha_expiracion", fill=GREEN)
    diagram_box(canvas_draw, 965, 1030, 470, 500, "RESERVAS\n\nPK id\nFK usuario_id\nFK asiento_id\nfecha_reserva\nfecha_expiracion\nestado", fill=YELLOW)
    diagram_arrow(canvas_draw, 1435, 455, 1780, 575)
    diagram_arrow(canvas_draw, 350, 790, 965, 1240)
    diagram_arrow(canvas_draw, 1780, 740, 1435, 1240)
    canvas_draw.text((1490, 490), "VUELO 1 ---- N ASIENTOS", font=small_font, fill=GREEN_DARK)
    canvas_draw.text((650, 1080), "USUARIO 1 ---- N RESERVAS", font=small_font, fill=BLUE_DARK)
    canvas_draw.text((1490, 1080), "ASIENTO 1 ---- N RESERVAS", font=small_font, fill=RED_DARK)
    diagram_box(canvas_draw, 520, 1510, 1360, 100, "Regla: un asiento solo puede tener una reserva activa PENDIENTE o CONFIRMADA", fill=RED, text_font=small_font)
    canvas.save(DIAGRAMS_DIR / "diagrama_er_reserva_vuelos.png", "PNG", optimize=True)


def create_sequence_diagram():
    canvas, canvas_draw = make_diagram_canvas(2600, 2300, "Diagrama de secuencia de reserva segura", "SELECT FOR UPDATE y bloqueo de 1 minuto")
    participants = [(170, "Cliente"), (760, "FastAPI"), (1430, "SQLAlchemy"), (2110, "PostgreSQL")]
    for x, name in participants:
        diagram_box(canvas_draw, x - 145, 220, 290, 90, name, fill=BLUE)
        canvas_draw.line((x, 310, x, 2140), fill=MUTED, width=3)
    events = [
        (420, 170, 760, "POST /reservar/seguro"),
        (560, 760, 1430, "Abrir transacción"),
        (700, 1430, 2110, "SELECT asiento FOR UPDATE"),
        (840, 2110, 1430, "Fila bloqueada"),
        (980, 1430, 2110, "Validar usuario y estado"),
        (1120, 1430, 2110, "Procesamiento simulado: 1 minuto (60 s)"),
        (1260, 1430, 2110, "UPDATE asiento = CONFIRMADO"),
        (1400, 1430, 2110, "INSERT reserva CONFIRMADA"),
        (1540, 1430, 2110, "COMMIT"),
        (1680, 760, 170, "200 Reserva confirmada"),
    ]
    for y, start, end, label in events:
        diagram_arrow(canvas_draw, start, y, end, y, BLUE_DARK)
        canvas_draw.text(((start + end) // 2, y - 35), label, font=tiny_font, fill=INK, anchor="mm")
    diagram_box(canvas_draw, 420, 2180, 1760, 90, "Las demás solicitudes esperan el desbloqueo y reciben 400 si el asiento ya no está disponible", fill=RED, text_font=small_font)
    canvas.save(DIAGRAMS_DIR / "diagrama_secuencia_reserva_vuelos.png", "PNG", optimize=True)


create_er_diagram()
create_sequence_diagram()
print("Creados: diagrama_flujo_reserva_vuelos.png, diagrama_er_reserva_vuelos.png, diagrama_secuencia_reserva_vuelos.png")