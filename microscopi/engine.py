from .actions import calibrate_with_value, add_measure_with_label
from .i18n import _


def handle_key(state, key):
    """
    Gestiona teclado.
    Devuelve True si la tecla ha sido consumida.
    """

    # ===============================
    # INPUT CALIBRACIÓN
    # ===============================
    if state.input_mode == "CAL_VALUE":

        if ord('0') <= key <= ord('9') or key == ord('.'):
            state.input_buffer += chr(key)

        elif key == 8:
            state.input_buffer = state.input_buffer[:-1]

        elif key == 13:
            try:
                calibrate_with_value(state, float(state.input_buffer))
            except:
                state.status_message = _("Invalid number")

            state.input_mode = None
            state.input_buffer = ""

        elif key == 27:
            state.input_mode = None
            state.input_buffer = ""

        return True


    # ===============================
    # INPUT LABEL
    # ===============================
    if state.input_mode == "LABEL":

        if key != -1:
            try:
                ch = chr(key)
                if ch.isprintable():
                    if len(state.input_buffer) < 8:
                        state.input_buffer += ch
            except:
                pass

        if key == 8:
            state.input_buffer = state.input_buffer[:-1]

        elif key == 13:
            add_measure_with_label(state, state.input_buffer)
            state.input_mode = None
            state.input_buffer = ""

        elif key == 27:
            state.input_mode = None
            state.input_buffer = ""

        return True


    # ===============================
    # CAMBIO UNIDADES VISUALIZACIÓN
    # ===============================
    if key == ord('v'):

        if state.current_unit == "mm":
            state.current_unit = "in"
        elif state.current_unit == "in":
            state.current_unit = "mil"
        else:
            state.current_unit = "mm"

        state.status_message = _("Display unit:") + " " + state.current_unit
        return True


    # ===============================
    # CAMBIO UNIDADES CALIBRACIÓN
    # ===============================
    if key == ord('u'):

        state.calibration_unit = (
            "in" if state.calibration_unit == "mm" else "mm"
        )

        state.status_message = _("Calibration unit:") + " " + state.calibration_unit
        return True


    return False
