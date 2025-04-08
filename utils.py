import json
import os
import re
import pandas as pd
import numpy as np

def get_guangdong_cities():
    """
    Get list of major cities in Guangdong Province
    
    Returns:
        list: List of city names in Chinese
    """
    # Load cities from the JSON file if it exists
    cities_file = "assets/guangdong_cities.json"
    if os.path.exists(cities_file):
        try:
            with open(cities_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Default list of cities in Guangdong Province
    cities = [
        "广州市", "深圳市", "佛山市", "东莞市", "珠海市", 
        "中山市", "惠州市", "江门市", "肇庆市", "茂名市",
        "湛江市", "汕头市", "揭阳市", "梅州市", "汕尾市",
        "河源市", "韶关市", "清远市", "云浮市", "阳江市",
        "潮州市"
    ]
    
    # Save to JSON for future use
    os.makedirs("assets", exist_ok=True)
    with open(cities_file, 'w', encoding='utf-8') as f:
        json.dump(cities, f, ensure_ascii=False)
    
    return cities

def extract_year_range(time_period):
    """
    Extract start and end years from a time period string
    
    Args:
        time_period (str): Time period in format "YYYY-YYYY"
        
    Returns:
        tuple: (start_year, end_year)
    """
    match = re.match(r'(\d{4})-(\d{4})', time_period)
    if match:
        start_year, end_year = map(int, match.groups())
        return start_year, end_year
    else:
        # Default to last 5 years if format is invalid
        current_year = 2022  # Using fixed year for stability
        return current_year - 5, current_year

def calculate_migration_efficiency(inflow, outflow):
    """
    Calculate migration efficiency index
    
    Args:
        inflow (float): Population inflow
        outflow (float): Population outflow
        
    Returns:
        float: Migration efficiency index (-1 to 1)
    """
    if inflow + outflow == 0:
        return 0
    
    return (inflow - outflow) / (inflow + outflow)

def calculate_migration_impact(migration, population):
    """
    Calculate migration impact index
    
    Args:
        migration (float): Net migration
        population (float): Total population
        
    Returns:
        float: Migration impact index
    """
    if population == 0:
        return 0
    
    return (migration / population) * 100  # As percentage

def forecast_population(data, years_ahead=5):
    """
    Forecast population for future years using linear regression
    
    Args:
        data (DataFrame): Historical population data
        years_ahead (int): Number of years to forecast
        
    Returns:
        DataFrame: Forecast data
    """
    if data.empty or 'year' not in data or 'population' not in data:
        return pd.DataFrame()
    
    forecasts = []
    
    for city in data['city'].unique():
        city_data = data[data['city'] == city].sort_values('year')
        
        if len(city_data) > 1:  # Need at least two points for regression
            # Prepare data for regression
            x = city_data['year'].values.reshape(-1, 1)
            y = city_data['population'].values
            
            # Simple linear regression
            coefficients = np.polyfit(x.flatten(), y, 1)
            slope, intercept = coefficients
            
            # Forecast future years
            last_year = city_data['year'].max()
            for i in range(1, years_ahead + 1):
                forecast_year = last_year + i
                forecast_population = intercept + slope * forecast_year
                
                forecasts.append({
                    'city': city,
                    'year': forecast_year,
                    'population': forecast_population,
                    'is_forecast': True
                })
    
    if not forecasts:
        return pd.DataFrame()
    
    forecast_df = pd.DataFrame(forecasts)
    
    # Add confidence intervals
    forecast_df['lower_bound'] = forecast_df['population'] * 0.95  # Simple 5% lower bound
    forecast_df['upper_bound'] = forecast_df['population'] * 1.05  # Simple 5% upper bound
    
    return forecast_df
