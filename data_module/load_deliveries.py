import json
from pathlib import Path

import pandas as pd


def parse_deliveries(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    match_id = Path(path).stem
    rows = []

    for innings_no, innings in enumerate(data["innings"], start=1):
        for over in innings["overs"]:
            for ball in over["deliveries"]:
                extras = ball.get("extras", {})
                wickets = ball.get("wickets", [])
                first_wicket = wickets[0] if wickets else {}

                rows.append({
                    "match_id": match_id,
                    "innings_no": innings_no,
                    "batting_team": innings["team"],
                    "is_super_over": innings.get("super_over", False),
                    "over": over["over"] + 1,
                    "batter": ball["batter"],
                    "bowler": ball["bowler"],
                    "non_striker": ball["non_striker"],
                    "runs_batter": ball["runs"]["batter"],
                    "runs_extras": ball["runs"]["extras"],
                    "runs_total": ball["runs"]["total"],
                    "extras_type": list(extras.keys())[0] if extras else None,
                    "is_legal_ball": not ("wides" in extras or "noballs" in extras),
                    "is_wicket": len(wickets) > 0,
                    "wicket_type": first_wicket.get("kind"),
                    "player_out": first_wicket.get("player_out"),
                })
    return rows


def load_all_deliveries(folder):
    all_rows = []
    for path in sorted(Path(folder).glob("*.json")):
        all_rows.extend(parse_deliveries(path))
    return pd.DataFrame(all_rows)


if __name__ == "__main__":
    df = load_all_deliveries("data/raw/ipl_json")
    df.to_csv("data/processed/deliveries.csv", index=False)
    print(df.shape)
    print(df.head())
    