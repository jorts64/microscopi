from dataclasses import dataclass

@dataclass
class Config:
    video_device: int = 2
    width: int = 1920
    height: int = 1080
    decimals: int = 3
    default_unit: str = "mm"
    draw_live: bool = True
