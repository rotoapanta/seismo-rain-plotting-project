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


def read_and_accumulate_stations(search_dir: Path) -> Tuple[Dict[str, float], Path]:
    """Lee y acumula los datos de todos los archivos JSON en un directorio."""
    json_files = list(search_dir.rglob('*.json'))
    if not json_files:
        raise FileNotFoundError(f"No se encontraron archivos JSON en {search_dir}")

    total_precip = 0.0
    last_station_info = {}

    logger.info(f"Acumulando datos de {len(json_files)} archivos en {search_dir}")

    for json_file in sorted(json_files):
        try:
            with json_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            lecturas = data.get('LECTURAS', [])
            if lecturas:
                precip_in_file = sum(float(reading.get('NIVEL', 0.0)) for reading in lecturas)
                total_precip += precip_in_file
                
                logger.info(f"  -> Archivo: {json_file.name}, Precipitación: {precip_in_file:.2f} mm")

                # Guardar la información de la última estación para lat/lon/nombre
                last_reading = lecturas[-1]
                last_station_info['lat'] = float(last_reading.get('LATITUD'))
                last_station_info['lon'] = float(last_reading.get('LONGITUD'))
                last_station_info['station_id'] = str(data.get('NOMBRE') or data.get('IDENTIFICADOR') or 'ACCUMULATED')
            else:
                logger.warning(f"Omitiendo archivo {json_file.name} por no contener lecturas.")
        except Exception as e:
            logger.warning(f"Omitiendo archivo {json_file.name} debido a un error: {e}")
            continue

    if not last_station_info:
        raise ValueError("No se encontraron lecturas válidas en ningún archivo JSON.")

    logger.info(f" -> Suma total de precipitación: {total_precip:.2f} mm")

    accumulated_station = {
        'station_id': last_station_info['station_id'],
        'lat': last_station_info['lat'],
        'lon': last_station_info['lon'],
        'precip_mm': max(0.0, total_precip)
    }
    
    # Usamos el directorio como "archivo" de origen para el log
    return accumulated_station, search_dir

def read_real_station_from_json(json_file: Path) -> Tuple[Dict[str, float], Path]:
    """
    Lee una estación desde un archivo JSON y devuelve los datos y la ruta del archivo.
    """
    with json_file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    lecturas = data.get('LECTURAS', [])
    if not lecturas:
        raise ValueError(f"El JSON {json_file} no contiene 'LECTURAS'.")
    
    precip = sum(float(reading.get('NIVEL', 0.0)) for reading in lecturas)

    last = lecturas[-1]
    lat = float(last.get('LATITUD'))
    lon = float(last.get('LONGITUD'))
    station_id = str(data.get('NOMBRE') or data.get('IDENTIFICADOR') or 'JSON_STATION')
    
    station_data = {
        'station_id': station_id,
        'lat': lat,
        'lon': lon,
        'precip_mm': max(0.0, precip)
    }
    return station_data, json_file


def find_specific_json(base_dir: Path, target_date: str, target_hour: int) -> Optional[Path]:
    """Busca un archivo JSON para una fecha y hora específicas."""
    try:
        dt = datetime.strptime(target_date, '%Y-%m-%d')
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')
        hour_str = f'{target_hour:02d}00'

        # Construir el patrón de búsqueda, ej: *20250926_1400.json
        file_pattern = f'*_{dt.year}{dt.month:02d}{dt.day:02d}_{hour_str}.json'
        
        # Buscar en el subdirectorio correspondiente
        search_path = base_dir / year / month / day
        if not search_path.exists():
            logger.warning(f"El directorio {search_path} no existe.")
            return None

        matches = list(search_path.glob(file_pattern))
        if matches:
            logger.info(f"Archivo encontrado para la fecha y hora especificadas: {matches[0]}")
            return matches[0]
        else:
            logger.warning(f"No se encontró ningún archivo para el patrón {file_pattern} en {search_path}")
            return None
    except Exception as e:
        logger.error(f"Error al buscar el archivo específico: {e}")
        return None

def get_real_station() -> Tuple[Dict[str, float], Path]:
    """Obtiene la estación real y la ruta del archivo de origen según la configuración."""
    base = Path(CFG.DTA_DIR)

    if getattr(CFG, 'USE_TARGET_DATETIME', False):
        logger.info("Modo de fecha/hora objetivo activado.")
        target_date = getattr(CFG, 'TARGET_DATE', '')
        target_hour = getattr(CFG, 'TARGET_HOUR', -1)
        
        if not target_date or not (0 <= target_hour <= 23):
            raise ValueError("TARGET_DATE y TARGET_HOUR deben estar definidos y ser válidos en config.py")

        specific_json = find_specific_json(base, target_date, target_hour)
        if specific_json:
            return read_real_station_from_json(specific_json)
        else:
            raise FileNotFoundError(f"No se pudo encontrar un archivo para la fecha {target_date} y hora {target_hour}.")
    
    manual_path = getattr(CFG, 'MANUAL_SEARCH_PATH', None)
    if manual_path:
        search_dir = base / manual_path
        logger.info(f"Modo de ruta manual activado. Buscando en: {search_dir}")
        
        if getattr(CFG, 'ACCUMULATE_FILES_IN_PATH', False):
            return read_and_accumulate_stations(search_dir)
        else:
            latest_json = find_latest_json(search_dir)
            if latest_json is None:
                raise FileNotFoundError(f"No se encontró ningún archivo JSON en la ruta manual: {search_dir}")
            return read_real_station_from_json(latest_json)

    logger.info("Buscando el archivo JSON más reciente en todo el directorio DTA.")
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
    fig = plt.figure(figsize=(fig_w, fig_h))
    ax = None
    tiles = None

    # Crear la figura y el eje, usando la proyección correcta
    try:
        import cartopy.crs as ccrs
        projection = ccrs.PlateCarree() # Proyección por defecto

        if getattr(CFG, 'MAP_BACKGROUND', False) and getattr(CFG, 'USE_TILE_BACKGROUND', False):
            import cartopy.io.img_tiles as cimgt
            provider_name = getattr(CFG, 'TILE_PROVIDER', 'Stamen-terrain')
            
            if provider_name == 'OSM':
                tiles = cimgt.OSM()
            else: # Default to Stamen-terrain
                tiles = cimgt.Stamen('terrain-background')
            
            projection = tiles.crs
            logger.info(f"Eje creado con proyección para tiles ({provider_name}).")

        if getattr(CFG, 'MAP_BACKGROUND', False):
            ax = fig.add_subplot(1, 1, 1, projection=projection)
        else:
            ax = fig.add_subplot(1, 1, 1)

    except ImportError:
        logger.warning("Cartopy no está instalado. El mapa de fondo no se puede dibujar.")
        ax = fig.add_subplot(1, 1, 1)

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

    # Añadir mapa de fondo si está activado
    if getattr(CFG, 'MAP_BACKGROUND', False) and hasattr(ax, 'coastlines'):
        try:
            ax.set_extent(extent, crs=ccrs.PlateCarree())

            if tiles: # Si se inicializaron los tiles, usarlos
                zoom_level = int(getattr(CFG, 'TILE_ZOOM_LEVEL', 10))
                alpha = float(getattr(CFG, 'TILE_BACKGROUND_ALPHA', 0.7))
                ax.add_image(tiles, zoom_level, zorder=0, interpolation='spline36', alpha=alpha)
                logger.info(f"Agregando mapa de fondo con tiles (zoom={zoom_level}, alpha={alpha})")
            else: # Fallback a Natural Earth
                import cartopy.feature as cfeature
                resolution = getattr(CFG, 'MAP_BACKGROUND_RESOLUTION', '110m')
                land_color = getattr(CFG, 'MAP_BACKGROUND_LAND_COLOR', '#F0F0F0')
                ocean_color = getattr(CFG, 'MAP_BACKGROUND_OCEAN_COLOR', '#D0E7FF')
                coastline_color = getattr(CFG, 'MAP_BACKGROUND_COASTLINE_COLOR', 'black')
                border_color = getattr(CFG, 'MAP_BACKGROUND_BORDER_COLOR', 'gray')

                ax.add_feature(cfeature.LAND, facecolor=land_color, edgecolor='none', zorder=0)
                ax.add_feature(cfeature.OCEAN, facecolor=ocean_color, edgecolor='none', zorder=0.1)
                ax.add_feature(cfeature.BORDERS.with_scale(resolution), edgecolor=border_color, linestyle=':', zorder=3.8)
                ax.add_feature(cfeature.COASTLINE.with_scale(resolution), edgecolor=coastline_color, zorder=4.0)
                logger.info(f"Mapa de fondo (Natural Earth) agregado con resolución: {resolution}")

        except Exception as e:
            logger.warning(f"No se pudo agregar el mapa de fondo: {e}")

    # Contornos rellenos
    cf_alpha = float(getattr(CFG, 'ISOHYET_ALPHA', 0.8))
    cf = ax.contourf(
        X, Y, Z,
        levels=levels,
        cmap='Blues',
        alpha=cf_alpha,
        zorder=1,
        transform=ccrs.PlateCarree() if hasattr(ax, 'coastlines') else ax.transData
    )
    # Si se requieren bordes entre bandas en el colorbar, los forzamos via cb.solids.set_edgecolor
    c = ax.contour(
        X, Y, Z,
        levels=levels,
        colors='k',
        linewidths=0.6,
        alpha=0.9,
        zorder=2,
        transform=ccrs.PlateCarree() if hasattr(ax, 'coastlines') else ax.transData
    )
    ax.clabel(c, inline=True, fontsize=8, fmt='%.1f')

    # Estaciones
    ax.scatter(
        [p['lon'] for p in stations],
        [p['lat'] for p in stations],
        c='red', edgecolors='white', s=40, zorder=5,
        transform=ccrs.PlateCarree() if hasattr(ax, 'coastlines') else ax.transData
    )
    for p in stations:
        ax.text(p['lon'], p['lat'], p['station_id'], fontsize=8, color='black', ha='left', va='bottom', zorder=4,
                transform=ccrs.PlateCarree() if hasattr(ax, 'coastlines') else ax.transData)

    # Añadir etiquetas de coordenadas (gridlines) si Cartopy está activo
    if hasattr(ax, 'gridlines'):
        try:
            import cartopy.crs as ccrs
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlabel_style = {'size': 9}
            gl.ylabel_style = {'size': 9}
            logger.info("Etiquetas de coordenadas añadidas al mapa.")
        except Exception as e:
            logger.warning(f"No se pudieron añadir etiquetas de coordenadas: {e}")
            ax.set_xlabel('Longitud (°)')
            ax.set_ylabel('Latitud (°)')
    else:
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
    if getattr(CFG, 'DRAW_SIDE_BOXES', False):
        try:
            from matplotlib.patches import Rectangle
            right_margin_cm = float(getattr(CFG, 'SIDE_BOX_RIGHT_CM', 1.0))
            box_width_cm = float(getattr(CFG, 'SIDE_BOX_WIDTH_CM', 6.0))
            top_margin_cm = float(getattr(CFG, 'SIDE_BOX_TOP_CM', 1.0))
            bottom_margin_cm = float(getattr(CFG, 'SIDE_BOX_BOTTOM_CM', 1.0))
            gap_cm = float(getattr(CFG, 'SIDE_BOX_GAP_CM', 0.0))
            n_boxes = int(getattr(CFG, 'SIDE_BOX_COUNT', 3))
            titles = list(getattr(CFG, 'SIDE_BOX_TITLES', []))
            edge_color = getattr(CFG, 'SIDE_BOX_EDGE_COLOR', 'black')
            edge_lw_pt = float(getattr(CFG, 'SIDE_BOX_EDGE_LINEWIDTH_PT', 0.56693))
            tit_size = float(getattr(CFG, 'SIDE_BOX_TITLE_FONT_SIZE', 10))
            tit_weight = getattr(CFG, 'SIDE_BOX_TITLE_FONT_WEIGHT', 'bold')
            tit_color = getattr(CFG, 'SIDE_BOX_TITLE_COLOR', 'black')
            tit_row_h_cm = float(getattr(CFG, 'SIDE_BOX_TITLE_ROW_HEIGHT_CM', 1.0))

            heights_list = getattr(CFG, 'SIDE_BOX_HEIGHTS_CM', None)
            if heights_list is not None:
                heights_cm = [float(h) for h in heights_list]
                content_h_cm = fig_h_cm - top_margin_cm - bottom_margin_cm
                sum_h = sum(heights_cm)
                if sum_h <= 0:
                    heights_cm = [max(0.1, content_h_cm / n_boxes)] * n_boxes
                elif sum_h > content_h_cm:
                    scale = content_h_cm / sum_h
                    heights_cm = [h * scale for h in heights_cm]
            else:
                content_h_cm = fig_h_cm - top_margin_cm - bottom_margin_cm
                total_gaps_cm = gap_cm * (n_boxes - 1)
                box_h_cm = max(0.1, (content_h_cm - total_gaps_cm) / n_boxes)
                heights_cm = [box_h_cm] * n_boxes

            def cm_to_frac(x_cm, y_cm, w_cm, h_cm):
                return (
                    max(0.0, min(1.0, x_cm / fig_w_cm)),
                    max(0.0, min(1.0, y_cm / fig_h_cm)),
                    max(1e-6, min(1.0, w_cm / fig_w_cm)),
                    max(1e-6, min(1.0, h_cm / fig_h_cm)),
                )

            y_cursor = fig_h_cm - top_margin_cm
            for i in range(n_boxes):
                h_cm = heights_cm[i] if i < len(heights_cm) else heights_cm[-1]
                x_cm = fig_w_cm - right_margin_cm - box_width_cm
                y_cm = y_cursor - h_cm
                
                left, bottom, width, height = cm_to_frac(x_cm, y_cm, box_width_cm, h_cm)
                rect = Rectangle((left, bottom), width, height, fill=False, edgecolor=edge_color, linewidth=edge_lw_pt, transform=fig.transFigure, clip_on=False)
                fig.add_artist(rect)

                if getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER', False):
                    offset_cm = float(getattr(CFG, 'SIDE_BOX_DOUBLE_BORDER_OFFSET_CM', 0.1))
                    offset_x = offset_cm / fig_w_cm
                    offset_y = offset_cm / fig_h_cm
                    rect2 = Rectangle((left + offset_x, bottom + offset_y), width - 2 * offset_x, height - 2 * offset_y, fill=False, edgecolor=edge_color, linewidth=edge_lw_pt, transform=fig.transFigure, clip_on=False)
                    fig.add_artist(rect2)

                if i < len(titles) and titles[i]:
                    title_y = bottom + height - (tit_row_h_cm / fig_h_cm) / 2.0
                    fig.text(left + width / 2.0, title_y, titles[i], ha='center', va='center', fontsize=tit_size, fontweight=tit_weight, color=tit_color)

                # Insertar imagen del logo si corresponde
                logo_idx = getattr(CFG, 'LOGO_BOX_INDEX', getattr(CFG, 'SIDE_BOX_IMAGE_INDEX', -1))
                if i == logo_idx:
                    try:
                        import matplotlib.image as mpimg
                        logo_path = getattr(CFG, 'LOGO_IMAGE_PATH', getattr(CFG, 'SIDE_BOX_IMAGE_PATH', 'images/logo-ig.png'))
                        if Path(logo_path).exists():
                            logo_img = mpimg.imread(logo_path)

                            # Tamaño configurable (opcional) en cm
                            img_w_cm = getattr(CFG, 'LOGO_WIDTH_CM', None)
                            if img_w_cm is None:
                                img_w_cm = getattr(CFG, 'SIDE_BOX_IMAGE_WIDTH_CM', None)
                            img_h_cm = getattr(CFG, 'LOGO_HEIGHT_CM', None)
                            if img_h_cm is None:
                                img_h_cm = getattr(CFG, 'SIDE_BOX_IMAGE_HEIGHT_CM', None)

                            resize_to_fit = bool(getattr(CFG, 'LOGO_RESIZE_TO_FIT', True))

                            if resize_to_fit:
                                # Margen configurable (opcional) en cm. Si no se define, usar margen fraccional por defecto
                                margin_cm = getattr(CFG, 'LOGO_MARGIN_CM', None)
                                if margin_cm is None:
                                    margin_cm = getattr(CFG, 'SIDE_BOX_IMAGE_MARGIN_CM', None)
                                if margin_cm is not None:
                                    margin_x = float(margin_cm) / fig_w_cm
                                    margin_y = float(margin_cm) / fig_h_cm
                                else:
                                    margin_x = margin_y = 0.05  # fracción de la figura

                                # Área disponible dentro de la caja (fracciones de la figura)
                                avail_left = left + margin_x
                                avail_bottom = bottom + margin_y
                                avail_width = max(1e-6, width - 2 * margin_x)
                                avail_height = max(1e-6, height - 2 * margin_y)

                                # Si no se especifican tamaños, llenar el área disponible
                                if img_w_cm is None and img_h_cm is None:
                                    logo_rect = [avail_left, avail_bottom, avail_width, avail_height]
                                else:
                                    # Mantener proporción si solo se provee un lado
                                    try:
                                        img_h_px, img_w_px = logo_img.shape[0], logo_img.shape[1]
                                        aspect = img_h_px / max(1, img_w_px)
                                    except Exception:
                                        aspect = 1.0

                                    if img_w_cm is not None and img_h_cm is None:
                                        img_h_cm = float(img_w_cm) * aspect
                                    if img_h_cm is not None and img_w_cm is None:
                                        img_w_cm = float(img_h_cm) / max(1e-9, aspect)

                                    # Convertir a fracciones de la figura
                                    logo_w = float(img_w_cm) / fig_w_cm
                                    logo_h = float(img_h_cm) / fig_h_cm

                                    # Escalar si excede el área disponible (preservar aspecto)
                                    scale = min(avail_width / logo_w, avail_height / logo_h, 1.0)
                                    logo_w *= scale
                                    logo_h *= scale

                                    # Centrar dentro de la zona disponible
                                    logo_left = avail_left + (avail_width - logo_w) / 2.0
                                    logo_bottom = avail_bottom + (avail_height - logo_h) / 2.0
                                    logo_rect = [logo_left, logo_bottom, logo_w, logo_h]

                                logo_ax = fig.add_axes(logo_rect)
                                im = logo_ax.imshow(logo_img)
                                logo_ax.axis('off')
                            else:
                                # Modo tamaño fijo: colocar el logo con dimensiones exactas en cm (independiente de la caja)
                                # Calcular proporción si solo se provee un lado
                                try:
                                    img_h_px, img_w_px = logo_img.shape[0], logo_img.shape[1]
                                    aspect = img_h_px / max(1, img_w_px)
                                except Exception:
                                    aspect = 1.0

                                if img_w_cm is not None and img_h_cm is None:
                                    img_h_cm = float(img_w_cm) * aspect
                                if img_h_cm is not None and img_w_cm is None:
                                    img_w_cm = float(img_h_cm) / max(1e-9, aspect)

                                # Si ambos son None, por compatibilidad, llenar el área disponible
                                if img_w_cm is None and img_h_cm is None:
                                    logo_rect = [left, bottom, width, height]
                                else:
                                    logo_w = float(img_w_cm) / fig_w_cm
                                    logo_h = float(img_h_cm) / fig_h_cm

                                    # Posicionamiento dentro de la caja según ancla y offset
                                    anchor = str(getattr(CFG, 'LOGO_ANCHOR', 'center')).lower()
                                    off_x_cm, off_y_cm = [float(v) for v in getattr(CFG, 'LOGO_OFFSET_CM', (0.0, 0.0))]
                                    off_x = off_x_cm / fig_w_cm
                                    off_y = off_y_cm / fig_h_cm

                                    if anchor in ('top-left', 'left-top', 'tl'):
                                        logo_left = left + off_x
                                        logo_bottom = bottom + height - logo_h - off_y
                                    elif anchor in ('top-right', 'right-top', 'tr'):
                                        logo_left = left + width - logo_w - off_x
                                        logo_bottom = bottom + height - logo_h - off_y
                                    elif anchor in ('bottom-left', 'left-bottom', 'bl'):
                                        logo_left = left + off_x
                                        logo_bottom = bottom + off_y
                                    elif anchor in ('bottom-right', 'right-bottom', 'br'):
                                        logo_left = left + width - logo_w - off_x
                                        logo_bottom = bottom + off_y
                                    else:  # center
                                        logo_left = left + (width - logo_w) / 2.0
                                        logo_bottom = bottom + (height - logo_h) / 2.0

                                    logo_rect = [logo_left, logo_bottom, logo_w, logo_h]

                                logo_ax = fig.add_axes(logo_rect)
                                im = logo_ax.imshow(logo_img)
                                logo_ax.axis('off')

                                # Opción de recortar el logo a los límites de la caja
                                if bool(getattr(CFG, 'LOGO_CLIP_TO_BOX', True)):
                                    from matplotlib.patches import Rectangle as RectClip
                                    clip_rect = RectClip((left, bottom), width, height, transform=fig.transFigure)
                                    im.set_clip_path(clip_rect)

                            logger.info(f"Logo insertado desde: {logo_path}")
                        else:
                            logger.warning(f"No se encontró la imagen del logo: {logo_path}")
                    except Exception as e:
                        logger.warning(f"Advertencia al insertar el logo: {e}")

                y_cursor -= (h_cm + gap_cm)
        except Exception as e:
            logger.warning(f"Advertencia al dibujar cajas laterales: {e}")

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
                        # Line2D ya importado a nivel de módulo
                        
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

                # Insertar rosa de los vientos y escala si corresponde a esta caja
                north_arrow_scale_idx = getattr(CFG, 'NORTH_ARROW_SCALE_BOX_INDEX', -1)
                if i == north_arrow_scale_idx:
                    try:
                        pad_cm = float(getattr(CFG, 'NORTH_ARROW_SCALE_PADDING_CM', 0.3))
                        content_h_cm = h_cm - tit_row_h_cm
                        
                        ax_left = (x_cm + pad_cm) / fig_w_cm
                        ax_bottom = (y_cm + pad_cm) / fig_h_cm
                        ax_width = (w_cm - 2 * pad_cm) / fig_w_cm
                        ax_height = (content_h_cm - 2 * pad_cm) / fig_h_cm
                        
                        ns_ax = fig.add_axes([ax_left, ax_bottom, ax_width, ax_height])
                        ns_ax.patch.set_visible(False)
                        ns_ax.set_xlim(0, 1)
                        ns_ax.set_ylim(0, 1)
                        ns_ax.axis('off')

                        draw_north_arrow(ns_ax)
                        
                        scale_bar_style = getattr(CFG, 'SCALE_BAR_STYLE', 'simple')
                        if scale_bar_style == 'segmented':
                            draw_segmented_scale_bar(ns_ax, extent)
                        else:
                            draw_simple_scale_bar(ns_ax, extent)

                    except Exception as e:
                        logger.warning(f"Advertencia al insertar rosa de los vientos y escala: {e}")

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
    # Obtener estación real y la ruta del archivo de origen
    real, source_file = get_real_station()
    logger.warning(f"--- INICIANDO PROCESO CON DATOS DE: {source_file.name} ---")

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


def draw_simple_scale_bar(ax, extent):
    scale_length_km = float(getattr(CFG, 'SCALE_LENGTH_KM', 10))
    scale_length_deg = scale_length_km / 111.0
    map_width_deg = extent[1] - extent[0]
    scale_bar_width = scale_length_deg / map_width_deg * 0.6
    scale_bar_width = min(scale_bar_width, 0.6)

    scale_y = float(getattr(CFG, 'SCALE_VERTICAL_POSITION', 0.25))
    scale_x_start = 0.5 - scale_bar_width / 2
    scale_x_end = 0.5 + scale_bar_width / 2

    bar_color = getattr(CFG, 'SCALE_BAR_COLOR', 'black')
    bar_lw = float(getattr(CFG, 'SCALE_BAR_LINEWIDTH_PT', 2.0))

    ax.plot([scale_x_start, scale_x_end], [scale_y, scale_y], color=bar_color, linewidth=bar_lw, solid_capstyle='butt')
    ax.plot([scale_x_start, scale_x_start], [scale_y - 0.02, scale_y + 0.02], color=bar_color, linewidth=bar_lw)
    ax.plot([scale_x_end, scale_x_end], [scale_y - 0.02, scale_y + 0.02], color=bar_color, linewidth=bar_lw)

    text_color = getattr(CFG, 'SCALE_TEXT_COLOR', 'black')
    text_size = float(getattr(CFG, 'SCALE_TEXT_FONT_SIZE', 9))
    text_weight = getattr(CFG, 'SCALE_TEXT_FONT_WEIGHT', 'bold')
    ax.text(0.5, scale_y - 0.08, f'{scale_length_km} km', ha='center', va='top', fontsize=text_size, fontweight=text_weight, color=text_color)

    logger.info(f"Escala del mapa simple agregada: {scale_length_km} km")

def draw_segmented_scale_bar(ax, extent):
    from matplotlib.patches import Rectangle

    segments_km = getattr(CFG, 'SCALE_BAR_SEGMENTS_KM', [0, 5, 10, 20, 30])
    total_length_km = segments_km[-1]
    map_width_deg = extent[1] - extent[0]
    total_length_deg = total_length_km / 111.0
    scale_bar_width = total_length_deg / map_width_deg * 0.8
    scale_bar_width = min(scale_bar_width, 0.8)

    bar_height_pt = float(getattr(CFG, 'SCALE_BAR_HEIGHT_PT', 5))
    colors = getattr(CFG, 'SCALE_SEGMENT_COLORS', ['black', 'white'])
    text_color = getattr(CFG, 'SCALE_TEXT_COLOR', 'black')
    text_size = float(getattr(CFG, 'SCALE_TEXT_FONT_SIZE', 9))
    units_label = getattr(CFG, 'SCALE_SEGMENTED_UNITS_LABEL', 'Kilometers')

    y_pos = float(getattr(CFG, 'SCALE_BAR_Y_POS', 0.2))
    x_start = 0.1

    for i in range(len(segments_km) - 1):
        start_km = segments_km[i]
        end_km = segments_km[i+1]
        
        start_frac = start_km / total_length_km
        end_frac = end_km / total_length_km
        
        rect_x = x_start + start_frac * scale_bar_width
        rect_width = (end_frac - start_frac) * scale_bar_width
        
        color = colors[i % len(colors)]
        
        rect = Rectangle((rect_x, y_pos), rect_width, bar_height_pt / 72.0, 
                         facecolor=color, edgecolor='black', linewidth=0.5, transform=ax.transAxes)
        ax.add_patch(rect)

    for km in segments_km:
        frac = km / total_length_km
        x_pos = x_start + frac * scale_bar_width
        ax.text(x_pos, y_pos + bar_height_pt / 72.0 + 0.02, str(km), 
                ha='center', va='bottom', fontsize=text_size, color=text_color, transform=ax.transAxes)

    ax.text(x_start + scale_bar_width + 0.02, y_pos + bar_height_pt / 144.0, units_label, 
            ha='left', va='center', fontsize=text_size, color=text_color, transform=ax.transAxes)

    logger.info(f"Escala del mapa segmentada agregada: {total_length_km} km")


def draw_north_arrow(ax):
    style = getattr(CFG, 'NORTH_ARROW_STYLE', 'drawn')

    if style == 'image':
        import matplotlib.image as mpimg
        image_path = getattr(CFG, 'NORTH_ARROW_IMAGE_PATH', 'images/image.png')
        if Path(image_path).exists():
            img = mpimg.imread(image_path)
            img_w_cm = getattr(CFG, 'NORTH_ARROW_IMAGE_WIDTH_CM', None)
            img_h_cm = getattr(CFG, 'NORTH_ARROW_IMAGE_HEIGHT_CM', None)

            if img_w_cm and img_h_cm:
                # Usar tamaño personalizado
                width = img_w_cm / ax.figure.get_figwidth() * 2.54
                height = img_h_cm / ax.figure.get_figheight() * 2.54
                y_pos = float(getattr(CFG, 'NORTH_ARROW_Y_POS', 0.65))
                ax.imshow(img, extent=[0.5 - width/2, 0.5 + width/2, y_pos - height/2, y_pos + height/2], aspect='auto')
            else:
                # Usar tamaño relativo
                y_pos = float(getattr(CFG, 'NORTH_ARROW_Y_POS', 0.65))
                size = float(getattr(CFG, 'NORTH_ARROW_SIZE', 0.25))
                ax.imshow(img, extent=[0.5 - size/2, 0.5 + size/2, y_pos - size/2, y_pos + size/2], aspect='equal')
            
            logger.info(f"Rosa de los vientos (imagen) agregada desde: {image_path}")
        else:
            logger.warning(f"No se encontró la imagen de la rosa de los vientos: {image_path}")
    else:
        from matplotlib.patches import Polygon

        y_pos = float(getattr(CFG, 'NORTH_ARROW_Y_POS', 0.65))
        size = float(getattr(CFG, 'NORTH_ARROW_SIZE', 0.25))
        color1 = getattr(CFG, 'NORTH_ARROW_COLOR1', 'black')
        color2 = getattr(CFG, 'NORTH_ARROW_COLOR2', 'white')
        edge_color = getattr(CFG, 'NORTH_ARROW_EDGE_COLOR', 'black')
        text_color = getattr(CFG, 'NORTH_ARROW_TEXT_COLOR', 'black')
        font_size = float(getattr(CFG, 'NORTH_ARROW_FONT_SIZE', 10))
        font_weight = getattr(CFG, 'NORTH_ARROW_FONT_WEIGHT', 'bold')

        center_x = 0.5
        
        # Triángulos
        # Norte
        ax.add_patch(Polygon([[center_x, y_pos + size], [center_x - size/4, y_pos], [center_x, y_pos - size/4]], closed=True, facecolor=color1, edgecolor=edge_color))
        ax.add_patch(Polygon([[center_x, y_pos + size], [center_x + size/4, y_pos], [center_x, y_pos - size/4]], closed=True, facecolor=color2, edgecolor=edge_color))
        # Sur
        ax.add_patch(Polygon([[center_x, y_pos - size], [center_x - size/4, y_pos], [center_x, y_pos + size/4]], closed=True, facecolor=color2, edgecolor=edge_color))
        ax.add_patch(Polygon([[center_x, y_pos - size], [center_x + size/4, y_pos], [center_x, y_pos + size/4]], closed=True, facecolor=color1, edgecolor=edge_color))
        # Este
        ax.add_patch(Polygon([[center_x + size, y_pos], [center_x, y_pos + size/4], [center_x - size/4, y_pos]], closed=True, facecolor=color1, edgecolor=edge_color))
        ax.add_patch(Polygon([[center_x + size, y_pos], [center_x, y_pos - size/4], [center_x - size/4, y_pos]], closed=True, facecolor=color2, edgecolor=edge_color))
        # Oeste
        ax.add_patch(Polygon([[center_x - size, y_pos], [center_x, y_pos + size/4], [center_x + size/4, y_pos]], closed=True, facecolor=color2, edgecolor=edge_color))
        ax.add_patch(Polygon([[center_x - size, y_pos], [center_x, y_pos - size/4], [center_x + size/4, y_pos]], closed=True, facecolor=color1, edgecolor=edge_color))

        # Texto
        ax.text(center_x, y_pos + size * 1.1, 'N', ha='center', va='bottom', fontsize=font_size, fontweight=font_weight, color=text_color)
        ax.text(center_x, y_pos - size * 1.1, 'S', ha='center', va='top', fontsize=font_size, fontweight=font_weight, color=text_color)
        ax.text(center_x + size * 1.1, y_pos, 'E', ha='left', va='center', fontsize=font_size, fontweight=font_weight, color=text_color)
        ax.text(center_x - size * 1.1, y_pos, 'W', ha='right', va='center', fontsize=font_size, fontweight=font_weight, color=text_color)

        logger.info("Rosa de los vientos (dibujada) agregada.")

if __name__ == '__main__':
    main()
