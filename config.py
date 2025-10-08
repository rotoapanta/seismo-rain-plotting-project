# Configuración del proyecto: mapa de isoyetas
# Todas las rutas y medidas (cuando aplica) son relativas al directorio del proyecto

# =====================================
# HOJA (tamaño y orientación)
# =====================================
# Tamaños ISO en centímetros
PAPER_SIZES_CM = {
    'A5': (14.8, 21.0),
    'A4': (21.0, 29.7),
    'A3': (29.7, 42.0),
    'A2': (42.0, 59.4),
    'A1': (59.4, 84.1),
    'A0': (84.1, 118.9),
}
# Selección de hoja: 'A3', 'A4', etc. Si es None, se usa MAP_SIZE_CM como tamaño de figura
PAPER_SIZE = 'A4'
# Orientación de la hoja: 'landscape' o 'portrait'
MAP_ORIENTATION = 'landscape'

# =====================================
# MÁRGENES Y MARCOS (hoja completa)
# =====================================
# Márgenes de página (izquierda, derecha, superior, inferior) en cm
PAGE_MARGINS_CM = (0.5, 0.5, 0.5, 0.5)

# Dibujo de doble margen visible: dos líneas paralelas al borde de la hoja
DRAW_DOUBLE_MARGINS = True
# Offset del segundo margen relativo a PAGE_MARGINS_CM (en cm). Ej: 0.3 => 0.5 cm y 0.8 cm
DOUBLE_MARGIN_OFFSET_CM = 0.3
DOUBLE_MARGINS_COLOR = 'black'
# Matplotlib usa pt (puntos tipográficos). 0.2 mm ≈ 0.56693 pt
DOUBLE_MARGINS_LINEWIDTH = 0.56693
DOUBLE_MARGINS_ALPHA = 1.0

# =====================================
# MAPA (tamaño, posición dentro de la hoja, y estilo)
# =====================================
# Tamaño del mapa en centímetros (ancho, alto). Se usa si PAPER_SIZE es None
# o en combinación con anclaje/caja
MAP_SIZE_CM = (18.0, 18.0)

# Anclaje del mapa: permite fijar su posición desde una esquina
# 'bottom-left' lo ubica a partir de la esquina inferior-izquierda usando MAP_OFFSET_CM
MAP_ANCHOR = 'bottom-left'
# Offset (x_cm, y_cm) desde la esquina inferior-izquierda de la hoja
MAP_OFFSET_CM = (3.0, 6.0)

# Caja exacta del mapa (left_cm, bottom_cm, width_cm, height_cm). Si se define,
# tiene prioridad sobre los márgenes y el anclaje
MAP_BOX_CM = None

# Título del mapa y personalización
TITLE = 'VOLCAN COTOPAXI - MAPA DE ISOYETAS (mm)'
TITLE_FONT_SIZE = 12            # tamaño de letra
TITLE_FONT_WEIGHT = 'bold'      # 'normal', 'bold', etc.
TITLE_FONT_FAMILY = None        # p.ej. 'sans-serif', 'serif' (opcional)
TITLE_FONT_NAME = None          # p.ej. 'DejaVu Sans' (opcional)
TITLE_COLOR = 'black'           # color
TITLE_LOC = 'center'            # 'left', 'center', 'right'
TITLE_PAD_PT = 6                # padding superior en puntos

# Niveles de isoyetas. Si es None, se calculan automáticamente
ISOHYET_LEVELS = None

# Resolución del grid (en grados) para la interpolación IDW
GRID_RESOLUTION_DEG = 0.01

# Extensión del mapa (lon_min, lon_max, lat_min, lat_max). Si es None se calcula a partir de las estaciones
EXTENT = None

# Parámetros de la interpolación IDW
IDW_POWER = 2.0
IDW_EPS = 1e-12

# =====================================
# COLORBAR (barra de colores del mapa)
# =====================================
SHOW_COLORBAR = True
COLORBAR_LOCATION = 'right'   # 'right' o 'left'
COLORBAR_WIDTH_CM = 0.6       # ancho en cm
COLORBAR_PAD_CM = 0.2         # separación (cm) respecto al eje del mapa
# No forzar bordes/fondos: la escala luce como por defecto
COLORBAR_DRAW_EDGES = False

# =====================================
# PIE DE PÁGINA (cajas inferiores)
# =====================================
DRAW_FOOTER_BOXES = True
FOOTER_ROW_BOTTOM_CM = 1.0        # distancia desde el borde inferior
FOOTER_ROW_HEIGHT_CM = 5.0        # altura de las cajas
FOOTER_LEFT_MARGIN_CM = 0.5       # margen izquierdo de la fila
FOOTER_RIGHT_MARGIN_CM = 0.5      # margen derecho de la fila
FOOTER_GAP_CM = 0.3               # separación horizontal entre cajas
FOOTER_BOX_COUNT = 4              # número de cajas (p.ej. 4)
FOOTER_TITLES = ['SIMBOLOGÍA', 'MAPA DE UBICACIÓN', 'ESCALA / ROSA', 'OBSERVACIONES']
# Estilo de borde
FOOTER_EDGE_COLOR = 'black'
FOOTER_EDGE_LINEWIDTH_PT = 0.56693   # ~0.2 mm
# Estilo de título
FOOTER_TITLE_FONT_SIZE = 10
FOOTER_TITLE_FONT_WEIGHT = 'bold'
FOOTER_TITLE_COLOR = 'black'
FOOTER_TITLE_PAD_CM = 0.2

# =====================================
# DATOS Y SALIDA
# =====================================
# Directorio raíz de datos donde se buscarán archivos JSON con lecturas reales
DTA_DIR = 'DTA'

# Directorio donde se guardarán los archivos generados (PDF/imagenes)
OUTPUT_DIR = 'output/isoyetas'

# Formato y DPI de salida
IMAGE_FORMAT = 'pdf'  # 'pdf', 'png', 'jpg', 'svg', etc.
IMAGE_DPI = 150

# Mostrar la figura en una ventana emergente después de guardar
POPUP_WINDOW = True

# Semilla para reproducibilidad en datos sintéticos
RANDOM_SEED = 42

# =====================================
# DATOS SINTÉTICOS (estaciones adicionales)
# =====================================
SYNTHETIC_STATIONS = 3               # cantidad de estaciones sintéticas
SYNTH_JITTER_DEG = 0.2               # dispersión espacial en grados alrededor de la estación real
SYNTH_VALUE_JITTER_MM = (-10, 10)    # rango de variación (mm) respecto al valor real
