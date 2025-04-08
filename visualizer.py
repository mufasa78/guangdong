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
    
    # Create a more detailed base map
    fig = go.Figure()
    
    # Add scatter mapbox for cities with population data
    fig.add_trace(go.Scattermapbox(
        lat=map_df['lat'],
        lon=map_df['lon'],
        mode='markers',
        marker=dict(
            size=map_df['population'].apply(lambda x: min(40, max(15, x/100000))),  # Scale by population
            color=map_df['value'],
            colorscale='RdBu_r',  # Red for outflow, blue for inflow
            cmin=-max_abs_value,
            cmax=max_abs_value,
            colorbar=dict(
                title="Population Flow",
                thickness=15,
                len=0.7,
                bgcolor='rgba(255,255,255,0.8)',
                borderwidth=0
            ),
            opacity=0.8,
            sizemode='diameter'
        ),
        text=map_df.apply(
            lambda row: f"<b>{row['city']}</b><br>" +
                      f"Population: {int(row['population']):,}<br>" +
                      f"Flow: {int(row['value']):+,}<br>" +
                      f"Year: {int(row['year'])}",
            axis=1
        ),
        hoverinfo='text',
        name='Cities'
    ))
    
    # For selected cities, add city names as text for better readability
    fig.add_trace(go.Scattermapbox(
        lat=map_df['lat'],
        lon=map_df['lon'],
        mode='text',
        text=map_df['city'],
        textfont=dict(
            family='Arial',
            size=12,
            color='black'
        ),
        textposition="bottom center",
        hoverinfo='none',
        name='City Labels'
    ))
    
    # Draw flow lines between major cities if we have multiple cities
    if len(map_df) > 1:
        # Find the city with highest inflow (center city)
        center_city = map_df.loc[map_df['value'].idxmax()]
        other_cities = map_df[map_df['city'] != center_city['city']]
        
        for _, city in other_cities.iterrows():
            # Only draw lines to/from cities with significant flow
            if abs(city['value']) > max_abs_value/10:
                # Line color based on flow direction
                line_color = 'rgba(65, 105, 225, 0.5)' if city['value'] > 0 else 'rgba(220, 20, 60, 0.5)'
                # Line width based on flow magnitude
                line_width = min(5, max(1, abs(city['value']) / max_abs_value * 5))
                
                fig.add_trace(go.Scattermapbox(
                    lat=[center_city['lat'], city['lat']],
                    lon=[center_city['lon'], city['lon']],
                    mode='lines',
                    line=dict(
                        width=line_width,
                        color=line_color
                    ),
                    opacity=0.7,
                    hoverinfo='none',
                    showlegend=False
                ))
    
    # Set up the mapbox layout
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",  # Light, detailed base map
            zoom=6.5,
            center={"lat": 23.3, "lon": 113.5},  # Center on Guangdong Province
        ),
        margin={"r":0, "t":0, "l":0, "b":0},
        legend=dict(
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            x=0.01,
            y=0.01
        )
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
    
    # Create a more detailed and visually appealing line chart
    fig = go.Figure()
    
    # Add a line and markers for each city
    for city in chart_data['city'].unique():
        city_data = chart_data[chart_data['city'] == city].sort_values('year')
        
        # Create hover text with detailed info
        hover_text = []
        for _, row in city_data.iterrows():
            hover_info = f"<b>{city}</b><br>"
            hover_info += f"Year: {int(row['year'])}<br>"
            hover_info += f"Population: {int(row[y_column]):,}<br>"
            hover_info += f"Change: {int(row['change']):+,}<br>"
            if 'growth_rate' in row:
                hover_info += f"Growth Rate: {row['growth_rate']:.2f}%"
            hover_text.append(hover_info)
        
        # Add line with custom styling
        fig.add_trace(go.Scatter(
            x=city_data['year'],
            y=city_data[y_column],
            mode='lines+markers',
            name=city,
            line=dict(
                width=3,
                shape='spline',  # Curved lines look better
            ),
            marker=dict(
                size=8,
                line=dict(
                    width=2,
                    color='white'
                )
            ),
            text=hover_text,
            hoverinfo='text'
        ))
    
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
    
    # Update layout with enhanced styling
    fig.update_layout(
        title={
            'text': 'Population Trends by City',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        xaxis_title={
            'text': 'Year',
            'font': dict(size=14)
        },
        yaxis_title={
            'text': y_title,
            'font': dict(size=14)
        },
        height=550,
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        plot_bgcolor='rgba(250,250,250,0.9)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(230,230,230,0.8)',
            tickmode='linear',
            dtick=1  # Show every year on the axis
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(230,230,230,0.8)',
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.2)',
            zerolinewidth=1
        ),
        margin=dict(l=60, r=30, t=80, b=60),
        annotations=[
            dict(
                text='Data Source: Combined from multiple sources including Excel file and web scraping',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=0.5,
                y=-0.15,
                font=dict(size=10, color='gray')
            )
        ]
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
    
    # Create a more detailed and enhanced comparison visualization
    fig = go.Figure()
    
    # Sort cities from highest to lowest net migration
    comparison_df = comparison_df.sort_values('net_migration', ascending=False)
    
    # Set color scale based on growth rates
    max_growth = max(abs(comparison_df['growth_rate'].max()), abs(comparison_df['growth_rate'].min()))
    
    # Add bars with custom styling and hover information
    for i, (_, row) in enumerate(comparison_df.iterrows()):
        # Determine bar color based on growth rate
        if row['growth_rate'] > 0:
            bar_color = f'rgba(65, 105, 225, {min(1.0, 0.4 + abs(row["growth_rate"]/max_growth*0.6))})'  # Blue for positive
        else:
            bar_color = f'rgba(220, 20, 60, {min(1.0, 0.4 + abs(row["growth_rate"]/max_growth*0.6))})'  # Red for negative
            
        hover_text = (
            f"<b>{row['city']}</b><br>" +
            f"Net Migration: {int(row['net_migration']):+,}<br>" +
            f"Growth Rate: {row['growth_rate']:.2f}%<br>" +
            f"Total Population: {int(row['total_population']):,}"
        )
        
        fig.add_trace(go.Bar(
            x=[row['city']],
            y=[row['net_migration']],
            name=row['city'],
            marker_color=bar_color,
            text=f"{int(row['net_migration']):+,}",
            textposition='auto',
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=False
        ))
    
    # Add a horizontal line at zero for reference
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(comparison_df) - 0.5,
        y0=0,
        y1=0,
        line=dict(color='black', width=1, dash='dash')
    )
    
    # Add annotations to show population size
    for i, (_, row) in enumerate(comparison_df.iterrows()):
        # Add a small dot above each bar indicating population size
        fig.add_trace(go.Scatter(
            x=[row['city']],
            y=[row['net_migration'] + (max(comparison_df['net_migration']) * 0.05)],
            mode='markers',
            marker=dict(
                size=row['total_population'] / 1000000 * 20,  # Size based on population (in millions)
                opacity=0.7,
                color='rgba(100,100,100,0.5)',
                line=dict(width=1, color='rgba(50,50,50,0.8)')
            ),
            name=f"{row['city']} Population",
            text=f"Population: {int(row['total_population']):,}",
            hoverinfo='text',
            showlegend=False
        ))
    
    # Update layout for better visualization
    fig.update_layout(
        title={
            'text': 'Net Population Migration by City',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='City',
        yaxis_title='Net Migration',
        height=600,
        barmode='group',
        bargap=0.2,
        bargroupgap=0.1,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            gridcolor='rgba(200,200,200,0.2)',
            zerolinecolor='rgba(0,0,0,0.2)'
        ),
        plot_bgcolor='rgba(250,250,250,0.9)',
        hovermode='closest',
        margin=dict(t=100, b=100)
    )
    
    # Add a color scale reference
    fig.add_annotation(
        x=1,
        y=1.05,
        xref="paper",
        yref="paper",
        text="Color intensity indicates growth rate",
        showarrow=False,
        font=dict(size=10),
        align="right"
    )
    
    return fig
