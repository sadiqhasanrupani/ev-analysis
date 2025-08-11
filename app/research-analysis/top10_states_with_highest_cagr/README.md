# Top 10 States with Highest CAGR - Analysis Dashboard

This Streamlit dashboard provides interactive visualizations and analysis of vehicle sales CAGR (Compound Annual Growth Rate) across Indian states from 2022 to 2024, with a focus on comparing total vehicle sales, EV sales, and non-EV sales.

## Features

- **Interactive Filters**: Select year range, states, and number of top states to display
- **Multiple Analysis Views**: Overview, Total Vehicle Sales, EV Sales, Non-EV Sales, and Comparison Analysis
- **Dynamic Visualizations**: Bar charts, scatter plots with regression, quadrant analysis, and more
- **Data Insights**: Key findings and interpretation for each analysis view

## Running the Dashboard

1. Make sure you have Streamlit installed:
   ```bash
   pip install streamlit
   ```

2. Run the Streamlit app:
   ```bash
   cd /path/to/ev-analysis/app/research-analysis/top10_states_with_highest_cagr
   streamlit run analysis.py
   ```

3. The dashboard will open in your default web browser.

## Dashboard Sections

### Overview
Provides a summary of CAGR trends across all categories with key metrics and insights.

### Total Vehicle Sales
Detailed analysis of states with the highest CAGR in total vehicle sales, including visualizations and insights.

### EV Sales
Analysis of states with the highest EV sales CAGR, showing growth patterns and emerging markets.

### Non-EV Sales
Analysis of traditional vehicle sales CAGR across states, with comparison between start and end years.

### Comparison Analysis
Correlation analysis between total vehicle CAGR and EV CAGR, including scatter plots with regression and quadrant analysis.

## Data Sources

The dashboard uses processed data from:
- `../../data/processed/ev_sales_by_state_enhanced_20250806.csv`

## Analysis Methodology

The dashboard calculates CAGR using the formula:
```
CAGR = ((End Value / Start Value) ^ (1 / Years)) - 1
```

For most analyses, the dashboard computes CAGR between 2022 and 2024 (2 years).
