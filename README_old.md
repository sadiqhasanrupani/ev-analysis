# 🚗⚡ Electric Vehicle Market Analysis in India

## 📖 Project Overview

This project provides a comprehensive analysis of India's Electric Vehicle (EV) market evolution from April 2021 to March 2024. Through detailed data analysis and visualization, we uncover market growth patterns, regional dynamics, and strategic opportunities in India's rapidly expanding EV ecosystem.

## 🎯 Project Objectives

- **Market Evolution Analysis**: Track EV adoption patterns across Indian states over 3 years
- **Regional Market Dynamics**: Identify regional leaders, emerging markets, and growth opportunities
- **Growth Pattern Recognition**: Understand market penetration trends and adoption velocity
- **Strategic Insights**: Provide actionable recommendations for market expansion
- **Data-Driven Decision Making**: Support policy makers and industry stakeholders with robust analytics

## 📊 Dataset Information

### Data Sources
The analysis is based on three primary datasets:

1. **`electric_vehicle_sales_by_state.csv`** - State-wise EV sales data
   - Monthly sales data by state and vehicle category (2-Wheeler/4-Wheeler)
   - Electric vehicles sold vs total vehicles sold
   - Period: April 2021 to March 2024

2. **`electric_vehicle_sales_by_makers.csv`** - Manufacturer-wise sales data
   - Sales data by EV manufacturers/brands
   - Vehicle category breakdown
   - Monthly tracking of market share

3. **`dim_date.csv`** - Date dimension table
   - Fiscal year and quarter mapping
   - Supports time-series analysis

### Key Metrics Analyzed
- **Penetration Rate**: `(Electric Vehicles Sold / Total Vehicles Sold) * 100`
- **CAGR**: Compound Annual Growth Rate over the analysis period
- **Market Share**: Regional and manufacturer distribution
- **Growth Velocity**: Month-over-month and year-over-year growth patterns

## 🗂️ Project Structure

```
ev-analysis/
├── data/
│   ├── raw/                           # Original datasets
│   │   ├── electric_vehicle_sales_by_state.csv
│   │   ├── electric_vehicle_sales_by_makers.csv
│   │   └── dim_date.csv
│   └── processed/                     # Cleaned and enhanced datasets
│       ├── ev_sales_enhanced.csv
│       └── processed_ev_sales_by_state.csv
│
├── notebooks/                         # Jupyter notebooks for analysis
│   ├── ev_sales_by_state_analysis/    # State-wise analysis
│   │   ├── 01_data_cleaning.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_feature_engineering.ipynb
│   │   ├── 04_exploratory_data_analysis.ipynb
│   │   └── feature_engineering_documentation.md
│   ├── ev_sales_by_markers_analysis/  # Manufacturer analysis
│   │   ├── 01_data_cleaning.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   └── 03_note_and_document.ipynb
│   └── 03_note_and_document.ipynb     # Main documentation notebook
│
├── docs/                             # Documentation and reports
│   ├── analysis_summary/
│   │   └── comprehensive_market_analysis.md  # Main analysis report
│   ├── presentations/
│   │   └── ev_market_analysis_presentation_script.md
│   ├── feature_engineering/          # Technical documentation
│   │   ├── feature_engineering_summary.md
│   │   ├── feature_engineering_technical.md
│   │   └── technical/
│   ├── ev-sales-by-month-analysis/   # Detailed monthly analysis docs
│   ├── problem/                      # Problem statement and metadata
│   │   ├── Problem Statement.pdf
│   │   ├── Questions.pdf
│   │   └── meta_data.txt
│   └── citations.md                  # Data citations and references
│
└── README.md                         # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Jupyter Notebook or JupyterLab
- Required Python libraries (see Installation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ev-analysis
   ```

2. **Install required dependencies:**
   ```bash
   pip install pandas numpy matplotlib seaborn plotly jupyter scikit-learn
   ```

3. **Additional geospatial data (if needed for mapping):**
   - Download GADM India boundary data from [https://gadm.org](https://gadm.org)
   - File: `gadm41_IND.gpkg` (for administrative boundaries)

### Data Access

The datasets are included in the `data/raw/` directory:

- **Primary Data**: Located in `data/raw/`
- **Processed Data**: Enhanced datasets in `data/processed/`
- **No external downloads required** - all data is self-contained

## 📋 Analysis Workflow

### Step 1: Data Preparation
1. **Data Cleaning** (`01_data_cleaning.ipynb`)
   - Handle missing values and data inconsistencies
   - Standardize date formats and state names
   - Validate data integrity

2. **Feature Engineering** (`02_feature_engineering.ipynb`, `03_feature_engineering.ipynb`)
   - Calculate penetration rates
   - Create temporal features (fiscal year, quarter, month)
   - Generate growth metrics and moving averages
   - Add regional classifications

### Step 2: Exploratory Data Analysis
3. **Market Analysis** (`04_exploratory_data_analysis.ipynb`)
   - State-wise sales distribution analysis
   - Temporal trend analysis
   - Regional performance comparison
   - Market penetration patterns
   - Growth correlation analysis

### Step 3: Documentation and Insights
4. **Documentation** (`03_note_and_document.ipynb`)
   - Comprehensive analysis documentation
   - Key findings and insights
   - Methodology explanations

## 🔍 Key Analysis Areas

### 1. Market Growth Analysis
- **Overall Growth**: EV penetration increased from 0.53% to 7.83% (April 2021 - March 2024)
- **Growth Pattern**: Exponential growth indicating accelerating adoption
- **Regional Variations**: Significant differences in adoption rates across states

### 2. Regional Market Leaders
**Top 5 States by Market Share:**
- Maharashtra
- Karnataka
- Tamil Nadu
- Gujarat
- Rajasthan

**Regional Performance:**
- **South Region**: 32% higher than national average penetration
- **West Region**: 28% higher than national average
- **North Region**: Strong emerging growth trajectory

### 3. Market Maturity Stages
- **Early Stage** (25% of regions): Low but rapidly growing penetration
- **Developing Stage** (35% of regions): Moderate penetration, stabilizing growth
- **Maturing Stage** (30% of regions): Above-average penetration, consistent growth
- **Advanced Stage** (10% of regions): High penetration, steady growth

### 4. Vehicle Category Insights
- **2-Wheelers**: Higher adoption in tier-2/3 cities, seasonal sensitivity
- **4-Wheelers**: Concentrated in metropolitan areas, stable growth

## 📈 Key Findings

### Market Opportunities
1. **High-Priority Development Regions**:
   - Northeast: Infrastructure development potential
   - Northwest: Market activation opportunities
   - Central: Middle-market expansion

2. **Segment-Specific Strategies**:
   - Urban 2-wheeler focus: Last-mile connectivity, delivery fleets
   - Metropolitan 4-wheeler strategy: Premium segments, corporate fleets

### Growth Drivers
- Infrastructure development
- Policy support and incentives
- Manufacturer presence and dealer networks
- Consumer awareness and acceptance

## 🛠️ Technical Implementation

### Data Processing Pipeline
1. **Raw Data Ingestion**: CSV files loaded with pandas
2. **Data Cleaning**: Missing value handling, data type conversion
3. **Feature Engineering**: Calculated metrics, temporal features
4. **Analysis**: Statistical analysis, visualization, correlation studies
5. **Documentation**: Automated report generation

### Technologies Used
- **Data Analysis**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Statistical Analysis**: SciPy, Scikit-learn
- **Documentation**: Jupyter Notebooks, Markdown
- **Geospatial Analysis**: GADM database for administrative boundaries

## 📊 Outputs and Deliverables

### Analysis Reports
1. **Comprehensive Market Analysis** (`docs/analysis_summary/comprehensive_market_analysis.md`)
   - Executive summary with key insights
   - Strategic recommendations
   - Market maturity analysis
   - Growth opportunities identification

2. **Technical Documentation** (`docs/feature_engineering/`)
   - Feature engineering methodology
   - Data transformation processes
   - Technical implementation details

3. **Presentation Materials** (`docs/presentations/`)
   - Ready-to-use presentation script
   - Key visualization guidelines
   - Storytelling framework

### Processed Datasets
- Enhanced datasets with calculated metrics
- Regional classifications and growth indicators
- Time-series ready data for further analysis

## 🔄 Reproducibility

### Running the Analysis
1. **Execute notebooks in sequence:**
   ```bash
   # Data preparation
   jupyter notebook notebooks/ev_sales_by_state_analysis/01_data_cleaning.ipynb
   jupyter notebook notebooks/ev_sales_by_state_analysis/02_feature_engineering.ipynb
   
   # Analysis
   jupyter notebook notebooks/ev_sales_by_state_analysis/04_exploratory_data_analysis.ipynb
   ```

2. **View processed data:**
   - Check `data/processed/` for enhanced datasets
   - Review feature engineering documentation

3. **Generate reports:**
   - Run documentation notebooks
   - Export analysis results

### Customization
- Modify analysis parameters in notebooks
- Add new regions or time periods
- Extend feature engineering pipeline
- Create additional visualizations

## 🎯 Strategic Applications

### For Policymakers
- Regional development prioritization
- Infrastructure investment planning
- Policy effectiveness assessment

### For Industry Stakeholders
- Market entry strategies
- Regional expansion planning
- Competitive analysis
- Investment decision support

### For Researchers
- EV adoption pattern studies
- Regional development analysis
- Market evolution research

## 📚 References and Citations

### Data Sources
- Administrative boundary data: GADM database (https://gadm.org)
- EV sales data: Government and industry sources

### Citation Format
```bibtex
@misc{gadm41,
  author = {{GADM}},
  title = {GADM database of Global Administrative Areas, version 4.1},
  year = {2023},
  url = {https://gadm.org}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report issues or bugs
- Suggest new analysis approaches
- Add additional data sources
- Improve documentation
- Enhance visualizations

## 📄 License

This project is available for academic and non-commercial use. Please cite appropriately when using this analysis or methodology.

## 📞 Contact

For questions, suggestions, or collaboration opportunities, please reach out through the repository's issue tracker or contact information provided in the project.

---

**Note**: This analysis is based on data through March 2024 and should be updated regularly to reflect market changes and new trends.

**Last Updated**: December 2024