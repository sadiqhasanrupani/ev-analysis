# Electric Vehicle Sales Analysis - Feature Engineering Technical Documentation

## Table of Contents
1. [Data Processing Overview](#data-processing-overview)
2. [Temporal Features](#temporal-features)
3. [Market Penetration Features](#market-penetration-features)
4. [Regional Features](#regional-features)
5. [Vehicle Segment Features](#vehicle-segment-features)
6. [Quality Control Features](#quality-control-features)
7. [Implementation Details](#implementation-details)

## Data Processing Overview

### Input Data Structure
- Primary dataset: `processed_ev_sales_by_state.csv`
- Key fields:
  * state
  * date
  * vehicle_category
  * electric_vehicles_sold
  * total_vehicles_sold

### Feature Engineering Pipeline
1. Temporal feature extraction
2. Market penetration calculations
3. Geographic data enrichment
4. Segment-specific metrics
5. Quality control implementation

## Temporal Features

### Basic Time Components
- `year`: Extracted year from date
- `month`: Numerical month (1-12)
- `quarter`: Calendar quarter (1-4)
- `month_name`: Full month name
- `year_month`: YYYY-MM format
- `months_from_start`: Continuous time index

### Time-Based Metrics
1. **Rolling Statistics**
   ```python
   rolling_mean_ev = rolling(window=3, min_periods=1).mean()
   ```
   - 3-month rolling average of EV sales
   - Handles seasonality and smooths fluctuations

2. **Growth Rate Calculations**
   ```python
   ev_growth_rate = pct_change()
   ```
   - Month-over-month growth
   - Infinity handling: replaced with NaN
   - NaN handling: filled with 0
   - Rounded to 2 decimal places

3. **Seasonal Indicators**
   - `is_q4`: Year-end quarter flag
   - `is_march`: Financial year-end flag

## Market Penetration Features

### Core Metrics
1. **EV Penetration Rate**
   ```python
   ev_penetration = (electric_vehicles_sold / total_vehicles_sold * 100).round(2)
   ```
   - Base metric for market adoption
   - Percentage scale (0-100)

2. **Market Share Analysis**
   ```python
   national_market_share = groupby('date').transform(lambda x: x / x.sum() * 100)
   ```
   - State's contribution to national sales
   - Normalized for comparison

### Advanced Market Metrics
1. **Growth Stage Classification**
   - Quartile-based categorization
   - Labels: Early, Developing, Maturing, Advanced
   - Based on penetration rate distribution

2. **Market Concentration**
   ```python
   market_concentration = x / x.max()
   ```
   - Normalized to market leader (0-1 scale)
   - Separate for each vehicle category

## Regional Features

### Geographic Data Processing
1. **Coordinate Acquisition**
   - Primary: Nominatim geocoding
   - Backup: Manual coordinates for key states
   - Coordinates used for regional classification

2. **Regional Classification**
   ```python
   def classify_region(lat, lon):
       if lat >= 28:
           if lon >= 85: return "Northeast"
           elif lon >= 75: return "North"
           else: return "Northwest"
       elif 23 <= lat < 28: return "Central"
       elif lat < 23:
           if lon < 80: return "West"
           else: return "South"
   ```

### Regional Metrics
1. **Regional Averages**
   - `regional_avg_penetration`
   - `state_to_region_ratio`
   - `regional_rank`
   - `market_maturity_score`

2. **Growth Metrics**
   - `regional_growth_rate`
   - `growth_vs_region`
   - Zero-handling for division operations

## Vehicle Segment Features

### Segment-Specific Analysis
1. **Penetration Metrics**
   ```python
   segment_penetration = (electric_vehicles_sold / total_vehicles_sold * 100).round(2)
   ```
   - Calculated separately for 2-wheelers and 4-wheelers

2. **Segment Comparison**
   ```python
   segment_preference_ratio = (
       segment_penetration_2_wheelers / segment_penetration_4_wheelers
   ).round(2)
   ```
   - Ratio analysis
   - Infinity handling implemented
   - Missing value treatment

### Advanced Segment Features
1. **Growth Patterns**
   - `segment_growth_diff`
   - Time-series based comparisons
   - Trend analysis capabilities

2. **Dominance Indicators**
   ```python
   dominant_segment = np.where(segment_preference_ratio > 1, "2-Wheelers", "4-Wheelers")
   ```
   - Binary classification
   - Market leadership indication

## Quality Control Features

### Missing Value Flags
- Created for critical metrics:
  * ev_growth_rate
  * segment_preference_ratio
  * segment_growth_diff
  * regional_avg_penetration
  * adoption_velocity

### Outlier Handling
```python
def cap_outliers(series, n_std=3):
    mean = series.mean()
    std = series.std()
    return series.clip(mean - n_std * std, mean + n_std * std)
```
- Applied to key metrics
- Standard deviation based approach
- Group-wise implementation

### Data Transformations
1. **Log Transformations**
   - Applied to:
     * segment_preference_ratio
     * ev_penetration
   - Preserves original data
   - Improves distribution normality

2. **Capped Versions**
   - Created for:
     * segment_preference_ratio
     * adoption_velocity
   - Maintains analysis stability
   - Original values preserved

## Implementation Details

### Data Pipeline
1. Feature Creation
   - Sequential processing
   - Grouped operations
   - Efficient transformations

2. Quality Checks
   - Consistency validation
   - Range checks
   - Logic verification

3. Missing Value Handling
   - Forward fill for time series
   - Median imputation
   - Zero substitution

4. Outlier Processing
   - Standard deviation based capping
   - Group-wise processing
   - Original value preservation

5. Export
   - CSV format
   - No index
   - Rounded values

### Critical Considerations
1. **Data Quality**
   - Missing value tracking
   - Outlier identification
   - Consistency checks

2. **Performance Optimization**
   - Efficient groupby operations
   - Minimized data copying
   - Memory management

3. **Maintainability**
   - Clear variable naming
   - Consistent methodology
   - Documented transformations

### Output Dataset Structure
File: `ev_sales_enhanced.csv`

#### Feature Categories:
1. **Temporal Features** (7)
   - date, year, month, quarter
   - months_from_start
   - rolling_mean_ev
   - ev_growth_rate

2. **Market Penetration Features** (7)
   - ev_penetration
   - ev_penetration_log
   - national_market_share
   - state_rank
   - growth_stage
   - market_concentration

3. **Regional Features** (7)
   - region
   - regional_avg_penetration
   - state_to_region_ratio
   - regional_rank
   - market_maturity_score
   - adoption_velocity
   - adoption_velocity_capped

4. **Segment Features** (7)
   - segment_penetration_2-wheelers
   - segment_penetration_4-wheelers
   - segment_preference_ratio
   - segment_preference_ratio_capped
   - segment_preference_ratio_log
   - dominant_segment
   - segment_growth_diff

5. **Quality Indicators** (5)
   - is_missing_ev_growth_rate
   - is_missing_segment_preference_ratio
   - is_missing_segment_growth_diff
   - is_missing_regional_avg_penetration
   - is_missing_adoption_velocity

6. **Original Features** (4)
   - state
   - vehicle_category
   - electric_vehicles_sold
   - total_vehicles_sold

## Future Enhancements

### Planned Improvements
1. **Additional Regional Metrics**
   - Population-adjusted metrics
   - Infrastructure correlation
   - Economic indicators

2. **Seasonality Adjustments**
   - Weather impact analysis
   - Festival season effects
   - Policy change impacts

3. **Advanced Growth Modeling**
   - Predictive indicators
   - Growth stage transitions
   - Market saturation metrics

4. **Enhanced Quality Controls**
   - Automated anomaly detection
   - Cross-validation checks
   - Confidence metrics

### Development Roadmap
1. Q3 2025
   - Population metrics integration
   - Weather impact analysis
   - Anomaly detection system

2. Q4 2025
   - Infrastructure correlation
   - Festival impact analysis
   - Confidence metrics

3. Q1 2026
   - Predictive indicators
   - Market saturation analysis
   - Cross-validation framework
