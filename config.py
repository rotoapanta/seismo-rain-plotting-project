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

# Transparencia del relleno de isoyetas (0=transparente, 1=opaco)
ISOHYET_ALPHA = 0.6

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
FOOTER_LEFT_MARGIN_CM = 2.0       # margen izquierdo de la fila
FOOTER_RIGHT_MARGIN_CM = 2.0      # margen derecho de la fila
FOOTER_GAP_CM = 0.0               # separación horizontal entre cajas
FOOTER_BOX_COUNT = 4              # número de cajas (p.ej. 4)
FOOTER_TITLES = ['SIMBOLOGÍA', 'MAPA DE UBICACIÓN', '', 'OBSERVACIONES']
# Estilo de borde
FOOTER_EDGE_COLOR = 'black'
FOOTER_EDGE_LINEWIDTH_PT = 0.56693   # ~0.2 mm
# Doble borde para cada caja (similar al de la página)
FOOTER_DOUBLE_BORDER = True
FOOTER_DOUBLE_BORDER_OFFSET_CM = 0.1
FOOTER_DOUBLE_BORDER_COLOR = 'black'
FOOTER_DOUBLE_BORDER_LINEWIDTH_PT = 0.56693
# Estilo de título
FOOTER_TITLE_FONT_SIZE = 10
FOOTER_TITLE_FONT_WEIGHT = 'bold'
FOOTER_TITLE_COLOR = 'black'
FOOTER_TITLE_PAD_CM = 0.2
# Alinear márgenes izquierdo/derecho de las cajas con el offset del mapa
FOOTER_ALIGN_WITH_MAP_OFFSETS = False
# Área exacta para ubicar y dimensionar el bloque de cajas (left_cm, bottom_cm, width_cm, height_cm)
# Si se define, tiene prioridad sobre los márgenes y la alineación con el mapa
FOOTER_BOX_AREA_CM = None
# Opcional: anchos por caja en cm (lista de longitud FOOTER_BOX_COUNT). Si None, se reparten iguales
FOOTER_BOX_WIDTHS_CM = None
# Recuadro del título dentro de cada caja
FOOTER_TITLE_BOX = False
FOOTER_TITLE_BOX_FACE_COLOR = 'white'
FOOTER_TITLE_BOX_EDGE_COLOR = 'black'
FOOTER_TITLE_BOX_LINEWIDTH_PT = 0.56693
FOOTER_TITLE_BOX_PAD = 0.15
# Altura de la fila del título dentro de cada caja del footer (en cm)
FOOTER_TITLE_ROW_HEIGHT_CM = 1.0

#

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
POPUP_WINDOW = False

# Semilla para reproducibilidad en datos sintéticos
RANDOM_SEED = 42

# =====================================
# DATOS SINTÉTICOS (estaciones adicionales)
# =====================================
SYNTHETIC_STATIONS = 3               # cantidad de estaciones sintéticas
SYNTH_JITTER_DEG = 0.2               # dispersión espacial en grados alrededor de la estación real
SYNTH_VALUE_JITTER_MM = (-10, 10)    # rango de variación (mm) respecto al valor real

# =====================================
# MINIMAPA (con Cartopy)
# =====================================
# Índice de la caja del footer donde se insertará el minimapa
# 0 = SIMBOLOGÍA, 1 = MAPA DE UBICACIÓN, 2 = vacío, 3 = OBSERVACIONES
# Si es -1, se desactiva el minimapa
MINIMAP_BOX_INDEX = 1  # Colocar en la segunda caja 'MAPA DE UBICACIÓN'

# Relleno (padding) interior del minimapa respecto a su caja, en cm
MINIMAP_PADDING_CM = 0.3

# Nivel de zoom del minimapa. Un valor mayor aleja la vista para mostrar más contexto
MINIMAP_ZOOM_LEVEL = 2.0

# Resolución de los datos de Cartopy ('110m'=baja, '50m'=media, '10m'=alta)
MINIMAP_CARTOPY_RESOLUTION = '50m'

# Colores del minimapa
MINIMAP_LAND_COLOR = '#F0F0F0'        # Color de la tierra
MINIMAP_OCEAN_COLOR = '#D0E7FF'       # Color del océano
MINIMAP_COASTLINE_COLOR = 'black'     # Color de las líneas costeras
MINIMAP_BORDER_COLOR = 'gray'         # Color de las fronteras
MINIMAP_EXTENT_COLOR = 'red'          # Color del rectángulo que marca el área del mapa principal
MINIMAP_EXTENT_ALPHA = 0.3            # Transparencia del rectángulo


# =====================================
# IMAGEN Y ESCALA
# =====================================
# Índice de la caja del footer donde se insertará la imagen y la escala
IMAGE_SCALE_BOX_INDEX = 2

# Relleno (padding) interior de la imagen y escala respecto a su caja, en cm
IMAGE_SCALE_PADDING_CM = 0.3

# Ruta de la imagen a insertar
IMAGE_PATH = 'images/image.png'

# Ancho y alto de la imagen en cm. Si es None, se ajusta automáticamente
IMAGE_WIDTH_CM = 15
IMAGE_HEIGHT_CM = 15

# Longitud de la barra de escala en km
SCALE_LENGTH_KM = 10

# --- Estilo de la barra de escala ---
# Estilo de la barra: 'simple' o 'segmented'
SCALE_BAR_STYLE = 'segmented'

# --- Opciones para estilo 'simple' ---
# Posición vertical de la barra de escala (0=abajo, 1=arriba del área de la escala)
SCALE_VERTICAL_POSITION = 0.25
# Color de la barra y texto
SCALE_BAR_COLOR = 'black'
SCALE_TEXT_COLOR = 'black'
# Ancho de la línea de la barra en puntos
SCALE_BAR_LINEWIDTH_PT = 2.0
# Estilo de la fuente del texto
SCALE_TEXT_FONT_SIZE = 9
SCALE_TEXT_FONT_WEIGHT = 'bold'

# --- Opciones para estilo 'segmented' ---
# Segmentos de la barra de escala en km. El último valor define la longitud total.
SCALE_BAR_SEGMENTS_KM = [0, 20, 40, 80, 120]
# Altura de la barra de escala en puntos
SCALE_BAR_HEIGHT_PT = 5
# Colores de los segmentos (alternados)
SCALE_SEGMENT_COLORS = ['black', 'white']
# Etiqueta de unidades
SCALE_UNITS_LABEL = 'Kilometers'


# =====================================
# SIMBOLOGÍA
# =====================================
# Índice de la caja del footer donde se insertará la simbología
# 0 = SIMBOLOGÍA, 1 = MAPA DE UBICACIÓN, 2 = vacío, 3 = OBSERVACIONES
SYMBOLOGY_BOX_INDEX = 0  # Colocar en la primera caja 'SIMBOLOGÍA'

# Relleno (padding) interior de la simbología respecto a su caja, en cm
SYMBOLOGY_PADDING_CM = 0.3


#


# =====================================
# ALINEACIÓN DE TÍTULOS EN CAJAS DEL FOOTER
# =====================================
# Alineación horizontal de los títulos ('left', 'center', 'right')
FOOTER_TITLE_HA = 'center'

# Alineación vertical de los títulos ('top', 'center', 'bottom', 'baseline')
FOOTER_TITLE_VA = 'center'


# =====================================
# MAPA DE FONDO (Cartopy)
# =====================================
# Activar o desactivar el mapa de fondo en el gráfico principal
MAP_BACKGROUND = True

# Resolución de los datos de Cartopy para el mapa de fondo ('110m', '50m', '10m')
MAP_BACKGROUND_RESOLUTION = '50m'

# Colores para el mapa de fondo
MAP_BACKGROUND_LAND_COLOR = '#F0F0F0'
MAP_BACKGROUND_OCEAN_COLOR = '#D0E7FF'
MAP_BACKGROUND_COASTLINE_COLOR = 'black'
MAP_BACKGROUND_BORDER_COLOR = 'gray'


#



# =====================================
# MAPA DE FONDO TIPO TILE (más detallado)
# =====================================
# Activar para usar un mapa de fondo con tiles (Stamen, OpenStreetMap) en lugar de Natural Earth
USE_TILE_BACKGROUND = True

# Proveedor de tiles. Opciones: 'Stamen-terrain', 'OSM'
TILE_PROVIDER = 'OSM'

# Nivel de zoom para el mapa de tiles (valor entre 1-14 aprox, depende del área)
TILE_ZOOM_LEVEL = 11

# Transparencia del mapa de fondo con tiles (0=transparente, 1=opaco)
TILE_BACKGROUND_ALPHA = 1.0


# =====================================
