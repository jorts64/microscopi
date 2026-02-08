
# ===================================================
# 
#                 (c) Jordi Orts 2026
# 
#                     Licencia MIT
#
# ===================================================

import cv2
import math
import time
import sys

# ================= CONFIG =================
VIDEO_DEVICE = 2
WIDTH, HEIGHT = 1920, 1080

LEFT_MENU_W = 120
RIGHT_PANEL_W = 300

MM_PER_INCH = 25.4
# =========================================

# ---------------- ESTADO ----------------
points = []
mode = "DIS"                 # DIS | RAD | SQR
gray = False
rotation = 0                 # 0 | 90 | 180 | 270

SCALE_MM_PER_PIXEL = None
current_unit = "mm"          # visualización
calibration_unit = "mm"      # calibración

measure_color = (0, 255, 0)
measure_color_name = "GRN"

measurements = []            # histórico

cursor_pos = None
last_frame = None
# ----------------------------------------

COLOR_MAP = {
    "RED": (0, 0, 255),
    "GRN": (0, 255, 0),
    "BLU": (255, 0, 0),
    "YEL": (0, 255, 255),
}

BUTTONS = [
    "CAL",
    "DIS",
    "RAD",
    "SQR",
    "ADD",
    "UNDO",
    "RED",
    "GRN",
    "BLU",
    "YEL",
    "GRY",
    "ROT",
    "SAVE",
    "QUIT",
]

# ================= UTILIDADES =================

def px_to_mm(px):
    if SCALE_MM_PER_PIXEL is None:
        return None
    return px * SCALE_MM_PER_PIXEL


def format_mm(mm):
    if current_unit == "mm":
        return f"{mm:.3f} mm"
    else:
        return f"{mm / MM_PER_INCH:.4f} in"


def current_measure_text():
    if len(points) != 2:
        return None

    (x1, y1), (x2, y2) = points

    if mode == "DIS":
        px = math.hypot(x2 - x1, y2 - y1)
        mm = px_to_mm(px)
        return format_mm(mm) if mm else f"{px:.1f}px"

    if mode == "RAD":
        r = math.hypot(x2 - x1, y2 - y1)
        mm = px_to_mm(2 * r)
        return format_mm(mm) if mm else f"{2*r:.1f}px"

    if mode == "SQR":
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        mm_w = px_to_mm(w)
        mm_h = px_to_mm(h)
        if mm_w and mm_h:
            return f"{format_mm(mm_w)} x {format_mm(mm_h)}"
        return f"{w:.1f}px x {h:.1f}px"

    return None


def add_measure():
    global points
    text = current_measure_text()
    if not text:
        return

    label = input("Etiqueta (max 5): ").strip()[:5]

    measurements.append({
        "type": mode,
        "label": label,
        "text": text,
        "color": measure_color
    })
    points = []


def undo_measure():
    if measurements:
        measurements.pop()


# ================= UI =================

def draw_menu(canvas):
    for i, txt in enumerate(BUTTONS):
        y = 20 + i * 38
        color = (70, 70, 70)

        if txt == mode:
            color = (0, 120, 0)

        if txt == measure_color_name:
            color = (120, 120, 0)

        cv2.rectangle(canvas,
                      (10, y),
                      (LEFT_MENU_W - 10, y + 28),
                      color, -1)

        cv2.putText(canvas, txt,
                    (18, y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 2)


def draw_measures(canvas):
    x = canvas.shape[1] - RIGHT_PANEL_W + 10
    y = 30

    cv2.putText(canvas, "MEDIDAS",
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2)
    y += 26

    for i, m in enumerate(measurements[-14:]):
        txt = f"{i+1:02d} {m['type']} {m['label']:5} {m['text']}"
        cv2.putText(canvas, txt,
                    (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    m["color"], 2)
        y += 20


def hit_menu(x, y):
    for i, txt in enumerate(BUTTONS):
        by = 20 + i * 38
        if 10 <= x <= LEFT_MENU_W - 10 and by <= y <= by + 28:
            return txt
    return None


# ================= MOUSE =================

def mouse(event, x, y, flags, param):
    global points, mode, gray, rotation
    global measure_color, measure_color_name, cursor_pos

    cursor_pos = (x, y)

    if event == cv2.EVENT_LBUTTONDOWN:
        cmd = hit_menu(x, y)
        if cmd:
            if cmd == "CAL":
                calibrate()
            elif cmd in ("DIS", "RAD", "SQR"):
                mode = cmd
            elif cmd == "ADD":
                add_measure()
            elif cmd == "UNDO":
                undo_measure()
            elif cmd in COLOR_MAP:
                measure_color = COLOR_MAP[cmd]
                measure_color_name = cmd
            elif cmd == "GRY":
                gray = not gray
            elif cmd == "ROT":
                rotation = (rotation + 90) % 360
            elif cmd == "SAVE":
                save_image()
            elif cmd == "QUIT":
                quit_app()
            return

        points.append((x - LEFT_MENU_W, y))
        if len(points) > 2:
            points = []


# ================= ACCIONES =================

def calibrate():
    global SCALE_MM_PER_PIXEL, points
    if len(points) != 2:
        return

    px = math.hypot(points[1][0] - points[0][0],
                    points[1][1] - points[0][1])

    ref = float(input(f"Distancia real ({calibration_unit}): "))
    ref_mm = ref * MM_PER_INCH if calibration_unit == "in" else ref

    SCALE_MM_PER_PIXEL = ref_mm / px
    print(f"📐 Calibrado: {SCALE_MM_PER_PIXEL:.6f} mm/px")
    points = []


def save_image():
    global last_frame
    ts = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(f"captura_{ts}.png", last_frame)
    print("💾 Captura guardada")


def quit_app():
    cap.release()
    cv2.destroyAllWindows()
    sys.exit(0)


# ================= CÁMARA =================

cap = cv2.VideoCapture(VIDEO_DEVICE, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not cap.isOpened():
    raise RuntimeError("No se puede abrir la cámara")

cv2.namedWindow("Microscopio PRO", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Microscopio PRO", mouse)

print("v = unidad visualización | u = unidad calibración | x = borrar medidas")

# ================= LOOP =================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if rotation == 90:
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 270:
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

    if gray:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    canvas = cv2.copyMakeBorder(
        frame, 0, 0,
        LEFT_MENU_W, RIGHT_PANEL_W,
        cv2.BORDER_CONSTANT,
        value=(30, 30, 30)
    )

    draw_menu(canvas)
    draw_measures(canvas)

    # ----- dibujo en vivo + valor -----
    if len(points) == 2:
        (x1, y1), (x2, y2) = points
        x1 += LEFT_MENU_W
        x2 += LEFT_MENU_W

        text = current_measure_text()

        if mode == "DIS":
            cv2.line(canvas, (x1, y1), (x2, y2), measure_color, 2)

        elif mode == "RAD":
            r = int(math.hypot(x2 - x1, y2 - y1))
            cv2.circle(canvas, (x1, y1), r, measure_color, 2)

        elif mode == "SQR":
            cv2.rectangle(canvas,
                          (min(x1, x2), min(y1, y2)),
                          (max(x1, x2), max(y1, y2)),
                          measure_color, 2)

        if text:
            cv2.putText(canvas, text,
                        (x2 + 6, y2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, measure_color, 2)

    # ----- cursor cruz -----
    if cursor_pos:
        cx, cy = cursor_pos
        size = 10
        cv2.line(canvas, (cx - size, cy), (cx + size, cy), (200,200,200), 1)
        cv2.line(canvas, (cx, cy - size), (cx, cy + size), (200,200,200), 1)

    last_frame = canvas.copy()
    cv2.imshow("Microscopio PRO", canvas)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        quit_app()
    elif k == ord('v'):
        current_unit = "in" if current_unit == "mm" else "mm"
    elif k == ord('u'):
        calibration_unit = "in" if calibration_unit == "mm" else "mm"
        print("Unidad calibración:", calibration_unit)
    elif k == ord('x'):
        measurements.clear()
    elif k == ord('c'):
        points = []

cap.release()
cv2.destroyAllWindows()
