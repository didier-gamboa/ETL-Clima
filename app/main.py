import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.db import get_engine
import streamlit as st
import pandas as pd



st.set_page_config(
    page_title="Clima en nuestras ciudades",
    layout="wide",
)

st.title("Clima en nuestras ciudades")


@st.cache_data(ttl=300)
def cargar_datos() -> pd.DataFrame:
    """
    Lee los datos de la base de datos y devuelve un DataFrame con:
    ts_utc, city_name, country, temp, humidity
    """
    engine = get_engine()
    query = """
        SELECT
            w.ts_utc,
            c.city_name,
            c.country,
            w.temp,
            w.humidity
        FROM fact_weather w
        JOIN dim_city c ON w.city_id = c.city_id
        ORDER BY w.ts_utc;
    """
    df = pd.read_sql(query, engine)

    # Asegurarse de que ts_utc es datetime
    if "ts_utc" in df.columns:
        df["ts_utc"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")

    return df


df = cargar_datos()

if df.empty:
    st.info(
        "Aún no hay datos en la base de datos.\n\n"
        "Ejecuta primero el ETL con:\n\n"
        "`python -m src.etl.pipeline`"
    )
else:
    # --- Filtros ---
    ciudades = sorted(df["city_name"].unique())
    ciudad_sel = st.selectbox("Selecciona una ciudad", ciudades)

    df_city = df[df["city_name"] == ciudad_sel].copy()
    df_city = df_city.sort_values("ts_utc").set_index("ts_utc")

    st.subheader(f"Datos recientes para {ciudad_sel}")

    ultimo = df_city.iloc[-1]

    col1, col2 = st.columns(2)
    col1.metric(
        "Temperatura actual (°C)",
        f"{ultimo['temp']:.1f}" if pd.notnull(ultimo['temp']) else "N/D",
    )
    col2.metric(
        "Humedad actual (%)",
        f"{ultimo['humidity']:.0f}" if pd.notnull(ultimo['humidity']) else "N/D",
    )

    st.markdown("---")

    # --- Gráfica de línea ---
    st.line_chart(
        df_city[["temp", "humidity"]],
        use_container_width=True,
    )

    # --- Tabla opcional con datos crudos ---
    with st.expander("Ver datos tabulares"):
        st.dataframe(df_city.reset_index())
