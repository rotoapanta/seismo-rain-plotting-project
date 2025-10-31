from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
import math
import re


def render_isoyetas_info(context: Dict[str, Any]) -> str:
    """
    Renderiza el texto dinámico para el panel de información de isoyetas.
    Extrae datos del contexto y los formatea en un string.
    """
    # Overrides: usar solo contexto o config; si no hay, generar dinámico
    try:
        override = context.get('information_text')
        if not override:
            import config as CFG
            override = getattr(CFG, 'INFORMATION_TEXT', None)
    except Exception:
        override = None
    if override:
        return str(override)

    source_file = context.get('source_file')
    stations = context.get('stations')
    
    fecha_str = 'N/A'
    fuente_str = 'N/A'

    if source_file:
        try:
            # Intenta obtener la fecha desde el nombre del archivo (ej: ..._YYYYMMDD_...)
            match = re.search(r'_(\d{8})_', source_file.name)
            if match:
                date_obj = datetime.strptime(match.group(1), '%Y%m%d')
                fecha_str = date_obj.strftime('%Y-%m-%d')
            else:  # Intenta obtenerla desde la ruta (ej: .../YYYY/MM/DD/...)
                parts = source_file.parts
                if len(parts) >= 4 and parts[-2].isdigit() and parts[-3].isdigit() and parts[-4].isdigit():
                    fecha_str = f"{parts[-4]}-{parts[-3]}-{parts[-2]}"
            
            # Obtiene la fuente desde el directorio padre
            if source_file.is_dir():
                fuente_str = source_file.name
            else:
                fuente_str = source_file.parent.name
        except Exception:
            pass

    nst = len(stations) if stations else 0
    if stations:
        vals = [p['precip_mm'] for p in stations if p.get('precip_mm') is not None]
        vmin = min(vals) if vals else float('nan')
        vmax = max(vals) if vals else float('nan')
    else:
        vmin = vmax = float('nan')

    precip_max_str = f"{vmax:.2f} mm" if not math.isnan(vmax) else "N/A"
    precip_min_str = f"{vmin:.2f} mm" if not math.isnan(vmin) else "N/A"

    return (
        f"Fuente: {fuente_str}\n"
        f"Fecha: {fecha_str}\n"
        f"Estaciones: {nst}\n"
        f"Precip. Máx: {precip_max_str}\n"
        f"Precip. Mín: {precip_min_str}"
    )

def render_description(context: Dict[str, Any]) -> str:
    """
    DESCRIPCIÓN: retorna texto desde contexto/config/texts, con soporte de fecha si está disponible.
    Prioridad: context['description_text'] > config.DESCRIPTION_TEXT > texts['description'].
    Si la plantilla contiene {fecha}, se reemplaza; caso contrario se anexa al final.
    """
    # 1) Prioridad de texto base
    user_text = context.get('description_text')
    if not user_text:
        try:
            import config as CFG
            user_text = getattr(CFG, 'DESCRIPTION_TEXT', None)
        except Exception:
            user_text = None
    base_text = None
    if not user_text:
        try:
            from box_config.texts import get_text
            try:
                import config as CFG
                locale = context.get('locale') or getattr(CFG, 'LOCALE', 'es')
            except Exception:
                locale = context.get('locale') or 'es'
            base_text = get_text('description', locale=locale, default=None)
        except Exception:
            base_text = None
    template_text = user_text or base_text or ''

    # 2) Enriquecer con fecha si disponible
    source_file = context.get('source_file')
    fecha_str = None
    if source_file:
        try:
            match = re.search(r'_(\d{8})_', source_file.name)
            if match:
                date_obj = datetime.strptime(match.group(1), '%Y%m%d')
                fecha_str = date_obj.strftime('%Y-%m-%d')
            else:
                parts = source_file.parts
                if len(parts) >= 4 and parts[-2].isdigit() and parts[-3].isdigit() and parts[-4].isdigit():
                    fecha_str = f"{parts[-4]}-{parts[-3]}-{parts[-2]}"
        except Exception:
            pass

    if fecha_str:
        if '{fecha}' in template_text:
            return template_text.replace('{fecha}', fecha_str)
        return f"{template_text} ({fecha_str})"
    return template_text or ''

def render_observations(context: Dict[str, Any]) -> str:
    """
    Genera el texto para la caja de OBSERVACIONES con prioridad:
    1) context['observations_text']
    2) config.OBSERVATIONS_TEXT
    3) texts.get_text('observations', locale)
    4) default
    """
    # 1) Contexto directo
    text = context.get('observations_text')
    if text:
        return text

    # 2) Configuración global (override rápido)
    try:
        import config as CFG
        cfg_text = getattr(CFG, 'OBSERVATIONS_TEXT', None)
    except Exception:
        cfg_text = None
    if cfg_text:
        return cfg_text

    # 3) Catálogo de textos centralizados
    try:
        from box_config.texts import get_text
        locale = context.get('locale')
        if not locale:
            # Intentar desde config si existe
            try:
                import config as CFG
                locale = getattr(CFG, 'LOCALE', 'es')
            except Exception:
                locale = 'es'
        catalog_text = get_text('observations', locale=locale, default=None)
    except Exception:
        catalog_text = None
    if catalog_text:
        return catalog_text

    # 4) Fallback por defecto
    return "PROYECTO DE INVESTIGACION CEDIA I+D+I 62 - 2023"

def render_credits(context: Dict[str, Any]) -> str:
    """
    CREDITS (último cajón vertical): prioridad de resolución
    1) context['credits_text'] > 2) config.CREDITS_TEXT > 3) texts['credits'] > 4) default.
    """
    # 1) Contexto directo
    text = context.get('credits_text')
    if text:
        return text
    # 2) Config global
    try:
        import config as CFG
        cfg_text = getattr(CFG, 'CREDITS_TEXT', None)
    except Exception:
        cfg_text = None
    if cfg_text:
        return cfg_text
    # 3) Catálogo
    try:
        from box_config.texts import get_text
        try:
            import config as CFG
            locale = context.get('locale') or getattr(CFG, 'LOCALE', 'es')
        except Exception:
            locale = context.get('locale') or 'es'
        t = get_text('credits', locale=locale, default=None)
    except Exception:
        t = None
    if t:
        return t
    # 4) Fallback
    return (
        "MAPA DE ISOYETAS\nROBERTO CARLOS\nTOAPANTA GUAMÁN\n\n"
        "INVESTIGADOR\nANALISTA DE REDES\nGEOFISICO 2"
    )

# --- Registro de renderers de contenido ---
# La PageTemplate buscará aquí la función a usar según la configuración de la caja.
def render_timeseries_info(context: Dict[str, Any]) -> str:
    """
    Renderiza texto de INFORMACIÓN para series temporales.
    Prioridad de override: context['timeseries_info_text'] > config.TIMESERIES_INFO_TEXT.
    Si no hay override, compone a partir de contexto: estación, rango de fechas, n puntos.
    """
    # Overrides
    try:
        txt = context.get('timeseries_info_text')
        if not txt:
            import config as CFG
            txt = getattr(CFG, 'TIMESERIES_INFO_TEXT', None)
    except Exception:
        txt = None
    if txt:
        return str(txt)

    st = context.get('ts_station') or 'N/A'
    npts = context.get('ts_count') or 0
    start = context.get('ts_start') or 'N/A'
    end = context.get('ts_end') or 'N/A'
    return (
        f"Estación: {st}\n" 
        f"Desde: {start}\n"
        f"Hasta: {end}\n"
        f"Muestras: {npts}"
    )

CONTENT_RENDERERS = {
    'isoyetas_info': render_isoyetas_info,
    'description': render_description,
    'observations': render_observations,
    'credits': render_credits,
    'timeseries_info': render_timeseries_info,
    # --- Se pueden añadir más renderers para otros tipos de gráficos aquí ---
    # 'seismic_info': render_seismic_info,
}
