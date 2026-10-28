from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_venues_lists_37_grounds():
    r = client.get("/venues").json()
    assert len(r["venues"]) == 37
    assert "Narendra Modi Stadium" in r["venues"]


def test_cities_includes_ahmedabad():
    assert "Ahmedabad" in client.get("/cities").json()["cities"]


def test_venue_stats_for_eden_gardens():
    r = client.get("/venue/Eden Gardens/stats").json()
    assert r["matches"] == 107
    assert r["avg_first_innings_runs"] == 168.6


def test_unknown_venue_returns_error():
    assert "error" in client.get("/venue/Nowhere Oval/stats").json()


def test_history_has_years_and_counts():
    r = client.get("/venue/Eden Gardens/history").json()
    assert len(r["history"]) > 5
    assert {"year", "count", "mean"} <= set(r["history"][0])


def test_predict_returns_sensible_score():
    r = client.get("/predict", params={
        "venue": "Narendra Modi Stadium", "temp_max": 35, "temp_min": 22,
        "rain_mm": 0, "wind_max": 12}).json()
    assert 150 < r["predicted_first_innings_runs"] < 250
    total = r["recent_average"] + r["model_adjustment"]
    assert abs(total - r["predicted_first_innings_runs"]) < 0.2


def test_predict_unknown_venue_returns_error():
    r = client.get("/predict", params={
        "venue": "Nowhere Oval", "temp_max": 35, "temp_min": 22,
        "rain_mm": 0, "wind_max": 12}).json()
    assert "error" in r


def test_weather_unknown_city_returns_error():
    assert "error" in client.get("/weather/Atlantis").json()