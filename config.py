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
DOUBLE_MARGINS_COLOR = 'black'
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
MANUAL_SEARCH_PATH = '2025/09/29/RGA' # por ejemplo: '2025/03/10'

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
# --- Posición y Tamaño ---
MAP_SIZE_CM = (18.0, 18.0)
MAP_ANCHOR = 'bottom-left'
MAP_OFFSET_CM = (3.0, 6.0)
MAP_BOX_CM = None
EXTENT = None

# --- Título ---
TITLE = 'VOLCAN COTOPAXI - MAPA DE ISOYETAS (mm)'
TITLE_FONT_SIZE = 12
TITLE_FONT_WEIGHT = 'bold'
TITLE_FONT_FAMILY = None
TITLE_FONT_NAME = None
TITLE_COLOR = 'black'
TITLE_LOC = 'center'
TITLE_PAD_PT = 6

# --- Mapa de Fondo (Cartopy) ---
MAP_BACKGROUND = True
USE_TILE_BACKGROUND = True
TILE_PROVIDER = 'OSM'
TILE_ZOOM_LEVEL = 11
TILE_BACKGROUND_ALPHA = 1.0
MAP_BACKGROUND_RESOLUTION = '50m'
MAP_BACKGROUND_LAND_COLOR = '#F0F0F0'
MAP_BACKGROUND_OCEAN_COLOR = '#D0E7FF'
MAP_BACKGROUND_COASTLINE_COLOR = 'black'
MAP_BACKGROUND_BORDER_COLOR = 'gray'


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
SIDE_BOX_TITLES = ['', 'ESTUDIO DE...', 'Mapa Climático', 'LEYENDA', '']
SIDE_BOX_HEIGHTS_CM = [3.0, 5.0, 4.0, 4.0, 3.0] # Ejemplo: Caja 1 (logo) es 3cm, pero el logo sigue siendo 5cm

# --- Estilo de Bordes y Títulos del Panel Lateral ---
SIDE_BOX_EDGE_COLOR = 'black'
SIDE_BOX_EDGE_LINEWIDTH_PT = 0.56693
SIDE_BOX_DOUBLE_BORDER = True
SIDE_BOX_DOUBLE_BORDER_OFFSET_CM = 0.1
SIDE_BOX_TITLE_FONT_SIZE = 10
SIDE_BOX_TITLE_FONT_WEIGHT = 'bold'
SIDE_BOX_TITLE_COLOR = 'black'
SIDE_BOX_TITLE_ROW_HEIGHT_CM = 1.0


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
FOOTER_TITLES = ['SIMBOLOGÍA', 'MAPA DE UBICACIÓN', '', 'OBSERVACIONES']
FOOTER_BOX_AREA_CM = None
FOOTER_ALIGN_WITH_MAP_OFFSETS = False
FOOTER_BOX_WIDTHS_CM = [5.0, 5.0, 5.0, 5.0]

# --- Estilo de Bordes y Títulos del Pie de Página ---
FOOTER_EDGE_COLOR = 'black'
FOOTER_EDGE_LINEWIDTH_PT = 0.56693
FOOTER_DOUBLE_BORDER = True
FOOTER_DOUBLE_BORDER_OFFSET_CM = 0.1
FOOTER_DOUBLE_BORDER_COLOR = 'black'
FOOTER_DOUBLE_BORDER_LINEWIDTH_PT = 0.56693
FOOTER_TITLE_FONT_SIZE = 10
FOOTER_TITLE_FONT_WEIGHT = 'bold'
FOOTER_TITLE_COLOR = 'black'
FOOTER_TITLE_PAD_CM = 0.2
FOOTER_TITLE_ROW_HEIGHT_CM = 1.0
FOOTER_TITLE_HA = 'center'
FOOTER_TITLE_VA = 'center'
FOOTER_TITLE_BOX = False
FOOTER_TITLE_BOX_FACE_COLOR = 'white'
FOOTER_TITLE_BOX_EDGE_COLOR = 'black'
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
MINIMAP_COASTLINE_COLOR = 'black'
MINIMAP_BORDER_COLOR = 'gray'
MINIMAP_EXTENT_COLOR = 'red'
MINIMAP_EXTENT_ALPHA = 0.3

# --- Simbología ---
SYMBOLOGY_BOX_INDEX = 0
SYMBOLOGY_PADDING_CM = 0.3

# --- Rosa de los Vientos y Escala ---
NORTH_ARROW_SCALE_BOX_INDEX = 2
NORTH_ARROW_SCALE_PADDING_CM = 0.3
# Rosa de los vientos
NORTH_ARROW_STYLE = 'image'
NORTH_ARROW_IMAGE_PATH = 'images/image.png'
NORTH_ARROW_IMAGE_WIDTH_CM = 2.7
NORTH_ARROW_IMAGE_HEIGHT_CM = 2.7
NORTH_ARROW_Y_POS = 0.65
NORTH_ARROW_SIZE = 0.25
NORTH_ARROW_COLOR1 = 'black'
NORTH_ARROW_COLOR2 = 'white'
NORTH_ARROW_EDGE_COLOR = 'black'
NORTH_ARROW_TEXT_COLOR = 'black'
NORTH_ARROW_FONT_SIZE = 10
NORTH_ARROW_FONT_WEIGHT = 'bold'
# Barra de escala
SCALE_BAR_STYLE = 'segmented'
SCALE_BAR_Y_POS = 0.0
SCALE_SIMPLE_LENGTH_KM = 10
SCALE_SIMPLE_BAR_COLOR = 'black'
SCALE_SIMPLE_TEXT_COLOR = 'black'
SCALE_SIMPLE_BAR_LINEWIDTH_PT = 2.0
SCALE_SIMPLE_TEXT_FONT_SIZE = 9
SCALE_SIMPLE_TEXT_FONT_WEIGHT = 'bold'
SCALE_SEGMENTED_SEGMENTS_KM = [0, 20, 40, 80, 120]
SCALE_SEGMENTED_BAR_HEIGHT_PT = 8
SCALE_SEGMENTED_COLORS = ['black', 'white']
SCALE_SEGMENTED_EDGE_COLOR = 'black'
SCALE_SEGMENTED_TEXT_COLOR = 'black'
SCALE_SEGMENTED_TEXT_FONT_SIZE = 10
SCALE_SEGMENTED_UNITS_LABEL = 'Km'
