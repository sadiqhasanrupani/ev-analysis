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
st.markdown(
    """
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
    /* ADHD-friendly styles */
    .adhd-insight-box {
        background-color: #f8f9fa;
        border-left: 5px solid #FF5722;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
        font-size: 1.1em;
    }
    .adhd-insight-box h4 {
        color: #FF5722;
        margin-bottom: 10px;
    }
    .adhd-insight-box ul {
        padding-left: 20px;
    }
    .adhd-insight-box li {
        margin-bottom: 8px;
    }
    .adhd-insight-box .highlight {
        background-color: #FFECB3;
        padding: 2px 4px;
        border-radius: 3px;
    }
    .adhd-key-number {
        font-size: 1.2em;
        font-weight: bold;
        color: #FF5722;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Helper function to load data
@st.cache_data
def load_data():
    # Configure logging
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "data_loading.log"
                )
            ),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("ev_analysis_data_loader")

    # Get the current file's directory
    current_file_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate up to the project root directory (3 levels up from current file)
    # Current file is in /app/research-analysis/top10_states_with_highest_cagr/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))

    logger.info(f"Project root identified as: {project_root}")

    # Define data paths - using absolute path to avoid relative path issues
    data_folder = os.path.join(project_root, "data")
    state_sales_path = os.path.join(
        data_folder, "raw/electric_vehicle_sales_by_state.csv"
    )
    dim_date_path = os.path.join(data_folder, "raw/dim_date.csv")

    logger.info(f"Sales data path: {state_sales_path}")
    logger.info(f"Date dimension path: {dim_date_path}")

    try:
        # Load the primary CSV file - electric_vehicle_sales_by_state.csv
        raw_data = pd.read_csv(state_sales_path)
        file_size = os.path.getsize(state_sales_path) / (1024 * 1024)  # Size in MB
        rows, cols = raw_data.shape

        logger.info(f"Sales data loaded successfully from: {state_sales_path}")
        logger.info(f"File size: {file_size:.2f} MB, Rows: {rows}, Columns: {cols}")

        # Load the date dimension table to get fiscal years
        try:
            dim_date = pd.read_csv(dim_date_path)
            logger.info(
                f"Date dimension data loaded successfully from: {dim_date_path}"
            )

            # Merge the sales data with the date dimension to get fiscal years
            merge_df = pd.merge(raw_data, dim_date, on="date", how="left")
            logger.info(
                f"Data merged successfully. Shape after merge: {merge_df.shape}"
            )

            # Check if we have fiscal_year column after merge
            if "fiscal_year" not in merge_df.columns:
                logger.warning(
                    "fiscal_year column not found after merge. Check date format compatibility."
                )
                # Fall back to using calendar year
                merge_df["date"] = pd.to_datetime(merge_df["date"], format="%d-%b-%y")
                merge_df["fiscal_year"] = merge_df["date"].dt.year
                logger.info("Created fiscal_year from calendar year as fallback.")
                st.sidebar.warning(
                    "Using calendar year as fiscal_year due to merge failure."
                )

            # Aggregate data by state and fiscal year - summing total and EV sales
            state_sales = (
                merge_df.groupby(["state", "fiscal_year"])[
                    ["electric_vehicles_sold", "total_vehicles_sold"]
                ]
                .sum()
                .reset_index()
            )

            # Show success message
            st.sidebar.success(f"Data loaded from: electric_vehicle_sales_by_state.csv")
            st.sidebar.info(f"Merged with fiscal year data from: dim_date.csv")
            st.sidebar.info(
                f"Processed data: {state_sales.shape[0]} rows, {state_sales.shape[1]} columns"
            )

            logger.info(
                f"Data processed successfully with fiscal years: {state_sales.shape[0]} rows, {state_sales.shape[1]} columns"
            )

            # Return the processed data
            return state_sales

        except Exception as e:
            # If date dimension load fails, fall back to calendar year
            logger.error(
                f"Error loading date dimension data: {str(e)}. Falling back to calendar year."
            )
            st.sidebar.warning(
                f"Could not load fiscal year data. Using calendar year instead."
            )

            # Process the data - convert date to datetime and extract year
            raw_data["date"] = pd.to_datetime(raw_data["date"], format="%d-%b-%y")
            raw_data["fiscal_year"] = raw_data[
                "date"
            ].dt.year  # Use calendar year but name column fiscal_year for consistency

            # Aggregate data by state and year - summing total and EV sales
            state_sales = (
                raw_data.groupby(["state", "fiscal_year"])[
                    ["electric_vehicles_sold", "total_vehicles_sold"]
                ]
                .sum()
                .reset_index()
            )

            # Show message
            st.sidebar.success(f"Data loaded from: electric_vehicle_sales_by_state.csv")
            st.sidebar.info(
                f"Processed data: {state_sales.shape[0]} rows, {state_sales.shape[1]} columns"
            )

            logger.info(
                f"Data processed with calendar year as fiscal_year: {state_sales.shape[0]} rows, {state_sales.shape[1]} columns"
            )

            # Return the processed data
            return state_sales

    except Exception as e:
        logger.error(f"Error loading or processing data: {str(e)}")
        st.error(f"Error loading or processing data: {str(e)}")

        # If all attempts fail, create simulated data
        logger.error("Data loading failed. Using simulated data.")
        st.error("Using simulated data for demonstration.")

        # Create a simple simulated dataset
        states = ["State_" + str(i) for i in range(1, 31)]
        years = [2022, 2023, 2024]

        # Generate simulated data
        data = []
        for state in states:
            for year in years:
                total_sales = np.random.randint(50000, 500000)
                ev_sales = np.random.randint(2000, 50000)
                data.append(
                    {
                        "state": state,
                        "year": year,
                        "total_vehicles_sold": total_sales,
                        "electric_vehicles_sold": ev_sales,
                    }
                )

        state_sales = pd.DataFrame(data)
        return state_sales

    # If primary paths fail, do a more exhaustive search
    logger.warning(
        "All direct paths failed, searching recursively through project directory"
    )
    if not is_production:
        st.warning("Searching for EV sales data files in project directory...")

    found_files = []
    searched_dirs = 0
    for root, _, files in os.walk(project_root):
        searched_dirs += 1
        for file in files:
            if (
                "ev_sales" in file.lower() or "sales_by_state" in file.lower()
            ) and file.endswith(".csv"):
                found_files.append(os.path.join(root, file))

    logger.info(
        f"Searched {searched_dirs} directories, found {len(found_files)} potential data files"
    )

    # If found, try to load each one until success
    for found_path in found_files:
        try:
            logger.info(f"Attempting to load from found file: {found_path}")
            state_sales = pd.read_csv(found_path)

            # Verify this is the right kind of data by checking for required columns
            required_columns = [
                "state",
                "year",
                "total_vehicles_sold",
                "electric_vehicles_sold",
            ]
            if all(col in state_sales.columns for col in required_columns):
                logger.info(f"Successfully loaded valid data from: {found_path}")

                if not is_production:
                    st.sidebar.success(
                        f"Found and loaded data from: {os.path.basename(found_path)}"
                    )
                else:
                    st.sidebar.success("Data loaded successfully")

                return state_sales.copy()
            else:
                logger.warning(f"File has wrong format (missing columns): {found_path}")
                continue
        except Exception as e:
            logger.error(f"Error loading found file {found_path}: {str(e)}")
            continue

    # If all attempts fail, create simulated data
    logger.error("All data loading attempts failed. Using simulated data.")
    if is_production:
        st.error("Error loading production data. Please contact support.")
    else:
        st.error(
            "All attempts to load data failed. Using simulated data for demonstration."
        )

    # Create a simple simulated dataset
    states = ["State_" + str(i) for i in range(1, 31)]
    years = [2022, 2023, 2024]

    # Generate simulated data
    data = []
    for state in states:
        for year in years:
            total_sales = np.random.randint(50000, 500000)
            ev_sales = np.random.randint(2000, 50000)
            data.append(
                {
                    "state": state,
                    "year": year,
                    "total_vehicles_sold": total_sales,
                    "electric_vehicles_sold": ev_sales,
                }
            )

    state_sales = pd.DataFrame(data)
    return state_sales


# Function to calculate CAGRs
def calculate_cagrs(state_sales, start_year, end_year, sales_type="total"):
    """Calculate CAGR for different sales types between specified fiscal years"""
    # Filter by fiscal years - create an explicit copy to avoid SettingWithCopyWarning
    filtered_data = state_sales.loc[
        state_sales["fiscal_year"].isin([start_year, end_year])
    ].copy()

    # Determine which column to use based on sales_type
    sales_column = "total_vehicles_sold"  # Default value
    if sales_type == "total":
        sales_column = "total_vehicles_sold"
    elif sales_type == "ev":
        sales_column = "electric_vehicles_sold"
    elif sales_type == "non_ev":
        # Create non-EV sales column if it doesn't exist
        filtered_data["none_ev_sales"] = (
            filtered_data["total_vehicles_sold"]
            - filtered_data["electric_vehicles_sold"]
        )
        sales_column = "none_ev_sales"

    # Group by state and fiscal year
    grouped = filtered_data.groupby(["state", "fiscal_year"], as_index=False)[
        sales_column
    ].sum()

    # Pivot data
    pivot_data = grouped.pivot(
        index="state", columns="fiscal_year", values=sales_column
    ).reset_index()

    # Rename columns for clarity
    pivot_data = pivot_data.rename(
        columns={start_year: f"sales_{start_year}", end_year: f"sales_{end_year}"}
    )

    # Calculate CAGR
    years_diff = end_year - start_year
    pivot_data["CAGR"] = (
        (
            (pivot_data[f"sales_{end_year}"] / pivot_data[f"sales_{start_year}"])
            ** (1 / years_diff)
            - 1
        )
        * 100
    ).round(2)

    # Handle zero or missing values
    pivot_data = pivot_data.dropna(subset=[f"sales_{start_year}", f"sales_{end_year}"])
    pivot_data = pivot_data[pivot_data[f"sales_{start_year}"] > 0]

    return pivot_data


# Create comparison data between different CAGRs
def create_cagr_comparison(total_cagr, ev_cagr):
    """Create comparison dataframe between total CAGR and EV CAGR"""
    comparison = pd.merge(
        total_cagr[["state", "CAGR"]].rename(columns={"CAGR": "Total_CAGR"}),
        ev_cagr[["state", "CAGR"]].rename(columns={"CAGR": "EV_CAGR"}),
        on="state",
        how="inner",
    )
    return comparison


# Main function to run the app
def main():
    # Load data
    state_sales = load_data()

    # Sidebar
    st.sidebar.title("CAGR Analysis Controls")

    # Year range selector
    available_years = sorted(state_sales["fiscal_year"].unique())
    start_year, end_year = st.sidebar.select_slider(
        "Select Fiscal Year Range for CAGR Calculation",
        options=available_years,
        value=(2022, 2024),
    )

    st.sidebar.markdown("---")

    # Region filter
    all_states = sorted(state_sales["state"].unique())
    selected_states = st.sidebar.multiselect(
        "Filter by States/UTs", options=all_states, default=[]
    )

    # Apply state filter if selected
    if selected_states:
        filtered_state_sales = state_sales[state_sales["state"].isin(selected_states)]
    else:
        filtered_state_sales = state_sales

    st.sidebar.markdown("---")

    # Top N selector
    top_n = st.sidebar.slider("Select Number of Top States to Display", 5, 20, 10)

    # Analysis type selector
    analysis_type = st.sidebar.radio(
        "Select Analysis View",
        [
            "Overview",
            "Total Vehicle Sales",
            "EV Sales",
            "Non-EV Sales",
            "Comparison Analysis",
        ],
    )

    # Calculate fresh CAGRs
    total_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "total")
    ev_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "ev")
    non_ev_cagr = calculate_cagrs(filtered_state_sales, start_year, end_year, "non_ev")

    # Get top N states
    top10_total = total_cagr.sort_values("CAGR", ascending=False).head(top_n)
    top10_ev = ev_cagr.sort_values("CAGR", ascending=False).head(top_n)
    top10_non_ev = non_ev_cagr.sort_values("CAGR", ascending=False).head(top_n)

    # Create comparison data
    comparison = create_cagr_comparison(total_cagr, ev_cagr)

    # Create content based on selected analysis type
    if analysis_type == "Overview":
        display_overview(
            top10_total, top10_ev, top10_non_ev, comparison, start_year, end_year
        )
    elif analysis_type == "Total Vehicle Sales":
        display_total_vehicle_analysis(top10_total, start_year, end_year)
    elif analysis_type == "EV Sales":
        display_ev_analysis(top10_ev, start_year, end_year)
    elif analysis_type == "Non-EV Sales":
        display_non_ev_analysis(top10_non_ev, start_year, end_year)
    elif analysis_type == "Comparison Analysis":
        display_comparison_analysis(comparison, start_year, end_year)


# Functions to display different analysis views
def display_overview(
    top10_total, top10_ev, top10_non_ev, comparison, start_year, end_year
):
    st.title(f"Vehicle Sales CAGR Analysis (FY {start_year}-{end_year})")

    # Overview metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Total Vehicle CAGR", f"{top10_total['CAGR'].mean():.2f}%")
    with col2:
        st.metric("Average EV CAGR", f"{top10_ev['CAGR'].mean():.2f}%")
    with col3:
        st.metric("Average Non-EV CAGR", f"{top10_non_ev['CAGR'].mean():.2f}%")

    st.markdown("---")

    # ADHD-friendly Key insights box
    st.markdown(
        f"""
    <div class="adhd-insight-box">
        <h4>⚡ Quick Insights: Top States by CAGR (FY {start_year}-{end_year})</h4>
        <ul>
            <li><span class="highlight">Meghalaya</span> leads vehicle sales growth with <span class="adhd-key-number">+28.47%</span> CAGR</li>
            <li><span class="highlight">Northeastern states</span> show better resilience in overall market</li>
            <li><span class="highlight">EV growth</span> is happening independently from traditional vehicle sales</li>
            <li><span class="highlight">Meghalaya's EV sales</span> grew at an incredible <span class="adhd-key-number">+476.63%</span> CAGR</li>
            <li><span class="highlight">Policy differences</span> likely driving regional variations in EV adoption</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Standard insights box
    st.markdown(
        """
    <div class="insights-box">
        <h4>Key Insights</h4>
        <ul>
            <li>Overall vehicle sales showed varying patterns across states during this period.</li>
            <li>Electric vehicle sales demonstrated significant growth in several states.</li>
            <li>There's a weak correlation between total vehicle CAGR and EV CAGR, suggesting independent market dynamics.</li>
            <li>States like Meghalaya, Goa, and Karnataka showed the strongest overall growth.</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Summary tabs for each category
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Total Vehicle Sales", "EV Sales", "Non-EV Sales", "CAGR Comparison"]
    )

    with tab1:
        fig = create_horizontal_bar_chart(
            top10_total.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by Total Vehicle Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = create_horizontal_bar_chart(
            top10_ev.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by EV Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = create_horizontal_bar_chart(
            top10_non_ev.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by Non-EV Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        fig = create_scatter_plot_with_regression(
            comparison,
            "Total_CAGR",
            "EV_CAGR",
            "state",
            f"Relationship Between Total Vehicle CAGR and EV CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)


def display_total_vehicle_analysis(top10_total, start_year, end_year):
    st.title(f"Total Vehicle Sales CAGR Analysis (FY {start_year}-{end_year})")

    # Show data table
    st.subheader("Top States by Total Vehicle Sales CAGR")
    st.dataframe(
        top10_total.sort_values("CAGR", ascending=False).style.background_gradient(
            cmap="RdYlGn", subset=["CAGR"]
        )
    )

    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Bubble Chart"])

    with tab1:
        fig = create_horizontal_bar_chart(
            top10_total.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by Total Vehicle Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Create a copy of the dataframe and add absolute value of CAGR for sizing
        plot_df = top10_total.sort_values("CAGR", ascending=False).copy()
        plot_df["CAGR_abs"] = plot_df["CAGR"].abs()

        fig = px.scatter(
            plot_df,
            x=f"sales_{start_year}",
            y=f"sales_{end_year}",
            size="CAGR_abs",  # Use absolute value for size
            color="CAGR",  # Use original value for color
            hover_name="state",
            size_max=50,
            color_continuous_scale="RdYlGn",
            title=f"Vehicle Sales Comparison: FY {start_year} vs FY {end_year} with CAGR",
            hover_data={
                "CAGR": True,
                "CAGR_abs": False,
            },  # Show CAGR in hover, hide CAGR_abs
        )
        st.plotly_chart(fig, use_container_width=True)

    # Analysis insights
    st.subheader("Analysis Insights")

    # ADHD-friendly insights
    st.markdown(
        f"""
    <div class="adhd-insight-box">
        <h4>⚡ Total Vehicle Sales Growth Leaders (FY {start_year}-{end_year})</h4>
        <ul>
            <li><span class="highlight">Meghalaya:</span> <span class="adhd-key-number">+28.47%</span> CAGR — highest growth state</li>
            <li><span class="highlight">Goa:</span> <span class="adhd-key-number">+27.41%</span> CAGR — strong tourism-driven sales</li>
            <li><span class="highlight">Karnataka:</span> <span class="adhd-key-number">+25.28%</span> CAGR — tech hub with rising incomes</li>
            <li><span class="highlight">Policy impact:</span> States with supportive tax structure showed better growth</li>
            <li><span class="highlight">Action point:</span> Focus marketing in these high-growth regions</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Standard insights
    st.markdown(
        """
    Between 2022 and 2024, India's overall vehicle sales market showed varied performance, with some states experiencing significant growth.
    
    The top performers like Meghalaya, Goa, and Karnataka demonstrated exceptional growth rates above 25% CAGR. States with strong economic indicators, tourism, and supportive policies performed particularly well.
    
    These insights point toward regions where expanded dealership networks, targeted promotional strategies, and increased inventory allocation could maximize returns.
    """
    )


def display_ev_analysis(top10_ev, start_year, end_year):
    st.title(f"Electric Vehicle Sales CAGR Analysis (FY {start_year}-{end_year})")

    # Show data table
    st.subheader("Top States by EV Sales CAGR")
    st.dataframe(
        top10_ev.sort_values("CAGR", ascending=False).style.background_gradient(
            cmap="RdYlGn", subset=["CAGR"]
        )
    )

    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Growth Chart"])

    with tab1:
        fig = create_horizontal_bar_chart(
            top10_ev.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by EV Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Create growth comparison chart
        fig = px.line(
            top10_ev,
            x="state",
            y=[f"sales_{start_year}", f"sales_{end_year}"],
            title=f"EV Sales Growth: FY {start_year} vs FY {end_year}",
            labels={
                "value": "Number of EV Sales",
                "variable": "Fiscal Year",
                "state": "State",
            },
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        st.plotly_chart(fig, use_container_width=True)

    # Analysis insights
    st.subheader("Analysis Insights")

    # ADHD-friendly insights
    st.markdown(
        f"""
    <div class="adhd-insight-box">
        <h4>⚡ EV Growth Champions (FY {start_year}-{end_year})</h4>
        <ul>
            <li><span class="highlight">Meghalaya:</span> <span class="adhd-key-number">+476.63%</span> CAGR — extraordinary EV boom</li>
            <li><span class="highlight">Tripura:</span> <span class="adhd-key-number">+229.50%</span> CAGR — rapid adoption rate</li>
            <li><span class="highlight">Nagaland:</span> <span class="adhd-key-number">+200.00%</span> CAGR — tripled EV presence</li>
            <li><span class="highlight">Northeast focus:</span> Region showing exceptional EV growth potential</li>
            <li><span class="highlight">Key takeaway:</span> EV growth isn't limited to traditional high-income states</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Standard insights
    st.markdown(
        """
    The electric vehicle market shows a dynamic growth pattern across states. Multiple states achieved triple-digit CAGR growth 
    for EV sales, with Meghalaya, Tripura, and Nagaland leading the transformation.
    
    This exceptional variation in EV adoption suggests that specific local factors, policy incentives, or infrastructure developments 
    are driving EV growth independently from overall market trends. Notably, northeastern states are emerging as surprising 
    leaders in the EV revolution, suggesting untapped market potential in regions traditionally considered peripheral to automotive markets.
    
    States with positive EV CAGR represent important emerging markets for electric mobility and should be prioritized for charging 
    infrastructure expansion.
    """
    )


def display_non_ev_analysis(top10_non_ev, start_year, end_year):
    st.title(f"Non-EV Vehicle Sales CAGR Analysis (FY {start_year}-{end_year})")

    # Show data table
    st.subheader("Top States by Non-EV Sales CAGR")
    st.dataframe(
        top10_non_ev.sort_values("CAGR", ascending=False).style.background_gradient(
            cmap="RdYlGn", subset=["CAGR"]
        )
    )

    # Visualization tabs
    tab1, tab2 = st.tabs(["Bar Chart", "Comparison Chart"])

    with tab1:
        fig = create_horizontal_bar_chart(
            top10_non_ev.sort_values("CAGR"),
            "state",
            "CAGR",
            f"Top States by Non-EV Sales CAGR (FY {start_year}-{end_year})",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Create a grouped bar chart comparing start and end year
        df_for_chart = top10_non_ev.sort_values("CAGR", ascending=False)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df_for_chart["state"],
                y=df_for_chart[f"sales_{start_year}"],
                name=f"FY {start_year} Sales",
                marker_color="lightskyblue",
            )
        )
        fig.add_trace(
            go.Bar(
                x=df_for_chart["state"],
                y=df_for_chart[f"sales_{end_year}"],
                name=f"FY {end_year} Sales",
                marker_color="royalblue",
            )
        )

        fig.update_layout(
            title=f"Non-EV Vehicle Sales: FY {start_year} vs FY {end_year}",
            xaxis_title="State",
            yaxis_title="Number of Non-EV Vehicles Sold",
            barmode="group",
            xaxis={"categoryorder": "total ascending"},
        )

        st.plotly_chart(fig, use_container_width=True)

    # Analysis insights
    st.subheader("Analysis Insights")

    # ADHD-friendly insights
    st.markdown(
        f"""
    <div class="adhd-insight-box">
        <h4>⚡ Non-EV Market Leaders (FY {start_year}-{end_year})</h4>
        <ul>
            <li><span class="highlight">Meghalaya:</span> <span class="adhd-key-number">+27.5%</span> CAGR — strongest traditional market</li>
            <li><span class="highlight">Goa:</span> <span class="adhd-key-number">+27.2%</span> CAGR — tourism driving traditional vehicles</li>
            <li><span class="highlight">Karnataka:</span> <span class="adhd-key-number">+25.1%</span> CAGR — balanced growth across vehicle types</li>
            <li><span class="highlight">Pattern:</span> States with good non-EV growth often show good EV growth too</li>
            <li><span class="highlight">Strategic insight:</span> These states have healthy overall automotive ecosystems</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Standard insights
    st.markdown(
        """
    Non-electric vehicle sales showed strong growth in several key states, with Meghalaya, Goa, and Karnataka 
    leading the way. These states maintained robust growth in traditional vehicles while simultaneously embracing electric mobility.
    
    The parallel growth in both traditional and electric vehicles in these states suggests healthy overall automotive markets with 
    consumers making choices based on their specific needs rather than policy pressure alone.
    
    States with strong growth in non-EV sales typically benefit from robust dealer networks, efficient financing ecosystems, 
    and consumer preferences that value vehicle ownership. These markets present excellent opportunities for hybrid strategy approaches 
    that offer both traditional and electric options to consumers.
    """
    )


def display_comparison_analysis(comparison, start_year, end_year):
    st.title(f"CAGR Comparison Analysis (FY {start_year}-{end_year})")

    # Show correlation stats
    correlation = comparison["Total_CAGR"].corr(comparison["EV_CAGR"])

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
        "Total_CAGR",
        "EV_CAGR",
        "state",
        f"Relationship Between Total Vehicle CAGR and EV CAGR (FY {start_year}-{end_year})",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show data table
    st.subheader("Total CAGR vs EV CAGR by State")
    st.dataframe(
        comparison.sort_values("EV_CAGR", ascending=False).style.background_gradient(
            cmap="RdYlGn", subset=["Total_CAGR", "EV_CAGR"]
        )
    )

    # Quadrant analysis
    st.subheader("Quadrant Analysis")

    # Create scatter with quadrants
    total_mean = comparison["Total_CAGR"].mean()
    ev_mean = comparison["EV_CAGR"].mean()

    fig = px.scatter(
        comparison,
        x="Total_CAGR",
        y="EV_CAGR",
        hover_name="state",
        # Removed the text="state" parameter to hide data labels
        color="state",
        title=f"Quadrant Analysis: Total Vehicle CAGR vs EV CAGR (FY {start_year}-{end_year})",
    )

    # Add quadrant lines
    fig.add_shape(
        type="line",
        x0=total_mean,
        y0=min(comparison["EV_CAGR"]),
        x1=total_mean,
        y1=max(comparison["EV_CAGR"]),
        line=dict(color="gray", width=1, dash="dash"),
    )
    fig.add_shape(
        type="line",
        x0=min(comparison["Total_CAGR"]),
        y0=ev_mean,
        x1=max(comparison["Total_CAGR"]),
        y1=ev_mean,
        line=dict(color="gray", width=1, dash="dash"),
    )

    # Add quadrant annotations
    fig.add_annotation(
        x=total_mean + (max(comparison["Total_CAGR"]) - total_mean) / 2,
        y=ev_mean + (max(comparison["EV_CAGR"]) - ev_mean) / 2,
        text="Better Than Average<br>(Both Total & EV)",
        showarrow=False,
        font=dict(size=10),
    )
    fig.add_annotation(
        x=total_mean - (total_mean - min(comparison["Total_CAGR"])) / 2,
        y=ev_mean + (max(comparison["EV_CAGR"]) - ev_mean) / 2,
        text="Better EV Growth<br>Worse Total Growth",
        showarrow=False,
        font=dict(size=10),
    )
    fig.add_annotation(
        x=total_mean + (max(comparison["Total_CAGR"]) - total_mean) / 2,
        y=ev_mean - (ev_mean - min(comparison["EV_CAGR"])) / 2,
        text="Better Total Growth<br>Worse EV Growth",
        showarrow=False,
        font=dict(size=10),
    )
    fig.add_annotation(
        x=total_mean - (total_mean - min(comparison["Total_CAGR"])) / 2,
        y=ev_mean - (ev_mean - min(comparison["EV_CAGR"])) / 2,
        text="Worse Than Average<br>(Both Total & EV)",
        showarrow=False,
        font=dict(size=10),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ADHD-friendly insights
    st.markdown(
        f"""
    <div class="adhd-insight-box">
        <h4>⚡ Total vs EV Growth Patterns (FY {start_year}-{end_year})</h4>
        <ul>
            <li><span class="highlight">Stand-out state:</span> <span class="adhd-key-number">Meghalaya</span> — exceptional in both total (+28.5%) and EV (+476.6%) growth</li>
            <li><span class="highlight">Independent markets:</span> Low correlation between total and EV growth (R² = 0.21)</li>
            <li><span class="highlight">Sweet spot:</span> Northeastern states showing strongest combined performance</li>
            <li><span class="highlight">Key finding:</span> EV market success doesn't depend on traditional market health</li>
            <li><span class="highlight">Action point:</span> Target EV investments in high-EV-CAGR states regardless of total market performance</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Standard insights
    st.markdown(
        """
    <div class="insights-box">
        <h4>Key Insights from CAGR Comparison</h4>
        <p>The relationship between total vehicle CAGR and EV CAGR reveals distinct patterns in India's automotive market transition:</p>
        <ol>
            <li><strong>Weak correlation</strong> indicates EV adoption is not strongly tied to overall vehicle sales trends, suggesting independent market dynamics.</li>
            <li><strong>States with positive EV growth</strong> demonstrate early adoption of electric mobility regardless of overall market conditions.</li>
            <li><strong>Northeastern states</strong> show exceptional performance across both metrics, suggesting untapped market potential.</li>
            <li><strong>Quadrant analysis</strong> helps identify states where targeted EV promotion strategies may be most effective based on existing market trends.</li>
            <li><strong>Meghalaya's exceptional performance</strong> (28.47% total CAGR, 476.63% EV CAGR) makes it the model state for studying successful EV market development.</li>
        </ol>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Helper functions for visualizations
def create_horizontal_bar_chart(df, x_col, y_col, title):
    """Create a horizontal bar chart with labels"""
    # Create color array based on values
    colors = ["#2ecc71" if val > 0 else "#e74c3c" for val in df[y_col]]

    fig = px.bar(
        df,
        y=x_col,
        x=y_col,
        orientation="h",
        text=y_col,
        title=title,
        color=y_col,
        color_continuous_scale="RdYlGn",
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")

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
        labels={x_col: "Total Vehicles CAGR (%)", y_col: "EV CAGR (%)"},
    )

    # Update marker style
    fig.update_traces(
        marker=dict(size=10, color="skyblue"),
        textposition="top center",
        textfont=dict(size=8),
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
            x=df[x_col].min() + (df[x_col].max() - df[x_col].min()) * 0.05,
            y=df[y_col].max() - (df[y_col].max() - df[y_col].min()) * 0.05,
            text=f"y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.3f}",
            showarrow=False,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="darkgray",
            borderwidth=1,
        )
    except:
        st.warning("Could not fit regression line. Check your data.")

    # Layout tweaks
    fig.update_layout(
        title=dict(x=0.5, xanchor="center", font=dict(size=18)),
        plot_bgcolor="white",
        xaxis=dict(
            showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="gray"
        ),
        yaxis=dict(
            showgrid=True, gridcolor="lightgray", zeroline=True, zerolinecolor="gray"
        ),
    )

    return fig


# Run the app
if __name__ == "__main__":
    main()
