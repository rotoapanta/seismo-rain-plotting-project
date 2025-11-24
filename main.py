import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional

import numpy as np
import subprocess

import config as CFG
from utils.logger_config import logger
from plotting.isoyetas import render_isoyetas_graph
from plotting.timeseries import render_timeseries_graph
from plotting.bars import render_bars_graph


# ----------------------------
# Utilidades de sincronización (rsync opcional)
# ----------------------------

def rsync_sync() -> None:
    """Ejecuta una sincronización rsync opcional según config (no detiene el flujo si falla)."""
    try:
        if not getattr(CFG, 'RSYNC_ENABLED', False):
            return
        src_base = getattr(CFG, 'RSYNC_SOURCE', None)
        if not src_base:
            logger.warning("RSYNC_ENABLED=True pero RSYNC_SOURCE no está definido en config.py")
            return
        dest_base = getattr(CFG, 'RSYNC_DEST', None) or getattr(CFG, 'DTA_DIR', 'DTA')
        subpath = getattr(CFG, 'RSYNC_SUBPATH', None) or getattr(CFG, 'MANUAL_SEARCH_PATH', None)
        # Construir rutas completas (agregar subruta si corresponde)
        src = src_base.rstrip('/') + '/'
        dest = dest_base.rstrip('/') + '/'
        if subpath:
            sp = str(subpath).strip('/') + '/'
            src += sp
            dest += sp
        # Asegurar destino
        Path(dest).mkdir(parents=True, exist_ok=True)

        # --- Construcción del comando rsync ---
        rsync_cmd = ['rsync', '-avz', '--progress', '--stats']
        
        # --- Manejo de sshpass si se provee una contraseña ---
        rsh_cmd = str(getattr(CFG, 'RSYNC_RSH', 'ssh'))
        password = getattr(CFG, 'RSYNC_PASSWORD', None)

        if password:
            # Verificar si sshpass está instalado antes de usarlo
            if subprocess.run(['which', 'sshpass'], capture_output=True).returncode != 0:
                logger.warning("RSYNC_PASSWORD está definida, pero 'sshpass' no se encuentra en el sistema. Intente instalarlo (ej: sudo apt-get install sshpass) o use autenticación por clave SSH.")
                return

            # Usar sshpass para pasar la contraseña de forma no interactiva
            rsh_cmd = f"sshpass -p \'{password}\' {rsh_cmd}"
        
        rsync_cmd.extend(['-e', rsh_cmd])

        # Modos opcionales
        if getattr(CFG, 'RSYNC_DRY_RUN', False):
            rsync_cmd.append('--dry-run')
        bwlimit = getattr(CFG, 'RSYNC_BWLIMIT', None)
        if bwlimit is not None:
            rsync_cmd.append(f'--bwlimit={int(bwlimit)}')
        if getattr(CFG, 'RSYNC_DELETE', False):
            rsync_cmd.append('--delete')
        if getattr(CFG, 'RSYNC_EXCLUDE_TMP', True):
            rsync_cmd.extend(['--exclude=.*', '--exclude=*.tmp', '--exclude=*.partial', '--exclude=*.swp'])
        if getattr(CFG, 'RSYNC_INCLUDE_JSON_ONLY', True):
            rsync_cmd.extend(["--include=*/", "--include=*.json", "--exclude=*"])
        
        extra = getattr(CFG, 'RSYNC_EXTRA_OPTS', []) or []
        for opt in extra:
            rsync_cmd.append(str(opt))
        
        rsync_cmd.extend([src, dest])
        
        logger.info(f"Iniciando sincronización con rsync...")
        logger.info(f"  - Origen: {src}")
        logger.info(f"  - Destino: {dest}")
        logger.debug(f"  - Comando: {' '.join(rsync_cmd)}")

        try:
            proc = subprocess.run(
                ' '.join(rsync_cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=float(getattr(CFG, 'RSYNC_TIMEOUT_SEC', 180))
            )
        except subprocess.TimeoutExpired as te:
            logger.error(f"Error: rsync excedió el tiempo límite de {CFG.RSYNC_TIMEOUT_SEC}s y fue abortado.")
            return
        out = proc.stdout or ''
        err = proc.stderr or ''
        if proc.returncode == 0:
            # Extraer líneas clave del resumen de rsync
            summary_keys = [
                'Number of files transferred',
                'Total file size',
                'Total transferred file size',
                'sent ',
                'received ',
                'speedup is'
            ]
            lines = [ln for ln in out.splitlines() if any(k in ln for k in summary_keys)]
            if lines:
                logger.info("Resumen de rsync:\n  " + "\n  ".join(lines))
            logger.info("Sincronización rsync completada con éxito.")
        else:
            logger.error(f"Error: rsync finalizó con código {proc.returncode}.")
            if out:
                logger.info(f"Salida de rsync (stdout):\n{out}")
            if err:
                logger.error(f"Errores de rsync (stderr):\n{err}")
    except FileNotFoundError:
        logger.warning("rsync no está disponible en el sistema. Omite sincronización.")
    except Exception as e:
        logger.warning(f"Fallo en sincronización rsync (continuando sin detener): {e}")

# ----------------------------
# Utilidades de IO de datos
# ----------------------------

def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


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
        logger.error(f"No se encontraron archivos JSON en {search_dir}")
        return None

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

        matches = list(search_path.rglob(file_pattern))
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
            logger.error(f"No se pudo encontrar un archivo para la fecha {target_date} y hora {target_hour} en {base}.")
            return None, base
    
    manual_path = getattr(CFG, 'MANUAL_SEARCH_PATH', None)
    if manual_path:
        search_dir = base / manual_path
        logger.info(f"Modo de ruta manual activado. Buscando en: {search_dir}")
        
        if getattr(CFG, 'ACCUMULATE_FILES_IN_PATH', False):
            result = read_and_accumulate_stations(search_dir)
            if result is None:
                return None, search_dir
            return result
        else:
            latest_json = find_latest_json(search_dir)
            if latest_json is None:
                logger.error(f"No se encontró ningún archivo JSON en la ruta manual: {search_dir}")
                return None, search_dir
            return read_real_station_from_json(latest_json)

    logger.info("Buscando el archivo JSON más reciente en todo el directorio DTA.")
    latest_json = find_latest_json(base)
    if latest_json is None:
        logger.error(f"No se encontró ningún archivo JSON en {base} (búsqueda recursiva).")
        return None, base
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
# Graficación: Isoyetas (usa PageTemplate como hoja en blanco)
# ----------------------------



def plot_isohyets(X: np.ndarray, Y: np.ndarray, Z: np.ndarray, stations: List[Dict[str, float]], extent: Tuple[float, float, float, float], **kwargs) -> Path:
    return render_isoyetas_graph(X, Y, Z, stations, extent, source_file=kwargs.get('source_file'))


# ----------------------------
# Utilidades TimeSeries
# ----------------------------

def build_timeseries_from_dir(search_dir: Path):
    """
    Construye (times, values, station_name) a partir de todos los JSON en un directorio.
    - time: se obtiene del nombre del archivo con patrón _YYYYMMDD_HHMM si es posible; si no, mtime.
    - value: suma de 'NIVEL' en 'LECTURAS' por archivo.
    - station: tomado de 'NOMBRE' o 'IDENTIFICADOR' del último archivo válido.
    """
    import re
    times: List[datetime] = []
    values: List[float] = []
    station_name: Optional[str] = None
    json_files = sorted(search_dir.rglob('*.json'))
    for jf in json_files:
        try:
            with jf.open('r', encoding='utf-8') as f:
                data = json.load(f)
            lecturas = data.get('LECTURAS', [])
            if not lecturas:
                continue
            v = sum(float(rd.get('NIVEL', 0.0)) for rd in lecturas)
            # timestamp desde nombre
            m = re.search(r'_(\d{8})_(\d{4})\.json$', jf.name)
            if m:
                dt = datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M')
            else:
                dt = datetime.fromtimestamp(jf.stat().st_mtime)
            times.append(dt)
            values.append(v)
            station_name = str(data.get('NOMBRE') or data.get('IDENTIFICADOR') or station_name or 'STATION')
        except Exception:
            continue
    # Agrupar y sumar valores por timestamp
    from collections import defaultdict
    grouped_values = defaultdict(float)
    for dt, v in zip(times, values):
        grouped_values[dt] += v

    # Ordenar por tiempo
    if grouped_values:
        sorted_items = sorted(grouped_values.items(), key=lambda item: item[0])
        times, values = zip(*sorted_items)
    else:
        times, values = [], []

    return list(times), list(values), station_name or 'STATION'


# ----------------------------
# Pipeline principal
# ----------------------------

def main(**overrides) -> None:
    """Ejecuta el pipeline completo con overrides de configuración opcionales."""
    # Aplicar overrides a config si se proporcionan
    if overrides:
        for k, v in overrides.items():
            if hasattr(CFG, k.upper()):
                setattr(CFG, k.upper(), v)
                logger.info(f"Override aplicado: {k.upper()} = {v}")

    # Sincronización opcional con rsync antes de leer datos
    rsync_sync()

    # Selección/lectura de datos
    real_station, source_file = get_real_station()
    if real_station is None:
        logger.error("No se pudo obtener datos de estaciones. Verifique DTA_DIR/MANUAL_SEARCH_PATH o el acceso a OneDrive.")
        return
    stations = [real_station] + generate_synthetic_stations(real_station)

    # Interpolación
    extent = compute_extent(stations)
    # Asegurar que timeseries use la misma extensión para el mapa de ubicación
    try:
        CFG.TIMESERIES_EXTENT = extent
    except Exception:
        pass
    X, Y = make_grid(extent, float(CFG.GRID_RESOLUTION_DEG))
    Z = idw_interpolate(X, Y, stations)

    # Graficar y guardar (Isoyetas)
    plot_isohyets(X, Y, Z, stations, extent, source_file=source_file)

    # Graficar y guardar (TimeSeries) — usando la carpeta de origen
    try:
        # Determinar carpeta base para los JSON utilizados
        if source_file.is_dir():
            ts_dir = source_file
        else:
            ts_dir = source_file.parent
        times, values, st_name = build_timeseries_from_dir(ts_dir)
        if times and values:
            render_timeseries_graph(
                times, values,
                station=st_name,
                title=getattr(CFG, 'TIMESERIES_TITLE', 'SERIE TEMPORAL'),
                output_dir=Path(getattr(CFG, 'OUTPUT_DIR_TIMESERIES', 'output/timeseries')),
                image_format=getattr(CFG, 'IMAGE_FORMAT', 'pdf'),
                popup=getattr(CFG, 'POPUP_WINDOW', False)
            )
            # Generar gráfico de barras con los mismos valores acumulados
            try:
                render_bars_graph(
                    values,
                    times=times,
                    title=getattr(CFG, 'BARS_TITLE', 'BARRAS'),
                    output_dir=Path(getattr(CFG, 'OUTPUT_DIR_BARS', 'output/bars')),
                    image_format=getattr(CFG, 'IMAGE_FORMAT', 'pdf'),
                    popup=getattr(CFG, 'POPUP_WINDOW', False)
                )
            except Exception as e:
                logger.error(f"No se pudo generar el gráfico de barras: {e}")
        else:
            logger.warning("No se encontraron datos válidos para la serie temporal en el directorio de origen.")
    except Exception as e:
        logger.error(f"No se pudo generar la serie temporal: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Genera mapas de isoyetas a partir de datos de estaciones.")
    
    # Argumentos para la selección de datos
    parser.add_argument('--use-target-datetime', action='store_true', help="Usar fecha/hora objetivo en lugar de buscar el último JSON.")
    parser.add_argument('--target-date', type=str, help="Fecha objetivo en formato YYYY-MM-DD.")
    parser.add_argument('--target-hour', type=int, help="Hora objetivo (0-23)."    )
    parser.add_argument('--manual-search-path', type=str, help="Ruta manual para buscar JSONs, relativa a DTA_DIR.")
    parser.add_argument('--accumulate', action='store_true', help="Acumular precipitación de todos los JSON en la ruta manual.")
    
    # Argumentos para la generación de datos sintéticos
    parser.add_argument('--synthetic-stations', type=int, help="Número de estaciones sintéticas a generar.")
    parser.add_argument('--random-seed', type=int, help="Semilla para la generación de números aleatorios.")
    
    # Argumentos para la interpolación
    parser.add_argument('--grid-resolution', type=float, help="Resolución de la grilla en grados.")
    parser.add_argument('--idw-power', type=float, help="Potencia para la interpolación IDW.")
    parser.add_argument('--idw-eps', type=float, help="Epsilon para la interpolación IDW.")
    
    # Argumentos para la visualización y salida
    parser.add_argument('--extent', type=float, nargs=4, metavar=('LON_MIN', 'LON_MAX', 'LAT_MIN', 'LAT_MAX'), help="Extensión geográfica del mapa.")
    parser.add_argument('--isohyet-levels', type=float, nargs='+', help="Niveles para las isoyetas.")
    parser.add_argument('--output-dir', type=str, help="Directorio de salida para las imágenes generadas.")
    parser.add_argument('--image-format', type=str, choices=['png', 'pdf', 'jpg', 'svg'], help="Formato de la imagen de salida.")
    parser.add_argument('--popup', action='store_true', help="Mostrar la ventana emergente con el gráfico.")
    
    # Argumentos para el fondo del mapa
    parser.add_argument('--map-background', action='store_true', default=True, help="Dibujar un fondo de mapa cartográfico.")
    parser.add_argument('--use-tiles', action='store_true', help="Usar tiles de mapa como fondo.")
    parser.add_argument('--tile-provider', type=str, help="Proveedor de tiles para el fondo del mapa (ej. 'OSM', 'Stamen-terrain').")
    parser.add_argument('--tile-zoom', type=int, help="Nivel de zoom para los tiles del mapa.")

    args = parser.parse_args()

    overrides = {
        'USE_TARGET_DATETIME': args.use_target_datetime,
        'TARGET_DATE': args.target_date,
        'TARGET_HOUR': args.target_hour,
        'MANUAL_SEARCH_PATH': args.manual_search_path,
        'ACCUMULATE_FILES_IN_PATH': args.accumulate,
        'SYNTHETIC_STATIONS': args.synthetic_stations,
        'RANDOM_SEED': args.random_seed,
        'GRID_RESOLUTION_DEG': args.grid_resolution,
        'IDW_POWER': args.idw_power,
        'IDW_EPS': args.idw_eps,
        'EXTENT': args.extent,
        'ISOHYET_LEVELS': args.isohyet_levels,
        'OUTPUT_DIR': args.output_dir,
        'IMAGE_FORMAT': args.image_format,
        'POPUP_WINDOW': args.popup,
        'MAP_BACKGROUND': args.map_background,
        'USE_TILE_BACKGROUND': args.use_tiles,
        'TILE_PROVIDER': args.tile_provider,
        'TILE_ZOOM_LEVEL': args.tile_zoom,
    }

    # Filtrar los overrides que no fueron proporcionados por el usuario (y manejar 'store_true' flags)
    active_overrides = {}
    for k, v in overrides.items():
        if v is not None:
            # Para argumentos que no son flags, cualquier valor es un override activo
            if not isinstance(v, bool) or (isinstance(v, bool) and v):
                 active_overrides[k] = v
            # Para flags, solo consideramos el override si el usuario lo pasó explícitamente
            # (argparse setea a True si está, a False si no está, pero no podemos distinguir
            # si el False es por defecto o intencional. La mejor práctica es que el flag solo active)
            elif k in ['use_target_datetime', 'accumulate', 'popup', 'use_tiles', 'map_background'] and v:
                active_overrides[k] = v

    main(**active_overrides)
