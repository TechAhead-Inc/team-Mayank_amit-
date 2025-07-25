"""
SQL Query Execution Module
"""

import sqlite3
import pandas as pd
import streamlit as st
from sqlalchemy import text
from utils.validators import validate_query_input
import re

def execute_sql_query(sql, db_engine_or_path):
    """
    Execute SQL query on either PostgreSQL engine or SQLite path
    
    Args:
        sql (str): SQL query to execute
        db_engine_or_path: SQLAlchemy engine or SQLite file path
        
    Returns:
        pandas.DataFrame: Query results
    """
    try:
        # Clean and validate the SQL query
        sql = clean_sql_query(sql)
        
        # Basic validation
        if not sql or len(sql.strip()) < 5:
            st.error("Generated SQL query is too short or empty")
            return pd.DataFrame()
        
        # Security validation
        if not is_safe_query(sql):
            st.error("Query contains potentially unsafe operations")
            return pd.DataFrame()
        
        # Execute based on database type
        if isinstance(db_engine_or_path, str):
            # SQLite path
            return execute_sqlite_query(sql, db_engine_or_path)
        else:
            # PostgreSQL engine
            return execute_postgres_query(sql, db_engine_or_path)
        
    except Exception as e:
        handle_query_error(e, sql)
        return pd.DataFrame()

def execute_postgres_query(sql, engine):
    """
    Execute query on PostgreSQL database
    
    Args:
        sql (str): SQL query
        engine: SQLAlchemy engine
        
    Returns:
        pandas.DataFrame: Query results
    """
    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql), conn)
    return df

def execute_sqlite_query(sql, db_path):
    """
    Execute query on SQLite database
    
    Args:
        sql (str): SQL query
        db_path (str): Path to SQLite database file
        
    Returns:
        pandas.DataFrame: Query results
    """
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()

def clean_sql_query(sql):
    """
    Clean and normalize SQL query
    
    Args:
        sql (str): Raw SQL query
        
    Returns:
        str: Cleaned SQL query
    """
    if not sql:
        return ""
    
    sql = sql.strip()
    
    # Remove markdown formatting
    if sql.startswith('```'):
        lines = sql.split('\n')
        sql_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            elif not in_code_block:
                sql_lines.append(line)
        sql = '\n'.join(sql_lines).strip()
    
    # Remove trailing semicolon
    sql = sql.rstrip(';').strip()
    
    # Remove extra whitespace
    sql = ' '.join(sql.split())
    
    return sql

def is_safe_query(sql):
    """
    Check if SQL query is safe to execute
    
    Args:
        sql (str): SQL query to check
        
    Returns:
        bool: True if query is safe, False otherwise
    """
    sql_upper = sql.upper().strip()
    
    # Must start with safe operations
    safe_starts = ['SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN']
    if not any(sql_upper.startswith(keyword) for keyword in safe_starts):
        return False
    
    # Check for dangerous keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 
        'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'--',  # SQL comments
        r'/\*',  # Multi-line comments
        r';.*SELECT',  # Multiple statements
        r'UNION.*SELECT',  # Union injections
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, sql_upper):
            return False
    
    return True

def validate_sql_query(sql):
    """
    Validate SQL query format and safety
    
    Args:
        sql (str): SQL query to validate
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not sql or not sql.strip():
        return False, "Query is empty"
    
    # Clean the query first
    cleaned_sql = clean_sql_query(sql)
    
    if len(cleaned_sql) < 5:
        return False, "Query is too short"
    
    if len(cleaned_sql) > 10000:
        return False, "Query is too long (max 10,000 characters)"
    
    # Check if it's safe
    if not is_safe_query(cleaned_sql):
        return False, "Query contains unsafe operations"
    
    # Basic syntax check
    if not cleaned_sql.upper().startswith(('SELECT', 'WITH')):
        return False, "Query must start with SELECT or WITH"
    
    return True, "Valid query"

def handle_query_error(error, sql):
    """
    Handle and display query execution errors
    
    Args:
        error (Exception): The exception that occurred
        sql (str): The SQL query that caused the error
    """
    error_msg = str(error)
    
    if "syntax error" in error_msg.lower():
        st.error(f"SQL Syntax Error: {error_msg}")
        st.error(f"**Query:** `{sql[:200]}{'...' if len(sql) > 200 else ''}`")
        st.info("💡 The AI might have generated invalid SQL. Try rephrasing your question.")
    
    elif "does not exist" in error_msg.lower():
        st.error(f"Database Error: {error_msg}")
        st.info("💡 The table or column might not exist. Check your data source.")
    
    elif "permission" in error_msg.lower():
        st.error(f"Permission Error: {error_msg}")
        st.info("💡 You don't have permission to access this data.")
    
    else:
        st.error(f"Database Error: {error_msg}")

def get_query_statistics(df):
    """
    Get statistics about query results
    
    Args:
        df (pandas.DataFrame): Query results
        
    Returns:
        dict: Query statistics
    """
    if df.empty:
        return {
            'rows': 0,
            'columns': 0,
            'memory_usage': 0,
            'has_nulls': False
        }
    
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'has_nulls': df.isnull().any().any(),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'text_columns': len(df.select_dtypes(include=['object']).columns),
        'datetime_columns': len(df.select_dtypes(include=['datetime']).columns)
    }

def format_query_for_display(sql):
    """
    Format SQL query for better display
    
    Args:
        sql (str): SQL query
        
    Returns:
        str: Formatted SQL query
    """
    if not sql:
        return ""
    
    # Basic SQL formatting
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING',
        'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'OUTER JOIN',
        'UNION', 'WITH', 'AS', 'AND', 'OR', 'IN', 'NOT IN', 'EXISTS',
        'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'LIMIT', 'OFFSET'
    ]
    
    formatted_sql = sql
    for keyword in keywords:
        # Add line breaks before major keywords
        if keyword in ['FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'HAVING']:
            formatted_sql = formatted_sql.replace(f' {keyword} ', f'\n{keyword} ')
    
    return formatted_sql