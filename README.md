# Guangdong Province Population Flow Analysis System

![Guangdong Population Flow](./assets/guangdong-population-banner.png)

## 📋 Project Overview

This comprehensive data analysis system focuses on population flow and migration patterns in Guangdong Province, China. The application combines deep data scraping capabilities with advanced statistical analysis and interactive visualization tools to provide insights into population movements across cities in Guangdong from 2008 to 2022.

### 🌟 Key Features

- **Bilingual Interface**: Full support for both English and Chinese languages
- **Deep Web Scraping**: Collects population data from multiple Chinese government sources
- **Data Integration**: Combines web-scraped data with uploaded Excel files
- **Interactive Visualizations**: Dynamic maps, charts, and comparative analytics
- **Statistical Analysis**: Comprehensive statistical metrics and trend forecasting
- **Performance Optimization**: Robust caching system for fast data processing
- **Data Export**: Export analysis results in CSV or Excel formats

## 🛠️ Technical Architecture

The application is built with a modular architecture that separates concerns for better maintainability:

```
├── app.py                # Main Streamlit application
├── scraper.py            # Web scraping and data collection
├── data_processor.py     # Data processing and statistical analysis
├── visualizer.py         # Data visualization components
├── translations.py       # Multilingual support system
├── utils.py              # Utility functions
├── cache/                # Cache directory for data persistence
└── data/                 # Directory for Excel data files
```

## 🧠 Algorithms and Models

### 1. Data Collection Algorithms

#### Web Scraping Techniques
- **Trafilatura Extraction**: Primary text extraction tool that preserves document structure while cleaning HTML
- **BeautifulSoup Fallback**: Secondary parsing method used when Trafilatura fails
- **Pattern-based Extraction**: Three-tiered regex pattern system to extract population data from text

#### Data Integration
- **Source Validation Algorithm**: Multi-level validation system to ensure data consistency
- **Cascading Source Selection**: Prioritization algorithm to select the most reliable data sources when multiple sources are available

### 2. Statistical Models and Algorithms

#### Population Flow Analysis
- **Net Migration Rate**: Calculated as `(immigration - emigration) / population * 100`
- **Migration Efficiency Index**: Implemented as `net_migration / gross_migration` to measure directional efficiency
- **Growth Rate Analysis**: Compound annual growth rate (CAGR) calculation with year-over-year comparison

#### Statistical Methods
- **Confidence Interval Calculation**: Using Student's t-distribution for population change estimates
- **Linear Regression**: Trend analysis implemented for population forecasting
- **Outlier Detection**: Z-score method to identify anomalous population changes
- **City Classification Algorithm**: K-means classification to identify similar city migration patterns

### 3. Visualization Algorithms

#### Interactive Map Generation
- **Choropleth Mapping**: Color-intensity mapping algorithm based on population metrics
- **Force-directed Graph**: For city connectivity visualization with migration flows
- **Curved Flow Lines**: Bezier curve algorithm for visualizing direction and volume of migration

#### Trend Visualization
- **Smoothed Trend Lines**: LOESS (Locally Estimated Scatterplot Smoothing) for trend visualization
- **Normalization Algorithm**: Data standardization for cross-city comparison
- **Interactive Tooltip System**: Context-aware information display

### 4. Performance Optimization

#### Caching System
- **Multi-level Caching**: Application-level and function-level caching
- **Memoization**: Intelligent function result caching based on input parameters
- **LRU Cache Implementation**: Least Recently Used algorithm for cache management

#### Parallelization
- **Concurrent Data Processing**: Parallel execution for heavy calculations
- **Asynchronous Data Loading**: Non-blocking data retrieval from multiple sources

## 💻 Technologies Used

### Core Technologies
- **Python**: Primary programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Statistical computing and scientific algorithms
- **Plotly**: Interactive data visualization

### Data Collection Libraries
- **Trafilatura**: Web content extraction
- **BeautifulSoup4**: HTML parsing
- **Requests**: HTTP requests handling

### Data Storage and Processing
- **Excel Support**: openpyxl and xlrd for Excel file handling
- **JSON**: For configuration and cache metadata
- **CSV**: For data export and storage

## 📊 Data Sources

The application collects data from multiple sources:

1. **Government Statistical Bureaus**:
   - Guangdong Provincial Bureau of Statistics (http://stats.gd.gov.cn/)
   - City-level statistical bureaus (e.g., http://tjj.gz.gov.cn/)

2. **Government Information Disclosures**:
   - Official government websites (e.g., http://www.gd.gov.cn/)
   - Baili Government Information Portal (https://www.bl.gov.cn/)

3. **Excel Data Integration**:
   - User-provided Excel files (e.g., "liudongrenkou.xls")
   - Historical population datasets

4. **Academic and News Sources**:
   - Guangzhou Academy of Social Sciences
   - Southern Metropolis Daily
   - Nanfang City Newspaper

## 📈 Analysis Capabilities

### Population Flow Analysis
- Inflow/outflow identification
- Net migration calculation
- City-to-city flow visualization

### Trend Analysis
- Year-over-year growth calculation
- Long-term trend projection
- Seasonal migration patterns

### Comparative Analytics
- City-to-city comparison
- Regional clustering
- Demographic impact analysis

### Statistical Metrics
- Confidence intervals for population estimates
- Statistical significance testing
- Growth rate forecasting

## 🔍 Implementation Details

### Multi-pattern Text Extraction
The system employs three distinct regex patterns for extracting population data:
```python
# Pattern 1: Extracts "XXX市常住人口XXX万人，比上年增加/减少XXX万人"
city_pattern1 = r'(\w+市)[^\d]*([\d\.]+)万人[^，]*，[^增减]*(增加|减少)[^，]*([\d\.]+)万人'

# Pattern 2: Extracts "XXX市人口XXX万人，同比增长/下降XX.XX%"
city_pattern2 = r'(\w+市)[^\d]*人口[^\d]*([\d\.]+)万人[^，]*，[^增长下降]*(增长|下降)[^，]*([\d\.]+)%'

# Pattern 3: Extracts table-like data with city and population
city_pattern3 = r'([\u4e00-\u9fa5]+市)[^\d\n]{0,20}([\d\.]+)[万千]?人'
```

### Data Merging and Deduplication
When data is collected from multiple sources, the system implements a sophisticated merging algorithm:
```python
# Deduplication logic (simplified)
cities_seen = {}
unique_data = []

for entry in population_data:
    city_year = (entry['city'], entry['year'])
    
    if city_year not in cities_seen:
        cities_seen[city_year] = entry
        unique_data.append(entry)
    else:
        # Prefer entries with non-zero change values
        if abs(entry['change']) > 0 and abs(cities_seen[city_year]['change']) == 0:
            unique_data.remove(cities_seen[city_year])
            cities_seen[city_year] = entry
            unique_data.append(entry)
```

### Performance Optimization with Memoization
The application implements a custom caching decorator for performance:
```python
def cache_result(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        cache_key = hashlib.md5(str(key_parts).encode()).hexdigest()
        
        # Check if result is in cache and still valid
        if cache_key in _CACHE:
            result, timestamp = _CACHE[cache_key]
            if time.time() - timestamp < _CACHE_TTL:
                return result
        
        # Calculate result and store in cache
        result = func(*args, **kwargs)
        _CACHE[cache_key] = (result, time.time())
        
        return result
    return wrapper
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Required Python packages: streamlit, pandas, numpy, scipy, plotly, trafilatura, beautifulsoup4, requests, openpyxl, xlrd

### Installation
1. Clone the repository
2. Install the required packages:
   ```bash
   pip install streamlit pandas numpy scipy plotly trafilatura beautifulsoup4 requests openpyxl xlrd
   ```
3. Make sure the `data` and `cache` directories exist:
   ```bash
   mkdir -p data cache
   ```

### Running the Application
```bash
streamlit run app.py
```

## 🌐 Language Support

The application supports full bilingual operation in English and Chinese. The translation system is implemented through the `translations.py` module, which contains comprehensive language mappings for all UI elements.

## 📑 Data Integrity

All data collected through the application is validated through multiple steps:
1. Source verification
2. Data format validation
3. Statistical anomaly detection
4. Cross-reference with known population figures

## 🔒 Performance and Security

- Data is cached locally to improve performance
- No personal or sensitive data is collected
- All web scraping respects rate limits and robots.txt
- Error handling prevents application crashes due to data issues

## 📝 Future Enhancements

Potential future improvements include:
- Adding more visualization types
- Expanding to other Chinese provinces
- Implementing machine learning for population prediction
- Adding more language support
- Developing a predictive model for future population trends

## 📚 References

1. Guangdong Statistical Yearbooks (2008-2022)
2. Chinese Population Census Data
3. Academic research papers on population flow in China
4. Government population reports and policy documents

---

## 🙏 Acknowledgements

This project was developed as a comprehensive data analysis system for understanding population dynamics in Guangdong Province. Special thanks to all contributors and data providers that made this analysis possible.

---

© 2025 Guangdong Population Flow Analysis Project