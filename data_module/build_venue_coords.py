import time

import pandas as pd
import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

COORD_OVERRIDES = {
    "Kochi": (9.93, 76.27),
    "New Chandigarh": (30.80, 76.72),
}


def find_city(city):
    r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=20)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    return results[0]


def build_venue_coords(matches_path):
    m = pd.read_csv(matches_path)
    venues = m[["venue", "city"]].drop_duplicates().reset_index(drop=True)

    rows = []
    for _, row in venues.iterrows():
        city = row["city"]
        if city in COORD_OVERRIDES:
            lat, lon = COORD_OVERRIDES[city]
            country, found = "manual", city
        else:
            hit = find_city(city)
            lat = hit["latitude"] if hit else None
            lon = hit["longitude"] if hit else None
            country = hit.get("country") if hit else None
            found = hit["name"] if hit else None
            time.sleep(0.3)
        rows.append({
            "venue": row["venue"],
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "country": country,
            "found_name": found,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = build_venue_coords("data/processed/matches_clean.csv")
    df.to_csv("data/processed/venues.csv", index=False)
    print(df.shape)
    print(df.to_string())