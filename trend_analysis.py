# trend_analysis.py —  Historical Poverty Trends (All NC Counties)
# Downloads SAIPE fixed-width text files directly from the Census Bureau for
# each year in the specified range, parses them using official column positions
# from the Census README.TXT, and combines them into a single long-format
# dataframe (1 row per county per year). On first run, downloads all years and
# saves to data/nc_poverty_trends.csv. On subsequent runs, loads from the saved
# CSV to avoid redundant Census requests. Produces four charts: statewide trend,
# multi-county comparison, racial disparity bar chart, and a child vs. overall
# poverty scatter plot — all using real Census SAIPE data.

import pandas as pd
import plotly.express as px
import urllib.request
import os

# ── Configuration ─────────────────────────────────────────────────────────────
YEARS = range(2015, 2025)          # 2015 through 2024 inclusive
TRENDS_CACHE = "data/nc_poverty_trends.csv"  # saved after first download

# Fixed-width column positions from Census SAIPE README.TXT (0-indexed)
COLSPECS = [
    (0,   2),   # state_fips
    (3,   6),   # county_fips
    (34,  38),  # poverty_all_pct
    (76,  80),  # child_poverty_pct
    (133, 139), # median_income
    (193, 238), # name
]

COLNAMES = [
    "state_fips", "county_fips",
    "poverty_all_pct", "child_poverty_pct",
    "median_income", "name",
]

# ── Data loading ───────────────────────────────────────────────────────────────
def fetch_saipe_year(year):
    """Download and parse the Census SAIPE NC file for a single year.
    Returns a dataframe of 100 county rows with poverty and income metrics."""
    url = (f"https://www2.census.gov/programs-surveys/saipe/datasets/"
           f"{year}/{year}-state-and-county/est{str(year)[2:]}-nc.txt")
    print(f"  Fetching {year} from Census...")

    # Download raw file locally before parsing
    local_path = f"data/est{str(year)[2:]}-nc.txt"
    try:
        urllib.request.urlretrieve(url, local_path)
    except Exception as e:
        print(f"  Failed {year}: {e}")
        return None

    # Parse fixed-width format using Census README column positions
    df = pd.read_fwf(local_path, colspecs=COLSPECS, names=COLNAMES, header=None)

    # Remove state-level summary row (county_fips == 0), keep only counties
    df = df[df["county_fips"] != 0].copy()

    # Strip " County" suffix and whitespace from name for cleaner labels
    df["name"] = df["name"].str.replace(" County", "", regex=False).str.strip()
    df = df.rename(columns={"name": "county"})

    # Tag each row with its year for the combined long-format dataframe
    df["year"] = year

    return df


def load_trends():
    """Load trends data from cache if available, otherwise download all years."""
    if os.path.exists(TRENDS_CACHE):
        # Cache exists — skip Census downloads entirely
        print(f"Loading cached data from {TRENDS_CACHE}")
        return pd.read_csv(TRENDS_CACHE)

    # No cache — download all years from Census and save
    print("No cache found — downloading from Census Bureau...")
    frames = []
    for year in YEARS:
        df_year = fetch_saipe_year(year)
        if df_year is not None:
            frames.append(df_year)

    trends = pd.concat(frames, ignore_index=True)
    trends.to_csv(TRENDS_CACHE, index=False)
    print(f"\nSaved {len(trends)} rows to {TRENDS_CACHE}")
    return trends


# ── Load data ─────────────────────────────────────────────────────────────────
trends = load_trends()
print(f"Loaded {len(trends)} rows ({trends['year'].nunique()} years × 100 counties)\n")

# Most recent year snapshot — used in scatter plot
nc_latest = trends[trends["year"] == trends["year"].max()].copy()
latest_year = trends["year"].max()

# ── Chart 1: NC statewide average trend ──────────────────────────────────────
# Aggregate to yearly averages across all 100 counties for both metrics
nc_avg = (trends
          .groupby("year")[["poverty_all_pct", "child_poverty_pct"]]
          .mean()
          .reset_index())

fig1 = px.line(
    nc_avg,
    x="year",
    y=["poverty_all_pct", "child_poverty_pct"],
    title="NC Statewide Poverty Rate Trend (2015–2024)",
    labels={
        "year":     "Year",
        "value":    "Poverty Rate (%)",
        "variable": "Metric",
    },
    markers=True,
    color_discrete_map={
        "poverty_all_pct":   "#e74c3c",  # red — overall poverty
        "child_poverty_pct": "#e67e22",  # orange — child poverty
    },
)
fig1.update_layout(title_x=0.5)
fig1.show()

# ── Chart 2: Multi-county trend comparison ────────────────────────────────────
# Compares selected counties over time — edit list to highlight any counties
HIGHLIGHT_COUNTIES = ["Cumberland", "Robeson", "Wake", "Mecklenburg", "Union"]

county_trends = trends[trends["county"].isin(HIGHLIGHT_COUNTIES)]

fig2 = px.line(
    county_trends,
    x="year",
    y="poverty_all_pct",
    color="county",
    title="Poverty Rate Trend by County (2015–2024)",
    labels={
        "year":            "Year",
        "poverty_all_pct": "Poverty Rate (%)",
        "county":          "County",
    },
    markers=True,
)
fig2.update_layout(title_x=0.5)
fig2.show()

# ── Chart 3: Racial disparity bar chart ──────────────────────────────────────
# Statewide racial poverty rates — sourced from ACS 2024 (not in SAIPE)
# SAIPE does not publish racial breakdowns at county level; ACS is the source
racial_data = pd.DataFrame({
    "Race/Ethnicity": ["White", "Black", "Latino", "American Indian", "Asian"],
    "poverty_rate":   [9.1, 18.9, 20.2, 17.1, 8.5],  # ACS 2024, NC statewide
})

fig3 = px.bar(
    racial_data,
    x="Race/Ethnicity",
    y="poverty_rate",
    title="Poverty Rate by Race in North Carolina (2024)",
    labels={"poverty_rate": "Poverty Rate (%)"},
    color="poverty_rate",
    color_continuous_scale="Reds",
)
fig3.update_layout(title_x=0.5)
fig3.show()

# ── Chart 4: Child vs. overall poverty scatter (most recent year) ─────────────
# Each dot is one county — shows that child poverty exceeds overall poverty
# in every NC county; counties above the diagonal have the largest gap
fig4 = px.scatter(
    nc_latest,
    x="poverty_all_pct",
    y="child_poverty_pct",
    text="county",
    title=f"Child Poverty vs Overall Poverty by NC County ({latest_year})",
    labels={
        "poverty_all_pct":   "Overall Poverty Rate (%)",
        "child_poverty_pct": "Child Poverty Rate (%)",
    },
)
fig4.update_traces(textposition="top center", textfont_size=8)
fig4.update_layout(title_x=0.5)
fig4.show()