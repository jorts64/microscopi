import cv2
import math

from .constants import LEFT_MENU_W
from .utils import current_measure_text, draw_text
from .utils import to_visual_coords


def draw_preview(canvas, state):

    base_w = state.base_width
    base_h = state.base_height

    if not state.config.draw_live:
        return

    if len(state.points) < 1 or not state.cursor_pos:
        return

    x1, y1 = state.points[0]

    # Punto 1 siempre es base → convertir
    x1, y1 = to_visual_coords(
        x1, y1,
        state.base_width,
        state.base_height,
        state.rotation
    )

    if len(state.points) == 2:
        # Punto 2 también base → convertir
        x2, y2 = state.points[1]
        x2, y2 = to_visual_coords(
            x2, y2,
            state.base_width,
            state.base_height,
            state.rotation
        )
    else:
        # Cursor ya está en visual
        cx, cy = state.cursor_pos
        x2 = cx - LEFT_MENU_W
        y2 = cy

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

    if len(state.points) == 2:
        text = current_measure_text(state)
        if text:
            draw_text(canvas, text,
                      (x2 + 6, y2),
                      20, state.measure_color)
