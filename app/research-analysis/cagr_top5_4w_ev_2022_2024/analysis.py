import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# Path to the data files
DATA_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "data"
EV_SALES_BY_MAKERS_PATH = DATA_DIR / "processed" / "ev_sales_by_makers_cleaned_20250806.csv"

def load_data():
    """Load and prepare the data for analysis"""
    # Load the data
    df = pd.read_csv(EV_SALES_BY_MAKERS_PATH)
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Create fiscal year column
    df['fiscal_year'] = df['date'].dt.year + np.where(df['date'].dt.month >= 4, 1, 0)
    
    # Filter for 4-wheeler manufacturers
    df_4w = df[df['segment'] == 'Four-Wheeler Manufacturer']
    
    return df, df_4w

def calculate_cagr(sales_2022, sales_2024, years=2):
    """Calculate CAGR between two years"""
    if sales_2022 <= 0:  # Avoid division by zero
        return None
    return ((sales_2024 / sales_2022) ** (1/years) - 1) * 100

def get_top_makers_cagr(df_4w, n_makers=5, start_year=2022, end_year=2024):
    """Get the top N makers by total sales with their CAGR"""
    # Group by maker and fiscal year, sum the EV sales
    sales_by_maker_year = df_4w.groupby(['maker', 'fiscal_year'])['electric_vehicles_sold'].sum().reset_index()
    
    # Calculate total sales across all years to find top N makers
    total_sales_by_maker = sales_by_maker_year.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
    top_n_makers = total_sales_by_maker.sort_values('electric_vehicles_sold', ascending=False).head(n_makers)['maker'].tolist()
    
    # Filter for only the top N makers
    top_n_sales = sales_by_maker_year[sales_by_maker_year['maker'].isin(top_n_makers)]
    
    # Pivot the data to get years as columns
    pivot_sales = top_n_sales.pivot(index='maker', columns='fiscal_year', values='electric_vehicles_sold').reset_index()
    
    # Ensure all required years exist
    for year in [start_year, end_year]:
        if year not in pivot_sales.columns:
            pivot_sales[year] = np.nan
    
    # Calculate CAGR
    pivot_sales['CAGR (%)'] = pivot_sales.apply(
        lambda row: calculate_cagr(row[start_year], row[end_year], end_year - start_year), 
        axis=1
    )
    
    # Sort by CAGR
    pivot_sales = pivot_sales.sort_values('CAGR (%)', ascending=False)
    
    # Rename columns for clarity
    result_df = pivot_sales[['maker'] + [col for col in pivot_sales.columns if isinstance(col, (int, np.integer))] + ['CAGR (%)']].copy()
    year_cols = [col for col in result_df.columns if isinstance(col, (int, np.integer))]
    for year in year_cols:
        result_df = result_df.rename(columns={year: f'{year} Sales'})
    
    return result_df, top_n_makers

def calculate_yoy_growth(result_df):
    """Calculate year-over-year growth rates"""
    df = result_df.copy()
    years = [int(col.split(' ')[0]) for col in df.columns if 'Sales' in col]
    years.sort()
    
    for i in range(1, len(years)):
        prev_year = years[i-1]
        curr_year = years[i]
        col_name = f'Growth {prev_year}-{curr_year} (%)'
        df[col_name] = ((df[f'{curr_year} Sales'] / df[f'{prev_year} Sales']) - 1) * 100
    
    return df

def calculate_market_share(result_df):
    """Calculate market share for each year"""
    df = result_df.copy()
    years = [int(col.split(' ')[0]) for col in df.columns if 'Sales' in col]
    
    for year in years:
        col_name = f'{year} Market Share (%)'
        total_sales = df[f'{year} Sales'].sum()
        df[col_name] = (df[f'{year} Sales'] / total_sales) * 100
    
    return df

def create_cagr_bar_chart(result_df, colormap=px.colors.sequential.Blues):
    """Create a bar chart for CAGR comparison"""
    # Sort the data by CAGR for better presentation
    result_sorted = result_df.sort_values('CAGR (%)', ascending=False)
    
    fig = go.Figure()
    
    # Add bar chart for CAGR
    fig.add_trace(
        go.Bar(
            x=result_sorted['maker'],
            y=result_sorted['CAGR (%)'],
            text=result_sorted['CAGR (%)'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"),
            textposition='outside',
            marker_color=colormap[-5:],
            marker_line_color='rgb(8,48,107)',
            marker_line_width=1.5,
            name='CAGR (%)'
        )
    )
    
    # Add horizontal line at 0% for reference
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="red",
        annotation_text="0% Growth", 
        annotation_position="bottom right"
    )
    
    # Add average CAGR reference line
    avg_cagr = result_sorted['CAGR (%)'].mean()
    if not pd.isna(avg_cagr):
        fig.add_hline(
            y=avg_cagr, 
            line_dash="dot", 
            line_color="green",
            annotation_text=f"Avg CAGR: {avg_cagr:.2f}%", 
            annotation_position="top right"
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'CAGR (%) for Top 4-Wheeler EV Makers (2022-2024)',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        xaxis_title='EV Maker',
        yaxis_title='CAGR (%)',
        template='plotly_white',
        height=500,
        yaxis=dict(
            ticksuffix='%',
            zeroline=False,
            gridcolor='lightgray'
        ),
        plot_bgcolor='white'
    )
    
    return fig

def create_sales_trend_chart(result_df, colormap=px.colors.qualitative.Bold):
    """Create a line chart to visualize sales growth over time"""
    years = [int(col.split(' ')[0]) for col in result_df.columns if 'Sales' in col]
    years.sort()
    
    # Prepare data for line chart
    sales_data = pd.melt(
        result_df, 
        id_vars=['maker', 'CAGR (%)'],
        value_vars=[f'{year} Sales' for year in years],
        var_name='Year',
        value_name='Sales'
    )
    
    # Extract just the year from the Year column
    sales_data['Year'] = sales_data['Year'].str.extract(r'(\d+)')
    
    # Create line chart
    fig = px.line(
        sales_data, 
        x='Year', 
        y='Sales', 
        color='maker',
        markers=True,
        title='4-Wheeler EV Sales Growth by Top Makers (2022-2024)',
        template='plotly_white',
        labels={'Sales': 'Units Sold', 'Year': 'Year'},
        color_discrete_sequence=colormap
    )
    
    # Add data labels
    for maker in sales_data['maker'].unique():
        maker_data = sales_data[sales_data['maker'] == maker]
        fig.add_trace(
            go.Scatter(
                x=maker_data['Year'],
                y=maker_data['Sales'],
                mode='text',
                text=maker_data['Sales'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A"),
                textposition='top center',
                showlegend=False,
                textfont=dict(color='black')
            )
        )
    
    # Update the layout
    fig.update_layout(
        legend_title_text='EV Maker',
        xaxis=dict(
            tickmode='array', 
            tickvals=[str(year) for year in years],
            ticktext=[f'FY {year}' for year in years]
        ),
        height=500,
        yaxis_title='Units Sold',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    
    # Update traces to make lines thicker and markers larger
    fig.update_traces(
        selector=dict(mode='lines+markers'),
        line=dict(width=3),
        marker=dict(size=10)
    )
    
    return fig

def create_combined_chart(result_df, colormap=px.colors.sequential.Blues):
    """Create a combined visualization with sales and CAGR"""
    years = [int(col.split(' ')[0]) for col in result_df.columns if 'Sales' in col]
    years.sort()
    
    # Sort data by CAGR
    result_sorted = result_df.sort_values('CAGR (%)', ascending=False)
    
    # Create subplot with 2 y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add bars for each year's sales
    for i, year in enumerate(years):
        year_color = colormap[2 + i*2]  # Different shade of blue for each year
        
        fig.add_trace(
            go.Bar(
                x=result_sorted['maker'],
                y=result_sorted[f'{year} Sales'],
                name=f'FY {year} Sales',
                marker_color=year_color,
                text=result_sorted[f'{year} Sales'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A"),
                textposition='inside',
                width=0.2,
                offset=(-0.25 + 0.25*i),
                textfont=dict(color='white', size=10),
            ),
            secondary_y=False
        )
    
    # Add line for CAGR
    fig.add_trace(
        go.Scatter(
            x=result_sorted['maker'],
            y=result_sorted['CAGR (%)'],
            name='CAGR (%)',
            mode='lines+markers+text',
            marker=dict(size=12, symbol='diamond', color='#E74C3C'),
            line=dict(width=3, color='#E74C3C', dash='dot'),
            text=result_sorted['CAGR (%)'].apply(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A"),
            textposition='top center',
            textfont=dict(color='#E74C3C')
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title_text='Sales Growth and CAGR by Top 4-Wheeler EV Makers (2022-2024)',
        barmode='group',
        template='plotly_white',
        legend=dict(
            orientation='h',
            y=1.1,
            x=0.5,
            xanchor='center'
        ),
        height=600,
        margin=dict(t=120)
    )
    
    # Update axes titles
    fig.update_yaxes(title_text='Units Sold', secondary_y=False)
    fig.update_yaxes(title_text='CAGR (%)', ticksuffix='%', secondary_y=True)
    fig.update_xaxes(title_text='EV Maker')
    
    return fig

def create_market_share_chart(result_df):
    """Create a stacked bar chart showing market share evolution"""
    years = [int(col.split(' ')[0]) for col in result_df.columns if 'Sales' in col]
    years.sort()
    
    # Create a dataframe with market share data
    market_share_data = []
    for year in years:
        total_sales = result_df[f'{year} Sales'].sum()
        for _, row in result_df.iterrows():
            maker = row['maker']
            sales = row[f'{year} Sales']
            share = (sales / total_sales * 100) if total_sales > 0 else 0
            market_share_data.append({
                'Year': str(year),
                'Maker': maker,
                'Market Share (%)': share
            })
    
    ms_df = pd.DataFrame(market_share_data)
    
    # Create stacked bar chart
    fig = px.bar(
        ms_df,
        x='Year',
        y='Market Share (%)',
        color='Maker',
        title='Market Share Evolution by Manufacturer (2022-2024)',
        template='plotly_white',
        text='Market Share (%)',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    # Format text labels
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='inside'
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            tickmode='array', 
            tickvals=[str(year) for year in years],
            ticktext=[f'FY {year}' for year in years]
        ),
        yaxis=dict(
            title='Market Share (%)',
            ticksuffix='%'
        ),
        legend_title='Manufacturer',
        height=500
    )
    
    return fig

def create_dashboard():
    """Create Streamlit dashboard"""
    # Set page configuration
    st.set_page_config(
        page_title="Top 5 4-Wheeler EV Makers CAGR Analysis",
        page_icon="🚗",
        layout="wide"
    )
    
    # Page title and introduction
    st.title("🚗 CAGR Analysis: Top 5 Four-Wheeler EV Makers (2022-2024)")
    st.markdown("""
    This dashboard analyzes the Compounded Annual Growth Rate (CAGR) for the top 5 four-wheeler electric vehicle 
    manufacturers in India from 2022 to 2024. The CAGR provides insights into the sustained growth of manufacturers 
    over this period, helping identify market leaders and emerging players.
    """)
    
    # Load data
    df, df_4w = load_data()
    
    # Sidebar for filters
    st.sidebar.header("Filters")
    
    # Filter for top N manufacturers
    top_n = st.sidebar.slider(
        "Number of Top Manufacturers", 
        min_value=3, 
        max_value=10, 
        value=5,
        help="Select the number of top manufacturers to analyze"
    )
    
    # Year range filter
    available_years = sorted(df_4w['fiscal_year'].unique())
    if len(available_years) >= 2:
        default_start = min(available_years)
        default_end = max(available_years)
    else:
        default_start = 2022
        default_end = 2024
    
    start_year, end_year = st.sidebar.select_slider(
        "Year Range",
        options=available_years,
        value=(default_start, default_end)
    )
    
    # Optional filter for specific manufacturers
    all_makers = sorted(df_4w['maker'].unique().tolist())
    selected_makers = st.sidebar.multiselect(
        "Filter by Specific Manufacturers (Optional)",
        options=all_makers,
        default=[]
    )
    
    # Calculate CAGR for top manufacturers
    result_df, top_makers = get_top_makers_cagr(df_4w, n_makers=top_n, start_year=start_year, end_year=end_year)
    
    # Apply manufacturer filter if selected
    if selected_makers:
        result_df = result_df[result_df['maker'].isin(selected_makers)]
    
    # Calculate additional metrics
    detailed_df = calculate_yoy_growth(result_df)
    detailed_df = calculate_market_share(detailed_df)
    
    # KPI Section
    st.subheader("Key Performance Indicators")
    
    # Find the top performer by CAGR
    if not result_df.empty and 'CAGR (%)' in result_df.columns:
        if not result_df['CAGR (%)'].isna().all():
            top_idx = result_df['CAGR (%)'].idxmax()
            top_cagr_maker = result_df.loc[top_idx, 'maker'] 
            top_cagr_value = result_df['CAGR (%)'].max()
        else:
            top_cagr_maker = "N/A"
            top_cagr_value = 0
        
        # Find the manufacturer with highest sales in the most recent year
        most_recent_year = max([int(col.split(' ')[0]) for col in result_df.columns if 'Sales' in col])
        sales_col = f'{most_recent_year} Sales'
        if not result_df[sales_col].isna().all():
            top_sales_idx = result_df[sales_col].idxmax()
            top_sales_maker = result_df.loc[top_sales_idx, 'maker']
            top_sales_value = result_df[sales_col].max()
        else:
            top_sales_maker = "N/A"
            top_sales_value = 0
        
        # Find the manufacturer with most improved market share
        if f'{start_year} Market Share (%)' in detailed_df.columns and f'{end_year} Market Share (%)' in detailed_df.columns:
            detailed_df['Market Share Change'] = detailed_df[f'{end_year} Market Share (%)'] - detailed_df[f'{start_year} Market Share (%)']
            if not detailed_df['Market Share Change'].isna().all():
                top_improved_idx = detailed_df['Market Share Change'].idxmax()
                top_improved_maker = detailed_df.loc[top_improved_idx, 'maker']
                top_improved_value = detailed_df['Market Share Change'].max()
            else:
                top_improved_maker = "N/A"
                top_improved_value = 0
        else:
            top_improved_maker = "N/A"
            top_improved_value = 0
        
        # Calculate industry average CAGR
        avg_cagr = result_df['CAGR (%)'].mean() if not result_df['CAGR (%)'].isna().all() else 0
        
        # Calculate total sales growth for the industry
        if f'{start_year} Sales' in detailed_df.columns and f'{end_year} Sales' in detailed_df.columns:
            total_start = detailed_df[f'{start_year} Sales'].sum()
            total_end = detailed_df[f'{end_year} Sales'].sum()
            industry_growth = ((total_end / total_start) ** (1/(end_year-start_year)) - 1) * 100 if total_start > 0 else 0
        else:
            industry_growth = 0
            
        # Display KPIs in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Highest CAGR Manufacturer",
                value=str(top_cagr_maker),
                delta=f"{top_cagr_value:.2f}%" if pd.notnull(top_cagr_value) else "N/A"
            )
        
        with col2:
            st.metric(
                label=f"Top Seller ({most_recent_year})",
                value=str(top_sales_maker),
                delta=str(f"{int(top_sales_value):,} units") if pd.notnull(top_sales_value) else "N/A"
            )
        
        with col3:
            st.metric(
                label="Most Improved Market Share",
                value=str(top_improved_maker),
                delta=str(f"+{top_improved_value:.2f}%") if pd.notnull(top_improved_value) and top_improved_value > 0 else str(f"{top_improved_value:.2f}%")
            )
        
        with col4:
            st.metric(
                label="Industry Average CAGR",
                value=f"{avg_cagr:.2f}%",
                delta=str(f"{industry_growth - avg_cagr:.2f}%") if industry_growth > avg_cagr else str(f"{industry_growth - avg_cagr:.2f}%")
            )
    
    # Visualization tabs
    st.subheader("Analysis & Visualizations")
    tabs = st.tabs(["CAGR Comparison", "Sales Trends", "Combined Analysis", "Market Share Evolution", "Detailed Data"])
    
    with tabs[0]:
        if not result_df.empty:
            st.plotly_chart(create_cagr_bar_chart(result_df), use_container_width=True)
            
            # Add explanatory text
            st.markdown("""
            ### CAGR Comparison Insights
            
            The Compound Annual Growth Rate (CAGR) indicates the mean annual growth rate over a specified time period.
            
            **Key observations:**
            - Manufacturers with higher CAGR show stronger sustained growth over the period
            - The horizontal red line represents zero growth - any manufacturer above this line is growing
            - The dotted green line shows the industry average CAGR among these top manufacturers
            """)
        else:
            st.warning("Not enough data to calculate CAGR with the current filters.")
    
    with tabs[1]:
        if not result_df.empty:
            st.plotly_chart(create_sales_trend_chart(result_df), use_container_width=True)
            
            # Add explanatory text
            st.markdown("""
            ### Sales Trend Insights
            
            This chart shows the absolute sales numbers for each manufacturer over the years.
            
            **Key observations:**
            - The steepness of each line indicates year-over-year growth
            - Manufacturers with consistently upward trajectories demonstrate sustainable growth
            - Large jumps between years may indicate successful model launches or policy impacts
            """)
        else:
            st.warning("Not enough data to display sales trends with the current filters.")
    
    with tabs[2]:
        if not result_df.empty:
            st.plotly_chart(create_combined_chart(result_df), use_container_width=True)
            
            # Add explanatory text
            st.markdown("""
            ### Combined Analysis Insights
            
            This visualization overlays annual sales with CAGR to show both absolute performance and growth rates.
            
            **Key observations:**
            - Manufacturers with both high bars and high CAGR line values are market leaders
            - Some manufacturers may have lower absolute sales but higher growth rates, indicating potential future leaders
            - The relationship between sales volume and growth rate reveals competitive positioning
            """)
        else:
            st.warning("Not enough data for combined analysis with the current filters.")
    
    with tabs[3]:
        if not result_df.empty:
            st.plotly_chart(create_market_share_chart(result_df), use_container_width=True)
            
            # Add explanatory text
            st.markdown("""
            ### Market Share Evolution Insights
            
            This stacked bar chart shows how market share distribution has changed over time among top manufacturers.
            
            **Key observations:**
            - Changes in the relative size of each segment indicate shifts in competitive positioning
            - Market consolidation or fragmentation trends become visible over time
            - Manufacturers with growing segments are gaining competitive advantage
            """)
        else:
            st.warning("Not enough data to analyze market share with the current filters.")
    
    with tabs[4]:
        st.subheader("Detailed Performance Data")
        
        # Format the data for display
        display_df = detailed_df.copy()
        
        # Format sales columns with commas
        sales_cols = [col for col in display_df.columns if 'Sales' in col and 'Market' not in col]
        for col in sales_cols:
            display_df[col] = display_df[col].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "N/A")
            display_df[col] = display_df[col].astype(str)
        
        # Format percentage columns
        pct_cols = [col for col in display_df.columns if '%' in col]
        for col in pct_cols:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
            display_df[col] = display_df[col].astype(str)
            
        # Display the table
        st.dataframe(display_df, use_container_width=True)
        
        # Add download button for the data
        csv = detailed_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"top_{top_n}_ev_makers_cagr_{start_year}_{end_year}.csv",
            mime="text/csv",
        )
    
    # Methodology section
    with st.expander("Analysis Methodology", expanded=False):
        st.markdown("""
        ### CAGR Calculation Methodology
        
        The Compounded Annual Growth Rate (CAGR) is calculated using the formula:
        
        $$CAGR = \\left(\\frac{\\text{Ending Value (2024)}}{\\text{Beginning Value (2022)}}\\right)^{\\frac{1}{\\text{Number of Years}}} - 1$$
        
        Where:
        - Ending Value: Sales in the final year (default: 2024)
        - Beginning Value: Sales in the starting year (default: 2022)
        - Number of Years: Difference between ending and beginning years (default: 2)
        
        The result is multiplied by 100 to express as a percentage.
        
        ### Data Processing Steps:
        
        1. Load the EV sales data for all manufacturers
        2. Filter for only 4-wheeler manufacturers
        3. Calculate total sales across all years to identify top manufacturers
        4. Calculate CAGR for each manufacturer between selected years
        5. Calculate additional metrics like year-over-year growth and market share
        6. Sort results by CAGR to identify highest-growth manufacturers
        
        > Note: Manufacturers with zero sales in the starting year are excluded from CAGR calculations to avoid division by zero.
        """)
    
    # Footer with data source information
    st.markdown("---")
    st.caption(f"Data source: EV Sales by Makers data from {EV_SALES_BY_MAKERS_PATH}. Analysis as of August 2025.")

def main():
    create_dashboard()

if __name__ == "__main__":
    main()
