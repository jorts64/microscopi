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
from .input import mouse

# ================= CONSTANTES =================
WINDOW_NAME = f"Microscopi {VERSION}"

# ================= ARGPARSE =================

def parse_args():
    parser = argparse.ArgumentParser(prog="microscopi")

    parser.add_argument("-d", "--device", type=str, default=None)
    parser.add_argument("-r", "--resolution", type=str)
    parser.add_argument("-n", "--decimals", type=int, default=3)
    parser.add_argument("--unit", choices=["mm", "in"], default="mm")
    parser.add_argument("--no-draw-live", action="store_true")

    args = parser.parse_args()

    width, height = 1920, 1080
    if args.resolution:
        width, height = map(int, args.resolution.lower().split("x"))

    if args.device is not None and args.device.isdigit():
        device = int(args.device)
    else:
        device = args.device

    return Config(
        video_device=device,
        width=width,
        height=height,
        decimals=args.decimals,
        default_unit=args.unit,
        draw_live=not args.no_draw_live,
    )


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
