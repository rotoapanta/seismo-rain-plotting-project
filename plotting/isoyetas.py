from __future__ import annotations
"""
Módulo para el gráfico de isoyetas con el nombre estandarizado `isoyetas_graph`.

Expone:
    - render_isoyetas_graph: función que genera el mapa de isoyetas sobre PageTemplate.

Uso recomendado:
    from plotting.isoyetas import render_isoyetas_graph
"""

from typing import List, Tuple, Optional
from pathlib import Path
from datetime import datetime
import math

import numpy as np
import matplotlib.pyplot as plt

import config as CFG
from utils.logger_config import logger
from ui.page_template import PageTemplate
# from ui.theme import apply_theme  # eliminado: llamada redundante


# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------

def compute_levels(Z: np.ndarray) -> np.ndarray:
    """Calcula niveles de isoyetas con fallback si no hay valores válidos."""
    if CFG.ISOHYET_LEVELS is not None:
        logger.info(f"Usando niveles de isoyetas definidos en config: {CFG.ISOHYET_LEVELS}")
        return np.array(CFG.ISOHYET_LEVELS, dtype=float)
    vmin = float(np.nanmin(Z))
    vmax = float(np.nanmax(Z))
    if not np.isfinite(vmin) or not np.isfinite(vmax) or math.isclose(vmin, vmax):
        vmax = vmin + 1.0
    levels = np.linspace(vmin, vmax, 10)
    logger.info(f"Calculando niveles de isoyetas automáticamente: {levels}")
    return levels


# --------------------------------------------------------------
# Render principal de Isoyetas sobre PageTemplate
# --------------------------------------------------------------

def render_isoyetas_graph(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    stations: List[dict],
    extent: Tuple[float, float, float, float],
    *,
    source_file: Optional[Path] = None,
) -> Path:
    """
    Dibuja el mapa de isoyetas dentro de un PageTemplate(kind='isoyetas') y guarda el resultado.

    - Respeta PageTemplate para: márgenes, panel lateral y pie.
    - Usa Cartopy si está disponible para fondo y cuadrícula geográfica.
    - Aplica el tema global.
    """
    # Directorio de salida
    out_dir = Path(CFG.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Tema y plantilla
    template = PageTemplate(kind='isoyetas', theme=getattr(CFG, 'THEME', None))
    fig = template.fig

    # Área de contenido
    left, bottom, width, height = template.areas.content_box

    ax = None
    tiles = None

    # Crear eje con proyección apropiada
    try:
        import cartopy.crs as ccrs
        projection = ccrs.PlateCarree()

        if getattr(CFG, 'MAP_BACKGROUND', False) and getattr(CFG, 'USE_TILE_BACKGROUND', False):
            import cartopy.io.img_tiles as cimgt
            provider_name = getattr(CFG, 'TILE_PROVIDER', 'Stamen-terrain')
            if provider_name == 'OSM':
                tiles = cimgt.OSM()
            else:
                tiles = cimgt.Stamen('terrain-background')
            projection = tiles.crs

        if getattr(CFG, 'MAP_BACKGROUND', False):
            ax = fig.add_axes([left, bottom, width, height], projection=projection)
        else:
            ax = fig.add_axes([left, bottom, width, height])

    except ImportError:
        ax = fig.add_axes([left, bottom, width, height])

    # Fondo y extensión
    if getattr(CFG, 'MAP_BACKGROUND', False) and hasattr(ax, 'coastlines'):
        try:
            import cartopy.crs as ccrs
            ax.set_extent(extent, crs=ccrs.PlateCarree())
            if tiles:
                zoom_level = int(getattr(CFG, 'TILE_ZOOM_LEVEL', 10))
                alpha = float(getattr(CFG, 'TILE_BACKGROUND_ALPHA', 1.0))
                ax.add_image(tiles, zoom_level, zorder=0, interpolation='spline36', alpha=alpha)
            else:
                import cartopy.feature as cfeature
                resolution = getattr(CFG, 'MAP_BACKGROUND_RESOLUTION', '110m')
                land_color = getattr(CFG, 'MAP_BACKGROUND_LAND_COLOR', '#F0F0F0')
                ocean_color = getattr(CFG, 'MAP_BACKGROUND_OCEAN_COLOR', '#D0E7FF')
                coastline_color = getattr(CFG, 'MAP_BACKGROUND_COASTLINE_COLOR', 'black')
                border_color = getattr(CFG, 'MAP_BACKGROUND_BORDER_COLOR', 'gray')
                ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none', zorder=0)
                ax.add_feature(cfeature.OCEAN, facecolor=ocean_color, edgecolor='none', zorder=0.1)
                ax.add_feature(cfeature.BORDERS.with_scale(resolution), edgecolor=border_color, linestyle=':', zorder=3.8)
                # Añadir divisiones políticas (provincias)
                ax.add_feature(cfeature.STATES, edgecolor='black', linestyle=':', linewidth=0.5, zorder=3.85)
                # Añadir carreteras
                ax.add_feature(cfeature.ROADS, edgecolor='gray', linestyle='--', linewidth=0.5, zorder=4.1)
                ax.add_feature(cfeature.COASTLINE.with_scale(resolution), edgecolor=coastline_color, zorder=4.0)
        except Exception:
            pass

    # Contornos e isoyetas
    levels = compute_levels(Z)
    try:
        import cartopy.crs as ccrs
        transform = ccrs.PlateCarree() if hasattr(ax, 'coastlines') else None
    except Exception:
        transform = None

    cf = ax.contourf(
        X, Y, Z,
        levels=levels,
        cmap='Blues',
        alpha=float(getattr(CFG, 'ISOHYET_ALPHA', 0.8)),
        zorder=1,
        transform=transform
    )
    c = ax.contour(
        X, Y, Z,
        levels=levels,
        colors='k',
        linewidths=0.6,
        alpha=0.9,
        zorder=2,
        transform=transform
    )
    ax.clabel(c, inline=True, fontsize=8, fmt='%.1f')

    # Estaciones
    if transform is not None:
        ax.scatter([p['lon'] for p in stations], [p['lat'] for p in stations], c='red', edgecolors='black', s=40, zorder=5, transform=transform, marker='o')
        for p in stations:
            ax.text(p['lon'] + 0.01, p['lat'], p['station_id'], fontsize=8, color='black', ha='left', va='bottom', zorder=4, transform=transform)
    else:
        ax.scatter([p['lon'] for p in stations], [p['lat'] for p in stations], c='red', edgecolors='black', s=40, zorder=5, marker='o')
        for p in stations:
            ax.text(p['lon'] + 0.01, p['lat'], p['station_id'], fontsize=8, color='black', ha='left', va='bottom', zorder=4)

    # Grid / ejes
    if hasattr(ax, 'gridlines'):
        try:
            import cartopy.crs as ccrs  # noqa: F401
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color=getattr(CFG, 'ISOYETAS_TICK_LABEL_COLOR', 'darkgray'), alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlabel_style = {'size': getattr(CFG, 'ISOYETAS_AXIS_LABEL_FONT_SIZE', 9), 'color': getattr(CFG, 'ISOYETAS_AXIS_LABEL_COLOR', '#000000'), 'weight': getattr(CFG, 'ISOYETAS_AXIS_LABEL_FONT_WEIGHT', 'normal')}
            gl.ylabel_style = {'size': getattr(CFG, 'ISOYETAS_AXIS_LABEL_FONT_SIZE', 9), 'color': getattr(CFG, 'ISOYETAS_AXIS_LABEL_COLOR', '#000000'), 'weight': getattr(CFG, 'ISOYETAS_AXIS_LABEL_FONT_WEIGHT', 'normal')}
        except Exception:
            ax.set_xlabel(getattr(CFG, 'ISOYETAS_X_LABEL', 'Longitud (°)'))
            ax.set_ylabel(getattr(CFG, 'ISOYETAS_Y_LABEL', 'Latitud (°)'))
    else:
        ax.set_xlabel(getattr(CFG, 'ISOYETAS_X_LABEL', 'Longitud (°)'))
        ax.set_ylabel(getattr(CFG, 'ISOYETAS_Y_LABEL', 'Latitud (°)'))

    ax.tick_params(axis='x', colors=getattr(CFG, 'ISOYETAS_TICK_LABEL_COLOR', '#A9A9A9'), labelsize=getattr(CFG, 'ISOYETAS_TICK_LABEL_FONT_SIZE', 8))
    ax.tick_params(axis='y', colors=getattr(CFG, 'ISOYETAS_TICK_LABEL_COLOR', '#A9A9A9'), labelsize=getattr(CFG, 'ISOYETAS_TICK_LABEL_FONT_SIZE', 8))
    ax.set_title(getattr(CFG, 'ISOYETAS_TITLE', 'Isoyetas'), color=getattr(CFG, 'ISOYETAS_TITLE_COLOR', 'black'))
    ax.grid(True, ls='--', alpha=0.3)
    ax.set_aspect('equal')

    # Colorbar contigua al área de contenido
    if getattr(CFG, 'SHOW_COLORBAR', True):
        pos = ax.get_position()
        fig_w_cm, fig_h_cm = template.areas.fig_w_cm, template.areas.fig_h_cm
        cb_w = max(1e-3, float(getattr(CFG, 'COLORBAR_WIDTH_CM', 0.6)) / fig_w_cm)
        cb_pad = max(0.0, float(getattr(CFG, 'COLORBAR_PAD_CM', 0.2)) / fig_w_cm)
        cb_rect = [pos.x1 + cb_pad, pos.y0, cb_w, pos.height]
        cb_ax = fig.add_axes(cb_rect)
        cb = fig.colorbar(plt.cm.ScalarMappable(), cax=cb_ax, label='Precipitación (mm)')
        try:
            cb.update_normal(cf)
        except Exception:
            pass

    # Finalizar plantilla: panel lateral y pie
    template.finalize(ax=ax, extent=extent, stations=stations, source_file=source_file)

    # Guardar
    import re
    plt.rcParams['savefig.bbox'] = 'standard'
    fig.patch.set_facecolor('white')

    # Generar timestamp a partir del nombre del archivo de origen o usar fecha actual
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    if source_file:
        match = re.search(r'_(\d{8})_(\d{4})', source_file.name)
        if match:
            ts = f"{match.group(1)}_{match.group(2)}"

    out_path = out_dir / f'isoyetas_{ts}.{CFG.IMAGE_FORMAT}'
    fig.savefig(out_path, dpi=CFG.IMAGE_DPI)
    logger.info(f"Mapa de isoyetas guardado en: {out_path}")

    if CFG.POPUP_WINDOW:
        try:
            plt.show()
        except Exception:
            pass
    else:
        plt.close(fig)

    return out_path
