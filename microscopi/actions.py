import math
import time
import csv
import cv2

from .constants import MM_PER_INCH
from .utils import px_to_mm, format_mm, current_measure_text
from .i18n import _

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

