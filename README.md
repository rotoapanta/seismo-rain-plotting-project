# Seismo Rain Plotting – Isoyetas, Series Temporales y Barras

Genera mapas de isoyetas (líneas de igual precipitación) a partir de datos de lluvia horarios en JSON, e incluye generación de gráficas de series temporales y de barras integradas en la misma plantilla (marcos, panel lateral y pie de página con minimapa/simbología/escala). Implementa interpolación IDW sobre una grilla configurable, admite fondo cartográfico (Cartopy/tiles), panel lateral, pie de página con minimapa/leyenda, logo, rosa de los vientos y barra de escala.

Puedes ejecutarlo:
- Directamente: `python main.py`
- Vía CLI (Click): `python -m cli.commands run ...`


## Novedades principales
- Gráfica de Series Temporales y Barras
  - Se generan además del mapa de isoyetas, usando la misma hoja/plantilla.
  - Eje X temporal con ticks cada hora y formato HH:MM.
  - Rotación configurable de las etiquetas del eje X (por defecto 90°).
  - Rango temporal mostrado por defecto al día completo:
    - Series temporales: 00:00 – 24:00 del día de los datos (si abarcan varios días, 00:00 del primero a 23:59:59 del último). Puede forzarse con `TIMESERIES_XLIM`.
    - Barras: igual comportamiento, respetando `BARS_XLIM` si está definido.
  - Espaciado físico de ticks en Y (centímetros) configurable; genera locators para aproximar la separación física deseada (lineal).
  - Escalas y límites configurables por componente: lineal/log, y límites X/Y opcionales.
  - Para barras con eje temporal, el ancho de las barras se adapta automáticamente al espaciado de tiempos (control por `BARS_BAR_WIDTH_FRACTION`).
- Manejo de errores sin traceback para “no hay JSON”
  - Cuando no se encuentran JSON en la ruta configurada, se registran mensajes de error claros y el programa termina de forma limpia sin traza de excepción.
- Sincronización de datos con rsync (ejemplo probado)
  - Se documenta un comando rsync para copiar datos desde un Raspberry Pi u otro host vía SSH.


## Características
- Lectura de datos JSON bajo una estructura de carpetas DTA/YYYY/MM/DD.
- Tres modos de selección de entrada: último JSON en el árbol, fecha/hora objetivo, o ruta manual.
- Acumulación opcional: suma de precipitación de todos los JSON encontrados en una carpeta.
- Generación de estaciones sintéticas alrededor de la estación real (jitter espacial y de valor).
- Interpolación IDW configurable (potencia, epsilon) sobre grilla con resolución variable.
- Niveles de isoyetas automáticos o definidos por el usuario.
- Fondo cartográfico con Cartopy (Natural Earth) o tiles (OSM, Stamen) con zoom configurable.
- Composición avanzada: título, márgenes, doble marco, panel lateral (logo/leyenda), pie de página (minimapa/simbología/escala), colorbar.
- Gráficas:
  - Series temporales: eje X por tiempo, ticks cada hora (HH:MM), rotación configurable, rango día completo, Y con separación física configurable, escalas y límites configurables.
  - Barras: soporta eje temporal con ticks por hora, rotación configurable, rango día completo, ancho de barra proporcional al espaciado de tiempo, Y con separación física configurable, escalas y límites configurables.
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
- `main.py` – Flujo principal de generación del mapa (lectura, interpolación, graficación) y la generación de gráficas complementarias (series temporales y barras).
- `config.py` – Parámetros de configuración (entrada, grilla, estilos, composición, etc.).
- `plotting/` – Implementaciones de graficación:
  - `isoyetas.py` – Mapa de isoyetas.
  - `timeseries.py` – Serie temporal con eje horario y rango de día completo.
  - `bars.py` – Barras con eje horario, rango de día completo y ancho automático.
- `ui/` – Plantillas de página (áreas de contenido, paneles laterales, pie de página) y tema.
- `box_config/` – Configuración de cajas/ contenidos (descripción, información, créditos) y renderizadores dinámicos.
- `utils/logger_config.py` – Configuración del logger (archivo + consola).
- `cli/commands.py` – Interfaz de línea de comandos (Click) para ejecutar el pipeline y ver configuración.
- `DTA/` – Datos de entrada (JSON) organizados por año/mes/día.
- `images/` – Recursos gráficos (logo, etc.).
- `output/` – Salidas generadas (`output/isoyetas/...`, `output/timeseries/...`, `output/bars/...`).
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
- `python -m cli.commands run [opciones]` – Ejecuta la generación (equivalente a `python main.py`) con soporte de overrides.

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
  - `python -m cli.commands run --manual-search-path '2025/09/26/RGA' --accumulate`
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


## Salida
- Isoyetas: `output/isoyetas/isoyetas_YYYYmmdd_HHMMSS.<formato>`
- Series: `output/timeseries/timeseries_YYYYmmdd_HHMMSS.<formato>`
- Barras: `output/bars/bars_YYYYmmdd_HHMMSS.<formato>`
- DPI, formato y ubicación controlados por `config.py` o por opciones del CLI.


## Logging (incluye manejo “sin datos” sin traceback)
- Archivo: `logs/seismo_rain_plotting.log` (con rotación automática).
- Consola: mismo formato. Usa `--verbose` para nivel DEBUG en el CLI.
- Si no se encuentran JSON en la ruta/fecha/hora configuradas, se registran mensajes de error claros y el programa termina sin traza de excepción.


## Configuración (config.py)
Parámetros clave editables en `config.py` (todos pueden ajustarse vía CLI cuando hay opción equivalente):

- General/salida: `OUTPUT_DIR`, `IMAGE_FORMAT`, `IMAGE_DPI`, `POPUP_WINDOW`.
- Datos/selección: `DTA_DIR`, `USE_TARGET_DATETIME`, `TARGET_DATE`, `TARGET_HOUR`, `MANUAL_SEARCH_PATH`, `ACCUMULATE_FILES_IN_PATH`.
- Estaciones sintéticas: `SYNTHETIC_STATIONS`, `SYNTH_JITTER_DEG`, `SYNTH_VALUE_JITTER_MM`, `RANDOM_SEED`.
- Interpolación y grilla: `GRID_RESOLUTION_DEG`, `IDW_POWER`, `IDW_EPS`, `ISOHYET_LEVELS`.
- Mapa principal: `EXTENT`, estilos, fondo cartográfico y elementos (minimapa, simbología, rosa/escala) vía `ui/page_template` y `box_config`.

- Series temporales (clave):
  - `OUTPUT_DIR_TIMESERIES`, `TIMESERIES_BOX_CM` / `TIMESERIES_SIZE_CM` + `TIMESERIES_OFFSET_CM`.
  - Etiquetas: `TIMESERIES_X_LABEL`, `TIMESERIES_Y_LABEL`.
  - Estilos: `TIMESERIES_LINE_STYLE`, `TIMESERIES_LINE_COLOR`, `TIMESERIES_LINE_WIDTH`, `TIMESERIES_MARKER`, `TIMESERIES_MARKER_SIZE`.
  - Grid: `TIMESERIES_GRID`, `TIMESERIES_GRID_LINESTYLE`, `TIMESERIES_GRID_ALPHA`, `TIMESERIES_GRID_COLOR`.
  - Eje X horario y formato HH:MM con rotación: `TIMESERIES_XTICK_ROTATION` (por defecto 90).
  - Escalas y límites: `TIMESERIES_YSCALE` ('linear'|'log'), `TIMESERIES_YLIM`, `TIMESERIES_XLIM`.
  - Espaciado físico en Y (cm): `TIMESERIES_YTICK_SPACING_CM` (lineal).

- Barras (clave):
  - `OUTPUT_DIR_BARS`, `BARS_BOX_CM` / `BARS_SIZE_CM` + `BARS_OFFSET_CM`.
  - Etiquetas: `BARS_X_LABEL` (por defecto 'Hora'), `BARS_Y_LABEL` (por defecto 'Precipitación (mm)').
  - Estilos: `BARS_FACE_COLOR`, `BARS_EDGE_COLOR`, `BARS_ALPHA`.
  - Grid: `BARS_GRID`, `BARS_GRID_LINESTYLE`, `BARS_GRID_ALPHA`, `BARS_GRID_COLOR`.
  - Eje X horario y formato HH:MM con rotación: `BARS_XTICK_ROTATION` (por defecto 90).
  - Ancho de barra temporal: `BARS_BAR_WIDTH_FRACTION` (fracción del espaciado mínimo entre timestamps; por defecto 0.8).
  - Escalas y límites: `BARS_YSCALE` ('linear'|'log'), `BARS_YLIM`, `BARS_XLIM`.
  - Espaciado físico en Y (cm): `BARS_YTICK_SPACING_CM` (lineal).

- Paneles laterales y pie: ver `box_config/` y `ui/page_template.py`. Los renderizadores específicos de barras (`bars_description`, `bars_info`) muestran descripción e información (Muestras/Mín/Máx/Promedio) usando el contexto del gráfico.


## Consumo de datos desde OneDrive
Hay varias formas de consumir datos alojados en OneDrive (Linux):

1) Sincronizador OneDrive local (ruta fija)
- Apunta `DTA_DIR` a la ruta sincronizada:
  - `DTA_DIR = '/home/usuario/OneDrive/Mis archivos/Proyecto CEDIA/09_Diseño/datos-seismo-rain/DTA'`
- Configura `MANUAL_SEARCH_PATH` o `USE_TARGET_DATETIME` según necesites.

2) Enlace simbólico (sin cambiar `DTA_DIR`)
- Crear symlink para que `./DTA` apunte a la carpeta DTA de OneDrive:
  - `mv DTA DTA.backup_$(date +%Y%m%d_%H%M%S)`
  - `ln -s "/home/usuario/OneDrive/Mis archivos/Proyecto CEDIA/09_Diseño/datos-seismo-rain/DTA" ./DTA`

3) rclone (copiar o montar)
- Copiar: `rclone copy "onedrive:Mis archivos/Proyecto CEDIA/09_Diseño/datos-seismo-rain/DTA" ./DTA --include "**/*.json"`
- Montar: `rclone mount "onedrive:Mis archivos/Proyecto CEDIA/09_Diseño/datos-seismo-rain" /home/usuario/mnt/onedrive --vfs-cache-mode full &`


## Sincronización de datos vía rsync (probado)
Para copiar JSON desde un host remoto (por ejemplo un Raspberry Pi) hacia el proyecto local conservando estructura y tiempos:

- Crear destino si no existe:
```
mkdir -p /home/rotoapanta/Documentos/Projects/seismo-rain-plotting-project/DTA/2025/10
```

- Copia real (probada):
```
rsync -avz --progress -e ssh \
  pi@192.168.190.29:/home/pi/Documents/Projects/volc-pi-project/DTA/2025/10/ \
  /home/rotoapanta/Documentos/Projects/seismo-rain-plotting-project/DTA/2025/10/
```

- Solo JSON (opcional):
```
rsync -avz --progress \
  --include='*/' --include='*.json' --exclude='*' \
  -e ssh \
  pi@192.168.190.29:/home/pi/Documents/Projects/volc-pi-project/DTA/2025/10/ \
  /home/rotoapanta/Documentos/Projects/seismo-rain-plotting-project/DTA/2025/10/
```

Notas:
- La `/` final en el origen `10/` copia el contenido dentro del destino `.../DTA/2025/10/`.
- Ajusta el puerto en `-e "ssh -p 22"` si no es el 22.
- Usa `-n` (dry-run) para probar: añade `n` a `-avz` y revisa el listado.


## Solución de problemas
- Cartopy no disponible: el script dibujará sin fondo y mostrará una advertencia. Instala Cartopy si deseas fondo.
- Tiles: requieren conexión a Internet; si falla, se usa Natural Earth cuando es posible.
- Sin JSONs: verifica `DTA_DIR` y la ruta/fecha/hora seleccionadas. El programa registra errores y termina sin traceback.
- Valores no finitos en Z: los niveles se ajustan automáticamente; revisa datos de entrada.
- Falta Click: instala con `pip install click` para usar la CLI.


## Desarrollo
- Estilo de código: Python estándar, logging mediante `utils/logger_config.py`.
- La CLI aplica overrides a `config.py` en tiempo de ejecuci��n y llama a `main.main()` (no duplica lógica).
- Para nuevas opciones, añade el parámetro en `config.py` y expón un flag en `cli/commands.py` si corresponde.
