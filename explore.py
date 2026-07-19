# explore.py — Week 1, Days 1–2: Data Download and Exploration
# Loads the USDA poverty Excel file, which contains multiple metadata header rows
# requiring a header offset (header=4) to reach the actual data. Filters out the
# state-level summary row (37000) and footnote rows, leaving a clean 100-county
# NC dataset with poverty rate and child poverty rate as the two key metrics.
# Renames columns from pandas auto-generated placeholders to readable field names.

import pandas as pd

# Load the USDA data — skip the 4 messy header rows, use row 4 as the header
df = pd.read_excel("data/usda_poverty.xlsx", header=4)

# See what columns are available
print("Columns:", df.columns.tolist())
print()

# See the first few rows
print(df.head())
print()

# Check which states are in the data
print("Unique state prefixes:", df["FIPS*"].astype(str).str[:2].unique())
print("Total rows in file:", len(df))
nc = df[df["FIPS*"].astype(str) != "37000"]

# Filter to North Carolina counties only
# The state-level row has FIPS ending in "000" — exclude it
# NC county FIPS codes all start with 37 and are NOT "37000"
nc = df[(df["FIPS*"].astype(str).str.startswith("37")) & 
        (df["FIPS*"].astype(str) != "37000")]

print(f"North Carolina counties: {len(nc)}")
print()

# Rename columns to something clean and usable
nc = nc.rename(columns={
    "FIPS*":         "fips",
    "Name":          "county",
    "RUC Code":      "ruc_code",
    "Percent":       "poverty_rate",      # All people in poverty %
    "Lower Bound":   "poverty_lower",
    "Upper Bound":   "poverty_upper",
    "Percent.1":     "child_poverty",     # Children 0-17 in poverty %
    "Lower Bound.1": "child_lower",
    "Upper Bound.1": "child_upper",
})

# Drop the empty columns
nc = nc[["fips", "county", "ruc_code", "poverty_rate", "child_poverty"]].copy()

print(nc.head(10))
print()
print("Columns we'll use:", nc.columns.tolist())

# Show basic statistics
print(nc.describe())
