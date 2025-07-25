"""
Application Configuration and Settings
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.1

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv("PG_HOST", "localhost"),
    'port': os.getenv("PG_PORT", "5432"),
    'database': os.getenv("PG_DATABASE"),
    'username': os.getenv("PG_USERNAME"),
    'password': os.getenv("PG_PASSWORD")
}

# Application Constants
APP_TITLE = "Data Analytics Dashboard"
MAX_FILE_SIZE_MB = 200
SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'json']
DEFAULT_QUERY_LIMIT = 1000
MAX_UNIQUE_VALUES_DISPLAY = 50

# Custom CSS Styles
CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #2c3e50;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .sidebar .sidebar-content {
        background-color: #f1f3f4;
    }
</style>
"""

def load_app_config():
    """Load and validate application configuration"""
    config = {
        'jwt': {
            'secret': JWT_SECRET,
            'algorithm': JWT_ALGORITHM,
            'expiration_hours': JWT_EXPIRATION_HOURS
        },
        'openai': {
            'api_key': OPENAI_API_KEY,
            'model': OPENAI_MODEL,
            'max_tokens': OPENAI_MAX_TOKENS,
            'temperature': OPENAI_TEMPERATURE
        },
        'database': DATABASE_CONFIG,
        'app': {
            'title': APP_TITLE,
            'max_file_size_mb': MAX_FILE_SIZE_MB,
            'supported_file_types': SUPPORTED_FILE_TYPES,
            'default_query_limit': DEFAULT_QUERY_LIMIT,
            'max_unique_values_display': MAX_UNIQUE_VALUES_DISPLAY
        }
    }
    
    # Validate critical configuration
    if not OPENAI_API_KEY:
        st.error("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        st.stop()
    
    return config

def get_env_template():
    """Get environment variables template for display"""
    return """
# Database Configuration
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=your_database_name
PG_USERNAME=your_db_username
PG_PASSWORD=your_db_password

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# JWT Configuration
JWT_SECRET=your_secret_key_change_this_in_production
"""