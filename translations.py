# Define all UI strings in multiple languages

LANGUAGES = {
    'en': 'English',
    'zh': '中文'
}

TRANSLATIONS = {
    # Navigation and titles
    'main_title': {
        'en': 'Guangdong Province Population Flow Analysis',
        'zh': '广东省人口流动分析'
    },
    'main_description': {
        'en': 'This application analyzes population flow patterns in Guangdong Province, China. Select cities, time periods, and analysis types using the sidebar controls.',
        'zh': '本应用程序分析中国广东省的人口流动模式。使用侧边栏控件选择城市、时间段和分析类型。'
    },
    'sidebar_title': {
        'en': 'Analysis Controls',
        'zh': '分析控制'
    },
    
    # Control labels
    'select_cities': {
        'en': 'Select Cities',
        'zh': '选择城市'
    },
    'select_time_period': {
        'en': 'Select Time Period',
        'zh': '选择时间段'
    },
    'analysis_type': {
        'en': 'Analysis Type',
        'zh': '分析类型'
    },
    'population_inflow': {
        'en': 'Population Inflow',
        'zh': '人口流入'
    },
    'population_outflow': {
        'en': 'Population Outflow',
        'zh': '人口流出'
    },
    'net_migration': {
        'en': 'Net Migration',
        'zh': '净迁移'
    },
    'advanced_options': {
        'en': 'Advanced Options',
        'zh': '高级选项'
    },
    'normalize_data': {
        'en': 'Normalize Data for Comparison',
        'zh': '标准化数据以进行比较'
    },
    'show_trend_lines': {
        'en': 'Show Trend Lines',
        'zh': '显示趋势线'
    },
    'confidence_interval': {
        'en': 'Confidence Interval (%)',
        'zh': '置信区间 (%)'
    },
    'refresh_data': {
        'en': 'Refresh Data',
        'zh': '刷新数据'
    },
    
    # Tab names
    'population_flow_map': {
        'en': 'Population Flow Map',
        'zh': '人口流动地图'
    },
    'trend_analysis': {
        'en': 'Trend Analysis',
        'zh': '趋势分析'
    },
    'city_comparison': {
        'en': 'City Comparison',
        'zh': '城市比较'
    },
    'statistical_data': {
        'en': 'Statistical Data',
        'zh': '统计数据'
    },
    
    # Section titles
    'population_flow_map_title': {
        'en': 'Population Flow Map of Guangdong Province',
        'zh': '广东省人口流动地图'
    },
    'trend_analysis_title': {
        'en': 'Population Trend Analysis by City',
        'zh': '按城市的人口趋势分析'
    },
    'city_comparison_title': {
        'en': 'City Population Flow Comparison',
        'zh': '城市人口流动比较'
    },
    'statistical_data_title': {
        'en': 'Statistical Data and Analysis',
        'zh': '统计数据和分析'
    },
    'statistical_summary': {
        'en': 'Statistical Summary',
        'zh': '统计摘要'
    },
    
    # Metrics
    'total_population': {
        'en': 'Total Population',
        'zh': '总人口'
    },
    'avg_annual_flow': {
        'en': 'Avg. Annual Flow',
        'zh': '年均流动'
    },
    'growth_rate': {
        'en': 'Growth Rate',
        'zh': '增长率'
    },
    
    # Data download
    'download_csv': {
        'en': 'Download CSV',
        'zh': '下载 CSV'
    },
    'download_excel': {
        'en': 'Download Excel',
        'zh': '下载 Excel'
    },
    
    # Notifications and messages
    'loading_data': {
        'en': 'Loading population data...',
        'zh': '正在加载人口数据...'
    },
    'using_xls_data': {
        'en': 'Using data from uploaded Excel file',
        'zh': '使用上传的Excel文件中的数据'
    },
    'data_sources_info': {
        'en': 'Data is being collected from multiple sources: {sources}',
        'zh': '数据正在从多个来源收集: {sources}'
    },
    'data_load_error': {
        'en': 'Error loading data',
        'zh': '数据加载错误'
    },
    'no_data_error': {
        'en': 'No data available for the selected criteria',
        'zh': '所选条件没有可用数据'
    },
    'try_refresh': {
        'en': 'Try refreshing the data using the sidebar button',
        'zh': '尝试使用侧边栏按钮刷新数据'
    },
    
    # Footer
    'footer_text': {
        'en': 'Guangdong Population Flow Analysis - Graduation Project',
        'zh': '广东人口流动分析 - 毕业项目'
    }
}

def get_translation(key, language='en'):
    """
    Get translated text for a given key and language
    
    Args:
        key (str): Translation key
        language (str): Language code ('en' or 'zh')
        
    Returns:
        str: Translated text or the key itself if translation not found
    """
    if key in TRANSLATIONS and language in TRANSLATIONS[key]:
        return TRANSLATIONS[key][language]
    
    # Fallback to English if the translation is not found
    if key in TRANSLATIONS and 'en' in TRANSLATIONS[key]:
        return TRANSLATIONS[key]['en']
    
    # Return the key as is if no translation is found
    return key
