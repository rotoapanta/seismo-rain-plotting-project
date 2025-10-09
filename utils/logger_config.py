import logging
import sys
from logging.handlers import RotatingFileHandler

# =====================================
# CONFIGURACIÓN DEL LOGGER
# =====================================

LOG_FILE = 'logs/seismo_rain_plotting.log'
LOG_LEVEL = logging.INFO

def setup_logger():
    """Configura y retorna un logger para el proyecto."""
    # Crear un logger
    logger = logging.getLogger('SeismoRainPlotting')
    logger.setLevel(LOG_LEVEL)

    # Evitar que los mensajes se propaguen al logger raíz
    logger.propagate = False

    # Si ya tiene handlers, no añadir más
    if logger.hasHandlers():
        return logger

    # Formateador para los mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para escribir en un archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5*1024*1024, backupCount=2, encoding='utf-8'
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Handler para mostrar mensajes en la consola
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOG_LEVEL)
    stream_handler.setFormatter(formatter)

    # Añadir handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

# Crear una instancia global del logger
logger = setup_logger()
