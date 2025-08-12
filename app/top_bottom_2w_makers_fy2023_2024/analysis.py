import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import sys

# Add the project root to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def load_data():
    """
    Load and preprocess the EV sales data.
    """
    try:
        # Load the dataset
        df = pd.read_csv('data/processed/ev_sales_by_makers_cleaned_20250806.csv')
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter for 2-Wheelers
        df = df[df['vehicle_category'] == '2-Wheelers']
        
        # Add fiscal year column (April to March)
        df['fiscal_year'] = df['date'].apply(lambda x: x.year if x.month >= 4 else x.year - 1)
        df['fiscal_year_label'] = df['fiscal_year'].apply(lambda x: f'FY {x}-{x+1}')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def calculate_top_bottom_makers(df, fiscal_year, num_makers=3):
    """
    Calculate the top and bottom makers for a given fiscal year.
    
    Args:
        df: DataFrame with EV sales data
        fiscal_year: Fiscal year to analyze
        num_makers: Number of top/bottom makers to return
        
    Returns:
        top_makers: DataFrame with top makers
        bottom_makers: DataFrame with bottom makers
    """
    # Filter for the specified fiscal year
    yearly_df = df[df['fiscal_year'] == fiscal_year]
    
    # Group by maker and calculate total sales
    maker_sales = yearly_df.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
    
    # Filter out makers with zero sales
    maker_sales = maker_sales[maker_sales['electric_vehicles_sold'] > 0]
    
    if maker_sales.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Sort by sales
    maker_sales = maker_sales.sort_values('electric_vehicles_sold', ascending=False)
    
    # Get top and bottom makers
    top_makers = maker_sales.head(num_makers)
    bottom_makers = maker_sales.tail(num_makers)
    
    return top_makers, bottom_makers

def plot_leaders_laggards(top_df, bottom_df, fiscal_year, title):
    """
    Create a comparative bar chart of leaders vs laggards
    
    Args:
        top_df: DataFrame with top makers
        bottom_df: DataFrame with bottom makers
        fiscal_year: Fiscal year being analyzed
        title: Title for the plot
        
    Returns:
        fig: Plotly figure
    """
    # Combine data and add a category
    top_df = top_df.copy()
    bottom_df = bottom_df.copy()
    
    top_df['category'] = 'Leaders'
    bottom_df['category'] = 'Laggards'
    
    combined_df = pd.concat([top_df, bottom_df])
    
    # Create figure
    fig = px.bar(
        combined_df,
        x='maker',
        y='electric_vehicles_sold',
        color='category',
        title=title,
        color_discrete_map={'Leaders': '#1E88E5', 'Laggards': '#FB8C00'},
        barmode='group',
        text='electric_vehicles_sold'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Manufacturer',
        yaxis_title='Total Units Sold',
        legend_title='Category',
        height=500
    )
    
    # Add text labels
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    
    return fig

def plot_market_share(df, makers, fiscal_year, title):
    """
    Plot market share pie chart for selected makers in a given fiscal year.
    
    Args:
        df: DataFrame with EV sales data
        makers: List of makers to include
        fiscal_year: Fiscal year to analyze
        title: Title for the plot
        
    Returns:
        fig: Plotly figure
    """
    # Filter data for selected fiscal year and makers
    filtered_df = df[(df['fiscal_year'] == fiscal_year) & (df['maker'].isin(makers))]
    
    # Group by maker
    maker_sales = filtered_df.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
    
    # Calculate market share
    total_sales = maker_sales['electric_vehicles_sold'].sum()
    maker_sales['market_share'] = maker_sales['electric_vehicles_sold'] / total_sales * 100
    
    # Create figure
    fig = px.pie(maker_sales, 
                values='market_share', 
                names='maker',
                title=title,
                hover_data=['electric_vehicles_sold'])
    
    # Update layout
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    return fig

def plot_yoy_comparison(df, makers, fiscal_years, title):
    """
    Plot year-over-year comparison for selected makers across fiscal years.
    
    Args:
        df: DataFrame with EV sales data
        makers: List of makers to include
        fiscal_years: List of fiscal years to compare
        title: Title for the plot
        
    Returns:
        fig: Plotly figure
    """
    # Filter data for selected fiscal years and makers
    filtered_df = df[(df['fiscal_year'].isin(fiscal_years)) & (df['maker'].isin(makers))]
    
    # Group by maker and fiscal year
    yearly_df = filtered_df.groupby(['maker', 'fiscal_year_label'])['electric_vehicles_sold'].sum().reset_index()
    
    # Create figure
    fig = px.bar(yearly_df, 
                x='maker', 
                y='electric_vehicles_sold', 
                color='fiscal_year_label',
                barmode='group',
                title=title,
                text_auto=True)
    
    # Update layout
    fig.update_layout(
        xaxis_title='Manufacturer',
        yaxis_title='Units Sold',
        legend_title='Fiscal Year',
        height=500
    )
    
    # Update text position
    fig.update_traces(texttemplate='%{y:,}', textposition='outside')
    
    return fig

def plot_market_dominance(top_df, bottom_df, fiscal_year, title):
    """
    Create a visual showing the market dominance of leaders vs laggards.
    
    Args:
        top_df: DataFrame with top makers
        bottom_df: DataFrame with bottom makers
        fiscal_year: Fiscal year being analyzed
        title: Title for the plot
        
    Returns:
        fig: Plotly figure
    """
    # Calculate totals
    top_total = top_df['electric_vehicles_sold'].sum()
    bottom_total = bottom_df['electric_vehicles_sold'].sum()
    
    # Create data for plot
    labels = ['Leaders', 'Laggards']
    values = [top_total, bottom_total]
    
    # Create figure
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        marker_colors=['#1E88E5', '#FB8C00']
    )])
    
    # Update layout
    fig.update_layout(
        title=title,
        height=400,
        annotations=[{
            'text': f'Total: {top_total + bottom_total:,}',
            'x': 0.5,
            'y': 0.5,
            'font_size': 15,
            'showarrow': False
        }]
    )
    
    return fig

def plot_quadrant_leaders_laggards(top_dict, bottom_dict, num_makers=3):
    """
    Create a subplot visualization showing top and bottom performers in each fiscal year.
    
    Args:
        top_dict: Dictionary with top makers for each fiscal year
        bottom_dict: Dictionary with bottom makers for each fiscal year
        num_makers: Number of top/bottom makers
        
    Returns:
        fig: Plotly figure
    """
    # Create a subplot with 2 rows and 2 columns
    fig = make_subplots(
        rows=2, 
        cols=2,
        subplot_titles=(
            'Top 3 Manufacturers - FY 2023', 
            'Top 3 Manufacturers - FY 2024',
            'Bottom 3 Manufacturers - FY 2023', 
            'Bottom 3 Manufacturers - FY 2024'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Define color schemes
    top_colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    bottom_colors = ['#d62728', '#9467bd', '#8c564b']
    
    # Add bars for top performers in FY 2023
    for idx, (_, row) in enumerate(top_dict['FY 2023_top'].iterrows()):
        fig.add_trace(
            go.Bar(
                x=[row['maker']], 
                y=[row['electric_vehicles_sold']],
                text=[f"{row['electric_vehicles_sold']:,}"],
                textposition='auto',
                name=row['maker'],
                marker_color=top_colors[idx % len(top_colors)],
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Add bars for top performers in FY 2024
    for idx, (_, row) in enumerate(top_dict['FY 2024_top'].iterrows()):
        fig.add_trace(
            go.Bar(
                x=[row['maker']], 
                y=[row['electric_vehicles_sold']],
                text=[f"{row['electric_vehicles_sold']:,}"],
                textposition='auto',
                name=row['maker'],
                marker_color=top_colors[idx % len(top_colors)],
                showlegend=False
            ),
            row=1, col=2
        )
    
    # Add bars for bottom performers in FY 2023
    for idx, (_, row) in enumerate(bottom_dict['FY 2023_bottom'].iterrows()):
        fig.add_trace(
            go.Bar(
                x=[row['maker']], 
                y=[row['electric_vehicles_sold']],
                text=[f"{row['electric_vehicles_sold']:,}"],
                textposition='auto',
                name=row['maker'],
                marker_color=bottom_colors[idx % len(bottom_colors)],
                showlegend=False
            ),
            row=2, col=1
        )
    
    # Add bars for bottom performers in FY 2024
    for idx, (_, row) in enumerate(bottom_dict['FY 2024_bottom'].iterrows()):
        fig.add_trace(
            go.Bar(
                x=[row['maker']], 
                y=[row['electric_vehicles_sold']],
                text=[f"{row['electric_vehicles_sold']:,}"],
                textposition='auto',
                name=row['maker'],
                marker_color=bottom_colors[idx % len(bottom_colors)],
                showlegend=False
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        title_text=f'<b>India\'s Electric 2-Wheeler Market: The Leaders and Laggards</b>',
        title_x=0.5,
        height=800,
        template='plotly_white',
        annotations=[
            dict(
                text="<b>The Top Performers:</b> OLA ELECTRIC dominated both years, with TVS making significant gains in FY 2024",
                showarrow=False,
                x=0.5,
                y=0.48,
                xref="paper",
                yref="paper",
                font=dict(size=12)
            ),
            dict(
                text="<b>The Struggling Manufacturers:</b> JOY E-BIKE and PURE EV remained among the bottom performers in both fiscal years",
                showarrow=False,
                x=0.5,
                y=-0.08,
                xref="paper",
                yref="paper",
                font=dict(size=12)
            )
        ]
    )
    
    # Update axes
    fig.update_xaxes(title_text=None)
    fig.update_yaxes(title_text='Electric Vehicles Sold', row=1, col=1)
    fig.update_yaxes(title_text='Electric Vehicles Sold', row=2, col=1)
    
    return fig

def run_app():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(layout="wide", page_title="2-Wheeler EV Market Analysis")
    
    st.title("🏍️ Top and Bottom 2-Wheeler EV Makers Analysis")
    st.write("Analysis of leaders and laggards in the 2-wheeler EV market in India for fiscal years 2023 and 2024.")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("Failed to load data. Please check the data file path.")
        return
        
    # Alternative approach directly with dates for exact fiscal years
    # Preprocess for FY 2023 and FY 2024 specific analysis
    two_wheelers = df.copy()
    
    # Extract fiscal year (April to March)
    two_wheelers['fiscal_year_label'] = two_wheelers['date'].apply(
        lambda x: f"FY {x.year}" if x.month < 4 else f"FY {x.year + 1}"
    )
    
    # Get unique fiscal years - for both naming formats
    fiscal_years = sorted(df['fiscal_year'].unique())
    fiscal_years_labels = sorted(two_wheelers['fiscal_year_label'].unique())
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # View type selection
    view_type = st.sidebar.radio(
        "Select Analysis View",
        ["Original Analysis", "Quadrant View (FY 2023-2024)"],
        index=0
    )
    
    # Initialize the dictionaries that will be used in both views
    total_sales_by_year = {}
    top_makers_by_year = {}
    bottom_makers_by_year = {}
    
    if view_type == "Original Analysis":
        # Select fiscal years for analysis
        selected_fiscal_years = st.sidebar.multiselect(
            "Select Fiscal Years",
            options=fiscal_years,
            default=[2022, 2023] if 2022 in fiscal_years and 2023 in fiscal_years else fiscal_years[-2:],
            format_func=lambda x: f"FY {x}-{x+1}"
        )
        
        # Number of top/bottom makers to show
        num_makers = st.sidebar.slider("Number of Top/Bottom Makers", 1, 10, 3)
        
        if not selected_fiscal_years:
            st.warning("Please select at least one fiscal year.")
            return
            
        # Calculate the top and bottom makers for each selected fiscal year
        for fy in selected_fiscal_years:
            fy_df = df[df['fiscal_year'] == fy]
            total_sales = fy_df['electric_vehicles_sold'].sum()
            total_sales_by_year[fy] = total_sales
            
            # Calculate top and bottom makers
            top_makers, bottom_makers = calculate_top_bottom_makers(df, fy, num_makers)
            top_makers_by_year[fy] = top_makers
            bottom_makers_by_year[fy] = bottom_makers
            
    else:  # Quadrant view
        # Filter to ensure FY 2023 and FY 2024
        filtered_years = [year for year in fiscal_years_labels if year in ['FY 2023', 'FY 2024']]
        if len(filtered_years) < 2:
            st.error("This analysis requires data for both FY 2023 and FY 2024, but they were not found in the dataset.")
            return
            
        # Number of top/bottom makers to show
        num_makers = st.sidebar.slider("Number of Top/Bottom Makers", 1, 10, 3)
        
        # Set selected_fiscal_years for quadrant view (2022 and 2023)
        selected_fiscal_years = [2022, 2023]
        
        # Process data for quadrant view
        # Filter for fiscal years 2023 and 2024
        two_wheelers_filtered = two_wheelers[
            two_wheelers['fiscal_year_label'].isin(['FY 2023', 'FY 2024'])
        ]
        
        # Group by maker and fiscal year to get total sales
        yearly_sales = two_wheelers_filtered.groupby(['maker', 'fiscal_year_label'])['electric_vehicles_sold'].sum().reset_index()
        
        # Get top and bottom makers for each fiscal year
        top_bottom_dict = {}
        for year in ['FY 2023', 'FY 2024']:
            year_data = yearly_sales[yearly_sales['fiscal_year_label'] == year].sort_values('electric_vehicles_sold', ascending=False)
            
            # Get top and bottom makers
            top_3 = year_data.head(num_makers)
            bottom_3 = year_data.tail(num_makers)
            
            # Store in dictionary
            top_bottom_dict[f'{year}_top'] = top_3
            top_bottom_dict[f'{year}_bottom'] = bottom_3
            
            # Also populate the dictionaries used by the original view for compatibility
            fiscal_year = 2022 if year == 'FY 2023' else 2023
            total_sales = year_data['electric_vehicles_sold'].sum()
            total_sales_by_year[fiscal_year] = total_sales
            top_makers_by_year[fiscal_year] = top_3
            bottom_makers_by_year[fiscal_year] = bottom_3
        
        # Calculate total sales for FY 2023 and FY 2024 for KPIs
        total_fy2023 = two_wheelers_filtered[two_wheelers_filtered['fiscal_year_label'] == 'FY 2023']['electric_vehicles_sold'].sum()
        total_fy2024 = two_wheelers_filtered[two_wheelers_filtered['fiscal_year_label'] == 'FY 2024']['electric_vehicles_sold'].sum()
        
        # Calculate growth rate
        overall_growth = ((total_fy2024 - total_fy2023) / total_fy2023 * 100) if total_fy2023 > 0 else 0
        
        # Calculate Top Performers metrics
        top_fy2023_sales = top_bottom_dict['FY 2023_top']['electric_vehicles_sold'].sum()
        top_fy2024_sales = top_bottom_dict['FY 2024_top']['electric_vehicles_sold'].sum()
        top_growth = ((top_fy2024_sales - top_fy2023_sales) / top_fy2023_sales * 100) if top_fy2023_sales > 0 else 0
        
        # Calculate Bottom Performers metrics
        bottom_fy2023_sales = top_bottom_dict['FY 2023_bottom']['electric_vehicles_sold'].sum()
        bottom_fy2024_sales = top_bottom_dict['FY 2024_bottom']['electric_vehicles_sold'].sum()
        bottom_growth = ((bottom_fy2024_sales - bottom_fy2023_sales) / bottom_fy2023_sales * 100) if bottom_fy2023_sales > 0 else 0
        
        # Calculate market concentration
        market_concentration_2023 = (top_fy2023_sales / bottom_fy2023_sales) if bottom_fy2023_sales > 0 else float('inf')
        market_concentration_2024 = (top_fy2024_sales / bottom_fy2024_sales) if bottom_fy2024_sales > 0 else float('inf')
        
        # Market share of top performers
        top_share_2023 = (top_fy2023_sales / total_fy2023 * 100) if total_fy2023 > 0 else 0
        top_share_2024 = (top_fy2024_sales / total_fy2024 * 100) if total_fy2024 > 0 else 0
        
        # Display Market Overview KPIs outside the tabs
        st.header("📊 Market Overview")
        
        # Market metrics row
        market_cols = st.columns(4)
        with market_cols[0]:
            st.metric("FY 2023 Total Sales", f"{total_fy2023:,} units")
        with market_cols[1]:
            st.metric("FY 2024 Total Sales", f"{total_fy2024:,} units")
        with market_cols[2]:
            st.metric("YoY Market Growth", f"{overall_growth:.1f}%", delta=f"{overall_growth:.1f}%")
        with market_cols[3]:
            conc_change = market_concentration_2024 - market_concentration_2023
            if market_concentration_2023 != float('inf') and market_concentration_2024 != float('inf'):
                conc_delta = f"{conc_change:.1f}x"
                st.metric("Market Concentration Change", conc_delta, delta=conc_delta)
            else:
                st.metric("Market Concentration", "High", "Leaders dominate")
        
        # Leaders vs Laggards comparison
        st.subheader("🏆 Leaders vs Laggards Performance")
        performance_cols = st.columns(4)
        
        with performance_cols[0]:
            st.metric("Top Performers FY 2023", f"{top_fy2023_sales:,} units", f"{top_share_2023:.1f}% share")
        with performance_cols[1]:
            st.metric("Top Performers FY 2024", f"{top_fy2024_sales:,} units", f"{top_share_2024:.1f}% share")
        with performance_cols[2]:
            st.metric("Bottom Performers FY 2023", f"{bottom_fy2023_sales:,} units", f"{(bottom_fy2023_sales/total_fy2023*100):.1f}% share")
        with performance_cols[3]:
            st.metric("Bottom Performers FY 2024", f"{bottom_fy2024_sales:,} units", f"{(bottom_fy2024_sales/total_fy2024*100):.1f}% share")
            
        # Create tabs for the Quadrant View - removing the KPIs tab
        quadrant_tabs = st.tabs(["Overview", "Comparison Tables", "Market Insights"])
        
        # Overview Tab - Main visualization and basic details
        with quadrant_tabs[0]:
            # Create the quadrant visualization
            fig = plot_quadrant_leaders_laggards(top_bottom_dict, top_bottom_dict, num_makers)
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a table to show the exact numbers
            st.subheader("Detailed Comparison: Top & Bottom Performers (2-Wheelers)")
            
            # Combine all data for a summary table
            all_highlighted = pd.concat([
                top_bottom_dict['FY 2023_top'].assign(position="Top 3"),
                top_bottom_dict['FY 2024_top'].assign(position="Top 3"),
                top_bottom_dict['FY 2023_bottom'].assign(position="Bottom 3"),
                top_bottom_dict['FY 2024_bottom'].assign(position="Bottom 3")
            ])
            
            # Pivot for better comparison
            pivot_table = all_highlighted.pivot_table(
                index=['position', 'maker'], 
                columns=['fiscal_year_label'],
                values='electric_vehicles_sold',
                aggfunc='sum'
            ).reset_index()
            
            # Calculate year-over-year change
            if 'FY 2023' in pivot_table.columns and 'FY 2024' in pivot_table.columns:
                # Handle division by zero and missing values
                pivot_table['YoY Change'] = np.where(
                    (pivot_table['FY 2023'] != 0) & (pivot_table['FY 2023'].notna()) & (pivot_table['FY 2024'].notna()),
                    (pivot_table['FY 2024'] - pivot_table['FY 2023']) / pivot_table['FY 2023'] * 100,
                    np.where(pivot_table['FY 2024'] > 0, float('inf'), 0)
                )
            
            # Sort and display
            pivot_table = pivot_table.sort_values(['position', 'FY 2024'], ascending=[True, False])
            
            # Handle missing values - use 0 instead of '-' for numeric columns
            formatted_pivot = pivot_table.fillna(0)
            
            # Display the table
            st.dataframe(
                formatted_pivot.style.format({
                    'FY 2023': lambda x: format_with_check(x, '{:,.0f}'),
                    'FY 2024': lambda x: format_with_check(x, '{:,.0f}'),
                    'YoY Change': lambda x: format_with_check(x, '{:+.1f}%') if x != 0 and not isinstance(x, str) else '-'
                }),
                use_container_width=True
            )
        
        # Comparison Tables tab is now the first tab (index 0)
        
        # Comparison Tables Tab - Detailed tables for deeper analysis
        with quadrant_tabs[1]:
            st.subheader("📋 Detailed Comparison Tables")
            
            # Create a selector for different table views
            table_view = st.radio(
                "Select Table View",
                ["Top Performers", "Bottom Performers", "Market Leaders Ranking", "Year-over-Year Growth"],
                horizontal=True
            )
            
            # Group data for market maker analysis
            maker_yearly_sales = two_wheelers_filtered.groupby(['maker', 'fiscal_year_label'])['electric_vehicles_sold'].sum().reset_index()
            maker_pivot = maker_yearly_sales.pivot(index='maker', columns='fiscal_year_label', values='electric_vehicles_sold').reset_index().fillna(0)
            
            # Add YoY growth column
            if 'FY 2023' in maker_pivot.columns and 'FY 2024' in maker_pivot.columns:
                maker_pivot['YoY Growth (%)'] = np.where(
                    maker_pivot['FY 2023'] > 0,
                    (maker_pivot['FY 2024'] - maker_pivot['FY 2023']) / maker_pivot['FY 2023'] * 100,
                    np.where(maker_pivot['FY 2024'] > 0, float('inf'), 0)
                )
            
            if table_view == "Top Performers":
                # Show detailed table of top performers
                st.markdown("### Top Performers Analysis")
                top_makers = pd.concat([
                    top_bottom_dict['FY 2023_top'][['maker']],
                    top_bottom_dict['FY 2024_top'][['maker']]
                ])['maker'].unique()
                
                # Filter pivot table for top makers
                top_pivot = maker_pivot[maker_pivot['maker'].isin(top_makers)].sort_values('FY 2024', ascending=False)
                
                # Add market share columns
                top_pivot['FY 2023 Market Share (%)'] = (top_pivot['FY 2023'] / total_fy2023 * 100).round(2)
                top_pivot['FY 2024 Market Share (%)'] = (top_pivot['FY 2024'] / total_fy2024 * 100).round(2)
                top_pivot['Market Share Change (pp)'] = (top_pivot['FY 2024 Market Share (%)'] - top_pivot['FY 2023 Market Share (%)']).round(2)
                
                # Display formatted table
                st.dataframe(
                    top_pivot.style.format({
                        'FY 2023': '{:,.0f}',
                        'FY 2024': '{:,.0f}',
                        'YoY Growth (%)': '{:+.1f}%',
                        'FY 2023 Market Share (%)': '{:.2f}%',
                        'FY 2024 Market Share (%)': '{:.2f}%',
                        'Market Share Change (pp)': '{:+.2f}'
                    }),
                    use_container_width=True
                )
                
                st.markdown("**Note:** pp = percentage points")
                
            elif table_view == "Bottom Performers":
                # Show detailed table of bottom performers
                st.markdown("### Bottom Performers Analysis")
                bottom_makers = pd.concat([
                    top_bottom_dict['FY 2023_bottom'][['maker']],
                    top_bottom_dict['FY 2024_bottom'][['maker']]
                ])['maker'].unique()
                
                # Filter pivot table for bottom makers
                bottom_pivot = maker_pivot[maker_pivot['maker'].isin(bottom_makers)].sort_values('FY 2024')
                
                # Add market share columns
                bottom_pivot['FY 2023 Market Share (%)'] = (bottom_pivot['FY 2023'] / total_fy2023 * 100).round(2)
                bottom_pivot['FY 2024 Market Share (%)'] = (bottom_pivot['FY 2024'] / total_fy2024 * 100).round(2)
                bottom_pivot['Market Share Change (pp)'] = (bottom_pivot['FY 2024 Market Share (%)'] - bottom_pivot['FY 2023 Market Share (%)']).round(2)
                
                # Display formatted table
                st.dataframe(
                    bottom_pivot.style.format({
                        'FY 2023': '{:,.0f}',
                        'FY 2024': '{:,.0f}',
                        'YoY Growth (%)': '{:+.1f}%',
                        'FY 2023 Market Share (%)': '{:.2f}%',
                        'FY 2024 Market Share (%)': '{:.2f}%',
                        'Market Share Change (pp)': '{:+.2f}'
                    }),
                    use_container_width=True
                )
                
                st.markdown("**Note:** pp = percentage points")
                
            elif table_view == "Market Leaders Ranking":
                # Show ranking changes across years
                st.markdown("### Market Ranking Changes")
                
                # Create ranking for both years
                fy2023_ranking = maker_yearly_sales[maker_yearly_sales['fiscal_year_label'] == 'FY 2023'].sort_values('electric_vehicles_sold', ascending=False)
                fy2023_ranking['FY 2023 Rank'] = range(1, len(fy2023_ranking) + 1)
                
                fy2024_ranking = maker_yearly_sales[maker_yearly_sales['fiscal_year_label'] == 'FY 2024'].sort_values('electric_vehicles_sold', ascending=False)
                fy2024_ranking['FY 2024 Rank'] = range(1, len(fy2024_ranking) + 1)
                
                # Merge rankings
                rankings = pd.merge(
                    fy2023_ranking[['maker', 'FY 2023 Rank', 'electric_vehicles_sold']].rename(columns={'electric_vehicles_sold': 'FY 2023 Sales'}),
                    fy2024_ranking[['maker', 'FY 2024 Rank', 'electric_vehicles_sold']].rename(columns={'electric_vehicles_sold': 'FY 2024 Sales'}),
                    on='maker',
                    how='outer'
                ).fillna({'FY 2023 Rank': 999, 'FY 2024 Rank': 999, 'FY 2023 Sales': 0, 'FY 2024 Sales': 0})
                
                # Calculate rank change
                rankings['Rank Change'] = rankings['FY 2023 Rank'] - rankings['FY 2024 Rank']
                
                # Sort by current rank
                rankings = rankings.sort_values('FY 2024 Rank')
                
                # Format ranks as integers
                rankings['FY 2023 Rank'] = rankings['FY 2023 Rank'].astype(int)
                rankings['FY 2024 Rank'] = rankings['FY 2024 Rank'].astype(int)
                
                # Replace rank 999 with 'N/A' for display
                rankings['FY 2023 Rank'] = rankings['FY 2023 Rank'].replace(999, None)
                rankings['FY 2024 Rank'] = rankings['FY 2024 Rank'].replace(999, None)
                
                # Display formatted table
                st.dataframe(
                    rankings.style.format({
                        'FY 2023 Sales': '{:,.0f}',
                        'FY 2024 Sales': '{:,.0f}',
                        'Rank Change': '{:+.0f}'
                    }),
                    use_container_width=True
                )
                
                # Add note about rank change colors
                st.info("💡 Positive rank changes indicate improvement in ranking (moving up), negative values show decline in position.")
                
                st.markdown("**Note:** Positive rank change indicates improvement in ranking.")
                
            elif table_view == "Year-over-Year Growth":
                # Show growth champions and declining manufacturers
                st.markdown("### Growth Champions vs Declining Manufacturers")
                
                # Calculate growth for all manufacturers
                growth_df = maker_pivot.copy()
                
                # Filter for manufacturers present in both years
                both_years_df = growth_df[(growth_df['FY 2023'] > 0) & (growth_df['FY 2024'] > 0)].copy()
                
                # Sort by growth rate
                growth_champions = both_years_df.sort_values('YoY Growth (%)', ascending=False).head(10)
                declining_makers = both_years_df.sort_values('YoY Growth (%)', ascending=True).head(10)
                
                # Display growth champions
                st.markdown("#### Top 10 Growth Champions")
                st.dataframe(
                    growth_champions.style.format({
                        'FY 2023': '{:,.0f}',
                        'FY 2024': '{:,.0f}',
                        'YoY Growth (%)': '{:+.1f}%'
                    }),
                    use_container_width=True
                )
                
                # Display declining manufacturers
                st.markdown("#### Top 10 Declining Manufacturers")
                st.dataframe(
                    declining_makers.style.format({
                        'FY 2023': '{:,.0f}',
                        'FY 2024': '{:,.0f}',
                        'YoY Growth (%)': '{:+.1f}%'
                    }),
                    use_container_width=True
                )
                
                # Add a note about growth rates
                st.info("💡 Growth champions show impressive YoY increases, while declining manufacturers experienced negative growth.")
        
        # Market Insights Tab - Visual insights and commentary
        with quadrant_tabs[2]:
            st.subheader("🔍 Market Insights")
            
            # Market Share Visualization
            st.markdown("### Market Share Evolution")
            
            # Create a pie chart comparison of top makers in both years
            pie_cols = st.columns(2)
            
            # FY 2023 Market Share
            with pie_cols[0]:
                fy2023_data = two_wheelers_filtered[two_wheelers_filtered['fiscal_year_label'] == 'FY 2023']
                top_makers_2023 = top_bottom_dict['FY 2023_top']['maker'].tolist()
                
                # Group data by maker
                maker_share_2023 = fy2023_data.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
                
                # Add "Others" category for non-top makers
                others_sales_2023 = maker_share_2023[~maker_share_2023['maker'].isin(top_makers_2023)]['electric_vehicles_sold'].sum()
                
                # Filter for top makers and add others
                top_share_2023 = maker_share_2023[maker_share_2023['maker'].isin(top_makers_2023)]
                top_share_2023 = pd.concat([
                    top_share_2023,
                    pd.DataFrame({'maker': ['Others'], 'electric_vehicles_sold': [others_sales_2023]})
                ])
                
                # Create pie chart
                fig_2023 = px.pie(
                    top_share_2023, 
                    values='electric_vehicles_sold', 
                    names='maker',
                    title=f'FY 2023 Market Share'
                )
                fig_2023.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_2023, use_container_width=True)
            
            # FY 2024 Market Share
            with pie_cols[1]:
                fy2024_data = two_wheelers_filtered[two_wheelers_filtered['fiscal_year_label'] == 'FY 2024']
                top_makers_2024 = top_bottom_dict['FY 2024_top']['maker'].tolist()
                
                # Group data by maker
                maker_share_2024 = fy2024_data.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
                
                # Add "Others" category for non-top makers
                others_sales_2024 = maker_share_2024[~maker_share_2024['maker'].isin(top_makers_2024)]['electric_vehicles_sold'].sum()
                
                # Filter for top makers and add others
                top_share_2024 = maker_share_2024[maker_share_2024['maker'].isin(top_makers_2024)]
                top_share_2024 = pd.concat([
                    top_share_2024,
                    pd.DataFrame({'maker': ['Others'], 'electric_vehicles_sold': [others_sales_2024]})
                ])
                
                # Create pie chart
                fig_2024 = px.pie(
                    top_share_2024, 
                    values='electric_vehicles_sold', 
                    names='maker',
                    title=f'FY 2024 Market Share'
                )
                fig_2024.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_2024, use_container_width=True)
            
            # Market Concentration Visualization
            st.markdown("### Market Concentration Analysis")
            
            # Create data for concentration chart
            concentration_data = pd.DataFrame({
                'Category': ['Top 3', 'Others'],
                'FY 2023': [top_fy2023_sales, total_fy2023 - top_fy2023_sales],
                'FY 2024': [top_fy2024_sales, total_fy2024 - top_fy2024_sales]
            })
            
            # Melt data for bar chart
            concentration_melted = pd.melt(
                concentration_data,
                id_vars=['Category'],
                value_vars=['FY 2023', 'FY 2024'],
                var_name='Fiscal Year',
                value_name='Sales'
            )
            
            # Create market concentration chart
            fig_concentration = px.bar(
                concentration_melted,
                x='Fiscal Year',
                y='Sales',
                color='Category',
                barmode='group',
                title='Market Concentration: Top 3 vs Others',
                color_discrete_map={'Top 3': '#1E88E5', 'Others': '#FB8C00'}
            )
            
            # Add percentage annotations
            for i, fiscal_year in enumerate(['FY 2023', 'FY 2024']):
                total = concentration_data[fiscal_year].sum()
                top_pct = concentration_data.loc[0, fiscal_year] / total * 100
                other_pct = concentration_data.loc[1, fiscal_year] / total * 100
                
                fig_concentration.add_annotation(
                    x=fiscal_year,
                    y=concentration_data.loc[0, fiscal_year],
                    text=f"{top_pct:.1f}%",
                    showarrow=False,
                    yshift=10
                )
                
                fig_concentration.add_annotation(
                    x=fiscal_year,
                    y=concentration_data.loc[1, fiscal_year],
                    text=f"{other_pct:.1f}%",
                    showarrow=False,
                    yshift=10
                )
            
            st.plotly_chart(fig_concentration, use_container_width=True)
            
            # Key Insights
            st.markdown("### Key Market Insights")
            st.markdown("""
            > **Market Dynamics:**
            > - 🚀 **Market Leaders:** OLA ELECTRIC dominated both fiscal years, with TVS making significant gains in FY 2024.
            > - 📉 **Struggling Manufacturers:** JOY E-BIKE and PURE EV remained among the bottom performers in both fiscal years.
            > - 🔍 **Market Concentration:** The top performers collectively sold many times more units than the bottom performers.
            > - 📊 **Industry Growth:** The 2-wheeler EV market showed robust growth, with leaders consolidating their positions.
            > - 💼 **Competitive Landscape:** New entrants are finding it increasingly difficult to compete with established players.
            > - 🏆 **Success Factors:** Product range, distribution network, and brand recognition appear to be key success factors.
            """)
        
        # Display selected filters applied
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Applied Filters:**")
        st.sidebar.markdown(f"- Number of top/bottom makers: {num_makers}")
        
        # Return early since we've completed the quadrant view
        return
    
    # In the Original Analysis view, handle the fiscal year selection
    if view_type == "Original Analysis":
        # Display summary KPIs for all selected years
        st.header("Market Overview")
        
        kpi_cols = st.columns(len(selected_fiscal_years))
        
        for i, fy in enumerate(selected_fiscal_years):
            # KPIs
            with kpi_cols[i]:
                total_sales = total_sales_by_year.get(fy, 0)
                st.metric(f"FY {fy}-{fy+1}", f"{total_sales:,} units")
                
                # Top maker
                if fy in top_makers_by_year and not top_makers_by_year[fy].empty:
                    top_maker = top_makers_by_year[fy].iloc[0]
                    top_share = (top_maker['electric_vehicles_sold'] / total_sales * 100).round(1)
                    st.metric("Top Maker", f"{top_maker['maker']}", f"{top_share}% share")
    
    # Create tabs for visualization
    tab1, tab2, tab3 = st.tabs(["Leaders vs Laggards", "Market Share", "Year Comparison"])
    
    # Leaders vs Laggards tab
    with tab1:
        st.subheader("Leaders vs Laggards Comparison")
        
        # Select year for analysis
        year_for_analysis = st.selectbox(
            "Select Fiscal Year",
            options=selected_fiscal_years,
            format_func=lambda x: f"FY {x}-{x+1}",
            key="leader_year"
        )
        
        if year_for_analysis in top_makers_by_year:
            top_makers = top_makers_by_year[year_for_analysis]
            bottom_makers = bottom_makers_by_year[year_for_analysis]
            
            # Plot leaders vs laggards
            title = f"Top vs Bottom {num_makers} 2-Wheeler EV Makers"
            if year_for_analysis is not None:
                title = f"Top vs Bottom {num_makers} 2-Wheeler EV Makers (FY {year_for_analysis}-{int(year_for_analysis)+1})"
                
            fig = plot_leaders_laggards(
                top_makers, 
                bottom_makers,
                year_for_analysis,
                title
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show market dominance
            dominance_fig = plot_market_dominance(
                top_makers,
                bottom_makers,
                year_for_analysis,
                f"Market Share: Top {num_makers} vs Bottom {num_makers} Makers"
            )
            st.plotly_chart(dominance_fig, use_container_width=True)
            
            # Calculate and display key metrics
            top_total = top_makers['electric_vehicles_sold'].sum()
            bottom_total = bottom_makers['electric_vehicles_sold'].sum()
            total = top_total + bottom_total
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Leaders Total Sales", f"{top_total:,} units", f"{(top_total/total*100):.1f}% of selection")
            with col2:
                st.metric("Laggards Total Sales", f"{bottom_total:,} units", f"{(bottom_total/total*100):.1f}% of selection")
            with col3:
                if bottom_total > 0:
                    st.metric("Market Concentration", f"{(top_total/bottom_total):.1f}x", "Leaders vs Laggards")
                else:
                    st.metric("Market Concentration", "∞", "Leaders dominate completely")
            
            # Data tables
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Top {num_makers} Manufacturers")
                st.dataframe(top_makers[['maker', 'electric_vehicles_sold']].rename(
                    columns={'maker': 'Manufacturer', 'electric_vehicles_sold': 'Units Sold'}
                ), use_container_width=True)
            
            with col2:
                st.subheader(f"Bottom {num_makers} Manufacturers")
                st.dataframe(bottom_makers[['maker', 'electric_vehicles_sold']].rename(
                    columns={'maker': 'Manufacturer', 'electric_vehicles_sold': 'Units Sold'}
                ), use_container_width=True)
    
    # Market Share tab
    with tab2:
        st.subheader("Market Share Analysis")
        
        # Select year for market share analysis
        year_for_share = st.selectbox(
            "Select Fiscal Year",
            options=selected_fiscal_years,
            format_func=lambda x: f"FY {x}-{x+1}",
            key="share_year"
        )
        
        if year_for_share in top_makers_by_year:
            top_makers = top_makers_by_year[year_for_share]
            bottom_makers = bottom_makers_by_year[year_for_share]
            
            # Combine makers for market share analysis
            all_selected_makers = list(pd.concat([top_makers, bottom_makers])['maker'].unique())
            
            # Plot market share
            title = "2-Wheeler EV Market Share"
            if year_for_share is not None:
                title = f"2-Wheeler EV Market Share (FY {year_for_share}-{int(year_for_share)+1})"
                
            fig = plot_market_share(
                df, all_selected_makers, year_for_share,
                title
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Market concentration metrics
            st.subheader("Market Concentration")
            
            # Calculate market share percentages
            market_data = df[df['fiscal_year'] == year_for_share]
            total_market = market_data['electric_vehicles_sold'].sum()
            
            maker_market_share = market_data.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
            maker_market_share['market_share'] = (maker_market_share['electric_vehicles_sold'] / total_market * 100).round(2)
            maker_market_share = maker_market_share.sort_values('market_share', ascending=False)
            
            # Top 3 market share
            top_3_share = maker_market_share.head(3)['market_share'].sum()
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Top 3 Makers Market Share", f"{top_3_share:.1f}%")
                
            with col2:
                top_maker_share = maker_market_share.iloc[0]['market_share']
                st.metric("Market Leader Share", f"{top_maker_share:.1f}%", 
                         f"{maker_market_share.iloc[0]['maker']}")
            
            # Show data table
            st.subheader("Market Share by Manufacturer")
            st.dataframe(
                maker_market_share.rename(columns={
                    'maker': 'Manufacturer',
                    'electric_vehicles_sold': 'Units Sold',
                    'market_share': 'Market Share (%)'
                }),
                use_container_width=True
            )
    
    # Year Comparison tab
    with tab3:
        st.subheader("Year-over-Year Comparison")
        
        if len(selected_fiscal_years) > 1:
            # Get all makers across all selected years
            all_makers = []
            for fy in selected_fiscal_years:
                top = top_makers_by_year[fy]['maker'].tolist()
                bottom = bottom_makers_by_year[fy]['maker'].tolist()
                all_makers.extend(top + bottom)
            
            all_makers = list(set(all_makers))
            
            # Year-over-year comparison chart
            fig = plot_yoy_comparison(
                df, all_makers, selected_fiscal_years, 
                f"2-Wheeler EV Sales by Manufacturer (FY {min(selected_fiscal_years)}-{max(selected_fiscal_years)+1})"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            yearly_data = df[(df['fiscal_year'].isin(selected_fiscal_years)) & 
                           (df['maker'].isin(all_makers))]
            yearly_summary = yearly_data.groupby(['maker', 'fiscal_year_label'])['electric_vehicles_sold'].sum().reset_index()
            yearly_pivot = yearly_summary.pivot(index='maker', columns='fiscal_year_label', values='electric_vehicles_sold').reset_index()
            
            # Add growth calculation if we have at least 2 years
            if len(selected_fiscal_years) >= 2:
                sorted_years = sorted(selected_fiscal_years)
                
                # Calculate growth for each consecutive pair of years
                for i in range(1, len(sorted_years)):
                    prev_year = sorted_years[i-1]
                    curr_year = sorted_years[i]
                    prev_label = f"FY {prev_year}-{prev_year+1}"
                    curr_label = f"FY {curr_year}-{curr_year+1}"
                    
                    # Add growth column if both columns exist
                    if prev_label in yearly_pivot.columns and curr_label in yearly_pivot.columns:
                        growth_col = f"Growth {prev_year}-{curr_year} (%)"
                        yearly_pivot[growth_col] = yearly_pivot.apply(
                            lambda row: calculate_growth_rate(row[prev_label], row[curr_label]),
                            axis=1
                        )
            
            # Sort by most recent year's sales
            recent_year = max(selected_fiscal_years)
            recent_label = f"FY {recent_year}-{recent_year+1}"
            if recent_label in yearly_pivot.columns:
                yearly_pivot = yearly_pivot.sort_values(by=recent_label, ascending=False)
            
            st.dataframe(yearly_pivot, use_container_width=True)
        else:
            st.info("Select at least two fiscal years for comparison")
    
    # Key insights
    st.header("Key Insights")
    
    if selected_fiscal_years:
        latest_fy = max(selected_fiscal_years)
        top_makers = top_makers_by_year[latest_fy]
        bottom_makers = bottom_makers_by_year[latest_fy]
        
        if not top_makers.empty and not bottom_makers.empty:
            # Leaders section
            st.write("### Market Leaders")
            
            leaders_text = f"In FY {latest_fy}-{latest_fy+1}, the top {num_makers} manufacturers dominated the 2-wheeler EV market:"
            
            for i, (_, row) in enumerate(top_makers.iterrows(), 1):
                sales = row['electric_vehicles_sold']
                share = (sales / total_sales_by_year[latest_fy] * 100).round(1)
                leaders_text += f"\n- **{row['maker']}**: {sales:,} units ({share}% market share)"
            
            st.write(leaders_text)
            
            # Laggards section
            st.write("### Market Laggards")
            
            laggards_text = f"The bottom {num_makers} manufacturers had significantly lower sales:"
            
            for i, (_, row) in enumerate(bottom_makers.iterrows(), 1):
                sales = row['electric_vehicles_sold']
                share = (sales / total_sales_by_year[latest_fy] * 100).round(1)
                laggards_text += f"\n- **{row['maker']}**: {sales:,} units ({share}% market share)"
            
            st.write(laggards_text)
            
            # Performance gap
            top_total = top_makers['electric_vehicles_sold'].sum()
            bottom_total = bottom_makers['electric_vehicles_sold'].sum()
            
            st.write("### Market Concentration")
            
            if bottom_total > 0:
                gap_ratio = top_total / bottom_total
                st.write(f"The top {num_makers} manufacturers sold **{gap_ratio:.1f}x more** 2-wheeler EVs than the bottom {num_makers}.")
                st.write(f"This indicates a **highly concentrated market** where a few players dominate the industry.")
            else:
                st.write(f"The bottom {num_makers} manufacturers had negligible market presence compared to the leaders.")
    
    # Footer
    st.markdown("---")
    st.caption("Data source: EV Sales by Makers | Last updated: August 2025")

def calculate_growth_rate(previous, current):
    """Calculate growth rate between two values, handling edge cases"""
    if previous == 0:
        return "∞%" if current > 0 else "0%"
    else:
        growth = round(((current - previous) / previous * 100), 1)
        return f"{growth}%"
        
def calculate_yoy(row):
    """Calculate year-over-year change for manufacturers present in both years"""
    try:
        # Check if both values exist and are valid numbers
        if 'FY 2023' in row and 'FY 2024' in row and isinstance(row['FY 2023'], (int, float)) and isinstance(row['FY 2024'], (int, float)):
            # Handle division by zero
            if row['FY 2023'] == 0:
                return float('inf') if row['FY 2024'] > 0 else 0
            return ((row['FY 2024'] - row['FY 2023'])/row['FY 2023']*100)
        return None
    except:
        return None

def format_with_check(val, format_str):
    """Format values safely handling strings"""
    if isinstance(val, str):
        return val
    else:
        return format_str.format(val)

def main():
    """Entry point for the application when called from the main app."""
    run_app()

if __name__ == "__main__":
    main()
