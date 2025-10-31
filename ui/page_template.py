from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import textwrap
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

import config as CFG
from utils.logger_config import logger
from ui.theme import apply_theme, text_style


@dataclass
class TemplateAreas:
    fig_w_cm: float
    fig_h_cm: float
    content_box: Tuple[float, float, float, float]  # [left, bottom, width, height] in figure fraction


class PageTemplate:
    """Plantilla unificada con: marco doble opcional, panel lateral derecho, pie de página e área de contenido.
    
    - kind: permite cambiar cajas según tipo (e.g., 'isoyetas', 'timeseries').
    - theme: aplica estilos globales.
    """
    def _haversine_distance(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calcula la distancia en km entre dos puntos usando la fórmula de Haversine."""
        R = 6371.0
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlon, dlat = lon2_rad - lon1_rad, lat2_rad - lat1_rad
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _get_nice_scale_number(self, distance_km: float) -> float:
        """Redondea una distancia a un número 'bonito' para la escala."""
        if distance_km <= 0:
            return 0
        power = math.floor(math.log10(distance_km))
        base = 10**power
        rescaled = distance_km / base
        if rescaled >= 10:
            return 10 * base
        if rescaled >= 5:
            return 5 * base
        if rescaled >= 2:
            return 2 * base
        return 1 * base

    def __init__(self, kind: str = 'default', theme: Optional[Dict[str, Any]] = None):
        self.kind = kind
        self.theme = apply_theme(theme or getattr(CFG, 'THEME', None))
        self.context: Dict[str, Any] = {}
        self.fig, self.areas = self._create_figure_and_layout()
        self._draw_margins()

    # --------------------------------------------------------------
    # Figura y layout base
    # --------------------------------------------------------------
    def _figure_size(self) -> Tuple[float, float, float, float]:
        ps = getattr(CFG, 'PAPER_SIZE', None)
        sizes = getattr(CFG, 'PAPER_SIZES_CM', {})
        if isinstance(ps, str) and ps in sizes:
            w_cm, h_cm = sizes[ps]
            orient = str(getattr(CFG, 'MAP_ORIENTATION', 'landscape')).lower()
            if orient == 'landscape' and h_cm > w_cm:
                w_cm, h_cm = h_cm, w_cm
            if orient == 'portrait' and w_cm > h_cm:
                w_cm, h_cm = h_cm, w_cm
        else:
            w_cm, h_cm = getattr(CFG, 'ISOYETAS_SIZE_CM', (29.7, 21.0))
            if getattr(CFG, 'MAP_ORIENTATION', 'landscape').lower() == 'portrait':
                w_cm, h_cm = h_cm, w_cm
        fig_w, fig_h = float(w_cm / 2.54), float(h_cm / 2.54)
        fig_w_cm, fig_h_cm = fig_w * 2.54, fig_h * 2.54
        return fig_w, fig_h, fig_w_cm, fig_h_cm

    def _to_frac(self, fig_w_cm: float, fig_h_cm: float, x_cm: float, y_cm: float, w_cm: float, h_cm: float):
        return (
            max(0.0, min(1.0, float(x_cm) / fig_w_cm)),
            max(0.0, min(1.0, float(y_cm) / fig_h_cm)),
            max(1e-6, min(1.0, float(w_cm) / fig_w_cm)),
            max(1e-6, min(1.0, float(h_cm) / fig_h_cm)),
        )

    def _create_figure_and_layout(self) -> Tuple[plt.Figure, TemplateAreas]:
        fig_w, fig_h, fig_w_cm, fig_h_cm = self._figure_size()
        fig = plt.figure(figsize=(fig_w, fig_h))

        # Márgenes de página (L, R, T, B)
        L_cm, R_cm, T_cm, B_cm = [float(x) for x in getattr(CFG, 'PAGE_MARGINS_CM', (1.5, 1.5, 1.5, 1.5))]

        # Anchos/altos de paneles
        right_bar_w_cm = float(getattr(CFG, 'SIDE_BOX_WIDTH_CM', 6.0)) if getattr(CFG, 'DRAW_SIDE_BOXES', True) else 0.0
        footer_h_cm = float(getattr(CFG, 'FOOTER_ROW_HEIGHT_CM', 5.0)) if getattr(CFG, 'DRAW_FOOTER_BOXES', True) else 0.0

        # Área de contenido (en cm)
        if self.kind == 'isoyetas':
            box = getattr(CFG, 'ISOYETAS_BOX_CM', None)
            if box is not None:
                try:
                    content_left_cm, content_bottom_cm, content_w_cm, content_h_cm = [float(v) for v in box]
                except Exception:
                    # Fallback a márgenes si el formato no es correcto
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
            else:
                size = getattr(CFG, 'ISOYETAS_SIZE_CM', None)
                offset = getattr(CFG, 'ISOYETAS_OFFSET_CM', None)
                if size is not None and offset is not None and len(size) == 2 and len(offset) == 2:
                    try:
                        content_left_cm = float(offset[0])
                        content_bottom_cm = float(offset[1])
                        content_w_cm = float(size[0])
                        content_h_cm = float(size[1])
                    except Exception:
                        content_left_cm = L_cm
                        content_bottom_cm = B_cm + footer_h_cm
                        content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                        content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
                else:
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
        elif self.kind == 'timeseries':
            box = getattr(CFG, 'TIMESERIES_BOX_CM', None)
            if box is not None:
                try:
                    content_left_cm, content_bottom_cm, content_w_cm, content_h_cm = [float(v) for v in box]
                except Exception:
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
            else:
                size = getattr(CFG, 'TIMESERIES_SIZE_CM', None)
                offset = getattr(CFG, 'TIMESERIES_OFFSET_CM', None)
                if size is not None and offset is not None and len(size) == 2 and len(offset) == 2:
                    try:
                        content_left_cm = float(offset[0])
                        content_bottom_cm = float(offset[1])
                        content_w_cm = float(size[0])
                        content_h_cm = float(size[1])
                    except Exception:
                        content_left_cm = L_cm
                        content_bottom_cm = B_cm + footer_h_cm
                        content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                        content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
                else:
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
        elif self.kind == 'bars':
            box = getattr(CFG, 'BARS_BOX_CM', None)
            if box is not None:
                try:
                    content_left_cm, content_bottom_cm, content_w_cm, content_h_cm = [float(v) for v in box]
                except Exception:
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
            else:
                size = getattr(CFG, 'BARS_SIZE_CM', None)
                offset = getattr(CFG, 'BARS_OFFSET_CM', None)
                if size is not None and offset is not None and len(size) == 2 and len(offset) == 2:
                    try:
                        content_left_cm = float(offset[0])
                        content_bottom_cm = float(offset[1])
                        content_w_cm = float(size[0])
                        content_h_cm = float(size[1])
                    except Exception:
                        content_left_cm = L_cm
                        content_bottom_cm = B_cm + footer_h_cm
                        content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                        content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
                else:
                    content_left_cm = L_cm
                    content_bottom_cm = B_cm + footer_h_cm
                    content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
                    content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)
        else:
            content_left_cm = L_cm
            content_bottom_cm = B_cm + footer_h_cm
            content_w_cm = max(0.1, fig_w_cm - L_cm - R_cm - right_bar_w_cm)
            content_h_cm = max(0.1, fig_h_cm - T_cm - B_cm - footer_h_cm)

        left, bottom, width, height = self._to_frac(fig_w_cm, fig_h_cm, content_left_cm, content_bottom_cm, content_w_cm, content_h_cm)
        fig.subplots_adjust(left=left, right=left + width, bottom=bottom, top=bottom + height)

        areas = TemplateAreas(fig_w_cm=fig_w_cm, fig_h_cm=fig_h_cm, content_box=(left, bottom, width, height))
        return fig, areas

    def _draw_margins(self):
        if not getattr(CFG, 'DRAW_DOUBLE_MARGINS', False):
            return
        try:
            fig_w_cm, fig_h_cm = self.areas.fig_w_cm, self.areas.fig_h_cm
            L_cm, R_cm, T_cm, B_cm = [float(x) for x in getattr(CFG, 'PAGE_MARGINS_CM', (0.5, 0.5, 0.5, 0.5))]
            off2 = float(getattr(CFG, 'DOUBLE_MARGIN_OFFSET_CM', 0.3))
            color = getattr(CFG, 'DOUBLE_MARGINS_COLOR', 'black')
            lw = float(getattr(CFG, 'DOUBLE_MARGINS_LINEWIDTH', 0.56693))
            alpha = float(getattr(CFG, 'DOUBLE_MARGINS_ALPHA', 1.0))

            def add_frame(l_cm, r_cm, t_cm, b_cm):
                left = max(0.0, min(1.0, l_cm / fig_w_cm))
                bottom = max(0.0, min(1.0, b_cm / fig_h_cm))
                width = max(1e-6, 1.0 - (l_cm + r_cm) / fig_w_cm)
                height = max(1e-6, 1.0 - (t_cm + b_cm) / fig_h_cm)
                rect = Rectangle((left, bottom), width, height, fill=False, edgecolor=color, linewidth=lw, alpha=alpha, transform=self.fig.transFigure, clip_on=False)
                self.fig.add_artist(rect)

            add_frame(L_cm, R_cm, T_cm, B_cm)
            add_frame(L_cm + off2, R_cm + off2, T_cm + off2, B_cm + off2)
        except Exception:
            pass

    # --------------------------------------------------------------
    # API de contenido
    # --------------------------------------------------------------
    def add_content_axes(self, nrows: int = 1, ncols: int = 1, index: int = 1):
        """Devuelve un Axes dentro del área de contenido. Soporta grillas via nrows/ncols/index."""
        if nrows == 1 and ncols == 1:
            ax = self.fig.add_subplot(1, 1, 1)
            return ax
        else:
            from matplotlib.gridspec import GridSpec
            left, bottom, width, height = self.areas.content_box
            gs = GridSpec(nrows, ncols, left=left, right=left + width, bottom=bottom, top=bottom + height, figure=self.fig)
            ax = self.fig.add_subplot(gs[index - 1])
            return ax

    # --------------------------------------------------------------
    # Panel lateral y pie de página
    # --------------------------------------------------------------
    def draw_side_bar(self):
        if not getattr(CFG, 'DRAW_SIDE_BOXES', True):
            return
        fig_w_cm, fig_h_cm = self.areas.fig_w_cm, self.areas.fig_h_cm
        right_margin_cm = float(getattr(CFG, 'SIDE_BOX_RIGHT_CM', 1.0))
        box_width_cm = float(getattr(CFG, 'SIDE_BOX_WIDTH_CM', 6.0))
        top_margin_cm = float(getattr(CFG, 'SIDE_BOX_TOP_CM', 1.0))
        gap_cm = float(getattr(CFG, 'SIDE_BOX_GAP_CM', 0.0))
        edge_color = getattr(CFG, 'SIDE_BOX_EDGE_COLOR', 'black')
        edge_lw_pt = float(getattr(CFG, 'SIDE_BOX_EDGE_LINEWIDTH_PT', 0.56693))
        tit_row_h_cm = float(getattr(CFG, 'SIDE_BOX_TITLE_ROW_HEIGHT_CM', 1.0))

        y_cursor = fig_h_cm - top_margin_cm
        boxes = getattr(CFG, f'VERTICAL_BOXES_{self.kind.upper()}', getattr(CFG, 'VERTICAL_BOXES', []))
        for box in boxes:
            h_cm = box['size_cm']
            x_cm = fig_w_cm - right_margin_cm - box_width_cm
            y_cm = y_cursor - h_cm

            left, bottom, width, height = self._to_frac(fig_w_cm, fig_h_cm, x_cm, y_cm, box_width_cm, h_cm)
            rect = Rectangle((left, bottom), width, height, fill=False, edgecolor=edge_color, linewidth=edge_lw_pt, transform=self.fig.transFigure, clip_on=False)
            self.fig.add_artist(rect)
            # Doble marco opcional para cajas verticales (soporta claves antiguas y actuales de config)
            if getattr(CFG, 'SIDE_BOX_DOUBLE_FRAME', getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER', False)):
                off_cm = float(getattr(CFG, 'SIDE_BOX_DOUBLE_FRAME_OFFSET_CM', getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER_OFFSET_CM', 0.2)))
                off_x = off_cm / fig_w_cm
                off_y = off_cm / fig_h_cm
                inner_edge_color = getattr(CFG, 'SIDE_BOX_DOUBLE_FRAME_COLOR', getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER_COLOR', edge_color))
                inner_edge_lw_pt = float(getattr(CFG, 'SIDE_BOX_DOUBLE_FRAME_LINEWIDTH_PT', getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER_LINEWIDTH_PT', edge_lw_pt)))
                inner_rect = Rectangle((left + off_x, bottom + off_y), max(1e-6, width - 2*off_x), max(1e-6, height - 2*off_y), fill=False, edgecolor=inner_edge_color, linewidth=inner_edge_lw_pt, transform=self.fig.transFigure, clip_on=False)
                self.fig.add_artist(inner_rect)

            # Título (con opciones para encajar/alinear)
            if box.get('title'):
                st = text_style('box_title', self.theme)
                title_y = bottom + height - (tit_row_h_cm / fig_h_cm) / 2.0

                # Dibujar línea separadora bajo el título (similar al pie)
                if getattr(CFG, 'SIDE_BOX_DRAW_TITLE_SEPARATOR', True):
                    sep_y = bottom + height - (tit_row_h_cm / fig_h_cm)
                    self.fig.add_artist(Line2D([left, left + width], [sep_y, sep_y],
                                               transform=self.fig.transFigure,
                                               color=getattr(CFG, 'SIDE_BOX_TITLE_SEPARATOR_COLOR', edge_color),
                                               linewidth=float(getattr(CFG, 'SIDE_BOX_TITLE_SEPARATOR_LINEWIDTH_PT', edge_lw_pt)),
                                               clip_on=False))

                # Opciones por caja para el título
                topts = box.get('title_options', {})
                t_align = topts.get('align', 'center')  # 'left' | 'center' | 'right'
                t_pad_cm = float(topts.get('pad_cm', 0.2))
                t_wrap_width = int(topts.get('wrap_width', 40))

                # Wrapping respetando saltos de línea
                raw_title = str(box.get('title', ''))
                wrapped_title = "\n".join(
                    textwrap.fill(line, width=t_wrap_width)
                    for line in raw_title.splitlines()
                )

                # Posición horizontal según alineación
                if t_align == 'left':
                    tx = left + (t_pad_cm / fig_w_cm)
                    ha = 'left'
                elif t_align == 'right':
                    tx = left + width - (t_pad_cm / fig_w_cm)
                    ha = 'right'
                else:
                    tx = left + width / 2.0
                    ha = 'center'

                self.fig.text(tx, title_y, wrapped_title, ha=ha, va='center', **st)

            # Contenido
            self._draw_box_content(left, bottom, width, height, box, tit_row_h_cm)

            y_cursor -= (h_cm + gap_cm)

    def draw_footer_bar(self):
        if not getattr(CFG, 'DRAW_FOOTER_BOXES', True):
            return
        try:
            import cartopy.crs as ccrs
            import cartopy.feature as cfeature
            from matplotlib.patches import Polygon
        except ImportError:
            logger.error("Cartopy no está instalado. El minimapa no se puede renderizar.")
            ccrs = cfeature = Polygon = None

        fig_w_cm, fig_h_cm = self.areas.fig_w_cm, self.areas.fig_h_cm
        row_bottom = float(getattr(CFG, 'FOOTER_ROW_BOTTOM_CM', 1.0))
        row_height = float(getattr(CFG, 'FOOTER_ROW_HEIGHT_CM', 5.0))
        left_margin = float(getattr(CFG, 'FOOTER_LEFT_MARGIN_CM', 0.5))
        if getattr(CFG, 'FOOTER_ALIGN_WITH_MAP_OFFSETS', False):
            try:
                if self.kind == 'isoyetas':
                    left_margin = float(getattr(CFG, 'ISOYETAS_OFFSET_CM', (left_margin, 0.0))[0])
                elif self.kind == 'timeseries':
                    # Mantener el pie alineado con el offset de isoyetas para evitar que cambiar
                    # TIMESERIES_OFFSET_CM mueva las cajas inferiores.
                    left_margin = float(getattr(CFG, 'ISOYETAS_OFFSET_CM', (left_margin, 0.0))[0])
                elif self.kind == 'bars':
                    # Alinear también barras con el offset de isoyetas para uniformidad
                    left_margin = float(getattr(CFG, 'ISOYETAS_OFFSET_CM', (left_margin, 0.0))[0])
            except Exception:
                pass
        gap_cm = float(getattr(CFG, 'FOOTER_GAP_CM', 0.3))
        edge_color = getattr(CFG, 'FOOTER_EDGE_COLOR', 'black')
        edge_lw_pt = float(getattr(CFG, 'FOOTER_EDGE_LINEWIDTH_PT', 0.56693))
        tit_row_h_cm = float(getattr(CFG, 'FOOTER_TITLE_ROW_HEIGHT_CM', 1.0))

        x_cursor = left_margin
        boxes = getattr(CFG, f'HORIZONTAL_BOXES_{self.kind.upper()}', getattr(CFG, 'HORIZONTAL_BOXES', []))
        for box in boxes:
            w_cm = box['size_cm']
            x_cm, y_cm, h_cm = x_cursor, row_bottom, row_height
            left, bottom, width, height = self._to_frac(fig_w_cm, fig_h_cm, x_cm, y_cm, w_cm, h_cm)

            rect = Rectangle((left, bottom), width, height, fill=False, edgecolor=edge_color, linewidth=edge_lw_pt, transform=self.fig.transFigure, clip_on=False)
            self.fig.add_artist(rect)
            # Doble marco opcional para cajas horizontales (pie) — compatible con claves actuales en config
            if getattr(CFG, 'FOOTER_BOX_DOUBLE_FRAME', getattr(CFG, 'FOOTER_DOUBLE_BORDER', False)):
                off_cm = float(getattr(CFG, 'FOOTER_BOX_DOUBLE_FRAME_OFFSET_CM', getattr(CFG, 'FOOTER_DOUBLE_BORDER_OFFSET_CM', 0.2)))
                off_x = off_cm / fig_w_cm
                off_y = off_cm / fig_h_cm
                inner_edge_color = getattr(CFG, 'FOOTER_BOX_DOUBLE_FRAME_COLOR', getattr(CFG, 'FOOTER_DOUBLE_BORDER_COLOR', edge_color))
                inner_edge_lw_pt = float(getattr(CFG, 'FOOTER_BOX_DOUBLE_FRAME_LINEWIDTH_PT', getattr(CFG, 'FOOTER_DOUBLE_BORDER_LINEWIDTH_PT', edge_lw_pt)))
                inner_rect = Rectangle((left + off_x, bottom + off_y), max(1e-6, width - 2*off_x), max(1e-6, height - 2*off_y), fill=False, edgecolor=inner_edge_color, linewidth=inner_edge_lw_pt, transform=self.fig.transFigure, clip_on=False)
                self.fig.add_artist(inner_rect)

            # Línea divisoria para título
            sep_y = bottom + height - (tit_row_h_cm / fig_h_cm)
            self.fig.add_artist(Line2D([left, left + width], [sep_y, sep_y], transform=self.fig.transFigure, color=edge_color, linewidth=edge_lw_pt, clip_on=False))

            # Título
            if box.get('title'):
                st = text_style('box_title', self.theme)
                title_y = sep_y + (tit_row_h_cm / fig_h_cm) / 2.0
                self.fig.text(left + width / 2.0, title_y, box['title'], ha='center', va='center', **st)

            # Contenido
            self._draw_box_content(left, bottom, width, height, box, tit_row_h_cm, footer=True, ccrs=ccrs, cfeature=cfeature)

            x_cursor += w_cm + gap_cm

    # --------------------------------------------------------------
    # Render de contenido de las cajas
    # --------------------------------------------------------------
    def _draw_box_content(self, left: float, bottom: float, width: float, height: float,
                          box: Dict[str, Any], tit_row_h_cm: float, footer: bool = False,
                          ccrs=None, cfeature=None):
        content = box.get('content', {})
        content_type = content.get('type')
        fig = self.fig
        fig_w_cm, fig_h_cm = self.areas.fig_w_cm, self.areas.fig_h_cm

        # Extraer datos del contexto
        extent = self.context.get('extent')
        stations = self.context.get('stations')

        if content_type == 'logo':
            try:
                logo_path = content.get('options', {}).get('path', 'images/logo-ig.png')
                logger.info(f"Añadiendo logo desde: {logo_path}")
                import matplotlib.image as mpimg
                img = mpimg.imread(logo_path)

                # Usar dimensiones de config.py
                target_size_cm = float(getattr(CFG, 'LOGO_TARGET_SIZE_CM', 3.0))
                img_h, img_w, _ = img.shape
                aspect_ratio = img_w / img_h

                if img_w >= img_h:
                    logo_w_cm = target_size_cm
                    logo_h_cm = target_size_cm / aspect_ratio
                else:
                    logo_h_cm = target_size_cm
                    logo_w_cm = target_size_cm * aspect_ratio

                # Convertir a fracción de la figura
                logo_w_frac = logo_w_cm / fig_w_cm
                logo_h_frac = logo_h_cm / fig_h_cm

                # Centrar el logo en la caja contenedora
                box_center_x = left + width / 2.0
                box_center_y = bottom + height / 2.0
                
                logo_left = box_center_x - logo_w_frac / 2.0
                logo_bottom = box_center_y - logo_h_frac / 2.0

                ax = fig.add_axes([logo_left, logo_bottom, logo_w_frac, logo_h_frac])
                ax.imshow(img, aspect='equal')  # 'equal' preserva la proporción de la imagen
                ax.axis('off')
            except Exception as e:
                logger.error(f"Error al renderizar el logo: {e}")
                pass

        elif content_type == 'text':
            logger.info(f"Añadiendo texto estático: {content.get('options', {}).get('value')}")
            st = text_style('box_text', self.theme)
            txt = content.get('options', {}).get('value', '')
            pad_cm = float(content.get('options', {}).get('pad_cm', 0.2))
            wrap_width = int(content.get('options', {}).get('wrap_width', 35))
            
            # Opciones de alineación
            text_align = content.get('options', {}).get('text_align', 'left')
            vertical_align = content.get('options', {}).get('vertical_align', 'top')
            bold_lines = content.get('options', {}).get('bold_lines')  # lista 1-based

            # Usar textwrap respetando saltos de línea explícitos
            wrapped_lines = [
                textwrap.fill(line, width=wrap_width)
                for line in txt.splitlines()
            ]
            # Expandir por líneas resultantes
            expanded_lines = []
            for seg in wrapped_lines:
                expanded_lines.extend(seg.splitlines())

            text_ax_left = left + (pad_cm / fig_w_cm)
            text_ax_bottom = bottom + (pad_cm / fig_h_cm)
            text_ax_width = width - 2 * (pad_cm / fig_w_cm)
            text_ax_height = height - (tit_row_h_cm / fig_h_cm) - 2 * (pad_cm / fig_h_cm)
            
            text_ax = fig.add_axes([text_ax_left, text_ax_bottom, text_ax_width, text_ax_height])
            text_ax.axis('off')
            
            if bold_lines:
                # Renderizado línea por línea con negritas selectivas
                n = len(expanded_lines)
                line_step = 0.12  # fracción del eje por línea (aprox)
                # Posición inicial según alineación vertical
                if vertical_align == 'center':
                    y0 = 0.5 + (line_step * (n-1) / 2.0)
                elif vertical_align == 'bottom':
                    y0 = 0.05 + line_step * (n-1)
                else:  # top
                    y0 = 0.95
                x_pos = {'left': 0, 'center': 0.5, 'right': 1.0}.get(text_align, 0)
                for i, line in enumerate(expanded_lines, start=1):
                    y = y0 - (i-1) * line_step
                    style = dict(**st)
                    if isinstance(bold_lines, (list, tuple)) and i in bold_lines:
                        style['fontweight'] = 'bold'
                    text_ax.text(x_pos, y, line, ha=text_align, va='top', **style)
            else:
                # Renderizado estándar de bloque
                x_pos = {'left': 0, 'center': 0.5, 'right': 1.0}.get(text_align, 0)
                y_pos = {'top': 0.95, 'center': 0.5, 'bottom': 0.05}.get(vertical_align, 0.95)
                text_ax.text(x_pos, y_pos, "\n".join(expanded_lines), ha=text_align, va=vertical_align, **st)

        elif content_type == 'dynamic_text':
            try:
                renderer_name = content.get('options', {}).get('renderer')
                if not renderer_name:
                    logger.warning("No se especificó un 'renderer' para el texto dinámico.")
                    return

                from box_config.content import CONTENT_RENDERERS
                renderer_func = CONTENT_RENDERERS.get(renderer_name)
                
                if not renderer_func:
                    logger.error(f"El renderer '{renderer_name}' no fue encontrado.")
                    return

                logger.info(f"Renderizando texto dinámico con '{renderer_name}'.")
                info_text = renderer_func(self.context)

                st = text_style('box_text', self.theme)
                st.setdefault('fontsize', 8)
                st.setdefault('color', '#333333')
                pad_cm = float(content.get('options', {}).get('pad_cm', 0.2))
                wrap_width = int(content.get('options', {}).get('wrap_width', 40))

                # Opciones de alineación
                text_align = content.get('options', {}).get('text_align', 'left')
                vertical_align = content.get('options', {}).get('vertical_align', 'top')

                # Usar textwrap respetando saltos de línea explícitos
                wrapped_lines = [
                    textwrap.fill(line, width=wrap_width)
                    for line in info_text.splitlines()
                ]
                expanded_lines = []
                for seg in wrapped_lines:
                    expanded_lines.extend(seg.splitlines())

                text_ax_left = left + (pad_cm / fig_w_cm)
                text_ax_bottom = bottom + (pad_cm / fig_h_cm)
                text_ax_width = width - 2 * (pad_cm / fig_w_cm)
                text_ax_height = height - (tit_row_h_cm / fig_h_cm) - 2 * (pad_cm / fig_h_cm)

                text_ax = fig.add_axes([text_ax_left, text_ax_bottom, text_ax_width, text_ax_height])
                text_ax.axis('off')

                bold_lines = content.get('options', {}).get('bold_lines')
                if bold_lines:
                    n = len(expanded_lines)
                    line_step = 0.12
                    if vertical_align == 'center':
                        y0 = 0.5 + (line_step * (n-1) / 2.0)
                    elif vertical_align == 'bottom':
                        y0 = 0.05 + line_step * (n-1)
                    else:
                        y0 = 0.95
                    x_pos = {'left': 0, 'center': 0.5, 'right': 1.0}.get(text_align, 0)
                    for i, line in enumerate(expanded_lines, start=1):
                        y = y0 - (i-1) * line_step
                        style = dict(**st)
                        if isinstance(bold_lines, (list, tuple)) and i in bold_lines:
                            style['fontweight'] = 'bold'
                        text_ax.text(x_pos, y, line, ha=text_align, va='top', **style)
                else:
                    x_pos = {'left': 0, 'center': 0.5, 'right': 1.0}.get(text_align, 0)
                    y_pos = {'top': 0.95, 'center': 0.5, 'bottom': 0.05}.get(vertical_align, 0.95)
                    text_ax.text(x_pos, y_pos, "\n".join(expanded_lines), ha=text_align, va=vertical_align, **st)

            except Exception as e:
                logger.error(f"Error al renderizar el texto dinámico: {e}")
                pass

        elif content_type == 'symbology':
            try:
                logger.info("Añadiendo simbología.")
                pad_cm = float(getattr(CFG, 'SYMBOLOGY_PADDING_CM', 0.3))
                ax_left = left + (pad_cm / fig_w_cm)
                ax_bottom = bottom + (pad_cm / fig_h_cm)
                ax_width = width - 2 * (pad_cm / fig_w_cm)
                ax_height = height - 2 * (pad_cm / fig_h_cm) - (tit_row_h_cm / fig_h_cm)
                sym_ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
                sym_ax.patch.set_visible(False)
                sym_ax.set_xlim(0, 1)
                sym_ax.set_ylim(0, 1)
                sym_ax.axis('off')
                legend_items, legend_labels = [], []
                
                # Estaciones
                legend_items.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='black', markersize=8, markeredgewidth=1.0))
                legend_labels.append('Estaciones')
                
                # Isoyetas
                legend_items.append(Line2D([0], [0], color='black', linewidth=1.0, alpha=1.0))
                legend_labels.append('Isoyetas (mm)')

                # Carreteras
                legend_items.append(Line2D([0], [0], color='gray', linewidth=1.0, linestyle='-'))
                legend_labels.append('Carreteras')

                # Divisiones Políticas
                legend_items.append(Line2D([0], [0], color='black', linewidth=0.5, linestyle=':'))
                legend_labels.append('Divisiones Políticas')

                sym_ax.legend(legend_items, legend_labels, loc='center left', fontsize=self.theme['font']['sizes']['legend'], frameon=False, facecolor='none')
            except Exception:
                pass

        elif content_type == 'minimap' and footer and ccrs is not None and cfeature is not None:
            try:
                logger.info("Añadiendo minimapa.")
                from matplotlib.patches import Polygon
                pad_cm = float(getattr(CFG, 'MINIMAP_PADDING_CM', 0.1))
                ax_left = left + (pad_cm / fig_w_cm)
                ax_bottom = bottom + (pad_cm / fig_h_cm)
                ax_width = width - 2 * (pad_cm / fig_w_cm)
                ax_height = height - 2 * (pad_cm / fig_h_cm) - (tit_row_h_cm / fig_h_cm)
                ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height], projection=ccrs.PlateCarree())
                land_color = getattr(CFG, 'MINIMAP_LAND_COLOR', '#E0E0E0')
                ocean_color = getattr(CFG, 'MINIMAP_OCEAN_COLOR', '#FFFFFF')
                coastline_color = getattr(CFG, 'MINIMAP_COASTLINE_COLOR', 'black')
                border_color = getattr(CFG, 'MINIMAP_BORDER_COLOR', 'gray')
                resolution = getattr(CFG, 'MINIMAP_CARTOPY_RESOLUTION', '110m')
                logger.info(f"Añadiendo características al minimapa: LAND, OCEAN, COASTLINE, BORDERS")
                ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none')
                ax.add_feature(cfeature.OCEAN, facecolor=ocean_color, edgecolor='none')
                ax.add_feature(cfeature.COASTLINE.with_scale(resolution), edgecolor=coastline_color)
                ax.add_feature(cfeature.BORDERS.with_scale(resolution), edgecolor=border_color, linestyle=':')

                mode = str(getattr(CFG, 'MINIMAP_MODE', 'auto')).lower()
                if mode == 'world':
                    # Mostrar mapa global independientemente del extent
                    ax.set_global()
                    logger.info("Minimapa en modo 'world' activado: mostrando mapa global.")
                elif extent:
                    lon_min, lon_max, lat_min, lat_max = extent
                    zoom_factor = getattr(CFG, 'MINIMAP_ZOOM_FACTOR', 1.5)
                    lon_pad = (lon_max - lon_min) * zoom_factor
                    lat_pad = (lat_max - lat_min) * zoom_factor
                    zoom_extent = [lon_min - lon_pad, lon_max + lon_pad, lat_min - lat_pad, lat_max + lat_pad]
                    ax.set_extent(zoom_extent, crs=ccrs.PlateCarree())
                    logger.info(f"Añadiendo extensión al minimapa: {extent}")
                    poly = Polygon([(extent[0], extent[2]), (extent[1], extent[2]), (extent[1], extent[3]), (extent[0], extent[3])], closed=True, color=getattr(CFG, 'MINIMAP_EXTENT_COLOR', 'red'), alpha=getattr(CFG, 'MINIMAP_EXTENT_ALPHA', 0.5), transform=ccrs.PlateCarree())
                    ax.add_patch(poly)
                else:
                    # Sin extent, usar mapa global como fallback para mantener consistencia
                    ax.set_global()
                    logger.info("No hay extent para minimapa; usando vista global por defecto.")
            except Exception as e:
                logger.error(f"Error al renderizar el minimapa: {e}")
                # Dibuja un cuadro vacío con un texto de error
                ax = fig.add_axes([left, bottom, width, height])
                ax.text(0.5, 0.5, "Error al renderizar el minimapa", ha='center', va='center', fontsize=8, color='red')
                ax.set_xticks([])
                ax.set_yticks([])
                pass
        elif content_type == 'north_arrow_scale':
            logger.info("Añadiendo rosa de los vientos y escala.")
            # Dibuja flecha del norte y barra de escala simple/segmentada en el pie
            pad_cm = float(getattr(CFG, 'NORTH_ARROW_SCALE_PADDING_CM', 0.3))
            ax_left = left + (pad_cm / fig_w_cm)
            ax_bottom = bottom + (pad_cm / fig_h_cm)
            ax_width = width - 2 * (pad_cm / fig_w_cm)
            ax_height = height - 2 * (pad_cm / fig_h_cm) - (tit_row_h_cm / fig_h_cm)
            ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
            ax.patch.set_visible(False)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            # Flecha del Norte
            try:
                style = getattr(CFG, 'NORTH_ARROW_STYLE', 'image')
                if style == 'image':
                    import matplotlib.image as mpimg
                    img_path = getattr(CFG, 'NORTH_ARROW_IMAGE_PATH', 'images/image.png')
                    img = mpimg.imread(img_path)
                    w_cm = float(getattr(CFG, 'NORTH_ARROW_IMAGE_WIDTH_CM', 2.5))
                    h_cm = float(getattr(CFG, 'NORTH_ARROW_IMAGE_HEIGHT_CM', 2.5))
                    w = w_cm / fig_w_cm
                    h = h_cm / fig_h_cm
                    # Colocar cerca del centro superior
                    cx, cy = 0.5, min(0.95, max(0.55, float(getattr(CFG, 'NORTH_ARROW_Y_POS', 0.65))))
                    ax_img = fig.add_axes([ax_left + cx * ax_width - w/2.0, ax_bottom + cy * ax_height - h/2.0, w, h])
                    ax_img.imshow(img)
                    ax_img.axis('off')
                else:
                    # Fallback básico con texto 'N'
                    ax.text(0.5, 0.8, 'N', ha='center', va='center', fontsize=getattr(CFG, 'NORTH_ARROW_FONT_SIZE', 10), fontweight=getattr(CFG, 'NORTH_ARROW_FONT_WEIGHT', 'bold'), color=getattr(CFG, 'NORTH_ARROW_TEXT_COLOR', '#000000'))
                    ax.plot([0.5, 0.5], [0.55, 0.75], color=getattr(CFG, 'NORTH_ARROW_EDGE_COLOR', '#000000'), lw=2)
                    ax.plot([0.47, 0.5, 0.53], [0.72, 0.75, 0.72], color=getattr(CFG, 'NORTH_ARROW_EDGE_COLOR', '#000000'), lw=2)
            except Exception:
                pass

            # Barra de escala
            try:
                if not extent:
                    logger.warning("No se puede dibujar la barra de escala: falta la extensión del mapa (extent).")
                    return

                style = getattr(CFG, 'SCALE_BAR_STYLE', 'simple')
                if style == 'segmented':
                    # TODO: Implementar cálculo automático para escala segmentada si es necesario.
                    logger.warning("El cálculo automático de escala solo está implementado para el estilo 'simple'.")
                    pass
                else:
                    # --- Barra simple con cálculo automático ---
                    # 1. Geometría del mapa y la barra
                    map_lon_min, map_lon_max, map_lat_min, map_lat_max = extent
                    map_lat_center = (map_lat_min + map_lat_max) / 2.0
                    map_width_deg = map_lon_max - map_lon_min
                    
                    main_map_width_frac = self.areas.content_box[2]
                    scale_ax_width_frac = ax_width
                    
                    x0_frac, x1_frac = getattr(CFG, 'SCALE_BAR_WIDTH_FRACTION', (0.1, 0.8))
                    bar_visual_width_on_ax = x1_frac - x0_frac
                    
                    # 2. Calcular la distancia real que representa la barra visualmente
                    width_ratio = (scale_ax_width_frac * bar_visual_width_on_ax) / main_map_width_frac
                    bar_width_deg = width_ratio * map_width_deg
                    max_bar_dist_km = self._haversine_distance(map_lon_min, map_lat_center, map_lon_min + bar_width_deg, map_lat_center)

                    # 3. Redondear a un número "bonito"
                    nice_dist_km = self._get_nice_scale_number(max_bar_dist_km)
                    if nice_dist_km == 0:
                        return

                    # 4. Ajustar el ancho visual de la barra para que represente el número bonito
                    final_bar_visual_width = bar_visual_width_on_ax * (nice_dist_km / max_bar_dist_km)
                    x1_final = x0_frac + final_bar_visual_width

                    # 5. Dibujar la barra y las etiquetas
                    y = max(0.05, min(0.4, float(getattr(CFG, 'SCALE_BAR_Y_POS', 0.05))))
                    
                    ax.plot([x0_frac, x1_final], [y, y], color=getattr(CFG, 'SCALE_BAR_COLOR', '#000'), lw=getattr(CFG, 'SCALE_BAR_LINE_WIDTH', 1.5))
                    ax.text(x0_frac, y - 0.03, '0', ha='center', va='top', fontsize=getattr(CFG, 'SCALE_BAR_FONT_SIZE', 9), color=getattr(CFG, 'SCALE_BAR_COLOR', '#000'))
                    ax.text(x1_final, y - 0.03, f"{int(nice_dist_km)}", ha='center', va='top', fontsize=getattr(CFG, 'SCALE_BAR_FONT_SIZE', 9), color=getattr(CFG, 'SCALE_BAR_COLOR', '#000'))
                    ax.text(x1_final + 0.05, y - 0.03, 'Km', ha='left', va='top', fontsize=getattr(CFG, 'SCALE_BAR_FONT_SIZE', 9), color=getattr(CFG, 'SCALE_BAR_COLOR', '#000'))

            except Exception as e:
                logger.error(f"Error al dibujar la barra de escala automática: {e}")
                pass

    # --------------------------------------------------------------
    # Finalización (dibujar marcos laterales y pie)
    # --------------------------------------------------------------
    def finalize(self, ax=None, extent=None, stations=None, source_file: Optional[Any] = None):
        # Guardar contexto para dynamic_text
        self.context['ax'] = ax
        self.context['extent'] = extent
        self.context['stations'] = stations
        self.context['source_file'] = source_file
        # Textos configurables para renderers
        try:
            import config as CFG
            self.context['observations_text'] = getattr(CFG, 'OBSERVATIONS_TEXT', None)
            self.context['description_text'] = getattr(CFG, 'DESCRIPTION_TEXT', None)
            self.context['information_text'] = getattr(CFG, 'INFORMATION_TEXT', None)
            self.context['credits_text'] = getattr(CFG, 'CREDITS_TEXT', None)
            if 'locale' not in self.context:
                self.context['locale'] = getattr(CFG, 'LOCALE', 'es')
        except Exception:
            pass
        # Dibujar paneles
        self.draw_side_bar()
        self.draw_footer_bar()
        return self.fig
