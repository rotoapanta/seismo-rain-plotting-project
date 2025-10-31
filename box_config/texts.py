from __future__ import annotations
from typing import Optional, Dict

# Catálogo centralizado de textos por locale
# Claves sugeridas: 'observations', 'description', 'info', etc.
TEXTS: Dict[str, Dict[str, str]] = {
    'es': {
        'description': (
            'Estudio de precipitaciones (isoyetas) en el área del volcán Cotopaxi. '
            'Se emplearon datos instrumentales disponibles y una interpolación por distancia inversa (IDW) '
            'para estimar la distribución espacial de la lluvia.'
        ),
        'information': (
            'Información general del evento: fuente de datos, fecha de referencia, número de estaciones y '
            'valores agregados estimados. Ajuste este texto en texts.py o config.py según su necesidad.'
        ),
        'observations': 'PROYECTO DE INVESTIGACION CEDIA I+D+I 62 - 2023',
        'credits': (
            'MAPA DE ISOYETAS\nROBERTO CARLOS\nTOAPANTA GUAMÁN\n\n'
            'INVESTIGADOR\nANALISTA DE REDES\nGEOFISICO 2'
        ),
    },
    # 'en': {
    #     'description': 'Rainfall (isohyets) study around Cotopaxi volcano using IDW interpolation.',
    #     'information': 'General information: data source, reference date, station count and aggregated values.',
    #     'observations': 'CEDIA R&D&I Project 62 - 2023',
    #     'credits': 'ISOHYET MAP\n[Author names]\n\n[Roles]'
    # },
}


def get_text(key: str, locale: str = 'es', default: Optional[str] = None) -> str:
    """
    Obtiene un texto del catálogo con soporte de fallback:
    - Primero intenta TEXTS[locale][key]
    - Luego TEXTS['es'][key]
    - Finalmente usa 'default' si no hay coincidencias
    """
    try:
        return (
            TEXTS.get(locale, {}).get(key)
            or TEXTS.get('es', {}).get(key)
            or (default if default is not None else '')
        )
    except Exception:
        return default if default is not None else ''
