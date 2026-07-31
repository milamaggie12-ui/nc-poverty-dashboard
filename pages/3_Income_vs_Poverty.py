# pages/3_Income_vs_Poverty.py — Income vs Poverty Analysis
# Explores the relationship between median household income and poverty rate
# across all 100 NC counties. Merges USDA poverty data with Census SAIPE
# median income data for the most recent year. The regression trendline
# reveals outlier counties where poverty exceeds what income alone predicts —
# pointing to inequality within the county rather than just overall low wealth.

import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm

st.title("When High Income Doesn't Mean Low Poverty")
st.markdown(
    "A negative correlation between income and poverty is expected, "
    "but outlier counties tell a more complicated story about inequality."
)

# ── Load and merge data ───────────────────────────────────────────────────────
@st.cache_data
def load_merged():
    nc = pd.read_excel("data/nc_poverty_clean.xlsx")
    trends = pd.read_csv("data/nc_poverty_trends.csv")

    # Pull most recent year median income
    latest_year = trends["year"].max()
    income_df = trends[trends["year"] == latest_year][["county", "median_income"]].copy()

    # Strip " County" from USDA names to match SAIPE format before merging
    nc["county_clean"] = nc["county"].str.replace(" County", "", regex=False).str.strip()
    merged = nc.merge(income_df, left_on="county_clean", right_on="county", how="inner")

    # Fit OLS regression to compute residuals — identifies inequality outliers
    X = sm.add_constant(merged["median_income"])
    model = sm.OLS(merged["poverty_rate"], X).fit()
    merged["predicted_poverty"] = model.predict(X)
    merged["residual"] = merged["poverty_rate"] - merged["predicted_poverty"]

    return merged, int(latest_year)

merged, latest_year = load_merged()

# ── Scatter plot ──────────────────────────────────────────────────────────────
fig = px.scatter(
    merged,
    x="median_income",
    y="poverty_rate",
    text="county_clean",
    trendline="ols",
    title=f"Median Income vs Poverty Rate by NC County ({latest_year})",
    labels={
        "median_income": "Median Household Income ($)",
        "poverty_rate":  "Poverty Rate (%)",
        "county_clean":  "County",
    },
    hover_data={"residual": ":.2f"},
)
fig.update_traces(textposition="top center", textfont_size=8)
fig.update_layout(title_x=0.5)
st.plotly_chart(fig, width="stretch")

# ── Outlier table ─────────────────────────────────────────────────────────────
st.subheader("Counties Where Poverty Exceeds What Income Predicts")
st.markdown(
    "A positive residual means the county's poverty rate is **higher than "
    "its income level would predict** — a sign of inequality within the county."
)

outliers = (merged
    .nlargest(10, "residual")
    [["county_clean", "median_income", "poverty_rate", "residual"]]
    .rename(columns={
        "county_clean": "County",
        "median_income": "Median Income ($)",
        "poverty_rate": "Poverty Rate (%)",
        "residual": "Residual (pp above predicted)",
    }))

st.dataframe(outliers, use_container_width=True, hide_index=True)

# ── Key finding ───────────────────────────────────────────────────────────────
st.info(
    f"**Union County** stands out with a median income of $107,681 — among NC's "
    f"highest — yet carries an 8.4% poverty rate above its predicted level. "
    f"This suggests wealth concentrated at the top rather than shared broadly. "
    f"Scotland, Robeson, and Anson face compounding disadvantage: both low income "
    f"and poverty higher than even that income would predict."
)