import json
from pathlib import Path

import pandas as pd

SOURCES = [
    ("male", "IPL", "data/raw/ipl_json"),
    ("female", "WPL", "data/raw/wpl"),
    ("male", "T20I", "data/raw/t20i_male"),
    ("female", "T20I", "data/raw/t20i_female"),
    ("male", "ODI", "data/raw/odi_male"),
    ("female", "ODI", "data/raw/odi_female"),
    ("male", "Test", "data/raw/test_male"),
    ("female", "Test", "data/raw/test_female"),
]

rows = []
for gender, fmt, folder in SOURCES:
    files = sorted(Path(folder).glob("*.json"))
    print(gender, fmt, len(files), "files")
    for path in files:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        info = data["info"]
        outcome = info.get("outcome", {})
        by = outcome.get("by", {})
        mt = list(by.keys())[0] if by else None
        first = None
        inns = data.get("innings", [])
        if inns and not inns[0].get("super_over", False):
            first = sum(b["runs"]["total"] for o in inns[0].get("overs", []) for b in o["deliveries"])
        rows.append({
            "gender": gender, "fmt": fmt, "venue": info.get("venue"),
            "start_date": info["dates"][0],
            "team_1": info["teams"][0], "team_2": info["teams"][1],
            "winner": outcome.get("winner"),
            "win_margin": by[mt] if mt else None, "margin_type": mt,
            "first_runs": first,
        })

pd.DataFrame(rows).to_csv("data/processed/matches_all.csv", index=False)
print(len(rows), "matches saved")
