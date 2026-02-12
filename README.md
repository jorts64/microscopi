# Microscopi

![GitHub release](https://img.shields.io/github/v/release/jorts64/microscopi)  
![License](https://img.shields.io/badge/license-MIT-green)  
![Debian](https://img.shields.io/badge/Debian-13%20Trixie-red)  
![Python](https://img.shields.io/badge/python-3.11%2B-blue)  
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)

![](microscopi.png)

**Microscopi** is an open-source digital microscope measurement tool for Linux.

It provides real-time calibrated measurement, coordinate export and PCB-oriented workflows using any V4L2 compatible camera (USB microscopes, webcams, etc.).

Designed for precision work in electronics, mechanical prototyping and laboratory environments.

---

## ✨ Features

### 📐 Measurement Modes

- **DIS** – Distance  
- **RAD** – Radius / Diameter  
- **SQR** – Rectangle  
- **XY** – Point coordinates  

### 🎯 Calibration

- Calibration in mm or inches  
- Display units: mm, inch, mil (thousandth of an inch)  
- Configurable precision (0.0 / 0.00 / 0.000)  
- Define custom origin (0,0)  

### 🔄 Rotation

- 0° / 90° / 180° / 270°  
- Geometrically consistent model/view separation  
- Measurements remain accurate under any rotation  

### 🖥 Visual Features

- Optional grayscale mode (image only, overlays remain in color)  
- Persistent overlays with visibility toggle  
- UTF-8 text rendering (OpenCV FreeType)  
- Real-time preview while measuring  

### ⌨ Keyboard Shortcuts

- **D / C / S / X** → measurement modes  
- **R** → rotate  
- **G** → grayscale toggle  
- **Z** → undo  
- **V / U** → unit switching  

### 💾 Persistence

- Remembers last video device  
- Remembers last resolution  
- Stored in `~/.config/microscopi/config.json`  

### 📤 Export Modes

- **PNG** – image only  
- **3D** – PNG + CSV (mm)  
- **PCB** – PNG + CSV (mil)  

CSV export includes:

- Label  
- Measurement type  
- Color code  
- Coordinates (relative to origin)  
- Measured value  

---

## 📦 Dependencies (Debian)

Microscopi requires:

- python3  
- python3-opencv (with FreeType support)  
- python3-tk  
- gettext  

Install with:

    sudo apt install python3 python3-opencv python3-tk gettext

If OpenCV was built without FreeType support, the program will not start.

---

## Installation

### Debian / Ubuntu

Download the `.deb` from Releases and install:

    sudo dpkg -i microscopi_0.11.1-1_amd64.deb
    sudo apt -f install

### From source

    pip install .

---

## 🚀 Running

Basic usage:

    python3 -m microscopi

With custom parameters:

    python3 -m microscopi -d 2 -r 1280x720 -n 2 --unit mm

### Command line options

| Option | Description |
|--------|------------|
| `-d` | Video device index |
| `-r` | Resolution (e.g. 1280x720) |
| `-n` | Number of decimals |
| `--unit` | Default unit (mm or in) |
| `--no-draw-live` | Disable live preview drawing |

If no device or resolution is specified, Microscopi will use the last working configuration.

---

## 📏 Typical Workflow

1. Rotate image if needed.  
2. Calibrate using a known reference.  
3. Select measurement mode (DIS / RAD / SQR / XY).  
4. Add measurement with label.  
5. Optionally define origin (0,0).  
6. Export using PNG / 3D / PCB.  

---

## 📂 Export Details

### PNG

Saves the current image with visible overlays.

### 3D

Saves:
- PNG image  
- CSV file in millimeters (1 decimal)  
- Coordinates relative to origin  

### PCB

Saves:
- PNG image  
- CSV file in mil (integer precision)  
- Coordinates relative to origin  

---

## 📄 CSV Format

CSV contains:

    label,type,color,x1,y1,x2,y2,value

Coordinates are:
- Relative to defined origin  
- In mm (3D mode)  
- In mil (PCB mode)  

---

## 🧱 Architecture (0.11.x)

Microscopi 0.11 introduced a modular architecture:

- `video.py` → video source abstraction  
- `renderer.py` → rendering pipeline  
- `preview.py` → live preview layer  
- `state.py` → application model  
- `actions.py` → measurement and export logic  

Rendering separates:

- Model coordinates (base system)  
- Visual coordinates (rotated system)  

This ensures geometrical consistency and future extensibility.

---

## 📌 Version

Current version: **0.11.1**

---

## 📜 License

MIT License

---

## Roadmap

- [x] Debian package  
- [x] i18n  
- [x] CSV export  
- [x] Geometrically consistent rotation  
- [ ] Measurement editing  
- [ ] Hardware profile presets  
- [ ] Session save/load  
- [ ] Debian official submission  

---

## 👤 Author

Created by Jordi Orts  
Open source contribution inspired by the Debian community.
