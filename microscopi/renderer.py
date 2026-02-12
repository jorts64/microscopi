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
    if state.origin:
        ox, oy = state.origin
        cv2.line(frame, (ox - 8, oy), (ox + 8, oy), (0, 0, 255), 2)
        cv2.line(frame, (ox, oy - 8), (ox, oy + 8), (0, 0, 255), 2)


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
    if state.cursor_pos:
        cx, cy = state.cursor_pos
        size = 10
        cv2.line(canvas, (cx - size, cy), (cx + size, cy), (200, 200, 200), 1)
        cv2.line(canvas, (cx, cy - size), (cx, cy + size), (200, 200, 200), 1)

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

    draw_preview(frame, state)

    canvas = _build_canvas(frame, state)

    _draw_cursor(canvas, state)

    return canvas
