# EV Analysis Dashboard Hub

This is a centralized navigation hub for all electric vehicle market analyses in the project. The dashboard provides easy access to various analyses and visualizations related to the Indian EV market from 2022 to 2024.

## Features

- **Central Navigation Hub**: Access all analysis dashboards from a single interface
- **Interactive Visualizations**: Explore data through dynamic charts and graphs
- **Multiple Analysis Views**: From CAGR analysis to regional trends
- **Responsive Design**: Adapts to different screen sizes

## Available Analyses

1. **Top 10 States with Highest CAGR**
   - Analysis of states with highest compound annual growth rate for total vehicles, EVs, and non-EVs

2. **Vehicle Analysis by State**
   - State-wise breakdown of vehicle sales patterns and trends

3. **EV Penetration Decline Analysis**
   - Investigation into states showing a decline in EV market penetration

4. **Top vs Bottom 2-Wheeler Makers**
   - Comparative analysis of top and bottom performing two-wheeler manufacturers

## Running the Dashboard

1. Navigate to the project root directory:
   ```bash
   cd /mnt/data/projects/data-analyst/python-based/ev-analysis/ev-analysis
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

3. The dashboard will open in your default web browser.

## Technical Implementation

The dashboard hub is built using Streamlit and dynamically loads analysis modules when selected. It uses a modular approach where each analysis is contained in its own module with a standard interface, making it easy to add new analyses in the future.

### Adding a New Analysis

To add a new analysis to the dashboard hub:

1. Create your analysis module with a `main()` function that renders the Streamlit UI
2. Add an entry to the `analyses` list in `app/main.py` with:
   - `name`: Display name for the analysis
   - `description`: Brief description of what the analysis shows
   - `path`: Relative path to the analysis module from the app directory
   - `icon`: Emoji icon to represent the analysis

## Data Sources

All analyses use data from the project's data directory, including:
- `data/processed/ev_sales_by_state_enhanced_20250806.csv`
- `data/processed/ev_manufacturer_performance_20250809.csv`
- And other processed datasets
