# app.py — NC Poverty Dashboard (Main Application)
# Streamlit dashboard visualizing poverty and economic inequality across
# all 100 North Carolina counties. Loads and cleans USDA poverty data on
# first run (cached thereafter), renders an interactive choropleth map and
# a ranked bar chart with Cumberland County highlighted, and summarizes
# key statewide findings. Run locally with: streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NC Poverty Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── GeoJSON loading ───────────────────────────────────────────────────────────
@st.cache_data
def load_geojson():
    with open("data/counties.geojson") as f:
        return json.load(f)

counties_geojson = load_geojson()

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Load and clean USDA poverty Excel file.
    Result is cached by Streamlit so cleaning only runs once per session."""

    # Skip 4 metadata rows at top of Excel file; row 4 contains real headers
    df = pd.read_excel("data/usda_poverty.xlsx", header=4)

    # Keep only NC counties: FIPS starts with 37, exclude state summary row 37000
    nc = df[
        (df["FIPS*"].astype(str).str.startswith("37")) &
        (df["FIPS*"].astype(str) != "37000")
    ]

    # Rename auto-generated pandas column names to readable field names
    nc = nc.rename(columns={
        "FIPS*":         "fips",
        "Name":          "county",
        "RUC Code":      "ruc_code",
        "Percent":       "poverty_rate",    # Overall poverty rate %
        "Lower Bound":   "poverty_lower",   # 90% CI lower bound
        "Upper Bound":   "poverty_upper",   # 90% CI upper bound
        "Percent.1":     "child_poverty",   # Children 0-17 poverty rate %
        "Lower Bound.1": "child_lower",
        "Upper Bound.1": "child_upper",
    })

    # Retain only columns needed for dashboard charts
    nc = nc[["fips", "county", "ruc_code", "poverty_rate", "child_poverty"]].copy()

    return nc

nc = load_data()

# ── Derived metrics (computed once, reused across widgets) ────────────────────
nc_avg_poverty  = nc["poverty_rate"].mean()
nc_avg_child    = nc["child_poverty"].mean()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Poverty Across North Carolina")
st.markdown(
    "An interactive analysis of poverty and economic inequality "
    "across NC's 100 counties"
)
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Filters")

# Dropdown to highlight any county across all charts
county_list = sorted(nc["county"].unique())
default_idx = county_list.index("Cumberland County") \
    if "Cumberland County" in nc["county"].values else 0

selected_county = st.sidebar.selectbox(
    "Select a county to highlight",
    options=county_list,
    index=default_idx,
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Sources**")
st.sidebar.markdown("- US Census Bureau (SAIPE)")
st.sidebar.markdown("- USDA Economic Research Service")
st.sidebar.markdown("- NC Office of State Budget & Management")
st.sidebar.markdown("---")
st.sidebar.markdown("Built by Magdalena Milanova | Summer 2026")

# ── KPI metrics row ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("NC Average Poverty Rate", f"{nc_avg_poverty:.1f}%")

with col2:
    # Pull selected county's rate dynamically from the dataframe
    selected_rate = nc[nc["county"] == selected_county]["poverty_rate"].values[0]
    st.metric(f"{selected_county}", f"{selected_rate:.1f}%")

with col3:
    # NC child poverty — sourced from Census SAIPE, displayed as context metric
    st.metric("NC Child Poverty Rate", f"{nc_avg_child:.1f}%")

# ── Choropleth map ────────────────────────────────────────────────────────────
st.subheader("Poverty Rate by County")

# Each county matched to its geographic shape via 5-digit FIPS code
fig_map = px.choropleth(
    nc,
    geojson=counties_geojson,
    locations="fips",
    featureidkey="id",
    color="poverty_rate",
    scope="usa",
    color_continuous_scale="Reds",       # Darker red = higher poverty
    hover_name="county",                 # Show county name on hover
    hover_data={"poverty_rate": ":.1f",  # Format hover values to 1 decimal
                "child_poverty": ":.1f",
                "fips": False},          # Hide raw FIPS from hover tooltip
    labels={"poverty_rate": "Poverty Rate (%)"},
    title="Poverty Rate Across North Carolina Counties",
)

# White county borders improve readability between adjacent counties
fig_map.update_traces(marker_line_width=0.5, marker_line_color="white")

# Zoom to NC bounds and hide surrounding US base map
fig_map.update_geos(
    fitbounds="locations",
    visible=False,
    lataxis_range=[33.5, 36.8],   # NC latitude: south to north
    lonaxis_range=[-84.5, -75.3], # NC longitude: west to east
)

fig_map.update_layout(
    height=600,
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_x=0.5,
)

st.plotly_chart(fig_map, width="stretch")

# ── Bar chart ─────────────────────────────────────────────────────────────────
st.subheader("All Counties Ranked")

# Sort highest to lowest so the bar chart reads left to right by severity
nc_sorted = nc.sort_values("poverty_rate", ascending=False).copy()

# Tag each county for two-tone coloring — drives color mapping in the chart
nc_sorted["is_home"] = nc_sorted["county"].apply(
    lambda x: "Cumberland (your county)" if "Cumberland" in str(x)
    else "All other counties"
)

fig_bar = px.bar(
    nc_sorted,
    x="county",
    y="poverty_rate",
    color="is_home",
    color_discrete_map={
        "Cumberland (your county)": "#E24B4A",
        "All other counties":       "#85B7EB",
    },
    hover_name="county",
    hover_data={"poverty_rate": ":.1f", "child_poverty": ":.1f", "is_home": False},
    labels={"poverty_rate": "Poverty Rate (%)", "county": "County"},
    title="Poverty Rate by County — Cumberland County Highlighted",
)

fig_bar.update_layout(
    legend=dict(
        title="County",
        orientation="v",
        x=1.02,          # Position legend just outside right edge of chart
        y=1,
        bgcolor="white",
        bordercolor="#cccccc",
        borderwidth=1,
    ),
    xaxis_tickangle=-45,
    height=600,
)

st.plotly_chart(fig_bar, width="stretch")

# ── Key findings ──────────────────────────────────────────────────────────────
st.subheader("Key Findings")

# Dynamically compute Cumberland comparison rather than hardcoding
cumberland_rate = nc[nc["county"] == selected_county]["poverty_rate"].values[0]
diff = cumberland_rate - nc_avg_poverty
direction = "above" if diff > 0 else "below"

st.markdown(f"""
- **{nc_avg_poverty:.1f}%** of North Carolinians live in poverty (USDA data)
- **Child poverty is higher** at {nc_avg_child:.1f}% — affecting hundreds of thousands of NC children
- **Racial disparities persist** — poverty rates for Black (18.9%) and Latino (20.2%)
  residents are more than double the rate for white residents (9.1%)
- **{selected_county}** at {cumberland_rate:.1f}% is {abs(diff):.1f} percentage points {direction} the state average
- **Income and poverty are negatively correlated** across NC counties — 
  but the relationship isn't perfect. Several counties have poverty rates 
  significantly higher than their income level would predict.
- **Union County** is the starkest example: with a median income of $107,681 
  — among NC's highest — it still carries an 8.4% poverty rate, suggesting 
  wealth concentrated at the top rather than shared broadly.
- **Scotland, Robeson, and Anson** counties face compounding disadvantage — 
  both low income and poverty rates higher than even their income would predict.
""")