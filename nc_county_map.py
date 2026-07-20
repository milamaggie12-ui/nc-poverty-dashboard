# nc_county_map.py 
# Creates an interactive county-level choropleth map of North Carolina showing
# poverty rate by county. Uses Plotly's built-in US county GeoJSON matched to
# counties via 5-digit FIPS codes. Color intensity (light to dark red) reflects
# poverty rate — darker counties have higher poverty. County borders are drawn
# in white for visual separation. Map is zoomed to NC's actual lat/lon bounds
# so the full US base map is hidden and NC fills the frame. The slight east-west
# tilt is geographically accurate — NC's western edge sits ~1 degree south of
# its eastern edge in real coordinates.

import plotly.express as px
import pandas as pd

# Load the cleaned NC poverty dataset
df = pd.read_excel("data/nc_poverty_clean.xlsx")
nc = df  # Assign to nc for clarity

# Build the choropleth — each county is matched to its shape via FIPS code
# GeoJSON source: Plotly's hosted US county boundaries dataset
fig = px.choropleth(
    nc,
    geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
    locations="fips",                  # FIPS code links each row to its county shape
    color="poverty_rate",              # Color encodes overall poverty rate
    scope="usa",                       # Restricts base map to US
    color_continuous_scale="Reds",     # Light = low poverty, dark red = high poverty
    title="Poverty Rate Across North Carolina Counties",
)

# Add white county borders for visual separation between adjacent counties
fig.update_traces(
    marker_line_width=0.5,
    marker_line_color="white",
)

# Zoom to NC's geographic bounds and hide the surrounding US base map
fig.update_geos(
    fitbounds="locations",             # Auto-fits the map frame to NC's extent
    visible=False,                     # Hides states, coastlines, and base map
    lataxis_range=[33.5, 36.8],        # NC latitude bounds (south to north)
    lonaxis_range=[-84.5, -75.3],      # NC longitude bounds (west to east)
)

# Remove surrounding whitespace and center the title
fig.update_layout(
    height=600,
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    title_x=0.5,
)

fig.show()