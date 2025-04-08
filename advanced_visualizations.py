import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from scipy import stats

def create_population_pie_chart(data, selected_cities):
    """
    Create a pie chart showing population distribution among selected cities
    
    Args:
        data (DataFrame): Processed population data
        selected_cities (list): List of selected cities
        
    Returns:
        Figure: Plotly figure object with the pie chart
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Get the latest year's data for each city
    latest_data = data.loc[data.groupby('city')['year'].idxmax()]
    
    # Filter for selected cities
    city_data = latest_data[latest_data['city'].isin(selected_cities)]
    
    if city_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No population data available for selected cities",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Sort by population (largest to smallest)
    city_data = city_data.sort_values('population', ascending=False)
    
    # Create a colorful pie chart with detailed hover info
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=city_data['city'],
        values=city_data['population'],
        textinfo='label+percent',
        insidetextorientation='radial',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Population: %{value:,}<br>Share: %{percent}<extra></extra>',
        marker=dict(
            colors=px.colors.qualitative.Plotly,
            line=dict(color='white', width=2)
        ),
        rotation=90,
        hole=0.3,
        pull=[0.05 if i < 3 else 0 for i in range(len(city_data))],  # Pull out the top 3 cities
    ))
    
    # Add an annotation in the center
    latest_year = city_data['year'].max()
    total_population = city_data['population'].sum()
    
    fig.update_layout(
        title={
            'text': f'Population Distribution ({latest_year})',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20)
        },
        annotations=[
            dict(
                text=f'Total<br>{int(total_population):,}',
                x=0.5,
                y=0.5,
                font=dict(size=16),
                showarrow=False
            )
        ],
        height=550,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.1,
            font=dict(size=12)
        ),
        margin=dict(t=80, b=40, l=40, r=150)
    )
    
    return fig

def create_growth_bar_chart(data, selected_cities):
    """
    Create a horizontal bar chart showing population growth rates
    
    Args:
        data (DataFrame): Processed population data
        selected_cities (list): List of selected cities
        
    Returns:
        Figure: Plotly figure object with the bar chart
    """
    if data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Calculate growth rate for each city across years
    growth_data = []
    
    for city in selected_cities:
        city_data = data[data['city'] == city]
        
        if len(city_data) > 1:
            # Get data for first and last year
            first_year_data = city_data.loc[city_data['year'].idxmin()]
            last_year_data = city_data.loc[city_data['year'].idxmax()]
            
            # Calculate CAGR (Compound Annual Growth Rate)
            years_diff = last_year_data['year'] - first_year_data['year']
            if years_diff > 0:
                starting_population = first_year_data['population']
                ending_population = last_year_data['population']
                
                if starting_population > 0:
                    cagr = ((ending_population / starting_population) ** (1 / years_diff) - 1) * 100
                    
                    growth_data.append({
                        'city': city,
                        'growth_rate': cagr,
                        'start_year': first_year_data['year'],
                        'end_year': last_year_data['year'],
                        'start_population': starting_population,
                        'end_population': ending_population,
                        'years': years_diff
                    })
    
    growth_df = pd.DataFrame(growth_data)
    
    if growth_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data to calculate growth rates",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Sort by growth rate (descending)
    growth_df = growth_df.sort_values('growth_rate', ascending=False)
    
    # Create color scale - gradient from red to blue
    colors = []
    for rate in growth_df['growth_rate']:
        if rate >= 0:
            # Positive growth: blue (darker for higher growth)
            intensity = min(255, 100 + int(rate * 15))
            colors.append(f'rgba(65, 105, {intensity}, 0.8)')
        else:
            # Negative growth: red (darker for more negative)
            intensity = min(255, 100 + int(abs(rate) * 15))
            colors.append(f'rgba({intensity}, 20, 60, 0.8)')
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=growth_df['growth_rate'],
        y=growth_df['city'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(50, 50, 50, 0.5)', width=1)
        ),
        text=[f"{rate:.2f}%" for rate in growth_df['growth_rate']],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Growth Rate: %{x:.2f}%<br>" +
            "Period: %{customdata[0]}-" +
            "%{customdata[1]} " +
            "(%{customdata[2]} years)<br>" +
            "Population Change: %{customdata[3]:,} → %{customdata[4]:,}" +
            "<extra></extra>"
        ),
        customdata=growth_df[['start_year', 'end_year', 'years', 'start_population', 'end_population']].values
    ))
    
    # Add a vertical line at zero
    fig.add_shape(
        type="line",
        x0=0, y0=-0.5,
        x1=0, y1=len(growth_df) - 0.5,
        line=dict(color="black", width=1, dash="dash")
    )
    
    # Update layout
    period_range = f"{growth_df['start_year'].min()}-{growth_df['end_year'].max()}"
    
    fig.update_layout(
        title={
            'text': f'Population Growth Rate by City ({period_range})',
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        xaxis_title={
            'text': 'Annual Growth Rate (%)',
            'font': dict(size=14)
        },
        yaxis_title={
            'text': 'City',
            'font': dict(size=14)
        },
        height=max(400, 100 + len(growth_df) * 30),  # Dynamic height based on number of cities
        margin=dict(l=20, r=20, t=80, b=60),
        xaxis=dict(
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            gridcolor='rgba(230,230,230,0.8)',
        ),
        yaxis=dict(
            autorange="reversed",  # Highest value at the top
            categoryorder='total ascending'
        ),
        plot_bgcolor='rgba(250,250,250,0.9)',
    )
    
    # Add annotation for the time period
    fig.add_annotation(
        text=f"Compound Annual Growth Rate (CAGR) over {period_range}",
        x=0.5,
        y=-0.15,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=12, color="gray")
    )
    
    return fig

def create_population_dashboard(data, selected_cities):
    """
    Create a dashboard with multiple visualizations in one figure
    
    Args:
        data (DataFrame): Processed population data
        selected_cities (list): List of selected cities
        
    Returns:
        Figure: Plotly figure object with multiple charts
    """
    if data.empty or not selected_cities:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected criteria",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Create a figure with subplots - 2 rows, 2 columns
    fig = make_subplots(
        rows=2, 
        cols=2,
        specs=[
            [{"type": "pie"}, {"type": "bar"}],
            [{"type": "scatter", "colspan": 2}, None]
        ],
        subplot_titles=(
            "Population Distribution", 
            "Annual Growth Rate (%)",
            "Population Trends Over Time"
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    # Latest year data for pie chart
    latest_data = data.loc[data.groupby('city')['year'].idxmax()]
    latest_data = latest_data[latest_data['city'].isin(selected_cities)]
    latest_data = latest_data.sort_values('population', ascending=False)
    
    if not latest_data.empty:
        # 1. Pie chart - top right
        fig.add_trace(
            go.Pie(
                labels=latest_data['city'],
                values=latest_data['population'],
                textinfo='percent',
                hovertemplate='<b>%{label}</b><br>Population: %{value:,}<br>Share: %{percent}<extra></extra>',
                marker=dict(colors=px.colors.qualitative.Plotly),
                showlegend=True
            ),
            row=1, col=1
        )
        
        # 2. Growth rate bars - top right
        growth_data = []
        for city in selected_cities:
            city_data = data[data['city'] == city]
            
            if len(city_data) > 1:
                first_year_data = city_data.loc[city_data['year'].idxmin()]
                last_year_data = city_data.loc[city_data['year'].idxmax()]
                
                years_diff = last_year_data['year'] - first_year_data['year']
                if years_diff > 0 and first_year_data['population'] > 0:
                    cagr = ((last_year_data['population'] / first_year_data['population']) ** (1 / years_diff) - 1) * 100
                    
                    growth_data.append({
                        'city': city,
                        'growth_rate': cagr
                    })
        
        growth_df = pd.DataFrame(growth_data)
        
        if not growth_df.empty:
            growth_df = growth_df.sort_values('growth_rate', ascending=False)
            
            # Determine colors based on rates
            colors = []
            for rate in growth_df['growth_rate']:
                if rate >= 0:
                    colors.append('rgba(65, 105, 225, 0.8)')  # Blue for positive growth
                else:
                    colors.append('rgba(220, 20, 60, 0.8)')   # Red for negative growth
            
            fig.add_trace(
                go.Bar(
                    x=growth_df['city'],
                    y=growth_df['growth_rate'],
                    marker_color=colors,
                    text=[f"{rate:.2f}%" for rate in growth_df['growth_rate']],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Growth Rate: %{y:.2f}%<extra></extra>',
                    showlegend=False
                ),
                row=1, col=2
            )
            
            # Add horizontal line at zero for growth rates
            fig.add_shape(
                type="line",
                x0=-0.5, x1=len(growth_df) - 0.5,
                y0=0, y1=0,
                line=dict(color="black", width=1, dash="dash"),
                row=1, col=2
            )
        
        # 3. Population trends - bottom
        for city in selected_cities:
            city_data = data[data['city'] == city].sort_values('year')
            
            if not city_data.empty:
                fig.add_trace(
                    go.Scatter(
                        x=city_data['year'],
                        y=city_data['population'],
                        mode='lines+markers',
                        name=city,
                        line=dict(width=2),
                        hovertemplate=(
                            "<b>%{data.name}</b><br>" +
                            "Year: %{x}<br>" +
                            "Population: %{y:,}<extra></extra>"
                        )
                    ),
                    row=2, col=1
                )
    
    # Update layout
    fig.update_layout(
        height=800,
        title={
            'text': 'Population Analysis Dashboard',
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=120, b=60, l=60, r=60)
    )
    
    # Update axes
    fig.update_xaxes(title_text="City", row=1, col=2, tickangle=45, categoryorder='array', categoryarray=growth_df['city'] if 'growth_df' in locals() else None)
    fig.update_yaxes(title_text="Growth Rate (%)", row=1, col=2)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Population", row=2, col=1)
    
    return fig