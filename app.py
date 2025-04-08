import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
from scraper import scrape_population_data, load_cached_data
from data_processor import process_data, calculate_statistics
from visualizer import create_flow_map, create_trend_chart, create_comparison_chart
from utils import get_guangdong_cities
from translations import get_translation, LANGUAGES

# Set page configuration
st.set_page_config(
    page_title="Guangdong Population Flow Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

# Function to get translated text
def t(key):
    return get_translation(key, st.session_state.language)

# Function to toggle language
def toggle_language():
    st.session_state.language = 'zh' if st.session_state.language == 'en' else 'en'
    st.rerun()

# Cache data loading function
@st.cache_data(ttl=3600)
def load_data():
    """Load data with caching to improve performance"""
    try:
        # First try to load cached data
        data = load_cached_data()
        if data is None or data.empty:
            # If no cached data, scrape fresh data
            with st.spinner(t('loading_data')):
                data = scrape_population_data()
        return data
    except Exception as e:
        st.error(f"{t('data_load_error')}: {str(e)}")
        return pd.DataFrame()

# Sidebar for controls
with st.sidebar:
    # Language toggle
    st.button(
        "🌐 " + ("English" if st.session_state.language == 'zh' else "中文"), 
        on_click=toggle_language
    )
    
    st.title(t('sidebar_title'))
    
    # Data refresh button
    if st.button(t('refresh_data')):
        st.cache_data.clear()
        st.rerun()
    
    # City selection
    cities = get_guangdong_cities()
    selected_cities = st.multiselect(
        t('select_cities'),
        options=cities,
        default=cities[:5]  # Default to first 5 cities
    )
    
    # Time period selection
    time_periods = ["2018-2022", "2013-2017", "2008-2012"]
    selected_period = st.selectbox(t('select_time_period'), time_periods)
    
    # Analysis type
    analysis_type = st.radio(
        t('analysis_type'),
        [t('population_inflow'), t('population_outflow'), t('net_migration')]
    )
    
    # Advanced options
    with st.expander(t('advanced_options')):
        normalize_data = st.checkbox(t('normalize_data'), value=False)
        show_trend_lines = st.checkbox(t('show_trend_lines'), value=True)
        confidence_interval = st.slider(t('confidence_interval'), 80, 99, 95)

# Main content
st.title(t('main_title'))
st.markdown(t('main_description'))

# Check if we're using the uploaded XLS file
xls_file_path = "data/liudongrenkou.xls"
if os.path.exists(xls_file_path):
    st.info(t('using_xls_data'))

# Load and process data
data = load_data()

if data is not None and not data.empty:
    # Process data based on selections
    processed_data = process_data(data, selected_cities, selected_period, analysis_type)
    
    # Calculate statistics
    stats = calculate_statistics(processed_data, confidence_interval/100)
    
    # Display main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t('total_population'), f"{stats['total_population']:,}")
    with col2:
        st.metric(t('avg_annual_flow'), f"{stats['avg_annual_flow']:,.0f}")
    with col3:
        st.metric(t('growth_rate'), f"{stats['growth_rate']:.2f}%", 
                 delta=f"{stats['growth_rate_change']:.2f}%" if 'growth_rate_change' in stats else None)
    
    # Main visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        t('population_flow_map'), 
        t('trend_analysis'), 
        t('city_comparison'),
        t('statistical_data')
    ])
    
    with tab1:
        st.subheader(t('population_flow_map_title'))
        flow_map = create_flow_map(processed_data, selected_cities, analysis_type)
        st.plotly_chart(flow_map, use_container_width=True)
    
    with tab2:
        st.subheader(t('trend_analysis_title'))
        trend_chart = create_trend_chart(processed_data, show_trend_lines, normalize_data)
        st.plotly_chart(trend_chart, use_container_width=True)
    
    with tab3:
        st.subheader(t('city_comparison_title'))
        comparison_chart = create_comparison_chart(processed_data, selected_cities)
        st.plotly_chart(comparison_chart, use_container_width=True)
    
    with tab4:
        st.subheader(t('statistical_data_title'))
        st.dataframe(processed_data, use_container_width=True)
        
        # Download options
        st.download_button(
            label=t('download_csv'),
            data=processed_data.to_csv(index=False).encode('utf-8'),
            file_name=f"guangdong_population_data_{selected_period}.csv",
            mime='text/csv'
        )
        
        # For Excel download, we need to use BytesIO
        from io import BytesIO
        excel_buffer = BytesIO()
        processed_data.to_excel(excel_buffer, index=False)
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label=t('download_excel'),
            data=excel_data,
            file_name=f"guangdong_population_data_{selected_period}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Display statistical summary
        st.subheader(t('statistical_summary'))
        st.json(stats)
        
else:
    st.error(t('no_data_error'))
    st.info(t('try_refresh'))

# Footer
st.markdown("---")
st.markdown(t('footer_text'))
