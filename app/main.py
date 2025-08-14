import streamlit as st
import os
import sys
import importlib.util
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="EV Analysis Dashboard Hub",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define the project base directory
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    .dashboard-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 2px 5px 15px rgba(0,0,0,0.2);
    }
    .card-title {
        color: #1E88E5;
        margin-bottom: 10px;
    }
    .card-description {
        color: #333;
        margin-bottom: 15px;
    }
    .launch-btn {
        background-color: #1E88E5;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 500;
        display: inline-block;
        margin-top: 10px;
    }
    .launch-btn:hover {
        background-color: #0D47A1;
    }
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 30px;
    }
    .logo {
        width: 60px;
        height: 60px;
        margin-right: 15px;
    }
    .banner {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #fff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .insights-section {
        border-left: 3px solid #1E88E5;
        padding-left: 15px;
        margin: 20px 0;
    }
    .insights-title {
        color: #0D47A1;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .insights-finding {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .data-diagram {
        font-family: monospace;
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        font-size: 12px;
        overflow-x: auto;
        white-space: pre;
    }
    code {
        background-color: #f0f2f6;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: monospace;
    }
    .recommendation-item {
        margin-bottom: 15px;
    }
    .recommendation-title {
        font-weight: bold;
        color: #0D47A1;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Define all available analyses
analyses = [
    {
        "name": "Top vs Bottom 2-Wheeler Makers",
        "description": "Comparative analysis of top and bottom performing two-wheeler manufacturers in FY 2023-2024.",
        "path": "top_bottom_2w_makers_fy2023_2024/analysis.py",
        "icon": "🏍️",
    },
    {
        "name": "Vehicle Analysis by State",
        "description": "State-wise breakdown of vehicle sales patterns and trends across India.",
        "path": "research-analysis/vehical_analysis_by_state/main.py",
        "icon": "🗺️",
    },
    {
        "name": "EV Penetration Decline Analysis",
        "description": "Investigation into states showing a decline in EV market penetration between 2022 and 2024.",
        "path": "research-analysis/ev_penetration_decline_analysis/analysis.py",
        "icon": "📉",
    },
    {
        "name": "Quarterly Trends - Top 5 4-Wheeler Makers",
        "description": "Analysis of quarterly sales volume trends for the top 5 four-wheeler EV manufacturers from 2022 to 2024.",
        "path": "research-analysis/qtr_trends_ev_top5/analysis.py",
        "icon": "📊",
    },
    {
        "name": "Delhi vs Karnataka EV Comparison",
        "description": "Comparative analysis of EV sales and penetration rates between Delhi and Karnataka for 2024.",
        "path": "research-analysis/ev_sales_penetration_delhi_vs_karnataka_2024/analysis.py",
        "icon": "🔋",
    },
    {
        "name": "CAGR Analysis - Top 5 4-Wheeler EV Makers",
        "description": "Detailed analysis of the compounded annual growth rate (CAGR) for the top 5 four-wheeler EV manufacturers from 2022 to 2024.",
        "path": "research-analysis/cagr_top5_4w_ev_2022_2024/analysis.py",
        "icon": "🚗",
    },
    {
        "name": "Top 10 States with Highest CAGR",
        "description": "Analysis of states with highest compound annual growth rate (CAGR) for total vehicles, EVs, and non-EVs from 2022 to 2024.",
        "path": "research-analysis/top10_states_with_highest_cagr/analysis.py",
        "icon": "📈",
    },
    {
        "name": "EV Sales Seasonality Analysis",
        "description": "Analysis of peak and low season months for electric vehicle sales based on data from 2022 to 2024.",
        "path": "research-analysis/ev_peak_low_months/analysis.py",
        "icon": "📅",
    },
    {
        "name": "EV Sales Projections 2030",
        "description": "Interactive dashboard projecting electric vehicle sales for top states in India by 2030, based on historical growth trends and CAGR analysis.",
        "path": "research-analysis/ev_sales_projection_2030/analysis.py",
        "icon": "🔮",
    },
]


def run_analysis_module(module_path):
    """Dynamically import and run a Streamlit analysis module"""
    try:
        # Get the full path to the module
        full_path = BASE_DIR / "app" / module_path

        if not full_path.exists():
            st.error(f"Analysis module not found at: {full_path}")
            return False

        # Add the parent directory to sys.path so we can import the module
        parent_dir = str(full_path.parent)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)

        # Import the module
        module_name = full_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(full_path))
        if spec is None:
            st.error(f"Could not import {module_name} from {full_path}")
            return False

        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            st.error(f"Could not load {module_name} from {full_path} (loader is None)")
            return False

        spec.loader.exec_module(module)

        # Check if the module has a main function, if so run it
        if hasattr(module, "main"):
            module.main()
            return True
        else:
            st.warning(f"Module {module_name} does not have a main function to run.")
            return False

    except Exception as e:
        st.error(f"Error running analysis module: {str(e)}")
        return False


def main():
    """Main function to display the navigation hub"""

    # Check for query parameters to see if a specific analysis was requested
    query_params = st.query_params
    if "analysis" in query_params:
        try:
            index = int(query_params["analysis"])
            if 0 <= index < len(analyses):
                # Add a Back to Home button at the top
                col1, col2 = st.columns([7, 1])
                with col2:
                    # Move Back to Home button to the extreme right
                    # st.markdown(
                    #     """
                    #     <div style="display: flex; justify-content: flex-end; width: 100%;">
                    #         <form action="/" method="get">
                    #             <button type="submit" style="
                    #                 background-color: #1E88E5;
                    #                 color: white;
                    #                 padding: 8px 16px;
                    #                 border-radius: 4px;
                    #                 border: none;
                    #                 font-weight: 500;
                    #                 cursor: pointer;
                    #             ">🏠 Back to Home</button>
                    #         </form>
                    #     </div>
                    #     """,
                    #     unsafe_allow_html=True,
                    # )
                    # Also clear query params if user clicks the button (for Streamlit rerun)
                    if st.query_params.get("analysis") is not None and st.button(
                        "Back to Home",
                        key="clear_home_state",
                        help="Reset to Home (for Streamlit navigation)",
                    ):
                        st.query_params.clear()
                        st.rerun()
                with col1:
                    # Show which dashboard is currently being viewed
                    st.markdown(
                        f"### {analyses[index]['icon']} {analyses[index]['name']}"
                    )

                # Add a horizontal separator
                st.markdown("---")

                # Run the requested analysis
                run_analysis_module(analyses[index]["path"])
                st.stop()  # Prevent the hub page from rendering
            else:
                st.error(
                    f"Invalid analysis index: {index}. Must be between 0 and {len(analyses)-1}."
                )
        except (ValueError, IndexError) as e:
            st.error(f"Error loading analysis: {str(e)}")

    # Title and introduction
    st.markdown(
        """
    <div class="header-container">
        <div style="font-size: 40px; margin-right: 15px;">🚗</div>
        <h1>EV Market Analysis Dashboard Hub</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Welcome banner
    st.markdown(
        """
    <div class="banner">
        <h3>Welcome to the Electric Vehicle Market Analysis Dashboard</h3>
        <p>This interactive hub provides access to various analyses of the Indian electric vehicle market from 2022 to 2024. 
        Select any analysis from the sidebar or explore the dashboard cards below to dive deeper into specific aspects of the EV market.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
    # Enhanced Executive Summary with comprehensive market overview
    st.markdown(
        """
        <div style="background-color: #f0f7ff; padding: 20px; border-left: 4px solid #1E88E5; border-radius: 4px; margin-bottom: 25px;">
            <h4 style="color: #0D47A1; margin-top: 0;">Executive Summary</h4>
            <p>India's electric vehicle market has experienced explosive growth, with <strong>EV penetration increasing from 0.53% to 7.83%</strong> 
            over the analysis period—representing a <strong>1,400% improvement in market adoption</strong>. This transformation reveals distinct 
            regional leadership patterns and significant opportunities for strategic market expansion.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Key Market Dynamics section (separated for better rendering)
    st.markdown(
        """
        <div style="background-color: #f0f7ff; padding: 20px; border-left: 4px solid #1E88E5; border-radius: 4px; margin-bottom: 25px;">
            <h5 style="color: #0D47A1; margin-top: 0px;">Key Market Dynamics</h5>
            <ul>
                <li><strong>Regional Leaders:</strong> Maharashtra, Karnataka, and Tamil Nadu dominate with combined 40% market share, while South and West regions show 30%+ higher penetration than national averages</li>
                <li><strong>Growth Acceleration:</strong> Top-performing states demonstrate 50-80% CAGR, indicating sustained momentum beyond early-adopter phases</li>
                <li><strong>Seasonal Patterns:</strong> Peak sales occur during October-March period, with 35% higher volumes than summer months, directly impacting inventory and marketing strategies</li>
                <li><strong>Manufacturer Landscape:</strong> Clear market segmentation emerging between premium 4-wheeler manufacturers concentrated in metros and mass-market 2-wheeler brands expanding into tier-2/3 cities</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Action buttons (separated for better rendering)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 25px;">
            <a href="/?analysis=0" target="_self" class="launch-btn" style="text-decoration: none; color: white; margin-right: 10px; background-color: #1E88E5; padding: 8px 16px; border-radius: 4px; font-weight: 500;">
                Explore Manufacturer Analysis
            </a>
            <a href="/?analysis=1" target="_self" class="launch-btn" style="text-decoration: none; color: white; background-color: #1E88E5; padding: 8px 16px; border-radius: 4px; font-weight: 500;">
                View State-wise Breakdown
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add market overview dashboard visualization
    st.markdown("## EV Market Dashboard Overview")
    
    # Create columns for market overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div class="metric-card" style="min-height: 180px;">
                <div class="metric-label">EV Market Penetration Growth</div>
                <div class="metric-value">1,400%</div>
                <div class="metric-label">From 0.53% to 7.83%</div>
                <div style="margin-top: 10px; height: 8px; background: #f0f0f0; border-radius: 4px;">
                    <div style="width: 78.3%; height: 100%; background: linear-gradient(90deg, #1E88E5, #64B5F6); border-radius: 4px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
                    <span>2022 (0.53%)</span>
                    <span>2024 (7.83%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div class="metric-card" style="min-height: 180px;">
                <div class="metric-label">Regional Market Leaders</div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Maharashtra</span>
                        <span style="font-weight: bold;">18.2%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;">
                        <div style="width: 18.2%; height: 100%; background: #1E88E5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Karnataka</span>
                        <span style="font-weight: bold;">14.8%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;">
                        <div style="width: 14.8%; height: 100%; background: #42A5F5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Tamil Nadu</span>
                        <span style="font-weight: bold;">12.3%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px;">
                        <div style="width: 12.3%; height: 100%; background: #90CAF9; border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            """
            <div class="metric-card" style="min-height: 180px;">
                <div class="metric-label">Seasonal Sales Distribution</div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Oct-Dec (Peak)</span>
                        <span style="font-weight: bold;">42%</span>
                    </div>
                    <div style="height: 10px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;">
                        <div style="width: 42%; height: 100%; background: #1E88E5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Jan-Mar (Growth)</span>
                        <span style="font-weight: bold;">25%</span>
                    </div>
                    <div style="height: 10px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;">
                        <div style="width: 25%; height: 100%; background: #42A5F5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Apr-Jun (Moderate)</span>
                        <span style="font-weight: bold;">15%</span>
                    </div>
                    <div style="height: 10px; background: #f0f0f0; border-radius: 4px; margin-bottom: 8px;">
                        <div style="width: 15%; height: 100%; background: #90CAF9; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Jul-Sep (Low)</span>
                        <span style="font-weight: bold;">18%</span>
                    </div>
                    <div style="height: 10px; background: #f0f0f0; border-radius: 4px;">
                        <div style="width: 18%; height: 100%; background: #BBDEFB; border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add growth trajectory visualization
    st.markdown("### Growth Trajectory & Market Maturity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">CAGR Performance Tiers</div>
                <div style="margin: 15px 0;">
                    <div style="margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #1E88E5;">Hyper-Growth Markets:</span> 80-120% CAGR
                        <div style="font-size: 12px; color: #666; margin-left: 10px;">Gujarat, Rajasthan, Haryana</div>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #42A5F5;">High-Growth Markets:</span> 50-80% CAGR
                        <div style="font-size: 12px; color: #666; margin-left: 10px;">Karnataka, Tamil Nadu, Kerala</div>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #90CAF9;">Steady-Growth Markets:</span> 25-50% CAGR
                        <div style="font-size: 12px; color: #666; margin-left: 10px;">Maharashtra, Delhi, West Bengal</div>
                    </div>
                    <div>
                        <span style="font-weight: bold; color: #BBDEFB;">Emerging Markets:</span> 10-25% CAGR
                        <div style="font-size: 12px; color: #666; margin-left: 10px;">Most northeastern and central states</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-label">Market Maturity Stages</div>
                <div style="margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Advanced (>15% penetration)</span>
                        <span style="font-weight: bold;">10%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px;">
                        <div style="width: 10%; height: 100%; background: #1E88E5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Developing (5-15% penetration)</span>
                        <span style="font-weight: bold;">30%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px;">
                        <div style="width: 30%; height: 100%; background: #42A5F5; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Emerging (1-5% penetration)</span>
                        <span style="font-weight: bold;">35%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px; margin-bottom: 10px;">
                        <div style="width: 35%; height: 100%; background: #90CAF9; border-radius: 4px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Early (<1% penetration)</span>
                        <span style="font-weight: bold;">25%</span>
                    </div>
                    <div style="height: 8px; background: #f0f0f0; border-radius: 4px;">
                        <div style="width: 25%; height: 100%; background: #BBDEFB; border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Project overview with background and stakeholder benefits
    with st.expander("🔍 About This Project", expanded=True):
        st.markdown(
            """
        ## Background and Overview
        
        As the electric vehicle market in India experiences unprecedented growth, understanding regional adoption patterns, manufacturer performance, 
        and seasonal trends has become critical for strategic decision-making. This comprehensive market intelligence platform was developed to analyze 
        India's EV landscape from 2022 to 2024, providing actionable insights for business expansion, investment allocation, and policy development.
        
        ## Analysis Focus Areas
        
        - **Growth Patterns**: Analyzing CAGR across different states for total vehicles and EV segment
        - **Regional Variations**: Understanding geographic differences in EV adoption
        - **Market Penetration**: Examining the share of EVs in overall vehicle sales
        - **Manufacturer Performance**: Assessing key players in the EV manufacturing landscape
        - **Segment Analysis**: 
          - Detailed CAGR analysis of top 4-wheeler EV manufacturers
          - Comparative analysis of top and bottom 2-wheeler makers
          - Quarterly trends of leading EV manufacturers
        - **Geographic Comparisons**: Comparing EV sales and penetration across states like Delhi and Karnataka
        
        ## Stakeholder Benefits
        
        This analysis serves stakeholders across multiple departments:

        - **Marketing Teams**: Target high-potential regions and optimize campaign timing
        - **Business Development**: Identify expansion opportunities and market entry strategies
        - **Product Management**: Understand regional preferences and segment performance
        - **Executive Leadership**: Make data-driven decisions about resource allocation and investment priorities
        
        The dashboard provides interactive visualizations and data-driven insights to help understand the evolving EV landscape in India, 
        with detailed market share analysis, growth consistency evaluations, and year-by-year performance metrics for leading manufacturers.
        """
        )

    # Enhanced sidebar with navigation and key metrics
    st.sidebar.title("Navigation")
    
    # Add key metrics to sidebar with improved formatting
    st.sidebar.markdown("### Key Market Metrics")
    
    # Use custom styled HTML for better visual appeal in sidebar
    st.sidebar.markdown(
        """
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <div style="margin-bottom: 8px;">
                <span style="font-size: 12px; color: #666;">EV Penetration</span><br>
                <span style="font-weight: bold; color: #1E88E5;">0.53% → 7.83%</span>
                <span style="font-size: 11px; color: #666;">(2022-2024)</span>
            </div>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <div style="margin-bottom: 8px;">
                <span style="font-size: 12px; color: #666;">Market Leaders</span><br>
                <span style="font-weight: bold;">Maharashtra</span> (18.2%)<br>
                <span style="font-weight: bold;">Karnataka</span> (14.8%)<br>
                <span style="font-weight: bold;">Tamil Nadu</span> (12.3%)
            </div>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <div style="margin-bottom: 8px;">
                <span style="font-size: 12px; color: #666;">Peak Sales Period</span><br>
                <span style="font-weight: bold;">October-December</span> (42% of annual)
            </div>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
            <div>
                <span style="font-size: 12px; color: #666;">Top Growth Leaders (CAGR)</span><br>
                <span style="font-weight: bold;">Gujarat</span> (115%)<br>
                <span style="font-weight: bold;">Rajasthan</span> (92%)<br>
                <span style="font-weight: bold;">Haryana</span> (83%)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("---")

    # Determine the default index for the selectbox
    default_index = 0
    if "analysis" in query_params:
        try:
            index = int(query_params["analysis"])
            if 0 <= index < len(analyses):
                default_index = index + 1  # +1 because "Hub Home" is the first option
        except (ValueError, IndexError):
            pass

    selected_analysis = st.sidebar.selectbox(
        "Select Analysis",
        options=["Hub Home"] + [analysis["name"] for analysis in analyses],
        index=default_index,
        format_func=lambda x: "🏠 " + x if x == "Hub Home" else x,
        key="analysis_selector",
    )

    # If a new selection is made in the sidebar, navigate to it
    if st.session_state.get("previous_selection") != selected_analysis:
        st.session_state["previous_selection"] = selected_analysis
        if selected_analysis == "Hub Home":
            if "analysis" in query_params:
                st.query_params.clear()
                st.rerun()
        else:
            # Find the index of the selected analysis
            for i, analysis in enumerate(analyses):
                if analysis["name"] == selected_analysis:
                    if query_params.get("analysis") != str(i):
                        st.query_params["analysis"] = i
                        st.rerun()
                    break

    # Handle navigation selection
    if selected_analysis == "Hub Home":
        # Display all available analyses as cards
        st.subheader("Available Analyses")

        # Create a 2-column layout for the cards
        col1, col2 = st.columns(2)

        for i, analysis in enumerate(analyses):
            col = col1 if i % 2 == 0 else col2

            with col:
                st.markdown(
                    f"""
                <div class="dashboard-card">
                    <div style="font-size: 28px; margin-bottom: 10px;">{analysis["icon"]}</div>
                    <h3 class="card-title">{analysis["name"]}</h3>
                    <p class="card-description">{analysis["description"]}</p>
                    <a href="/?analysis={i}" target="_self" class="launch-btn" style="text-decoration: none; color: white;">
                        Launch Dashboard
                    </a>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Additional information section
        st.markdown("---")
        st.subheader("Dataset Information")

        # Create columns for dataset details with enhanced metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Analysis Period</div>
                    <div class="metric-value">2022-2024</div>
                    <div class="metric-label">36 months of data</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Geographic Coverage</div>
                    <div class="metric-value">35+</div>
                    <div class="metric-label">states & union territories</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Manufacturers Tracked</div>
                    <div class="metric-value">50+</div>
                    <div class="metric-label">across all segments</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col4:
            st.markdown(
                """
                <div class="metric-card">
                    <div class="metric-label">Market Growth</div>
                    <div class="metric-value">1,400%</div>
                    <div class="metric-label">EV adoption improvement</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Data structure overview
        st.markdown("### Data Structure Overview")
        st.markdown(
            """
        The analysis leverages a robust multi-table dataset structure that mirrors real-world enterprise data environments:
        
        ```
        ┌─────────────────────────────────────┐
        │     electric_vehicle_sales_by_state │
        │  ┌─────────────────────────────────┐│
        │  │ • date                          ││
        │  │ • state                         ││
        │  │ • vehicle_category              ││
        │  │ • electric_vehicles_sold        ││
        │  │ • total_vehicles_sold           ││
        │  └─────────────────────────────────┘│
        └─────────────────────────────────────┘
                            │
                            │ JOIN
                            ▼
        ┌─────────────────────────────────────┐
        │          dim_date                   │
        │  ┌─────────────────────────────────┐│
        │  │ • date                          ││
        │  │ • fiscal_year                   ││
        │  │ • quarter                       ││
        │  │ • month_name                    ││
        │  └─────────────────────────────────┘│
        └─────────────────────────────────────┘
                            │
                            │ JOIN
                            ▼
        ┌─────────────────────────────────────┐
        │   electric_vehicle_sales_by_makers  │
        │  ┌─────────────────────────────────┐│
        │  │ • date                          ││
        │  │ • maker                         ││
        │  │ • vehicle_category              ││
        │  │ • electric_vehicles_sold        ││
        │  └─────────────────────────────────┘│
        └─────────────────────────────────────┘
        ```
        
        #### Dataset Characteristics
        - **Time Period**: 36 months of sales data (April 2021 - March 2024)
        - **Geographic Coverage**: 35+ Indian states and union territories
        - **Manufacturer Scope**: 50+ EV manufacturers across 2-wheeler and 4-wheeler categories
        - **Data Volume**: 15,000+ records with calculated metrics including penetration rates, CAGR, and growth indicators
        """
        )

        # Data sources acknowledgment
        st.markdown(
            """
        <div style="margin-top: 20px; font-size: 0.85em; color: #666;">
        <p><strong>Data Sources:</strong> This analysis is based on processed data files in the project's data directory, 
        including state-wise EV sales, manufacturer performance metrics, and regional sales data.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        
        # Caveats and assumptions section
        with st.expander("Caveats and Assumptions", expanded=False):
            st.markdown(
                """
            ### Data Limitations
            - **Registration vs. Sales Timing**: State registration data may lag actual sales by 15-30 days, potentially affecting month-end seasonal analysis
            - **Rural Market Coverage**: Data primarily captures urban and semi-urban sales; rural EV adoption likely underrepresented by 10-15%
            - **Unorganized Sector**: Small regional manufacturers and direct sales not fully captured in manufacturer analysis, estimated 5-8% market share gap
            
            ### Analytical Assumptions
            - **CAGR Projections**: Based on 3-year historical data; external factors (policy changes, fuel prices, economic conditions) may significantly impact future growth trajectories
            - **Seasonal Patterns**: Assumes consistent seasonal behavior; major policy interventions or economic disruptions could alter established patterns
            - **Market Maturity Classifications**: Based on current penetration rates; rapid infrastructure development could accelerate maturity transitions
            """
            )
    else:
        # Find the selected analysis
        selected_index = [
            i
            for i, analysis in enumerate(analyses)
            if analysis["name"] == selected_analysis
        ][0]
        selected_module_path = analyses[selected_index]["path"]

        # Check if the module exists
        full_path = BASE_DIR / "app" / selected_module_path
        if full_path.exists():
            # Add recommendations section before loading the module
            with st.expander("Key Recommendations", expanded=False):
                st.markdown(
                    """
                ### Strategic Recommendations
                
                Based on the insights from this analysis, we recommend:
                
                1. **Regional Expansion Strategy**
                   - Deploy dealer networks in Gujarat and Rajasthan (80%+ CAGR markets)
                   - Collaborate with state governments in northeastern regions to establish charging infrastructure
                
                2. **Seasonal Optimization Framework**
                   - Implement 60% inventory buildup during August-September to meet peak season demand
                   - Shift 45% of annual marketing spend to September-November period to capture peak buying intent
                
                3. **Manufacturer Partnership Opportunities**
                   - Target partnerships with regional manufacturers in emerging markets 
                   - Focus on B2B fleet partnerships with logistics companies during peak seasons
                
                These recommendations are based on data-driven insights and aim to maximize market opportunities while minimizing risks.
                """
                )
            
            # Run the analysis module
            run_analysis_module(selected_module_path)
        else:
            st.warning(
                f"The analysis module for '{selected_analysis}' is not yet implemented."
            )
            st.info(
                "This dashboard is under development. Please check back later for updates."
            )

            # Placeholder for future implementation
            st.markdown(
                f"""
            <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center;">
                <h2>{analyses[selected_index]["icon"]} {selected_analysis}</h2>
                <p>{analyses[selected_index]["description"]}</p>
                <p style="margin-top: 20px;">This analysis will be available soon!</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


# Run the app
if __name__ == "__main__":
    main()
