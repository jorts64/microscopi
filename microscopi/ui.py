# microscopi/ui.py

import cv2
from .constants import LEFT_MENU_W, RIGHT_PANEL_W, BOTTOM_PANEL_H, BUTTONS, COLOR_MAP, VERSION
from .utils import draw_text


def draw_menu(canvas, state):
    for i, txt in enumerate(BUTTONS):
        y = 20 + i * 38
        color = (70, 70, 70)
        text_size = 20
        border_thickness = 0

        if txt == state.mode:
            color = (0, 160, 0)
            text_size = 24
            border_thickness = 3

        if txt == state.measure_color_name:
            color = (120, 120, 0)

        cv2.rectangle(canvas,
                      (10, y),
                      (LEFT_MENU_W - 10, y + 28),
                      color,
                      -1)

        if border_thickness:
            cv2.rectangle(canvas,
                          (10, y),
                          (LEFT_MENU_W - 10, y + 28),
                          (255, 255, 255),
                          border_thickness)

        if txt in COLOR_MAP:
            sample_color = COLOR_MAP[txt]

            cv2.rectangle(canvas,
                          (20, y + 5),
                          (LEFT_MENU_W - 20, y + 23),
                          sample_color,
                          -1)

            if state.measure_color == sample_color:
                cv2.rectangle(canvas,
                              (20, y + 5),
                              (LEFT_MENU_W - 20, y + 23),
                              (255, 255, 255),
                              3)
        else:
            draw_text(canvas, txt,
                      (18, y + 22),
                      text_size,
                      (255, 255, 255))


def draw_measures(canvas, state):
    x = canvas.shape[1] - RIGHT_PANEL_W + 10
    y = 30

    for idx, m in enumerate(state.measurements[-14:]):
        box_x = x
        box_y = y - 14

        cv2.rectangle(canvas,
                      (box_x, box_y),
                      (box_x + 14, box_y + 14),
                      (255, 255, 255),
                      2)

        if m["visible"]:
            cv2.line(canvas,
                     (box_x + 3, box_y + 7),
                     (box_x + 6, box_y + 11),
                     (255, 255, 255), 2)
            cv2.line(canvas,
                     (box_x + 6, box_y + 11),
                     (box_x + 11, box_y + 3),
                     (255, 255, 255), 2)

        txt = f"{m['type']} {m['label']} {m['text']}"
        draw_text(canvas, txt, (x + 20, y), 18, m["color"])

        y += 22


def draw_bottom_panel(canvas, state):
    h = canvas.shape[0]
    y = h - BOTTOM_PANEL_H + 25

    draw_text(canvas, state.status_message,
              (LEFT_MENU_W + 10, y), 20, (255, 255, 255))

    draw_text(canvas,
              f"v{VERSION}",
              (canvas.shape[1] - 140, h - BOTTOM_PANEL_H + 25),
              18,
              (180, 180, 180))

    if state.input_mode:
        draw_text(canvas, "> " + state.input_buffer,
                  (LEFT_MENU_W + 10, y + 28), 20, (0, 255, 255))


def hit_menu(x, y):
    for i, txt in enumerate(BUTTONS):
        by = 20 + i * 38
        if 10 <= x <= LEFT_MENU_W - 10 and by <= y <= by + 28:
            return txt
    return None
