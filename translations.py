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
        'en': 'Analysis Dashboard',
        'zh': '分析仪表板'
    },
    'about': {
        'en': 'About',
        'zh': '关于'
    },
    'about_title': {
        'en': 'About This Project',
        'zh': '关于此项目'
    },
    'about_content': {
        'en': 'This application analyzes population flow patterns in Guangdong Province using data from multiple sources including government statistics bureaus and Excel files. It provides visualization tools for understanding migration patterns and population changes across all major cities in the province.',
        'zh': '此应用程序使用来自多个来源（包括政府统计局和Excel文件）的数据分析广东省的人口流动模式。它提供可视化工具，用于理解该省所有主要城市的迁移模式和人口变化。'
    },
    'data_controls': {
        'en': 'Data Controls',
        'zh': '数据控制'
    },
    'analysis_controls': {
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
    'force_refresh': {
        'en': 'Force Refresh',
        'zh': '强制刷新'
    },
    'data_sources_expander': {
        'en': 'Data Sources',
        'zh': '数据来源'
    },
    'excel_source': {
        'en': 'Excel File',
        'zh': 'Excel文件'
    },
    'web_scraping_source': {
        'en': 'Web Scraping',
        'zh': '网络抓取'
    },
    'data_freshness_note': {
        'en': 'Data is automatically refreshed when you restart the application. Use "Force Refresh" to re-scrape all sources.',
        'zh': '当您重新启动应用程序时，数据会自动刷新。使用"强制刷新"重新抓取所有来源。'
    },
    'select_all': {
        'en': 'Select All',
        'zh': '全选'
    },
    'select_none': {
        'en': 'Clear All',
        'zh': '清除全部'
    },
    'filter_cities': {
        'en': 'Filter cities...',
        'zh': '筛选城市...'
    },
    'available_cities': {
        'en': 'Available Cities',
        'zh': '可用城市'
    },
    'no_cities_warning': {
        'en': 'Please select at least one city to continue',
        'zh': '请至少选择一个城市以继续'
    },
    'visualization_options': {
        'en': 'Visualization Options',
        'zh': '可视化选项'
    },
    'statistical_options': {
        'en': 'Statistical Options',
        'zh': '统计选项'
    },
    'performance_options': {
        'en': 'Performance Options',
        'zh': '性能选项'
    },
    'enable_caching': {
        'en': 'Enable Data Caching',
        'zh': '启用数据缓存'
    },
    'caching_help': {
        'en': 'Caching improves performance by storing data and calculations locally',
        'zh': '通过本地存储数据和计算结果，缓存提高性能'
    },
    'reset_settings': {
        'en': 'Reset All Settings',
        'zh': '重置所有设置'
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
    'population_pie_chart': {
        'en': 'Population Distribution',
        'zh': '人口分布'
    },
    'growth_bar_chart': {
        'en': 'Growth Rates',
        'zh': '增长率'
    },
    'dashboard': {
        'en': 'Dashboard View',
        'zh': '仪表板视图'
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
    'population_distribution_title': {
        'en': 'Population Distribution by City',
        'zh': '城市人口分布'
    },
    'growth_rate_title': {
        'en': 'Annual Growth Rate Comparison',
        'zh': '年增长率比较'
    },
    'dashboard_title': {
        'en': 'Population Analysis Dashboard',
        'zh': '人口分析仪表板'
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
    'loading_data_from_cache': {
        'en': 'Loading data from local cache...',
        'zh': '正在从本地缓存加载数据...'
    },
    'loading_data_from_xls': {
        'en': 'Loading data from Excel file...',
        'zh': '正在从Excel文件加载数据...'
    },
    'scraping_data': {
        'en': 'Collecting data from online sources...',
        'zh': '正在从在线来源收集数据...'
    },
    'cache_loaded_success': {
        'en': 'Successfully loaded data from cache',
        'zh': '成功从缓存加载数据'
    },
    'xls_loaded_success': {
        'en': 'Successfully loaded data from Excel file',
        'zh': '成功从Excel文件加载数据'
    },
    'bl_gov_loaded_success': {
        'en': 'Successfully loaded government data',
        'zh': '成功加载政府数据'
    },
    'stats_loaded_success': {
        'en': 'Successfully loaded statistics bureau data',
        'zh': '成功加载统计局数据'
    },
    'supp_loaded_success': {
        'en': 'Successfully loaded supplementary data',
        'zh': '成功加载补充数据'
    },
    'data_loaded_success': {
        'en': 'Successfully loaded data from {sources} sources ({records} records)',
        'zh': '成功从{sources}来源加载数据 ({records}条记录)'
    },
    'no_data_sources': {
        'en': 'No data sources available',
        'zh': '没有可用的数据来源'
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
    },
    
    # Migration reasons analysis
    'migration_reasons': {
        'en': 'Migration Reasons',
        'zh': '迁移原因'
    },
    'migration_reasons_title': {
        'en': 'Migration Reasons Analysis',
        'zh': '迁移原因分析'
    },
    'overall_distribution': {
        'en': 'Overall Distribution of Migration Reasons',
        'zh': '迁移原因整体分布'
    },
    'reason_distribution': {
        'en': 'Distribution of Migration Reasons',
        'zh': '迁移原因分布'
    },
    'top_reasons_by_city': {
        'en': 'Top Migration Reasons by City',
        'zh': '各城市主要迁移原因'
    },
    'select_city_analysis': {
        'en': 'Select a city for detailed analysis',
        'zh': '选择城市进行详细分析'
    },
    'migration_reasons_for_city': {
        'en': 'Migration Reasons Distribution for {}',
        'zh': '{}迁移原因分布'
    },
    'total_factors': {
        'en': 'Total Migration Factors Identified',
        'zh': '已识别迁移因素总数'
    },
    'no_reasons_data': {
        'en': 'Migration reason analysis is not available for the selected data range. Try selecting a more recent time period or different cities.',
        'zh': '所选数据范围内无迁移原因分析。请尝试选择更近的时间段或不同的城市。'
    },
    'employment_opportunities': {
        'en': 'Employment Opportunities',
        'zh': '就业机会'
    },
    'educational_resources': {
        'en': 'Educational Resources',
        'zh': '教育资源'
    },
    'healthcare_improvements': {
        'en': 'Healthcare Improvements',
        'zh': '医疗改善'
    },
    'industrial_development': {
        'en': 'Industrial Development',
        'zh': '产业发展'
    },
    'living_environment': {
        'en': 'Living Environment',
        'zh': '居住环境'
    },
    'transportation_infrastructure': {
        'en': 'Transportation Infrastructure',
        'zh': '交通基础设施'
    },
    'policy_support': {
        'en': 'Policy Support',
        'zh': '政策支持'
    },
    'reason_sankey': {
        'en': 'Flow Diagram',
        'zh': '流动图'
    },
    'reason_heatmap': {
        'en': 'Correlation Map',
        'zh': '相关性图'
    },
    'reason_timeline': {
        'en': 'Time Trends',
        'zh': '时间趋势'
    },
    'reason_city_profile': {
        'en': 'City Profile',
        'zh': '城市画像'
    },
    'reason_distribution': {
        'en': 'Distribution',
        'zh': '分布'
    },
    'export_data': {
        'en': 'Export Data',
        'zh': '导出数据'
    },
    'processing_data': {
        'en': 'Processing data...',
        'zh': '正在处理数据...'
    },
    'generating_map': {
        'en': 'Generating population flow map...',
        'zh': '正在生成人口流动地图...'
    },
    'analyzing_trends': {
        'en': 'Analyzing population trends...',
        'zh': '正在分析人口趋势...'
    },
    'comparing_cities': {
        'en': 'Comparing city data...',
        'zh': '正在比较城市数据...'
    },
    'analyzing_growth': {
        'en': 'Analyzing growth patterns...',
        'zh': '正在分析增长模式...'
    },
    'creating_dashboard': {
        'en': 'Creating analysis dashboard...',
        'zh': '正在创建分析仪表板...'
    },
    'please_load_data': {
        'en': 'Please wait while data is being loaded...',
        'zh': '请等待数据加载...'
    },
    'growth_analysis': {
        'en': 'Growth Analysis',
        'zh': '增长分析'
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
