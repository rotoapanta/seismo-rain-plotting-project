"""
Configuración Detallada de Cajas Verticales y Horizontales.

Este archivo define la estructura y contenido de cada caja utilizada en el layout
del mapa, tanto en el panel lateral (vertical) como en el pie de página (horizontal).

Cada caja se define como un diccionario con las siguientes claves:
- id (str): Identificador único para la caja (ej: "VER_BOX_1", "HOR_BOX_2").
- title (str): Título que se mostrará en la cabecera de la caja.
- size_cm (float): Altura para cajas verticales, anchura para cajas horizontales.
- content (dict): Define qué contenido va dentro de la caja.
    - type (str): El tipo de contenido. Puede ser:
        - "logo": Muestra una imagen de logo.
        - "minimap": Muestra el mapa de ubicación.
        - "symbology": Muestra la simbología de las isoyetas.
        - "north_arrow_scale": Muestra la rosa de los vientos y la barra de escala.
        - "text": Muestra un texto estático.
        - "dynamic_text": Muestra texto generado dinámicamente.
        - "empty": La caja está vacía.
    - options (dict, opcional): Opciones específicas para el tipo de contenido.
        - Para "logo": {"path": "ruta/al/logo.png"}
        - Para "text": {"value": "Este es un texto de ejemplo."}
"""

# =============================================================================
# 1. CAJAS VERTICALES (PANEL LATERAL DERECHO)
# =============================================================================
# Clasificadas como VER_BOX_1, VER_BOX_2, etc. de arriba hacia abajo.

VERTICAL_BOXES = [
    {
        "id": "VER_BOX_1",
        "title": "",
        "size_cm": 3.0,
        "content": {
            "type": "logo",
            "options": {
                "path": "images/logo-ig.png"
            }
        }
    },
    {
        "id": "VER_BOX_2",
        "title": "DESCRIPCIÓN",
        "size_cm": 7.0,
        "content": {
            "type": "dynamic_text",
            "options": {
                "renderer": "description",
                "wrap_width": 26,
                "pad_cm": 0.5,
                "text_align": "left",
                "vertical_align": "top"
            }
        }
    },
        {
        "id": "VER_BOX_4",
        "title": "INFORMACIÓN",
        "size_cm": 4.0,
        "content": {
            "type": "dynamic_text",
            "options": {
                "renderer": "isoyetas_info",
                "wrap_width": 22,
                "pad_cm": 0.5,
                "text_align": "left",
                "vertical_align": "top"
            }
        }
    },
    {
        "id": "VER_BOX_5",
        "title": "",
        "size_cm": 5.0,
        "content": {
            "type": "dynamic_text",
            "options": {
                "renderer": "credits",
                "wrap_width": 26,
                "pad_cm": 0.5,
                "text_align": "center",
                "vertical_align": "center",
                "bold_lines": [1, 2, 3]
            }
        }
    }
]


# =============================================================================
# 2. CAJAS HORIZONTALES (PIE DE PÁGINA)
# =============================================================================
# Clasificadas como HOR_BOX_1, HOR_BOX_2, etc. de izquierda a derecha.

HORIZONTAL_BOXES = [
    {
        "id": "HOR_BOX_1",
        "title": "SIMBOLOGÍA",
        "size_cm": 5.0,
        "content": {
            "type": "symbology"
        }
    },
    {
        "id": "HOR_BOX_2",
        "title": "MAPA DE UBICACIÓN",
        "size_cm": 5.0,
        "content": {
            "type": "minimap"
        }
    },
    {
        "id": "HOR_BOX_3",
        "title": "ORIENTACIÓN-ESCALA",
        "size_cm": 5.0,
        "content": {
            "type": "north_arrow_scale"
        }
    },
    {
        "id": "HOR_BOX_4",
        "title": "OBSERVACIONES",
        "size_cm": 5.0,
        "content": {
            "type": "dynamic_text",
            "options": {
                "renderer": "observations",
                "wrap_width": 26,
                "pad_cm": 0.5,
                "text_align": "left",
                "vertical_align": "top"
            }
        }
    }
]
