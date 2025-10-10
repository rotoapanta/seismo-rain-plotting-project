import os
import csv
import json
import math
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import config as CFG
from utils.logger_config import logger


# ----------------------------
# Utilidades de IO de datos
# ----------------------------

def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def ensure_example_real_station() -> Path:
    """
    Garantiza que exista un archivo CSV con una estación real.
    Solo crea un ejemplo si no existe. Formato: station_id,lat,lon,precip_mm
    """
    ensure_dir(CFG.DTA_DIR)
    csv_path = Path(CFG.DTA_DIR) / CFG.REAL_STATION_FILE
    if not csv_path.exists():
        # Crear un ejemplo de estación real (Quito aprox.)
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['station_id', 'lat', 'lon', 'precip_mm'])
            writer.writerow(['REAL1', -0.19, -78.50, 35.0])
    return csv_path


def read_real_station(csv_file: Path) -> Dict[str, float]:
    """Lee una sola estación real desde CSV y retorna un dict con keys: station_id, lat, lon, precip_mm."""
    with csv_file.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if len(rows) == 0:
            raise ValueError(f"El archivo {csv_file} no contiene filas de datos.")
        if len(rows) > 1:
            # Si hay múltiples filas, tomamos la primera y avisamos
            logger.warning(f"Se encontraron {len(rows)} filas en {csv_file}. Se usará solo la primera.")
        row = rows[0]
        return {
            'station_id': str(row['station_id']),
            'lat': float(row['lat']),
            'lon': float(row['lon']),
            'precip_mm': float(row['precip_mm'])
        }


def find_latest_json(base_dir: Path) -> Optional[Path]:
    """Busca recursivamente el JSON más reciente dentro de base_dir. Retorna None si no hay JSONs."""
    if not base_dir.exists():
        logger.warning(f"El directorio base {base_dir} no existe.")
        return None
    logger.info(f"Buscando archivos JSON en: {base_dir}")
    json_files = list(base_dir.rglob('*.json'))
    if not json_files:
        logger.warning("No se encontraron archivos JSON.")
        return None
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Archivo JSON más reciente encontrado: {latest}")
    return latest


def read_real_station_from_json(json_file: Path) -> Dict[str, float]:
    """
    Lee una estación desde un archivo JSON con estructura tipo RGA.
    Usa la última lectura en el arreglo 'LECTURAS'.
    Usa LATITUD, LONGITUD y toma NIVEL como precip_mm (si no existe, 0.0).
    """
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    lecturas = data.get('LECTURAS', [])
    if not lecturas:
        raise ValueError(f"El JSON {json_file} no contiene 'LECTURAS'.")
    last = lecturas[-1]
    lat = float(last.get('LATITUD'))
    lon = float(last.get('LONGITUD'))
    precip = float(last.get('NIVEL', 0.0))
    station_id = str(data.get('NOMBRE') or data.get('IDENTIFICADOR') or 'JSON_STATION')
    logger.info(f"Usando JSON real: {json_file}")
    return {
        'station_id': station_id,
        'lat': lat,
        'lon': lon,
        'precip_mm': max(0.0, precip)
    }


def get_real_station() -> Dict[str, float]:
    """Obtiene la estación real desde el JSON más reciente en DTA. Si no hay, lanza error."""
    base = Path(CFG.DTA_DIR)
    latest_json = find_latest_json(base)
    if latest_json is None:
        raise FileNotFoundError(f"No se encontró ningún archivo JSON en {base} (búsqueda recursiva).")
    return read_real_station_from_json(latest_json)


# ----------------------------
# Generación de datos sintéticos
# ----------------------------

def set_random_seed(seed: Optional[int]) -> None:
    if seed is not None:
        np.random.seed(seed)


def generate_synthetic_stations(real_station: Dict[str, float]) -> List[Dict[str, float]]:
    """
    Genera N estaciones sintéticas alrededor de la estación real con jitter espacial y de precipitación.
    """
    n_syn = int(CFG.SYNTHETIC_STATIONS)
    jitter_deg = float(CFG.SYNTH_JITTER_DEG)
    val_jitter = CFG.SYNTH_VALUE_JITTER_MM
    if isinstance(val_jitter, (list, tuple)) and len(val_jitter) == 2:
        val_jitter_min, val_jitter_max = float(val_jitter[0]), float(val_jitter[1])
    else:
        val_jitter_min, val_jitter_max = -10.0, 10.0

    set_random_seed(CFG.RANDOM_SEED)

    lat0 = real_station['lat']
    lon0 = real_station['lon']
    val0 = real_station['precip_mm']

    syn = []
    for i in range(n_syn):
        dlat = np.random.uniform(-jitter_deg, jitter_deg)
        dlon = np.random.uniform(-jitter_deg, jitter_deg)
        dval = np.random.uniform(val_jitter_min, val_jitter_max)
        syn.append({
            'station_id': f'SYN{i+1}',
            'lat': lat0 + dlat,
            'lon': lon0 + dlon,
            'precip_mm': max(0.0, val0 + dval)  # no negativa
        })
    return syn


# ----------------------------
# Interpolación IDW y grilla
# ----------------------------

def compute_extent(points: List[Dict[str, float]]) -> Tuple[float, float, float, float]:
    if CFG.EXTENT is not None:
        lon_min, lon_max, lat_min, lat_max = CFG.EXTENT
        logger.info(f"Usando extensión definida en config: {CFG.EXTENT}")
        return float(lon_min), float(lon_max), float(lat_min), float(lat_max)

    lats = np.array([p['lat'] for p in points])
    lons = np.array([p['lon'] for p in points])
    # Padding pequeño basado en jitter por defecto o 5% del rango
    pad_lat = max(0.02, 0.1 * (lats.max() - lats.min() + 1e-9))
    pad_lon = max(0.02, 0.1 * (lons.max() - lons.min() + 1e-9))
    extent = (lons.min() - pad_lon, lons.max() + pad_lon, lats.min() - pad_lat, lats.max() + pad_lat)
    logger.info(f"Calculando extensión a partir de las estaciones: {extent}")
    return float(extent[0]), float(extent[1]), float(extent[2]), float(extent[3])


def make_grid(extent: Tuple[float, float, float, float], res_deg: float) -> Tuple[np.ndarray, np.ndarray]:
    lon_min, lon_max, lat_min, lat_max = extent
    xs = np.arange(lon_min, lon_max + res_deg, res_deg)
    ys = np.arange(lat_min, lat_max + res_deg, res_deg)
    X, Y = np.meshgrid(xs, ys)
    return X, Y


def idw_interpolate(X: np.ndarray, Y: np.ndarray, stations: List[Dict[str, float]]) -> np.ndarray:
    power = float(CFG.IDW_POWER)
    eps = float(CFG.IDW_EPS)

    # Inicializar acumuladores
    num = np.zeros_like(X, dtype=float)
    den = np.zeros_like(X, dtype=float)

    for p in stations:
        px = float(p['lon'])
        py = float(p['lat'])
        val = float(p['precip_mm'])
        dx = X - px
        dy = Y - py
        dist2 = dx * dx + dy * dy
        w = 1.0 / (np.power(dist2, power / 2.0) + eps)  # IDW con control eps
        num += w * val
        den += w

    Z = num / np.maximum(den, eps)
    return Z


# ----------------------------
# Graficación
# ----------------------------

def compute_levels(Z: np.ndarray) -> np.ndarray:
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


def figure_size() -> Tuple[float, float]:
    # Si PAPER_SIZE está definido en config y existe en PAPER_SIZES_CM, usarlo
    ps = getattr(CFG, 'PAPER_SIZE', None)
    sizes = getattr(CFG, 'PAPER_SIZES_CM', {})
    if isinstance(ps, str) and ps in sizes:
        w_cm, h_cm = sizes[ps]
        orient = str(CFG.MAP_ORIENTATION).lower()
        # Ajustar orientación de la hoja
        if orient == 'landscape' and h_cm > w_cm:
            w_cm, h_cm = h_cm, w_cm
        if orient == 'portrait' and w_cm > h_cm:
            w_cm, h_cm = h_cm, w_cm
        return float(w_cm / 2.54), float(h_cm / 2.54)
    # Fallback a tamaño manual en cm
    w_cm, h_cm = CFG.MAP_SIZE_CM
    if CFG.MAP_ORIENTATION.lower() == 'portrait':
        return float(h_cm / 2.54), float(w_cm / 2.54)
    return float(w_cm / 2.54), float(h_cm / 2.54)


def plot_isohyets(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, stations: List[Dict[str, float]], extent: Tuple[float, float, float, float]) -> Path:
    ensure_dir(CFG.OUTPUT_DIR)

    levels = compute_levels(Z)

    fig_w, fig_h = figure_size()
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # Colocación del mapa dentro de la hoja:
    # Si MAP_BOX_CM está definido (left_cm, bottom_cm, width_cm, height_cm), se usa ese cuadro exacto.
    # En caso contrario, se aplican los márgenes PAGE_MARGINS_CM.
    fig_w_cm, fig_h_cm = fig_w * 2.54, fig_h * 2.54
    # Anclaje desde esquina inferior-izquierda (preferido) o superior-izquierda
    anchor = str(getattr(CFG, 'MAP_ANCHOR', '')).lower()
    applied_anchor = False
    if anchor in ('bottom-left', 'left-bottom', 'bl'):
        try:
            off_x_cm, off_y_cm = [float(v) for v in getattr(CFG, 'MAP_OFFSET_CM', (1.0, 1.0))]
            W_cm, H_cm = [float(v) for v in getattr(CFG, 'MAP_SIZE_CM', (10.0, 10.0))]
            L_cm = off_x_cm
            B_cm = off_y_cm
            left = max(0.0, min(0.95, L_cm / fig_w_cm))
            bottom = max(0.0, min(0.95, B_cm / fig_h_cm))
            right = min(1.0, (L_cm + W_cm) / fig_w_cm)
            top = min(1.0, (B_cm + H_cm) / fig_h_cm)
            if right <= left:
                right = min(0.999, left + 1e-3)
            if top <= bottom:
                top = min(0.999, bottom + 1e-3)
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
            applied_anchor = True
        except Exception as e:
            logger.warning(f"No se pudo aplicar MAP_ANCHOR bottom-left: {e}")
    elif anchor in ('top-left', 'left-top', 'tl'):
        try:
            # Offsets desde la esquina superior-izquierda
            off_x_cm, off_y_cm = [float(v) for v in getattr(CFG, 'MAP_OFFSET_CM', (1.0, 1.0))]
            # Márgenes declarados (L, R, T, B) pero L y T serán reemplazados por los offsets
            margins = getattr(CFG, 'PAGE_MARGINS_CM', (0.5, 0.5, 0.5, 0.5))
            _, R_cm, _, B_cm_cfg = [float(x) for x in margins]

            L_cm = off_x_cm  # margen izquierdo exacto
            T_cm = off_y_cm  # margen superior exacto
            # Ajustar el tamaño del mapa para respetar los márgenes derecho e inferior
            W_cm = max(0.1, fig_w_cm - L_cm - R_cm)
            H_cm = max(0.1, fig_h_cm - T_cm - B_cm_cfg)

            # Derivar posición inferior a partir del margen superior y la altura
            B_cm = fig_h_cm - T_cm - H_cm

            left = max(0.0, min(0.95, L_cm / fig_w_cm))
            bottom = max(0.0, min(0.95, B_cm / fig_h_cm))
            right = min(1.0, (L_cm + W_cm) / fig_w_cm)
            top = min(1.0, (B_cm + H_cm) / fig_h_cm)
            if right <= left:
                right = min(0.999, left + 1e-3)
            if top <= bottom:
                top = min(0.999, bottom + 1e-3)
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
            applied_anchor = True
        except Exception as e:
            logger.warning(f"No se pudo aplicar MAP_ANCHOR top-left: {e}")
    box = getattr(CFG, 'MAP_BOX_CM', None)
    if not applied_anchor and box is not None:
        L_cm, B_cm, W_cm, H_cm = [float(v) for v in box]
        # Convertir a fracciones del tamaño de la hoja
        left = max(0.0, min(0.95, L_cm / fig_w_cm))
        bottom = max(0.0, min(0.95, B_cm / fig_h_cm))
        right = min(1.0, (L_cm + W_cm) / fig_w_cm)
        top = min(1.0, (B_cm + H_cm) / fig_h_cm)
        # asegurar tamaño mínimo válido sin forzar 5% del ancho/alto
        if right <= left:
            right = min(0.999, left + 1e-3)
        if top <= bottom:
            top = min(0.999, bottom + 1e-3)
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
    elif not applied_anchor:
        margins = getattr(CFG, 'PAGE_MARGINS_CM', (1.5, 1.5, 1.5, 1.5))
        L_cm, R_cm, T_cm, B_cm = [float(x) for x in margins]
        # Aplicar márgenes dobles si corresponde
        if getattr(CFG, 'USE_DOUBLE_MARGINS', False):
            factor = float(getattr(CFG, 'DOUBLE_MARGINS_FACTOR', 2.0))
            sides = set(getattr(CFG, 'DOUBLE_MARGINS_SIDES', ()))
            if 'left' in sides:
                L_cm *= factor
            if 'right' in sides:
                R_cm *= factor
            if 'top' in sides:
                T_cm *= factor
            if 'bottom' in sides:
                B_cm *= factor

        # Si la figura corresponde a una hoja estándar (A3/A4, etc.), usar MAP_SIZE_CM para definir
        # el tamaño del mapa dentro de la hoja, posicionándolo según los márgenes.
        ps = getattr(CFG, 'PAPER_SIZE', None)
        sizes = getattr(CFG, 'PAPER_SIZES_CM', {})
        if isinstance(ps, str) and ps in sizes:
            map_size = getattr(CFG, 'MAP_SIZE_CM', None)
            if isinstance(map_size, (list, tuple)) and len(map_size) == 2:
                W_cm, H_cm = float(map_size[0]), float(map_size[1])
                left = max(0.0, min(0.95, L_cm / fig_w_cm))
                bottom = max(0.0, min(0.95, B_cm / fig_h_cm))
                right = min(1.0, (L_cm + W_cm) / fig_w_cm)
                top = min(1.0, (B_cm + H_cm) / fig_h_cm)
                if right <= left:
                    right = min(0.999, left + 1e-3)
                if top <= bottom:
                    top = min(0.999, bottom + 1e-3)
                fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
            else:
                # Sin MAP_SIZE_CM válido, usar el área por márgenes
                left = max(0.0, min(0.9, (L_cm / 2.54) / fig_w))
                right = max(left + 0.05, min(1.0, 1.0 - (R_cm / 2.54) / fig_w))
                bottom = max(0.0, min(0.9, (B_cm / 2.54) / fig_h))
                top = max(bottom + 0.05, min(1.0, 1.0 - (T_cm / 2.54) / fig_h))
                fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
        else:
            # Hoja personalizada (figura = MAP_SIZE_CM), mantener comportamiento por márgenes
            left = max(0.0, min(0.9, (L_cm / 2.54) / fig_w))
            right = max(left + 0.05, min(1.0, 1.0 - (R_cm / 2.54) / fig_w))
            bottom = max(0.0, min(0.9, (B_cm / 2.54) / fig_h))
            top = max(bottom + 0.05, min(1.0, 1.0 - (T_cm / 2.54) / fig_h))
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)

    # Contornos rellenos
    cf = ax.contourf(X, Y, Z, levels=levels, cmap='Blues')
    # Si se requieren bordes entre bandas en el colorbar, los forzamos via cb.solids.set_edgecolor
    c = ax.contour(X, Y, Z, levels=levels, colors='k', linewidths=0.6, alpha=0.7)
    ax.clabel(c, inline=True, fontsize=8, fmt='%.1f')

    # Estaciones
    ax.scatter([p['lon'] for p in stations], [p['lat'] for p in stations], c='red', edgecolors='white', s=40, zorder=3)
    for p in stations:
        ax.text(p['lon'], p['lat'], p['station_id'], fontsize=8, color='black', ha='left', va='bottom', zorder=4)

    ax.set_xlabel('Longitud (°)')
    ax.set_ylabel('Latitud (°)')
    # Título personalizable desde configuración
    title_fontdict = {}
    fs = getattr(CFG, 'TITLE_FONT_SIZE', None)
    if fs is not None:
        title_fontdict['size'] = fs
    fw = getattr(CFG, 'TITLE_FONT_WEIGHT', None)
    if fw is not None:
        title_fontdict['weight'] = fw
    ff = getattr(CFG, 'TITLE_FONT_FAMILY', None)
    if ff is not None:
        title_fontdict['family'] = ff
    fn = getattr(CFG, 'TITLE_FONT_NAME', None)
    if fn is not None:
        title_fontdict['fontname'] = fn
    title_color = getattr(CFG, 'TITLE_COLOR', 'black')
    title_loc = getattr(CFG, 'TITLE_LOC', 'center')
    title_pad = getattr(CFG, 'TITLE_PAD_PT', None)
    if title_pad is not None:
        ax.set_title(CFG.TITLE, fontdict=title_fontdict, loc=title_loc, color=title_color, pad=title_pad)
    else:
        ax.set_title(CFG.TITLE, fontdict=title_fontdict, loc=title_loc, color=title_color)
    ax.grid(True, ls='--', alpha=0.3)
    ax.set_aspect('equal')

    # Crear colorbar con ancho y padding en cm si está activo
    cb = None
    if getattr(CFG, 'SHOW_COLORBAR', True):
        cb_loc = str(getattr(CFG, 'COLORBAR_LOCATION', 'right')).lower()
        cb_w_cm = float(getattr(CFG, 'COLORBAR_WIDTH_CM', 0.6))
        cb_pad_cm = float(getattr(CFG, 'COLORBAR_PAD_CM', 0.2))
        # convert to fractions
        cb_w = max(1e-3, cb_w_cm / fig_w_cm)
        cb_pad = max(0.0, cb_pad_cm / fig_w_cm)

        # Posición tomando los límites del eje principal (ax) ya ajustado por subplots_adjust
        pos = ax.get_position()
        if cb_loc == 'left':
            cb_rect = [pos.x0 - cb_pad - cb_w, pos.y0, cb_w, pos.height]
        else:
            cb_rect = [pos.x1 + cb_pad, pos.y0, cb_w, pos.height]
        cb_ax = fig.add_axes(cb_rect)
        cb = fig.colorbar(plt.cm.ScalarMappable(), cax=cb_ax, label='Precipitación (mm)')
        # Reusar el mapeo del contourf si existe
        try:
            cb.update_normal(cf)
        except Exception:
            pass
        # Dibujar líneas separadoras para cada rango si está activado
        if getattr(CFG, 'COLORBAR_DRAW_EDGES', False):
            try:
                cb.solids.set_edgecolor(getattr(CFG, 'COLORBAR_EDGE_COLOR', 'black'))
                cb.solids.set_linewidth(getattr(CFG, 'COLORBAR_EDGE_LINEWIDTH_PT', 0.56693))
            except Exception:
                pass

    # Doble margen visible: dibujar rectángulos a 0.5 cm y 0.7 cm del borde de la hoja
    if getattr(CFG, 'DRAW_DOUBLE_MARGINS', False):
        try:
            from matplotlib.patches import Rectangle
            # Primer marco en PAGE_MARGINS_CM, segundo a PAGE_MARGINS_CM + DOUBLE_MARGIN_OFFSET_CM
            L_cm, R_cm, T_cm, B_cm = [float(x) for x in getattr(CFG, 'PAGE_MARGINS_CM', (0.5, 0.5, 0.5, 0.5))]
            off2 = float(getattr(CFG, 'DOUBLE_MARGIN_OFFSET_CM', 0.3))
            color = getattr(CFG, 'DOUBLE_MARGINS_COLOR', 'black')
            lw = float(getattr(CFG, 'DOUBLE_MARGINS_LINEWIDTH', 0.56693))
            alpha = float(getattr(CFG, 'DOUBLE_MARGINS_ALPHA', 1.0))

            def add_frame(l_cm, r_cm, t_cm, b_cm):
                # Coordenadas fraccionarias 0-1 en figura (origen: esquina inferior-izquierda)
                left = max(0.0, min(1.0, l_cm / fig_w_cm))
                bottom = max(0.0, min(1.0, b_cm / fig_h_cm))
                width = max(1e-6, 1.0 - (l_cm + r_cm) / fig_w_cm)
                height = max(1e-6, 1.0 - (t_cm + b_cm) / fig_h_cm)
                rect = Rectangle((left, bottom), width, height,
                                 fill=False, edgecolor=color, linewidth=lw, alpha=alpha,
                                 transform=fig.transFigure, clip_on=False)
                fig.add_artist(rect)

            # Marco 1
            add_frame(L_cm, R_cm, T_cm, B_cm)
            # Marco 2
            add_frame(L_cm + off2, R_cm + off2, T_cm + off2, B_cm + off2)
        except Exception as e:
            logger.warning(f"Advertencia al dibujar doble margen: {e}")

    # Cajas de pie de página (footer)
    if getattr(CFG, 'DRAW_FOOTER_BOXES', False):
        try:
            from matplotlib.patches import Rectangle
            # Si se define un área exacta para el bloque, usarla; en caso contrario, usar márgenes y fila
            area = getattr(CFG, 'FOOTER_BOX_AREA_CM', None)
            if area is not None:
                L_cm, B_cm, W_cm, H_cm = [float(v) for v in area]
                left_margin = L_cm
                right_margin = max(0.0, fig_w_cm - (L_cm + W_cm))
                row_bottom = B_cm
                row_height = H_cm
            else:
                row_bottom = float(getattr(CFG, 'FOOTER_ROW_BOTTOM_CM', 1.0))
                row_height = float(getattr(CFG, 'FOOTER_ROW_HEIGHT_CM', 5.0))
                left_margin = float(getattr(CFG, 'FOOTER_LEFT_MARGIN_CM', 0.5))
                right_margin = float(getattr(CFG, 'FOOTER_RIGHT_MARGIN_CM', 0.5))
                # Si se desea alinear con los offsets del mapa, sobrescribir márgenes izquierdos
                if getattr(CFG, 'FOOTER_ALIGN_WITH_MAP_OFFSETS', False):
                    try:
                        map_left_off = float(getattr(CFG, 'MAP_OFFSET_CM', (0.5, 0.5))[0])
                        left_margin = map_left_off
                    except Exception:
                        pass
            gap_cm = float(getattr(CFG, 'FOOTER_GAP_CM', 0.3))
            n_boxes = int(getattr(CFG, 'FOOTER_BOX_COUNT', 4))
            titles = list(getattr(CFG, 'FOOTER_TITLES', []))
            edge_color = getattr(CFG, 'FOOTER_EDGE_COLOR', 'black')
            edge_lw_pt = float(getattr(CFG, 'FOOTER_EDGE_LINEWIDTH_PT', 0.56693))
            tit_size = float(getattr(CFG, 'FOOTER_TITLE_FONT_SIZE', 10))
            tit_weight = getattr(CFG, 'FOOTER_TITLE_FONT_WEIGHT', 'bold')
            tit_color = getattr(CFG, 'FOOTER_TITLE_COLOR', 'black')
            tit_pad_cm = float(getattr(CFG, 'FOOTER_TITLE_PAD_CM', 0.2))
            # Altura (cm) de la fila superior (título) dentro de cada recuadro del pie de página
            tit_row_h_cm = float(getattr(CFG, 'FOOTER_TITLE_ROW_HEIGHT_CM', 1.0))

            # Calcular anchos por caja
            widths_list = getattr(CFG, 'FOOTER_BOX_WIDTHS_CM', None)
            if widths_list is not None:
                widths_cm = [float(w) for w in widths_list]
                # Si la suma excede el ancho disponible, se escalan proporcionalmente
                content_w_cm = fig_w_cm - left_margin - right_margin
                sum_w = sum(widths_cm)
                if sum_w <= 0:
                    widths_cm = [max(0.1, content_w_cm / n_boxes)] * n_boxes
                elif sum_w > content_w_cm:
                    scale = content_w_cm / sum_w
                    widths_cm = [w * scale for w in widths_cm]
            else:
                # Reparto uniforme
                content_w_cm = fig_w_cm - left_margin - right_margin
                total_gaps_cm = gap_cm * (n_boxes - 1)
                box_w_cm = max(0.1, (content_w_cm - total_gaps_cm) / n_boxes)
                widths_cm = [box_w_cm] * n_boxes

            # Convertir a fracciones
            def cm_to_frac(x_cm, y_cm, w_cm, h_cm):
                return (
                    max(0.0, min(1.0, x_cm / fig_w_cm)),
                    max(0.0, min(1.0, y_cm / fig_h_cm)),
                    max(1e-6, min(1.0, w_cm / fig_w_cm)),
                    max(1e-6, min(1.0, h_cm / fig_h_cm)),
                )

            # Dibujar cajas y títulos
            x_cursor = left_margin
            for i in range(n_boxes):
                w_cm = widths_cm[i] if i < len(widths_cm) else widths_cm[-1]
                x_cm = x_cursor
                y_cm = row_bottom
                h_cm = row_height
                left, bottom, width, height = cm_to_frac(x_cm, y_cm, w_cm, h_cm)
                rect = Rectangle((left, bottom), width, height,
                                 fill=False, edgecolor=edge_color, linewidth=edge_lw_pt,
                                 transform=fig.transFigure, clip_on=False)
                fig.add_artist(rect)

                # Doble borde si está activado
                if getattr(CFG, 'FOOTER_DOUBLE_BORDER', False):
                    try:
                        offset_cm = float(getattr(CFG, 'FOOTER_DOUBLE_BORDER_OFFSET_CM', 0.2))
                        db_color = getattr(CFG, 'FOOTER_DOUBLE_BORDER_COLOR', 'black')
                        db_lw = float(getattr(CFG, 'FOOTER_DOUBLE_BORDER_LINEWIDTH_PT', 0.56693))
                        offset_x = offset_cm / fig_w_cm
                        offset_y = offset_cm / fig_h_cm
                        rect2 = Rectangle((left + offset_x, bottom + offset_y),
                                          width - 2 * offset_x, height - 2 * offset_y,
                                          fill=False, edgecolor=db_color, linewidth=db_lw,
                                          transform=fig.transFigure, clip_on=False)
                        fig.add_artist(rect2)

                        # Línea divisoria para el título, alineada con el recuadro interior
                        sep_y_line = bottom + height - (tit_row_h_cm / fig_h_cm)
                        line_x_start = left + offset_x
                        line_x_end = left + width - offset_x
                        line = Line2D([line_x_start, line_x_end], [sep_y_line, sep_y_line],
                                      transform=fig.transFigure, color=edge_color, linewidth=edge_lw_pt, clip_on=False)
                        fig.add_artist(line)

                    except Exception as e:
                        logger.warning(f"Advertencia al dibujar doble borde/línea de footer: {e}")
                
                sep_y = bottom + height - (tit_row_h_cm / fig_h_cm)
                
                # Título centrado dentro de la fila superior
                if i < len(titles) and titles[i]:
                    title_y = sep_y + (tit_row_h_cm / fig_h_cm) / 2.0
                    # Dibujar recuadro del título (bbox)
                    if getattr(CFG, 'FOOTER_TITLE_BOX', False):
                        bbox_props = dict(
                            boxstyle=f"square,pad={float(getattr(CFG, 'FOOTER_TITLE_BOX_PAD', 0.15))}",
                            facecolor=getattr(CFG, 'FOOTER_TITLE_BOX_FACE_COLOR', 'white'),
                            edgecolor=getattr(CFG, 'FOOTER_TITLE_BOX_EDGE_COLOR', 'black'),
                            linewidth=float(getattr(CFG, 'FOOTER_TITLE_BOX_LINEWIDTH_PT', 0.56693)),
                        )
                    else:
                        bbox_props = None
                    fig.text(left + width/2.0, title_y, titles[i], 
                             ha=getattr(CFG, 'FOOTER_TITLE_HA', 'center'), 
                             va=getattr(CFG, 'FOOTER_TITLE_VA', 'center'),
                             fontsize=tit_size, fontweight=tit_weight, color=tit_color,
                             bbox=bbox_props)

                # --- DIBUJAR LÍNEA DIVISORIA DEL TÍTULO ---
                # Se dibuja aquí para asegurar que siempre aparezca, independientemente de excepciones
                # en bloques posteriores como el de simbología.
                try:
                    line_x_start, line_x_end = left, left + width
                    # Si el doble borde está activo, la línea se alinea con el borde interior
                    if getattr(CFG, 'FOOTER_DOUBLE_BORDER', False):
                        offset_cm = float(getattr(CFG, 'FOOTER_DOUBLE_BORDER_OFFSET_CM', 0.2))
                        offset_x = offset_cm / fig_w_cm
                        line_x_start = left + offset_x
                        line_x_end = left + width - offset_x
                    
                    div_line = Line2D([line_x_start, line_x_end], [sep_y, sep_y],
                                      transform=fig.transFigure, color=edge_color, 
                                      linewidth=edge_lw_pt, clip_on=False)
                    fig.add_artist(div_line)
                except Exception as e:
                    logger.warning(f"Advertencia al dibujar la línea divisoria del footer: {e}")
                # --- FIN LÍNEA DIVISORIA ---

                # Insertar minimapa con Cartopy si corresponde a esta caja
                minimap_idx = getattr(CFG, 'MINIMAP_BOX_INDEX', -1)
                if i == minimap_idx:
                    try:
                        import cartopy.crs as ccrs
                        import cartopy.feature as cfeature
                        from matplotlib.patches import Polygon

                        pad_cm = float(getattr(CFG, 'MINIMAP_PADDING_CM', 0.1))
                        content_h_cm = h_cm - tit_row_h_cm
                        ax_left = (x_cm + pad_cm) / fig_w_cm
                        ax_bottom = (y_cm + pad_cm) / fig_h_cm
                        ax_width = (w_cm - 2 * pad_cm) / fig_w_cm
                        ax_height = (content_h_cm - 2 * pad_cm) / fig_h_cm

                        # Crear un nuevo eje para el minimapa con proyección PlateCarree
                        minimap_ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height], projection=ccrs.PlateCarree())

                        # Añadir características al mapa
                        resolution = getattr(CFG, 'MINIMAP_CARTOPY_RESOLUTION', '110m')
                        logger.info(f"Añadiendo características al minimapa con resolución: {resolution}")

                        land_color = getattr(CFG, 'MINIMAP_LAND_COLOR', '#E0E0E0')
                        ocean_color = getattr(CFG, 'MINIMAP_OCEAN_COLOR', '#FFFFFF')
                        coastline_color = getattr(CFG, 'MINIMAP_COASTLINE_COLOR', 'black')
                        border_color = getattr(CFG, 'MINIMAP_BORDER_COLOR', 'gray')

                        minimap_ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none')
                        minimap_ax.add_feature(cfeature.OCEAN, facecolor=ocean_color, edgecolor='none')
                        minimap_ax.add_feature(cfeature.COASTLINE.with_scale(resolution), edgecolor=coastline_color)
                        minimap_ax.add_feature(cfeature.BORDERS.with_scale(resolution), edgecolor=border_color, linestyle=':')
                        logger.info("Características del minimapa añadidas.")

                        logger.info(f"Extensión del mapa principal para el minimapa: {extent}")

                        # Resaltar la extensión del mapa principal
                        extent_poly = Polygon(
                            [
                                (extent[0], extent[2]),
                                (extent[1], extent[2]),
                                (extent[1], extent[3]),
                                (extent[0], extent[3]),
                            ],
                            closed=True,
                            color=getattr(CFG, 'MINIMAP_EXTENT_COLOR', 'red'),
                            alpha=getattr(CFG, 'MINIMAP_EXTENT_ALPHA', 0.5),
                            transform=ccrs.PlateCarree() # Usar la misma proyección
                        )
                        minimap_ax.add_patch(extent_poly)

                        # Ajustar los límites del minimapa para que se centren en el área de estudio
                        zoom_level = float(getattr(CFG, 'MINIMAP_ZOOM_LEVEL', 2.0))
                        minimap_ax.set_extent([extent[0]-zoom_level, extent[1]+zoom_level, extent[2]-zoom_level, extent[3]+zoom_level], crs=ccrs.PlateCarree())
                        logger.info(f"Límites del minimapa ajustados a: {[extent[0]-zoom_level, extent[1]+zoom_level, extent[2]-zoom_level, extent[3]+zoom_level]}")

                    except ImportError:
                        logger.warning("cartopy no está instalado. No se puede dibujar el minimapa.")
                    except Exception as e:
                        logger.warning(f"Advertencia al insertar minimapa con Cartopy: {e}")

                # Insertar simbología si corresponde a esta caja
                symbology_idx = getattr(CFG, 'SYMBOLOGY_BOX_INDEX', 0)
                if i == symbology_idx:
                    try:
                        from matplotlib.patches import Circle, Rectangle as RectPatch
                        from matplotlib.lines import Line2D
                        
                        pad_cm = float(getattr(CFG, 'SYMBOLOGY_PADDING_CM', 0.3))
                        content_h_cm = h_cm - tit_row_h_cm
                        
                        # Crear un nuevo eje para la simbología
                        ax_left = (x_cm + pad_cm) / fig_w_cm
                        ax_bottom = (y_cm + pad_cm) / fig_h_cm
                        ax_width = (w_cm - 2 * pad_cm) / fig_w_cm
                        ax_height = (content_h_cm - 2 * pad_cm) / fig_h_cm
                        
                        symbology_ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
                        # Hacer el fondo del eje transparente para no tapar la línea del título
                        symbology_ax.patch.set_visible(False)
                        symbology_ax.set_xlim(0, 1)
                        symbology_ax.set_ylim(0, 1)
                        symbology_ax.axis('off')
                        
                        # Configuración de la simbología
                        legend_items = []
                        legend_labels = []
                        
                        # 1. Estaciones (punto rojo con borde blanco)
                        legend_items.append(Line2D([0], [0], marker='o', color='w', 
                                                  markerfacecolor='red', markeredgecolor='white',
                                                  markersize=8, markeredgewidth=1.5))
                        legend_labels.append('Estaciones')
                        
                        # 2. Isoyetas (línea negra)
                        legend_items.append(Line2D([0], [0], color='black', linewidth=1.5, alpha=0.7))
                        legend_labels.append('Isoyetas (mm)')
                        
                        # Agregar la leyenda con los elementos
                        legend = symbology_ax.legend(legend_items, legend_labels,
                                                    loc='center',
                                                    fontsize=9,
                                                    frameon=False,
                                                    facecolor='none')
                        
                        logger.info("Simbología agregada correctamente.")
                        
                    except Exception as e:
                        logger.warning(f"Advertencia al insertar simbología: {e}")

                # --- DIBUJAR LÍNEA DIVISORIA DEL TÍTULO ---
                # Se dibuja aquí para asegurar que siempre aparezca, independientemente de excepciones
                # en bloques posteriores como el de simbología.
                try:
                    line_x_start, line_x_end = left, left + width
                    # Si el doble borde está activo, la línea se alinea con el borde interior
                    if getattr(CFG, 'FOOTER_DOUBLE_BORDER', False):
                        offset_cm = float(getattr(CFG, 'FOOTER_DOUBLE_BORDER_OFFSET_CM', 0.2))
                        offset_x = offset_cm / fig_w_cm
                        line_x_start = left + offset_x
                        line_x_end = left + width - offset_x
                    
                    div_line = Line2D([line_x_start, line_x_end], [sep_y, sep_y],
                                      transform=fig.transFigure, color=edge_color, 
                                      linewidth=edge_lw_pt, clip_on=False)
                    fig.add_artist(div_line)
                except Exception as e:
                    logger.warning(f"Advertencia al dibujar la línea divisoria del footer: {e}")
                # --- FIN LÍNEA DIVISORIA ---

                # Avanzar cursor
                x_cursor += w_cm + gap_cm
        except Exception as e:
            logger.warning(f"Advertencia al dibujar footer boxes: {e}")

            # Convertir a fracciones
            def cm_to_frac(x_cm, y_cm, w_cm, h_cm):
                return (
                    max(0.0, min(1.0, x_cm / fig_w_cm)),
                    max(0.0, min(1.0, y_cm / fig_h_cm)),
                    max(1e-6, min(1.0, w_cm / fig_w_cm)),
                    max(1e-6, min(1.0, h_cm / fig_h_cm)),
                )

            # Dibujar cajas y títulos
            for i in range(n_boxes):
                x_cm = left_margin + i * (box_w_cm + gap_cm)
                y_cm = row_bottom
                w_cm = box_w_cm
                h_cm = row_height
                left, bottom, width, height = cm_to_frac(x_cm, y_cm, w_cm, h_cm)
                rect = Rectangle((left, bottom), width, height,
                                 fill=False, edgecolor=edge_color, linewidth=edge_lw_pt,
                                 transform=fig.transFigure, clip_on=False)
                fig.add_artist(rect)
                sep_y = bottom + height - (tit_row_h_cm / fig_h_cm)
                # Título centrado dentro de la fila superior
                if i < len(titles) and titles[i]:
                    title_y = sep_y + (tit_row_h_cm / fig_h_cm) / 2.0
                    fig.text(left + width/2.0, title_y, titles[i], ha='center', va='center',
                             fontsize=tit_size, fontweight=tit_weight, color=tit_color)
        except Exception as e:
            logger.warning(f"Advertencia al dibujar footer boxes: {e}")

    # Forzar que no se recorten márgenes aunque rcParams tenga savefig.bbox='tight'
    plt.rcParams['savefig.bbox'] = 'standard'
    # Asegurar fondo blanco para que los márgenes sean visibles en PDF
    fig.patch.set_facecolor('white')

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(CFG.OUTPUT_DIR) / f'isoyetas_{ts}.{CFG.IMAGE_FORMAT}'
    fig.savefig(out_path, dpi=CFG.IMAGE_DPI)

    if CFG.POPUP_WINDOW:
        try:
            plt.show()
        except Exception as e:
            logger.warning(f"No se pudo abrir la ventana emergente: {e}")
    else:
        plt.close(fig)

    logger.info(f"Imagen guardada en: {out_path}")
    return out_path


# ----------------------------
# Flujo principal
# ----------------------------

def main() -> None:
    # Obtener estación real desde JSON más reciente en DTA
    real = get_real_station()

    # Generar sintéticas
    syn = generate_synthetic_stations(real)

    # Unir puntos
    stations = [real] + syn

    # Extensión y grilla
    extent = compute_extent(stations)
    X, Y = make_grid(extent, float(CFG.GRID_RESOLUTION_DEG))

    # Interpolación
    Z = idw_interpolate(X, Y, stations)

    # Graficar y guardar
    plot_isohyets(X, Y, Z, stations, extent)


if __name__ == '__main__':
    main()
