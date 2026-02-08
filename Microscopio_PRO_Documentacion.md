# Microscopio PRO – Documentación del Proyecto

## 📌 Descripción general

**Microscopio PRO** es una aplicación de medición en tiempo real basada en **Python + OpenCV**,
diseñada para trabajar con microscopios USB UVC (como los basados en eMPIA) en Linux (Debian 13).

Permite:
- Visualizar vídeo en tiempo real
- Calibrar en **milímetros o pulgadas**
- Medir **distancias, diámetros y rectángulos**
- Asignar **etiquetas y colores** a cada medida
- Mantener un **histórico de medidas**
- Guardar capturas con overlays
- Usar una interfaz tipo **instrumento industrial**

---

## 🧩 Arquitectura del sistema

- **Lenguaje**: Python 3
- **Librerías**:
  - OpenCV (`cv2`)
- **Entrada de vídeo**:
  - Dispositivo UVC (`/dev/videoX`)
- **Interfaz gráfica**:
  - OpenCV (sin GTK / Qt)
- **Persistencia**:
  - En memoria (exportable posteriormente)

---

## ⚙️ Requisitos

### Software
```bash
sudo apt install python3-opencv python3-numpy v4l-utils
```

### Hardware
- Microscopio USB compatible con UVC
- Linux con soporte Video4Linux2

---

## ▶️ Ejecución

```bash
python3 microscopio_pro_menu_final_v3.py
```

El script debe ejecutarse desde una **terminal**, ya que algunas acciones solicitan entrada por consola.

---

## 🖥️ Interfaz de usuario

### Distribución de la ventana

```
┌────────────┬──────────────────────────────┬──────────────────┐
│ MENÚ IZQ   │          IMAGEN              │  MEDIDAS (DER)   │
│            │                              │                  │
│ CAL        │                              │ 01 DIS R1 2.54mm │
│ DIS        │                              │ 02 RAD C1 0.63mm │
│ RAD        │                              │                  │
│ SQR        │                              │                  │
│ ADD        │                              │                  │
│ UNDO       │                              │                  │
│ RED/GRN…   │                              │                  │
│ GRY        │                              │                  │
│ ROT        │                              │                  │
│ SAVE       │                              │                  │
│ QUIT       │                              │                  │
└────────────┴──────────────────────────────┴──────────────────┘
```

---

## 🎛️ Botones del menú izquierdo

### Modos de medida
- **DIS** – Distancia entre dos puntos
- **RAD** – Diámetro (círculo definido por centro + borde)
- **SQR** – Rectángulo (ancho × alto)

### Acciones
- **CAL** – Calibrar usando dos puntos y una distancia real
- **ADD** – Añadir la medida actual al histórico (pide etiqueta)
- **UNDO** – Elimina la última medida añadida
- **SAVE** – Guarda una captura PNG con overlays
- **QUIT** – Cierra la aplicación

### Colores
- **RED / GRN / BLU / YEL**
  - Cambian el color de las **nuevas medidas**
  - Cada medida conserva su color original

### Otros
- **GRY** – Activa / desactiva escala de grises
- **ROT** – Rota la imagen 90° (cíclico)

---

## 🖱️ Uso del ratón

- **Clic izquierdo (imagen)**:
  - Marca puntos de medición
- **Cursor en cruz**:
  - Mejora la precisión visual
- **Clic izquierdo (menú)**:
  - Ejecuta la acción del botón

---

## ⌨️ Teclas de teclado

| Tecla | Acción |
|------|-------|
| `v` | Cambiar unidad de visualización (mm / in) |
| `u` | Cambiar unidad de calibración (mm / in) |
| `x` | Borrar todas las medidas |
| `c` | Borrar puntos actuales |
| `ESC` | Salir (igual que QUIT) |

---

## 📐 Calibración

1. Selecciona **DIS**
2. Marca dos puntos sobre una referencia conocida
3. Pulsa **CAL**
4. Introduce la distancia real por consola (en mm o pulgadas)

> Internamente, la calibración siempre se guarda en **mm/píxel**.

Ejemplo (paso PCB):
```
Distancia real (in): 0.1
```

---

## 📊 Histórico de medidas

Cada medida guarda:
- Tipo (DIS / RAD / SQR)
- Etiqueta (≤ 5 caracteres)
- Valor + unidad
- Color

Ejemplo:
```
01 DIS R1   2.54 mm
02 RAD C1   0.63 mm
03 SQR U2   1.20 x 0.80 mm
```

---

## 💾 Capturas

- El botón **SAVE** guarda una imagen PNG
- Incluye:
  - Imagen del microscopio
  - Todas las geometrías visibles
  - Textos y colores

Formato:
```
captura_YYYYMMDD_HHMMSS.png
```

---

## ⚠️ Limitaciones conocidas

- No hay persistencia entre sesiones (aún)
- No hay zoom avanzado con ROI guardado
- No hay exportación CSV (prevista)
- No hay edición de medidas existentes

---

## 🚀 Posibles mejoras futuras

- Exportar medidas a CSV
- Guardar / cargar sesiones
- Presets de calibración (PCB 0.1”, 0.05”…)
- Retícula calibrada
- Áreas automáticas
- Selección y resaltado de medidas

---

## 📄 Licencia

Uso libre para proyectos personales y técnicos.
Sin garantías implícitas.

---

## 👤 Autor / Contexto

Desarrollado iterativamente para uso práctico con microscopio USB en Linux,
priorizando **robustez**, **claridad** y **flujo de trabajo real**.

