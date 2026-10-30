import json
import sys
import time

import pandas as pd
import requests

URL = "https://api.open-meteo.com/v1/forecast"
OUT = "data/processed/venue_forecasts.json"
VARS = "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"

c = pd.read_csv("data/processed/venue_coords_all.csv").dropna(subset=["lat", "lon"])
c["key"] = c.lat.round(2).astype(str) + "," + c.lon.round(2).astype(str)
uniq = c.drop_duplicates("key").reset_index(drop=True)

try:
    with open(OUT, encoding="utf-8") as f:
        old = json.load(f)
except Exception:
    old = {}

by_key = {}
for start in range(0, len(uniq), 40):
    part = uniq.iloc[start:start + 40]
    data = None
    for attempt in range(3):
        try:
            r = requests.get(URL, params={
                "latitude": ",".join(str(x) for x in part.lat.round(4)),
                "longitude": ",".join(str(x) for x in part.lon.round(4)),
                "daily": VARS, "forecast_days": 5, "timezone": "auto"}, timeout=60)
        except requests.exceptions.RequestException:
            break
        if r.status_code == 200:
            data = r.json()
            break
        if r.status_code != 429:
            break
        time.sleep(10 * (attempt + 1))
    if data is None:
        continue
    if isinstance(data, dict):
        data = [data]
    for key, item in zip(part.key, data):
        d = item["daily"]
        keys = list(d.keys())
        recs = [dict(zip(keys, vals)) for vals in zip(*d.values())]
        for rec in recs:
            rec["date"] = rec.pop("time")
        by_key[key] = recs
    time.sleep(2)

result = dict(old)
for _, row in c.iterrows():
    if row.key in by_key:
        result[row.venue] = {"venue": row.venue, "forecast": by_key[row.key]}

print("Forecasts for", len(result), "grounds")
if not result:
    sys.exit(1)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f)
