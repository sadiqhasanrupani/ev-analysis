import streamlit as st


def main():
    st.title("EV Analysis Dashboard Overview")
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric(label="Total EVs Sold", value="1,250,000")
      st.metric(label="Charging Stations", value="45,000")
    with col2:
      st.metric(label="Market Share (%)", value="7.5%")
      st.metric(label="Average Range (km)", value="350")
    with col3:
      st.metric(label="Annual Growth Rate", value="18%")
      st.metric(label="CO2 Saved (tons)", value="2,500,000")


if __name__ == "__main__":
    main()
