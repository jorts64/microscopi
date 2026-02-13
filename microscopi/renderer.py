import cv2
import math

from .constants import (
    LEFT_MENU_W,
    RIGHT_PANEL_W,
    BOTTOM_PANEL_H,
)
from .ui import draw_menu, draw_measures, draw_bottom_panel
from .preview import draw_preview
from .utils import to_visual_coords


def _apply_rotation(frame, state):
    if state.rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif state.rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif state.rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame


def _draw_saved_measures(frame, state):

    base_w = state.base_width
    base_h = state.base_height

    for m in state.measurements:
        if not m.get("visible", False):
            continue

        (x1, y1), (x2, y2) = m["points"]

        x1, y1 = to_visual_coords(x1, y1, base_w, base_h, state.rotation)
        x2, y2 = to_visual_coords(x2, y2, base_w, base_h, state.rotation)


        if m["type"] == "DIS":
            cv2.line(frame, (x1, y1), (x2, y2), m["color"], 2)

        elif m["type"] == "RAD":
            r = int(math.hypot(x2 - x1, y2 - y1))
            cv2.circle(frame, (x1, y1), r, m["color"], 2)

        elif m["type"] == "SQR":
            cv2.rectangle(
                frame,
                (min(x1, x2), min(y1, y2)),
                (max(x1, x2), max(y1, y2)),
                m["color"], 2
            )

        elif m["type"] == "XY":
            x1, y1 = m["points"][0]
            cv2.circle(frame, (x1, y1), 4, m["color"], -1)


def _draw_origin(frame, state):

    if not state.origin:
        return

    ox, oy = state.origin

    # Convertir base → visual según rotación
    ox, oy = to_visual_coords(
        ox, oy,
        state.base_width,
        state.base_height,
        state.rotation
    )

    size = 8

    cv2.line(frame, (ox - size, oy), (ox + size, oy), (0, 0, 255), 2)
    cv2.line(frame, (ox, oy - size), (ox, oy + size), (0, 0, 255), 2)


def _apply_gray(frame, state):
    if state.gray:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    return frame


def _build_canvas(frame, state):
    canvas = cv2.copyMakeBorder(
        frame, 0, BOTTOM_PANEL_H,
        LEFT_MENU_W, RIGHT_PANEL_W,
        cv2.BORDER_CONSTANT,
        value=(30, 30, 30)
    )

    draw_menu(canvas, state)
    draw_measures(canvas, state)
    draw_bottom_panel(canvas, state)

    return canvas

def _draw_cursor(canvas, state):

    if not state.cursor_pos:
        return

    cx, cy = state.cursor_pos
    size = 10

    # Línea base negra (más gruesa)
    cv2.line(canvas, (cx - size, cy), (cx + size, cy), (0, 0, 0), 3)
    cv2.line(canvas, (cx, cy - size), (cx, cy + size), (0, 0, 0), 3)

    # Línea blanca encima (más fina)
    cv2.line(canvas, (cx - size, cy), (cx + size, cy), (255, 255, 255), 1)
    cv2.line(canvas, (cx, cy - size), (cx, cy + size), (255, 255, 255), 1)

def _transform_point(x, y, width, height, rotation):

    if rotation == 0:
        return x, y

    if rotation == 90:
        return height - y, x

    if rotation == 180:
        return width - x, height - y

    if rotation == 270:
        return y, width - x

    return x, y

def render(frame, state):

    frame = _apply_rotation(frame, state)

    frame = _apply_gray(frame, state)

    _draw_saved_measures(frame, state)

    _draw_grid(frame, state)

    _draw_origin(frame, state) 

    draw_preview(frame, state)

    canvas = _build_canvas(frame, state)

    _draw_cursor(canvas, state)

    return canvas


from .utils import to_visual_coords
import cv2

def _draw_grid(frame, state):

    if not state.grid_enabled:
        return

    if state.scale_mm_per_pixel is None:
        return

    base_w = state.base_width
    base_h = state.base_height

    # Paso: 0.1 pulgadas → mm
    step_mm = 0.1 * 25.4

    # Convertir mm → píxeles base
    step_px = int(step_mm / state.scale_mm_per_pixel)

    if step_px <= 0:
        return

    color = (0, 0, 255)  # rojo

    # Líneas verticales
    x = 0
    while x < base_w:
        x1, y1 = to_visual_coords(x, 0, base_w, base_h, state.rotation)
        x2, y2 = to_visual_coords(x, base_h, base_w, base_h, state.rotation)
        cv2.line(frame, (x1, y1), (x2, y2), color, 1)
        x += step_px

    # Líneas horizontales
    y = 0
    while y < base_h:
        x1, y1 = to_visual_coords(0, y, base_w, base_h, state.rotation)
        x2, y2 = to_visual_coords(base_w, y, base_w, base_h, state.rotation)
        cv2.line(frame, (x1, y1), (x2, y2), color, 1)
        y += step_px
