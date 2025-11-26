-- Activar llaves foráneas en SQLite
PRAGMA foreign_keys = ON;

-- Tabla de ciudades (dimensión)
CREATE TABLE IF NOT EXISTS dim_city (
    city_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name   TEXT NOT NULL,
    country     TEXT NOT NULL,
    lat         REAL NOT NULL,
    lon         REAL NOT NULL,

    UNIQUE(city_name, country)
);

-- Tabla de clima (hechos)
CREATE TABLE IF NOT EXISTS fact_weather (
    weather_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id             INTEGER NOT NULL,
    ts_utc              DATETIME NOT NULL, 
    
    -- Variables principales
    temp                REAL,                
    feels_like          REAL,
    pressure            REAL,
    humidity            REAL,
    wind_speed          REAL,
    wind_deg            REAL,
    clouds              INTEGER,             
    uvi                 REAL,                
    
    weather_main        TEXT,                
    weather_description TEXT,                

    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (city_id) REFERENCES dim_city(city_id)
);

-- Índice para acelerar consultas por ciudad y tiempo
CREATE INDEX IF NOT EXISTS idx_fact_weather_city_ts
    ON fact_weather (city_id, ts_utc);
