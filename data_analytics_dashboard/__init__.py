"""
Data Analytics Dashboard - AI-Powered Analytics Platform

A comprehensive data analytics dashboard with natural language query generation,
interactive visualizations, and secure user authentication.

Version: 1.0.0
Author: Data Analytics Team
License: MIT
"""

__version__ = "1.0.0"
__title__ = "Data Analytics Dashboard"
__description__ = "AI-powered data analytics dashboard with natural language query generation"
__author__ = "Data Analytics Team"
__license__ = "MIT"

# Optional: Import main application components for easy access
try:
    from .main import main
    from .config import load_app_config
    from .auth import get_current_user
    from .database import execute_sql_query
    from .ai import generate_sql_from_question
    from .visualization import create_visualization
    
    __all__ = [
        'main',
        'load_app_config',
        'get_current_user', 
        'execute_sql_query',
        'generate_sql_from_question',
        'create_visualization'
    ]
except ImportError:
    # Handle case where dependencies aren't installed yet
    __all__ = []

def get_version():
    """Get the current version of the application"""
    return __version__

def get_info():
    """Get application information"""
    return {
        'title': __title__,
        'version': __version__,
        'description': __description__,
        'author': __author__,
        'license': __license__
    }
