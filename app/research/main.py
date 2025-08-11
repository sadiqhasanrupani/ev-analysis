import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# Set page configuration
st.set_page_config(
    page_title="EV Sales Analysis Research",
    page_icon="🔍",
    layout="wide"
)

# Load and prepare the data
@st.cache_data
def load_data():
    try:
        # Load datasets
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data", "raw")
        state_path = os.path.join(data_dir, "electric_vehicle_sales_by_state.csv")
        makers_path = os.path.join(data_dir, "electric_vehicle_sales_by_makers.csv")

        ev_sales_state = pd.read_csv(state_path)
        ev_sales_makers = pd.read_csv(makers_path)
    except FileNotFoundError as e:
        st.error(f"Error: Could not find one or more data files. Please ensure the data files exist in the correct location.")
        st.error(f"Missing file: {str(e)}")
        raise e
    
    # Process makers data
    ev_sales_makers['date'] = pd.to_datetime(ev_sales_makers['date'])
    ev_sales_makers['fiscal_year'] = ev_sales_makers['date'].dt.year.where(
        ev_sales_makers['date'].dt.month < 4,
        ev_sales_makers['date'].dt.year + 1
    )
    
    # Process state data
    ev_sales_state['date'] = pd.to_datetime(ev_sales_state['date'])
    ev_sales_state['fiscal_year'] = ev_sales_state['date'].dt.year.where(
        ev_sales_state['date'].dt.month < 4,
        ev_sales_state['date'].dt.year + 1
    )
    
    return ev_sales_state, ev_sales_makers

def main():
    st.title("🔍 EV Market Research Analysis")
    st.markdown("### Analysis of Key Research Questions")
    
    # Load data
    ev_sales_state, ev_sales_makers = load_data()

    # Question 1: Top and Bottom Makers Analysis
    st.header("1. Top 3 and Bottom 3 Makers in 2-Wheeler Segment (FY 2023-2024)")
    
    # Debug information to understand the data structure
    st.subheader("Data Structure Analysis")
    st.write("Available columns in ev_sales_makers:", ev_sales_makers.columns.tolist())
    st.write("Data Types:", ev_sales_makers.dtypes)
    st.write("First few rows of ev_sales_makers:", ev_sales_makers.head())
    
    # Check for the sales column
    possible_sales_columns = ['units_sold', 'electric_vehicles', 'vehicles_sold', 'sales', 'volume']
    sales_column = None
    for col in possible_sales_columns:
        if col in ev_sales_makers.columns:
            sales_column = col
            break
            
    if sales_column is None:
        st.error("Could not find a column representing sales volume. Available columns are: " + ", ".join(ev_sales_makers.columns.tolist()))
        return
        
    st.success(f"Using '{sales_column}' as the sales volume column")
    
    # Filter for 2-wheelers and relevant fiscal years
    makers_analysis = ev_sales_makers[
        (ev_sales_makers['vehicle_category'] == '2-wheeler') &
        (ev_sales_makers['fiscal_year'].isin([2023, 2024]))
    ].groupby(['maker', 'fiscal_year'])[sales_column].sum().reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create figure for FY 2023
        fy_2023 = makers_analysis[makers_analysis['fiscal_year'] == 2023]
        top_3_2023 = fy_2023.nlargest(3, sales_column)
        bottom_3_2023 = fy_2023.nsmallest(3, sales_column)
        combined_2023 = pd.concat([top_3_2023, bottom_3_2023])
        
        fig_2023 = px.bar(
            combined_2023,
            x='maker',
            y=sales_column,
            title='Top 3 and Bottom 3 Makers - FY 2023',
            color=sales_column,
            color_continuous_scale='Viridis',
            labels={sales_column: '2-Wheelers Sold', 'maker': 'Manufacturer'}
        )
        st.plotly_chart(fig_2023, use_container_width=True)
        
        # Display numeric data
        st.markdown("#### FY 2023 Details:")
        col1a, col1b = st.columns(2)
        with col1a:
            st.markdown("**Top 3 Makers:**")
            st.dataframe(top_3_2023[['maker', sales_column]])
        with col1b:
            st.markdown("**Bottom 3 Makers:**")
            st.dataframe(bottom_3_2023[['maker', sales_column]])
    
    with col2:
        # Create figure for FY 2024
        fy_2024 = makers_analysis[makers_analysis['fiscal_year'] == 2024]
        top_3_2024 = fy_2024.nlargest(3, sales_column)
        bottom_3_2024 = fy_2024.nsmallest(3, sales_column)
        combined_2024 = pd.concat([top_3_2024, bottom_3_2024])
        
        fig_2024 = px.bar(
            combined_2024,
            x='maker',
            y=sales_column,
            title='Top 3 and Bottom 3 Makers - FY 2024',
            color=sales_column,
            color_continuous_scale='Viridis',
            labels={sales_column: '2-Wheelers Sold', 'maker': 'Manufacturer'}
        )
        st.plotly_chart(fig_2024, use_container_width=True)
        
        # Display numeric data
        st.markdown("#### FY 2024 Details:")
        col2a, col2b = st.columns(2)
        with col2a:
            st.markdown("**Top 3 Makers:**")
            st.dataframe(top_3_2024[['maker', sales_column]])
        with col2b:
            st.markdown("**Bottom 3 Makers:**")
            st.dataframe(bottom_3_2024[['maker', sales_column]])

    # Question 2: Top 5 States by Vehicle Category
    st.header("2. Top 5 States by EV Penetration Rate (FY 2024)")
    
    # Filter for FY 2024
    fy_2024_state = ev_sales_state[ev_sales_state['fiscal_year'] == 2024]
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Analysis for 2-wheelers
        two_wheeler_penetration = fy_2024_state[
            fy_2024_state['vehicle_category'] == '2-wheeler'
        ].groupby('state').agg({
            'electric_vehicles': 'sum',
            'total_vehicles': 'sum'
        })
        two_wheeler_penetration['penetration_rate'] = (
            two_wheeler_penetration['electric_vehicles'] / 
            two_wheeler_penetration['total_vehicles'] * 100
        )
        top_5_2w = two_wheeler_penetration.nlargest(5, 'penetration_rate')
        
        fig_2w = px.bar(
            top_5_2w.reset_index(),
            x='state',
            y='penetration_rate',
            title='Top 5 States - 2-Wheeler EV Penetration (FY 2024)',
            color='penetration_rate',
            color_continuous_scale='Viridis',
            labels={'penetration_rate': 'Penetration Rate (%)', 'state': 'State'}
        )
        st.plotly_chart(fig_2w, use_container_width=True)
        
        # Display numeric data
        st.markdown("#### 2-Wheeler Penetration Details:")
        st.dataframe(top_5_2w.reset_index()[['state', 'penetration_rate']].round(2))
    
    with col4:
        # Analysis for 4-wheelers
        four_wheeler_penetration = fy_2024_state[
            fy_2024_state['vehicle_category'] == '4-wheeler'
        ].groupby('state').agg({
            'electric_vehicles': 'sum',
            'total_vehicles': 'sum'
        })
        four_wheeler_penetration['penetration_rate'] = (
            four_wheeler_penetration['electric_vehicles'] / 
            four_wheeler_penetration['total_vehicles'] * 100
        )
        top_5_4w = four_wheeler_penetration.nlargest(5, 'penetration_rate')
        
        fig_4w = px.bar(
            top_5_4w.reset_index(),
            x='state',
            y='penetration_rate',
            title='Top 5 States - 4-Wheeler EV Penetration (FY 2024)',
            color='penetration_rate',
            color_continuous_scale='Viridis',
            labels={'penetration_rate': 'Penetration Rate (%)', 'state': 'State'}
        )
        st.plotly_chart(fig_4w, use_container_width=True)
        
        # Display numeric data
        st.markdown("#### 4-Wheeler Penetration Details:")
        st.dataframe(top_5_4w.reset_index()[['state', 'penetration_rate']].round(2))

    # Question 3: States with Negative Penetration
    st.header("3. States with Declining EV Penetration (FY 2022-2024)")
    
    # Calculate yearly penetration rates
    yearly_penetration = ev_sales_state.groupby(['state', 'fiscal_year']).agg({
        'electric_vehicles': 'sum',
        'total_vehicles': 'sum'
    }).reset_index()
    
    yearly_penetration['penetration_rate'] = (
        yearly_penetration['electric_vehicles'] / 
        yearly_penetration['total_vehicles'] * 100
    )
    
    # Calculate year-over-year change
    penetration_change = yearly_penetration.pivot(
        index='state',
        columns='fiscal_year',
        values='penetration_rate'
    ).reset_index()
    
    penetration_change['change_22_24'] = penetration_change[2024] - penetration_change[2022]
    declining_states = penetration_change[penetration_change['change_22_24'] < 0].sort_values('change_22_24')
    
    if not declining_states.empty:
        # Create visualization
        fig_decline = px.bar(
            declining_states,
            x='state',
            y='change_22_24',
            title='States with Declining EV Penetration (FY 2022-2024)',
            color='change_22_24',
            color_continuous_scale='Reds_r',
            labels={
                'change_22_24': 'Change in Penetration Rate (%)',
                'state': 'State'
            }
        )
        st.plotly_chart(fig_decline, use_container_width=True)
        
        # Display numeric data
        st.markdown("#### Detailed Analysis of Declining States:")
        st.dataframe(
            declining_states[['state', 2022, 2024, 'change_22_24']]
            .round(2)
            .rename(columns={
                2022: 'FY 2022 Rate (%)',
                2024: 'FY 2024 Rate (%)',
                'change_22_24': 'Change (%)'
            })
        )
    else:
        st.success("No states showed declining EV penetration from FY 2022 to 2024")

    # Add insights and explanations
    st.markdown("""
    ### Key Findings:
    
    1. **2-Wheeler Manufacturer Analysis (FY 2023-24)**
        - Comparison shows market leadership changes
        - Clear differentiation between market leaders and smaller players
        - Year-over-year growth patterns in manufacturer performance
        
    2. **State-wise EV Penetration (FY 2024)**
        - Distinct patterns between 2-wheeler and 4-wheeler adoption
        - Regional variations in EV preference
        - Impact of state policies on adoption rates
        
    3. **Penetration Trend Analysis (FY 2022-24)**
        - Identification of challenging markets
        - Potential areas for policy intervention
        - Understanding of market stability and growth patterns
    """)

if __name__ == "__main__":
    main()
