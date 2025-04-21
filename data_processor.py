import pandas as pd
import numpy as np
from scipy import stats
import functools
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from datetime import datetime

# Cache for storing processed results
_CACHE = {}
_CACHE_TTL = 3600  # 1 hour cache validity

def validate_data_point(row):
    """Validate a single data point"""
    try:
        # Basic validation rules
        if not row['city'].strip().endswith('市'):
            return False

        current_year = datetime.now().year
        if not (2000 <= row['year'] <= current_year):
            return False

        if row['population'] <= 0:
            return False

        # Sanity checks for extreme values
        if row['population'] > 50000000:  # No city should have > 50M population
            return False

        # Check if change is reasonable if it exists
        if 'change' in row and pd.notna(row['change']):
            if abs(row['change']) > row['population'] * 0.5:  # Change shouldn't be >50% of population
                return False

        return True
    except:
        return False

def clean_and_standardize(df):
    """Clean and standardize the dataframe"""
    if df.empty:
        return df

    # Remove duplicates
    df = df.drop_duplicates(subset=['city', 'year'], keep='last')

    # Sort by city and year
    df = df.sort_values(['city', 'year'])

    # Fill missing changes
    if 'change' in df.columns:
        df['change'] = df.groupby('city')['population'].diff().fillna(0)

    # Calculate growth rates
    df['growth_rate'] = df.groupby('city')['population'].pct_change().fillna(0) * 100

    # Add rolling metrics
    df['rolling_growth'] = df.groupby('city')['growth_rate'].rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)

    # Detect and handle outliers
    for city in df['city'].unique():
        city_data = df[df['city'] == city]
        if len(city_data) >= 3:  # Need at least 3 points for zscore
            z_scores = np.abs(stats.zscore(city_data['population']))
            outliers = z_scores > 3
            if outliers.any():
                # Interpolate outliers
                df.loc[df['city'] == city, 'population'] = df.loc[df['city'] == city, 'population'].interpolate()

    return df

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
    """Process population data with enhanced validation and analysis"""
    # Filter by cities
    filtered_data = data[data['city'].isin(selected_cities)].copy()

    # Filter by time period
    year_start, year_end = map(int, time_period.split('-'))
    year_filter = (filtered_data['year'] >= year_start) & (filtered_data['year'] <= year_end)
    filtered_data = filtered_data[year_filter]

    # Apply cleaning and standardization
    filtered_data = clean_and_standardize(filtered_data)

    # Validate each data point
    valid_data = filtered_data[filtered_data.apply(validate_data_point, axis=1)]

    # Ensure 'change' column exists
    if 'change' not in valid_data.columns and len(valid_data) > 0:
        valid_data['change'] = valid_data.groupby('city')['population'].diff().fillna(0)

    # Calculate migration efficiency
    if len(valid_data) > 0:
        valid_data['net_migration'] = valid_data.groupby('city')['change'].rolling(window=2, min_periods=1).sum().reset_index(0, drop=True)
        valid_data['migration_efficiency'] = valid_data['net_migration'] / valid_data['population'].where(valid_data['population'] > 0, 0)

    # Process based on analysis type
    if "inflow" in analysis_type.lower():
        valid_data['analysis_value'] = valid_data['change'].apply(lambda x: x if x > 0 else 0)
    elif "outflow" in analysis_type.lower():
        valid_data['analysis_value'] = valid_data['change'].apply(lambda x: -x if x < 0 else 0)
    else:  # Net migration
        valid_data['analysis_value'] = valid_data['change']

    # Calculate additional metrics
    valid_data['cumulative_change'] = valid_data.groupby('city')['change'].cumsum()
    valid_data['percent_of_total'] = valid_data.groupby('year')['population'].transform(lambda x: x / x.sum() * 100)

    # Generate migration reasons if they don't exist
    if 'migration_reasons' not in valid_data.columns:
        from scraper import generate_migration_reasons
        valid_data['migration_reasons'] = valid_data.apply(
            lambda row: generate_migration_reasons(row['city'], row['year']), 
            axis=1
        )

    return valid_data

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

    # Basic metrics calculation (existing code)
    stats_dict['total_population'] = data['population'].sum() if 'population' in data else 0
    stats_dict['avg_annual_flow'] = data['change'].mean() if 'change' in data else 0

    # Add migration reasons analysis if available
    if 'migration_reasons' in data.columns:
        stats_dict['migration_reasons'] = {}

        # Overall reason distribution
        all_reasons = []
        for reasons in data['migration_reasons'].dropna():
            if isinstance(reasons, list):
                all_reasons.extend(reasons)

        if all_reasons:
            from collections import Counter
            reason_counts = Counter(all_reasons)
            total_reasons = sum(reason_counts.values())

            stats_dict['migration_reasons']['distribution'] = {
                reason: {
                    'count': count,
                    'percentage': (count / total_reasons) * 100
                }
                for reason, count in reason_counts.most_common()
            }

            # Top reasons by city
            city_reasons = {}
            for city in data['city'].unique():
                city_data = data[data['city'] == city]
                city_reasons_list = []
                for reasons in city_data['migration_reasons'].dropna():
                    if isinstance(reasons, list):
                        city_reasons_list.extend(reasons)

                if city_reasons_list:
                    city_reason_counts = Counter(city_reasons_list)
                    city_reasons[city] = {
                        'top_reasons': dict(city_reason_counts.most_common(3)),
                        'total_reasons': len(city_reasons_list)
                    }

            stats_dict['migration_reasons']['by_city'] = city_reasons

    # Continue with existing statistical calculations
    if 'growth_rate' in data.columns and not data.empty:
        stats_dict['growth_rate'] = data['growth_rate'].mean()

        latest_year = data['year'].max() if 'year' in data else 0
        previous_year = latest_year - 1

        latest_rate = data[data['year'] == latest_year]['growth_rate'].mean() if not data[data['year'] == latest_year].empty else 0
        previous_rate = data[data['year'] == previous_year]['growth_rate'].mean() if not data[data['year'] == previous_year].empty else 0

        if not np.isnan(latest_rate) and not np.isnan(previous_rate):
            stats_dict['growth_rate_change'] = latest_rate - previous_rate
    else:
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
