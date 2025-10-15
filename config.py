# =============================================================================
#
#      CONFIGURACIÓN DEL PROYECTO: MAPA DE ISOYETAS
#
# =============================================================================
# Este archivo centraliza todos los parámetros para personalizar la apariencia
# y el comportamiento del mapa. Está organizado por componentes para facilitar
# la localización de cada ajuste.
# =============================================================================


# =============================================================================
# 1. CONFIGURACIÓN GENERAL Y DE SALIDA
# =============================================================================

# --- Modo de Ejecución ---
# Si True, el script buscará un archivo para una fecha y hora específicas.
# Si False, el script usará el archivo JSON más reciente que encuentre en DTA_DIR.
USE_TARGET_DATETIME = False

# Fecha y hora objetivo (solo si USE_TARGET_DATETIME es True)
TARGET_DATE = '2025-10-03'  # Formato YYYY-MM-DD
TARGET_HOUR = 14            # Hora en formato 24h (0-23)


# --- Tamaño y Orientación de la Hoja ---
PAPER_SIZES_CM = {
    'A5': (14.8, 21.0), 'A4': (21.0, 29.7), 'A3': (29.7, 42.0),
    'A2': (42.0, 59.4), 'A1': (59.4, 84.1), 'A0': (84.1, 118.9),
}
PAPER_SIZE = 'A4'
MAP_ORIENTATION = 'landscape'

# --- Márgenes y Marcos de la Hoja ---
PAGE_MARGINS_CM = (0.5, 0.5, 0.5, 0.5)
DRAW_DOUBLE_MARGINS = True
DOUBLE_MARGIN_OFFSET_CM = 0.3
DOUBLE_MARGINS_COLOR = '#000000'
DOUBLE_MARGINS_LINEWIDTH = 0.56693
DOUBLE_MARGINS_ALPHA = 1.0

# --- Archivos de Salida ---
OUTPUT_DIR = 'output/isoyetas'
IMAGE_FORMAT = 'pdf'
IMAGE_DPI = 150
POPUP_WINDOW = False


# =============================================================================
# 2. DATOS E INTERPOLACIÓN
# =============================================================================
# --- Fuentes de Datos ---
DTA_DIR = 'DTA'

# Ruta manual para buscar datos (relativa a DTA_DIR). Si se define, el script buscará el archivo
# más reciente solo en esta carpeta. Ej: '2025/09/26'.
# Tiene prioridad solo si USE_TARGET_DATETIME es False.
MANUAL_SEARCH_PATH = '2025/10/14/RGA' # por ejemplo: '2025/03/10'

# Si True, acumula (suma) los valores de todos los JSON en la ruta manual. 
# Si False, solo usa el archivo más reciente en esa ruta.
ACCUMULATE_FILES_IN_PATH = True

RANDOM_SEED = 42

# --- Estaciones Sintéticas ---
SYNTHETIC_STATIONS = 3
SYNTH_JITTER_DEG = 0.2
SYNTH_VALUE_JITTER_MM = (-10, 10)

# --- Parámetros de Interpolación y Grilla ---
GRID_RESOLUTION_DEG = 0.01
IDW_POWER = 2.0
IDW_EPS = 1e-12
ISOHYET_LEVELS = None
ISOHYET_ALPHA = 0.6


# =============================================================================
# 3. COMPONENTE: MAPA PRINCIPAL
# =============================================================================
# --- Posición y Tamaño para el Mapa de Isoyetas ---
# Ancho y alto en cm del área donde se dibuja el mapa de isoyetas.
ISOYETAS_SIZE_CM = (18.0, 14.0)
# Ancla de la esquina desde donde se calcula la posición ('bottom-left', 'top-left', etc.).
ISOYETAS_ANCHOR = 'bottom-left'
# Desplazamiento (offset) en cm (x, y) desde el ancla.
ISOYETAS_OFFSET_CM = (3.0, 6.0)
# (Opcional) Define una caja fija [izquierda, abajo, ancho, alto] en cm, ignorando lo anterior.
ISOYETAS_BOX_CM = None

# --- Posición y Tamaño para Gráficas de Series de Tiempo ---
# Ancho y alto en cm del área donde se dibuja la gráfica de series de tiempo.
TIMESERIES_SIZE_CM = (18.0, 10.0)
# Ancla de la esquina para la posición.
TIMESERIES_ANCHOR = 'bottom-left'
# Desplazamiento (offset) en cm (x, y) desde el ancla.
TIMESERIES_OFFSET_CM = (3.0, 8.0)
EXTENT = None

# --- Título para el Mapa de Isoyetas ---
ISOYETAS_TITLE = 'VOLCAN COTOPAXI - MAPA DE ISOYETAS (mm)'
ISOYETAS_TITLE_FONT_SIZE = 12
ISOYETAS_TITLE_FONT_WEIGHT = 'bold'
ISOYETAS_TITLE_FONT_FAMILY = None
ISOYETAS_TITLE_FONT_NAME = None
ISOYETAS_TITLE_COLOR = "#0941DA"
ISOYETAS_TITLE_LOC = 'center'
ISOYETAS_TITLE_PAD_PT = 6

# --- Ejes para el Mapa de Isoyetas ---
# Texto de la etiqueta para el eje X.
ISOYETAS_X_LABEL = 'Longitud (°)'
# Texto de la etiqueta para el eje Y.
ISOYETAS_Y_LABEL = 'Latitud (°)'
# Tamaño de la fuente para las etiquetas de los ejes.
ISOYETAS_AXIS_LABEL_FONT_SIZE = 9
# Color de la fuente para las etiquetas de los ejes.
ISOYETAS_AXIS_LABEL_COLOR = "#921C2C"
# Grosor de la fuente para las etiquetas de los ejes ('normal', 'bold').
ISOYETAS_AXIS_LABEL_FONT_WEIGHT = 'normal'
# Tamaño de la fuente para las marcas de los ejes (los números).
ISOYETAS_TICK_LABEL_FONT_SIZE = 8
# Color de la fuente para las marcas de los ejes.
ISOYETAS_TICK_LABEL_COLOR = '#A9A9A9'

# --- Título para Gráficas de Series de Tiempo ---
TIMESERIES_TITLE = 'VOLCAN COTOPAXI - SERIE DE TIEMPO'
TIMESERIES_TITLE_FONT_SIZE = 12
TIMESERIES_TITLE_FONT_WEIGHT = 'bold'
TIMESERIES_TITLE_FONT_FAMILY = None
TIMESERIES_TITLE_FONT_NAME = None
TIMESERIES_TITLE_COLOR = "#0941DA"
TIMESERIES_TITLE_LOC = 'center'
TIMESERIES_TITLE_PAD_PT = 6

# --- Configuración de Ejes para Series de Tiempo ---
# Texto de la etiqueta para el eje X.
TIMESERIES_X_LABEL = 'Tiempo'
# Texto de la etiqueta para el eje Y.
TIMESERIES_Y_LABEL = 'Precipitación (mm)'

# Tamaño de la fuente para las etiquetas de los ejes (ej. 'Tiempo', 'Precipitación (mm)').
TIMESERIES_AXIS_LABEL_FONT_SIZE = 10
# Color de la fuente para las etiquetas de los ejes.
TIMESERIES_AXIS_LABEL_COLOR = "#921C2C"
# Grosor de la fuente para las etiquetas de los ejes ('normal', 'bold').
TIMESERIES_AXIS_LABEL_FONT_WEIGHT = 'normal'

# Tamaño de la fuente para las marcas de los ejes (los números).
TIMESERIES_TICK_LABEL_FONT_SIZE = 9
# Color de la fuente para las marcas de los ejes.
TIMESERIES_TICK_LABEL_COLOR = '#A9A9A9'


# --- Mapa de Fondo (Cartopy) ---
MAP_BACKGROUND = True
USE_TILE_BACKGROUND = True
TILE_PROVIDER = 'OSM'
TILE_ZOOM_LEVEL = 11
TILE_BACKGROUND_ALPHA = 1.0
MAP_BACKGROUND_RESOLUTION = '50m'
MAP_BACKGROUND_LAND_COLOR = '#F0F0F0'
MAP_BACKGROUND_OCEAN_COLOR = '#D0E7FF'
MAP_BACKGROUND_COASTLINE_COLOR = '#000000'
MAP_BACKGROUND_BORDER_COLOR = '#808080'


# =============================================================================
# 4. COMPONENTE: BARRA DE COLOR (COLORBAR)
# =============================================================================
SHOW_COLORBAR = True
COLORBAR_LOCATION = 'right'
COLORBAR_WIDTH_CM = 0.6
COLORBAR_PAD_CM = 0.2
COLORBAR_DRAW_EDGES = False


# =============================================================================
# 5. COMPONENTE: PANEL LATERAL (CAJAS VERTICALES A LA DERECHA)
# =============================================================================
DRAW_SIDE_BOXES = True
SIDE_BOX_RIGHT_CM = 1.0
SIDE_BOX_WIDTH_CM = 5.0
SIDE_BOX_TOP_CM = 1.0
SIDE_BOX_BOTTOM_CM = 1.0
SIDE_BOX_GAP_CM = 0.0
SIDE_BOX_COUNT = 5
SIDE_BOX_TITLES = ['', 'ESTUDIO DE...', 'Mapa Climático', 'INFORMACIÓN', '']
SIDE_BOX_HEIGHTS_CM = [3.0, 5.0, 4.0, 4.0, 3.0] # Ejemplo: Caja 1 (logo) es 3cm, pero el logo sigue siendo 5cm

# --- Estilo de Bordes y Títulos del Panel Lateral ---
SIDE_BOX_EDGE_COLOR = '#000000'
SIDE_BOX_EDGE_LINEWIDTH_PT = 0.56693
SIDE_BOX_DOUBLE_BORDER = True
SIDE_BOX_DOUBLE_BORDER_OFFSET_CM = 0.1
SIDE_BOX_TITLE_FONT_SIZE = 10
SIDE_BOX_TITLE_FONT_WEIGHT = 'bold'
SIDE_BOX_TITLE_COLOR = '#000000'
SIDE_BOX_TITLE_ROW_HEIGHT_CM = 1.0

#

#

#


# =============================================================================
# 6. COMPONENTE: PIE DE PÁGINA (CAJAS HORIZONTALES INFERIORES)
# =============================================================================
DRAW_FOOTER_BOXES = True
FOOTER_ROW_BOTTOM_CM = 1.0
FOOTER_ROW_HEIGHT_CM = 5.0
FOOTER_LEFT_MARGIN_CM = 2.0
FOOTER_RIGHT_MARGIN_CM = 2.0
FOOTER_GAP_CM = 0.0
FOOTER_BOX_COUNT = 4
FOOTER_TITLES = ['SIMBOLOGÍA', 'MAPA DE UBICACIÓN', 'ORIENTACIÓN-ESCALA', 'OBSERVACIONES']
FOOTER_BOX_AREA_CM = None
FOOTER_ALIGN_WITH_MAP_OFFSETS = False
FOOTER_BOX_WIDTHS_CM = [5.0, 5.0, 5.0, 5.0]

# --- Estilo de Bordes y Títulos del Pie de Página ---
FOOTER_EDGE_COLOR = '#000000'
FOOTER_EDGE_LINEWIDTH_PT = 0.56693
FOOTER_DOUBLE_BORDER = True
FOOTER_DOUBLE_BORDER_OFFSET_CM = 0.1
FOOTER_DOUBLE_BORDER_COLOR = '#000000'
FOOTER_DOUBLE_BORDER_LINEWIDTH_PT = 0.56693
FOOTER_TITLE_FONT_SIZE = 10
FOOTER_TITLE_FONT_WEIGHT = 'bold'
FOOTER_TITLE_COLOR = '#000000'
FOOTER_TITLE_PAD_CM = 0.2
FOOTER_TITLE_ROW_HEIGHT_CM = 1.0
FOOTER_TITLE_HA = 'center'
FOOTER_TITLE_VA = 'center'
FOOTER_TITLE_BOX = False
FOOTER_TITLE_BOX_FACE_COLOR = '#FFFFFF'
FOOTER_TITLE_BOX_EDGE_COLOR = '#000000'
FOOTER_TITLE_BOX_LINEWIDTH_PT = 0.56693
FOOTER_TITLE_BOX_PAD = 0.15


# =============================================================================
# 7. SUB-COMPONENTES (LOGO, MINIMAPA, SIMBOLOGÍA, ETC.)
# =============================================================================

# --- Logo ---
LOGO_BOX_INDEX = 0
LOGO_IMAGE_PATH = 'images/logo-ig.png'
LOGO_WIDTH_CM = 5.0
LOGO_HEIGHT_CM = 5.0
LOGO_MARGIN_CM = 0.0
# --- Comportamiento del Logo dentro de su Caja ---
# Si True, el logo se escala para caber en la caja (dependiente del tamaño de la caja).
# Si False, el logo usa un tamaño fijo (independiente) y puede recortarse o desbordarse.
LOGO_RESIZE_TO_FIT = False

# Ancla para posicionar el logo en modo de tamaño fijo ('center', 'top-left', 'bottom-right', etc.)
LOGO_ANCHOR = 'center'

# Offset en cm (dx, dy) desde el ancla en modo de tamaño fijo.
LOGO_OFFSET_CM = (0.0, 0.0)

# Si True y el logo es más grande que la caja, se recorta a los límites de la caja.
# Si False, el logo se dibuja completo, incluso si se desborda.
LOGO_CLIP_TO_BOX = True

# --- Minimapa ---
MINIMAP_BOX_INDEX = 1
MINIMAP_PADDING_CM = 0.3
MINIMAP_ZOOM_LEVEL = 2.0
MINIMAP_CARTOPY_RESOLUTION = '50m'
MINIMAP_LAND_COLOR = '#F0F0F0'
MINIMAP_OCEAN_COLOR = '#D0E7FF'
MINIMAP_COASTLINE_COLOR = '#000000'
MINIMAP_BORDER_COLOR = '#808080'
MINIMAP_EXTENT_COLOR = '#FF0000'
MINIMAP_EXTENT_ALPHA = 0.3

# --- Simbología ---
SYMBOLOGY_BOX_INDEX = 0
SYMBOLOGY_PADDING_CM = 0.3

# --- Rosa de los Vientos y Escala ---
NORTH_ARROW_SCALE_BOX_INDEX = 2
NORTH_ARROW_SCALE_PADDING_CM = 0.3

#
# Rosa de los vientos
NORTH_ARROW_STYLE = 'image'
NORTH_ARROW_IMAGE_PATH = 'images/image.png'
NORTH_ARROW_IMAGE_WIDTH_CM = 2.7
NORTH_ARROW_IMAGE_HEIGHT_CM = 2.7
NORTH_ARROW_Y_POS = 0.65
NORTH_ARROW_SIZE = 0.25
NORTH_ARROW_COLOR1 = '#000000'
NORTH_ARROW_COLOR2 = '#FFFFFF'
NORTH_ARROW_EDGE_COLOR = '#000000'
NORTH_ARROW_TEXT_COLOR = '#000000'
NORTH_ARROW_FONT_SIZE = 10
NORTH_ARROW_FONT_WEIGHT = 'bold'
# Barra de escala
SCALE_BAR_STYLE = 'segmented'
SCALE_BAR_Y_POS = 0.0
SCALE_SIMPLE_LENGTH_KM = 10
SCALE_SIMPLE_BAR_COLOR = '#000000'
SCALE_SIMPLE_TEXT_COLOR = '#000000'
SCALE_SIMPLE_BAR_LINEWIDTH_PT = 2.0
SCALE_SIMPLE_TEXT_FONT_SIZE = 9
SCALE_SIMPLE_TEXT_FONT_WEIGHT = 'bold'
SCALE_SEGMENTED_SEGMENTS_KM = [0, 20, 40, 80, 120]
SCALE_SEGMENTED_BAR_HEIGHT_PT = 8
SCALE_SEGMENTED_COLORS = ['#000000', '#FFFFFF']
SCALE_SEGMENTED_EDGE_COLOR = '#000000'
SCALE_SEGMENTED_TEXT_COLOR = '#000000'
SCALE_SEGMENTED_TEXT_FONT_SIZE = 10
SCALE_SEGMENTED_UNITS_LABEL = 'Km'
