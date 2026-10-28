import joblib
import requests
import pandas as pd
from fastapi import FastAPI

app = FastAPI()

matches = pd.read_csv("data/processed/matches_clean.csv")


@app.get("/venues")
def get_venues():
    names = sorted(matches.venue.unique().tolist())
    return {"venues": names}
features = pd.read_csv("data/processed/match_features.csv")


@app.get("/venue/{name}/stats")
def venue_stats(name: str):
    g = features[features.venue == name]
    if g.empty:
        return {"error": "venue not found"}
    return {
        "venue": name,
        "matches": len(g),
        "avg_first_innings_runs": round(g.first_innings_runs.mean(), 1),
        "avg_temp_max": round(g.temp_max.mean(), 1),
        "avg_rain_mm": round(g.rain_mm.mean(), 2),
    }
venues = pd.read_csv("data/processed/venues.csv")

import time

_weather_cache = {}  # city -> (time saved, result)


@app.get("/weather/{city}")
def forecast(city: str):
    key = city.lower()
    cached = _weather_cache.get(key)
    if cached and time.time() - cached[0] < 3600:
        return cached[1]

    row = venues[venues.city.str.lower() == key]
    if row.empty:
        return {"error": "city not found"}

    lat = float(row.iloc[0].latitude)
    lon = float(row.iloc[0].longitude)

    r = None
    for attempt in range(3):
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=30,
        )
        if r.status_code != 429:
            break
        time.sleep(2 * (attempt + 1))

    if r.status_code != 200:
        if cached:
            return cached[1]
        return {"error": "weather service failed", "status": r.status_code}

    days = pd.DataFrame(r.json()["daily"]).rename(columns={"time": "date"})
    result = {"city": city, "forecast": days.to_dict("records")}
    _weather_cache[key] = (time.time(), result)
    return result
bundle = joblib.load("ml/model_v2.joblib")


@app.get("/predict")
def predict(venue: str, temp_max: float, temp_min: float,
            rain_mm: float, wind_max: float,
            batting_first_won_toss: int = 0):
    edge = bundle["venue_edge"].get(venue)
    if edge is None:
        return {"error": "venue not found"}
    row = pd.DataFrame([{
        "temp_max": temp_max, "temp_min": temp_min, "rain_mm": rain_mm,
        "wind_max": wind_max, "batting_first_won_toss": batting_first_won_toss,
        "venue_edge": edge,
    }])
    adj = float(bundle["model"].predict(row[bundle["features"]])[0])
    base = bundle["recent_avg"]
    return {"venue": venue, "recent_average": round(base, 1),
            "model_adjustment": round(adj, 1),
            "predicted_first_innings_runs": round(base + adj, 1)}
@app.get("/venue/{name}/history")
def venue_history(name: str):
    g = features[features.venue == name].copy()
    if g.empty:
        return {"error": "venue not found"}
    g["year"] = pd.to_datetime(g.start_date).dt.year
    by_year = (g.groupby("year").first_innings_runs
               .agg(["count", "mean"]).round(1).reset_index())
    return {"venue": name, "history": by_year.to_dict("records")}
@app.get("/cities")
def cities():
    return {"cities": sorted(venues.city.dropna().unique().tolist())}