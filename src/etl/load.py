# src/etl/load.py
from __future__ import annotations

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import text


def load_dim_city(dim_city_df: pd.DataFrame, engine: Engine) -> None:
    if dim_city_df.empty:
        return

    with engine.begin() as conn:
        existing = pd.read_sql("SELECT city_name, country FROM dim_city", conn)

    merged = dim_city_df.merge(
        existing,
        on=["city_name", "country"],
        how="left",
        indicator=True,
    )

    new_cities = merged[merged["_merge"] == "left_only"][
        ["city_name", "country", "lat", "lon"]
    ]

    if new_cities.empty:
        return

    new_cities.to_sql("dim_city", engine, if_exists="append", index=False)


def load_fact_weather(fact_weather_df: pd.DataFrame, engine: Engine) -> None:
    if fact_weather_df.empty:
        return

    with engine.begin() as conn:
        dim_city_db = pd.read_sql("SELECT city_id, city_name, country FROM dim_city", conn)

    df_merged = fact_weather_df.merge(
        dim_city_db,
        on=["city_name", "country"],
        how="left",
    )

    cols = [
        "city_id",
        "ts_utc",
        "temp",
        "feels_like",
        "pressure",
        "humidity",
        "wind_speed",
        "wind_deg",
        "clouds",
        "uvi",
        "weather_main",
        "weather_description",
    ]

    df_insert = df_merged[cols]

    df_insert.to_sql("fact_weather", engine, if_exists="append", index=False)
