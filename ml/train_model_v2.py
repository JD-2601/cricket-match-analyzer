import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

FEATURES = ["temp_max", "temp_min", "rain_mm", "wind_max",
            "batting_first_won_toss", "venue_edge"]


def prepare(training_path, matches_path):
    d = pd.read_csv(training_path)
    dates = pd.read_csv(matches_path)[["match_id", "start_date"]]
    d = d.merge(dates, on="match_id")
    d = d.sort_values(["start_date", "match_id"]).reset_index(drop=True)

    d["recent_avg"] = d.first_innings_runs.shift(1).rolling(60, min_periods=20).mean()
    d["resid"] = d.first_innings_runs - d.recent_avg
    d["venue_edge"] = d.groupby("venue").resid.transform(
        lambda s: s.shift(1).expanding().mean()
    ).fillna(0)
    return d.dropna(subset=["recent_avg"]).reset_index(drop=True)


if __name__ == "__main__":
    d = prepare("data/processed/training_data.csv", "data/processed/matches_clean.csv")

    train = d[d.year < 2024]
    test = d[d.year >= 2024]

    model = RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=42)
    model.fit(train[FEATURES], train.resid)

    pred = test.recent_avg + model.predict(test[FEATURES])
    print("test matches:", len(test))
    print("recent-average baseline:",
          round((test.first_innings_runs - test.recent_avg).abs().mean(), 1))
    print("model average error:",
          round(mean_absolute_error(test.first_innings_runs, pred), 1))

    final = RandomForestRegressor(n_estimators=200, min_samples_leaf=5, random_state=42)
    final.fit(d[FEATURES], d.resid)
    bundle = {
        "model": final,
        "features": FEATURES,
        "recent_avg": float(d.first_innings_runs.tail(60).mean()),
        "venue_edge": d.groupby("venue").resid.mean().to_dict(),
    }
    joblib.dump(bundle, "ml/model_v2.joblib")
    print("saved. recent_avg:", round(bundle["recent_avg"], 1))