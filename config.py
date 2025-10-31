# =============================================================================
#
#      CONFIGURACIÓN DEL PROYECTO: MAPA DE ISOYETAS
#
# =============================================================================
# Este archivo centraliza todos los parámetros para personalizar la apariencia
# y el comportamiento del mapa. Está organizado por componentes para facilitar
# la localización de cada ajuste.
# =============================================================================

from box_config.boxes import VERTICAL_BOXES, HORIZONTAL_BOXES

# Variantes de cajas por tipo de página (isoyetas, timeseries, etc.)
VERTICAL_BOXES_ISOYETAS = VERTICAL_BOXES
HORIZONTAL_BOXES_ISOYETAS = HORIZONTAL_BOXES

# Para timeseries reutilizamos títulos y tamaños pero cambiamos renderers de contenido
VERTICAL_BOXES_TIMESERIES = [
    {
        "id": "VER_BOX_1",
        "title": "",
        "size_cm": 3.0,
        "content": {"type": "logo", "options": {"path": "images/logo-ig.png"}}
    },
    {
        "id": "VER_BOX_2",
        "title": "DESCRIPCIÓN",
        "size_cm": 7.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "description", "wrap_width": 26, "pad_cm": 0.5, "text_align": "left", "vertical_align": "top"}
        }
    },
    {
        "id": "VER_BOX_4",
        "title": "INFORMACIÓN",
        "size_cm": 4.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "timeseries_info", "wrap_width": 22, "pad_cm": 0.5, "text_align": "left", "vertical_align": "top"}
        }
    },
    {
        "id": "VER_BOX_5",
        "title": "",
        "size_cm": 5.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "credits", "wrap_width": 26, "pad_cm": 0.5, "text_align": "center", "vertical_align": "center", "bold_lines": [1,2,3]}
        }
    },
]

HORIZONTAL_BOXES_TIMESERIES = HORIZONTAL_BOXES

# Variantes de cajas para barras (reutilizan las generales)
VERTICAL_BOXES_BARS = [
    {
        "id": "VER_BOX_1",
        "title": "",
        "size_cm": 3.0,
        "content": {"type": "logo", "options": {"path": "images/logo-ig.png"}}
    },
    {
        "id": "VER_BOX_2",
        "title": "DESCRIPCIÓN",
        "size_cm": 7.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "bars_description", "wrap_width": 26, "pad_cm": 0.5, "text_align": "left", "vertical_align": "top"}
        }
    },
    {
        "id": "VER_BOX_4",
        "title": "INFORMACIÓN",
        "size_cm": 4.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "bars_info", "wrap_width": 22, "pad_cm": 0.5, "text_align": "left", "vertical_align": "top"}
        }
    },
    {
        "id": "VER_BOX_5",
        "title": "",
        "size_cm": 5.0,
        "content": {
            "type": "dynamic_text",
            "options": {"renderer": "credits", "wrap_width": 26, "pad_cm": 0.5, "text_align": "center", "vertical_align": "center", "bold_lines": [1,2,3]}
        }
    },
]
HORIZONTAL_BOXES_BARS = HORIZONTAL_BOXES

# Locale global por defecto para textos
LOCALE = 'es'

# Overrides rápidos de textos (opcional): si None, se usará texts.py
DESCRIPTION_TEXT = None
INFORMATION_TEXT = None
OBSERVATIONS_TEXT = None
CREDITS_TEXT = None

#

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
DOUBLE_MARGIN_OFFSET_CM = 0.1
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
MANUAL_SEARCH_PATH = '2025/10/30/RGA' # por ejemplo: '2025/03/10'

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

# Extensión por defecto para el mapa principal
EXTENT = None


# =============================================================================
# 3. COMPONENTE: MAPA PRINCIPAL
# =============================================================================
# --- Posición y Tamaño para el Mapa de Isoyetas ---
# Ancho y alto en cm del área donde se dibuja el mapa de isoyetas.
ISOYETAS_SIZE_CM = (18.0, 12.0)
# Ancla de la esquina desde donde se calcula la posición ('bottom-left', 'top-left', etc.).
ISOYETAS_ANCHOR = 'bottom-left'
# Desplazamiento (offset) en cm (x, y) desde el ancla.
ISOYETAS_OFFSET_CM = (3.0, 7.0)
# (Opcional) Define una caja fija [izquierda, abajo, ancho, alto] en cm, ignorando lo anterior.
ISOYETAS_BOX_CM = None


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




# --- Mapa de Fondo (Cartopy) ---
MAP_BACKGROUND = True
USE_TILE_BACKGROUND = True
TILE_PROVIDER = 'OSM'
TILE_ZOOM_LEVEL = 12
TILE_BACKGROUND_ALPHA = 1.0
MAP_BACKGROUND_RESOLUTION = '110m'
MAP_BACKGROUND_LAND_COLOR = '#F0F0F0'
MAP_BACKGROUND_OCEAN_COLOR = '#D0E7FF'
MAP_BACKGROUND_COASTLINE_COLOR = '#000000'
MAP_BACKGROUND_BORDER_COLOR = '#808080'


# =============================================================================
# 3b. COMPONENTE: SERIE TEMPORAL
# =============================================================================
# Directorio de salida e imagen
OUTPUT_DIR_TIMESERIES = 'output/timeseries'

# Área de contenido para series temporales (tamaño/posición)
# Opción 1: caja fija [left_cm, bottom_cm, width_cm, height_cm]
TIMESERIES_BOX_CM = None
# Opción 2: tamaño y offset (se usa si TIMESERIES_BOX_CM es None)
TIMESERIES_SIZE_CM = (18.0, 11.0)
TIMESERIES_OFFSET_CM = (3.0, 8.0)

# Título
TIMESERIES_TITLE = 'VOLCAN COTOPAXI - SERIE TEMPORAL (mm)'
TIMESERIES_TITLE_FONT_SIZE = 12
TIMESERIES_TITLE_FONT_WEIGHT = 'bold'
TIMESERIES_TITLE_FONT_FAMILY = None
TIMESERIES_TITLE_FONT_NAME = None
TIMESERIES_TITLE_COLOR = '#0941DA'
TIMESERIES_TITLE_LOC = 'center'
TIMESERIES_TITLE_PAD_PT = 6

# Ejes
TIMESERIES_X_LABEL = 'Tiempo'
TIMESERIES_Y_LABEL = 'Valor'
TIMESERIES_AXIS_LABEL_FONT_SIZE = 9
TIMESERIES_AXIS_LABEL_COLOR = '#333333'
TIMESERIES_AXIS_LABEL_FONT_WEIGHT = 'normal'
TIMESERIES_TICK_LABEL_FONT_SIZE = 8
TIMESERIES_TICK_LABEL_COLOR = '#4D4D4D'

# Escala y límites (opcional)
TIMESERIES_YSCALE = 'linear'  # 'linear' | 'log'
TIMESERIES_YLIM = None        # (ymin, ymax) o None
TIMESERIES_XLIM = None        # (xmin, xmax) o None (admite datetime si aplica)
# Espaciado físico de ticks en Y (cm)
TIMESERIES_YTICK_SPACING_CM = 0.5

# Línea/Marcadores
TIMESERIES_LINE_STYLE = '-'
TIMESERIES_LINE_COLOR = '#1f77b4'
TIMESERIES_LINE_WIDTH = 1.8
TIMESERIES_MARKER = 'o'
TIMESERIES_MARKER_SIZE = 3.0

# Cuadrícula
TIMESERIES_GRID = True
TIMESERIES_GRID_LINESTYLE = '--'
TIMESERIES_GRID_ALPHA = 1.0
TIMESERIES_GRID_COLOR = "#995A5A"  # Color de líneas de grilla del gráfico de series temporales


# =============================================================================
# 3c. COMPONENTE: BARRAS
# =============================================================================
# Directorio de salida e imagen
OUTPUT_DIR_BARS = 'output/bars'

# Área de contenido para barras (tamaño/posición)
# Opción 1: caja fija [left_cm, bottom_cm, width_cm, height_cm]
BARS_BOX_CM = None
# Opción 2: tamaño y offset (se usa si BARS_BOX_CM es None)
BARS_SIZE_CM = (16.0, 11.0)
BARS_OFFSET_CM = (3.0, 8.0)

# Título
BARS_TITLE = 'VOLCAN COTOPAXI - BARRAS (mm)'
BARS_TITLE_FONT_SIZE = 12
BARS_TITLE_FONT_WEIGHT = 'bold'
BARS_TITLE_FONT_FAMILY = None
BARS_TITLE_FONT_NAME = None
BARS_TITLE_COLOR = '#0941DA'
BARS_TITLE_LOC = 'center'
BARS_TITLE_PAD_PT = 6

# Ejes
BARS_X_LABEL = 'Hora'
BARS_Y_LABEL = 'Precipitación (mm)'
BARS_AXIS_LABEL_FONT_SIZE = 9
BARS_AXIS_LABEL_COLOR = '#333333'
BARS_AXIS_LABEL_FONT_WEIGHT = 'normal'
BARS_TICK_LABEL_FONT_SIZE = 8
BARS_TICK_LABEL_COLOR = '#4D4D4D'

# Estilo de barras
BARS_FACE_COLOR = '#1f77b4'
BARS_EDGE_COLOR = '#1f77b4'
BARS_ALPHA = 0.9

# Cuadrícula
BARS_GRID = True
BARS_GRID_LINESTYLE = '--'
BARS_GRID_ALPHA = 1.0
BARS_GRID_COLOR = '#995A5A'

# =============================================================================
# 4. COMPONENTE: BARRA DE COLOR (COLORBAR)
# =============================================================================
SHOW_COLORBAR = True
COLORBAR_LOCATION = 'right'
COLORBAR_WIDTH_CM = 1.0
COLORBAR_PAD_CM = 0.2
COLORBAR_DRAW_EDGES = False


# =============================================================================
# 5. COMPONENTE: PANEL LATERAL (CAJAS VERTICALES A LA DERECHA)
# =============================================================================
# La configuración detallada de las cajas (títulos, tamaños, contenido) 
# se ha movido a config/boxes.py para una mejor organización.

DRAW_SIDE_BOXES = True
SIDE_BOX_RIGHT_CM = 1.0
SIDE_BOX_WIDTH_CM = 5.0
SIDE_BOX_TOP_CM = 1.0
SIDE_BOX_BOTTOM_CM = 1.0
SIDE_BOX_GAP_CM = 0.0

# --- Estilo de Bordes y Títulos del Panel Lateral ---
SIDE_BOX_EDGE_COLOR = '#000000'
SIDE_BOX_EDGE_LINEWIDTH_PT = 0.56693
SIDE_BOX_DOUBLE_BORDER = True
SIDE_BOX_DOUBLE_BORDER_OFFSET_CM = 0.1
SIDE_BOX_TITLE_FONT_SIZE = 10
SIDE_BOX_TITLE_FONT_WEIGHT = 'bold'
SIDE_BOX_TITLE_COLOR = '#000000'
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
FOOTER_BOX_AREA_CM = None
FOOTER_ALIGN_WITH_MAP_OFFSETS = False

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
# La configuración específica de estos componentes ahora se gestiona a través
# de los tipos de contenido en `config/boxes.py`. Las opciones que antes estaban
# aquí se pueden añadir al diccionario `options` de cada caja si es necesario
# un ajuste fino.

# --- Logo ---
# Define el tamaño del logo. El valor corresponde a la dimensión más grande (ancho o alto) en cm.
# La otra dimensión se ajustará automáticamente para mantener la proporción original de la imagen.
LOGO_TARGET_SIZE_CM = 5.0

# --- Minimapa ---
# Configurado en la caja con content.type = "minimap"
# Relleno (padding) interior en cm dentro de la caja del minimapa.
MINIMAP_PADDING_CM = 0.3
# Factor de zoom para el minimapa. Un valor más alto aleja la vista (mapa más pequeño).
MINIMAP_ZOOM_FACTOR = 8.0
# Modo del minimapa: 'auto' usa extent si existe, 'world' muestra el mundo completo
MINIMAP_MODE = 'auto'
# Resolución de los datos de Cartopy (ej: '110m', '50m', '10m').
MINIMAP_CARTOPY_RESOLUTION = '110m'
# Color para la tierra.
MINIMAP_LAND_COLOR = '#F0F0F0'
# Color para el océano.
MINIMAP_OCEAN_COLOR = '#D0E7FF'
# Color de las líneas de costa.
MINIMAP_COASTLINE_COLOR = '#000000'
# Color de las fronteras de los países.
MINIMAP_BORDER_COLOR = '#808080'
# Color del recuadro que muestra la extensión del mapa principal.
MINIMAP_EXTENT_COLOR = '#FF0000'
# Transparencia del recuadro de extensión (0.0 a 1.0).
MINIMAP_EXTENT_ALPHA = 0.3

# --- Simbología ---
# Configurado en la caja con content.type = "symbology"
SYMBOLOGY_PADDING_CM = 0.3

# --- Rosa de los Vientos y Escala ---
# Configurado en la caja con content.type = "north_arrow_scale"
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
# La barra de escala ahora se dibuja dinámicamente en el mapa principal.
# Los siguientes valores configuran su apariencia.
SCALE_BAR_WIDTH_FRACTION = (0.1, 0.9)  # Ancho fraccional de la barra de escala (de 0.0 a 1.0).
SCALE_BAR_LOCATION = 'lower right'  # Ubicación de la barra de escala en el mapa.
SCALE_BAR_COLOR = 'black'  # Color de la línea y texto de la barra de escala.
SCALE_BAR_LINE_WIDTH = 5.0  # Grosor de la línea de la barra de escala en puntos.
SCALE_BAR_FONT_SIZE = 8  # Tamaño de la fuente para los números y unidades.
