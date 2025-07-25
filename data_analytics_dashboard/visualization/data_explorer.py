"""
Data Explorer UI Components Module
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils.constants import DEFAULT_VALUES
from visualization.dashboard_components import render_metrics_cards, render_status_indicator

def render_column_selector(columns, data_types=None, default_selection=None, key="column_selector"):
    """
    Render column selection interface with data type indicators
    
    Args:
        columns (list): List of available columns
        data_types (dict): Dictionary mapping columns to data types
        default_selection (list): Default selected columns
        key (str): Unique key for the widget
        
    Returns:
        list: Selected columns
    """
    if not columns:
        st.warning("No columns available for selection")
        return []
    
    # Set default selection
    if default_selection is None:
        default_selection = columns[:5] if len(columns) > 5 else columns
    
    # Ensure default selection is valid
    default_selection = [col for col in default_selection if col in columns]
    
    st.subheader("Column Selection")
    
    # Create column selection with data type indicators
    if data_types:
        # Group columns by data type for better organization
        col_groups = {}
        for col in columns:
            dtype = data_types.get(col, 'unknown')
            if dtype not in col_groups:
                col_groups[dtype] = []
            col_groups[dtype].append(col)
        
        # Show column counts by type
        type_counts = {dtype: len(cols) for dtype, cols in col_groups.items()}
        st.write("**Available columns by type:**")
        
        cols = st.columns(len(type_counts))
        for i, (dtype, count) in enumerate(type_counts.items()):
            with cols[i]:
                icon = get_data_type_icon(dtype)
                st.metric(f"{icon} {dtype.title()}", count)
    
    # Column selection widget
    selected_columns = st.multiselect(
        "Select columns to explore:",
        options=columns,
        default=default_selection,
        key=key,
        help="Choose which columns to include in your analysis"
    )
    
    # Show selection summary
    if selected_columns:
        st.success(f"Selected {len(selected_columns)} out of {len(columns)} columns")
    else:
        st.warning("Please select at least one column")
    
    return selected_columns

def render_filter_interface(df, columns=None, key="filter_interface"):
    """
    Render dynamic filter interface based on column data types
    
    Args:
        df (pandas.DataFrame): DataFrame to filter
        columns (list): Columns to create filters for (None = all columns)
        key (str): Unique key for the widget
        
    Returns:
        dict: Filter conditions to apply
    """
    if df.empty:
        st.warning("No data available for filtering")
        return {}
    
    if columns is None:
        columns = df.columns.tolist()
    
    st.subheader("Data Filters")
    
    filters = {}
    
    # Create filters based on data types
    for col in columns:
        with st.expander(f"Filter by {col}", expanded=False):
            
            if df[col].dtype in ['int64', 'float64']:
                # Numeric filter
                filters[col] = render_numeric_filter(df, col, f"{key}_{col}")
            
            elif df[col].dtype == 'object':
                # Categorical filter
                filters[col] = render_categorical_filter(df, col, f"{key}_{col}")
            
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                # Date filter
                filters[col] = render_date_filter(df, col, f"{key}_{col}")
            
            else:
                # Generic filter
                filters[col] = render_generic_filter(df, col, f"{key}_{col}")
    
    # Show active filters summary
    active_filters = {k: v for k, v in filters.items() if v is not None}
    if active_filters:
        st.info(f"Active filters: {len(active_filters)}")
    
    return filters

def render_numeric_filter(df, column, key):
    """Render numeric range filter"""
    try:
        min_val = float(df[column].min())
        max_val = float(df[column].max())
        
        if min_val == max_val:
            st.write(f"All values are {min_val}")
            return None
        
        # Range slider
        range_values = st.slider(
            f"Range for {column}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            key=key
        )
        
        # Show statistics
        st.write(f"**Statistics:** Min: {min_val:.2f}, Max: {max_val:.2f}, Mean: {df[column].mean():.2f}")
        
        return {'type': 'range', 'min': range_values[0], 'max': range_values[1]}
    
    except Exception as e:
        st.error(f"Error creating numeric filter: {str(e)}")
        return None

def render_categorical_filter(df, column, key):
    """Render categorical multiselect filter"""
    try:
        unique_values = df[column].dropna().unique()
        
        if len(unique_values) == 0:
            st.write("No values to filter")
            return None
        
        if len(unique_values) > 50:
            st.warning(f"Too many unique values ({len(unique_values)}). Showing top 50.")
            # Show most frequent values
            value_counts = df[column].value_counts().head(50)
            unique_values = value_counts.index.tolist()
        
        selected_values = st.multiselect(
            f"Select values for {column}",
            options=sorted(unique_values.astype(str)),
            key=key,
            help=f"Choose from {len(unique_values)} unique values"
        )
        
        return {'type': 'categorical', 'values': selected_values} if selected_values else None
    
    except Exception as e:
        st.error(f"Error creating categorical filter: {str(e)}")
        return None

def render_date_filter(df, column, key):
    """Render date range filter"""
    try:
        min_date = df[column].min()
        max_date = df[column].max()
        
        if pd.isna(min_date) or pd.isna(max_date):
            st.write("No valid dates to filter")
            return None
        
        date_range = st.date_input(
            f"Date range for {column}",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key=key
        )
        
        if len(date_range) == 2:
            return {'type': 'date_range', 'start': date_range[0], 'end': date_range[1]}
        
        return None
    
    except Exception as e:
        st.error(f"Error creating date filter: {str(e)}")
        return None

def render_generic_filter(df, column, key):
    """Render generic text filter"""
    try:
        search_term = st.text_input(
            f"Search in {column}",
            key=key,
            help="Enter text to search for in this column"
        )
        
        return {'type': 'text_search', 'term': search_term} if search_term else None
    
    except Exception as e:
        st.error(f"Error creating generic filter: {str(e)}")
        return None

def apply_filters(df, filters):
    """
    Apply filters to DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to filter
        filters (dict): Filter conditions
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for column, filter_config in filters.items():
        if filter_config is None or column not in df.columns:
            continue
        
        try:
            if filter_config['type'] == 'range':
                mask = (df[column] >= filter_config['min']) & (df[column] <= filter_config['max'])
                filtered_df = filtered_df[mask]
            
            elif filter_config['type'] == 'categorical':
                if filter_config['values']:
                    mask = df[column].astype(str).isin(filter_config['values'])
                    filtered_df = filtered_df[mask]
            
            elif filter_config['type'] == 'date_range':
                mask = (df[column] >= pd.to_datetime(filter_config['start'])) & \
                       (df[column] <= pd.to_datetime(filter_config['end']))
                filtered_df = filtered_df[mask]
            
            elif filter_config['type'] == 'text_search':
                if filter_config['term']:
                    mask = df[column].astype(str).str.contains(
                        filter_config['term'], case=False, na=False
                    )
                    filtered_df = filtered_df[mask]
        
        except Exception as e:
            st.error(f"Error applying filter for {column}: {str(e)}")
    
    return filtered_df

def render_data_preview(df, max_rows=100):
    """
    Render data preview with pagination and controls
    
    Args:
        df (pandas.DataFrame): DataFrame to preview
        max_rows (int): Maximum rows to display
    """
    if df.empty:
        st.warning("No data to preview")
        return
    
    st.subheader("Data Preview")
    
    # Show summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Displayed Rows", f"{min(len(df), max_rows):,}")
    with col3:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory Usage", f"{memory_mb:.1f} MB")
    
    # Display options
    col1, col2 = st.columns(2)
    with col1:
        show_data_types = st.checkbox("Show data types", value=False)
    with col2:
        show_statistics = st.checkbox("Show column statistics", value=False)
    
    # Show data types if requested
    if show_data_types:
        st.subheader("Data Types")
        dtypes_df = pd.DataFrame({
            'Column': df.columns,
            'Data Type': [str(dtype) for dtype in df.dtypes],
            'Non-Null Count': [df[col].count() for col in df.columns],
            'Null Count': [df[col].isnull().sum() for col in df.columns]
        })
        st.dataframe(dtypes_df, use_container_width=True, hide_index=True)
    
    # Show statistics if requested
    if show_statistics:
        st.subheader("Column Statistics")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No numeric columns for statistical summary")
    
    # Show the actual data
    display_df = df.head(max_rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if len(df) > max_rows:
        st.info(f"Showing first {max_rows} rows out of {len(df):,} total rows")

def render_export_options(df, filename_prefix="data_export"):
    """
    Render export options for the filtered data
    
    Args:
        df (pandas.DataFrame): DataFrame to export
        filename_prefix (str): Prefix for the export filename
    """
    if df.empty:
        st.warning("No data to export")
        return
    
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Export
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv_data,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON Export
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            label="Download as JSON",
            data=json_data,
            file_name=f"{filename_prefix}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Excel Export (if openpyxl is available)
        try:
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            
            st.download_button(
                label="Download as Excel",
                data=buffer.getvalue(),
                file_name=f"{filename_prefix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except ImportError:
            st.info("Excel export requires openpyxl package")

def get_data_type_icon(data_type):
    """Get icon for data type"""
    icons = {
        'integer': '🔢',
        'numeric': '📊',
        'text': '📝',
        'datetime': '📅',
        'boolean': '✅',
        'unknown': '❓'
    }
    return icons.get(data_type.lower(), '❓')

def render_quick_stats(df):
    """
    Render quick statistics for the DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
    """
    if df.empty:
        return
    
    st.subheader("Quick Statistics")
    
    # Basic metrics
    metrics = [
        {'label': 'Rows', 'value': len(df)},
        {'label': 'Columns', 'value': len(df.columns)},
        {'label': 'Memory (MB)', 'value': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f}"}
    ]
    
    # Data type counts
    numeric_count = len(df.select_dtypes(include=[np.number]).columns)
    text_count = len(df.select_dtypes(include=['object']).columns)
    
    if numeric_count > 0:
        metrics.append({'label': 'Numeric Cols', 'value': numeric_count})
    if text_count > 0:
        metrics.append({'label': 'Text Cols', 'value': text_count})
    
    render_metrics_cards(metrics)

def render_column_profiler(df, column):
    """
    Render detailed profile for a specific column
    
    Args:
        df (pandas.DataFrame): DataFrame containing the column
        column (str): Column name to profile
    """
    if column not in df.columns:
        st.error(f"Column '{column}' not found")
        return
    
    st.subheader(f"Column Profile: {column}")
    
    col_data = df[column]
    
    # Basic info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Type", str(col_data.dtype))
    with col2:
        st.metric("Non-Null Count", col_data.count())
    with col3:
        st.metric("Null Count", col_data.isnull().sum())
    with col4:
        st.metric("Unique Values", col_data.nunique())
    
    # Type-specific analysis
    if pd.api.types.is_numeric_dtype(col_data):
        # Numeric column analysis
        st.write("**Numeric Statistics:**")
        stats = col_data.describe()
        st.dataframe(stats.to_frame().T, use_container_width=True)
    
    elif col_data.dtype == 'object':
        # Text column analysis
        st.write("**Text Statistics:**")
        if col_data.count() > 0:
            value_counts = col_data.value_counts().head(10)
            st.write("**Top 10 Values:**")
            st.dataframe(value_counts.to_frame('Count'), use_container_width=True)
    
    # Show sample values
    st.write("**Sample Values:**")
    sample_values = col_data.dropna().head(10).tolist()
    if sample_values:
        st.write(", ".join([str(val) for val in sample_values]))
    else:
        st.write("No non-null values found")