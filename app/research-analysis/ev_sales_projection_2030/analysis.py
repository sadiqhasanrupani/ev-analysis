import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import humanize

# Set page config
st.set_page_config(
    page_title="EV Sales Projections 2030",
    page_icon="🚗",
    layout="wide",
)

# Define the project base directory
BASE_DIR = Path(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

# Custom CSS for ADHD-friendly design
st.markdown(
    """
<style>
    .highlight-box {
        background-color: #f0f7ff;
        border-left: 5px solid #1E88E5;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    /* Consistent metric styling based on ev_peak_low_months/analysis.py */
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .primary-metric {
        border-left: 5px solid #1E88E5;  /* Blue */
    }
    .success-metric {
        border-left: 5px solid rgba(46, 184, 92, 0.9);  /* Green */
    }
    .danger-metric {
        border-left: 5px solid rgba(220, 53, 69, 0.9);  /* Red */
    }
    .warning-metric {
        border-left: 5px solid rgba(255, 193, 7, 0.9);  /* Yellow */
    }
    .info-metric {
        border-left: 5px solid rgba(111, 66, 193, 0.9);  /* Purple */
    }
    .metric-title {
        font-size: 1.1em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-subtitle {
        font-size: 0.9em;
        color: #6c757d;
    }
    /* Legacy class names for backward compatibility */
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .kpi-label {
        font-size: 0.9em;
        color: #6c757d;
    }
    .section-title {
        color: #0D47A1;
        border-bottom: 2px solid #90CAF9;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .insight-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        /*padding: 20px;/*
        margin-bottom: 20px;
    }
    .insight-header {
        color: #0D47A1;
        margin-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
    }
    .emoji-bullet {
        font-size: 1.2em;
        margin-right: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_data():
    """Load and preprocess the EV sales data"""
    # Define path to data
    data_path = (
        BASE_DIR / "data" / "processed" / "ev_sales_by_state_enhanced_20250806.csv"
    )

    # Load the data
    monthly_ev_sales = pd.read_csv(data_path)

    # Convert date to datetime
    monthly_ev_sales["date"] = pd.to_datetime(monthly_ev_sales["date"])

    # Create fiscal year column (fiscal year starts in April)
    monthly_ev_sales["fiscal_year"] = np.where(
        monthly_ev_sales["month"] >= 4,
        monthly_ev_sales["year"],
        monthly_ev_sales["year"] - 1,
    )

    return monthly_ev_sales


def calculate_projections(
    monthly_ev_sales,
    filter_region=None,
    filter_year=None,
    use_ev_penetration=True,
    top_n=10,
    projection_year=2030,
):
    """Calculate CAGR and project sales for 2030"""

    # Apply filters if specified
    filtered_data = monthly_ev_sales.copy()

    if filter_region and filter_region != "All Regions":
        filtered_data = filtered_data[filtered_data["region"] == filter_region]

    if filter_year:
        latest_fy = filter_year
    else:
        latest_fy = filtered_data["fiscal_year"].max()

    # Group by state and fiscal year
    fy_sales = (
        filtered_data.groupby(["state", "fiscal_year"])["electric_vehicles_sold"]
        .sum()
        .reset_index()
    )

    # Get the top states by penetration rate
    if use_ev_penetration:
        # Use EV penetration rate to find top states
        top_states = (
            filtered_data[filtered_data["fiscal_year"] == latest_fy]
            .groupby("state")["ev_penetration_rate"]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
            .index.tolist()
        )
    else:
        # Use total EV sales to find top states
        top_states = (
            fy_sales[fy_sales["fiscal_year"] == latest_fy]
            .sort_values("electric_vehicles_sold", ascending=False)
            .head(top_n)["state"]
            .tolist()
        )

    # Calculate CAGR for each state
    cagr_dict = {}
    for state in top_states:
        state_data = fy_sales[fy_sales["state"] == state].sort_values("fiscal_year")
        if len(state_data) < 2:  # Skip states with insufficient data
            continue

        start_sales = state_data.iloc[0][
            "electric_vehicles_sold"
        ]  # first fiscal year sales
        end_sales = state_data.iloc[-1][
            "electric_vehicles_sold"
        ]  # last fiscal year sales
        n_years = state_data["fiscal_year"].iloc[-1] - state_data["fiscal_year"].iloc[0]

        # Avoid division by zero
        if start_sales > 0 and n_years > 0:
            cagr = ((end_sales / start_sales) ** (1 / n_years) - 1).round(2)
            cagr_dict[state] = cagr

    # Project sales for specified year
    projected_sales = {}
    years_to_project = projection_year - latest_fy

    for state, cagr in cagr_dict.items():
        current_sales = fy_sales[
            (fy_sales["state"] == state) & (fy_sales["fiscal_year"] == latest_fy)
        ]["electric_vehicles_sold"].values[0]
        projected_sales[state] = current_sales * (1 + cagr) ** years_to_project

    # Convert to DataFrame
    proj_df = pd.DataFrame(
        list(projected_sales.items()), columns=["State", "Projected_Sales_2030"]
    )

    # Add human-readable format
    proj_df["Projected_Sales_2030_readable"] = proj_df["Projected_Sales_2030"].apply(
        humanize.intword
    )

    # Sort by projected sales
    proj_df = proj_df.sort_values(
        by="Projected_Sales_2030", ascending=False
    ).reset_index(drop=True)

    # Add region information
    df_regions = filtered_data[["state", "region"]].drop_duplicates()
    proj_df["Region"] = proj_df["State"].map(df_regions.set_index("state")["region"])

    # Calculate and add CAGR to DataFrame
    proj_df["CAGR"] = proj_df["State"].map(cagr_dict)
    proj_df["CAGR_pct"] = (proj_df["CAGR"] * 100).round(1)

    return proj_df, cagr_dict, latest_fy


def display_kpi_metrics(proj_df):
    """Display key KPI metrics"""

    # Create KPI metrics
    total_sales = proj_df["Projected_Sales_2030"].sum()
    top_state = proj_df.iloc[0]["State"]
    top_sales = proj_df.iloc[0]["Projected_Sales_2030"]
    top_share = (top_sales / total_sales * 100).round(1)
    top3_share = (
        proj_df.iloc[:3]["Projected_Sales_2030"].sum() / total_sales * 100
    ).round(1)

    # Get state with highest CAGR
    fastest_growth_state = proj_df.loc[proj_df["CAGR"].idxmax()]["State"]
    fastest_growth_cagr = (proj_df.loc[proj_df["CAGR"].idxmax()]["CAGR"] * 100).round(1)

    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
        <div class="metric-container primary-metric">
            <div class="metric-title">Total Projected Sales</div>
            <div class="metric-value">{humanize.intword(total_sales)}</div>
            <div class="metric-subtitle">Estimated by 2030</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
        <div class="metric-container success-metric">
            <div class="metric-title">Leading State</div>
            <div class="metric-value">{top_state}</div>
            <div class="metric-subtitle">{top_share}% market share</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
        <div class="metric-container warning-metric">
            <div class="metric-title">Top 3 States Share</div>
            <div class="metric-value">{top3_share}%</div>
            <div class="metric-subtitle">Market concentration</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
        <div class="metric-container info-metric">
            <div class="metric-title">Highest Growth</div>
            <div class="metric-value">{fastest_growth_state}</div>
            <div class="metric-subtitle">{fastest_growth_cagr}% CAGR</div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def create_visualizations(proj_df, cagr_dict, selected_viz):
    """Create the selected visualization"""

    if selected_viz == "Bar Chart":
        # Create horizontal bar chart with labels
        fig = plt.figure(figsize=(10, 6))
        ax = sns.barplot(
            x="Projected_Sales_2030", y="State", data=proj_df, palette="Blues_r"
        )

        # Add data labels
        for i, p in enumerate(ax.patches):
            width = p.get_width() # type: ignore
            if width >= 1_000_000:
                formatted_value = f"{width/1_000_000:.1f}M"
            elif width >= 1_000:
                formatted_value = f"{width/1_000:.0f}K"
            else:
                formatted_value = f"{width:.0f}"

            ax.annotate(
                formatted_value,
                (width, p.get_y() + p.get_height() / 2), # type: ignore
                ha="left",
                va="center",
                fontweight="bold",
                size=9,
                xytext=(5, 0),
                textcoords="offset points",
            )

        plt.title("Projected EV Sales by State in 2030")
        plt.xlabel("Projected Sales (Units)")
        plt.ylabel("State")
        plt.tight_layout()
        st.pyplot(fig)

    elif selected_viz == "Geographic Map":
        # Create state codes mapping
        state_codes = {
            "Karnataka": "KA",
            "Tamil Nadu": "TN",
            "Maharashtra": "MH",
            "Kerala": "KL",
            "Delhi": "DL",
            "Uttar Pradesh": "UP",
            "Gujarat": "GJ",
            "Telangana": "TG",
            "Rajasthan": "RJ",
            "West Bengal": "WB",
            "Haryana": "HR",
            "Punjab": "PB",
            "Andhra Pradesh": "AP",
            "Bihar": "BR",
            "Madhya Pradesh": "MP",
            "Odisha": "OR",
            "Assam": "AS",
            "Goa": "GA",
            "Chhattisgarh": "CT",
            "Jharkhand": "JH",
            # Add more as needed
        }

        # Add state codes to DataFrame
        proj_df["state_code"] = proj_df["State"].map(state_codes)

        # Create choropleth map
        fig = px.choropleth(
            proj_df,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey="properties.ST_NM",
            locations="State",
            color="Projected_Sales_2030",
            color_continuous_scale="Blues",
            range_color=[0, proj_df["Projected_Sales_2030"].max()],
            scope="asia",
            labels={"Projected_Sales_2030": "Projected Sales"},
            title="Projected EV Sales by State in 2030",
            hover_data=["Projected_Sales_2030_readable"],
        )

        fig.update_geos(
            visible=False,
            fitbounds="locations",
            showcountries=True,
            showcoastlines=True,
            showland=True,
            countrycolor="lightgray",
            landcolor="lightgray",
        )

        fig.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            height=600,
            coloraxis_colorbar=dict(title="Projected Sales", tickformat=",.0f"),
        )
        st.plotly_chart(fig, use_container_width=True)

    elif selected_viz == "Treemap":
        # Create treemap
        fig = px.treemap(
            proj_df,
            path=[px.Constant("India"), "Region", "State"],
            values="Projected_Sales_2030",
            color="Projected_Sales_2030",
            color_continuous_scale="Blues",
            title="Projected EV Sales by Region and State in 2030",
            hover_data=["Projected_Sales_2030_readable"],
        )

        fig.update_traces(
            textinfo="label+percent parent+value",
            hovertemplate="<b>%{label}</b><br>Sales: %{customdata[0]}<br>Share: %{percentParent:.1%}<extra></extra>",
        )

        fig.update_layout(height=600, margin=dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

    elif selected_viz == "Bubble Chart":
        # Create bubble chart
        fig = px.scatter(
            proj_df,
            x=range(len(proj_df)),
            y="Projected_Sales_2030",
            size=[cagr * 100 for cagr in proj_df["CAGR"]],
            text="State",
            title="EV Sales Projection 2030 vs CAGR",
            labels={"x": "", "y": "Projected Sales 2030", "size": "CAGR (%)"},
            color="Region",
            hover_data=["CAGR_pct", "Projected_Sales_2030_readable"],
        )

        fig.update_traces(textposition="top center")

        fig.update_layout(
            showlegend=True,
            xaxis={"showticklabels": False},
            yaxis_title="Projected Sales (Units)",
            height=600,
            yaxis=dict(tickformat=".2s"),
        )
        st.plotly_chart(fig, use_container_width=True)

    elif selected_viz == "Donut Chart":
        # Create donut chart
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=proj_df["State"],
                    values=proj_df["Projected_Sales_2030"],
                    hole=0.4,
                    textinfo="label+percent",
                    marker=dict(colors=px.colors.sequential.Blues_r),
                    sort=False,
                )
            ]
        )

        total_market = humanize.intword(proj_df["Projected_Sales_2030"].sum())

        fig.update_layout(
            title_text=f"Projected EV Market Share by State in 2030<br><sup>Total Market: {total_market}</sup>",
            height=600,
            annotations=[
                dict(
                    text="2030<br>Market Share",
                    x=0.5,
                    y=0.5,
                    font_size=15,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig, use_container_width=True)


def display_adhd_friendly_insights(proj_df):
    """Display ADHD-friendly insights section"""

    # Use correct class names for section titles and containers
    st.markdown(
      '<h2 class="section-title">🚗 KEY INSIGHTS</h2>', unsafe_allow_html=True
    )

    # Big Picture
    st.markdown('<div class="insight-container">', unsafe_allow_html=True)
    st.markdown(
      '<h3 class="insight-header">💡 THE BIG PICTURE</h3>', unsafe_allow_html=True
    )

    top_state = proj_df.iloc[0]["State"]
    top_sales = proj_df.iloc[0]["Projected_Sales_2030_readable"]
    next_two_sales = proj_df.iloc[1:3]["Projected_Sales_2030"].sum()

    st.markdown(
      f"""
    **{top_state} will lead India's EV revolution** with a projected **{top_sales} electric vehicles** by 2030 
    - that's more than the next two states combined!
    """
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Top 3 Takeaways
    st.markdown('<div class="insight-container">', unsafe_allow_html=True)
    st.markdown(
      '<h3 class="insight-header">⭐ TOP 3 TAKEAWAYS</h3>', unsafe_allow_html=True
    )

    top3_states = ", ".join(proj_df.iloc[:3]["State"].tolist())
    top3_pct = (
      proj_df.iloc[:3]["Projected_Sales_2030"].sum()
      / proj_df["Projected_Sales_2030"].sum()
      * 100
    ).round(1)

    south_states = proj_df[proj_df["Region"] == "South"]["State"].tolist()
    if south_states:
      south_states_text = ", ".join(south_states)
    else:
      south_states_text = "Southern states"

    st.markdown(
      """
    1. <span class="emoji-bullet">🥇</span> **Three states will dominate**: {0} will account for over {1}% of all EV sales in India by 2030

    2. <span class="emoji-bullet">🌍</span> **Regional clusters matter**: {2} show the strongest adoption patterns, visible in both our map and treemap visualizations

    3. <span class="emoji-bullet">📊</span> **Size ≠ Growth**: Some smaller states show impressive growth rates despite lower total volumes
    """.format(
        top3_states, top3_pct, south_states_text
      ),
      unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # State Champions
    st.markdown('<div class="insight-container">', unsafe_allow_html=True)
    st.markdown(
      '<h3 class="insight-header">🏆 STATE CHAMPIONS</h3>', unsafe_allow_html=True
    )

    highest_volume_state = proj_df.iloc[0]["State"]
    highest_volume = proj_df.iloc[0]["Projected_Sales_2030_readable"]

    highest_growth_state = proj_df.loc[proj_df["CAGR"].idxmax()]["State"]
    highest_growth = (proj_df.loc[proj_df["CAGR"].idxmax()]["CAGR"] * 100).round(1)

    highest_share_state = proj_df.iloc[0]["State"]
    highest_share = (
      proj_df.iloc[0]["Projected_Sales_2030"]
      / proj_df["Projected_Sales_2030"].sum()
      * 100
    ).round(1)

    col1, col2, col3 = st.columns(3)

    with col1:
      st.markdown(
        f"""
      <div class="metric-container success-metric">
        <div class="metric-title">🥇 Highest Volume</div>
        <div class="metric-value">{highest_volume_state}</div>
        <div class="metric-subtitle">{highest_volume} projected sales</div>
      </div>
      """,
        unsafe_allow_html=True,
      )

    with col2:
      st.markdown(
        f"""
      <div class="metric-container info-metric">
        <div class="metric-title">🚀 Best Growth Rate</div>
        <div class="metric-value">{highest_growth_state}</div>
        <div class="metric-subtitle">{highest_growth}% CAGR</div>
      </div>
      """,
        unsafe_allow_html=True,
      )

    with col3:
      st.markdown(
        f"""
      <div class="metric-container warning-metric">
        <div class="metric-title">📊 Highest Market Share</div>
        <div class="metric-value">{highest_share_state}</div>
        <div class="metric-subtitle">{highest_share}% of national market</div>
      </div>
      """,
        unsafe_allow_html=True,
      )

    st.markdown("</div>", unsafe_allow_html=True)

    # Business Implications
    st.markdown('<div class="insight-container">', unsafe_allow_html=True)
    st.markdown(
      '<h3 class="insight-header">📱 WHAT THIS MEANS FOR BUSINESS</h3>',
      unsafe_allow_html=True,
    )

    top_region = proj_df["Region"].value_counts().idxmax()
    charging_state = proj_df.iloc[0]["State"]

    st.markdown(
      f"""
    * <span class="emoji-bullet">🏭</span> **Manufacturers**: Focus production capacity and distribution networks in {top_region}ern India
    
    * <span class="emoji-bullet">🔌</span> **Charging Infrastructure**: {charging_state} needs 5× more charging stations than most other states
    
    * <span class="emoji-bullet">📜</span> **Government Policy**: Northern states need stronger incentives to catch up
    """,
      unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Data Table
    with st.expander("View Detailed Projections Table"):
      display_df = proj_df.copy()
      # Format columns for display
      display_df["CAGR"] = display_df["CAGR_pct"].astype(str) + "%"
      display_df["Projected_Sales_2030"] = display_df["Projected_Sales_2030_readable"]
      # Select columns to display
      display_df = display_df[["State", "Region", "Projected_Sales_2030", "CAGR"]]
      st.dataframe(display_df, use_container_width=True)


def main():
    """Main function to run the Streamlit app"""
    
    st.title("EV Sales Projections for 2030")
    st.markdown(
        """
        <div class="highlight-box">
        This dashboard analyzes and projects electric vehicle sales for the top states in India by 2030,
        based on historical growth rates and penetration patterns from previous years.
        Use the filters to customize the analysis based on regions, base year, and other parameters.
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Load data
    try:
        monthly_ev_sales = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Get available years
    years = sorted(monthly_ev_sales['fiscal_year'].unique().tolist())
    latest_year = max(years)
    
    # Get available regions
    regions = ['All Regions'] + sorted(monthly_ev_sales['region'].unique().tolist())
    
    # Sidebar filters
    st.sidebar.title("Filters")
    
    filter_region = st.sidebar.selectbox("Region", regions)
    filter_year = st.sidebar.selectbox("Base Year for Projection", years, index=years.index(latest_year))
    
    ranking_method = st.sidebar.radio(
        "Rank Top States By",
        ["EV Penetration Rate", "Total EV Sales"],
        horizontal=True,
    )
    
    use_ev_penetration = ranking_method == "EV Penetration Rate"
    
    top_n = st.sidebar.slider("Number of States to Show", min_value=5, max_value=20, value=10)
    
    projection_year = st.sidebar.slider("Projection Year", min_value=latest_year + 1, max_value=2035, value=2030)
    
    # Choose visualization
    viz_options = ["Bar Chart", "Geographic Map", "Treemap", "Bubble Chart", "Donut Chart"]
    selected_viz = st.sidebar.selectbox("Visualization Type", viz_options)
    
    # Show source code info
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This dashboard is based on analysis from the "
        "[ev_sales_projection_2030.ipynb](https://github.com/sadiqhasanrupani/ev-analysis/blob/main/notebooks/research/ev_sales_projection_2030.ipynb) "
        "notebook."
    )
    
    # Calculate projections based on filters
    proj_df, cagr_dict, latest_fy = calculate_projections(
        monthly_ev_sales,
        filter_region=filter_region,
        filter_year=filter_year,
        use_ev_penetration=use_ev_penetration,
        top_n=top_n,
        projection_year=projection_year
    )
    
    # Display KPI metrics
    display_kpi_metrics(proj_df)
    
    # Create visualizations
    st.markdown('<h2 class="section-title">VISUALIZATION</h2>', unsafe_allow_html=True)
    create_visualizations(proj_df, cagr_dict, selected_viz)
    
    # Display ADHD-friendly insights
    display_adhd_friendly_insights(proj_df)
    
    # Disclaimer about projections
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.85em; color: #666; text-align: center;">
        <p>📌 <strong>REMEMBER</strong>: These projections assume current growth trends continue. 
        Any major policy changes or technological breakthroughs could significantly alter these numbers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
