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
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

# Define all available analyses
analyses = [
    {
        "name": "Top 10 States with Highest CAGR",
        "description": "Analysis of states with highest compound annual growth rate (CAGR) for total vehicles, EVs, and non-EVs from 2022 to 2024.",
        "path": "research-analysis/top10_states_with_highest_cagr/analysis.py",
        "icon": "📈"
    },
    {
        "name": "Vehicle Analysis by State",
        "description": "State-wise breakdown of vehicle sales patterns and trends across India.",
        "path": "research-analysis/vehical_analysis_by_state/main.py",
        "icon": "🗺️"
    },
    # Add more analyses here as they are developed
    {
        "name": "EV Penetration Decline Analysis",
        "description": "Investigation into states showing a decline in EV market penetration between 2022 and 2024.",
        "path": "research-analysis/ev_penetration_decline_analysis/analysis.py", 
        "icon": "📉"
    },
    {
        "name": "Top vs Bottom 2-Wheeler Makers",
        "description": "Comparative analysis of top and bottom performing two-wheeler manufacturers in FY 2023-2024.",
        "path": "top_bottom_2w_makers_fy2023_2024/analysis.py",
        "icon": "🏍️"
    },
    {
        "name": "Quarterly Trends - Top 5 4-Wheeler Makers",
        "description": "Analysis of quarterly sales volume trends for the top 5 four-wheeler EV manufacturers from 2022 to 2024.",
        "path": "research-analysis/qtr_trends_ev_top5/analysis.py",
        "icon": "📊"
    },
    {
        "name": "Delhi vs Karnataka EV Comparison",
        "description": "Comparative analysis of EV sales and penetration rates between Delhi and Karnataka for 2024.",
        "path": "research-analysis/ev_sales_penetration_delhi_vs_karnataka_2024/analysis.py",
        "icon": "🔋"
    },
    {
        "name": "CAGR Analysis - Top 5 4-Wheeler EV Makers",
        "description": "Detailed analysis of the compounded annual growth rate (CAGR) for the top 5 four-wheeler EV manufacturers from 2022 to 2024.",
        "path": "research-analysis/cagr_top5_4w_ev_2022_2024/analysis.py",
        "icon": "🚗"
    }
]

def run_analysis_module(module_path):
    """Dynamically import and run a Streamlit analysis module"""
    try:
        # Get the full path to the module
        full_path = BASE_DIR / 'app' / module_path
        
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
        if hasattr(module, 'main'):
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
    
    # Title and introduction
    st.markdown("""
    <div class="header-container">
        <div style="font-size: 40px; margin-right: 15px;">🚗</div>
        <h1>EV Market Analysis Dashboard Hub</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome banner
    st.markdown("""
    <div class="banner">
        <h3>Welcome to the Electric Vehicle Market Analysis Dashboard</h3>
        <p>This interactive hub provides access to various analyses of the Indian electric vehicle market from 2022 to 2024. 
        Select any analysis from the sidebar or explore the dashboard cards below to dive deeper into specific aspects of the EV market.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Project overview
    with st.expander("🔍 About This Project", expanded=True):
        st.markdown("""
        This comprehensive analysis explores the Indian electric vehicle (EV) market between 2022 and 2024, focusing on:
        
        - **Growth Patterns**: Analyzing CAGR across different states for total vehicles and EV segment
        - **Regional Variations**: Understanding geographic differences in EV adoption
        - **Market Penetration**: Examining the share of EVs in overall vehicle sales
        - **Manufacturer Performance**: Assessing key players in the EV manufacturing landscape
        - **Segment Analysis**: 
          - Detailed CAGR analysis of top 4-wheeler EV manufacturers
          - Comparative analysis of top and bottom 2-wheeler makers
          - Quarterly trends of leading EV manufacturers
        - **Geographic Comparisons**: Comparing EV sales and penetration across states like Delhi and Karnataka
        
        The dashboard provides interactive visualizations and data-driven insights to help understand the evolving EV landscape in India, with detailed market share analysis, growth consistency evaluations, and year-by-year performance metrics for leading manufacturers.
        """)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    selected_analysis = st.sidebar.selectbox(
        "Select Analysis",
        options=["Hub Home"] + [analysis["name"] for analysis in analyses],
        index=0,
        format_func=lambda x: "🏠 " + x if x == "Hub Home" else x
    )
    
    # Handle navigation selection
    if selected_analysis == "Hub Home":
        # Display all available analyses as cards
        st.subheader("Available Analyses")
        
        # Create a 2-column layout for the cards
        col1, col2 = st.columns(2)
        
        for i, analysis in enumerate(analyses):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                st.markdown(f"""
                <div class="dashboard-card">
                    <div style="font-size: 28px; margin-bottom: 10px;">{analysis["icon"]}</div>
                    <h3 class="card-title">{analysis["name"]}</h3>
                    <p class="card-description">{analysis["description"]}</p>
                    <button 
                        onclick="window.location.href='?analysis={i}'" 
                        class="launch-btn">
                        Launch Dashboard
                    </button>
                </div>
                """, unsafe_allow_html=True)
        
        # Additional information section
        st.markdown("---")
        st.subheader("Dataset Information")
        
        # Create columns for dataset details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Time Period", "2022-2024")
        with col2:
            st.metric("States Covered", "35+")
        with col3:
            st.metric("Analysis Categories", "4")
        
        # Data sources acknowledgment
        st.markdown("""
        <div style="margin-top: 20px; font-size: 0.85em; color: #666;">
        <p><strong>Data Sources:</strong> This analysis is based on processed data files in the project's data directory, 
        including state-wise EV sales, manufacturer performance metrics, and regional sales data.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Find the selected analysis
        selected_index = [i for i, analysis in enumerate(analyses) if analysis["name"] == selected_analysis][0]
        selected_module_path = analyses[selected_index]["path"]
        
        # Check if the module exists
        full_path = BASE_DIR / 'app' / selected_module_path
        if full_path.exists():
            run_analysis_module(selected_module_path)
        else:
            st.warning(f"The analysis module for '{selected_analysis}' is not yet implemented.")
            st.info("This dashboard is under development. Please check back later for updates.")
            
            # Placeholder for future implementation
            st.markdown(f"""
            <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center;">
                <h2>{analyses[selected_index]["icon"]} {selected_analysis}</h2>
                <p>{analyses[selected_index]["description"]}</p>
                <p style="margin-top: 20px;">This analysis will be available soon!</p>
            </div>
            """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()