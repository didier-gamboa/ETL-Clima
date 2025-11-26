# ETL-CLIMA 🌤️

## 1. Descripción
Proyecto para la asignatura "Fundamentos de Ingeniería de Datos" que incluye:

- Extracción de datos de clima desde la API **One Call 3.0** de OpenWeatherMap.
- Transformación de las respuestas JSON a tablas relacionales.
- Carga de los datos en una base de datos SQL (SQLite por defecto).
- Visualización de la información en una app sencilla hecha con **Streamlit**.


## 2. Requisitos

- Python 3.10+  
- Conda (Anaconda o Miniconda)  
- Cuenta en [OpenWeatherMap](https://openweathermap.org/) y API key activa para **One Call 3.0**.


## 3. Estructura de carpetas

Estructura mínima del proyecto:

```text
ETL-CLIMA/
├─ app/
│  └─ main.py
├─ config/
│  ├─ cities.csv
│  └─ settings.yaml
├─ data/
│  ├─ raw/
│  └─ processed/
├─ sql/
│  └─ schema.sql
├─ src/
│  ├─ etl/
│  │  ├─ extract.py
│  │  ├─ load.py
│  │  ├─ pipeline.py
│  │  └─ transform.py
│  └─ utils/
│     └─ db.py
├─ .env
└─ requirements.txt
```



## 4. Configuración del entorno con conda

Desde la carpeta raíz del proyecto (`ETL-CLIMA/`):

```bash
# 1) Crear entorno conda
conda create -n etl-clima python=3.11 -y

# 2) Activar entorno
conda activate etl-clima

# 3) Instalar dependencias (vía pip dentro del entorno conda)
pip install -r requirements.txt
```




## 5. Configuración de variables y archivos de configuración

### 5.1 Archivo `.env`

En la raíz del proyecto, crea un archivo `.env` con el siguiente contenido:

```env
# Clave de la API de clima (OpenWeatherMap)
WEATHER_API_KEY=TU_API_KEY_AQUI

# Base de datos: usaremos SQLite en data/weather.db
DB_URL=sqlite:///./data/weather.db
```

> Asegúrate de reemplazar `TU_API_KEY_AQUI` por tu API key real de OpenWeatherMap.



### 5.2 Archivo `config/cities.csv`

Define las ciudades a monitorear (ejemplo):

```csv
city_name,country,lat,lon
Merida,mx,20.97,-89.62
Mexico City,mx,19.43,-99.13
Monterrey,mx,25.67,-100.31
Guadalajara,mx,20.67,-103.35
```

- `city_name`: nombre de la ciudad.
- `country`: código de país (ISO 2 letras).
- `lat`, `lon`: coordenadas aproximadas.



### 5.3 Archivo `config/settings.yaml`

Ejemplo mínimo de configuración:

```yaml
api:
  base_url: "https://api.openweathermap.org/data/3.0/onecall"
  units: "metric"             # 'metric' para °C
  lang: "es"                  # descripciones en español
  exclude: "minutely,alerts"  # reducimos tamaño de la respuesta

etl:
  save_raw: true              # guardar JSON crudos
  raw_path: "data/raw"
  processed_path: "data/processed"
```



### 5.4 Carpetas de datos

Si no existen, créalas:

```bash
mkdir -p data/raw
mkdir -p data/processed
```

En Windows, puedes crear las carpetas manualmente o con:

```bash
mkdir data
aw data\processed
```



## 6. Inicializar base de datos y ejecutar el ETL

El script del pipeline:

- Crea las tablas a partir de `sql/schema.sql` (vía `init_db`).
- Llama a la API de OpenWeatherMap para cada ciudad.
- Genera los DataFrames de `dim_city` y `fact_weather`.
- Inserta/actualiza los datos en la base de datos.

Desde la raíz del proyecto, con el entorno conda activado:

```bash
conda activate etl-clima

# Ejecutar el pipeline ETL
python -m src.etl.pipeline
```

Si todo funciona correctamente, deberías ver un mensaje similar a:

```text
[OK] ETL completado correctamente.
```

Y se creará el archivo `data/weather.db` (base de datos SQLite).



## 7. Ejecutar la aplicación Streamlit

Con el entorno `etl-clima` activado:

```bash
conda activate etl-clima
streamlit run app/main.py
```

Esto abrirá automáticamente el navegador o mostrará una URL como:

```text
http://localhost:8501
```

En la app verás:

- Un **selector de ciudad**.
- Dos **métricas**:
  - Temperatura actual (°C).
  - Humedad actual (%).
- Una **gráfica de línea** con la evolución de temperatura y humedad.
- Un *expander* con la tabla de datos.



## 8. Actualizar los datos

Cada vez que quieras refrescar la información del clima:

1. Ejecuta de nuevo el ETL:

   ```bash
   conda activate etl-clima
   python -m src.etl.pipeline
   ```

2. Regresa a la app de Streamlit y recarga la página (o usa el botón **“Rerun”**).

