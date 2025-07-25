"""
Dashboard UI Components Module
"""

import streamlit as st
import pandas as pd
from utils.helpers import format_number
from utils.constants import UI_MESSAGES, VISUALIZATION_CONSTANTS

def render_metrics_cards(metrics_data):
    """
    Render metrics cards in a responsive grid layout
    
    Args:
        metrics_data (list): List of dictionaries with metric information
                            Each dict should have: {'label': str, 'value': any, 'delta': float, 'help': str}
    """
    if not metrics_data:
        st.warning("No metrics data provided")
        return
    
    # Create columns based on number of metrics (max 4 per row)
    num_metrics = len(metrics_data)
    cols_per_row = min(4, num_metrics)
    
    # Split metrics into rows if more than 4
    rows = [metrics_data[i:i + cols_per_row] for i in range(0, num_metrics, cols_per_row)]
    
    for row in rows:
        cols = st.columns(len(row))
        
        for i, metric in enumerate(row):
            with cols[i]:
                label = metric.get('label', 'Metric')
                value = metric.get('value', 0)
                delta = metric.get('delta', None)
                help_text = metric.get('help', None)
                
                # Format value if it's numeric
                if isinstance(value, (int, float)):
                    formatted_value = format_number(value)
                else:
                    formatted_value = str(value)
                
                st.metric(
                    label=label,
                    value=formatted_value,
                    delta=delta,
                    help=help_text
                )

def render_data_summary(df, show_sample=True, max_rows=5):
    """
    Render comprehensive data summary component
    
    Args:
        df (pandas.DataFrame): DataFrame to summarize
        show_sample (bool): Whether to show sample data
        max_rows (int): Maximum rows to show in sample
    """
    if df.empty:
        st.warning("No data to summarize")
        return
    
    # Basic statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Overview")
        
        metrics = [
            {'label': 'Total Rows', 'value': len(df), 'help': 'Total number of records'},
            {'label': 'Total Columns', 'value': len(df.columns), 'help': 'Total number of columns'},
        ]
        
        # Add data type breakdown
        numeric_cols = len(df.select_dtypes(include=['number']).columns)
        text_cols = len(df.select_dtypes(include=['object']).columns)
        date_cols = len(df.select_dtypes(include=['datetime']).columns)
        
        if numeric_cols > 0:
            metrics.append({'label': 'Numeric Columns', 'value': numeric_cols, 'help': 'Columns with numeric data'})
        if text_cols > 0:
            metrics.append({'label': 'Text Columns', 'value': text_cols, 'help': 'Columns with text data'})
        if date_cols > 0:
            metrics.append({'label': 'Date Columns', 'value': date_cols, 'help': 'Columns with date/time data'})
        
        render_metrics_cards(metrics)
    
    with col2:
        st.subheader("Data Quality")
        
        # Check for missing values
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        
        quality_metrics = [
            {'label': 'Missing Values', 'value': int(total_missing), 'help': 'Total number of missing values'},
            {'label': 'Complete Rows', 'value': len(df.dropna()), 'help': 'Rows with no missing values'},
        ]
        
        # Data completeness percentage
        completeness = ((len(df) * len(df.columns) - total_missing) / (len(df) * len(df.columns))) * 100
        quality_metrics.append({
            'label': 'Data Completeness', 
            'value': f"{completeness:.1f}%", 
            'help': 'Percentage of non-missing values'
        })
        
        render_metrics_cards(quality_metrics)
    
    # Show sample data if requested
    if show_sample:
        st.subheader("Sample Data")
        sample_df = df.head(max_rows)
        st.dataframe(sample_df, use_container_width=True, hide_index=True)

def render_status_indicator(status, message, details=None):
    """
    Render status indicator with appropriate styling
    
    Args:
        status (str): Status type ('success', 'warning', 'error', 'info')
        message (str): Status message
        details (str): Additional details (optional)
    """
    status_configs = {
        'success': {'icon': '✅', 'method': st.success},
        'warning': {'icon': '⚠️', 'method': st.warning},
        'error': {'icon': '❌', 'method': st.error},
        'info': {'icon': 'ℹ️', 'method': st.info}
    }
    
    config = status_configs.get(status, status_configs['info'])
    
    display_message = f"{config['icon']} {message}"
    if details:
        display_message += f"\n\n**Details:** {details}"
    
    config['method'](display_message)

def render_info_box(title, content, box_type="info", expandable=False, expanded=False):
    """
    Render styled information box
    
    Args:
        title (str): Box title
        content (str): Box content
        box_type (str): Type of box ('info', 'success', 'warning', 'error')
        expandable (bool): Whether the box is expandable
        expanded (bool): Whether the box is expanded by default
    """
    if expandable:
        with st.expander(title, expanded=expanded):
            render_status_indicator(box_type, content)
    else:
        st.subheader(title)
        render_status_indicator(box_type, content)

def render_progress_bar(current, total, label="Progress"):
    """
    Render progress bar with percentage
    
    Args:
        current (int): Current progress value
        total (int): Total/maximum value
        label (str): Progress label
    """
    if total <= 0:
        st.warning("Invalid progress values")
        return
    
    progress = min(current / total, 1.0)  # Ensure progress doesn't exceed 100%
    percentage = progress * 100
    
    st.write(f"**{label}:** {current:,} / {total:,} ({percentage:.1f}%)")
    st.progress(progress)

def render_key_value_pairs(data, title="Information", columns=2):
    """
    Render key-value pairs in a formatted layout
    
    Args:
        data (dict): Dictionary of key-value pairs
        title (str): Section title
        columns (int): Number of columns to display
    """
    if not data:
        st.warning("No data to display")
        return
    
    st.subheader(title)
    
    # Split data into columns
    items = list(data.items())
    items_per_col = len(items) // columns + (1 if len(items) % columns else 0)
    
    cols = st.columns(columns)
    
    for i, (key, value) in enumerate(items):
        col_idx = i // items_per_col
        if col_idx < len(cols):
            with cols[col_idx]:
                # Format value
                if isinstance(value, (int, float)):
                    formatted_value = format_number(value)
                elif isinstance(value, bool):
                    formatted_value = "✅" if value else "❌"
                else:
                    formatted_value = str(value)
                
                st.write(f"**{key}:** {formatted_value}")

def render_data_table_with_controls(df, title="Data Table", show_controls=True):
    """
    Render data table with search and filter controls
    
    Args:
        df (pandas.DataFrame): DataFrame to display
        title (str): Table title
        show_controls (bool): Whether to show control widgets
    """
    if df.empty:
        st.warning("No data to display in table")
        return
    
    st.subheader(title)
    
    if show_controls:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Search functionality
            search_term = st.text_input("Search in data:", key=f"search_{title}")
            
        with col2:
            # Row limit
            max_rows = st.selectbox(
                "Rows to display:",
                options=[10, 25, 50, 100, 500],
                index=1,
                key=f"rows_{title}"
            )
        
        with col3:
            # Column selection
            selected_columns = st.multiselect(
                "Select columns:",
                options=df.columns.tolist(),
                default=df.columns.tolist()[:5],  # Show first 5 columns by default
                key=f"cols_{title}"
            )
        
        # Apply filters
        filtered_df = df.copy()
        
        # Apply search filter
        if search_term:
            # Search across all string columns
            string_cols = df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                mask = df[string_cols].astype(str).apply(
                    lambda x: x.str.contains(search_term, case=False, na=False)
                ).any(axis=1)
                filtered_df = df[mask]
        
        # Apply column selection
        if selected_columns:
            filtered_df = filtered_df[selected_columns]
        
        # Apply row limit
        display_df = filtered_df.head(max_rows)
        
        # Show filter info
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(display_df)} rows (filtered from {len(df)} total rows)")
        else:
            st.info(f"Showing {len(display_df)} rows")
    
    else:
        display_df = df
    
    # Display the table
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_loading_spinner(message="Loading...", key=None):
    """
    Render loading spinner with message
    
    Args:
        message (str): Loading message
        key (str): Unique key for the spinner
    """
    with st.spinner(message):
        # This is typically used as a context manager
        # The actual loading content should be placed inside this block
        pass

def render_alert_banner(message, alert_type="info", dismissible=False):
    """
    Render alert banner at the top of the page
    
    Args:
        message (str): Alert message
        alert_type (str): Type of alert ('info', 'success', 'warning', 'error')
        dismissible (bool): Whether the alert can be dismissed
    """
    alert_key = f"alert_{hash(message)}"
    
    # Check if alert was dismissed
    if dismissible and st.session_state.get(f"dismissed_{alert_key}", False):
        return
    
    # Render alert
    if alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.info(message)
    
    # Add dismiss button if dismissible
    if dismissible:
        if st.button("Dismiss", key=f"dismiss_{alert_key}"):
            st.session_state[f"dismissed_{alert_key}"] = True
            st.rerun()

def render_sidebar_section(title, content_func, collapsed=False):
    """
    Render a collapsible section in the sidebar
    
    Args:
        title (str): Section title
        content_func (callable): Function that renders the section content
        collapsed (bool): Whether the section starts collapsed
    """
    with st.sidebar:
        with st.expander(title, expanded=not collapsed):
            content_func()

def render_empty_state(message, action_button=None, action_callback=None):
    """
    Render empty state placeholder
    
    Args:
        message (str): Empty state message
        action_button (str): Optional action button text
        action_callback (callable): Optional action button callback
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <h3 style="color: #666;">No Data Available</h3>
            <p style="color: #888;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if action_button and action_callback:
            if st.button(action_button, use_container_width=True):
                action_callback()