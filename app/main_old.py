import streamlit as st
from ev_sales_by_state_analysis.main import main as ev_sales_main
from research.main import main as research_main



# Main function
def main():
    analysis_type = st.selectbox(
        "Select Analysis Type",
        [
            "Overall Market Growth",
            "First 3 Research Analysis",
            "Vehicle Segment Analysis",
        ],
    )

    if analysis_type == "Overall Market Growth":
        # Set page configuration
        st.set_page_config(
            page_title=analysis_type, page_icon="🚗", layout="wide"
        )
        ev_sales_main()
    elif analysis_type == "First 3 Research Analysis":
        # Set page configuration
        st.set_page_config(
            page_title=analysis_type, page_icon="🔎", layout="wide"
        )
        research_main()
    elif analysis_type == "Vehicle Segment Analysis":
        st.info("Vehicle Segment Analysis is currently under development. Please check back later.")


if __name__ == "__main__":
    main()
