from __future__ import annotations

from typing import Iterable, Tuple

import pandas as pd


def raw_to_dim_city_and_fact(raw_responses: Iterable[dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    dim_city_rows = []
    fact_rows = []

    for item in raw_responses:
        city_name = item["city_name"]
        country = item["country"]
        lat = item["lat"]
        lon = item["lon"]
        data = item["data"]

        dim_city_rows.append(
            {
                "city_name": city_name,
                "country": country,
                "lat": lat,
                "lon": lon,
            }
        )

        # Estructura de /data/2.5/weather
        dt = data.get("dt")  # epoch seconds

        main = data.get("main", {}) or {}
        wind = data.get("wind", {}) or {}
        clouds = data.get("clouds", {}) or {}
        weather_list = data.get("weather", []) or []

        if weather_list:
            weather_main = weather_list[0].get("main")
            weather_desc = weather_list[0].get("description")
        else:
            weather_main = None
            weather_desc = None

        fact_rows.append(
            {
                "city_name": city_name,
                "country": country,
                "ts_utc": pd.to_datetime(dt, unit="s", utc=True) if dt is not None else pd.NaT,
                "temp": main.get("temp"),
                "feels_like": main.get("feels_like"),
                "pressure": main.get("pressure"),
                "humidity": main.get("humidity"),
                "wind_speed": wind.get("speed"),
                "wind_deg": wind.get("deg"),
                "clouds": clouds.get("all"),
                "uvi": None,  # este endpoint no trae UVI; lo dejamos nulo
                "weather_main": weather_main,
                "weather_description": weather_desc,
            }
        )

    dim_city_df = pd.DataFrame(dim_city_rows).drop_duplicates(
        subset=["city_name", "country"]
    )

    fact_weather_df = pd.DataFrame(fact_rows)

    return dim_city_df, fact_weather_df
