import pandas as pd


def build_innings_summary(deliveries_path, matches_path):
    deliveries = pd.read_csv(deliveries_path)
    matches = pd.read_csv(matches_path)

    summary = (
        deliveries
        .groupby(["match_id", "innings_no", "batting_team", "is_super_over"])
        .agg(
            total_runs=("runs_total", "sum"),
            wickets=("is_wicket", "sum"),
            legal_balls=("is_legal_ball", "sum"),
        )
        .reset_index()
    )

    summary["overs"] = (summary["legal_balls"] / 6).round(2)
    summary["run_rate"] = (summary["total_runs"] / summary["overs"]).round(2)

    match_info = matches[["match_id", "gender", "match_format", "venue", "city", "start_date"]]
    summary = summary.merge(match_info, on="match_id")
    return summary


if __name__ == "__main__":
    df = build_innings_summary("data/processed/deliveries.csv", "data/processed/matches.csv")
    df.to_csv("data/processed/innings_summary.csv", index=False)
    print(df.shape)
    print(df[df.match_id == 335982][["batting_team", "total_runs", "wickets", "overs", "run_rate"]])
    