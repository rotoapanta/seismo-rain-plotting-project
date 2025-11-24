from __future__ import annotations
"""
Módulo para graficar series temporales usando el mismo marco (PageTemplate) y
cajas, pero con kind='timeseries' para cambiar el contenido dinámico del panel
INFORMACIÓN y mantener los títulos.

Expone:
    - render_timeseries_graph: genera la figura de series temporales y la guarda.

Uso recomendado:
    from plotting.timeseries import render_timeseries_graph
"""

from typing import Iterable, Optional, Any, Dict
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

import config as CFG
from utils.logger_config import logger
from ui.page_template import PageTemplate


def _is_datetime_like(x: Iterable[Any]) -> bool:
    try:
        first = next(iter(x))
    except StopIteration:
        return False
    return isinstance(first, (datetime, np.datetime64))


def render_timeseries_graph(
    times: Iterable[Any],
    values: Iterable[float],
    *,
    station: Optional[str] = None,
    title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    image_format: Optional[str] = None,
    popup: Optional[bool] = None,
    context_overrides: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Dibuja una serie temporal en el área de contenido de PageTemplate(kind='timeseries')
    y guarda el resultado.

    Parámetros:
    - times: iterable de tiempos (datetime, np.datetime64 o numérico)
    - values: iterable de valores float
    - station: nombre/código de estación (para panel INFORMACIÓN)
    - title: título del gráfico principal (si None, usa CFG.TIMESERIES_TITLE o un default)
    - output_dir: directorio de salida (si None, usa CFG.OUTPUT_DIR_TIMESERIES o 'output/timeseries')
    - image_format: formato de la imagen (si None, usa CFG.IMAGE_FORMAT)
    - popup: mostrar ventana emergente (si None, usa CFG.POPUP_WINDOW)
    - context_overrides: dict opcional para inyectar claves adicionales a template.context
    """
    # Salida
    out_dir = Path(getattr(CFG, 'OUTPUT_DIR_TIMESERIES', 'output/timeseries')) if output_dir is None else Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img_fmt = (image_format or getattr(CFG, 'IMAGE_FORMAT', 'pdf')).lower()
    show_popup = bool(popup if popup is not None else getattr(CFG, 'POPUP_WINDOW', False))

    # Plantilla: mismo marco, distinto kind para cajas
    template = PageTemplate(kind='timeseries', theme=getattr(CFG, 'THEME', None))
    fig = template.fig

    # Área de contenido
    left, bottom, width, height = template.areas.content_box
    ax = fig.add_axes([left, bottom, width, height])

    # Datos
    t = list(times)
    y = np.asarray(list(values), dtype=float)
    npts = len(y)

    # Ejes y trazado
    if _is_datetime_like(t):
        try:
            import matplotlib.dates as mdates
            ax.plot(
                t,
                y,
                getattr(CFG, 'TIMESERIES_LINE_STYLE', '-'),
                color=getattr(CFG, 'TIMESERIES_LINE_COLOR', '#1f77b4'),
                lw=float(getattr(CFG, 'TIMESERIES_LINE_WIDTH', 1.5)),
                marker=getattr(CFG, 'TIMESERIES_MARKER', None),
                markersize=float(getattr(CFG, 'TIMESERIES_MARKER_SIZE', 3.0))
            )
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # Rotación de etiquetas X
            try:
                rot = float(getattr(CFG, 'TIMESERIES_XTICK_ROTATION', 90))
            except Exception:
                rot = 90
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(rot)
                lbl.set_ha('center')
            # Rango de día completo (00:00 a 24:00) si no hay XLIM definido
            try:
                xlim_cfg = getattr(CFG, 'TIMESERIES_XLIM', None)
                if not (isinstance(xlim_cfg, (list, tuple)) and len(xlim_cfg) == 2 and None not in xlim_cfg):
                    xnums = mdates.date2num(t)
                    dmin = mdates.num2date(np.nanmin(xnums))
                    dmax = mdates.num2date(np.nanmax(xnums))
                    from datetime import datetime as _dt, timedelta as _td
                    start = _dt(dmin.year, dmin.month, dmin.day, 0, 0)
                    if dmin.date() != dmax.date():
                        end = _dt(dmax.year, dmax.month, dmax.day, 23, 59, 59)
                    else:
                        end = start + _td(days=1)
                    ax.set_xlim(mdates.date2num(start), mdates.date2num(end))
            except Exception:
                pass
            ax.set_xlabel(getattr(CFG, 'TIMESERIES_X_LABEL', 'Tiempo'))
        except Exception:
            # Fallback como numérico si algo falla
            x = np.arange(npts)
            ax.plot(
                x,
                y,
                getattr(CFG, 'TIMESERIES_LINE_STYLE', '-'),
                color=getattr(CFG, 'TIMESERIES_LINE_COLOR', '#1f77b4'),
                lw=float(getattr(CFG, 'TIMESERIES_LINE_WIDTH', 1.5)),
                marker=getattr(CFG, 'TIMESERIES_MARKER', None),
                markersize=float(getattr(CFG, 'TIMESERIES_MARKER_SIZE', 3.0))
            )
            ax.set_xlabel(getattr(CFG, 'TIMESERIES_X_LABEL', 'Tiempo'))
    else:
        x = np.asarray(t, dtype=float)
        if x.shape[0] != npts:
            x = np.arange(npts)
        ax.plot(
            x,
            y,
            getattr(CFG, 'TIMESERIES_LINE_STYLE', '-'),
            color=getattr(CFG, 'TIMESERIES_LINE_COLOR', '#1f77b4'),
            lw=float(getattr(CFG, 'TIMESERIES_LINE_WIDTH', 1.5)),
            marker=getattr(CFG, 'TIMESERIES_MARKER', None),
            markersize=float(getattr(CFG, 'TIMESERIES_MARKER_SIZE', 3.0))
        )
        ax.set_xlabel(getattr(CFG, 'TIMESERIES_X_LABEL', 'Tiempo'))

    ax.set_ylabel(getattr(CFG, 'TIMESERIES_Y_LABEL', 'Valor'))
    ts_title = title or getattr(CFG, 'TIMESERIES_TITLE', 'SERIE TEMPORAL')
    ax.set_title(
        ts_title,
        fontsize=getattr(CFG, 'TIMESERIES_TITLE_FONT_SIZE', 12),
        fontweight=getattr(CFG, 'TIMESERIES_TITLE_FONT_WEIGHT', 'bold'),
        color=getattr(CFG, 'TIMESERIES_TITLE_COLOR', '#0941DA'),
        loc=getattr(CFG, 'TIMESERIES_TITLE_LOC', 'center'),
        pad=float(getattr(CFG, 'TIMESERIES_TITLE_PAD_PT', 6) or 0),
        fontfamily=getattr(CFG, 'TIMESERIES_TITLE_FONT_FAMILY', None),
        fontname=getattr(CFG, 'TIMESERIES_TITLE_FONT_NAME', None)
    )
    # Etiquetas de ejes y ticks
    ax.xaxis.label.set_size(getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_SIZE', 9))
    ax.xaxis.label.set_color(getattr(CFG, 'TIMESERIES_AXIS_LABEL_COLOR', '#333333'))
    try:
        ax.xaxis.label.set_weight(getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_WEIGHT', 'normal'))
    except Exception:
        pass
    ax.yaxis.label.set_size(getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_SIZE', 9))
    ax.yaxis.label.set_color(getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_COLOR', getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_COLOR', None)) or getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_COLOR', None) or getattr(CFG, 'TIMESERIES_AXIS_LABEL_COLOR', '#333333'))
    try:
        ax.yaxis.label.set_weight(getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_WEIGHT', 'normal'))
    except Exception:
        pass
    for tick in ax.get_xticklabels():
        tick.set_fontsize(getattr(CFG, 'TIMESERIES_TICK_LABEL_FONT_SIZE', 8))
        tick.set_color(getattr(CFG, 'TIMESERIES_TICK_LABEL_COLOR', '#4D4D4D'))
    for tick in ax.get_yticklabels():
        tick.set_fontsize(getattr(CFG, 'TIMESERIES_TICK_LABEL_FONT_SIZE', 8))
        tick.set_color(getattr(CFG, 'TIMESERIES_TICK_LABEL_COLOR', '#4D4D4D'))

    # Escala y límites desde config + espaciado físico en Y
    try:
        yscale = str(getattr(CFG, 'TIMESERIES_YSCALE', 'linear'))
        if yscale:
            ax.set_yscale(yscale)
    except Exception:
        pass
    try:
        ylim = getattr(CFG, 'TIMESERIES_YLIM', None)
        if isinstance(ylim, (list, tuple)) and len(ylim) == 2 and None not in ylim:
            ax.set_ylim(float(ylim[0]), float(ylim[1]))
    except Exception:
        pass
    try:
        xlim = getattr(CFG, 'TIMESERIES_XLIM', None)
        if isinstance(xlim, (list, tuple)) and len(xlim) == 2 and None not in xlim:
            # soporta datetimes
            if _is_datetime_like(t):
                import matplotlib.dates as mdates
                from datetime import datetime as _dt
                import numpy as _np
                def to_num(val):
                    if isinstance(val, (_dt, _np.datetime64)):
                        return mdates.date2num(val)
                    return float(val)
                ax.set_xlim(to_num(xlim[0]), to_num(xlim[1]))
            else:
                ax.set_xlim(float(xlim[0]), float(xlim[1]))
    except Exception:
        pass

    # Espaciado físico de ticks en Y (cm) para escala lineal
    try:
        if str(getattr(CFG, 'TIMESERIES_YSCALE', 'linear')) == 'linear':
            spacing_cm = float(getattr(CFG, 'TIMESERIES_YTICK_SPACING_CM', 0) or 0)
            if spacing_cm > 0:
                bbox = ax.get_position()
                fig_w_in, fig_h_in = fig.get_size_inches()
                axis_h_cm = bbox.height * fig_h_in * 2.54
                if axis_h_cm > 0:
                    import math
                    n = max(1, int(round(axis_h_cm / spacing_cm)))
                    ymin, ymax = ax.get_ylim()
                    data_range = ymax - ymin
                    if data_range > 0 and n > 0:
                        raw = data_range / n
                        power = math.floor(math.log10(raw))
                        base = 10 ** power
                        for c in [1, 2, 2.5, 5, 10]:
                            step = c * base
                            if raw <= step:
                                break
                        from matplotlib.ticker import MultipleLocator
                        ax.yaxis.set_major_locator(MultipleLocator(step))
    except Exception:
        pass

    # Grid
    if getattr(CFG, 'TIMESERIES_GRID', True):
        ax.grid(
            True,
            ls=getattr(CFG, 'TIMESERIES_GRID_LINESTYLE', '--'),
            alpha=float(getattr(CFG, 'TIMESERIES_GRID_ALPHA', 0.3)),
            color=getattr(CFG, 'TIMESERIES_GRID_COLOR', '#DDDDDD')
        )
    else:
        ax.grid(False)

    # Contexto para las cajas dinámicas
    if npts > 0:
        ts_start = t[0]
        ts_end = t[-1]
        # Convertir fechas a string si son datetime
        def _to_str(v: Any) -> str:
            if isinstance(v, datetime):
                return v.strftime('%Y-%m-%d %H:%M')
            return str(v)
        template.context['ts_station'] = station or 'N/A'
        template.context['ts_count'] = npts
        template.context['ts_start'] = _to_str(ts_start)
        template.context['ts_end'] = _to_str(ts_end)
    else:
        template.context['ts_station'] = station or 'N/A'
        template.context['ts_count'] = 0
        template.context['ts_start'] = 'N/A'
        template.context['ts_end'] = 'N/A'

    if context_overrides:
        template.context.update(context_overrides)

    # Finalizar (panel lateral y pie)
    # Extensión para que el minimapa y la escala se comporten igual que en isoyetas
    ts_extent = getattr(CFG, 'TIMESERIES_EXTENT', getattr(CFG, 'EXTENT', None))
    template.finalize(ax=ax, extent=ts_extent, stations=None, source_file=None)

    # Guardar
    plt.rcParams['savefig.bbox'] = 'standard'
    fig.patch.set_facecolor('white')

    # Generar timestamp a partir del primer tiempo de la serie o usar fecha actual
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    if t and _is_datetime_like(t):
        try:
            ts = t[0].strftime('%Y%m%d_%H%M%S')
        except Exception:
            pass

    out_path = out_dir / f'timeseries_{ts}.{img_fmt}'
    fig.savefig(out_path, dpi=getattr(CFG, 'IMAGE_DPI', 150))
    logger.info(f"Serie temporal guardada en: {out_path}")

    if show_popup:
        try:
            plt.show()
        except Exception:
            pass
    else:
        plt.close(fig)

    return out_path
