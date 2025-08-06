# 📄 EV Sales Analysis – Feature Engineering

**Version**: 1.0  
**Last Updated**: August 5, 2025

## 🔍 What This Document Covers

This document explains how we created new data columns (called **features**) from the original Electric Vehicle (EV) sales data. These features help us better understand how EV sales are growing across different states in India over time, and what factors are influencing this growth.

---

## 📊 Data Details

- **Original File**: `electric_vehicle_sales_by_state.csv`
- **Processed File**: `ev_sales_enhanced.csv`
- **Time Covered**: April 2021 to March 2024
- **Coverage**: All Indian states and union territories
- **Vehicle Types**: 2-wheelers and 4-wheelers

---

## 🧩 What Are Features?

Features are new pieces of information we created from the original data to help us see trends more clearly, make comparisons, and build useful models. We grouped them into different types.

---

## ⏱️ 1. Time-Based Features

These help us understand how EV sales change over time.

|Feature|What It Means|
|---|---|
|`year`|The year when the sale happened|
|`month`|The month of the sale|
|`quarter`|Which quarter of the financial year (e.g., Q1, Q2...)|
|`months_from_start`|How many months have passed since the first record|
|`rolling_mean_ev`|3-month average of EV sales to show smoother trends|
|`ev_growth_rate`|Change in EV sales from last month|
|`is_q4`|A flag to show if it’s the last quarter (Q4) of the year|
|`is_march`|A flag to show if it’s March (financial year-end)|

---

## 📈 2. Market Share Features

These show how well EVs are being adopted compared to other vehicles.

|Feature|What It Means|
|---|---|
|`ev_penetration`|% of total vehicles that are EVs|
|`ev_penetration_log`|A smoothed version of the above to avoid big swings|
|`national_market_share`|How much EV sales in a state contribute to national EV sales|
|`state_rank`|Rank of the state based on EV sales|
|`growth_stage`|Market phase (early, growing, mature)|
|`market_concentration`|How dominant a state is in the EV market|

---

## 📍 3. Regional Features

These compare states to others in the same region.

|Feature|What It Means|
|---|---|
|`region`|Group of states (North, South, etc.)|
|`regional_avg_penetration`|Average EV adoption in that region|
|`state_to_region_ratio`|How a state compares to its regional average|
|`regional_rank`|Rank of the state within its region|
|`market_maturity_score`|Score from 0-100 to show how developed the region's EV market is|
|`adoption_velocity`|Speed of growth in EV adoption|
|`adoption_velocity_capped`|Same as above but with extreme values limited|

---

## 🚗 4. Vehicle Type Features

These help us see if people prefer 2-wheelers or 4-wheelers when buying EVs.

|Feature|What It Means|
|---|---|
|`segment_penetration_2-wheelers`|% of EV 2-wheelers compared to all 2-wheelers sold|
|`segment_penetration_4-wheelers`|Same for 4-wheelers|
|`segment_preference_ratio`|How much more popular 2W is vs 4W (or vice versa)|
|`segment_preference_ratio_capped`|Same, but without extreme values|
|`segment_preference_ratio_log`|A smoother version of the above|
|`dominant_segment`|Which type of vehicle is preferred in the state|
|`segment_growth_diff`|Change in this preference over time|

---

## ✅ 5. Data Quality Flags

These help us track if any important values are missing.

|Feature|What It Means|
|---|---|
|`is_missing_ev_growth_rate`|EV growth rate data missing|
|`is_missing_segment_preference_ratio`|Segment ratio missing|
|`is_missing_segment_growth_diff`|Segment growth difference missing|
|`is_missing_regional_avg_penetration`|Region average penetration missing|
|`is_missing_adoption_velocity`|Adoption velocity missing|

---

## ✨ 6. Extra Features for Insights

|Feature|What It Means|
|---|---|
|`ev_sales_growth_rank_state`|Rank of state based on growth in EV sales|
|`ev_sales_growth_rank_region`|Same, but within region|
|`is_early_adopter`|True if the state adopted EVs early|
|`months_since_peak`|How long since the state had its highest EV sales|
|`is_at_peak`|True if the state is currently at its highest EV sales|

---

## 🛠️ How We Handled Data Problems

### Missing Values

- We used **previous values** to fill missing time data.
- We used **average/median** values to fill other gaps.
- We created flags to track where data was missing.

### Outliers (Unusual Data)

- We limited extreme values so they don’t affect results too much.
- Used log scales to smooth large numbers.

### Checks and Balances

- Double-checked all ratios and rankings.
- Validated totals and averages across states and regions.

---

## 💡 How to Use These Features

### For Time Trend Analysis

- Use `rolling_mean_ev` to view smooth sales trends.
- Use `ev_growth_rate` and note where data might be missing.
- Use `quarter` and `is_march` for seasonal patterns.

### For Regional Comparison

- Use `regional_rank`, `state_to_region_ratio`, and `market_maturity_score` to compare states.
- Use `region` for grouping.

### For Market Insights

- `growth_stage` and `is_early_adopter` show market maturity.
- `market_concentration` shows how concentrated the market is.

### For Segment Comparison

- Use `segment_preference_ratio` to see if 2W or 4W EVs are more popular.
- Use `dominant_segment` to track preference over time.

### For Predictive Modeling

- Use smoothed (log or capped) versions for better model accuracy.
- Include flags for missing values to improve predictions.

---

## 🔮 What’s Next?

### More Features We May Add

- Government policy impacts
- Charging infrastructure availability
- State-level economic conditions
- Weather and seasonal effects

### Improvements Planned

- Better ways to detect market phases
- Smarter handling of outliers
- Stronger checks for accuracy