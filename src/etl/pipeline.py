from src.etl.extract import fetch_weather_data
from src.etl.transform import raw_to_dim_city_and_fact
from src.etl.load import load_dim_city, load_fact_weather
from src.utils.db import get_engine, init_db


def run() -> None:
    engine = get_engine()
    init_db(engine)

    # 1) Extract
    raw_responses = fetch_weather_data()
    if not raw_responses:
        print("[INFO] No se obtuvo ningún dato de la API.")
        return

    # 2) Transform
    dim_city_df, fact_weather_df = raw_to_dim_city_and_fact(raw_responses)

    # 3) Load
    load_dim_city(dim_city_df, engine)
    load_fact_weather(fact_weather_df, engine)

    print("[OK] ETL completado correctamente.")


if __name__ == "__main__":
    run()
