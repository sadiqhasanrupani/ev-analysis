import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Quarterly Trends for Top 5 EV Makers (4-Wheelers)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    h1, h2, h3 {
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the EV manufacturer data"""
    data_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..",
        "data", "processed",
        "ev_manufacturer_performance_20250809.csv"
    )
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Add quarter column
    df['quarter'] = df['date'].dt.to_period('Q').astype(str)
    df['year_quarter'] = df['date'].dt.year.astype(str) + "-Q" + df['date'].dt.quarter.astype(str)
    
    return df

def main():
    # Load data
    df = load_data()
    
    # Filter for 4-wheelers only
    df_4w = df[df['vehicle_category'] == '4-Wheelers'].copy()
    
    # Filter for the timeframe with data from 2022-2024
    df_4w = df_4w[(df_4w['date'].dt.year >= 2022) & (df_4w['date'].dt.year <= 2024)]
    
    # Page header
    with st.container():
        st.markdown('<div class="header-container">', unsafe_allow_html=True)
        st.title("📊 Quarterly Trends for Top 5 EV Makers (4-Wheelers)")
        
        # Dynamically display the date range in the subtitle
        min_year = df_4w['date'].min().year
        max_year = df_4w['date'].max().year
        max_month = df_4w['date'].max().strftime('%B')
        
        st.markdown(f"### Analysis of sales volume trends from {min_year} to {max_month} {max_year}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Get top 5 makers by total sales volume
    top_makers = df_4w.groupby('maker')['electric_vehicles_sold'].sum().nlargest(5).index.tolist()
    
    # Create filters in sidebar
    st.sidebar.header("Filters")
    
    # Manufacturer selection
    selected_makers = st.sidebar.multiselect(
        "Select Manufacturers",
        options=top_makers,
        default=top_makers
    )
    
    # Time period selection
    min_date = df_4w['date'].min().to_pydatetime().date()
    max_date = df_4w['date'].max().to_pydatetime().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df_4w[
            (df_4w['maker'].isin(selected_makers)) &
            (df_4w['date'] >= pd.Timestamp(start_date)) &
            (df_4w['date'] <= pd.Timestamp(end_date))
        ]
    else:
        filtered_df = df_4w[df_4w['maker'].isin(selected_makers)]
    
    # Aggregate data by quarter
    quarterly_sales = filtered_df.groupby(['maker', 'year_quarter'])['electric_vehicles_sold'].sum().reset_index()
    
    # Pivot the data for easier visualization
    pivot_df = quarterly_sales.pivot(index='year_quarter', columns='maker', values='electric_vehicles_sold').fillna(0)
    
    # Sort by year_quarter
    all_quarters = sorted(quarterly_sales['year_quarter'].unique())
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["Quarterly Sales", "Market Share", "Growth Rates", "Performance KPIs"])
    
    with tab1:
        st.markdown("### Sales Volume Analysis")
        
        # Add ranking information to the quarterly_sales dataframe
        quarterly_sales['rank'] = quarterly_sales.groupby('year_quarter')['electric_vehicles_sold'].rank(
            method='min', ascending=False
        )
        
        # Line chart of sales over time (full width)
        fig_line = px.line(
            quarterly_sales,
            x='year_quarter',
            y='electric_vehicles_sold',
            color='maker',
            markers=True,
            title="Quarterly Sales Volume with Rankings",
            labels={'electric_vehicles_sold': 'Sales Volume', 'year_quarter': 'Quarter', 'maker': 'Manufacturer'},
            custom_data=['rank']
        )
        
        fig_line.update_traces(
            hovertemplate='<b>%{fullData.name}</b><br>Sales: %{y:,}<br>Rank: #%{customdata[0]:.0f}<extra></extra>'
        )
        
        fig_line.update_layout(
            xaxis=dict(categoryorder='array', categoryarray=all_quarters),
            height=400,
            legend_title_text='Manufacturer'
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Create 3-column grid layout for the remaining charts
        grid_col1, grid_col2 = st.columns(2)
        
        # First grid column: Heatmap of rankings
        with grid_col1:
            # Create a heatmap to visualize rankings over quarters
            # First pivot the data to create a matrix of ranks with makers as rows and quarters as columns
            rank_pivot = quarterly_sales.pivot_table(
                index='maker', 
                columns='year_quarter', 
                values=['rank', 'electric_vehicles_sold'],
                aggfunc='first'
            )
            
            # Extract the rank and sales data
            rank_data = rank_pivot['rank']
            sales_data = rank_pivot['electric_vehicles_sold']
            
            # Create a text matrix that combines rank and sales information
            text_matrix = []
            for maker in rank_data.index:
                row = []
                for quarter in rank_data.columns:
                    rank = rank_data.loc[maker, quarter]
                    sales = sales_data.loc[maker, quarter]
                    row.append(f"Rank: #{int(rank)}<br>Sales: {int(sales):,}")
                text_matrix.append(row)
            
            # Create the heatmap for rankings
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=rank_data.values,
                x=rank_data.columns,
                y=rank_data.index,
                colorscale='Blues_r',  # Reversed scale so lower ranks (better performance) are darker
                showscale=False,
                text=text_matrix,
                hoverinfo='text'
            ))
            
            # Add rank numbers as text
            for i, maker in enumerate(rank_data.index):
                for j, quarter in enumerate(rank_data.columns):
                    rank_value = rank_data.loc[maker, quarter]
                    fig_heatmap.add_annotation(
                        x=quarter,
                        y=maker,
                        text=f"#{int(rank_value)}",
                        showarrow=False,
                        font=dict(
                            color='white' if rank_value <= 2 else 'black',
                            size=14
                        )
                    )
            
            fig_heatmap.update_layout(
                title="Rankings by Quarter (lower is better)",
                height=400,
                margin=dict(l=100, r=30, t=50, b=50),  # Add right padding
                xaxis=dict(categoryorder='array', categoryarray=all_quarters)
            )
            
            # Bar chart for each quarter
            fig_bar = px.bar(
                quarterly_sales,
                x='maker',
                y='electric_vehicles_sold',
                color='maker',
                animation_frame='year_quarter',
                title="Quarterly Sales by Manufacturer",
                labels={'electric_vehicles_sold': 'Sales Volume', 'maker': 'Manufacturer'},
                text='rank'  # Show rank on bars
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            fig_bar.update_traces(
                texttemplate='#%{text:.0f}',
                textposition='outside'
            )
            
            fig_bar.update_layout(
                height=400,
                showlegend=False,
                yaxis=dict(title='Sales Volume'),
                margin=dict(r=10),  # Add right padding
                autosize=True,
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Second grid column: Animated bar chart
        # with grid_col2:
            # Bar chart for each quarter
            # fig_bar = px.bar(
            #     quarterly_sales,
            #     x='maker',
            #     y='electric_vehicles_sold',
            #     color='maker',
            #     animation_frame='year_quarter',
            #     title="Quarterly Sales by Manufacturer",
            #     labels={'electric_vehicles_sold': 'Sales Volume', 'maker': 'Manufacturer'},
            #     text='rank'  # Show rank on bars
            # )
            
        
        # Calculate quarter-over-quarter changes
        qoq_changes = []
        
        for maker in quarterly_sales['maker'].unique():
            maker_data = quarterly_sales[quarterly_sales['maker'] == maker].sort_values('year_quarter')
            
            if len(maker_data) < 2:
                continue
                
            for i in range(1, len(maker_data)):
                prev_quarter = maker_data.iloc[i-1]['year_quarter']
                curr_quarter = maker_data.iloc[i]['year_quarter']
                prev_sales = maker_data.iloc[i-1]['electric_vehicles_sold']
                curr_sales = maker_data.iloc[i]['electric_vehicles_sold']
                prev_rank = maker_data.iloc[i-1]['rank']
                curr_rank = maker_data.iloc[i]['rank']
                
                if prev_sales > 0:
                    pct_change = ((curr_sales - prev_sales) / prev_sales) * 100
                else:
                    pct_change = float('inf') if curr_sales > 0 else 0
                    
                rank_change = prev_rank - curr_rank  # Positive means improvement in rank
                
                qoq_changes.append({
                    'maker': maker,
                    'from_quarter': prev_quarter,
                    'to_quarter': curr_quarter,
                    'from_sales': prev_sales,
                    'to_sales': curr_sales,
                    'pct_change': pct_change,
                    'from_rank': prev_rank,
                    'to_rank': curr_rank,
                    'rank_change': rank_change
                })
        
        qoq_df = pd.DataFrame(qoq_changes)
        
        # Third grid column: Summary statistics
        with grid_col2:
            st.markdown("#### Summary Statistics")
            
            total_sales = quarterly_sales.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
            total_sales = total_sales.sort_values('electric_vehicles_sold', ascending=False)
            
            # Add average rank
            avg_rank = quarterly_sales.groupby('maker')['rank'].mean().reset_index()
            avg_rank.columns = ['maker', 'avg_rank']
            
            # Merge total sales and average rank
            summary_stats = total_sales.merge(avg_rank, on='maker')
            summary_stats.columns = ['Manufacturer', 'Total Sales', 'Average Rank']
            summary_stats['Average Rank'] = summary_stats['Average Rank'].round(2)
            
            st.dataframe(summary_stats, use_container_width=True)
            
            # Top performer by quarter
            top_by_quarter = quarterly_sales.loc[
                quarterly_sales.groupby('year_quarter')['electric_vehicles_sold'].idxmax()
            ][['year_quarter', 'maker', 'electric_vehicles_sold']]
            
            top_by_quarter.columns = ['Quarter', 'Top Manufacturer', 'Sales Volume']
            
            st.markdown("#### Top Performing by Quarter")
            st.dataframe(top_by_quarter, use_container_width=True)
        
        # Display quarter-over-quarter changes
        if not qoq_df.empty:
            st.markdown("### Quarter-over-Quarter Performance Changes")
            
            # Create visual indicators for QoQ changes
            def format_pct_change(val):
                if pd.isna(val) or val == float('inf'):
                    return "N/A"
                elif val > 0:
                    return f"▲ {val:.2f}%"
                elif val < 0:
                    return f"▼ {val:.2f}%"
                else:
                    return "0.00%"
            
            def format_rank_change(val):
                if val > 0:
                    return f"▲ +{val} (improved)"
                elif val < 0:
                    return f"▼ {val} (declined)"
                else:
                    return "● No change"
            
            # Format the display dataframe
            qoq_display = qoq_df.copy()
            qoq_display['pct_change'] = qoq_display['pct_change'].apply(format_pct_change)
            qoq_display['rank_change'] = qoq_display['rank_change'].apply(format_rank_change)
            
            # Rename columns for better readability
            qoq_display = qoq_display[[
                'maker', 'from_quarter', 'to_quarter', 
                'from_sales', 'to_sales', 'pct_change',
                'rank_change'
            ]]
            qoq_display.columns = [
                'Manufacturer', 'From Quarter', 'To Quarter',
                'Previous Sales', 'Current Sales', 'Sales Change %',
                'Rank Change'
            ]
            
            # Sort by the most recent quarters first, then by manufacturer
            qoq_display = qoq_display.sort_values(['To Quarter', 'From Quarter', 'Manufacturer'], ascending=[False, False, True])
            
            st.dataframe(qoq_display, use_container_width=True)
    
    with tab2:
        st.markdown("### Market Share Analysis")
        
        # Calculate market share by quarter
        market_share_df = quarterly_sales.copy()
        total_by_quarter = market_share_df.groupby('year_quarter')['electric_vehicles_sold'].sum().reset_index()
        total_by_quarter.columns = ['year_quarter', 'total_sales']
        
        market_share_df = market_share_df.merge(total_by_quarter, on='year_quarter', how='left')
        market_share_df['market_share'] = (market_share_df['electric_vehicles_sold'] / market_share_df['total_sales']) * 100
        
        # Add rank based on market share for each quarter
        market_share_df['rank'] = market_share_df.groupby('year_quarter')['market_share'].rank(
            method='min', ascending=False
        )
        
        # Define first and last quarters for comparison
        if len(all_quarters) >= 2:
            first_quarter = all_quarters[0]
            last_quarter = all_quarters[-1]
            
            first_quarter_data = market_share_df[market_share_df['year_quarter'] == first_quarter]
            last_quarter_data = market_share_df[market_share_df['year_quarter'] == last_quarter]
            
            # Create comparison dataframe
            comparison_df = pd.merge(
                first_quarter_data[['maker', 'market_share', 'rank']],
                last_quarter_data[['maker', 'market_share', 'rank']],
                on='maker',
                how='outer',
                suffixes=('_start', '_end')
            ).fillna(0)
            
            comparison_df['change'] = comparison_df['market_share_end'] - comparison_df['market_share_start']
            comparison_df['rank_change'] = comparison_df['rank_start'] - comparison_df['rank_end']
        
        # Create 2-column layout for the first row
        ms_col1, ms_col2 = st.columns(2)
        
        # First column: Area chart for market share evolution
        with ms_col1:
            fig_area = px.area(
                market_share_df,
                x='year_quarter',
                y='market_share',
                color='maker',
                title="Market Share Evolution by Quarter",
                labels={'market_share': 'Market Share (%)', 'year_quarter': 'Quarter', 'maker': 'Manufacturer'},
                custom_data=['rank', 'electric_vehicles_sold']  # Include rank and sales for hover data
            )
            
            fig_area.update_traces(
                hovertemplate='<b>%{fullData.name}</b><br>Market Share: %{y:.2f}%<br>Rank: #%{customdata[0]:.0f}<br>Sales: %{customdata[1]:,}<extra></extra>'
            )
            
            fig_area.update_layout(
                xaxis=dict(categoryorder='array', categoryarray=all_quarters),
                yaxis=dict(ticksuffix="%"),
                hovermode="x unified",
                height=400,
                legend_title_text='Manufacturer'
            )
            
            st.plotly_chart(fig_area, use_container_width=True)
        
        # Second column: Pie charts comparison
        with ms_col2:
            # Always define first_quarter_data and last_quarter_data to avoid unbound errors
            first_quarter_data = pd.DataFrame()
            last_quarter_data = pd.DataFrame()
            if len(all_quarters) >= 2:
                first_quarter = all_quarters[0]
                last_quarter = all_quarters[-1]
                first_quarter_data = market_share_df[market_share_df['year_quarter'] == first_quarter]
                last_quarter_data = market_share_df[market_share_df['year_quarter'] == last_quarter]
                # Create pie charts side by side within the column
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=(
                        f"Share in {first_quarter}",
                        f"Share in {last_quarter}"
                    ),
                    specs=[[{"type": "domain"}, {"type": "domain"}]]
                )
                
                # First quarter pie chart
                fig.add_trace(
                    go.Pie(
                        labels=first_quarter_data['maker'],
                        values=first_quarter_data['market_share'],
                        name=first_quarter,
                        marker_colors=px.colors.qualitative.Set1,
                        textinfo='percent+label',
                        hole=.3
                    ),
                    row=1, col=1
                )
                
                # Last quarter pie chart
                fig.add_trace(
                    go.Pie(
                        labels=last_quarter_data['maker'],
                        values=last_quarter_data['market_share'],
                        name=last_quarter,
                        marker_colors=px.colors.qualitative.Set1,
                        textinfo='percent+label',
                        hole=.3
                    ),
                    row=1, col=2
                )
                
                fig.update_layout(
                    title="Market Share Comparison by Quarter",
                    height=400,
                    legend_title_text='Manufacturer'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Need at least two quarters of data to show comparison.")
                
        # Create a second row with 2-column layout for market share comparison
        if len(all_quarters) >= 2:
            ms_col3, ms_col4 = st.columns(2)
            
            # Third column: Market share comparison bar chart
            with ms_col3:
                # Market share comparison by quarter (start vs. end)
                first_quarter = all_quarters[0]
                last_quarter = all_quarters[-1]
                
                first_quarter_data = market_share_df[market_share_df['year_quarter'] == first_quarter]
                last_quarter_data = market_share_df[market_share_df['year_quarter'] == last_quarter]
                # Create a dataframe for comparison
                comparison_df = pd.merge(
                    first_quarter_data[['maker', 'market_share', 'rank']],
                    last_quarter_data[['maker', 'market_share', 'rank']],
                    on='maker',
                    how='outer',
                    suffixes=('_start', '_end')
                ).fillna(0)
                
                comparison_df['change'] = comparison_df['market_share_end'] - comparison_df['market_share_start']
                comparison_df['rank_change'] = comparison_df['rank_start'] - comparison_df['rank_end']
                
                # Create visualization for market share changes
                fig_change = go.Figure()
                
                # Sort by end market share
                comparison_df_sorted = comparison_df.sort_values('market_share_end', ascending=False)
                
                # Add bars for start and end market share
                fig_change.add_trace(
                    go.Bar(
                        x=comparison_df_sorted['maker'],
                        y=comparison_df_sorted['market_share_start'],
                        name=f'Market Share ({first_quarter})',
                        marker_color='lightblue',
                        opacity=0.7,
                        text=comparison_df_sorted['market_share_start'].round(1).astype(str) + '%',
                        textposition='inside'
                    )
                )
                
                fig_change.add_trace(
                    go.Bar(
                        x=comparison_df_sorted['maker'],
                        y=comparison_df_sorted['market_share_end'],
                        name=f'Market Share ({last_quarter})',
                        marker_color='darkblue',
                        text=comparison_df_sorted['market_share_end'].round(1).astype(str) + '%',
                        textposition='inside'
                    )
                )
                
                # Add rank change indicators
                for i, row in comparison_df_sorted.iterrows():
                    if row['rank_change'] > 0:  # Improved rank (moved up)
                        symbol = '▲'  # Up arrow
                        color = 'green'
                        text = f"+{int(row['rank_change'])}"
                    elif row['rank_change'] < 0:  # Declined rank (moved down)
                        symbol = '▼'  # Down arrow
                        color = 'red'
                        text = f"{int(row['rank_change'])}"
                    else:  # No change in rank
                        symbol = '●'  # Circle
                        color = 'grey'
                        text = "0"
                    
                    # Add annotation for rank change
                    fig_change.add_annotation(
                        x=row['maker'],
                        y=max(row['market_share_start'], row['market_share_end']) + 2,  # Position above the higher bar
                        text=f"{symbol} {text}",
                        showarrow=False,
                        font=dict(size=14, color=color)
                    )
                
                fig_change.update_layout(
                    title=f"Market Share: {first_quarter} vs {last_quarter}",
                    xaxis_title='Manufacturer',
                    yaxis_title='Market Share (%)',
                    yaxis=dict(ticksuffix='%'),
                    barmode='group',
                    height=400,
                    legend=dict(
                        orientation='h',
                        y=1.1,
                        x=0.5,
                        xanchor='center'
                    )
                )
                
                st.plotly_chart(fig_change, use_container_width=True)
            
            # Market share change table
            st.markdown("### Market Share Change")
            
            # Format the comparison dataframe for display
            comparison_df_display = comparison_df.copy()
            comparison_df_display['market_share_start'] = comparison_df_display['market_share_start'].round(2).astype(str) + '%'
            comparison_df_display['market_share_end'] = comparison_df_display['market_share_end'].round(2).astype(str) + '%'
            comparison_df_display['change'] = comparison_df_display['change'].round(2).astype(str) + '%'
            
            # Format rank changes with symbols
            def format_rank_change(val):
                val = int(val)
                if val > 0:
                    return f"▲ +{val} (improved)"
                elif val < 0:
                    return f"▼ {val} (declined)"
                else:
                    return "● No change"
            
            comparison_df_display['rank_change'] = comparison_df_display['rank_change'].apply(format_rank_change)
            
            # Rename columns for better readability
            comparison_df_display.columns = [
                'Manufacturer', 
                f'Market Share ({first_quarter})', 
                f'Rank ({first_quarter})',
                f'Market Share ({last_quarter})', 
                f'Rank ({last_quarter})',
                'Market Share Change',
                'Rank Change'
            ]
            
            # Reorder columns
            comparison_df_display = comparison_df_display[[
                'Manufacturer', 
                f'Market Share ({first_quarter})',
                f'Market Share ({last_quarter})',
                'Market Share Change',
                'Rank Change'
            ]]
            
            # Sort by the change column (descending)
            comparison_df_display = comparison_df_display.sort_values('Market Share Change', key=lambda x: pd.to_numeric(x.str.rstrip('%')), ascending=False)
            
            st.dataframe(comparison_df_display, use_container_width=True)
    
    # Initialize variables used across tabs
    cagr_df = pd.DataFrame()  # Initialize empty DataFrame to avoid "possibly unbound" errors
    
    with tab3:
        st.markdown("### Growth Rate Analysis")
        
        # Calculate quarter-over-quarter growth rates
        growth_df = pivot_df.pct_change().reset_index()
        growth_df = pd.melt(
            growth_df, 
            id_vars=['year_quarter'], 
            var_name='maker', 
            value_name='qoq_growth'
        )
        
        # Replace infinity and NaN with 0 (first quarters)
        growth_df = growth_df.replace([np.inf, -np.inf], np.nan)
        growth_df['qoq_growth'] = growth_df['qoq_growth'].fillna(0)
        
        # Convert to percentage
        growth_df['qoq_growth'] = growth_df['qoq_growth'] * 100
        
        # Filter for selected makers
        growth_df = growth_df[growth_df['maker'].isin(selected_makers)]
        

        
        # Create a 2-column layout for charts
        gr_col1, gr_col2 = st.columns(2)
        
        # First column: Average growth rate
        with gr_col1:
            # Bar chart for average growth rate by manufacturer
            avg_growth = growth_df.groupby('maker')['qoq_growth'].mean().reset_index()
            avg_growth = avg_growth.sort_values('qoq_growth', ascending=False)
            
            fig_avg_growth = px.bar(
                avg_growth,
                x='maker',
                y='qoq_growth',
                color='maker',
                title="Average QoQ Growth Rate",
                labels={'qoq_growth': 'Average Growth Rate (%)', 'maker': 'Manufacturer'},
                text=avg_growth['qoq_growth'].round(2).astype(str) + '%'
            )
            
            fig_avg_growth.update_layout(
                xaxis_title="Manufacturer",
                yaxis_title="Average Growth Rate (%)",
                yaxis=dict(ticksuffix="%"),
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig_avg_growth, use_container_width=True)
        
        # Second column: Manufacturer rankings
        with gr_col2:
            # Calculate quarterly rank of manufacturers (based on sales volume)
            # Create a ranking dataframe for the bump chart
            rank_df = quarterly_sales.copy()
            rank_df['rank'] = rank_df.groupby('year_quarter')['electric_vehicles_sold'].rank(
                method='min', ascending=False
            )
            
            # Filter for selected makers
            rank_df = rank_df[rank_df['maker'].isin(selected_makers)]
            
            # Create the bump chart
            fig_bump = go.Figure()
            
            # Sort to ensure correct line connections
            rank_df = rank_df.sort_values(by=['maker', 'year_quarter'])
            
            # Add a line for each manufacturer
            for maker in selected_makers:
                maker_data = rank_df[rank_df['maker'] == maker]
                
                fig_bump.add_trace(
                    go.Scatter(
                        x=maker_data['year_quarter'],
                        y=maker_data['rank'],
                        mode='lines+markers+text',
                        name=maker,
                        line=dict(width=6),
                        marker=dict(size=12),
                        text=maker_data['rank'].astype(int),
                        textposition='top center',
                        hovertemplate=
                        '<b>%{text}</b><br>' +
                        'Rank: %{y}<br>' +
                        'Quarter: %{x}<br>' +
                        'Sales: %{customdata:,}<extra></extra>',
                        customdata=maker_data['electric_vehicles_sold']
                    )
                )
            
            # Invert y-axis so rank 1 is at the top
            fig_bump.update_layout(
                yaxis=dict(
                    autorange='reversed',
                    title='Rank',
                    tickmode='array',
                    tickvals=list(range(1, len(selected_makers) + 1)),
                    ticktext=[f"#{i}" for i in range(1, len(selected_makers) + 1)],
                    gridcolor='lightgrey'
                ),
                title="Manufacturer Ranking by Quarter",
                xaxis_title="Quarter",
                height=400,
                hovermode="closest",
                plot_bgcolor='white',
                legend_title_text='Manufacturer',
                margin=dict(t=50, b=50, l=50, r=50)
            )
            
            st.plotly_chart(fig_bump, use_container_width=True)
        
        # Show explanation text
        st.markdown("""
        ### 📊 Reading the Bump Chart
        
        The **Bump Chart** above visualizes how the ranking of manufacturers changes over time:
        
        - **Lines** represent the path of each manufacturer's rank across quarters
        - **Higher position** (closer to the top) indicates better rank (#1 is best)
        - **Steeper lines** indicate significant changes in ranking
        - **Numbers** on each point show the exact rank for that quarter
        
        This visualization makes it easy to track which manufacturers are consistently at the top
        and which ones are improving or declining in their competitive position.
        """)
        
        # Calculate CAGR (Compound Annual Growth Rate)
        if len(all_quarters) >= 2:
            # Get first and last quarter data for CAGR calculation
            first_quarter_data = quarterly_sales[quarterly_sales['year_quarter'] == all_quarters[0]].copy()
            last_quarter_data = quarterly_sales[quarterly_sales['year_quarter'] == all_quarters[-1]].copy()
            
            # Create a dataframe for CAGR calculation
            cagr_df = pd.merge(
                first_quarter_data[['maker', 'electric_vehicles_sold']],
                last_quarter_data[['maker', 'electric_vehicles_sold']],
                on='maker',
                how='outer',
                suffixes=('_start', '_end')
            ).fillna(1)  # Use 1 instead of 0 to avoid division by zero
            
            # Calculate the number of years
            start_year = int(all_quarters[0].split('-')[0])
            start_quarter = int(all_quarters[0].split('Q')[1])
            end_year = int(all_quarters[-1].split('-')[0])
            end_quarter = int(all_quarters[-1].split('Q')[1])
            
            # Calculate time in years (approximating quarters)
            time_period = (end_year - start_year) + (end_quarter - start_quarter) / 4
            
            # Calculate CAGR
            cagr_df['cagr'] = (
                (cagr_df['electric_vehicles_sold_end'] / cagr_df['electric_vehicles_sold_start']) ** (1 / time_period) - 1
            ) * 100
            
            # Replace infinity and NaN with 0
            cagr_df.replace([np.inf, -np.inf], np.nan, inplace=True)
            
            # For cases where start was 0 but end was positive, set a high growth
            mask = (cagr_df['electric_vehicles_sold_start'] <= 1) & (cagr_df['electric_vehicles_sold_end'] > 1)
            cagr_df.loc[mask, 'cagr'] = 1000  # 1000% growth for new entrants
            
            # Bar chart for CAGR by manufacturer
            cagr_df = cagr_df.sort_values('cagr', ascending=False)
            
            # Format CAGR values for display
            cagr_df['cagr_formatted'] = cagr_df['cagr'].apply(
                lambda x: f"{x:.1f}%" if abs(x) < 1000 else "New Entrant" if x > 0 else "Exit"
            )
            
            fig_cagr = px.bar(
                cagr_df,
                x='maker',
                y='cagr',
                color='maker',
                title=f"Compound Annual Growth Rate (CAGR) - {all_quarters[0]} to {all_quarters[-1]}",
                labels={'cagr': 'CAGR (%)', 'maker': 'Manufacturer'},
                text='cagr_formatted'
            )
            
            fig_cagr.update_layout(
                xaxis_title="Manufacturer",
                yaxis_title="CAGR (%)",
                yaxis=dict(ticksuffix="%"),
                showlegend=False,
                height=400
            )
            
            # Add reference line at y=0
            fig_cagr.add_hline(
                y=0,
                line_dash="dash",
                line_color="black"
            )
            
            st.plotly_chart(fig_cagr, use_container_width=True)
    
    with tab4:
        st.markdown("### Performance KPIs")
        
        # Calculate total sales for selected period
        total_sales_by_maker = filtered_df.groupby('maker')['electric_vehicles_sold'].sum().reset_index()
        total_sales_by_maker = total_sales_by_maker.sort_values('electric_vehicles_sold', ascending=False)
        
        # Calculate market share for the entire period
        total_market = total_sales_by_maker['electric_vehicles_sold'].sum()
        total_sales_by_maker['market_share'] = (total_sales_by_maker['electric_vehicles_sold'] / total_market) * 100
        
        # Calculate average quarterly sales
        avg_quarterly_sales = quarterly_sales.groupby('maker')['electric_vehicles_sold'].mean().reset_index()
        avg_quarterly_sales.columns = ['maker', 'avg_quarterly_sales']
        
        # Calculate consistency (standard deviation / mean)
        std_quarterly_sales = quarterly_sales.groupby('maker')['electric_vehicles_sold'].std().reset_index()
        std_quarterly_sales.columns = ['maker', 'std_quarterly_sales']
        
        # Merge all KPIs
        kpi_df = pd.merge(total_sales_by_maker, avg_quarterly_sales, on='maker', how='left')
        kpi_df = pd.merge(kpi_df, std_quarterly_sales, on='maker', how='left')
        
        # Calculate coefficient of variation (higher is more volatile)
        kpi_df['volatility'] = (kpi_df['std_quarterly_sales'] / kpi_df['avg_quarterly_sales']) * 100
        kpi_df['volatility'] = kpi_df['volatility'].fillna(0)  # Handle cases where avg_quarterly_sales is 0
        
        # Create KPI cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Find market leader
        market_leader = kpi_df.iloc[0]['maker']
        market_leader_share = kpi_df.iloc[0]['market_share']
        
        # Initialize variables for fastest growing
        fastest_growing = "N/A"
        fastest_growing_cagr = 0
        
        # Find fastest growing (highest CAGR) if we have sufficient data
        if len(all_quarters) >= 2:
            # Get the previously calculated CAGR data
            fastest_growing = cagr_df.iloc[0]['maker']
            fastest_growing_cagr = cagr_df.iloc[0]['cagr']
        
        # Find most consistent (lowest volatility)
        most_consistent = kpi_df.sort_values('volatility').iloc[0]['maker']
        most_consistent_vol = kpi_df.sort_values('volatility').iloc[0]['volatility']
        
        # Calculate total market size
        total_market_size = filtered_df['electric_vehicles_sold'].sum()
        
        # Calculate quarter with highest sales
        quarterly_total = quarterly_sales.groupby('year_quarter')['electric_vehicles_sold'].sum().reset_index()
        best_quarter = quarterly_total.sort_values('electric_vehicles_sold', ascending=False).iloc[0]['year_quarter']
        best_quarter_sales = quarterly_total.sort_values('electric_vehicles_sold', ascending=False).iloc[0]['electric_vehicles_sold']
        
        # Display KPI cards
        with col1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                "Market Leader",
                market_leader,
                f"{market_leader_share:.1f}% Share"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                "Fastest Growing",
                fastest_growing,
                f"{fastest_growing_cagr:.1f}% CAGR" if fastest_growing_cagr < 1000 else "New Entrant"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                "Most Consistent",
                most_consistent,
                f"{most_consistent_vol:.1f}% Volatility"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                "Total Market Size",
                f"{total_market_size:,}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col5:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.metric(
                "Best Quarter",
                best_quarter,
                f"{best_quarter_sales:,} Units"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Display the KPI table
        st.markdown("### Manufacturer Performance Summary")
        
        # Format KPI dataframe for display
        kpi_display = kpi_df.copy()
        kpi_display['market_share'] = kpi_display['market_share'].round(2).astype(str) + '%'
        kpi_display['volatility'] = kpi_display['volatility'].round(2).astype(str) + '%'
        
        # Rename columns for display
        kpi_display = kpi_display.rename(columns={
            'maker': 'Manufacturer',
            'electric_vehicles_sold': 'Total Sales',
            'market_share': 'Market Share',
            'avg_quarterly_sales': 'Avg. Quarterly Sales',
            'std_quarterly_sales': 'Std. Deviation',
            'volatility': 'Volatility'
        })
        
        # Reorder columns
        kpi_display = kpi_display[['Manufacturer', 'Total Sales', 'Market Share', 
                                   'Avg. Quarterly Sales', 'Volatility']]
        
        st.dataframe(kpi_display, use_container_width=True)
        
        # Add executive summary
        st.markdown("### Executive Summary")
        
        # Create a summary text
        st.markdown(f"""
        Based on the analysis of quarterly sales data for the top 5 four-wheeler EV manufacturers from 2022 to 2024:
        
        1. **Market Leadership**: {market_leader} is the dominant player with {kpi_df.iloc[0]['market_share']:.1f}% market share.
        
        2. **Growth Dynamics**: {fastest_growing} shows the strongest growth trajectory with a CAGR of {fastest_growing_cagr:.1f}% (excluding new entrants).
        
        3. **Market Consistency**: {most_consistent} demonstrates the most consistent performance with only {most_consistent_vol:.1f}% volatility in quarterly sales.
        
        4. **Market Timing**: The {best_quarter} quarter saw the highest overall market volume with {best_quarter_sales:,} units sold.
        
        5. **Market Concentration**: The top 2 manufacturers control {kpi_df.iloc[:2]['market_share'].sum():.1f}% of the market, indicating {
            "high" if kpi_df.iloc[:2]['market_share'].sum() > 70 else 
            "moderate" if kpi_df.iloc[:2]['market_share'].sum() > 40 else "low"
        } market concentration.
        """)
        
if __name__ == "__main__":
    main()
