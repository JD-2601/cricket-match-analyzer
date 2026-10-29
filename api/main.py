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
import json

try:
    with open("data/processed/forecasts.json") as f:
        _forecasts = json.load(f)
except Exception:
    _forecasts = {}


@app.get("/weather/{city}")
def forecast(city: str):
    result = _forecasts.get(city.lower())
    if result is None:
        return {"error": "forecast not available for this city"}
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

players_df = pd.read_csv("data/processed/players.csv")


@app.get("/players")
def list_players():
    return {"players": sorted(players_df.player.tolist())}


@app.get("/player/{name}")
def player_stats(name: str):
    row = players_df[players_df.player == name]
    if row.empty:
        return {"error": "player not found"}
    return row.iloc[0].to_dict()


@app.get("/venue/{venue}/matches")
def venue_matches(venue: str):
    m = matches[matches.venue == venue].sort_values("start_date", ascending=False)
    m = m[["start_date", "team_1", "team_2", "winner", "win_margin", "margin_type"]].copy()
    m["win_margin"] = m["win_margin"].fillna(0)
    m = m.fillna("")
    return {"venue": venue, "matches": m.to_dict("records")}


wmatches = pd.read_csv("data/processed/matches_women.csv")
wfirst = pd.read_csv("data/processed/first_innings_women.csv")
wplayers = pd.read_csv("data/processed/players_women.csv")


@app.get("/women/venues")
def women_venues():
    return {"venues": sorted(wmatches.venue.dropna().unique().tolist())}


@app.get("/women/venue/{venue}/stats")
def women_venue_stats(venue: str):
    f = wfirst[wfirst.venue == venue]
    return {"matches": int((wmatches.venue == venue).sum()),
            "avg_first_innings_runs": round(float(f.runs.mean()), 1) if len(f) else 0}


@app.get("/women/venue/{venue}/history")
def women_venue_history(venue: str):
    f = wfirst[wfirst.venue == venue]
    h = f.groupby("year").runs.agg(["count", "mean"]).round(1).reset_index()
    return {"history": h.to_dict("records")}


@app.get("/women/venue/{venue}/matches")
def women_venue_matches(venue: str):
    m = wmatches[wmatches.venue == venue].sort_values("start_date", ascending=False)
    m = m[["start_date", "team_1", "team_2", "winner", "win_margin", "margin_type"]].copy()
    m["win_margin"] = m["win_margin"].fillna(0)
    m = m.fillna("")
    return {"venue": venue, "matches": m.to_dict("records")}


@app.get("/women/players")
def women_players():
    return {"players": sorted(wplayers.player.tolist())}


@app.get("/women/player/{name}")
def women_player(name: str):
    row = wplayers[wplayers.player == name]
    if row.empty:
        return {"error": "player not found"}
    return row.iloc[0].to_dict()


all_players = pd.read_csv("data/processed/players_all.csv")
all_teams = pd.read_csv("data/processed/teams_all.csv")


@app.get("/stats/players")
def stats_players(gender: str, fmt: str):
    df = all_players[(all_players.gender == gender) & (all_players.fmt == fmt)]
    return {"players": sorted(df.player.tolist())}


@app.get("/stats/player")
def stats_player(gender: str, fmt: str, name: str):
    df = all_players[(all_players.gender == gender) & (all_players.fmt == fmt) & (all_players.player == name)]
    if df.empty:
        return {"error": "player not found"}
    return df.iloc[0].to_dict()


@app.get("/stats/teams")
def stats_teams(gender: str, fmt: str):
    df = all_teams[(all_teams.gender == gender) & (all_teams.fmt == fmt)]
    df = df.sort_values("matches", ascending=False)
    return {"teams": df.to_dict("records")}


matches_all = pd.read_csv("data/processed/matches_all.csv")


@app.get("/fmt/venues")
def fmt_venues(gender: str, fmt: str):
    df = matches_all[(matches_all.gender == gender) & (matches_all.fmt == fmt)]
    return {"venues": sorted(df.venue.dropna().unique().tolist())}


@app.get("/fmt/matches")
def fmt_matches(gender: str, fmt: str, venue: str):
    df = matches_all[(matches_all.gender == gender) & (matches_all.fmt == fmt) & (matches_all.venue == venue)]
    df = df.sort_values("start_date", ascending=False)
    df = df[["start_date", "team_1", "team_2", "winner", "win_margin", "margin_type"]].copy()
    df["win_margin"] = df["win_margin"].fillna(0)
    return {"matches": df.fillna("").to_dict("records")}


@app.get("/fmt/predict")
def fmt_predict(gender: str, fmt: str, venue: str):
    df = matches_all[(matches_all.gender == gender) & (matches_all.fmt == fmt)]
    overall = df.first_runs.dropna()
    g = df[df.venue == venue].first_runs.dropna()
    n = len(g)
    w = n / (n + 5)
    pred = w * g.mean() + (1 - w) * overall.mean() if n else overall.mean()
    sd = g.std() if n >= 3 else overall.std()
    sd = 0 if pd.isna(sd) else float(sd)
    return {"predicted": round(float(pred)), "low": round(float(pred - 0.5 * sd)),
            "high": round(float(pred + 0.5 * sd)), "matches": int(n)}
