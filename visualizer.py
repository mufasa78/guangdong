import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats

def create_flow_map(data, selected_cities, analysis_type):
    """
    Create a choropleth map showing population flow in Guangdong Province
    
    Args:
        data (DataFrame): Processed population data
        selected_cities (list): List of selected cities
        analysis_type (str): Type of analysis to perform
        
    Returns:
        Figure: Plotly figure object with the map
    """
    # Create city coordinates - approximate values for Guangdong cities
    city_coordinates = {
        "广州市": [113.2644, 23.1291],
        "深圳市": [114.0579, 22.5431],
        "佛山市": [113.1231, 23.0229],
        "东莞市": [113.7518, 23.0209],
        "珠海市": [113.5762, 22.2701],
        "中山市": [113.3922, 22.5176],
        "惠州市": [114.4161, 23.1133],
        "江门市": [113.0781, 22.5903],
        "肇庆市": [112.4709, 23.0466],
        "茂名市": [110.9254, 21.6618],
        "湛江市": [110.3594, 21.2707],
        "汕头市": [116.6827, 23.3535],
        "揭阳市": [116.3722, 23.5498],
        "梅州市": [116.1187, 24.3045],
        "汕尾市": [115.3729, 22.7713],
        "河源市": [114.6978, 23.7462],
        "韶关市": [113.5972, 24.8011],
        "清远市": [113.0507, 23.6821],
        "云浮市": [112.0441, 22.9138],
        "阳江市": [111.9755, 21.8589],
        "潮州市": [116.6323, 23.6618]
    }
    
    # Prepare data for map
    map_data = []
    
    if not data.empty:
        # Get the latest year's data for each city
        latest_data = data.loc[data.groupby('city')['year'].idxmax()]
        
        for _, row in latest_data.iterrows():
            city = row['city']
            if city in city_coordinates and city in selected_cities:
                coords = city_coordinates[city]
                
                # Determine value based on analysis type
                if 'analysis_value' in row:
                    value = row['analysis_value']
                elif "inflow" in analysis_type.lower():
                    value = row['change'] if row.get('flow_type') == 'inflow' else 0
                elif "outflow" in analysis_type.lower():
                    value = -row['change'] if row.get('flow_type') == 'outflow' else 0
                else:  # Net migration
                    value = row['change']
                
                map_data.append({
                    'city': city,
                    'lat': coords[1],
                    'lon': coords[0],
                    'value': value,
                    'population': row['population'],
                    'year': row['year']
                })
    
    # Create a DataFrame for the map
    map_df = pd.DataFrame(map_data)
    
    # If no data, return empty figure
    if map_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create the map
    # Get max absolute value for symmetric color scale
    max_abs_value = max(abs(map_df['value'].max()), abs(map_df['value'].min())) if not map_df.empty else 0
    
    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="population",
        size_max=40,
        color="value",
        color_continuous_scale="RdBu_r",  # Red for outflow, blue for inflow
        range_color=[-max_abs_value, max_abs_value],
        hover_name="city",
        hover_data={
            "lat": False,
            "lon": False,
            "value": True,
            "population": True,
            "year": True
        },
        zoom=6,
        center={"lat": 23.3, "lon": 113.5},  # Center on Guangdong Province
        mapbox_style="carto-positron"
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title="Population Change"
        )
    )
    
    return fig

def create_trend_chart(data, show_trend_lines=True, normalize_data=False):
    """
    Create a line chart showing population trends over time
    
    Args:
        data (DataFrame): Processed population data
        show_trend_lines (bool): Whether to show trend lines
        normalize_data (bool): Whether to normalize data for comparison
        
    Returns:
        Figure: Plotly figure object with the chart
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Prepare data for the chart
    if normalize_data:
        # Normalize to percentage of initial value
        normalized_data = []
        for city in data['city'].unique():
            city_data = data[data['city'] == city].sort_values('year')
            if len(city_data) > 0:
                initial_value = city_data['population'].iloc[0]
                city_data = city_data.copy()
                city_data['normalized_population'] = city_data['population'] / initial_value * 100
                normalized_data.append(city_data)
        
        if normalized_data:
            chart_data = pd.concat(normalized_data)
            y_column = 'normalized_population'
            y_title = 'Population (% of initial value)'
        else:
            chart_data = data
            y_column = 'population'
            y_title = 'Population'
    else:
        chart_data = data
        y_column = 'population'
        y_title = 'Population'
    
    # Create the basic line chart
    hover_data = ['change']
    if 'growth_rate' in chart_data.columns:
        hover_data.append('growth_rate')
        
    fig = px.line(
        chart_data, 
        x='year', 
        y=y_column,
        color='city',
        markers=True,
        hover_data=hover_data,
        title='Population Trends by City'
    )
    
    # Add trend lines if requested
    if show_trend_lines:
        for city in chart_data['city'].unique():
            city_data = chart_data[chart_data['city'] == city].sort_values('year')
            
            if len(city_data) > 1:  # Need at least two points for regression
                x = city_data['year'].values
                y = city_data[y_column].values
                
                # Fit a linear regression line
                slope, intercept, r_value, _, _ = stats.linregress(x, y)
                
                # Generate points for the trend line
                x_trend = np.array([city_data['year'].min(), city_data['year'].max()])
                y_trend = intercept + slope * x_trend
                
                # Add the trend line to the figure
                fig.add_trace(
                    go.Scatter(
                        x=x_trend,
                        y=y_trend,
                        mode='lines',
                        name=f'{city} Trend (r={r_value:.2f})',
                        line=dict(dash='dash', width=1),
                        opacity=0.7,
                        showlegend=False,
                        hoverinfo='skip'
                    )
                )
    
    # Update layout
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title=y_title,
        height=500,
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_comparison_chart(data, selected_cities):
    """
    Create a bar chart comparing cities based on population flows
    
    Args:
        data (DataFrame): Processed population data
        selected_cities (list): List of selected cities
        
    Returns:
        Figure: Plotly figure object with the chart
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Calculate net migration for each city across all years
    comparison_data = []
    
    for city in selected_cities:
        city_data = data[data['city'] == city]
        
        if not city_data.empty:
            total_population = city_data['population'].iloc[-1]  # Latest population
            net_migration = city_data['change'].sum()
            
            # Check if growth_rate column exists
            if 'growth_rate' in city_data.columns:
                growth_rate = city_data['growth_rate'].mean()
            else:
                # Calculate simple growth rate
                growth_rate = (net_migration / total_population) * 100 if total_population > 0 else 0
            
            comparison_data.append({
                'city': city,
                'total_population': total_population,
                'net_migration': net_migration,
                'growth_rate': growth_rate
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    if comparison_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No comparison data available",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Sort by net migration
    comparison_df = comparison_df.sort_values('net_migration', ascending=False)
    
    # Create a bar chart with net migration
    fig = px.bar(
        comparison_df,
        x='city',
        y='net_migration',
        color='growth_rate',
        color_continuous_scale='RdYlBu',
        hover_data=['total_population', 'growth_rate'],
        title='Net Population Migration by City'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title='City',
        yaxis_title='Net Migration',
        coloraxis_colorbar=dict(title='Growth Rate (%)'),
        height=500
    )
    
    # Add a horizontal line at zero
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(comparison_df) - 0.5,
        y0=0,
        y1=0,
        line=dict(color='black', width=1, dash='dash')
    )
    
    return fig
