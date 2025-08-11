import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
import os

# Set page config
st.set_page_config(
    page_title="EV Sales Analysis - Top States by CAGR",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem 1rem;
    }
    .st-emotion-cache-16txtl3 h1, .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
        color: #1E88E5;
    }
    .st-emotion-cache-16txtl3 h4 {
        color: #0D47A1;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .insights-box {
        background-color: #e3f2fd;
        border-left: 5px solid #1e88e5;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load data
@st.cache_data
def load_data():
    # Define data paths - use absolute path to avoid relative path issues
    base_dir = "/mnt/data/projects/data-analyst/python-based/ev-analysis/ev-analysis"
    data_folder = os.path.join(base_dir, "data")
    state_sales_path = os.path.join(data_folder, "processed/ev_sales_by_state_enhanced_20250806.csv")
    
    # Print the path for debugging
    st.sidebar.text(f"Looking for data at: {state_sales_path}")
    
    # Check if file exists
    if not os.path.exists(state_sales_path):
        st.error(f"Data file not found at {state_sales_path}")
        # Try to find the file in the workspace
        possible_paths = []
        for root, dirs, files in os.walk(base_dir):
            if "ev_sales_by_state_enhanced_20250806.csv" in files:
                possible_paths.append(os.path.join(root, "ev_sales_by_state_enhanced_20250806.csv"))
        
        if possible_paths:
            st.sidebar.success(f"Found alternative data file at: {possible_paths[0]}")
            state_sales_path = possible_paths[0]
        else:
            # If still can't find, try the notebook's path for loading
            notebook_data_path = os.path.join(base_dir, "notebooks/research/top10_states_with_highest_cagr.ipynb")
            st.sidebar.info(f"Searching relative to notebook: {notebook_data_path}")
    
    # Load data
    try:
        state_sales = pd.read_csv(state_sales_path)
        st.sidebar.success("Data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Fallback to a simulated dataset if the real one can't be loaded
        st.warning("Using simulated data for demonstration purposes.")
        
        # Create a simple simulated dataset
        states = ["State_" + str(i) for i in range(1, 31)]
        years = [2022, 2023, 2024]
        
        # Generate simulated data
        data = []
        for state in states:
            for year in years:
                total_sales = np.random.randint(50000, 500000)
                ev_sales = np.random.randint(2000, 50000)
                data.append({
                    "state": state,
                    "year": year, 
                    "total_vehicles_sold": total_sales,
                    "electric_vehicles_sold": ev_sales
                })
        
        state_sales = pd.DataFrame(data)
    
    return state_sales

# Function to calculate CAGRs
def calculate_cagrs(state_sales, start_year, end_year, sales_type="total"):
    """Calculate CAGR for different sales types between specified years"""
    # Filter by years
    filtered_data = state_sales.loc[state_sales['year'].isin([start_year, end_year])]
    
    # Determine which column to use based on sales_type
    sales_column = "total_vehicles_sold"  # Default value
    if sales_type == "total":
        sales_column = "total_vehicles_sold"
    elif sales_type == "ev":
        sales_column = "electric_vehicles_sold"
    elif sales_type == "non_ev":
        # Create non-EV sales column if it doesn't exist
        filtered_data['none_ev_sales'] = filtered_data['total_vehicles_sold'] - filtered_data['electric_vehicles_sold']
        sales_column = "none_ev_sales"
    
    # Group by state and year
    grouped = filtered_data.groupby(['state', 'year'], as_index=False)[sales_column].sum()
    
    # Pivot data
    pivot_data = (
        grouped.pivot(
            index='state',
            columns='year',
            values=sales_column
        )
        .reset_index()
    )
    
    # Rename columns for clarity
    pivot_data = pivot_data.rename(columns={
        start_year: f'sales_{start_year}',
        end_year: f'sales_{end_year}'
    })
    
    # Calculate CAGR
    years_diff = end_year - start_year
    pivot_data['CAGR'] = (
        ((pivot_data[f'sales_{end_year}'] / pivot_data[f'sales_{start_year}']) ** (1/years_diff) - 1) * 100
    ).round(2)
    
    # Handle zero or missing values
    pivot_data = pivot_data.dropna(subset=[f'sales_{start_year}', f'sales_{end_year}'])
    pivot_data = pivot_data[pivot_data[f'sales_{start_year}'] > 0]
    
    return pivot_data

# Create comparison data between different CAGRs
def create_cagr_comparison(total_cagr, ev_cagr):
    """Create comparison dataframe between total CAGR and EV CAGR"""
    comparison = pd.merge(
        total_cagr[['state', 'CAGR']].rename(columns={'CAGR': 'Total_CAGR'}),
        ev_cagr[['state', 'CAGR']].rename(columns={'CAGR': 'EV_CAGR'}),
        on='state',
        how='inner'
    )
    return comparison

# Main function to run the app
def main():
    # Load data
    state_sales = load_data()
    
    # Sidebar
    st.sidebar.title("CAGR Analysis Controls")
    
    # Year range selector
    available_years = sorted(state_sales['year'].unique())
    start_year, end_year = st.sidebar.select_slider(
        "Select Year Range for CAGR Calculation",
        options=available_years,
        value=(2022, 2024)
    )
    
    st.sidebar.markdown("---")
    
    # Region filter
    all_states = sorted(state_sales['state'].unique())
    selected_states = st.sidebar.multiselect(
        "Filter by States/UTs",
        options=all_states,
        default=[]
    )
    
    # Apply state filter if selected
    if selected_states:
        filtered_state_sales = state_sales[state_sales['state'].isin(selected_states)]
    else:
        filtered_state_sales = state_sales
    
    st.sidebar.markdown("---")
    
    # Top N selector
    top_n = st.sidebar.slider("Select Number of Top States to Display", 5, 20, 10)
    
    # Analysis type selector
    analysis_type = st.sidebar.radio(
        "Select Analysis View",
        ["Overview", "Total Vehicle Sales", "EV Sales", "Non-EV Sales", "Comparison Analysis"]
    )
    
    # Calculate fresh CAGRs
    total_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "total")
    ev_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "ev")
    non_ev_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "non_ev")
    
    # Get top N states
    top10_total = total_cagr.sort_values('CAGR', ascending=False).head(top_n)
    top10_ev = ev_cagr.sort_values('CAGR', ascending=False).head(top_n)
    top10_non_ev = non_ev_cagr.sort_values('CAGR', ascending=False).head(top_n)
    
    # Create comparison data
    comparison = create_cagr_comparison(total_cagr, ev_cagr)
    
    # Create content based on selected analysis type
    if analysis_type == "Overview":
        display_overview(top10_total, top10_ev, top10_non_ev, comparison, start_year, end_year)
    elif analysis_type == "Total Vehicle Sales":
        display_total_vehicle_analysis(top10_total, start_year, end_year)
    elif analysis_type == "EV Sales":
        display_ev_analysis(top10_ev, start_year, end_year)
    elif analysis_type == "Non-EV Sales":
        display_non_ev_analysis(top10_non_ev, start_year, end_year)
    elif analysis_type == "Comparison Analysis":
        display_comparison_analysis(comparison, start_year, end_year)

# Functions to display different analysis views
def display_overview(top10_total, top10_ev, top10_non_ev, comparison, start_year, end_year):
    st.title(f"Vehicle Sales CAGR Analysis ({start_year}-{end_year})")
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Total Vehicle CAGR", f"{top10_total['CAGR'].mean():.2f}%")
    with col2:
        st.metric("Average EV CAGR", f"{top10_ev['CAGR'].mean():.2f}%")
    with col3:
        st.metric("Average Non-EV CAGR", f"{top10_non_ev['CAGR'].mean():.2f}%")
    
    st.markdown("---")
    
    # Key insights box
    st.markdown("""
    <div class="insights-box">
        <h4>Key Insights</h4>
        <ul>
            <li>Overall vehicle sales showed a decline across most states during this period.</li>
            <li>Electric vehicle sales demonstrated a mixed pattern with some states showing growth.</li>
            <li>There's a weak correlation between total vehicle CAGR and EV CAGR, suggesting independent market dynamics.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary tabs for each category
    tab1, tab2, tab3, tab4 = st.tabs(["Total Vehicle Sales", "EV Sales", "Non-EV Sales", "CAGR Comparison"])
    
    with tab1:
        fig = create_horizontal_bar_chart(
            top10_total.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by Total Vehicle Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_horizontal_bar_chart(
            top10_ev.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by EV Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = create_horizontal_bar_chart(
            top10_non_ev.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by Non-EV Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with tab4:
        fig = create_scatter_plot_with_regression(
            comparison,
            "Total_CAGR", "EV_CAGR", "state",
            f"Relationship Between Total Vehicle CAGR and EV CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_total_vehicle_analysis(top10_total, start_year, end_year):
    st.title(f"Total Vehicle Sales CAGR Analysis ({start_year}-{end_year})")
    
    # Show data table
    st.subheader("Top States by Total Vehicle Sales CAGR")
    st.dataframe(top10_total.sort_values('CAGR', ascending=False).style.background_gradient(
        cmap='RdYlGn', subset=['CAGR']
    ))
    
    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Bubble Chart"])
    
    with tab1:
        fig = create_horizontal_bar_chart(
            top10_total.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by Total Vehicle Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create a copy of the dataframe and add absolute value of CAGR for sizing
        plot_df = top10_total.sort_values('CAGR', ascending=False).copy()
        plot_df['CAGR_abs'] = plot_df['CAGR'].abs()
        
        fig = px.scatter(
            plot_df,
            x=f"sales_{start_year}", 
            y=f"sales_{end_year}", 
            size="CAGR_abs",  # Use absolute value for size
            color="CAGR",     # Use original value for color
            hover_name="state",
            size_max=50,
            color_continuous_scale="RdYlGn",
            title=f"Vehicle Sales Comparison: {start_year} vs {end_year} with CAGR",
            hover_data={"CAGR": True, "CAGR_abs": False}  # Show CAGR in hover, hide CAGR_abs
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis insights
    st.subheader("Analysis Insights")
    st.markdown("""
    Between 2022 and 2024, India's overall vehicle sales market faced a slowdown, with most states registering a decline in compounded annual growth rate (CAGR).
    
    The top performers managed to limit the drop more effectively than others. States like Nagaland, Puducherry, and Assam demonstrated relative resilience, managing to contain the decline better than other regions.
    
    This insight points toward states where market re-entry or targeted promotional strategies could recover sales faster once macroeconomic conditions improve.
    """)

def display_ev_analysis(top10_ev, start_year, end_year):
    st.title(f"Electric Vehicle Sales CAGR Analysis ({start_year}-{end_year})")
    
    # Show data table
    st.subheader("Top States by EV Sales CAGR")
    st.dataframe(top10_ev.sort_values('CAGR', ascending=False).style.background_gradient(
        cmap='RdYlGn', subset=['CAGR']
    ))
    
    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Growth Chart"])
    
    with tab1:
        fig = create_horizontal_bar_chart(
            top10_ev.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by EV Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create growth comparison chart
        fig = px.line(
            top10_ev,
            x='state',
            y=[f'sales_{start_year}', f'sales_{end_year}'],
            title=f"EV Sales Growth: {start_year} vs {end_year}",
            labels={
                'value': 'Number of EV Sales',
                'variable': 'Year',
                'state': 'State'
            }
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis insights
    st.subheader("Analysis Insights")
    st.markdown("""
    The electric vehicle market shows a more mixed pattern compared to the overall vehicle market. Some states like Arunachal Pradesh and Mizoram 
    demonstrated significant positive growth in EV sales, with CAGR exceeding 90%.
    
    This variation in EV adoption suggests that specific local factors, policy incentives, or infrastructure developments may be driving EV growth 
    independently from overall market trends. States with positive EV CAGR represent important emerging markets for electric mobility.
    """)

def display_non_ev_analysis(top10_non_ev, start_year, end_year):
    st.title(f"Non-EV Vehicle Sales CAGR Analysis ({start_year}-{end_year})")
    
    # Show data table
    st.subheader("Top States by Non-EV Sales CAGR")
    st.dataframe(top10_non_ev.sort_values('CAGR', ascending=False).style.background_gradient(
        cmap='RdYlGn', subset=['CAGR']
    ))
    
    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Comparison Chart"])
    
    with tab1:
        fig = create_horizontal_bar_chart(
            top10_non_ev.sort_values('CAGR'), 
            'state', 'CAGR',
            f"Top States by Non-EV Sales CAGR ({start_year}-{end_year})"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create a grouped bar chart comparing start and end year
        df_for_chart = top10_non_ev.sort_values('CAGR', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_for_chart['state'],
            y=df_for_chart[f'sales_{start_year}'],
            name=f'{start_year} Sales',
            marker_color='lightskyblue'
        ))
        fig.add_trace(go.Bar(
            x=df_for_chart['state'],
            y=df_for_chart[f'sales_{end_year}'],
            name=f'{end_year} Sales',
            marker_color='royalblue'
        ))
        
        fig.update_layout(
            title=f"Non-EV Vehicle Sales: {start_year} vs {end_year}",
            xaxis_title="State",
            yaxis_title="Number of Non-EV Vehicles Sold",
            barmode='group',
            xaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis insights
    st.subheader("Analysis Insights")
    st.markdown("""
    Non-electric vehicle sales followed a trend similar to the overall vehicle market, with all states experiencing a decline. However, 
    some states showed greater resilience than others.
    
    The market contraction in traditional vehicles contrasts with the growth seen in the EV segment in some states, potentially indicating 
    a gradual shift in consumer preferences or the impact of policy measures favoring electric mobility.
    
    States with less severe decline in non-EV sales might have stronger established dealer networks, better access to financing, or different 
    consumer preferences that sustained traditional vehicle demand.
    """)

def display_comparison_analysis(comparison, start_year, end_year):
    st.title(f"CAGR Comparison Analysis ({start_year}-{end_year})")
    
    # Show correlation stats
    correlation = comparison['Total_CAGR'].corr(comparison['EV_CAGR'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Correlation Coefficient", f"{correlation:.3f}")
    with col2:
        if correlation > 0.6:
            relationship = "Strong positive"
        elif correlation > 0.3:
            relationship = "Moderate positive"
        elif correlation > 0:
            relationship = "Weak positive"
        elif correlation > -0.3:
            relationship = "Weak negative"
        elif correlation > -0.6:
            relationship = "Moderate negative"
        else:
            relationship = "Strong negative"
        st.metric("Relationship Type", relationship)
    
    # Main scatter plot with regression
    fig = create_scatter_plot_with_regression(
        comparison,
        "Total_CAGR", "EV_CAGR", "state",
        f"Relationship Between Total Vehicle CAGR and EV CAGR ({start_year}-{end_year})"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Show data table
    st.subheader("Total CAGR vs EV CAGR by State")
    st.dataframe(comparison.sort_values('EV_CAGR', ascending=False).style.background_gradient(
        cmap='RdYlGn', subset=['Total_CAGR', 'EV_CAGR']
    ))
    
    # Quadrant analysis
    st.subheader("Quadrant Analysis")
    
    # Create scatter with quadrants
    total_mean = comparison['Total_CAGR'].mean()
    ev_mean = comparison['EV_CAGR'].mean()
    
    fig = px.scatter(
        comparison,
        x="Total_CAGR",
        y="EV_CAGR",
        hover_name="state",
        # Removed the text="state" parameter to hide data labels
        color="state",
        title=f"Quadrant Analysis: Total Vehicle CAGR vs EV CAGR ({start_year}-{end_year})"
    )
    
    # Add quadrant lines
    fig.add_shape(
        type="line", x0=total_mean, y0=min(comparison['EV_CAGR']), 
        x1=total_mean, y1=max(comparison['EV_CAGR']),
        line=dict(color="gray", width=1, dash="dash")
    )
    fig.add_shape(
        type="line", x0=min(comparison['Total_CAGR']), y0=ev_mean, 
        x1=max(comparison['Total_CAGR']), y1=ev_mean,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Add quadrant annotations
    fig.add_annotation(
        x=total_mean + (max(comparison['Total_CAGR']) - total_mean)/2, 
        y=ev_mean + (max(comparison['EV_CAGR']) - ev_mean)/2,
        text="Better Than Average<br>(Both Total & EV)",
        showarrow=False,
        font=dict(size=10)
    )
    fig.add_annotation(
        x=total_mean - (total_mean - min(comparison['Total_CAGR']))/2, 
        y=ev_mean + (max(comparison['EV_CAGR']) - ev_mean)/2,
        text="Better EV Growth<br>Worse Total Growth",
        showarrow=False,
        font=dict(size=10)
    )
    fig.add_annotation(
        x=total_mean + (max(comparison['Total_CAGR']) - total_mean)/2, 
        y=ev_mean - (ev_mean - min(comparison['EV_CAGR']))/2,
        text="Better Total Growth<br>Worse EV Growth",
        showarrow=False,
        font=dict(size=10)
    )
    fig.add_annotation(
        x=total_mean - (total_mean - min(comparison['Total_CAGR']))/2, 
        y=ev_mean - (ev_mean - min(comparison['EV_CAGR']))/2,
        text="Worse Than Average<br>(Both Total & EV)",
        showarrow=False,
        font=dict(size=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analysis insights
    st.markdown("""
    <div class="insights-box">
        <h4>Key Insights from CAGR Comparison</h4>
        <p>The relationship between total vehicle CAGR and EV CAGR reveals distinct patterns in India's automotive market transition:</p>
        <ol>
            <li><strong>Weak correlation</strong> indicates EV adoption is not strongly tied to overall vehicle sales trends, suggesting independent market dynamics.</li>
            <li><strong>States with positive EV growth</strong> despite negative total vehicle CAGR show early adoption of electric mobility regardless of overall market conditions.</li>
            <li><strong>Quadrant analysis</strong> helps identify states where targeted EV promotion strategies may be most effective based on existing market trends.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Helper functions for visualizations
def create_horizontal_bar_chart(df, x_col, y_col, title):
    """Create a horizontal bar chart with labels"""
    # Create color array based on values
    colors = ["#2ecc71" if val > 0 else "#e74c3c" for val in df[y_col]]
    
    fig = px.bar(
        df,
        y=x_col,
        x=y_col,
        orientation='h',
        text=y_col,
        title=title,
        color=y_col,
        color_continuous_scale="RdYlGn",
    )
    
    fig.update_traces(
        texttemplate='%{text:.2f}%', 
        textposition='outside'
    )
    
    fig.update_layout(
        xaxis_title="CAGR (%)",
        yaxis_title="State",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(autorange="reversed"),  # Reverse y-axis for descending order
    )
    
    return fig

def create_scatter_plot_with_regression(df, x_col, y_col, hover_col, title):
    """Create scatter plot with regression line"""
    # Create scatter plot
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        hover_name=hover_col,
        text=hover_col,
        title=title,
        labels={x_col: "Total Vehicles CAGR (%)", y_col: "EV CAGR (%)"}
    )
    
    # Update marker style
    fig.update_traces(
        marker=dict(size=10, color="skyblue"),
        textposition="top center",
        textfont=dict(size=8)
    )
    
    # Add regression line
    X = df[x_col].values.reshape(-1, 1)
    y = df[y_col].values
    
    try:
        model = LinearRegression().fit(X, y)
        x_range = np.linspace(df[x_col].min(), df[x_col].max(), 100)
        y_pred = model.predict(x_range.reshape(-1, 1))
        
        fig.add_traces(
            px.line(x=x_range, y=y_pred, labels={"x": x_col, "y": y_col})
            .update_traces(line=dict(color="darkorange", width=3))
            .data
        )
        
        # Add equation and R² as annotation
        r_squared = model.score(X, y)
        slope = model.coef_[0]
        intercept = model.intercept_
        
        fig.add_annotation(
            x=df[x_col].min() + (df[x_col].max() - df[x_col].min())*0.05,
            y=df[y_col].max() - (df[y_col].max() - df[y_col].min())*0.05,
            text=f"y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.3f}",
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="darkgray",
            borderwidth=1
        )
    except:
        st.warning("Could not fit regression line. Check your data.")
    
    # Layout tweaks
    fig.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=18)),
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="gray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="gray")
    )
    
    return fig

# Run the app
if __name__ == "__main__":
    main()
