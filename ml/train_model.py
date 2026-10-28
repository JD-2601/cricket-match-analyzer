import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

FEATURES = ["year", "temp_max", "temp_min", "rain_mm", "wind_max",
            "batting_first_won_toss"]


def prepare(path):
    d = pd.read_csv(path)
    X = pd.get_dummies(d[FEATURES + ["venue"]], columns=["venue"])
    y = d["first_innings_runs"]
    return d, X, y


if __name__ == "__main__":
    d, X, y = prepare("data/processed/training_data.csv")

    train = d.year < 2024
    test = d.year >= 2024

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X[train], y[train])

    pred = model.predict(X[test])
    error = mean_absolute_error(y[test], pred)

    print("model average error:", round(error, 1), "runs")
    print("baseline to beat: 30.5 runs")

    joblib.dump(model, "ml/model.joblib")