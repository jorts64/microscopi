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
from .actions import (
    calibrate_with_value,
    add_measure_with_label,
    undo_measure,
    save_png,
    save_export,
)
from .engine import handle_key

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

        # Delegar teclado al engine
        if handle_key(state, k):
            continue

        # ESC global (si no está en input_mode)
        if k == 27:
            break


    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
