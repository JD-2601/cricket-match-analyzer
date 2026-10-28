import json
import sys
import time

import pandas as pd
import requests

OUT = "data/processed/forecasts.json"
URL = "https://api.open-meteo.com/v1/forecast"


def fetch(lat, lon):
    for attempt in range(3):
        try:
            r = requests.get(
                URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                    "forecast_days": 5,
                    "timezone": "auto",
                },
                timeout=15,
            )
        except requests.exceptions.RequestException:
            return None
        if r.status_code == 200:
            return r.json()["daily"]
        if r.status_code != 429:
            break
        time.sleep(5 * (attempt + 1))
    return None

def main():
    venues = pd.read_csv("data/processed/venues.csv").drop_duplicates("city")
    try:
        with open(OUT) as f:
            result = json.load(f)
    except Exception:
        result = {}

    ok = 0
    for _, row in venues.iterrows():
        daily = fetch(float(row.latitude), float(row.longitude))
        if daily:
            keys = list(daily.keys())
            records = [dict(zip(keys, vals)) for vals in zip(*daily.values())]
            for rec in records:
                rec["date"] = rec.pop("time")
            result[row.city.lower()] = {"city": row.city, "forecast": records}
            ok += 1
        time.sleep(1)

    print(f"Updated {ok} of {len(venues)} cities")
    if ok == 0 and not result:
        sys.exit(1)
    with open(OUT, "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()