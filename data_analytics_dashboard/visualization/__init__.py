"""
Visualization package for charts and dashboard components

This package handles all visualization-related functionality including
chart generation, dashboard components, and data exploration UI.
"""

from .chart_generator import (
    create_visualization, 
    create_plotly_chart,
    display_single_metric,
    create_pie_chart,
    create_bar_chart,
    create_line_chart,
    create_scatter_plot,
    create_histogram,
    create_box_plot,
    create_heatmap,
    customize_chart_appearance
)

# Note: These imports will be available once the remaining files are created
# from .dashboard_components import (
#     render_metrics_cards, 
#     render_data_summary,
#     render_status_indicator,
#     render_info_box
# )
# from .data_explorer import (
#     render_column_selector, 
#     render_filter_interface,
#     render_data_preview,
#     render_export_options
# )

__version__ = "1.0.0"
__all__ = [
    # Chart Generation
    'create_visualization', 
    'create_plotly_chart',
    'display_single_metric',
    'create_pie_chart',
    'create_bar_chart',
    'create_line_chart',
    'create_scatter_plot',
    'create_histogram',
    'create_box_plot',
    'create_heatmap',
    'customize_chart_appearance',
    # Dashboard Components (will be available after creation)
    # 'render_metrics_cards', 
    # 'render_data_summary',
    # 'render_status_indicator',
    # 'render_info_box',
    # Data Explorer (will be available after creation)
    # 'render_column_selector', 
    # 'render_filter_interface',
    # 'render_data_preview',
    # 'render_export_options'
]
