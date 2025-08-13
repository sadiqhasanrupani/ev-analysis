# EV Sales Seasonality Analysis - User Guide

## Introduction

The EV Sales Seasonality Analysis dashboard provides a comprehensive view of seasonal patterns in electric vehicle sales across India from 2022 to 2024. This analysis helps identify peak and low months for EV sales, enabling manufacturers, dealers, and policymakers to optimize their strategies based on these patterns.

## Accessing the Dashboard

1. Start the main dashboard hub:
   ```
   cd /mnt/data/projects/data-analyst/python-based/ev-analysis/ev-analysis
   uv run streamlit run app/main.py
   ```

2. Open the dashboard in your browser:
   - Local URL: http://localhost:8503
   - Or use the Network URL if accessing from another device

3. Navigate to the EV Sales Seasonality Analysis by either:
   - Clicking on the "EV Sales Seasonality Analysis" card on the main hub page
   - Selecting "EV Sales Seasonality Analysis" from the dropdown menu in the sidebar

## Using the Dashboard

### Filters
Located in the sidebar, these filters allow you to customize your analysis:

- **Years**: Select specific years to analyze (2022-2024)
- **States**: Filter by specific states or "All States"
- **Vehicle Categories**: Filter by 2-Wheelers, 4-Wheelers, or "All Categories"
- **Calendar vs. Fiscal Year**: Toggle between calendar year and fiscal year (Apr-Mar) views

### Key Performance Indicators (KPIs)
At the top of the dashboard, you'll find four key metrics:

- **Peak Sales Month**: Month with highest EV sales and percentage above average
- **Low Sales Month**: Month with lowest EV sales and percentage below average
- **Peak-to-Low Ratio**: Measure of seasonality intensity (higher ratio = stronger seasonality)
- **Sales Volatility**: Measure of month-to-month variability (higher % = more unpredictable)

### Visualizations

1. **Monthly Sales Distribution**: Bar chart showing sales for each month, with peak and low months highlighted
2. **Monthly Sales Heatmap**: Heat map showing sales patterns across years and months
3. **Seasonality Radar**: Radar chart visualizing how each month compares to the average
4. **Yearly Comparison**: Line chart comparing monthly sales patterns across different years

### Insights Section
The bottom section provides data-driven insights about:
- Detailed analysis of seasonal patterns
- Business implications for manufacturers and dealers
- Recommended strategies based on the identified patterns

## Key Features

- **Interactive Filters**: Dynamically update all visualizations and metrics
- **Comparative Analysis**: Compare seasonal patterns across years
- **Market Segmentation**: Analyze different vehicle categories separately
- **Regional Insights**: Filter by states to understand regional variations
- **Business Recommendations**: Actionable insights for inventory, marketing, and staffing

## Data Sources

This analysis is based on processed EV sales data from 2022 to 2024, which includes:
- Monthly sales volumes for electric vehicles across different states in India
- Categorization by vehicle types (2-Wheelers, 4-Wheelers, etc.)
- Regional and state-level breakdowns

## Troubleshooting

If you encounter any issues:

1. Ensure all required Python packages are installed
2. Check that the data files exist in the expected locations
3. Verify that the streamlit server is running correctly
4. Try refreshing the browser if visualizations don't load properly

For any technical issues, please refer to the project documentation or contact the development team.
