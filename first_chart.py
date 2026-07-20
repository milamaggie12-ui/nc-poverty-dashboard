# first_chart.py 
# Loads the cleaned NC poverty dataset produced by explore.py and creates
# an interactive bar chart ranking all 100 counties by overall poverty rate.
# Iteratively developed from a basic color-scaled bar chart to a two-tone
# chart highlighting Cumberland County in red against all other counties in blue.
# Legend styled with plain-English labels, vertical orientation, and a bordered
# box positioned outside the chart area to avoid overlapping the bars.

import pandas as pd
import plotly.express as px

# Load and filter to NC
df = pd.read_excel("data/nc_poverty_clean.xlsx")
nc = df # Assign it to nc dataframe for clarity

# Sort by poverty rate (highest to lowest)
nc = nc.sort_values("poverty_rate", ascending=False)

# Add a column to highlight Cumberland County
nc["is_home"] = nc["county"].apply(
    lambda x: "Cumberland County" if "Cumberland" in str(x) else "Other"
)

# Create bar chart
fig = px.bar(
    nc,
    x="county",
    y="poverty_rate",
    labels={"poverty_rate": "Poverty Rate (%)", "county": "County"},
    color="is_home",
    color_discrete_map={"Cumberland County": "#E24B4A", "Other": "#85B7EB"},
    title="Poverty Rate by County — Cumberland County Highlighted"
)

# Tag each county as Cumberland or other — drives the two-tone color mapping in the chart
nc["is_home"] = nc["county"].apply(
    lambda x: "Cumberland (your county)" if "Cumberland" in str(x) else "All other counties"
)

fig = px.bar(
    nc,
    x="county",
    y="poverty_rate",
    labels={"poverty_rate": "Poverty Rate (%)", "county": "County"},
    color="is_home",
    color_discrete_map={
        "Cumberland (your county)": "#E24B4A",
        "All other counties":       "#85B7EB",
    },
    title="Poverty Rate by County — Cumberland County Highlighted",
)
# fig.show()
fig.update_layout(
    legend=dict(
        title="County",
        orientation="v",        # vertical legend
        x=1.02,                 # position just outside the right edge of the chart
        y=1,                    # align to top
        bgcolor="white",
        bordercolor="#cccccc",
        borderwidth=1,
    ),
    xaxis_tickangle=-45,
    height=600,
)
fig.show()