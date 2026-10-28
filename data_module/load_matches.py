import json
from pathlib import Path

import pandas as pd


def parse_match(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    info = data["info"]

    toss = info.get("toss", {})
    outcome = info.get("outcome", {})
    by = outcome.get("by", {})

    margin_type = list(by.keys())[0] if by else None
    win_margin = by[margin_type] if by else None

    return {
        "match_id": Path(path).stem,
        "gender": info["gender"],
        "match_format": info["match_type"],
        "competition": info.get("event", {}).get("name"),
        "venue": info["venue"],
        "city": info.get("city"),
        "start_date": info["dates"][0],
        "team_1": info["teams"][0],
        "team_2": info["teams"][1],
        "toss_winner": toss.get("winner"),
        "toss_decision": toss.get("decision"),
        "winner": outcome.get("winner"),
        "result_type": outcome.get("result", "normal"),
        "win_margin": win_margin,
        "margin_type": margin_type,
    }


def load_all_matches(folder):
    rows = []
    for path in sorted(Path(folder).glob("*.json")):
        rows.append(parse_match(path))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = load_all_matches("data/raw/ipl_json")
    df.to_csv("data/processed/matches.csv", index=False)
    print(df.shape)
    print(df.head())