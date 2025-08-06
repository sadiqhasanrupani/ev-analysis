import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import os


# Define functions
def calculate_yoy(row):
    try:
        if pd.notna(row["FY 2023"]) and pd.notna(row["FY 2024"]):
            return (row["FY 2024"] - row["FY 2023"]) / row["FY 2023"] * 100
        return pd.NA
    except:
        return pd.NA


def format_with_check(val, format_str):
    if isinstance(val, str):
        return val
    else:
        return format_str.format(val)


# Streamlit app layout
st.set_page_config(page_title="EV 2-Wheeler Dashboard", layout="wide")

st.title("🚀 India's Electric 2-Wheeler Market (FY 2023 vs FY 2024)")

# Load data
# Fix the relative path to point to the correct location
data_path = os.path.join(
  os.path.dirname(__file__),
  "..", "..", "..", "data", "processed", "ev_sales_by_makers_cleaned_20250806.csv"
)
data_path = os.path.abspath(data_path)
df = pd.read_csv(data_path, parse_dates=["date"])

# Data Transformation
# Filter for 2-wheelers
two_wheelers = df[df["vehicle_category"] == "2-Wheelers"].copy()

# Extract fiscal year
two_wheelers["fiscal_year"] = two_wheelers["date"].apply(
    lambda x: f"FY {x.year}" if x.month < 4 else f"FY {x.year + 1}"
)

# Filter for fiscal years
filtered = two_wheelers[two_wheelers["fiscal_year"].isin(["FY 2023", "FY 2024"])]

# Group sales
yearly_sales = (
    filtered.groupby(["maker", "fiscal_year"])["electric_vehicles_sold"]
    .sum()
    .reset_index()
)

# Get top and bottom performers
top_bottom_dict = {}
for year in ["FY 2023", "FY 2024"]:
    year_data = yearly_sales[yearly_sales["fiscal_year"] == year].sort_values(
        "electric_vehicles_sold", ascending=False
    )
    top_bottom_dict[f"{year}_top"] = year_data.head(3)
    top_bottom_dict[f"{year}_bottom"] = year_data.tail(3)

"""
  Plot the chart using plotly
"""
fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "Top 3 Manufacturers - FY 2023",
        "Top 3 Manufacturers - FY 2024",
        "Bottom 3 Manufacturers - FY 2023",
        "Bottom 3 Manufacturers - FY 2024",
    ),
    vertical_spacing=0.12,
    horizontal_spacing=0.1,
)

top_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
bottom_colors = ["#d62728", "#9467bd", "#8c564b"]

# Top 3 FY 2023
for i, (_, row) in enumerate(top_bottom_dict["FY 2023_top"].iterrows()):
    fig.add_trace(
        go.Bar(
            x=[row["maker"]],
            y=[row["electric_vehicles_sold"]],
            marker_color=top_colors[i],
            name=row["maker"],
        ),
        row=1,
        col=1,
    )

# Top 3 FY 2024
for i, (_, row) in enumerate(top_bottom_dict["FY 2024_top"].iterrows()):
    fig.add_trace(
        go.Bar(
            x=[row["maker"]],
            y=[row["electric_vehicles_sold"]],
            marker_color=top_colors[i],
            name=row["maker"],
        ),
        row=1,
        col=2,
    )

# Bottom 3 FY 2023
for i, (_, row) in enumerate(top_bottom_dict["FY 2023_bottom"].iterrows()):
    fig.add_trace(
        go.Bar(
            x=[row["maker"]],
            y=[row["electric_vehicles_sold"]],
            marker_color=bottom_colors[i],
            name=row["maker"],
        ),
        row=2,
        col=1,
    )

# Bottom 3 FY 2024
for i, (_, row) in enumerate(top_bottom_dict["FY 2024_bottom"].iterrows()):
    fig.add_trace(
        go.Bar(
            x=[row["maker"]],
            y=[row["electric_vehicles_sold"]],
            marker_color=bottom_colors[i],
            name=row["maker"],
        ),
        row=2,
        col=2,
    )

fig.update_layout(
    title="<b>India's Electric 2-Wheeler Market: Leaders & Laggards</b>",
    height=800,
    width=1000,
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

"""
  Show table with YoY Change
"""
# Create combined summary
all_highlighted = pd.concat(
    [
        top_bottom_dict["FY 2023_top"].assign(position="Top 3"),
        top_bottom_dict["FY 2024_top"].assign(position="Top 3"),
        top_bottom_dict["FY 2023_bottom"].assign(position="Bottom 3"),
        top_bottom_dict["FY 2024_bottom"].assign(position="Bottom 3"),
    ]
)

# Pivot
pivot_table = all_highlighted.pivot_table(
    index=["position", "maker"],
    columns="fiscal_year",
    values="electric_vehicles_sold",
    aggfunc="sum",
).reset_index()

pivot_table["YoY Change"] = pivot_table.apply(calculate_yoy, axis=1)
pivot_table = pivot_table.sort_values(["position", "FY 2024"], ascending=[True, False])
formatted_pivot = pivot_table.fillna("-")

# Display in Streamlit
st.markdown("### 📊 Detailed Comparison Table")
st.dataframe(
    formatted_pivot.style.format(
        {
            "FY 2023": lambda x: format_with_check(x, "{:,.0f}"),
            "FY 2024": lambda x: format_with_check(x, "{:,.0f}"),
            "YoY Change": lambda x: format_with_check(x, "{:+.1f}%"),
        }
    ),
    use_container_width=True,
)


"""
  Annotations
"""
st.markdown(
    """
> **Insights:**
> - 🚀 **Top Performer**: OLA ELECTRIC led both years; TVS gained big in FY 2024.
> - 🐌 **Struggling Makers**: JOY E-BIKE and PURE EV stayed in the bottom.
"""
)
