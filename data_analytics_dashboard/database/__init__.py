"""
Database package for connection management and queries

This package handles all database-related functionality including
PostgreSQL and SQLite connections, query execution, and file processing.
"""

from .connection import (
    create_postgres_connection, 
    get_postgres_tables, 
    get_postgres_table_info,
    test_database_connection,
    render_data_connection_ui,
    disconnect_database,
    get_connection_status
)
from .queries import (
    execute_sql_query, 
    validate_sql_query,
    execute_postgres_query,
    execute_sqlite_query,
    clean_sql_query,
    is_safe_query,
    get_query_statistics
)
from .file_handler import (
    handle_file_upload,
    process_uploaded_file,
    process_csv_file,
    process_excel_file,
    process_json_file,
    get_file_info
)

__version__ = "1.0.0"
__all__ = [
    # Connection Management
    'create_postgres_connection', 
    'get_postgres_tables', 
    'get_postgres_table_info',
    'test_database_connection',
    'render_data_connection_ui',
    'disconnect_database',
    'get_connection_status',
    # Query Execution
    'execute_sql_query', 
    'validate_sql_query',
    'execute_postgres_query',
    'execute_sqlite_query',
    'clean_sql_query',
    'is_safe_query',
    'get_query_statistics',
    # File Handling
    'handle_file_upload',
    'process_uploaded_file',
    'process_csv_file',
    'process_excel_file',
    'process_json_file',
    'get_file_info'
]