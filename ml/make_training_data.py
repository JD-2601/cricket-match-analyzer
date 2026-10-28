import pandas as pd


def make_training_data(path):
    d = pd.read_csv(path)

    short = d.first_innings_overs < 19.5
    allout = d.first_innings_wickets == 10
    d = d[~(short & ~allout)].copy()

    d["year"] = pd.to_datetime(d.start_date).dt.year
    d["batting_first_won_toss"] = (d.toss_winner == d.batting_first).astype(int)

    cols = ["match_id", "year", "venue", "temp_max", "temp_min", "rain_mm",
            "wind_max", "batting_first_won_toss", "first_innings_runs"]
    return d[cols]


if __name__ == "__main__":
    d = make_training_data("data/processed/match_features.csv")
    d.to_csv("data/processed/training_data.csv", index=False)

    train = d[d.year < 2024]
    test = d[d.year >= 2024]
    guess = train.first_innings_runs.mean()
    error = (test.first_innings_runs - guess).abs().mean()

    print("rows:", len(d), "train:", len(train), "test:", len(test))
    print("always guess", round(guess, 1), "-> average error", round(error, 1), "runs")
    