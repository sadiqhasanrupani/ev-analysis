import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

def load_data():
    """Load and preprocess the EV sales data"""
    # Define base directory for data files
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    data_path = BASE_DIR / "data" / "processed" / "ev_sales_by_state_enhanced_20250806.csv"
    
    # Load the data
    ev_sales = pd.read_csv(data_path)
    
    # Convert date to pandas datetime
    ev_sales["date"] = pd.to_datetime(ev_sales["date"], errors="coerce")
    ev_sales["month_name"] = ev_sales["date"].dt.month_name()
    ev_sales["year_month"] = ev_sales["date"].dt.strftime("%Y-%m")
    ev_sales["month_numeric"] = ev_sales["date"].dt.month
    
    # Create fiscal year column (fiscal year starts in April)
    ev_sales["fiscal_year"] = np.where(
        ev_sales["month"] >= 4, ev_sales["year"], ev_sales["year"] - 1
    )
    
    return ev_sales

def get_monthly_sales(df, filter_year=None, filter_states=None, filter_categories=None, use_fiscal_year=False):
    """Aggregate sales by month with optional filters"""
    # Apply filters
    filtered_df = df.copy()
    
    if filter_year:
        if use_fiscal_year:
            filtered_df = filtered_df[filtered_df["fiscal_year"].isin(filter_year)]
        else:
            filtered_df = filtered_df[filtered_df["year"].isin(filter_year)]
    
    if filter_states and "All States" not in filter_states:
        filtered_df = filtered_df[filtered_df["state"].isin(filter_states)]
        
    if filter_categories and "All Categories" not in filter_categories:
        filtered_df = filtered_df[filtered_df["vehicle_category"].isin(filter_categories)]
    
    # Aggregate by month
    monthly_sales = (
        filtered_df.groupby(["month_numeric", "month_name"])["electric_vehicles_sold"]
        .sum()
        .reset_index()
        .sort_values(by="month_numeric", ascending=True)
    )
    
    return monthly_sales

def calculate_kpis(monthly_sales):
    """Calculate KPIs for monthly sales"""
    # Find peak and low months
    peak_month_idx = monthly_sales["electric_vehicles_sold"].idxmax()
    low_month_idx = monthly_sales["electric_vehicles_sold"].idxmin()
    
    peak_month = monthly_sales.loc[peak_month_idx, "month_name"]
    low_month = monthly_sales.loc[low_month_idx, "month_name"]
    
    peak_sales = monthly_sales.loc[peak_month_idx, "electric_vehicles_sold"]
    low_sales = monthly_sales.loc[low_month_idx, "electric_vehicles_sold"]
    
    # Calculate additional KPIs
    average_monthly_sales = monthly_sales["electric_vehicles_sold"].mean()
    peak_vs_avg_percentage = ((peak_sales / average_monthly_sales) - 1) * 100
    low_vs_avg_percentage = ((low_sales / average_monthly_sales) - 1) * 100
    peak_to_low_ratio = peak_sales / low_sales if low_sales > 0 else float('inf')
    
    # Calculate month-to-month volatility (standard deviation / mean)
    sales_volatility = (monthly_sales["electric_vehicles_sold"].std() / average_monthly_sales) * 100
    
    # Create monthly seasonality score (how far each month is from the average)
    monthly_sales["seasonality_score"] = (monthly_sales["electric_vehicles_sold"] / average_monthly_sales) - 1
    
    return {
        "peak_month": peak_month,
        "low_month": low_month,
        "peak_sales": peak_sales,
        "low_sales": low_sales,
        "average_monthly_sales": average_monthly_sales,
        "peak_vs_avg_percentage": peak_vs_avg_percentage,
        "low_vs_avg_percentage": low_vs_avg_percentage,
        "peak_to_low_ratio": peak_to_low_ratio,
        "sales_volatility": sales_volatility,
        "monthly_seasonality": monthly_sales[["month_name", "seasonality_score"]]
    }

def create_monthly_sales_chart(monthly_sales, kpis):
    """Create a bar chart of monthly sales with peak and low months highlighted"""
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    
    # Create custom color array for highlighting peak and low months
    colors = ['rgba(64, 164, 223, 0.7)'] * 12  # Default color
    for i, month in enumerate(month_order):
        if month == kpis["peak_month"]:
            colors[i] = 'rgba(46, 184, 92, 0.9)'  # Green for peak
        elif month == kpis["low_month"]:
            colors[i] = 'rgba(220, 53, 69, 0.9)'  # Red for low
    
    # Sort monthly sales by the defined month order
    monthly_sales_sorted = monthly_sales.copy()
    monthly_sales_sorted['month_order'] = monthly_sales_sorted['month_name'].apply(lambda x: month_order.index(x))
    monthly_sales_sorted = monthly_sales_sorted.sort_values('month_order')
    
    fig = px.bar(
        monthly_sales_sorted,
        x="month_name",
        y="electric_vehicles_sold",
        title="Monthly EV Sales Distribution",
        labels={"month_name": "Month", "electric_vehicles_sold": "Total EV Sales"},
        category_orders={"month_name": month_order},
        text=monthly_sales_sorted["electric_vehicles_sold"]
    )
    
    # Format the text labels
    fig.update_traces(texttemplate='%{y:.2s}', textposition='outside')
    
    # Update colors based on peak/low months
    fig.update_traces(marker_color=colors)
    
    # Add average line
    fig.add_hline(
        y=kpis["average_monthly_sales"],
        line_dash="dash",
        line_color="rgba(0,0,0,0.5)",
        annotation_text="Average",
        annotation_position="bottom right"
    )
    
    # Improve layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total EV Sales",
        legend_title="Month Type",
        height=500,
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(tickangle=-45),
    )
    
    return fig

def create_seasonal_heatmap(df, use_fiscal_year=False):
    """Create a heatmap showing month-by-month sales across years"""
    # Prepare data for the heatmap
    year_field = "fiscal_year" if use_fiscal_year else "year"
    
    # Group by year and month
    heatmap_data = (
        df.groupby([year_field, "month_numeric", "month_name"])["electric_vehicles_sold"]
        .sum()
        .reset_index()
    )
    
    # Create the pivot table
    pivot_table = pd.pivot_table(
        heatmap_data, 
        values="electric_vehicles_sold", 
        index=year_field, 
        columns="month_name",
        aggfunc="sum"
    )
    
    # Reorder columns by month
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    
    if use_fiscal_year:
        # For fiscal year, reorder starting with April
        fiscal_month_order = month_order[3:] + month_order[:3]
        pivot_table = pivot_table[fiscal_month_order]
    else:
        pivot_table = pivot_table[month_order]
    
    # Create heatmap
    fig = px.imshow(
        pivot_table.values,
        labels=dict(x="Month", y="Year", color="Sales"),
        x=pivot_table.columns.tolist(),
        y=pivot_table.index.tolist(),
        color_continuous_scale="YlGnBu",
        text_auto=True,
        aspect="auto"
    )
    
    fig.update_layout(
        title=f"{'Fiscal' if use_fiscal_year else 'Calendar'} Year-Month EV Sales Heatmap",
        height=400,
        xaxis_title="Month",
        yaxis_title=f"{'Fiscal' if use_fiscal_year else 'Calendar'} Year"
    )
    
    return fig

def create_seasonality_radar(kpis):
    """Create a radar chart showing the seasonality of each month"""
    # Get the seasonality data
    seasonality_data = kpis["monthly_seasonality"]
    
    # Sort by month order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    
    seasonality_data = seasonality_data.set_index('month_name').reindex(month_order).reset_index()
    seasonality_data['seasonality_pct'] = seasonality_data['seasonality_score'] * 100
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=seasonality_data['seasonality_pct'].tolist() + [seasonality_data['seasonality_pct'].iloc[0]],  # Close the loop
        theta=seasonality_data['month_name'].tolist() + [seasonality_data['month_name'].iloc[0]],  # Close the loop
        fill='toself',
        line=dict(color='rgba(64, 164, 223, 0.8)', width=2),
        fillcolor='rgba(64, 164, 223, 0.3)',
        name='Monthly Seasonality'
    ))
    
    # Add annotations for peak and low months
    peak_idx = seasonality_data[seasonality_data['month_name'] == kpis['peak_month']].index[0]
    low_idx = seasonality_data[seasonality_data['month_name'] == kpis['low_month']].index[0]
    
    peak_score = seasonality_data.iloc[peak_idx]['seasonality_pct']
    low_score = seasonality_data.iloc[low_idx]['seasonality_pct']
    
    # Highlight peak and low points
    fig.add_trace(go.Scatterpolar(
        r=[peak_score],
        theta=[kpis['peak_month']],
        mode='markers',
        marker=dict(size=12, color='rgba(46, 184, 92, 0.9)'),
        name='Peak Month'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[low_score],
        theta=[kpis['low_month']],
        mode='markers',
        marker=dict(size=12, color='rgba(220, 53, 69, 0.9)'),
        name='Low Month'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-40, 40]  # Adjust based on your data
            )
        ),
        title="Monthly Sales Seasonality (%)",
        showlegend=True,
        height=500
    )
    
    return fig

def create_monthly_trend_line(df, filter_year=None, filter_states=None, filter_categories=None):
    """Create a line chart showing month-by-month trend over multiple years"""
    # Apply filters
    filtered_df = df.copy()
    
    if filter_year:
        filtered_df = filtered_df[filtered_df["year"].isin(filter_year)]
    
    if filter_states and "All States" not in filter_states:
        filtered_df = filtered_df[filtered_df["state"].isin(filter_states)]
        
    if filter_categories and "All Categories" not in filter_categories:
        filtered_df = filtered_df[filtered_df["vehicle_category"].isin(filter_categories)]
    
    # Aggregate by year and month
    trend_data = (
        filtered_df.groupby(["year", "month_numeric", "month_name"])["electric_vehicles_sold"]
        .sum()
        .reset_index()
        .sort_values(by=["year", "month_numeric"], ascending=True)
    )
    
    # Create line chart
    fig = px.line(
        trend_data,
        x="month_name",
        y="electric_vehicles_sold",
        color="year",
        markers=True,
        title="Monthly EV Sales Trends by Year",
        labels={"month_name": "Month", "electric_vehicles_sold": "Total EV Sales", "year": "Year"},
        category_orders={"month_name": ['January', 'February', 'March', 'April', 'May', 'June', 
                                       'July', 'August', 'September', 'October', 'November', 'December']}
    )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total EV Sales",
        legend_title="Year",
        height=500,
        xaxis=dict(tickangle=-45)
    )
    
    return fig

def main():
    # Page configuration
    st.set_page_config(
        page_title="EV Sales Seasonality Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
        .metric-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .peak-metric {
            border-left: 5px solid rgba(46, 184, 92, 0.9);
        }
        .low-metric {
            border-left: 5px solid rgba(220, 53, 69, 0.9);
        }
        .ratio-metric {
            border-left: 5px solid rgba(255, 193, 7, 0.9);
        }
        .volatility-metric {
            border-left: 5px solid rgba(111, 66, 193, 0.9);
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
        .section-title {
            border-left: 4px solid #4361ee;
            padding-left: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Load data
    ev_sales = load_data()
    
    # Title
    st.title("📊 EV Sales Seasonality Analysis")
    st.markdown("""
    This dashboard analyzes the seasonal patterns in electric vehicle (EV) sales across India from 2022 to 2024, 
    identifying peak and low months for sales volume. Use the filters to explore different segments and regions.
    """)
    
    # Sidebar filters
    st.sidebar.title("Filters")
    
    # Year selection
    available_years = sorted(ev_sales["year"].unique().tolist())
    selected_years = st.sidebar.multiselect(
        "Select Years",
        options=available_years,
        default=available_years
    )
    
    # State selection
    all_states = sorted(ev_sales["state"].unique().tolist())
    selected_states = st.sidebar.multiselect(
        "Select States",
        options=["All States"] + all_states,
        default=["All States"]
    )
    
    # Vehicle category selection
    all_categories = sorted(ev_sales["vehicle_category"].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "Select Vehicle Categories",
        options=["All Categories"] + all_categories,
        default=["All Categories"]
    )
    
    # Calendar vs Fiscal Year toggle
    use_fiscal_year = st.sidebar.checkbox("Use Fiscal Year (Apr-Mar)", value=False)
    
    # Apply filters and calculate data
    monthly_sales = get_monthly_sales(
        ev_sales, 
        filter_year=selected_years, 
        filter_states=selected_states, 
        filter_categories=selected_categories,
        use_fiscal_year=use_fiscal_year
    )
    
    kpis = calculate_kpis(monthly_sales)
    
    # Display KPIs in a row
    st.markdown('<div class="section-title"><h3>Key Performance Indicators</h3></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container peak-metric">
            <div class="metric-title">Peak Sales Month</div>
            <div class="metric-value">{kpis["peak_month"]}</div>
            <div class="metric-subtitle">{int(kpis["peak_sales"]):,} units</div>
            <div class="metric-subtitle">+{kpis["peak_vs_avg_percentage"]:.1f}% vs. average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container low-metric">
            <div class="metric-title">Low Sales Month</div>
            <div class="metric-value">{kpis["low_month"]}</div>
            <div class="metric-subtitle">{int(kpis["low_sales"]):,} units</div>
            <div class="metric-subtitle">{kpis["low_vs_avg_percentage"]:.1f}% vs. average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container ratio-metric">
            <div class="metric-title">Peak-to-Low Ratio</div>
            <div class="metric-value">{kpis["peak_to_low_ratio"]:.1f}x</div>
            <div class="metric-subtitle">Higher ratio = more seasonality</div>
            <div class="metric-subtitle">Avg. monthly sales: {int(kpis["average_monthly_sales"]):,} units</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container volatility-metric">
            <div class="metric-title">Sales Volatility</div>
            <div class="metric-value">{kpis["sales_volatility"]:.1f}%</div>
            <div class="metric-subtitle">Monthly sales variability</div>
            <div class="metric-subtitle">Higher % = more unpredictable</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main visualizations
    st.markdown('<div class="section-title"><h3>Monthly Sales Distribution</h3></div>', unsafe_allow_html=True)
    
    # Display monthly sales chart
    fig_monthly_sales = create_monthly_sales_chart(monthly_sales, kpis)
    st.plotly_chart(fig_monthly_sales, use_container_width=True)
    
    # Create two columns layout for the next visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Display yearly seasonality heatmap
        fig_heatmap = create_seasonal_heatmap(ev_sales, use_fiscal_year=use_fiscal_year)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Display seasonality radar chart
        fig_radar = create_seasonality_radar(kpis)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Display monthly trend line
    st.markdown('<div class="section-title"><h3>Yearly Comparison of Monthly Trends</h3></div>', unsafe_allow_html=True)
    
    fig_trend = create_monthly_trend_line(
        ev_sales, 
        filter_year=selected_years, 
        filter_states=selected_states, 
        filter_categories=selected_categories
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Insights section
    st.markdown('<div class="section-title"><h3>Key Insights</h3></div>', unsafe_allow_html=True)
    
    # Generate dynamic insights based on data
    st.markdown(f"""
    ### Seasonal Patterns:
    
    - **Peak Season**: The data shows that **{kpis["peak_month"]}** is the peak month for EV sales with **{int(kpis["peak_sales"]):,}** units sold, **{kpis["peak_vs_avg_percentage"]:.1f}%** higher than the monthly average.
    
    - **Low Season**: **{kpis["low_month"]}** shows the lowest sales with **{int(kpis["low_sales"]):,}** units, **{abs(kpis["low_vs_avg_percentage"]):.1f}%** lower than the monthly average.
    
    - **Seasonality Ratio**: The peak-to-low sales ratio is **{kpis["peak_to_low_ratio"]:.1f}x**, indicating {'strong' if kpis["peak_to_low_ratio"] > 2 else 'moderate' if kpis["peak_to_low_ratio"] > 1.5 else 'relatively low'} seasonality in the EV market.
    
    - **Monthly Volatility**: Sales show a volatility of **{kpis["sales_volatility"]:.1f}%**, suggesting {'highly' if kpis["sales_volatility"] > 30 else 'moderately' if kpis["sales_volatility"] > 15 else 'relatively stable'} month-to-month variations.
    
    ### Business Implications:
    
    - **Supply Chain Planning**: Manufacturers should increase production capacity ahead of **{kpis["peak_month"]}** to meet higher demand.
    
    - **Marketing Strategy**: Consider promotional campaigns during **{kpis["low_month"]}** to boost sales during the slow period.
    
    - **Inventory Management**: Optimize inventory levels based on the seasonal patterns to avoid overstocking during low seasons and stockouts during peak seasons.
    
    - **Dealership Staffing**: Adjust staffing levels at dealerships to match the seasonal demand patterns, with increased staffing during **{kpis["peak_month"]}**.
    """)

    # Data notes
    with st.expander("About the Data"):
        st.markdown("""
        **Data Source**: The analysis is based on processed EV sales data by state from 2022 to 2024, which includes:
        
        - Monthly sales volumes for electric vehicles across different states in India
        - Categorization by vehicle types (2-Wheelers, 4-Wheelers, etc.)
        - Calendar year and fiscal year analysis options
        
        **Methodology**: 
        - Peak and low months are determined based on the total sales volume across the selected period, states, and vehicle categories.
        - Seasonality score represents how much each month deviates from the average monthly sales (as a percentage).
        - Sales volatility is calculated as the standard deviation of monthly sales divided by the average monthly sales.
        
        **Limitations**:
        - The analysis is based on historical data and past patterns might not always predict future trends.
        - External factors like policy changes, fuel prices, and economic conditions also influence EV sales beyond seasonal patterns.
        """)

if __name__ == "__main__":
    main()
