import pandas as pd


def build_match_features(matches_path, weather_path, innings_path):
    m = pd.read_csv(matches_path)

    w = pd.read_csv(weather_path).rename(columns={
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "precipitation_sum": "rain_mm",
        "wind_speed_10m_max": "wind_max",
    })

    inn = pd.read_csv(innings_path)
    first = inn[(inn.innings_no == 1) & (~inn.is_super_over)]
    first = first[["match_id", "batting_team", "total_runs", "wickets", "overs", "run_rate"]]
    first = first.rename(columns={
        "batting_team": "batting_first",
        "total_runs": "first_innings_runs",
        "wickets": "first_innings_wickets",
        "overs": "first_innings_overs",
        "run_rate": "first_innings_run_rate",
    })

    df = m.merge(
        w,
        left_on=["venue", "city", "start_date"],
        right_on=["venue", "city", "date"],
        how="left",
    ).drop(columns="date")
    df = df.merge(first, on="match_id", how="left")
    return df


if __name__ == "__main__":
    df = build_match_features(
        "data/processed/matches_clean.csv",
        "data/processed/weather.csv",
        "data/processed/innings_summary.csv",
    )
    df.to_csv("data/processed/match_features.csv", index=False)
    print(df.shape)
    print(df.isna().sum()[df.isna().sum() > 0])
    print(df.first_innings_runs.describe())
    