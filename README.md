# Cricket Match Analyzer

A data analytics project on IPL (men's) cricket. It predicts first-innings scores, explores ground statistics and shows a 5-day weather forecast for match cities.

**Live app:** https://cricket-match-analyzer-clqdxtaygjo5jtcetwhhvf.streamlit.app

(The API sleeps when unused. If the page shows an error at first, wait about a minute and refresh.)

## Features

- **Score Predictor:** choose a ground and weather conditions to get a predicted first-innings score, compared with the ground's recent average.
- **Ground Explorer:** matches played, average first-innings score, average weather, and a yearly trend per ground.
- **Weather Forecast:** next 5 days (temperature, rain, wind) for a city.
- **Player Stats:** batting and bowling records for every IPL player (runs, strike rate, average, wickets, economy).
- **Matches per ground:** date, both teams and result for every match at a ground.

## How it works

- `data_module/` loads and cleans Cricsheet IPL data and builds match, venue and weather tables.
- `ml/` trains the prediction model.
- `api/` is a FastAPI backend with endpoints for venues, stats, history, weather and prediction.
- `app/` is the Streamlit front end, which calls the API.
- `tests/` has the automated tests.
- A GitHub Actions job refreshes the weather forecasts every 12 hours.

## Model result

The model scores about the same as a simple "recent average at the ground" baseline (29.6 vs 29.7 error). So ground and weather add little beyond history. This is an honest finding, not a bug.

## Run locally

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn api.main:app --reload
    streamlit run app/app.py

Run the tests with `pytest`.

## Data and tools

Data: Cricsheet (IPL ball-by-ball), Open-Meteo (weather). Tools: Python, pandas, scikit-learn, FastAPI, Streamlit, Plotly.

## Still to do

Women's data, other formats (ODI, Test), humidity, head-to-head records.
