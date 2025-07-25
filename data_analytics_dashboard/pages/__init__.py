"""
Pages package for main application pages

This package contains all page-level components including
dashboard overview, custom query interface, and data explorer.
"""

from .dashboard_overview import (
    render_dashboard_overview,
    get_table_statistics,
    display_key_metrics,
    display_dataset_info,
    create_overview_visualizations,
    display_quick_insights
)

# Note: These imports will be available once the remaining files are created
# from .custom_query import (
#     render_custom_query,
#     handle_query_submission,
#     display_query_suggestions,
#     handle_auto_run_queries
# )
# from .data_explorer_page import (
#     render_data_explorer,
#     render_column_selection,
#     render_filter_controls,
#     handle_data_exploration
# )

__version__ = "1.0.0"
__all__ = [
    # Dashboard Overview
    'render_dashboard_overview',
    'get_table_statistics',
    'display_key_metrics',
    'display_dataset_info',
    'create_overview_visualizations',
    'display_quick_insights',
    # Custom Query (will be available after creation)
    # 'render_custom_query',
    # 'handle_query_submission',
    # 'display_query_suggestions',
    # 'handle_auto_run_queries',
    # Data Explorer (will be available after creation)
    # 'render_data_explorer',
    # 'render_column_selection',
    # 'render_filter_controls',
    # 'handle_data_exploration'
]