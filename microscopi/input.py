import cv2
from .constants import LEFT_MENU_W, RIGHT_PANEL_W
from .ui import hit_menu
from .actions import (
    calibrate_with_value,
    add_measure_with_label,
    undo_measure,
    save_png,
    save_export,
)
from .i18n import _
from .utils import to_base_coords


def mouse(event, x, y, flags, state):

    state.cursor_pos = (x, y)

    if event != cv2.EVENT_LBUTTONDOWN:
        return

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
        _handle_menu_command(cmd, state)
        return

    # --- CLICK EN ÁREA DE VÍDEO ---

    px = x - LEFT_MENU_W
    py = y

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


def _handle_menu_command(cmd, state):

    if cmd == "CAL":
        if len(state.points) == 2:
            from tkinter import simpledialog, Tk
            root = Tk()
            root.withdraw()
            value = simpledialog.askstring(_("Calibration"),
                                           _("Enter real distance"))
            root.destroy()

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

            from tkinter import simpledialog, Tk
            root = Tk()
            root.withdraw()
            label = simpledialog.askstring(_("New measure"),
                                           _("Enter label"))
            root.destroy()

            if label:
                add_measure_with_label(state, label)
        else:
            state.status_message = _("Select required points first")

    elif cmd == "UNDO":
        undo_measure(state)

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
