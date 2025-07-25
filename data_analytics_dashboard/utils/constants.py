"""
Application Constants and Configuration Values
"""

# Application Information
APP_NAME = "Data Analytics Dashboard"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered data analytics dashboard with natural language query generation"

# UI Constants
UI_MESSAGES = {
    'welcome': "Welcome to the Data Analytics Dashboard",
    'login_required': "Please login to access the dashboard",
    'connection_required': "Please connect your data source to get started",
    'table_selection_required': "Please select a table from the sidebar",
    'query_processing': "Processing your query...",
    'generating_sql': "Generating SQL from your question...",
    'executing_query': "Executing database query...",
    'creating_visualization': "Creating visualization...",
    'success_login': "Successfully logged in!",
    'success_logout': "Successfully logged out!",
    'success_connection': "Database connected successfully!",
    'success_file_upload': "File uploaded successfully!",
    'error_connection': "Failed to connect to database",
    'error_query': "Query execution failed",
    'error_authentication': "Authentication failed",
    'error_file_upload': "File upload failed"
}

# Database Constants
DATABASE_CONSTANTS = {
    'max_query_length': 10000,
    'max_results_rows': 10000,
    'query_timeout_seconds': 60,
    'connection_timeout_seconds': 30,
    'max_connections': 10,
    'supported_databases': ['postgresql', 'sqlite'],
    'reserved_table_names': ['users', 'sessions', 'logs']
}

# File Upload Constants
FILE_UPLOAD_CONSTANTS = {
    'max_file_size_mb': 200,
    'supported_formats': ['csv', 'xlsx', 'xls', 'json'],
    'max_columns': 1000,
    'max_rows': 1000000,
    'temp_file_retention_hours': 24,
    'encoding_attempts': ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1'],
    'csv_separators': [',', ';', '\t', '|']
}

# AI/OpenAI Constants
AI_CONSTANTS = {
    'max_prompt_length': 4000,
    'max_response_tokens': 1000,
    'temperature': 0.1,
    'model': 'gpt-4',
    'retry_attempts': 3,
    'timeout_seconds': 30,
    'supported_viz_types': [
        'bar_chart', 'line_chart', 'pie_chart', 'scatter_plot',
        'histogram', 'box_plot', 'heatmap', 'table'
    ]
}

# Authentication Constants
AUTH_CONSTANTS = {
    'jwt_expiration_hours': 24,
    'password_min_length': 6,
    'username_min_length': 3,
    'password_max_length': 128,
    'username_max_length': 50,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 15,
    'session_refresh_threshold_hours': 2
}

# Visualization Constants
VISUALIZATION_CONSTANTS = {
    'default_chart_height': 400,
    'default_chart_width': 600,
    'max_categories_pie_chart': 10,
    'max_data_points_scatter': 10000,
    'default_bin_count_histogram': 30,
    'color_palettes': {
        'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'business': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83'],
        'professional': ['#264653', '#2A9D8F', '#E9C46A', '#F4A261', '#E76F51']
    }
}

# Data Type Mappings
DATA_TYPE_MAPPINGS = {
    'pandas_to_sql': {
        'int64': 'INTEGER',
        'int32': 'INTEGER',
        'float64': 'REAL',
        'float32': 'REAL',
        'object': 'TEXT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP'
    },
    'sql_to_category': {
        'INTEGER': 'integer',
        'BIGINT': 'integer',
        'SERIAL': 'integer',
        'REAL': 'numeric',
        'NUMERIC': 'numeric',
        'DECIMAL': 'numeric',
        'FLOAT': 'numeric',
        'DOUBLE': 'numeric',
        'TEXT': 'text',
        'VARCHAR': 'text',
        'CHAR': 'text',
        'STRING': 'text',
        'TIMESTAMP': 'datetime',
        'DATE': 'datetime',
        'TIME': 'datetime',
        'BOOLEAN': 'boolean'
    }
}

# Error Messages
ERROR_MESSAGES = {
    'database': {
        'connection_failed': "Failed to connect to database. Please check your credentials.",
        'query_failed': "Query execution failed. Please check your SQL syntax.",
        'timeout': "Database operation timed out. Please try again.",
        'no_results': "Query returned no results.",
        'too_many_results': "Query returned too many results. Please add filters."
    },
    'authentication': {
        'invalid_credentials': "Invalid username or password.",
        'user_not_found': "User not found.",
        'user_exists': "Username already exists.",
        'session_expired': "Your session has expired. Please login again.",
        'insufficient_permissions': "You don't have permission to perform this action."
    },
    'file_upload': {
        'file_too_large': "File size exceeds maximum allowed size.",
        'invalid_format': "File format not supported.",
        'corrupted_file': "File appears to be corrupted or unreadable.",
        'empty_file': "Uploaded file is empty.",
        'processing_failed': "Failed to process uploaded file."
    },
    'ai': {
        'api_error': "AI service is currently unavailable. Please try again.",
        'invalid_response': "Received invalid response from AI service.",
        'quota_exceeded': "AI service quota exceeded. Please try again later.",
        'prompt_too_long': "Query is too complex. Please simplify your request."
    }
}

# Success Messages
SUCCESS_MESSAGES = {
    'database': {
        'connected': "Successfully connected to database!",
        'query_executed': "Query executed successfully!",
        'data_loaded': "Data loaded successfully!"
    },
    'authentication': {
        'login_success': "Login successful!",
        'logout_success': "Logout successful!",
        'registration_success': "Account created successfully!"
    },
    'file_upload': {
        'upload_success': "File uploaded successfully!",
        'processing_complete': "File processing completed!"
    },
    'ai': {
        'query_generated': "SQL query generated successfully!",
        'analysis_complete': "Data analysis completed!"
    }
}

# Default Values
DEFAULT_VALUES = {
    'query_limit': 1000,
    'chart_theme': 'plotly',
    'date_format': '%Y-%m-%d',
    'number_format': '{:,.2f}',
    'max_display_rows': 100,
    'max_display_columns': 20,
    'session_timeout_minutes': 30
}

# Business Domain Keywords
BUSINESS_DOMAINS = {
    'retail': [
        'sales', 'product', 'customer', 'order', 'price', 'quantity', 
        'inventory', 'store', 'purchase', 'revenue', 'discount', 'category'
    ],
    'finance': [
        'account', 'transaction', 'balance', 'amount', 'payment', 'credit', 
        'debit', 'investment', 'portfolio', 'risk', 'return', 'profit', 'loss'
    ],
    'healthcare': [
        'patient', 'diagnosis', 'treatment', 'medication', 'hospital', 'doctor',
        'nurse', 'appointment', 'symptom', 'medical', 'health', 'clinical'
    ],
    'marketing': [
        'campaign', 'click', 'impression', 'conversion', 'lead', 'channel',
        'audience', 'engagement', 'ctr', 'roi', 'brand', 'advertising'
    ],
    'hr': [
        'employee', 'salary', 'department', 'hire', 'performance', 'training',
        'manager', 'staff', 'payroll', 'benefits', 'recruitment', 'skill'
    ],
    'education': [
        'student', 'course', 'grade', 'enrollment', 'teacher', 'class',
        'school', 'university', 'exam', 'curriculum', 'semester', 'degree'
    ],
    'logistics': [
        'shipment', 'delivery', 'warehouse', 'supplier', 'inventory', 'transport',
        'freight', 'carrier', 'tracking', 'distribution', 'logistics', 'supply'
    ]
}

# Chart Configuration
CHART_CONFIGS = {
    'bar_chart': {
        'max_categories': 50,
        'min_categories': 1,
        'recommended_height': 400,
        'color_scheme': 'category10'
    },
    'line_chart': {
        'max_data_points': 1000,
        'min_data_points': 2,
        'recommended_height': 400,
        'show_markers': True
    },
    'pie_chart': {
        'max_categories': 10,
        'min_categories': 2,
        'recommended_height': 400,
        'show_labels': True
    },
    'scatter_plot': {
        'max_data_points': 5000,
        'min_data_points': 5,
        'recommended_height': 400,
        'show_trend_line': False
    },
    'histogram': {
        'default_bins': 30,
        'max_bins': 100,
        'min_bins': 5,
        'recommended_height': 400
    },
    'box_plot': {
        'max_categories': 20,
        'min_categories': 1,
        'recommended_height': 400,
        'show_outliers': True
    },
    'heatmap': {
        'max_dimensions': 50,
        'min_dimensions': 2,
        'recommended_height': 400,
        'color_scale': 'RdYlBu'
    }
}

# SQL Query Templates
SQL_TEMPLATES = {
    'basic_select': "SELECT {columns} FROM {table} LIMIT {limit}",
    'count_all': "SELECT COUNT(*) as total_records FROM {table}",
    'group_by_count': "SELECT {column}, COUNT(*) as count FROM {table} GROUP BY {column} ORDER BY count DESC",
    'statistics': "SELECT AVG({column}) as avg_value, MIN({column}) as min_value, MAX({column}) as max_value FROM {table}",
    'top_n': "SELECT {columns} FROM {table} ORDER BY {order_column} DESC LIMIT {n}",
    'date_range': "SELECT MIN({date_column}) as start_date, MAX({date_column}) as end_date FROM {table}",
    'null_check': "SELECT COUNT(*) as null_count FROM {table} WHERE {column} IS NULL"
}

# Regular Expressions
REGEX_PATTERNS = {
    'sql_keywords': r'\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|JOIN|UNION|WITH)\b',
    'table_name': r'^[a-zA-Z][a-zA-Z0-9_]*$',
    'column_name': r'^[a-zA-Z][a-zA-Z0-9_]*$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
    'url': r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
}

# API Endpoints (if needed for future expansion)
API_ENDPOINTS = {
    'openai': 'https://api.openai.com/v1/chat/completions',
    'health_check': '/health',
    'metrics': '/metrics',
    'status': '/status'
}

# Cache Settings
CACHE_SETTINGS = {
    'query_results_ttl_seconds': 3600,  # 1 hour
    'table_info_ttl_seconds': 7200,     # 2 hours
    'user_session_ttl_seconds': 86400,  # 24 hours
    'max_cache_size_mb': 100,
    'cleanup_interval_minutes': 30
}

# Logging Configuration
LOGGING_CONFIG = {
    'levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'default_level': 'INFO',
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'max_file_size_mb': 10,
    'backup_count': 5
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'query_execution_warning_seconds': 5,
    'query_execution_error_seconds': 30,
    'file_upload_warning_mb': 50,
    'response_time_warning_seconds': 2,
    'memory_usage_warning_mb': 500
}

# Feature Flags
FEATURE_FLAGS = {
    'enable_file_upload': True,
    'enable_postgresql': True,
    'enable_query_caching': True,
    'enable_advanced_visualizations': True,
    'enable_export_functionality': True,
    'enable_query_history': True,
    'enable_user_preferences': True,
    'enable_error_tracking': True
}

# Security Settings
SECURITY_SETTINGS = {
    'require_https': False,  # Set to True in production
    'enable_csrf_protection': True,
    'max_request_size_mb': 100,
    'rate_limit_requests_per_minute': 60,
    'password_complexity_required': True,
    'session_cookie_secure': False,  # Set to True in production
    'session_cookie_httponly': True
}

# Notification Settings
NOTIFICATION_SETTINGS = {
    'show_success_messages': True,
    'show_warning_messages': True,
    'show_error_messages': True,
    'auto_dismiss_success_after_seconds': 5,
    'auto_dismiss_warning_after_seconds': 10,
    'auto_dismiss_error_after_seconds': 0  # Don't auto-dismiss errors
}

# Export Settings
EXPORT_SETTINGS = {
    'supported_formats': ['csv', 'excel', 'json'],
    'max_export_rows': 100000,
    'default_format': 'csv',
    'include_headers': True,
    'date_format_export': '%Y-%m-%d %H:%M:%S'
}

# Help and Documentation
HELP_MESSAGES = {
    'query_examples': [
        "Show me sales trends over time",
        "What are the top 10 customers by revenue?",
        "Compare performance across different categories",
        "Show me data quality insights",
        "What's the distribution of orders by region?"
    ],
    'tips': [
        "Be specific about what you want to analyze",
        "Mention time periods if relevant (last month, this year, etc.)",
        "Ask for comparisons between different groups",
        "Request specific metrics (average, total, count, etc.)",
        "Use natural language - the AI will convert it to SQL"
    ],
    'troubleshooting': [
        "If no results appear, try rephrasing your question",
        "Check that your data source is properly connected",
        "Ensure your question matches the available data columns",
        "Try simpler queries if complex ones fail",
        "Use the sample suggestions for inspiration"
    ]
}

# App Configuration Validation
def validate_app_constants():
    """Validate application constants for consistency"""
    errors = []
    
    # Check file size limits
    if FILE_UPLOAD_CONSTANTS['max_file_size_mb'] > SECURITY_SETTINGS['max_request_size_mb']:
        errors.append("File upload size exceeds maximum request size")
    
    # Check authentication settings
    if AUTH_CONSTANTS['password_min_length'] < 1:
        errors.append("Minimum password length must be at least 1")
    
    if AUTH_CONSTANTS['username_min_length'] < 1:
        errors.append("Minimum username length must be at least 1")
    
    # Check AI settings
    if AI_CONSTANTS['max_prompt_length'] < 100:
        errors.append("Maximum prompt length too small")
    
    return len(errors) == 0, errors

# Configuration Export Function
def get_app_constants():
    """Get all application constants as a dictionary"""
    return {
        'app_info': {
            'name': APP_NAME,
            'version': APP_VERSION,
            'description': APP_DESCRIPTION
        },
        'ui_messages': UI_MESSAGES,
        'database': DATABASE_CONSTANTS,
        'file_upload': FILE_UPLOAD_CONSTANTS,
        'ai': AI_CONSTANTS,
        'auth': AUTH_CONSTANTS,
        'visualization': VISUALIZATION_CONSTANTS,
        'data_types': DATA_TYPE_MAPPINGS,
        'errors': ERROR_MESSAGES,
        'success': SUCCESS_MESSAGES,
        'defaults': DEFAULT_VALUES,
        'business_domains': BUSINESS_DOMAINS,
        'charts': CHART_CONFIGS,
        'sql_templates': SQL_TEMPLATES,
        'regex': REGEX_PATTERNS,
        'cache': CACHE_SETTINGS,
        'logging': LOGGING_CONFIG,
        'performance': PERFORMANCE_THRESHOLDS,
        'features': FEATURE_FLAGS,
        'security': SECURITY_SETTINGS,
        'notifications': NOTIFICATION_SETTINGS,
        'export': EXPORT_SETTINGS,
        'help': HELP_MESSAGES
    }