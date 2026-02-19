import cv2


class VideoSource:
    def __init__(self, device, width: int, height: int):
        self.device = device
        self.width = width
        self.height = height

        # Si es entero → dispositivo local V4L2
        if isinstance(device, int):
            self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        else:
            # URL o ruta → backend automático (FFMPEG)
            self.cap = cv2.VideoCapture(device)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source {device}")

        # Solo intentar fijar resolución en dispositivos locales
        if isinstance(device, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def read(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            raise RuntimeError("Cannot read from video source")
        return frame

    def release(self):
        if self.cap:
            self.cap.release()
