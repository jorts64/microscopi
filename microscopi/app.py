#!/usr/bin/env python3
import cv2
import math
import time
import argparse
import tkinter as tk
from tkinter import simpledialog
import csv

from microscopi.config import Config
from microscopi.i18n import _
from microscopi.state import AppState
from microscopi.utils import px_to_mm, format_mm, current_measure_text, draw_text
from .constants import (
    LEFT_MENU_W,
    RIGHT_PANEL_W,
    BOTTOM_PANEL_H,
    MM_PER_INCH,
    VERSION,
    COLOR_MAP,
    BUTTONS,
)
from .ui import draw_menu, draw_measures, draw_bottom_panel, hit_menu

# ================= CONSTANTES =================
WINDOW_NAME = f"Microscopi {VERSION}"

# ================= ARGPARSE =================

def parse_args():
    parser = argparse.ArgumentParser(prog="microscopi")

    parser.add_argument("-d", "--device", type=int, default=2)
    parser.add_argument("-r", "--resolution", type=str)
    parser.add_argument("-n", "--decimals", type=int, default=3)
    parser.add_argument("--unit", choices=["mm", "in"], default="mm")
    parser.add_argument("--no-draw-live", action="store_true")

    args = parser.parse_args()

    width, height = 1920, 1080
    if args.resolution:
        width, height = map(int, args.resolution.lower().split("x"))

    return Config(
        video_device=args.device,
        width=width,
        height=height,
        decimals=args.decimals,
        default_unit=args.unit,
        draw_live=not args.no_draw_live,
    )

# ================= UTILIDADES =================

def ask_string(title, prompt):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    value = simpledialog.askstring(title, prompt, parent=root)
    root.destroy()
    return value

# ================= ACCIONES =================

def calibrate_with_value(state, value):
    (x1, y1), (x2, y2) = state.points
    px = math.hypot(x2 - x1, y2 - y1)

    ref_mm = value * MM_PER_INCH if state.calibration_unit == "in" else value
    state.scale_mm_per_pixel = ref_mm / px

    state.status_message = _("Calibrated:") + f" {state.scale_mm_per_pixel:.6f} mm/px"
    state.points = []

def add_measure_with_label(state, label):

    if state.mode == "XY" and len(state.points) == 1:
        x, y = state.points[0]

        if state.origin:
            ox, oy = state.origin
            dx = x - ox
            dy = y - oy
        else:
            dx, dy = x, y

        mmx = px_to_mm(state, dx)
        mmy = px_to_mm(state, dy)

        if mmx is not None:
            text = f"({format_mm(state, mmx)}, {format_mm(state, mmy)})"
        else:
            text = f"({dx}px, {dy}px)"

        state.measurements.append({
            "type": "XY",
            "label": label[:8],
            "text": text,
            "color": state.measure_color,
            "color_name": state.measure_color_name,
            "points": [(x, y), (x, y)],
            "visible": True
        })

        state.points = []
        state.status_message = _("Measure added")
        return

    text = current_measure_text(state)
    if not text:
        return

    state.measurements.append({
        "type": state.mode,
        "label": label[:8],
        "text": text,
        "color": state.measure_color,
        "color_name": state.measure_color_name,
        "points": state.points.copy(),   # NUEVO
        "visible": True                  # NUEVO
    })

    state.points = []
    state.status_message = _("Measure added")

def undo_measure(state):
    if state.measurements:
        state.measurements.pop()

def save_png(state):
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"captura_{ts}.png"
    cv2.imwrite(filename, state.last_frame)
    state.status_message = _("PNG saved")

def save_export(state, mode):
    if state.origin is None:
        state.status_message = _("Origin not defined")
        return

    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"medidas_{mode}_{ts}.csv"

    ox, oy = state.origin

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "label", "type", "color",
            "x1", "y1", "x2", "y2",
            "value"
        ])

        for m in state.measurements:
            if not m.get("visible", False):
                continue

            (x1, y1), (x2, y2) = m["points"]

            # relativo a origen
            dx1 = x1 - ox
            dy1 = y1 - oy
            dx2 = x2 - ox
            dy2 = y2 - oy

            # convertir a mm
            mm1x = px_to_mm(state, dx1)
            mm1y = px_to_mm(state, dy1)
            mm2x = px_to_mm(state, dx2)
            mm2y = px_to_mm(state, dy2)

            if mode == "3D":
                writer.writerow([
                    m["label"],
                    m["type"],
                    m["color_name"],
                    round(mm1x, 1), round(mm1y, 1),
                    round(mm2x, 1), round(mm2y, 1),
                    m["text"]
                ])

            elif mode == "PCB":
                # mm -> mil
                mil1x = (mm1x / MM_PER_INCH) * 1000
                mil1y = (mm1y / MM_PER_INCH) * 1000
                mil2x = (mm2x / MM_PER_INCH) * 1000
                mil2y = (mm2y / MM_PER_INCH) * 1000

                writer.writerow([
                    m["label"],
                    m["type"],
                    m["color_name"],
                    round(mil1x), round(mil1y),
                    round(mil2x), round(mil2y),
                    m["text"]
                ])

    save_png(state)
    state.status_message = _("Export saved")

# ================= MOUSE =================

def mouse(event, x, y, flags, state):
    state.cursor_pos = (x, y)

    if event == cv2.EVENT_LBUTTONDOWN:
        cmd = hit_menu(x, y)

        # --- CLICK EN PANEL DERECHO ---
        if state.last_frame is not None:
            panel_x_start = state.last_frame.shape[1] - RIGHT_PANEL_W

            if x >= panel_x_start:
                rel_y = y - 30
                idx = rel_y // 22

                if 0 <= idx < len(state.measurements):
                    state.measurements[idx]["visible"] = \
                        not state.measurements[idx]["visible"]
                return

        if cmd:
            if cmd == "CAL":
                if len(state.points) == 2:
                    value = ask_string(_("Calibration"), _("Enter real distance"))
                    if value:
                        try:
                            calibrate_with_value(state, float(value))
                        except:
                            state.status_message = _("Invalid number")
                else:
                    state.status_message = _("Select two points first")

            elif cmd in ("0.0", "0.00", "0.000"):
                state.config.decimals = len(cmd) - 2
                state.status_message = _("Precision:") + " " + cmd

            elif cmd in ("DIS", "RAD", "SQR", "XY"):
                state.mode = cmd

            elif cmd == "ADD":
                if (state.mode == "XY" and len(state.points) == 1) or \
                   (state.mode != "XY" and len(state.points) == 2):

                    label = ask_string(_("New measure"), _("Enter label"))
                    if label:
                        add_measure_with_label(state, label)
                else:
                    state.status_message = _("Select required points first")

            elif cmd == "UNDO":
                undo_measure(state)

            elif cmd in COLOR_MAP:
                state.measure_color = COLOR_MAP[cmd]
                state.measure_color_name = cmd

            elif cmd == "GRY":
                state.gray = not state.gray

            elif cmd == "ROT":
                state.rotation = (state.rotation + 90) % 360

            elif cmd == "PNG":
                save_png(state)

            elif cmd == "(0,0)":
                if state.mode == "XY" and len(state.points) == 1:
                    state.origin = state.points[0]
                    state.status_message = _("Origin set")
                    state.points = []
                else:
                    state.status_message = _("Select a point in XY mode first")

            elif cmd == "3D":
                save_export(state, "3D")

            elif cmd == "PCB":
                save_export(state, "PCB")

            elif cmd == "QUIT":
                state.quit = True

            return

        px = x - LEFT_MENU_W
        py = y

        if state.mode == "XY":
            state.points = [(px, py)]
            state.status_message = _("Point selected")
            return

        state.points.append((px, py))

        if len(state.points) > 2:
            state.points = []

        if len(state.points) > 2:
            state.points = []

# ================= MAIN =================

def main():
    config = parse_args()
    state = AppState(config)

    cap = cv2.VideoCapture(config.video_device, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(_("Error: Cannot open video device") + f" {config.video_device}")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, mouse, state)

    while True:
        if state.quit:
            break

        ret, frame = cap.read()
        if not ret or frame is None:
            print(_("Error: Cannot read from video device"))
            cap.release()
            return

        if state.rotation == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif state.rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif state.rotation == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # --- Redibujar medidas guardadas activas SOBRE frame ---
        for m in state.measurements:
            if not m.get("visible", False):
                continue

            (x1, y1), (x2, y2) = m["points"]

            if m["type"] == "DIS":
                cv2.line(frame, (x1, y1), (x2, y2),
                         m["color"], 2)

            elif m["type"] == "RAD":
                r = int(math.hypot(x2 - x1, y2 - y1))
                cv2.circle(frame, (x1, y1), r,
                           m["color"], 2)

            elif m["type"] == "SQR":
                cv2.rectangle(frame,
                              (min(x1, x2), min(y1, y2)),
                              (max(x1, x2), max(y1, y2)),
                              m["color"], 2)

            elif m["type"] == "XY":
                x1, y1 = m["points"][0]
                cv2.circle(frame, (x1, y1), 4, m["color"], -1)

        # --- Dibujar origen ---
        if state.origin:
            ox, oy = state.origin
            cv2.line(frame, (ox - 8, oy), (ox + 8, oy), (0, 0, 255), 2)
            cv2.line(frame, (ox, oy - 8), (ox, oy + 8), (0, 0, 255), 2)

        if state.gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        canvas = cv2.copyMakeBorder(
            frame, 0, BOTTOM_PANEL_H,
            LEFT_MENU_W, RIGHT_PANEL_W,
            cv2.BORDER_CONSTANT,
            value=(30, 30, 30)
        )

        draw_menu(canvas, state)
        draw_measures(canvas, state)
        draw_bottom_panel(canvas, state)

        # Dibujo dinámico (preview en tiempo real)
        if state.config.draw_live and len(state.points) >= 1 and state.cursor_pos:

            x1, y1 = state.points[0]

            if len(state.points) == 2:
                x2, y2 = state.points[1]
            else:
                # Segundo punto provisional = cursor
                cx, cy = state.cursor_pos
                x2 = cx - LEFT_MENU_W
                y2 = cy

            # Ajustar desplazamiento para canvas
            x1 += LEFT_MENU_W
            x2 += LEFT_MENU_W

            if state.mode == "DIS":
                cv2.line(canvas, (x1, y1), (x2, y2),
                         state.measure_color, 2)

            elif state.mode == "RAD":
                r = int(math.hypot(x2 - x1, y2 - y1))
                cv2.circle(canvas, (x1, y1), r,
                           state.measure_color, 2)

            elif state.mode == "SQR":
                cv2.rectangle(canvas,
                              (min(x1, x2), min(y1, y2)),
                              (max(x1, x2), max(y1, y2)),
                              state.measure_color, 2)

            # Mostrar valor si ya hay calibración
            if len(state.points) == 2:
                text = current_measure_text(state)
                if text:
                    draw_text(canvas, text,
                              (x2 + 6, y2),
                              20, state.measure_color)

        # Cruz cursor
        if state.cursor_pos:
            cx, cy = state.cursor_pos
            size = 10
            cv2.line(canvas, (cx - size, cy), (cx + size, cy), (200, 200, 200), 1)
            cv2.line(canvas, (cx, cy - size), (cx, cy + size), (200, 200, 200), 1)

        state.last_frame = canvas.copy()
        cv2.imshow(WINDOW_NAME, canvas)

        k = cv2.waitKey(1) 

        # ==== INPUT CALIBRACIÓN ====
        if state.input_mode == "CAL_VALUE":
            if ord('0') <= k <= ord('9') or k == ord('.'):
                state.input_buffer += chr(k)
            elif k == 8:
                state.input_buffer = state.input_buffer[:-1]
            elif k == 13:
                try:
                    calibrate_with_value(state, float(state.input_buffer))
                except:
                    state.status_message = _("Invalid number")
                state.input_mode = None
                state.input_buffer = ""
            elif k == 27:
                state.input_mode = None
                state.input_buffer = ""
            continue

        # ==== INPUT LABEL ====
        if state.input_mode == "LABEL":
            if k != -1:
                try:
                    ch = chr(k)
                    if ch.isprintable():
                        if len(state.input_buffer) < 5:
                            state.input_buffer += ch
                except:
                    pass
            if k == 8:
                state.input_buffer = state.input_buffer[:-1]
            elif k == 13:
                add_measure_with_label(state, state.input_buffer)
                state.input_mode = None
                state.input_buffer = ""
            elif k == 27:
                state.input_mode = None
                state.input_buffer = ""
            continue

        # Cambio unidades
        if k == ord('v'):
            if state.current_unit == "mm":
                state.current_unit = "in"
            elif state.current_unit == "in":
                state.current_unit = "mil"
            else:
                state.current_unit = "mm"

            state.status_message = _("Display unit:") + " " + state.current_unit

        elif k == ord('u'):
            state.calibration_unit = (
                "in" if state.calibration_unit == "mm" else "mm"
            )
            state.status_message = _("Calibration unit:") + " " + state.calibration_unit

        elif k == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
