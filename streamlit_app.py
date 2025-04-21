"""
Streamlit Cloud entry point for the Guangdong Population Flow Analysis application.
This file serves as the main entry point for Streamlit Cloud deployment.
"""

import streamlit as st
import pandas as pd
# Import functions from local modules
from data_processor import process_data, calculate_statistics
from scraper import scrape_population_data

# Define load_data function to match app.py
def load_data():
    """Load population data from various sources"""
    return scrape_population_data(use_synthetic=True)
from visualizer import create_flow_map, create_trend_chart, create_comparison_chart
from advanced_visualizations import create_population_pie_chart, create_growth_bar_chart, create_population_dashboard
from utils import get_guangdong_cities
from translations import get_translation, LANGUAGES
import time
import asyncio

# Page config
st.set_page_config(
    page_title="Guangdong Population Flow Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'data' not in st.session_state:
    st.session_state.data = None
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def t(key):
    """Get translated text"""
    return get_translation(key, st.session_state.language)

# Sidebar
with st.sidebar:
    # Language selector
    lang = st.selectbox(
        "Language/语言",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language)
    )
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()

    st.title(t('sidebar_title'))

    # Data loading with progress
    if not st.session_state.data_loaded:
        with st.spinner(t('loading_data')):
            data = load_data()
            if data is not None and not data.empty:
                st.session_state.data = data
                st.session_state.data_loaded = True
                st.success(t('data_loaded_success'))
            else:
                st.error(t('no_data_error'))
                st.info(t('try_refresh'))

    # City selection
    st.subheader(t('select_cities'))
    cities = get_guangdong_cities()

    # Add select all/none buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('select_all'), use_container_width=True):
            st.session_state.selected_cities = cities
    with col2:
        if st.button(t('select_none'), use_container_width=True):
            st.session_state.selected_cities = []

    # City filter
    city_filter = st.text_input(t('filter_cities'))
    filtered_cities = [city for city in cities if city_filter.lower() in city.lower()]

    # City multiselect
    selected_cities = st.multiselect(
        t('available_cities'),
        options=filtered_cities,
        default=filtered_cities[:5] if 'selected_cities' not in st.session_state else st.session_state.selected_cities
    )
    st.session_state.selected_cities = selected_cities

    # Time period selection
    time_periods = ["2018-2024", "2013-2017", "2008-2012"]
    selected_period = st.selectbox(t('select_time_period'), time_periods)

    # Analysis type
    analysis_type = st.radio(
        t('analysis_type'),
        [t('population_inflow'), t('population_outflow'), t('net_migration')]
    )

# Main content
st.title(t('main_title'))
st.markdown(t('main_description'))

if st.session_state.data_loaded and st.session_state.data is not None:
    # Process data with loading indicator
    with st.spinner(t('processing_data')):
        processed_data = process_data(
            st.session_state.data,
            selected_cities,
            selected_period,
            analysis_type
        )

        # Calculate statistics
        stats = calculate_statistics(processed_data)

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            t('total_population'),
            f"{int(stats['total_population']):,}"
        )
    with col2:
        st.metric(
            t('avg_annual_flow'),
            f"{int(stats['avg_annual_flow']):,}"
        )
    with col3:
        st.metric(
            t('growth_rate'),
            f"{stats['growth_rate']:.2f}%",
            delta=f"{stats.get('growth_rate_change', 0):.2f}%"
        )

    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        t('population_flow_map'),
        t('trend_analysis'),
        t('city_comparison'),
        t('growth_analysis'),
        t('dashboard'),
        t('migration_reasons')
    ])

    with tab1:
        with st.spinner(t('generating_map')):
            flow_map = create_flow_map(processed_data, selected_cities, analysis_type)
            st.plotly_chart(flow_map, use_container_width=True)

    with tab2:
        with st.spinner(t('analyzing_trends')):
            trend_chart = create_trend_chart(processed_data)
            st.plotly_chart(trend_chart, use_container_width=True)

    with tab3:
        with st.spinner(t('comparing_cities')):
            comparison_chart = create_comparison_chart(processed_data, selected_cities)
            st.plotly_chart(comparison_chart, use_container_width=True)

    with tab4:
        with st.spinner(t('analyzing_growth')):
            growth_chart = create_growth_bar_chart(processed_data, selected_cities)
            st.plotly_chart(growth_chart, use_container_width=True)

    with tab5:
        with st.spinner(t('creating_dashboard')):
            dashboard = create_population_dashboard(processed_data, selected_cities)
            st.plotly_chart(dashboard, use_container_width=True)

    with tab6:
        st.subheader(t('migration_reasons_title'))

        if 'migration_reasons' in processed_data.columns:
            # Create subtabs for different visualizations
            reason_tab1, reason_tab2, reason_tab3, reason_tab4 = st.tabs([
                t('reason_distribution'),
                t('reason_sankey'),
                t('reason_heatmap'),
                t('reason_timeline')
            ])

            with reason_tab1:
                # Overall distribution
                st.write(t('overall_distribution'))

                # Import visualization functions
                from reason_visualizations import create_reason_treemap
                with st.spinner("Creating treemap visualization..."):
                    treemap_fig = create_reason_treemap(processed_data)
                    if treemap_fig:
                        st.plotly_chart(treemap_fig, use_container_width=True)

            with reason_tab2:
                # Sankey diagram
                from reason_visualizations import create_reason_sankey
                with st.spinner("Creating sankey diagram..."):
                    sankey_fig = create_reason_sankey(processed_data)
                    if sankey_fig:
                        st.plotly_chart(sankey_fig, use_container_width=True)

            with reason_tab3:
                # Heatmap visualization
                from reason_visualizations import create_reason_heatmap
                with st.spinner("Creating heatmap visualization..."):
                    heatmap_fig = create_reason_heatmap(processed_data)
                    if heatmap_fig:
                        st.plotly_chart(heatmap_fig, use_container_width=True)

            with reason_tab4:
                # Timeline visualization
                from reason_visualizations import create_reason_timeline
                with st.spinner("Creating timeline visualization..."):
                    timeline_fig = create_reason_timeline(processed_data)
                    if timeline_fig:
                        st.plotly_chart(timeline_fig, use_container_width=True)
        else:
            st.info("No migration reasons data available. Please ensure your data includes migration reasons information.")

    # Data export options
    st.subheader(t('export_data'))
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            t('download_csv'),
            data=processed_data.to_csv(index=False).encode('utf-8'),
            file_name=f"guangdong_population_data_{selected_period}.csv",
            mime='text/csv'
        )
    with col2:
        excel_buffer = pd.ExcelWriter(f"guangdong_population_data_{selected_period}.xlsx", engine='openpyxl')
        processed_data.to_excel(excel_buffer, index=False)
        excel_buffer.close()

        with open(f"guangdong_population_data_{selected_period}.xlsx", 'rb') as f:
            st.download_button(
                t('download_excel'),
                data=f,
                file_name=f"guangdong_population_data_{selected_period}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    # Display statistical summary
    with st.expander(t('statistical_summary')):
        st.json(stats)

else:
    st.warning(t('please_load_data'))
