import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the data
@st.cache_data
def load_data():
    ev_sales_state = pd.read_csv('data/processed/processed_ev_sales_by_state.csv')
    ev_sales_enhanced = pd.read_csv('data/processed/ev_sales_enhanced.csv')
    
    # Convert date column to datetime and create year_month column
    if 'date' in ev_sales_state.columns:
        ev_sales_state['date'] = pd.to_datetime(ev_sales_state['date'])
        ev_sales_state['year_month'] = ev_sales_state['date'].dt.strftime('%Y-%m')
    elif 'month' in ev_sales_state.columns and 'year' in ev_sales_state.columns:
        ev_sales_state['year_month'] = ev_sales_state['year'].astype(str) + '-' + ev_sales_state['month'].astype(str).str.zfill(2)
    
    return ev_sales_state, ev_sales_enhanced


def main():
    st.title("🚗 EV Market Analysis Dashboard")
    
    # Load data
    ev_sales_state, ev_sales_enhanced = load_data()
    
    # Debug information
    st.write("Available columns in ev_sales_state:", ev_sales_state.columns.tolist())
    st.write("First few rows of data:", ev_sales_state.head())
    
    # Question 1: Overall Market Growth
    st.header("1. Overall EV Market Growth (2021-2024)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate monthly total EV sales and penetration
        monthly_metrics = ev_sales_state.groupby('year_month').agg({
            'electric_vehicles_sold': 'sum',
            'total_vehicles_sold': 'sum'
        }).reset_index()
        monthly_metrics['ev_penetration'] = (
            monthly_metrics['electric_vehicles_sold'] / monthly_metrics['total_vehicles_sold'] * 100
        )
        
        # Create line chart for EV penetration trend
        fig_penetration = px.line(
            monthly_metrics,
            x='year_month',
            y='ev_penetration',
            title='EV Market Penetration Over Time',
            labels={'ev_penetration': 'EV Penetration Rate (%)', 'year_month': 'Month'}
        )
        st.plotly_chart(fig_penetration)
        
    with col2:
        # Calculate cumulative growth
        monthly_metrics['cumulative_ev_sales'] = monthly_metrics['electric_vehicles_sold'].cumsum()
        
        fig_cumulative = px.line(
            monthly_metrics,
            x='year_month',
            y='cumulative_ev_sales',
            title='Cumulative EV Sales Growth',
            labels={'cumulative_ev_sales': 'Total EVs Sold', 'year_month': 'Month'}
        )
        st.plotly_chart(fig_cumulative)

    # Question 2: Regional Market Analysis
    st.header("2. Regional Market Performance")
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Top 5 states by EV sales
        top_states = ev_sales_state.groupby('state').agg({
            'electric_vehicles_sold': 'sum'
        }).sort_values('electric_vehicles_sold', ascending=False).head(10)
        
        fig_top_states = px.bar(
            top_states,
            title='Top 10 States by EV Sales',
            labels={'state': 'State', 'electric_vehicles_sold': 'Total EVs Sold'}
        )
        st.plotly_chart(fig_top_states)
        
    with col4:
        # State-wise penetration rates
        state_penetration = ev_sales_state.groupby('state').agg({
            'electric_vehicles_sold': 'sum',
            'total_vehicles_sold': 'sum'
        })
        state_penetration['ev_penetration'] = (
            state_penetration['electric_vehicles_sold'] / state_penetration['total_vehicles_sold'] * 100
        )
        state_penetration = state_penetration.sort_values('ev_penetration', ascending=False).head(10)
        
        fig_penetration_states = px.bar(
            state_penetration,
            y='ev_penetration',
            title='Top 10 States by EV Penetration Rate',
            labels={'state': 'State', 'ev_penetration': 'EV Penetration Rate (%)'}
        )
        st.plotly_chart(fig_penetration_states)

    # Question 3: Vehicle Segment Analysis
    st.header("3. Vehicle Segment Analysis")
    
    col5, col6 = st.columns(2)
    
    with col5:
        # Segment-wise sales trend
        segment_trend = ev_sales_state.groupby(['year_month', 'vehicle_category']).agg({
            'electric_vehicles_sold': 'sum'
        }).reset_index()
        
        fig_segment = px.line(
            segment_trend,
            x='year_month',
            y='electric_vehicles_sold',
            color='vehicle_category',
            title='EV Sales Trend by Vehicle Category',
            labels={
                'electric_vehicles_sold': 'Units Sold',
                'year_month': 'Month',
                'vehicle_category': 'Vehicle Type'
            }
        )
        st.plotly_chart(fig_segment)
        
    with col6:
        # Segment penetration comparison
        segment_penetration = ev_sales_state.groupby('vehicle_category').agg({
            'electric_vehicles_sold': 'sum',
            'total_vehicles_sold': 'sum'
        })
        segment_penetration['penetration_rate'] = (
            segment_penetration['electric_vehicles_sold'] / segment_penetration['total_vehicles_sold'] * 100
        )
        
        fig_segment_pen = px.bar(
            segment_penetration,
            y='penetration_rate',
            title='EV Penetration Rate by Vehicle Category',
            labels={
                'vehicle_category': 'Vehicle Type',
                'penetration_rate': 'Penetration Rate (%)'
            }
        )
        st.plotly_chart(fig_segment_pen)

    # Add insights and explanations
    st.markdown("""
    ### Key Insights:
    
    1. **Market Growth**
        - EV penetration has increased from 0.53% to 7.83% between April 2021 and March 2024
        - The growth shows an exponential pattern, indicating accelerating adoption
        
    2. **Regional Performance**
        - Five states (Maharashtra, Karnataka, Tamil Nadu, Gujarat, and Rajasthan) dominate the market
        - Significant variations in adoption rates across states
        - Some states show higher penetration despite lower total sales
        
    3. **Vehicle Segments**
        - Data shows distinct patterns between 2-wheeler and 4-wheeler adoption
        - Segment preferences vary by region
        - Growth rates differ between segments
    """)