"""
Database Connection Management Module
"""

import streamlit as st
from sqlalchemy import create_engine, text
from config.settings import DATABASE_CONFIG, get_env_template
from auth.user_manager import create_users_table
from database.file_handler import handle_file_upload

def create_postgres_connection():
    """
    Create PostgreSQL connection using configuration
    
    Returns:
        tuple: (engine, success: bool, message: str)
    """
    try:
        config = DATABASE_CONFIG
        host = config['host']
        port = config['port']
        database = config['database']
        username = config['username']
        password = config['password']
        
        if not all([database, username, password]):
            return None, False, "Missing PostgreSQL credentials in .env file"
        
        # Create connection string
        conn_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(conn_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create users table
        create_users_table(engine)
        
        return engine, True, "Connected successfully to PostgreSQL"
        
    except Exception as e:
        return None, False, f"PostgreSQL connection failed: {str(e)}"

def get_postgres_tables(engine):
    """
    Get all tables from PostgreSQL database excluding system tables
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        list: List of table names
    """
    try:
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE' 
        AND table_name != 'users'
        ORDER BY table_name
        """
        with engine.connect() as conn:
            result = conn.execute(text(tables_query))
            tables = [row[0] for row in result]
        return tables
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []

def get_postgres_table_info(engine, table_name):
    """
    Get detailed table information from PostgreSQL
    
    Args:
        engine: SQLAlchemy database engine
        table_name (str): Name of the table
        
    Returns:
        dict or None: Table information including columns, data types, and row count
    """
    try:
        # Get column information
        columns_query = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' AND table_schema = 'public'
        ORDER BY ordinal_position
        """
        
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        
        with engine.connect() as conn:
            # Get columns
            columns_result = conn.execute(text(columns_query))
            columns_data = columns_result.fetchall()
            
            # Get count
            count_result = conn.execute(text(count_query))
            row_count = count_result.fetchone()[0]
        
        if not columns_data:
            return None
        
        columns = [col[0] for col in columns_data]
        
        # Create data types dictionary
        data_types = {}
        for col_data in columns_data:
            col_name, data_type, is_nullable = col_data
            if 'int' in data_type or 'serial' in data_type:
                data_types[col_name] = 'integer'
            elif 'numeric' in data_type or 'decimal' in data_type or 'float' in data_type or 'double' in data_type:
                data_types[col_name] = 'numeric'
            elif 'timestamp' in data_type or 'date' in data_type:
                data_types[col_name] = 'datetime'
            else:
                data_types[col_name] = 'text'
        
        return {
            "columns": columns,
            "data_types": data_types,
            "row_count": row_count
        }
        
    except Exception as e:
        st.error(f"Error getting table info: {str(e)}")
        return None

def test_database_connection(engine):
    """
    Test database connection
    
    Args:
        engine: SQLAlchemy database engine
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            if test_value == 1:
                return True, "Connection successful"
            else:
                return False, "Connection test failed"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def render_data_connection_ui():
    """Render data connection UI in sidebar"""
    st.subheader("Data Connection")
    
    connection_type = st.radio(
        "Choose data source:",
        ["PostgreSQL Database", "Upload File"],
        key="connection_radio"
    )

    if connection_type == "PostgreSQL Database":
        render_postgres_connection_ui()
    elif connection_type == "Upload File":
        render_file_upload_ui()

def render_postgres_connection_ui():
    """Render PostgreSQL connection interface"""
    st.markdown("**PostgreSQL Configuration**")
    
    # Show configuration info
    with st.expander("Environment Setup", expanded=False):
        st.code(get_env_template())
    
    config = DATABASE_CONFIG
    st.write(f"**Host:** {config['host']}")
    st.write(f"**Port:** {config['port']}")
    st.write(f"**Database:** {config['database'] or 'Not configured'}")
    st.write(f"**Username:** {config['username'] or 'Not configured'}")
    
    # Connection status and table selection
    if st.session_state.connection_type == "postgres" and st.session_state.db_engine:
        render_postgres_connected_state()
    else:
        render_postgres_connection_button()

def render_postgres_connected_state():
    """Render UI when PostgreSQL is connected"""
    st.success("Connected to PostgreSQL")
    
    try:
        tables = get_postgres_tables(st.session_state.db_engine)
        
        if tables:
            current_table = st.session_state.table_name if st.session_state.table_name in tables else tables[0]
            selected_table = st.selectbox("Select Table:", tables, 
                                        index=tables.index(current_table) if current_table in tables else 0)
            
            if selected_table != st.session_state.table_name or not st.session_state.columns:
                table_info = get_postgres_table_info(st.session_state.db_engine, selected_table)
                
                if table_info:
                    st.session_state.table_name = selected_table
                    st.session_state.columns = table_info['columns']
                    st.session_state.data_types = table_info['data_types']
                    st.session_state.row_count = table_info['row_count']
            
            if st.session_state.table_name:
                st.info(f"**Table:** {st.session_state.table_name}")
                st.info(f"**Rows:** {st.session_state.row_count:,}")
                st.info(f"**Columns:** {len(st.session_state.columns)}")
            
            if st.button("Disconnect", use_container_width=True):
                disconnect_database()
                
        else:
            st.warning("No tables found in database")
            if st.button("Disconnect", use_container_width=True):
                disconnect_database()
                
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        if st.button("Reconnect", use_container_width=True):
            disconnect_database()

def render_postgres_connection_button():
    """Render PostgreSQL connection button"""
    if st.button("Connect to PostgreSQL", use_container_width=True):
        with st.spinner("Connecting to PostgreSQL..."):
            engine, success, message = create_postgres_connection()
        
        if success:
            tables = get_postgres_tables(engine)
            
            if tables:
                st.session_state.db_engine = engine
                st.session_state.connection_type = "postgres"
                
                # Auto-select first table
                first_table = tables[0]
                table_info = get_postgres_table_info(engine, first_table)
                
                if table_info:
                    st.session_state.table_name = first_table
                    st.session_state.columns = table_info['columns']
                    st.session_state.data_types = table_info['data_types']
                    st.session_state.row_count = table_info['row_count']
                    
                    st.success("Connected to PostgreSQL!")
                    st.rerun()
            else:
                st.warning("No tables found in database")
        else:
            st.error(message)

def render_file_upload_ui():
    """Render file upload interface"""
    st.markdown("**File Upload**")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Upload CSV, Excel, or JSON files"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            result = handle_file_upload(uploaded_file)
        
        if result[0]:  # db_path exists
            db_path, table_name, columns, data_types, row_count = result
            
            st.session_state.db_engine = db_path
            st.session_state.table_name = table_name
            st.session_state.columns = columns
            st.session_state.data_types = data_types
            st.session_state.row_count = row_count
            st.session_state.connection_type = "file"
            
            st.success("File loaded successfully!")
            st.info(f"**Table:** {table_name}")
            st.info(f"**Rows:** {row_count:,}")
            st.info(f"**Columns:** {len(columns)}")

def disconnect_database():
    """Disconnect from database and clear session state"""
    st.session_state.db_engine = None
    st.session_state.connection_type = None
    st.session_state.table_name = None
    st.session_state.columns = []
    st.session_state.data_types = {}
    st.session_state.row_count = 0
    st.rerun()

def get_connection_status():
    """
    Get current connection status
    
    Returns:
        dict: Connection status information
    """
    return {
        'is_connected': st.session_state.db_engine is not None,
        'connection_type': st.session_state.connection_type,
        'table_name': st.session_state.table_name,
        'columns_count': len(st.session_state.columns) if st.session_state.columns else 0,
        'row_count': st.session_state.row_count
    }