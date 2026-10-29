import pandas as pd
from load_matches import load_all_matches
from load_deliveries import load_all_deliveries

m = load_all_matches("data/raw/wpl")
d = load_all_deliveries("data/raw/wpl")
m.to_csv("data/processed/matches_women.csv", index=False)
d = d[~d.is_super_over].copy()

first = d[d.innings_no == 1].groupby("match_id").runs_total.sum().rename("runs").reset_index()
first = first.merge(m[["match_id", "venue", "start_date"]], on="match_id")
first["year"] = first.start_date.str[:4].astype(int)
first.to_csv("data/processed/first_innings_women.csv", index=False)

bat = d[d.extras_type != "wides"]
g = bat.groupby("batter")
b = pd.DataFrame({
    "bat_matches": g.match_id.nunique(),
    "bat_runs": g.runs_batter.sum(),
    "balls_faced": g.size(),
    "fours": g.runs_batter.apply(lambda s: (s == 4).sum()),
    "sixes": g.runs_batter.apply(lambda s: (s == 6).sum()),
})
out = d[d.is_wicket & d.player_out.notna()].groupby("player_out").size()
b["dismissals"] = out.reindex(b.index).fillna(0)
ms = bat.groupby(["batter", "match_id"]).runs_batter.sum()
b["highest"] = ms.groupby(level=0).max()
b["fifties"] = ms.between(50, 99).groupby(level=0).sum()
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
p.reset_index().to_csv("data/processed/players_women.csv", index=False)
print(len(m), "matches,", len(p), "players")
print(p.sort_values("bat_runs", ascending=False).head(3)[["bat_runs", "strike_rate", "bat_avg"]])
