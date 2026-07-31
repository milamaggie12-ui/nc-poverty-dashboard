# NC Poverty Data Dashboard 📊

An interactive data science dashboard visualizing poverty and economic
inequality across all 100 counties of North Carolina, built with real
Census Bureau and USDA data.

## 🔗 Live Dashboard
[Insert Streamlit Cloud URL after deployment]

**GitHub:** github.com/milamaggie12-ui/nc-poverty-dashboard

---

## About This Project

This dashboard began as a question: what does poverty actually look like
across North Carolina — county by county, year by year — and can the
patterns be made visible to anyone, not just researchers with access to
raw federal datasets?

Built during Summer 2026 while completing Andrew Ng's AI Python for
Beginners course (DeepLearning.AI), this project applies data science
methods to a real problem in the home community: Cumberland County, NC.
Rather than working through tutorial exercises, the goal was to build
something deployable, publicly accessible, and analytically meaningful
using the same tools professional data scientists use: Python, pandas,
Plotly, and Streamlit, with real Census Bureau and USDA data.

The result is a multi-page web application that answers six analytical
questions about NC poverty with interactive visualizations, a regression-
based inequality analysis, and findings that go beyond what the raw data
makes visible on its own.

---

## Dashboard Pages

**Home** — NC poverty overview with an interactive choropleth map and
county rankings bar chart. Any county selectable from the sidebar;
Cumberland County highlighted by default.

**County Map** — Full-screen choropleth map of all 100 NC counties
colored by poverty rate, with hover tooltips showing county-level detail.

**Poverty Trends (2015–2024)** — Four-tab analysis of historical data
downloaded programmatically from the Census Bureau SAIPE program.
Includes statewide trend lines, an interactive multi-county comparison
(user-selectable via multiselect widget), a racial disparity bar chart,
and a child vs. overall poverty scatter plot for the most recent year.

**When High Income Doesn't Mean Low Poverty** — OLS regression analysis
identifying counties where poverty significantly exceeds predictions based
on median income as a signal of within-county inequality. Includes
a ranked outlier table and the Union County paradox finding.

---

## Key Findings

- NC's average poverty rate is **15.4%**, above the national average
- **Child poverty exceeds overall poverty in all 100 NC counties** —
  the gap averages +6.4 percentage points statewide, without exception
- **Scotland County (28.6%)** and **Robeson County (27.7%)** have the
  highest poverty rates in NC; **Camden County (8.1%)** the lowest
- **Cumberland County (15.3%)** sits at the state average, but is
  surrounded by some of NC's most economically distressed counties —
  Scotland, Robeson, Hoke, Bladen, and Sampson all exceed 18%
- **Racial disparities are large and structural** — Latino (20.2%) and
  Black (18.9%) residents face poverty rates more than double that of
  white residents (9.1%)
- **Union County paradox** — NC's highest-income county ($107,681
  median) still carries a poverty rate above its predicted level,
  consistent with within-county income inequality rather than overall
  low wealth
- NC poverty fell by ~3 percentage points from 2015–2024, but
  COVID-19 temporarily reversed that progress in 2020

---

## Technical Approach

**Data pipeline:**
Raw federal data (USDA Excel, Census fixed-width .txt) → pandas
cleaning and merging → OLS regression (statsmodels) → Plotly
interactive charts → Streamlit multi-page deployment

**Key engineering decisions:**
- `pd.read_fwf()` with exact column positions from the Census SAIPE
  README to parse fixed-width files — not regex, not assumptions
- CSV caching layer so SAIPE files download once from Census and load
  instantly on all subsequent runs (`@st.cache_data`)
- OLS residual analysis to identify inequality outliers beyond what
  income predicts — shifts the question from "how poor?" to "how equal?"
- Multi-page Streamlit architecture using the `pages/` folder pattern
- Fully documented commit history on GitHub

**Data sources:**
- US Census Bureau — SAIPE 2015–2024, programmatically downloaded
- American Community Survey (ACS) — 1-Year Estimate 2024, Source: https://data.census.gov/table/ACSST1Y2024.S1701?g=040XX00US37
- USDA Economic Research Service — County-Level Poverty Estimates

---

## How to Run Locally

```bash
git clone https://github.com/milamaggie12-ui/nc-poverty-dashboard.git
cd nc-poverty-dashboard
pip install -r requirements.txt
streamlit run app.py
```

On first run, the Poverty Trends page downloads 10 years of SAIPE data
from the Census Bureau (~30 seconds). All subsequent runs load from the
cached CSV in `data/`.

---

## Project Structure

```
nc-poverty-dashboard/
├── app.py                         # Home — map + bar chart + findings
├── pages/
│   ├── 1_County_Map.py            # Full-screen choropleth map
│   ├── 2_Trend_Analysis.py        # Historical trends + racial disparities
│   └── 3_Income_vs_Poverty.py     # Inequality regression analysis
├── data/
│   ├── usda_poverty.xlsx          # USDA source data
│   ├── nc_poverty_clean.xlsx      # Cleaned NC dataset
│   └── nc_poverty_trends.csv      # SAIPE 2015–2024 (generated on first run)
├── requirements.txt
└── README.md
```

---

## Author

**Magdalena Milanova**
Rising Senior · Cross Creek High School /
Fayetteville State University Early College · Fayetteville, NC

Intended major: B.S. Data Science
Class of 2031