import pandas as pd

VENUE_FIXES = {
    "M.Chinnaswamy Stadium": "M Chinnaswamy Stadium",
    "Feroz Shah Kotla": "Arun Jaitley Stadium",
    "Zayed Cricket Stadium": "Sheikh Zayed Stadium",
    "Sardar Patel Stadium": "Narendra Modi Stadium",
    "Punjab Cricket Association IS Bindra Stadium": "Punjab Cricket Association Stadium",
}
CITY_FIXES = {
    "Bangalore": "Bengaluru",
    "Navi Mumbai": "Mumbai",
}
VENUE_CITY_FILL = {
    "Dubai International Cricket Stadium": "Dubai",
    "Sharjah Cricket Stadium": "Sharjah",
}


def clean_matches(matches_path):
    m = pd.read_csv(matches_path)
    m["venue"] = m["venue"].str.split(",").str[0].str.strip()
    m["venue"] = m["venue"].replace(VENUE_FIXES)
    m["city"] = m["city"].fillna(m["venue"].map(VENUE_CITY_FILL))
    m["city"] = m["city"].replace(CITY_FIXES)
    return m


if __name__ == "__main__":
    m = clean_matches("data/processed/matches.csv")
    m.to_csv("data/processed/matches_clean.csv", index=False)
    print("venues:", m.venue.nunique())
    print("blank cities:", m.city.isna().sum())
