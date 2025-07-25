"""
Configuration package for the Data Analytics Dashboard

This package contains all configuration-related modules including
application settings, database configuration, and environment management.
"""

from .settings import (
    load_app_config, 
    JWT_SECRET, 
    OPENAI_API_KEY, 
    CUSTOM_CSS,
    get_env_template
)
from .database import (
    DATABASE_CONFIG, 
    get_database_url, 
    create_database_engine,
    validate_database_config
)

__version__ = "1.0.0"
__all__ = [
    'load_app_config', 
    'JWT_SECRET', 
    'OPENAI_API_KEY', 
    'CUSTOM_CSS',
    'get_env_template',
    'DATABASE_CONFIG',
    'get_database_url',
    'create_database_engine',
    'validate_database_config'
]
