import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
from scraper import scrape_population_data, load_cached_data
from data_processor import process_data, calculate_statistics
from visualizer import create_flow_map, create_trend_chart, create_comparison_chart
from advanced_visualizations import create_population_pie_chart, create_growth_bar_chart, create_population_dashboard
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

# Split the data loading into two functions - one for caching the core functionality
# and another for handling UI elements

# This function is cached and contains no Streamlit UI elements
@st.cache_data(ttl=7200)  # Extended TTL to 2 hours for better performance
def _load_data_core(force_refresh=False):
    """
    Core data loading function (without UI elements) for caching

    Returns:
        tuple: (data, source_info, error_info)
    """
    try:
        # Track data sources successfully loaded
        data_sources = []
        source_labels = []
        errors = []

        # 1. Try to load from local cache first (fastest)
        cached_data = load_cached_data()
        if cached_data is not None and not cached_data.empty:
            data_sources.append(cached_data)
            source_labels.append("Cache")

        # 2. Try loading from the XLS file
        try:
            from scraper import load_xls_data
            xls_data = load_xls_data()
            if not xls_data.empty:
                data_sources.append(xls_data)
                source_labels.append("Excel")
        except Exception as e:
            errors.append(f"XLS loading error: {str(e)}")

        # 3. If still no data or force_refresh, scrape from web sources
        if not data_sources or force_refresh:
            # Only scrape the necessary parts to avoid unnecessary web requests
            from scraper import scrape_bl_gov_cn, scrape_stats_gd_gov_cn, scrape_supplementary_sources

            # Try each source independently to ensure we get as much data as possible
            try:
                bl_data = scrape_bl_gov_cn()
                if not bl_data.empty:
                    data_sources.append(bl_data)
                    source_labels.append("Government")
            except Exception as e:
                errors.append(f"Error scraping bl.gov.cn: {str(e)}")

            try:
                stats_data = scrape_stats_gd_gov_cn()
                if not stats_data.empty:
                    data_sources.append(stats_data)
                    source_labels.append("Statistics")
            except Exception as e:
                errors.append(f"Error scraping stats.gd.gov.cn: {str(e)}")

            try:
                supp_data = scrape_supplementary_sources()
                if not supp_data.empty:
                    data_sources.append(supp_data)
                    source_labels.append("Supplementary")
            except Exception as e:
                errors.append(f"Error scraping supplementary sources: {str(e)}")

        # Merge all available data sources
        if data_sources:
            from scraper import merge_and_clean_data
            data = merge_and_clean_data(data_sources)

            # Save the merged data to cache for future use
            from scraper import save_to_cache
            save_to_cache(data)

            return data, {
                "sources": source_labels,
                "count": len(data)
            }, errors
        else:
            return pd.DataFrame(), {"sources": [], "count": 0}, errors + ["No data sources available"]

    except Exception as e:
        import traceback
        return pd.DataFrame(), {"sources": [], "count": 0}, [str(e), traceback.format_exc()]

# This wrapper function handles the UI elements but delegates the actual data loading to the cached function
def load_data():
    """
    Load data with advanced caching and performance optimizations

    This function loads data from multiple sources:
    1. Streamlit's built-in cache
    2. Local file cache from scraper
    3. XLS file data
    4. Web scraping (as a last resort)

    The data is merged from all available sources for comprehensive analysis.
    """
    force_refresh = st.session_state.get('force_refresh', False)

    with st.spinner(t('loading_data')):
        # Call the cached core function
        data, source_info, errors = _load_data_core(force_refresh=force_refresh)

    # Reset force refresh flag if it was used
    if force_refresh:
        st.session_state.force_refresh = False

    # Display appropriate UI messages based on the results
    if source_info["sources"]:
        # Show toast notifications for each source
        if "Cache" in source_info["sources"]:
            st.toast(t('cache_loaded_success'))
        if "Excel" in source_info["sources"]:
            st.toast(t('xls_loaded_success'))
        if "Government" in source_info["sources"]:
            st.toast(t('bl_gov_loaded_success'))
        if "Statistics" in source_info["sources"]:
            st.toast(t('stats_loaded_success'))
        if "Supplementary" in source_info["sources"]:
            st.toast(t('supp_loaded_success'))

        # Show overall success message
        st.success(t('data_loaded_success').format(
            sources=", ".join(source_info["sources"]),
            records=source_info["count"]
        ))

    # Show any errors that occurred
    for error in errors:
        st.warning(error)

    if data.empty:
        st.error(t('no_data_sources'))

    return data

# Sidebar for controls
with st.sidebar:
    # Language toggle button with improved styling
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button(
            "🌐 " + ("English" if st.session_state.language == 'zh' else "中文"),
            on_click=toggle_language,
            use_container_width=True
        )
    with col2:
        if st.button("ℹ️ " + t('about'), use_container_width=True):
            st.session_state.show_about = not st.session_state.get('show_about', False)

    # Add an about section if toggled
    if st.session_state.get('show_about', False):
        with st.expander(t('about_title'), expanded=True):
            st.markdown(t('about_content'))
            st.markdown("---")

    st.title(t('sidebar_title'))

    # Data controls section
    st.subheader(t('data_controls'))

    # Organize data refresh options in columns
    datacol1, datacol2 = st.columns(2)
    with datacol1:
        # Normal refresh (just clears cache)
        if st.button(t('refresh_data'), use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with datacol2:
        # Force refresh (triggers re-scraping)
        if st.button(t('force_refresh'), use_container_width=True):
            st.session_state.force_refresh = True
            st.cache_data.clear()
            st.rerun()

    # Display data sources summary
    data_sources = []
    xls_file_path = "data/liudongrenkou.xls"
    # Ensure data directory exists for Streamlit Cloud
    try:
        data_dir = os.path.dirname(xls_file_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    except Exception as e:
        st.debug(f"Could not create data directory: {e}")

    if os.path.exists(xls_file_path):
        data_sources.append(t('excel_source'))
    data_sources.append(t('web_scraping_source'))

    # Data source info
    with st.expander(t('data_sources_expander')):
        st.markdown(t('data_sources_info').format(sources=", ".join(data_sources)))
        st.markdown(t('data_freshness_note'))

    # Analysis controls section
    st.subheader(t('analysis_controls'))

    # City selection with search
    st.markdown(f"**{t('select_cities')}**")
    # Add select all/none buttons in columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t('select_all'), use_container_width=True):
            st.session_state.selected_all_cities = True
    with col2:
        if st.button(t('select_none'), use_container_width=True):
            st.session_state.selected_all_cities = False

    # Get city list
    cities = get_guangdong_cities()

    # Handle city selection state
    if 'selected_all_cities' not in st.session_state:
        st.session_state.selected_all_cities = False

    # Set default cities based on selection state
    default_cities = cities if st.session_state.selected_all_cities else cities[:5]

    # Allow user to filter cities by typing
    city_filter = st.text_input(t('filter_cities'), '')
    filtered_cities = [city for city in cities if city_filter.lower() in city.lower()]

    # Show multiselect with filtered cities
    selected_cities = st.multiselect(
        t('available_cities'),
        options=filtered_cities,
        default=default_cities
    )

    # Show warning if no cities selected
    if not selected_cities:
        st.warning(t('no_cities_warning'))

    # Time period selection
    time_periods = ["2018-2024", "2013-2017", "2008-2012"]
    selected_period = st.selectbox(t('select_time_period'), time_periods)

    # Analysis type
    analysis_type = st.radio(
        t('analysis_type'),
        [t('population_inflow'), t('population_outflow'), t('net_migration')]
    )

    # Advanced options
    with st.expander(t('advanced_options')):
        # Vizualization options
        st.subheader(t('visualization_options'))
        normalize_data = st.checkbox(t('normalize_data'), value=False)
        show_trend_lines = st.checkbox(t('show_trend_lines'), value=True)

        # Statistical options
        st.subheader(t('statistical_options'))
        confidence_interval = st.slider(t('confidence_interval'), 80, 99, 95)

        # Performance options
        st.subheader(t('performance_options'))
        st.checkbox(t('enable_caching'), value=True, disabled=True,
                   help=t('caching_help'))

        # Reset all settings
        if st.button(t('reset_settings'), use_container_width=True):
            # Clear session state except language
            current_lang = st.session_state.language
            for key in list(st.session_state.keys()):
                if key != 'language':
                    del st.session_state[key]
            st.session_state.language = current_lang
            st.rerun()

# Main content
st.title(t('main_title'))
st.markdown(t('main_description'))

# Display info about data sources
data_sources = []
xls_file_path = "data/liudongrenkou.xls"
# Check if Excel file exists (already created directory in sidebar)
if os.path.exists(xls_file_path):
    data_sources.append("Excel")
data_sources.append("Web Scraping")
st.info(t('data_sources_info').format(sources=", ".join(data_sources)))

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

    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        t('population_flow_map'),
        t('trend_analysis'),
        t('city_comparison'),
        t('population_pie_chart'),
        t('growth_bar_chart'),
        t('dashboard'),
        t('migration_reasons'),  # New tab
        t('statistical_data')
    ])

    with tab1:
        st.subheader(t('population_flow_map_title'))
        flow_map = create_flow_map(processed_data, selected_cities, analysis_type)
        st.plotly_chart(flow_map, use_container_width=True, key="flow_map_chart")

    with tab2:
        st.subheader(t('trend_analysis_title'))
        trend_chart = create_trend_chart(processed_data, show_trend_lines, normalize_data)
        st.plotly_chart(trend_chart, use_container_width=True, key="trend_chart")

    with tab3:
        st.subheader(t('city_comparison_title'))
        comparison_chart = create_comparison_chart(processed_data, selected_cities)
        st.plotly_chart(comparison_chart, use_container_width=True, key="comparison_chart")

    with tab4:
        st.subheader(t('population_distribution_title'))
        pie_chart = create_population_pie_chart(processed_data, selected_cities)
        st.plotly_chart(pie_chart, use_container_width=True, key="pie_chart")

    with tab5:
        st.subheader(t('growth_rate_title'))
        bar_chart = create_growth_bar_chart(processed_data, selected_cities)
        st.plotly_chart(bar_chart, use_container_width=True, key="bar_chart")

    with tab6:
        st.subheader(t('dashboard_title'))
        dashboard = create_population_dashboard(processed_data, selected_cities)
        st.plotly_chart(dashboard, use_container_width=True, key="dashboard_chart")

    with tab7:
        st.subheader(t('migration_reasons_title'))

        if 'migration_reasons' in stats:
            # Create tabs for different visualizations
            reason_tab1, reason_tab2, reason_tab3, reason_tab4, reason_tab5 = st.tabs([
                t('reason_distribution'),
                t('reason_sankey'),
                t('reason_heatmap'),
                t('reason_timeline'),
                t('reason_city_profile')
            ])

            with reason_tab1:
                # Overall distribution
                if 'distribution' in stats['migration_reasons']:
                    st.write(t('overall_distribution'))

                    # Create treemap visualization
                    from reason_visualizations import create_reason_treemap
                    treemap_fig = create_reason_treemap(processed_data)
                    if treemap_fig:
                        st.plotly_chart(treemap_fig, use_container_width=True)

            with reason_tab2:
                # Sankey diagram
                from reason_visualizations import create_reason_sankey
                sankey_fig = create_reason_sankey(processed_data)
                if sankey_fig:
                    st.plotly_chart(sankey_fig, use_container_width=True)

            with reason_tab3:
                # Heatmap visualization
                from reason_visualizations import create_reason_heatmap
                heatmap_fig = create_reason_heatmap(processed_data)
                if heatmap_fig:
                    st.plotly_chart(heatmap_fig, use_container_width=True)

            with reason_tab4:
                # Timeline visualization
                from reason_visualizations import create_reason_timeline
                timeline_fig = create_reason_timeline(processed_data)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)

            with reason_tab5:
                # City-specific analysis
                st.write(t('top_reasons_by_city'))

                # Create a city selector for detailed view
                selected_city = st.selectbox(
                    t('select_city_analysis'),
                    options=list(stats['migration_reasons']['by_city'].keys())
                )

                if selected_city:
                    # Create two columns for different charts
                    col1, col2 = st.columns(2)

                    with col1:
                        # Pie chart for selected city
                        city_data = stats['migration_reasons']['by_city'][selected_city]
                        fig = px.pie(
                            values=list(city_data['top_reasons'].values()),
                            names=list(city_data['top_reasons'].keys()),
                            title=t('migration_reasons_for_city').format(selected_city)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # Radar chart for selected city
                        from reason_visualizations import create_reason_radar
                        radar_fig = create_reason_radar(processed_data, selected_city)
                        if radar_fig:
                            st.plotly_chart(radar_fig, use_container_width=True)

                    # Show statistics
                    st.metric(
                        t('total_factors'),
                        city_data['total_reasons']
                    )
        else:
            st.info(t('no_reasons_data'))

    with tab8:
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
