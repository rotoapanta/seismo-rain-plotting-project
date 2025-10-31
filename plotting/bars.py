from __future__ import annotations
from typing import Sequence, Dict, Any, Optional, Iterable, Any
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import config as CFG
from utils.logger_config import logger
from ui.page_template import PageTemplate
from ui.theme import bar_style


def _resolve_style(defaults: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    st = dict(defaults)
    if override:
        st.update({k: v for k, v in override.items() if v is not None})
    return st


def plot_bars(ax: Axes, x: Sequence[float] | np.ndarray, heights: Sequence[float] | np.ndarray,
              theme: Dict[str, Any], label: Optional[str] = None,
              style: Optional[Dict[str, Any]] = None):
    """Plot a simple bar series with unified style from theme."""
    defaults = bar_style(theme)
    st = _resolve_style(defaults, style)
    bars = ax.bar(x, heights, label=label, **st)
    return bars


def plot_grouped_bars(ax: Axes, x: Sequence[float] | np.ndarray, groups: Sequence[Sequence[float]] | np.ndarray,
                       theme: Dict[str, Any], labels: Optional[Sequence[str]] = None,
                       style: Optional[Dict[str, Any]] = None):
    """Grouped bar chart with identical base style across series."""
    x = np.asarray(x)
    groups = [np.asarray(g) for g in groups]
    n_series = len(groups)
    defaults = bar_style(theme)
    width_total = defaults.get('width', 0.8)
    width = width_total / n_series
    st = _resolve_style(defaults, style)
    st['width'] = width

    handles = []
    for i, g in enumerate(groups):
        offs = (i - (n_series - 1) / 2.0) * width
        h = ax.bar(x + offs, g, label=labels[i] if labels else None, **st)
        handles.append(h)
    return handles


def plot_stacked_bars(ax: Axes, x: Sequence[float] | np.ndarray, layers: Sequence[Sequence[float]] | np.ndarray,
                       theme: Dict[str, Any], labels: Optional[Sequence[str]] = None,
                       style: Optional[Dict[str, Any]] = None):
    """Stacked bar chart with consistent style."""
    x = np.asarray(x)
    layers = [np.asarray(l) for l in layers]
    defaults = bar_style(theme)
    st = _resolve_style(defaults, style)

    cum = np.zeros_like(layers[0], dtype=float)
    handles = []
    for i, l in enumerate(layers):
        h = ax.bar(x, l, bottom=cum, label=labels[i] if labels else None, **st)
        handles.append(h)
        cum += l
    return handles


# -----------------------------------------------------------------------------
# Render de barras con PageTemplate (misma integración que isoyetas/timeseries)
# -----------------------------------------------------------------------------

def render_bars_graph(
    values: Iterable[float],
    *,
    times: Optional[Iterable[Any]] = None,
    title: Optional[str] = None,
    output_dir: Optional[Path] = None,
    image_format: Optional[str] = None,
    popup: Optional[bool] = None,
    context_overrides: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Dibuja un gráfico de barras dentro del área de contenido del PageTemplate(kind='bars') y guarda el resultado.
    """
    # Salida
    out_dir = Path(getattr(CFG, 'OUTPUT_DIR_BARS', 'output/bars')) if output_dir is None else Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    img_fmt = (image_format or getattr(CFG, 'IMAGE_FORMAT', 'pdf')).lower()
    show_popup = bool(popup if popup is not None else getattr(CFG, 'POPUP_WINDOW', False))

    # Plantilla
    template = PageTemplate(kind='bars', theme=getattr(CFG, 'THEME', None))
    fig = template.fig

    # Área de contenido
    left, bottom, width, height = template.areas.content_box
    ax = fig.add_axes([left, bottom, width, height])

    # Datos
    y = np.asarray(list(values), dtype=float)
    npts = y.shape[0]

    # Eje X: horas si se proporcionan tiempos
    use_time_axis = False
    x = np.arange(npts)
    if times is not None:
        t_list = list(times)
        if len(t_list) == npts and npts > 0:
            try:
                from datetime import datetime as _dt
                first = t_list[0]
                if isinstance(first, (_dt, np.datetime64)):
                    use_time_axis = True
                    x = t_list
            except Exception:
                pass

    # Estilos de barras
    face_color = getattr(CFG, 'BARS_FACE_COLOR', '#1f77b4')
    edge_color = getattr(CFG, 'BARS_EDGE_COLOR', '#1f77b4')
    alpha = float(getattr(CFG, 'BARS_ALPHA', 0.9))

    # Dibujar barras (ajustando ancho cuando el eje X es temporal)
    if use_time_axis:
        try:
            import matplotlib.dates as mdates
            x_num = mdates.date2num(x)
            if len(x_num) > 1:
                diffs = np.diff(np.sort(x_num))
                spacing = float(np.nanmin(diffs)) if diffs.size else 1.0
            else:
                spacing = 1.0
            width_frac = float(getattr(CFG, 'BARS_BAR_WIDTH_FRACTION', 0.8))
            width_frac = max(0.05, min(1.0, width_frac))
            bar_width = spacing * width_frac
            ax.bar(x_num, y, width=bar_width, color=face_color, edgecolor=edge_color, alpha=alpha, align='center')
        except Exception:
            ax.bar(x, y, color=face_color, edgecolor=edge_color, alpha=alpha)
    else:
        ax.bar(x, y, color=face_color, edgecolor=edge_color, alpha=alpha)

    # Ejes y títulos
    # Formato de ejes y etiquetas
    if use_time_axis:
        try:
            import matplotlib.dates as mdates
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # Rotación de etiquetas X
            try:
                rot = float(getattr(CFG, 'BARS_XTICK_ROTATION', 90))
            except Exception:
                rot = 90
            for lbl in ax.get_xticklabels():
                lbl.set_rotation(rot)
                lbl.set_ha('center')
            # Rango de día completo (00:00 a 24:00) si no hay XLIM definido
            try:
                xlim_cfg = getattr(CFG, 'BARS_XLIM', None)
                if not (isinstance(xlim_cfg, (list, tuple)) and len(xlim_cfg) == 2 and None not in xlim_cfg):
                    xnums = mdates.date2num(x)
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
        except Exception:
            pass
    ax.set_xlabel(getattr(CFG, 'BARS_X_LABEL', 'Hora'))
    ax.set_ylabel(getattr(CFG, 'BARS_Y_LABEL', 'Precipitación (mm)'))

    # Escala y límites desde config
    try:
        yscale = str(getattr(CFG, 'BARS_YSCALE', 'linear'))
        if yscale:
            ax.set_yscale(yscale)
    except Exception:
        pass
    try:
        ylim = getattr(CFG, 'BARS_YLIM', None)
        if isinstance(ylim, (list, tuple)) and len(ylim) == 2 and None not in ylim:
            ax.set_ylim(float(ylim[0]), float(ylim[1]))
    except Exception:
        pass
    try:
        xlim = getattr(CFG, 'BARS_XLIM', None)
        if isinstance(xlim, (list, tuple)) and len(xlim) == 2 and None not in xlim:
            if use_time_axis:
                import matplotlib.dates as mdates
                def to_num(val):
                    import numpy as _np
                    from datetime import datetime as _dt
                    if isinstance(val, (_dt, _np.datetime64)):
                        return mdates.date2num(val)
                    return float(val)
                ax.set_xlim(to_num(xlim[0]), to_num(xlim[1]))
            else:
                ax.set_xlim(float(xlim[0]), float(xlim[1]))
    except Exception:
        pass

    # Título
    bars_title = title or getattr(CFG, 'BARS_TITLE', 'BARRAS')
    ax.set_title(
        bars_title,
        fontsize=getattr(CFG, 'BARS_TITLE_FONT_SIZE', 12),
        fontweight=getattr(CFG, 'BARS_TITLE_FONT_WEIGHT', 'bold'),
        color=getattr(CFG, 'BARS_TITLE_COLOR', '#0941DA'),
        loc=getattr(CFG, 'BARS_TITLE_LOC', 'center'),
        pad=float(getattr(CFG, 'BARS_TITLE_PAD_PT', 6) or 0),
    )

    # Estilo de etiquetas y ticks
    ax.xaxis.label.set_size(getattr(CFG, 'BARS_AXIS_LABEL_FONT_SIZE', getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_SIZE', 9)))
    ax.xaxis.label.set_color(getattr(CFG, 'BARS_AXIS_LABEL_COLOR', getattr(CFG, 'TIMESERIES_AXIS_LABEL_COLOR', '#333333')))
    try:
        ax.xaxis.label.set_weight(getattr(CFG, 'BARS_AXIS_LABEL_FONT_WEIGHT', getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_WEIGHT', 'normal')))
    except Exception:
        pass

    ax.yaxis.label.set_size(getattr(CFG, 'BARS_AXIS_LABEL_FONT_SIZE', getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_SIZE', 9)))
    ax.yaxis.label.set_color(getattr(CFG, 'BARS_AXIS_LABEL_COLOR', getattr(CFG, 'TIMESERIES_AXIS_LABEL_COLOR', '#333333')))
    try:
        ax.yaxis.label.set_weight(getattr(CFG, 'BARS_AXIS_LABEL_FONT_WEIGHT', getattr(CFG, 'TIMESERIES_AXIS_LABEL_FONT_WEIGHT', 'normal')))
    except Exception:
        pass

    for tick in ax.get_xticklabels():
        tick.set_fontsize(getattr(CFG, 'BARS_TICK_LABEL_FONT_SIZE', getattr(CFG, 'TIMESERIES_TICK_LABEL_FONT_SIZE', 8)))
        tick.set_color(getattr(CFG, 'BARS_TICK_LABEL_COLOR', getattr(CFG, 'TIMESERIES_TICK_LABEL_COLOR', '#4D4D4D')))
    for tick in ax.get_yticklabels():
        tick.set_fontsize(getattr(CFG, 'BARS_TICK_LABEL_FONT_SIZE', getattr(CFG, 'TIMESERIES_TICK_LABEL_FONT_SIZE', 8)))
        tick.set_color(getattr(CFG, 'BARS_TICK_LABEL_COLOR', getattr(CFG, 'TIMESERIES_TICK_LABEL_COLOR', '#4D4D4D')))

    # Espaciado físico de ticks en Y (cm) para escala lineal
    try:
        if str(getattr(CFG, 'BARS_YSCALE', 'linear')) == 'linear':
            spacing_cm = float(getattr(CFG, 'BARS_YTICK_SPACING_CM', 0) or 0)
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
    if getattr(CFG, 'BARS_GRID', getattr(CFG, 'TIMESERIES_GRID', True)):
        ax.grid(
            True,
            ls=getattr(CFG, 'BARS_GRID_LINESTYLE', getattr(CFG, 'TIMESERIES_GRID_LINESTYLE', '--')),
            alpha=float(getattr(CFG, 'BARS_GRID_ALPHA', getattr(CFG, 'TIMESERIES_GRID_ALPHA', 0.3))),
            color=getattr(CFG, 'BARS_GRID_COLOR', getattr(CFG, 'TIMESERIES_GRID_COLOR', '#DDDDDD'))
        )
    else:
        ax.grid(False)

    # Contexto para paneles dinámicos (si fuese necesario)
    template.context['bars_count'] = int(npts)
    template.context['bars_min'] = float(np.nanmin(y)) if npts else float('nan')
    template.context['bars_max'] = float(np.nanmax(y)) if npts else float('nan')
    template.context['bars_mean'] = float(np.nanmean(y)) if npts else float('nan')
    if context_overrides:
        template.context.update(context_overrides)

    # Finalizar (panel lateral y pie) usando misma extensión que otras figuras
    bars_extent = getattr(CFG, 'BARS_EXTENT', getattr(CFG, 'TIMESERIES_EXTENT', getattr(CFG, 'EXTENT', None)))
    template.finalize(ax=ax, extent=bars_extent, stations=None, source_file=None)

    # Guardar
    plt.rcParams['savefig.bbox'] = 'standard'
    fig.patch.set_facecolor('white')
    ts_now = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = out_dir / f'bars_{ts_now}.{img_fmt}'
    fig.savefig(out_path, dpi=getattr(CFG, 'IMAGE_DPI', 150))
    logger.info(f"Barras guardado en: {out_path}")

    if show_popup:
        try:
            plt.show()
        except Exception:
            pass
    else:
        plt.close(fig)

    return out_path
