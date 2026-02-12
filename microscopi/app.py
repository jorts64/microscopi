#!/usr/bin/env python3
import cv2
import math
import time
import argparse
import tkinter as tk
from tkinter import simpledialog
import csv

from .config import Config
from .i18n import _
from .state import AppState
from .utils import px_to_mm, format_mm, current_measure_text, draw_text
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
from .video import VideoSource
from .dialogs import ask_string, show_error
from .renderer import render
from .preview import draw_preview
from .user_config import load_user_config, save_user_config
from .utils import to_base_coords

# ================= CONSTANTES =================
WINDOW_NAME = f"Microscopi {VERSION}"

# ================= ARGPARSE =================

def parse_args():
    parser = argparse.ArgumentParser(prog="microscopi")

    parser.add_argument("-d", "--device", type=int)
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

        # Convertir coordenadas visuales a base
        px, py = to_base_coords(
            px,
            py,
            state.base_width,
            state.base_height,
            state.rotation
        )

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

    user_conf = load_user_config()

    # --- Resolver video_device ---
    if config.video_device is not None:
        final_device = config.video_device
    elif "video_device" in user_conf:
        final_device = user_conf["video_device"]
    else:
        final_device = 2  # default seguro

    # --- Resolver resolución ---
    if config.width and config.height:
        final_width = config.width
        final_height = config.height
    elif "resolution" in user_conf:
        final_width = user_conf["resolution"]["width"]
        final_height = user_conf["resolution"]["height"]
    else:
        final_width = 1920
        final_height = 1080

    # Aplicar al config
    config.video_device = final_device
    config.width = final_width
    config.height = final_height

    state = AppState(config)

    try:
        video = VideoSource(
            config.video_device,
            config.width,
            config.height
        )

    except RuntimeError:
        show_error(
            _("Camera error"),
            _("Cannot open video device") + f" {config.video_device}"
        )
        return

    # Guardar configuración válida
    save_user_config({
        "video_device": config.video_device,
        "resolution": {
            "width": config.width,
            "height": config.height
        }
    })

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW_NAME, mouse, state)

    while True:
        if state.quit:
            break

        try:
            frame = video.read()
        except RuntimeError:
            show_error(
                _("Camera error"),
                _("Cannot read from video device")
            )
            video.release()
            return

        # Guardar dimensiones base si aún no están
        if not hasattr(state, "base_width"):
            state.base_height, state.base_width = frame.shape[:2]
            
        canvas = render(frame, state)

        state.last_frame = canvas.copy()
        cv2.imshow(WINDOW_NAME, canvas)

        k = cv2.waitKey(1)

        if handle_key(state, k):
            continue

        if k == 27:
            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
