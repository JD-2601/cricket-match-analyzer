import pandas as pd

from data_module.load_matches import parse_match

P = "data/processed/"


def test_matches_table_is_complete():
    m = pd.read_csv(P + "matches_clean.csv")
    assert len(m) == 1243
    assert m.match_id.is_unique
    assert m.city.isna().sum() == 0
    assert m.venue.nunique() == 37
    assert set(m.result_type) <= {"normal", "tie", "no result"}


def test_no_result_match_has_no_winner():
    row = parse_match("data/raw/ipl_json/1527685.json")
    assert row["result_type"] == "no result"
    assert row["winner"] is None


def test_first_ipl_match_scores_match_the_scorecard():
    inn = pd.read_csv(P + "innings_summary.csv")
    m = inn[(inn.match_id == 335982) & (~inn.is_super_over)].sort_values("innings_no")
    assert list(m.total_runs) == [222, 82]
    assert list(m.wickets) == [3, 10]


def test_every_match_has_weather():
    f = pd.read_csv(P + "match_features.csv")
    assert len(f) == 1243
    assert f.temp_max.isna().sum() == 0
    assert f.rain_mm.isna().sum() == 0


def test_training_data_excludes_rain_shortened_innings():
    t = pd.read_csv(P + "training_data.csv")
    assert len(t) == 1217


def test_venue_coordinates_are_filled_in():
    v = pd.read_csv(P + "venues.csv")
    assert v.latitude.notna().all()
    assert v.longitude.notna().all()
    assert v.latitude.between(-90, 90).all()