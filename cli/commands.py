import sys
from pathlib import Path
from typing import Optional, Tuple, List

import click

import config as CFG
from utils.logger_config import logger

# Importar el flujo actual para reutilizar la lógica existente
# Nota: Este flujo usa la configuración de config.py, la cual
# será sobreescrita dinámicamente con las opciones CLI.
# from main import main as run_pipeline
from main import main


# ----------------------------
# Helpers para overrides
# ----------------------------

def _set_if_not_none(module, name: str, value):
    if value is not None:
        setattr(module, name, value)


def _bool_to_str(b: bool) -> str:
    return 'True' if b else 'False'


# ----------------------------
# CLI
# ----------------------------

@click.group(help="Herramientas CLI para generar mapas de isoyetas")
def cli():
    pass


@cli.command('run', help='Ejecuta la generación de isoyetas (equivalente a python main.py)')
# Selección/lectura de datos
@click.option('--use-target-datetime/--no-use-target-datetime', default=CFG.USE_TARGET_DATETIME, show_default=True,
              help='Usar fecha/hora objetivo en lugar de buscar el último JSON')
@click.option('--target-date', default=CFG.TARGET_DATE, show_default=True,
              help='Fecha objetivo YYYY-MM-DD (si --use-target-datetime)')
@click.option('--target-hour', type=int, default=CFG.TARGET_HOUR, show_default=True,
              help='Hora objetivo (0-23) (si --use-target-datetime)')
@click.option('--manual-search-path', default=CFG.MANUAL_SEARCH_PATH, show_default=True,
              help='Ruta manual (relativa a DTA_DIR) para buscar JSONs')
@click.option('--accumulate/--no-accumulate', default=CFG.ACCUMULATE_FILES_IN_PATH, show_default=True,
              help='Acumular la precipitación de todos los JSON en la ruta manual')
# Parámetros de estaciones sintéticas e interpolación
@click.option('--synthetic-stations', type=int, default=CFG.SYNTHETIC_STATIONS, show_default=True,
              help='Número de estaciones sintéticas')
@click.option('--seed', 'random_seed', type=int, default=CFG.RANDOM_SEED, show_default=True,
              help='Semilla aleatoria')
@click.option('--grid-res', type=float, default=CFG.GRID_RESOLUTION_DEG, show_default=True,
              help='Resolución de la grilla (grados)')
@click.option('--idw-power', type=float, default=CFG.IDW_POWER, show_default=True,
              help='Parámetro de potencia para IDW')
@click.option('--idw-eps', type=float, default=CFG.IDW_EPS, show_default=True,
              help='Pequeño epsilon para IDW')
# Extensión y niveles
@click.option('--extent', nargs=4, type=float, metavar='LON_MIN LON_MAX LAT_MIN LAT_MAX',
              help='Caja de extensión del mapa (4 números)')
@click.option('--level', 'levels', type=float, multiple=True,
              help='Niveles de isoyetas (puede repetirse: --level 0 --level 10 ...)')
# Salida y formato
@click.option('--output-dir', type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              default=Path(CFG.OUTPUT_DIR), show_default=True, help='Directorio de salida')
@click.option('--image-format', type=click.Choice(['png', 'pdf', 'jpg', 'jpeg', 'svg'], case_sensitive=False),
              default=CFG.IMAGE_FORMAT, show_default=True, help='Formato de imagen')
@click.option('--popup/--no-popup', default=CFG.POPUP_WINDOW, show_default=True,
              help='Mostrar ventana emergente al finalizar')
# Fondo del mapa
@click.option('--map-background/--no-map-background', default=CFG.MAP_BACKGROUND, show_default=True,
              help='Dibujar fondo del mapa (cartopy)')
@click.option('--use-tiles/--no-use-tiles', default=getattr(CFG, 'USE_TILE_BACKGROUND', False), show_default=True,
              help='Usar tiles como fondo (requiere cartopy)')
@click.option('--tile-provider', default=getattr(CFG, 'TILE_PROVIDER', 'OSM'), show_default=True,
              help='Proveedor de tiles (OSM, Stamen-terrain)')
@click.option('--tile-zoom', type=int, default=getattr(CFG, 'TILE_ZOOM_LEVEL', 11), show_default=True,
              help='Nivel de zoom para tiles')
# Logging
@click.option('--verbose', is_flag=True, help='Aumentar verbosidad (INFO -> DEBUG)')
def run_command(use_target_datetime: bool,
                target_date: Optional[str],
                target_hour: Optional[int],
                manual_search_path: Optional[str],
                accumulate: bool,
                synthetic_stations: int,
                random_seed: Optional[int],
                grid_res: float,
                idw_power: float,
                idw_eps: float,
                extent: Optional[Tuple[float, float, float, float]],
                levels: Optional[List[float]],
                output_dir: Path,
                image_format: str,
                popup: bool,
                map_background: bool,
                use_tiles: bool,
                tile_provider: str,
                tile_zoom: int,
                verbose: bool):
    """
    Ejecuta el pipeline de generación de isoyetas aplicando overrides de configuración
    provenientes de la línea de comandos.
    """

    # Verbosidad
    if verbose:
        try:
            import logging
            logger.setLevel(logging.DEBUG)
            for h in logger.handlers:
                h.setLevel(logging.DEBUG)
            logger.debug('Logger ajustado a DEBUG')
        except Exception:
            pass

    # Overrides básicos de adquisición
    _set_if_not_none(CFG, 'USE_TARGET_DATETIME', use_target_datetime)
    _set_if_not_none(CFG, 'TARGET_DATE', target_date)
    _set_if_not_none(CFG, 'TARGET_HOUR', target_hour)
    _set_if_not_none(CFG, 'MANUAL_SEARCH_PATH', manual_search_path)
    _set_if_not_none(CFG, 'ACCUMULATE_FILES_IN_PATH', accumulate)

    # Overrides de procesamiento
    _set_if_not_none(CFG, 'SYNTHETIC_STATIONS', synthetic_stations)
    _set_if_not_none(CFG, 'RANDOM_SEED', random_seed)
    _set_if_not_none(CFG, 'GRID_RESOLUTION_DEG', grid_res)
    _set_if_not_none(CFG, 'IDW_POWER', idw_power)
    _set_if_not_none(CFG, 'IDW_EPS', idw_eps)

    # Overrides de graficación y salida
    _set_if_not_none(CFG, 'OUTPUT_DIR', str(output_dir))
    _set_if_not_none(CFG, 'IMAGE_FORMAT', image_format.lower())
    _set_if_not_none(CFG, 'POPUP_WINDOW', popup)

    _set_if_not_none(CFG, 'MAP_BACKGROUND', map_background)
    _set_if_not_none(CFG, 'USE_TILE_BACKGROUND', use_tiles)
    _set_if_not_none(CFG, 'TILE_PROVIDER', tile_provider)
    _set_if_not_none(CFG, 'TILE_ZOOM_LEVEL', tile_zoom)

    # Extensión/levels
    if extent is not None:
        _set_if_not_none(CFG, 'EXTENT', tuple(map(float, extent)))
    if levels:
        _set_if_not_none(CFG, 'ISOHYET_LEVELS', [float(v) for v in levels])

    # Log de parámetros clave
    logger.info('Parámetros efectivos: ' +
                f" USE_TARGET_DATETIME={_bool_to_str(CFG.USE_TARGET_DATETIME)}" +
                f", TARGET_DATE={CFG.TARGET_DATE}, TARGET_HOUR={CFG.TARGET_HOUR}" +
                f", MANUAL_SEARCH_PATH={CFG.MANUAL_SEARCH_PATH}, ACCUMULATE={_bool_to_str(CFG.ACCUMULATE_FILES_IN_PATH)}" +
                f", GRID_RESOLUTION_DEG={CFG.GRID_RESOLUTION_DEG}, IDW_POWER={CFG.IDW_POWER}, IDW_EPS={CFG.IDW_EPS}" +
                f", SYNTHETIC_STATIONS={CFG.SYNTHETIC_STATIONS}, RANDOM_SEED={CFG.RANDOM_SEED}" +
                f", OUTPUT_DIR={CFG.OUTPUT_DIR}, IMAGE_FORMAT={CFG.IMAGE_FORMAT}, POPUP={_bool_to_str(CFG.POPUP_WINDOW)}" +
                f", MAP_BACKGROUND={_bool_to_str(CFG.MAP_BACKGROUND)}, USE_TILE_BACKGROUND={_bool_to_str(getattr(CFG, 'USE_TILE_BACKGROUND', False))}" +
                f", TILE_PROVIDER={getattr(CFG, 'TILE_PROVIDER', None)}, TILE_ZOOM_LEVEL={getattr(CFG, 'TILE_ZOOM_LEVEL', None)}" +
                (f", EXTENT={CFG.EXTENT}" if getattr(CFG, 'EXTENT', None) is not None else '') +
                (f", ISOHYET_LEVELS={CFG.ISOHYET_LEVELS}" if getattr(CFG, 'ISOHYET_LEVELS', None) is not None else '')
                )

    # Ejecutar pipeline existente
    try:
        main()
    except Exception as e:
        logger.error(f'Error durante la ejecución del pipeline: {e}', exc_info=verbose)
        sys.exit(1)


@cli.command('show-config', help='Imprime los valores actuales de configuración relevantes')
def show_config_command():
    keys = [
        'DTA_DIR', 'USE_TARGET_DATETIME', 'TARGET_DATE', 'TARGET_HOUR', 'MANUAL_SEARCH_PATH', 'ACCUMULATE_FILES_IN_PATH',
        'SYNTHETIC_STATIONS', 'SYNTH_JITTER_DEG', 'SYNTH_VALUE_JITTER_MM', 'RANDOM_SEED',
        'GRID_RESOLUTION_DEG', 'IDW_POWER', 'IDW_EPS', 'ISOHYET_LEVELS',
        'OUTPUT_DIR', 'IMAGE_FORMAT', 'POPUP_WINDOW',
        'EXTENT', 'MAP_BACKGROUND', 'USE_TILE_BACKGROUND', 'TILE_PROVIDER', 'TILE_ZOOM_LEVEL',
        'TITLE', 'PAPER_SIZE', 'MAP_ORIENTATION'
    ]
    for k in keys:
        v = getattr(CFG, k, None)
        logger.info(f'{k}: {v}')


if __name__ == '__main__':
    cli()  # Permite ejecutar: python -m cli.commands run ...
