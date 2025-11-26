import os
import json
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path("config")


def load_settings() -> dict:
    settings_path = CONFIG_DIR / "settings.yaml"
    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cities() -> pd.DataFrame:
    cities_path = CONFIG_DIR / "cities.csv"
    return pd.read_csv(cities_path)


def build_weather_url(
    lat: float,
    lon: float,
    api_key: str,
    base_url: str,
    units: str = "metric",
    lang: str = "es",
) -> str:
    return (
        f"{base_url}"
        f"?lat={lat}&lon={lon}"
        f"&units={units}&lang={lang}"
        f"&appid={api_key}"
    )


def fetch_weather_data() -> list[dict]:
    settings = load_settings()
    cities_df = load_cities()

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró WEATHER_API_KEY en el entorno (.env).")

    base_url = settings["api"]["base_url"]
    units = settings["api"].get("units", "metric")
    lang = settings["api"].get("lang", "es")

    etl_cfg = settings.get("etl", {})
    save_raw = etl_cfg.get("save_raw", True)
    raw_path = Path(etl_cfg.get("raw_path", "data/raw"))
    raw_path.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for _, row in cities_df.iterrows():
        city_name = row["city_name"]
        country = row["country"]
        lat = float(row["lat"])
        lon = float(row["lon"])

        url = build_weather_url(
            lat=lat,
            lon=lon,
            api_key=api_key,
            base_url=base_url,
            units=units,
            lang=lang,
        )

        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[WARN] Error al llamar a la API para {city_name} ({lat},{lon}): {e}")
            continue

        if save_raw:
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            filename = f"{city_name}_{country}_{ts}.json".replace(" ", "_")
            filepath = raw_path / filename
            filepath.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        results.append(
            {
                "city_name": city_name,
                "country": country,
                "lat": lat,
                "lon": lon,
                "data": data,
            }
        )

    return results
