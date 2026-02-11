# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and follows semantic
versioning principles.

------------------------------------------------------------------------

## \[0.9.0\] - 2026-02-11

### Added

-   Real-time measurement modes:
    -   DIS (distance)
    -   RAD (radius/diameter)
    -   SQR (rectangle)
    -   XY (coordinate point)
-   Calibration in millimeters and inches
-   Display units: mm, in, mil
-   Configurable decimal precision (0.0 / 0.00 / 0.000)
-   Custom origin (0,0) definition
-   Persistent overlay system with visibility toggle (checkbox per
    measure)
-   Export modes:
    -   PNG (image only)
    -   3D (PNG + CSV in millimeters)
    -   PCB (PNG + CSV in mil)
-   CSV export includes:
    -   Label
    -   Measurement type
    -   Color code
    -   Relative coordinates
    -   Measured value
-   UTF-8 rendering using OpenCV FreeType
-   Rotation support (0°, 90°, 180°, 270°)
-   Version display in window title and status bar
-   Proper video device error handling
-   Internationalization framework (i18n)

### Improved

-   Cleaner video device detection and error handling
-   Robust origin definition logic
-   Consistent measurement storage including coordinates and color
-   Improved UI highlighting of active measurement mode

### Known Limitations

-   Changing rotation after measurements may visually misalign overlays
-   Calibration must be performed before exporting accurate values

------------------------------------------------------------------------

Future versions will focus on packaging for Debian/Ubuntu and UX
refinements.
