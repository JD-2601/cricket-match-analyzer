import os
import time

import pandas as pd
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY = "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
OUT_PATH = "data/processed/weather.csv"


def fetch_weather(lat, lon, start, end):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": DAILY,
        "timezone": "auto",
    }
    for attempt in range(4):
        r = requests.get(ARCHIVE_URL, params=params, timeout=60)
        if r.status_code == 200:
            return pd.DataFrame(r.json()["daily"])
        print("  status", r.status_code, "- waiting")
        time.sleep(30 * (attempt + 1))
    r.raise_for_status()


def season_windows(dates):
    d = pd.to_datetime(pd.Series(dates)).sort_values()
    out = []
    for _, g in d.groupby(d.dt.year):
        out.append((g.min().strftime("%Y-%m-%d"), g.max().strftime("%Y-%m-%d")))
    return out


def build_weather(matches_path, venues_path):
    m = pd.read_csv(matches_path)
    venues = pd.read_csv(venues_path)

    done = set()
    if os.path.exists(OUT_PATH):
        old = pd.read_csv(OUT_PATH)
        done = set(zip(old.venue, old.city))
    else:
        columns = ["date", "temperature_2m_max", "temperature_2m_min",
                   "precipitation_sum", "wind_speed_10m_max", "venue", "city"]
        pd.DataFrame(columns=columns).to_csv(OUT_PATH, index=False)

    for _, v in venues.iterrows():
        key = (v["venue"], v["city"])
        if key in done:
            print("skip", key)
            continue
        games = m[(m.venue == v["venue"]) & (m.city == v["city"])]
        for start, end in season_windows(games.start_date):
            print("fetching", v["venue"], v["city"], start, end)
            w = fetch_weather(v["latitude"], v["longitude"], start, end)
            w = w.rename(columns={"time": "date"})
            w["venue"] = v["venue"]
            w["city"] = v["city"]
            w.to_csv(OUT_PATH, mode="a", header=False, index=False)
            time.sleep(3)


if __name__ == "__main__":
    build_weather("data/processed/matches_clean.csv", "data/processed/venues.csv")
    df = pd.read_csv(OUT_PATH)
    print(df.shape)
    print(df.head())