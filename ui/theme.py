from __future__ import annotations
from typing import Dict, Any
import matplotlib as mpl

# Theme application and style helpers

DEFAULT_THEME: Dict[str, Any] = {
    'font': {
        'family': 'DejaVu Sans',
        'base_size': 9,
        'sizes': {
            'title': 12,
            'axis_label': 10,
            'tick': 9,
            'legend': 9,
            'box_title': 10,
            'box_text': 8,
        },
        'weight': {
            'title': 'bold',
            'axis_label': 'normal',
            'box_title': 'bold',
        }
    },
    'colors': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'accent': '#2ca02c',
        'text': '#222222',
        'grid': '#D0D0D0',
        'frame': '#000000',
        'bars': '#4C78A8',
        'bars_edge': '#1F3A5A',
    },
    'axes': {
        'facecolor': 'white',
        'edgecolor': '#333333',
        'linewidth': 0.8,
        'grid': True,
        'grid_linestyle': '--',
        'grid_linewidth': 0.6,
        'grid_alpha': 0.6,
    },
    'legend': {
        'frameon': False,
        'loc': 'best',
    },
    'bars': {
        'width': 0.8,
        'alpha': 0.9,
        'edgecolor': '#1F3A5A',
        'facecolor': '#4C78A8',
        'linewidth': 0.8,
    },
    'lines': {
        'linewidth': 1.5,
    }
}


def merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def apply_theme(theme: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Apply matplotlib rcParams from theme and return the resolved theme dict."""
    th = merge_dict(DEFAULT_THEME, theme or {})

    # Fonts
    mpl.rcParams['font.family'] = th['font']['family']
    mpl.rcParams['font.size'] = th['font']['base_size']

    # Axes
    mpl.rcParams['axes.facecolor'] = th['axes']['facecolor']
    mpl.rcParams['axes.edgecolor'] = th['axes']['edgecolor']
    mpl.rcParams['axes.linewidth'] = th['axes']['linewidth']
    mpl.rcParams['axes.titlesize'] = th['font']['sizes']['title']
    mpl.rcParams['axes.titleweight'] = th['font']['weight']['title']
    mpl.rcParams['axes.labelsize'] = th['font']['sizes']['axis_label']

    # Grid
    mpl.rcParams['axes.grid'] = th['axes']['grid']
    mpl.rcParams['grid.linestyle'] = th['axes']['grid_linestyle']
    mpl.rcParams['grid.linewidth'] = th['axes']['grid_linewidth']
    mpl.rcParams['grid.alpha'] = th['axes']['grid_alpha']
    mpl.rcParams['grid.color'] = th['colors']['grid']

    # Ticks
    mpl.rcParams['xtick.labelsize'] = th['font']['sizes']['tick']
    mpl.rcParams['ytick.labelsize'] = th['font']['sizes']['tick']

    # Legend
    mpl.rcParams['legend.frameon'] = th['legend']['frameon']
    mpl.rcParams['legend.fontsize'] = th['font']['sizes']['legend']

    # Lines default
    mpl.rcParams['lines.linewidth'] = th['lines']['linewidth']

    return th


def text_style(role: str, th: Dict[str, Any]) -> Dict[str, Any]:
    sizes = th['font']['sizes']
    weights = th['font']['weight']
    if role == 'title':
        return dict(fontsize=sizes['title'], fontweight=weights['title'], color=th['colors']['text'])
    if role == 'axis_label':
        return dict(fontsize=sizes['axis_label'], color=th['colors']['text'])
    if role == 'legend':
        return dict(fontsize=sizes['legend'], color=th['colors']['text'])
    if role == 'box_title':
        return dict(fontsize=sizes['box_title'], fontweight=weights['box_title'], color=th['colors']['text'])
    if role == 'box_text':
        return dict(fontsize=sizes['box_text'], color=th['colors']['text'])
    return dict(color=th['colors']['text'])


def axis_style(th: Dict[str, Any]) -> Dict[str, Any]:
    return dict(edgecolor=th['axes']['edgecolor'], linewidth=th['axes']['linewidth'])


def bar_style(th: Dict[str, Any]) -> Dict[str, Any]:
    return dict(
        width=th['bars']['width'],
        alpha=th['bars']['alpha'],
        edgecolor=th['bars']['edgecolor'],
        color=th['bars']['facecolor'],
        linewidth=th['bars']['linewidth'],
    )


def get_palette(th: Dict[str, Any]):
    return [th['colors']['primary'], th['colors']['secondary'], th['colors']['accent']]
