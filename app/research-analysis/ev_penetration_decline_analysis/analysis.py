import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from pathlib import Path

# Base directory for data
BASE_DIR = Path(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)

st.set_page_config(
    page_title="EV Penetration Decline Analysis",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main function to run the EV Penetration Decline Analysis dashboard"""

    # Set page title
    st.title("📉 EV Penetration Decline Analysis (2022-2024)")
    st.markdown(
        "This dashboard analyzes states that experienced a decline in electric vehicle (EV) penetration rates from 2022 to 2024."
    )

    # Load the data using the existing function in the ev_pen_dec.py module
    import sys
    import os

    # Add the current directory to the system path to allow imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    # Now import using a direct import
    from ev_pen_dec import load_data

    df = load_data()

    if df is None:
        st.error("Failed to load data. Please check the data files.")
        return

    # Extract year and compute yearly averages
    df["year"] = df["date"].dt.year
    yearly_avg = (
        df.groupby(["state", "year"])["ev_penetration_rate"].mean().reset_index()
    )
    pivot = yearly_avg.pivot(
        index="state", columns="year", values="ev_penetration_rate"
    ).fillna(0)

    # Check years present
    available_years = pivot.columns.tolist()

    # If all required years exist
    if all(year in available_years for year in [2022, 2023, 2024]):
        pivot["change_2022_2023"] = pivot[2023] - pivot[2022]
        pivot["change_2023_2024"] = pivot[2024] - pivot[2023]
        pivot["change_2022_2024"] = pivot[2024] - pivot[2022]

        # Add percentage changes
        pivot["pct_change_2022_2023"] = (pivot["change_2022_2023"] / pivot[2022]) * 100
        pivot["pct_change_2023_2024"] = (pivot["change_2023_2024"] / pivot[2023]) * 100
        pivot["pct_change_2022_2024"] = (pivot["change_2022_2024"] / pivot[2022]) * 100

        # Find states with declines
        decline_22_23 = pivot[pivot["change_2022_2023"] < 0].copy()
        decline_23_24 = pivot[pivot["change_2023_2024"] < 0].copy()
        decline_22_24 = pivot[pivot["change_2022_2024"] < 0].copy()

        # Create KPI section
        st.subheader("Key Performance Indicators (KPIs)")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "States with 2022-2023 Decline",
                len(decline_22_23),
                f"{len(decline_22_23)/len(pivot):.1%} of states",
            )

        with col2:
            st.metric(
                "States with 2023-2024 Decline",
                len(decline_23_24),
                f"{len(decline_23_24)/len(pivot):.1%} of states",
            )

        with col3:
            st.metric(
                "States with Overall Decline",
                len(decline_22_24),
                f"{len(decline_22_24)/len(pivot):.1%} of states",
            )

        # Add filters
        st.sidebar.title("Filters & Controls")
        analysis_options = st.sidebar.multiselect(
            "Select Analysis Views",
            options=[
                "States with 2022-2023 Decline",
                "States with 2023-2024 Decline",
                "States with Overall Decline",
                "Monthly Trends for Declining States",
                "Comparative Analysis",
            ],
            default=[
                "States with 2022-2023 Decline",
                "Monthly Trends for Declining States",
            ],
        )

        # Add state selection
        all_states = sorted(df["state"].unique().tolist())
        # Default to states with any decline
        default_states = sorted(
            list(
                set(
                    decline_22_23.index.tolist()
                    + decline_23_24.index.tolist()
                    + decline_22_24.index.tolist()
                )
            )
        )

        selected_states = st.sidebar.multiselect(
            "Select States to Analyze", options=all_states, default=default_states
        )

        # Create tabs for different analysis views
        tabs = st.tabs(
            ["Year-over-Year Analysis", "Monthly Trends", "Detailed State Analysis"]
        )

        with tabs[0]:
            st.subheader("Year-over-Year EV Penetration Analysis")

            if "States with 2022-2023 Decline" in analysis_options:
                st.markdown("#### States with Decline from 2022 to 2023")

                if decline_22_23.empty:
                    st.success(
                        "✅ No states showed a decline in EV penetration from 2022 to 2023."
                    )
                else:
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        fig = px.bar(
                            decline_22_23.sort_values("change_2022_2023").reset_index(),
                            x="state",
                            y="change_2022_2023",
                            color="change_2022_2023",
                            color_continuous_scale="Reds_r",
                            labels={
                                "change_2022_2023": "Change in Penetration",
                                "state": "State",
                            },
                            title="Change in EV Penetration Rate (2022-2023)",
                        )
                        fig.update_layout(height=400, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.dataframe(
                            decline_22_23[
                                [2022, 2023, "change_2022_2023", "pct_change_2022_2023"]
                            ]
                            .sort_values("change_2022_2023")
                            .rename(
                                columns={
                                    2022: "2022 Avg",
                                    2023: "2023 Avg",
                                    "change_2022_2023": "Change",
                                    "pct_change_2022_2023": "% Change",
                                }
                            ),
                            use_container_width=True,
                        )

            if "States with 2023-2024 Decline" in analysis_options:
                st.markdown("#### States with Decline from 2023 to 2024")

                if decline_23_24.empty:
                    st.success(
                        "✅ No states showed a decline in EV penetration from 2023 to 2024."
                    )
                else:
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        fig = px.bar(
                            decline_23_24.sort_values("change_2023_2024").reset_index(),
                            x="state",
                            y="change_2023_2024",
                            color="change_2023_2024",
                            color_continuous_scale="Reds_r",
                            labels={
                                "change_2023_2024": "Change in Penetration",
                                "state": "State",
                            },
                            title="Change in EV Penetration Rate (2023-2024)",
                        )
                        fig.update_layout(height=400, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.dataframe(
                            decline_23_24[
                                [2023, 2024, "change_2023_2024", "pct_change_2023_2024"]
                            ]
                            .sort_values("change_2023_2024")
                            .rename(
                                columns={
                                    2023: "2023 Avg",
                                    2024: "2024 Avg",
                                    "change_2023_2024": "Change",
                                    "pct_change_2023_2024": "% Change",
                                }
                            ),
                            use_container_width=True,
                        )

            if "States with Overall Decline" in analysis_options:
                st.markdown("#### States with Overall Decline from 2022 to 2024")

                if decline_22_24.empty:
                    st.success(
                        "✅ No states showed an overall decline in EV penetration from 2022 to 2024."
                    )
                else:
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        fig = px.bar(
                            decline_22_24.sort_values("change_2022_2024").reset_index(),
                            x="state",
                            y="change_2022_2024",
                            color="change_2022_2024",
                            color_continuous_scale="Reds_r",
                            labels={
                                "change_2022_2024": "Change in Penetration",
                                "state": "State",
                            },
                            title="Overall Change in EV Penetration Rate (2022-2024)",
                        )
                        fig.update_layout(height=400, xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.dataframe(
                            decline_22_24[
                                [2022, 2024, "change_2022_2024", "pct_change_2022_2024"]
                            ]
                            .sort_values("change_2022_2024")
                            .rename(
                                columns={
                                    2022: "2022 Avg",
                                    2024: "2024 Avg",
                                    "change_2022_2024": "Change",
                                    "pct_change_2022_2024": "% Change",
                                }
                            ),
                            use_container_width=True,
                        )

            # Show yearly trend for selected states
            st.markdown("#### EV Penetration Trends by Year")

            if selected_states:
                state_data = pivot.loc[
                    selected_states,
                    [year for year in [2022, 2023, 2024] if year in pivot.columns],
                ]
                melted_data = state_data.reset_index().melt(
                    id_vars="state",
                    value_vars=[
                        year for year in [2022, 2023, 2024] if year in pivot.columns
                    ],
                    var_name="Year",
                    value_name="EV Penetration Rate",
                )

                fig = px.line(
                    melted_data,
                    x="Year",
                    y="EV Penetration Rate",
                    color="state",
                    markers=True,
                    title=f"EV Penetration Rate Trends (2022-2024) for Selected States",
                    labels={
                        "Year": "Year",
                        "EV Penetration Rate": "EV Penetration Rate",
                    },
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(
                    "Please select states in the sidebar to view their yearly trends."
                )

        with tabs[1]:
            st.subheader("Monthly EV Penetration Trends")

            if "Monthly Trends for Declining States" in analysis_options:
                # Filter states for analysis
                states_to_analyze = (
                    selected_states
                    if selected_states
                    else sorted(
                        list(
                            set(
                                decline_22_23.index.tolist()
                                + decline_22_24.index.tolist()
                            )
                        )
                    )
                )

                if states_to_analyze:
                    st.markdown(
                        f"#### Monthly Trends for Selected States ({len(states_to_analyze)} states)"
                    )

                    # Filter data for selected states
                    monthly_data = df[df["state"].isin(states_to_analyze)].copy()

                    # Group by state and month, calculate mean penetration rate
                    monthly_trends = (
                        monthly_data.groupby(
                            ["state", pd.Grouper(key="date", freq="ME")]
                        )["ev_penetration_rate"]
                        .mean()
                        .reset_index()
                    )

                    # Add year-month column for easier plotting
                    monthly_trends["year_month"] = monthly_trends["date"].dt.strftime(
                        "%Y-%m"
                    )

                    # Create the line chart
                    fig = px.line(
                        monthly_trends,
                        x="date",
                        y="ev_penetration_rate",
                        color="state",
                        markers=True,
                        title="Monthly EV Penetration Rate Trends",
                        labels={
                            "date": "Date",
                            "ev_penetration_rate": "EV Penetration Rate",
                            "state": "State",
                        },
                    )

                    fig.update_layout(height=500, hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)

                    # Calculate month-over-month changes
                    pivot_monthly = monthly_trends.pivot_table(
                        index="state", columns="date", values="ev_penetration_rate"
                    )

                    monthly_changes = pivot_monthly.diff(axis=1)

                    st.markdown("#### Month-over-Month Changes in EV Penetration")

                    # Create heatmap of monthly changes
                    fig_heatmap = go.Figure(
                        data=go.Heatmap(
                            z=monthly_changes.values,
                            x=monthly_changes.columns,
                            y=monthly_changes.index,
                            colorscale="RdBu_r",
                            zmid=0,
                            colorbar=dict(title="Change Rate"),
                            hovertemplate="State: %{y}<br>Month: %{x}<br>Change: %{z:.4f}<extra></extra>",
                        )
                    )

                    fig_heatmap.update_layout(
                        title="Monthly Changes in EV Penetration Rate",
                        height=600,
                        xaxis_title="Month",
                        yaxis_title="State",
                    )

                    st.plotly_chart(fig_heatmap, use_container_width=True)
                else:
                    st.info(
                        "No states found with declining EV penetration or in your selection."
                    )

        with tabs[2]:
            st.subheader("Detailed State-wise Analysis")

            # Add state selector for detailed analysis
            if selected_states:
                state_for_detail = st.selectbox(
                    "Select a state for detailed analysis:", options=selected_states
                )

                if state_for_detail:
                    st.markdown(f"### Detailed Analysis for {state_for_detail}")

                    # Filter data for this state
                    state_data = df[df["state"] == state_for_detail].copy()

                    # Create summary metrics
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        avg_penetration = state_data["ev_penetration_rate"].mean()
                        st.metric("Avg. EV Penetration", f"{avg_penetration:.4f}")

                    # Get yearly averages if available
                    years_present = sorted(state_data["year"].unique())

                    avg_2022 = None
                    avg_2023 = None
                    avg_2024 = None

                    if 2022 in years_present:
                        with col2:
                            avg_2022 = state_data[state_data["year"] == 2022][
                                "ev_penetration_rate"
                            ].mean()
                            st.metric("2022 Avg.", f"{avg_2022:.4f}")

                    if 2023 in years_present:
                        with col3:
                            avg_2023 = state_data[state_data["year"] == 2023][
                                "ev_penetration_rate"
                            ].mean()
                            delta = None
                            if avg_2022 is not None:
                                delta = (
                                    f"{((avg_2023 - avg_2022) / avg_2022 * 100):.2f}%"
                                )
                            st.metric("2023 Avg.", f"{avg_2023:.4f}", delta)

                    if 2024 in years_present:
                        with col4:
                            avg_2024 = state_data[state_data["year"] == 2024][
                                "ev_penetration_rate"
                            ].mean()
                            delta = None
                            if avg_2023 is not None:
                                delta = (
                                    f"{((avg_2024 - avg_2023) / avg_2023 * 100):.2f}%"
                                )
                            st.metric("2024 Avg.", f"{avg_2024:.4f}", delta)

                    # Create monthly trends chart
                    monthly_data = (
                        state_data.groupby(pd.Grouper(key="date", freq="ME"))[
                            "ev_penetration_rate"
                        ]
                        .mean()
                        .reset_index()
                    )
                    monthly_data["month"] = monthly_data["date"].dt.strftime("%b %Y")
                    monthly_data["mom_change"] = monthly_data[
                        "ev_penetration_rate"
                    ].diff()

                    # Create a subplot with penetration rate and MoM changes
                    fig = make_subplots(
                        rows=2,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=(
                            "Monthly EV Penetration Rate",
                            "Month-over-Month Change",
                        ),
                    )

                    # Add traces
                    fig.add_trace(
                        go.Scatter(
                            x=monthly_data["date"],
                            y=monthly_data["ev_penetration_rate"],
                            mode="lines+markers",
                            name="EV Penetration Rate",
                            line=dict(color="royalblue", width=2),
                            marker=dict(size=8),
                        ),
                        row=1,
                        col=1,
                    )

                    # Add MoM change
                    fig.add_trace(
                        go.Bar(
                            x=monthly_data["date"],
                            y=monthly_data["mom_change"],
                            name="MoM Change",
                            marker_color=monthly_data["mom_change"].apply(
                                lambda x: "green" if x >= 0 else "red"
                            ),
                        ),
                        row=2,
                        col=1,
                    )

                    # Add a reference line at y=0 for MoM change
                    fig.add_shape(
                        type="line",
                        x0=monthly_data["date"].min(),
                        x1=monthly_data["date"].max(),
                        y0=0,
                        y1=0,
                        line=dict(color="black", width=1, dash="dash"),
                        row=2,
                        col=1,
                    )

                    fig.update_layout(
                        height=600,
                        showlegend=False,
                        title=f"Monthly EV Penetration Trends for {state_for_detail}",
                        hovermode="x unified",
                    )

                    fig.update_xaxes(title="Date", row=2, col=1)
                    fig.update_yaxes(title="EV Penetration Rate", row=1, col=1)
                    fig.update_yaxes(title="MoM Change", row=2, col=1)

                    st.plotly_chart(fig, use_container_width=True)

                    # Show position compared to other states
                    st.markdown("#### Comparison with Other States")

                    # Get this state's ranking
                    state_avg = pivot.mean(axis=1).sort_values(ascending=False)
                    state_rank = state_avg.index.get_indexer([state_for_detail])[0] + 1
                    total_states = len(state_avg)

                    st.markdown(
                        f"Rank by Average EV Penetration Rate: **{state_rank}** out of **{total_states}** states"
                    )

                    # Create a percentile bar
                    percentile = (1 - (state_rank / total_states)) * 100

                    # Display the percentile bar
                    st.progress(float(percentile) / 100)
                    st.markdown(f"Better than **{percentile:.1f}%** of all states")
            else:
                st.info(
                    "Please select states in the sidebar to view detailed analysis."
                )

        # Final section with key findings
        st.markdown("---")
        st.subheader("Key Findings and Insights")

        # Based on actual data analysis
        if decline_22_24.empty:
            st.success(
                "✅ No states showed an overall decline in EV penetration from 2022 to 2024, "
                + "indicating positive growth across India."
            )
        else:
            st.warning(
                f"⚠️ {len(decline_22_24)} states showed an overall decline in EV penetration from 2022 to 2024: "
                + f"{', '.join(decline_22_24.index.tolist())}"
            )

        if not decline_22_23.empty:
            st.info(
                f"🔍 {len(decline_22_23)} states showed a temporary decline between 2022-2023: "
                + f"{', '.join(decline_22_23.index.tolist())}, but most recovered by 2024."
            )

            # Get state with highest decline in 2022-2023
            worst_state_22_23 = decline_22_23.sort_values("change_2022_2023").iloc[0]

            st.markdown(
                f"- **{worst_state_22_23.name}** had the largest decline from 2022 to 2023 with a change "
                + f"of {worst_state_22_23['change_2022_2023']:.4f} in penetration rate ({worst_state_22_23['pct_change_2022_2023']:.2f}%)."
            )

            # List key factors if available
            st.markdown(
                """
            **Factors that might have contributed to the decline:**
            
            - Policy changes or subsidy modifications in these states
            - Supply chain disruptions affecting EV availability
            - Economic factors influencing purchasing decisions
            - Infrastructure challenges (charging stations, service centers)
            """
            )

        if "Comparative Analysis" in analysis_options and selected_states:
            st.markdown("#### Year-over-Year Comparison")

            # Create a comparison table for selected states
            comparison_df = pivot.loc[selected_states, :].copy()

            display_cols = [
                col for col in [2022, 2023, 2024] if col in comparison_df.columns
            ]
            change_cols = [
                col
                for col in ["change_2022_2023", "change_2023_2024", "change_2022_2024"]
                if col in comparison_df.columns
            ]

            st.dataframe(
                comparison_df[display_cols + change_cols].sort_values(
                    by=str(display_cols[-1]), ascending=False
                ),
                use_container_width=True,
            )
    else:
        st.warning(
            f"Required years (2022, 2023, 2024) not found in data. Available years: {available_years}"
        )


if __name__ == "__main__":
    main()
