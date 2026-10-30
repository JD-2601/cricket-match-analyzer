import time
from pathlib import Path

import pandas as pd
import requests

OUT = "data/processed/venue_coords_all.csv"
HEAD = {"User-Agent": "cricket-match-analyzer-student-project"}

m = pd.read_csv("data/processed/matches_all.csv")
venues = sorted(m[~m.fmt.isin(["IPL", "WPL"])].venue.dropna().unique())

done = pd.read_csv(OUT) if Path(OUT).exists() else pd.DataFrame(columns=["venue", "lat", "lon", "source"])
have = set(done.venue)
rows = done.to_dict("records")


def nominatim(q):
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": q, "format": "json", "limit": 1}, headers=HEAD, timeout=30)
    j = r.json()
    return (float(j[0]["lat"]), float(j[0]["lon"])) if j else None


def openmeteo(name):
    r = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                     params={"name": name, "count": 1}, timeout=30)
    j = r.json().get("results")
    return (j[0]["latitude"], j[0]["longitude"]) if j else None


todo = [v for v in venues if v not in have]
print(len(venues), "grounds,", len(todo), "to do")
for i, v in enumerate(todo, 1):
    res, src = None, ""
    try:
        res = nominatim(v)
        src = "stadium"
        time.sleep(1.1)
        if res is None and "," in v:
            res = openmeteo(v.split(",")[-1].strip())
            src = "city"
    except Exception as e:
        print("  error:", v, e)
    if res:
        rows.append({"venue": v, "lat": res[0], "lon": res[1], "source": src})
    if i % 20 == 0:
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(i, "of", len(todo))

pd.DataFrame(rows).to_csv(OUT, index=False)
print("Found", len(rows), "of", len(venues), "grounds")
