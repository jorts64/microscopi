# microscopi/state.py

class AppState:
    def __init__(self, config):
        self.config = config

        self.points = []
        self.mode = "DIS"
        self.gray = False
        self.rotation = 0

        self.scale_mm_per_pixel = None
        self.current_unit = config.default_unit
        self.calibration_unit = "mm"

        self.measure_color = (0, 255, 0)
        self.measure_color_name = "GRN"

        self.measurements = []

        self.cursor_pos = None
        self.last_frame = None
        self.quit = False

        self.status_message = ""
        self.input_mode = None
        self.input_buffer = ""

        self.origin = None  # Coordenada origen en píxeles
