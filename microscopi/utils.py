# microscopi/utils.py

import math
import cv2
from .constants import MM_PER_INCH

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

try:
    ft = cv2.freetype.createFreeType2()
    ft.loadFontData(FONT_PATH, 0)
except Exception:
    raise RuntimeError(
        "Microscopi requires OpenCV built with FreeType support"
    )

def draw_text(img, text, pos, size, color):
    ft.putText(img, text, pos, size, color, -1, cv2.LINE_AA, True)

def px_to_mm(state, px):
    if state.scale_mm_per_pixel is None:
        return None
    return px * state.scale_mm_per_pixel


def format_mm(state, mm):
    d = state.config.decimals

    if state.current_unit == "mm":
        return f"{mm:.{d}f} mm"

    elif state.current_unit == "in":
        return f"{mm / MM_PER_INCH:.{d}f} in"

    elif state.current_unit == "mil":
        mil = (mm / MM_PER_INCH) * 1000
        return f"{mil:.{d}f} mil"


def current_measure_text(state):
    if len(state.points) != 2:
        return None

    (x1, y1), (x2, y2) = state.points

    if state.mode == "DIS":
        px = math.hypot(x2 - x1, y2 - y1)
        mm = px_to_mm(state, px)
        return format_mm(state, mm) if mm else f"{px:.1f}px"

    if state.mode == "RAD":
        r = math.hypot(x2 - x1, y2 - y1)
        mm = px_to_mm(state, 2 * r)
        return format_mm(state, mm) if mm else f"{2*r:.1f}px"

    if state.mode == "SQR":
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        mm_w = px_to_mm(state, w)
        mm_h = px_to_mm(state, h)
        if mm_w and mm_h:
            return f"{format_mm(state, mm_w)} x {format_mm(state, mm_h)}"
        return f"{w:.1f}px x {h:.1f}px"

    return None

def to_base_coords(x, y, base_width, base_height, rotation):

    if rotation == 0:
        return x, y

    if rotation == 90:
        xb = y
        yb = base_height - 1 - x
        return xb, yb

    if rotation == 180:
        xb = base_width - 1 - x
        yb = base_height - 1 - y
        return xb, yb

    if rotation == 270:
        xb = base_width - 1 - y
        yb = x
        return xb, yb

    return x, y

def to_visual_coords(x, y, base_width, base_height, rotation):

    if rotation == 0:
        return x, y

    if rotation == 90:
        # ROTATE_90_CLOCKWISE
        return base_height - 1 - y, x

    if rotation == 180:
        return base_width - 1 - x, base_height - 1 - y

    if rotation == 270:
        return y, base_width - 1 - x

    return x, y
