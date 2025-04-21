import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_reason_sankey(data):
    """
    Create a Sankey diagram showing flow of population between cities and their reasons
    """
    if 'migration_reasons' not in data.columns:
        return None

    # Process data for Sankey diagram
    cities = data['city'].unique()
    all_reasons = set()
    for reasons in data['migration_reasons'].dropna():
        if isinstance(reasons, list) and len(reasons) > 0:
            all_reasons.update(reasons)

    if not all_reasons:
        return None

    # Create nodes
    nodes = list(cities) + list(all_reasons)
    node_indices = {node: idx for idx, node in enumerate(nodes)}

    # Create links
    links = []

    for _, row in data.iterrows():
        reasons = row['migration_reasons']
        if isinstance(reasons, list) and len(reasons) > 0:
            city = row['city']
            population_change = abs(row['change']) if pd.notna(row['change']) else 0

            # Distribute population change among reasons
            value_per_reason = population_change / len(reasons)
            for reason in reasons:
                links.append({
                    'source': node_indices[city],
                    'target': node_indices[reason],
                    'value': value_per_reason
                })

    if not links:
        return None

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=["rgba(31, 119, 180, 0.8)"]*len(cities) +
                  ["rgba(255, 127, 14, 0.8)"]*len(all_reasons)
        ),
        link=dict(
            source=[link['source'] for link in links],
            target=[link['target'] for link in links],
            value=[link['value'] for link in links]
        )
    )])

    fig.update_layout(
        title="Population Flow by Migration Reasons",
        font=dict(size=10),
        height=800
    )

    return fig

def create_reason_heatmap(data):
    """
    Create a heatmap showing correlation between cities and migration reasons
    """
    if 'migration_reasons' not in data.columns:
        return None

    # Process data for heatmap
    cities = data['city'].unique()
    all_reasons = set()
    for reasons in data['migration_reasons'].dropna():
        if isinstance(reasons, list) and len(reasons) > 0:
            all_reasons.update(reasons)

    if not all_reasons:
        return None

    # Create matrix
    matrix = np.zeros((len(cities), len(all_reasons)))
    reasons_list = list(all_reasons)

    for i, city in enumerate(cities):
        city_data = data[data['city'] == city]
        for _, row in city_data.iterrows():
            if isinstance(row['migration_reasons'], list) and len(row['migration_reasons']) > 0:
                for reason in row['migration_reasons']:
                    j = reasons_list.index(reason)
                    matrix[i, j] += 1

    # Normalize the matrix
    row_sums = matrix.sum(axis=1, keepdims=True)
    matrix = np.divide(matrix, row_sums, out=np.zeros_like(matrix), where=row_sums!=0) * 100

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=reasons_list,
        y=cities,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>'
    ))

    fig.update_layout(
        title="City-Reason Correlation Heatmap",
        xaxis_title="Migration Reasons",
        yaxis_title="Cities",
        height=800,
        xaxis={'tickangle': 45}
    )

    return fig

def create_reason_treemap(data):
    """
    Create a treemap showing hierarchical breakdown of migration reasons
    """
    if 'migration_reasons' not in data.columns:
        return None

    # Process data for treemap
    treemap_data = []

    for _, row in data.iterrows():
        city = row['city']
        reasons = row['migration_reasons']
        if isinstance(reasons, list) and len(reasons) > 0:
            population_change = abs(row['change']) if pd.notna(row['change']) else 0

            for reason in reasons:
                treemap_data.append({
                    'City': city,
                    'Reason': reason,
                    'Value': population_change / len(reasons)
                })

    if not treemap_data:
        return None

    df = pd.DataFrame(treemap_data)

    fig = px.treemap(
        df,
        path=['Reason', 'City'],
        values='Value',
        title='Hierarchical View of Migration Reasons'
    )

    fig.update_layout(height=800)

    return fig

def create_reason_timeline(data):
    """
    Create a timeline view of how migration reasons evolved
    """
    if 'migration_reasons' not in data.columns or 'year' not in data.columns:
        return None

    # Process data for timeline
    timeline_data = []

    for _, row in data.iterrows():
        year = row['year']
        if isinstance(row['migration_reasons'], list) and len(row['migration_reasons']) > 0:
            for reason in row['migration_reasons']:
                timeline_data.append({
                    'Year': year,
                    'Reason': reason,
                    'Count': 1
                })

    if not timeline_data:
        return None

    df = pd.DataFrame(timeline_data)
    df_grouped = df.groupby(['Year', 'Reason'])['Count'].sum().reset_index()

    # Calculate percentages for each year
    df_grouped['Total'] = df_grouped.groupby('Year')['Count'].transform('sum')
    df_grouped['Percentage'] = (df_grouped['Count'] / df_grouped['Total'] * 100).round(1)

    fig = px.line(
        df_grouped,
        x='Year',
        y='Percentage',
        color='Reason',
        title='Evolution of Migration Reasons Over Time',
        markers=True,
        hover_data={'Year': True, 'Percentage': ':.1f', 'Count': True}
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Percentage of Total Reasons (%)",
        height=600,
        hovermode='x unified',
        legend={'orientation': 'h', 'y': -0.2}
    )

    return fig

def create_reason_radar(data, city):
    """
    Create a radar chart showing reason profile for a specific city
    """
    if 'migration_reasons' not in data.columns:
        return None

    # Get data for specific city
    city_data = data[data['city'] == city]

    # Count reasons
    reason_counts = {}
    total_count = 0

    for _, row in city_data.iterrows():
        if isinstance(row['migration_reasons'], list) and len(row['migration_reasons']) > 0:
            for reason in row['migration_reasons']:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
                total_count += 1

    if not reason_counts or total_count == 0:
        return None

    # Calculate percentages
    categories = list(reason_counts.keys())
    values = [reason_counts[cat]/total_count * 100 for cat in categories]

    # Create radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=city,
        hovertemplate='<b>%{theta}</b><br>' +
                      'Percentage: %{r:.1f}%<br>' +
                      'Count: %{customdata}<extra></extra>',
        customdata=[reason_counts[cat] for cat in categories]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickformat='.0f',
                ticksuffix='%'
            )
        ),
        showlegend=True,
        title=f'Migration Reason Profile for {city}',
        height=600
    )

    return fig