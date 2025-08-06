import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import fiona

# Get the root path of the data directory
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
data_dir = os.path.join(current_dir, "../../../data/processed")


from typing import Optional

def get_gpkg_layers(file_path: str) -> list:
    """Get available layers in a GeoPackage file."""
    try:
        return fiona.listlayers(file_path)
    except Exception as e:
        print(f"Error reading layers: {e}")
        return []

def plot_ev_penetration_map(
    top_states_df: pd.DataFrame,
    geo_file_path: str,
    geo_layer: str,
    geo_state_col: str = "NAME_1",
    df_state_col: str = "state",
    penetration_col: str = "penetration_rate",
    replace_state_names: Optional[dict] = None,
    title: str = "Top States by EV Penetration Rate",
    cmap: str = "viridis",
    figsize=(15, 10),
    annotate: bool = True,
):
    """
    Plots a choropleth map of top Indian states by EV penetration rate.
    """
    if replace_state_names:
        top_states_df[df_state_col] = top_states_df[df_state_col].replace(replace_state_names)

    top_state_dict = dict(zip(top_states_df[df_state_col], top_states_df[penetration_col]))
    india_states = gpd.read_file(geo_file_path, layer=geo_layer)
    
    # Debug information
    st.write("Available columns in the GeoDataFrame:", india_states.columns.tolist())
    
    # Try to find the state name column
    possible_state_cols = [col for col in india_states.columns if 'NAME' in col or 'name' in col or 'State' in col]
    if possible_state_cols:
        geo_state_col = possible_state_cols[0]
        st.write(f"Using column '{geo_state_col}' for state names")
    else:
        st.error("Could not find a suitable column for state names")
        st.write("Available columns:", india_states.columns.tolist())
        return None
        
    india_states["penetration_rate"] = india_states[geo_state_col].map(top_state_dict)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    india_states.plot(ax=ax, color="lightgray", edgecolor="white")
    
    top_states = india_states[india_states["penetration_rate"].notna()]
    top_states.plot(
        column="penetration_rate",
        ax=ax,
        cmap=cmap,
        legend=True,
        legend_kwds={"label": "EV Penetration Rate (%)"},
    )

    ax.set_title(title, pad=20)
    ax.axis("off")

    if annotate:
        for _, row in top_states.iterrows():
            centroid = row.geometry.centroid
            ax.annotate(
                f"{row[geo_state_col]}\n{row['penetration_rate']:.1f}%",
                xy=(centroid.x, centroid.y),
                xytext=(3, 3),
                textcoords="offset points",
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="gray", alpha=0.7),
                fontsize=8,
            )

    return fig


def main():
    # BEFORE rendering the chart
    st.markdown(
        """
        <style>
        .styled-chart {
            border: 2px solid #ccc;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            background-color: #ffffff;
            margin-bottom: 20px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.set_page_config(layout="wide", page_title="EV Penetration Dashboard")
    st.title("🔌 Electric Vehicle Penetration Dashboard - India (FY 2024)")
    st.markdown(
        "Analyze EV penetration rates by **2-Wheelers** and **4-Wheelers** across top Indian states."
    )

    df: pd.DataFrame | None = None
    error_message = None

    try:
        df = pd.read_csv(os.path.join(data_dir, "ev_sales_enhanced.csv"))
        df["date"] = pd.to_datetime(df["date"])
        df["fiscal_year"] = df["date"].dt.year.where(
            df["date"].dt.month < 4, df["date"].dt.year + 1
        )
    except Exception as e:
        error_message = f"❌ Error loading or processing data: {e}"

    if error_message:
        st.error(error_message)
        return

    fy_2024_df = df[df["fiscal_year"] == 2024]  # type: ignore

    def calculate_top_states(dataframe, category):
        category_df = dataframe[dataframe["vehicle_category"] == category]
        stats = (
            category_df.groupby("state")
            .agg({"electric_vehicles_sold": "sum", "total_vehicles_sold": "sum"})
            .reset_index()
        )
        stats["penetration_rate"] = (
            stats["electric_vehicles_sold"] / stats["total_vehicles_sold"] * 100
        )
        return stats.nlargest(5, "penetration_rate")

    top_5_2w = calculate_top_states(fy_2024_df, "2-Wheelers")
    top_5_4w = calculate_top_states(fy_2024_df, "4-Wheelers")

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[
            "🏍️ Top 5 States - 2-Wheeler EV Penetration",
            "🚗 Top 5 States - 4-Wheeler EV Penetration",
        ],
    )


    fig.add_trace(
        go.Bar(
            x=top_5_2w["state"],
            y=top_5_2w["penetration_rate"],
            text=top_5_2w["penetration_rate"].round(2).astype(str) + "%",
            textposition="auto",
            marker_color="rgb(58, 71, 80)",
            hovertemplate="<b>%{x}</b><br>Penetration: %{y:.2f}%<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=top_5_4w["state"],
            y=top_5_4w["penetration_rate"],
            text=top_5_4w["penetration_rate"].round(2).astype(str) + "%",
            textposition="auto",
            marker_color="rgb(26, 118, 255)",
            hovertemplate="<b>%{x}</b><br>Penetration: %{y:.2f}%<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        height=500,
        title="📊 EV Penetration Rate by Vehicle Type in Top States (FY 2024)",
        title_font_size=20,
        showlegend=False,
        margin=dict(t=80),
        yaxis=dict(title="Penetration Rate (%)", gridcolor="lightgray"),
        yaxis2=dict(title="Penetration Rate (%)", gridcolor="lightgray"),
    )

    # Wrap with styled div AFTER figure is fully defined
    # st.markdown('<div class="styled-chart">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    # st.markdown("</div>", unsafe_allow_html=True)

    # Add state maps for both 2W and 4W EV penetration
    st.markdown("## 🗺️ Geographic Distribution of EV Penetration")
    
    # Check available layers in the GeoPackage
    gpkg_path = os.path.join(current_dir, "../../../data/external/gadm41_IND.gpkg")
    available_layers = get_gpkg_layers(gpkg_path)
    st.write("Available layers in GeoPackage:", available_layers)
    
    # Use ADM_ADM_1 layer for state-level data
    if "ADM_ADM_1" not in available_layers:
        st.error("Required layer 'ADM_ADM_1' not found in the GeoPackage file!")
        return
        
    geo_layer = "ADM_ADM_1"  # Use state-level layer
    
    # 2-Wheeler Map
    top_5_2w_map = dict(zip(top_5_2w["state"].replace({"Delhi": "NCT of Delhi"}), top_5_2w["penetration_rate"]))
    top_5_2w_df_map = pd.DataFrame(list(top_5_2w_map.items()), columns=["state", "penetration_rate"])
    
    fig_2w = plot_ev_penetration_map(
        top_states_df=top_5_2w_df_map,
        geo_file_path=gpkg_path,
        geo_layer=geo_layer,
        title="🏍️ Top 5 States by 2-Wheeler EV Penetration Rate (FY 2024)",
        cmap="viridis"
    )
    st.pyplot(fig_2w)

    # 4-Wheeler Map
    top_5_4w_map = dict(zip(top_5_4w["state"].replace({"Delhi": "NCT of Delhi"}), top_5_4w["penetration_rate"]))
    top_5_4w_df_map = pd.DataFrame(list(top_5_4w_map.items()), columns=["state", "penetration_rate"])
    
    fig_4w = plot_ev_penetration_map(
        top_states_df=top_5_4w_df_map,
        geo_file_path=gpkg_path,
        geo_layer=geo_layer,
        title="🚗 Top 5 States by 4-Wheeler EV Penetration Rate (FY 2024)",
        cmap="viridis"
    )
    st.pyplot(fig_4w)

    with st.expander("🔍 View Raw Data for Top 5 States"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🏍️ 2-Wheelers")
            st.dataframe(top_5_2w.style.format({"penetration_rate": "{:.2f}"}))
        with col2:
            st.markdown("#### 🚗 4-Wheelers")
            st.dataframe(top_5_4w.style.format({"penetration_rate": "{:.2f}"}))

    # 📘 Data Storytelling Section
    st.markdown("---")
    st.markdown("## 📘 EV Adoption Story: Top 5 States in FY 2024")
    st.markdown(
        """
In **FY 2024**, several Indian states made notable progress in the adoption of electric vehicles (EVs), especially in the **2-wheeler and 4-wheeler segments**. Let’s break it down:

### 🛵 2-Wheelers: Goa Leads the Charge

- **Goa** leads with a **penetration rate of ~18%**—almost 1 in every 5 two-wheelers sold was electric.
- **Kerala** follows with **13.5%**.
- **Karnataka**, **Maharashtra**, and **Delhi** complete the top 5 with impressive uptake.

**👉 Why it matters:** Goa’s compact size and tourism economy likely helped it adopt EVs faster, with easier charging and mobility needs.

---

### 🚗 4-Wheelers: Kerala Stands Tall

- **Kerala** tops the list with **5.76%** penetration.
- **Chandigarh**, **Delhi**, **Karnataka**, and **Goa** also make the list—highlighting strong policy and awareness.

**👉 Why it matters:** 4-wheelers typically have slower adoption, but these regions show that awareness, affordability, and incentives work.

---

### 🌱 Final Thought

Smaller and progressive regions like **Goa, Kerala, and Chandigarh** are leading India's EV transformation. This isn’t just a trend—it’s the beginning of a nationwide movement toward clean mobility.
"""
    )

    # 🧩 Key Insights Table
    st.markdown("## 🧩 Key Insights Summary")
    st.markdown(
        """
| #   | Insight                                                                         |
| --- | ------------------------------------------------------------------------------- |
| 🔝  | **Goa** leads in 2-wheeler EV penetration with ~18%.                           |
| ✅  | **Kerala** is the **only state** in top 5 for **both** 2W and 4W.               |
| 🏙️ | **Delhi and Karnataka** perform well across both categories.                    |
| 🧭  | **Smaller or UT regions** like **Goa and Chandigarh** show higher EV uptake.    |
| 🚗  | **4-wheeler EV penetration is lower** overall but steadily rising.             |
| 📈  | The trend shows that **policy + awareness = adoption**.                         |
""",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
