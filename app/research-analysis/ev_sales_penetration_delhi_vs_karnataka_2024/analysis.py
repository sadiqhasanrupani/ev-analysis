import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# Path to the data files
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data"
)
EV_SALES_BY_STATE_PATH = os.path.join(
    DATA_DIR, "processed", "ev_sales_by_state_enhanced_20250806.csv"
)


def load_data():
    """Load and prepare the data for analysis"""
    # Load the data
    df = pd.read_csv(EV_SALES_BY_STATE_PATH)

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Calculate penetration rate
    df["ev_penetration"] = (
        df["electric_vehicles_sold"] / df["total_vehicles_sold"]
    ) * 100

    # Getting fiscal year
    df["fiscal_year"] = df["date"].dt.year.where(
        df["date"].dt.month < 4, df["date"].dt.year + 1
    )

    # Filter for fiscal year 2024 data and Delhi and Karnataka states
    # filter out by 2024 and data should of delhi and karnataka
    df_filtered = df[df["fiscal_year"] == 2024]
    df_filtered = df_filtered[df_filtered["state"].isin(["Delhi", "Karnataka"])]

    return df, df_filtered


def calculate_kpis(df_filtered):
    """Calculate Key Performance Indicators (KPIs)"""
    # Group by state and vehicle category to get total EV sales and penetration rates
    kpis = (
        df_filtered.groupby(["state", "vehicle_category"])
        .agg({"electric_vehicles_sold": "sum", "total_vehicles_sold": "sum"})
        .reset_index()
    )

    # Calculate penetration rate for each vehicle category
    kpis["ev_penetration"] = (
        kpis["electric_vehicles_sold"] / kpis["total_vehicles_sold"]
    ) * 100

    # Calculate overall KPIs by state - using the same approach as in the notebook
    overall_kpis = (
        df_filtered.groupby("state")
        .agg(
            {
                "electric_vehicles_sold": "sum",
                "total_vehicles_sold": "sum",
                "ev_penetration": "mean",  # Calculate mean of penetration rates directly
            }
        )
        .reset_index()
    )

    # No need to calculate overall penetration rate as it's now taken directly from the mean
    # Rename the column to match the rest of the code
    overall_kpis = overall_kpis.rename(columns={"ev_penetration": "avg_ev_penetration"})
    # Keep the original calculation for backwards compatibility with the rest of the code
    overall_kpis["ev_penetration"] = overall_kpis["avg_ev_penetration"]

    # Calculate market share percentages (for the two states combined)
    total_ev_sales = overall_kpis["electric_vehicles_sold"].sum()
    overall_kpis["market_share"] = (
        overall_kpis["electric_vehicles_sold"] / total_ev_sales * 100
    )

    # Add a 'Combined' category to kpis dataframe for overall stats
    for _, row in overall_kpis.iterrows():
        new_row = {
            "state": row["state"],
            "vehicle_category": "Combined",
            "electric_vehicles_sold": row["electric_vehicles_sold"],
            "total_vehicles_sold": row["total_vehicles_sold"],
            "ev_penetration": row["ev_penetration"],
        }
        kpis = pd.concat([kpis, pd.DataFrame([new_row])], ignore_index=True)

    return kpis, overall_kpis


def create_monthly_trend_analysis(df_filtered):
    """Analyze monthly trends for 2024"""
    # Group by state, month and aggregate the metrics
    monthly_trend = (
        df_filtered.groupby(["state", "month"])
        .agg({"electric_vehicles_sold": "sum", "total_vehicles_sold": "sum"})
        .reset_index()
    )

    # Calculate penetration rate
    monthly_trend["ev_penetration"] = (
        monthly_trend["electric_vehicles_sold"] / monthly_trend["total_vehicles_sold"]
    ) * 100

    # Sort by month for proper trend visualization
    monthly_trend = monthly_trend.sort_values(by=["state", "month"])

    return monthly_trend


def create_category_comparison(df_filtered):
    """Compare vehicle categories between Delhi and Karnataka"""
    # Group by state, vehicle category and calculate metrics
    category_comparison = (
        df_filtered.groupby(["state", "vehicle_category"])
        .agg({"electric_vehicles_sold": "sum", "total_vehicles_sold": "sum"})
        .reset_index()
    )

    # Calculate penetration rate
    category_comparison["ev_penetration"] = (
        category_comparison["electric_vehicles_sold"]
        / category_comparison["total_vehicles_sold"]
    ) * 100

    # Calculate percentage distribution of EVs by category within each state
    state_totals = (
        category_comparison.groupby("state")["electric_vehicles_sold"]
        .sum()
        .reset_index()
    )
    category_comparison = category_comparison.merge(
        state_totals, on="state", suffixes=("", "_state_total")
    )
    category_comparison["category_percentage"] = (
        category_comparison["electric_vehicles_sold"]
        / category_comparison["electric_vehicles_sold_state_total"]
        * 100
    )

    return category_comparison


def create_dashboard():
    """Create Streamlit dashboard"""
    # Set page configuration
    st.set_page_config(
        page_title="Delhi vs Karnataka EV Analysis FY 2024",
        page_icon="🚗",
        layout="wide",
    )

    # Page title and introduction
    st.title("🔋 EV Sales & Penetration Analysis: Delhi vs Karnataka (FY 2024)")
    st.markdown(
        """
    This dashboard presents a detailed comparison of Electric Vehicle (EV) sales and penetration rates 
    between Delhi and Karnataka for the fiscal year 2024 (April 2023 - March 2024). 
    The penetration rate is calculated as (electric_vehicles_sold / total_vehicles_sold) * 100.
    Explore the insights through various metrics and visualizations.
    """
    )

    # Load and process data
    df, df_filtered = load_data()

    # Calculate metrics
    kpis, overall_kpis = calculate_kpis(df_filtered)
    monthly_trend = create_monthly_trend_analysis(df_filtered)
    category_comparison = create_category_comparison(df_filtered)

    # Sidebar for filters
    st.sidebar.header("Filters")

    # Vehicle category filter
    categories = ["All"] + sorted(df_filtered["vehicle_category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Vehicle Category", categories)

    # Month range filter
    months = sorted(df_filtered["month"].unique().tolist())
    min_month, max_month = st.sidebar.slider(
        "Month Range",
        min_value=min(months),
        max_value=max(months),
        value=(min(months), max(months)),
    )

    # Add fiscal year information
    st.sidebar.markdown(f"**Fiscal Year:** 2024 (April 2023 - March 2024)")

    # Apply filters to the dataframe
    if selected_category != "All":
        filtered_data = df_filtered[
            df_filtered["vehicle_category"] == selected_category
        ]
    else:
        filtered_data = df_filtered

    filtered_data = filtered_data[
        (filtered_data["month"] >= min_month) & (filtered_data["month"] <= max_month)
    ]

    # Recalculate metrics after filtering
    if not filtered_data.empty:
        filtered_kpis, filtered_overall_kpis = calculate_kpis(filtered_data)
        filtered_monthly_trend = create_monthly_trend_analysis(filtered_data)
        filtered_category_comparison = create_category_comparison(filtered_data)
    else:
        st.error("No data available for the selected filters.")
        return

    # Dashboard Layout
    # Top row: KPI cards
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    # Find the state with higher overall penetration rate
    max_penetration_state = filtered_overall_kpis.loc[
        filtered_overall_kpis["ev_penetration"].idxmax()
    ]["state"]
    penetration_diff = (
        filtered_overall_kpis["ev_penetration"].max()
        - filtered_overall_kpis["ev_penetration"].min()
    )

    # Header for the KPIs section - removed combined penetration rate
    st.markdown(
        "### EV Penetration Rates by State"
    )

    with col1:
        st.metric(
            label="Total EV Sales (Delhi)",
            value=f"{int(filtered_overall_kpis[filtered_overall_kpis['state'] == 'Delhi']['electric_vehicles_sold'].values[0]):,}",
            delta=None,
        )

    with col2:
        st.metric(
            label="Total EV Sales (Karnataka)",
            value=f"{int(filtered_overall_kpis[filtered_overall_kpis['state'] == 'Karnataka']['electric_vehicles_sold'].values[0]):,}",
            delta=None,
        )

    with col3:
        delhi_penetration = filtered_overall_kpis[
            filtered_overall_kpis["state"] == "Delhi"
        ]["ev_penetration"].values[0]
        st.metric(
            label="EV Penetration Rate (Delhi)",
            value=f"{delhi_penetration:.2f}%",
            delta=None,
        )

    with col4:
        karnataka_penetration = filtered_overall_kpis[
            filtered_overall_kpis["state"] == "Karnataka"
        ]["ev_penetration"].values[0]
        st.metric(
            label="EV Penetration Rate (Karnataka)",
            value=f"{karnataka_penetration:.2f}%",
            delta=None,
        )

    # Second row: Additional KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delhi_market_share = filtered_overall_kpis[
            filtered_overall_kpis["state"] == "Delhi"
        ]["market_share"].values[0]
        st.metric(
            label="Market Share (Delhi)", value=f"{delhi_market_share:.2f}%", delta=None
        )

    with col2:
        karnataka_market_share = filtered_overall_kpis[
            filtered_overall_kpis["state"] == "Karnataka"
        ]["market_share"].values[0]
        st.metric(
            label="Market Share (Karnataka)",
            value=f"{karnataka_market_share:.2f}%",
            delta=None,
        )

    with col3:
        st.metric(
            label="Higher Penetration State",
            value=max_penetration_state,
            delta=(
                f"+{penetration_diff:.2f}%"
                if max_penetration_state == "Karnataka"
                else f"-{penetration_diff:.2f}%"
            ),
        )

    with col4:
        # Calculate 2-wheeler to 4-wheeler ratio for each state
        delhi_2w = filtered_kpis[
            (filtered_kpis["state"] == "Delhi")
            & (filtered_kpis["vehicle_category"] == "2-Wheelers")
        ]["electric_vehicles_sold"].sum()
        delhi_4w = filtered_kpis[
            (filtered_kpis["state"] == "Delhi")
            & (filtered_kpis["vehicle_category"] == "4-Wheelers")
        ]["electric_vehicles_sold"].sum()
        karnataka_2w = filtered_kpis[
            (filtered_kpis["state"] == "Karnataka")
            & (filtered_kpis["vehicle_category"] == "2-Wheelers")
        ]["electric_vehicles_sold"].sum()
        karnataka_4w = filtered_kpis[
            (filtered_kpis["state"] == "Karnataka")
            & (filtered_kpis["vehicle_category"] == "4-Wheelers")
        ]["electric_vehicles_sold"].sum()

        delhi_ratio = delhi_2w / delhi_4w if delhi_4w > 0 else 0
        karnataka_ratio = karnataka_2w / karnataka_4w if karnataka_4w > 0 else 0
        ratio_diff = karnataka_ratio - delhi_ratio

        dominant_state = "Karnataka" if karnataka_ratio > delhi_ratio else "Delhi"

        st.metric(
            label="2W:4W EV Ratio Comparison",
            value=dominant_state,
            delta=f"{abs(ratio_diff):.2f}" + " (higher ratio)",
        )

    # Third row: Main visualizations
    st.subheader("EV Sales and Penetration Comparison")

    # Tab layout for different visualization types
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Sales vs. Penetration",
            "Monthly Trends",
            "Vehicle Categories",
            "Comparison Tables",
            "Penetration Analysis",
        ]
    )

    with tab1:
        # Create a grouped bar chart comparing sales and penetration
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "bar"}, {"type": "bar"}]],
            subplot_titles=["EV Sales Distribution", "EV Penetration Rate (%)"],
        )

        # Sales comparison
        fig.add_trace(
            go.Bar(
                x=filtered_overall_kpis["state"],
                y=filtered_overall_kpis["electric_vehicles_sold"],
                text=filtered_overall_kpis["electric_vehicles_sold"].apply(
                    lambda x: f"{int(x):,}"
                ),
                textposition="auto",
                marker_color=["#4C78A8", "#72B7B2"],
                name="EV Sales",
            ),
            row=1,
            col=1,
        )

        # Penetration rate comparison
        fig.add_trace(
            go.Bar(
                x=filtered_overall_kpis["state"],
                y=filtered_overall_kpis["ev_penetration"],
                text=filtered_overall_kpis["ev_penetration"].apply(
                    lambda x: f"{x:.2f}%"
                ),
                textposition="auto",
                marker_color=["#4C78A8", "#72B7B2"],
                name="EV Penetration Rate",
            ),
            row=1,
            col=2,
        )

        # Update layout
        fig.update_layout(
            height=500,
            showlegend=False,
            title_text="EV Sales vs. Penetration Rate: Delhi vs Karnataka (2024)",
            template="plotly_white",
        )

        # Update y-axes
        fig.update_yaxes(title_text="Number of EVs Sold", row=1, col=1)
        fig.update_yaxes(title_text="Penetration Rate (%)", row=1, col=2)

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Create line charts for monthly trends
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "scatter"}, {"type": "scatter"}]],
            subplot_titles=["Monthly EV Sales", "Monthly EV Penetration Rate (%)"],
        )

        # Monthly sales trend
        for state, color in zip(["Delhi", "Karnataka"], ["#4C78A8", "#72B7B2"]):
            state_data = filtered_monthly_trend[
                filtered_monthly_trend["state"] == state
            ]

            fig.add_trace(
                go.Scatter(
                    x=state_data["month"],
                    y=state_data["electric_vehicles_sold"],
                    mode="lines+markers+text",
                    name=f"{state} - Sales",
                    line=dict(color=color, width=3),
                    text=state_data["electric_vehicles_sold"].apply(
                        lambda x: f"{int(x):,}"
                    ),
                    textposition="top center",
                    textfont=dict(size=10),
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=state_data["month"],
                    y=state_data["ev_penetration"],
                    mode="lines+markers+text",
                    name=f"{state} - Penetration",
                    line=dict(color=color, width=3, dash="dash"),
                    text=state_data["ev_penetration"].apply(lambda x: f"{x:.2f}%"),
                    textposition="top center",
                    textfont=dict(size=10),
                ),
                row=1,
                col=2,
            )

        # Update layout
        fig.update_layout(
            height=500,
            title_text="Monthly Trends in EV Sales and Penetration (2024)",
            template="plotly_white",
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center"),
        )

        # Update axes
        fig.update_xaxes(title_text="Month", row=1, col=1)
        fig.update_xaxes(title_text="Month", row=1, col=2)
        fig.update_yaxes(title_text="Number of EVs Sold", row=1, col=1)
        fig.update_yaxes(title_text="Penetration Rate (%)", row=1, col=2)

        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # Vehicle category comparison
        category_data = filtered_category_comparison[
            filtered_category_comparison["vehicle_category"] != "Combined"
        ]

        # Create a grouped bar chart for category comparison
        fig = make_subplots(
            rows=1,
            cols=2,
            specs=[[{"type": "bar"}, {"type": "bar"}]],
            subplot_titles=[
                "EV Sales by Vehicle Category",
                "EV Penetration by Vehicle Category (%)",
            ],
        )

        # Sales by category
        for i, state in enumerate(["Delhi", "Karnataka"]):
            state_data = category_data[category_data["state"] == state]

            fig.add_trace(
                go.Bar(
                    x=state_data["vehicle_category"],
                    y=state_data["electric_vehicles_sold"],
                    name=state,
                    text=state_data["electric_vehicles_sold"].apply(
                        lambda x: f"{int(x):,}"
                    ),
                    textposition="auto",
                    marker_color=["#4C78A8", "#72B7B2"][i],
                    offsetgroup=i,
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=state_data["vehicle_category"],
                    y=state_data["ev_penetration"],
                    name=state,
                    text=state_data["ev_penetration"].apply(lambda x: f"{x:.2f}%"),
                    textposition="auto",
                    marker_color=["#4C78A8", "#72B7B2"][i],
                    offsetgroup=i,
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

        # Update layout
        fig.update_layout(
            height=500,
            barmode="group",
            title_text="EV Comparison by Vehicle Category (2024)",
            template="plotly_white",
            legend=dict(orientation="h", y=1.15, x=0.5, xanchor="center"),
        )

        # Update axes
        fig.update_yaxes(title_text="Number of EVs Sold", row=1, col=1)
        fig.update_yaxes(title_text="Penetration Rate (%)", row=1, col=2)

        st.plotly_chart(fig, use_container_width=True)

        # Copy filtered data
        category_radar = filtered_kpis.copy()

        # Create a radar chart for more comprehensive comparison
        categories = category_radar["vehicle_category"].unique().tolist()
        states = category_radar["state"].unique().tolist()

        # First, let's display the raw data in a table for transparency
        if "2-Wheelers" in categories and "4-Wheelers" in categories:
            # Create a table of raw values
            st.subheader("Raw Data for Radar Chart")
            
            # Create a copy to avoid SettingWithCopyWarning
            raw_data_table = category_radar[["state", "vehicle_category", "ev_penetration", "electric_vehicles_sold"]].copy()
            
            # Create a formatted display column instead of modifying the original
            raw_data_table["penetration_formatted"] = raw_data_table["ev_penetration"].apply(lambda x: f"{x:.2f}%")
            
            # Rename columns for better display
            raw_data_table = raw_data_table.rename(columns={
                "ev_penetration": "Penetration Rate (%)",
                "electric_vehicles_sold": "EV Sales (units)",
                "state": "State",
                "vehicle_category": "Category",
                "penetration_formatted": "Penetration Display"
            })
            
            # Reorder columns for better display
            display_columns = ["State", "Category", "Penetration Display", "EV Sales (units)"]
            st.dataframe(raw_data_table[display_columns])
        
        # Define metrics in the order we want to plot
        metrics = [
            ("2-Wheelers", "ev_penetration"),
            ("4-Wheelers", "ev_penetration"),
            ("Combined", "ev_penetration"),
            ("2-Wheelers", "electric_vehicles_sold"),
            ("4-Wheelers", "electric_vehicles_sold"),
        ]

        # Define fixed benchmarks for normalization
        # These represent reasonable maximum values for each metric
        benchmarks = {
            ("2-Wheelers", "ev_penetration"): 20.0,     # 20% penetration
            ("4-Wheelers", "ev_penetration"): 20.0,     # 20% penetration
            ("Combined", "ev_penetration"): 20.0,       # 20% penetration
            ("2-Wheelers", "electric_vehicles_sold"): 100000,  # 100,000 units
            ("4-Wheelers", "electric_vehicles_sold"): 50000,   # 50,000 units
        }

        # Normalize each metric using fixed benchmarks
        normalized_data = []
        for vehicle_category, column in metrics:
            benchmark = benchmarks[(vehicle_category, column)]
            for state in states:
                # Get the value safely
                filtered_rows = category_radar[
                    (category_radar["vehicle_category"] == vehicle_category) &
                    (category_radar["state"] == state)
                ]
                val = filtered_rows[column].iloc[0] if not filtered_rows.empty else 0
                # Normalize against benchmark (capped at 1.0)
                norm_val = min(val / benchmark, 1.0)
                normalized_data.append((state, vehicle_category, column, val, norm_val))

        # Convert to DataFrame for plotting
        norm_df = pd.DataFrame(normalized_data, columns=["state", "vehicle_category", "metric", "raw_value", "normalized_value"])

        # Create two radar charts - one with fixed benchmark normalization and one with relative normalization
        if "2-Wheelers" in categories and "4-Wheelers" in categories:
            # Fixed benchmark normalization
            radar_fig = go.Figure()
            # Add padding to the radar chart layout for better spacing
            radar_fig.update_layout(
              margin=dict(l=80, r=80, t=80, b=120),  # Increase padding as needed
            )
            
            # Define colors with higher opacity
            colors = {"Delhi": "rgba(76, 120, 168, 0.8)", "Karnataka": "rgba(114, 183, 178, 0.8)"}
            
            for state in states:
                state_values = []
                for vehicle_category, column in metrics:
                    # Get the normalized value safely
                    filtered_norm_rows = norm_df[
                        (norm_df["state"] == state) &
                        (norm_df["vehicle_category"] == vehicle_category) &
                        (norm_df["metric"] == column)
                    ]
                    norm_val = filtered_norm_rows["normalized_value"].iloc[0] if not filtered_norm_rows.empty else 0
                    state_values.append(norm_val)
                
                radar_fig.add_trace(
                    go.Scatterpolar(
                        r=state_values + [state_values[0]],  # Close loop
                        theta=[
                            "2W Penetration (%)",
                            "4W Penetration (%)",
                            "Overall Penetration (%)",
                            "2W Sales",
                            "4W Sales"
                        ] + ["2W Penetration (%)"],  # Close loop
                        fill="toself",
                        name=state,
                        fillcolor=colors[state],
                        line=dict(color=colors[state].replace("0.8", "1.0"), width=2)
                    )
                )

            # Add a legend explaining the benchmarks
            benchmark_text = "<br>".join([
                f"<br><br><br><b>Benchmarks used for normalization:</b>",
                f"• 2W Penetration: {benchmarks[('2-Wheelers', 'ev_penetration')]}%",
                f"• 4W Penetration: {benchmarks[('4-Wheelers', 'ev_penetration')]}%", 
                f"• Overall Penetration: {benchmarks[('Combined', 'ev_penetration')]}%",
                f"• 2W Sales: {benchmarks[('2-Wheelers', 'electric_vehicles_sold')]:,} units",
                f"• 4W Sales: {benchmarks[('4-Wheelers', 'electric_vehicles_sold')]:,} units"
            ])

            radar_fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                        ticktext=["20%", "40%", "60%", "80%", "100%"]
                    )
                ),
                showlegend=True,
                title="Fixed Benchmark Comparison (% of Benchmark)",
                height=600,
                annotations=[
                    go.layout.Annotation(
                        x=0.5,
                        y=-0.26,
                        xref="paper",
                        yref="paper",
                        text=benchmark_text,
                        showarrow=False,
                        align="center"
                    )
                ]
            )

            st.plotly_chart(radar_fig, use_container_width=True)


        # Add a radar chart to compare different metrics across states and categories
        # category_radar = filtered_kpis.copy()

        # # Create a radar chart for more comprehensive comparison
        # categories = category_radar["vehicle_category"].unique().tolist()
        # states = category_radar["state"].unique().tolist()

        # # Only include if we have both 2-wheelers and 4-wheelers data
        # if "2-Wheelers" in categories and "4-Wheelers" in categories:
        #     radar_fig = go.Figure()

        #     for i, state in enumerate(states):
        #         state_data = category_radar[category_radar["state"] == state]

        #         radar_fig.add_trace(
        #             go.Scatterpolar(
        #                 r=[
        #                     state_data[state_data["vehicle_category"] == "2-Wheelers"][
        #                         "ev_penetration"
        #                     ].values[0],
        #                     state_data[state_data["vehicle_category"] == "4-Wheelers"][
        #                         "ev_penetration"
        #                     ].values[0],
        #                     state_data[state_data["vehicle_category"] == "Combined"][
        #                         "ev_penetration"
        #                     ].values[0],
        #                     state_data[state_data["vehicle_category"] == "2-Wheelers"][
        #                         "electric_vehicles_sold"
        #                     ].values[0]
        #                     / 1000,  # Scaled down for visualization
        #                     state_data[state_data["vehicle_category"] == "4-Wheelers"][
        #                         "electric_vehicles_sold"
        #                     ].values[0]
        #                     / 1000,  # Scaled down for visualization
        #                 ],
        #                 theta=[
        #                     "2W Penetration (%)",
        #                     "4W Penetration (%)",
        #                     "Overall Penetration (%)",
        #                     "2W Sales (thousands)",
        #                     "4W Sales (thousands)",
        #                 ],
        #                 fill="toself",
        #                 name=state,
        #             )
        #         )

        #     radar_fig.update_layout(
        #         polar=dict(
        #             radialaxis=dict(
        #                 visible=True,
        #                 range=[
        #                     0,
        #                     max(
        #                         category_radar["ev_penetration"].max() * 1.1,
        #                         category_radar["electric_vehicles_sold"].max() / 900,
        #                     ),
        #                 ],  # Adjust range for better visualization
        #             )
        #         ),
        #         showlegend=True,
        #         title="Multi-dimensional Comparison of EV Metrics",
        #         height=600,
        #     )

        #     st.plotly_chart(radar_fig, use_container_width=True)

    with tab4:
        # Tables for detailed comparison
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("EV Sales & Penetration by Vehicle Category")
            # Format the dataframe for display
            display_df = filtered_kpis.copy()
            display_df["electric_vehicles_sold"] = display_df[
                "electric_vehicles_sold"
            ].apply(lambda x: f"{int(x):,}")
            display_df["total_vehicles_sold"] = display_df["total_vehicles_sold"].apply(
                lambda x: f"{int(x):,}"
            )
            display_df["ev_penetration"] = display_df["ev_penetration"].apply(
                lambda x: f"{x:.2f}%"
            )

            st.dataframe(
                display_df[
                    [
                        "state",
                        "vehicle_category",
                        "electric_vehicles_sold",
                        "total_vehicles_sold",
                        "ev_penetration",
                    ]
                ],
                use_container_width=True,
            )

        with col2:
            st.subheader("Monthly Trends")
            # Format the dataframe for display
            monthly_display = filtered_monthly_trend.copy()
            monthly_display["electric_vehicles_sold"] = monthly_display[
                "electric_vehicles_sold"
            ].apply(lambda x: f"{int(x):,}")
            monthly_display["total_vehicles_sold"] = monthly_display[
                "total_vehicles_sold"
            ].apply(lambda x: f"{int(x):,}")
            monthly_display["ev_penetration"] = monthly_display["ev_penetration"].apply(
                lambda x: f"{x:.2f}%"
            )

            st.dataframe(
                monthly_display[
                    [
                        "state",
                        "month",
                        "electric_vehicles_sold",
                        "total_vehicles_sold",
                        "ev_penetration",
                    ]
                ],
                use_container_width=True,
            )

            # Add a summary table like the image example
            st.subheader("EV Sales Summary")
            summary = filtered_overall_kpis.copy()
            summary = summary.rename(
                columns={
                    "electric_vehicles_sold": "total_ev_sales",
                    # The ev_penetration column is already renamed to avg_ev_penetration in calculate_kpis
                }
            )
            summary["ev_sales(%)"] = (
                summary["total_ev_sales"] / summary["total_ev_sales"].sum() * 100
            ).round(2)
            summary = summary.sort_values("total_ev_sales", ascending=False)

            # State-specific penetration rates are shown in the table

            # Format the styled dataframe
            # Use a simpler approach to avoid dimension errors
            summary_styled = summary[
                ["state", "total_ev_sales", "avg_ev_penetration", "ev_sales(%)"]
            ].copy()

            # Use the new Streamlit DataFrame styling
            st.dataframe(
                summary_styled,
                column_config={
                    "state": st.column_config.TextColumn("state"),
                    "total_ev_sales": st.column_config.NumberColumn(
                        "total_ev_sales", format="%d"
                    ),
                    "avg_ev_penetration": st.column_config.NumberColumn(
                        "avg_ev_penetration", format="%.5f"
                    ),
                    "ev_sales(%)": st.column_config.NumberColumn(
                        "ev_sales(%)", format="%.2f"
                    ),
                },
                use_container_width=True,
                hide_index=False,
            )

    with tab5:
        st.subheader("Detailed Penetration Rate Analysis")

        # Create a dataframe for penetration analysis
        penetration_data = filtered_kpis.copy()

        # Create columns for different visualizations
        col1, col2 = st.columns(2)

        with col1:
            # Bar chart comparing penetration rates by state
            fig = px.bar(
                filtered_overall_kpis,
                x="state",
                y="ev_penetration",
                title="Average Penetration Rate by State",
                labels={"ev_penetration": "Average EV Penetration Rate (%)"},
                color="state",
                color_discrete_sequence=["#4C78A8", "#72B7B2"],
                text_auto=True,
            )

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Comparison table with more detailed metrics
            category_penetration = filtered_kpis[
                filtered_kpis["vehicle_category"] != "Combined"
            ].copy()

            # Pivot the data for a better comparison
            penetration_pivot = category_penetration.pivot(
                index="vehicle_category", columns="state", values="ev_penetration"
            ).reset_index()

            # Calculate the difference between states
            if (
                "Delhi" in penetration_pivot.columns
                and "Karnataka" in penetration_pivot.columns
            ):
                penetration_pivot["Difference"] = (
                    penetration_pivot["Karnataka"] - penetration_pivot["Delhi"]
                )

            st.write("Penetration Rate Comparison by Vehicle Category")
            st.dataframe(penetration_pivot, use_container_width=True)

            # Calculate state level metrics
            state_metrics = pd.DataFrame(
                {
                    "Metric": [
                        "Average EV Penetration Rate (%)",
                        "Weighted Penetration Rate (%)",
                        "Maximum Monthly Penetration Rate (%)",
                        "Minimum Monthly Penetration Rate (%)",
                        "Penetration Rate Volatility (%)",
                    ]
                }
            )

            # Calculate metrics for each state
            for state in ["Delhi", "Karnataka"]:
                # Overall average
                state_average = filtered_overall_kpis[
                    filtered_overall_kpis["state"] == state
                ]["ev_penetration"].values[0]

                # Monthly stats
                monthly_state = filtered_monthly_trend[
                    filtered_monthly_trend["state"] == state
                ]
                max_monthly = monthly_state["ev_penetration"].max()
                min_monthly = monthly_state["ev_penetration"].min()
                volatility = monthly_state["ev_penetration"].std()

                # Calculate weighted penetration (weighted by total vehicles sold)
                category_state = filtered_kpis[
                    (filtered_kpis["state"] == state)
                    & (filtered_kpis["vehicle_category"] != "Combined")
                ]
                weighted_penetration = (
                    category_state["electric_vehicles_sold"].sum()
                    / category_state["total_vehicles_sold"].sum()
                ) * 100

                state_metrics[state] = [
                    round(state_average, 5),
                    round(weighted_penetration, 5),
                    round(max_monthly, 5),
                    round(min_monthly, 5),
                    round(volatility, 5),
                ]

            st.write("Detailed Penetration Metrics")
            st.dataframe(state_metrics, use_container_width=True)

        # Show the trend of penetration rate over months
        st.subheader("Monthly Penetration Rate Trend")

        # Create a line chart for the trend
        fig = px.line(
            filtered_monthly_trend,
            x="month",
            y="ev_penetration",
            color="state",
            title="Monthly EV Penetration Rate Trend",
            labels={"ev_penetration": "Penetration Rate (%)", "month": "Month"},
            markers=True,
            line_dash_sequence=["solid"],
            line_shape="spline",
            color_discrete_sequence=["#4C78A8", "#72B7B2"],
        )

        # No reference line for combined penetration

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Add a conclusion section
    st.subheader("Summary of Findings")

    # Determine which state is performing better overall
    if (
        filtered_overall_kpis[filtered_overall_kpis["state"] == "Karnataka"][
            "ev_penetration"
        ].values[0]
        > filtered_overall_kpis[filtered_overall_kpis["state"] == "Delhi"][
            "ev_penetration"
        ].values[0]
    ):
        leading_state = "Karnataka"
        trailing_state = "Delhi"
    else:
        leading_state = "Delhi"
        trailing_state = "Karnataka"

    st.markdown(
        f"""
    ### Key Insights:
    
    1. **Overall Performance**: {leading_state} is leading in EV adoption with a higher average penetration rate compared to {trailing_state}.
    
    2. **Market Size**: Karnataka accounts for approximately {karnataka_market_share:.1f}% of the combined EV sales between the two states, 
       while Delhi accounts for {delhi_market_share:.1f}%.
    
    3. **Vehicle Category Trends**: 
       - In 2-Wheelers: {"Karnataka" if karnataka_2w > delhi_2w else "Delhi"} has higher sales volume
       - In 4-Wheelers: {"Karnataka" if karnataka_4w > delhi_4w else "Delhi"} has higher sales volume
    
    4. **EV Penetration**: {leading_state} shows a stronger average EV penetration rate at 
       {max(delhi_penetration, karnataka_penetration):.5f}% compared to {min(delhi_penetration, karnataka_penetration):.5f}% in {trailing_state}.
    """
    )


def main():
    create_dashboard()


if __name__ == "__main__":
    main()
