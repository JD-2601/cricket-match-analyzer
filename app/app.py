import math
import streamlit.components.v1 as components
import base64
from pathlib import Path
from plotly.subplots import make_subplots

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

import os
API = os.environ.get("API_URL", "http://127.0.0.1:8000")
GOLD = "#F5C542"
BLUE = "#2F8BFF"
ICE = "#E6EEFF"
MUTED = "#8FA8D8"
PHOTO = Path(__file__).resolve().parent.parent / "assets" / "pitch.jpg"

st.set_page_config(page_title="Cricket Match Analyzer", page_icon="🏏", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&display=swap');
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #050914; border-right: 1px solid rgba(47,139,255,.4); }
.block-container { padding-top: 1.2rem; max-width: 1200px; }

.topbar { display:flex; justify-content:space-between; align-items:center;
  background: rgba(10,19,48,.9); border:1px solid rgba(47,139,255,.55);
  border-left: 6px solid #F5C542; border-radius: 10px; padding: 14px 22px; margin-bottom: 16px; }
.brand { font-family:'Orbitron',sans-serif; font-weight:800; letter-spacing:2px; color:#F5C542; font-size:1.1rem; }
.crumb { font-family:'Orbitron',sans-serif; font-weight:600; color:#E6EEFF; letter-spacing:1.5px; font-size:.9rem; }
.crumb span { color:#2F8BFF; margin:0 8px; }

.card { background: rgba(10,19,48,.9); border:1px solid rgba(47,139,255,.55);
  border-top: 3px solid #2F8BFF; border-radius: 10px; padding: 14px 18px; }
.card .label { font-size:.8rem; color:#8FA8D8; letter-spacing:1px; }
.card .value { font-family:'Orbitron',sans-serif; font-weight:800; font-size:2.2rem; color:#F5C542; line-height:1.3; }
.card .sub { font-size:.8rem; color:#8FA8D8; }

.st-key-controls { background: rgba(10,19,48,.88); border:1px solid rgba(47,139,255,.55);
  border-radius: 10px; padding: 14px 18px; margin-bottom: 16px; }
[data-testid="stPlotlyChart"] { background: rgba(10,19,48,.9); border:1px solid rgba(47,139,255,.55);
  border-radius: 10px; padding: 10px; }

.section { font-family:'Orbitron',sans-serif; font-weight:600; color:#F5C542; letter-spacing:1.5px; margin:18px 0 8px; }
.note { border-left:4px solid #2F8BFF; background: rgba(15,30,69,.9); padding:10px 16px;
  border-radius:6px; color:#E6EEFF; font-size:.9rem; margin-top:10px; }
.hint { background: rgba(5,9,20,.8); border:1px solid rgba(232,245,236,.25); border-radius:10px;
  padding:14px 18px; color:#E6EEFF; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def photo_b64():
    if PHOTO.exists():
        return base64.b64encode(PHOTO.read_bytes()).decode()
    return None


def apply_background(results):
    if results:
        css = """
        .stApp {
            background-color: #060B1A;
            background-image:
                radial-gradient(circle at 100% 0%, rgba(47,139,255,.45), transparent 45%),
                radial-gradient(circle at 0% 100%, rgba(47,139,255,.22), transparent 40%),
                linear-gradient(rgba(47,139,255,.12) 1px, transparent 1px),
                linear-gradient(90deg, rgba(47,139,255,.12) 1px, transparent 1px);
            background-size: auto, auto, 32px 32px, 32px 32px;
            background-attachment: fixed;
        }"""
    else:
        b64 = photo_b64()
        if b64:
            css = (".stApp { background: linear-gradient(rgba(4,10,8,.30), rgba(4,10,8,.30)), "
                   f"url(data:image/jpeg;base64,{b64}) center / cover fixed; }}")
        else:
            css = ".stApp { background: #12301F; }"
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def header(section, page):
    st.markdown(
        f'<div class="topbar"><div class="brand">🏏 Cricket match analyzer</div>'
        f'<div class="crumb">{section}<span>/</span>{page}</div></div>',
        unsafe_allow_html=True)


def card(label, value, sub=""):
    return (f'<div class="card"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>')


def hint(text):
    st.markdown(f'<div class="hint">{text}</div>', unsafe_allow_html=True)


@st.cache_data
def get_venues():
    return requests.get(f"{API}/venues", timeout=30).json()["venues"]


def year_chart(df, overall):
    last = df.iloc[-1]
    others = [f"{v:g}" for v in df["avg_score"][:-1]] + [""]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["year"], y=df["avg_score"], width=0.3, marker_color=GOLD,
        text=others, textposition="outside", textfont=dict(color=ICE, size=12),
        customdata=df["matches"],
        hovertemplate="Year %{x}<br>Average %{y} runs<br>Matches %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["avg_score"], mode="markers",
        marker=dict(symbol="line-ew", size=20, line=dict(width=3, color=ICE)),
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=[last["year"]], y=[last["avg_score"]], mode="text",
        text=[f"{last['avg_score']:g}"], textposition="top center",
        textfont=dict(color=GOLD, size=16), hoverinfo="skip",
    ))
    fig.add_hline(y=overall, line_dash="dash", line_color=BLUE, line_width=2,
                  annotation_text=f"Ground average: {overall}",
                  annotation_position="top left", annotation_font_color=BLUE)
    fig.update_layout(
        height=440, showlegend=False, margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=ICE, family="sans-serif"),
        xaxis=dict(tickmode="array", tickvals=df["year"],
                   ticktext=[f"{int(y)}<br>n={int(n)}" for y, n in zip(df["year"], df["matches"])],
                   gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Runs", range=[0, df["avg_score"].max() * 1.2],
                   gridcolor="rgba(143,168,216,.22)"),
    )
    return fig
def stump_chart(df, overall, height=500):
    W, H = 1000, 440
    left, right, top, bottom = 64, 24, 46, 74
    plot_w, plot_h = W - left - right, H - top - bottom
    ymax = math.ceil(max(df["avg_score"].max(), overall) * 1.15 / 50) * 50

    def y(v):
        return top + plot_h * (1 - v / ymax)

    base = y(0)
    n = len(df)
    slot = plot_w / n
    w = min(30, slot * 0.42)
    r = w / 2
    parts = []

    for t in range(0, int(ymax) + 1, 50):
        parts.append(
            f'<line x1="{left}" y1="{y(t):.1f}" x2="{W - right}" y2="{y(t):.1f}" '
            f'stroke="#8FA8D8" stroke-opacity=".22"/>'
            f'<text x="{left - 10}" y="{y(t) + 4:.1f}" text-anchor="end" '
            f'fill="#8FA8D8" font-size="13">{t}</text>')
    parts.append(f'<text x="{left - 10}" y="{top - 22}" text-anchor="end" fill="#8FA8D8" font-size="13">Runs</text>')

    parts.append(f'<rect x="{left}" y="{base:.1f}" width="{plot_w}" height="7" rx="3" fill="#1E6B38"/>')

    ya = y(overall)
    parts.append(
        f'<line x1="{left}" y1="{ya:.1f}" x2="{W - right}" y2="{ya:.1f}" '
        f'stroke="#2F8BFF" stroke-width="2" stroke-dasharray="7 5"/>'
        f'<text x="{left + 8}" y="{top - 22}" fill="#2F8BFF" font-size="13" '
        f'font-weight="600">Ground average: {overall}</text>')

    for i, row in enumerate(df.itertuples()):
        cx = left + slot * (i + 0.5)
        v = row.avg_score
        top_y = y(v)
        x0, x1 = cx - r, cx + r
        last = i == n - 1
        fill = "url(#woodGold)" if last else "url(#wood)"
        path = (f"M{x0:.1f},{base:.1f} L{x0:.1f},{top_y + r:.1f} "
                f"A{r:.1f},{r:.1f} 0 0 1 {x1:.1f},{top_y + r:.1f} L{x1:.1f},{base:.1f} Z")
        label_fill = "#F5C542" if last else "#E6EEFF"
        label_size = 18 if last else 13
        parts.append(
            f'<g><title>{int(row.year)}: average {v:g} runs, {int(row.matches)} matches</title>'
            f'<ellipse cx="{cx:.1f}" cy="{base + 1:.1f}" rx="{w * 0.95:.1f}" ry="4" fill="#27853F"/>'
            f'<path d="{path}" fill="{fill}" stroke="#4A2E0E" stroke-width="2" stroke-linejoin="round"/>'
            f'<rect x="{x0 + 4:.1f}" y="{top_y + r:.1f}" width="4" height="{max(base - top_y - r - 8, 0):.1f}" '
            f'rx="2" fill="#FFFFFF" fill-opacity=".28"/>'
            f'<rect x="{cx - w * 0.85:.1f}" y="{top_y - 8:.1f}" width="{w * 1.7:.1f}" height="7" rx="3.5" '
            f'fill="#F4E9C9" stroke="#4A2E0E" stroke-width="1.5"/>'
            f'<text x="{cx:.1f}" y="{top_y - 18:.1f}" text-anchor="middle" fill="{label_fill}" '
            f'font-size="{label_size}" font-weight="700">{v:g}</text>'
            f'<text x="{cx:.1f}" y="{base + 28:.1f}" text-anchor="middle" fill="#E6EEFF" font-size="14">{int(row.year)}</text>'
            f'<text x="{cx:.1f}" y="{base + 46:.1f}" text-anchor="middle" fill="#8FA8D8" font-size="12">n={int(row.matches)}</text>'
            f'</g>')

    html = f"""
    <style>body {{ margin:0; background:transparent; }}</style>
    <div style="background:rgba(10,19,48,.9);border:1px solid rgba(47,139,255,.55);
                border-radius:10px;padding:10px;">
    <svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg"
         style="font-family:sans-serif">
    <defs>
      <linearGradient id="wood" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stop-color="#E9CB8F"/><stop offset=".55" stop-color="#C9954A"/>
        <stop offset="1" stop-color="#9A6A2A"/></linearGradient>
      <linearGradient id="woodGold" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0" stop-color="#FFE08A"/><stop offset=".55" stop-color="#F5C542"/>
        <stop offset="1" stop-color="#C9962A"/></linearGradient>
    </defs>
    {''.join(parts)}
    </svg></div>"""
    components.html(html, height=height)
TEMP_STOPS = [(10, (47, 139, 255)), (20, (26, 188, 156)), (28, (245, 197, 66)),
              (36, (255, 140, 66)), (44, (255, 77, 77))]


def temp_rgb(t):
    if t <= TEMP_STOPS[0][0]:
        return TEMP_STOPS[0][1]
    for (t0, c0), (t1, c1) in zip(TEMP_STOPS, TEMP_STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * f) for a, b in zip(c0, c1))
    return TEMP_STOPS[-1][1]

def weather_card(label, value, sub, t):
    r, g, b = temp_rgb(t)
    dr, dg, db = (round(c * 0.62) for c in (r, g, b))
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    ink = "#0A1330" if lum > 150 else "#FFFFFF"
    return (
        f'<div class="card" style="background: linear-gradient(145deg, '
        f'rgb({r},{g},{b}), rgb({dr},{dg},{db})); '
        f'border:1px solid rgba(255,255,255,.35); border-top:1px solid rgba(255,255,255,.35); '
        f'box-shadow: 0 6px 18px rgba(0,0,0,.35);">'
        f'<div class="label" style="color:{ink}; font-weight:600">{label}</div>'
        f'<div class="value" style="color:{ink}">{value}</div>'
        f'<div class="sub" style="color:{ink}">{sub}</div></div>')
st.sidebar.markdown("### 🏏 Menu")
gender = st.sidebar.radio("Section", ["Men's", "Women's"])
page = st.sidebar.radio("Page", ["Score Predictor", "Ground Explorer", "Weather Forecast", "Player Stats"])

header(gender, page)

if gender == "Women's":
    apply_background(False)
    hint("Women's data isn't loaded yet. We'll add it after the men's pipeline is finished.")
    st.stop()

try:
    venues = get_venues()
except Exception:
    apply_background(False)
    st.error("Can't reach the API. Start it with: uvicorn api.main:app --reload")
    st.stop()

results = False

if page == "Score Predictor":
    with st.container(key="controls"):
        c1, c2, c3, c4, c5 = st.columns([2.2, 1, 1, 1, 1])
        venue = c1.selectbox("Ground", venues, index=None, placeholder="Choose a ground")
        temp_max = c2.slider("Max temp (°C)", 15, 48, 35)
        temp_min = c3.slider("Min temp (°C)", 5, 35, 22)
        rain = c4.slider("Rain (mm)", 0, 10, 0)
        wind = c5.slider("Wind (km/h)", 0, 40, 12)
        b1, b2 = st.columns([1, 4])
        clicked = b1.button("Predict", type="primary", use_container_width=True)
        toss = b2.checkbox("Team batting first won the toss")

    if clicked:
        if venue is None:
            st.warning("Choose a ground first.")
        else:
            st.session_state["pred"] = requests.get(f"{API}/predict", params={
                "venue": venue, "temp_max": temp_max, "temp_min": temp_min,
                "rain_mm": rain, "wind_max": wind,
                "batting_first_won_toss": int(toss),
            }, timeout=30).json()

    r = st.session_state.get("pred")
    if r and "error" in r:
        st.error(r["error"])
    elif r:
        results = True
        pred, base, adj = r["predicted_first_innings_runs"], r["recent_average"], r["model_adjustment"]

        k1, k2, k3 = st.columns(3)
        k1.markdown(card("Predicted score", pred, r["venue"]), unsafe_allow_html=True)
        k2.markdown(card("Recent average", base, "last 60 matches"), unsafe_allow_html=True)
        k3.markdown(card("Ground + weather", f"{adj:+}", "runs vs recent average"), unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=pred,
            gauge={"axis": {"range": [120, 260], "tickcolor": ICE},
                   "bar": {"color": GOLD}, "bgcolor": "rgba(255,255,255,0.05)",
                   "threshold": {"line": {"color": BLUE, "width": 5}, "value": base}},
            number={"font": {"color": GOLD}},
        ))
        fig.update_layout(height=300, margin=dict(l=30, r=30, t=30, b=10),
                          paper_bgcolor="rgba(0,0,0,0)", font=dict(color=ICE))
        st.markdown('<div class="section">Prediction vs recent average</div>', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<div class="note">Blue line = recent average. Ground and weather add little beyond '
            'recent scoring levels (model error 29.6 runs vs 29.7 for the recent average). '
            'Treat this as a rough estimate.</div>', unsafe_allow_html=True)
    else:
        hint("Choose a ground, set the conditions, and click Predict.")

if page == "Ground Explorer":
    with st.container(key="controls"):
        venue = st.selectbox("Ground", venues, index=None, placeholder="Choose a ground")

    if venue is None:
        hint("Choose a ground to see its average scores, weather and history.")
    else:
        results = True
        stats = requests.get(f"{API}/venue/{venue}/stats", timeout=30).json()
        hist = requests.get(f"{API}/venue/{venue}/history", timeout=30).json()

        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(card("Matches", stats["matches"]), unsafe_allow_html=True)
        k2.markdown(card("Avg first-innings", stats["avg_first_innings_runs"], "runs"), unsafe_allow_html=True)
        k3.markdown(card("Avg max temp", stats["avg_temp_max"], "°C"), unsafe_allow_html=True)
        k4.markdown(card("Avg rain", stats["avg_rain_mm"], "mm per match day"), unsafe_allow_html=True)

        df = pd.DataFrame(hist["history"]).rename(columns={"count": "matches", "mean": "avg_score"})
        st.markdown(f'<div class="section">Average first-innings score by year, {venue}</div>',
                    unsafe_allow_html=True)
        stump_chart(df, stats["avg_first_innings_runs"])
        text = "Years with few matches are less reliable."
        if len(df) >= 2:
            diff = round(df.iloc[-1]["avg_score"] - df.iloc[0]["avg_score"])
            word = "rose" if diff > 0 else "fell"
            text = (f"Scores here {word} about {abs(diff)} runs from {int(df.iloc[0]['year'])} "
                    f"to {int(df.iloc[-1]['year'])}. " + text)
        st.markdown(f'<div class="note">{text} Raw averages, not adjusted for year.</div>',
                    unsafe_allow_html=True)

        mm = requests.get(f"{API}/venue/{venue}/matches", timeout=30).json()
        st.markdown('<div class="section">Matches at this ground</div>', unsafe_allow_html=True)
        mdf = pd.DataFrame(mm["matches"])
        if mdf.empty:
            st.info("No matches found for this ground.")
        else:
            mdf["Result"] = mdf.apply(
                lambda r: (f"{r.winner} by {int(r.win_margin)} {r.margin_type}"
                           if r.winner and r.margin_type else (r.winner or "No result")), axis=1)
            mdf["Date"] = pd.to_datetime(mdf["start_date"]).dt.strftime("%d %b %Y")
            mdf = mdf.rename(columns={"team_1": "Team 1", "team_2": "Team 2"})
            st.dataframe(mdf[["Date", "Team 1", "Team 2", "Result"]],
                         hide_index=True, use_container_width=True)
if page == "Weather Forecast":
    with st.container(key="controls"):
        cities = requests.get(f"{API}/cities", timeout=30).json()["cities"]
        city = st.selectbox("City", cities, index=None, placeholder="Choose a city")

    if city is None:
        hint("Choose a city to see the next 5 days of weather.")
    else:
        data = requests.get(f"{API}/weather/{city}", timeout=60).json()
        if "error" in data:
            st.error(data["error"])
        else:
            results = True
            days = pd.DataFrame(data["forecast"])
            days["label"] = pd.to_datetime(days["date"]).dt.strftime("%a %d %b")

            cols = st.columns(len(days))
            for col, row in zip(cols, days.itertuples()):
                icon = "🌧️" if row.precipitation_sum >= 1 else "☀️"
                col.markdown(weather_card(
                    f"{icon} {row.label}",
                    f"{row.temperature_2m_max:g}°",
                    f"Low {row.temperature_2m_min:g}°<br>Rain {row.precipitation_sum:g} mm"
                    f"<br>Wind {row.wind_speed_10m_max:g} km/h",
                    row.temperature_2m_max), unsafe_allow_html=True)
            st.caption("Card colour follows the day's high: blue is cool, gold is warm, red is very hot.")
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(
                x=days["label"], y=days["precipitation_sum"], name="Rain (mm)",
                marker_color=BLUE, opacity=0.55, width=0.3), secondary_y=True)
            fig.add_trace(go.Scatter(
                x=days["label"], y=days["temperature_2m_max"], name="Max temp (°C)",
                mode="lines+markers+text", line=dict(color=GOLD, width=3),
                text=days["temperature_2m_max"], textposition="top center",
                textfont=dict(color=GOLD)), secondary_y=False)
            fig.add_trace(go.Scatter(
                x=days["label"], y=days["temperature_2m_min"], name="Min temp (°C)",
                mode="lines+markers+text", line=dict(color=ICE, width=3),
                text=days["temperature_2m_min"], textposition="bottom center",
                textfont=dict(color=ICE)), secondary_y=False)
            fig.update_yaxes(
                title_text="Temperature (°C)", secondary_y=False,
                range=[days["temperature_2m_min"].min() - 5, days["temperature_2m_max"].max() + 5],
                gridcolor="rgba(143,168,216,.22)")
            fig.update_yaxes(
                title_text="Rain (mm)", secondary_y=True, showgrid=False,
                range=[0, max(5, days["precipitation_sum"].max() * 1.5)])
            fig.update_layout(
                height=380, margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=ICE), legend=dict(orientation="h", y=1.15))
            st.markdown(f'<div class="section">Next 5 days, {city}</div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                '<div class="note">Forecast from Open-Meteo for the city centre. '
                'Conditions at the ground itself can differ a little.</div>',
                unsafe_allow_html=True)
apply_background(results)


if page == "Player Stats":
    results = True

    @st.cache_data(ttl=3600)
    def get_players():
        return requests.get(f"{API}/players", timeout=30).json()["players"]

    with st.container(key="controls"):
        names = get_players()
        default = names.index("V Kohli") if "V Kohli" in names else 0
        player = st.selectbox("Player (type to search)", names, index=default)

    p = requests.get(f"{API}/player/{player}", timeout=30).json()

    if "error" in p:
        st.error(p["error"])
    else:
        st.subheader("Batting")
        batting = [
            ("Runs", f"{int(p['bat_runs'])}", f"{int(p['bat_matches'])} matches"),
            ("Strike rate", f"{p['strike_rate']}", "runs per 100 balls"),
            ("Average", f"{p['bat_avg']}", "runs per dismissal"),
            ("Highest", f"{int(p['highest'])}", f"{int(p['fifties'])} fifties, {int(p['hundreds'])} hundreds"),
        ]
        for col, item in zip(st.columns(4), batting):
            col.markdown(card(*item), unsafe_allow_html=True)

        if p["bowl_matches"] > 0 and p["balls_bowled"] >= 30:
            st.subheader("Bowling")
            bowling = [
                ("Wickets", f"{int(p['wickets'])}", f"{int(p['bowl_matches'])} matches"),
                ("Economy", f"{p['economy']}", "runs per over"),
                ("Balls bowled", f"{int(p['balls_bowled'])}", f"{int(p['runs_conceded'])} runs conceded"),
            ]
            for col, item in zip(st.columns(3), bowling):
                col.markdown(card(*item), unsafe_allow_html=True)

        fours = p["fours"] * 4
        sixes = p["sixes"] * 6
        other = max(p["bat_runs"] - fours - sixes, 0)
        fig = go.Figure(go.Bar(
            x=["Fours", "Sixes", "Singles, twos and threes"],
            y=[fours, sixes, other],
            text=[int(fours), int(sixes), int(other)],
            textposition="outside",
            marker_color=["#f5c542", "#ff6b4a", "#3b82f6"],
        ))
        fig.update_layout(
            title=f"Where {player}'s runs came from",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
