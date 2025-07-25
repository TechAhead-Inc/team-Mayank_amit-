"""
File Upload and Processing Module
"""

import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import json
from utils.validators import validate_file_upload, validate_dataframe
from utils.helpers import clean_column_name, infer_data_type

def handle_file_upload(uploaded_file):
    """
    Handle file upload and create temporary database
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        tuple: (db_path, table_name, columns, data_types, row_count) or (None, None, None, None, None)
    """
    try:
        # Validate file
        is_valid, message = validate_file_upload(uploaded_file)
        if not is_valid:
            st.error(message)
            return None, None, None, None, None
        
        # Process file based on type
        df = process_uploaded_file(uploaded_file)
        if df is None:
            return None, None, None, None, None
        
        # Validate DataFrame
        is_valid, message = validate_dataframe(df)
        if not is_valid:
            st.error(message)
            return None, None, None, None, None
        
        # Clean and prepare data
        df = prepare_dataframe(df)
        
        # Create temporary SQLite database
        db_path = create_temp_database(df, uploaded_file.name)
        if not db_path:
            return None, None, None, None, None
        
        # Generate metadata
        table_name = generate_table_name(uploaded_file.name)
        columns = df.columns.tolist()
        data_types = analyze_data_types(df)
        row_count = len(df)
        
        return db_path, table_name, columns, data_types, row_count
        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None, None, None, None, None

def process_uploaded_file(uploaded_file):
    """
    Process uploaded file based on its type
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame or None: Processed DataFrame
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            return process_csv_file(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            return process_excel_file(uploaded_file)
        elif file_extension == 'json':
            return process_json_file(uploaded_file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            return None
            
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None

def process_csv_file(uploaded_file):
    """
    Process CSV file with various encodings and separators
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Processed DataFrame
    """
    # Try different encodings and separators
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    separators = [',', ';', '\t', '|']
    
    for encoding in encodings:
        for separator in separators:
            try:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(
                    uploaded_file,
                    encoding=encoding,
                    sep=separator,
                    low_memory=False,
                    na_values=['', 'NULL', 'null', 'None', 'N/A', 'n/a', '#N/A']
                )
                
                # Check if we got reasonable results
                if len(df.columns) > 1 and len(df) > 0:
                    return df
                    
            except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError):
                continue
    
    # If all attempts failed, try with default settings
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file)

def process_excel_file(uploaded_file):
    """
    Process Excel file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Processed DataFrame
    """
    try:
        # Read Excel file
        excel_data = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # If multiple sheets, use the first one with data
        if isinstance(excel_data, dict):
            for sheet_name, sheet_data in excel_data.items():
                if not sheet_data.empty:
                    return sheet_data
        
        return excel_data
        
    except Exception as e:
        # Try with xlrd engine for older Excel files
        try:
            uploaded_file.seek(0)
            return pd.read_excel(uploaded_file, engine='xlrd')
        except Exception:
            raise e

def process_json_file(uploaded_file):
    """
    Process JSON file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        pandas.DataFrame: Processed DataFrame
    """
    try:
        # Read JSON content
        json_content = uploaded_file.read().decode('utf-8')
        data = json.loads(json_content)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of objects
            if data and isinstance(data[0], dict):
                return pd.json_normalize(data)
            else:
                # Array of primitives
                return pd.DataFrame({'value': data})
        
        elif isinstance(data, dict):
            # Single object or nested structure
            if all(isinstance(v, (list, dict)) for v in data.values()):
                # Nested structure - normalize
                return pd.json_normalize(data)
            else:
                # Simple key-value pairs
                return pd.DataFrame([data])
        
        else:
            # Single primitive value
            return pd.DataFrame({'value': [data]})
            
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON format: {str(e)}")
        return None

def prepare_dataframe(df):
    """
    Clean and prepare DataFrame for database storage
    
    Args:
        df (pandas.DataFrame): Raw DataFrame
        
    Returns:
        pandas.DataFrame: Cleaned DataFrame
    """
    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # Handle duplicate column names
    df.columns = make_unique_columns(df.columns)
    
    # Convert data types for better database compatibility
    df = optimize_data_types(df)
    
    # Handle missing values
    df = handle_missing_values(df)
    
    return df

def make_unique_columns(columns):
    """
    Make column names unique by adding suffixes
    
    Args:
        columns (list): List of column names
        
    Returns:
        list: List of unique column names
    """
    unique_columns = []
    column_counts = {}
    
    for col in columns:
        if col in column_counts:
            column_counts[col] += 1
            unique_columns.append(f"{col}_{column_counts[col]}")
        else:
            column_counts[col] = 0
            unique_columns.append(col)
    
    return unique_columns

def optimize_data_types(df):
    """
    Optimize DataFrame data types for better performance
    
    Args:
        df (pandas.DataFrame): DataFrame to optimize
        
    Returns:
        pandas.DataFrame: Optimized DataFrame
    """
    for col in df.columns:
        # Skip if column is empty
        if df[col].isna().all():
            continue
        
        # Try to convert to numeric
        if df[col].dtype == 'object':
            # Try to convert to numeric
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            if not numeric_series.isna().all():
                df[col] = numeric_series
                continue
            
            # Try to convert to datetime
            try:
                datetime_series = pd.to_datetime(df[col], errors='coerce')
                if not datetime_series.isna().all():
                    df[col] = datetime_series
                    continue
            except:
                pass
    
    return df

def handle_missing_values(df):
    """
    Handle missing values in DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame with potential missing values
        
    Returns:
        pandas.DataFrame: DataFrame with handled missing values
    """
    # For now, just ensure NaN values are properly represented
    # In the future, could implement more sophisticated imputation
    return df.fillna('')  # Replace NaN with empty string for database compatibility

def analyze_data_types(df):
    """
    Analyze and categorize data types in DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
        
    Returns:
        dict: Dictionary mapping column names to data type categories
    """
    data_types = {}
    
    for col in df.columns:
        data_types[col] = infer_data_type(df[col])
    
    return data_types

def create_temp_database(df, filename):
    """
    Create temporary SQLite database from DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to store
        filename (str): Original filename for table naming
        
    Returns:
        str or None: Path to temporary database file
    """
    try:
        # Create temporary file
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        # Connect to database and store data
        conn = sqlite3.connect(temp_db.name)
        
        table_name = generate_table_name(filename)
        df.to_sql(table_name, conn, index=False, if_exists='replace')
        
        conn.close()
        
        return temp_db.name
        
    except Exception as e:
        st.error(f"Error creating temporary database: {str(e)}")
        return None

def generate_table_name(filename):
    """
    Generate table name from filename
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Clean table name
    """
    # Remove extension and clean name
    base_name = filename.split('.')[0]
    table_name = clean_column_name(base_name).upper()
    
    # Ensure it starts with a letter
    if not table_name[0].isalpha():
        table_name = 'TABLE_' + table_name
    
    return table_name

def get_file_info(uploaded_file):
    """
    Get information about uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        dict: File information
    """
    return {
        'name': uploaded_file.name,
        'size': uploaded_file.size,
        'type': uploaded_file.type,
        'size_mb': round(uploaded_file.size / (1024 * 1024), 2)
    }