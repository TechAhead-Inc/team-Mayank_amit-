"""
General Utility Functions and Helpers
"""

import streamlit as st
import pandas as pd
import numpy as np

def initialize_session_state():
    """Initialize all session state variables"""
    session_vars = {
        'db_engine': None,
        'table_name': None,
        'columns': [],
        'data_types': {},
        'row_count': 0,
        'connection_type': None,
        'jwt_token': None,
        'clear_input': False
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

def format_number(number):
    """
    Format number with appropriate suffixes
    
    Args:
        number: Number to format
        
    Returns:
        str: Formatted number string
    """
    if pd.isna(number):
        return "N/A"
    
    if abs(number) >= 1e9:
        return f"{number/1e9:.1f}B"
    elif abs(number) >= 1e6:
        return f"{number/1e6:.1f}M"
    elif abs(number) >= 1e3:
        return f"{number/1e3:.1f}K"
    elif isinstance(number, float):
        return f"{number:.2f}"
    else:
        return f"{number:,}"

def clean_column_name(column_name):
    """
    Clean column name for database usage
    
    Args:
        column_name (str): Original column name
        
    Returns:
        str: Cleaned column name
    """
    return (column_name.strip()
            .replace(' ', '_')
            .replace('-', '_')
            .replace('.', '_')
            .replace('(', '')
            .replace(')', '')
            .replace('[', '')
            .replace(']', '')
            .replace('/', '_')
            .replace('\\', '_'))

def infer_data_type(series):
    """
    Infer data type from pandas series
    
    Args:
        series: Pandas series
        
    Returns:
        str: Data type category
    """
    if pd.api.types.is_numeric_dtype(series):
        if series.dtype in ['int64', 'int32', 'int16', 'int8']:
            return 'integer'
        else:
            return 'numeric'
    elif pd.api.types.is_datetime64_any_dtype(series):
        return 'datetime'
    else:
        return 'text'

def get_sample_data_summary(df, max_rows=5):
    """
    Get sample data summary
    
    Args:
        df: Pandas DataFrame
        max_rows (int): Maximum rows to show
        
    Returns:
        dict: Summary information
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'datetime_columns': datetime_cols,
        'sample_data': df.head(max_rows),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'null_counts': df.isnull().sum().to_dict()
    }

def safe_execute_function(func, *args, **kwargs):
    """
    Safely execute function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        tuple: (success: bool, result: any, error: str)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        return False, None, str(e)

def create_download_link(df, filename="data.csv", file_format="csv"):
    """
    Create download link for DataFrame
    
    Args:
        df: Pandas DataFrame
        filename (str): Download filename
        file_format (str): File format (csv, excel)
        
    Returns:
        str: Download link HTML
    """
    if file_format.lower() == "csv":
        csv_data = df.to_csv(index=False)
        return st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
    elif file_format.lower() == "excel":
        excel_data = df.to_excel(index=False)
        return st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=filename.replace('.csv', '.xlsx'),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

def truncate_text(text, max_length=50):
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(str(text)) <= max_length:
        return str(text)
    return str(text)[:max_length] + "..."

def get_column_statistics(df, column_name):
    """
    Get statistics for a specific column
    
    Args:
        df: Pandas DataFrame
        column_name (str): Column name
        
    Returns:
        dict: Column statistics
    """
    if column_name not in df.columns:
        return None
    
    col = df[column_name]
    stats = {
        'name': column_name,
        'dtype': str(col.dtype),
        'non_null_count': col.count(),
        'null_count': col.isnull().sum(),
        'unique_count': col.nunique(),
        'memory_usage': col.memory_usage(deep=True)
    }
    
    if pd.api.types.is_numeric_dtype(col):
        stats.update({
            'mean': col.mean(),
            'median': col.median(),
            'std': col.std(),
            'min': col.min(),
            'max': col.max(),
            'q25': col.quantile(0.25),
            'q75': col.quantile(0.75)
        })
    elif pd.api.types.is_categorical_dtype(col) or col.dtype == 'object':
        stats.update({
            'most_frequent': col.mode().iloc[0] if not col.mode().empty else None,
            'frequency_top': col.value_counts().iloc[0] if not col.empty else 0
        })
    
    return stats

def validate_sql_query(query):
    """
    Basic SQL query validation
    
    Args:
        query (str): SQL query string
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not query or not query.strip():
        return False, "Query is empty"
    
    query = query.strip().upper()
    
    # Check for dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
    for keyword in dangerous_keywords:
        if keyword in query:
            return False, f"Query contains potentially dangerous keyword: {keyword}"
    
    # Check if it starts with SELECT
    if not query.startswith('SELECT') and not query.startswith('WITH'):
        return False, "Query must start with SELECT or WITH"
    
    return True, "Valid query"

def get_table_preview(df, max_rows=10, max_cols=10):
    """
    Get table preview with size limits
    
    Args:
        df: Pandas DataFrame
        max_rows (int): Maximum rows to show
        max_cols (int): Maximum columns to show
        
    Returns:
        pandas.DataFrame: Preview DataFrame
    """
    preview_df = df.head(max_rows)
    
    if len(df.columns) > max_cols:
        preview_df = preview_df.iloc[:, :max_cols]
        
    return preview_df