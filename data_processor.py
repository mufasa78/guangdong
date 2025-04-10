import pandas as pd
import numpy as np
from scipy import stats
import functools
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Cache for storing processed results to avoid redundant calculations
_CACHE = {}
_CACHE_TTL = 3600  # 1 hour cache validity

def cache_result(func):
    """Decorator to cache function results based on parameters"""
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
                print(f"Using cached result for {func.__name__}")
                return result
        
        # Calculate result and store in cache
        result = func(*args, **kwargs)
        _CACHE[cache_key] = (result, time.time())
        
        # Limit cache size to prevent memory issues
        if len(_CACHE) > 100:
            # Remove oldest entries
            oldest_keys = sorted(_CACHE.items(), key=lambda x: x[1][1])[:20]
            for k, _ in oldest_keys:
                _CACHE.pop(k, None)
                
        return result
    return wrapper

@cache_result
def process_data(data, selected_cities, time_period, analysis_type):
    """
    Process population data based on user selections with optimizations
    
    Args:
        data (DataFrame): Raw population data
        selected_cities (list): List of selected cities
        time_period (str): Selected time period (e.g., "2018-2022")
        analysis_type (str): Type of analysis to perform
        
    Returns:
        DataFrame: Processed data for visualization
    """
    # Filter by cities
    filtered_data = data[data['city'].isin(selected_cities)].copy()
    
    # Filter by time period
    year_start, year_end = map(int, time_period.split('-'))
    year_filter = (filtered_data['year'] >= year_start) & (filtered_data['year'] <= year_end)
    filtered_data = filtered_data[year_filter]
    
    # Check if the flow_type column exists, if not create it based on change values
    if 'flow_type' not in filtered_data.columns:
        filtered_data['flow_type'] = filtered_data['change'].apply(
            lambda x: 'inflow' if x > 0 else 'outflow'
        )
    
    # Process based on analysis type
    if "inflow" in analysis_type.lower():
        # Focus on cities with positive change (inflow)
        filtered_data['analysis_value'] = filtered_data['change'].apply(
            lambda x: x if x > 0 else 0
        )
    elif "outflow" in analysis_type.lower():
        # Focus on cities with negative change (outflow)
        filtered_data['analysis_value'] = filtered_data['change'].apply(
            lambda x: -x if x < 0 else 0
        )
    else:  # Net migration
        filtered_data['analysis_value'] = filtered_data['change']
    
    # Calculate additional metrics
    filtered_data['cumulative_change'] = filtered_data.groupby('city')['change'].cumsum()
    filtered_data['percent_of_total'] = filtered_data.groupby('year')['population'].transform(
        lambda x: x / x.sum() * 100
    )
    
    return filtered_data

@cache_result
def calculate_statistics(data, confidence_level=0.95):
    """
    Calculate statistical metrics from the processed data with optimized performance
    
    Args:
        data (DataFrame): Processed population data
        confidence_level (float): Confidence level for statistical intervals
        
    Returns:
        dict: Dictionary of calculated statistics
    """
    stats_dict = {}
    
    # Basic metrics
    stats_dict['total_population'] = data['population'].sum() if 'population' in data else 0
    stats_dict['avg_annual_flow'] = data['change'].mean() if 'change' in data else 0
    
    # Calculate growth rates
    if 'growth_rate' in data.columns and not data.empty:
        stats_dict['growth_rate'] = data['growth_rate'].mean()
        
        # Growth rate change (current year vs previous year)
        latest_year = data['year'].max() if 'year' in data else 0
        previous_year = latest_year - 1
        
        latest_rate = data[data['year'] == latest_year]['growth_rate'].mean() if not data[data['year'] == latest_year].empty else 0
        previous_rate = data[data['year'] == previous_year]['growth_rate'].mean() if not data[data['year'] == previous_year].empty else 0
        
        if not np.isnan(latest_rate) and not np.isnan(previous_rate):
            stats_dict['growth_rate_change'] = latest_rate - previous_rate
    else:
        # Calculate simple growth rate
        if not data.empty and 'population' in data.columns and 'change' in data.columns:
            total_population = data['population'].sum()
            total_change = data['change'].sum()
            stats_dict['growth_rate'] = (total_change / total_population) * 100 if total_population > 0 else 0
        else:
            stats_dict['growth_rate'] = 0
    
    # Calculate confidence intervals if enough data points
    if len(data) > 2 and 'change' in data:
        changes = data['change'].dropna()
        if len(changes) > 0:
            mean = changes.mean()
            stderr = stats.sem(changes)
            ci = stats.t.interval(confidence_level, len(changes)-1, mean, stderr)
            
            stats_dict['mean_change'] = mean
            stats_dict['change_confidence_interval'] = [float(ci[0]), float(ci[1])]
    
    # City with highest inflow and outflow
    if not data.empty and 'city' in data and 'change' in data:
        inflow = data[data['change'] > 0]
        outflow = data[data['change'] < 0]
        
        if not inflow.empty:
            highest_inflow_city = inflow.groupby('city')['change'].sum().idxmax()
            stats_dict['highest_inflow_city'] = highest_inflow_city
            stats_dict['highest_inflow_amount'] = inflow.groupby('city')['change'].sum().max()
        
        if not outflow.empty:
            highest_outflow_city = outflow.groupby('city')['change'].sum().idxmin()
            stats_dict['highest_outflow_city'] = highest_outflow_city
            stats_dict['highest_outflow_amount'] = outflow.groupby('city')['change'].sum().min()
    
    # Trend analysis
    if not data.empty and 'year' in data and 'population' in data:
        years = data['year'].unique()
        if len(years) > 1:
            # Fit a linear regression to estimate trend
            city_trends = {}
            for city in data['city'].unique():
                city_data = data[data['city'] == city]
                if len(city_data) > 1:  # Need at least two points for regression
                    x = city_data['year'].values.reshape(-1, 1)
                    y = city_data['population'].values
                    model = stats.linregress(x.flatten(), y)
                    
                    # Slope indicates growth trend
                    city_trends[city] = {
                        'slope': model.slope,
                        'r_value': model.rvalue,
                        'p_value': model.pvalue
                    }
            
            stats_dict['city_trends'] = city_trends
    
    return stats_dict

@cache_result
def calculate_flow_indices(data):
    """
    Calculate population flow indices for cities with performance optimization
    
    Args:
        data (DataFrame): Processed population data
        
    Returns:
        DataFrame: Data with additional flow indices
    """
    if data.empty:
        return data
    
    # Create a copy to avoid modifying the original
    result = data.copy()
    
    # Calculate net migration rate
    result['net_migration_rate'] = result['change'] / result['population'] * 100
    
    # Calculate migration efficiency
    # Group by city and year to calculate total inflow and outflow
    if 'flow_type' in result:
        city_year_groups = result.groupby(['city', 'year'])
        
        # Calculate inflow and outflow for each city and year
        inflows = []
        outflows = []
        
        for (city, year), group in city_year_groups:
            inflow = group[group['flow_type'] == 'inflow']['change'].sum()
            outflow = -group[group['flow_type'] == 'outflow']['change'].sum()
            
            inflows.append({
                'city': city,
                'year': year,
                'inflow': inflow
            })
            
            outflows.append({
                'city': city,
                'year': year,
                'outflow': outflow
            })
        
        # Convert to DataFrames
        inflow_df = pd.DataFrame(inflows)
        outflow_df = pd.DataFrame(outflows)
        
        # Merge back with the original data
        if not inflow_df.empty and not outflow_df.empty:
            flow_df = pd.merge(inflow_df, outflow_df, on=['city', 'year'])
            flow_df['gross_migration'] = flow_df['inflow'] + flow_df['outflow']
            flow_df['net_migration'] = flow_df['inflow'] - flow_df['outflow']
            flow_df['migration_efficiency'] = flow_df.apply(
                lambda row: row['net_migration'] / row['gross_migration'] if row['gross_migration'] > 0 else 0,
                axis=1
            )
            
            # Merge the calculated indices back to the result
            result = pd.merge(result, flow_df, on=['city', 'year'], how='left')
    
    return result
