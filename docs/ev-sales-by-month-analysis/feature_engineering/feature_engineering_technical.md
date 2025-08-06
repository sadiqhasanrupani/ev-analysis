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
- Created for critical metrics
- Binary indicators (0/1)
- Tracks data completeness

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
   - Applied to skewed features
   - Preserves original data
   - Improves distribution normality

2. **Capped Versions**
   - Created for volatile metrics
   - Maintains analysis stability
   - Original values preserved

## Implementation Details

### Data Pipeline
1. Feature Creation
2. Quality Checks
3. Missing Value Handling
4. Outlier Processing
5. Export

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

### Output Dataset
- File: `ev_sales_enhanced.csv`
- Features: 40+ engineered columns
- Quality indicators included
- Ready for analysis use

## Future Enhancements
1. Additional regional metrics
2. Seasonality adjustments
3. Advanced growth modeling
4. Enhanced quality controls
