import io
import zipfile
from pathlib import Path

import pandas as pd
import requests
from load_matches import load_all_matches
from load_deliveries import load_all_deliveries

SOURCES = [
    ("male", "IPL", "data/raw/ipl_json", None),
    ("female", "WPL", "data/raw/wpl", None),
    ("male", "T20I", "data/raw/t20i_male", "t20s_male_json"),
    ("female", "T20I", "data/raw/t20i_female", "t20s_female_json"),
    ("male", "ODI", "data/raw/odi_male", "odis_male_json"),
    ("female", "ODI", "data/raw/odi_female", "odis_female_json"),
    ("male", "Test", "data/raw/test_male", "tests_male_json"),
    ("female", "Test", "data/raw/test_female", "tests_female_json"),
]


def download(name, folder):
    if list(Path(folder).glob("*.json")):
        return True
    r = requests.get(f"https://cricsheet.org/downloads/{name}.zip", timeout=300)
    if r.status_code != 200:
        print("  download failed:", name, r.status_code)
        return False
    Path(folder).mkdir(parents=True, exist_ok=True)
    zipfile.ZipFile(io.BytesIO(r.content)).extractall(folder)
    return True


def player_stats(d):
    d = d[~d.is_super_over].copy()
    bat = d[d.extras_type != "wides"].copy()
    bat["f"] = bat.runs_batter == 4
    bat["s"] = bat.runs_batter == 6
    g = bat.groupby("batter")
    b = pd.DataFrame({
        "bat_matches": g.match_id.nunique(),
        "bat_runs": g.runs_batter.sum(),
        "balls_faced": g.size(),
        "fours": g.f.sum(),
        "sixes": g.s.sum(),
    })
    out = d[d.is_wicket & d.player_out.notna()].groupby("player_out").size()
    b["dismissals"] = out.reindex(b.index).fillna(0)
    ms = bat.groupby(["batter", "match_id", "innings_no"]).runs_batter.sum()
    b["highest"] = ms.groupby(level=0).max()
    b["fifties"] = ((ms >= 50) & (ms < 100)).groupby(level=0).sum()
    b["hundreds"] = (ms >= 100).groupby(level=0).sum()
    b["strike_rate"] = (b.bat_runs / b.balls_faced * 100).round(1)
    b["bat_avg"] = (b.bat_runs / b.dismissals.where(b.dismissals > 0)).round(1)

    d["bowl_runs"] = d.runs_batter + d.runs_extras.where(d.extras_type.isin(["wides", "noballs"]), 0)
    gb = d.groupby("bowler")
    o = pd.DataFrame({
        "bowl_matches": gb.match_id.nunique(),
        "balls_bowled": gb.is_legal_ball.sum(),
        "runs_conceded": gb.bowl_runs.sum(),
    })
    nb = ["run out", "retired hurt", "retired out", "obstructing the field"]
    wk = d[d.is_wicket & ~d.wicket_type.isin(nb)].groupby("bowler").size()
    o["wickets"] = wk.reindex(o.index).fillna(0)
    o["economy"] = (o.runs_conceded / (o.balls_bowled / 6)).round(2)
    p = b.join(o, how="outer").fillna(0)
    p.index.name = "player"
    return p.reset_index()


def team_stats(d, m):
    d = d[~d.is_super_over]
    inn = d.groupby(["match_id", "innings_no", "batting_team"]).runs_total.sum().reset_index()
    avg = inn.groupby("batting_team").runs_total.mean().round(1)
    top = inn.groupby("batting_team").runs_total.max()
    t = pd.concat([
        m[["match_id", "team_1", "winner"]].rename(columns={"team_1": "team"}),
        m[["match_id", "team_2", "winner"]].rename(columns={"team_2": "team"}),
    ])
    t["won"] = t.team == t.winner
    t["nores"] = t.winner.isna()
    s = t.groupby("team").agg(matches=("match_id", "count"), wins=("won", "sum"), no_result=("nores", "sum"))
    s["losses"] = s.matches - s.wins - s.no_result
    s["win_pct"] = (s.wins / s.matches * 100).round(1)
    s["avg_score"] = avg.reindex(s.index)
    s["highest_total"] = top.reindex(s.index)
    s.index.name = "team"
    return s.reset_index().fillna(0)


players, teams = [], []
for gender, fmt, folder, name in SOURCES:
    print(gender, fmt)
    if name and not download(name, folder):
        continue
    m = load_all_matches(folder)
    d = load_all_deliveries(folder)
    p = player_stats(d)
    p["gender"], p["fmt"] = gender, fmt
    ts = team_stats(d, m)
    ts["gender"], ts["fmt"] = gender, fmt
    players.append(p)
    teams.append(ts)
    print("  ", len(m), "matches,", len(p), "players,", len(ts), "teams")

pd.concat(players).to_csv("data/processed/players_all.csv", index=False)
pd.concat(teams).to_csv("data/processed/teams_all.csv", index=False)
print("Done")
