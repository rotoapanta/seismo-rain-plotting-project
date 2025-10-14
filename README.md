# Seismo Rain Plotting – Mapa de Isoyetas

Genera mapas de isoyetas (líneas de igual precipitación) a partir de datos de lluvia horarios en JSON. Implementa interpolación IDW sobre una grilla configurable, admite fondo cartográfico (Cartopy/tiles), panel lateral, pie de página con minimapa/leyenda, logo, rosa de los vientos y barra de escala. Puede ejecutarse:

- Directamente: `python main.py`
- Vía CLI (Click): `python -m cli.commands run ...`


## Características
- Lectura de datos JSON bajo una estructura de carpetas DTA/YYYY/MM/DD.
- Tres modos de selección de entrada: último JSON en el árbol, fecha/hora objetivo, o ruta manual.
- Acumulación opcional: suma de precipitación de todos los JSON encontrados en una carpeta.
- Generación de estaciones sintéticas alrededor de la estación real (jitter espacial y de valor).
- Interpolación IDW configurable (potencia, epsilon) sobre grilla con resolución variable.
- Niveles de isoyetas automáticos o definidos por el usuario.
- Fondo cartográfico con Cartopy (Natural Earth) o tiles (OSM, Stamen) con zoom configurable.
- Composición avanzada: título, márgenes, doble marco, panel lateral (logo/leyenda), pie de página (minimapa/simbología/escala), colorbar.
- Configuración centralizada en `config.py` y sobrescribible desde el CLI.
- Logging a `logs/seismo_rain_plotting.log`.


## Requisitos
- Python 3.8+ recomendado.
- Dependencias principales (ver `requirements.txt`):
  - numpy>=1.21
  - matplotlib>=3.5
  - cartopy>=0.20
- Para el CLI: Click (instalar con `pip install click`).

Nota sobre Cartopy: si no hay rueda binaria disponible para tu plataforma, puede requerir bibliotecas del sistema (PROJ, GEOS). En la mayoría de distribuciones recientes, `pip install cartopy` funciona directamente; de lo contrario, consulta la documentación de Cartopy.


## Instalación rápida
1) (Opcional) Crear y activar un entorno virtual.
2) Instalar dependencias:
   - `pip install -r requirements.txt`
   - Para usar la CLI: `pip install click` (o añade `click>=8.1` a `requirements.txt` y vuelve a instalar)


## Estructura del proyecto (principal)
- `main.py` – Flujo principal de generación del mapa (lectura, interpolación, graficación).
- `config.py` – Parámetros de configuración (entrada, grilla, estilos, composición, etc.).
- `utils/logger_config.py` – Configuración del logger (archivo + consola).
- `cli/commands.py` – Interfaz de línea de comandos (Click) para ejecutar el pipeline y ver configuración.
- `DTA/` – Datos de entrada (JSON) organizados por año/mes/día.
- `images/` – Recursos gráficos (logo, etc.).
- `output/` – Salidas generadas (`output/isoyetas/...`).
- `requirements.txt` – Dependencias del proyecto.
- `setup_environment.sh` – Script auxiliar de entorno (si aplica).


## Formato de datos de entrada (JSON)
- Ubicación por defecto: `DTA/YYYY/MM/DD/...*.json`.
- Campos esperados:
  - Nivel superior: `NOMBRE` o `IDENTIFICADOR` (nombre de estación).
  - `LECTURAS`: lista de lecturas, cada una con:
    - `NIVEL`: valor de precipitación (mm) a acumular.
    - `LATITUD`, `LONGITUD`: coordenadas de la estación.
- El valor total de precipitación se obtiene sumando `NIVEL` en las lecturas del archivo; para modo acumulado se suman todos los archivos de la carpeta objetivo.


## Uso (Usage)

Comandos disponibles del CLI:
- `python -m cli.commands --help` – Ayuda general del CLI.
- `python -m cli.commands show-config` – Imprime los valores actuales de configuración relevantes.
- `python -m cli.commands run [opciones]` – Ejecuta la generación de isoyetas (equivalente a `python main.py`) con soporte de overrides.

Ayuda detallada de cada comando:
- `python -m cli.commands show-config --help`
- `python -m cli.commands run --help`

Ejecución básica:
- Ejecutar con la configuración por defecto (equivale a `python main.py`):
  - `python -m cli.commands run`
- Ver configuración efectiva:
  - `python -m cli.commands show-config`

Ejemplos por comando:
1) show-config
- Mostrar los parámetros relevantes cargados desde `config.py`:
  - `python -m cli.commands show-config`

2) run (con diversas combinaciones de opciones)
- Usar ruta manual y acumular todos los JSON de esa carpeta:
  - `python -m cli.commands run --manual-search-path '2025/09/26' --accumulate`
- Usar fecha/hora específicas (debes activar el modo objetivo):
  - `python -m cli.commands run --use-target-datetime --target-date 2025-09-26 --target-hour 14`
- Fijar extensión y niveles de isoyetas, salida PNG con directorio dedicado:
  - `python -m cli.commands run --extent -78.8 -78.3 -0.6 -0.1 --level 0 --level 10 --level 20 --image-format png --output-dir output/pruebas`
- Fondo con tiles (OSM) y logging en DEBUG:
  - `python -m cli.commands run --map-background --use-tiles --tile-provider OSM --tile-zoom 11 --verbose`
- Ajustar parámetros de interpolación y grilla:
  - `python -m cli.commands run --grid-res 0.005 --idw-power 2.5 --idw-eps 1e-10`
- Controlar estaciones sintéticas y semilla:
  - `python -m cli.commands run --synthetic-stations 5 --seed 1234`
- Mostrar la ventana emergente al finalizar en lugar de solo guardar:
  - `python -m cli.commands run --popup`

Descripción rápida de opciones clave de `run`:
- Entrada de datos:
  - `--use-target-datetime / --no-use-target-datetime` – Activa modo fecha/hora objetivo vs. búsqueda del último JSON.
  - `--target-date YYYY-MM-DD`, `--target-hour 0..23` – Fecha/hora a buscar (solo con `--use-target-datetime`).
  - `--manual-search-path 'YYYY/MM/DD[/subcarpeta]'` – Ruta relativa a `DTA_DIR` (cuando no se usa fecha/hora objetivo).
  - `--accumulate / --no-accumulate` – Sumar todos los JSON de la ruta manual o usar solo el último.
- Procesamiento:
  - `--synthetic-stations N`, `--seed N` – Estaciones sintéticas y reproducibilidad.
  - `--grid-res`, `--idw-power`, `--idw-eps` – Parámetros de grilla e IDW.
- Mapa y salida:
  - `--extent LON_MIN LON_MAX LAT_MIN LAT_MAX` – Caja de extensión fija.
  - `--level VALOR` (repetible) – Niveles de isoyetas manuales.
  - `--output-dir PATH`, `--image-format [png|pdf|jpg|jpeg|svg]`, `--popup`.
  - `--map-background`, `--use-tiles`, `--tile-provider`, `--tile-zoom` – Fondo cartográfico.
  - `--verbose` – Logging a DEBUG.


## Salida
- Archivo: `output/isoyetas/isoyetas_YYYYmmdd_HHMMSS.<formato>`.
- DPI, formato y ubicación controlados por `config.py` o por opciones del CLI.


## Logging
- Archivo: `logs/seismo_rain_plotting.log` (con rotación automática).
- Consola: mismo formato. Usa `--verbose` para nivel DEBUG en el CLI.


## Configuración (config.py)
Parámetros clave editables en `config.py` (todos pueden ajustarse vía CLI cuando hay opción equivalente):
- General/salida: `OUTPUT_DIR`, `IMAGE_FORMAT`, `IMAGE_DPI`, `POPUP_WINDOW`.
- Datos/selección: `DTA_DIR`, `USE_TARGET_DATETIME`, `TARGET_DATE`, `TARGET_HOUR`, `MANUAL_SEARCH_PATH`, `ACCUMULATE_FILES_IN_PATH`.
- Estaciones sintéticas: `SYNTHETIC_STATIONS`, `SYNTH_JITTER_DEG`, `SYNTH_VALUE_JITTER_MM`, `RANDOM_SEED`.
- Interpolación y grilla: `GRID_RESOLUTION_DEG`, `IDW_POWER`, `IDW_EPS`, `ISOHYET_LEVELS`.
- Mapa principal: `PAPER_SIZE`, `MAP_ORIENTATION`, `MAP_SIZE_CM`, `MAP_ANCHOR`, `MAP_OFFSET_CM`, `MAP_BOX_CM`, `EXTENT`, `TITLE` y fuentes/estilos.
- Fondo: `MAP_BACKGROUND`, `USE_TILE_BACKGROUND`, `TILE_PROVIDER`, `TILE_ZOOM_LEVEL`, colores y resolución.
- Colorbar: `SHOW_COLORBAR`, `COLORBAR_LOCATION`, `COLORBAR_WIDTH_CM`, `COLORBAR_PAD_CM`, `COLORBAR_DRAW_EDGES`.
- Panel lateral: switches y estilos; incluye logo (`LOGO_*`).
- Footer: `DRAW_FOOTER_BOXES`, tamaños, `FOOTER_*`, minimapa (`MINIMAP_*`), simbología, rosa de los vientos/escala (`NORTH_ARROW_*`, `SCALE_*`).


## Solución de problemas
- Cartopy no disponible: el script dibujará sin fondo y mostrará una advertencia. Instala Cartopy si deseas fondo.
- Tiles: requieren conexión a Internet; si falla, se usa Natural Earth cuando es posible.
- Sin JSONs: verifica `DTA_DIR` y la ruta/fecha/hora seleccionadas.
- Valores no finitos en Z: los niveles se ajustan automáticamente; revisa datos de entrada.
- Falta Click: instala con `pip install click` para usar la CLI.


## Desarrollo
- Estilo de código: Python estándar, logging mediante `utils/logger_config.py`.
- La CLI aplica overrides a `config.py` en tiempo de ejecución y llama a `main.main()` (no duplica lógica).
- Para nuevas opciones, añade el parámetro en `config.py` y expón un flag en `cli/commands.py` si corresponde.
